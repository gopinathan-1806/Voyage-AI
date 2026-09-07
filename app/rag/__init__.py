"""
RAG package initialization.
"""

from app.rag.embeddings import get_embedding_model, DeterministicHashEmbeddings
from app.rag.indexer import TravelKnowledgeIndexer
from app.rag.hybrid_retriever import HybridTravelRetriever, ScoredDocument
from app.rag.retrieval_quality import compute_lexical_overlap
from app.rag.query_rewriter import TravelQueryRewriter
from app.rag.source_formatter import format_context_for_llm, extract_unique_sources
from app.rag.prompts import VOYAGEAI_SYSTEM_PROMPT, CLARIFICATION_PROMPT, FALLBACK_NO_EVIDENCE_PROMPT

__all__ = [
    "get_embedding_model",
    "DeterministicHashEmbeddings",
    "TravelKnowledgeIndexer",
    "HybridTravelRetriever",
    "ScoredDocument",
    "compute_lexical_overlap",
    "TravelQueryRewriter",
    "format_context_for_llm",
    "extract_unique_sources",
    "VOYAGEAI_SYSTEM_PROMPT",
    "CLARIFICATION_PROMPT",
    "FALLBACK_NO_EVIDENCE_PROMPT",
]
