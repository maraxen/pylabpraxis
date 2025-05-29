from pydantic import BaseModel
from pydantic.fields import Field
from typing import Dict, Any, Optional, List, Union


class ProtocolStartRequest(BaseModel):
    protocol_class: str
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None  # TODO: make ParameterModel
    assets: Optional[Dict[str, str]] = None  # TODO: make AssetModel
    deck_configuration: Optional[str] = (
        None  # This could be a DeckConfigurationOrm ID or name
    )
    workcell_id: Optional[int] = None  # ID of the WorkcellOrm, if applicable
    protocol_definition_id: Optional[int] = (
        None  # ID of the FunctionProtocolDefinitionOrm, if applicable
    )
    config_data: Dict[str, Any]
    kwargs: Optional[Dict[str, Any]] = None


class ProtocolStatus(BaseModel):
    name: str
    status: str


class ProtocolDirectories(BaseModel):
    directories: List[str]


class ProtocolPrepareRequest(BaseModel):
    protocol_path: (
        str  # This will likely become a protocol_definition_id or name/version
    )
    parameters: Optional[Dict[str, Any]] = None
    asset_assignments: Optional[Dict[str, str]] = None  # asset_name -> instance_name/id


class ProtocolInfo(BaseModel):
    name: str
    path: str  # Corresponds to source_file_path in ORM
    description: str
    has_assets: Optional[bool] = False
    has_parameters: Optional[bool] = False
    version: Optional[str] = None  # Added version
    protocol_definition_id: Optional[int] = None  # Added ID


# Placeholder for UI hints or constraints, to be expanded
class UIHint(BaseModel):
    widget_type: Optional[str] = None
    # TODO: figure out what else should go here


class ParameterConstraintsModel(BaseModel):
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    regex_pattern: Optional[str] = None  # For string validation
    options: Optional[List[Any]] = None  # For dropdowns or choice fields

    class Config:
        from_attributes = True
        validate_assignment = True


class ParameterMetadataModel(BaseModel):
    name: str
    type_hint_str: str  # String representation of the type hint
    actual_type_str: str  # More refined type string, e.g. 'int', 'float', 'bool', 'str', 'list', 'dict', 'PlrResource'
    is_deck_param: bool = False
    optional: bool
    default_value_repr: Optional[str] = (
        None  # String representation of the default value
    )
    description: Optional[str] = None
    # Using Field(default_factory=dict) for constraints_json to ensure a new dict is created for each instance
    constraints_json: ParameterConstraintsModel = Field(
        default_factory=ParameterConstraintsModel
    )  # For things like min/max, length, etc. TODO: make ParameterConstraintsModel
    ui_hint: UIHint = Field(default_factory=UIHint)  # For frontend rendering hints


class AssetConstraintsModel(BaseModel):
    required_methods: List[str] = Field(
        default_factory=list
    )  # Methods that must be available on the asset
    required_attributes: List[str] = Field(
        default_factory=list
    )  # Attributes that must be present on the asset
    required_method_signatures: Dict[str, str] = Field(
        default_factory=dict
    )  # Method names and their expected signatures
    required_method_args: Dict[str, List[str]] = Field(
        default_factory=dict
    )  # Method names and their required argument names, less strict than signature


class AssetRequirementModel(BaseModel):
    name: str  # Argument name in the function signature
    type_hint_str: str  # String representation of the type hint (e.g., "Pipette", "Optional[Plate]")
    actual_type_str: str  # More refined type string, e.g. 'Pipette', 'Plate'
    optional: bool
    default_value_repr: Optional[str] = (
        None  # String representation of the default value, if any
    )
    description: Optional[str] = None  # Description of the asset's role
    constraints: AssetConstraintsModel = Field(
        default_factory=AssetConstraintsModel
    )  # ADDED FIELD


class FunctionProtocolDefinitionModel(BaseModel):
    # Core definition
    name: str
    version: str = "0.1.0"
    description: Optional[str] = None

    # Source information
    source_file_path: str  # Relative path within the source
    module_name: str  # e.g., my_protocols.transfer
    function_name: str  # The actual Python function name

    # Link to source repository or filesystem (one of these should be set by DiscoveryService)
    source_repository_name: Optional[str] = None
    commit_hash: Optional[str] = None
    file_system_source_name: Optional[str] = None

    # Execution behavior
    is_top_level: bool = False
    solo_execution: bool = False  # Requires exclusive workcell access
    preconfigure_deck: bool = (
        False  # If deck needs specific setup from DeckConfigurationOrm
    )
    deck_param_name: Optional[str] = (
        None  # Name of the parameter that receives the deck if preconfigure_deck=True
    )
    state_param_name: Optional[str] = (
        "state"  # Name of the state parameter (PraxisState or dict)
    )

    # Categorization and metadata
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    deprecated: bool = False

    # Derived from function signature and decorator
    parameters: List[ParameterMetadataModel] = Field(default_factory=list)
    assets: List[AssetRequirementModel] = Field(
        default_factory=list
    )  # Assets inferred from type hints

    # db_id will be populated by ProtocolDiscoveryService after saving to FunctionProtocolDefinitionOrm
    db_id: Optional[int] = None

    class Config:
        from_attributes = True
        validate_assignment = True


class ProtocolParameters(BaseModel):
    """
    Represents the parameters for a protocol run, including both user-defined and system-generated parameters.
    """

    user_parameters: Dict[str, ParameterMetadataModel] = Field(
        default_factory=dict
    )  # User-defined parameters
    system_parameters: Dict[str, ParameterMetadataModel] = Field(
        default_factory=dict
    )  # System-generated parameters (e.g., run GUID, timestamps)

    class Config:
        from_attributes = True
        validate_assignment = True
