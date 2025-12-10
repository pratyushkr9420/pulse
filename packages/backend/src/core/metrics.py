"""Prometheus metrics configuration.

Prometheus metrics can be enabled/disabled via ENABLE_METRICS environment variable.
Metrics are exposed at the /metrics endpoint when enabled.

Features provided by prometheus-fastapi-instrumentator:
- HTTP request duration histograms
- HTTP request counts by status code
- In-progress request gauges
- Request/response size histograms

To enable metrics, set in .env:
  ENABLE_METRICS=true

To scrape metrics, configure your Prometheus server to scrape:
  http://your-backend-host:8000/metrics
"""

import os
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from prometheus_fastapi_instrumentator import Instrumentator

from src.core.logging import get_logger

if TYPE_CHECKING:
    from fastapi import FastAPI

logger = get_logger(__name__)

# Load .env file to ensure ENABLE_METRICS is available
# This must happen before creating the Instrumentator instance
load_dotenv()

# Configure the instrumentator
# Note: should_respect_env_var checks ENABLE_METRICS at instantiation time
instrumentator = Instrumentator(
    should_group_status_codes=True,      # Group 4xx and 5xx codes
    should_ignore_untemplated=True,      # Ignore paths not matching routes
    should_respect_env_var=True,         # Respect ENABLE_METRICS env var
    should_instrument_requests_inprogress=True,  # Track in-progress requests
    excluded_handlers=["/health", "/metrics"],   # Don't instrument these paths
    inprogress_name="http_requests_inprogress",
    inprogress_labels=True,
)


def setup_metrics(app: "FastAPI") -> None:
    """Set up Prometheus metrics for FastAPI app.

    Instruments the app and exposes metrics at /metrics endpoint.

    Args:
        app: FastAPI application instance
    """
    instrumentator.instrument(app).expose(app, endpoint="/metrics")

    logger.info(
        "Prometheus metrics enabled",
        endpoint="/metrics",
    )
