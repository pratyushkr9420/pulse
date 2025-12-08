"""LangSmith tracing configuration.

LangSmith is an OPTIONAL feature for LLM observability. It provides:
- Trace visualization for RAG pipeline execution
- LLM call monitoring and debugging
- Performance metrics and cost tracking

To enable: Set LANGSMITH_API_KEY environment variable.
To disable: Leave LANGSMITH_API_KEY empty or unset.

Get your API key at: https://smith.langchain.com
"""

import os

from src.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)


def setup_langsmith() -> None:
    """Configure LangSmith for LLM observability.

    Sets the required environment variables for LangChain to send traces
    to LangSmith. Only configures if LANGSMITH_API_KEY is set.

    Environment variables set when enabled:
    - LANGCHAIN_TRACING_V2: "true" - Enables tracing
    - LANGCHAIN_API_KEY: Your LangSmith API key
    - LANGCHAIN_PROJECT: Project name for organizing traces
    """
    settings = get_settings()

    if not settings.langsmith_enabled:
        logger.info("LangSmith disabled (LANGSMITH_API_KEY not configured)")
        return

    # Set environment variables for LangChain
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGSMITH_PROJECT

    logger.info(
        "LangSmith initialized",
        project=settings.LANGSMITH_PROJECT,
        tracing_enabled=True,
    )
