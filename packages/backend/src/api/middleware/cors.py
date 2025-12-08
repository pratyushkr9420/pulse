"""CORS middleware configuration.

Extracted from main.py for better modularity per .cursorrules specification.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware.

    Args:
        app: FastAPI application instance.
    """
    settings = get_settings()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
