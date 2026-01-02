"""SQLAlchemy ORM models for managing workcells in the Praxis application.

This file defines the database schema for storing workcell information,
including their names, descriptions, and relationships to associated machines.
"""

import uuid
from datetime import datetime
from functools import partial
from typing import TYPE_CHECKING, Any

from sqlalchemy import UUID, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from praxis.backend.models.enums.workcell import WorkcellStatusEnum
from praxis.backend.models.orm.types import JsonVariant
from praxis.backend.utils.db import Base
from praxis.backend.utils.uuid import generate_name, uuid7

if TYPE_CHECKING:
  from . import DeckOrm, MachineOrm, ResourceOrm


class WorkcellOrm(Base):
  """SQLAlchemy ORM model representing a workcell.

  This model stores details about a logical grouping of machines and resources,
  often representing a physical lab space or automation setup.
  """

  __tablename__ = "workcells"

  accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    primary_key=True,
    index=True,
    init=True,
    default_factory=uuid7,
  )
  name: Mapped[str] = mapped_column(
    String,
    unique=True,
    index=True,
    nullable=False,
    default_factory=partial(generate_name, prefix="workcell_"),
  )
  description: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    default=None,
    comment="Description of the workcell's purpose or contents",
  )
  physical_location: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="Physical location of the workcell (e.g., 'Lab 2, Room 301')",
    default=None,
  )

  latest_state_json: Mapped[dict[str, Any] | None] = mapped_column(
    JsonVariant,
    nullable=True,
    comment="JSONB representation of the latest state of the workcell",
    default=None,
  )
  last_state_update_time: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="Timestamp of the last state update",
    default=None,
  )
  status: Mapped[str] = mapped_column(
    String,
    nullable=False,
    default=WorkcellStatusEnum.AVAILABLE.value,
    comment="Current status of the workcell",
  )

  machines: Mapped[list["MachineOrm"]] = relationship(
    "MachineOrm",
    back_populates="workcell",
    foreign_keys="MachineOrm.workcell_accession_id",
    default_factory=list,
  )
  decks: Mapped[list["DeckOrm"]] = relationship(
    "DeckOrm",
    back_populates="workcell",
    foreign_keys="DeckOrm.workcell_accession_id",
    default_factory=list,
  )
  resources: Mapped[list["ResourceOrm"]] = relationship(
    "ResourceOrm",
    back_populates="workcell",
    foreign_keys="ResourceOrm.workcell_accession_id",
    overlaps="decks",
    default_factory=list,
  )

  def __repr__(self) -> str:
    """Return a string representation of the WorkcellOrm object."""
    return (
      f"<WorkcellOrm(id={self.accession_id}, name='{self.name}',"
      f" physical_location='{self.physical_location}', status='{self.status}')>"
    )
