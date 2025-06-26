"""Asset Pydantic Models for API Responses."""

from typing import Any

from pydantic import UUID7, BaseModel, Field

from .enums import AssetType
from .pydantic_base import TimestampedModel


class AssetBase(BaseModel):
  """Define the base properties for an asset."""

  accession_id: UUID7 = Field(..., description="The unique accession ID of the asset.")
  name: str = Field(description="The unique name of the asset.")
  asset_type: AssetType = Field(description="The type of the asset.")
  fqn: str | None = Field(
    None, description="Fully qualified name of the asset's class, if applicable.",
  )
  location: str | None = Field(None, description="The location of the asset.")


class AssetResponse(AssetBase, TimestampedModel):
  """Represent an asset for API responses."""

  plr_state: dict[str, Any] | None = Field(
    default_factory=dict,
    description="A dictionary for additional state information about the asset.",
  )
  plr_definition: dict[str, Any] | None = Field(
    default_factory=dict,
    description="A dictionary for the PyLabRobot definition of the asset.",
  )
  properties_json: dict[str, Any] | None = Field(
    default_factory=dict,
    description="A dictionary for additional metadata about the asset.",
  )


class AssetUpdate(BaseModel):
  """Define the properties for updating an asset."""

  name: str | None = Field(None, description="The unique name of the asset.")
  fqn: str | None = Field(
    None, description="Fully qualified name of the asset's class, if applicable.",
  )
  location: str | None = Field(None, description="The location of the asset.")
  plr_state: dict[str, Any] | None = Field(
    None,
    description="A dictionary for additional state information about the asset.",
  )
  plr_definition: dict[str, Any] | None = Field(
    None,
    description="A dictionary for the PyLabRobot definition of the asset.",
  )
  properties_json: dict[str, Any] | None = Field(
    None, description="A dictionary for additional metadata about the asset.",
  )

  class Config:
    """Pydantic configuration for AssetUpdate."""

    from_attributes = True
