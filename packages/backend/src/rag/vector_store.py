"""Vector store configuration using Qdrant."""

import threading

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from src.config import get_settings
from src.rag.embeddings import get_embeddings

# Thread-safe singletons using double-checked locking pattern
_qdrant_client_instance: QdrantClient | None = None
_qdrant_client_lock = threading.Lock()

_vector_store_instance: QdrantVectorStore | None = None
_vector_store_lock = threading.Lock()


def get_qdrant_client() -> QdrantClient:
    """Get Qdrant client instance.

    Thread-safe singleton implementation using double-checked locking.

    Returns:
        Configured Qdrant client.
    """
    global _qdrant_client_instance

    # First check (without lock for performance)
    if _qdrant_client_instance is not None:
        return _qdrant_client_instance

    # Acquire lock for initialization
    with _qdrant_client_lock:
        # Second check (with lock to prevent race condition)
        if _qdrant_client_instance is None:
            settings = get_settings()
            _qdrant_client_instance = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT,
            )

        return _qdrant_client_instance


def get_vector_store() -> QdrantVectorStore:
    """Get Qdrant vector store instance.

    Thread-safe singleton implementation using double-checked locking.

    Returns:
        Configured Qdrant vector store.
    """
    global _vector_store_instance

    # First check (without lock for performance)
    if _vector_store_instance is not None:
        return _vector_store_instance

    # Acquire lock for initialization
    with _vector_store_lock:
        # Second check (with lock to prevent race condition)
        if _vector_store_instance is None:
            settings = get_settings()
            client = get_qdrant_client()
            embeddings = get_embeddings()

            _vector_store_instance = QdrantVectorStore(
                client=client,
                collection_name=settings.QDRANT_COLLECTION_NAME,
                embedding=embeddings,
            )

        return _vector_store_instance


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
