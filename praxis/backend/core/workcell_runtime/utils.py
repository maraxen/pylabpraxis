"""Utility functions for WorkcellRuntime."""

import importlib


def get_class_from_fqn(class_fqn: str) -> type:
  """Import and return a class dynamically from its fully qualified name."""
  if not class_fqn or "." not in class_fqn:
    msg = "Invalid fully qualified class name: %s"
    raise ValueError(msg, class_fqn)
  module_name, class_name = class_fqn.rsplit(".", 1)
  imported_module = importlib.import_module(module_name)
  return getattr(imported_module, class_name)
