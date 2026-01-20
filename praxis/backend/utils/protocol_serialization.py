import cloudpickle
from typing import Any, Callable


def serialize_protocol_function(func: Callable) -> bytes:
  """
  Serializes a protocol function using cloudpickle.
  If the function is decorated (e.g. by Praxis @protocol decorator),
  it unwraps it to get the original function.
  """
  # Check for Praxis decorator markers or standard __wrapped__
  # We want the inner function that actually contains the logic
  # so that we don't try to pickle the backend-heavy decorators.
  if hasattr(func, "__wrapped__"):
    func = func.__wrapped__
  elif hasattr(func, "_protocol_definition"):
    # This is a specific Praxis marker, but usually @protocol
    # should also set __wrapped__ if using functools.wraps
    pass

  return cloudpickle.dumps(func)
