"""Asset Pydantic Models for API Responses."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class AssetBase(BaseModel):
  """Define the base properties for an asset.

  This model is used for common attributes shared by asset representations,
  primarily for responses rather than direct database interaction.

  """

  name: str = Field(description="The unique name of the asset.")
  type: str = Field(description="The type of the asset (e.g., 'tip_rack', 'plate').")
  metadata: Dict[str, Any] = Field(
    default_factory=dict,
    description="A dictionary for additional metadata about the asset.",
  )


class AssetResponse(AssetBase):
  """Represent an asset for API responses.

  This model extends `AssetBase` by adding availability status and an
  optional description, suitable for client-facing responses.

  """

  is_available: bool = Field(
    description="Indicate if the asset is currently available for use."
  )
  description: Optional[str] = Field(
    None, description="A brief description of the asset."
  )
