import importlib
import inspect
from typing import List, Any, Dict, Optional, Union
from pydantic import BaseModel


class ArgumentInfo(BaseModel):
  name: str
  type: Optional[str] = None
  default: Optional[Any] = None


class MethodInfo(BaseModel):
  name: str
  doc: Optional[str] = None
  args: List[ArgumentInfo]


def inspect_machine_methods(fqn: str) -> List[MethodInfo]:
  """
  Inspects a class given its fully qualified name and returns a list of its public methods.
  Only allows classes within the 'pylabrobot' package for security.
  """
  if not fqn.startswith("pylabrobot."):
    raise ValueError(f"Access denied: '{fqn}' is not within 'pylabrobot' namespace.")

  try:
    module_name, class_name = fqn.rsplit(".", 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
  except (ImportError, AttributeError, ValueError) as e:
    raise ValueError(f"Could not load class '{fqn}': {str(e)}") from e

  if not inspect.isclass(cls):
    raise ValueError(f"'{fqn}' is not a class.")

  methods = []
  # Use inspect.getmembers with predicate to find methods (functions in the class)
  for name, member in inspect.getmembers(cls, predicate=inspect.isroutine):
    # Filter out private methods and methods inherited from 'object'
    if name.startswith("_"):
      continue

    # Check if the method is defined in 'object'
    if hasattr(object, name):
      continue

    try:
      sig = inspect.signature(member)
    except ValueError:
      # Some built-in methods might not have a signature
      continue

    args = []
    for param_name, param in sig.parameters.items():
      if param_name == "self":
        continue

      arg_type = None
      if param.annotation is not inspect.Parameter.empty:
        if hasattr(param.annotation, "__name__"):
          arg_type = param.annotation.__name__
        else:
          arg_type = str(param.annotation)

      default = None
      if param.default is not inspect.Parameter.empty:
        default = param.default
        # Basic JSON serialization check for default values
        try:
          import json

          json.dumps(default)
        except (TypeError, OverflowError):
          default = str(default)

      args.append(ArgumentInfo(name=param_name, type=arg_type, default=default))

    methods.append(MethodInfo(name=name, doc=inspect.getdoc(member), args=args))

  return methods
