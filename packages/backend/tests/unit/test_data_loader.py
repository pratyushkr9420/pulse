"""Tests for data loader."""

import pytest
from unittest.mock import patch, MagicMock
import json


class TestDataLoader:
    """Test data loading functionality."""

    def test_load_json_data_returns_documents(self):
        """Should load JSON and return LangChain documents."""
        from src.rag.data_loader import load_json_data

        # Create mock JSON data
        mock_data = [
            {
                "headline": "Apple Stock Rises",
                "content": "Apple stock increased...",
                "ticker": "AAPL",
                "source": "Reuters",
                "link": "https://example.com/1",
                "date": "2024-01-15"
            }
        ]

        with patch("builtins.open", MagicMock()):
            with patch("json.load", return_value=mock_data):
                docs = load_json_data("dummy.json")

        assert len(docs) == 1
        assert docs[0].page_content == "Apple stock increased..."
        assert docs[0].metadata["ticker"] == "AAPL"

    def test_document_has_required_metadata(self):
        """Documents should have headline, ticker, source, link, date."""
        from src.rag.data_loader import load_json_data

        mock_data = [
            {
                "headline": "Test Headline",
                "content": "Test content",
                "ticker": "MSFT",
                "source": "Bloomberg",
                "link": "https://example.com",
                "date": "2024-01-15"
            }
        ]

        with patch("builtins.open", MagicMock()):
            with patch("json.load", return_value=mock_data):
                docs = load_json_data("dummy.json")

        metadata = docs[0].metadata
        assert "headline" in metadata
        assert "ticker" in metadata
        assert "source" in metadata
        assert "link" in metadata
        assert "date" in metadata

    def test_filters_invalid_entries(self):
        """Should filter out entries missing required fields."""
        from src.rag.data_loader import load_json_data

        mock_data = [
            {"headline": "Valid", "content": "Content", "ticker": "AAPL",
             "source": "Source", "link": "https://x.com", "date": "2024-01-01"},
            {"headline": "Invalid"},  # Missing fields
            {"content": "No headline"},  # Missing headline
        ]

        with patch("builtins.open", MagicMock()):
            with patch("json.load", return_value=mock_data):
                docs = load_json_data("dummy.json")

        assert len(docs) == 1
