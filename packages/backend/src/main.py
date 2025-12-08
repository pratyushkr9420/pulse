"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.middleware.cors import setup_cors
from src.api.middleware.logging import LoggingMiddleware
from src.api.middleware.rate_limit import setup_rate_limiting
from src.api.routes import auth, health
from src.api.routes.chat import router as chat_router
from src.api.routes.chat import tickers_router
from src.config import get_settings
from src.core.exceptions import PulseException
from src.core.logging import get_logger, setup_logging

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.

    Args:
        app: FastAPI application instance.

    Yields:
        None
    """
    # Startup
    setup_logging(debug=settings.DEBUG)
    logger.info("Starting Pulse API", environment=settings.ENVIRONMENT)
    yield
    # Shutdown
    logger.info("Shutting down Pulse API")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

# Setup middleware (per .cursorrules - modular middleware files)
setup_cors(app)
app.add_middleware(LoggingMiddleware)
setup_rate_limiting(app)


# Exception handler
@app.exception_handler(PulseException)
async def pulse_exception_handler(
    request: Request,
    exc: PulseException,
) -> JSONResponse:
    """Handle custom Pulse exceptions.

    Args:
        request: HTTP request.
        exc: Pulse exception.

    Returns:
        JSON response with error details.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


# Include routers
app.include_router(health.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(tickers_router, prefix="/api/v1")
