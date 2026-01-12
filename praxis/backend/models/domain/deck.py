from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Literal, Optional, List

from pydantic import ConfigDict
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.orm import relationship

from praxis.backend.models.domain.asset import Asset, AssetBase, AssetRead, AssetUpdate
from praxis.backend.models.domain.resource import ResourceBase

if TYPE_CHECKING:
  from praxis.backend.models.domain.resource import Resource
from praxis.backend.models.domain.sqlmodel_base import PraxisBase
from praxis.backend.utils.db import JsonVariant

if TYPE_CHECKING:
  from praxis.backend.models.domain.machine import Machine
  from praxis.backend.models.domain.resource import Resource, ResourceDefinition


class PositioningConfig(SQLModel):
  """Configuration for how positions are calculated/managed for this deck type."""

  method_name: str = Field(
    description="Name of the PyLabRobot deck method to call (e.g., 'rail_to_location')."
  )
  arg_name: str = Field(
    description="Name of the argument for the position in the method (e.g., 'rail', 'slot')."
  )
  arg_type: Literal["str", "int"] = Field(
    default="str",
    description="Expected type of the position argument ('str' or 'int').",
  )
  params: dict[str, Any] | None = Field(
    default=None,
    sa_type=JsonVariant,
    description="Additional parameters for the positioning method.",
  )


# =============================================================================
# Deck Position Definition
# =============================================================================


class DeckPositionDefinitionBase(PraxisBase):
  """Base schema for DeckPositionDefinition - shared fields for create/update/response."""

  position_accession_id: str = Field(
    index=True, description="Human-readable identifier for the position (e.g., 'A1', 'trash_bin')"
  )
  nominal_x_mm: float = Field(default=0.0, description="X-coordinate of the position's center")
  nominal_y_mm: float = Field(default=0.0, description="Y-coordinate of the position's center")
  nominal_z_mm: float = Field(default=0.0, description="Z-coordinate of the position's center")
  pylabrobot_position_type_name: str | None = Field(
    default=None, description="PyLabRobot position type"
  )
  accepts_tips: bool | None = Field(default=None, description="Whether position accepts tips")
  accepts_plates: bool | None = Field(default=None, description="Whether position accepts plates")
  accepts_tubes: bool | None = Field(default=None, description="Whether position accepts tubes")
  notes: str | None = Field(default=None, description="Additional notes for the position")


class DeckPositionDefinition(DeckPositionDefinitionBase, table=True):
  """DeckPositionDefinition ORM model - defines a position on a deck type."""

  __tablename__ = "deck_position_definitions"

  allowed_resource_definition_names: list[str] | None = Field(
    default=None, sa_type=JsonVariant, description="List of allowed resource definition names"
  )
  compatible_resource_fqns: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Compatible resource FQNs"
  )

  # Foreign keys
  deck_type_id: uuid.UUID = Field(foreign_key="deck_definition_catalog.accession_id", index=True)


class DeckPositionDefinitionCreate(DeckPositionDefinitionBase):
  """Schema for creating a DeckPositionDefinition."""

  deck_type_id: uuid.UUID


class DeckPositionDefinitionRead(DeckPositionDefinitionBase):
  """Schema for reading a DeckPositionDefinition (API response)."""

  accession_id: uuid.UUID


class DeckPositionDefinitionUpdate(SQLModel):
  """Schema for updating a DeckPositionDefinition (partial update)."""

  name: str | None = None
  position_accession_id: str | None = None
  nominal_x_mm: float | None = None
  nominal_y_mm: float | None = None
  nominal_z_mm: float | None = None
  pylabrobot_position_type_name: str | None = None
  accepts_tips: bool | None = None
  accepts_plates: bool | None = None
  accepts_tubes: bool | None = None
  notes: str | None = None


# =============================================================================
# Deck Definition (Catalog)
# =============================================================================


