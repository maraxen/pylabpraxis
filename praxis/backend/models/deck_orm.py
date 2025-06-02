# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""Define SQLAlchemy ORM models for deck management.

praxis/database_models/deck_management_orm.py

This module contains ORM models for managing deck configurations, poses, and types.
These models represent the structure of deck configurations, poses within those
configurations, and definitions of deck types, including their poses and layout
definitions. The models are designed to work with SQLAlchemy and provide a
consistent interface for interacting with the database.

ORM models include:
- DeckConfigurationOrm: Represents a named deck layout configuration.
- DeckConfigurationPoseItemOrm: Represents a specific resource placed at a pose
  within a deck configuration.
- DeckPoseDefinitionOrm: Defines a specific pose (location) on a type of deck.
- DeckTypeDefinitionOrm: Defines a type of deck, mapping to a PyLabRobot deck class.

"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
  JSON,
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
  associating it with a physical deck machine and containing a collection
  of `DeckConfigurationPoseItemOrm` entries.

  Attributes:
      id (int): Primary key, unique identifier for the deck configuration.
      layout_name (str): A unique, human-readable name for the deck layout.
      deck_id (int): Foreign key to the `MachineOrm` representing
          the physical deck associated with this layout.
      description (Optional[str]): An optional description of the deck layout.
      created_at (Optional[datetime]): Timestamp when the record was created.
      updated_at (Optional[datetime]): Timestamp when the record was last updated.
      deck_machine (relationship): Establishes a relationship to the
          `MachineOrm` representing the deck.
      pose_items (relationship): Establishes a one-to-many relationship to
          `DeckConfigurationPoseItemOrm` instances, representing the resources
          placed on this deck configuration.

  """

  __tablename__ = "deck_configurations"

  id: Mapped[int] = mapped_column(
    Integer, primary_key=True, index=True
  )  # praxis_deck_config_id
  layout_name: Mapped[str] = mapped_column(
    String, nullable=False, unique=True, index=True
  )

  # A Deck itself is a Machine
  deck_id: Mapped[int] = mapped_column(
    Integer, ForeignKey("machines.id"), nullable=False
  )
  description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

  created_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )
  updated_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
  )

  deck_machine = relationship("MachineOrm", back_populates="deck_configurations")
  pose_items = relationship(
    "DeckConfigurationPoseItemOrm",
    back_populates="deck_configuration",
    cascade="all, delete-orphan",
  )

  def __repr__(self):
    """Render string representation of the DeckConfigurationOrm instance."""
    return f"<DeckConfigurationOrm(id={self.id}, name='{self.layout_name}')>"


class DeckConfigurationPoseItemOrm(Base):
  """Represent a specific resource placed at a pose within a deck configuration.

  This ORM model links a `ResourceInstanceOrm` to a particular `pose_id`
  (e.g., "A1", "SLOT_7") within a `DeckConfigurationOrm`. It can also
  optionally store the `expected_resource_definition_name` for validation
  purposes.

  Attributes:
      id (int): Primary key, unique identifier for the pose item.
      deck_configuration_id (int): Foreign key to the parent
          `DeckConfigurationOrm`.
      pose_id (str): The identifier for the pose on the deck (e.g., "A1",
          "SLOT_7").
      resource_instance_id (int): Foreign key to the `ResourceInstanceOrm`
          representing the physical resource placed at this pose.
      expected_resource_definition_name (Optional[str]): Foreign key to the
          `ResourceDefinitionCatalogOrm` representing the expected type of
          resource for this pose in this layout.
      deck_pose_definition_id (Optional[int]): Foreign key to a specific
          `DeckPoseDefinitionOrm` if this pose item corresponds to a predefined
          pose on the deck type.
      deck_configuration (relationship): Establishes a relationship to the
          parent `DeckConfigurationOrm`.
      resource_instance (relationship): Establishes a relationship to the
          `ResourceInstanceOrm` placed at this pose.
      expected_resource_definition (relationship): Establishes a relationship
          to the `ResourceDefinitionCatalogOrm` for expected resource type.
      deck_pose_definition (relationship): Establishes a relationship to the
          `DeckPoseDefinitionOrm` for the specific pose definition.

  """

  __tablename__ = "deck_configuration_pose_items"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  deck_configuration_id: Mapped[int] = mapped_column(
    Integer, ForeignKey("deck_configurations.id"), nullable=False
  )
  pose_id: Mapped[str] = mapped_column(
    String, nullable=False, comment="Pose name on the deck (e.g., A1, SLOT_7)"
  )

  # This links to a specific physical piece of resource
  resource_instance_id: Mapped[int] = mapped_column(
    Integer, ForeignKey("resource_instances.id"), nullable=False
  )

  # Optional: for validation, store the expected type of resource for this
  # pose in this layout
  expected_resource_definition_name: Mapped[Optional[str]] = mapped_column(
    String,
    ForeignKey("resource_definition_catalog.pylabrobot_definition_name"),
    nullable=True,
  )
  deck_pose_definition_id: Mapped[Optional[int]] = mapped_column(
    ForeignKey("deck_pose_definitions.id"), nullable=True, index=True
  )

  deck_configuration = relationship("DeckConfigurationOrm", back_populates="pose_items")
  resource_instance = relationship(
    "ResourceInstanceOrm", back_populates="deck_configuration_items"
  )
  expected_resource_definition = relationship(
    "ResourceDefinitionCatalogOrm"
  )  # Simple relationship
  deck_pose_definition = relationship("DeckPoseDefinitionOrm")

  __table_args__ = (
    UniqueConstraint("deck_configuration_id", "pose_id", name="uq_deck_pose_item"),
  )

  def __repr__(self):
    """Render string representation of the DeckConfigurationPoseItemOrm instance."""
    return (
      f"<DeckConfigurationPoseItemOrm(deck_config_id="
      f"{self.deck_configuration_id}, pose='{self.pose_id}', "
      f"lw_instance_id={self.resource_instance_id})>"
    )


class DeckPoseDefinitionOrm(Base):
  """Define a specific pose (location) on a type of deck.

  This ORM model describes a predefined position or slot on a `DeckTypeDefinitionOrm`,
  including its nominal coordinates and what types of resources it can accept.

  Attributes:
      id (int): Primary key, unique identifier for the pose definition.
      deck_type_definition_id (int): Foreign key to the `DeckTypeDefinitionOrm`
          this pose belongs to.
      pose_id (str): The unique identifier for this pose within its deck type
          (e.g., "A1", "trash_pose").
      nominal_x_mm (Optional[float]): The nominal X coordinate of the pose's
          origin in millimeters, relative to the deck.
      nominal_y_mm (Optional[float]): The nominal Y coordinate of the pose's
          origin in millimeters, relative to the deck.
      nominal_z_mm (Optional[float]): The nominal Z coordinate of the pose's
          origin in millimeters, relative to the deck (often the deck surface
          at this pose).
      accepted_resource_categories_json (Optional[list[str]]): A JSON array
          of resource categories (e.g., ["PLATE", "TIP_RACK"]) that this pose
          can accept.
      pose_specific_details_json (Optional[dict[str, Any]]): A JSON object
          for additional, unstructured details specific to this pose.
      deck_type_definition (relationship): Establishes a relationship to the
          parent `DeckTypeDefinitionOrm`.

  """

  __tablename__ = "deck_pose_definitions"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
  deck_type_definition_id: Mapped[int] = mapped_column(
    ForeignKey("deck_type_definitions.id"), nullable=False
  )
  pose_id: Mapped[str] = mapped_column(String, nullable=False)
  nominal_x_mm: Mapped[Optional[float]] = mapped_column(
    Float, nullable=True
  )  # From plan, but PLR might always provide these
  nominal_y_mm: Mapped[Optional[float]] = mapped_column(
    Float, nullable=True
  )  # From plan
  nominal_z_mm: Mapped[Optional[float]] = mapped_column(
    Float, nullable=True
  )  # From plan
  accepted_resource_categories_json: Mapped[Optional[list[str]]] = mapped_column(
    JSON, nullable=True
  )
  pose_specific_details_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
    JSON, nullable=True
  )

  # Relationship
  deck_type_definition: Mapped["DeckTypeDefinitionOrm"] = relationship(
    back_populates="pose_definitions"
  )

  # Unique constraint for pose_id within a deck_type_definition
  __table_args__ = (
    UniqueConstraint(
      "deck_type_definition_id", "pose_id", name="uq_deck_pose_definition"
    ),
  )

  def __repr__(self):
    """Render string representation of the DeckPoseDefinitionOrm instance."""
    return (
      f"<DeckPoseDefinitionOrm(id={self.id}, name='{self.pose_id}', "
      f"deck_type_id={self.deck_type_definition_id})>"
    )


class DeckTypeDefinitionOrm(Base):
  """Define a type of deck, mapping to a PyLabRobot deck class.

  This ORM model stores metadata and configuration details for a specific
  type of deck, such as its PyLabRobot fully qualified name, display name,
  default dimensions, and methods for handling poses and constructor arguments.

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
      serialized_to_location_method_json (Optional[dict[str, Any]]): A JSON
          object representing how to serialize a location method.
      pose_to_location_method_name (Optional[str]): The name of the method
          used to convert a pose to a location on the deck.
      pose_argument_name (Optional[str]): The name of the argument used for
          pose in the location conversion method.
      serialized_constructor_args_json (Optional[dict[str, Any]]): A JSON
          object representing serialized constructor arguments for PyLabRobot
          instantiation.
      serialized_assignment_methods_json (Optional[dict[str, Any]]): A JSON
          object representing serialized assignment methods for PyLabRobot
          instantiation.
      serialized_constructor_layout_hints_json (Optional[dict[str, Any]]): A
          JSON object representing serialized layout hints for PyLabRobot
          constructor.
      additional_properties_json (Optional[dict[str, Any]]): A JSON object
          for additional, unstructured properties.
      pose_definitions (relationship): Establishes a one-to-many relationship
          to `DeckPoseDefinitionOrm` instances associated with this deck type.

  """

  __tablename__ = "deck_type_definitions"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
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
  serialized_to_location_method_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
    JSON, nullable=True
  )
  pose_to_location_method_name: Mapped[Optional[str]] = mapped_column(
    String, nullable=True, comment="Name of the method to convert pose to location"
  )
  pose_argument_name: Mapped[Optional[str]] = mapped_column(
    String, nullable=True, comment="Name of the argument for pose in the method"
  )
  pose_argument_type: Mapped[Optional[str]] = mapped_column(
    String,
    nullable=True,
    comment="Type of the pose argument in the method (e.g., 'str', 'int')",
  )

  serialized_constructor_args_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
    JSON, nullable=True
  )
  serialized_assignment_methods_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
    JSON, nullable=True
  )
  serialized_constructor_layout_hints_json: Mapped[Optional[dict[str, Any]]] = (
    mapped_column(JSON, nullable=True)
  )
  additional_properties_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
    JSON, nullable=True
  )

  # Relationships
  pose_definitions: Mapped[list[DeckPoseDefinitionOrm]] = relationship(
    back_populates="deck_type_definition", cascade="all, delete-orphan"
  )

  def __repr__(self):
    """Render string representation of the DeckTypeDefinitionOrm instance."""
    return (
      f"<DeckTypeDefinitionOrm(id={self.id}, "
      f"fqn='{self.pylabrobot_deck_fqn}', name='{self.display_name}')>"
    )
