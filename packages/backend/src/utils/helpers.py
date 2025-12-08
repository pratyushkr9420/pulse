"""Helper utility functions."""

import html
import re
from datetime import UTC, datetime
from uuid import UUID, uuid4

# Supported tickers for validation
SUPPORTED_TICKERS = {'AAPL', 'MSFT', 'AMZN', 'NFLX', 'NVDA', 'INTC', 'IBM'}


def generate_uuid() -> UUID:
    """Generate a new UUID."""
    return uuid4()


def format_timestamp(dt: datetime | None = None) -> str:
    """Format a datetime to ISO 8601 string.

    Args:
        dt: Datetime to format. If None, uses current UTC time.

    Returns:
        ISO 8601 formatted string with Z suffix.
    """
    if dt is None:
        dt = datetime.now(UTC)
    return dt.isoformat().replace('+00:00', '') + "Z"


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to a maximum length.

    Args:
        text: Text to truncate.
        max_length: Maximum length including suffix.
        suffix: String to append when truncating.

    Returns:
        Truncated text.
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def sanitize_input(text: str) -> str:
    """Sanitize user input by removing dangerous characters and HTML.

    This function:
    1. Removes HTML tags
    2. Escapes remaining HTML entities
    3. Removes control characters
    4. Normalizes whitespace

    Args:
        text: User input text.

    Returns:
        Sanitized text.
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Escape remaining HTML entities for safety
    text = html.unescape(text)
    # Remove control characters (except newlines and tabs which we'll normalize)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    # Normalize whitespace (convert all whitespace to single spaces)
    text = ' '.join(text.split())
    return text.strip()


def is_valid_ticker(ticker: str) -> bool:
    """Check if a ticker symbol is valid (in supported list).

    Args:
        ticker: Ticker symbol to validate.

    Returns:
        True if valid, False otherwise.
    """
    return ticker.upper() in SUPPORTED_TICKERS


def extract_tickers_from_query(query: str) -> list[str]:
    """Extract ticker symbols from a user query.

    Only returns tickers that are in the supported list.

    Args:
        query: User query string.

    Returns:
        List of found supported ticker symbols.
    """
    # Find all uppercase words that could be tickers (2-5 characters)
    words = re.findall(r'\b[A-Z]{2,5}\b', query.upper())
    # Filter to only supported tickers
    return [w for w in words if w in SUPPORTED_TICKERS]
