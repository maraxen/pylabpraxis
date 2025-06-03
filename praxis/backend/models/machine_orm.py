# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""Machine ORM Model for Asset Management.

praxis/database_models/machine_orm.py

SQLAlchemy ORM models for Machine Management, including:
- MachineOrm (represents a physical machine or instrument)
- MachineStatusEnum (enumeration for machine operational statuses)
- MachineCategoryEnum (enumeration for machine categories)
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
  JSON,
  DateTime,
  ForeignKey,
  Integer,
  String,
  Text,
)
from sqlalchemy import (
  Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from praxis.backend.models.workcell_orm import WorkcellOrm
from praxis.backend.utils.db import Base


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

  These categories help in broad classification of instruments based on their
  functionality, mapping to PyLabRobot's instrument types.
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


class MachineOrm(Base):
  """SQLAlchemy ORM model representing a physical machine or instrument.

  This model stores details about automation hardware, including its status,
  configuration, and relationships to deck configurations and resource instances.
  """

  __tablename__ = "machines"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
  user_friendly_name: Mapped[str] = mapped_column(
    String, nullable=False, unique=True, index=True
  )
  python_fqn: Mapped[str] = mapped_column(
    String,
    nullable=False,
    comment="Fully qualified PyLabRobot class name \
          (e.g., pylabrobot.liquid_handling.hamilton.STAR)",
  )
  praxis_machine_category: Mapped[Optional[MachineCategoryEnum]] = mapped_column(
    SAEnum(MachineCategoryEnum, name="praxis_machine_category_enum"),
    nullable=True,
    index=True,
    comment="Praxis-defined category based on PLR class",
  )
  backend_config_json: Mapped[Optional[dict]] = mapped_column(
    JSON, nullable=True, comment="JSON storing PLR backend connection details"
  )
  pylabrobot_runtime_config_json: Mapped[Optional[dict]] = mapped_column(
    JSON,
    nullable=True,
    comment="Runtime configuration and defaults from introspection",
  )

  deck_type_definition_id: Mapped[Optional[int]] = mapped_column(
    ForeignKey("deck_type_definitions.id"), nullable=True, index=True
  )

  current_status: Mapped[MachineStatusEnum] = mapped_column(
    SAEnum(MachineStatusEnum, name="machine_status_enum"),
    default=MachineStatusEnum.OFFLINE,
    nullable=False,
  )
  status_details: Mapped[Optional[str]] = mapped_column(
    Text, nullable=True, comment="More details on error or current operation"
  )
  current_protocol_run_guid: Mapped[Optional[str]] = mapped_column(
    String,
    ForeignKey("protocol_runs.run_guid", ondelete="SET NULL"),
    nullable=True,
    index=True,
  )  # Link to ProtocolRunOrm.run_guid

  workcell_id: Mapped[Optional[int]] = mapped_column(
    ForeignKey("workcells.id"),
    nullable=True,
    index=True,
    comment="FK to workcell table",
  )

  # Link to Workcell table
  workcell: Mapped[Optional["WorkcellOrm"]] = relationship(
    "WorkcellOrm", foreign_keys=[workcell_id], back_populates="machines"
  )

  physical_location_description: Mapped[Optional[str]] = mapped_column(
    String, nullable=True
  )
  properties_json: Mapped[Optional[dict]] = mapped_column(
    JSON,
    nullable=True,
    comment="Additional machine-specific properties, calibration data",
  )

  last_seen_online: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  created_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )
  updated_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
  )

  # Relationships
  # deck_type_definition: Mapped[Optional["DeckTypeDefinitionOrm"]] = relationship(
  #    back_populates="machines"
  # )
  deck_configurations = relationship(
    "DeckConfigurationOrm", back_populates="deck_machine"
  )
  located_resource_instances = relationship(
    "ResourceInstanceOrm", back_populates="location_machine"
  )

  def __repr__(self):
    """Render a string representation of the MachineOrm instance."""
    return f"<MachineOrm(id={self.id}, name='{self.user_friendly_name}', \
          type='{self.python_fqn}')>"
