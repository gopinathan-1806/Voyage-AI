"""
VoyageAI Configuration Module.
Loads settings from environment variables with sensible defaults.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Base paths
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
else:
    load_dotenv()


@dataclass(frozen=True)
class AppConfig:
    """Application configuration parameters."""
    app_name: str = os.getenv("APP_NAME", "VoyageAI")
    app_env: str = os.getenv("APP_ENV", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # OpenAI
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # RAG parameters
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))
    
    # Retrieval & Hybrid Weights
    retrieval_top_k: int = int(os.getenv("RETRIEVAL_TOP_K", "6"))
    relevance_threshold: float = float(os.getenv("RELEVANCE_THRESHOLD", "0.35"))
    vector_weight: float = float(os.getenv("VECTOR_WEIGHT", "0.60"))
    bm25_weight: float = float(os.getenv("BM25_WEIGHT", "0.30"))
    lexical_weight: float = float(os.getenv("LEXICAL_WEIGHT", "0.10"))
    
    # Scraper & Ingestion
    scraper_timeout_ms: int = int(os.getenv("SCRAPER_TIMEOUT_MS", "30000"))
    scraper_delay_seconds: float = float(os.getenv("SCRAPER_DELAY_SECONDS", "2.0"))
    playwright_headless: bool = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
    
    # Paths
    data_dir: Path = ROOT_DIR / "data" / "travel"
    raw_data_dir: Path = ROOT_DIR / "data" / "travel" / "raw"
    processed_data_dir: Path = ROOT_DIR / "data" / "travel" / "processed"
    indexes_dir: Path = ROOT_DIR / "indexes"
    faiss_index_dir: Path = ROOT_DIR / "indexes" / "faiss_index"
    bm25_index_path: Path = ROOT_DIR / "indexes" / "bm25_index.pkl"
    metadata_index_path: Path = ROOT_DIR / "indexes" / "metadata.json"
    
    # Observability
    langchain_tracing_v2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    langchain_api_key: Optional[str] = os.getenv("LANGCHAIN_API_KEY")
    langchain_project: str = os.getenv("LANGCHAIN_PROJECT", "voyageai")


# Global singleton config
config = AppConfig()
