"""Database initialization utilities for testing."""

from sqlalchemy.ext.asyncio import AsyncEngine

from src.db.base import Base
from src.db.session import engine as default_engine


async def init_db(engine: AsyncEngine | None = None) -> None:
    """Initialize database by creating all tables.

    Args:
        engine: Optional async engine. Uses default if not provided.
    """
    if engine is None:
        engine = default_engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db(engine: AsyncEngine | None = None) -> None:
    """Drop all database tables.

    Args:
        engine: Optional async engine. Uses default if not provided.
    """
    if engine is None:
        engine = default_engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
