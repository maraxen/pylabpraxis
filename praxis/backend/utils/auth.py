"""JWT authentication utilities for PyLabPraxis.

This module provides utilities for creating and verifying JWT tokens for
user authentication.
"""

import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from pydantic import BaseModel

from keycloak import KeycloakOpenID

logger = logging.getLogger(__name__)

# TODO: Move these to configuration file (praxis.ini)
# For now, use environment variables with sensible defaults
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Keycloak Configuration
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080/")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "praxis")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "praxis")

# Cache for Keycloak public key
_KEYCLOAK_PUBLIC_KEY: str | None = None


class TokenData(BaseModel):
  """Model for JWT token payload data."""

  username: str | None = None
  user_id: str | None = None


class Token(BaseModel):
  """Model for API token response."""

  access_token: str
  token_type: str = "bearer"


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
  """Create a JWT access token."""
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.now(timezone.utc) + expires_delta
  else:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _get_keycloak_public_key() -> str:
  """Get or fetch Keycloak public key."""
  global _KEYCLOAK_PUBLIC_KEY  # noqa: PLW0603
  if _KEYCLOAK_PUBLIC_KEY:
    return _KEYCLOAK_PUBLIC_KEY

  try:
    keycloak_openid = KeycloakOpenID(
      server_url=KEYCLOAK_URL,
      client_id=KEYCLOAK_CLIENT_ID,
      realm_name=KEYCLOAK_REALM,
    )
    # python-keycloak public_key() returns the raw key string without headers
    public_key = keycloak_openid.public_key()
    _KEYCLOAK_PUBLIC_KEY = f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
    return _KEYCLOAK_PUBLIC_KEY
  except Exception as e:
    logger.error("Failed to fetch Keycloak public key: %s", e)
    return ""


def verify_token(token: str) -> TokenData | None:
  """Verify and decode a JWT token.

  Supports both local HS256 tokens and Keycloak RS256 tokens.
  """
  try:
    # Peek at header to determine algorithm without verification
    header = jwt.get_unverified_header(token)
    alg = header.get("alg")

    if alg == "HS256":
      # Verify local token
      payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      username = payload.get("sub")
      user_id = payload.get("user_id")
    elif alg == "RS256":
      # Verify Keycloak token
      public_key = _get_keycloak_public_key()
      if not public_key:
        return None

      # Use python-jose to verify with the public key
      # We skip 'aud' check by default or we can check against client_id
      payload = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        options={"verify_aud": False},  # Keycloak access tokens might have different audience
      )

      # Map Keycloak claims
      username = payload.get("preferred_username")
      user_id = payload.get("sub")
    else:
      return None

    if username is None:
      return None

    return TokenData(username=username, user_id=user_id)
  except JWTError:
    return None
  except Exception:
    return None
