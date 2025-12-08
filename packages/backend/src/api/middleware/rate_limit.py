"""Rate limiting middleware using SlowAPI.

Per .cursorrules specification for middleware modularity.
"""


from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


def get_rate_limiter() -> Limiter:
    """Create and configure rate limiter.

    Returns:
        Configured Limiter instance.
    """
    return Limiter(
        key_func=get_remote_address,
        default_limits=["100/minute"],
        storage_uri="memory://",  # Use Redis in production via REDIS_URL env var
    )


def setup_rate_limiting(app: FastAPI) -> None:
    """Configure rate limiting for the application.

    Args:
        app: FastAPI application instance.
    """
    limiter = get_rate_limiter()

    # Add rate limiter to app state
    app.state.limiter = limiter

    # Add exception handler for rate limit exceeded
    # Type ignore needed due to SlowAPI's exception handler signature
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
