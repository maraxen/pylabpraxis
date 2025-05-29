from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import datetime

# TODO: Consider importing MachineStatusEnum and PlrCategoryEnum
# from praxis.backend.database_models.asset_management_orm import MachineStatusEnum, PlrCategoryEnum
# if direct import is feasible and preferred over string types.


class DeckInfo(BaseModel):
    """Basic information about a deck."""

    id: int = Field(description="ORM ID of the MachineOrm for the deck")
    user_friendly_name: str = Field(description="User-assigned name for the deck")
    pylabrobot_class_name: str = Field(
        description="PyLabRobot class name for the deck (e.g., 'Deck')"
    )
    current_status: str = Field(
        description="Current operational status of the deck (e.g., 'ONLINE', 'OFFLINE')"
    )
    # current_status: MachineStatusEnum # Alternative if enum is imported


class ResourceInfo(BaseModel):
    """Detailed information about a resource instance on the deck."""

    resource_instance_id: int = Field(description="ORM ID of the ResourceInstanceOrm")
    user_assigned_name: str = Field(
        description="User-assigned name for this specific resource instance"
    )
    pylabrobot_definition_name: str = Field(
        description="PyLabRobot definition name (e.g., 'corning_96_wellplate_360ul_flat')"
    )
    python_fqn: str = Field(
        description="Fully qualified Python name of the PyLabRobot resource class"
    )
    category: str = Field(
        description="Category of the resource (e.g., 'PLATE', 'TIP_RACK')"
    )
    # category: PlrCategoryEnum # Alternative if enum is imported
    size_x_mm: Optional[float] = Field(None, description="Dimension X in millimeters")
    size_y_mm: Optional[float] = Field(None, description="Dimension Y in millimeters")
    size_z_mm: Optional[float] = Field(
        None, description="Dimension Z in millimeters (height)"
    )
    nominal_volume_ul: Optional[float] = Field(
        None, description="Nominal volume of a well/container in microliters"
    )
    properties_json: Optional[Dict[str, Any]] = Field(
        None, description="Custom properties, e.g., well contents, calibration data"
    )
    model: Optional[str] = Field(
        None, description="Manufacturer model number or identifier"
    )


class SlotInfo(BaseModel):
    """Information about a single slot on the deck."""

    name: str = Field(
        description="Identifier for the slot (e.g., 'A1', 'slot_1', 'trash_slot')"
    )
    x_coordinate: Optional[float] = Field(
        None,
        description="X coordinate of the slot's origin relative to the deck, in millimeters",
    )
    y_coordinate: Optional[float] = Field(
        None,
        description="Y coordinate of the slot's origin relative to the deck, in millimeters",
    )
    z_coordinate: Optional[float] = Field(
        None,
        description="Z coordinate of the slot's origin relative to the deck, in millimeters (often the deck surface at this slot)",
    )
    labware: Optional[ResourceInfo] = Field(
        None, description="Resource instance currently occupying this slot, if any"
    )


class DeckStateResponse(BaseModel):
    """Represents the complete state of a deck, including its slots and contained labware."""

    deck_id: int = Field(description="ORM ID of the MachineOrm for the deck")
    user_friendly_name: str = Field(description="User-assigned name for the deck")
    pylabrobot_class_name: str = Field(description="PyLabRobot class name for the deck")
    size_x_mm: Optional[float] = Field(
        None, description="Overall physical dimension X of the deck in millimeters"
    )
    size_y_mm: Optional[float] = Field(
        None, description="Overall physical dimension Y of the deck in millimeters"
    )
    size_z_mm: Optional[float] = Field(
        None,
        description="Overall physical dimension Z of the deck in millimeters (e.g., height)",
    )
    slots: List[SlotInfo] = Field(description="List of all slots defined on this deck")


class DeckUpdateMessage(BaseModel):
    """Model for WebSocket messages broadcasting updates to the deck state."""

    deck_id: int = Field(description="ORM ID of the deck that was updated")
    update_type: str = Field(
        description="Type of update (e.g., 'labware_added', 'labware_removed', 'labware_updated', 'slot_cleared')"
    )
    slot_name: Optional[str] = Field(
        None, description="Name of the slot affected by the update, if applicable"
    )
    labware_info: Optional[ResourceInfo] = Field(
        None,
        description="The new state of the labware in the slot, or null if labware was removed",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat(),
        description="Timestamp of the update in ISO format (UTC)",
    )

    class Config:
        # Ensure that default_factory works as expected
        validate_assignment = True
