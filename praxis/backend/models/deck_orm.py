# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""Define SQLAlchemy ORM models for deck management.

praxis/database_models/deck_orm.py

This module contains ORM models for managing decks, positions,
and types. These models represent the structure of deck,
positions within those configurations, and definitions of deck types, including
their positions and instance definitions. The models are designed to work with
SQLAlchemy and provide a consistent interface for interacting with the database.

ORM models include:
- DeckPositionDefinitionOrm: Defines a specific position (location) on a type
  of deck.
- DeckTypeDefinitionOrm: Defines a type of deck, mapping to a PyLabRobot deck
  class.
- DeckOrm: Represents a physical deck instance in the lab.

"""

import uuid
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
  JSON,
  UUID,
  Float,
  ForeignKey,
  String,
  Text,
  UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from praxis.backend.models.resource_orm import ResourceOrm
from praxis.backend.models.timestamp_mixin import TimestampMixin
from praxis.backend.utils.db import Base

if TYPE_CHECKING:
  from praxis.backend.models.machine_orm import MachineOrm


class DeckOrm(ResourceOrm):
  """Represents a physical deck instance in the lab.

  A deck is a specialized resource that holds other resources and is
  typically part of a machine.

  Attributes:
      accession_id (uuid.UUID): Primary key, linked to the resource's accession_id.
      machine_id (Optional[uuid.UUID]): Foreign key to the machine this deck
          is part of.
      machine (Optional[MachineOrm]): Relationship to the parent machine.
      deck_type_id (uuid.UUID): Foreign key to the deck type definition.
      deck_type (DeckTypeDefinitionOrm): Relationship to the deck's type
          definition.

  """

  __tablename__ = "decks"
  __mapper_args__ = {"polymorphic_identity": "deck"}

  accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("resources.accession_id"),
    primary_key=True,
  )

  machine_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("machines.accession_id"),
    nullable=True,
    index=True,
  )
  machine: Mapped[Optional["MachineOrm"]] = relationship(
    "MachineOrm",
    back_populates="decks",
  )

  deck_type_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("deck_type_definitions.accession_id"),
    index=True,  # type: ignore
  )
  deck_type: Mapped["DeckTypeDefinitionOrm"] = relationship(
    "DeckTypeDefinitionOrm",
    back_populates="deck",
  )


class DeckTypeDefinitionOrm(TimestampMixin, Base):
  """Define a type of deck, its properties, and its positions.

  This ORM model stores definitions for different types of decks that can be
  used in the lab, such as a Hamilton STAR deck or an Opentrons OT-2 deck.
  It includes metadata like the corresponding PyLabRobot class and a
  description. Each deck type can have multiple physical instances represented
  by the `DeckOrm` model.

  Attributes:
      accession_id (uuid.UUID): Unique identifier for the deck type definition.
      name (str): A human-readable name for the deck type (e.g., "Hamilton STAR Deck").
      fqn (str): The fully qualified name of the PyLabRobot deck class
          (e.g., "pylabrobot.liquid_handling.backends.hamilton.STARDeck").
      description (Optional[str]): A detailed description of the deck type.
      plr_category (Optional[str]): The category of the deck type in PyLabRobot.
      default_size_x_mm (Optional[float]): The default size in X dimension in mm.
      default_size_y_mm (Optional[float]): The default size in Y dimension in mm.
      default_size_z_mm (Optional[float]): The default size in Z dimension in mm.
      serialized_constructor_args_json (Optional[dict[str, Any]]): JSON field to store
          serialized constructor arguments for the deck type.
      serialized_assignment_methods_json (Optional[dict[str, Any]]): JSON field to store
          serialized assignment methods for the deck type.
      serialized_constructor_hints_json (Optional[dict[str, Any]]): JSON field to store
          serialized constructor hints for the deck type.
      additional_properties_json (Optional[dict[str, Any]]): JSON field to store
          additional properties for the deck type.
      positioning_config_json (Optional[dict[str, Any]]): JSON field to store
          positioning configuration, such as the method and parameters for calculating
          coordinates from slot names.
      positions (list[DeckPositionDefinitionOrm]): A list of all defined
          positions (slots) available on this deck type.
      deck (list[DeckOrm]): A list of all physical deck instances
          of this type.

  """

  __tablename__ = "deck_type_definitions"
  __table_args__ = (UniqueConstraint("fqn", name="uq_deck_type_definitions_fqn"),)

  accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    primary_key=True,
    index=True,
    default=uuid.uuid4,
  )
  name: Mapped[str] = mapped_column(String, unique=True, index=True)
  fqn: Mapped[str] = mapped_column(String, nullable=False, index=True)
  description: Mapped[str | None] = mapped_column(Text, nullable=True)
  plr_category: Mapped[str | None] = mapped_column(String, nullable=True)
  default_size_x_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
  default_size_y_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
  default_size_z_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
  serialized_constructor_args_json: Mapped[dict[str, Any] | None] = mapped_column(
    JSON,
    nullable=True,
  )
  serialized_assignment_methods_json: Mapped[dict[str, Any] | None] = mapped_column(
    JSON,
    nullable=True,
  )
  serialized_constructor_hints_json: Mapped[dict[str, Any] | None] = mapped_column(
    JSON,
    nullable=True,
  )
  additional_properties_json: Mapped[dict[str, Any] | None] = mapped_column(
    JSON,
    nullable=True,
  )
  positioning_config_json: Mapped[dict[str, Any] | None] = mapped_column(
    JSON,
    nullable=True,
  )

  positions: Mapped[list["DeckPositionDefinitionOrm"]] = relationship(
    "DeckPositionDefinitionOrm",
    back_populates="deck_type",
    cascade="all, delete-orphan",
  )
  deck: Mapped[list["DeckOrm"]] = relationship(
    "DeckOrm",
    back_populates="deck_type",
  )


class DeckPositionDefinitionOrm(TimestampMixin, Base):
  """Define a position on a deck, such as a slot or location.

  This model represents a specific, addressable location on a deck type. For
  example, "A1" or "slot_1". It links a human-readable identifier to
  physical coordinates and specifies what types of resources can be placed
  there.

  Attributes:
      accession_id (uuid.UUID): Unique identifier for the deck position definition.
      deck_type_id (uuid.UUID): Foreign key to the parent deck type definition.
      position_accession_id (str): The human-readable identifier for the position
          (e.g., "A1", "trash_bin").
      x_coord (float): The x-coordinate of the position's center.
      y_coord (float): The y-coordinate of the position's center.
      z_coord (float): The z-coordinate of the position's center.
      compatible_resource_fqns (Optional[dict[str, Any]]): A JSON field to store a
          list or mapping of PyLabRobot resource FQNs that are compatible with
          this position.
      deck_type (DeckTypeDefinitionOrm): Relationship to the parent deck type.

  """

  __tablename__ = "deck_position_definitions"
  __table_args__ = (UniqueConstraint("deck_type_id", "position_accession_id", name="uq_deck_position"),)

  accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    primary_key=True,
    index=True,
    default=uuid.uuid4,
  )
  deck_type_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("deck_type_definitions.accession_id"),
    index=True,
  )  # type: ignore
  position_accession_id: Mapped[str] = mapped_column(String, nullable=False)

  x_coord: Mapped[float] = mapped_column(Float, nullable=False)
  y_coord: Mapped[float] = mapped_column(Float, nullable=False)
  z_coord: Mapped[float] = mapped_column(Float, nullable=False)

  # Reverting to compatible_resource_fqns as per user request
  compatible_resource_fqns: Mapped[dict[str, Any] | None] = mapped_column(
    JSON,
    nullable=True,
    comment="JSON field to store additional, position-specific details.",
  )

  deck_type: Mapped["DeckTypeDefinitionOrm"] = relationship(
    "DeckTypeDefinitionOrm",
    back_populates="positions",
  )
