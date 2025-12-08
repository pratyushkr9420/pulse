"""Authentication service."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AuthenticationError, ValidationError
from src.core.security import create_access_token, hash_password, verify_password
from src.models.user import User
from src.schemas.auth import TokenResponse, UserCreate
from src.schemas.user import UserResponse


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        """Initialize auth service.

        Args:
            db: Database session.
        """
        self.db = db

    async def register(self, user_data: UserCreate) -> UserResponse:
        """Register a new user."""
        # Check if username exists
        query = select(User).where(User.username == user_data.username)
        result = await self.db.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValidationError("Username already exists")

        # Create new user
        user = User(
            username=user_data.username,
            hashed_password=hash_password(user_data.password),
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return UserResponse.model_validate(user)

    async def login(self, username: str, password: str) -> TokenResponse:
        """Authenticate user and return JWT token."""
        # Find user
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid username or password")

        # Create token
        access_token = create_access_token(data={"sub": user.username})

        return TokenResponse(access_token=access_token)

    async def get_user_by_username(self, username: str) -> User | None:
        """Get user by username."""
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
