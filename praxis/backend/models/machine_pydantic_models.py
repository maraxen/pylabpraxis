from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import datetime


class MachineTypeInfo(BaseModel):
    name: str
    parent_class: str
    constructor_params: Dict[str, Dict]
    backends: List[str]
    doc: str
    module: str


class MachineCreationRequest(BaseModel):
    name: str
    machineType: str
    backend: Optional[str] = None
    description: Optional[str] = None
    params: Dict[str, Any] = {}


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
