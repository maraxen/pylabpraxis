# praxis/backend/protocol/parameter.py
# Minimal placeholder for legacy classes to allow jsonschema_utils to be refactored.

from typing import Dict, Any, Type, Optional

class Parameter:
    def __init__(self, name: str, datatype: Type, default: Optional[Any] = None, description: Optional[str] = None, constraints: Optional[Dict[str, Any]] = None, required: bool = True):
        self.name = name
        self.datatype = datatype
        self.default = default
        self.description = description
        self.constraints = constraints or {}
        self.required = required if default is None else False # Required if no default

class ProtocolParameters:
    def __init__(self):
        self._parameters: Dict[str, Parameter] = {}

    def add_parameter(self, param: Parameter):
        self._parameters[param.name] = param
        
    # Add other methods if jsonschema_utils immediately needs them, but likely not for refactoring.
