from pydantic import BaseModel
from typing import Optional, List
import datetime


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


class DeckSlotDefinitionBase(BaseModel):
    slot_name: str
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
