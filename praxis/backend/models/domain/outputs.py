# pylint: disable=too-few-public-methods,missing-class-docstring
"""Unified SQLModel definitions for Data Output entities."""

import uuid
from typing import Any

from sqlmodel import Field, SQLModel

from praxis.backend.models.domain.sqlmodel_base import PraxisBase, json_field

# =============================================================================
# Function Data Output
# =============================================================================


class FunctionDataOutputBase(PraxisBase):
  """Base schema for FunctionDataOutput - shared fields for create/update/response."""

  data_type: str | None = Field(default=None, index=True, description="Type of data output")
  file_path: str | None = Field(default=None, description="File path for output data")
  mime_type: str | None = Field(default=None, description="MIME type of the output")


class FunctionDataOutput(FunctionDataOutputBase, table=True):
  """FunctionDataOutput ORM model - represents data output from a function call."""

  __tablename__ = "function_data_outputs"

  data_json: dict[str, Any] | None = json_field(default=None, description="Data output as JSON")

  # Foreign keys
  function_call_log_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="function_call_logs.accession_id", index=True
  )
  protocol_run_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="protocol_runs.accession_id", index=True
  )
  machine_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="machines.accession_id", index=True
  )
  resource_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="resources.accession_id", index=True
  )
  deck_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="decks.accession_id", index=True
  )


class FunctionDataOutputCreate(FunctionDataOutputBase):
  """Schema for creating a FunctionDataOutput."""



class FunctionDataOutputRead(FunctionDataOutputBase):
  """Schema for reading a FunctionDataOutput (API response)."""

  accession_id: uuid.UUID
  data_json: dict[str, Any] | None = None
  data_quality_score: float | None = None
  data_key: str | None = None


class FunctionDataOutputUpdate(SQLModel):
  """Schema for updating a FunctionDataOutput (partial update)."""

  name: str | None = None
  data_type: str | None = None
  file_path: str | None = None
  data_json: dict[str, Any] | None = None
  data_quality_score: float | None = None
  data_key: str | None = None


# =============================================================================
# Well Data Output
# =============================================================================


class WellDataOutputBase(PraxisBase):
  """Base schema for WellDataOutput - shared fields for create/update/response."""

  well_position: str | None = Field(
    default=None, index=True, description="Well position (e.g., 'A1')"
  )
  measurement_type: str | None = Field(default=None, index=True, description="Type of measurement")
  value: float | None = Field(default=None, description="Measured value")
  unit: str | None = Field(default=None, description="Unit of measurement")
  well_name: str | None = Field(default=None, description="Well name (e.g. A1)")
  data_value: float | None = None


class WellDataOutput(WellDataOutputBase, table=True):
  """WellDataOutput ORM model - represents well-specific data output."""

  __tablename__ = "well_data_outputs"

  metadata_json: dict[str, Any] | None = json_field(
    default=None, description="Additional well metadata"
  )

  # Foreign keys
  function_data_output_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="function_data_outputs.accession_id", index=True
  )
  resource_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="resources.accession_id", index=True
  )


class WellDataOutputCreate(WellDataOutputBase):
  """Schema for creating a WellDataOutput."""



class WellDataOutputRead(WellDataOutputBase):
  """Schema for reading a WellDataOutput (API response)."""

  accession_id: uuid.UUID
  metadata_json: dict[str, Any] | None = None


class WellDataOutputUpdate(SQLModel):
  """Schema for updating a WellDataOutput (partial update)."""

  name: str | None = None
  well_position: str | None = None
  measurement_type: str | None = None
  value: float | None = None
  unit: str | None = None
  well_name: str | None = None
  data_value: float | None = None
