"""Authentication API endpoints for PyLabPraxis."""

import logging
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.api.dependencies import get_db
from praxis.backend.models.pydantic_internals.user import UserResponse
from praxis.backend.services.user import user_service
from praxis.backend.utils.auth import (
  ACCESS_TOKEN_EXPIRE_MINUTES,
  create_access_token,
  verify_token,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class LoginRequest(BaseModel):
  """Login request model."""

  username: str
  password: str


class LoginResponse(BaseModel):
  """Login response model with user data and token."""

  user: UserResponse
  access_token: str
  token_type: str = "bearer"


@router.post("/login", response_model=LoginResponse)
async def login(
  credentials: LoginRequest,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> LoginResponse:
  """Authenticate user and return access token.

  Args:
      credentials: User login credentials (username and password)
      db: Database session

  Returns:
      LoginResponse with user data and JWT token

  Raises:
      HTTPException: If authentication fails (401 Unauthorized)

  """
  logger.info("Login attempt for username: %s", credentials.username)

  # Authenticate user
  user = await user_service.authenticate(
    db,
    username=credentials.username,
    password=credentials.password,
  )

  if not user:
    logger.warning("Failed login attempt for username: %s", credentials.username)
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Incorrect username or password",
      headers={"WWW-Authenticate": "Bearer"},
    )

  # Create access token
  access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  access_token = create_access_token(
    data={"sub": user.username, "user_id": str(user.accession_id)},
    expires_delta=access_token_expires,
  )

  logger.info("User '%s' logged in successfully", credentials.username)

  # Return user data and token
  return LoginResponse(
    user=UserResponse(
      username=user.username,
      email=user.email,
      full_name=user.full_name,
      is_active=user.is_active,
    ),
    access_token=access_token,
    token_type="bearer",
  )


@router.post("/logout")
async def logout() -> dict[str, str]:
  """Logout endpoint.

  Note: JWT tokens are stateless, so logout is handled client-side
  by removing the token from storage. This endpoint exists for
  API consistency and can be extended to implement token blacklisting
  if needed in the future.

  Returns:
      Success message

  """
  return {"message": "Logged out successfully"}


async def get_current_user(
  token: Annotated[str, Depends(oauth2_scheme)],
  db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
  """Get the current authenticated user from JWT token.

  This dependency can be used in protected routes to require authentication.

  Args:
      token: JWT access token from Authorization header
      db: Database session

  Returns:
      UserResponse for the authenticated user

  Raises:
      HTTPException: If token is invalid or user not found (401 Unauthorized)

  """
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )

  # Verify token
  token_data = verify_token(token)
  if token_data is None or token_data.username is None:
    raise credentials_exception

  # Get user from database
  user = await user_service.get_by_username(db, username=token_data.username)
  if user is None:
    raise credentials_exception

  if not user.is_active:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Inactive user",
    )

  return UserResponse(
    username=user.username,
    email=user.email,
    full_name=user.full_name,
    is_active=user.is_active,
  )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
  current_user: Annotated[UserResponse, Depends(get_current_user)],
) -> UserResponse:
  """Get the current authenticated user's information.

  This is a protected route that requires a valid JWT token.

  Args:
      current_user: Current authenticated user (injected by dependency)

  Returns:
      UserResponse with current user's data

  """
  return current_user
