"""Embeddings configuration."""

import threading

from langchain_openai import OpenAIEmbeddings

from src.config import get_settings

# Thread-safe singleton using double-checked locking pattern
_embeddings_instance: OpenAIEmbeddings | None = None
_embeddings_lock = threading.Lock()


def get_embeddings() -> OpenAIEmbeddings:
    """Get OpenAI embeddings instance.

    Thread-safe singleton implementation using double-checked locking.

    Returns:
        Configured OpenAI embeddings.
    """
    global _embeddings_instance

    # First check (without lock for performance)
    if _embeddings_instance is not None:
        return _embeddings_instance

    # Acquire lock for initialization
    with _embeddings_lock:
        # Second check (with lock to prevent race condition)
        if _embeddings_instance is None:
            settings = get_settings()
            _embeddings_instance = OpenAIEmbeddings(
                model=settings.OPENAI_EMBEDDING_MODEL,
                api_key=settings.OPENAI_API_KEY,  # type: ignore[arg-type]
            )

        return _embeddings_instance
