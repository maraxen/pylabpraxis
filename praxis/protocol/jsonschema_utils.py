"""Utilities for generating JSONSchema from ProtocolParameters."""

from typing import Dict, Any, Type, get_origin, get_args, Union
import inspect
from .parameter import Parameter, ProtocolParameters


def _map_python_type_to_jsonschema(py_type: Type) -> str:
    """Map Python types to JSONSchema type strings.

    Args:
        py_type: The Python type to map

    Returns:
        The corresponding JSONSchema type string
    """
    # Handle Optional[T] and Union[T, None]
    origin = get_origin(py_type)
    if origin is Union:
        args = get_args(py_type)
        if type(None) in args:  # This is Optional[T]
            # Get the non-None type
            non_none_types = [t for t in args if t is not type(None)]
            if len(non_none_types) == 1:
                return _map_python_type_to_jsonschema(non_none_types[0])

    # Handle basic types
    if py_type is int:
        return "integer"
    elif py_type is float:
        return "number"
    elif py_type is str:
        return "string"
    elif py_type is bool:
        return "boolean"
    elif py_type is list:
        return "array"
    elif py_type is dict:
        return "object"
    elif inspect.isclass(py_type) and hasattr(py_type, "__name__"):
        # Handle custom classes - treat as object with additionalProperties
        return "object"
    else:
        # Default to string if type is unknown
        return "string"


def parameter_to_jsonschema_property(param: Parameter) -> Dict[str, Any]:
    """Convert a Parameter object to a JSONSchema property definition.

    Args:
        param: The Parameter instance to convert

    Returns:
        Dictionary representing the JSONSchema property
    """
    prop_schema: Dict[str, Any] = {
        "type": _map_python_type_to_jsonschema(param.datatype),
    }

    if param.description:
        prop_schema["description"] = param.description

    if param.default is not None:
        prop_schema["default"] = param.default

    # Handle constraints
    if param.constraints:
        if "min_value" in param.constraints:
            prop_schema["minimum"] = param.constraints["min_value"]
        if "max_value" in param.constraints:
            prop_schema["maximum"] = param.constraints["max_value"]
        if "allowed_values" in param.constraints:
            prop_schema["enum"] = param.constraints["allowed_values"]
        if "min_length" in param.constraints:
            prop_schema["minLength"] = param.constraints["min_length"]
        if "max_length" in param.constraints:
            prop_schema["maxLength"] = param.constraints["max_length"]
        if "pattern" in param.constraints:
            prop_schema["pattern"] = param.constraints["pattern"]

    # Handle Optional types by allowing null
    origin = get_origin(param.datatype)
    if origin is Union:
        args = get_args(param.datatype)
        if type(None) in args:
            if isinstance(prop_schema["type"], str):
                prop_schema["type"] = [prop_schema["type"], "null"]
            elif isinstance(prop_schema["type"], list):
                if "null" not in prop_schema["type"]:
                    prop_schema["type"].append("null")

    return prop_schema


# Asset schema definition
ASSET_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string"},
        "required": {"type": "boolean", "default": True},
        "description": {"type": "string"},
        "stackable": {"type": "boolean", "default": False},
        "needs_96_head": {"type": "boolean"},
        "requires_calibration": {"type": "boolean"},
        "deck_position": {"type": "string", "enum": ["front", "middle", "back"]},
        "carrier_compatibility": {"type": "array", "items": {"type": "string"}},
        "min_slots": {"type": "integer", "minimum": 1},
    },
    "required": ["type"],
}


def validate_protocol_config(config: dict) -> None:
    """Validate complete protocol configuration against schemas."""
    from jsonschema import validate

    # Validate parameters if present
    if "parameters" in config:
        param_schema = parameters_to_jsonschema(ProtocolParameters())
        validate(config["parameters"], param_schema)

    # Validate assets if present
    if "required_assets" in config:
        validate(config["required_assets"], ASSET_SCHEMA)


def parameters_to_jsonschema(
    params: ProtocolParameters,
    protocol_name: str = "Protocol",
    protocol_description: str = "",
) -> Dict[str, Any]:
    """Convert ProtocolParameters to a complete JSONSchema object.

    Args:
        params: The ProtocolParameters instance
        protocol_name: Name of the protocol (for title)
        protocol_description: Description of the protocol

    Returns:
        Complete JSONSchema dictionary
    """
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": protocol_name,
        "description": protocol_description,
        "type": "object",
        "properties": {},
        "required": [],
    }

    for param_name, param in params._parameters.items():
        schema["properties"][param_name] = parameter_to_jsonschema_property(param)
        if param.required and param.default is None:
            schema["required"].append(param_name)

    return schema
