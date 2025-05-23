"""Utilities for generating JSONSchema from ProtocolParameters."""

from typing import Dict, Any, List, Optional, Union # get_origin, get_args not used in target
# Removed: import inspect
# Removed: from .parameter import Parameter, ProtocolParameters
from praxis.backend.protocol_core.protocol_definition_models import ParameterMetadataModel # UIHint not used
import json # For parsing default_value_repr

# Mapping of basic Python type strings (from ParameterMetadataModel.actual_type_str) to JSONSchema types
TYPE_STRING_MAP = {
    "int": "integer",
    "float": "number",
    "str": "string",
    "bool": "boolean",
    "list": "array", 
    "dict": "object",
    # Add more: e.g. for specific PLR resources if they have direct JSON representations
}

def _map_type_str_to_jsonschema(type_str: str, type_hint_str: Optional[str] = None) -> Union[str, Dict[str, Any]]:
    """Map Python type strings to JSONSchema type definitions."""

    # Basic mapping
    json_type_val = TYPE_STRING_MAP.get(type_str.lower(), "string") # Default to string

    # Handle generic types like List[int], Dict[str, Any] from type_hint_str if needed
    # For now, simple mapping. If type_hint_str is "List[int]", json_type is "array".
    # A more advanced version could set "items": {"type": "integer"}.
    # This example keeps it simple based on actual_type_str primarily.
    # Note: type_hint_str might be like "typing.List[int]" or just "List[int]"
    if type_str.lower().startswith("list"): # actual_type_str might be 'list' or 'List[...]'
        # Basic array, item type not deeply inspected here for simplicity for now
        return {"type": "array"} 
    if type_str.lower().startswith("dict"): # actual_type_str might be 'dict' or 'Dict[...]'
        # Basic object, property types not deeply inspected here
        return {"type": "object"}
        
    return {"type": json_type_val}


def parameter_model_to_jsonschema_property(param: ParameterMetadataModel) -> Dict[str, Any]:
    """Convert a ParameterMetadataModel object to a JSONSchema property definition."""
    prop_schema: Dict[str, Any] = _map_type_str_to_jsonschema(param.actual_type_str, param.type_hint_str)

    if param.description:
        prop_schema["description"] = param.description

    if param.default_value_repr is not None:
        try:
            # Attempt to parse the repr string back to a Python value
            # For simple types (int, float, bool, str, list, dict), json.loads might work if repr is valid JSON.
            # Or ast.literal_eval for more general Python literals.
            if param.actual_type_str in ["int", "float", "bool"]:
                 prop_schema["default"] = eval(param.default_value_repr) # Risky, but common for simple defaults
            elif param.actual_type_str == "str":
                 # repr of string includes quotes, e.g. "'my_string'"
                 # json.loads expects double quotes for strings
                 # A more robust way might be ast.literal_eval if it's a simple string literal
                 try:
                     prop_schema["default"] = json.loads(f'"{param.default_value_repr.strip(" ").strip("\'").strip("\\"")}"') # Attempt to make it valid JSON string
                 except json.JSONDecodeError:
                     prop_schema["default"] = param.default_value_repr.strip(" ").strip("'").strip('"') # Fallback: Basic unquoting
            elif param.actual_type_str in ["list", "dict"]:
                 prop_schema["default"] = json.loads(param.default_value_repr) # If default is valid JSON string
            # else: For other types, default_value_repr might be complex. Not setting JSON schema default.
        except (SyntaxError, json.JSONDecodeError, NameError, TypeError) as e: # Added TypeError
            print(f"Warning: Could not parse default_value_repr '{param.default_value_repr}' for param '{param.name}' into a JSON default: {e}")
            # Cannot set default if not easily parsable to JSON compatible value

    if param.constraints_json:
        # Map known constraint keys to JSONSchema keywords
        if "min_value" in param.constraints_json:
            prop_schema["minimum"] = param.constraints_json["min_value"]
        if "max_value" in param.constraints_json:
            prop_schema["maximum"] = param.constraints_json["max_value"]
        if "allowed_values" in param.constraints_json: # Custom 'allowed_values'
            prop_schema["enum"] = param.constraints_json["allowed_values"]
        if "min_length" in param.constraints_json:
            prop_schema["minLength"] = param.constraints_json["min_length"]
        if "max_length" in param.constraints_json:
            prop_schema["maxLength"] = param.constraints_json["max_length"]
        if "pattern" in param.constraints_json:
            prop_schema["pattern"] = param.constraints_json["pattern"]
        # Add other constraint mappings as needed

    if param.optional and param.default_value_repr is None: # Optional and no default means it can be omitted or explicitly null
        current_type_val = prop_schema.get("type")
        if isinstance(current_type_val, str): # e.g. "type": "string"
            prop_schema["type"] = [current_type_val, "null"]
        elif isinstance(current_type_val, list): # e.g. "type": ["string", "number"] (less common from our map)
            if "null" not in current_type_val: # pragma: no cover
                current_type_val.append("null")
        # This case handles when _map_type_str_to_jsonschema returns a dict like {"type": "array"}
        # And we need to make the *internal* type nullable.
        elif isinstance(current_type_val, dict) and "type" in current_type_val: 
             internal_type_val = current_type_val["type"]
             if isinstance(internal_type_val, str):
                 current_type_val["type"] = [internal_type_val, "null"]
             elif isinstance(internal_type_val, list) and "null" not in internal_type_val: # pragma: no cover
                 internal_type_val.append("null")
    return prop_schema

def definition_model_parameters_to_jsonschema(
    parameters: List[ParameterMetadataModel],
    protocol_name: str = "Protocol",
    protocol_description: str = ""
) -> Dict[str, Any]:
    """Convert a list of ParameterMetadataModel to a complete JSONSchema object."""
    schema: Dict[str, Any] = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": protocol_name,
        "description": protocol_description,
        "type": "object",
        "properties": {},
        # "required" list will be built based on param_model.optional
    }
    required_params: List[str] = []

    for param_model in parameters:
        schema["properties"][param_model.name] = parameter_model_to_jsonschema_property(param_model)
        if not param_model.optional:
            required_params.append(param_model.name)
            
    if required_params: # Only add 'required' key if there are any required params
        schema["required"] = required_params

    return schema

# Comment out or remove old/unused functions
# ASSET_SCHEMA = {
# "type": "object",
# "properties": {
# "type": {"type": "string"},
# "required": {"type": "boolean", "default": True},
# "description": {"type": "string"},
# "stackable": {"type": "boolean", "default": False},
# "needs_96_head": {"type": "boolean"},
# "requires_calibration": {"type": "boolean"},
# "deck_position": {"type": "string", "enum": ["front", "middle", "back"]},
# "carrier_compatibility": {"type": "array", "items": {"type": "string"}},
# "min_slots": {"type": "integer", "minimum": 1},
#     },
# "required": ["type"],
# }
#
# def validate_protocol_config(config: dict) -> None:
# """Validate complete protocol configuration against schemas."""
#     from jsonschema import validate
#
# # Validate parameters if present
#     if "parameters" in config:
# # This would need to be adapted if ProtocolParameters is removed.
# # For now, this function is effectively disabled by the refactor.
# # param_schema = parameters_to_jsonschema(ProtocolParameters()) # Old call
#         pass # Placeholder
# # validate(config["parameters"], param_schema)
#
# # Validate assets if present
#     if "required_assets" in config:
# # validate(config["required_assets"], ASSET_SCHEMA)
#         pass # Placeholder
