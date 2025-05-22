# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""
praxis/database_models/asset_management_orm.py

SQLAlchemy ORM models for Asset Management, including:
- ManagedDeviceOrm (Instruments/Hardware)
- LabwareDefinitionCatalogOrm (Types of Labware from PLR)
- LabwareInstanceOrm (Specific physical labware items)
- DeckConfigurationOrm (Named deck layouts)
- DeckConfigurationSlotItemOrm (Labware in a slot for a layout)
"""
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, JSON, DateTime, UniqueConstraint, Enum as SAEnum, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

# TODO: DB-SETUP-1 (Asset ORM): Ensure this import path for Base is correct for your project structure.
try:
    from praxis.backend.utils.db import Base # Import your project's Base
except ImportError:
    print("WARNING: Could not import Base from praxis.backend.utils.db. Using a local Base for Asset ORM definition only.")
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()

# --- Enum Definitions for Asset Status Fields ---
class ManagedDeviceStatusEnum(enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use" # Could store protocol_run_guid in properties_json
    ERROR = "error"
    OFFLINE = "offline"
    INITIALIZING = "initializing"
    MAINTENANCE = "maintenance"

class LabwareInstanceStatusEnum(enum.Enum):
    AVAILABLE_IN_STORAGE = "available_in_storage"
    AVAILABLE_ON_DECK = "available_on_deck" # Implies it's on a known deck slot
    IN_USE = "in_use" # Could store protocol_run_guid in properties_json
    EMPTY = "empty" # e.g., tip rack, reagent trough
    PARTIALLY_FILLED = "partially_filled"
    FULL = "full" # e.g., waste, source plate
    NEEDS_REFILL = "needs_refill"
    TO_BE_DISPOSED = "to_be_disposed"
    ERROR = "error" # e.g., damaged, contaminated
    UNKNOWN = "unknown"

class LabwareCategoryEnum(enum.Enum):
    PLATE = "plate"
    TIP_RACK = "tip_rack"
    RESERVOIR = "reservoir"
    TUBE_RACK = "tube_rack"
    CARRIER = "carrier" # e.g., tip carrier, plate carrier
    ADAPTER = "adapter"
    LID = "lid"
    WASTE = "waste"
    OTHER = "other"

# --- Asset Management ORM Models ---

class AssetInstanceOrm(Base):
  """
  Abstract base class representing any physical asset in the lab.
  This serves as an umbrella for both devices and labware instances.
  """
  __tablename__ = "asset_instances"

  id = Column(Integer, primary_key=True, index=True)
  asset_type = Column(String, nullable=False, index=True)  # 'device', 'labware', etc.
  asset_id = Column(Integer, nullable=False, index=True)  # FK to concrete asset table (interpreted based on asset_type)

  barcode = Column(String, nullable=True, unique=True, index=True)
  serial_number = Column(String, nullable=True, unique=True, index=True)

  acquisition_date = Column(DateTime(timezone=True), nullable=True)
  warranty_expiry = Column(DateTime(timezone=True), nullable=True)
  last_maintenance = Column(DateTime(timezone=True), nullable=True)
  next_maintenance_due = Column(DateTime(timezone=True), nullable=True)

  owner = Column(String, nullable=True)  # Person or group responsible for this asset
  #cost_center = Column(String, nullable=True)
  #purchase_value = Column(Float, nullable=True)

  metadata_json = Column(JSON, nullable=True, comment="Additional asset metadata")

  created_at = Column(DateTime(timezone=True), server_default=func.now())
  updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

  __table_args__ = (
    UniqueConstraint('asset_type', 'asset_id', name='uq_asset_instance'),
  )

  def __repr__(self):
    return f"<AssetInstanceOrm(id={self.id}, type='{self.asset_type}', asset_id={self.asset_id})>"

class ManagedDeviceOrm(Base):
    __tablename__ = "managed_devices"

    id = Column(Integer, primary_key=True, index=True)
    # praxis_device_id = Column(String, unique=True, index=True, nullable=False, comment="Unique identifier within Praxis, e.g., Serial Number or user-defined ID")
    user_friendly_name = Column(String, nullable=False, unique=True, index=True)
    pylabrobot_class_name = Column(String, nullable=False, comment="Fully qualified PyLabRobot class name (e.g., pylabrobot.liquid_handling.hamilton.STAR)")
    backend_config_json = Column(JSON, nullable=True, comment="JSON storing PLR backend connection details")

    current_status = Column(SAEnum(ManagedDeviceStatusEnum, name="managed_device_status_enum"), default=ManagedDeviceStatusEnum.OFFLINE, nullable=False)
    status_details = Column(Text, nullable=True, comment="More details on error or current operation")
    current_protocol_run_guid = Column(String, ForeignKey("protocol_runs.run_guid", ondelete="SET NULL"), nullable=True, index=True) # Link to ProtocolRunOrm.run_guid

    # TODO: ASSET-DB-1: Define WorkcellOrm if supporting multiple workcells and link here.
    workcell_id = Column(Integer, nullable=True, index=True, comment="FK to a future Workcells table")
    physical_location_description = Column(String, nullable=True)
    properties_json = Column(JSON, nullable=True, comment="Additional device-specific properties, calibration data")

    last_seen_online = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship to protocol runs (if a device is associated with a run, e.g. the main robot)
    # protocol_run = relationship("ProtocolRunOrm", foreign_keys=[current_protocol_run_guid]) # Needs careful thought if run_guid is used as FK

    # Relationship to deck configurations if this device IS a deck
    deck_configurations = relationship("DeckConfigurationOrm", back_populates="deck_device")
    # Relationship to labware instances located on this device (e.g. plate in reader, tips on pipette)
    located_labware_instances = relationship("LabwareInstanceOrm", back_populates="location_device")


    def __repr__(self):
        return f"<ManagedDeviceOrm(id={self.id}, name='{self.user_friendly_name}', type='{self.pylabrobot_class_name}')>"


class LabwareDefinitionCatalogOrm(Base): # TODO: ASSET-DB-2: Bring in line with PLR labware definition
    __tablename__ = "labware_definition_catalog"

    # Using pylabrobot_definition_name as PK assumes it's globally unique and stable in PLR
    pylabrobot_definition_name = Column(String, primary_key=True, index=True, comment="Unique name from PyLabRobot (e.g., corning_96_wellplate_360ul_flat)")

    praxis_labware_type_name = Column(String, nullable=True, unique=True, comment="Optional user-friendly alias in Praxis")
    category = Column(SAEnum(LabwareCategoryEnum, name="labware_category_enum"), nullable=True, index=True)
    description = Column(Text, nullable=True)
    is_consumable = Column(Boolean, default=True)
    nominal_volume_ul = Column(Float(64), nullable=True) # TODO: ASSET-DB-3: Use a more precise type if needed
    material = Column(String, nullable=True)
    manufacturer = Column(String, nullable=True)

    # Store key details from PLR definition for quick access & filtering without loading PLR object
    plr_definition_details_json = Column(JSON, nullable=True, comment="Dimensions, well layout, etc.")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship to specific instances of this labware type
    labware_instances = relationship("LabwareInstanceOrm", back_populates="labware_definition")

    def __repr__(self):
        return f"<LabwareDefinitionCatalogOrm(name='{self.pylabrobot_definition_name}', category='{self.category.value}')>" # TODO: ASSET-DB-4: Add more details if needed


class LabwareInstanceOrm(Base):
    __tablename__ = "labware_instances"

    id = Column(Integer, primary_key=True, index=True) # praxis_labware_instance_id
    user_assigned_name = Column(String, nullable=False, unique=True, index=True, comment="User-friendly unique name for this physical item")

    pylabrobot_definition_name = Column(String, ForeignKey("labware_definition_catalog.pylabrobot_definition_name"), nullable=False, index=True)

    lot_number = Column(String, nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True) # Use DateTime for date part
    date_added_to_inventory = Column(DateTime(timezone=True), server_default=func.now())

    current_status = Column(SAEnum(LabwareInstanceStatusEnum, name="labware_instance_status_enum"), default=LabwareInstanceStatusEnum.UNKNOWN, nullable=False, index=True)

    # Location tracking
    # If on a deck, deck_device_id + current_deck_slot_name should be set.
    # If inside another device (e.g. plate in reader), location_device_id is set.
    # If in general storage, physical_location_description can be used.
    current_deck_slot_name = Column(String, nullable=True, comment="If on a deck, the slot name (e.g., A1, SLOT_7)")
    location_device_id = Column(Integer, ForeignKey("managed_devices.id"), nullable=True, comment="FK to ManagedDeviceOrm if located on/in a device (deck, reader, etc.)")
    physical_location_description = Column(String, nullable=True, comment="General storage location if not on a device")

    properties_json = Column(JSON, nullable=True, comment="Instance-specific state (e.g., well contents, used tips map)")
    is_permanent_fixture = Column(Boolean, default=False, comment="e.g., built-in waste chute")

    current_protocol_run_guid = Column(String, ForeignKey("protocol_runs.run_guid", ondelete="SET NULL"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    labware_definition = relationship("LabwareDefinitionCatalogOrm", back_populates="labware_instances")
    location_device = relationship("ManagedDeviceOrm", back_populates="located_labware_instances")
    # protocol_run = relationship("ProtocolRunOrm", foreign_keys=[current_protocol_run_guid]) # If linking to runs

    # Relationship to deck configuration items
    deck_configuration_items = relationship("DeckConfigurationSlotItemOrm", back_populates="labware_instance")


    def __repr__(self):
        return f"<LabwareInstanceOrm(id={self.id}, name='{self.user_assigned_name}', type='{self.pylabrobot_definition_name}')>"


class DeckConfigurationOrm(Base):
    __tablename__ = "deck_configurations"

    id = Column(Integer, primary_key=True, index=True) # praxis_deck_config_id
    layout_name = Column(String, nullable=False, unique=True, index=True)

    # A Deck itself is a ManagedDevice
    deck_device_id = Column(Integer, ForeignKey("managed_devices.id"), nullable=False)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    deck_device = relationship("ManagedDeviceOrm", back_populates="deck_configurations")
    slot_items = relationship("DeckConfigurationSlotItemOrm", back_populates="deck_configuration", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DeckConfigurationOrm(id={self.id}, name='{self.layout_name}')>"


class DeckConfigurationSlotItemOrm(Base):
    __tablename__ = "deck_configuration_slot_items"

    id = Column(Integer, primary_key=True, index=True)
    deck_configuration_id = Column(Integer, ForeignKey("deck_configurations.id"), nullable=False)
    slot_name = Column(String, nullable=False, comment="Slot name on the deck (e.g., A1, SLOT_7)")

    # This links to a specific physical piece of labware
    labware_instance_id = Column(Integer, ForeignKey("labware_instances.id"), nullable=False)

    # Optional: for validation, store the expected type of labware for this slot in this layout
    expected_labware_definition_name = Column(String, ForeignKey("labware_definition_catalog.pylabrobot_definition_name"), nullable=True)

    deck_configuration = relationship("DeckConfigurationOrm", back_populates="slot_items")
    labware_instance = relationship("LabwareInstanceOrm", back_populates="deck_configuration_items")
    expected_labware_definition = relationship("LabwareDefinitionCatalogOrm") # Simple relationship

    __table_args__ = (UniqueConstraint('deck_configuration_id', 'slot_name', name='uq_deck_slot_item'),)

    def __repr__(self):
        return f"<DeckConfigurationSlotItemOrm(deck_config_id={self.deck_configuration_id}, slot='{self.slot_name}', lw_instance_id={self.labware_instance_id})>"

