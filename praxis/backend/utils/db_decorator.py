"""Database transaction decorator for handling session management."""

from functools import wraps
from typing import Awaitable, Callable, ParamSpec, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

P = ParamSpec("P")
R = TypeVar("R")


def handle_db_transaction(
  func: Callable[P, Awaitable[R]],
) -> Callable[P, Awaitable[R]]:
  """Decorator to manage database transactions in service layer methods.

  This decorator wraps an async function that takes a SQLAlchemy `AsyncSession`
  as its first argument. It ensures that the session is properly committed
  on success and rolled back on any exception.

  Args:
      func (Callable): The async function to be decorated.

  Returns:
      Callable: The wrapped async function with transaction management logic.

  Raises:
      Exception: Re-raises any exception that occurs within the decorated function
      after rolling back the transaction.

  """

  @wraps(func)
  async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
    """Wrap the function with transaction handling.

    Args:
        *args: Positional arguments passed to the decorated function.
        **kwargs: Keyword arguments passed to the decorated function.

    Returns:
        The return value of the decorated function.

    Raises:
        Exception: Re-raises any exception from the decorated function.

    """
    db_session_arg_index = -1
    for i, arg in enumerate(args):
      if isinstance(arg, AsyncSession):
        db_session_arg_index = i
        break

    if db_session_arg_index == -1 and "db" not in kwargs:
      msg = "Function decorated with @handle_db_transaction must have a 'db' argument."
      raise TypeError(
        msg,
      )

    db: AsyncSession = args[db_session_arg_index] if db_session_arg_index != -1 else kwargs["db"]
    try:
      result = await func(*args, **kwargs)
      await db.commit()
      return result
    except Exception:
      await db.rollback()
      raise

  return wrapper
