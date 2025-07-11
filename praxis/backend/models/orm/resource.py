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

import uuid
from typing import TYPE_CHECKING, ClassVar

from sqlalchemy import (
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
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from praxis.backend.models.enums.resource import ResourceStatusEnum
from praxis.backend.models.orm.asset import AssetOrm
from praxis.backend.models.orm.plr_sync import PLRTypeDefinitionOrm

if TYPE_CHECKING:
  from . import (
    DeckDefinitionOrm,
    DeckOrm,
    FunctionDataOutputOrm,
    MachineDefinitionOrm,
    MachineOrm,
    WellDataOutputOrm,
    WorkcellOrm,
  )


class ResourceDefinitionOrm(PLRTypeDefinitionOrm):
  """SQLAlchemy ORM model for cataloging PyLabRobot resource definitions.

  This model stores comprehensive metadata about various types of lab resources,
  derived from PyLabRobot's definitions, including their dimensions and categories.
  """

  __tablename__ = "resource_definition_catalog"

  resource_type: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="Human-readable type of the resource.",
    default=None,
  )
  is_consumable: Mapped[bool] = mapped_column(Boolean, default=False)
  nominal_volume_ul: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
    comment="Nominal volume in microliters, if applicable.",
  )
  material: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
    comment="Material of the resource, e.g., 'polypropylene', 'glass'.",
  )
  manufacturer: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
    comment="Manufacturer of the resource, if applicable.",
  )
  plr_definition_details_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="Additional PyLabRobot specific definition details as JSONB.",
    default=None,
  )

  size_x_mm: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
    comment="Size in X dimension (mm).",
  )
  size_y_mm: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
    comment="Size in Y dimension (mm).",
  )
  size_z_mm: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
    comment="Size in Z dimension (mm).",
  )
  model: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
    comment="Model of the resource, if applicable.",
  )
  rotation_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment=(
      "Represents PLR Resource.rotation, e.g., {'x_deg': 0, 'y_deg': 0,"
      " 'z_deg': 90} or PLR rotation object serialized"
    ),
    default=None,
  )

  resource_list: Mapped[list["ResourceOrm"]] = relationship(
    "ResourceOrm",
    back_populates="resource_definition",
    cascade="all, delete-orphan",
    comment="List of all physical resources defined by this definition.",
    default_factory=list,
  )

  is_machine: Mapped[bool] = mapped_column(Boolean, default=False)

  machine_definition_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("machine_definition_catalog.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the machine definition catalog, if this resource is also a machine.",
    default=None,
  )
  deck_definition_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("deck_definition_catalog.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the deck definition catalog, if this resource is also a deck.",
    default=None,
  )
  machine_definition: Mapped["MachineDefinitionOrm | None"] = relationship(
    "MachineDefinitionOrm",
    back_populates="resource_definition",
    nullable=True,
    uselist=False,
    foreign_keys=[machine_definition_accession_id],
    comment="Machine definition associated with this resource, if applicable.",
    default=None,
  )
  deck_definition: Mapped["DeckDefinitionOrm | None"] = relationship(
    "DeckDefinitionOrm",
    back_populates="resource_definition",
    uselist=False,
    foreign_keys=[deck_definition_accession_id],
    comment="Deck definition associated with this resource, if applicable.",
    nullable=True,
    default=None,
  )


class ResourceOrm(AssetOrm):
  """SQLAlchemy ORM model representing a physical instance of a resource.

  This model tracks individual physical items of lab resources,
  including their unique name, current status, location, and associated properties.
  It also supports hierarchical relationships between resources (parent-child).
  """

  __tablename__ = "resources"
  __mapper_args__: ClassVar[dict[str, str]] = {"polymorphic_identity": "resource"}

  accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("assets.accession_id"),
    primary_key=True,
    index=True,
    comment="Unique identifier for the resource, derived from the Asset base class.",
    kw_only=True,
  )

  parent_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("resources.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the parent resource's accession ID, if this is a child resource.",
    default=None,
  )
  parent: Mapped["ResourceOrm | None"] = relationship(
    "ResourceOrm",
    remote_side=[accession_id],
    back_populates="children",
    foreign_keys=[parent_accession_id],
    uselist=False,
    comment="Parent resource in a hierarchical structure, if applicable.",
    default=None,
  )
  children: Mapped[list["ResourceOrm"]] = relationship(
    "ResourceOrm",
    back_populates="parent",
    cascade="all, delete-orphan",
    default_factory=list,
  )

  # Definition
  resource_definition_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("resource_definition_catalog.accession_id"),
    nullable=False,
    index=True,
    comment="Foreign key to the resource definition catalog.",
    default=None,
  )
  resource_definition: Mapped["ResourceDefinitionOrm"] = relationship(
    "ResourceDefinitionOrm",
    back_populates="resource_list",
    default=None,
  )

  # State
  status: Mapped[ResourceStatusEnum] = mapped_column(
    SAEnum(ResourceStatusEnum, name="resource_status_enum"),
    default=ResourceStatusEnum.UNKNOWN,
    nullable=False,
    index=True,
  )
  status_details: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    comment="Additional details about the current status, e.g., error message",
    default=None,
  )

  # Counterparts
  machine_counterpart: Mapped["MachineOrm | None"] = relationship(
    "MachineOrm",
    back_populates="resource_counterpart",
    default=None,
  )
  deck_counterpart: Mapped["DeckOrm | None"] = relationship(
    "DeckOrm",
    back_populates="resource_counterpart",
    default=None,
  )
  data_outputs: Mapped[list["FunctionDataOutputOrm"]] = relationship(
    "FunctionDataOutputOrm",
    back_populates="resource",
    cascade="all, delete-orphan",
    default_factory=list,
  )
  well_data_outputs: Mapped[list["WellDataOutputOrm"]] = relationship(
    "WellDataOutputOrm",
    back_populates="plate_resource",
    cascade="all, delete-orphan",
    default_factory=list,
  )
  location_machine: Mapped["MachineOrm | None"] = relationship(
    "MachineOrm",
    back_populates="located_resource",
    uselist=False,
    default=None,
  )
  workcell_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("workcells.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the workcell this resource belongs to, if applicable.",
    default=None,
  )
  workcell: Mapped["WorkcellOrm | None"] = relationship(
    "WorkcellOrm",
    back_populates="resources",
    uselist=False,
    default=None,
  )
  location_deck: Mapped["DeckOrm | None"] = relationship(
    "DeckOrm",
    back_populates="resources",
    uselist=False,
    default=None,
  )

  def __repr__(self) -> str:
    """Return a string representation of the ResourceOrm object."""
    fqn = (
      self.resource_definition.fqn
      if self.resource_definition and hasattr(self.resource_definition, "fqn")
      else "N/A"
    )
    return (
      f"<ResourceOrm(accession_id={self.accession_id}, name='{self.name}',"
      f" type='{fqn}')> status={self.status.value}, "
    )
