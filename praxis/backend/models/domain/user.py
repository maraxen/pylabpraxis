# pylint: disable=too-few-public-methods,missing-class-docstring
"""Unified SQLModel definitions for User."""

import uuid

from sqlmodel import Field, SQLModel

from praxis.backend.models.domain.sqlmodel_base import PraxisBase


class UserBase(PraxisBase):
    """Base schema for User - shared fields for create/update/response."""

    username: str = Field(unique=True, index=True, description="Unique username for login")
    email: str = Field(unique=True, index=True, description="User's email address")
    full_name: str | None = Field(default=None, description="User's full name")
    is_active: bool = Field(default=True, description="Whether the user account is active")
    phone_number: str | None = Field(default=None, index=True, description="Phone number for SMS notifications")
    phone_carrier: str | None = Field(default=None, description="Phone carrier for SMS gateway")


class User(UserBase, table=True):
    """User ORM model - represents a user account."""

    __tablename__ = "users"

    hashed_password: str = Field(description="Hashed password for authentication")


class UserCreate(UserBase):
    """Schema for creating a User."""

    password: str  # Plain password, will be hashed before storage


class UserRead(UserBase):
    """Schema for reading a User (API response) - excludes hashed_password."""

    accession_id: uuid.UUID


class UserUpdate(SQLModel):
    """Schema for updating a User (partial update)."""

    name: str | None = None
    username: str | None = None
    email: str | None = None
    full_name: str | None = None
    is_active: bool | None = None
    phone_number: str | None = None
    phone_carrier: str | None = None
    password: str | None = None  # Plain password, will be hashed if provided
