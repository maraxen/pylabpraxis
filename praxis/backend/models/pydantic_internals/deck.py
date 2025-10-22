"""Pydantic models for deck-related entities in the Praxis application.

These models are used for data validation and serialization/deserialization of deck
configurations, positioning with "positions" which are human accessible location
accession_ids (e.g., slots or rails), and decks.
"""

from typing import Any, Literal

from pydantic import UUID7, BaseModel, Field, ConfigDict

from praxis.backend.models.pydantic_internals.plr_sync import (
  PLRTypeDefinitionCreate,
  PLRTypeDefinitionUpdate,
)

from .resource import (
  ResourceBase,
  ResourceCreate,
  ResourceResponse,
  ResourceUpdate,
)


class DeckBase(ResourceBase):
  """Base model for a deck."""

  machine_id: UUID7 | None = None
  deck_type_id: UUID7 | None = None


class DeckCreate(ResourceCreate, DeckBase):
  """Model for creating a new deck."""


class DeckUpdate(ResourceUpdate):
  """Model for updating a deck."""


class DeckResponse(ResourceResponse, DeckBase):
  """Model for API responses for a deck."""


class PositioningConfig(BaseModel):
  """Configuration for how positions are calculated/managed for this deck type.

  A general configuration for methods that follow the pattern:
  `deck.method_name(position_arg)` -> Coordinate

  """

  method_name: str = Field(
    ...,
    description="Name of the PyLabRobot deck method to call (e.g., 'rail_to_location',"
    "'slot_to_location').",
  )
  arg_name: str = Field(
    ...,
    description="Name of the argument for the position in the method (e.g., 'rail', 'slot').",
  )
  arg_type: Literal["str", "int"] = Field(
    "str",
    description="Expected type of the position argument ('str' or 'int').",
  )
  params: dict[str, Any] | None = Field(
    None,
    description="Additional parameters for the positioning method.",
  )
  model_config = ConfigDict(
    from_attributes=True,
  )


class DeckPositionDefinitionBase(BaseModel):
  """Define the base properties for a deck position definition.

  This model specifies the characteristics of a specific position or "position"
  on a deck, including its identifier, compatibility with different resource
  types, and physical location coordinates.
  """

  position_accession_id: str
  x_coord: float
  y_coord: float
  z_coord: float


class DeckPositionDefinitionCreate(DeckPositionDefinitionBase):
  """Model for creating a new deck position definition."""

  pylabrobot_position_type_name: str | None = Field(
    None,
    description="PyLabRobot specific position type name.",
  )
  allowed_resource_definition_names: list[str] | None = Field(
    None,
    description="List of specific resource definition names allowed at this position.",
  )
  accepts_tips: bool | None = Field(
    None,
    description="Indicates if the position accepts tips.",
  )
  accepts_plates: bool | None = Field(
    None,
    description="Indicates if the position accepts plates.",
  )
  accepts_tubes: bool | None = Field(
    None,
    description="Indicates if the position accepts tubes.",
  )
  notes: str | None = Field(None, description="Additional notes for the position.")

  compatible_resource_fqns: dict[str, Any] | None = Field(
    None,
    description="Additional, position-specific details as a JSON-serializable dictionary.",
  )


class DeckPositionDefinitionResponse(DeckPositionDefinitionBase):
  """Model for API responses for a deck position definition."""

  accession_id: UUID7
  deck_type_accession_id: UUID7
  model_config = ConfigDict(
    from_attributes=True,
  )


class DeckPositionDefinitionUpdate(BaseModel):
  """Model for updating a deck position definition."""


class DeckTypeDefinitionBase(BaseModel):
  """Base model for a deck type definition."""

  name: str
  fqn: str
  description: str | None = None
  positioning_config: PositioningConfig
  position_definitions: list[DeckPositionDefinitionCreate] | None = None
  plr_category: str | None = None
  default_size_x_mm: float | None = None
  default_size_y_mm: float | None = None
  default_size_z_mm: float | None = None
  serialized_constructor_args_json: dict[str, Any] | None = None
  serialized_assignment_methods_json: dict[str, Any] | None = None
  serialized_constructor_hints_json: dict[str, Any] | None = None
  additional_properties_json: dict[str, Any] | None = None


class DeckTypeDefinitionCreate(DeckTypeDefinitionBase, PLRTypeDefinitionCreate):
  """Model for creating a new deck type definition."""


class DeckTypeDefinitionResponse(DeckTypeDefinitionBase):
  """Model for API responses for a deck type definition."""

  accession_id: UUID7
  positions: list[DeckPositionDefinitionResponse]

  model_config = ConfigDict(
    from_attributes=True,
    use_enum_values=True,
  )


class DeckTypeDefinitionUpdate(PLRTypeDefinitionUpdate):
  """Model for updating a deck type definition."""

  description: str | None = None
  positioning_config: PositioningConfig | None = None
  position_definitions: list[DeckPositionDefinitionCreate] | None = None
  plr_category: str | None = None
  default_size_x_mm: float | None = None
  default_size_y_mm: float | None = None
  default_size_z_mm: float | None = None
  serialized_constructor_args_json: dict[str, Any] | None = None
  serialized_assignment_methods_json: dict[str, Any] | None = None
  serialized_constructor_hints_json: dict[str, Any] | None = None
  additional_properties_json: dict[str, Any] | None = None

  model_config = ConfigDict(
    from_attributes=True,
  )
