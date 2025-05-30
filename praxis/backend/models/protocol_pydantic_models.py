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
- FunctionProtocolDefinitionModel
- ProtocolParameters
"""

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel
from pydantic.fields import Field


class ProtocolStartRequest(BaseModel):
  """Represents a request to start a protocol run.

  This includes details about the protocol to be run, its parameters,
  asset assignments, and configuration data.
  """

  protocol_class: str
  name: str
  description: Optional[str] = None
  parameters: Optional[Dict[str, Any]] = None
  assets: Optional[Dict[str, str]] = None
  deck_configuration: Optional[str] = None
  workcell_id: Optional[int] = None
  protocol_definition_id: Optional[int] = None
  config_data: Dict[str, Any]
  kwargs: Optional[Dict[str, Any]] = None


class ProtocolStatus(BaseModel):
  """Provides a simple status update for a protocol."""

  name: str
  status: str


class ProtocolDirectories(BaseModel):
  """Lists directories associated with protocols."""

  directories: List[str]


class ProtocolPrepareRequest(BaseModel):
  """Represents a request to prepare a protocol for execution.

  This includes the protocol's path or ID, along with any necessary
  parameters and asset assignments.
  """

  protocol_path: str
  parameters: Optional[Dict[str, Any]] = None
  asset_assignments: Optional[Dict[str, str]] = None


class ProtocolInfo(BaseModel):
  """Provides essential information about a protocol.

  This includes its name, source path, description, and whether it has
  parameters or assets, along with version and database ID.
  """

  name: str
  path: str
  description: str
  has_assets: Optional[bool] = False
  has_parameters: Optional[bool] = False
  version: Optional[str] = None
  protocol_definition_id: Optional[int] = None


class UIHint(BaseModel):
  """Provides hints for how a parameter or asset should be rendered in a user interface."""

  widget_type: Optional[str] = None


class ParameterConstraintsModel(BaseModel):
  """Defines validation constraints for a protocol parameter."""

  min_value: Optional[Union[int, float]] = None
  max_value: Optional[Union[int, float]] = None
  min_length: Optional[int] = None
  max_length: Optional[int] = None
  regex_pattern: Optional[str] = None
  options: Optional[List[Any]] = None

  class Config:
    """Pydantic configuration for ParameterConstraintsModel."""

    from_attributes = True
    validate_assignment = True


class ParameterMetadataModel(BaseModel):
  """Provides comprehensive metadata for a protocol parameter.

  This includes its name, type information, default value, description,
  constraints, and UI rendering hints.
  """

  name: str
  type_hint_str: str
  actual_type_str: str
  is_deck_param: bool = False
  optional: bool
  default_value_repr: Optional[str] = None
  description: Optional[str] = None
  constraints: ParameterConstraintsModel = Field(
    default_factory=ParameterConstraintsModel
  )
  ui_hint: UIHint = Field(default_factory=UIHint)


class AssetConstraintsModel(BaseModel):
  """Defines constraints for an asset required by a protocol."""

  required_methods: List[str] = Field(default_factory=list)
  required_attributes: List[str] = Field(default_factory=list)
  required_method_signatures: Dict[str, str] = Field(default_factory=dict)
  required_method_args: Dict[str, List[str]] = Field(default_factory=dict)


class AssetRequirementModel(BaseModel):
  """Describes a single asset required by a protocol.

  This includes its name, type information, optionality, default value,
  description, and specific constraints.
  """

  name: str
  type_hint_str: str
  actual_type_str: str
  optional: bool
  default_value_repr: Optional[str] = None
  description: Optional[str] = None
  constraints: AssetConstraintsModel = Field(default_factory=AssetConstraintsModel)


class FunctionProtocolDefinitionModel(BaseModel):
  """Represents a detailed definition of a function-based protocol.

  This model encapsulates core definition details, source information,
  execution behavior, categorization, and inferred parameters and assets.
  """

  name: str
  version: str = "0.1.0"
  description: Optional[str] = None

  source_file_path: str
  module_name: str
  function_name: str

  source_repository_name: Optional[str] = None
  commit_hash: Optional[str] = None
  file_system_source_name: Optional[str] = None

  is_top_level: bool = False
  solo_execution: bool = False
  preconfigure_deck: bool = False
  deck_param_name: Optional[str] = None
  state_param_name: Optional[str] = "state"

  category: Optional[str] = None
  tags: List[str] = Field(default_factory=list)
  deprecated: bool = False

  parameters: List[ParameterMetadataModel] = Field(default_factory=list)
  assets: List[AssetRequirementModel] = Field(default_factory=list)

  db_id: Optional[int] = None

  class Config:
    """Pydantic configuration for FunctionProtocolDefinitionModel."""

    from_attributes = True
    validate_assignment = True


class ProtocolParameters(BaseModel):
  """Represents the parameters for a protocol run.

  This includes both user-defined parameters, derived from the protocol's
  function signature, and system-generated parameters that might be
  used internally for logging or tracking.
  """

  user_parameters: Dict[str, ParameterMetadataModel] = Field(default_factory=dict)
  system_parameters: Dict[str, ParameterMetadataModel] = Field(default_factory=dict)

  class Config:
    """Pydantic configuration for ProtocolParameters."""

    from_attributes = True
    validate_assignment = True
