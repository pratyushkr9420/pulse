"""Application configuration using Pydantic Settings.

Environment Variable Categories:
- REQUIRED: Must be set (no default) - app won't start without these
- OPTIONAL: Have sensible defaults - can be omitted
- OPTIONAL-FEATURE: Only needed if using specific features (Sentry, LangSmith)
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # =========================================================================
    # CORE APPLICATION [OPTIONAL - have defaults]
    # =========================================================================
    APP_NAME: str = "Pulse API"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # =========================================================================
    # API SERVER [OPTIONAL - have defaults]
    # =========================================================================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000"  # Comma-separated list

    # =========================================================================
    # DATABASE [REQUIRED - no default]
    # =========================================================================
    DATABASE_URL: str  # Must be set: postgresql+asyncpg://user:pass@host:port/db

    # =========================================================================
    # REDIS [OPTIONAL - has default]
    # Used for caching and rate limiting. App works without it but some
    # features will be disabled.
    # =========================================================================
    REDIS_URL: str = "redis://localhost:6379/0"

    # =========================================================================
    # QDRANT VECTOR DATABASE [OPTIONAL - have defaults]
    # =========================================================================
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "stock_news"

    # =========================================================================
    # OPENAI [REQUIRED - API key has no default]
    # =========================================================================
    OPENAI_API_KEY: str  # Must be set: sk-...
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # =========================================================================
    # JWT AUTHENTICATION [REQUIRED - secret has no default]
    # =========================================================================
    JWT_SECRET_KEY: str  # Must be set: generate with `openssl rand -hex 32`
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # =========================================================================
    # OBSERVABILITY [OPTIONAL-FEATURE]
    # These features are disabled when their keys are empty strings.
    # =========================================================================

    # Sentry Error Tracking - leave empty to disable
    SENTRY_DSN: str = ""

    # LangSmith LLM Tracing - leave empty to disable
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = "pulse"

    # Note: Prometheus metrics are always enabled at /metrics endpoint
    # No configuration needed - uses prometheus-fastapi-instrumentator

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins as list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def sentry_enabled(self) -> bool:
        """Check if Sentry is configured."""
        return bool(self.SENTRY_DSN)

    @property
    def langsmith_enabled(self) -> bool:
        """Check if LangSmith is configured."""
        return bool(self.LANGSMITH_API_KEY)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Singleton Settings instance.
    """
    return Settings()  # type: ignore[call-arg]
