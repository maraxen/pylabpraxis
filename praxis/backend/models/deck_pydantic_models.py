"""Pydantic models for deck-related entities in the Praxis application.

These models are used for data validation and serialization/deserialization of deck
configurations, positioning with "positions" which are human accessible location accession_ides
(e.g., slots or rails), and decks.
"""

import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import UUID7, BaseModel, Field


class PositioningConfig(BaseModel):
  """Configuration for how positions are calculated/managed for this deck type.

  A general configuration for methods that follow the pattern:
  `deck_instance.method_name(position_arg)` -> Coordinate

  """

  method_name: str = Field(
    ...,
    description="Name of the PyLabRobot deck method to call (e.g., 'rail_to_location',"
    "'slot_to_location').",
  )
  arg_name: str = Field(
    ...,
    description="Name of the argument for the position in the method (e.g., 'rail', "
    "'slot').",
  )
  arg_type: Literal["str", "int"] = Field(
    "str", description="Expected type of the position argument ('str' or 'int')."
  )
  params: Optional[Dict[str, Any]] = Field(
    None, description="Additional parameters for the positioning method."
  )

  class Config:
    """Configuration for Pydantic model behavior."""

    from_attributes = True


class DeckPositionResourceBase(BaseModel):
  """Define the base properties for an item placed on a deck position.

  This model captures the essential information about an item's placement,
  including its position identifier and optional associated resource details.
  """

  position_accession_id: str | int | UUID7
  resource_instance_accession_id: Optional[UUID7] = None
  expected_resource_definition_name: Optional[UUID7] = None

  class Config:
    """Configuration for Pydantic model behavior."""

    from_attributes = True


class DeckPositionResourceCreate(DeckPositionResourceBase):
  """Represent a deck position item for creation requests.

  This model inherits all properties from `DeckPositionResourceBase` and is used
  specifically when creating new position item entries.
  """

  pass


class DeckPositionResourceResponse(DeckPositionResourceBase):
  """Represent a deck position item for API responses.

  This model extends `DeckPositionResourceBase` by adding system-generated identifiers,
  suitable for client-facing responses.
  """

  item_accession_id: UUID7
  deck_instance_accession_id: UUID7


class DeckInstanceBase(BaseModel):
  """Define the base properties for a deck instance.

  This model includes fundamental attributes like deck name, associated deck,
  and an optional description, serving as a base for more specific deck models.
  """

  deck_name: str
  deck_accession_id: UUID7
  python_fqn: str
  description: Optional[str] = None

  class Config:
    """Configuration for Pydantic model behavior."""

    from_attributes = True


class DeckInstanceCreate(DeckInstanceBase):
  """Represent a deck for creation requests.

  This model extends `DeckInstanceBase` by allowing the inclusion of
  `DeckPositionResourceCreate` instances, enabling the definition of a deck's
  contents upon creation.
  """

  position_items: Optional[List[DeckPositionResourceCreate]] = []


class DeckInstanceUpdate(BaseModel):
  """Represent a deck instance for update requests.

  This model provides optional fields for updating various properties of a
  deck instance, including its name, associated deck, description, and
  its constituent position items.
  """

  deck_name: Optional[str] = None
  deck_accession_id: Optional[UUID7] = None
  description: Optional[str] = None
  position_items: Optional[List[DeckPositionResourceCreate]] = None


class DeckInstanceResponse(DeckInstanceBase):
  """Represent a deck instance for API responses.

  This model extends `DeckInstanceBase` by including system-generated identifiers,
  associated position items (as `DeckPositionResourceResponse`), and timestamps for
  creation and last update, suitable for client-facing responses.
  """

  id: UUID7
  position_items: List[DeckPositionResourceResponse] = []
  created_at: Optional[datetime.datetime] = None
  updated_at: Optional[datetime.datetime] = None


class DeckPositionDefinitionBase(BaseModel):
  """Define the base properties for a deck position definition.

  This model specifies the characteristics of a specific position or "position"
  on a deck, including its identifier, compatibility with different resource
  types, and physical location coordinates.
  """

  position_accession_id: str | int
  uuid: Optional[UUID7] = None
  pylabrobot_position_type_name: Optional[str] = None
  allowed_resource_categories: Optional[List[str]] = None
  allowed_resource_definition_names: Optional[List[UUID7]] = None
  accepts_tips: Optional[bool] = None
  accepts_plates: Optional[bool] = None
  accepts_tubes: Optional[bool] = None
  location_x_mm: Optional[float] = None
  location_y_mm: Optional[float] = None
  location_z_mm: Optional[float] = None
  notes: Optional[str] = None

  class Config:
    """Configuration for Pydantic model behavior."""

    from_attributes = True
    use_enum_values = True


class DeckPositionDefinitionCreate(DeckPositionDefinitionBase):
  """Represent a deck position definition for creation requests.

  This model inherits all properties from `DeckPositionDefinitionBase` and is used
  specifically when creating new position definition entries.
  """

  pass


class DeckPositionDefinitionResponse(DeckPositionDefinitionBase):
  """Represent a deck position definition for API responses.

  This model extends `DeckPositionDefinitionBase` by adding system-generated
  identifiers, a foreign key to its associated deck type definition, and
  timestamps for creation and last update, suitable for client-facing responses.
  """

  id: int
  deck_type_definition_accession_id: int  # Foreign Key to the DeckTypeDefinition
  created_at: Optional[datetime.datetime] = None
  updated_at: Optional[datetime.datetime] = None


