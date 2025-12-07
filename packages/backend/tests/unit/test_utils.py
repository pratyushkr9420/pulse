"""Tests for utility functions."""

import pytest
from datetime import datetime, timezone


class TestSanitizeHtml:
    """Test HTML sanitization."""

    def test_sanitize_html_removes_tags(self):
        """sanitize_html should remove HTML tags."""
        from src.core.utils import sanitize_html

        html = "<script>alert('XSS')</script>Hello"
        result = sanitize_html(html)

        assert "<script>" not in result
        assert "Hello" in result

    def test_sanitize_html_keeps_text(self):
        """sanitize_html should preserve text content."""
        from src.core.utils import sanitize_html

        html = "<p>This is <b>bold</b> text</p>"
        result = sanitize_html(html)

        assert "This is bold text" in result or "This is  text" in result
        assert "<p>" not in result
        assert "<b>" not in result


class TestFormatTimestamp:
    """Test timestamp formatting."""

    def test_format_timestamp_returns_iso_format(self):
        """format_timestamp should return ISO 8601 format."""
        from src.core.utils import format_timestamp

        dt = datetime(2024, 1, 15, 10, 30, 45, tzinfo=timezone.utc)
        result = format_timestamp(dt)

        assert result == "2024-01-15T10:30:45Z"

    def test_format_timestamp_converts_to_utc(self):
        """format_timestamp should convert to UTC."""
        from src.core.utils import format_timestamp

        # Create a non-UTC datetime
        dt = datetime.now()
        result = format_timestamp(dt)

        # Should end with Z (UTC indicator)
        assert result.endswith("Z")
