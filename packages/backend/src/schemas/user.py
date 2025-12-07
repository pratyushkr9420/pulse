"""User schemas - per .cursorrules all user schemas in dedicated file."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """Schema for user response."""

    id: UUID
    username: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Schema for updating user."""

    username: str | None = Field(
        None,
        min_length=3,
        max_length=50,
        description="New username (optional)",
    )


class UserProfile(BaseModel):
    """Schema for user profile."""

    id: UUID
    username: str
    created_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}
