"""Pydantic models for user management in the Praxis application.

These models are used for data validation and serialization/deserialization
of user configurations, enabling consistent API interactions.
"""

from pydantic import BaseModel, Field

from praxis.backend.models.pydantic.pydantic_base import PraxisBaseModel


class UserBase(BaseModel):
  """Defines the base properties for a user."""

  username: str = Field(description="The unique name of the user.")
  email: str = Field(description="The user's email address.")
  full_name: str | None = Field(None, description="The user's full name.")
  is_active: bool = Field(True, description="Whether the user is active.")


class UserCreate(UserBase):
  """Represents a user for creation requests."""

  password: str = Field(description="The user's password.")


class UserUpdate(BaseModel):
  """Specifies the fields that can be updated for an existing user."""

  username: str | None = Field(None, description="The new unique name of the user.")
  email: str | None = Field(None, description="The new email address for the user.")
  full_name: str | None = Field(None, description="The new full name for the user.")
  is_active: bool | None = Field(None, description="Whether the user is active.")
  password: str | None = Field(None, description="The new password for the user.")


class UserResponse(UserBase, PraxisBaseModel):
  """Represents a user for API responses."""

  class Config(PraxisBaseModel.Config):
    """Pydantic configuration for UserResponse."""
