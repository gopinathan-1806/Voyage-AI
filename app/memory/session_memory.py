"""
Conversational Session Memory Abstraction.
Stores message history, active TripContext, and retrieved sources per user session.
Designed for easy extension to Redis, PostgreSQL, or DynamoDB.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.rag.query_understanding import TripContext


class ChatMessage(BaseModel):
    """Single message in a conversational session."""
    role: str  # "user", "assistant", "system"
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseSessionMemory(ABC):
    """Abstract interface for session-isolated conversation state."""

    @abstractmethod
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Append a message to the session history."""
        pass

    @abstractmethod
    def get_messages(self) -> List[ChatMessage]:
        """Retrieve all messages for the current session."""
        pass

    @abstractmethod
    def get_trip_context(self) -> TripContext:
        """Get the active trip context."""
        pass

    @abstractmethod
    def update_trip_context(self, context: TripContext) -> None:
        """Update or merge trip context."""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Reset conversation session."""
        pass


class InMemorySessionStore(BaseSessionMemory):
    """
    Thread-safe in-memory session store for local/Streamlit sessions.
    Maintains isolation per session_id.
    """

    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id
        self.messages: List[ChatMessage] = []
        self.trip_context: TripContext = TripContext()

    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.messages.append(
            ChatMessage(role=role, content=content, metadata=metadata or {})
        )

    def get_messages(self) -> List[ChatMessage]:
        return list(self.messages)

    def get_trip_context(self) -> TripContext:
        return self.trip_context

    def update_trip_context(self, context: TripContext) -> None:
        self.trip_context = self.trip_context.merge_with(context)

    def clear(self) -> None:
        self.messages = []
        self.trip_context = TripContext()
