"""
Application runtime manager for initializing singletons, caches, and indexes.
"""

from typing import Optional
from app.config import config
from app.chatbot import TravelImmigrationChatbot
from app.rag.hybrid_retriever import HybridTravelRetriever
from app.rag.indexer import TravelKnowledgeIndexer
from app.logging_config import get_logger

logger = get_logger(__name__)

_chatbot_instance: Optional[TravelImmigrationChatbot] = None


def get_chatbot() -> TravelImmigrationChatbot:
    """Get or create singleton TravelImmigrationChatbot instance."""
    global _chatbot_instance
    if _chatbot_instance is None:
        logger.info("Initializing global TravelImmigrationChatbot runtime...")
        retriever = HybridTravelRetriever()
        _chatbot_instance = TravelImmigrationChatbot()
    return _chatbot_instance
