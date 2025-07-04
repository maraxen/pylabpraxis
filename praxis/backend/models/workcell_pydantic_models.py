"""Pydantic models for managing workcell entities in the Praxis application.

These models are used for data validation and serialization/deserialization
of workcell configurations, enabling consistent API interactions.

Models included:
- WorkcellBase
- WorkcellCreate
- WorkcellUpdate
- WorkcellResponse
"""

import datetime
from typing import List, Optional

from pydantic import UUID7, BaseModel, Field

from praxis.backend.models.deck_pydantic_models import DeckStateResponse
from praxis.backend.models.machine_pydantic_models import MachineResponse
from praxis.backend.models.resource_pydantic_models import ResourceInstanceResponse


class WorkcellBase(BaseModel):
  """Defines the base properties for a workcell.

  This model captures essential attributes shared across workcell
  representations, such as name, description, and physical location.
  """

  name: str = Field(description="The unique name of the workcell.")
  id: Optional[UUID7] = Field(
    None, description="The unique identifier for the workcell (optional for creation)."
  )
  description: Optional[str] = Field(None, description="A description of the workcell.")
  physical_location: Optional[str] = Field(
    None, description="The physical location of the workcell (e.g., 'Lab 2, Room 301')."
  )

  class Config:
    """Pydantic configuration for WorkcellBase."""

    from_attributes = True


class WorkcellCreate(WorkcellBase):
  """Represents a workcell for creation requests.

  This model inherits all properties from `WorkcellBase` and is used
  specifically when creating new workcell entries.
  """

  pass


class WorkcellUpdate(BaseModel):
  """Specifies the fields that can be updated for an existing workcell.

  All fields are optional, allowing for partial updates to a workcell's
  attributes.
  """

  name: Optional[str] = Field(None, description="The new unique name of the workcell.")
  description: Optional[str] = Field(
    None, description="The new description of the workcell."
  )
  physical_location: Optional[str] = Field(
    None, description="The new physical location of the workcell."
  )


class WorkcellResponse(WorkcellBase):
  """Represents a workcell for API responses.

  This model extends `WorkcellBase` by adding system-generated identifiers
  and timestamps for creation and last update, suitable for client-facing
  responses.
  """

  db_accession_id: UUID7 = Field(description="The unique database ID of the workcell.")
  created_at: Optional[datetime.datetime] = Field(
    None, description="Timestamp when the workcell was created (UTC)."
  )
  updated_at: Optional[datetime.datetime] = Field(
    None, description="Timestamp when the workcell was last updated (UTC)."
  )
  machines: List[MachineResponse] = Field(
    default_factory=list, description="List of machines associated with this workcell."
  )

  resources: Optional[List[ResourceInstanceResponse]] = Field(
    default_factory=list, description="List of resources associated with this workcell."
  )

  decks: Optional[List[DeckStateResponse]] = Field(
    default_factory=list,
    description="List of deck instanceurations associated with this workcell.",
  )
