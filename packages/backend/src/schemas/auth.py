"""Authentication schemas."""

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    """Schema for user registration."""

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username (3-50 characters)",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (minimum 8 characters)",
    )


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""

    username: str | None = None
