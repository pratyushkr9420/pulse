"""Security utilities for password hashing and JWT tokens."""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from src.config import get_settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt.

    Args:
        password: Plain text password to hash.

    Returns:
        Bcrypt hashed password.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash.

    Args:
        plain_password: Plain text password to verify.
        hashed_password: Bcrypt hash to verify against.

    Returns:
        True if password matches, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token.

    Args:
        data: Data to encode in the token.
        expires_delta: Optional custom expiration time.

    Returns:
        Encoded JWT token.
    """
    settings = get_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """Decode a JWT access token.

    Args:
        token: JWT token to decode.

    Returns:
        Decoded payload dict or None if invalid/expired.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
