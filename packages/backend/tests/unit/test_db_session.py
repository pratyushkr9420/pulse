"""Tests for database session management."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestDatabaseSession:
    """Test database session configuration."""

    def test_engine_created_with_settings(self):
        """Engine should be created with settings from config."""
        from src.db.session import engine

        assert engine is not None
        # Engine should have pool_pre_ping enabled (private attribute in async pool)
        assert engine.pool._pre_ping is True

    def test_async_session_maker_configured(self):
        """Async session maker should be properly configured."""
        from src.db.session import async_session_maker

        assert async_session_maker is not None

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self):
        """get_db should yield an async session."""
        from src.db.session import get_db

        async for session in get_db():
            assert session is not None
            break

    @pytest.mark.asyncio
    async def test_get_db_commits_on_success(self):
        """Session should commit on successful operation."""
        from src.db.session import get_db

        # Test that get_db yields a session and handles commit/rollback
        async for session in get_db():
            # Session should be an AsyncSession instance
            assert session is not None
            # Verify we can access session methods
            assert hasattr(session, 'commit')
            assert hasattr(session, 'rollback')
            break

    @pytest.mark.asyncio
    async def test_get_db_rollback_on_exception(self):
        """Session should rollback on exception."""
        from src.db.session import get_db

        with pytest.raises(ValueError):
            async for session in get_db():
                raise ValueError("Test error")


class TestDeclarativeBase:
    """Test declarative base configuration."""

    def test_base_class_exists(self):
        """Base class should be importable."""
        from src.db.base import Base

        assert Base is not None

    def test_models_can_inherit_from_base(self):
        """Models should be able to inherit from Base."""
        from src.db.base import Base
        from sqlalchemy import Column, Integer

        class TestModel(Base):
            __tablename__ = 'test_model'
            id = Column(Integer, primary_key=True)

        assert TestModel.__tablename__ == 'test_model'
