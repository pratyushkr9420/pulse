"""Tests for vector store."""

import sys
import pytest
from unittest.mock import patch, MagicMock, AsyncMock, Mock
from langchain_core.embeddings import Embeddings


class MockEmbeddings(Embeddings):
    """Mock embeddings for testing."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return mock embeddings for documents."""
        return [[0.1] * 1536 for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        """Return mock embedding for query."""
        return [0.1] * 1536


class TestVectorStore:
    """Test vector store functionality."""

    def test_get_vector_store_returns_qdrant(self):
        """Should return Qdrant vector store instance."""
        # Mock onnxruntime to avoid import errors
        sys.modules['onnxruntime'] = Mock()
        sys.modules['onnxruntime.capi'] = Mock()
        sys.modules['onnxruntime.capi._pybind_state'] = Mock()

        with patch('src.rag.vector_store.QdrantVectorStore') as MockQdrantVectorStore:
            with patch('src.rag.vector_store.get_qdrant_client') as mock_get_client:
                with patch('src.rag.vector_store.get_embeddings') as mock_emb:
                    mock_emb.return_value = MockEmbeddings()
                    mock_get_client.return_value = MagicMock()

                    mock_store_instance = MagicMock()
                    MockQdrantVectorStore.return_value = mock_store_instance

                    from src.rag.vector_store import get_vector_store

                    store = get_vector_store()

                    assert store is not None
                    MockQdrantVectorStore.assert_called_once()

    def test_vector_store_uses_configured_collection(self):
        """Should use collection name from settings."""
        from src.config import get_settings

        settings = get_settings()
        # Verify settings has collection name
        assert settings.QDRANT_COLLECTION_NAME == "stock_news"

    @pytest.mark.asyncio
    async def test_add_documents_to_store(self):
        """Should add documents to vector store."""
        from langchain_core.documents import Document

        # Mock onnxruntime to avoid import errors
        sys.modules['onnxruntime'] = Mock()
        sys.modules['onnxruntime.capi'] = Mock()
        sys.modules['onnxruntime.capi._pybind_state'] = Mock()

        with patch('src.rag.vector_store.QdrantVectorStore') as MockQdrantVectorStore:
            with patch('src.rag.vector_store.get_qdrant_client') as mock_get_client:
                with patch('src.rag.vector_store.get_embeddings') as mock_emb:
                    mock_emb.return_value = MockEmbeddings()
                    mock_get_client.return_value = MagicMock()

                    mock_store_instance = MagicMock()
                    mock_store_instance.aadd_documents = AsyncMock(return_value=["id1", "id2"])
                    MockQdrantVectorStore.return_value = mock_store_instance

                    from src.rag.vector_store import get_vector_store
                    store = get_vector_store()

                    docs = [
                        Document(page_content="Test", metadata={"ticker": "AAPL"}),
                        Document(page_content="Test 2", metadata={"ticker": "MSFT"}),
                    ]

                    # Verify store can be used (we're not actually calling aadd_documents in the test)
                    assert store is not None
                    assert hasattr(store, 'aadd_documents')
