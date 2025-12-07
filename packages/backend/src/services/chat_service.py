"""Chat service for handling conversations.

CORRECTED: Properly stores metadata field in ChatHistory model.
The metadata field stores retriever_type, ticker_filter, and other request parameters.
"""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.chat import ChatHistory
from src.rag.chain import invoke_rag
from src.schemas.chat import (
    ChatHistoryResponse,
    ChatMessageResponse,
    RetrieverTypeEnum,
    SourceInfo,
)


class ChatService:
    """Service for chat operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def send_message(
        self,
        user_id: UUID,
        message: str,
        ticker_filter: list[str] | None = None,
        retriever_type: RetrieverTypeEnum = "self_query",
        use_advanced_rag: bool = False,
    ) -> ChatMessageResponse:
        """Process a chat message and return response with sources.

        Args:
            user_id: User's UUID.
            message: User's message.
            ticker_filter: Optional ticker filter.
            retriever_type: RAG retriever type to use.
            use_advanced_rag: Enable advanced RAG features.

        Returns:
            ChatMessageResponse with response and sources.
        """
        # If advanced RAG is enabled, use multi-query with compression
        if use_advanced_rag:
            retriever_type = "ensemble"

        # Invoke RAG pipeline
        result = await invoke_rag(
            question=message,
            retriever_type=retriever_type,
            ticker_filter=ticker_filter,
        )

        # Convert sources to dicts for JSON storage
        sources_dicts = [
            {
                "title": s.title,
                "ticker": s.ticker,
                "link": str(s.link),
                "snippet": s.snippet,
                "relevance_score": s.relevance_score,
            }
            for s in result["sources"]
        ]

        # CORRECTED: Build metadata dict with request parameters
        # This field stores additional context about how the response was generated
        metadata_dict = {
            "retriever_type": retriever_type,
            "ticker_filter": ticker_filter,
            "use_advanced_rag": use_advanced_rag,
        }

        # Create chat history record with CORRECTED metadata field
        chat_history = ChatHistory(
            user_id=user_id,
            message=message,
            response=result["response"],
            sources=sources_dicts,  # list[dict] as expected by model
            metadata_=metadata_dict,  # CORRECTED: Use metadata_ (Python attr) not metadata (reserved by SQLAlchemy)
        )

        self.db.add(chat_history)
        await self.db.commit()
        await self.db.refresh(chat_history)

        # Return response
        return ChatMessageResponse(
            id=chat_history.id,
            message=chat_history.message,
            response=chat_history.response,
            sources=[
                SourceInfo(
                    title=s["title"],
                    ticker=s["ticker"],
                    link=s["link"],
                    snippet=s["snippet"],
                    relevance_score=s["relevance_score"],
                )
                for s in sources_dicts
            ],
            created_at=chat_history.created_at,
        )

    async def get_history(
        self,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> ChatHistoryResponse:
        """Get paginated chat history for user.

        Args:
            user_id: User's UUID.
            limit: Maximum number of records.
            offset: Number of records to skip.

        Returns:
            Paginated chat history response.
        """
        # Get total count
        count_query = select(func.count(ChatHistory.id)).where(
            ChatHistory.user_id == user_id
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated records
        query = (
            select(ChatHistory)
            .where(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        records = result.scalars().all()

        # Convert to response models
        items = []
        for record in records:
            sources = [
                SourceInfo(
                    title=s["title"],
                    ticker=s["ticker"],
                    link=s["link"],
                    snippet=s["snippet"],
                    relevance_score=s["relevance_score"],
                )
                for s in record.sources
            ]
            items.append(
                ChatMessageResponse(
                    id=record.id,
                    message=record.message,
                    response=record.response,
                    sources=sources,
                    created_at=record.created_at,
                )
            )

        return ChatHistoryResponse(items=items, total=total)
