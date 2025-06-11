"""SQLAlchemy ORM models for asset management in the Praxis application.

These models define the database schema for:
- **ResourceDefinitionCatalogOrm**: Stores static definitions of resource types from
  PyLabRobot.
- **ResourceInstanceOrm**: Represents specific physical instances of resources, tracking
  their status and location.
- **ResourceInstanceStatusEnum**: Enumerates the possible operational statuses of a
  resource instance.
- **ResourceDefinitionCatalogOrm**: Catalogs resource definitions with metadata
  including dimensions, categories, and PyLabRobot definitions.
- **ResourceCategoryEnum**: Enumerates the categories of resources in the catalog,
  providing a hierarchical classification system.
"""

import enum
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
  from .deck_orm import DeckInstanceOrm
  from .machine_orm import MachineOrm

import uuid_utils as uuid
from sqlalchemy import (
  JSON,
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
from sqlalchemy.sql import func

from praxis.backend.utils.db import Base


class ResourceInstanceStatusEnum(enum.Enum):
  """Enumeration for the possible operational statuses of a resource instance."""

  AVAILABLE_IN_STORAGE = "available_in_storage"
  AVAILABLE_ON_DECK = "available_on_deck"
  IN_USE = "in_use"
  EMPTY = "empty"
  PARTIALLY_FILLED = "partially_filled"
  FULL = "full"
  NEEDS_REFILL = "needs_refill"
  TO_BE_DISPOSED = "to_be_disposed"
  TO_BE_CLEANED = "to_be_cleaned"
  ERROR = "error"
  UNKNOWN = "unknown"


class ResourceCategoryEnum(enum.Enum):
  """Enumeration for the categories of resources in the catalog.

  This enum defines the main categories of lab resources based on a hierarchical
  classification, used to classify resources in the catalog.
  """

  # Top-level categories
  ARM = "Arm"
  CARRIER = "Carrier"
  CONTAINER = "Container"
  DECK = "Deck"
  ITEMIZED_RESOURCE = "ItemizedResource"
  RESOURCE_HOLDER = "ResourceHolder"
  LID = "Lid"
  PLATE_ADAPTER = "PlateAdapter"
  RESOURCE_STACK = "ResourceStack"
  # General catch-all for resources not fitting specific categories
  OTHER = "Other"

  # Subcategories (can be used for more granular classification if needed)
  # Arm

  # Carrier
  MFX_CARRIER = "MFXCarrier"
  PLATE_CARRIER = "PlateCarrier"
  TIP_CARRIER = "TipCarrier"
  TROUGH_CARRIER = "TroughCarrier"
  TUBE_CARRIER = "TubeCarrier"

  # Container
  PETRI_DISH = "PetriDish"
  TROUGH = "Trough"
  TUBE = "Tube"
  WELL = "Well"

  # Deck
  OT_DECK = "OTDeck"
  HAMILTON_DECK = "HamiltonDeck"
  TECAN_DECK = "TecanDeck"

  # ItemizedResource
  PLATE = "Plate"
  TIP_RACK = "TipRack"
  TUBE_RACK = "TubeRack"

  # ResourceHolder
  PLATE_HOLDER = "PlateHolder"

  # Machines
  SHAKER = "Shaker"
  HEATERSHAKER = "HeaterShaker"
  PLATE_READER = "PlateReader"
  TEMPERATURE_CONTROLLER = "TemperatureController"
  CENTRIFUGE = "Centrifuge"
  INCUBATOR = "Incubator"
  TILTER = "Tilter"
  THERMOCYCLER = "Thermocycler"  # not yet available in standard PLR
  SCALE = "Scale"

  @classmethod
  def choices(cls) -> List[str]:
    """Return a list of valid top-level category choices."""
    # This method returns the top-level categories, similar to how
    # the original `choices` might have been used for a general filter.
    return [
      cls.ARM.value,
      cls.CARRIER.value,
      cls.CONTAINER.value,
      cls.DECK.value,
      cls.ITEMIZED_RESOURCE.value,
      cls.RESOURCE_HOLDER.value,
      cls.LID.value,
      cls.PLATE_ADAPTER.value,
      cls.RESOURCE_STACK.value,
      cls.OTHER.value,
    ]

  @classmethod
  def consumables(cls) -> List[str]:
    """Return a list of common consumable categories.

    This list might need refinement based on how 'consumable' is strictly
    defined for each new category.
    """
    return [
      cls.PETRI_DISH.value,
      cls.TROUGH.value,
      cls.TUBE.value,
      cls.WELL.value,  # Individual wells might be considered consumable parts
      cls.PLATE.value,  # Plates are typically consumables
      cls.TIP_RACK.value,
      cls.TUBE_RACK.value,
      cls.LID.value,
    ]

  @classmethod
  def machines(cls) -> List[str]:
    """Return a list of resources that are also machines."""
    return [
      cls.ARM.value,
      cls.SHAKER.value,
      cls.HEATERSHAKER.value,
      cls.PLATE_READER.value,
      cls.TEMPERATURE_CONTROLLER.value,
      cls.CENTRIFUGE.value,
      cls.INCUBATOR.value,
      cls.TILTER.value,
      cls.THERMOCYCLER.value,  # not yet pulled in PLR
      cls.SCALE.value,
    ]


class ResourceDefinitionCatalogOrm(Base):
  """SQLAlchemy ORM model for cataloging PyLabRobot resource definitions.

  This model stores comprehensive metadata about various types of lab resources,
  derived from PyLabRobot's definitions, including their dimensions and categories.
  """

  __tablename__ = "resource_definition_catalog"

  id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  name: Mapped[str] = mapped_column(
    String,
    primary_key=True,
    index=True,
    comment=(
      "Unique name from PyLabRobot (e.g., corning_96_wellplate_360ul_flat),"
      " corresponds to PLR Resource.name"
    ),
  )
  python_fqn: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment=(
      "Fully qualified Python class name of the specific PyLabRobot"
      " resource definition (e.g., 'pylabrobot.resources.corning_96_wellplate_360ul_"
      "flat.Corning96WellPlate360uLFlat',"
      " or 'pylabrobot.resources.plate.Plate' if generic)."
    ),
  )

  size_x_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  size_y_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  size_z_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  plr_category: Mapped[Optional[str]] = mapped_column(
    String,
    nullable=True,
    index=True,
    comment=(
      "Specific PyLabRobot resource class name (e.g., 'Plate', 'TipRack',"
      " 'Carrier', 'Trough') from the PLR ontology. Corresponds to PLR"
      " Resource.category or the direct subclass name."
    ),
  )
  model: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  rotation_json: Mapped[Optional[dict]] = mapped_column(
    JSON,
    nullable=True,
    comment=(
      "Represents PLR Resource.rotation, e.g., {'x_deg': 0, 'y_deg': 0,"
      " 'z_deg': 90} or PLR rotation object serialized"
    ),
  )

  resource_type: Mapped[Optional[str]] = mapped_column(
    String, nullable=True, unique=True
  )
  description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
  is_consumable: Mapped[bool] = mapped_column(Boolean, default=True)
  nominal_volume_ul: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  material: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  manufacturer: Mapped[Optional[str]] = mapped_column(String, nullable=True)

  plr_definition_details_json: Mapped[Optional[dict]] = mapped_column(
    JSON,
    nullable=True,
    comment=(
      "Additional PLR-specific details not covered by dedicated columns"
      " (e.g., well layout, specific geometry details)"
    ),
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

  is_machine: Mapped[bool] = mapped_column(Boolean, default=False)

  def __repr__(self):
    """Return a string representation of the ResourceDefinitionCatalogOrm object."""
    return (
      f"<ResourceDefinitionCatalogOrm(name='{self.name}',"
      f" category='{self.plr_category}')>"
    )


class ResourceInstanceOrm(Base):
  """SQLAlchemy ORM model representing a physical instance of a resource.

  This model tracks individual physical items of lab resources,
  including their unique name, current status, location, and associated properties.
  """

  __tablename__ = "resource_instances"

  id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  user_assigned_name: Mapped[str] = mapped_column(
    String,
    nullable=False,
    unique=True,
    index=True,
    comment="User-friendly unique name for this physical item",
  )

  name: Mapped[str] = mapped_column(
    String,
    ForeignKey("resource_definition_catalog.name"),
    nullable=False,
    index=True,
  )

  lot_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  expiry_date: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
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
    comment="Additional details about the current status," " e.g., error message",
  )

  current_deck_position_name: Mapped[Optional[str]] = mapped_column(
    String, nullable=True, comment="If on a deck, the position name (e.g., A1, SLOT_7)"
  )

  location_machine_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    UUID,
    ForeignKey("machines.id"),
    nullable=True,
    comment="FK to MachineOrm if located on/in a machine (LiquidHandler, etc.)",
  )

  physical_location_description: Mapped[Optional[str]] = mapped_column(
    String, nullable=True, comment="General storage location if not on a machine"
  )

  properties_json: Mapped[Optional[dict]] = mapped_column(
    JSON,
    nullable=True,
    comment=(
      "Instance-specific state combining PLR runtime inspection (e.g., well"
      " contents, used tips map) and user-provided metadata (e.g., sample"
      " info, reagent data)"
    ),
  )
  is_permanent_fixture: Mapped[bool] = mapped_column(
    Boolean, default=False, comment="e.g., built-in waste chute"
  )

  current_protocol_run_guid: Mapped[Optional[uuid.UUID]] = mapped_column(
    UUID,
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

  deck_instance_items = relationship(
    "DeckInstancePositionResourceOrm", back_populates="resource_instance"
  )

  is_consumable: Mapped[bool] = mapped_column(
    Boolean, default=True, comment="True if this instance is a consumable item"
  )

  is_machine: Mapped[bool] = mapped_column(
    Boolean, default=False, comment="True if this instance is a machine (e.g., shaker)"
  )

  machine_counterpart_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    UUID,
    ForeignKey("machines.id", ondelete="SET NULL"),
    nullable=True,
    index=True,
    comment="If this resource instance is a machine, links to the MachineOrm entry",
  )

  machine_counterpart: Mapped[Optional["MachineOrm"]] = relationship(
    "MachineOrm",
    back_populates="resource_counterpart",
    foreign_keys=[machine_counterpart_id],
    uselist=False,
    cascade="all, delete-orphan",
    comment="If this resource instance is a machine, links to the MachineOrm entry",
  )

  deck_counterpart_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    UUID,
    ForeignKey("deck_instances.id", ondelete="SET NULL"),
    nullable=True,
    index=True,
    comment="If this resource instance is a deck instanceuration item, links to the "
    "DeckInstanceOrm entry",
  )

  deck_counterpart: Mapped[Optional["DeckInstanceOrm"]] = relationship(
    "DeckInstanceOrm",
    back_populates="resource_instance",
    foreign_keys=[deck_counterpart_id],
    uselist=False,
    cascade="all, delete-orphan",
    comment="If this resource instance is a deck instanceuration item, links to the "
    "DeckInstanceOrm entry",
  )

  def __repr__(self):
    """Return a string representation of the ResourceInstanceOrm object."""
    return (
      f"<ResourceInstanceOrm(id={self.id}, name='{self.user_assigned_name}',"
      f" type='{self.name}', is_machine={self.is_machine})>"
    )
