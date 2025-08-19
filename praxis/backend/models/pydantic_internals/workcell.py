"""Pydantic models for managing workcell entities in the Praxis application.

These models are used for data validation and serialization/deserialization
of workcell configurations, enabling consistent API interactions.

Models included:
- WorkcellBase
- WorkcellCreate
- WorkcellUpdate
- WorkcellResponse
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from praxis.backend.models.enums.workcell import WorkcellStatusEnum
from praxis.backend.models.pydantic_internals.deck import DeckResponse
from praxis.backend.models.pydantic_internals.machine import MachineResponse
from praxis.backend.models.pydantic_internals.pydantic_base import PraxisBaseModel
from praxis.backend.models.pydantic_internals.resource import ResourceResponse


class WorkcellBase(BaseModel):

  """Defines the base properties for a workcell."""

  name: str = Field(description="The unique name of the workcell.")
  description: str | None = Field(None, description="A description of the workcell.")
  physical_location: str | None = Field(
    None,
    description="The physical location of the workcell (e.g., 'Lab 2, Room 301').",
  )
  status: WorkcellStatusEnum = Field(
    default=WorkcellStatusEnum.AVAILABLE,
    description="The current status of the workcell.",
  )
  latest_state_json: dict[str, Any] | None = Field(
    None,
    description="The latest state of the workcell as a JSON object.",
  )
  last_state_update_time: datetime | None = Field(
    None,
    description="The timestamp of the last state update.",
  )


class WorkcellCreate(WorkcellBase):

  """Represents a workcell for creation requests.

  This model inherits all properties from `WorkcellBase` and is used
  specifically when creating new workcell entries.
  """


class WorkcellUpdate(BaseModel):

  """Specifies the fields that can be updated for an existing workcell.

  All fields are optional, allowing for partial updates to a workcell's
  attributes.
  """

  name: str | None = Field(None, description="The new unique name of the workcell.")
  description: str | None = Field(
    None,
    description="The new description of the workcell.",
  )
  physical_location: str | None = Field(
    None,
    description="The new physical location of the workcell.",
  )
  status: WorkcellStatusEnum | None = Field(
    None,
    description="The new status of the workcell.",
  )
  latest_state_json: dict[str, Any] | None = Field(
    None,
    description="The new state of the workcell as a JSON object.",
  )


class WorkcellResponse(WorkcellBase, PraxisBaseModel):

  """Represents a workcell for API responses.

  This model extends `WorkcellBase` by adding system-generated identifiers
  and timestamps for creation and last update, suitable for client-facing
  responses.
  """

  machines: list[MachineResponse] = Field(
    default_factory=list,
    description="List of machines associated with this workcell.",
  )

  resources: list[ResourceResponse] | None = Field(
    default_factory=list,
    description="List of resources associated with this workcell.",
  )

  decks: list[DeckResponse] | None = Field(
    default_factory=list,
    description="List of deck configurations associated with this workcell.",
  )

  class Config(PraxisBaseModel.Config):

    """Pydantic configuration for WorkcellResponse."""
