from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Literal

from pydantic import AliasChoices, ConfigDict
from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel

from praxis.backend.models.domain.asset import Asset, AssetUpdate
from praxis.backend.models.domain.resource import ResourceBase

if TYPE_CHECKING:
  from praxis.backend.models.domain.resource import Resource
from praxis.backend.models.domain.sqlmodel_base import PraxisBase
from praxis.backend.utils.db import JsonVariant

if TYPE_CHECKING:
  from praxis.backend.models.domain.machine import Machine
  from praxis.backend.models.domain.resource import Resource, ResourceDefinition
  from praxis.backend.models.domain.workcell import Workcell


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

  position_accession_id: str | None = Field(
    default=None,
    index=True,
    description="Human-readable identifier for the position (e.g., 'A1', 'trash_bin')",
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
  __table_args__ = (UniqueConstraint("deck_type_id", "position_accession_id"),)

  allowed_resource_definition_names: list[str] | None = Field(
    default=None, sa_type=JsonVariant, description="List of allowed resource definition names"
  )
  compatible_resource_fqns: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Compatible resource FQNs"
  )

  # Foreign keys
  deck_type_id: uuid.UUID = Field(foreign_key="deck_definition_catalog.accession_id", index=True)

  # Relationship back to deck definition
  deck_type: DeckDefinition | None = Relationship(
    sa_relationship=relationship("DeckDefinition", back_populates="positions")
  )


class DeckPositionDefinitionCreate(DeckPositionDefinitionBase):
  """Schema for creating a DeckPositionDefinition."""

  deck_type_id: uuid.UUID | None = None
  deck_type_accession_id: uuid.UUID | None = None
  compatible_resource_fqns: dict[str, Any] | None = None


class DeckPositionDefinitionRead(DeckPositionDefinitionBase):
  """Schema for reading a DeckPositionDefinition (API response)."""

  deck_type_id: uuid.UUID | None = Field(
    default=None, validation_alias=AliasChoices("deck_type_id", "deck_type_accession_id")
  )
  deck_type_accession_id: uuid.UUID | None = Field(
    default=None, validation_alias=AliasChoices("deck_type_accession_id", "deck_type_id")
  )


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

  name: str = Field(default="", description="Human readable name for the deck type")
  fqn: str = Field(index=True, unique=True, description="Fully qualified name")
  version: str | None = Field(default=None, description="Version string for the deck type")
  positioning_config: PositioningConfig | None = Field(
    default=None,
    sa_column=Column(JsonVariant),
    description="Positioning configuration for the deck type",
  )
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
  parent: DeckDefinition | None = Relationship(
    sa_relationship=relationship(
      "DeckDefinition",
      back_populates="children",
      remote_side="DeckDefinition.accession_id",
    )
  )
  children: list[DeckDefinition] = Relationship(
    sa_relationship=relationship("DeckDefinition", back_populates="parent")
  )
  deck: list[Deck] = Relationship(sa_relationship=relationship("Deck", back_populates="deck_type"))

  # Position definitions relationship (exposed as `positions` to match existing callers)
  positions: list[DeckPositionDefinition] = Relationship(
    sa_relationship=relationship(
      "DeckPositionDefinition",
      back_populates="deck_type",
      cascade="all, delete-orphan",
      lazy="selectin",
    )
  )

  @property
  def decks(self) -> list[Deck]:
    """Compatibility property."""
    return self.deck


