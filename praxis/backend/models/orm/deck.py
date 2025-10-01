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
from functools import partial
from typing import TYPE_CHECKING, Any, ClassVar

from sqlalchemy import (
  UUID,
  Boolean,
  Float,
  ForeignKey,
  String,
  Text,
  UniqueConstraint,
  text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from praxis.backend.models.orm.plr_sync import PLRTypeDefinitionOrm
from praxis.backend.models.orm.resource import ResourceOrm
from praxis.backend.utils.db import Base
from praxis.backend.utils.uuid import generate_name

if TYPE_CHECKING:
  from praxis.backend.models.orm import (
    AssetRequirementOrm,
    FunctionDataOutputOrm,
    MachineOrm,
    ResourceDefinitionOrm,
  )

generate_deck_name = partial(
  generate_name,
  prefix="deck",
)


class DeckOrm(ResourceOrm):

  """Represents a physical deck instance in the lab.

  A deck is a specialized resource that holds other resources and is
  typically part of a machine.

  Attributes:
      accession_id (uuid.UUID): Primary key, linked to the resource's accession_id.
      machine_id (uuid.UUID | None): Foreign key to the machine this deck
          is part of.
      machine (MachineOrm | None): Relationship to the parent machine.
      deck_type_id (uuid.UUID): Foreign key to the deck type definition.
      deck_type (DeckTypeDefinitionOrm): Relationship to the deck's type
          definition.

  """

  __tablename__ = "decks"
  __mapper_args__: ClassVar[dict] = {
      "polymorphic_identity": "deck",
      "inherit_condition": text("decks.accession_id == resources.accession_id"),
  }

  accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("resources.accession_id"),
    primary_key=True,
    index=True,
    comment="Primary key, linked to the resource's accession_id.",
    kw_only=True,
  )

  parent_machine_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("machines.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the machine this deck is part of.",
    default=None,
  )
  parent_machine: Mapped["MachineOrm | None"] = relationship(
    "MachineOrm",
    back_populates="decks",
    uselist=False,
    foreign_keys=[parent_machine_accession_id],
    default=None,
  )

  workcell_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("workcells.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the workcell this deck belongs to, if applicable.",
    default=None,
  )
  workcell: Mapped["WorkcellOrm | None"] = relationship(
    "WorkcellOrm",
    back_populates="decks",
    foreign_keys=[workcell_accession_id],
    default=None,
  )

  deck_type_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("deck_definition_catalog.accession_id"),
    index=True,
    comment="Foreign key to the deck type definition.",
    kw_only=True,
  )

  deck_type: Mapped["DeckDefinitionOrm"] = relationship(
    "DeckDefinitionOrm",
    back_populates="deck",
    uselist=False,
    foreign_keys=[deck_type_id],
    init=False,
    )

  data_outputs: Mapped[list["FunctionDataOutputOrm"]] = relationship(
    "FunctionDataOutputOrm",
    back_populates="deck",
    cascade="all, delete-orphan",
    default_factory=list,
  )
  resource_counterpart: Mapped["ResourceOrm"] = relationship(
    "ResourceOrm",
    back_populates="deck_counterpart",
    uselist=False,
    foreign_keys=[accession_id],
    init=False,
    )
  resources: Mapped[list["ResourceOrm"]] = relationship(
    "ResourceOrm",
    back_populates="deck",
    cascade="all, delete-orphan",
    default_factory=list,
  )


