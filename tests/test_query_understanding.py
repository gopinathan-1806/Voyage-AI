"""
Unit tests for Query Understanding and structured TripContext extraction.
"""

import pytest
from app.rag.query_understanding import TravelQueryUnderstanding, TripContext


def test_extract_full_trip_context():
    query = "I am an Indian citizen travelling from India to France for 10 days in December for tourism."
    ctx = TravelQueryUnderstanding.extract_context(query)

    assert ctx.origin_country == "India"
    assert ctx.destination_country == "France"
    assert ctx.travel_purpose == "Tourism"
    assert ctx.duration == "10 days"
    assert ctx.travel_date == "December"
    assert ctx.question_type == "visa_requirements"


def test_extract_germany_documents_query():
    query = "What documents do I need for a Germany tourist visa?"
    ctx = TravelQueryUnderstanding.extract_context(query)

    assert ctx.destination_country == "Germany"
    assert ctx.travel_purpose == "Tourism"
    assert ctx.question_type == "documents"


def test_extract_uk_fee_query():
    query = "How much does a UK standard visitor visa cost?"
    ctx = TravelQueryUnderstanding.extract_context(query)

    assert ctx.destination_country == "United Kingdom"
    assert ctx.question_type == "fees"


def test_context_merging_on_followups():
    # First turn
    turn1 = "I am travelling to France for tourism"
    ctx1 = TravelQueryUnderstanding.extract_context(turn1)
    assert ctx1.destination_country == "France"
    assert ctx1.duration is None

    # Second turn (user gives duration)
    turn2 = "I will stay for 2 weeks"
    ctx2 = TravelQueryUnderstanding.extract_context(turn2, existing_context=ctx1)
    assert ctx2.destination_country == "France"
    assert ctx2.duration == "2 weeks"
    assert ctx2.travel_purpose == "Tourism"
