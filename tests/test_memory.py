"""
Unit tests for Session Memory isolation.
"""

import pytest
from app.memory.session_memory import InMemorySessionStore
from app.rag.query_understanding import TripContext


def test_session_memory_isolation():
    session1 = InMemorySessionStore(session_id="user_1")
    session2 = InMemorySessionStore(session_id="user_2")

    session1.add_message("user", "Travelling to France")
    session1.update_trip_context(TripContext(destination_country="France"))

    session2.add_message("user", "Travelling to Japan")
    session2.update_trip_context(TripContext(destination_country="Japan"))

    assert len(session1.get_messages()) == 1
    assert session1.get_trip_context().destination_country == "France"

    assert len(session2.get_messages()) == 1
    assert session2.get_trip_context().destination_country == "Japan"

    session1.clear()
    assert len(session1.get_messages()) == 0
    assert len(session2.get_messages()) == 1
