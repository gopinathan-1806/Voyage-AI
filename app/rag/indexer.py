"""
Indexer module: Chunking, FAISS vector store creation, BM25 index creation, and persistence.
"""

import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from app.config import config
from app.ingestion.pipeline import IngestionPipeline
from app.rag.embeddings import get_embedding_model
from app.logging_config import get_logger

logger = get_logger(__name__)


class TravelKnowledgeIndexer:
    """Responsible for building and storing searchable Vector and BM25 representations of TravelDocuments."""

    def __init__(self):
        self.config = config
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=["\n### ", "\n## ", "\n# ", "\n\n", "\n", ". ", " "]
        )
        self.embedding_model = get_embedding_model()

    def build_indexes(self) -> Tuple[FAISS, BM25Okapi, List[Document]]:
        """Load processed documents, chunk them, build FAISS & BM25 indexes, and save to disk."""
        pipeline = IngestionPipeline()
        travel_docs = pipeline.load_all_processed_documents()
        
        if not travel_docs:
            logger.warning("No travel documents found to index! Attempting to seed first...")
            from data.travel.seed_data import seed_knowledge_base
            seed_knowledge_base()
            travel_docs = pipeline.load_all_processed_documents()

        langchain_docs: List[Document] = []
        for t_doc in travel_docs:
            metadata = t_doc.to_metadata()
            # Split document text into chunks
            chunks = self.text_splitter.split_text(t_doc.content)
            for idx, chunk in enumerate(chunks):
                chunk_meta = dict(metadata)
                chunk_meta["chunk_index"] = idx
                chunk_meta["total_chunks"] = len(chunks)
                langchain_docs.append(Document(page_content=chunk, metadata=chunk_meta))

        logger.info(f"Generated {len(langchain_docs)} chunks from {len(travel_docs)} travel documents.")

        # 1. Build FAISS Vector Index
        vector_store = FAISS.from_documents(langchain_docs, self.embedding_model)

        # 2. Build BM25 Keyword Index
        tokenized_corpus = [doc.page_content.lower().split() for doc in langchain_docs]
        bm25_index = BM25Okapi(tokenized_corpus)

        # 3. Save indexes to disk
        self.save_indexes(vector_store, bm25_index, langchain_docs)

        return vector_store, bm25_index, langchain_docs

    def save_indexes(self, vector_store: FAISS, bm25_index: BM25Okapi, docs: List[Document]) -> None:
        """Persist FAISS index, BM25 pickle, and metadata documents."""
        self.config.indexes_dir.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS
        vector_store.save_local(str(self.config.faiss_index_dir))
        
        # Save BM25 and Chunk Docs
        with open(self.config.bm25_index_path, "wb") as f:
            pickle.dump({"bm25": bm25_index, "docs": docs}, f)
            
        # Save metadata summary
        meta_summary = [
            {"metadata": d.metadata, "preview": d.page_content[:120]}
            for d in docs
        ]
        with open(self.config.metadata_index_path, "w", encoding="utf-8") as f:
            json.dump(meta_summary, f, indent=2)

        logger.info(f"Successfully saved FAISS to {self.config.faiss_index_dir} and BM25 to {self.config.bm25_index_path}")

    @classmethod
    def load_indexes(cls) -> Tuple[Optional[FAISS], Optional[BM25Okapi], List[Document]]:
        """Load stored indexes from disk, or return empty structures if not found."""
        embedding_model = get_embedding_model()
        vector_store = None
        bm25_index = None
        docs: List[Document] = []

        if config.faiss_index_dir.exists():
            try:
                vector_store = FAISS.load_local(
                    str(config.faiss_index_dir),
                    embedding_model,
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                logger.error(f"Error loading FAISS index: {e}")

        if config.bm25_index_path.exists():
            try:
                with open(config.bm25_index_path, "rb") as f:
                    data = pickle.load(f)
                    bm25_index = data.get("bm25")
                    docs = data.get("docs", [])
            except Exception as e:
                logger.error(f"Error loading BM25 index: {e}")

        return vector_store, bm25_index, docs


def run_indexer():
    indexer = TravelKnowledgeIndexer()
    v_store, bm25, docs = indexer.build_indexes()
    print(f"Indexing complete! Indexed {len(docs)} chunks into FAISS and BM25.")


if __name__ == "__main__":
    run_indexer()
