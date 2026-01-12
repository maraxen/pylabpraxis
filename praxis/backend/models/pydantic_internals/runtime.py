"""Pydantic models for runtime-specific data structures."""

from typing import Any

from pydantic import UUID7, ConfigDict

from praxis.backend.models.domain.machine import MachineDefinition
from praxis.backend.models.domain.resource import ResourceDefinition
from praxis.backend.models.domain.protocol import AssetRequirement as AssetRequirementModel
from praxis.backend.models.pydantic_internals.pydantic_base import PraxisBaseModel


class RuntimeAssetRequirement(PraxisBaseModel):
  """Represents a specific asset requirement for a *protocol run*.

  This wraps the static AssetRequirementModel definition with runtime details
  like its specific 'type' for the run (e.g., 'asset', 'deck') and a reservation ID.
  Access asset details via the `asset_definition` attribute.
  """

  asset_definition: AssetRequirementModel
  asset_type: str  # e.g., "asset", "deck"
  estimated_duration_ms: int | None = None
  priority: int = 1
  reservation_id: UUID7 | None = None
  suggested_asset_id: UUID7 | None = None  # Auto-assigned consumable suggestion

  @property
  def asset_name(self) -> str:
    """Get the name of the asset from the asset definition."""
    return self.asset_definition.name

  @classmethod
  def from_asset_definition_model(
    cls,
    asset_def_model: ResourceDefinition | MachineDefinition,
    asset_type: str,
    estimated_duration_ms: int | None = None,
    priority: int = 1,
  ) -> "RuntimeAssetRequirement":
    """Create a RuntimeAssetRequirement from an ORM object."""
    asset_definition = AssetRequirementModel.model_validate(asset_def_model)
    return cls(
      asset_definition=asset_definition,
      asset_type=asset_type,
      estimated_duration_ms=estimated_duration_ms,
      priority=priority,
    )

  model_config = ConfigDict(
    from_attributes=True,
    validate_assignment=True,
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