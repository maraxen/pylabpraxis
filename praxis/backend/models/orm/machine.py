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
  from . import DeckDefinitionOrm, DeckOrm, ResourceDefinitionOrm, ResourceOrm, WorkcellOrm

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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from praxis.backend.models.enums import (
  AssetType,
  MachineCategoryEnum,
  MachineStatusEnum,
)
from praxis.backend.utils.db import Base

from .asset import Asset


class MachineDefinitionOrm(Base):
  """SQLAlchemy ORM model for cataloging machine definitions.

  This model stores comprehensive metadata about various types of lab machines,
  including their categories, capabilities, and PyLabRobot definitions.
  """

  __tablename__ = "machine_definition_catalog"

  name: Mapped[str] = mapped_column(
    String,
    unique=True,
    index=True,
    comment="Name of the machine definition.",
    init=False,
  )
  fqn: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="Fully qualified name of the machine's class, if applicable.",
    default="pylabrobot.machines.Machine",
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
    default=None,
    comment="Description of the resource type.",
  )
  is_consumable: Mapped[bool] = mapped_column(Boolean, default=False)
  nominal_volume_ul: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
    comment="Nominal volume in microliters, if applicable.",
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
    JSONB,
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
  plr_category: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    index=True,
    default=None,
    comment=(
      "Specific PyLabRobot resource class name (e.g., 'Plate', 'TipRack',"
      " 'Carrier', 'Trough') from the PLR ontology. Corresponds to PLR"
      " Resource.category or the direct subclass name."
    ),
  )
  model: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
    comment="Model of the resource, if applicable.",
  )
  rotation_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment=(
      "Represents PLR Resource.rotation, e.g., {'x_deg': 0, 'y_deg': 0,"
      " 'z_deg': 90} or PLR rotation object serialized"
    ),
    default=None,
  )

  resource_list: Mapped[list["ResourceOrm"]] = relationship(
    "ResourceOrm",
    back_populates="resource_definition",
    cascade="all, delete-orphan",
    comment="List of all physical resources defined by this definition.",
    default_factory=list,
  )

  is_machine: Mapped[bool] = mapped_column(Boolean, default=False)

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
    back_populates="resource_definition",
    default=None,
  )

  has_deck: Mapped[bool] = mapped_column(
    Boolean,
    default=False,
    comment="If True, this machine definition includes a deck.",
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
    comment="Deck definition associated with this machine, if applicable.",
  )
  setup_method_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="JSONB representation of setup method for this machine definition.",
    default=None,
  )

  def __repr__(self) -> str:
    """Return a string representation of the MachineDefinitionOrm object."""
    return f"<MachineDefinitionOrm(accession_id={self.accession_id}, name={self.name})>"


class MachineOrm(Asset):
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
  connection_info: Mapped[dict | None] = mapped_column(
    JSONB,
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
  )
  workcell: Mapped["WorkcellOrm | None"] = relationship(
    "WorkcellOrm",
    back_populates="machines",
    default=None,
  )

  # If this machine is also a resource (e.g., a shaker that can hold a plate)
  is_resource: Mapped[bool] = mapped_column(
    Boolean,
    default=False,
    comment="If True, this machine is also a resource that can be used in protocols.",
  )
  resource_counterpart_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("resources.accession_id", ondelete="SET NULL"),
    nullable=True,
    index=True,
    comment="Foreign key to the resource counterpart of this machine, if applicable.",
    default=None,
  )
  resource_counterpart: Mapped["ResourceOrm | None"] = relationship(
    "ResourceOrm",
    back_populates="machine_counterpart",
    foreign_keys=[resource_counterpart_accession_id],
    default=None,
    comment="Resource counterpart of this machine, if applicable.",
  )

  # If this machine has a deck (e.g., a liquid handler)
  deck: Mapped["DeckOrm | None"] = relationship(
    "DeckOrm",
    back_populates="deck_machine",
    uselist=False,
    default=None,
    comment="Deck associated with this machine, if applicable.",
  )

  # Resources located on/in this machine
  located_resource: Mapped["ResourceOrm | None"] = relationship(
    "ResourceOrm",
    back_populates="location_machine",
    default=None,
    uselist=False,
    comment="Resource located on or in this machine, if applicable.",
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

  def __repr__(self) -> str:
    """Return a string representation of the MachineOrm object."""
    return (
      f"<MachineOrm(id={self.accession_id}, name='{self.name}', "
      f"category='{self.machine_category.value}', status='{self.status.value}')>"
    )
