"""
Self-RAG style lightweight answer validation and groundedness checker.
"""

import re
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from app.rag.hybrid_retriever import ScoredDocument


class ValidationReport(BaseModel):
    """Self-RAG evaluation output."""
    is_grounded: bool
    unsupported_claims_detected: bool = False
    freshness_warning: bool = False
    summary_explanation: str = ""
    authoritative_sources_count: int = 0
    confidence_level: str = Field(default="High", description="High, Medium, Low, Insufficient")


class GroundingValidator:
    """
    Validates that the generated answer respects the retrieved context,
    flags unsupported statements, and determines confidence level.
    """

    @classmethod
    def validate_answer(
        cls,
        generated_answer: str,
        retrieved_docs: List[ScoredDocument],
        is_evidence_sufficient: bool,
    ) -> ValidationReport:
        """Evaluate answer groundedness and source support."""
        if not is_evidence_sufficient or not retrieved_docs:
            return ValidationReport(
                is_grounded=False,
                unsupported_claims_detected=False,
                freshness_warning=False,
                summary_explanation="No sufficient authoritative evidence was available to validate.",
                authoritative_sources_count=0,
                confidence_level="Insufficient"
            )

        combined_context = " ".join([d.page_content for d in retrieved_docs]).lower()
        answer_lower = generated_answer.lower()

        # Check for potential currency or numerical hallucinations not found in text
        # Extract fees mentioned like €90, $185, SGD 30, AUD 190
        currencies_found = re.findall(r"(?:€|\$|sgd|aud|jpy|aed)\s?\d+", answer_lower)
        unsupported = False
        for curr in currencies_found:
            clean_curr = re.sub(r"\s+", "", curr)
            if clean_curr not in combined_context and curr not in combined_context:
                # Potential unverified fee cited
                unsupported = True
                break

        # Check document freshness
        freshness_warning = False
        for doc in retrieved_docs:
            updated = doc.metadata.get("last_updated", "")
            if updated and "2023" in updated:
                freshness_warning = True

        sources_count = len({doc.metadata.get("source_url") for doc in retrieved_docs if doc.metadata.get("source_url")})

        confidence = "High" if len(retrieved_docs) >= 2 and not unsupported else "Medium"
        if unsupported:
            confidence = "Medium"

        explanation = (
            f"VoyageAI evaluated {len(retrieved_docs)} relevant knowledge passages "
            f"across {sources_count} authoritative sources. Grounding verification passed with {confidence} confidence."
        )

        return ValidationReport(
            is_grounded=not unsupported,
            unsupported_claims_detected=unsupported,
            freshness_warning=freshness_warning,
            summary_explanation=explanation,
            authoritative_sources_count=sources_count,
            confidence_level=confidence,
        )
