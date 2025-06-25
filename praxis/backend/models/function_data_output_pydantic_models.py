"""Pydantic models for Function Data Output management.

This module provides Pydantic models for data outputs from protocol function calls,
enabling proper validation, serialization, and API interaction for experimental data.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from pydantic import UUID7, BaseModel, Field, field_validator

from praxis.backend.models.function_data_output_orm import (
  DataOutputSpatialContextEnum,
  DataOutputTypeEnum,
)


class FunctionDataOutputBase(BaseModel):
  """Base fields for function data outputs."""

  data_type: DataOutputTypeEnum = Field(..., description="Type of data output")

  data_key: str = Field(
    ..., max_length=255, description="Unique key within the function call"
  )

  spatial_context: DataOutputSpatialContextEnum = Field(
    ..., description="Spatial context of the data"
  )

  spatial_coordinates_json: Optional[Dict[str, Any]] = Field(
    None, description="Spatial coordinates within resource"
  )

  data_units: Optional[str] = Field(
    None, max_length=50, description="Units of measurement"
  )

  data_quality_score: Optional[float] = Field(
    None, ge=0.0, le=1.0, description="Quality score (0.0-1.0)"
  )

  measurement_conditions_json: Optional[Dict[str, Any]] = Field(
    None, description="Measurement conditions"
  )

  sequence_in_function: Optional[int] = Field(
    None, description="Sequence number within the function call"
  )

  processing_metadata_json: Optional[Dict[str, Any]] = Field(
    None, description="Data processing metadata"
  )

  class Config:
    """Pydantic configuration."""

    from_attributes = True
    use_enum_values = True


class FunctionDataOutputCreate(FunctionDataOutputBase):
  """Model for creating function data outputs."""

  function_call_log_accession_id: UUID7 = Field(
    ..., description="ID of the function call that generated this data"
  )

  protocol_run_accession_id: UUID7 = Field(..., description="ID of the protocol run")

  resource_instance_accession_id: Optional[UUID7] = Field(
    None, description="ID of associated resource"
  )

  machine_accession_id: Optional[UUID7] = Field(
    None, description="ID of associated machine/device"
  )

  deck_instance_accession_id: Optional[UUID7] = Field(
    None, description="ID of associated deck position"
  )

  # Data content (only one should be provided)
  data_value_numeric: Optional[float] = Field(None, description="Numeric data value")

  data_value_json: Optional[Dict[str, Any]] = Field(None, description="Structured data")

  data_value_text: Optional[str] = Field(None, description="Text data")

  file_path: Optional[str] = Field(
    None, max_length=500, description="Path to external file"
  )

  file_size_bytes: Optional[int] = Field(None, description="File size in bytes")

  measurement_timestamp: Optional[datetime] = Field(
    None, description="When the measurement was captured"
  )

  derived_from_data_output_accession_id: Optional[UUID7] = Field(
    None, description="ID of source data if this is derived"
  )

  @field_validator(
    "data_value_numeric", "data_value_json", "data_value_text", "file_path"
  )
  def validate_data_content(cls, v, values):
    """Ensure at least one data field is provided."""
    data_fields = [
      values.get("data_value_numeric"),
      values.get("data_value_json"),
      values.get("data_value_text"),
      values.get("file_path"),
    ]

    # Count non-None values
    non_none_count = sum(1 for field in data_fields if field is not None)

    if non_none_count == 0:
      raise ValueError("At least one data field must be provided")

    return v


class FunctionDataOutputUpdate(BaseModel):
  """Model for updating function data outputs."""

  data_quality_score: Optional[float] = Field(
    None, ge=0.0, le=1.0, description="Updated quality score"
  )

  measurement_conditions_json: Optional[Dict[str, Any]] = Field(
    None, description="Updated measurement conditions"
  )

  processing_metadata_json: Optional[Dict[str, Any]] = Field(
    None, description="Updated processing metadata"
  )


class FunctionDataOutputResponse(FunctionDataOutputBase):
  """Model for function data output responses."""

  accession_id: UUID7 = Field(..., description="Unique identifier")

  function_call_log_accession_id: UUID7 = Field(
    ..., description="ID of the function call"
  )

  protocol_run_accession_id: UUID7 = Field(..., description="ID of the protocol run")

  resource_instance_accession_id: Optional[UUID7] = Field(
    None, description="ID of associated resource"
  )

  machine_accession_id: Optional[UUID7] = Field(
    None, description="ID of associated machine"
  )

  deck_instance_accession_id: Optional[UUID7] = Field(
    None, description="ID of associated deck position"
  )

  data_value_numeric: Optional[float] = Field(None, description="Numeric data value")

  data_value_json: Optional[Dict[str, Any]] = Field(None, description="Structured data")

  data_value_text: Optional[str] = Field(None, description="Text data")

  file_path: Optional[str] = Field(None, description="Path to external file")

  file_size_bytes: Optional[int] = Field(None, description="File size in bytes")

  measurement_timestamp: datetime = Field(
    ..., description="When the measurement was captured"
  )

  derived_from_data_output_accession_id: Optional[UUID7] = Field(
    None, description="ID of source data if derived"
  )

  created_at: datetime = Field(..., description="Creation timestamp")
  updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class WellDataOutputBase(BaseModel):
  """Base fields for well-specific data outputs."""

  well_name: str = Field(..., max_length=10, description="Well name (e.g., 'A1')")

  well_row: int = Field(..., ge=0, description="0-based row index")

  well_column: int = Field(..., ge=0, description="0-based column index")

  well_index: Optional[int] = Field(None, ge=0, description="Linear well index")

  data_value: Optional[float] = Field(
    None, description="Primary numeric value for this well"
  )

  class Config:
    """Pydantic configuration."""

    from_attributes = True
    use_enum_values = True


class WellDataOutputCreate(WellDataOutputBase):
  """Model for creating well data outputs."""

  function_data_output_accession_id: UUID7 = Field(
    ..., description="ID of the parent function data output"
  )

  plate_resource_instance_accession_id: UUID7 = Field(
    ..., description="ID of the plate resource"
  )


class WellDataOutputResponse(WellDataOutputBase):
  """Model for well data output responses."""

  accession_id: UUID7 = Field(..., description="Unique identifier")

  function_data_output_accession_id: UUID7 = Field(
    ..., description="ID of the parent function data output"
  )

  plate_resource_instance_accession_id: UUID7 = Field(
    ..., description="ID of the plate resource"
  )

  created_at: datetime = Field(..., description="Creation timestamp")


class WellDataOutputUpdate(BaseModel):
  """Model for updating well data outputs."""

  data_value: Optional[float] = Field(None, description="Updated data value")

  metadata_json: Optional[Dict[str, Any]] = Field(
    None, description="Updated metadata"
  )  # TODO: figure out how to integrate this


class PlateDataVisualization(BaseModel):
  """Model for plate-based data visualization."""

  plate_resource_instance_accession_id: UUID7 = Field(
    ..., description="ID of the plate resource"
  )

  plate_name: str = Field(..., description="Name of the plate")

  data_type: DataOutputTypeEnum = Field(
    ..., description="Type of data being visualized"
  )

  measurement_timestamp: datetime = Field(..., description="When the data was captured")

  well_data: List[WellDataOutputResponse] = Field(..., description="Data for each well")

  plate_layout: Dict[str, Any] = Field(
    ..., description="Plate layout information (rows, columns, etc.)"
  )

  data_range: Dict[str, float] = Field(
    ..., description="Min/max values for visualization scaling"
  )

  units: Optional[str] = Field(None, description="Data units")

  class Config:
    """Pydantic configuration for PlateDataVisualization."""

    from_attributes = True
    use_enum_values = True
    arbitrary_types_allowed = True


class ProtocolRunDataSummary(BaseModel):
  """Model for summarizing all data from a protocol run."""

  protocol_run_accession_id: UUID7 = Field(..., description="ID of the protocol run")

  total_data_outputs: int = Field(..., description="Total number of data outputs")

  data_types: List[str] = Field(..., description="List of data types captured")

  machines_used: Sequence[UUID7] = Field(
    ..., description="List of machine IDs that generated data"
  )

  resource_with_data: Sequence[UUID7] = Field(
    ..., description="List of resource IDs with associated data"
  )

  data_timeline: List[Dict[str, Any]] = Field(
    ..., description="Timeline of data capture events"
  )

  file_attachments: List[Dict[str, Any]] = Field(
    ..., description="List of file attachments with metadata"
  )

  class Config:
    """Pydantic configuration for ProtocolRunDataSummary."""

    from_attributes = True
    use_enum_values = True
    arbitrary_types_allowed = True


class DataSearchFilters(BaseModel):
  """Model for data search and filtering."""

  protocol_run_accession_id: Optional[UUID7] = Field(
    None, description="Filter by protocol run"
  )

  function_call_log_accession_id: Optional[UUID7] = Field(
    None, description="Filter by function call"
  )

  data_types: Optional[List[DataOutputTypeEnum]] = Field(
    None, description="Filter by data types"
  )

  spatial_contexts: Optional[List[DataOutputSpatialContextEnum]] = Field(
    None, description="Filter by spatial context"
  )

  machine_accession_id: Optional[UUID7] = Field(None, description="Filter by machine")

  resource_instance_accession_id: Optional[UUID7] = Field(
    None, description="Filter by resource"
  )

  date_range_start: Optional[datetime] = Field(None, description="Start of date range")

  date_range_end: Optional[datetime] = Field(None, description="End of date range")

  has_numeric_data: Optional[bool] = Field(
    None, description="Filter for entries with numeric data"
  )

  has_file_data: Optional[bool] = Field(
    None, description="Filter for entries with file attachments"
  )

  min_quality_score: Optional[float] = Field(
    None, ge=0.0, le=1.0, description="Minimum quality score"
  )


class DataExportRequest(BaseModel):
  """Model for requesting data export."""

  filters: DataSearchFilters = Field(..., description="Filters for data selection")

  export_format: str = Field(..., description="Export format (csv, json, xlsx, etc.)")

  include_metadata: bool = Field(True, description="Whether to include metadata")

  include_spatial_info: bool = Field(
    True, description="Whether to include spatial information"
  )

  flatten_structure: bool = Field(
    False, description="Whether to flatten hierarchical data"
  )
