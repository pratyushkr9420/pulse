"""Structured logging configuration using structlog."""

import structlog


def setup_logging(debug: bool = False) -> None:
    """Configure structlog for the application.

    Args:
        debug: If True, use console renderer. If False, use JSON renderer.
    """
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if debug:
        # Console renderer for development (human-readable)
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        # JSON renderer for production (machine-parseable)
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structlog logger instance.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Configured structlog logger.
    """
    return structlog.get_logger(name)
