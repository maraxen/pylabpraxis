"""Pydantic models for protocol management and execution in the Praxis application.

These models facilitate the definition, preparation, and execution of protocols,
including requests to start a run, status updates, and detailed metadata
about protocol parameters and required assets.

Models included:
- ProtocolStartRequest
- ProtocolStatus
- ProtocolDirectories
- ProtocolPrepareRequest
- ProtocolInfo
- UIHint
- ParameterConstraintsModel
- ParameterMetadataModel
- AssetConstraintsModel
- AssetRequirementModel
- FunctionProtocolDefinitionCreate
- ProtocolParameters
"""

from datetime import datetime
from typing import Any

from pydantic import UUID7, BaseModel, ConfigDict
from pydantic.fields import Field

from praxis.backend.models.enums import FunctionCallStatusEnum, ProtocolRunStatusEnum
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.models.pydantic_internals.pydantic_base import PraxisBaseModel


class ProtocolStartRequest(BaseModel):
  """Represents a request to start a protocol run.

  This includes details about the protocol to be run, its parameters,
  asset assignments, and configuration data.
  """

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

  protocol_class: str
  description: str | None = None
  parameters: dict[str, Any] | None = None
  assets: dict[str, str] | None = None
  deck: str | None = None
  workcell_accession_id: UUID7 | None = None
  protocol_definition_accession_id: UUID7 | None = None
  config_data: dict[str, Any]
  kwargs: dict[str, Any] | None = None


class ProtocolStatus(BaseModel):
  """Provides a simple status update for a protocol."""

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

  name: str
  status: str


class ProtocolDirectories(BaseModel):
  """Lists directories associated with protocols."""

  directories: list[str]


class ProtocolPrepareRequest(BaseModel):
  """Represents a request to prepare a protocol for execution.

  This includes the protocol's path or ID, along with any necessary
  parameters and asset assignments.
  """

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

  protocol_path: str
  parameters: dict[str, Any] | None = None
  asset_assignments: dict[str, str] | None = None


class ProtocolInfo(BaseModel):
  """Provides essential information about a protocol.

  This includes its name, source path, description, and whether it has
  parameters or assets, along with version and database ID.
  """

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

  name: str
  path: str
  description: str
  has_assets: bool | None = False
  has_parameters: bool | None = False
  version: str | None = None
  protocol_definition_accession_id: UUID7 | None = None


class UIHint(BaseModel):
  """Provides hints for parameter/asset rendering in a user interface."""

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

  widget_type: str | None = None


class DataViewMetadataModel(BaseModel):
  """Defines a data view required by a protocol for input data.

  Data views allow protocols to declare what input data they need in a structured way.
  They can reference:
  - PLR state data (e.g., liquid volume tracking, resource positions)
  - Function data outputs from previous protocol runs (e.g., plate reader reads)

  Schema validation errors during protocol setup generate warnings but do not
  block protocol execution.
  """

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True, from_attributes=True)

  name: str
  description: str | None = None
  source_type: str = "function_output"  # "plr_state", "function_output", "external"
  source_filter_json: dict[str, Any] | None = Field(
    default=None,
    description="Filter criteria to select specific data. "
    "For 'plr_state': {'state_key': 'tracker.volumes', 'resource_pattern': '*plate*'}. "
    "For 'function_output': {'function_fqn': '...', 'output_type': 'absorbance'}.",
  )
  data_schema_json: dict[str, Any] | None = Field(
    default=None,
    description="Expected data schema for validation (column names, types).",
  )
  required: bool = False
  default_value_json: Any = None


class ParameterConstraintsModel(BaseModel):
  """Defines validation constraints for a protocol parameter."""

  min_value: int | float | None = None
  max_value: int | float | None = None
  min_length: int | None = None
  max_length: int | None = None
  regex_pattern: str | None = None
  options: list[Any] | None = None

  model_config = ConfigDict(
    from_attributes=True,
    validate_assignment=True,
  )


class ParameterMetadataModel(BaseModel):
  """Provides comprehensive metadata for a protocol parameter.

  This includes its name, type information, default value, description,
  constraints, and UI rendering hints.
  """

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

  name: str
  type_hint: str
  fqn: str
  is_deck_param: bool = False
  optional: bool
  default_value_repr: str | None = None
  description: str | None = None
  constraints: ParameterConstraintsModel = Field(
    default_factory=ParameterConstraintsModel,
  )
  ui_hint: UIHint | None = None
  linked_to: str | None = None


class LocationConstraintsModel(BaseModel):
  """Defines constraints for the location of an asset in a protocol.

  This includes required locations, optional locations, and any specific
  location-related constraints.
  """

  location_requirements: list[str] = Field(default_factory=list)
  on_resource_type: str = Field(default="")
  stack: bool = Field(default=False)
  directly_position: bool = Field(default=False)
  position_condition: list[str] = Field(default_factory=list)

  model_config = ConfigDict(
    from_attributes=True,
    validate_assignment=True,
  )


