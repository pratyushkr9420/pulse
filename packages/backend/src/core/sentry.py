"""Sentry error tracking configuration.

Sentry is an OPTIONAL feature. It is only enabled when SENTRY_DSN is set.
To enable: Set SENTRY_DSN environment variable with your Sentry project DSN.
To disable: Leave SENTRY_DSN empty or unset.
"""

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from src.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)


def init_sentry() -> None:
    """Initialize Sentry error tracking.

    Only initializes if SENTRY_DSN is configured.
    Safe to call even when Sentry is not configured.
    """
    settings = get_settings()

    if not settings.sentry_enabled:
        logger.info("Sentry disabled (SENTRY_DSN not configured)")
        return

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        # Capture 10% of transactions for performance monitoring
        traces_sample_rate=0.1,
        # Capture 10% of transactions for profiling
        profiles_sample_rate=0.1,
        # Send PII data (be careful in production)
        send_default_pii=settings.DEBUG,
    )

    logger.info(
        "Sentry initialized",
        environment=settings.ENVIRONMENT,
        dsn_configured=True,
    )
