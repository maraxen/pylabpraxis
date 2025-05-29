from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import datetime


class ResourceDefinitionBase(BaseModel):
    pylabrobot_definition_name: str
    python_fqn: str
    praxis_resource_type_name: Optional[str] = None
    description: Optional[str] = None
    is_consumable: bool = True
    nominal_volume_ul: Optional[float] = None
    material: Optional[str] = None
    manufacturer: Optional[str] = None
    plr_definition_details_json: Optional[Dict[str, Any]] = None
    size_x_mm: Optional[float] = None
    size_y_mm: Optional[float] = None
    size_z_mm: Optional[float] = None
    model: Optional[str] = None

    class Config:
        orm_mode = True
        use_enum_values = True


class ResourceDefinitionCreate(ResourceDefinitionBase):
    pass


class ResourceDefinitionUpdate(BaseModel):
    python_fqn: Optional[str] = None
    praxis_resource_type_name: Optional[str] = None
    description: Optional[str] = None
    is_consumable: Optional[bool] = None
    nominal_volume_ul: Optional[float] = None
    material: Optional[str] = None
    manufacturer: Optional[str] = None
    plr_definition_details_json: Optional[Dict[str, Any]] = None
    size_x_mm: Optional[float] = None
    size_y_mm: Optional[float] = None
    size_z_mm: Optional[float] = None
    model: Optional[str] = None


class ResourceDefinitionResponse(ResourceDefinitionBase):
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


class ResourceInventoryReagentItem(BaseModel):
    reagent_id: str
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
    item_type: Optional[str] = None
    initial_max_items: Optional[int] = None
    current_available_items: Optional[int] = None
    positions_used: Optional[List[str]] = None


class ResourceInventoryDataIn(BaseModel):
    praxis_inventory_schema_version: Optional[str] = "1.0"
    reagents: Optional[List[ResourceInventoryReagentItem]] = None
    item_count: Optional[ResourceInventoryItemCount] = None
    consumable_state: Optional[str] = None
    last_updated_by: Optional[str] = None
    inventory_notes: Optional[str] = None


class ResourceInventoryDataOut(ResourceInventoryDataIn):
    last_updated_at: Optional[str] = None


class ResourceTypeInfo(BaseModel):
    name: str
    parent_class: str
    can_create_directly: bool
    constructor_params: Dict[str, Dict]
    doc: str
    module: str


class ResourceCategoriesResponse(BaseModel):
    categories: Dict[str, List[str]]


class ResourceCreationRequest(BaseModel):
    name: str
    resourceType: str
    description: Optional[str] = None
    params: Dict[str, Any] = {}


class ResourceInstanceSharedFields(BaseModel):
    """
    Fields that are common across different ResourceInstance models
    and have fully compatible type signatures.
    """

    lot_number: Optional[str] = None
    serial_number: Optional[str] = None
    status: Optional[str] = (
        "new"  # e.g., "new", "in_use", "empty", "discarded", "reserved", "contaminated"
    )
    current_parent_slot_id: Optional[int] = None
    current_position_in_slot: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None
    date_added_to_inventory: Optional[datetime.datetime] = (
        None  # Consistently Optional here
    )

    class Config:
        orm_mode = True
        use_enum_values = True


class ResourceInstanceCreate(ResourceInstanceSharedFields):
    # Fields specific to creation or with different handling during creation
    instance_name: Optional[str] = (
        None  # Optional for creation, service can auto-generate
    )
    pylabrobot_definition_name: (
        str  # e.g., "Cos_96_DW_1mL"; used by service to find/link ResourceDefinition
    )
    resource_definition_id: Optional[int] = (
        None  # Optional: if user provides ID directly
    )
    inventory_data: Optional[ResourceInventoryDataIn] = None
    # Override date_added_to_inventory to provide a default for creation, type remains Optional
    date_added_to_inventory: Optional[datetime.datetime] = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )


class ResourceInstanceResponse(ResourceInstanceSharedFields):
    # Fields specific to response or with different type requirements for response
    id: int
    resource_definition_id: int  # Should be resolved and returned
    pylabrobot_definition_name: (
        str  # Return for clarity, from the linked ResourceDefinition
    )

    # Defined fresh here to be non-optional, avoiding incompatible override
    instance_name: str  # Non-optional in response, guaranteed by service

    # Defined fresh here with the 'Out' version of inventory data
    inventory_data: Optional[ResourceInventoryDataOut] = (
        None  # Uses ResourceInventoryDataOut for response
    )

    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    # date_added_to_inventory is inherited from ResourceInstanceSharedFields as Optional[datetime.datetime]
    # Its value will be populated from the database for the response.


class ResourceInstanceUpdate(BaseModel):
    """
    Model for updating a ResourceInstance. Fields are all optional.
    Does not inherit from SharedFields to allow for partial updates without
    default values from SharedFields interfering, unless that is desired.
    If inheriting SharedFields is desired, ensure any defaults are acceptable for updates.
    """

    instance_name: Optional[str] = None
    lot_number: Optional[str] = None
    serial_number: Optional[str] = None
    status: Optional[str] = None
    current_parent_slot_id: Optional[int] = None
    current_position_in_slot: Optional[str] = None
    inventory_data: Optional[ResourceInventoryDataIn] = (
        None  # Allow updating inventory (using In model)
    )
    custom_fields: Optional[Dict[str, Any]] = None
    date_added_to_inventory: Optional[datetime.datetime] = (
        None  # Less common to update, but possible
    )

    class Config:
        orm_mode = True
        use_enum_values = True