class DeckDefinitionBase(PraxisBase):
  """Base schema for DeckDefinition - shared fields for create/update/response."""

  fqn: str = Field(index=True, unique=True, description="Fully qualified name")
  description: str | None = Field(default=None, description="Description of the deck type")
  plr_category: str | None = Field(default=None, description="PyLabRobot category")
  default_size_x_mm: float | None = Field(
    default=None, description="Default size in X dimension (mm)"
  )
  default_size_y_mm: float | None = Field(
    default=None, description="Default size in Y dimension (mm)"
  )
  default_size_z_mm: float | None = Field(
    default=None, description="Default size in Z dimension (mm)"
  )


class DeckDefinition(DeckDefinitionBase, table=True):
  """DeckDefinition ORM model - catalog of deck types."""

  __tablename__ = "deck_definition_catalog"

  serialized_constructor_args_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Serialized constructor arguments"
  )
  serialized_assignment_methods_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Serialized assignment methods"
  )
  serialized_constructor_hints_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Serialized constructor hints"
  )
  additional_properties_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Additional properties"
  )
  positioning_config_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Positioning configuration"
  )

  # Foreign keys
  asset_requirement_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Asset requirement accession ID",
    foreign_key="protocol_asset_requirements.accession_id",
  )
  resource_definition_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Resource definition accession ID",
    foreign_key="resource_definitions.accession_id",
  )
  parent_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Parent asset accession ID (e.g. for nested checks)",
    foreign_key="deck_definition_catalog.accession_id",
  )
  # Relationships
  parent: Optional["DeckDefinition"] = Relationship(
    back_populates="children",
    sa_relationship_kwargs={
      "remote_side": "DeckDefinition.accession_id",
    },
  )
  children: List["DeckDefinition"] = Relationship(back_populates="parent")
  decks: List["Deck"] = Relationship(back_populates="deck_type")


class DeckDefinitionCreate(DeckDefinitionBase):
  """Schema for creating a DeckDefinition."""


class DeckDefinitionRead(DeckDefinitionBase):
  """Schema for reading a DeckDefinition (API response)."""

  accession_id: uuid.UUID


class DeckDefinitionUpdate(SQLModel):
  """Schema for updating a DeckDefinition (partial update)."""

  name: str | None = None
  fqn: str | None = None
  description: str | None = None
  plr_category: str | None = None
  default_size_x_mm: float | None = None
  default_size_y_mm: float | None = None
  default_size_z_mm: float | None = None


# =============================================================================
# Deck (Physical Instance)
# =============================================================================


class DeckBase(ResourceBase):
  """Base schema for Deck - shared fields for create/update/response."""


class Deck(DeckBase, Asset, table=True):
  """Deck table - represents a physical deck instance (extends Resource)."""

  __tablename__ = "decks"

  # Foreign key references
  parent_machine_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Parent machine this deck belongs to",
    foreign_key="machines.accession_id",
  )
  deck_type_id: uuid.UUID | None = Field(
    default=None,
    description="Reference to deck definition catalog",
    foreign_key="deck_definition_catalog.accession_id",
  )

  # Relationships
  deck_type: Optional[DeckDefinition] = Relationship(back_populates="decks")
  # ResourceDefinition is imported from resource.py
  # We need to use string forward ref if circular, but ResourceDefinition is in resource.py?
  resource_definition_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Reference to resource definition catalog",
    foreign_key="resource_definitions.accession_id",
  )
  resource_definition: Optional["ResourceDefinition"] = Relationship()

  parent_machine: Optional["Machine"] = Relationship(
    back_populates="decks",
    sa_relationship_kwargs={
      "primaryjoin": "Deck.parent_machine_accession_id == Machine.accession_id"
    },
  )
  resources: List["Resource"] = Relationship(back_populates="deck")


class DeckCreate(DeckBase):
  """Schema for creating a Deck."""

  deck_type_id: uuid.UUID
  parent_accession_id: uuid.UUID | None = None
  resource_definition_accession_id: uuid.UUID | None = None
  machine_id: uuid.UUID | None = None  # For compatibility with some tests/services
  plr_state: str | None = None


class DeckRead(DeckBase):
  """Schema for reading a Deck (API response)."""

  accession_id: uuid.UUID


class DeckUpdate(SQLModel):
  """Schema for updating a Deck (partial update)."""

  name: str | None = None
  status: Any | None = None  # ResourceStatusEnum
  parent_machine_accession_id: uuid.UUID | None = None
