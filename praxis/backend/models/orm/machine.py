# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""Machine ORM Model for Asset Management.

praxis/database_models/machine_orm.py

SQLAlchemy ORM models for Machine Management, including:
- MachineOrm (represents a physical machine or machine)
- MachineStatusEnum (enumeration for machine operational statuses)
- MachineCategoryEnum (enumeration for machine categories)
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, ClassVar

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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from praxis.backend.models.enums import (
  AssetType,
  MachineCategoryEnum,
  MachineStatusEnum,
)
from praxis.backend.models.orm.plr_sync import PLRTypeDefinitionOrm

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
  )
  material: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
  )
  manufacturer: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
  )
  plr_definition_details_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )

  size_x_mm: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
  )
  size_y_mm: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
  )
  size_z_mm: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
  )
  model: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
  )
  rotation_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )

  resource_child_list: Mapped[list["ResourceOrm"]] = relationship(
    "ResourceOrm",
    back_populates="resource_definition",
    cascade="all, delete-orphan",
    default_factory=list,
  )

  resource_definition_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    ForeignKey("resource_definition_catalog.accession_id"),
    nullable=True,
    index=True,
    default=None,
  )
  resource_definition: Mapped["ResourceDefinitionOrm | None"] = relationship(
    "ResourceDefinitionOrm",
    back_populates="machine_definition",
    foreign_keys=[resource_definition_accession_id],
    default=None,
    init=False,
  )


  deck_definition_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    ForeignKey("deck_definition_catalog.accession_id"),
    nullable=True,
    index=True,
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
    JSONB,
    nullable=True,
    default=None,
  )
  asset_requirement: Mapped["AssetRequirementOrm"] = relationship(
    "AssetRequirementOrm",
    back_populates="machine_definitions",
    uselist=False,
    default=None,
  )


class MachineOrm(AssetOrm):

  """SQLAlchemy ORM model representing a physical machine or machine.

  This model tracks individual physical items of lab machines,
  including their unique name, category, status, and connection details.
  """

  __tablename__ = "machines"
  accession_id: Mapped[uuid.UUID] = mapped_column(
    ForeignKey("assets.accession_id"),
    primary_key=True,
  )
  __mapper_args__: ClassVar[dict[str, Any]] = {
    "polymorphic_identity": AssetType.MACHINE,
    "inherit_condition": accession_id == AssetOrm.accession_id,
  }
  __table_args__ = ({'extend_existing': True},)


  machine_category: Mapped[MachineCategoryEnum] = mapped_column(
    SAEnum(MachineCategoryEnum, name="machine_category_enum"),
    nullable=False,
    index=True,
    default=MachineCategoryEnum.UNKNOWN,
  )
  description: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    default=None,
  )
  manufacturer: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
  )
  model: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
  )
  serial_number: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    unique=True,
    default=None,
  )
  installation_date: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
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
    default=None,
  )
  connection_info: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )
  is_simulation_override: Mapped[bool | None] = mapped_column(
    Boolean,
    nullable=True,
    default=None,
  )

  workcell_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    ForeignKey("workcells.accession_id"),
    nullable=True,
    index=True,
    default=None,
  )
  workcell: Mapped["WorkcellOrm | None"] = relationship(
    "WorkcellOrm",
    back_populates="machines",
    default=None,
  )
  resource_counterpart_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    ForeignKey("resources.accession_id", ondelete="SET NULL"),
    nullable=True,
    index=True,
    default=None,
  )
  resource_counterpart: Mapped["ResourceOrm | None"] = relationship(
    "ResourceOrm",
    back_populates="machine_counterpart",
    foreign_keys=[resource_counterpart_accession_id],
    default=None,
    init=False,
  )

  deck_child_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    ForeignKey("deck_catalog.accession_id", ondelete="SET NULL"),
    nullable=True,
    index=True,
    default=None,
  )

  deck_child_definition_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    ForeignKey("deck_definition_catalog.accession_id", ondelete="SET NULL"),
    nullable=True,
    index=True,
    default=None,
  )

  # If this machine has a deck (e.g., a liquid handler)
  deck_child_definition: Mapped["DeckDefinitionOrm | None"] = relationship(
    "DeckDefinitionOrm",
    back_populates="machine",
    uselist=False,
    default=None,
    foreign_keys=[deck_child_definition_accession_id],
  )

  # Resources located on/in this machine
  located_resource: Mapped["ResourceOrm | None"] = relationship(
    "ResourceOrm",
    back_populates="location_machine",
    default=None,
    uselist=False,
  )

  # Additional fields for machine state tracking
  last_seen_online: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    default=None,
    index=True,
  )
  current_protocol_run_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    ForeignKey("protocol_runs.accession_id", ondelete="SET NULL"),
    nullable=True,
    index=True,
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
    back_populates="machine",
    cascade="all, delete-orphan",
    default_factory=list,
  )

  def __repr__(self) -> str:
    """Return a string representation of the MachineOrm object."""
    return (
      f"<MachineOrm(id={self.accession_id}, name='{self.name}', "
      f"category='{self.machine_category.value}', status='{self.status.value}')>"
    )
