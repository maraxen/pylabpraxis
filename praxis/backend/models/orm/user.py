"""SQLAlchemy ORM model for user management in the Praxis application.

This file defines the database schema for storing user information,
including authentication credentials, contact details, and account status.
"""

import uuid

from sqlalchemy import UUID, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from praxis.backend.utils.db import Base
from praxis.backend.utils.uuid import uuid7


class UserOrm(Base):
  """SQLAlchemy ORM model representing a user in the Praxis application.

  This model stores user account details such as username, email, hashed password,
  full name, active status, and optional contact information.
  """

  __tablename__ = "users"

  # Override accession_id from Base to allow it in __init__
  accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    primary_key=True,
    index=True,
    default_factory=uuid7,
    kw_only=True,  # Optional in init, will auto-generate if not provided
  )

  # Override name from Base - for Users, name is the same as username
  # We hide it from __init__ and auto-set it from username
  name: Mapped[str] = mapped_column(
    String,
    unique=True,
    index=True,
    nullable=False,
    comment="Username (same as username field, required by Base class)",
    init=False,  # Don't require in __init__, will be set from username
  )

  username: Mapped[str] = mapped_column(
    String,
    unique=True,
    index=True,
    nullable=False,
    comment="Unique username for user login",
    kw_only=True,
  )
  email: Mapped[str] = mapped_column(
    String,
    unique=True,
    index=True,
    nullable=False,
    comment="User's email address for notifications and account recovery",
    kw_only=True,
  )
  hashed_password: Mapped[str] = mapped_column(
    String,
    nullable=False,
    comment="Hashed password for user authentication",
    kw_only=True,
  )
  full_name: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="User's full name for display purposes",
    default=None,
  )
  is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

  phone_number: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    index=True,
    comment="User's phone number for SMS notifications",
    default=None,
  )
  phone_carrier: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="User's phone carrier for SMS gateway emails, e.g., 'verizon', 'att'",
    default=None,
  )

  def __post_init__(self) -> None:
    """Initialize computed fields after dataclass initialization."""
    # Auto-set name to username since for users, name == username
    if not self.name:
      self.name = self.username

  def __repr__(self) -> str:
    """Return a string representation of the UserOrm object."""
    return (
      f"<UserOrm(id={self.accession_id}, username='{self.username}',"
      f" email='{self.email}', is_active={self.is_active})>"
    )
