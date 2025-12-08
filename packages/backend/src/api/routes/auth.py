"""Authentication routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.deps import get_auth_service, get_current_user
from src.core.exceptions import AuthenticationError, ValidationError
from src.models.user import User
from src.schemas.auth import TokenResponse, UserCreate
from src.schemas.user import UserResponse
from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    """Register a new user.

    Args:
        user_data: User registration data.
        auth_service: Auth service instance.

    Returns:
        Created user response.

    Raises:
        HTTPException: If validation fails.
    """
    try:
        return await auth_service.register(user_data)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """Login and get JWT token.

    Args:
        form_data: OAuth2 form with username and password.
        auth_service: Auth service instance.

    Returns:
        Token response with JWT.

    Raises:
        HTTPException: If authentication fails.
    """
    try:
        return await auth_service.login(form_data.username, form_data.password)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Get current user info.

    Args:
        current_user: Current authenticated user.

    Returns:
        User response.
    """
    return UserResponse.model_validate(current_user)
