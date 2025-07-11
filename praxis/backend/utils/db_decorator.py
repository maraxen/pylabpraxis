"""Utility for managing database transactions in service layer methods."""

import functools
from collections.abc import Callable, Coroutine
from typing import Any, ParamSpec, TypeVar

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)
P = ParamSpec("P")
R = TypeVar("R")


def ensure_async_session(session: Any) -> AsyncSession:
  """Ensure the session is an AsyncSession."""
  if isinstance(session, AsyncSession):
    return session
  msg = "The decorated function must have a `db: AsyncSession` argument."
  raise TypeError(
    msg,
  )


def handle_db_transaction(
  func: Callable[P, Coroutine[Any, Any, R]],
) -> Callable[P, Coroutine[Any, Any, R]]:
  """Manage database transactions for service layer methods.

  Wrap a service method to provide automatic transaction
  handling (commit/rollback) and standardized exception handling. It ensures
  that the service layer remains decoupled from the web (HTTP) layer.
  """

  @functools.wraps(func)
  async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
    """Wrap the function to handle transactions."""
    db: AsyncSession | None = None
    _db: Any = None
    try:
      if "db" in kwargs:
        _db = kwargs["db"]
      else:
        arg_names = func.__code__.co_varnames[: func.__code__.co_argcount]
        if "db" in arg_names:
          db_index = arg_names.index("db")
          if db_index < len(args):
            _db = args[db_index]

      db = ensure_async_session(_db)

      result: R = await func(*args, **kwargs)
      await db.commit()
    except IntegrityError as e:
      if db:
        await db.rollback()
      logger.warning(
        "Database integrity error in %s: %s",
        func.__name__,
        e,
      )
      msg = (
        "A resource with this name or identifier already exists. "
        "Please choose a different name or identifier."
      )
      logger.exception(
        "Integrity error in %s",
        func.__name__,
      )
      raise ValueError(msg) from e
    except ValueError:
      # If it's already a ValueError, rollback and re-raise
      if db:
        await db.rollback()
      raise
    except TypeError as e:
      if db:
        await db.rollback()
      logger.exception(
        "Type error in %s",
        func.__name__,
      )
      msg = "Invalid input data provided."
      raise ValueError(msg) from e
    except Exception as e:
      if db:
        await db.rollback()
      logger.exception(
        "An unexpected error occurred in %s",
        func.__name__,
      )
      msg = "An unexpected internal error occurred."
      raise ValueError(msg) from e
    else:
      return result

  return wrapper
