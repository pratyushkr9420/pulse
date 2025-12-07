"""Tests for configuration module."""

import pytest
from pydantic import ValidationError


class TestSettings:
    """Test Settings configuration."""

    def test_settings_loads_from_env(self, monkeypatch):
        """Settings should load from environment variables."""
        monkeypatch.setenv("APP_NAME", "Test App")
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")

        from src.config import Settings
        settings = Settings()

        assert settings.APP_NAME == "Test App"
        assert "postgresql" in settings.DATABASE_URL
        assert settings.JWT_ALGORITHM == "HS256"

    def test_settings_validates_required_fields(self, monkeypatch):
        """Settings should fail if required fields missing."""
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        from src.config import Settings

        with pytest.raises(ValidationError):
            Settings(_env_file=None)

    def test_cors_origins_parsed_correctly(self, monkeypatch):
        """CORS origins should be parsed as list."""
        monkeypatch.setenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")

        from src.config import Settings
        settings = Settings()

        assert len(settings.cors_origins_list) == 2
        assert "http://localhost:3000" in settings.cors_origins_list
