# pylint: disable=too-few-public-methods,missing-class-docstring
"""Unified SQLModel definitions for Deck, DeckDefinition, and DeckPositionDefinition."""

from typing import Any
import uuid

from sqlmodel import Field, SQLModel

from praxis.backend.models.domain.resource import ResourceBase
from praxis.backend.models.domain.sqlmodel_base import PraxisBase, json_field


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
    pylabrobot_position_type_name: str | None = Field(default=None, description="PyLabRobot position type")
    accepts_tips: bool | None = Field(default=None, description="Whether position accepts tips")
    accepts_plates: bool | None = Field(default=None, description="Whether position accepts plates")
    accepts_tubes: bool | None = Field(default=None, description="Whether position accepts tubes")
    notes: str | None = Field(default=None, description="Additional notes for the position")


class DeckPositionDefinition(DeckPositionDefinitionBase, table=True):
    """DeckPositionDefinition ORM model - defines a position on a deck type."""

    __tablename__ = "deck_position_definitions"

    allowed_resource_definition_names: list[str] | None = json_field(
        default=None, description="List of allowed resource definition names"
    )
    compatible_resource_fqns: dict[str, Any] | None = json_field(
        default=None, description="Compatible resource FQNs"
    )

    # Foreign keys
    deck_type_id: uuid.UUID = Field(
        foreign_key="deck_definition_catalog.accession_id", index=True
    )

    # Relationships (commented out to avoid circular imports during initial migration)
    # deck_type: "DeckDefinition" = Relationship(back_populates="positions")


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
    default_size_x_mm: float | None = Field(default=None, description="Default size in X dimension (mm)")
    default_size_y_mm: float | None = Field(default=None, description="Default size in Y dimension (mm)")
    default_size_z_mm: float | None = Field(default=None, description="Default size in Z dimension (mm)")


class DeckDefinition(DeckDefinitionBase, table=True):
    """DeckDefinition ORM model - catalog of deck types."""

    __tablename__ = "deck_definition_catalog"

    serialized_constructor_args_json: dict[str, Any] | None = json_field(
        default=None, description="Serialized constructor arguments"
    )
    serialized_assignment_methods_json: dict[str, Any] | None = json_field(
        default=None, description="Serialized assignment methods"
    )
    serialized_constructor_hints_json: dict[str, Any] | None = json_field(
        default=None, description="Serialized constructor hints"
    )
    additional_properties_json: dict[str, Any] | None = json_field(
        default=None, description="Additional properties"
    )
    positioning_config_json: dict[str, Any] | None = json_field(
        default=None, description="Positioning configuration"
    )

    # Foreign keys
    asset_requirement_accession_id: uuid.UUID | None = Field(
        default=None, foreign_key="protocol_asset_requirements.accession_id", index=True
    )

    # Relationships (commented out to avoid circular imports during initial migration)
    # positions: list["DeckPositionDefinition"] = Relationship(back_populates="deck_type")
    # deck: list["Deck"] = Relationship(back_populates="deck_type")
    # resource_definition: "ResourceDefinition | None" = Relationship(back_populates="deck_definition")
    # machine_definition: "MachineDefinition | None" = Relationship(back_populates="deck_definition")


class DeckDefinitionCreate(DeckDefinitionBase):
    """Schema for creating a DeckDefinition."""
    pass


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
    pass


class Deck(DeckBase):
    """Deck schema - represents a physical deck instance (extends Resource).

    Note: This is a schema class for API validation. The actual ORM table
    is defined in praxis.backend.models.orm.deck.DeckOrm using
    SQLAlchemy's polymorphic joined table inheritance.

    SQLModel doesn't support multi-table inheritance with dict fields properly,
    so we use schema-only classes here and keep the ORM separate.
    """

    # Foreign key references (for schema validation)
    parent_machine_accession_id: uuid.UUID | None = Field(
        default=None, description="Parent machine this deck belongs to"
    )
    deck_type_id: uuid.UUID | None = Field(
        default=None, description="Reference to deck definition catalog"
    )


class DeckCreate(DeckBase):
    """Schema for creating a Deck."""
    deck_type_id: uuid.UUID


class DeckRead(DeckBase):
    """Schema for reading a Deck (API response)."""
    accession_id: uuid.UUID


class DeckUpdate(SQLModel):
    """Schema for updating a Deck (partial update)."""

    name: str | None = None
    status: Any | None = None  # ResourceStatusEnum
    parent_machine_accession_id: uuid.UUID | None = None
