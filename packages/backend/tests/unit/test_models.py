"""Tests for database models."""

import pytest
import uuid
from datetime import datetime


class TestUserModel:
    """Test User model."""

    def test_user_has_required_fields(self):
        """User model should have required fields."""
        from src.models.user import User

        # Check class has required attributes
        assert hasattr(User, "id")
        assert hasattr(User, "username")
        assert hasattr(User, "hashed_password")
        assert hasattr(User, "created_at")


class TestChatHistoryModel:
    """Test ChatHistory model."""

    def test_chat_history_has_required_fields(self):
        """ChatHistory model should have required fields."""
        from src.models.chat import ChatHistory

        assert hasattr(ChatHistory, "id")
        assert hasattr(ChatHistory, "user_id")
        assert hasattr(ChatHistory, "message")
        assert hasattr(ChatHistory, "response")
        assert hasattr(ChatHistory, "sources")
        assert hasattr(ChatHistory, "metadata_")
        assert hasattr(ChatHistory, "created_at")

    def test_chat_history_sources_is_json(self):
        """ChatHistory sources field should support JSON."""
        from src.models.chat import ChatHistory
        import uuid

        # Create instance to verify JSON field works
        chat = ChatHistory(
            user_id=uuid.uuid4(),
            message="Test message",
            response="Test response",
            sources=[{"ticker": "AAPL", "title": "Test"}],
        )

        assert isinstance(chat.sources, list)
        assert chat.sources[0]["ticker"] == "AAPL"
