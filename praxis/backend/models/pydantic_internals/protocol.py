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

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

  required_methods: list[str] = Field(default_factory=list)
  required_attributes: list[str] = Field(default_factory=list)
  required_method_signatures: dict[str, str] = Field(default_factory=dict)
  required_method_args: dict[str, list[str]] = Field(default_factory=dict)


class AssetRequirementModel(BaseModel):

  """Describes a single asset required by a protocol.

  This includes its name, type information, optionality, default value,
  description, and specific constraints.
  """

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

  accession_id: UUID7
  name: str
  fqn: str
  type_hint_str: str
  optional: bool = False
  default_value_repr: str | None = None
  description: str | None = None
  constraints: AssetConstraintsModel = Field(default_factory=AssetConstraintsModel)
  location_constraints: LocationConstraintsModel = Field(
    default_factory=LocationConstraintsModel,
  )


class FunctionProtocolDefinitionBase(BaseModel):

  """Base model for a function protocol definition."""

  model_config = ConfigDict(use_enum_values=True, validate_assignment=True)

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
  deck_param_name: str | None = None
  deck_construction_function_fqn: str | None = None  # New field for deck construction callable
  state_param_name: str | None = "state"

  category: str | None = None
  tags: Any = Field(default_factory=list)
  deprecated: bool = False

  parameters: list[ParameterMetadataModel] = Field(default_factory=list)
  assets: list[AssetRequirementModel] = Field(default_factory=list)


class FunctionProtocolDefinitionCreate(FunctionProtocolDefinitionBase):

  """Represents a detailed definition of a function-based protocol.

  This model encapsulates core definition details, source information,
  execution behavior, categorization, and inferred parameters and assets.
  """

  tags: list[str] = Field(default_factory=list)


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
  deck_param_name: str | None = None
  deck_construction_function_fqn: str | None = None
  state_param_name: str | None = None
  category: str | None = None
  tags: list[str] | None = None
  deprecated: bool | None = None
  parameters: list[ParameterMetadataModel] | None = None
  assets: list[AssetRequirementModel] | None = None


class FunctionProtocolDefinitionResponse(FunctionProtocolDefinitionBase, PraxisBaseModel):

  """Model for API responses for a function protocol definition."""

  model_config = ConfigDict(from_attributes=True)


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
