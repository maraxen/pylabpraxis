# pylint: disable=too-few-public-methods,missing-class-docstring
"""Unified SQLModel definitions for Workcell."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Column, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

from praxis.backend.models.domain.sqlmodel_base import PraxisBase
from praxis.backend.models.enums.workcell import WorkcellStatusEnum
from praxis.backend.utils.db import JsonVariant

if TYPE_CHECKING:
  from praxis.backend.models.domain.deck import Deck
  from praxis.backend.models.domain.machine import Machine
  from praxis.backend.models.domain.resource import Resource


class WorkcellBase(PraxisBase):
  """Base schema for Workcell - shared fields for create/update/response."""

  fqn: str | None = Field(default=None, index=True, description="Fully qualified name")
  description: str | None = Field(default=None, description="Description of the workcell's purpose")
  physical_location: str | None = Field(
    default=None, description="Physical location (e.g., 'Lab 2, Room 301')"
  )
  status: WorkcellStatusEnum = Field(
    default=WorkcellStatusEnum.AVAILABLE,
    description="Current status of the workcell",
  )
  last_state_update_time: datetime | None = Field(
    default=None, description="Timestamp of last state update"
  )
  latest_state_json: dict[str, Any] | None = Field(
    default=None, description="Latest state of the workcell"
  )


class Workcell(WorkcellBase, table=True):
  """Workcell ORM model - represents a logical grouping of machines and resources."""

  __tablename__ = "workcells"
  __table_args__ = (UniqueConstraint("name"),)

  status: WorkcellStatusEnum = Field(
    default=WorkcellStatusEnum.AVAILABLE,
    sa_column=Column(
      SAEnum(WorkcellStatusEnum), default=WorkcellStatusEnum.AVAILABLE, nullable=False
    ),
  )

  # Redefine with sa_type for table
  latest_state_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Latest state of the workcell"
  )

  # Relationships with explicit join conditions to avoid mapper errors
  machines: list["Machine"] = Relationship(
    sa_relationship=relationship(
      "Machine",
      back_populates="workcell",
      primaryjoin="Machine.workcell_accession_id == Workcell.accession_id",
    )
  )
  decks: list["Deck"] = Relationship(
    sa_relationship=relationship(
      "Deck",
      back_populates="workcell",
      primaryjoin="Deck.workcell_accession_id == Workcell.accession_id",
    )
  )
  resources: list["Resource"] = Relationship(
    sa_relationship=relationship(
      "Resource",
      back_populates="workcell",
      primaryjoin="Resource.workcell_accession_id == Workcell.accession_id",
    )
  )


class WorkcellCreate(WorkcellBase):
  """Schema for creating a Workcell."""


class WorkcellRead(WorkcellBase):
  """Schema for reading a Workcell (API response)."""

  accession_id: uuid.UUID = Field(default_factory=uuid.uuid4)
  machines: list[Any] = Field(default_factory=list)
  decks: list[Any] = Field(default_factory=list)
  resources: list[Any] = Field(default_factory=list)


class WorkcellUpdate(SQLModel):
  """Schema for updating a Workcell (partial update)."""

  name: str | None = None
  description: str | None = None
  physical_location: str | None = None
  status: str | None = None
  latest_state_json: dict[str, Any] | None = None
