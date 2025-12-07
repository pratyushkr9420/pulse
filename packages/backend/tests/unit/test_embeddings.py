"""Tests for embeddings module."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock


class TestEmbeddings:
    """Test embeddings functionality."""

    def test_get_embeddings_returns_openai_embeddings(self):
        """Should return OpenAI embeddings instance."""
        from src.rag.embeddings import get_embeddings

        embeddings = get_embeddings()

        assert embeddings is not None
        assert hasattr(embeddings, 'embed_documents')
        assert hasattr(embeddings, 'embed_query')

    def test_embeddings_uses_configured_model(self):
        """Should use model from settings."""
        from src.rag.embeddings import get_embeddings
        from src.config import get_settings

        settings = get_settings()
        embeddings = get_embeddings()

        assert embeddings.model == settings.OPENAI_EMBEDDING_MODEL

    @pytest.mark.asyncio
    async def test_embed_query_returns_vector(self):
        """embed_query should return embedding vector."""
        from src.rag.embeddings import get_embeddings

        with patch('langchain_openai.OpenAIEmbeddings.embed_query') as mock:
            mock.return_value = [0.1] * 1536

            embeddings = get_embeddings()
            result = embeddings.embed_query("test query")

            assert len(result) == 1536
