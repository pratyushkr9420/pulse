"""End-to-end tests for complete user flow.

Uses the same fixture pattern as integration tests which work 100%.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch
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


@pytest.fixture
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


class TestFullUserFlow:
    """Test complete user journey."""

    @pytest.mark.asyncio
    async def test_register_login_chat_flow(self, client: AsyncClient):
        """Test: Register → Login → Send Message → Get History."""

        # 1. Register new user
        register_response = await client.post(
            "/api/v1/auth/register",
            json={"username": "e2euser", "password": "password123"}
        )
        assert register_response.status_code == 201
        user_data = register_response.json()
        assert user_data["username"] == "e2euser"

        # 2. Login
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": "e2euser", "password": "password123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Verify current user
        me_response = await client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["username"] == "e2euser"

        # 4. Send chat message (mocked RAG)
        with patch('src.services.chat_service.invoke_rag') as mock_rag:
            mock_rag.return_value = {
                "response": "Apple stock is performing well.",
                "sources": [],  # Empty sources to avoid AttributeError with mock
            }

            chat_response = await client.post(
                "/api/v1/chat",
                json={"message": "How is AAPL doing?"},
                headers=headers,
            )
            assert chat_response.status_code == 200
            chat_data = chat_response.json()
            assert "response" in chat_data
            assert chat_data["response"] == "Apple stock is performing well."
            assert "sources" in chat_data

        # 5. Get chat history
        history_response = await client.get(
            "/api/v1/chat/history",
            headers=headers,
        )
        assert history_response.status_code == 200
        history_data = history_response.json()
        assert history_data["total"] >= 1
        assert len(history_data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_unauthenticated_access_denied(self, client: AsyncClient):
        """Unauthenticated requests should be denied."""

        # Chat endpoint
        chat_response = await client.post(
            "/api/v1/chat",
            json={"message": "Test"}
        )
        assert chat_response.status_code == 401

        # History endpoint
        history_response = await client.get("/api/v1/chat/history")
        assert history_response.status_code == 401

        # Me endpoint
        me_response = await client.get("/api/v1/auth/me")
        assert me_response.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, client: AsyncClient):
        """Invalid tokens should be rejected."""
        headers = {"Authorization": "Bearer invalid.token.here"}

        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_ticker_filter_applied(self, client: AsyncClient):
        """Ticker filter should be passed to RAG."""
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"username": "filteruser", "password": "password123"}
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": "filteruser", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        with patch('src.services.chat_service.invoke_rag') as mock_rag:
            mock_rag.return_value = {"response": "Filtered response", "sources": []}

            response = await client.post(
                "/api/v1/chat",
                json={
                    "message": "Compare stocks",
                    "ticker_filter": ["AAPL", "MSFT"],
                },
                headers=headers,
            )

            assert response.status_code == 200

            # Verify filter was passed
            mock_rag.assert_called_once()
            call_kwargs = mock_rag.call_args[1]
            assert call_kwargs["ticker_filter"] == ["AAPL", "MSFT"]
