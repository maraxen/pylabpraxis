"""
Utilities for inspecting PyLabRobot resources and machines.
"""

# Standard Library Imports
import inspect
import importlib
import pkgutil
import logging
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
    Union,
    Set,
    Tuple,
    Callable,
    get_type_hints,
)


# PyLabRobot Imports
from pylabrobot.resources import (
    Deck as PlrDeck,
    Resource as PlrResource,
    ResourceHolder,
)
from pylabrobot.machines.machine import Machine as PlrMachine
from pylabrobot.resources.coordinate import Coordinate
from pylabrobot.resources.carrier import (
    Carrier,
    PlateCarrier,
    TipCarrier,
    TroughCarrier,
)

from pylabrobot.resources.plate import Plate
from pylabrobot.resources.tip_rack import TipRack
from pylabrobot.resources.trough import Trough

logger = logging.getLogger(__name__)


def get_class_fqn(klass: Type[Any]) -> str:
    """Get the fully qualified name of a class."""
    return f"{klass.__module__}.{klass.__name__}"


def get_module_classes(
    module: Any, parent_class: Optional[Type[Any]] = None, concrete_only: bool = False
) -> Dict[str, Type[Any]]:
    """
    Get all classes from a module that are subclasses of parent_class.

    Args:
        module: The module to inspect.
        parent_class: The parent class to filter by. If None, all classes are returned.
        concrete_only: If True, only return non-abstract classes.

    Returns:
        A dictionary of class names to class objects.
    """
    classes = {}
    for name, obj in inspect.getmembers(module, inspect.isclass):
        if parent_class and not issubclass(obj, parent_class):
            continue
        # Ensure the class is defined in the module itself, not just imported.
        if obj.__module__ != module.__name__ and not obj.__module__.startswith(
            module.__name__ + "."
        ):
            # Allow classes from submodules of the given module if module is a package root
            is_submodule_class = False
            if hasattr(module, "__path__"):  # Check if module is a package
                for importer, modname, ispkg in pkgutil.iter_modules(
                    module.__path__, module.__name__ + "."
                ):
                    if obj.__module__.startswith(modname):
                        is_submodule_class = True
                        break
            if not is_submodule_class:
                continue

        if concrete_only and inspect.isabstract(obj):
            continue
        classes[name] = obj
    return classes


def get_constructor_params_with_defaults(
    klass: Type[Any], required_only: bool = False
) -> Dict[str, Any]:
    """
    Get the constructor parameters and their default values for a class.

    Args:
        klass: The class to inspect.
        required_only: If True, only return parameters without default values.

    Returns:
        A dictionary of parameter names to their default values
        (or inspect.Parameter.empty if no default).
    """
    params = {}
    try:
        signature = inspect.signature(klass.__init__)
        for name, param in signature.parameters.items():
            if name == "self" or name == "args" or name == "kwargs":
                continue
            if required_only and param.default is not inspect.Parameter.empty:
                continue
            params[name] = param.default
    except Exception as e:
        logger.error(f"Error inspecting constructor for {get_class_fqn(klass)}: {e}")
    return params


def is_resource_subclass(item_class: Type[Any]) -> bool:
    """Check if a class is a non-abstract subclass of pylabrobot.resources.Resource."""
    return (
        inspect.isclass(item_class)
        and issubclass(item_class, PlrResource)
        and not inspect.isabstract(item_class)
        and item_class is not PlrResource
    )


def is_machine_subclass(item_class: Type[Any]) -> bool:
    """Check if a class is a non-abstract subclass of pylabrobot.machines.machine.Machine."""
    return (
        inspect.isclass(item_class)
        and issubclass(item_class, PlrMachine)
        and not inspect.isabstract(item_class)
        and item_class is not PlrMachine
    )


def is_deck_subclass(item_class: Type[Any]) -> bool:
    """Check if a class is a non-abstract subclass of pylabrobot.resources.Deck."""
    return (
        inspect.isclass(item_class)
        and issubclass(item_class, PlrDeck)
        and not inspect.isabstract(item_class)
        and item_class is not PlrDeck  # Exclude the base Deck class itself
    )


