# Standard Library Imports
import inspect
import warnings
from typing import (
  Any,
)

from pylabrobot.resources import Deck

from .runtime import (
  get_class_fqn,
  get_constructor_params_with_defaults,
)


def get_capabilities(class_obj: type[Any]) -> dict[str, Any]:
  """Extract capabilities from a PLR class (LiquidHandler or Backend).

  .. deprecated::
    Use :class:`praxis.backend.utils.plr_static_analysis.PLRSourceParser` instead.
    Static analysis provides more accurate capability extraction via AST analysis.

  """
  warnings.warn(
    "get_capabilities() is deprecated. Use PLRSourceParser for capability extraction instead.",
    DeprecationWarning,
    stacklevel=2,
  )
  capabilities: dict[str, Any] = {
    "channels": [],
    "modules": [],
    "is_backend": False,
  }

  # Heuristics for capabilities based on class name or attributes
  name = class_obj.__name__.lower()
  doc = inspect.getdoc(class_obj) or ""
  doc_lower = doc.lower()

  # Channels
  if "96" in name or "96" in doc_lower:
    capabilities["channels"].append(96)
  if "384" in name or "384" in doc_lower:
    capabilities["channels"].append(384)
  if "8" in name or "8" in doc_lower or "channels" in doc_lower:  # Basic assumption
    # Refine this: check for 'num_channels' attribute if instantiated, but we are static here
    pass

  # Modules
  if "swap" in name or "swap" in doc_lower:
    capabilities["modules"].append("swap")
  if "hepa" in name or "hepa" in doc_lower:
    capabilities["modules"].append("hepa")

  return capabilities


def get_deck_details(deck_class: type[Deck]) -> dict[str, Any]:
  """Return detailed info about a Deck class.

  Includes all position-to-location methods and their signatures.
  """
  details = {
    "fqn": get_class_fqn(deck_class),
    "constructor_args": get_constructor_params_with_defaults(deck_class),
    "assignment_methods": [],
    "category": getattr(deck_class, "category", None),
    "model": getattr(deck_class, "model", None),
  }

  # Find all *_to_location methods
  assignment_methods: list[dict[str, Any]] = []
  for name, method in inspect.getmembers(deck_class, inspect.isfunction):
    if name.endswith("_to_location"):
      sig = inspect.signature(method)
      params = [
        {
          "name": pname,
          "annotation": str(param.annotation),
          "default": (param.default if param.default is not inspect.Parameter.empty else None),
        }
        for pname, param in sig.parameters.items()
      ]
      assignment_methods.append(
        {
          "name": name,
          "signature": str(sig),
          "parameters": params,
          "doc": inspect.getdoc(method),
        },
      )

  details["assignment_methods"] = assignment_methods

  # Optionally, add more deck metadata here
  return details
