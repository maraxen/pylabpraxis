"""Custom exceptions and logging utility for Praxis backend."""

import logging
import traceback
from functools import wraps
from typing import Any, Callable, Type


class PraxisError(Exception):
  """Base exception for all custom Praxis backend errors.

  Attributes:
    message (str): The error message.

  """

  def __init__(self, message: str):
    """Initialize a new instance of the PraxisError.

    Args:
      message (str): The detailed error message.

    """
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    """Return the string representation of the error."""
    return f"{self.message}"


class OrchestratorError(Exception):
  """Exception raised for errors in the orchestrator service.

  Attributes:
    message (str): The error message.

  """

  def __init__(self, message: str):
    """Initialize a new instance of the OrchestratorError.

    Args:
      message (str): The detailed error message.

    """
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    """Return the string representation of the error."""
    return f"{self.message}"


class DataError(Exception):
  """Exception raised for errors during data operations (e.g., database interactions).

  Attributes:
    message (str): The error message.

  """

  def __init__(self, message: str):
    """Initialize a new instance of the DataError.

    Args:
      message (str): The detailed error message.

    """
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    """Return the string representation of the error."""
    return f"{self.message}"


class ModelError(Exception):
  """Exception raised for data models errors (e.g., validation, serialization).

  Attributes:
    message (str): The error message.

  """

  def __init__(self, message: str):
    """Initialize a new instance of the ModelError.

    Args:
      message (str): The detailed error message.

    """
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    """Return the string representation of the error."""
    return f"{self.message}"


class AssetAcquisitionError(RuntimeError):
  """Exception raised when there is an issue acquiring or assigning assets.

  Attributes:
    message (str): The error message.

  """

  def __init__(self, message: str):
    """Initialize a new instance of the AssetAcquisitionError.

    Args:
      message (str): The detailed error message.

    """
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    """Return the string representation of the error."""
    return f"{self.message}"


class ProtocolCancelledError(Exception):
  """Exception raised when a protocol run is explicitly cancelled.

  Attributes:
    message (str): The cancellation message.

  """

  def __init__(self, message: str = "Protocol run was cancelled."):
    """Initialize a new instance of the ProtocolCancelledError.

    Args:
      message (str): The detailed cancellation message.
        Defaults to "Protocol run was cancelled.".

    """
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    """Return the string representation of the error."""
    return f"{self.message}"


class WorkcellRuntimeError(Exception):
  """Exception raised for errors specific to the WorkcellRuntime.

  Attributes:
    message (str): The error message.

  """

  def __init__(self, message: str):
    """Initialize a new instance of the WorkcellRuntimeError.

    Args:
      message (str): The detailed error message.

    """
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    """Return the string representation of the error."""
    return f"{self.message}"


def _process_exception(
  logger_instance: logging.Logger,
  exception: Exception,
  exception_type: Type[Exception],
  raises: bool,
  raises_exception: Type[Exception],
  prefix: str,
  suffix: str,
  return_: Any,
) -> Any:
  """Process the exception to generate a custom error message."""
  error_message = f"{prefix}{exception.__class__.__name__}: \
    {str(exception)}{suffix}".strip()
  logger_instance.error(error_message)
  traceback.print_exc()
  full_error_message = f"{error_message} {traceback.format_exc()}"
  logger_instance.debug(full_error_message)
  if isinstance(exception, exception_type):
    if raises:
      raise raises_exception(full_error_message) from exception
  else:
    unexpected_error_message = (
      f"Unexpected error in {exception.__class__.__name__}: " f"{str(exception)[:250]}"
    )
    logger_instance.critical(unexpected_error_message)
    if raises:
      raise raises_exception(unexpected_error_message) from exception
  return return_


def log_async_runtime_errors(
  logger_instance: logging.Logger,
  exception_type: Type[Exception] = Exception,
  raises: bool = True,
  raises_exception: Type[Exception] = Exception,
  prefix: str = "",
  suffix: str = "",
  return_: Any = None,
) -> Callable:
  """Log specified exceptions in a function and optionally re-raise them.

  This decorator allows you to:
  - Specify which logger instance to use.
  - Define the specific type of exception to catch.
  - Control whether the caught exception is re-raised (as WorkcellRuntimeError).
  - Add a custom message to the error log.

  Args:
      logger_instance (logging.Logger): The logger instance to use for logging errors.
      exception_type (Type[Exception]): The type of exception to catch. Only exceptions
                                        of this type (or its subclasses) will be
                                        handled.
                                        Defaults to `Exception` (catches all).
      raises (bool): If True, the caught exception will be re-raised as a
                      `WorkcellRuntimeError`, preserving the original exception chain.
                      If False, the exception is suppressed, and the decorated function
                      will return `None` upon error. Defaults to True.
      raises_exception (Type[Exception]): The type of exception to raise if `raises` is
      True.
      prefix (str): An optional prefix to prepend to the generated error log
      entry.
      suffix (str): An optional suffix to append to the generated error log
      entry.
      return_ (Any): The value to return if an exception occurs and `raises` is False.

  Returns:
      Callable: The actual decorator function, which can then be applied to
                an `async` function.

  """

  def decorator(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
      try:
        return await func(*args, **kwargs)
      except Exception as e:
        _process_exception(
          logger_instance=logger_instance,
          exception=e,
          exception_type=exception_type,
          raises=raises,
          raises_exception=raises_exception,
          prefix=prefix,
          suffix=suffix,
          return_=return_,
        )

    return wrapper

  return decorator


def log_runtime_errors(
  logger_instance: logging.Logger,
  exception_type: Type[Exception] = Exception,
  raises: bool = True,
  raises_exception: Type[Exception] = Exception,
  prefix: str = "",
  suffix: str = "",
  return_: Any = None,
) -> Callable:
  """Log specified exceptions in a function and optionally re-raise them.

  This decorator allows you to:
  - Specify which logger instance to use.
  - Define the specific type of exception to catch.
  - Control whether the caught exception is re-raised (as WorkcellRuntimeError).
  - Add a custom message to the error log.

  Args:
      logger_instance (logging.Logger): The logger instance to use for logging errors.
      exception_type (Type[Exception]): The type of exception to catch. Only exceptions
                                        of this type (or its subclasses) will be
                                        handled.
                                        Defaults to `Exception` (catches all).
      raises (bool): If True, the caught exception will be re-raised as a
                      `WorkcellRuntimeError`, preserving the original exception chain.
                      If False, the exception is suppressed, and the decorated function
                      will return `None` upon error. Defaults to True.
      raises_exception (Type[Exception]): The type of exception to raise if `raises` is
      True.
      prefix (str): An optional prefix to prepend to the generated error log
      entry.
      suffix (str): An optional suffix to append to the generated error log
      entry.
      return_ (Any): The value to return if an exception occurs and `raises` is False.

  Returns:
      Callable: The actual decorator function, which can then be applied to
                a synchronous function.

  """

  def decorator(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
      try:
        return func(*args, **kwargs)
      except Exception as e:
        _process_exception(
          logger_instance=logger_instance,
          exception=e,
          exception_type=exception_type,
          raises=raises,
          raises_exception=raises_exception,
          prefix=prefix,
          suffix=suffix,
          return_=return_,
        )

    return wrapper

  return decorator
