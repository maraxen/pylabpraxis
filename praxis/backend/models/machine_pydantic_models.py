"""Pydantic models for managing machine assets within the Praxis application.

These models define the structure for requests and responses related to
machine instances, including their creation, retrieval, and updates,
enabling robust data validation and serialization for API interactions.
"""

from typing import Any, Dict, Optional

from pydantic import UUID7, Field

from .asset_pydantic_models import AssetBase, AssetResponse, AssetUpdate
from .machine_orm import MachineStatusEnum
from .resource_orm import ResourceStatusEnum


class MachineBase(AssetBase):
  """Defines the base properties for a machine."""

  status: MachineStatusEnum = Field(default=MachineStatusEnum.OFFLINE)
  status_details: Optional[str] = None
  workcell_id: Optional[UUID7] = None
  is_resource: bool = Field(default=False)
  resource_counterpart_accession_id: Optional[UUID7] = None

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
  resource_def_name: Optional[str] = Field(
    default=None,
    description=(
      "The definition name for the resource counterpart. Required if is_resource is "
      "True and no counterpart ID is provided."
    ),
  )
  resource_properties_json: Optional[Dict[str, Any]] = Field(
    default=None,
    description="Properties for the new resource counterpart.",
  )
  resource_initial_status: Optional[ResourceStatusEnum] = Field(
    default=None,
    description="Initial status for the new resource counterpart.",
  )


class MachineUpdate(AssetUpdate):
  """Represents a machine for update requests."""

  status: Optional[MachineStatusEnum] = None
  status_details: Optional[str] = None
  workcell_id: Optional[UUID7] = None
  is_resource: Optional[bool] = None
  resource_counterpart_accession_id: Optional[UUID7] = None
  # You can also update resource counterpart details if needed
  resource_def_name: Optional[str] = None
  resource_properties_json: Optional[Dict[str, Any]] = None
  resource_initial_status: Optional[ResourceStatusEnum] = None


class MachineResponse(AssetResponse, MachineBase):
  """Represents a machine for API responses.

  Extends `MachineBase` and `AssetResponse` to provide a complete
  view of the machine, including system-generated fields.
  """

  class Config(AssetResponse.Config, MachineBase.Config):
    """Pydantic configuration for MachineResponse."""

    pass
