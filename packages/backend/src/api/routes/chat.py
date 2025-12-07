"""Chat routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_current_user
from src.db.session import get_db
from src.models.user import User
from src.schemas.chat import (
    ChatHistoryResponse,
    ChatMessageCreate,
    ChatMessageResponse,
)
from src.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])

# Supported tickers
SUPPORTED_TICKERS = ["AAPL", "MSFT", "AMZN", "NFLX", "NVDA", "INTC", "IBM"]


async def get_chat_service(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ChatService:
    """Get chat service dependency."""
    return ChatService(db)


@router.post("", response_model=ChatMessageResponse)
async def send_message(
    message_data: ChatMessageCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
) -> ChatMessageResponse:
    """Send a chat message and get AI response."""
    return await chat_service.send_message(
        user_id=current_user.id,
        message=message_data.message,
        ticker_filter=message_data.ticker_filter,
        retriever_type=message_data.retriever_type,
        use_advanced_rag=message_data.use_advanced_rag,
    )


@router.get("/history", response_model=ChatHistoryResponse)
async def get_history(
    current_user: Annotated[User, Depends(get_current_user)],
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ChatHistoryResponse:
    """Get chat history for current user."""
    return await chat_service.get_history(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )


# Tickers endpoint (separate router or same)
tickers_router = APIRouter(tags=["tickers"])


@tickers_router.get("/tickers", response_model=list[str])
async def get_tickers() -> list[str]:
    """Get list of supported ticker symbols."""
    return SUPPORTED_TICKERS
