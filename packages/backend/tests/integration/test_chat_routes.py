"""Integration tests for chat routes.

ADDED: This file was identified as missing in the data mismatch analysis.
It covers authentication, message sending, ticker filtering, retriever types, and history.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.db.base import Base
from src.main import app


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    yield session_maker

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope="function")
async def client(test_db):
    """Create test client."""
    from src.db.session import get_db

    async def override_get_db():
        async with test_db() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def auth_headers(client: AsyncClient):
    """Get auth headers for authenticated requests."""
    # Use unique username per test to avoid conflicts
    username = f"chatuser_{uuid4().hex[:8]}"

    # Register user
    await client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": "password123"}
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": "password123"}
    )
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


class TestChatRoutes:
    """Test chat routes."""

    @pytest.mark.asyncio
    async def test_send_message_requires_auth(self, client: AsyncClient):
        """Should require authentication."""
        response = await client.post(
            "/api/v1/chat",
            json={"message": "What's the latest AAPL news?"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_send_message_success(self, client: AsyncClient, auth_headers: dict):
        """Should send message and get response."""
        with patch('src.services.chat_service.invoke_rag') as mock_rag:
            mock_rag.return_value = {
                "response": "Apple stock is up.",
                "sources": [],
            }

            response = await client.post(
                "/api/v1/chat",
                json={"message": "What's the latest AAPL news?"},
                headers=auth_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert "sources" in data
            assert "id" in data

    @pytest.mark.asyncio
    async def test_send_message_with_ticker_filter(self, client: AsyncClient, auth_headers: dict):
        """Should accept ticker filter parameter."""
        with patch('src.services.chat_service.invoke_rag') as mock_rag:
            mock_rag.return_value = {
                "response": "Filtered response.",
                "sources": [],
            }

            response = await client.post(
                "/api/v1/chat",
                json={
                    "message": "Compare these stocks",
                    "ticker_filter": ["AAPL", "MSFT"],
                },
                headers=auth_headers,
            )

            assert response.status_code == 200

            # Verify filter was passed to RAG
            mock_rag.assert_called_once()
            call_kwargs = mock_rag.call_args[1]
            assert call_kwargs["ticker_filter"] == ["AAPL", "MSFT"]

    @pytest.mark.asyncio
    async def test_send_message_with_retriever_type(self, client: AsyncClient, auth_headers: dict):
        """Should accept retriever_type parameter."""
        with patch('src.services.chat_service.invoke_rag') as mock_rag:
            mock_rag.return_value = {
                "response": "Multi-query response.",
                "sources": [],
            }

            response = await client.post(
                "/api/v1/chat",
                json={
                    "message": "Complex query",
                    "retriever_type": "multi_query",
                },
                headers=auth_headers,
            )

            assert response.status_code == 200

            # Verify retriever type was passed
            mock_rag.assert_called_once()
            call_kwargs = mock_rag.call_args[1]
            assert call_kwargs["retriever_type"] == "multi_query"

    @pytest.mark.asyncio
    async def test_get_history_requires_auth(self, client: AsyncClient):
        """Should require authentication for history."""
        response = await client.get("/api/v1/chat/history")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_history_success(self, client: AsyncClient, auth_headers: dict):
        """Should return chat history."""
        response = await client.get(
            "/api/v1/chat/history",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_get_history_pagination(self, client: AsyncClient, auth_headers: dict):
        """Should support pagination parameters."""
        response = await client.get(
            "/api/v1/chat/history",
            params={"limit": 5, "offset": 0},
            headers=auth_headers,
        )

        assert response.status_code == 200


class TestTickersRoute:
    """Test tickers endpoint."""

    @pytest.mark.asyncio
    async def test_get_tickers(self, client: AsyncClient):
        """Should return list of supported tickers."""
        response = await client.get("/api/v1/tickers")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "AAPL" in data
        assert "MSFT" in data
        assert len(data) == 7  # All 7 supported tickers
