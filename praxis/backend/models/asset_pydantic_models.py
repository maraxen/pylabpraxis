from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime

class LabwareDefinitionBase(BaseModel):
    pylabrobot_definition_name: str
    python_fqn: str
    praxis_labware_type_name: Optional[str] = None
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

class LabwareDefinitionCreate(LabwareDefinitionBase):
    pass

class LabwareDefinitionUpdate(BaseModel):
    python_fqn: Optional[str] = None
    praxis_labware_type_name: Optional[str] = None
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

class LabwareDefinitionResponse(LabwareDefinitionBase):
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


# --- Pydantic Models for Deck Layouts ---
class DeckSlotItemBase(BaseModel):
    slot_name: str
    labware_instance_id: Optional[int] = None
    expected_labware_definition_name: Optional[str] = None

    class Config:
        orm_mode = True

class DeckSlotItemCreate(DeckSlotItemBase):
    pass

class DeckSlotItemResponse(DeckSlotItemBase):
    id: int
    deck_configuration_id: int


class DeckLayoutBase(BaseModel):
    layout_name: str
    deck_device_id: int
    description: Optional[str] = None

    class Config:
        orm_mode = True

class DeckLayoutCreate(DeckLayoutBase):
    slot_items: Optional[List[DeckSlotItemCreate]] = []

class DeckLayoutUpdate(BaseModel):
    layout_name: Optional[str] = None
    deck_device_id: Optional[int] = None
    description: Optional[str] = None
    slot_items: Optional[List[DeckSlotItemCreate]] = None

class DeckLayoutResponse(DeckLayoutBase):
    id: int
    slot_items: List[DeckSlotItemResponse] = []
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


# --- Inventory Pydantic Models ---
class LabwareInventoryReagentItem(BaseModel):
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

class LabwareInventoryItemCount(BaseModel):
    item_type: Optional[str] = None
    initial_max_items: Optional[int] = None
    current_available_items: Optional[int] = None
    positions_used: Optional[List[str]] = None

class LabwareInventoryDataIn(BaseModel):
    praxis_inventory_schema_version: Optional[str] = "1.0"
    reagents: Optional[List[LabwareInventoryReagentItem]] = None
    item_count: Optional[LabwareInventoryItemCount] = None
    consumable_state: Optional[str] = None
    last_updated_by: Optional[str] = None
    inventory_notes: Optional[str] = None

class LabwareInventoryDataOut(LabwareInventoryDataIn):
    last_updated_at: Optional[str] = None


# --- Original Asset Models (Kept for existing endpoints' response models) ---
class AssetBase(BaseModel): # Used for response, not directly for DB interaction now
    name: str
    type: str
    metadata: dict = {}

class AssetResponse(AssetBase): # Used for response
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
