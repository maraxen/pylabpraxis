"""Pydantic models for managing machine assets within the Praxis application.

These models define the structure for requests and responses related to
machine instances, including their creation, retrieval, and updates,
enabling robust data validation and serialization for API interactions.
"""

from typing import Any

from pydantic import UUID7, Field

from praxis.backend.models.enums import MachineCategoryEnum, MachineStatusEnum, ResourceStatusEnum
from praxis.backend.models.pydantic_internals.plr_sync import (
  PLRTypeDefinitionBase,
  PLRTypeDefinitionCreate,
  PLRTypeDefinitionResponse,
  PLRTypeDefinitionUpdate,
)
from praxis.backend.utils.uuid import uuid7

from .asset import AssetBase, AssetResponse, AssetUpdate


class MachineBase(AssetBase):

  """Defines the base properties for a machine."""

  status: MachineStatusEnum | None = Field(default=MachineStatusEnum.OFFLINE)
  status_details: str | None = None
  workcell_id: UUID7 | None = None
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


class MachineCreate(MachineBase):

  """Represents a machine for creation requests.

  Extends `MachineBase` with fields required for creating a new machine,
  including details for an optional resource counterpart.
  """

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
  resource_counterpart_accession_id: UUID7 | None = None
  has_deck_child: bool | None = None
  has_resource_child: bool | None = None
  description: str | None = None
  manufacturer: str | None = None
  model: str | None = None
  serial_number: str | None = None
  installation_date: Any | None = None
  connection_info: dict[str, Any] | None = None
  is_simulation_override: bool | None = None
  last_seen_online: Any | None = None
  current_protocol_run_accession_id: UUID7 | None = None

  resource_def_name: str | None = None
  resource_properties_json: dict[str, Any] | None = None
  resource_initial_status: ResourceStatusEnum | None = None


class MachineResponse(AssetResponse, MachineBase):
  # Re-declare accession_id to fix from_attributes inheritance/shadowing issue
  accession_id: UUID7 = Field(default_factory=uuid7)

  """Represents a machine for API responses.

  Extends `MachineBase` and `AssetResponse` to provide a complete
  view of the machine, including system-generated fields.
  """


class MachineDefinitionBase(PLRTypeDefinitionBase):

  """Defines the base properties for a machine definition."""

  machine_category: MachineCategoryEnum | None = Field(
    default=None,
    description="The category of the machine.",
  )
  nominal_volume_ul: float | None = Field(
    default=None,
    description="The nominal volume in microliters.",
  )
  material: str | None = Field(default=None, description="The material of the machine.")
  manufacturer: str | None = Field(default=None, description="The manufacturer of the machine.")
  plr_definition_details_json: dict[str, Any] | None = Field(
    default=None,
    description="PyLabRobot specific definition details.",
  )
  size_x_mm: float | None = Field(
    default=None,
    description="The size in the x-dimension in millimeters.",
  )
  size_y_mm: float | None = Field(
    default=None,
    description="The size in the y-dimension in millimeters.",
  )
  size_z_mm: float | None = Field(
    default=None,
    description="The size in the z-dimension in millimeters.",
  )
  model: str | None = Field(default=None, description="The model of the machine.")
  rotation_json: dict[str, Any] | None = Field(
    default=None,
    description="The rotation of the machine.",
  )
  resource_definition_accession_id: UUID7 | None = Field(
    default=None,
    description="The accession ID of the resource definition.",
  )
  has_deck: bool | None = Field(default=None, description="Whether the machine has a deck.")
  deck_definition_accession_id: UUID7 | None = Field(
    default=None,
    description="The accession ID of the deck definition.",
  )
  setup_method_json: dict[str, Any] | None = Field(
    default=None,
    description="The setup method for the machine.",
  )


class MachineDefinitionCreate(MachineDefinitionBase, PLRTypeDefinitionCreate):

  """Represents a machine definition for creation requests."""


class MachineDefinitionUpdate(PLRTypeDefinitionUpdate):

  """Specifies the fields that can be updated for an existing machine definition."""

  machine_category: MachineCategoryEnum | None = None
  nominal_volume_ul: float | None = None
  material: str | None = None
  manufacturer: str | None = None
  plr_definition_details_json: dict[str, Any] | None = None
  size_x_mm: float | None = None
  size_y_mm: float | None = None
  size_z_mm: float | None = None
  model: str | None = None
  rotation_json: dict[str, Any] | None = None
  resource_definition_accession_id: UUID7 | None = None
  has_deck: bool | None = None
  deck_definition_accession_id: UUID7 | None = None
  setup_method_json: dict[str, Any] | None = None


class MachineDefinitionResponse(MachineDefinitionBase, PLRTypeDefinitionResponse):

  """Represents a machine definition for API responses."""


# Rebuild models to resolve any forward references
MachineBase.model_rebuild()
MachineCreate.model_rebuild()
MachineUpdate.model_rebuild()
MachineResponse.model_rebuild()

