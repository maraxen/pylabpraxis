# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""Machine ORM Model for Asset Management.

praxis/database_models/machine_orm.py

SQLAlchemy ORM models for Machine Management, including:
- MachineOrm (represents a physical machine or machine)
- MachineStatusEnum (enumeration for machine operational statuses)
- MachineCategoryEnum (enumeration for machine categories)
"""

from datetime import datetime
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
  from . import (
    AssetRequirementOrm,
    DeckDefinitionOrm,
    DeckOrm,
    FunctionDataOutputOrm,
    ResourceDefinitionOrm,
    ResourceOrm,
    WorkcellOrm,
  )

import uuid

from sqlalchemy import (
  UUID,
  Boolean,
  DateTime,
  Float,
  ForeignKey,
  String,
  Text,
)
from sqlalchemy import (
  Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from praxis.backend.models.enums import (
  AssetType,
  MachineCategoryEnum,
  MachineStatusEnum,
)
from praxis.backend.models.orm.plr_sync import PLRTypeDefinitionOrm
from praxis.backend.models.orm.types import JsonVariant
from praxis.backend.utils.uuid import uuid7

from .asset import AssetOrm


class MachineDefinitionOrm(PLRTypeDefinitionOrm):

  """SQLAlchemy ORM model for cataloging machine definitions.

  This model stores comprehensive metadata about various types of lab machines,
  including their categories, capabilities, and PyLabRobot definitions.
  """

  __tablename__ = "machine_definition_catalog"

  machine_category: Mapped[MachineCategoryEnum] = mapped_column(
    SAEnum(MachineCategoryEnum, name="machine_category_enum"),
    nullable=False,
    index=True,
    default=MachineCategoryEnum.UNKNOWN,
    comment="Category of the machine, e.g., liquid handler, centrifuge, etc.",
  )
  material: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
    comment="Material of the resource, e.g., 'polypropylene', 'glass'.",
  )
  manufacturer: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
    comment="Manufacturer of the resource, if applicable.",
  )
  plr_definition_details_json: Mapped[dict | None] = mapped_column(
    JsonVariant,
    nullable=True,
    comment="Additional PyLabRobot specific definition details as JSONB.",
    default=None,
  )

  size_x_mm: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
    comment="Size in X dimension (mm).",
  )
  size_y_mm: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
    comment="Size in Y dimension (mm).",
  )
  size_z_mm: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
    comment="Size in Z dimension (mm).",
  )
  model: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
    comment="Model of the resource, if applicable.",
  )
  rotation_json: Mapped[dict | None] = mapped_column(
    JsonVariant,
    nullable=True,
    comment=(
      "Represents PLR Resource.rotation, e.g., {'x_deg': 0, 'y_deg': 0,"
      " 'z_deg': 90} or PLR rotation object serialized"
    ),
    default=None,
  )

  resource_definition_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("resource_definition_catalog.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the resource definition catalog, if this resource is also a machine.",
    default=None,
  )
  resource_definition: Mapped["ResourceDefinitionOrm | None"] = relationship(
    "ResourceDefinitionOrm",
    uselist=False,
    foreign_keys=[resource_definition_accession_id],
    back_populates="machine_definition",
    default=None,
    init=False,
  )

  has_deck: Mapped[bool] = mapped_column(
    Boolean,
    default=False,
    nullable=False,
    comment="Flag indicating if this machine has a deck.",
  )

  deck_definition_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("deck_definition_catalog.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the deck definition catalog, if this machine has a deck.",
    default=None,
  )
  deck_definition: Mapped["DeckDefinitionOrm | None"] = relationship(
    "DeckDefinitionOrm",
    back_populates="machine_definition",
    default=None,
    foreign_keys=[deck_definition_accession_id],
    uselist=False,
    init=False,
  )
  setup_method_json: Mapped[dict | None] = mapped_column(
    JsonVariant,
    nullable=True,
    comment="JSONB representation of setup method for this machine definition.",
    default=None,
  )
  asset_requirement_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("protocol_asset_requirements.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the asset requirement this machine definition satisfies.",
    default=None,
  )
  asset_requirement: Mapped["AssetRequirementOrm"] = relationship(
    "AssetRequirementOrm",
    back_populates="machine_definitions",
    uselist=False,
    default=None,
    foreign_keys=[asset_requirement_accession_id],
    init=False,
  )


class MachineOrm(AssetOrm):

  """SQLAlchemy ORM model representing a physical machine or machine.

  This model tracks individual physical items of lab machines,
  including their unique name, category, status, and connection details.
  """

  __tablename__ = "machines"
  __mapper_args__: ClassVar[dict[str, str]] = {"polymorphic_identity": AssetType.MACHINE}

  accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("assets.accession_id"),
    primary_key=True,
    comment="Unique identifier for the machine, derived from the Asset base class.",
    init=False,
    default_factory=uuid7,
  )

  machine_category: Mapped[MachineCategoryEnum] = mapped_column(
    SAEnum(MachineCategoryEnum, name="machine_category_enum"),
    nullable=False,
    index=True,
    default=MachineCategoryEnum.UNKNOWN,
    comment="Category of the machine, e.g., liquid handler, centrifuge, etc.",
  )
  description: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    comment="Description of the machine's purpose or capabilities.",
    default=None,
  )
  manufacturer: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="Manufacturer of the machine.",
    default=None,
  )
  model: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="Model of the machine.",
    default=None,
  )
  serial_number: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    unique=True,
    comment="Unique serial number of the machine, if applicable.",
    default=None,
  )
  installation_date: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="Date when the machine was installed or commissioned.",
    default=None,
  )
  status: Mapped[MachineStatusEnum] = mapped_column(
    SAEnum(MachineStatusEnum, name="machine_status_enum"),
    default=MachineStatusEnum.OFFLINE,
    nullable=False,
    index=True,
  )
  status_details: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    comment="Additional details about the current status, e.g., error message",
    default=None,
  )
  connection_info: Mapped[dict | None] = mapped_column(
    JsonVariant,
    nullable=True,
    comment="e.g., {'backend': 'hamilton', 'address': '192.168.1.1'}",
    default=None,
  )
  is_simulation_override: Mapped[bool | None] = mapped_column(
    Boolean,
    nullable=True,
    default=None,
    comment="If True, this machine is a simulation override for testing purposes.",
  )

  workcell_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("workcells.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the workcell this machine belongs to, if applicable.",
    default=None,
    init=False,
  )
  workcell: Mapped["WorkcellOrm | None"] = relationship(
    "WorkcellOrm",
    back_populates="machines",
    default=None,
    init=False,
  )
  resource_counterpart_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey(
      "resources.accession_id",
      ondelete="SET NULL",
      use_alter=True,
      name="fk_machine_resource_counterpart",
    ),
    nullable=True,
    index=True,
    comment="Foreign key to the resource counterpart of this machine, if applicable.",
    default=None,
  )
  resource_counterpart: Mapped["ResourceOrm | None"] = relationship(
    "ResourceOrm",
    back_populates="machine_counterpart",
    foreign_keys=[resource_counterpart_accession_id],
    remote_side="ResourceOrm.accession_id",
    default=None,
    init=False,
  )

  deck_child_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey(
      "decks.accession_id",
      ondelete="SET NULL",
      use_alter=True,
      name="fk_machine_deck_child",
    ),
    nullable=True,
    index=True,
    comment="Foreign key to the deck this machine has, if applicable.",
    default=None,
    init=False,
  )

  deck_child_definition_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("deck_definition_catalog.accession_id", ondelete="SET NULL"),
    nullable=True,
    index=True,
    comment="Foreign key to the deck definition this machine uses, if applicable.",
    default=None,
    init=False,
  )

  # If this machine has a deck (e.g., a liquid handler)
  deck_child_definition: Mapped["DeckDefinitionOrm | None"] = relationship(
    "DeckDefinitionOrm",
    uselist=False,
    default=None,
    foreign_keys=[deck_child_definition_accession_id],
    init=False,
  )

  # Resources located on/in this machine
  located_resource: Mapped["ResourceOrm | None"] = relationship(
    "ResourceOrm",
    back_populates="location_machine",
    default=None,
    uselist=False,
    foreign_keys="ResourceOrm.machine_location_accession_id",
    init=False,
  )

  # Additional fields for machine state tracking
  last_seen_online: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    default=None,
    comment="Timestamp of the last time the machine was seen online.",
    index=True,
  )
  current_protocol_run_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    ForeignKey("protocol_runs.accession_id", ondelete="SET NULL"),
    nullable=True,
    index=True,
    comment="Foreign key to the current protocol run this machine is executing, if applicable.",
    default=None,
  )

  data_outputs: Mapped[list["FunctionDataOutputOrm"]] = relationship(
    "FunctionDataOutputOrm",
    back_populates="machine",
    cascade="all, delete-orphan",
    default_factory=list,
  )

  decks: Mapped[list["DeckOrm"]] = relationship(
    "DeckOrm",
    back_populates="parent_machine",
    cascade="all, delete-orphan",
    default_factory=list,
    foreign_keys="DeckOrm.parent_machine_accession_id",
  )

  def __repr__(self) -> str:
    """Return a string representation of the MachineOrm object."""
    return (
      f"<MachineOrm(id={self.accession_id}, name='{self.name}', "
      f"category='{self.machine_category.value}', status='{self.status.value}')>"
    )

  @property
  def is_machine(self) -> bool:
    """Return True if the asset is a machine."""
    return True

  @property
  def is_resource(self) -> bool:
    """Return True if the asset is also a resource."""
    return self.resource_counterpart_accession_id is not None
