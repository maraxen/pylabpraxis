from typing import Any, Optional, Union, List, Dict, Callable


class Parameter:
    def __init__(
        self,
        name: str,
        datatype: type,
        description: Optional[str] = None,
        default: Optional[Any] = None,
        required: bool = True,
        constraints: Optional[Dict[str, Any]] = None,
        validation_func: Optional[Callable[[Any], bool]] = None,
    ):
        self.name = name
        self.datatype = datatype
        self.description = description
        self.default = default
        self.required = required
        self.constraints = constraints if constraints else {}
        self.validation_func = validation_func

    def validate(self, value: Any) -> bool:
        """
        Validates the given value against the parameter's data type and constraints.
        """
        # Check data type
        if not isinstance(value, self.datatype):
            raise TypeError(
                f"Invalid data type for parameter '{self.name}'. Expected {self.datatype}, got {type(value)}."
            )

        # Check constraints
        for constraint_name, constraint_value in self.constraints.items():
            if constraint_name == "min_value":
                if value < constraint_value:
                    raise ValueError(
                        f"Value for parameter '{self.name}' must be greater than or equal to {constraint_value}."
                    )
            elif constraint_name == "max_value":
                if value > constraint_value:
                    raise ValueError(
                        f"Value for parameter '{self.name}' must be less than or equal to {constraint_value}."
                    )
            elif constraint_name == "allowed_values":
                if value not in constraint_value:
                    raise ValueError(
                        f"Invalid value for parameter '{self.name}'. Allowed values are: {constraint_value}."
                    )
            # Add more constraint checks as needed

        # Custom validation function
        if self.validation_func and not self.validation_func(value):
            raise ValueError(
                f"Value for parameter '{self.name}' failed custom validation."
            )

        return True


class ProtocolParameters:  # TODO: name safety
    def __init__(
        self, parameters: Optional[Union[List[Parameter], Dict[str, Any]]] = None
    ):
        self._parameters: Dict[str, Parameter] = {}
        self._values: Dict[str, Any] = {}
        self.initial_input: Optional[Union[List[Parameter], Dict[str, Any]]] = (
            parameters
        )

        if parameters:
            if isinstance(parameters, list):
                for param in parameters:
                    self.add_parameter(param)
            elif isinstance(parameters, dict):
                for param_name, param_details in parameters.items():
                    self.add_parameter_from_dict(param_name, param_details)

    def add_parameter(self, parameter: Parameter):
        """Add a parameter to the protocol parameters."""
        self._parameters[parameter.name] = parameter
        if parameter.default is not None:
            self._values[parameter.name] = parameter.default

    def add_parameter_from_dict(self, param_name: str, param_details: Dict[str, Any]):
        """Add a parameter from a dictionary specification."""
        param = Parameter(
            name=param_name,
            datatype=param_details.get("type", Any),
            description=param_details.get("description"),
            default=param_details.get("default"),
            required=param_details.get("required", True),
            constraints=param_details.get("constraints"),
            validation_func=param_details.get("validation_func"),
        )
        self.add_parameter(param)

    def validate_parameters(self, input_parameters: Dict[str, Any]) -> bool:
        """Validate input parameters against parameter specifications."""
        for param_name, param in self._parameters.items():
            if param.required and param_name not in input_parameters:
                if param.default is None:
                    raise ValueError(f"Required parameter '{param_name}' not provided.")
                value = param.default
            else:
                value = input_parameters.get(param_name, param.default)

            if value is not None:
                param.validate(value)
                self._values[param_name] = value

        return True

    def get(self, name: str, default: Any = None) -> Any:
        """Get a parameter value by name."""
        return self._values.get(name, default)

    def __getattr__(self, name: str) -> Any:
        """Support attribute-style access to parameter values."""
        if name in self._values:
            return self._values[name]
        raise AttributeError(f"Parameter '{name}' not found")

    def __setattr__(self, name: str, value: Any) -> None:
        """Support attribute-style setting of parameter values."""
        if name.startswith("_"):
            super().__setattr__(name, value)
            return

        if name in getattr(self, "_parameters", {}):
            self._parameters[name].validate(value)
            self._values[name] = value
        else:
            super().__setattr__(name, value)

    def get_parameter_info(self, param_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a parameter."""
        if param_name not in self._parameters:
            return None

        return self._param_info(param_name)

    def _param_info(self, param_name: str) -> Dict[str, Any]:
        """Get information about a parameter."""

        param = self._parameters[param_name]
        return {
            "name": param.name,
            "type": param.datatype,
            "description": param.description,
            "default": param.default,
            "required": param.required,
            "constraints": param.constraints,
            "current_value": self._values.get(param_name),
        }

    def serialize(self) -> Dict[str, Dict[str, Any]]:
        """Get parameter information formatted for UI display."""
        return {name: self._param_info(name) for name in self._parameters}
