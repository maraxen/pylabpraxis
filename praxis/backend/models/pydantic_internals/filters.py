"""General-purpose Pydantic models for search and filtering criteria across service layers."""

from datetime import datetime
from typing import Any

from pydantic import UUID7, BaseModel, ConfigDict, Field


class SearchFilters(BaseModel):

  """A general-purpose model for search and filtering criteria across service layers."""

  limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of results to return.")
  offset: int = Field(default=0, ge=0, description="Number of results to skip before returning.")
  sort_by: str | None = Field(default=None, description="Field to sort by.")
  search_filters: dict[str, Any] | None = Field(
    default=None,
    description="Generic key-value filters for searching.",
  )
  date_range_start: datetime | None = Field(
    default=None,
    description="Filter records created/updated after this timestamp.",
  )
  date_range_end: datetime | None = Field(
    default=None,
    description="Filter records created/updated before this timestamp.",
  )
  property_filters: dict[str, Any] | None = Field(
    default=None,
    description="Generic key-value filters for properties stored as JSON or arbitrary fields. "
    "Exact matching for now; can be extended for operators.",
  )
  # Specific IDs for common relationships, can be extended as needed
  protocol_run_accession_id: UUID7 | None = Field(
    default=None,
    description="Filter by associated protocol run ID.",
  )
  machine_accession_id: UUID7 | None = Field(default=None, description="Filter by associated machine ID.")
  resource_accession_id: UUID7 | None = Field(default=None, description="Filter by associated resource ID.")
  parent_accession_id: UUID7 | None = Field(default=None, description="Filter by parent asset ID.")

  model_config = ConfigDict(
    from_attributes=True,
    use_enum_values=True,
  )
