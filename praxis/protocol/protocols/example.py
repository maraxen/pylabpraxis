"""
Example protocol for testing purposes
"""

from praxis.protocol.protocol import Protocol
from praxis.protocol.parameter import ProtocolParameters
from praxis.protocol.required_assets import WorkcellAssets

from pylabrobot.resources import Resource
from pylabrobot.machines import Machine

from typing import Any

from praxis.protocol.config import ProtocolConfiguration

baseline_parameters = ProtocolParameters(
    {
        "boolean_example": {
            "type": bool,
            "description": "An example of a boolean parameter",
            "default": False,
        },
        "unconstrained_array_example": {
            "type": list,
            "description": "A list of array values",
            "default": ["a", "b"],
        },
        "constrained_options_array_example": {
            "type": list,
            "description": "A list of array values",
            "default": ["a", "b"],
            "constraints": {"array": ["a", "b", "c"]},
        },
        "constrained_number_custom_array_example": {
            "type": list,
            "description": "An example of a custom array parameter",
            "default": 0,
            "constraints": {"array_len": 3},
        },
        "constrained_number_constrained_options_array_example": {
            "type": list,
            "description": "An example of a custom array parameter",
            "default": 0,
            "constraints": {"array_len": 3, "array": ["a", "b", "c", "d"]},
        },
        "single_choice_example": {
            "type": str,
            "description": "An example of a single choice parameter",
            "default": "a",
            "constraints": {"array": ["a", "b", "c"]},
        },
        "constrained_range_example": {
            "type": int,
            "description": "An example of a range-constrained parameter",
            "default": 0,
            "constraints": {"min_value": 0, "max_value": 10},
        },
        "integer_example": {
            "type": int,
            "description": "An example of an integer parameter",
            "default": 0,
        },
        "float_example": {
            "type": float,
            "description": "An example of a float parameter",
            "default": 0.0,
        },
        "constrained_float_example": {
            "type": float,
            "description": "An example of a constrained float parameter",
            "default": 0.5,
            "constraints": {"min_value": 0.0, "max_value": 1.0},
        },
        "tiny_step_float": {
            "type": float,
            "description": "An example of a float parameter with a tiny step",
            "default": 0.0,
            "constraints": {"step": 0.01},
        },
        "mapping_example_general": {
            "type": dict,
            "description": "An example of a mapping parameter",
            "default": {},
            "constraints": {"key_type": str, "value_type": int, "creatable": True},
        },
        "mapping_key_example": {
            "type": list,
            "description": "An example of a mapping key parameter",
            "default": ["a", "b"],
            "constraints": {"array": ["a", "b", "c"], "array_len": 3},
        },
        "mapping_value_example": {
            "type": list,
            "description": "An example of a mapping value parameter",
            "default": [1, 2],
            "constraints": {"array": [1, 2, 3], "array_len": 3},
        },
        "mapping_example_other_params": {
            "type": dict,
            "description": "An example of a mapping parameter",
            "default": {},
            "constraints": {
                "key_type": str,  # Use actual Python type
                "value_type": int,  # Use actual Python type
                "key_array": ["a", "b", "c"],
                "value_array": [1, 2, 3],
                "key_array_len": 3,
                "value_array_len": 3,
                "key_min_len": 1,
                "key_max_len": 10,
                "value_min_len": 1,
                "value_max_len": 10,
                "key_param": "mapping_key_example",
                "value_param": "mapping_value_example",
                "hierarchical": True,
                "parent": "key",
            },
        },
        "mapping_example": {
            "type": dict,
            "description": "An example of a one-to-one mapping parameter",
            "default": {"key1": "value1", "key2": "value2"},
            "constraints": {
                "key_type": "string",
                "value_type": "string",
                "key_array": ["key1", "key2", "key3"],
                "value_array": ["value1", "value2", "value3"],
            },
        },
        "array_mapping_example": {
            "type": dict,
            "description": "A mapping where each key maps to an array of values",
            "default": {},
            "constraints": {
                "key_type": "string",
                "value_type": "array",
                "key_array": ["group1", "group2", "group3"],
                "value_array": ["option1", "option2", "option3", "option4"],
                "key_array_len": 3,
                "value_array_len": 2,  # Max 2 values per key
                "creatable": True,
            },
        },
        "string_example": {
            "type": str,
            "description": "An example of a string parameter",
            "default": "",
        },
        "mapping_example_with_subvariables": {
            "type": dict,
            "description": "An example of a mapping parameter with subvariables",
            "default": {},
            "constraints": {
                "key_type": str,
                "value_type": dict,
                "key_array": ["key1", "key2", "key3"],
                "subvariables": {
                    "subvar1": {
                        "type": str,
                        "description": "Subvariable 1",
                        "default": "default1",
                        "constraints": {"array": ["option1", "option2"]},
                    },
                    "subvar2": {
                        "type": int,
                        "description": "Subvariable 2",
                        "default": 2,
                        "constraints": {"min_value": 1, "max_value": 10},
                    },
                    "subvar3": {
                        "type": float,
                        "description": "Subvariable 3",
                        "default": 3.0,
                        "constraints": {"min_value": 0.0, "max_value": 5.0},
                    },
                    "subvar4": {
                        "type": bool,
                        "description": "Subvariable 4",
                        "default": True,
                    },
                },
            },
        },
    }
)

required_assets = WorkcellAssets(
    {
        "example_resource": {"type": Resource, "description": "Example resource"},
        "example_machine": {"type": Machine, "description": "Example machine"},
    }
)


class Example(Protocol):
    def __init__(self, config: ProtocolConfiguration | dict[str, Any]):
        super().__init__(config)
        self.baseline_parameters = baseline_parameters

    async def execute(self):
        pass
