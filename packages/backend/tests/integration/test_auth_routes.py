"""Integration tests for auth routes."""

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

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


class TestAuthRoutes:
    """Test authentication routes."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Should register new user successfully."""
        response = await client.post(
            "/api/v1/auth/register",
            json={"username": "testuser", "password": "password123"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient):
        """Should reject duplicate username."""
        # First registration
        await client.post(
            "/api/v1/auth/register",
            json={"username": "duplicate", "password": "password123"}
        )

        # Second registration with same username
        response = await client.post(
            "/api/v1/auth/register",
            json={"username": "duplicate", "password": "password456"}
        )

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """Should login and return JWT token."""
        # Register first
        await client.post(
            "/api/v1/auth/register",
            json={"username": "loginuser", "password": "password123"}
        )

        # Login
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "loginuser", "password": "password123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Should reject invalid credentials."""
        response = await client.post(
            "/api/v1/auth/login",
            data={"username": "nonexistent", "password": "wrongpassword"}
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me_authenticated(self, client: AsyncClient):
        """Should return current user info when authenticated."""
        # Register and login
        await client.post(
            "/api/v1/auth/register",
            json={"username": "meuser", "password": "password123"}
        )
        login_response = await client.post(
            "/api/v1/auth/login",
            data={"username": "meuser", "password": "password123"}
        )
        token = login_response.json()["access_token"]

        # Get current user
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "meuser"

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, client: AsyncClient):
        """Should reject unauthenticated request."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
