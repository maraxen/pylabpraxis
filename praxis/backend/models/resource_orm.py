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
from typing import Optional
import enum

from sqlalchemy import (
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    JSON,
    DateTime,
    Enum as SAEnum,
    Float,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from praxis.backend.utils.db import Base  # Import your project's Base


class ResourceInstanceStatusEnum(enum.Enum):
    AVAILABLE_IN_STORAGE = "available_in_storage"
    AVAILABLE_ON_DECK = "available_on_deck"  # Implies it's on a known deck slot
    IN_USE = "in_use"  # Could store protocol_run_guid in properties_json
    EMPTY = "empty"  # e.g., tip rack, reagent trough
    PARTIALLY_FILLED = "partially_filled"
    FULL = "full"  # e.g., waste, source plate
    NEEDS_REFILL = "needs_refill"
    TO_BE_DISPOSED = "to_be_disposed"
    ERROR = "error"  # e.g., damaged, contaminated
    UNKNOWN = "unknown"


class ResourceDefinitionCatalogOrm(
    Base
):  # TODO: ASSET-DB-2: Bring in line with PLR resource definition
    __tablename__ = "resource_definition_catalog"

    pylabrobot_definition_name: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        index=True,
        comment="Unique name from PyLabRobot (e.g., corning_96_wellplate_360ul_flat), corresponds to PLR Resource.name",
    )
    python_fqn: Mapped[str] = mapped_column(
        String,
        nullable=False,
        index=True,
        comment="Fully qualified Python class name of the specific PyLabRobot resource definition (e.g., 'pylabrobot.resources.corning_96_wellplate_360ul_flat.Corning96WellPlate360uLFlat', or 'pylabrobot.resources.plate.Plate' if generic).",
    )

    # Fields for PLR Resource base attributes
    size_x_mm: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Dimension X in millimeters, from PLR Resource.size_x",
    )
    size_y_mm: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Dimension Y in millimeters, from PLR Resource.size_y",
    )
    size_z_mm: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Dimension Z in millimeters, from PLR Resource.size_z",
    )
    plr_category: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        index=True,
        comment="Specific PyLabRobot resource class name (e.g., 'Plate', 'TipRack', 'Carrier', 'Trough') from the PLR ontology. Corresponds to PLR Resource.category or the direct subclass name.",
    )
    model: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, comment="Model identifier, from PLR Resource.model"
    )
    rotation_json: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Represents PLR Resource.rotation, e.g., {'x_deg': 0, 'y_deg': 0, 'z_deg': 90} or PLR rotation object serialized",
    )

    # Existing Praxis-specific or other fields
    praxis_resource_type_name: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        unique=True,
        comment="Optional user-friendly alias in Praxis",
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_consumable: Mapped[bool] = mapped_column(Boolean, default=True)
    nominal_volume_ul: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    material: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    manufacturer: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    plr_definition_details_json: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Additional PLR-specific details not covered by dedicated columns (e.g., well layout, specific geometry details)",
    )

    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    resource_instances = relationship(
        "ResourceInstanceOrm", back_populates="resource_definition"
    )

    def __repr__(self):
        return f"<ResourceDefinitionCatalogOrm(name='{self.pylabrobot_definition_name}', category='{self.plr_category}')>"


class ResourceInstanceOrm(Base):
    __tablename__ = "resource_instances"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )  # praxis_resource_instance_id
    user_assigned_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True,
        index=True,
        comment="User-friendly unique name for this physical item",
    )

    pylabrobot_definition_name: Mapped[str] = mapped_column(
        String,
        ForeignKey("resource_definition_catalog.pylabrobot_definition_name"),
        nullable=False,
        index=True,
    )

    lot_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # Use DateTime for date part
    date_added_to_inventory: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    current_status: Mapped[ResourceInstanceStatusEnum] = mapped_column(
        SAEnum(ResourceInstanceStatusEnum, name="resource_instance_status_enum"),
        default=ResourceInstanceStatusEnum.UNKNOWN,
        nullable=False,
        index=True,
    )
    status_details: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional details about the current status, e.g., error message",
    )  # ADDED

    # Location tracking
    # If on a deck, deck_machine_id + current_deck_slot_name should be set.
    # If inside another machine (e.g. plate in reader), location_machine_id is set.
    # If in general storage, physical_location_description can be used.
    current_deck_slot_name: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, comment="If on a deck, the slot name (e.g., A1, SLOT_7)"
    )
    location_machine_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("machines.id"),
        nullable=True,
        comment="FK to MachineOrm if located on/in a machine (deck, reader, etc.)",
    )
    physical_location_description: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, comment="General storage location if not on a machine"
    )

    properties_json: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Instance-specific state combining PLR runtime inspection (e.g., well contents, used tips map) and user-provided metadata (e.g., sample info, reagent data)",
    )
    is_permanent_fixture: Mapped[bool] = mapped_column(
        Boolean, default=False, comment="e.g., built-in waste chute"
    )

    current_protocol_run_guid: Mapped[Optional[str]] = mapped_column(
        String,
        ForeignKey("protocol_runs.run_guid", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    resource_definition = relationship(
        "ResourceDefinitionCatalogOrm", back_populates="resource_instances"
    )
    location_machine = relationship(
        "MachineOrm", back_populates="located_resource_instances"
    )
    # protocol_run = relationship("ProtocolRunOrm", foreign_keys=[current_protocol_run_guid]) # If linking to runs

    # Relationship to deck configuration items
    deck_configuration_items = relationship(
        "DeckConfigurationSlotItemOrm", back_populates="resource_instance"
    )

    def __repr__(self):
        return f"<ResourceInstanceOrm(id={self.id}, name='{self.user_assigned_name}', type='{self.pylabrobot_definition_name}')>"
