"""Tests for services."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4

from pydantic import ValidationError

from src.schemas.auth import UserCreate


class TestAuthService:
    """Test AuthService."""

    @pytest.mark.asyncio
    async def test_register_creates_user(self):
        """Should create new user with hashed password."""
        from src.services.auth_service import AuthService
        from datetime import datetime

        mock_db = AsyncMock()
        # Create a mock execute result
        mock_execute_result = MagicMock()
        mock_execute_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_execute_result)

        # Mock refresh to set id and created_at
        async def mock_refresh(obj):
            obj.id = uuid4()
            obj.created_at = datetime.now()

        mock_db.refresh = mock_refresh

        service = AuthService(mock_db)

        # CORRECTED: Use UserCreate object instead of keyword arguments
        user_data = UserCreate(username="testuser", password="password123")
        result = await service.register(user_data)

        assert result.username == "testuser"
        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_duplicate_raises_error(self):
        """Should raise ValidationError for duplicate username."""
        from src.services.auth_service import AuthService
        from src.core.exceptions import ValidationError as PulseValidationError

        mock_db = AsyncMock()
        mock_db.execute.return_value.scalar_one_or_none.return_value = MagicMock()

        service = AuthService(mock_db)

        # CORRECTED: Use UserCreate object
        user_data = UserCreate(username="existing", password="password123")

        # CORRECTED: Expect PulseValidationError (custom exception), not Pydantic ValidationError
        with pytest.raises(PulseValidationError):
            await service.register(user_data)


class TestChatService:
    """Test ChatService."""

    @pytest.mark.asyncio
    async def test_send_message_saves_to_db(self):
        """Should save message and response to database."""
        with patch('src.services.chat_service.invoke_rag') as mock_rag:
            mock_rag.return_value = {
                "response": "Test response",
                "sources": [],
            }

            from src.services.chat_service import ChatService
            from datetime import datetime

            mock_db = AsyncMock()

            # Mock refresh to set id and created_at on the chat_history object
            async def mock_refresh(obj):
                obj.id = uuid4()
                obj.created_at = datetime.now()

            mock_db.refresh = mock_refresh
            service = ChatService(mock_db)

            result = await service.send_message(
                user_id=uuid4(),
                message="Test question",
            )

            assert result.response == "Test response"
            mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_includes_sources(self):
        """Should include sources in response."""
        from src.schemas.chat import SourceInfo
        from datetime import datetime

        mock_sources = [
            SourceInfo(
                title="Test Article",
                ticker="AAPL",
                link="https://example.com",
                snippet="Test snippet content",
                relevance_score=0.9,
            )
        ]

        with patch('src.services.chat_service.invoke_rag') as mock_rag:
            mock_rag.return_value = {
                "response": "Test response",
                "sources": mock_sources,
            }

            from src.services.chat_service import ChatService

            mock_db = AsyncMock()

            # Mock refresh to set id and created_at
            async def mock_refresh(obj):
                obj.id = uuid4()
                obj.created_at = datetime.now()

            mock_db.refresh = mock_refresh
            service = ChatService(mock_db)

            result = await service.send_message(
                user_id=uuid4(),
                message="Test question",
            )

            assert len(result.sources) == 1
            assert result.sources[0].ticker == "AAPL"

    @pytest.mark.asyncio
    async def test_send_message_stores_metadata(self):
        """Should store retriever_type and ticker_filter in metadata."""
        with patch('src.services.chat_service.invoke_rag') as mock_rag:
            mock_rag.return_value = {
                "response": "Test response",
                "sources": [],
            }

            from src.services.chat_service import ChatService
            from datetime import datetime

            mock_db = AsyncMock()

            # Mock refresh to set id and created_at
            async def mock_refresh(obj):
                obj.id = uuid4()
                obj.created_at = datetime.now()

            mock_db.refresh = mock_refresh
            service = ChatService(mock_db)

            result = await service.send_message(
                user_id=uuid4(),
                message="Test question",
                retriever_type="multi_query",
                ticker_filter=["AAPL", "MSFT"],
            )

            # Verify db.add was called with chat history containing metadata
            call_args = mock_db.add.call_args
            chat_history = call_args[0][0]
            assert chat_history.metadata_ is not None
            assert chat_history.metadata_["retriever_type"] == "multi_query"
            assert chat_history.metadata_["ticker_filter"] == ["AAPL", "MSFT"]

    @pytest.mark.asyncio
    async def test_get_history_returns_paginated(self):
        """Should return paginated chat history."""
        from src.services.chat_service import ChatService

        mock_db = AsyncMock()

        # Create mock execute results for count query
        mock_count_result = AsyncMock()
        mock_count_result.scalar = MagicMock(return_value=0)

        # Create mock execute results for records query
        mock_records_result = AsyncMock()
        mock_scalars = MagicMock()
        mock_scalars.all = MagicMock(return_value=[])
        mock_records_result.scalars = MagicMock(return_value=mock_scalars)

        # Set up execute to return appropriate results
        mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_records_result])

        service = ChatService(mock_db)

        result = await service.get_history(
            user_id=uuid4(),
            limit=10,
            offset=0,
        )

        assert result.total == 0
        assert result.items == []

    @pytest.mark.asyncio
    async def test_send_message_timeout_raises_http_exception(self):
        """Should raise HTTPException with 504 when RAG invocation times out."""
        import asyncio
        from fastapi import HTTPException

        with patch('src.services.chat_service.invoke_rag') as mock_rag:
            # Simulate slow RAG that exceeds timeout
            async def slow_rag(*args, **kwargs):
                await asyncio.sleep(35)  # Longer than 30s timeout
                return {"response": "...", "sources": []}

            mock_rag.side_effect = slow_rag

            from src.services.chat_service import ChatService

            mock_db = AsyncMock()
            service = ChatService(mock_db)

            with pytest.raises(HTTPException) as exc_info:
                await service.send_message(
                    user_id=uuid4(),
                    message="Test question",
                )

            assert exc_info.value.status_code == 504
            assert "timed out" in exc_info.value.detail.lower()