class AssetConstraintsModel(BaseModel):
  """Defines constraints for an asset required by a protocol."""

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True, from_attributes=True)

  required_methods: list[str] = Field(default_factory=list)
  required_attributes: list[str] = Field(default_factory=list)
  required_method_signatures: dict[str, str] = Field(default_factory=dict)
  required_method_args: dict[str, list[str]] = Field(default_factory=dict)
  min_volume_ul: float | None = None


class AssetRequirementModel(BaseModel):
  """Describes a single asset required by a protocol.

  This includes its name, type information, optionality, default value,
  description, and specific constraints.
  """

  model_config = ConfigDict(
    use_enum_values=True,
    validate_assignment=True,
    from_attributes=True,
    populate_by_name=True,
  )

  accession_id: UUID7
  name: str
  fqn: str
  type_hint_str: str
  optional: bool = False
  default_value_repr: str | None = None
  description: str | None = None
  constraints: AssetConstraintsModel = Field(
    default_factory=AssetConstraintsModel,
    validation_alias="constraints_json",
  )
  location_constraints: LocationConstraintsModel = Field(
    default_factory=LocationConstraintsModel,
    validation_alias="location_constraints_json",
  )


class FunctionProtocolDefinitionBase(BaseModel):
  """Base model for a function protocol definition."""

  model_config = ConfigDict(
    use_enum_values=True,
    validate_assignment=True,
    populate_by_name=True,
    from_attributes=True,
  )

  name: str
  fqn: str
  version: str = "0.1.0"
  description: str | None = None

  source_file_path: str
  module_name: str
  function_name: str

  source_repository_name: str | None = None
  commit_hash: str | None = None
  file_system_source_name: str | None = None

  is_top_level: bool = False
  solo_execution: bool = False
  preconfigure_deck: bool = False
  requires_deck: bool = True  # False for machine-only protocols (e.g., plate reader)
  deck_param_name: str | None = None
  deck_construction_function_fqn: str | None = None  # FQN of deck construction callable
  deck_layout_path: str | None = None  # Path to JSON deck layout configuration
  state_param_name: str | None = "state"

  category: str | None = None
  tags: Any = Field(default_factory=list)
  deprecated: bool = False

  source_hash: str | None = None
  computation_graph_json: dict[str, Any] | None = Field(
    default=None,
    alias="computation_graph",
  )

  parameters: list[ParameterMetadataModel] = Field(default_factory=list)
  assets: list[AssetRequirementModel] = Field(default_factory=list)
  data_views_json: list[DataViewMetadataModel] | None = Field(
    default_factory=list,
    alias="data_views",
  )
  hardware_requirements_json: dict[str, Any] | None = Field(
    default=None,
    alias="hardware_requirements",
  )
  setup_instructions_json: list[dict[str, Any]] | None = Field(
    default=None,
    description="Pre-run setup instructions to display in Deck Setup wizard",
  )


class FunctionProtocolDefinitionCreate(FunctionProtocolDefinitionBase):
  """Represents a detailed definition of a function-based protocol.

  This model encapsulates core definition details, source information,
  execution behavior, categorization, and inferred parameters and assets.
  """

  tags: list[str] = Field(default_factory=list)
  accession_id: UUID7 | None = Field(default=None, description="Optional accession ID.")


class FunctionProtocolDefinitionUpdate(BaseModel):
  """Model for updating a function protocol definition."""

  name: str | None = None
  version: str | None = None
  description: str | None = None
  source_file_path: str | None = None
  module_name: str | None = None
  function_name: str | None = None
  source_repository_name: str | None = None
  commit_hash: str | None = None
  file_system_source_name: str | None = None
  is_top_level: bool | None = None
  solo_execution: bool | None = None
  preconfigure_deck: bool | None = None
  requires_deck: bool | None = None
  deck_param_name: str | None = None
  deck_construction_function_fqn: str | None = None
  deck_layout_path: str | None = None
  state_param_name: str | None = None
  category: str | None = None
  tags: list[str] | None = None
  deprecated: bool | None = None
  parameters: list[ParameterMetadataModel] | None = None
  assets: list[AssetRequirementModel] | None = None
  data_views: list[DataViewMetadataModel] | None = None
  hardware_requirements: dict[str, Any] | None = None
  setup_instructions_json: list[dict[str, Any]] | None = None
  source_hash: str | None = None
  computation_graph: dict[str, Any] | None = None


class InferredRequirementModel(BaseModel):
  """A requirement inferred from protocol simulation."""

  model_config = ConfigDict(from_attributes=True)

  requirement_type: str = Field(description="Type: tips_required, resource_on_deck, liquid_present")
  resource: str | None = Field(default=None, description="Resource involved")
  details: dict[str, Any] = Field(default_factory=dict)
  inferred_at_level: str = Field(default="", description="Level at which this was inferred")


class FailureModeModel(BaseModel):
  """A detected failure mode for a protocol."""

  model_config = ConfigDict(from_attributes=True)

  initial_state: dict[str, Any] = Field(
    default_factory=dict, description="State configuration that causes failure"
  )
  failure_point: str = Field(default="", description="Operation ID where failure occurs")
  failure_type: str = Field(default="", description="Type of failure")
  message: str = Field(default="", description="Human-readable failure description")
  suggested_fix: str | None = Field(default=None, description="How to prevent this failure")
  severity: str = Field(default="error", description="Severity: error, warning, info")


