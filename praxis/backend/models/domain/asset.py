"""Unified Asset domain model using SQLModel."""

import uuid
from typing import Any

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

from praxis.backend.models.domain.sqlmodel_base import PraxisBase
from praxis.backend.models.enums import AssetType
from praxis.backend.utils.db import JsonVariant
from praxis.backend.utils.uuid import uuid7


class AssetBase(PraxisBase):
  """Base schema for Asset - shared fields for create/update/response."""

  asset_type: AssetType = Field(
    default=AssetType.ASSET,
    description="Type of asset, e.g., machine, resource, etc.",
  )

  fqn: str = Field(
    default="",
    index=True,
    description="Fully qualified name (e.g., 'pylabrobot.resources.Plate')",
  )

  name: str = Field(
    index=True, unique=True, description="Unique, human-readable name for the asset"
  )

  location: str | None = Field(
    default=None,
    index=True,
    description="Location of the asset in the lab.",
  )


class Asset(AssetBase):
  """Asset domain schema (abstract base for Table-Per-Class inheritance)."""

  properties_json: dict[str, Any] | None = Field(
    default=None,
    sa_type=JsonVariant,
    description="Arbitrary metadata associated with the record.",
  )

  plr_state: dict[str, Any] | None = Field(
    default=None,
    sa_type=JsonVariant,
    description="PLR state of the asset, if applicable.",
  )

  plr_definition: dict[str, Any] | None = Field(
    default=None,
    sa_type=JsonVariant,
    description="PLR definition of the asset, if applicable.",
  )


class AssetCreate(AssetBase):
  """Schema for creating an Asset."""


class AssetRead(SQLModel):
  """Schema for reading an Asset (API response)."""

  model_config = ConfigDict(use_enum_values=True)

  accession_id: uuid.UUID = Field(default_factory=uuid7)

  name: str

  asset_type: AssetType

  fqn: str | None = None

  location: str | None = None

  plr_state: dict[str, Any] | None = None

  plr_definition: dict[str, Any] | None = None

  properties_json: dict[str, Any] | None = None


class AssetUpdate(SQLModel):
  """Schema for updating an Asset (partial update)."""

  model_config = ConfigDict(use_enum_values=True)

  asset_type: AssetType | None = None
  name: str | None = None

  fqn: str | None = None

  location: str | None = None

  plr_state: dict[str, Any] | None = None

  plr_definition: dict[str, Any] | None = None

  properties_json: dict[str, Any] | None = None
