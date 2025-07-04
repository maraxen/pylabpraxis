"""Base Pydantic models for reuse across the application.

This module provides common base models, such as a timestamped model,
to ensure consistency in API responses.
"""

import datetime
from typing import Any

from pydantic import UUID7, BaseModel, Field

from praxis.backend.utils.uuid import uuid7


class PraxisBaseModel(BaseModel):
  """A base model that includes timestamp fields for API responses."""

  accession_id: UUID7 = Field(
    description="The unique accession ID of the record.",
    default_factory=uuid7,
    frozen=True,
  )
  created_at: datetime.datetime = Field(
    description="The time the record was created.",
    default_factory=lambda: datetime.datetime.now(tz=datetime.timezone.utc),
    frozen=True,
  )
  updated_at: datetime.datetime | None = Field(
    default=None,
    alias="last_updated",
    description="The time the record was last updated.",
  )

  def model_post_init(self, __context: Any) -> None:  # noqa: ANN401
    """Set the updated_at field to the current time after model initialization."""
    self.updated_at = datetime.datetime.now(tz=datetime.timezone.utc)

  class Config:
    """Pydantic configuration."""

    from_attributes = True
    validate_assignment = True