class SimulationResultModel(BaseModel):
  """Cached simulation result for a protocol definition."""

  model_config = ConfigDict(from_attributes=True)

  passed: bool = Field(default=False, description="Whether protocol passed all validation")
  level_completed: str = Field(default="none", description="Highest level completed")
  level_failed: str | None = Field(default=None, description="Level where failure occurred")
  structural_error: str | None = Field(default=None, description="Structural error if any")
  violations: list[dict[str, Any]] = Field(
    default_factory=list, description="All violations from simulation"
  )
  inferred_requirements: list[InferredRequirementModel] = Field(
    default_factory=list, description="Requirements inferred from simulation"
  )
  failure_modes: list[FailureModeModel] = Field(
    default_factory=list, description="Enumerated failure modes"
  )
  failure_mode_stats: dict[str, Any] = Field(
    default_factory=dict, description="Failure detection statistics"
  )
  simulation_version: str = Field(default="", description="Simulator version")
  simulated_at: datetime | None = Field(default=None, description="When simulation was run")
  execution_time_ms: float = Field(default=0.0, description="Simulation execution time")


class FunctionProtocolDefinitionResponse(FunctionProtocolDefinitionBase, PraxisBaseModel):
  """Model for API responses for a function protocol definition."""

  model_config = ConfigDict(from_attributes=True)

  # Override base field to map from ORM JSON field
  hardware_requirements: dict[str, Any] | None = Field(
    default=None,
    validation_alias="hardware_requirements_json",
  )

  # Simulation cache fields
  simulation_result: SimulationResultModel | None = Field(
    default=None,
    validation_alias="simulation_result_json",
    description="Cached simulation result",
  )
  inferred_requirements: list[InferredRequirementModel] | None = Field(
    default_factory=list,
    validation_alias="inferred_requirements_json",
    description="Inferred state requirements",
  )
  failure_modes: list[FailureModeModel] | None = Field(
    default_factory=list,
    validation_alias="failure_modes_json",
    description="Known failure modes",
  )
  simulation_version: str | None = Field(
    default=None,
    description="Simulator version for cache validation",
  )
  simulation_cached_at: datetime | None = Field(
    default=None,
    description="When simulation was last run",
  )


class ProtocolParameters(BaseModel):
  """Represents the parameters for a protocol run.

  This includes both user-defined parameters, derived from the protocol's
  function signature, and system-generated parameters that might be
  used internally for logging or tracking.
  """

  model_config = ConfigDict(
    from_attributes=True,
    validate_assignment=True,
  )

  user_parameters: dict[str, ParameterMetadataModel] = Field(default_factory=dict)
  system_parameters: dict[str, ParameterMetadataModel] = Field(default_factory=dict)


class ProtocolDefinitionFilters(BaseModel):
  """Model for filtering protocol definitions."""

  search_filters: SearchFilters
  source_name: str | None = None
  is_top_level: bool | None = None
  category: str | None = None
  tags: list[str] | None = None
  include_deprecated: bool = False


class ProtocolRunBase(BaseModel):
  """Base model for a protocol run."""

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

  name: str | None = None
  status: ProtocolRunStatusEnum | None = None
  start_time: datetime | None = None
  end_time: datetime | None = None
  input_parameters_json: dict[str, Any] | None = None
  resolved_assets_json: dict[str, Any] | None = None
  output_data_json: dict[str, Any] | None = None
  initial_state_json: dict[str, Any] | None = None
  final_state_json: dict[str, Any] | None = None
  data_directory_path: str | None = None
  created_by_user: dict[str, Any] | None = None
  previous_accession_id: UUID7 | None = None


class ProtocolRunCreate(ProtocolRunBase):
  """Model for creating a new protocol run."""

  run_accession_id: UUID7
  top_level_protocol_definition_accession_id: UUID7


class ProtocolRunUpdate(ProtocolRunBase):
  """Model for updating a protocol run."""


class ProtocolRunResponse(ProtocolRunBase, PraxisBaseModel):
  """Model for API responses for a protocol run."""

  model_config = PraxisBaseModel.model_config


class FunctionCallLogBase(BaseModel):
  """Base model for a function call log."""

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

  end_time: datetime | None = None
  input_args_json: dict[str, Any] | None = None
  return_value_json: dict[str, Any] | None = None
  status: FunctionCallStatusEnum = FunctionCallStatusEnum.UNKNOWN
  error_message_text: str | None = None
  error_traceback_text: str | None = None


class FunctionCallLogCreate(FunctionCallLogBase, PraxisBaseModel):
  """Model for creating a new function call log."""

  parent_function_call_log_accession_id: UUID7 | None = None
  start_time: datetime
  protocol_run_accession_id: UUID7
  sequence_in_run: int
  function_protocol_definition_accession_id: UUID7


class FunctionCallLogUpdate(FunctionCallLogBase):
  """Model for updating a function call log."""


class FunctionCallLogResponse(FunctionCallLogCreate):
  """Model for API responses for a function call log."""

  model_config = PraxisBaseModel.model_config
