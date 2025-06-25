# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""Machine ORM Model for Asset Management.

praxis/database_models/machine_orm.py

SQLAlchemy ORM models for Machine Management, including:
- MachineOrm (represents a physical machine or machine)
- MachineStatusEnum (enumeration for machine operational statuses)
- MachineCategoryEnum (enumeration for machine categories)
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
  from .resource_orm import ResourceOrm

import uuid

from sqlalchemy import (
  JSON,
  UUID,
  Boolean,
  DateTime,
  ForeignKey,
  String,
  Text,
)
from sqlalchemy import (
  Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from praxis.backend.models.asset_orm import Asset
from praxis.backend.models.enums import AssetType
from praxis.backend.models.workcell_orm import WorkcellOrm


class MachineStatusEnum(enum.Enum):
  """Enumeration for the possible operational statuses of a machine."""

  AVAILABLE = "available"
  IN_USE = "in_use"
  ERROR = "error"
  OFFLINE = "offline"
  INITIALIZING = "initializing"
  MAINTENANCE = "maintenance"


class MachineCategoryEnum(enum.Enum):
  """Enumeration for classifying machines into predefined categories.

  These categories help in broad classification of machines based on their
  functionality, mapping to PyLabRobot's machine types.
  """

  LIQUID_HANDLER = "LiquidHandler"
  PLATE_READER = "PlateReader"
  INCUBATOR = "Incubator"
  SHAKER = "Shaker"
  HEATER_SHAKER = "HeaterShaker"
  PUMP = "Pump"
  FAN = "Fan"
  TEMPERATURE_CONTROLLER = "TemperatureController"
  TILTING = "Tilting"
  THERMOCYCLER = "Thermocycler"
  SEALER = "Sealer"
  FLOW_CYTOMETER = "FlowCytometer"
  SCALE = "Scale"
  CENTRIFUGE = "Centrifuge"
  ARM = "Arm"
  GENERAL_AUTOMATION_DEVICE = "GeneralAutomationDevice"
  OTHER_INSTRUMENT = "OtherInstrument"
  UNKNOWN = "Unknown"

  @classmethod
  def resources(cls):
    """Return a list of resource categories that map to this enum."""
    return [
      cls.PLATE_READER,
      cls.INCUBATOR,
      cls.SHAKER,
      cls.HEATER_SHAKER,
      cls.TEMPERATURE_CONTROLLER,
      cls.TILTING,
      cls.THERMOCYCLER,
      cls.FLOW_CYTOMETER,
      cls.SCALE,
      cls.CENTRIFUGE,
      cls.ARM,
      cls.GENERAL_AUTOMATION_DEVICE,
    ]


class MachineOrm(Asset):
  """SQLAlchemy ORM model representing a physical machine or machine.

  This model tracks individual physical items of lab machines,
  including their unique name, category, status, and connection details.
  """

  __tablename__ = "machines"
  __mapper_args__ = {"polymorphic_identity": AssetType.MACHINE}

  accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID, ForeignKey("assets.accession_id"), primary_key=True
  )

  machine_category: Mapped[MachineCategoryEnum] = mapped_column(
    SAEnum(MachineCategoryEnum, name="machine_category_enum"),
    nullable=False,
    index=True,
  )
  description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
  manufacturer: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  model: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  serial_number: Mapped[Optional[str]] = mapped_column(
    String, nullable=True, unique=True
  )
  installation_date: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  status: Mapped[MachineStatusEnum] = mapped_column(
    SAEnum(MachineStatusEnum, name="machine_status_enum"),
    default=MachineStatusEnum.OFFLINE,
    nullable=False,
    index=True,
  )
  connection_info: Mapped[Optional[dict]] = mapped_column(
    JSON,
    nullable=True,
    comment="e.g., {'backend': 'hamilton', 'address': '192.168.1.1'}",
  )
  is_simulation_override: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

  workcell_accession_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    UUID, ForeignKey("workcells.accession_id"), nullable=True
  )
  workcell: Mapped[Optional["WorkcellOrm"]] = relationship(
    "WorkcellOrm", back_populates="machines"
  )

  # If this machine is also a resource (e.g., a shaker that can hold a plate)
  is_resource: Mapped[bool] = mapped_column(Boolean, default=False)
  resource_counterpart_accession_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    UUID,
    ForeignKey("resources.accession_id", ondelete="SET NULL"),
    nullable=True,
    index=True,
  )
  resource_counterpart: Mapped[Optional["ResourceOrm"]] = relationship(
    "ResourceOrm",
    back_populates="machine_counterpart",
    foreign_keys=[resource_counterpart_accession_id],
  )

  # If this machine has a deck (e.g., a liquid handler)
  deck_instances = relationship("DeckOrm", back_populates="deck_machine")

  # Resources located on/in this machine
  located_resource_instances = relationship(
    "ResourceOrm", back_populates="location_machine"
  )

  # Additional fields for machine state tracking
  last_seen_online: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  current_protocol_run_accession_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    UUID(as_uuid=True), nullable=True
  )  # TODO: Add ForeignKey to protocol_runs

  def __repr__(self):
    """Return a string representation of the MachineOrm object."""
    return (
      f"<MachineOrm(id={self.accession_id}, name='{self.name}', "
      f"category='{self.machine_category.value}', status='{self.status.value}')>"
    )