class DeckDefinitionCreate(DeckDefinitionBase):
  """Schema for creating a DeckDefinition."""

  position_definitions: list[DeckPositionDefinitionCreate] | None = None
  positions: list[DeckPositionDefinitionCreate] | None = None


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

  plr_state: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="PyLabRobot state blob for PLR devices"
  )

  model_config = ConfigDict(extra="allow")

  @property
  def deck_accession_id(self) -> uuid.UUID | None:
    """Compatibility property."""
    if "deck_accession_id" in self.__dict__:
      return self.__dict__["deck_accession_id"]
    if self.model_extra and "deck_accession_id" in self.model_extra:
      return self.model_extra["deck_accession_id"]
    return getattr(self, "deck_location_accession_id", None)

  @property
  def machine_id(self) -> uuid.UUID | None:
    """Compatibility property."""
    if "machine_id" in self.__dict__:
      return self.__dict__["machine_id"]
    if self.model_extra and "machine_id" in self.model_extra:
      return self.model_extra["machine_id"]
    return getattr(self, "parent_machine_accession_id", None)

  @property
  def deck_type_id(self) -> uuid.UUID | None:
    """Compatibility property."""
    if "deck_type_id" in self.__dict__:
      return self.__dict__["deck_type_id"]
    if self.model_extra and "deck_type_id" in self.model_extra:
      return self.model_extra["deck_type_id"]
    return getattr(self, "deck_type_accession_id", None)


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
  workcell_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Workcell this deck belongs to",
    foreign_key="workcells.accession_id",
  )

  # Relationships
  deck_type: DeckDefinition | None = Relationship(
    sa_relationship=relationship("DeckDefinition", back_populates="deck")
  )
  # ResourceDefinition is imported from resource.py
  # We need to use string forward ref if circular, but ResourceDefinition is in resource.py?
  resource_definition_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Reference to resource definition catalog",
    foreign_key="resource_definitions.accession_id",
  )

  @property
  def deck_accession_id(self) -> uuid.UUID | None:
    """Compatibility property."""
    if "deck_accession_id" in self.__dict__:
      return self.__dict__["deck_accession_id"]
    return getattr(self, "deck_location_accession_id", None)

  @property
  def machine_id(self) -> uuid.UUID | None:
    """Compatibility property."""
    if "machine_id" in self.__dict__:
      return self.__dict__["machine_id"]
    return getattr(
      self, "machine_location_accession_id", getattr(self, "parent_machine_accession_id", None)
    )

  resource_definition: ResourceDefinition | None = Relationship(
    sa_relationship=relationship("ResourceDefinition")
  )

  parent_machine: Machine | None = Relationship(
    sa_relationship=relationship(
      "Machine",
      back_populates="decks",
      primaryjoin="Deck.parent_machine_accession_id == Machine.accession_id",
    )
  )
  resources: list[Resource] = Relationship(
    sa_relationship=relationship("Resource", back_populates="deck")
  )
  workcell: Workcell | None = Relationship(
    sa_relationship=relationship("Workcell", back_populates="decks")
  )

  @machine_id.setter
  def machine_id(self, value: uuid.UUID | None):
    self.parent_machine_accession_id = value

  # Self-referential or parent relationships for compatibility
  parent: Machine | None = Relationship(
    sa_relationship=relationship(
      "Machine",
      primaryjoin="Deck.parent_machine_accession_id == Machine.accession_id",
      viewonly=True,
    )
  )
  children: list[Resource] = Relationship(sa_relationship=relationship("Resource", viewonly=True))


class DeckCreate(DeckBase):
  """Schema for creating a Deck."""

  machine_id: uuid.UUID | None = Field(
    default=None, validation_alias=AliasChoices("machine_id", "parent_machine_accession_id")
  )
  deck_type_id: uuid.UUID | None = Field(
    default=None, validation_alias=AliasChoices("deck_type_id", "deck_type_accession_id")
  )
  name: str | None = None


class DeckRead(DeckBase):
  """Schema for reading a Deck (API response)."""

  machine_id: uuid.UUID | None = Field(
    default=None, validation_alias=AliasChoices("machine_id", "parent_machine_accession_id")
  )
  deck_type_id: uuid.UUID | None = Field(
    default=None, validation_alias=AliasChoices("deck_type_id", "deck_type_accession_id")
  )
  deck_accession_id: uuid.UUID | None = Field(
    default=None, validation_alias=AliasChoices("deck_accession_id", "deck_location_accession_id")
  )


class DeckUpdate(AssetUpdate):
  """Schema for updating a Deck (partial update)."""

  name: str | None = None
  status: Any | None = None  # ResourceStatusEnum
  parent_machine_accession_id: uuid.UUID | None = None
  machine_id: uuid.UUID | None = None
