# pylint: disable=too-few-public-methods,missing-class-docstring
"""Unified SQLModel definitions for Workcell."""

import uuid
from datetime import datetime
from typing import Any

from typing import Any, List, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
  from praxis.backend.models.domain.machine import Machine
  from praxis.backend.models.domain.resource import Resource

from praxis.backend.models.domain.sqlmodel_base import PraxisBase
from praxis.backend.models.enums.workcell import WorkcellStatusEnum
from praxis.backend.utils.db import JsonVariant


class WorkcellBase(PraxisBase):
  """Base schema for Workcell - shared fields for create/update/response."""

  description: str | None = Field(default=None, description="Description of the workcell's purpose")
  physical_location: str | None = Field(
    default=None, description="Physical location (e.g., 'Lab 2, Room 301')"
  )
  status: str = Field(
    default=WorkcellStatusEnum.AVAILABLE.value, description="Current status of the workcell"
  )
  last_state_update_time: datetime | None = Field(
    default=None, description="Timestamp of last state update"
  )


class Workcell(WorkcellBase, table=True):
  """Workcell ORM model - represents a logical grouping of machines and resources."""

  __tablename__ = "workcells"

  latest_state_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Latest state of the workcell"
  )

  # Relationships
  machines: List["Machine"] = Relationship(back_populates="workcell")
  # decks: list["Deck"] = Relationship(back_populates="workcell")
  resources: List["Resource"] = Relationship(back_populates="workcell")


class WorkcellCreate(WorkcellBase):
  """Schema for creating a Workcell."""


class WorkcellRead(WorkcellBase):
  """Schema for reading a Workcell (API response)."""

  accession_id: uuid.UUID
  latest_state_json: dict[str, Any] | None = None


class WorkcellUpdate(SQLModel):
  """Schema for updating a Workcell (partial update)."""

  name: str | None = None
  description: str | None = None
  physical_location: str | None = None
  status: str | None = None
  latest_state_json: dict[str, Any] | None = None
