# praxis/backend/protocol_core/protocol_definition_models.py
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator # type: ignore # Assuming Pydantic v1, add ignore for potential v2 import issues if any

# Placeholder for UI hints or constraints, to be expanded
class UIHint(BaseModel):
    widget_type: Optional[str] = None # e.g., "slider", "dropdown", "textfield"
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    step: Optional[Union[int, float]] = None
    options: Optional[List[Any]] = None # For dropdowns
    regex_pattern: Optional[str] = None # For string validation

class ParameterMetadataModel(BaseModel):
    name: str
    type_hint_str: str # String representation of the type hint
    actual_type_str: str # More refined type string, e.g. 'int', 'float', 'bool', 'str', 'list', 'dict', 'PlrResource'
    is_deck_param: bool = False
    optional: bool
    default_value_repr: Optional[str] = None # String representation of the default value
    description: Optional[str] = None
    # Using Field(default_factory=dict) for constraints_json to ensure a new dict is created for each instance
    constraints_json: Dict[str, Any] = Field(default_factory=dict) # For things like min/max, length, etc.
    ui_hints: Optional[UIHint] = None # For frontend rendering hints

class AssetRequirementModel(BaseModel):
    name: str # Argument name in the function signature
    type_hint_str: str # String representation of the type hint (e.g., "Pipette", "Optional[Plate]")
    actual_type_str: str # More refined type string, e.g. 'Pipette', 'Plate'
    optional: bool
    default_value_repr: Optional[str] = None # String representation of the default value, if any
    description: Optional[str] = None # Description of the asset's role
    constraints_json: Dict[str, Any] = Field(default_factory=dict) # ADDED FIELD

class FunctionProtocolDefinitionModel(BaseModel):
    # Core definition
    name: str
    version: str = "0.1.0"
    description: Optional[str] = None
    
    # Source information
    source_file_path: str # Relative path within the source
    module_name: str # e.g., my_protocols.transfer
    function_name: str # The actual Python function name
    
    # Link to source repository or filesystem (one of these should be set by DiscoveryService)
    source_repository_name: Optional[str] = None 
    commit_hash: Optional[str] = None
    file_system_source_name: Optional[str] = None

    # Execution behavior
    is_top_level: bool = False
    solo_execution: bool = False # Requires exclusive workcell access
    preconfigure_deck: bool = False # If deck needs specific setup from DeckConfigurationOrm
    deck_param_name: Optional[str] = None # Name of the parameter that receives the deck if preconfigure_deck=True
    state_param_name: Optional[str] = "state" # Name of the state parameter (PraxisState or dict)

    # Categorization and metadata
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    deprecated: bool = False

    # Derived from function signature and decorator
    parameters: List[ParameterMetadataModel] = Field(default_factory=list)
    assets: List[AssetRequirementModel] = Field(default_factory=list) # Assets inferred from type hints

    # db_id will be populated by ProtocolDiscoveryService after saving to FunctionProtocolDefinitionOrm
    db_id: Optional[int] = None 

    class Config:
        # For Pydantic v1:
        orm_mode = True 
        # For Pydantic v2, it would be:
        # from_attributes = True
        # However, stick to orm_mode if the project primarily uses Pydantic v1.
        # If pydantic is v2 and `Field` is from `pydantic.fields`, this should be fine.
        # If `Field` is from `pydantic.v1.fields`, then `orm_mode` is correct.
        # Assuming the `type: ignore` for pydantic import means it could be v1 or v2,
        # let's keep orm_mode for now as it's more common in slightly older codebases.
        # The worker can adjust if it knows the specific Pydantic version being used.
        validate_assignment = True # Useful for catching errors if attributes are modified post-init
