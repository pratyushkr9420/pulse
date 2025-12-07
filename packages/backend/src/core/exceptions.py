"""Custom exception hierarchy."""


class PulseException(Exception):
    """Base exception for Pulse application."""

    def __init__(self, message: str, status_code: int = 500):
        """Initialize exception.

        Args:
            message: Error message.
            status_code: HTTP status code.
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(PulseException):
    """Exception for validation errors."""

    def __init__(self, message: str):
        """Initialize validation error.

        Args:
            message: Error message.
        """
        super().__init__(message, status_code=400)


class AuthenticationError(PulseException):
    """Exception for authentication errors."""

    def __init__(self, message: str):
        """Initialize authentication error.

        Args:
            message: Error message.
        """
        super().__init__(message, status_code=401)


class AuthorizationError(PulseException):
    """Exception for authorization errors."""

    def __init__(self, message: str):
        """Initialize authorization error.

        Args:
            message: Error message.
        """
        super().__init__(message, status_code=403)


class NotFoundError(PulseException):
    """Exception for not found errors."""

    def __init__(self, message: str):
        """Initialize not found error.

        Args:
            message: Error message.
        """
        super().__init__(message, status_code=404)


class ConflictError(PulseException):
    """Exception for conflict errors."""

    def __init__(self, message: str):
        """Initialize conflict error.

        Args:
            message: Error message.
        """
        super().__init__(message, status_code=409)


class RateLimitError(PulseException):
    """Exception for rate limit errors."""

    def __init__(self, message: str):
        """Initialize rate limit error.

        Args:
            message: Error message.
        """
        super().__init__(message, status_code=429)
