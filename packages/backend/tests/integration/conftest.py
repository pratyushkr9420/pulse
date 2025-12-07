"""Integration test configuration."""

import pytest


@pytest.fixture(scope="function", autouse=True)
async def cleanup_db_connections():
    """Ensure database connections are cleaned up between tests."""
    yield
    # Clean up database connections after each test
    from src.db.session import engine
    await engine.dispose()
