from typing import Any, Optional, Union, List, Dict, Callable

class Parameter:
    def __init__(self, name: str, datatype: type, description: Optional[str] = None,
                 default: Optional[Any] = None, required: bool = True,
                 constraints: Optional[Dict[str, Any]] = None,
                 validation_func: Optional[Callable[[Any], bool]] = None):
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
            raise TypeError(f"Invalid data type for parameter '{self.name}'. Expected {self.datatype}, got {type(value)}.")

        # Check constraints
        for constraint_name, constraint_value in self.constraints.items():
            if constraint_name == "min_value":
                if value < constraint_value:
                    raise ValueError(f"Value for parameter '{self.name}' must be greater than or equal to {constraint_value}.")
            elif constraint_name == "max_value":
                if value > constraint_value:
                    raise ValueError(f"Value for parameter '{self.name}' must be less than or equal to {constraint_value}.")
            elif constraint_name == "allowed_values":
                if value not in constraint_value:
                    raise ValueError(f"Invalid value for parameter '{self.name}'. Allowed values are: {constraint_value}.")
            # Add more constraint checks as needed

        # Custom validation function
        if self.validation_func and not self.validation_func(value):
            raise ValueError(f"Value for parameter '{self.name}' failed custom validation.")

        return True

class ProtocolParameters:
    def __init__(self, parameters: Optional[Union[List[Parameter], Dict[str, Any]]] = None):
        self.parameters: Dict[str, Parameter] = {}

        if parameters:
            if isinstance(parameters, list):
                for param in parameters:
                    self.add_parameter(param)
            elif isinstance(parameters, dict):
                for param_name, param_details in parameters.items():
                    self.add_parameter_from_dict(param_name, param_details)

    def add_parameter(self, parameter: Parameter):
        """Adds a Parameter object to the collection."""
        self.parameters[parameter.name] = parameter

    def add_parameter_from_dict(self, param_name: str, param_details: Dict[str, Any]):
        """Adds a parameter from a dictionary."""
        datatype = param_details.get("datatype")
        description = param_details.get("description")
        default = param_details.get("default")
        required = param_details.get("required", True)
        constraints = param_details.get("constraints")
        validation_func = param_details.get("validation_func")

        parameter = Parameter(param_name, datatype, description, default, required, constraints, validation_func)
        self.add_parameter(parameter)

    def validate_parameters(self, input_parameters: Dict[str, Any]) -> bool:
        """
        Validates the given input parameters against the defined parameters.
        """
        # Check for missing required parameters
        for param_name, parameter in self.parameters.items():
            if parameter.required and param_name not in input_parameters:
                raise ValueError(f"Missing required parameter: {param_name}")

        # Validate each parameter
        for param_name, param_value in input_parameters.items():
            if param_name in self.parameters:
                self.parameters[param_name].validate(param_value)

        return True

    def get_parameter_info(self, param_name: str) -> Optional[Dict[str, Any]]:
        """
        Returns information about a parameter for the dashboard.
        """
        param = self.parameters.get(param_name)
        if param:
            return {
                "name": param.name,
                "datatype": str(param.datatype),
                "description": param.description,
                "default": param.default,
                "required": param.required,
                "constraints": param.constraints,
            }
        else:
            return None

    def get_parameters_for_ui(self) -> List[Dict[str, Any]]:
        """
        Returns a list of parameter information for the dashboard.
        """
        parameters_info = []
        for param_name, param in self.parameters.items():
            parameters_info.append({
                "name": param_name,
                "datatype": str(param.datatype),  # Convert type to string for easier handling in UI
                "description": param.description,
                "default": param.default,
                "required": param.required,
                "constraints": param.constraints,
            })
        return parameters_info
