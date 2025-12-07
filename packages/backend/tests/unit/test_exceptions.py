"""Tests for custom exceptions."""

import pytest


class TestPulseException:
    """Test base PulseException."""

    def test_pulse_exception_has_message(self):
        """PulseException should store message."""
        from src.core.exceptions import PulseException

        exc = PulseException("Test error")

        assert exc.message == "Test error"
        assert exc.status_code == 500

    def test_pulse_exception_custom_status_code(self):
        """PulseException should accept custom status code."""
        from src.core.exceptions import PulseException

        exc = PulseException("Test error", status_code=400)

        assert exc.message == "Test error"
        assert exc.status_code == 400


class TestDerivedExceptions:
    """Test derived exception classes."""

    def test_validation_error(self):
        """ValidationError should have 400 status code."""
        from src.core.exceptions import ValidationError

        exc = ValidationError("Invalid data")

        assert exc.message == "Invalid data"
        assert exc.status_code == 400

    def test_authentication_error(self):
        """AuthenticationError should have 401 status code."""
        from src.core.exceptions import AuthenticationError

        exc = AuthenticationError("Unauthorized")

        assert exc.message == "Unauthorized"
        assert exc.status_code == 401

    def test_authorization_error(self):
        """AuthorizationError should have 403 status code."""
        from src.core.exceptions import AuthorizationError

        exc = AuthorizationError("Forbidden")

        assert exc.message == "Forbidden"
        assert exc.status_code == 403

    def test_not_found_error(self):
        """NotFoundError should have 404 status code."""
        from src.core.exceptions import NotFoundError

        exc = NotFoundError("Not found")

        assert exc.message == "Not found"
        assert exc.status_code == 404

    def test_conflict_error(self):
        """ConflictError should have 409 status code."""
        from src.core.exceptions import ConflictError

        exc = ConflictError("Conflict")

        assert exc.message == "Conflict"
        assert exc.status_code == 409

    def test_rate_limit_error(self):
        """RateLimitError should have 429 status code."""
        from src.core.exceptions import RateLimitError

        exc = RateLimitError("Too many requests")

        assert exc.message == "Too many requests"
        assert exc.status_code == 429
