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


# --- Pydantic Models for Deck Layouts ---
class DeckSlotItemBase(BaseModel):
    slot_name: str
    resource_instance_id: Optional[int] = None
    expected_resource_definition_name: Optional[str] = None

    class Config:
        orm_mode = True


class DeckSlotItemCreate(DeckSlotItemBase):
    pass


class DeckSlotItemResponse(DeckSlotItemBase):
    id: int
    deck_configuration_id: int


class DeckLayoutBase(BaseModel):
    layout_name: str
    deck_machine_id: int
    description: Optional[str] = None

    class Config:
        orm_mode = True


class DeckLayoutCreate(DeckLayoutBase):
    slot_items: Optional[List[DeckSlotItemCreate]] = []


class DeckLayoutUpdate(BaseModel):
    layout_name: Optional[str] = None
    deck_machine_id: Optional[int] = None
    description: Optional[str] = None
    slot_items: Optional[List[DeckSlotItemCreate]] = None


class DeckLayoutResponse(DeckLayoutBase):
    id: int
    slot_items: List[DeckSlotItemResponse] = []
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


# --- Inventory Pydantic Models ---
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


# --- Original Asset Models (Kept for existing endpoints' response models) ---
class AssetBase(BaseModel):  # Used for response, not directly for DB interaction now
    name: str
    type: str
    metadata: dict = {}


class AssetResponse(AssetBase):  # Used for response
    is_available: bool
    description: Optional[str] = None


# --- Request Models for creation (if needed, or use existing Resource/MachineCreationRequest) ---
# No changes needed for these request models themselves


class ResourceTypeInfo(BaseModel):
    name: str
    parent_class: str
    can_create_directly: bool
    constructor_params: Dict[str, Dict]
    doc: str
    module: str


class MachineTypeInfo(BaseModel):
    name: str
    parent_class: str
    constructor_params: Dict[str, Dict]
    backends: List[str]
    doc: str
    module: str


class ResourceCategoriesResponse(BaseModel):
    categories: Dict[str, List[str]]


class ResourceCreationRequest(BaseModel):
    name: str
    resourceType: str
    description: Optional[str] = None
    params: Dict[str, Any] = {}


class MachineCreationRequest(BaseModel):
    name: str
    machineType: str
    backend: Optional[str] = None
    description: Optional[str] = None
    params: Dict[str, Any] = {}


# --- Pydantic Models for Deck Slot Definitions (part of Deck Type Definitions) ---
class DeckSlotDefinitionBase(BaseModel):
    slot_name: str  # e.g., "A1", "trash_slot", "plate_carrier_1"
    pylabrobot_slot_type_name: Optional[str] = (
        None  # e.g., "PlateCarrier", "TipRackSlot" from PLR spot.resource_type.__name__
    )
    allowed_resource_categories: Optional[List[str]] = (
        None  # e.g., ["plate", "tip_rack"] or specific praxis_resource_type_name
    )
    allowed_resource_definition_names: Optional[List[str]] = (
        None  # List of specific pylabrobot_definition_name
    )
    accepts_tips: Optional[bool] = None
    accepts_plates: Optional[bool] = None
    accepts_tubes: Optional[bool] = None
    location_x_mm: Optional[float] = None  # Relative X from PLR spot.location.x
    location_y_mm: Optional[float] = None  # Relative Y from PLR spot.location.y
    location_z_mm: Optional[float] = None  # Relative Z from PLR spot.location.z
    notes: Optional[str] = None

    class Config:
        orm_mode = True
        use_enum_values = True


class DeckSlotDefinitionCreate(DeckSlotDefinitionBase):
    pass


class DeckSlotDefinitionResponse(DeckSlotDefinitionBase):
    id: int
    deck_type_definition_id: int  # Foreign Key to the DeckTypeDefinition
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


