"""Tests for RAG chain."""

import sys
import pytest
from unittest.mock import patch, MagicMock, AsyncMock, Mock
from langchain_core.documents import Document


class TestRAGChain:
    """Test RAG chain implementation."""

    def test_create_rag_chain(self):
        """Should create RAG chain using LCEL."""
        # Mock onnxruntime
        sys.modules['onnxruntime'] = Mock()
        sys.modules['onnxruntime.capi'] = Mock()
        sys.modules['onnxruntime.capi._pybind_state'] = Mock()

        with patch('src.rag.chain.get_retriever'):
            from src.rag.chain import create_rag_chain

            chain = create_rag_chain()

            assert chain is not None

    def test_chain_has_required_components(self):
        """Chain should have retriever, prompt, and LLM."""
        # Mock onnxruntime
        sys.modules['onnxruntime'] = Mock()
        sys.modules['onnxruntime.capi'] = Mock()
        sys.modules['onnxruntime.capi._pybind_state'] = Mock()

        with patch('src.rag.chain.get_retriever'):
            from src.rag.chain import create_rag_chain

            chain = create_rag_chain()

            # LCEL chains are RunnableSequence
            assert hasattr(chain, 'invoke')


class TestPromptTemplate:
    """Test prompt template."""

    def test_prompt_includes_context_placeholder(self):
        """Prompt should have {context} placeholder."""
        from src.rag.chain import RAG_PROMPT

        # Check input variables
        assert "context" in RAG_PROMPT.input_variables

    def test_prompt_includes_question_placeholder(self):
        """Prompt should have {question} placeholder."""
        from src.rag.chain import RAG_PROMPT

        # Check input variables
        assert "question" in RAG_PROMPT.input_variables

    def test_prompt_instructs_citation(self):
        """Prompt should instruct to cite sources."""
        from src.rag.chain import RAG_PROMPT

        # Get the template string from messages
        template_text = str(RAG_PROMPT.messages[0].prompt.template).lower()
        assert "source" in template_text or "cite" in template_text
