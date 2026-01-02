"""Tests for JWT authentication utilities.

This module tests the security-critical JWT token creation and verification
functions in praxis.backend.utils.auth.
"""

from datetime import datetime, timedelta, timezone

from jose import jwt

from praxis.backend.utils.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    verify_token,
)


class TestCreateAccessToken:
    """Tests for create_access_token function."""

    def test_create_access_token_contains_required_claims(self):
        """Verify JWT contains required claims (sub, exp)."""
        # Arrange
        test_data = {"sub": "testuser", "user_id": "123"}

        # Act
        token = create_access_token(data=test_data)

        # Assert - decode without verification to inspect claims
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "sub" in payload
        assert payload["sub"] == "testuser"
        assert "user_id" in payload
        assert payload["user_id"] == "123"
        assert "exp" in payload
        assert isinstance(payload["exp"], int)

    def test_create_access_token_expires_after_24_hours(self):
        """Verify default 24-hour expiration is set correctly."""
        # Arrange
        test_data = {"sub": "testuser", "user_id": "123"}
        before_creation = datetime.now(timezone.utc)

        # Act
        token = create_access_token(data=test_data)

        # Assert
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expiration = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_expiration = before_creation + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        # Allow 5 second tolerance for test execution time
        time_diff = abs((expiration - expected_expiration).total_seconds())
        assert time_diff < 5, f"Expiration differs by {time_diff} seconds"

    def test_create_access_token_with_custom_expiration(self):
        """Verify custom expiration override works."""
        # Arrange
        test_data = {"sub": "testuser", "user_id": "123"}
        custom_delta = timedelta(hours=1)
        before_creation = datetime.now(timezone.utc)

        # Act
        token = create_access_token(data=test_data, expires_delta=custom_delta)

        # Assert
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expiration = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        expected_expiration = before_creation + custom_delta

        # Allow 5 second tolerance
        time_diff = abs((expiration - expected_expiration).total_seconds())
        assert time_diff < 5


class TestVerifyToken:
    """Tests for verify_token function."""

    def test_verify_token_accepts_valid_token(self):
        """Verify valid token returns TokenData with correct values."""
        # Arrange
        test_data = {"sub": "testuser", "user_id": "123"}
        token = create_access_token(data=test_data)

        # Act
        token_data = verify_token(token)

        # Assert
        assert token_data is not None
        assert token_data.username == "testuser"
        assert token_data.user_id == "123"

    def test_verify_token_rejects_expired_token(self):
        """Verify expired token returns None (JWT validation fails)."""
        # Arrange - create token that expired 1 second ago
        test_data = {"sub": "testuser", "user_id": "123"}
        token = create_access_token(
            data=test_data,
            expires_delta=timedelta(seconds=-1),
        )

        # Act
        token_data = verify_token(token)

        # Assert - verify_token returns None for invalid tokens
        assert token_data is None

    def test_verify_token_rejects_malformed_token(self):
        """Verify invalid JWT format returns None."""
        # Test cases: various malformed tokens
        malformed_tokens = [
            "invalid.jwt.string",
            "",
            "not-a-jwt-at-all",
            "Bearer malformed",
        ]

        for bad_token in malformed_tokens:
            # Act
            token_data = verify_token(bad_token)

            # Assert
            assert token_data is None, f"Should reject malformed token: {bad_token}"

    def test_verify_token_rejects_tampered_token(self):
        """Verify signature validation prevents token tampering."""
        # Arrange - create valid token
        test_data = {"sub": "testuser", "user_id": "123"}
        token = create_access_token(data=test_data)

        # Tamper with the payload by decoding, modifying, and re-encoding with wrong secret
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload["user_id"] = "999"  # Escalate privileges
        tampered_token = jwt.encode(payload, "wrong-secret-key", algorithm=ALGORITHM)

        # Act
        token_data = verify_token(tampered_token)

        # Assert - signature mismatch should cause verification to fail
        assert token_data is None

    def test_verify_token_requires_sub_claim(self):
        """Verify token without 'sub' claim is rejected."""
        # Arrange - create token without 'sub' claim
        test_data = {"user_id": "123"}  # Missing 'sub'
        token = create_access_token(data=test_data)

        # Act
        token_data = verify_token(token)

        # Assert - verify_token returns None if 'sub' is missing
        assert token_data is None
