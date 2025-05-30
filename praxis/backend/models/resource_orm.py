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
"""

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import (
  JSON,
  Boolean,
  DateTime,
  Float,
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
  ERROR = "error"
  UNKNOWN = "unknown"


class ResourceDefinitionCatalogOrm(Base):
  """SQLAlchemy ORM model for cataloging PyLabRobot resource definitions.

  This model stores comprehensive metadata about various types of lab resources,
  derived from PyLabRobot's definitions, including their dimensions and categories.
  """

  __tablename__ = "resource_definition_catalog"

  pylabrobot_definition_name: Mapped[str] = mapped_column(
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

  praxis_resource_type_name: Mapped[Optional[str]] = mapped_column(
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

  def __repr__(self):
    """Return a string representation of the ResourceDefinitionCatalogOrm object."""
    return (
      f"<ResourceDefinitionCatalogOrm(name='{self.pylabrobot_definition_name}',"
      f" category='{self.plr_category}')>"
    )


class ResourceInstanceOrm(Base):
  """SQLAlchemy ORM model representing a physical instance of a resource.

  This model tracks individual physical items of lab resources,
  including their unique name, current status, location, and associated properties.
  """

  __tablename__ = "resource_instances"

  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
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
    comment=(
      "Instance-specific state combining PLR runtime inspection (e.g., well"
      " contents, used tips map) and user-provided metadata (e.g., sample"
      " info, reagent data)"
    ),
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

  deck_configuration_items = relationship(
    "DeckConfigurationSlotItemOrm", back_populates="resource_instance"
  )

  def __repr__(self):
    """Return a string representation of the ResourceInstanceOrm object."""
    return (
      f"<ResourceInstanceOrm(id={self.id}, name='{self.user_assigned_name}',"
      f" type='{self.pylabrobot_definition_name}')>"
    )
