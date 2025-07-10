"""Pydantic models for managing machine assets within the Praxis application.

These models define the structure for requests and responses related to
machine instances, including their creation, retrieval, and updates,
enabling robust data validation and serialization for API interactions.
"""

from typing import Any

from pydantic import UUID7, Field

from praxis.backend.models.enums import MachineStatusEnum, ResourceStatusEnum
from praxis.backend.models.pydantic.plr_sync import PLRTypeDefinitionCreate, PLRTypeDefinitionUpdate

from .asset import AssetBase, AssetResponse, AssetUpdate


class MachineBase(AssetBase):
  """Defines the base properties for a machine."""

  status: MachineStatusEnum = Field(default=MachineStatusEnum.OFFLINE)
  status_details: str | None = None
  workcell_id: UUID7 | None = None
  is_resource: bool = Field(default=False)
  resource_counterpart_accession_id: UUID7 | None = None
  has_deck_child: bool = Field(
    default=False,
    description="Indicates if this machine has a deck resource as a child.",
  )
  has_resource_child: bool = Field(
    default=False,
    description="Indicates if this machine has a resource child.",
  )
  description: str | None = None
  manufacturer: str | None = None
  model: str | None = None
  serial_number: str | None = None
  installation_date: Any | None = None
  connection_info: dict[str, Any] | None = None
  is_simulation_override: bool | None = None
  last_seen_online: Any | None = None
  current_protocol_run_accession_id: UUID7 | None = None

  class Config:
    """Configuration for Pydantic model behavior."""

    from_attributes = True
    use_enum_values = True


class MachineCreate(MachineBase):
  """Represents a machine for creation requests.

  Extends `MachineBase` with fields required for creating a new machine,
  including details for an optional resource counterpart.
  """

  # Fields for creating a resource counterpart if is_resource is True
  resource_def_name: str | None = Field(
    default=None,
    description=(
      "The definition name for the resource counterpart. Required if is_resource is "
      "True and no counterpart ID is provided."
    ),
  )
  resource_properties_json: dict[str, Any] | None = Field(
    default=None,
    description="Properties for the new resource counterpart.",
  )
  resource_initial_status: ResourceStatusEnum | None = Field(
    default=None,
    description="Initial status for the new resource counterpart.",
  )


class MachineUpdate(AssetUpdate):
  """Represents a machine for update requests."""

  status: MachineStatusEnum | None = None
  status_details: str | None = None
  workcell_id: UUID7 | None = None
  is_resource: bool | None = None
  resource_counterpart_accession_id: UUID7 | None = None
  # You can also update resource counterpart details if needed
  resource_def_name: str | None = None
  resource_properties_json: dict[str, Any] | None = None
  resource_initial_status: ResourceStatusEnum | None = None


class MachineResponse(AssetResponse, MachineBase):
  """Represents a machine for API responses.

  Extends `MachineBase` and `AssetResponse` to provide a complete
  view of the machine, including system-generated fields.
  """

  class Config(AssetResponse.Config, MachineBase.Config):
    """Pydantic configuration for MachineResponse."""


class MachineTypeDefinitionCreate(PLRTypeDefinitionCreate):
  """Model for creating a new machine type definition."""


class MachineTypeDefinitionUpdate(PLRTypeDefinitionUpdate):
  """Model for updating a machine type definition."""
