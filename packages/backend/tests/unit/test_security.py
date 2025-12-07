"""Tests for security utilities."""

import pytest
from datetime import timedelta


class TestPasswordHashing:
    """Test password hashing utilities."""

    def test_hash_password_returns_bcrypt_hash(self):
        """hash_password should return a bcrypt hash."""
        from src.core.security import hash_password

        hashed = hash_password("securepassword123")

        assert hashed != "securepassword123"
        assert hashed.startswith("$2b$")
        assert len(hashed) > 50

    def test_hash_password_different_each_time(self):
        """Each hash should be unique due to salt."""
        from src.core.security import hash_password

        hash1 = hash_password("samepassword")
        hash2 = hash_password("samepassword")

        assert hash1 != hash2

    def test_verify_password_correct(self):
        """verify_password should return True for correct password."""
        from src.core.security import hash_password, verify_password

        password = "securepassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """verify_password should return False for incorrect password."""
        from src.core.security import hash_password, verify_password

        hashed = hash_password("correctpassword")

        assert verify_password("wrongpassword", hashed) is False


class TestJWTTokens:
    """Test JWT token utilities."""

    def test_create_access_token_returns_string(self):
        """create_access_token should return a JWT string."""
        from src.core.security import create_access_token

        token = create_access_token(data={"sub": "testuser"})

        assert isinstance(token, str)
        assert len(token.split(".")) == 3  # JWT has 3 parts

    def test_create_access_token_with_custom_expiry(self):
        """Should create token with custom expiration."""
        from src.core.security import create_access_token

        token = create_access_token(
            data={"sub": "testuser"}, expires_delta=timedelta(minutes=5)
        )

        assert isinstance(token, str)

    def test_decode_access_token_returns_payload(self):
        """decode_access_token should return the payload."""
        from src.core.security import create_access_token, decode_access_token

        original_data = {"sub": "testuser", "email": "test@example.com"}
        token = create_access_token(data=original_data)

        payload = decode_access_token(token)

        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["email"] == "test@example.com"
        assert "exp" in payload

    def test_decode_invalid_token_returns_none(self):
        """decode_access_token should return None for invalid token."""
        from src.core.security import decode_access_token

        payload = decode_access_token("invalid.token.here")

        assert payload is None

    def test_decode_expired_token_returns_none(self):
        """decode_access_token should return None for expired token."""
        from src.core.security import create_access_token, decode_access_token

        # Create token that expires immediately
        token = create_access_token(
            data={"sub": "testuser"}, expires_delta=timedelta(seconds=-1)
        )

        payload = decode_access_token(token)

        assert payload is None
