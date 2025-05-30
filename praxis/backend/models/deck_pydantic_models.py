"""Pydantic models for deck-related entities in the Praxis application.

These models are used for data validation and serialization/deserialization of deck
configurations, positioning with "poses" which are human accessible location guides
(e.g., slots or rails), and layouts.
"""

import datetime
from typing import List, Optional

from pydantic import BaseModel


class DeckPoseItemBase(BaseModel):
  """Define the base properties for an item placed on a deck pose.

  This model captures the essential information about an item's placement,
  including its pose identifier and optional associated resource details.
  """

  pose_id: str | int
  resource_instance_id: Optional[int] = None
  expected_resource_definition_name: Optional[str] = None

  class Config:
    """Configuration for Pydantic model behavior."""

    orm_mode = True


class DeckPoseItemCreate(DeckPoseItemBase):
  """Represent a deck pose item for creation requests.

  This model inherits all properties from `DeckPoseItemBase` and is used
  specifically when creating new pose item entries.
  """

  pass


class DeckPoseItemResponse(DeckPoseItemBase):
  """Represent a deck pose item for API responses.

  This model extends `DeckPoseItemBase` by adding system-generated identifiers,
  suitable for client-facing responses.
  """

  item_id: int
  deck_configuration_id: int


class DeckLayoutBase(BaseModel):
  """Define the base properties for a deck layout.

  This model includes fundamental attributes like layout name, associated deck,
  and an optional description, serving as a base for more specific layout models.
  """

  layout_name: str
  deck_id: int
  description: Optional[str] = None

  class Config:
    """Configuration for Pydantic model behavior."""

    orm_mode = True


class DeckLayoutCreate(DeckLayoutBase):
  """Represent a deck layout for creation requests.

  This model extends `DeckLayoutBase` by allowing the inclusion of
  `DeckPoseItemCreate` instances, enabling the definition of a layout's
  contents upon creation.
  """

  pose_items: Optional[List[DeckPoseItemCreate]] = []


class DeckLayoutUpdate(BaseModel):
  """Represent a deck layout for update requests.

  This model provides optional fields for updating various properties of a
  deck layout, including its name, associated deck, description, and
  its constituent pose items.
  """

  layout_name: Optional[str] = None
  deck_id: Optional[int] = None
  description: Optional[str] = None
  pose_items: Optional[List[DeckPoseItemCreate]] = None


class DeckLayoutResponse(DeckLayoutBase):
  """Represent a deck layout for API responses.

  This model extends `DeckLayoutBase` by including system-generated identifiers,
  associated pose items (as `DeckPoseItemResponse`), and timestamps for
  creation and last update, suitable for client-facing responses.
  """

  id: int
  pose_items: List[DeckPoseItemResponse] = []
  created_at: Optional[datetime.datetime] = None
  updated_at: Optional[datetime.datetime] = None


class DeckPoseDefinitionBase(BaseModel):
  """Define the base properties for a deck pose definition.

  This model specifies the characteristics of a specific position or "pose"
  on a deck, including its identifier, compatibility with different resource
  types, and physical location coordinates.
  """

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
    """Configuration for Pydantic model behavior."""

    orm_mode = True
    use_enum_values = True


class DeckPoseDefinitionCreate(DeckPoseDefinitionBase):
  """Represent a deck pose definition for creation requests.

  This model inherits all properties from `DeckPoseDefinitionBase` and is used
  specifically when creating new pose definition entries.
  """

  pass


class DeckPoseDefinitionResponse(DeckPoseDefinitionBase):
  """Represent a deck pose definition for API responses.

  This model extends `DeckPoseDefinitionBase` by adding system-generated
  identifiers, a foreign key to its associated deck type definition, and
  timestamps for creation and last update, suitable for client-facing responses.
  """

  id: int
  deck_type_definition_id: int  # Foreign Key to the DeckTypeDefinition
  created_at: Optional[datetime.datetime] = None
  updated_at: Optional[datetime.datetime] = None


class DeckPoseDefinitionUpdate(BaseModel):
  """Represent a deck pose definition for update requests.

  This model provides optional fields for updating various properties of a
  deck pose definition, such as its identifier, compatible resource types,
  and physical location details.
  """

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
  """Define the base properties for a deck type definition.

  This model encapsulates the fundamental attributes of a specific type of
  deck, including its PyLabRobot class mapping, Praxis-specific name,
  and methods for pose-to-location mapping, along with descriptive metadata.
  """

  pylabrobot_class_name: str
  praxis_deck_type_name: str
  pose_arg_name: str
  pose_to_location_method_name: str
  description: Optional[str] = None
  manufacturer: Optional[str] = None
  model: Optional[str] = None
  notes: Optional[str] = None

  class Config:
    """Configuration for Pydantic model behavior."""

    orm_mode = True
    use_enum_values = True


class DeckTypeDefinitionCreate(DeckTypeDefinitionBase):
  """Represent a deck type definition for creation requests.

  This model extends `DeckTypeDefinitionBase` by allowing the inclusion of
  `DeckPoseDefinitionCreate` instances, enabling the definition of a deck type's
  associated poses upon creation.
  """

  pose_definitions: Optional[List[DeckPoseDefinitionCreate]] = []


class DeckTypeDefinitionResponse(DeckTypeDefinitionBase):
  """Represent a deck type definition for API responses.

  This model extends `DeckTypeDefinitionBase` by including system-generated
  identifiers, associated pose definitions (as `DeckPoseDefinitionResponse`),
  and timestamps for creation and last update, suitable for client-facing responses.
  """

  id: int
  pose_definitions: List[DeckPoseDefinitionResponse] = []
  created_at: Optional[datetime.datetime] = None
  updated_at: Optional[datetime.datetime] = None


class DeckTypeDefinitionUpdate(BaseModel):
  """Represent a deck type definition for update requests.

  This model provides optional fields for updating various properties of a
  deck type definition, such as its PyLabRobot class name, Praxis-specific name,
  and descriptive metadata. Pose definitions are typically managed via their
  own CRUD operations or through `DeckTypeDefinitionCreate`.
  """

  pylabrobot_class_name: Optional[str] = None
  praxis_deck_type_name: Optional[str] = None
  pose_arg_name: Optional[str] = None
  pose_to_location_method_name: Optional[str] = None
  description: Optional[str] = None
  manufacturer: Optional[str] = None
  model: Optional[str] = None
  notes: Optional[str] = None
  # Pose definitions are typically managed via their own CRUD or through
  # DeckTypeDefinitionCreate
