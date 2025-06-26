"""SQLAlchemy ORM model for user management in the Praxis application.

This file defines the database schema for storing user information,
including authentication credentials, contact details, and account status.
"""

import uuid
from datetime import datetime

from sqlalchemy import UUID, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from praxis.backend.utils.db import Base


class UserOrm(Base):
  """SQLAlchemy ORM model representing a user in the Praxis application.

  This model stores user account details such as username, email, hashed password,
  full name, active status, and optional contact information.
  """

  __tablename__ = "users"

  accession_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
  email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
  hashed_password: Mapped[str] = mapped_column(String, nullable=False)
  full_name: Mapped[str | None] = mapped_column(String, nullable=True)
  is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

  phone_number: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    index=True,
    comment="User's phone number for SMS notifications",
  )
  phone_carrier: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="User's phone carrier for SMS gateway emails, e.g., 'verizon', 'att'",
  )

  created_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True), server_default=func.now(),
  )
  updated_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),
  )

  def __repr__(self):
    """Return a string representation of the UserOrm object."""
    return (
      f"<UserOrm(id={self.accession_id}, username='{self.username}',"
      f" email='{self.email}', is_active={self.is_active})>"
    )
