"""Tests for database layer."""

import pytest


class TestDatabaseBase:
    """Test database base class."""

    def test_base_exists(self):
        """Base declarative class should exist."""
        from src.db.base import Base

        assert Base is not None


class TestDatabaseSession:
    """Test database session management."""

    def test_async_engine_exists(self):
        """Async engine should be created."""
        from src.db.session import engine

        assert engine is not None

    def test_async_session_maker_exists(self):
        """Async session maker should be created."""
        from src.db.session import async_session_maker

        assert async_session_maker is not None

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self):
        """get_db should yield an async session."""
        from src.db.session import get_db

        async for session in get_db():
            assert session is not None
            break  # Only test first yield
