"""Logging utilities and decorators for error handling in PyLabPraxis."""

import logging
import traceback
from functools import wraps
from typing import Any, Callable, Type


def get_logger(name):  # TODO: change to use built-in logging.getLogger and config
  """Create and return a configured logger with stream handler."""
  logger = logging.getLogger(name)
  logger.setLevel(logging.DEBUG)
  formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
  ch = logging.StreamHandler()
  ch.setFormatter(formatter)
  logger.addHandler(ch)
  return logger


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
      f"Unexpected error in {exception.__class__.__name__}: {str(exception)[:250]}"
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
