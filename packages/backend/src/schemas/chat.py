"""Chat schemas."""

import re
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator

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

    @field_validator('message')
    @classmethod
    def validate_no_prompt_injection(cls, v: str) -> str:
        """Detect and reject prompt injection attempts.

        This validator protects against system prompt override attacks by detecting
        common prompt injection patterns. It uses regex to identify suspicious phrases
        while allowing legitimate financial questions.

        Args:
            v: The message string to validate.

        Returns:
            The validated message string.

        Raises:
            ValueError: If the message contains prompt injection patterns.
        """
        # Define dangerous patterns that indicate prompt injection attempts
        # These patterns are designed to be specific enough to catch attacks
        # while avoiding false positives on legitimate financial questions
        dangerous_patterns = [
            # "Ignore X instructions" patterns
            r'ignore\s+(all\s+)?(previous|prior|above|earlier)\s+instructions?',

            # "Disregard X" patterns
            r'disregard\s+(everything|all|the)\s+(above|before|previous|earlier)',

            # "New/Different instructions" patterns
            r'(new|different)\s+instructions?\s*:',

            # "You are now X" patterns
            r'you\s+are\s+now\s+(a|an)\s+',

            # "Forget X" patterns (specific to avoid false positives)
            r'forget\s+(your|the)\s+(previous|earlier|above)\s+',

            # System role manipulation
            r'system\s*:',
            r'<\s*system\s*>',
        ]

        # Check each pattern against the message (case-insensitive)
        for pattern in dangerous_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(
                    "Your message contains patterns associated with prompt injection attacks. "
                    "Please rephrase your question about stock news and financial information."
                )

        return v


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
