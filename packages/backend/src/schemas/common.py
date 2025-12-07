"""Common response schemas."""

from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str
