"""SQLAlchemy ORM model for user management in the Praxis application.

This file defines the database schema for storing user information,
including authentication credentials, contact details, and account status.
"""

import uuid

from sqlalchemy import UUID, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from praxis.backend.utils.db import Base


class UserOrm(Base):
  """SQLAlchemy ORM model representing a user in the Praxis application.

  This model stores user account details such as username, email, hashed password,
  full name, active status, and optional contact information.
  """

  __tablename__ = "users"

  accession_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  username: Mapped[str] = mapped_column(
    String,
    unique=True,
    index=True,
    nullable=False,
    comment="Unique username for user login",
    init=False,
  )
  email: Mapped[str] = mapped_column(
    String,
    unique=True,
    index=True,
    nullable=False,
    comment="User's email address for notifications and account recovery",
    init=False,
  )
  hashed_password: Mapped[str] = mapped_column(
    String,
    nullable=False,
    comment="Hashed password for user authentication",
    init=False,
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

  def __repr__(self) -> str:
    """Return a string representation of the UserOrm object."""
    return (
      f"<UserOrm(id={self.accession_id}, username='{self.username}',"
      f" email='{self.email}', is_active={self.is_active})>"
    )
