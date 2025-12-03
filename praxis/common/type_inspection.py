# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements,fixme,logging-fstring-interpolation
"""Utilities for inspecting and serializing Python types."""

import inspect
from typing import Any, Union, get_args, get_origin


def is_pylabrobot_resource(type_str: str) -> bool:
    """Check if the given type string is a Pylabrobot Resource."""
    # This is a simplified check. A more robust implementation would involve
    # more sophisticated parsing of the type string.
    return "Plate" in type_str or "TipRack" in type_str or "Container" in type_str


def serialize_type_hint(type_hint: Any) -> str:
    """Serialize a type hint to a string representation."""
    if type_hint == inspect.Parameter.empty:
        return "Any"
    origin = get_origin(type_hint)
    args = get_args(type_hint)

    if origin is None:
        return getattr(type_hint, "__name__", str(type_hint))

    # Handle Union types, especially for Optional[T] which is Union[T, None]
    if origin is Union:
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            return f"typing.Optional[{serialize_type_hint(non_none_args[0])}]"
        return f"typing.Union[{', '.join(serialize_type_hint(arg) for arg in args)}]"

    # Handle generic collections like list, dict, etc.
    if hasattr(origin, "__name__"):
        origin_name = origin.__name__
        if args:
            args_repr = ", ".join(serialize_type_hint(arg) for arg in args)
            return f"{origin_name}[{args_repr}]"
        return origin_name

    # Fallback for other complex types
    if hasattr(type_hint, "__module__") and hasattr(type_hint, "__name__"):
        return f"{type_hint.__module__}.{type_hint.__name__}"

    return str(type_hint)
