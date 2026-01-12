# pylint: disable=too-few-public-methods,missing-class-docstring
"""Unified SQLModel definitions for Resource and ResourceDefinition."""

import uuid
from typing import Any

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, SQLModel

from praxis.backend.models.domain.asset import AssetBase
from praxis.backend.models.domain.sqlmodel_base import PraxisBase, json_field
from praxis.backend.models.enums.resource import ResourceStatusEnum

# =============================================================================
# Resource Definition (Catalog)
# =============================================================================


class ResourceDefinitionBase(PraxisBase):
  """Base schema for ResourceDefinition - shared fields for create/update/response."""

  fqn: str = Field(index=True, unique=True, description="Fully qualified name")
  description: str | None = Field(default=None, description="Description of the resource type")
  plr_category: str | None = Field(default=None, description="PyLabRobot category")
  resource_type: str | None = Field(default=None, description="Human-readable type of the resource")
  is_consumable: bool = Field(default=False)
  nominal_volume_ul: float | None = Field(default=None, description="Nominal volume in microliters")
  material: str | None = Field(default=None, description="Material (polypropylene, glass, etc.)")
  manufacturer: str | None = Field(default=None)
  model: str | None = Field(default=None)
  ordering: str | None = Field(default=None, description="Ordering information")
  size_x_mm: float | None = Field(default=None, description="Size in X dimension (mm)")
  size_y_mm: float | None = Field(default=None, description="Size in Y dimension (mm)")
  size_z_mm: float | None = Field(default=None, description="Size in Z dimension (mm)")
  # Dynamic filtering fields
  num_items: int | None = Field(
    default=None, index=True, description="Number of items (wells, tips)"
  )
  plate_type: str | None = Field(default=None, index=True, description="Plate skirt type")
  well_volume_ul: float | None = Field(
    default=None, index=True, description="Well volume for plates"
  )
  tip_volume_ul: float | None = Field(
    default=None, index=True, description="Tip volume for tip racks"
  )
  vendor: str | None = Field(default=None, index=True, description="Vendor from FQN")


class ResourceDefinition(ResourceDefinitionBase, table=True):
  """ResourceDefinition ORM model - catalog of resource types."""

  __tablename__ = "resource_definition_catalog"

  plr_definition_details_json: dict[str, Any] | None = json_field(
    default=None, description="Additional PyLabRobot definition details"
  )
  rotation_json: dict[str, Any] | None = json_field(default=None, description="PLR rotation object")

  # Foreign keys
  deck_definition_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="deck_definition_catalog.accession_id", index=True
  )
  asset_requirement_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="protocol_asset_requirements.accession_id", index=True
  )

  # Relationships (commented out to avoid circular imports during initial migration)
  # machine_definition: "MachineDefinition | None" = Relationship(back_populates="resource_definition")
  # deck_definition: "DeckDefinition | None" = Relationship(back_populates="resource_definition")


class ResourceDefinitionCreate(ResourceDefinitionBase):
  """Schema for creating a ResourceDefinition."""



class ResourceDefinitionRead(ResourceDefinitionBase):
  """Schema for reading a ResourceDefinition (API response)."""

  accession_id: uuid.UUID
  plr_definition_details_json: dict[str, Any] | None = None
  rotation_json: dict[str, Any] | None = None


class ResourceDefinitionUpdate(SQLModel):
  """Schema for updating a ResourceDefinition (partial update)."""

  name: str | None = None
  fqn: str | None = None
  description: str | None = None
  plr_category: str | None = None
  resource_type: str | None = None
  is_consumable: bool | None = None
  nominal_volume_ul: float | None = None
  material: str | None = None
  manufacturer: str | None = None
  model: str | None = None
  ordering: str | None = None
  size_x_mm: float | None = None
  size_y_mm: float | None = None
  size_z_mm: float | None = None
  num_items: int | None = None
  plate_type: str | None = None
  well_volume_ul: float | None = None
  tip_volume_ul: float | None = None
  vendor: str | None = None


# =============================================================================
# Resource (Physical Instance)
# =============================================================================


class ResourceBase(AssetBase):
  """Base schema for Resource - shared fields for create/update/response."""

  status: ResourceStatusEnum = Field(
    default=ResourceStatusEnum.UNKNOWN,
    sa_column=Column(
      SAEnum(ResourceStatusEnum, name="resource_status_enum"), nullable=False, index=True
    ),
  )
  status_details: str | None = Field(default=None, description="Additional status details")
  location_label: str | None = Field(default=None, description="Physical location label")
  current_deck_position_name: str | None = Field(default=None, description="Current deck position")


class Resource(ResourceBase):
  """Resource schema - represents a physical resource instance.

  Note: This is a schema class for API validation. The actual ORM table
  is defined in praxis.backend.models.orm.resource.ResourceOrm using
  SQLAlchemy's polymorphic joined table inheritance.

  SQLModel doesn't support multi-table inheritance with dict fields properly,
  so we use schema-only classes here and keep the ORM separate.
  """

  # Foreign key references (for schema validation, not actual FK constraints)
  resource_definition_accession_id: uuid.UUID | None = Field(
    default=None, description="Reference to resource definition catalog"
  )
  parent_accession_id: uuid.UUID | None = Field(
    default=None, description="Parent resource for hierarchies"
  )
  current_protocol_run_accession_id: uuid.UUID | None = Field(
    default=None, description="Current protocol run if in use"
  )
  machine_location_accession_id: uuid.UUID | None = Field(
    default=None, description="Machine where resource is located"
  )
  deck_location_accession_id: uuid.UUID | None = Field(
    default=None, description="Deck where resource is located"
  )
  workcell_accession_id: uuid.UUID | None = Field(
    default=None, description="Workcell this resource belongs to"
  )


class ResourceCreate(ResourceBase):
  """Schema for creating a Resource."""

  resource_definition_accession_id: uuid.UUID | None = None
  parent_accession_id: uuid.UUID | None = None
  machine_location_accession_id: uuid.UUID | None = None
  deck_location_accession_id: uuid.UUID | None = None
  workcell_accession_id: uuid.UUID | None = None
  plr_state: dict[str, Any] | None = None


class ResourceRead(ResourceBase):
  """Schema for reading a Resource (API response)."""

  accession_id: uuid.UUID


class ResourceUpdate(SQLModel):
  """Schema for updating a Resource (partial update)."""

  name: str | None = None
  fqn: str | None = None
  location: str | None = None
  status: ResourceStatusEnum | None = None
  status_details: str | None = None
  location_label: str | None = None
  current_deck_position_name: str | None = None
  resource_definition_accession_id: uuid.UUID | None = None
