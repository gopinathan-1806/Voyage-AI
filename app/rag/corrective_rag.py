"""
Corrective RAG (CRAG) Engine:
Evaluates retrieval relevance, triggers query transformation and secondary retrieval
when evidence is weak, and prevents hallucinations when no authoritative sources match.
"""

from typing import List, Tuple, Optional, Dict
from pydantic import BaseModel, Field

from app.config import config
from app.rag.hybrid_retriever import HybridTravelRetriever, ScoredDocument
from app.rag.source_formatter import extract_unique_sources
from app.logging_config import get_logger

logger = get_logger(__name__)


class RetrievalEvaluationResult(BaseModel):
    """Encapsulates the outcome of evaluating retrieved evidence."""
    is_sufficient: bool
    confidence_score: float = Field(default=0.0, description="Average relevance score of top documents")
    relevant_documents_count: int
    total_retrieved: int
    used_sources: List[dict] = Field(default_factory=list)
    action_taken: str = Field(default="DIRECT_GENERATION", description="DIRECT_GENERATION, CORRECTIVE_RETRY, or NO_EVIDENCE_FALLBACK")
    explanation: str = ""


class CorrectiveRAGEngine:
    """
    Implements corrective retrieval flow:
    1. Assess initial retrieval quality against configured threshold.
    2. If relevance is low, reformulate query with broader/alternate search terms.
    3. Perform secondary retrieval.
    4. Re-evaluate. If still insufficient, return explicit no-hallucination signal.
    """

    def __init__(self, retriever: Optional[HybridTravelRetriever] = None):
        self.retriever = retriever or HybridTravelRetriever()
        self.relevance_threshold = config.relevance_threshold

    def evaluate_retrieval(
        self,
        scored_docs: List[ScoredDocument],
        query: str,
        destination_country: Optional[str] = None
    ) -> Tuple[List[ScoredDocument], RetrievalEvaluationResult]:
        """
        Evaluate retrieved documents. Filter out sub-threshold documents.
        """
        if not scored_docs:
            return [], RetrievalEvaluationResult(
                is_sufficient=False,
                confidence_score=0.0,
                relevant_documents_count=0,
                total_retrieved=0,
                action_taken="NO_EVIDENCE_FALLBACK",
                explanation="No relevant documents found matching query."
            )

        # Filter by threshold
        valid_docs = [
            doc for doc in scored_docs 
            if doc.combined_score >= self.relevance_threshold
        ]

        avg_score = (
            sum(d.combined_score for d in valid_docs) / len(valid_docs)
            if valid_docs else 0.0
        )
        sources = extract_unique_sources(valid_docs)

        # Check destination alignment if known
        if destination_country and destination_country.lower() != "all":
            dest_matches = [
                d for d in valid_docs 
                if d.metadata.get("destination_country", "").lower() in [destination_country.lower(), "all"]
            ]
            if not dest_matches and valid_docs:
                logger.info(f"Retrieved documents do not match destination country: {destination_country}")
                valid_docs = []
                avg_score = 0.0

        is_sufficient = len(valid_docs) >= 1 and avg_score >= self.relevance_threshold

        explanation = (
            f"Found {len(scored_docs)} candidate chunks; {len(valid_docs)} passed "
            f"relevance threshold ({self.relevance_threshold:.2f}) with confidence {avg_score:.2f}."
        )

        result = RetrievalEvaluationResult(
            is_sufficient=is_sufficient,
            confidence_score=round(avg_score, 3),
            relevant_documents_count=len(valid_docs),
            total_retrieved=len(scored_docs),
            used_sources=sources,
            action_taken="DIRECT_GENERATION" if is_sufficient else "CORRECTIVE_RETRY",
            explanation=explanation
        )

        return valid_docs, result

    def retrieve_with_correction(
        self,
        query: str,
        destination_country: Optional[str] = None,
        context_metadata: Optional[Dict[str, str]] = None,
    ) -> Tuple[List[ScoredDocument], RetrievalEvaluationResult]:
        """
        Full corrective retrieval pipeline.
        """
        # Step 1: Initial Retrieval
        initial_docs = self.retriever.retrieve(
            query=query,
            destination_filter=destination_country,
            context_metadata=context_metadata
        )
        valid_docs, eval_result = self.evaluate_retrieval(
            initial_docs, query, destination_country
        )

        if eval_result.is_sufficient:
            return valid_docs, eval_result

        logger.info(f"Initial retrieval weak (eval: {eval_result.action_taken}). Initiating Corrective Retrieval...")

        # Step 2: Corrective Query Transformation
        fallback_query = query
        if destination_country:
            fallback_query = f"{destination_country} visa tourist entry requirements documents"
        else:
            fallback_query = f"{query} visa entry requirements travel"

        second_docs = self.retriever.retrieve(
            query=fallback_query,
            destination_filter=destination_country,
            context_metadata=context_metadata
        )
        second_valid_docs, second_eval = self.evaluate_retrieval(
            second_docs, fallback_query, destination_country
        )

        if second_eval.is_sufficient:
            second_eval.action_taken = "CORRECTIVE_RETRY_SUCCEEDED"
            second_eval.explanation = (
                f"Initial retrieval was insufficient. Corrective query reformulation succeeded with "
                f"{second_eval.relevant_documents_count} relevant chunks."
            )
            return second_valid_docs, second_eval

        # Step 3: Insufficient evidence fallback
        final_eval = RetrievalEvaluationResult(
            is_sufficient=False,
            confidence_score=second_eval.confidence_score,
            relevant_documents_count=0,
            total_retrieved=len(initial_docs) + len(second_docs),
            used_sources=[],
            action_taken="NO_EVIDENCE_FALLBACK",
            explanation="Insufficient authoritative knowledge found in current database even after corrective refinement."
        )
        return [], final_eval


# Backward compatibility alias
CorrectiveRAG = CorrectiveRAGEngine