class DeckPositionDefinitionUpdate(BaseModel):
  """Represent a deck position definition for update requests.

  This model provides optional fields for updating various properties of a
  deck position definition, such as its identifier, compatible resource types,
  and physical location details.
  """

  position_accession_id: Optional[str | int | UUID7] = None
  pylabrobot_position_type_name: Optional[str] = None
  allowed_resource_categories: Optional[List[str]] = None
  allowed_resource_definition_names: Optional[List[UUID7]] = None
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
  and methods for position-to-location mapping, along with descriptive metadata.
  """

  id: Optional[UUID7] = None
  python_fqn: str
  deck_type: str
  positioning_config: Optional[PositioningConfig] = Field(
    None,
    description="Configuration for the primary method to calculate positions on this \
      deck.",
  )
  description: Optional[str] = None
  manufacturer: Optional[str] = None
  model: Optional[str] = None
  notes: Optional[str] = None

  class Config:
    """Configuration for Pydantic model behavior."""

    from_attributes = True
    use_enum_values = True


class DeckTypeDefinitionCreate(DeckTypeDefinitionBase):
  """Represent a deck type definition for creation requests.

  This model extends `DeckTypeDefinitionBase` by allowing the inclusion of
  `DeckPositionDefinitionCreate` instances, enabling the definition of a deck type's
  associated positions upon creation.
  """

  position_definitions: Optional[List[DeckPositionDefinitionCreate]] = []


class DeckTypeDefinitionResponse(DeckTypeDefinitionBase):
  """Represent a deck type definition for API responses.

  This model extends `DeckTypeDefinitionBase` by including system-generated
  identifiers, associated position definitions (as `DeckPositionDefinitionResponse`),
  and timestamps for creation and last update, suitable for client-facing responses.
  """

  position_definitions: List[DeckPositionDefinitionResponse] = []
  created_at: Optional[datetime.datetime] = None
  updated_at: Optional[datetime.datetime] = None


class DeckTypeDefinitionUpdate(BaseModel):
  """Represent a deck type definition for update requests.

  This model provides optional fields for updating various properties of a
  deck type definition, such as its PyLabRobot class name, Praxis-specific name,
  and descriptive metadata. Position definitions are typically managed via their
  own CRUD operations or through `DeckTypeDefinitionCreate`.
  """

  python_fqn: Optional[str] = None
  deck_type: Optional[str] = None
  positioning_config: Optional[PositioningConfig] = None
  description: Optional[str] = None
  manufacturer: Optional[str] = None
  model: Optional[str] = None
  notes: Optional[str] = None


class DeckInfo(BaseModel):
  """Basic information about a deck."""

  id: UUID7 = Field(description="ORM ID of the MachineOrm for the deck")
  user_friendly_name: str = Field(description="User-assigned name for the deck")
  python_fqn: str = Field(
    description="PyLabRobot class name for the deck (e.g., 'Deck')"
  )
  current_status: str = Field(
    description="Current operational status of the deck (e.g., 'ONLINE', 'OFFLINE')"
  )
  # current_status: MachineStatusEnum # Alternative if enum is imported


class DeckResourceInfo(BaseModel):
  """Detailed information about a resource instance on the deck."""

  resource_instance_accession_id: UUID7 = Field(
    description="ORM ID of the ResourceInstanceOrm"
  )
  user_assigned_name: str = Field(
    description="User-assigned name for this specific resource instance"
  )
  name: str = Field(
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


class DeckPositionInfo(BaseModel):
  """Information about a single position on the deck."""

  name: str = Field(
    description="Identifier for the position (e.g., 'A1', 'position_1', \
      'trash_position')"
  )
  x_coordinate: Optional[float] = Field(
    None,
    description="X coordinate of the position's origin relative to the deck, in "
    "millimeters",
  )
  y_coordinate: Optional[float] = Field(
    None,
    description="Y coordinate of the position's origin relative to the deck, in "
    "millimeters",
  )
  z_coordinate: Optional[float] = Field(
    None,
    description="Z coordinate of the position's origin relative to the deck, in "
    "millimeters (often the deck surface at this position)",
  )
  resource: Optional[DeckResourceInfo] = Field(
    None, description="Resource instance currently occupying this position, if any"
  )


class DeckStateResponse(BaseModel):
  """Represents the complete state of a deck, including its positions and resource."""

  deck_accession_id: UUID7 = Field(description="ORM ID of the MachineOrm for the deck")
  name: str = Field(description="User-assigned name for the deck")
  python_fqn: str = Field(description="PyLabRobot class name for the deck")
  size_x_mm: Optional[float] = Field(
    None, description="Overall physical dimension X of the deck in millimeters"
  )
  size_y_mm: Optional[float] = Field(
    None, description="Overall physical dimension Y of the deck in millimeters"
  )
  size_z_mm: Optional[float] = Field(
    None,
    description="Overall physical dimension Z of the deck in millimeters (e.g., "
    "height)",
  )
  positions: List[DeckPositionInfo] = Field(
    description="List of all positions defined on this deck"
  )


class DeckUpdateMessage(BaseModel):
  """Model for WebSocket messages broadcasting updates to the deck state."""

  deck_accession_id: UUID7 = Field(description="ORM ID of the deck that was updated")
  update_type: str = Field(
    description="Type of update (e.g., 'resource_added', 'resource_removed', "
    "'resource_updated', 'position_cleared')"
  )
  position_name: Optional[str] = Field(
    None, description="Name of the position affected by the update, if applicable"
  )
  resource_info: Optional[DeckResourceInfo] = Field(
    None,
    description="The new state of the resource in the position, or null if resource was "
    "removed",
  )
  timestamp: str = Field(
    default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat(),
    description="Timestamp of the update in ISO format (UTC)",
  )

  class Config:
    """Configuration for Pydantic model."""

    # Ensure that default_factory works as expected
    validate_assignment = True
