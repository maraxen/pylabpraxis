# pylint: disable=too-few-public-methods,missing-class-docstring
"""Unified SQLModel definitions for Protocol-related entities.

Note: This is a simplified initial implementation focusing on ProtocolRun.
Additional models (FunctionProtocolDefinition, FunctionCallLog, etc.) can be added as needed.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlmodel import Field, SQLModel, Relationship

from praxis.backend.models.domain.sqlmodel_base import PraxisBase
from praxis.backend.models.enums import (
  FunctionCallStatusEnum,
  ProtocolRunStatusEnum,
)
from praxis.backend.utils.db import JsonVariant


class AssetConstraintsModel(SQLModel):
  """Model for asset constraints."""

  min_volume_ul: float | None = None
  max_volume_ul: float | None = None
  dead_volume_ul: float | None = None
  min_quantity: int | None = None
  max_quantity: int | None = None
  allow_partial: bool | None = None


class LocationConstraintsModel(SQLModel):
  """Model for location constraints."""

  allowed_decks: list[str] | None = None
  allowed_slots: list[str] | None = None
  required_capabilities: dict[str, Any] | None = None


class ParameterConstraintsModel(SQLModel):
  """Model for parameter constraints."""

  min_value: float | None = None
  max_value: float | None = None
  allowed_values: list[Any] | None = None
  regex: str | None = None


class ParameterMetadataModel(SQLModel):
  """Model for parameter metadata."""

  name: str
  type_hint: str
  description: str | None = None
  default_value: Any | None = None
  constraints: ParameterConstraintsModel | None = None


class DataViewMetadataModel(SQLModel):
  """Model for data view metadata."""

  name: str
  description: str | None = None
  source_type: str = "function_output"
  source_filter_json: dict[str, Any] | None = None
  data_schema_json: dict[str, Any] | None = None
  required: bool = False
  default_value_json: Any = None


class ProtocolDefinitionFilters(SQLModel):
  """Model for protocol definition filters."""

  search_text: str | None = None
  category: str | None = None
  is_latest: bool | None = None


class ProtocolDirectories(SQLModel):
  """Model for protocol directories."""

  data_dir: str
  logs_dir: str
  temp_dir: str


class ProtocolInfo(SQLModel):
  """Model for protocol info."""

  name: str
  description: str | None = None
  version: str | None = None
  author: str | None = None


class ProtocolParameters(SQLModel):
  """Model for protocol parameters."""

  params: dict[str, Any]


class ProtocolPrepareRequest(SQLModel):
  """Model for protocol prepare request."""

  protocol_id: uuid.UUID
  params: dict[str, Any] | None = None


class ProtocolStartRequest(SQLModel):
  """Model for protocol start request."""

  run_id: uuid.UUID


class ProtocolStatus(SQLModel):
  """Model for protocol status."""

  status: ProtocolRunStatusEnum
  progress: float | None = None
  message: str | None = None


# =============================================================================
# Parameter Definition
# =============================================================================


class ParameterDefinitionBase(PraxisBase):
  """Base schema for ParameterDefinition."""

  name: str = Field(index=True, description="The name of the parameter")
  type_hint: str = Field(index=True, description="The type hint of the parameter")
  fqn: str = Field(index=True, description="The fully qualified name of the parameter")
  is_deck_param: bool = Field(default=False)
  optional: bool = Field(default=False, description="Whether the parameter is optional")
  default_value_repr: str | None = Field(
    default=None, description="String representation of default value"
  )
  description: str | None = Field(default=None, description="Description of the parameter")
  field_type: str | None = Field(default=None)
  is_itemized: bool = Field(default=False)
  linked_to: str | None = Field(default=None)


class ParameterDefinition(ParameterDefinitionBase, table=True):
  """ParameterDefinition ORM model."""

  __tablename__ = "parameter_definitions"

  constraints_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Parameter constraints"
  )
  itemized_spec_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Itemized resource specification"
  )
  ui_hint_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="UI hints"
  )

  protocol_definition_accession_id: uuid.UUID = Field(
    foreign_key="function_protocol_definitions.accession_id", index=True
  )


class ParameterDefinitionRead(ParameterDefinitionBase):
  """Schema for reading a ParameterDefinition."""

  accession_id: uuid.UUID


class ParameterDefinitionUpdate(SQLModel):
  """Schema for updating a ParameterDefinition."""

  description: str | None = None
  optional: bool | None = None
  default_value_repr: str | None = None


# =============================================================================
# Asset Requirement
# =============================================================================


class AssetRequirementBase(PraxisBase):
  """Base schema for AssetRequirement."""

  name: str = Field(index=True, description="The name of the asset requirement")
  type_hint_str: str = Field(index=True, description="Type hint")
  fqn: str | None = Field(default=None, index=True, description="Fully qualified name")
  actual_type_str: str | None = Field(default=None, index=True, description="Actual type")
  optional: bool = Field(default=False)
  default_value_repr: str | None = Field(default=None)
  description: str | None = Field(default=None)
  required_plr_category: str | None = Field(default=None, index=True)


class AssetRequirement(AssetRequirementBase, table=True):
  """AssetRequirement ORM model."""

  __tablename__ = "protocol_asset_requirements"

  constraints_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Asset constraints"
  )
  location_constraints_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Location constraints"
  )

  protocol_definition_accession_id: uuid.UUID = Field(
    foreign_key="function_protocol_definitions.accession_id", index=True
  )


class AssetRequirementRead(AssetRequirementBase):
  """Schema for reading an AssetRequirement."""

  accession_id: uuid.UUID
  constraints: AssetConstraintsModel | None = None
  location_constraints: LocationConstraintsModel | None = None


class AssetRequirementCreate(AssetRequirementBase):
  """Schema for creating an AssetRequirement."""

  protocol_definition_accession_id: uuid.UUID


class AssetRequirementUpdate(SQLModel):
  """Schema for updating an AssetRequirement."""

  description: str | None = None
  optional: bool | None = None


# =============================================================================
# Function Protocol Definition
# =============================================================================


class FunctionProtocolDefinitionBase(PraxisBase):
  """Base schema for FunctionProtocolDefinition."""

  fqn: str = Field(index=True, description="Fully qualified name")
  version: str = Field(default="0.1.0", description="Semantic version")
  description: str | None = Field(default=None)
  source_file_path: str = Field(index=True)
  module_name: str = Field(index=True)
  function_name: str = Field(index=True)
  is_top_level: bool = Field(default=False, index=True)
  solo_execution: bool = Field(default=False)
  preconfigure_deck: bool = Field(default=False)
  requires_deck: bool = Field(default=True)
  deck_param_name: str | None = Field(default=None)
  deck_construction_function_fqn: str | None = Field(default=None)
  deck_layout_path: str | None = Field(default=None)
  state_param_name: str | None = Field(default=None)
  category: str | None = Field(default=None, index=True)
  deprecated: bool = Field(default=False, index=True)
  source_hash: str | None = Field(default=None)
  graph_cached_at: datetime | None = Field(default=None)
  simulation_version: str | None = Field(default=None)
  simulation_cached_at: datetime | None = Field(default=None)
  bytecode_python_version: str | None = Field(default=None)
  bytecode_cache_version: str | None = Field(default=None)
  bytecode_cached_at: datetime | None = Field(default=None)
  commit_hash: str | None = Field(default=None, index=True)


class FunctionProtocolDefinition(FunctionProtocolDefinitionBase, table=True):
  """FunctionProtocolDefinition ORM model."""

  __tablename__ = "function_protocol_definitions"

  tags: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)
  hardware_requirements_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)
  data_views_json: list[Any] | None = Field(default=None, sa_type=JsonVariant)
  computation_graph_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)
  setup_instructions_json: list[Any] | None = Field(default=None, sa_type=JsonVariant)
  simulation_result_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)
  inferred_requirements_json: list[Any] | None = Field(default=None, sa_type=JsonVariant)
  failure_modes_json: list[Any] | None = Field(default=None, sa_type=JsonVariant)
  cached_bytecode: bytes | None = Field(default=None)

  source_repository_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="protocol_source_repositories.accession_id", index=True
  )
  file_system_source_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="file_system_protocol_sources.accession_id", index=True
  )


class FunctionProtocolDefinitionCreate(FunctionProtocolDefinitionBase):
  """Schema for creating a FunctionProtocolDefinition."""

  accession_id: uuid.UUID | None = None
  tags: dict[str, Any] | None = None
  parameters: list[ParameterMetadataModel] | None = None
  assets: list[AssetRequirementCreate] | None = None
  data_views: list[DataViewMetadataModel] | None = None
  setup_instructions_json: list[dict[str, Any]] | None = None


class FunctionProtocolDefinitionRead(FunctionProtocolDefinitionBase):
  """Schema for reading a FunctionProtocolDefinition."""

  accession_id: uuid.UUID


class FunctionProtocolDefinitionUpdate(SQLModel):
  """Schema for updating a FunctionProtocolDefinition."""

  description: str | None = None
  tags: dict[str, Any] | None = None
  deprecated: bool | None = None


# =============================================================================
# Protocol Run
# =============================================================================


class ProtocolRunBase(PraxisBase):
  """Base schema for ProtocolRun - shared fields for create/update/response."""

  status: ProtocolRunStatusEnum = Field(
    default=ProtocolRunStatusEnum.PENDING,
    index=True,
  )
  start_time: datetime | None = Field(default=None, description="When the protocol run started")
  end_time: datetime | None = Field(default=None, description="When the protocol run completed")
  data_directory_path: str | None = Field(default=None, description="Path to data directory")
  duration_ms: int | None = Field(default=None, description="Duration in milliseconds")


class ProtocolRun(ProtocolRunBase, table=True):
  """ProtocolRun ORM model - represents a protocol execution."""

  __tablename__ = "protocol_runs"

  input_parameters_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Input parameters"
  )
  resolved_assets_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Resolved assets"
  )
  output_data_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Output data"
  )
  initial_state_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Initial state"
  )
  final_state_json: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="Final state"
  )
  created_by_user: dict[str, Any] | None = Field(
    default=None, sa_type=JsonVariant, description="User info"
  )

  # Foreign keys
  top_level_protocol_definition_accession_id: uuid.UUID = Field(
    foreign_key="function_protocol_definitions.accession_id", index=True
  )
  previous_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="protocol_runs.accession_id", index=True
  )


class ProtocolRunCreate(ProtocolRunBase):
  """Schema for creating a ProtocolRun."""

  top_level_protocol_definition_accession_id: uuid.UUID


class ProtocolRunRead(ProtocolRunBase):
  """Schema for reading a ProtocolRun (API response)."""

  accession_id: uuid.UUID
  input_parameters_json: dict[str, Any] | None = None
  resolved_assets_json: dict[str, Any] | None = None
  output_data_json: dict[str, Any] | None = None


class ProtocolRunUpdate(SQLModel):
  """Schema for updating a ProtocolRun (partial update)."""

  status: ProtocolRunStatusEnum | None = None
  start_time: datetime | None = None
  end_time: datetime | None = None
  output_data_json: dict[str, Any] | None = None
  data_directory_path: str | None = None


# =============================================================================
# Function Call Log
# =============================================================================


class FunctionCallLogBase(PraxisBase):
  """Base schema for FunctionCallLog."""

  sequence_in_run: int = Field(index=True)
  status: FunctionCallStatusEnum = Field(default=FunctionCallStatusEnum.UNKNOWN)
  start_time: datetime = Field(default_factory=datetime.now)
  end_time: datetime | None = Field(default=None)
  duration_ms: int | None = Field(default=None)
  error_message_text: str | None = Field(default=None)
  error_traceback_text: str | None = Field(default=None)


class FunctionCallLog(FunctionCallLogBase, table=True):
  """FunctionCallLog ORM model."""

  __tablename__ = "function_call_logs"

  input_args_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)
  return_value_json: dict[str, Any] | None = Field(default=None, sa_type=JsonVariant)

  protocol_run_accession_id: uuid.UUID = Field(foreign_key="protocol_runs.accession_id", index=True)
  function_protocol_definition_accession_id: uuid.UUID = Field(
    foreign_key="function_protocol_definitions.accession_id", index=True
  )
  parent_function_call_log_accession_id: uuid.UUID | None = Field(
    default=None, foreign_key="function_call_logs.accession_id", index=True
  )


class FunctionCallLogCreate(FunctionCallLogBase):
  """Schema for creating a FunctionCallLog."""

  protocol_run_accession_id: uuid.UUID
  function_protocol_definition_accession_id: uuid.UUID


class FunctionCallLogRead(FunctionCallLogBase):
  """Schema for reading a FunctionCallLog."""

  accession_id: uuid.UUID
  input_args_json: dict[str, Any] | None = None
  return_value_json: dict[str, Any] | None = None


class FunctionCallLogUpdate(SQLModel):
  """Schema for updating a FunctionCallLog."""

  status: FunctionCallStatusEnum | None = None
  end_time: datetime | None = None
  duration_ms: int | None = None
  error_message_text: str | None = None
  error_traceback_text: str | None = None
  return_value_json: dict[str, Any] | None = None
