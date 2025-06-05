# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""Define SQLAlchemy ORM models for deck management.

praxis/database_models/deck_management_orm.py

This module contains ORM models for managing deck configurations, positions, and types.
These models represent the structure of deck configurations, positions within those
configurations, and definitions of deck types, including their positions and layout
definitions. The models are designed to work with SQLAlchemy and provide a
consistent interface for interacting with the database.

ORM models include:
- DeckConfigurationOrm: Represents a named deck layout configuration.
- DeckConfigurationPositionItemOrm: Represents a specific resource placed at a position
  within a deck configuration.
- DeckPositionDefinitionOrm: Defines a specific position (location) on a type of deck.
- DeckTypeDefinitionOrm: Defines a type of deck, mapping to a PyLabRobot deck class.

"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
  JSON,
  UUID,
  DateTime,
  Float,
  ForeignKey,
  Integer,
  String,
  Text,
  UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from praxis.backend.utils.db import Base


class DeckConfigurationOrm(Base):
  """Represent a named deck layout configuration.

  This ORM model defines a specific arrangement of resources on a deck,
  associating it with a physical deck and containing a collection
  of `DeckConfigurationPositionItemOrm` entries.

  Attributes:
      id (int): Primary key, unique identifier for the deck configuration.
      name (str): A unique, human-readable name for the deck layout.
      deck_id (UUID): Foreign key to the `MachineOrm` representing
          the physical deck associated with this layout.
      description (Optional[str]): An optional description of the deck layout.
      created_at (Optional[datetime]): Timestamp when the record was created.
      updated_at (Optional[datetime]): Timestamp when the record was last updated.
      deck_machine (relationship): Establishes a relationship to the
          `MachineOrm` representing the deck parent.
      position_items (relationship): Establishes a one-to-many relationship to
          `DeckConfigurationPositionItemOrm` instances, representing the resources
          placed on this deck configuration.

  """

  __tablename__ = "deck_configurations"

  id: Mapped[UUID] = mapped_column(UUID, primary_key=True, index=True)

  python_fqn: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="The fully qualified Python name of the deck class.",
  )

  name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)

  deck_id: Mapped[UUID] = mapped_column(
    UUID, ForeignKey("resources.id"), nullable=False
  )
  description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

  created_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )
  updated_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
  )

  deck_type_definition_id: Mapped[Optional[UUID]] = mapped_column(
    UUID, ForeignKey("deck_type_definitions.id"), nullable=True, index=True
  )

  deck_parent_machine = relationship("MachineOrm", back_populates="deck_configurations")

  position_items = relationship(
    "DeckConfigurationPositionItemOrm",
    back_populates="deck_configuration",
    cascade="all, delete-orphan",
  )

  def __repr__(self):
    """Render string representation of the DeckConfigurationOrm instance."""
    return f"<DeckConfigurationOrm(id={self.id}, name='{self.name}')>"


