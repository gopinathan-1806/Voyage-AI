"""
Hybrid Retriever combining FAISS Vector Similarity + BM25 Keyword Search + Lexical Overlap.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from rank_bm25 import BM25Okapi

from app.config import config
from app.rag.indexer import TravelKnowledgeIndexer
from app.rag.retrieval_quality import compute_lexical_overlap
from app.rag.query_rewriter import TravelQueryRewriter
from app.logging_config import get_logger

logger = get_logger(__name__)


class ScoredDocument:
    """Document paired with comprehensive retrieval metrics."""
    def __init__(
        self,
        document: Document,
        combined_score: float,
        vector_score: float = 0.0,
        bm25_score: float = 0.0,
        lexical_score: float = 0.0,
        authority_boost: float = 1.0,
    ):
        self.document = document
        self.combined_score = combined_score
        self.vector_score = vector_score
        self.bm25_score = bm25_score
        self.lexical_score = lexical_score
        self.authority_boost = authority_boost

    @property
    def page_content(self) -> str:
        return self.document.page_content

    @property
    def metadata(self) -> Dict[str, Any]:
        return self.document.metadata


class HybridTravelRetriever:
    """
    Orchestrates Vector and BM25 retrievers with reciprocal/weighted ranking,
    metadata filtering, and relevance evaluation.
    """

    def __init__(
        self,
        vector_store: Optional[FAISS] = None,
        bm25_index: Optional[BM25Okapi] = None,
        docs: Optional[List[Document]] = None,
    ):
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        self.docs = docs or []

        if self.vector_store is None or self.bm25_index is None or not self.docs:
            self._lazy_load()

    def _lazy_load(self):
        v_store, bm25, docs = TravelKnowledgeIndexer.load_indexes()
        if v_store is None or bm25 is None or not docs:
            logger.info("Indexes not found on disk. Building new indexes...")
            indexer = TravelKnowledgeIndexer()
            v_store, bm25, docs = indexer.build_indexes()
            
        self.vector_store = v_store
        self.bm25_index = bm25
        self.docs = docs

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        destination_filter: Optional[str] = None,
        context_metadata: Optional[Dict[str, str]] = None,
    ) -> List[ScoredDocument]:
        """
        Executes hybrid retrieval:
        1. Query rewriting with travel context.
        2. Vector similarity search with normalized distance.
        3. BM25 keyword search with min-max normalization.
        4. Lexical overlap calculation.
        5. Weighted combination and authority scoring.
        6. Metadata post-filtering.
        """
        k = top_k or config.retrieval_top_k
        rewritten_query = TravelQueryRewriter.rewrite_query(query, context_metadata)

        # 1. Vector Search
        vector_candidates: Dict[int, float] = {}  # index -> score (0 to 1)
        if self.vector_store:
            try:
                # FAISS returns (doc, L2 distance). Smaller L2 = higher similarity
                results_with_scores = self.vector_store.similarity_search_with_score(rewritten_query, k=k * 2)
                for doc, score in results_with_scores:
                    # Map doc back to index in self.docs by content match or metadata
                    doc_idx = self._find_doc_index(doc)
                    if doc_idx is not None:
                        # Convert L2 distance or cosine to a [0, 1] similarity metric
                        sim = float(1.0 / (1.0 + max(0.0, score)))
                        vector_candidates[doc_idx] = sim
            except Exception as e:
                logger.error(f"Vector search failed: {e}")

        # 2. BM25 Search
        bm25_candidates: Dict[int, float] = {}
        if self.bm25_index and self.docs:
            tokens = rewritten_query.lower().split()
            bm25_scores = self.bm25_index.get_scores(tokens)
            max_bm25 = float(np.max(bm25_scores)) if len(bm25_scores) > 0 and np.max(bm25_scores) > 0 else 1.0
            
            top_indices = np.argsort(bm25_scores)[::-1][:k * 2]
            for idx in top_indices:
                score = float(bm25_scores[idx]) / max_bm25 if max_bm25 > 0 else 0.0
                if score > 0:
                    bm25_candidates[int(idx)] = score

        # 3. Combine Candidates
        all_candidate_indices = set(vector_candidates.keys()).union(set(bm25_candidates.keys()))
        if not all_candidate_indices:
            # Fallback: scan all documents for lexical overlap if candidate sets empty
            all_candidate_indices = set(range(len(self.docs)))

        scored_docs: List[ScoredDocument] = []
        w_vec = config.vector_weight
        w_bm25 = config.bm25_weight
        w_lex = config.lexical_weight

        for idx in all_candidate_indices:
            if idx >= len(self.docs):
                continue
            doc = self.docs[idx]

            # Destination Filter
            if destination_filter:
                doc_dest = doc.metadata.get("destination_country", "").strip().lower()
                target_dest = destination_filter.strip().lower()
                if doc_dest and target_dest and doc_dest != target_dest and doc_dest != "all":
                    continue

            v_score = vector_candidates.get(idx, 0.0)
            b_score = bm25_candidates.get(idx, 0.0)
            l_score = compute_lexical_overlap(rewritten_query, doc.page_content)

            # Metadata boost for destination matching query or destination_filter
            meta_boost = 1.0
            doc_country = doc.metadata.get("destination_country", "").lower()
            query_lower = rewritten_query.lower()
            if destination_filter and doc_country == destination_filter.lower():
                meta_boost = 2.0
            elif doc_country and doc_country in query_lower:
                meta_boost = 2.0

            combined_score = (
                (v_score * w_vec) +
                (b_score * w_bm25) +
                (l_score * w_lex)
            ) * meta_boost

            scored_docs.append(
                ScoredDocument(
                    document=doc,
                    combined_score=round(combined_score, 4),
                    vector_score=round(v_score, 4),
                    bm25_score=round(b_score, 4),
                    lexical_score=round(l_score, 4),
                    authority_boost=meta_boost,
                )
            )

        # Sort descending by combined score
        scored_docs.sort(key=lambda x: x.combined_score, reverse=True)
        return scored_docs[:k]

    def _find_doc_index(self, target_doc: Document) -> Optional[int]:
        """Match returned vector document to internal indexed document list."""
        for idx, doc in enumerate(self.docs):
            if (
                doc.page_content == target_doc.page_content and
                doc.metadata.get("doc_id") == target_doc.metadata.get("doc_id") and
                doc.metadata.get("chunk_index") == target_doc.metadata.get("chunk_index")
            ):
                return idx
        return None
