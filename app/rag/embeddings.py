"""
Embeddings wrapper for VoyageAI supporting OpenAI embeddings and a deterministic local fallback
for testing, offline evaluation, and CI pipelines without API keys.
"""

import hashlib
import numpy as np
from typing import List, Optional
from langchain_core.embeddings import Embeddings
from app.config import config
from app.logging_config import get_logger

logger = get_logger(__name__)


class DeterministicHashEmbeddings(Embeddings):
    """
    Lightweight deterministic embedding generator producing normalized dense vectors.
    Useful for offline development, local unit testing, and CI/CD environments.
    """
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    def _embed_string(self, text: str) -> List[float]:
        # Hash text into fixed dimension vector
        vec = np.zeros(self.dimension, dtype=np.float32)
        words = text.lower().split()
        if not words:
            return vec.tolist()
            
        for i, word in enumerate(words):
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            val = ((h % 1000) / 500.0) - 1.0  # -1 to 1
            vec[idx] += val * (1.0 / (i + 1)**0.5)
            
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_string(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_string(text)


def get_embedding_model(prefer_openai: bool = True) -> Embeddings:
    """
    Factory to retrieve OpenAI embeddings if API key is present, otherwise fallback gracefully.
    """
    if prefer_openai and config.openai_api_key and config.openai_api_key != "your-openai-api-key-here":
        try:
            from langchain_openai import OpenAIEmbeddings
            logger.info(f"Initializing OpenAIEmbeddings with model: {config.openai_embedding_model}")
            return OpenAIEmbeddings(
                model=config.openai_embedding_model,
                api_key=config.openai_api_key
            )
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAIEmbeddings: {e}. Falling back to deterministic embeddings.")
            
    logger.info("Using DeterministicHashEmbeddings (Local/Offline mode)")
    return DeterministicHashEmbeddings()
