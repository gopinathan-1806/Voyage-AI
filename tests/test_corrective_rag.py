"""
Unit tests for Corrective RAG, Grounding Validation, and Readiness Score.
"""

import pytest
from app.rag.corrective_rag import CorrectiveRAGEngine
from app.rag.grounding_checker import GroundingValidator
from app.rag.readiness_calculator import TravelReadinessCalculator
from app.rag.query_understanding import TripContext


def test_corrective_rag_sufficient_evidence():
    crag = CorrectiveRAGEngine()
    docs, eval_res = crag.retrieve_with_correction(
        query="France Schengen tourist visa documents",
        destination_country="France"
    )
    assert eval_res.is_sufficient is True
    assert len(docs) > 0
    assert eval_res.confidence_score > 0.3


def test_corrective_rag_insufficient_evidence():
    crag = CorrectiveRAGEngine()
    # Unseeded non-existent country
    docs, eval_res = crag.retrieve_with_correction(
        query="entry visa rules for Atlantis Wonderland",
        destination_country="Atlantis"
    )
    assert eval_res.is_sufficient is False
    assert eval_res.action_taken == "NO_EVIDENCE_FALLBACK"


def test_travel_readiness_calculator():
    ctx = TripContext(
        origin_country="India",
        destination_country="France",
        travel_purpose="Tourism",
        duration="10 days"
    )
    crag = CorrectiveRAGEngine()
    docs, _ = crag.retrieve_with_correction("France visa", destination_country="France")
    
    readiness = TravelReadinessCalculator.calculate(ctx, docs)
    assert readiness.overall_score >= 80
    assert readiness.status_label == "High Readiness"
    assert len(readiness.components) == 5
