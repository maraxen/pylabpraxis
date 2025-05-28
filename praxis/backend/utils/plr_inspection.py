import inspect
from typing import Dict, List, Type

from pylabrobot.resources import Resource
from pylabrobot.machines import Machine


def get_all_resource_types() -> Dict[str, Type[Resource]]:
    """
    Get all available PyLabRobot resource types.
    Returns a dictionary with the class name as key and class as value.
    """
    from pylabrobot.resources import Resource

    # Get all Resource subclasses
    resource_types = {}

    # Recursive function to find all subclasses
    def get_all_subclasses(cls):
        all_subclasses = {}

        for subclass in cls.__subclasses__():
            all_subclasses[subclass.__name__] = subclass
            all_subclasses.update(get_all_subclasses(subclass))

        return all_subclasses

    resource_types = get_all_subclasses(Resource)
    return resource_types


def get_all_machine_types() -> Dict[str, Type[Machine]]:
    """
    Get all available PyLabRobot machine types.
    Returns a dictionary with the class name as key and class as value.
    """
    from pylabrobot.machines import Machine

    # Recursive function to find all subclasses
    def get_all_subclasses(cls):
        all_subclasses = {}

        for subclass in cls.__subclasses__():
            all_subclasses[subclass.__name__] = subclass
            all_subclasses.update(get_all_subclasses(subclass))

        return all_subclasses

    machine_types = get_all_subclasses(Machine)
    return machine_types


def get_resource_constructor_params(resource_class: Type[Resource]) -> Dict[str, Dict]:
    """
    Extract constructor parameters for a resource class.

    Returns:
        Dict with parameter name as key and parameter info as value.
        Parameter info includes type, required status, default value, and description.
    """
    sig = inspect.signature(resource_class.__init__)
    doc = inspect.getdoc(resource_class.__init__) or ""

    params = {}
    for name, param in sig.parameters.items():
        if name == "self":
            continue

        param_info = {
            "name": name,
            "type": (
                str(param.annotation)
                if param.annotation is not inspect.Parameter.empty
                else "Any"
            ),
            "required": param.default is inspect.Parameter.empty,
            "default": (
                None if param.default is inspect.Parameter.empty else param.default
            ),
            "description": "",  # We'll try to extract from docstring if available
        }

        # Try to extract description from docstring
        param_doc_match = [
            line
            for line in doc.split("\n")
            if f"{name}:" in line or f"{name} :" in line
        ]
        if param_doc_match:
            param_info["description"] = param_doc_match[0].split(":", 1)[1].strip()

        params[name] = param_info

    return params


def can_be_created_directly(resource_class: Type[Resource]) -> bool:
    """
    Determine if a resource can be created directly, or if it requires a parent.

    Generally, resources that would be placed directly on a deck can be created directly.
    Resources like Wells that would be children of other resources cannot.
    """
    # Check if parent is required in constructor
    constructor_params = get_resource_constructor_params(resource_class)

    # Resources that typically need parents will have parent as a required parameter
    if "parent" in constructor_params and constructor_params["parent"]["required"]:
        return False

    # Some specific cases
    if resource_class.__name__ in ["Well", "Tip", "Lid"]:
        return False

    return True


def get_machine_constructor_params(machine_class: Type[Machine]) -> Dict[str, Dict]:
    """
    Extract constructor parameters for a machine class.

    Returns:
        Dict with parameter name as key and parameter info as value.
        Parameter info includes type, required status, default value, and description.
    """
    sig = inspect.signature(machine_class.__init__)
    doc = inspect.getdoc(machine_class.__init__) or ""

    params = {}
    for name, param in sig.parameters.items():
        if name == "self":
            continue

        param_info = {
            "name": name,
            "type": (
                str(param.annotation)
                if param.annotation is not inspect.Parameter.empty
                else "Any"
            ),
            "required": param.default is inspect.Parameter.empty,
            "default": (
                None if param.default is inspect.Parameter.empty else param.default
            ),
            "description": "",  # We'll try to extract from docstring if available
        }

        # Try to extract description from docstring
        param_doc_match = [
            line
            for line in doc.split("\n")
            if f"{name}:" in line or f"{name} :" in line
        ]
        if param_doc_match:
            param_info["description"] = param_doc_match[0].split(":", 1)[1].strip()

        params[name] = param_info

    return params


def get_backend_types(machine_class: Type[Machine]) -> List[str]:
    """
    Get available backend types for a given machine class.
    """
    # This would need to be customized based on how PyLabRobot handles backends
    # For now, this is a simplified approach
    backends = []

    # Try to access a backend attribute if it exists
    backend_attr = getattr(machine_class, "BACKENDS", None) or getattr(
        machine_class, "backends", None
    )
    if backend_attr:
        if isinstance(backend_attr, dict):
            backends = list(backend_attr.keys())
        elif isinstance(backend_attr, list):
            backends = backend_attr

    return backends


def get_resource_hierarchy() -> Dict[str, List[str]]:
    """
    Build a hierarchy of resource types to help with UI organization.

    Returns:
        Dict with parent type as key and list of child types as value.
    """
    hierarchy = {}
    resource_types = get_all_resource_types()

    for name, cls in resource_types.items():
        parent_cls = cls.__base__
        parent_name = parent_cls.__name__

        if parent_name not in hierarchy:
            hierarchy[parent_name] = []

        hierarchy[parent_name].append(name)

    return hierarchy


def get_resource_metadata() -> Dict[str, Dict]:
    """
    Get comprehensive metadata about all resource types.

    Returns:
        Dict with resource name as key and metadata dict as value.
    """
    metadata = {}
    resource_types = get_all_resource_types()

    for name, cls in resource_types.items():
        metadata[name] = {
            "name": name,
            "parent_class": cls.__base__.__name__,
            "can_create_directly": can_be_created_directly(cls),
            "constructor_params": get_resource_constructor_params(cls),
            "doc": inspect.getdoc(cls) or "",
            "module": cls.__module__,
        }

    return metadata


def get_machine_metadata() -> Dict[str, Dict]:
    """
    Get comprehensive metadata about all machine types.

    Returns:
        Dict with machine name as key and metadata dict as value.
    """
    metadata = {}
    machine_types = get_all_machine_types()

    for name, cls in machine_types.items():
        metadata[name] = {
            "name": name,
            "parent_class": cls.__base__.__name__,
            "constructor_params": get_machine_constructor_params(cls),
            "backends": get_backend_types(cls),
            "doc": inspect.getdoc(cls) or "",
            "module": cls.__module__,
        }

    return metadata


def get_resource_categories() -> Dict[str, List[str]]:
    """
    Categorize resources to make them easier to navigate in the UI.
    """
    metadata = get_resource_metadata()
    categories = {
        "Containers": [],
        "Carriers": [],
        "Tips": [],
        "Plates": [],
        "Other": [],
    }

    for name, data in metadata.items():
        if "Plate" in name:
            categories["Plates"].append(name)
        elif "Carrier" in name:
            categories["Carriers"].append(name)
        elif "Tip" in name:
            categories["Tips"].append(name)
        elif "Container" in name or "Trough" in name:
            categories["Containers"].append(name)
        elif can_be_created_directly(get_all_resource_types()[name]):
            categories["Other"].append(name)

    return categories
