"""SQLAlchemy ORM models for asset management in the Praxis application.

These models define the database schema for:
- **ResourceDefinitionOrm**: Stores static definitions of resource types from
  PyLabRobot.
- **ResourceOrm**: Represents specific physical instances of resources, tracking
  their status and location.
- **ResourceStatusEnum**: Enumerates the possible operational statuses of a
  resource instance.
- **ResourceDefinitionOrm**: Catalogs resource definitions with metadata
  including dimensions, categories, and PyLabRobot definitions.
- **ResourceCategoryEnum**: Enumerates the categories of resources in the catalog,
  providing a hierarchical classification system.
"""

import enum
import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
  JSON,
  UUID,
  Boolean,
  Float,
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
from praxis.backend.models.timestamp_mixin import TimestampMixin
from praxis.backend.utils.db import Base
from praxis.backend.utils.uuid import uuid7

if TYPE_CHECKING:
  from praxis.backend.models.deck_orm import DeckOrm
  from praxis.backend.models.machine_orm import MachineOrm


class ResourceStatusEnum(enum.Enum):
  """Enumeration for the possible operational statuses of a resource instance."""

  AVAILABLE_IN_STORAGE = "available_in_storage"
  AVAILABLE_ON_DECK = "available_on_deck"
  IN_USE = "in_use"
  EMPTY = "empty"
  PARTIALLY_FILLED = "partially_filled"
  FULL = "full"
  NEEDS_REFILL = "needs_refill"
  TO_BE_DISPOSED = "to_be_disposed"
  DISPOSED = "disposed"
  TO_BE_CLEANED = "to_be_cleaned"
  CLEANED = "cleaned"
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
  def choices(cls) -> list[str]:
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
  def consumables(cls) -> list[str]:
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
  def machines(cls) -> list[str]:
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


class ResourceDefinitionOrm(TimestampMixin, Base):
  """SQLAlchemy ORM model for cataloging PyLabRobot resource definitions.

  This model stores comprehensive metadata about various types of lab resources,
  derived from PyLabRobot's definitions, including their dimensions and categories.
  """

  __tablename__ = "resource_definition_catalog"

  accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    primary_key=True,
    default=uuid7,
    index=True,
  )
  name: Mapped[str] = mapped_column(String, unique=True, index=True)
  fqn: Mapped[str] = mapped_column(  # Renamed from 'fqn' to 'fqn'
    String,
    nullable=False,
    index=True,
    comment="Fully qualified name of the resource definition.",
  )
  resource_type: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="Human-readable type of the resource.",
  )
  description: Mapped[str | None] = mapped_column(Text, nullable=True)
  is_consumable: Mapped[bool] = mapped_column(Boolean, default=True)
  nominal_volume_ul: Mapped[float | None] = mapped_column(Float, nullable=True)
  material: Mapped[str | None] = mapped_column(String, nullable=True)
  manufacturer: Mapped[str | None] = mapped_column(String, nullable=True)
  plr_definition_details_json: Mapped[dict | None] = mapped_column(
    JSON,
    nullable=True,
    comment="Additional PyLabRobot specific definition details as JSON.",
  )

  size_x_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
  size_y_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
  size_z_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
  plr_category: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    index=True,
    comment=(
      "Specific PyLabRobot resource class name (e.g., 'Plate', 'TipRack',"
      " 'Carrier', 'Trough') from the PLR ontology. Corresponds to PLR"
      " Resource.category or the direct subclass name."
    ),
  )
  model: Mapped[str | None] = mapped_column(String, nullable=True)
  rotation_json: Mapped[dict | None] = mapped_column(
    JSON,
    nullable=True,
    comment=(
      "Represents PLR Resource.rotation, e.g., {'x_deg': 0, 'y_deg': 0,"
      " 'z_deg': 90} or PLR rotation object serialized"
    ),
  )

  resource_list: Mapped[list["ResourceOrm"]] = relationship(
    "ResourceOrm",
    back_populates="resource_definition",
  )

  is_machine: Mapped[bool] = mapped_column(Boolean, default=False)

  def __repr__(self):
    """Return a string representation of the ResourceDefinitionOrm object."""
    return f"<ResourceDefinitionOrm(name='{self.name}', category='{self.plr_category}')>"


class ResourceOrm(Asset):
  """SQLAlchemy ORM model representing a physical instance of a resource.

  This model tracks individual physical items of lab resources,
  including their unique name, current status, location, and associated properties.
  It also supports hierarchical relationships between resources (parent-child).
  """

  __tablename__ = "resources"
  __mapper_args__ = {"polymorphic_identity": "resource"}

  accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("assets.accession_id"),
    primary_key=True,
    default=uuid7,
  )
  name: Mapped[str] = mapped_column(String, nullable=False, index=True)
  asset_type: Mapped[AssetType] = mapped_column(
    SAEnum(AssetType, name="asset_type_enum"),
    nullable=False,
    index=True,
  )

  # Hierarchical relationship
  parent_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("resources.accession_id"),
    nullable=True,
    index=True,
  )
  parent: Mapped[Optional["ResourceOrm"]] = relationship(
    "ResourceOrm",
    remote_side=[accession_id],
    back_populates="children",
    foreign_keys=[parent_accession_id],
  )
  children: Mapped[list["ResourceOrm"]] = relationship(
    "ResourceOrm",
    back_populates="parent",
    cascade="all, delete-orphan",
  )

  # Definition
  resource_definition_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("resource_definition_catalog.accession_id"),
    nullable=False,
    index=True,
  )
  resource_definition: Mapped["ResourceDefinitionOrm"] = relationship(
    "ResourceDefinitionOrm",
    back_populates="resource_list",
  )

  # State
  location: Mapped[str | None] = mapped_column(String, nullable=True)
  properties_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
  current_status: Mapped[ResourceStatusEnum] = mapped_column(
    SAEnum(ResourceStatusEnum, name="resource_status_enum"),
    default=ResourceStatusEnum.UNKNOWN,
    nullable=False,
    index=True,
  )
  status_details: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    comment="Additional details about the current status, e.g., error message",
  )

  # Counterparts
  machine_counterpart: Mapped[Optional["MachineOrm"]] = relationship(
    "MachineOrm",
    back_populates="resource_counterpart",
  )
  deck_counterpart: Mapped[Optional["DeckOrm"]] = relationship(
    "DeckOrm",
    back_populates="resource_counterpart",
  )

  def __repr__(self):
    """Return a string representation of the ResourceOrm object."""
    fqn = (
      self.resource_definition.fqn  # type: ignore
      if self.resource_definition and hasattr(self.resource_definition, "fqn")
      else "N/A"
    )
    return (
      f"<ResourceOrm(accession_id={self.accession_id}, name='{self.name}',"
      f" type='{fqn}')> status={self.current_status.value}, "
    )