class DeckConfigurationPositionItemOrm(Base):
  """Represent a specific resource placed at a position within a deck configuration.

  This ORM model links a `ResourceInstanceOrm` to a particular `position_id`
  (e.g., "A1", "SLOT_7") within a `DeckConfigurationOrm`. It can also
  optionally store the `expected_resource_definition_name` for validation
  purposes.

  Attributes:
      id (int): Primary key, unique identifier for the position item.
      deck_configuration_id (int): Foreign key to the parent
          `DeckConfigurationOrm`.
      position_id (str): The identifier for the position on the deck (e.g., "A1",
          "SLOT_7").
      resource_instance_id (int): Foreign key to the `ResourceInstanceOrm`
          representing the physical resource placed at this position.
      expected_resource_definition_name (Optional[str]): Foreign key to the
          `ResourceDefinitionCatalogOrm` representing the expected type of
          resource for this position in this layout.
      deck_position_definition_id (Optional[int]): Foreign key to a specific
          `DeckPositionDefinitionOrm` if this position item corresponds to a predefined
          position on the deck type.
      deck_configuration (relationship): Establishes a relationship to the
          parent `DeckConfigurationOrm`.
      resource_instance (relationship): Establishes a relationship to the
          `ResourceInstanceOrm` placed at this position.
      expected_resource_definition (relationship): Establishes a relationship
          to the `ResourceDefinitionCatalogOrm` for expected resource type.
      deck_position_definition (relationship): Establishes a relationship to the
          `DeckPositionDefinitionOrm` for the specific position definition.

  """

  __tablename__ = "deck_configuration_position_items"

  id: Mapped[UUID] = mapped_column(UUID, primary_key=True, index=True)
  deck_configuration_id: Mapped[UUID] = mapped_column(
    UUID, ForeignKey("deck_configurations.id"), nullable=False
  )
  position_id: Mapped[str] = mapped_column(
    String, nullable=False, comment="Position name on the deck (e.g., A1, SLOT_7)"
  )

  # This links to a specific physical piece of resource
  resource_instance_id: Mapped[UUID] = mapped_column(
    UUID, ForeignKey("resource_instances.id"), nullable=False
  )

  # Optional: for validation, store the expected type of resource for this
  # position in this layout
  expected_resource_definition_name: Mapped[Optional[UUID]] = mapped_column(
    UUID,
    ForeignKey("resource_definition_catalog.name"),
    nullable=True,
  )

  deck_position_definition_id: Mapped[Optional[UUID]] = mapped_column(
    UUID, ForeignKey("deck_position_definitions.id"), nullable=True, index=True
  )

  deck_configuration = relationship(
    "DeckConfigurationOrm", back_populates="position_items"
  )
  resource_instance = relationship(
    "ResourceInstanceOrm", back_populates="deck_configuration_items"
  )
  expected_resource_definition = relationship(
    "ResourceDefinitionCatalogOrm"
  )  # Simple relationship
  deck_position_definition = relationship("DeckPositionDefinitionOrm")

  __table_args__ = (
    UniqueConstraint(
      "deck_configuration_id", "position_id", name="uq_deck_position_item"
    ),
  )

  def __repr__(self):
    """Render string representation of the DeckConfigurationPositionItemOrm instance."""
    return (
      f"<DeckConfigurationPositionItemOrm(deck_config_id="
      f"{self.deck_configuration_id}, position='{self.position_id}', "
      f"lw_instance_id={self.resource_instance_id})>"
    )


class DeckPositionDefinitionOrm(Base):
  """Define a specific position (location) on a type of deck.

  This ORM model describes a predefined position or slot on a `DeckTypeDefinitionOrm`,
  including its nominal coordinates and what types of resources it can accept.

  Attributes:
      id (int): Primary key, unique identifier for the position definition.
      deck_type_definition_id (int): Foreign key to the `DeckTypeDefinitionOrm`
          this position belongs to.
      position_id (str): The unique identifier for this position within its deck type
          (e.g., "A1", "trash_position").
      nominal_x_mm (Optional[float]): The nominal X coordinate of the position's
          origin in millimeters, relative to the deck.
      nominal_y_mm (Optional[float]): The nominal Y coordinate of the position's
          origin in millimeters, relative to the deck.
      nominal_z_mm (Optional[float]): The nominal Z coordinate of the position's
          origin in millimeters, relative to the deck (often the deck surface
          at this position).
      accepted_resource_categories_json (Optional[list[str]]): A JSON array
          of resource categories (e.g., ["PLATE", "TIP_RACK"]) that this position
          can accept.
      position_specific_details_json (Optional[dict[str, Any]]): A JSON object
          for additional, unstructured details specific to this position.
      deck_type_definition (relationship): Establishes a relationship to the
          parent `DeckTypeDefinitionOrm`.

  """

  __tablename__ = "deck_position_definitions"

  id: Mapped[UUID] = mapped_column(UUID, primary_key=True, autoincrement=True)
  deck_type_definition_id: Mapped[UUID] = mapped_column(
    UUID, ForeignKey("deck_type_definitions.id"), nullable=False
  )
  position_id: Mapped[UUID] = mapped_column(UUID, nullable=False)
  nominal_x_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  nominal_y_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  nominal_z_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  accepted_resource_categories_json: Mapped[Optional[list[str]]] = mapped_column(
    JSON, nullable=True
  )
  position_specific_details_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
    JSON, nullable=True
  )

  # Relationship
  deck_type_definition: Mapped["DeckTypeDefinitionOrm"] = relationship(
    back_populates="position_definitions"
  )

  # Unique constraint for position_id within a deck_type_definition
  __table_args__ = (
    UniqueConstraint(
      "deck_type_definition_id", "position_id", name="uq_deck_position_definition"
    ),
  )

  def __repr__(self):
    """Render string representation of the DeckPositionDefinitionOrm instance."""
    return (
      f"<DeckPositionDefinitionOrm(id={self.id}, name='{self.position_id}', "
      f"deck_type_id={self.deck_type_definition_id})>"
    )


