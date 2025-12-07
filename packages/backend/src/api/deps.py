"""FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.security import decode_access_token
from src.db.session import get_db
from src.models.user import User
from src.services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> AuthService:
    """Get auth service dependency.

    Args:
        db: Database session.

    Returns:
        AuthService instance.
    """
    return AuthService(db)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """Get current authenticated user.

    Args:
        token: JWT token from Authorization header.
        auth_service: Auth service instance.

    Returns:
        Current authenticated user.

    Raises:
        HTTPException: If credentials are invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str | None = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = await auth_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception

    return user
