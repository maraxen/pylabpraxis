"""Pydantic models for runtime-specific data structures."""

import uuid

from pydantic import BaseModel

from praxis.backend.models.orm.machine import MachineDefinitionOrm
from praxis.backend.models.orm.resource import ResourceDefinitionOrm
from praxis.backend.models.pydantic.protocol import AssetRequirementModel


class RuntimeAssetRequirement(BaseModel):

  """Represents a specific asset requirement for a *protocol run*.

  This wraps the static AssetRequirementModel definition with runtime details
  like its specific 'type' for the run (e.g., 'asset', 'deck') and a reservation ID.
  Access asset details via the `asset_definition` attribute.
  """

  asset_definition: AssetRequirementModel
  asset_type: str  # e.g., "asset", "deck"
  estimated_duration_ms: int | None = None
  priority: int = 1
  reservation_id: uuid.UUID | None = None

  @property
  def asset_name(self) -> str:
    """Get the name of the asset from the asset definition."""
    return self.asset_definition.name

  @classmethod
  def from_asset_definition_orm(
    cls,
    asset_def_orm: ResourceDefinitionOrm | MachineDefinitionOrm,
    asset_type: str,
    estimated_duration_ms: int | None = None,
    priority: int = 1,
  ) -> "RuntimeAssetRequirement":
    """Create a RuntimeAssetRequirement from an ORM object."""
    asset_definition = AssetRequirementModel.model_validate(asset_def_orm)
    return cls(
      asset_definition=asset_definition,
      asset_type=asset_type,
      estimated_duration_ms=estimated_duration_ms,
      priority=priority,
    )

  class Config:

    """Pydantic configuration for RuntimeAssetRequirement."""

    from_attributes = True
    validate_assignment = True
