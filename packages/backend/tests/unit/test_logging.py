"""Tests for structured logging."""

import pytest


class TestLoggingSetup:
    """Test logging configuration."""

    def test_setup_logging_exists(self):
        """setup_logging function should exist."""
        from src.core.logging import setup_logging

        # Should not raise
        setup_logging(debug=True)

    def test_get_logger_returns_logger(self):
        """get_logger should return a logger instance."""
        from src.core.logging import get_logger

        logger = get_logger(__name__)

        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "warning")
        assert hasattr(logger, "debug")
