"""Pydantic models for deck-related entities in the Praxis application.

These models are used for data validation and serialization/deserialization of deck configurations,
positioning with "poses" which are human accessible location guides (e.g., slots or rails), and
layouts.
"""

import datetime
from typing import List, Optional

from pydantic import BaseModel


class DeckPoseItemBase(BaseModel):
  pose_id: str | int
  resource_instance_id: Optional[int] = None
  expected_resource_definition_name: Optional[str] = None

  class Config:
    orm_mode = True


class DeckPoseItemCreate(DeckPoseItemBase):
  pass


class DeckPoseItemResponse(DeckPoseItemBase):
  item_id: int
  deck_configuration_id: int


class DeckLayoutBase(BaseModel):
  layout_name: str
  deck_id: int
  description: Optional[str] = None

  class Config:
    orm_mode = True


class DeckLayoutCreate(DeckLayoutBase):
  pose_items: Optional[List[DeckPoseItemCreate]] = []


class DeckLayoutUpdate(BaseModel):
  layout_name: Optional[str] = None
  deck_id: Optional[int] = None
  description: Optional[str] = None
  pose_items: Optional[List[DeckPoseItemCreate]] = None


class DeckLayoutResponse(DeckLayoutBase):
  id: int
  pose_items: List[DeckPoseItemResponse] = []
  created_at: Optional[datetime.datetime] = None
  updated_at: Optional[datetime.datetime] = None


class DeckPoseDefinitionBase(BaseModel):
  pose_id: str | int
  pylabrobot_pose_type_name: Optional[str] = None
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


class DeckPoseDefinitionCreate(DeckPoseDefinitionBase):
  pass


class DeckPoseDefinitionResponse(DeckPoseDefinitionBase):
  id: int
  deck_type_definition_id: int  # Foreign Key to the DeckTypeDefinition
  created_at: Optional[datetime.datetime] = None
  updated_at: Optional[datetime.datetime] = None


class DeckPoseDefinitionUpdate(BaseModel):
  pose_id: Optional[str | int] = None
  pylabrobot_pose_type_name: Optional[str] = None
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
  pylabrobot_class_name: str
  praxis_deck_type_name: str
  pose_arg_name: str
  pose_to_location_method_name: str
  description: Optional[str] = None
  manufacturer: Optional[str] = None
  model: Optional[str] = None
  notes: Optional[str] = None

  class Config:
    orm_mode = True
    use_enum_values = True


class DeckTypeDefinitionCreate(DeckTypeDefinitionBase):
  pose_definitions: Optional[List[DeckPoseDefinitionCreate]] = []


class DeckTypeDefinitionResponse(DeckTypeDefinitionBase):
  id: int
  pose_definitions: List[DeckPoseDefinitionResponse] = []
  created_at: Optional[datetime.datetime] = None
  updated_at: Optional[datetime.datetime] = None


class DeckTypeDefinitionUpdate(BaseModel):
  pylabrobot_class_name: Optional[str] = None
  praxis_deck_type_name: Optional[str] = None
  pose_arg_name: Optional[str] = None
  pose_to_location_method_name: Optional[str] = None
  description: Optional[str] = None
  manufacturer: Optional[str] = None
  model: Optional[str] = None
  notes: Optional[str] = None
  # Pose definitions are typically managed via their own CRUD or through DeckTypeDefinitionCreate
