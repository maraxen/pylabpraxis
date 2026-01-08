"""Pydantic models for Function Data Output management.

This module provides Pydantic models for data outputs from protocol function calls,
enabling proper validation, serialization, and API interaction for experimental data.
"""

from collections.abc import Sequence
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import UUID7, BaseModel, ConfigDict, Field, model_validator

from praxis.backend.models.enums import (
  DataOutputTypeEnum,
  SpatialContextEnum,
)
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.models.pydantic_internals.pydantic_base import PraxisBaseModel


class FunctionDataOutputBase(PraxisBaseModel):
  """Base fields for function data outputs."""

  data_type: DataOutputTypeEnum = Field(..., description="Type of data output")

  data_key: str = Field(
    ...,
    max_length=255,
    description="Unique key within the function call",
  )

  spatial_context: SpatialContextEnum = Field(
    ...,
    description="Spatial context of the data",
  )

  spatial_coordinates_json: dict[str, Any] | None = Field(
    default=None,
    description="Spatial coordinates within resource",
  )

  data_units: str | None = Field(
    default=None,
    max_length=50,
    description="Units of measurement",
  )

  data_quality_score: float | None = Field(
    default=None,
    ge=0.0,
    le=1.0,
    description="Quality score (0.0-1.0)",
  )

  measurement_conditions_json: dict[str, Any] | None = Field(
    default=None,
    description="Measurement conditions",
  )

  sequence_in_function: int | None = Field(
    default=None,
    description="Sequence number within the function call",
  )

  model_config = ConfigDict(
    from_attributes=True,
    use_enum_values=True,
  )


class FunctionDataOutputCreate(FunctionDataOutputBase):
  name: str = "default_name"
  """Model for creating function data outputs."""

  function_call_log_accession_id: UUID7 = Field(
    ...,
    description="ID of the function call that generated this data",
  )

  protocol_run_accession_id: UUID7 = Field(..., description="ID of the protocol run")

  resource_accession_id: UUID7 | None = Field(
    default=None,
    description="ID of associated resource",
  )

  machine_accession_id: UUID7 | None = Field(
    default=None,
    description="ID of associated machine/device",
  )

  deck_accession_id: UUID7 | None = Field(
    default=None,
    description="ID of associated deck position",
  )

  # Data content (only one should be provided)
  data_value_numeric: float | None = Field(default=None, description="Numeric data value")

  data_value_json: dict[str, Any] | None = Field(default=None, description="Structured data")

  data_value_text: str | None = Field(default=None, description="Text data")

  file_path: str | None = Field(
    default=None,
    max_length=500,
    description="Path to external file",
  )

  file_size_bytes: int | None = Field(default=None, description="File size in bytes")

  measurement_timestamp: datetime | None = Field(
    default=None,
    description="When the measurement was captured",
  )

  derived_from_data_output_accession_id: UUID7 | None = Field(
    default=None,
    description="ID of source data if this is derived",
  )

  @model_validator(mode="after")
  def validate_data_content(self):
    """Ensure at least one data field is provided."""
    data_fields = [
      self.data_value_numeric,
      self.data_value_json,
      self.data_value_text,
      self.file_path,
    ]

    # Count non-None values
    non_none_count = sum(1 for field in data_fields if field is not None)

    if non_none_count == 0:
      msg = "At least one data field must be provided"
      raise ValueError(msg)

    return self


class FunctionDataOutputUpdate(BaseModel):
  """Model for updating function data outputs."""

  data_quality_score: float | None = Field(
    default=None,
    ge=0.0,
    le=1.0,
    description="Updated quality score",
  )

  measurement_conditions_json: dict[str, Any] | None = Field(
    default=None,
    description="Updated measurement conditions",
  )

  processing_metadata_json: dict[str, Any] | None = Field(
    default=None,
    description="Updated processing metadata",
  )


class FunctionDataOutputResponse(FunctionDataOutputBase):
  """Model for function data output responses."""

  function_call_log_accession_id: UUID7 = Field(
    ...,
    description="ID of the function call",
  )

  protocol_run_accession_id: UUID7 = Field(..., description="ID of the protocol run")

  resource_accession_id: UUID7 | None = Field(
    None,
    description="ID of associated resource",
  )

  machine_accession_id: UUID7 | None = Field(
    None,
    description="ID of associated machine",
  )

  deck_accession_id: UUID7 | None = Field(
    None,
    description="ID of associated deck position",
  )

  data_value_numeric: float | None = Field(None, description="Numeric data value")

  data_value_json: dict[str, Any] | None = Field(None, description="Structured data")

  data_value_text: str | None = Field(None, description="Text data")

  file_path: str | None = Field(None, description="Path to external file")

  file_size_bytes: int | None = Field(None, description="File size in bytes")

  measurement_timestamp: datetime = Field(
    ...,
    description="When the measurement was captured",
  )

  derived_from_data_output_accession_id: UUID7 | None = Field(
    None,
    description="ID of source data if derived",
  )


