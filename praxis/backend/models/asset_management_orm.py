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

# TODO: refactor to align with PLR and be more modular
from datetime import datetime
from typing import Optional, Any
import enum

from sqlalchemy import (
    Integer,
    String,
    Text,
    Boolean,
    ForeignKey,
    JSON,
    DateTime,
    UniqueConstraint,
    Enum as SAEnum,
    Float,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from praxis.backend.utils.db import Base  # Import your project's Base


# --- Enum Definitions for Asset Status Fields ---
class MachineStatusEnum(enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"  # Could store protocol_run_guid in properties_json
    ERROR = "error"
    OFFLINE = "offline"
    INITIALIZING = "initializing"
    MAINTENANCE = "maintenance"


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


class PraxisDeviceCategoryEnum(enum.Enum):
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


# --- Asset Management ORM Models ---


class AssetInstanceOrm(Base):
    """
    Abstract base class representing any physical asset in the lab.
    This serves as an umbrella for both machines and resource instances.
    """

    __tablename__ = "asset_instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_type: Mapped[str] = mapped_column(
        String, nullable=False, index=True
    )  # 'machine', 'resource', etc.
    asset_id: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )  # FK to concrete asset table (interpreted based on asset_type)

    barcode: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, unique=True, index=True
    )
    serial_number: Mapped[Optional[str]] = mapped_column(
        String, nullable=True, unique=True, index=True
    )

    acquisition_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    warranty_expiry: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_maintenance: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_maintenance_due: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    owner: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )  # Person or group responsible for this asset
    # cost_center = Column(String, nullable=True)
    # purchase_value = Column(Float, nullable=True)

    metadata_json: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, comment="Additional asset metadata"
    )

    created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        UniqueConstraint("asset_type", "asset_id", name="uq_asset_instance"),
    )

    def __repr__(self):
        return f"<AssetInstanceOrm(id={self.id}, type='{self.asset_type}', asset_id={self.asset_id})>"


class MachineOrm(Base):
    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # praxis_machine_id = Column(String, unique=True, index=True, nullable=False, comment="Unique identifier within Praxis, e.g., Serial Number or user-defined ID")
    user_friendly_name: Mapped[str] = mapped_column(
        String, nullable=False, unique=True, index=True
    )
    pylabrobot_class_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Fully qualified PyLabRobot class name (e.g., pylabrobot.liquid_handling.hamilton.STAR)",
    )
    praxis_machine_category: Mapped[Optional[PraxisDeviceCategoryEnum]] = mapped_column(
        SAEnum(PraxisDeviceCategoryEnum, name="praxis_machine_category_enum"),
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
    deck_type_definition: Mapped[Optional["DeckTypeDefinitionOrm"]] = relationship(
        back_populates="machines"
    )
    deck_configurations = relationship(
        "DeckConfigurationOrm", back_populates="deck_machine"
    )
    located_resource_instances = relationship(
        "ResourceInstanceOrm", back_populates="location_machine"
    )

    def __repr__(self):
        return f"<MachineOrm(id={self.id}, name='{self.user_friendly_name}', type='{self.pylabrobot_class_name}')>"


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


class DeckConfigurationOrm(Base):
    __tablename__ = "deck_configurations"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )  # praxis_deck_config_id
    layout_name: Mapped[str] = mapped_column(
        String, nullable=False, unique=True, index=True
    )

    # A Deck itself is a Machine
    deck_machine_id: Mapped[int] = mapped_column(
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
    slot_items = relationship(
        "DeckConfigurationSlotItemOrm",
        back_populates="deck_configuration",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<DeckConfigurationOrm(id={self.id}, name='{self.layout_name}')>"


class DeckConfigurationSlotItemOrm(Base):
    __tablename__ = "deck_configuration_slot_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    deck_configuration_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("deck_configurations.id"), nullable=False
    )
    slot_name: Mapped[str] = mapped_column(
        String, nullable=False, comment="Slot name on the deck (e.g., A1, SLOT_7)"
    )

    # This links to a specific physical piece of resource
    resource_instance_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("resource_instances.id"), nullable=False
    )

    # Optional: for validation, store the expected type of resource for this slot in this layout
    expected_resource_definition_name: Mapped[Optional[str]] = mapped_column(
        String,
        ForeignKey("resource_definition_catalog.pylabrobot_definition_name"),
        nullable=True,
    )
    deck_slot_definition_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("deck_slot_definitions.id"), nullable=True, index=True
    )

    deck_configuration = relationship(
        "DeckConfigurationOrm", back_populates="slot_items"
    )
    resource_instance = relationship(
        "ResourceInstanceOrm", back_populates="deck_configuration_items"
    )
    expected_resource_definition = relationship(
        "ResourceDefinitionCatalogOrm"
    )  # Simple relationship
    deck_slot_definition = relationship("DeckSlotDefinitionOrm")

    __table_args__ = (
        UniqueConstraint(
            "deck_configuration_id", "slot_name", name="uq_deck_slot_item"
        ),
    )

    def __repr__(self):
        return f"<DeckConfigurationSlotItemOrm(deck_config_id={self.deck_configuration_id}, slot='{self.slot_name}', lw_instance_id={self.resource_instance_id})>"


class DeckSlotDefinitionOrm(Base):
    __tablename__ = "deck_slot_definitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deck_type_definition_id: Mapped[int] = mapped_column(
        ForeignKey("deck_type_definitions.id"), nullable=False
    )
    slot_name: Mapped[str] = mapped_column(String, nullable=False)
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
    slot_specific_details_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )

    # Relationship
    deck_type_definition: Mapped["DeckTypeDefinitionOrm"] = relationship(
        back_populates="slot_definitions"
    )

    # Unique constraint for slot_name within a deck_type_definition
    __table_args__ = (
        UniqueConstraint(
            "deck_type_definition_id", "slot_name", name="uq_deck_slot_definition"
        ),
    )

    def __repr__(self):
        return f"<DeckSlotDefinitionOrm(id={self.id}, name='{self.slot_name}', \
          deck_type_id={self.deck_type_definition_id})>"


class DeckTypeDefinitionOrm(Base):
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
    serialized_constructor_args_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )
    serialized_assignment_methods_json: Mapped[Optional[dict[str, Any]]] = (
        mapped_column(JSON, nullable=True)
    )
    serialized_constructor_layout_hints_json: Mapped[Optional[dict[str, Any]]] = (
        mapped_column(JSON, nullable=True)
    )
    additional_properties_json: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )

    # Relationships
    slot_definitions: Mapped[list[DeckSlotDefinitionOrm]] = relationship(
        back_populates="deck_type_definition", cascade="all, delete-orphan"
    )
    machines: Mapped[list[MachineOrm]] = relationship(
        back_populates="deck_type_definition"
    )

    def __repr__(self):
        return f"<DeckTypeDefinitionOrm(id={self.id}, fqn='{self.pylabrobot_deck_fqn}', \
          name='{self.display_name}')>"