class DeckSlotDefinitionUpdate(BaseModel):
    slot_name: Optional[str] = None
    pylabrobot_slot_type_name: Optional[str] = None
    allowed_resource_categories: Optional[List[str]] = None
    allowed_resource_definition_names: Optional[List[str]] = None
    accepts_tips: Optional[bool] = None
    accepts_plates: Optional[bool] = None
    accepts_tubes: Optional[bool] = None
    location_x_mm: Optional[float] = None
    location_y_mm: Optional[float] = None
    location_z_mm: Optional[float] = None
    notes: Optional[str] = None


# --- Pydantic Models for Deck Type Definitions ---
class DeckTypeDefinitionBase(BaseModel):
    pylabrobot_class_name: (
        str  # PLR FQN, e.g., "pylabrobot.resources.hamilton.STARDeck"
    )
    praxis_deck_type_name: str  # User-friendly name, e.g., "Hamilton STAR Deck"
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        orm_mode = True
        use_enum_values = True


class DeckTypeDefinitionCreate(DeckTypeDefinitionBase):
    slot_definitions: Optional[List[DeckSlotDefinitionCreate]] = []


class DeckTypeDefinitionResponse(DeckTypeDefinitionBase):
    id: int
    slot_definitions: List[DeckSlotDefinitionResponse] = []
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


class DeckTypeDefinitionUpdate(BaseModel):
    pylabrobot_class_name: Optional[str] = None
    praxis_deck_type_name: Optional[str] = None
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    notes: Optional[str] = None
    # Slot definitions are typically managed via their own CRUD or through DeckTypeDefinitionCreate


# --- Pydantic Models for Managed Devices (includes Decks as a type of machine) ---
class MachineBase(BaseModel):
    name: str  # User-defined unique name for this instance
    machine_category: str  # e.g., "deck", "liquid_handler", "plate_reader", "heater_shaker", "robot_arm"
    # deck_type_definition_id is intentionally in Create/Response/Update as it's resolved or specified there
    description: Optional[str] = None
    manufacturer: Optional[str] = None  # Can be pre-filled from PLR inspection
    model: Optional[str] = None  # Can be pre-filled from PLR inspection
    serial_number: Optional[str] = None
    installation_date: Optional[datetime.date] = None
    status: Optional[str] = (
        "operational"  # e.g., "operational", "maintenance_required", "decommissioned", "unavailable"
    )
    location_description: Optional[str] = None  # e.g., "Lab 1, Bench 2, Position 3"
    connection_info: Optional[Dict[str, Any]] = (
        None  # e.g. {'backend': 'SerialBackend', 'port': '/dev/ttyUSB0'} or {'backend': 'HamiltonVenusBackend', 'address': 'localhost'}
    )
    is_simulation_override: Optional[bool] = (
        None  # User's preference to override default sim/real behavior
    )
    custom_fields: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True
        use_enum_values = True


class MachineCreate(MachineBase):
    pylabrobot_class_name: str  # PLR FQN, e.g., "pylabrobot.liquid_handling.hamilton.STAR" or "pylabrobot.resources.hamilton.STARDeck"
    deck_type_definition_id: Optional[int] = (
        None  # Optional: if known, service can also try to resolve it if pylabrobot_class_name is a known deck type
    )


class MachineResponse(MachineBase):
    id: int
    pylabrobot_class_name: str  # Reflects the class it was instantiated from
    deck_type_definition_id: Optional[int] = (
        None  # FK to DeckTypeDefinition, if this machine IS a deck and is linked
    )
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


class MachineUpdate(BaseModel):  # Explicit fields for update
    name: Optional[str] = None
    # pylabrobot_class_name: Optional[str] = None # Typically not updatable without re-instantiation logic
    machine_category: Optional[str] = None
    deck_type_definition_id: Optional[int] = (
        None  # Allow updating the link if necessary (e.g. more specific type identified)
    )
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    installation_date: Optional[datetime.date] = None
    status: Optional[str] = None
    location_description: Optional[str] = None
    connection_info: Optional[Dict[str, Any]] = None
    is_simulation_override: Optional[bool] = None
    custom_fields: Optional[Dict[str, Any]] = None


# --- Pydantic Models for Resource Instances ---
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
