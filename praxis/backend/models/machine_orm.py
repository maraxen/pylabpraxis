# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""
praxis/database_models/asset_management_orm.py

SQLAlchemy ORM models for Asset Management, including:
- MachineOrm (Instruments/Hardware)
- ResourceDefinitionCatalogOrm (Types of Resource from PLR)
- ResourceInstanceOrm (Specific physical resource items)
- DeckConfigurationOrm (Named deck layouts)
- DeckConfigurationSlotItemOrm (Resource in a slot for a layout)
"""

from datetime import datetime
from typing import Optional, Any
import enum

from sqlalchemy import (
    Integer,
    String,
    Text,
    ForeignKey,
    JSON,
    DateTime,
    Enum as SAEnum,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func


from praxis.backend.utils.db import Base  # Import your project's Base


class MachineStatusEnum(enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    ERROR = "error"
    OFFLINE = "offline"
    INITIALIZING = "initializing"
    MAINTENANCE = "maintenance"


class MachineCategoryEnum(enum.Enum):  # TODO: change this to PLR categories
    LIQUID_HANDLER = "LiquidHandler"
    DECK = "Deck"
    PLATE_READER = "PlateReader"
    INCUBATOR = "Incubator"
    CENTRIFUGE = "Centrifuge"
    MICROSCOPE = "Microscope"
    ARM = "Arm"
    CARRIER_HANDLER = "CarrierHandler"
    GENERAL_AUTOMATION_DEVICE = "GeneralAutomationDevice"
    OTHER_INSTRUMENT = "OtherInstrument"
    UNKNOWN = "Unknown"


class MachineOrm(Base):
    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_friendly_name: Mapped[str] = mapped_column(
        String, nullable=False, unique=True, index=True
    )
    pylabrobot_class_name: Mapped[str] = mapped_column(
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

    # TODO: ASSET-DB-1: Define WorkcellOrm if supporting multiple workcells and link here.
    workcell_id: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, index=True, comment="FK to a future Workcells table"
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
        return f"<MachineOrm(id={self.id}, name='{self.user_friendly_name}', \
          type='{self.pylabrobot_class_name}')>"
