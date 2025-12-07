"""Integration tests for database operations."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import async_session_maker
from src.db.init_db import init_db, drop_db
from src.models.user import User
from src.models.chat import ChatHistory
from src.core.security import hash_password


@pytest.fixture
async def db_session() -> AsyncSession:
    """Create a database session for testing."""
    await init_db()
    async with async_session_maker() as session:
        yield session
    await drop_db()


class TestDatabaseOperations:
    """Test database CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a user in database."""
        user = User(
            username="testuser",
            hashed_password=hash_password("password123"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.created_at is not None

    @pytest.mark.asyncio
    async def test_read_user(self, db_session: AsyncSession):
        """Test reading a user from database."""
        from sqlalchemy import select

        # Create user
        user = User(
            username="readtest",
            hashed_password=hash_password("password123"),
        )
        db_session.add(user)
        await db_session.commit()

        # Read user
        query = select(User).where(User.username == "readtest")
        result = await db_session.execute(query)
        found_user = result.scalar_one_or_none()

        assert found_user is not None
        assert found_user.username == "readtest"

    @pytest.mark.asyncio
    async def test_unique_username_constraint(self, db_session: AsyncSession):
        """Test that duplicate usernames are rejected."""
        from sqlalchemy.exc import IntegrityError

        user1 = User(
            username="duplicate",
            hashed_password=hash_password("password123"),
        )
        db_session.add(user1)
        await db_session.commit()

        user2 = User(
            username="duplicate",
            hashed_password=hash_password("password456"),
        )
        db_session.add(user2)

        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_create_chat_history(self, db_session: AsyncSession):
        """Test creating chat history."""
        # Create user first
        user = User(
            username="chatuser",
            hashed_password=hash_password("password123"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Create chat history
        chat = ChatHistory(
            user_id=user.id,
            message="Test message",
            response="Test response",
            sources=[{"title": "Test", "ticker": "AAPL", "link": "https://example.com", "snippet": "Test snippet"}],
        )
        db_session.add(chat)
        await db_session.commit()
        await db_session.refresh(chat)

        assert chat.id is not None
        assert chat.message == "Test message"
        assert chat.response == "Test response"
        assert len(chat.sources) == 1
        assert chat.sources[0]["ticker"] == "AAPL"

    @pytest.mark.asyncio
    async def test_user_chat_relationship(self, db_session: AsyncSession):
        """Test user to chat history relationship."""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        # Create user with chats
        user = User(
            username="relationuser",
            hashed_password=hash_password("password123"),
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        # Add multiple chats
        for i in range(3):
            chat = ChatHistory(
                user_id=user.id,
                message=f"Message {i}",
                response=f"Response {i}",
                sources=[],
            )
            db_session.add(chat)
        await db_session.commit()

        # Query user with chats
        query = select(User).where(User.id == user.id).options(selectinload(User.chat_history))
        result = await db_session.execute(query)
        found_user = result.scalar_one()

        assert len(found_user.chat_history) == 3
