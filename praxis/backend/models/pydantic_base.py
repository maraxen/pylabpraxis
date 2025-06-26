"""Base Pydantic models for reuse across the application.

This module provides common base models, such as a timestamped model,
to ensure consistency in API responses.
"""

import datetime

from pydantic import BaseModel, Field


class TimestampedModel(BaseModel):
  """A base model that includes timestamp fields for API responses."""

  created_at: datetime.datetime = Field(
    ..., description="The time the record was created.",
  )
  updated_at: datetime.datetime = Field(
    ..., description="The time the record was last updated.",
  )

  class Config:
    """Pydantic configuration."""

    from_attributes = True