def _discover_classes_in_module_recursive(
    module_name: str,
    parent_class: Optional[Type[Any]],
    concrete_only: bool,
    visited_modules: Set[str],
) -> Dict[str, Type[Any]]:
    """
    Recursively discover classes in a module and its submodules.
    """
    if module_name in visited_modules:
        return {}
    visited_modules.add(module_name)

    found_classes: Dict[str, Type[Any]] = {}
    try:
        module = importlib.import_module(module_name)
        classes_in_module = get_module_classes(module, parent_class, concrete_only)
        for klass_name, klass in classes_in_module.items():
            if klass.__module__.startswith(
                module_name
            ):  # Check it's defined in or under this module path
                found_classes[get_class_fqn(klass)] = klass

        if hasattr(module, "__path__"):
            for _, sub_module_name, _ in pkgutil.walk_packages(
                module.__path__, module_name + "."
            ):
                if sub_module_name not in visited_modules:
                    found_classes.update(
                        _discover_classes_in_module_recursive(
                            sub_module_name,
                            parent_class,
                            concrete_only,
                            visited_modules,
                        )
                    )
    except ImportError as e:
        logger.warning(f"Could not import module {module_name}: {e}")
    except Exception as e:
        logger.error(f"Error processing module {module_name}: {e}")
    return found_classes


def get_all_plr_classes(
    base_module_names: Union[str, List[str]] = "pylabrobot",
    parent_class: Optional[Type[Any]] = None,
    concrete_only: bool = False,
) -> Dict[str, Type[Any]]:
    """
    Get all PyLabRobot classes from base module(s) and their submodules.
    """
    all_classes: Dict[str, Type[Any]] = {}
    visited_modules: Set[str] = set()
    module_list = (
        [base_module_names] if isinstance(base_module_names, str) else base_module_names
    )
    for base_module_name in module_list:
        all_classes.update(
            _discover_classes_in_module_recursive(
                base_module_name, parent_class, concrete_only, visited_modules
            )
        )
    return all_classes


def get_all_plr_resource_classes(
    concrete_only: bool = True,
) -> Dict[str, Type[PlrResource]]:
    return get_all_plr_classes(  # type: ignore
        base_module_names=[
            "pylabrobot.resources",
            "pylabrobot.liquid_handling.resources",
        ],
        parent_class=PlrResource,
        concrete_only=concrete_only,
    )


def get_all_plr_machine_classes(
    concrete_only: bool = True,
) -> Dict[str, Type[PlrMachine]]:
    return get_all_plr_classes(  # type: ignore
        base_module_names="pylabrobot.machines",
        parent_class=PlrMachine,
        concrete_only=concrete_only,
    )


def get_all_plr_deck_classes(concrete_only: bool = True) -> Dict[str, Type[PlrDeck]]:
    all_decks = get_all_plr_classes(  # type: ignore
        base_module_names=[
            "pylabrobot.resources",
            "pylabrobot.liquid_handling.resources",
        ],
        parent_class=PlrDeck,
        concrete_only=concrete_only,
    )
    return {
        fqn: deck_class
        for fqn, deck_class in all_decks.items()
        if deck_class is not PlrDeck
    }


# --- Phase 1: Enhanced PyLabRobot Deck and General Asset Introspection ---


def discover_plr_deck_classes(
    packages: Union[str, List[str]] = "pylabrobot.resources",
) -> Dict[str, Type[PlrDeck]]:
    """
    Discovers all non-abstract PLR Deck subclasses within the specified Python package(s).
    """
    package_list = [packages] if isinstance(packages, str) else list(packages)
    discovered_deck_classes: Dict[str, Type[PlrDeck]] = {}
    visited_modules: Set[str] = set()
    for package_name in package_list:
        try:
            deck_classes_in_pkg = _discover_classes_in_module_recursive(
                package_name,
                PlrDeck,
                concrete_only=True,
                visited_modules=visited_modules,
            )
            for fqn, deck_class in deck_classes_in_pkg.items():
                if issubclass(deck_class, PlrDeck) and deck_class is not PlrDeck:
                    discovered_deck_classes[fqn] = deck_class  # type: ignore
        except ImportError:
            logger.warning(f"Package {package_name} not found during deck discovery.")
        except Exception as e:
            logger.error(
                f"Error discovering deck classes in package {package_name}: {e}"
            )
    return discovered_deck_classes


