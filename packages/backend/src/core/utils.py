"""Utility helper functions."""

from datetime import datetime, timezone

import bleach


def sanitize_html(text: str) -> str:
    """Remove HTML tags from text to prevent XSS attacks.

    Args:
        text: Input text that may contain HTML.

    Returns:
        Sanitized text with HTML tags removed.
    """
    return bleach.clean(text, tags=[], strip=True)


def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO 8601 string in UTC.

    Args:
        dt: Datetime object to format.

    Returns:
        ISO 8601 formatted string with 'Z' suffix (UTC).
    """
    # Convert to UTC if not already
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    # Format as ISO 8601 with Z suffix
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
