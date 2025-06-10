"""SQLAlchemy ORM models for managing workcells in the Praxis application.

This file defines the database schema for storing workcell information,
including their names, descriptions, and relationships to associated machines.
"""

from datetime import datetime
from typing import Any, Optional

import uuid_utils as uuid
from sqlalchemy import JSON, UUID, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from praxis.backend.utils.db import Base


class WorkcellStatusEnum:
  """Enumeration for workcell status.

  This enum defines the possible statuses a workcell can have.
  """

  ACTIVE = "active"
  IN_USE = "in_use"
  RESERVED = "reserved"
  AVAILABLE = "available"
  ERROR = "error"
  INACTIVE = "inactive"
  MAINTENANCE = "maintenance"

  @classmethod
  def choices(cls):
    """Return a list of valid status choices."""
    return [
      cls.ACTIVE,
      cls.IN_USE,
      cls.RESERVED,
      cls.AVAILABLE,
      cls.ERROR,
      cls.INACTIVE,
      cls.MAINTENANCE,
    ]


class WorkcellOrm(Base):
  """SQLAlchemy ORM model representing a workcell.

  This model stores details about a logical grouping of machines and resources,
  often representing a physical lab space or automation setup.
  """

  __tablename__ = "workcells"

  id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
  description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
  physical_location: Mapped[Optional[str]] = mapped_column(
    String,
    nullable=True,
    comment="Physical location of the workcell (e.g., 'Lab 2, Room 301')",
  )

  created_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )
  updated_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
  )

  latest_state_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
    JSON,
    nullable=True,
    comment="JSON representation of the latest state of the workcell",
  )
  last_state_update_time: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="Timestamp of the last state update",
  )
  status: Mapped[str] = mapped_column(
    String,
    nullable=False,
    default=WorkcellStatusEnum.AVAILABLE,
    comment="Current status of the workcell",
  )

  # Relationship to machines within this workcell
  machines = relationship(
    "MachineOrm", back_populates="workcell", foreign_keys="[MachineOrm.workcell_id]"
  )

  def __repr__(self):
    """Return a string representation of the WorkcellOrm object."""
    return (
      f"<WorkcellOrm(id={self.id}, name='{self.name}',"
      f" physical_location='{self.physical_location}', status='{self.status}')>"
    )
