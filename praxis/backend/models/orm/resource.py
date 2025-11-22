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
  ordering: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
    comment="Ordering information for the resource, if applicable.",
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
    default_factory=list,
  )

  deck_definition_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("deck_definition_catalog.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the deck definition catalog, if this resource is also a deck.",
    default=None,
  )
  asset_requirement_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("protocol_asset_requirements.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the asset requirement this resource definition satisfies.",
    default=None,
  )
  asset_requirement: Mapped["AssetRequirementOrm"] = relationship(
    "AssetRequirementOrm",
    back_populates="resource_definitions",
    uselist=False,
    default=None,
    foreign_keys=[asset_requirement_accession_id],
  )
  machine_definition: Mapped["MachineDefinitionOrm | None"] = relationship(
    "MachineDefinitionOrm",
    back_populates="resource_definition",
    uselist=False,
    default=None,
    init=False,
  )
  deck_definition: Mapped["DeckDefinitionOrm | None"] = relationship(
    "DeckDefinitionOrm",
    back_populates="resource_definition",
    uselist=False,
    foreign_keys=[deck_definition_accession_id],
    default=None,
    init=False,
  )


class ResourceOrm(AssetOrm):

  """SQLAlchemy ORM model representing a physical instance of a resource.

  This model tracks individual physical items of lab resources,
  including their unique name, current status, location, and associated properties.
  It also supports hierarchical relationships between resources (parent-child).
  """

  __tablename__ = "resources"
  __mapper_args__: ClassVar[dict[str, str]] = {"polymorphic_identity": "RESOURCE"}

  accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("assets.accession_id"),
    primary_key=True,
    index=True,
    comment="Unique identifier for the resource, derived from the Asset base class.",
  )

  # Definition
  resource_definition_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("resource_definition_catalog.accession_id"),
    nullable=True,  # Nullable due to MappedAsDataclass + joined inheritance limitation
    index=True,
    comment="Foreign key to the resource definition catalog.",
    default=None,
  )

  resource_definition: Mapped["ResourceDefinitionOrm"] = relationship(
    "ResourceDefinitionOrm",
    back_populates="resource_list",
    uselist=False,
    foreign_keys=[resource_definition_accession_id],
    init=False,
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
    init=False,
  )

  children: Mapped[list["ResourceOrm"]] = relationship(
    "ResourceOrm",
    back_populates="parent",
    cascade="all, delete-orphan",
    default_factory=list,
    uselist=True,
    init=False,
    foreign_keys=[parent_accession_id],
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

  current_protocol_run_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("protocol_runs.accession_id", ondelete="SET NULL"),
    nullable=True,
    index=True,
    comment="Foreign key to the current protocol run this resource is used in, if applicable.",
    default=None,
  )

  current_deck_position_name: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="Name of the deck position where the resource is currently located.",
    default=None,
  )

  # Counterparts
  machine_counterpart: Mapped["MachineOrm | None"] = relationship(
    "MachineOrm",
    back_populates="resource_counterpart",
    uselist=False,
    primaryjoin="ResourceOrm.accession_id == foreign(MachineOrm.accession_id)",
    viewonly=True,
    init=False,
  )
  deck_counterpart: Mapped["DeckOrm | None"] = relationship(
    "DeckOrm",
    back_populates="resource_counterpart",
    uselist=False,
    foreign_keys=[accession_id],
    init=False,
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

  machine_location_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("machines.accession_id", use_alter=True, name="fk_resource_machine_location"),
    nullable=True,
    index=True,
    comment="Foreign key to the machine where this resource is currently located, if applicable.",
    default=None,
  )

  location_machine: Mapped["MachineOrm | None"] = relationship(
    "MachineOrm",
    back_populates="located_resource",
    uselist=False,
    foreign_keys=[machine_location_accession_id],
    init=False,
  )

  deck_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("decks.accession_id", use_alter=True, name="fk_resource_deck"),
    nullable=True,
    index=True,
    comment="Foreign key to the deck this resource is located on, if applicable.",
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
    foreign_keys=[workcell_accession_id],
    init=False,
  )

  deck: Mapped["DeckOrm | None"] = relationship(
    "DeckOrm",
    back_populates="resources",
    uselist=False,
    foreign_keys=[deck_accession_id],
    init=False,
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

  @property
  def child_accession_ids(self) -> list[uuid.UUID]:
    """Return a list of accession IDs for child resources."""
    return [child.accession_id for child in self.children]

  @property
  def is_machine(self) -> bool:
    """Return True if the asset is also a machine."""
    return self.machine_counterpart_accession_id is not None

  @property
  def is_resource(self) -> bool:
    """Return True if the asset is a resource."""
    return True
