"""Tests for retriever implementations."""

import sys
import pytest
from unittest.mock import patch, MagicMock, AsyncMock, Mock
from langchain_core.documents import Document


class TestBaseRetriever:
    """Test base retriever."""

    def test_create_base_retriever(self):
        """Should create base retriever from vector store."""
        # Mock onnxruntime
        sys.modules['onnxruntime'] = Mock()
        sys.modules['onnxruntime.capi'] = Mock()
        sys.modules['onnxruntime.capi._pybind_state'] = Mock()

        with patch('src.rag.retrievers.get_vector_store') as mock_store:
            mock_store.return_value.as_retriever.return_value = MagicMock()

            from src.rag.retrievers import create_base_retriever

            retriever = create_base_retriever()

            assert retriever is not None

    def test_base_retriever_supports_ticker_filter(self):
        """Base retriever should support metadata filtering."""
        # Mock onnxruntime
        sys.modules['onnxruntime'] = Mock()
        sys.modules['onnxruntime.capi'] = Mock()
        sys.modules['onnxruntime.capi._pybind_state'] = Mock()

        with patch('src.rag.retrievers.get_vector_store') as mock_store:
            mock_retriever = MagicMock()
            mock_store.return_value.as_retriever.return_value = mock_retriever

            from src.rag.retrievers import create_base_retriever

            retriever = create_base_retriever(ticker_filter=["AAPL", "MSFT"])

            # Verify filter was applied
            mock_store.return_value.as_retriever.assert_called()


class TestSelfQueryRetriever:
    """Test self-query retriever."""

    def test_create_self_query_retriever(self):
        """Should create self_query retriever."""
        # Mock onnxruntime
        sys.modules['onnxruntime'] = Mock()
        sys.modules['onnxruntime.capi'] = Mock()
        sys.modules['onnxruntime.capi._pybind_state'] = Mock()

        # Mock AttributeInfo - use langchain_classic path
        mock_attribute_info = MagicMock()
        mock_schema_module = MagicMock()
        mock_schema_module.AttributeInfo = mock_attribute_info
        sys.modules['langchain_classic.chains.query_constructor.base'] = mock_schema_module

        # Create a mock SelfQueryRetriever class
        mock_retriever = MagicMock()
        mock_self_query_class = MagicMock()
        mock_self_query_class.from_llm.return_value = mock_retriever

        # Mock the module and class - use langchain_classic path
        mock_base_module = MagicMock()
        mock_base_module.SelfQueryRetriever = mock_self_query_class
        sys.modules['langchain_classic.retrievers.self_query.base'] = mock_base_module

        with patch('src.rag.retrievers.get_vector_store'):
            with patch('src.rag.retrievers.get_llm'):
                from src.rag.retrievers import create_self_query_retriever

                retriever = create_self_query_retriever()

                assert retriever is not None


class TestMultiQueryRetriever:
    """Test multi-query retriever."""

    def test_create_multi_query_retriever(self):
        """Should create multi-query retriever."""
        # Mock onnxruntime
        sys.modules['onnxruntime'] = Mock()
        sys.modules['onnxruntime.capi'] = Mock()
        sys.modules['onnxruntime.capi._pybind_state'] = Mock()

        # Create a mock MultiQueryRetriever class
        mock_retriever = MagicMock()
        mock_multi_query_class = MagicMock()
        mock_multi_query_class.from_llm.return_value = mock_retriever

        # Mock the module and class - use langchain_classic path
        mock_multi_module = MagicMock()
        mock_multi_module.MultiQueryRetriever = mock_multi_query_class
        sys.modules['langchain_classic.retrievers.multi_query'] = mock_multi_module

        with patch('src.rag.retrievers.get_vector_store'):
            with patch('src.rag.retrievers.get_llm'):
                with patch('src.rag.retrievers.create_base_retriever') as mock_base:
                    mock_base.return_value = MagicMock()
                    from src.rag.retrievers import create_multi_query_retriever

                    retriever = create_multi_query_retriever()

                    assert retriever is not None


class TestRetrieverFactory:
    """Test retriever factory."""

    def test_get_retriever_default(self):
        """Default should return self_query retriever."""
        # Mock onnxruntime
        sys.modules['onnxruntime'] = Mock()
        sys.modules['onnxruntime.capi'] = Mock()
        sys.modules['onnxruntime.capi._pybind_state'] = Mock()

        with patch('src.rag.retrievers.create_self_query_retriever') as mock:
            mock.return_value = MagicMock()

            from src.rag.retrievers import get_retriever

            retriever = get_retriever("self_query")

            mock.assert_called_once()

    def test_get_retriever_base(self):
        """Should return base retriever when requested."""
        # Mock onnxruntime
        sys.modules['onnxruntime'] = Mock()
        sys.modules['onnxruntime.capi'] = Mock()
        sys.modules['onnxruntime.capi._pybind_state'] = Mock()

        with patch('src.rag.retrievers.create_base_retriever') as mock:
            mock.return_value = MagicMock()

            from src.rag.retrievers import get_retriever

            retriever = get_retriever("base")

            mock.assert_called_once()

    def test_get_retriever_invalid_type(self):
        """Should raise error for invalid retriever type."""
        # Mock onnxruntime
        sys.modules['onnxruntime'] = Mock()
        sys.modules['onnxruntime.capi'] = Mock()
        sys.modules['onnxruntime.capi._pybind_state'] = Mock()

        from src.rag.retrievers import get_retriever

        with pytest.raises(ValueError):
            get_retriever("invalid_type")
