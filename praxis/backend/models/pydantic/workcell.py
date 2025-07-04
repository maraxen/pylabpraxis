"""Pydantic models for managing workcell entities in the Praxis application.

These models are used for data validation and serialization/deserialization
of workcell configurations, enabling consistent API interactions.

Models included:
- WorkcellBase
- WorkcellCreate
- WorkcellUpdate
- WorkcellResponse
"""


from pydantic import UUID7, BaseModel, Field

from praxis.backend.models.deck_pydantic_models import DeckStateResponse
from praxis.backend.models.machine_pydantic_models import MachineResponse
from praxis.backend.models.pydantic_base import TimestampedModel
from praxis.backend.models.resource_pydantic_models import ResourceResponse


class WorkcellBase(BaseModel):
  """Defines the base properties for a workcell."""

  name: str = Field(description="The unique name of the workcell.")
  description: str | None = Field(None, description="A description of the workcell.")
  physical_location: str | None = Field(
    None, description="The physical location of the workcell (e.g., 'Lab 2, Room 301').",
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
    None, description="The new description of the workcell.",
  )
  physical_location: str | None = Field(
    None, description="The new physical location of the workcell.",
  )


class WorkcellResponse(WorkcellBase, TimestampedModel):
  """Represents a workcell for API responses.

  This model extends `WorkcellBase` by adding system-generated identifiers
  and timestamps for creation and last update, suitable for client-facing
  responses.
  """

  accession_id: UUID7 = Field(description="The unique database ID of the workcell.")
  machines: list[MachineResponse] = Field(
    default_factory=list, description="List of machines associated with this workcell.",
  )

  resources: list[ResourceResponse] | None = Field(
    default_factory=list, description="List of resources associated with this workcell.",
  )

  decks: list[DeckStateResponse] | None = Field(
    default_factory=list,
    description="List of deck configurations associated with this workcell.",
  )

  class Config(TimestampedModel.Config):
    """Pydantic configuration for WorkcellResponse."""

