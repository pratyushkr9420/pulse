"""Embeddings configuration."""

from functools import lru_cache

from langchain_openai import OpenAIEmbeddings

from src.config import get_settings


@lru_cache
def get_embeddings() -> OpenAIEmbeddings:
    """Get OpenAI embeddings instance.
    
    Returns:
        Configured OpenAI embeddings.
    """
    settings = get_settings()
    
    return OpenAIEmbeddings(
        model=settings.OPENAI_EMBEDDING_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
    )
