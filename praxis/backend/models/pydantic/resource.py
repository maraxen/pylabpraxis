"""Pydantic models for managing resource definitions and instances in Praxis.

These models handle the structured representation of various lab resources,
from their generic definitions to specific physical instances and their
inventory data.
"""

from typing import Any, ClassVar, Optional

from pydantic import UUID7, BaseModel, Field

from praxis.backend.models.enums import MachineStatusEnum, ResourceStatusEnum
from praxis.backend.models.pydantic.plr_sync import (
  PLRTypeDefinitionCreate,
  PLRTypeDefinitionResponse,
  PLRTypeDefinitionUpdate,
)

from .asset import AssetBase, AssetResponse, AssetUpdate
from .pydantic_base import PraxisBaseModel


class ResourceBase(AssetBase):

  """Base model for a resource instance."""

  status: ResourceStatusEnum | None = Field(default=ResourceStatusEnum.UNKNOWN)
  status_details: str | None = None
  workcell_accession_id: UUID7 | None = None
  resource_definition_accession_id: UUID7 | None = None
  parent_accession_id: UUID7 | None = None
  plr_state: dict | None = None
  plr_definition: dict | None = None
  children: list["ResourceBase"] = Field(
    default_factory=list,
    description="List of child resources associated with this resource.",
  )
  parent: "ResourceBase | None" = None
  child_accession_ids: list[UUID7] = Field(
    default_factory=list,
    description="List of accession IDs for child resources to be associated with this resource.",
  )


class ResourceCreate(ResourceBase, PraxisBaseModel):

  """Model for creating a new resource instance."""

  machine_initial_status: Optional["MachineStatusEnum"] = Field(
    default=None,
    description="Initial status for the new machine counterpart.",
  )

  deck_initial_status: ResourceStatusEnum | None = Field(
    default=None,
    description="Initial status for the new deck counterpart.",
  )


class ResourceUpdate(ResourceBase, AssetUpdate):

  """Model for updating a resource instance."""


class ResourceResponse(AssetResponse, ResourceBase, PraxisBaseModel):

  """Model for API responses for a resource instance."""

  parent_response: "ResourceResponse | None" = None
  child_responses: ClassVar[list["ResourceResponse"]] = []

  class Config(AssetResponse.Config):

    """Pydantic configuration for ResourceResponse."""


ResourceResponse.model_rebuild()


class ResourceDefinitionBase(BaseModel):

  """Defines the base properties for a resource definition."""

  resource_type: str | None = None
  description: str | None = None
  is_consumable: bool = True
  nominal_volume_ul: float | None = None
  material: str | None = None
  manufacturer: str | None = None
  plr_definition_details_json: dict[str, Any] | None = None
  size_x_mm: float | None = None
  size_y_mm: float | None = None
  size_z_mm: float | None = None
  model: str | None = None
  plr_category: str | None = None
  rotation_json: dict[str, Any] | None = None
  ordering: str | None = None


class ResourceDefinitionCreate(ResourceDefinitionBase, PLRTypeDefinitionCreate):

  """Represents a resource definition for creation requests."""


class ResourceDefinitionUpdate(ResourceDefinitionBase, PLRTypeDefinitionUpdate):

  """Specifies the fields that can be updated for an existing resource definition."""


class ResourceDefinitionResponse(ResourceDefinitionBase, PLRTypeDefinitionResponse):

  """Represents a resource definition for API responses."""


class ResourceInventoryReagentItem(BaseModel):

  """Represents a single reagent item within resource inventory data."""

  reagent_accession_id: UUID7
  reagent_name: str | None = None
  lot_number: str | None = None
  expiry_date: str | None = None
  supplier: str | None = None
  catalog_number: str | None = None
  date_received: str | None = None
  date_opened: str | None = None
  concentration: dict[str, Any] | None = None
  initial_quantity: dict[str, Any]
  current_quantity: dict[str, Any]
  quantity_unit_is_volume: bool | None = True
  custom_fields: dict[str, Any] | None = None


class ResourceInventoryItemCount(BaseModel):

  """Provides counts and usage information for items within a resource inventory."""

  item_type: str | None = None
  initial_max_items: int | None = None
  current_available_items: int | None = None
  positions_used: list[str] | None = None


class ResourceInventoryDataIn(BaseModel):

  """Represents inbound inventory data for a resource instance."""

  praxis_inventory_schema_version: str | None = "1.0"
  reagents: list[ResourceInventoryReagentItem] | None = None
  item_count: ResourceInventoryItemCount | None = None
  consumable_state: str | None = None
  last_updated_by: str | None = None
  inventory_notes: str | None = None


class ResourceInventoryDataOut(ResourceInventoryDataIn):

  """Represents outbound inventory data for a resource instance."""

  last_updated_at: str | None = None


class ResourceTypeInfo(BaseModel):

  """Provides detailed information about a specific resource type."""

  name: str
  parent_class: str
  can_create_directly: bool
  constructor_params: dict[str, dict]
  doc: str
  module: str


class ResourceCategoriesResponse(BaseModel):

  """Organizes resource types by category for categorization and discovery."""

  categories: dict[str, list[str]]