class DeckDefinitionOrm(PLRTypeDefinitionOrm):

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
      description (str): A detailed description of the deck type.
      plr_category (str | None): The category of the deck type in PyLabRobot.
      default_size_x_mm (float | None): The default size in X dimension in mm.
      default_size_y_mm (float | None): The default size in Y dimension in mm.
      default_size_z_mm (float | None): The default size in Z dimension in mm.
      serialized_constructor_args_json (dict[str, Any] | None): JSONB field to store
          serialized constructor arguments for the deck type.
      serialized_assignment_methods_json (dict[str, Any] | None): JSONB field to store
          serialized assignment methods for the deck type.
      serialized_constructor_hints_json (dict[str, Any] | None): JSONB field to store
          serialized constructor hints for the deck type.
      additional_properties_json (dict[str, Any] | None): JSONB field to store
          additional properties for the deck type.
      positioning_config_json (dict[str, Any] | None): JSONB field to store
          positioning configuration, such as the method and parameters for calculating
          coordinates from slot names.
      positions (list[DeckPositionDefinitionOrm]): A list of all defined
          positions (slots) available on this deck type.
      deck (list[DeckOrm]): A list of all physical deck instances
          of this type.

  """

  __tablename__ = "deck_definition_catalog"
  __table_args__ = (UniqueConstraint("fqn", name="uq_deck_type_definitions_fqn"),)

  default_size_x_mm: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
    comment="Default size in X dimension in mm.",
  )
  default_size_y_mm: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
    comment="Default size in Y dimension in mm.",
  )
  default_size_z_mm: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
    comment="Default size in Z dimension in mm.",
  )
  serialized_constructor_args_json: Mapped[dict[str, Any] | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )
  serialized_assignment_methods_json: Mapped[dict[str, Any] | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )
  serialized_constructor_hints_json: Mapped[dict[str, Any] | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )
  additional_properties_json: Mapped[dict[str, Any] | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )
  positioning_config_json: Mapped[dict[str, Any] | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )

  positions: Mapped[list["DeckPositionDefinitionOrm"]] = relationship(
    "DeckPositionDefinitionOrm",
    back_populates="deck_type",
    cascade="all, delete-orphan",
    default_factory=list,
  )
  deck: Mapped[list["DeckOrm"]] = relationship(
    "DeckOrm",
    back_populates="deck_type",
    cascade="all, delete-orphan",
    default_factory=list,
  )
  machine_definition: Mapped["ResourceDefinitionOrm"] = relationship(
    "ResourceDefinitionOrm",
    back_populates="deck_definition",
    uselist=False,
    default=None,
  )
  asset_requirement: Mapped["AssetRequirementOrm"] = relationship(
    "AssetRequirementOrm",
    back_populates="deck_definitions",
    uselist=False,
    default=None,
  )


class DeckPositionDefinitionOrm(Base):

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
      compatible_resource_fqns (dict[str, Any] | None): A JSONB field to store a
          list or mapping of PyLabRobot resource FQNs that are compatible with
          this position.
      deck_type (DeckTypeDefinitionOrm): Relationship to the parent deck type.

  """

  __tablename__ = "deck_position_definitions"
  __table_args__ = (UniqueConstraint("deck_type_id", "position_accession_id", name="uq_deck_position"),)

  deck_type_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("deck_definition_catalog.accession_id"),
    index=True,
    nullable=False,
    comment="Foreign key to the parent deck type definition.",
    kw_only=True,
  )
  position_accession_id: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="Human-readable identifier for the position (e.g., 'A1', 'trash_bin').",
    kw_only=True,
  )

  nominal_x_mm: Mapped[float] = mapped_column(
    Float,
    nullable=False,
    comment="X-coordinate of the position's center.",
    default=0.0,
  )
  nominal_y_mm: Mapped[float] = mapped_column(
    Float,
    nullable=False,
    comment="Y-coordinate of the position's center.",
    default=0.0,
  )
  nominal_z_mm: Mapped[float] = mapped_column(
    Float,
    nullable=False,
    comment="Z-coordinate of the position's center.",
    default=0.0,
  )
  pylabrobot_position_type_name: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="PyLabRobot specific position type name.",
    default=None,
  )
  allowed_resource_definition_names: Mapped[list[str] | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="List of specific resource definition names allowed at this position.",
    default=None,
  )
  accepts_tips: Mapped[bool | None] = mapped_column(
    Boolean,
    nullable=True,
    comment="Indicates if the position accepts tips.",
    default=None,
  )
  accepts_plates: Mapped[bool | None] = mapped_column(
    Boolean,
    nullable=True,
    comment="Indicates if the position accepts plates.",
    default=None,
  )
  accepts_tubes: Mapped[bool | None] = mapped_column(
    Boolean,
    nullable=True,
    comment="Indicates if the position accepts tubes.",
    default=None,
  )
  notes: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    comment="Additional notes for the position.",
    default=None,
  )

  compatible_resource_fqns: Mapped[dict[str, Any] | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="JSONB field to store additional, position-specific details.",
    default=None,
  )

  deck_type: Mapped["DeckDefinitionOrm"] = relationship(
    "DeckDefinitionOrm",
    back_populates="positions",
    uselist=False,
    kw_only=True,
  )
