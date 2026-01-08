"""Asset Pydantic Models for API Responses."""

from typing import Any

from pydantic import UUID7, BaseModel, ConfigDict, Field

from praxis.backend.models.enums import AssetType

from .pydantic_base import PraxisBaseModel


class AssetBase(PraxisBaseModel):
  """Define the base properties for an asset."""

  asset_type: AssetType | None = Field(description="The type of the asset.")
  fqn: str | None = Field(
    None,
    description="Fully qualified name of the asset's class, if applicable.",
  )
  location: str | None = Field(None, description="The location of the asset.")


class AssetResponse(AssetBase, PraxisBaseModel):
  """Represent an asset for API responses."""

  plr_state: dict[str, Any] | None = Field(
    default_factory=dict,
    description="A dictionary for additional state information about the asset.",
  )
  plr_definition: dict[str, Any] | None = Field(
    default_factory=dict,
    description="A dictionary for the PyLabRobot definition of the asset.",
  )


class AssetUpdate(BaseModel):
  """Define the properties for updating an asset."""

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

  name: str | None = Field(default=None, description="The unique name of the asset.")
  fqn: str | None = Field(
    default=None,
    description="Fully qualified name of the asset's class, if applicable.",
  )
  location: str | None = Field(default=None, description="The location of the asset.")
  plr_state: dict[str, Any] | None = Field(
    default=None,
    description="A dictionary for additional state information about the asset.",
  )
  plr_definition: dict[str, Any] | None = Field(
    default=None,
    description="A dictionary for the PyLabRobot definition of the asset.",
  )
  properties_json: dict[str, Any] | None = Field(
    default=None,
    description="A dictionary for additional metadata about the asset.",
  )


class AcquireAssetLock(PraxisBaseModel):
  """Model for acquiring an asset lock."""

  asset_type: str
  asset_name: str
  protocol_run_id: UUID7
  reservation_id: UUID7
  timeout_seconds: int | None = None
  required_capabilities: dict[str, Any] | None = None


class AcquireAsset(PraxisBaseModel):
  """Model for acquiring an asset."""

  protocol_run_accession_id: UUID7
  requested_asset_name_in_protocol: str
  fqn: str
  instance_accession_id: UUID7 | None = None
  location_constraints: dict[str, Any] | None = None
  property_constraints: dict[str, Any] | None = None


class ReleaseAsset(PraxisBaseModel):
  """Model for releasing an asset."""

  asset_accession_id: UUID7
  final_status: str
  final_properties_json_update: dict[str, Any] | None = None
  clear_from_protocol_accession_id: UUID7 | None = None
  clear_from_position_name: str | None = None
  status_details: str | None = "Released from run"