class DeckTypeDefinitionOrm(Base):
  """Define a type of deck, mapping to a PyLabRobot deck class.

  This ORM model stores metadata and configuration details for a specific
  type of deck, such as its PyLabRobot fully qualified name, display name,
  default dimensions, and methods for handling positions and constructor arguments.

  Attributes:
      id (int): Primary key, unique identifier for the deck type definition.
      pylabrobot_deck_fqn (str): The unique fully qualified Python name of the
          PyLabRobot deck class (e.g., "pylabrobot.resources.Deck").
      display_name (str): A human-readable name for the deck type.
      plr_category (Optional[str]): The PyLabRobot category for the deck
          (e.g., "deck", "plate"). Defaults to "deck".
      default_size_x_mm (Optional[float]): The default X dimension of the deck
          in millimeters.
      default_size_y_mm (Optional[float]): The default Y dimension of the deck
          in millimeters.
      default_size_z_mm (Optional[float]): The default Z dimension (height) of
          the deck in millimeters.
      positioning_config_json (Optional[dict[str, Any]]): A JSON object
          representing the primary positioning strategy for this deck type.
      serialized_constructor_args_json (Optional[dict[str, Any]]): A JSON
          object representing serialized constructor arguments for PyLabRobot
          instantiation.
      serialized_assignment_methods_json (Optional[dict[str, Any]]): A JSON
          object representing serialized assignment methods for PyLabRobot
          instantiation.
      serialized_constructor_hints_json (Optional[dict[str, Any]]): A
          JSON object representing serialized layout hints for PyLabRobot
          constructor.
      additional_properties_json (Optional[dict[str, Any]]): A JSON object
          for additional, unstructured properties.
      position_definitions (relationship): Establishes a one-to-many relationship
          to `DeckPositionDefinitionOrm` instances associated with this deck type.

  """

  __tablename__ = "deck_type_definitions"

  id: Mapped[UUID] = mapped_column(UUID, primary_key=True, autoincrement=True)
  pylabrobot_deck_fqn: Mapped[str] = mapped_column(
    String, unique=True, nullable=False, index=True
  )
  display_name: Mapped[str] = mapped_column(String, nullable=False)
  plr_category: Mapped[Optional[str]] = mapped_column(
    String, default="deck"
  )  # If PLR provides it, could be nullable=False
  default_size_x_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  default_size_y_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  default_size_z_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

  positioning_config_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
    JSON,
    nullable=True,
    comment="JSON representation of the primary positioning strategy for this deck "
    "type.",
  )

  serialized_constructor_args_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
    JSON, nullable=True
  )
  serialized_assignment_methods_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
    JSON, nullable=True
  )
  serialized_constructor_hints_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
    JSON, nullable=True
  )
  additional_properties_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
    JSON, nullable=True
  )

  # Relationships
  position_definitions: Mapped[list[DeckPositionDefinitionOrm]] = relationship(
    back_populates="deck_type_definition", cascade="all, delete-orphan"
  )

  def __repr__(self):
    """Render string representation of the DeckTypeDefinitionOrm instance."""
    return (
      f"<DeckTypeDefinitionOrm(id={self.id}, "
      f"fqn='{self.pylabrobot_deck_fqn}', name='{self.display_name}')>"
    )
