"""Utility functions for WorkcellRuntime."""

import importlib
from functools import partial

from praxis.backend.utils.errors import WorkcellRuntimeError
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

log_workcell_runtime_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  raises=True,
  raises_exception=WorkcellRuntimeError,
)


def get_class_from_fqn(class_fqn: str) -> type:
  """Import and return a class dynamically from its fully qualified name."""
  if not class_fqn or "." not in class_fqn:
    msg = "Invalid fully qualified class name: %s"
    raise ValueError(msg, class_fqn)
  module_name, class_name = class_fqn.rsplit(".", 1)
  imported_module = importlib.import_module(module_name)
  return getattr(imported_module, class_name)
