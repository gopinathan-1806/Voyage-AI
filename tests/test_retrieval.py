"""
Unit tests for Hybrid Retrieval (Vector + BM25 + Lexical) and Indexing.
"""

import pytest
from app.rag.hybrid_retriever import HybridTravelRetriever
from app.rag.query_rewriter import TravelQueryRewriter
from app.rag.retrieval_quality import compute_lexical_overlap


def test_lexical_overlap_calculation():
    q = "France tourist visa documents"
    doc = "This document covers France tourist visa requirements and documents checklist."
    overlap = compute_lexical_overlap(q, doc)
    assert overlap > 0.5

    doc_unrelated = "Completely different text without matching terms."
    overlap_zero = compute_lexical_overlap(q, doc_unrelated)
    assert overlap_zero == 0.0


def test_query_rewriter():
    raw_query = "What documents for Paris?"
    rewritten = TravelQueryRewriter.rewrite_query(raw_query)
    assert "France" in rewritten
    assert "documents checklist" in rewritten


def test_hybrid_retrieval_returns_relevant_documents():
    retriever = HybridTravelRetriever()
    results = retriever.retrieve("France tourist visa required documents", top_k=3)
    
    assert len(results) > 0
    top_doc = results[0]
    assert top_doc.combined_score > 0
    assert "France" in top_doc.metadata.get("destination_country", "")


def test_hybrid_retrieval_destination_filter():
    retriever = HybridTravelRetriever()
    results = retriever.retrieve("tourist visa", destination_filter="Germany", top_k=3)
    
    for r in results:
        dest = r.metadata.get("destination_country", "")
        assert dest.lower() in ["germany", "all"]
