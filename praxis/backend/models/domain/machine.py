# pylint: disable=too-few-public-methods,missing-class-docstring
"""Unified SQLModel definitions for Machine and MachineDefinition."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional

from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.orm import relationship

from praxis.backend.models.domain.asset import Asset, AssetBase, AssetRead
from praxis.backend.models.domain.sqlmodel_base import PraxisBase
from praxis.backend.models.enums import (
  MachineCategoryEnum,
  MachineStatusEnum,
)
from praxis.backend.utils.db import JsonVariant

if TYPE_CHECKING:
  from praxis.backend.models.domain.deck import Deck
  from praxis.backend.models.domain.resource import Resource
  from praxis.backend.models.domain.workcell import Workcell

# =============================================================================
# Machine Definition (Catalog)
# =============================================================================


class MachineDefinitionBase(PraxisBase):
  """Base schema for MachineDefinition - shared fields for create/update/response."""

  fqn: str = Field(index=True, unique=True, description="Fully qualified name")
  description: str | None = Field(default=None, description="Description of the machine type")
  plr_category: str | None = Field(default=None, description="PyLabRobot category")
  machine_category: MachineCategoryEnum = Field(
    default=MachineCategoryEnum.UNKNOWN,
    description="Category of the machine",
  )
  material: str | None = Field(default=None)
  manufacturer: str | None = Field(default=None)
  model: str | None = Field(default=None)
  size_x_mm: float | None = Field(default=None, description="Size in X dimension (mm)")
  size_y_mm: float | None = Field(default=None, description="Size in Y dimension (mm)")
  size_z_mm: float | None = Field(default=None, description="Size in Z dimension (mm)")
  has_deck: bool = Field(default=False, description="Whether this machine has a deck")
  frontend_fqn: str | None = Field(default=None, description="PLR frontend class FQN")


class MachineDefinition(MachineDefinitionBase, table=True):
  """MachineDefinition ORM model - catalog of machine types."""

  __tablename__ = "machine_definitions"

  plr_definition_details_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Additional PyLabRobot definition details"
  )
  rotation_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="PLR rotation object"
  )
  setup_method_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Setup method configuration"
  )
  capabilities: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Hardware capabilities (channels, modules)"
  )
  compatible_backends: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Compatible backend class FQNs"
  )
  capabilities_config: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="User-configurable capabilities schema"
  )
  connection_config: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Connection parameters schema"
  )

  # Foreign keys
  resource_definition_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Resource definition accession ID",
    foreign_key="resource_definitions.accession_id",
  )
  deck_definition_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Deck definition accession ID",
    foreign_key="deck_definition_catalog.accession_id",
  )
  asset_requirement_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Asset requirement accession ID",
    foreign_key="protocol_asset_requirements.accession_id",
  )


class MachineDefinitionCreate(MachineDefinitionBase):
  """Schema for creating a MachineDefinition."""


class MachineDefinitionRead(MachineDefinitionBase):
  """Schema for reading a MachineDefinition (API response)."""

  accession_id: uuid.UUID
  plr_definition_details_json: dict[str, Any] | None = None
  rotation_json: dict[str, Any] | None = None
  setup_method_json: dict[str, Any] | None = None


class MachineDefinitionUpdate(SQLModel):
  """Schema for updating a MachineDefinition (partial update)."""

  name: str | None = None
  fqn: str | None = None
  description: str | None = None
  plr_category: str | None = None
  machine_category: MachineCategoryEnum | None = None
  material: str | None = None
  manufacturer: str | None = None
  model: str | None = None
  size_x_mm: float | None = None
  size_y_mm: float | None = None
  size_z_mm: float | None = None
  has_deck: bool | None = None
  frontend_fqn: str | None = None
  plr_definition_details_json: dict[str, Any] | None = None
  rotation_json: dict[str, Any] | None = None
  setup_method_json: dict[str, Any] | None = None


# =============================================================================
# Machine (Physical Instance)
# =============================================================================


class MachineBase(AssetBase):
  """Base schema for Machine - shared fields for create/update/response."""

  machine_category: MachineCategoryEnum = Field(
    default=MachineCategoryEnum.UNKNOWN,
  )
  description: str | None = Field(default=None)
  manufacturer: str | None = Field(default=None)
  model: str | None = Field(default=None)
  serial_number: str | None = Field(default=None)  # Removed unique=True constraint for schema
  location_label: str | None = Field(default=None, description="Physical location label")
  installation_date: datetime | None = Field(default=None)
  status: MachineStatusEnum = Field(
    default=MachineStatusEnum.OFFLINE,
  )
  status_details: str | None = Field(default=None)
  is_simulation_override: bool | None = Field(default=None)
  last_seen_online: datetime | None = Field(default=None, index=True)
  maintenance_enabled: bool = Field(default=True)

  # JSON fields
  connection_info: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Connection details (backend, address, etc.)"
  )
  user_configured_capabilities: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="User-specified capability overrides"
  )
  maintenance_schedule_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Custom maintenance schedule"
  )
  last_maintenance_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Record of last maintenance"
  )


class Machine(MachineBase, Asset, table=True):
  """Machine table - represents a physical machine instance."""

  __tablename__ = "machines"

  # Foreign key references (for schema validation)
  workcell_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Workcell this machine belongs to",
    foreign_key="workcells.accession_id",
  )
  resource_counterpart_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Resource counterpart for this machine",
    foreign_key="resources.accession_id",
  )
  deck_child_accession_id: uuid.UUID | None = Field(
    default=None, description="Child deck if this machine has one", foreign_key="decks.accession_id"
  )  # Assuming child deck is a Deck definition or Instance? Usually Instance.
  deck_child_definition_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Deck definition for child deck",
    foreign_key="deck_definition_catalog.accession_id",
  )
  current_protocol_run_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Current protocol run if in use",
    foreign_key="protocol_runs.accession_id",
  )
  machine_definition_accession_id: uuid.UUID | None = Field(
    default=None,
    description="Reference to machine definition catalog",
    foreign_key="machine_definitions.accession_id",
  )

  # Relationships
  decks: list["Deck"] = Relationship(
    sa_relationship=relationship(
      "Deck",
      back_populates="parent_machine",
      primaryjoin="Deck.parent_machine_accession_id == Machine.accession_id",
    )
  )
  resources: list["Resource"] = Relationship(
    sa_relationship=relationship(
      "Resource",
      back_populates="machine",
      primaryjoin="Resource.machine_location_accession_id == Machine.accession_id",
    )
  )

  workcell: Optional["Workcell"] = Relationship(back_populates="machines")


class MachineCreate(MachineBase):
  """Schema for creating a Machine."""


from praxis.backend.models.domain.asset import AssetRead, AssetUpdate


class MachineRead(AssetRead, MachineBase):
  """Schema for reading a Machine (API response)."""


class MachineUpdate(AssetUpdate):
  """Schema for updating a Machine (partial update)."""

  status: MachineStatusEnum | None = None
  status_details: str | None = None
  workcell_accession_id: uuid.UUID | None = None
  resource_counterpart_accession_id: uuid.UUID | None = None
  has_deck_child: bool | None = None
  has_resource_child: bool | None = None
  description: str | None = None
  manufacturer: str | None = None
  model: str | None = None
  serial_number: str | None = None
  installation_date: Any | None = None
  connection_info: dict[str, Any] | None = None
  is_simulation_override: bool | None = None
  user_configured_capabilities: dict[str, Any] | None = None
  current_protocol_run_accession_id: uuid.UUID | None = None
  location_label: str | None = None
  maintenance_enabled: bool | None = None
  maintenance_schedule_json: dict[str, Any] | None = None
  last_maintenance_json: dict[str, Any] | None = None

  resource_def_name: str | None = None
  resource_properties_json: dict[str, Any] | None = None
  resource_initial_status: str | None = (
    None  # Enum as string for loose coupling here? Or import ResourceStatusEnum
  )
