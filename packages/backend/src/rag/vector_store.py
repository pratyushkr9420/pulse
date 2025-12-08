"""Vector store configuration using Qdrant."""

from functools import lru_cache

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from src.config import get_settings
from src.rag.embeddings import get_embeddings


@lru_cache
def get_qdrant_client() -> QdrantClient:
    """Get Qdrant client instance.

    Returns:
        Configured Qdrant client.
    """
    settings = get_settings()

    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
    )


@lru_cache
def get_vector_store() -> QdrantVectorStore:
    """Get Qdrant vector store instance.

    Returns:
        Configured Qdrant vector store.
    """
    settings = get_settings()
    client = get_qdrant_client()
    embeddings = get_embeddings()

    return QdrantVectorStore(
        client=client,
        collection_name=settings.QDRANT_COLLECTION_NAME,
        embedding=embeddings,
    )


async def initialize_collection() -> None:
    """Initialize Qdrant collection if it doesn't exist."""
    from qdrant_client.models import Distance, VectorParams

    settings = get_settings()
    client = get_qdrant_client()

    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]

    if settings.QDRANT_COLLECTION_NAME not in collection_names:
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION_NAME,
            vectors_config=VectorParams(
                size=1536,  # OpenAI embedding dimension
                distance=Distance.COSINE,
            ),
        )