def _get_accepted_categories_for_resource_holder(
    holder: ResourceHolder, parent_carrier: Optional[Carrier] = None
) -> List[str]:
    """
    Helper to determine accepted resource categories for a ResourceHolder.
    Infers based on the type of the holder or its parent carrier.
    """
    accepted_categories: List[str] = []

    # Check the parent carrier first, as it's often more specific
    if parent_carrier:
        if isinstance(parent_carrier, PlateCarrier):
            accepted_categories.append("Plate")
        elif isinstance(parent_carrier, TipCarrier):
            accepted_categories.append("TipRack")
        elif isinstance(parent_carrier, TroughCarrier):  # Added TroughCarrier check
            accepted_categories.append("Trough")
        # Add other specific carrier types here if needed

    # If no specific parent carrier type, or if it's a direct holder, check holder type
    if not accepted_categories:
        if isinstance(holder, PlateCarrier):
            accepted_categories.append("Plate")
        elif isinstance(holder, TipCarrier):
            accepted_categories.append("TipRack")
        elif isinstance(holder, TroughCarrier):  # Added TroughCarrier check
            accepted_categories.append("Trough")
        elif isinstance(holder, Trough):  # Troughs are ResourceHolders
            accepted_categories.append("Trough")
        # Heuristic: If the holder's class name suggests a type
        elif (
            "Plate" in holder.__class__.__name__ and "Plate" not in accepted_categories
        ):
            accepted_categories.append("Plate")
        elif (
            "Tip" in holder.__class__.__name__ and "TipRack" not in accepted_categories
        ):
            accepted_categories.append("TipRack")

    # Fallback if no specific category could be inferred
    if not accepted_categories:
        accepted_categories.append("Resource")  # General resource

    return list(set(accepted_categories))  # Unique categories


def _get_method_signature_details(method: Callable) -> Dict[str, Any]:
    """Helper to get details of a method's signature."""
    sig_details: Dict[str, Any] = {"name": method.__name__, "parameters": []}
    try:
        signature = inspect.signature(method)
        type_hints = get_type_hints(method)  # Get resolved type hints

        for name, param in signature.parameters.items():
            param_info = {
                "name": name,
                "annotation": str(
                    type_hints.get(name, param.annotation)
                ),  # Use resolved hint
                "default": param.default
                if param.default is not inspect.Parameter.empty
                else "REQUIRED",
            }
            sig_details["parameters"].append(param_info)
    except (
        ValueError,
        TypeError,
    ) as e:  # ValueError for methods like builtins, TypeError for unresolveable hints
        logger.warning(
            f"Could not get signature or type hints for method {method.__name__}: {e}"
        )
        sig_details["error"] = str(e)
    return sig_details


def get_plr_deck_details(deck_class: Type[PlrDeck]) -> Dict[str, Any]:
    """
    Extracts detailed information about a PLR Deck subclass.
    """
    details: Dict[str, Any] = {"fqn": get_class_fqn(deck_class)}
    details["constructor_args"] = get_constructor_params_with_defaults(deck_class)

    deck_instance: Optional[PlrDeck] = None
    temp_deck_name = f"temp_inspection_{deck_class.__name__}"

    try:
        # Attempt instantiation (simplified for now, may need refinement for complex constructors)
        required_params = get_constructor_params_with_defaults(
            deck_class, required_only=True
        )
        if not required_params or list(required_params.keys()) == ["name"]:
            deck_instance = deck_class(name=temp_deck_name)
        elif "name" in inspect.signature(deck_class.__init__).parameters:
            logger.warning(
                f"Deck class {details['fqn']} has required constructor parameters "
                f"other than 'name': {required_params}. Attempting instantiation with only 'name'. "
                f"This might provide incomplete default layout info."
            )
            deck_instance = deck_class(name=temp_deck_name)
        else:  # Cannot satisfy constructor easily
            logger.error(
                f"Cannot auto-instantiate deck {details['fqn']} due to complex constructor: {required_params}"
            )
            raise ValueError(f"Complex constructor for {details['fqn']}")

        details["serialized_properties"] = deck_instance.serialize()
        details["category"] = deck_instance.category
        details["model"] = getattr(deck_instance, "model", None)
        details["default_size_x_mm"] = deck_instance.get_size_x()
        details["default_size_y_mm"] = deck_instance.get_size_y()
        details["default_size_z_mm"] = deck_instance.get_size_z()
        details["slots"] = details.get("slots", [])

    except Exception as e:
        logger.error(
            f"Could not instantiate or fully inspect deck {details['fqn']}: {e}"
        )
        details["serialized_properties"] = None
        details["category"] = "deck"
        details["model"] = None
        details["default_size_x_mm"] = None
        details["default_size_y_mm"] = None
        details["default_size_z_mm"] = None
        details["slots"] = []  # Ensure slots key exists

    # Deck Assignment Interface Inspection
    assignment_methods_info: List[Dict[str, Any]] = []
    # Look for 'assign_child_resource' and common overrides/alternatives.
    # This list can be expanded based on PLR conventions.
    potential_assignment_method_names = [
        "assign_child_resource",
        "add_resource",
        "assign_resource",
        "add_plate",
        "add_tip_rack",
        "assign_to_slot",
        "assign_to_rail",
    ]
    for method_name, method_obj in inspect.getmembers(deck_class, inspect.isfunction):
        if method_name in potential_assignment_method_names:
            # Ensure it's a method defined in this class or its PLR base, not from object or too far up MRO
            if (
                method_name in deck_class.__dict__
                or (
                    hasattr(PlrDeck, method_name)
                    and getattr(deck_class, method_name)
                    == getattr(PlrDeck, method_name)
                )
                or any(
                    method_name in base_cls.__dict__
                    for base_cls in deck_class.__mro__
                    if issubclass(base_cls, PlrDeck)
                )
            ):
                assignment_methods_info.append(
                    _get_method_signature_details(method_obj)
                )
    details["assignment_methods_info"] = assignment_methods_info

    # Constructor Layout Hints (Heuristic)
    # Analyzing constructor_args for patterns suggesting layout elements
    constructor_layout_hints = {}
    for param_name, default_value in details["constructor_args"].items():
        if (
            "rail" in param_name
            or "num_slots" == param_name
            or "slot_names" == param_name
        ):
            constructor_layout_hints[param_name] = str(
                default_value
            )  # Store as string for JSON
    details["constructor_layout_hints"] = constructor_layout_hints

    return details


