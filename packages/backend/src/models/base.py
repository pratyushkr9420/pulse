"""Base model for SQLAlchemy models.

Per .cursorrules: models/base.py contains mixins and re-exports Base from db/base.py
"""

from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

# Import Base from db module (per .cursorrules structure)
from src.db.base import Base


class TimestampMixin:
    """Mixin for created_at timestamp."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class UUIDMixin:
    """Mixin for UUID primary key."""

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )


# Re-export Base for convenience
__all__ = ["Base", "TimestampMixin", "UUIDMixin"]
