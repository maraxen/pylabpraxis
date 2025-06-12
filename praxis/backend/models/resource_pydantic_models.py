"""Pydantic models for managing resource definitions and instances in Praxis.

These models handle the structured representation of various lab resources,
from their generic definitions to specific physical instances and their
inventory data.

Models included:
- ResourceDefinitionBase
- ResourceDefinitionCreate
- ResourceDefinitionUpdate
- ResourceDefinitionResponse
- ResourceInventoryReagentItem
- ResourceInventoryItemCount
- ResourceInventoryDataIn
- ResourceInventoryDataOut
- ResourceTypeInfo
- ResourceCategoriesResponse
- ResourceCreationRequest
- ResourceInstanceSharedFields
- ResourceInstanceCreate
- ResourceInstanceResponse
- ResourceInstanceUpdate
"""

import datetime
from typing import Any, Dict, List, Optional

from pydantic import UUID7, BaseModel, Field


class ResourceDefinitionBase(BaseModel):
  """Defines the base properties for a resource definition.

  This model captures general attributes of a type of lab resource,
  such as its PyLabRobot definition name, type, and physical dimensions.
  """

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
  """Represents a resource definition for creation requests.

  This model inherits all properties from `ResourceDefinitionBase` and is
  used when creating new resource definitions.
  """

  pass


class ResourceDefinitionUpdate(BaseModel):
  """Specifies the fields that can be updated for an existing resource definition.

  All fields are optional, allowing for partial updates of a resource's
  definitional attributes.
  """

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


class ResourceDefinitionResponse(ResourceDefinitionBase):
  """Represents a resource definition for API responses.

  Extends `ResourceDefinitionBase` by including timestamps for creation and
  last update, suitable for client-facing responses.
  """

  created_at: Optional[datetime.datetime] = None
  updated_at: Optional[datetime.datetime] = None


class ResourceInventoryReagentItem(BaseModel):
  """Represents a single reagent item within resource inventory data.

  This model captures specific details about a reagent, such as lot number,
  expiry, and quantities, for inventory tracking.
  """

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
  """Provides counts and usage information for items within a resource inventory.

  This helps track the maximum capacity, current availability, and used positions
  for consumable resources.
  """

  item_type: Optional[str] = None
  initial_max_items: Optional[int] = None
  current_available_items: Optional[int] = None
  positions_used: Optional[List[str]] = None


class ResourceInventoryDataIn(BaseModel):
  """Represents inbound inventory data for a resource instance.

  This model is used when submitting or updating inventory details,
  including reagents, item counts, and general state information.
  """

  praxis_inventory_schema_version: Optional[str] = "1.0"
  reagents: Optional[List[ResourceInventoryReagentItem]] = None
  item_count: Optional[ResourceInventoryItemCount] = None
  consumable_state: Optional[str] = None
  last_updated_by: Optional[str] = None
  inventory_notes: Optional[str] = None


class ResourceInventoryDataOut(ResourceInventoryDataIn):
  """Represents outbound inventory data for a resource instance.

  Extends `ResourceInventoryDataIn` by adding a `last_updated_at` timestamp,
  suitable for responses.
  """

  last_updated_at: Optional[str] = None


class ResourceTypeInfo(BaseModel):
  """Provides detailed information about a specific resource type.

  This includes its name, parent class, constructor parameters, and
  whether it can be directly instantiated.
  """

  name: str
  parent_class: str
  can_create_directly: bool
  constructor_params: Dict[str, Dict]
  doc: str
  module: str


class ResourceCategoriesResponse(BaseModel):
  """Organizes resource types by category for categorization and discovery."""

  categories: Dict[str, List[str]]


class ResourceCreationRequest(BaseModel):
  """Represents a request to create a new resource instance.

  It includes the desired name, resource type, description, and
  specific parameters for resource instantiation.
  """

  name: str
  resourceType: str
  description: Optional[str] = None
  params: Dict[str, Any] = {}


class ResourceInstanceSharedFields(BaseModel):
  """Defines fields common across different ResourceInstance models.

  These fields have compatible type signatures and represent general
  attributes of a physical resource item, such as status and location.
  """

  id: UUID7
  user_assigned_name: str = Field(
    ...,
    description="A user-friendly name for the resource instance, which can be \
      different from the PyLabRobot definition name.",
  )
  lot_number: Optional[str] = None
  serial_number: Optional[str] = None
  status: Optional[str] = "unknown"
  current_parent_accession_id: Optional[UUID7] = None
  current_position_accession_id: Optional[UUID7] = None
  custom_fields: Optional[Dict[str, Any]] = None
  date_added_to_inventory: Optional[datetime.datetime] = None
  is_machine: bool = Field(
    default=False,
    description="True if this resource instance is also registered as a machine.",
  )
  machine_counterpart_accession_id: Optional[UUID7] = Field(
    default=None,
    description="ID of the associated MachineOrm if this resource instance is a \
      machine.",
  )

  class Config:
    """Pydantic configuration for ResourceInstanceSharedFields."""

    from_attributes = True
    use_enum_values = True


class ResourceInstanceCreate(ResourceInstanceSharedFields):
  """Represents a resource instance for creation requests.

  Extends `ResourceInstanceSharedFields` by including the PyLabRobot
  definition name and an optional resource definition ID, used to link
  to a resource definition.
  """

  name: str
  resource_definition_accession_id: Optional[UUID7] = None
  inventory_data: Optional[ResourceInventoryDataIn] = None
  date_added_to_inventory: Optional[datetime.datetime] = Field(
    default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
  )


class ResourceInstanceResponse(ResourceInstanceSharedFields):
  """Represents a resource instance for API responses.

  Extends `ResourceInstanceSharedFields` by adding system-generated identifiers,
  the linked resource definition ID and PyLabRobot definition name,
  and timestamps for creation and last update.
  """

  id: UUID7
  resource_definition_accession_id: Optional[UUID7]
  name: str

  instance_name: str

  inventory_data: Optional[ResourceInventoryDataOut] = None

  created_at: Optional[datetime.datetime] = None
  updated_at: Optional[datetime.datetime] = None


class ResourceInstanceUpdate(BaseModel):
  """Specifies the fields that can be updated for an existing resource instance.

  All fields are optional, allowing for partial updates to the instance's
  attributes, including its status and inventory data.
  """

  instance_name: Optional[str] = None
  lot_number: Optional[str] = None
  serial_number: Optional[str] = None
  status: Optional[str] = None
  current_parent_accession_id: Optional[UUID7] = None
  current_position_accession_id: Optional[UUID7] = None
  inventory_data: Optional[ResourceInventoryDataIn] = None
  custom_fields: Optional[Dict[str, Any]] = None
  date_added_to_inventory: Optional[datetime.datetime] = None
  is_machine: Optional[bool] = Field(
    default=None,
    description="True if this resource instance is also registered as a machine.",
  )
  machine_counterpart_accession_id: Optional[UUID7] = Field(
    default=None,
    description="ID of the associated MachineOrm if this resource instance is a \
      machine.",
  )

  class Config:
    """Pydantic configuration for ResourceInstanceUpdate."""

    from_attributes = True
    use_enum_values = True
