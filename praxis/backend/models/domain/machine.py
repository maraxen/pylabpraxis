# pylint: disable=too-few-public-methods,missing-class-docstring
"""Unified SQLModel definitions for Machine and MachineDefinition."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel

from praxis.backend.models.domain.asset import AssetBase
from praxis.backend.models.domain.sqlmodel_base import PraxisBase, json_field
from praxis.backend.models.enums import (
    MachineCategoryEnum,
    MachineStatusEnum,
)

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
        sa_column=Column(SAEnum(MachineCategoryEnum, name="machine_category_enum"), nullable=False, index=True),
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

    __tablename__ = "machine_definition_catalog"

    plr_definition_details_json: dict[str, Any] | None = json_field(
        default=None, description="Additional PyLabRobot definition details"
    )
    rotation_json: dict[str, Any] | None = json_field(
        default=None, description="PLR rotation object"
    )
    setup_method_json: dict[str, Any] | None = json_field(
        default=None, description="Setup method configuration"
    )
    capabilities: dict[str, Any] | None = json_field(
        default=None, description="Hardware capabilities (channels, modules)"
    )
    compatible_backends: dict[str, Any] | None = json_field(
        default=None, description="Compatible backend class FQNs"
    )
    capabilities_config: dict[str, Any] | None = json_field(
        default=None, description="User-configurable capabilities schema"
    )
    connection_config: dict[str, Any] | None = json_field(
        default=None, description="Connection parameters schema"
    )

    # Foreign keys
    resource_definition_accession_id: uuid.UUID | None = Field(
        default=None, foreign_key="resource_definition_catalog.accession_id"
    )
    deck_definition_accession_id: uuid.UUID | None = Field(
        default=None, foreign_key="deck_definition_catalog.accession_id"
    )
    asset_requirement_accession_id: uuid.UUID | None = Field(
        default=None, foreign_key="protocol_asset_requirements.accession_id"
    )

    # Relationships (commented out to avoid circular imports during initial migration)
    # resource_definition: "ResourceDefinition | None" = Relationship(back_populates="machine_definition")
    # deck_definition: "DeckDefinition | None" = Relationship(back_populates="machine_definition")


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
        sa_column=Column(SAEnum(MachineCategoryEnum, name="machine_category_enum"), nullable=False, index=True),
    )
    description: str | None = Field(default=None)
    manufacturer: str | None = Field(default=None)
    model: str | None = Field(default=None)
    serial_number: str | None = Field(default=None, unique=True)
    location_label: str | None = Field(default=None, description="Physical location label")
    installation_date: datetime | None = Field(default=None)
    status: MachineStatusEnum = Field(
        default=MachineStatusEnum.OFFLINE,
        sa_column=Column(SAEnum(MachineStatusEnum, name="machine_status_enum"), nullable=False, index=True),
    )
    status_details: str | None = Field(default=None)
    is_simulation_override: bool | None = Field(default=None)
    last_seen_online: datetime | None = Field(default=None, index=True)
    maintenance_enabled: bool = Field(default=True)


class Machine(MachineBase):
    """Machine schema - represents a physical machine instance.

    Note: This is a schema class for API validation. The actual ORM table
    is defined in praxis.backend.models.orm.machine.MachineOrm using
    SQLAlchemy's polymorphic joined table inheritance.

    SQLModel doesn't support multi-table inheritance with dict fields properly,
    so we use schema-only classes here and keep the ORM separate.
    """

    # JSON fields (for schema validation)
    connection_info: dict[str, Any] | None = Field(
        default=None, description="Connection details (backend, address, etc.)"
    )
    user_configured_capabilities: dict[str, Any] | None = Field(
        default=None, description="User-specified capability overrides"
    )
    maintenance_schedule_json: dict[str, Any] | None = Field(
        default=None, description="Custom maintenance schedule"
    )
    last_maintenance_json: dict[str, Any] | None = Field(
        default=None, description="Record of last maintenance"
    )

    # Foreign key references (for schema validation)
    workcell_accession_id: uuid.UUID | None = Field(
        default=None, description="Workcell this machine belongs to"
    )
    resource_counterpart_accession_id: uuid.UUID | None = Field(
        default=None, description="Resource counterpart for this machine"
    )
    deck_child_accession_id: uuid.UUID | None = Field(
        default=None, description="Child deck if this machine has one"
    )
    deck_child_definition_accession_id: uuid.UUID | None = Field(
        default=None, description="Deck definition for child deck"
    )
    current_protocol_run_accession_id: uuid.UUID | None = Field(
        default=None, description="Current protocol run if in use"
    )
    machine_definition_accession_id: uuid.UUID | None = Field(
        default=None, description="Reference to machine definition catalog"
    )


class MachineCreate(MachineBase):
    """Schema for creating a Machine."""



class MachineRead(MachineBase):
    """Schema for reading a Machine (API response)."""

    accession_id: uuid.UUID
    connection_info: dict[str, Any] | None = None
    user_configured_capabilities: dict[str, Any] | None = None


class MachineUpdate(SQLModel):
    """Schema for updating a Machine (partial update)."""

    name: str | None = None
    fqn: str | None = None
    location: str | None = None
    machine_category: MachineCategoryEnum | None = None
    description: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    serial_number: str | None = None
    location_label: str | None = None
    installation_date: datetime | None = None
    status: MachineStatusEnum | None = None
    status_details: str | None = None
    is_simulation_override: bool | None = None
    connection_info: dict[str, Any] | None = None
    user_configured_capabilities: dict[str, Any] | None = None
    maintenance_enabled: bool | None = None
