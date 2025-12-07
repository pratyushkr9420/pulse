"""Chat history model."""

from typing import Any
from uuid import UUID
from sqlalchemy import Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.models.base import Base, UUIDMixin, TimestampMixin


class ChatHistory(Base, UUIDMixin, TimestampMixin):
    """Chat history model for storing conversations."""

    __tablename__ = "chat_history"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    response: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    # Sources is a list of dicts
    sources: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    # Optional metadata field for storing retriever_type, ticker_filter, etc.
    # Note: Using metadata_ to avoid conflict with SQLAlchemy's reserved metadata attribute
    metadata_: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",  # Column name in database
        JSON,
        nullable=True,
        default=None,
    )

    # Relationship to user
    user: Mapped["User"] = relationship(
        "User",
        back_populates="chat_history",
    )

    def __repr__(self) -> str:
        return f"<ChatHistory(id={self.id}, user_id={self.user_id})>"
