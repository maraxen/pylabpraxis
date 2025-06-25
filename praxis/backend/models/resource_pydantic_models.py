"""Pydantic models for managing resource definitions and instances in Praxis.

These models handle the structured representation of various lab resources,
from their generic definitions to specific physical instances and their
inventory data.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from pydantic import UUID7, BaseModel, Field

from .asset_pydantic_models import AssetBase, AssetResponse, AssetUpdate
from .pydantic_base import TimestampedModel
from .resource_orm import ResourceStatusEnum

if TYPE_CHECKING:
  from .machine_orm import MachineStatusEnum

# =============================================================================
# Resource Instance Models
# =============================================================================


class ResourceBase(AssetBase):
  """Base model for a resource instance."""

  status: ResourceStatusEnum = Field(default=ResourceStatusEnum.UNKNOWN)
  resource_definition_accession_id: Optional[UUID7] = None
  machine_counterpart_accession_id: Optional[UUID7] = None
  deck_counterpart_accession_id: Optional[UUID7] = None
  parent_accession_id: Optional[UUID7] = None
  plr_state: Optional[dict] = None
  plr_definition: Optional[dict] = None
  properties_json: Optional[dict] = None

  class Config:
    """Configuration for Pydantic model behavior."""

    from_attributes = True
    use_enum_values = True


class ResourceCreate(ResourceBase):
  """Model for creating a new resource instance."""

  is_machine: bool = Field(
    default=False,
    description="Indicates if this resource is also registered as a machine instance.",
  )
  # Fields for creating a machine counterpart if is_machine is True
  machine_fqn: Optional[str] = Field(
    default=None,
    description=(
      "The FQN for the machine counterpart. Required if is_machine is True and no "
      "counterpart ID is provided."
    ),
  )
  machine_properties_json: Optional[Dict[str, Any]] = Field(
    default=None,
    description="Properties for the new machine counterpart.",
  )
  machine_initial_status: Optional["MachineStatusEnum"] = Field(
    default=None,
    description="Initial status for the new machine counterpart.",
  )


class ResourceUpdate(AssetUpdate):
  """Model for updating a resource instance."""

  status: Optional[ResourceStatusEnum] = None
  resource_definition_accession_id: Optional[UUID7] = None
  machine_counterpart_accession_id: Optional[UUID7] = None
  deck_counterpart_accession_id: Optional[UUID7] = None
  parent_accession_id: Optional[UUID7] = None
  is_machine: Optional[bool] = None
  machine_fqn: Optional[str] = None
  machine_properties_json: Optional[Dict[str, Any]] = None
  machine_initial_status: Optional["MachineStatusEnum"] = None


class ResourceResponse(AssetResponse, ResourceBase):
  """Model for API responses for a resource instance."""

  parent: Optional["ResourceResponse"] = None
  children: List["ResourceResponse"] = []

  class Config(AssetResponse.Config, ResourceBase.Config):
    """Pydantic configuration for ResourceResponse."""

    pass


ResourceResponse.model_rebuild()


# =============================================================================
# Resource Definition Models (Existing)
# =============================================================================


class ResourceDefinitionBase(BaseModel):
  """Defines the base properties for a resource definition."""

  accession_id: UUID7
  name: str
  python_fqn: str
  resource_type: Optional[str] = None
  description: Optional[str] = None
  is_consumable: bool = True
  is_machine: bool = False
  nominal_volume_ul: Optional[float] = None
  material: Optional[str] = None
  manufacturer: Optional[str] = None
  plr_definition_details_json: Optional[Dict[str, Any]] = None
  size_x_mm: Optional[float] = None
  size_y_mm: Optional[float] = None
  size_z_mm: Optional[float] = None
  model: Optional[str] = None

  class Config:
    """Pydantic configuration for ResourceDefinitionBase."""

    from_attributes = True
    use_enum_values = True


class ResourceDefinitionCreate(ResourceDefinitionBase):
  """Represents a resource definition for creation requests."""

  pass


class ResourceDefinitionUpdate(BaseModel):
  """Specifies the fields that can be updated for an existing resource definition."""

  python_fqn: Optional[str] = None
  resource_type: Optional[str] = None
  description: Optional[str] = None
  nominal_volume_ul: Optional[float] = None
  material: Optional[str] = None
  manufacturer: Optional[str] = None
  plr_definition_details_json: Optional[Dict[str, Any]] = None
  size_x_mm: Optional[float] = None
  size_y_mm: Optional[float] = None
  size_z_mm: Optional[float] = None
  model: Optional[str] = None


class ResourceDefinitionResponse(ResourceDefinitionBase, TimestampedModel):
  """Represents a resource definition for API responses."""

  class Config(ResourceDefinitionBase.Config, TimestampedModel.Config):
    """Pydantic configuration for ResourceDefinitionResponse."""

    pass


class ResourceInventoryReagentItem(BaseModel):
  """Represents a single reagent item within resource inventory data."""

  reagent_accession_id: UUID7
  reagent_name: Optional[str] = None
  lot_number: Optional[str] = None
  expiry_date: Optional[str] = None
  supplier: Optional[str] = None
  catalog_number: Optional[str] = None
  date_received: Optional[str] = None
  date_opened: Optional[str] = None
  concentration: Optional[Dict[str, Any]] = None
  initial_quantity: Dict[str, Any]
  current_quantity: Dict[str, Any]
  quantity_unit_is_volume: Optional[bool] = True
  custom_fields: Optional[Dict[str, Any]] = None


class ResourceInventoryItemCount(BaseModel):
  """Provides counts and usage information for items within a resource inventory."""

  item_type: Optional[str] = None
  initial_max_items: Optional[int] = None
  current_available_items: Optional[int] = None
  positions_used: Optional[List[str]] = None


class ResourceInventoryDataIn(BaseModel):
  """Represents inbound inventory data for a resource instance."""

  praxis_inventory_schema_version: Optional[str] = "1.0"
  reagents: Optional[List[ResourceInventoryReagentItem]] = None
  item_count: Optional[ResourceInventoryItemCount] = None
  consumable_state: Optional[str] = None
  last_updated_by: Optional[str] = None
  inventory_notes: Optional[str] = None


class ResourceInventoryDataOut(ResourceInventoryDataIn):
  """Represents outbound inventory data for a resource instance."""

  last_updated_at: Optional[str] = None


class ResourceTypeInfo(BaseModel):
  """Provides detailed information about a specific resource type."""

  name: str
  parent_class: str
  can_create_directly: bool
  constructor_params: Dict[str, Dict]
  doc: str
  module: str


class ResourceCategoriesResponse(BaseModel):
  """Organizes resource types by category for categorization and discovery."""

  categories: Dict[str, List[str]]