def get_plr_asset_details(asset_fqn: str) -> Dict[str, Any]:
    """
    Extracts details for any PLR Resource or Machine FQN.
    """
    properties: Dict[str, Any] = {"fqn": asset_fqn}
    try:
        module_name, class_name = asset_fqn.rsplit(".", 1)
        module = importlib.import_module(module_name)
        asset_class = getattr(module, class_name)
        instance = None

        if not inspect.isclass(asset_class):
            logger.error(f"{asset_fqn} is not a class.")
            return {"fqn": asset_fqn, "error": "Not a class."}

        constructor_params_for_asset = get_constructor_params_with_defaults(asset_class)

        if issubclass(asset_class, PlrResource):
            try:
                required_params = get_constructor_params_with_defaults(
                    asset_class, required_only=True
                )
                if not required_params or list(required_params.keys()) == ["name"]:
                    instance = asset_class(
                        name=f"temp_inspect_{class_name}", **required_params
                    )
                elif (
                    "name" in constructor_params_for_asset
                ):  # Try with name if other required exist
                    instance = asset_class(
                        name=f"temp_inspect_{class_name}", **required_params
                    )
                else:  # Attempt default instantiation if no 'name' and no other required args
                    if not required_params:
                        instance = asset_class(**required_params)
                    else:
                        raise ValueError(
                            f"Complex constructor with required params: {required_params}"
                        )
            except Exception as e:
                logger.warning(
                    f"Failed to instantiate PLR Resource {asset_fqn} simply: {e}. Params: {constructor_params_for_asset}"
                )

        elif issubclass(asset_class, PlrMachine):  # TODO: improve this flow
            try:
                # Simplified machine instantiation for inspection
                if (
                    "backend" in constructor_params_for_asset
                    and "name" in constructor_params_for_asset
                ):
                    instance = asset_class(
                        name=f"temp_inspect_{class_name}",  # type: ignore
                        backend=None,  # type: ignore
                    )
                else:
                    instance = asset_class(backend=None)  # type: ignore
            except Exception as e:
                logger.warning(
                    f"Failed to instantiate PLR Machine {asset_fqn} simply: {e}. Params: {constructor_params_for_asset}"
                )
        else:
            logger.warning(
                f"{asset_fqn} is not a recognized PLR Resource or Machine subclass."
            )
            return {"fqn": asset_fqn, "error": "Not a PLR Resource or Machine."}

        if instance:
            try:
                if hasattr(instance, "serialize") and callable(instance.serialize):
                    properties.update(instance.serialize())  # type: ignore
                # Ensure common properties are present
                properties["name"] = getattr(
                    instance, "name", f"temp_inspect_{class_name}"
                )
                properties["category"] = getattr(instance, "category", None)
                properties["model"] = getattr(instance, "model", None)
                if isinstance(instance, PlrResource):
                    properties["size_x"] = instance.get_size_x()
                    properties["size_y"] = instance.get_size_y()
                    properties["size_z"] = instance.get_size_z()
            except Exception as e:
                logger.error(
                    f"Error during serialization/property extraction for {asset_fqn}: {e}"
                )
                properties["serialization_error"] = str(e)
        else:
            properties["instantiation_error"] = (
                f"Could not create an instance of {asset_fqn} for detail extraction. Constructor params: {constructor_params_for_asset}"
            )

    except ImportError:
        return {"fqn": asset_fqn, "error": "Module not found."}
    except AttributeError:
        return {"fqn": asset_fqn, "error": "Class not found in module."}
    except Exception as e:
        return {"fqn": asset_fqn, "error": f"Unexpected error: {e}"}
    return properties
