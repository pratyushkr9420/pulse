"""Chat schemas."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

# Retriever types available for advanced RAG features
RetrieverTypeEnum = Literal[
    "self_query",
    "base",
    "multi_query",
    "contextual_compression",
    "hybrid",
    "ensemble",
]


class SourceInfo(BaseModel):
    """Source information for cited articles."""

    title: str = Field(..., description="Article headline")
    ticker: str = Field(..., description="Stock ticker symbol")
    link: HttpUrl = Field(..., description="URL to source article")
    snippet: str = Field(
        ...,
        max_length=500,
        description="Relevant excerpt from article",
    )
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity score (0.0-1.0)",
    )


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's message",
    )
    ticker_filter: list[str] | None = Field(
        default=None,
        description="Optional ticker filter (e.g., ['AAPL', 'MSFT'])",
    )
    retriever_type: RetrieverTypeEnum = Field(
        default="self_query",
        description="RAG retriever type: self_query (default), multi_query, contextual_compression, hybrid, ensemble",
    )
    use_advanced_rag: bool = Field(
        default=False,
        description="Enable advanced RAG features (multi-query + compression)",
    )


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""

    id: UUID
    message: str
    response: str
    sources: list[SourceInfo]
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    """Schema for paginated chat history."""

    items: list[ChatMessageResponse]
    total: int
