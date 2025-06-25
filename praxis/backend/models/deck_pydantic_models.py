"""Pydantic models for deck-related entities in the Praxis application.

These models are used for data validation and serialization/deserialization of deck
configurations, positioning with "positions" which are human accessible location
accession_ides (e.g., slots or rails), and decks.
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import UUID7, BaseModel, Field

from .resource_pydantic_models import (
  ResourceBase,
  ResourceCreate,
  ResourceResponse,
  ResourceUpdate,
)


class DeckBase(ResourceBase):
  """Base model for a deck."""

  # Do not override fqn, asset_type, or other fields from AssetBase unless necessary


class DeckCreate(ResourceCreate, DeckBase):
  """Model for creating a new deck."""

  pass


class DeckUpdate(ResourceUpdate):
  """Model for updating a deck."""

  pass


class DeckResponse(ResourceResponse, DeckBase):
  """Model for API responses for a deck."""

  pass


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
    """Pydantic configuration."""

    from_attributes = True


class DeckPositionDefinitionBase(BaseModel):
  """Define the base properties for a deck position definition.

  This model specifies the characteristics of a specific position or "position"
  on a deck, including its identifier, compatibility with different resource
  types, and physical location coordinates.
  """

  position_accession_id: str | int


class DeckPositionDefinitionCreate(DeckPositionDefinitionBase):
  """Model for creating a new deck position definition."""

  pass


class DeckPositionDefinitionResponse(DeckPositionDefinitionBase):
  """Model for API responses for a deck position definition."""

  accession_id: UUID7
  deck_type_accession_id: UUID7

  class Config:
    """Pydantic configuration."""

    from_attributes = True


class DeckPositionDefinitionUpdate(BaseModel):
  """Model for updating a deck position definition."""

  pass


class DeckTypeDefinitionBase(BaseModel):
  """Base model for a deck type definition."""

  name: str
  python_fqn: str
  description: Optional[str] = None
  positioning_config: PositioningConfig


class DeckTypeDefinitionCreate(DeckTypeDefinitionBase):
  """Model for creating a new deck type definition."""

  pass


class DeckTypeDefinitionResponse(DeckTypeDefinitionBase):
  """Model for API responses for a deck type definition."""

  accession_id: UUID7
  positions: List[DeckPositionDefinitionResponse]

  class Config:
    """Pydantic configuration."""

    from_attributes = True


class DeckTypeDefinitionUpdate(BaseModel):
  """Model for updating a deck type definition."""

  name: Optional[str] = None
  python_fqn: Optional[str] = None
  description: Optional[str] = None
  positioning_config: Optional[PositioningConfig] = None
