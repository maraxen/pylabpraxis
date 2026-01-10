"""Unified Asset domain model using SQLModel."""

from typing import TYPE_CHECKING, Any, ClassVar

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship

from praxis.backend.models.domain.sqlmodel_base import PraxisBase, json_field
from praxis.backend.models.enums import AssetType

if TYPE_CHECKING:
  from praxis.backend.models.orm.schedule import AssetReservationOrm


class AssetBase(PraxisBase):
  """Base schema for Asset - shared fields for create/update/response."""

  asset_type: AssetType = Field(
    default=AssetType.ASSET,
    sa_column=Column(SAEnum(AssetType), index=True, nullable=False),
    description="Type of asset, e.g., machine, resource, etc.",
  )
  fqn: str = Field(
    default="",
    index=True,
    description="Fully qualified name of the asset's class, if applicable.",
  )
  location: str | None = Field(
    default=None,
    index=True,
    description="Location of the asset in the lab.",
  )


class Asset(AssetBase, table=True):
  """Asset ORM model with polymorphic inheritance."""

  __tablename__ = "assets"

  plr_state: dict[str, Any] | None = json_field(
    default=None,
    description="PLR state of the asset, if applicable.",
  )
  plr_definition: dict[str, Any] | None = json_field(
    default=None,
    description="PLR definition of the asset, if applicable.",
  )

  # Relationships
  # Note: Using string forward reference for AssetReservationOrm to avoid circular imports
  # and sticking to the existing ORM class name as per requirements/existing code
  # FIXME: This relationship causes conflict with AssetOrm and circular import issues
  # during migration. Re-enable when AssetOrm is removed or deprecated.
  # asset_reservations: list["AssetReservationOrm"] = Relationship(
  #     back_populates="asset",
  #     sa_relationship_kwargs={
  #         "cascade": "all, delete-orphan",
  #         "foreign_keys": "[AssetReservationOrm.asset_accession_id]",
  #     },
  # )

  __mapper_args__: ClassVar[dict[str, Any]] = {
    "polymorphic_on": "asset_type",
    "polymorphic_identity": AssetType.ASSET,
  }


class AssetCreate(AssetBase):
  """Schema for creating an Asset."""

  pass


class AssetRead(AssetBase):
  """Schema for reading an Asset (API response)."""

  plr_state: dict[str, Any] | None = None
  plr_definition: dict[str, Any] | None = None


class AssetUpdate(PraxisBase):
  """Schema for updating an Asset (partial update)."""

  name: str | None = None
  fqn: str | None = None
  location: str | None = None
  plr_state: dict[str, Any] | None = None
  plr_definition: dict[str, Any] | None = None
  properties_json: dict[str, Any] | None = None