class WellDataOutputBase(PraxisBaseModel):
  """Base fields for well-specific data outputs."""

  well_name: str = Field(..., max_length=10, description="Well name (e.g., 'A1')")

  well_row: int = Field(..., ge=0, description="0-based row index")

  well_column: int = Field(..., ge=0, description="0-based column index")

  well_index: int | None = Field(None, ge=0, description="Linear well index")

  data_value: float | None = Field(
    None,
    description="Primary numeric value for this well",
  )

  model_config = ConfigDict(
    from_attributes=True,
    use_enum_values=True,
  )


class WellDataOutputCreate(WellDataOutputBase):
  """Model for creating well data outputs."""

  function_data_output_accession_id: UUID7 = Field(
    ...,
    description="ID of the parent function data output",
  )

  plate_resource_accession_id: UUID7 = Field(
    ...,
    description="ID of the plate resource",
  )

  well_row: int | None = Field(default=None, ge=0, description="0-based row index")
  well_column: int | None = Field(default=None, ge=0, description="0-based column index")


class WellDataOutputResponse(WellDataOutputBase):
  """Model for well data output responses."""

  function_data_output_accession_id: UUID7 = Field(
    ...,
    description="ID of the parent function data output",
  )

  plate_resource_accession_id: UUID7 = Field(
    ...,
    description="ID of the plate resource",
  )


class WellDataOutputUpdate(BaseModel):
  """Model for updating well data outputs."""

  data_value: float | None = Field(None, description="Updated data value")

  metadata_json: dict[str, Any] | None = Field(
    None,
    description="Updated metadata",
  )  # TODO: figure out how to integrate this


class PlateDataVisualization(PraxisBaseModel):
  """Model for plate-based data visualization."""

  plate_resource_accession_id: UUID7 = Field(
    ...,
    description="ID of the plate resource",
  )

  plate_name: str = Field(..., description="Name of the plate")

  data_type: DataOutputTypeEnum = Field(
    ...,
    description="Type of data being visualized",
  )

  measurement_timestamp: datetime = Field(..., description="When the data was captured")

  well_data: list[WellDataOutputResponse] = Field(..., description="Data for each well")

  plate_layout: dict[str, Any] = Field(
    ...,
    description="Plate layout information (rows, columns, etc.)",
  )

  data_range: dict[str, float] = Field(
    ...,
    description="Min/max values for visualization scaling",
  )

  units: str | None = Field(None, description="Data units")

  model_config = ConfigDict(
    from_attributes=True,
    use_enum_values=True,
    arbitrary_types_allowed=True,
  )


class ProtocolRunDataSummary(PraxisBaseModel):
  """Model for summarizing all data from a protocol run."""

  protocol_run_accession_id: UUID7 = Field(..., description="ID of the protocol run")

  total_data_outputs: int = Field(..., description="Total number of data outputs")

  data_types: list[str] = Field(..., description="List of data types captured")

  machines_used: Sequence[UUID7] = Field(
    ...,
    description="List of machine IDs that generated data",
  )

  resource_with_data: Sequence[UUID7] = Field(
    ...,
    description="List of resource IDs with associated data",
  )

  data_timeline: list[dict[str, Any]] = Field(
    ...,
    description="Timeline of data capture events",
  )

  file_attachments: list[dict[str, Any]] = Field(
    ...,
    description="List of file attachments with metadata",
  )

  model_config = ConfigDict(
    from_attributes=True,
    use_enum_values=True,
    arbitrary_types_allowed=True,
  )


class DataExportRequest(PraxisBaseModel):
  """Model for requesting data export."""

  filters: SearchFilters = Field(..., description="Filters for data selection")

  export_format: str = Field(..., description="Export format (csv, json, xlsx, etc.)")

  include_metadata: bool = Field(True, description="Whether to include metadata")

  include_spatial_info: bool = Field(
    True,
    description="Whether to include spatial information",
  )

  flatten_structure: bool = Field(
    False,
    description="Whether to flatten hierarchical data",
  )


class FunctionDataOutputFilters(PraxisBaseModel):
  """Model for filtering function data outputs."""

  search_filters: SearchFilters = Field(..., description="Search filters for data selection")
  data_types: list[DataOutputTypeEnum] | None = Field(None, description="Filter by data types.")
  spatial_contexts: list[SpatialContextEnum] | None = Field(
    None,
    description="Filter by spatial context.",
  )
  has_numeric_data: bool | None = Field(None, description="Filter for entries with numeric data.")
  has_file_data: bool | None = Field(None, description="Filter for entries with file attachments.")
  min_quality_score: float | None = Field(
    None,
    ge=0.0,
    le=1.0,
    description="Minimum quality score.",
  )


class WellDataOutputFilters(PraxisBaseModel):
  """Model for filtering well data outputs."""

  plate_resource_id: UUID | None = Field(None)
  function_call_id: UUID | None = Field(None)
  protocol_run_id: UUID | None = Field(None)
  data_type: DataOutputTypeEnum | None = Field(None)
  well_row: int | None = Field(None, ge=0)
  well_column: int | None = Field(None, ge=0)
  skip: int = Field(0, ge=0)
  limit: int = Field(100, ge=1, le=1000)
