"""
LangSmith and Tracing Observability integration.
Completely optional: runs cleanly with zero dependencies when LangSmith is disabled.
"""

import os
from typing import Optional
from app.config import config
from app.logging_config import get_logger

logger = get_logger(__name__)


def setup_observability() -> bool:
    """
    Initialize LangSmith tracing if enabled in configuration.
    Guarantees no secrets are logged or exposed.
    """
    if config.langchain_tracing_v2 and config.langchain_api_key:
        try:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = config.langchain_api_key
            os.environ["LANGCHAIN_PROJECT"] = config.langchain_project
            logger.info(f"LangSmith tracing enabled for project: {config.langchain_project}")
            return True
        except Exception as e:
            logger.warning(f"Failed to enable LangSmith tracing: {e}")
            return False
            
    logger.info("LangSmith tracing is disabled (Local Execution Mode)")
    return False
