# pylint: disable=too-few-public-methods,duplicate-code
"""Run context and serialization utilities for PylabPraxis protocol system.

Defines the `PraxisRunContext` class, which encapsulates the context for a protocol run,
including identifiers, shared objects, and call sequence management. Also provides
serialization utilities for arguments passed to protocol functions.
This module is part of the PylabPraxis protocol system.

praxis/protocol_core/definitions.py

Includes:

- `PraxisRunContext`: Context object for protocol runs, tracking identifiers, state, and
call logs.
- `serialize_arguments`: Utility to serialize function arguments (positional and
keyword) into a JSON string.
"""

import io
import json
import logging
import os
import uuid
import warnings
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel
from pylabrobot.resources import Deck, Resource
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.services.state import PraxisState

DeckInputType = str | os.PathLike | io.IOBase | Deck

logger = logging.getLogger(__name__)


@dataclass
class PraxisRunContext:
  """Context for a Praxis protocol run.

  It is progressively updated as calls are nested.

  """

  run_accession_id: uuid.UUID
  """Unique identifier for the protocol run."""
  canonical_state: PraxisState
  """Canonical state of the protocol run, shared across all calls."""
  current_db_session: AsyncSession
  """Current database session for the run, shared across all calls."""
  is_simulation: bool = False
  """Whether the current run is a simulation."""
  simulation_state: dict[str, Any] = None  # type: ignore[assignment]
  """Persistent state for browser-mode simulation.
  Shared across all contexts in a single run.
  """
  runtime: Any | None = None
  """Reference to the WorkcellRuntime instance for capturing snapshots."""
  current_call_log_db_accession_id: uuid.UUID | None = None
  """ID of the current function call log entry, if any.
  This is set to the ID of the FunctionCallLog entry for the currently executing function
  call, or None if not set.
  This is used to track the current call in the run context.
  If this is None, it indicates that the context is not currently associated with a specific
  function call log entry.
  """
  last_logged_state: dict[str, Any] | None = None
  """The last state snapshot that was logged (either before or after a call).
  Used to calculate diffs for subsequent logging entries.
  """
  _shared_run_data: dict[str, Any] = None  # type: ignore[assignment]
  """Internal dictionary shared across all nested contexts in a run.
  Used to hold mutable run-global data like the last logged state.
  """
  _call_sequence_next_val: int = 1
  """Internal counter for call sequence numbers.
  This is used to assign a unique sequence number to each function call within the run.
  It starts at 1 and increments with each call.
  This is used to track the order of function calls within the run context.
  It is not part of the public API and should not be modified directly.
  It is used internally to assign sequence numbers to function calls.
  """

  def __post_init__(self) -> None:
    if self._shared_run_data is None:
      self._shared_run_data = {}
    if self.simulation_state is None:
      self.simulation_state = {}

  def get_and_increment_sequence_val(self) -> int:
    """Return the current sequence value and then increment it for the next call."""
    current_val = self._call_sequence_next_val
    self._call_sequence_next_val += 1
    return current_val

  def get_simulation_state(self) -> dict[str, Any]:
    """Get the current simulation state dictionary."""
    return self.simulation_state

  def update_simulation_state(self, updates: dict[str, Any]) -> None:
    """Update the simulation state with new key-value pairs."""
    self.simulation_state.update(updates)

  def create_context_for_nested_call(
    self,
    new_parent_call_log_db_accession_id: uuid.UUID | None,
  ) -> "PraxisRunContext":
    """Prepare context for a nested function call.

    Set `current_call_log_db_accession_id` to represent the
    log ID of the *calling* function, which will be the parent for the nested call.
    The sequence counter continues from the current context.

    Args:
      new_parent_call_log_db_accession_id: The ID of the FunctionCallLog entry for the calling
      function.

    Returns:
      A new `PraxisRunContext` instance for the nested call, with the updated parent
      call log ID.

    """
    nested_ctx = PraxisRunContext(
      run_accession_id=self.run_accession_id,
      canonical_state=self.canonical_state,
      current_db_session=self.current_db_session,
      is_simulation=self.is_simulation,
      simulation_state=self.simulation_state,
      runtime=self.runtime,
      current_call_log_db_accession_id=new_parent_call_log_db_accession_id,
      _shared_run_data=self._shared_run_data,
    )
    nested_ctx._call_sequence_next_val = self._call_sequence_next_val
    return nested_ctx


def serialize_arguments(args: tuple, kwargs: dict) -> str:
  """Serialize positional and keyword arguments to a JSON string."""
  try:

    def make_serializable(item: Any) -> Any:
      if isinstance(item, BaseModel):  # Check for Pydantic models
        try:
          return item.model_dump()  # Use Pydantic v2 style
        except AttributeError:
          pass  # Not a Pydantic model, proceed to other checks

      if isinstance(item, PraxisRunContext | PraxisState):
        return f"<{type(item).__name__} object>"
      if isinstance(item, Resource | Deck):  # PLR objects
        return repr(item)  # repr() often includes name and key details

      # Add other custom non-serializable types here if needed in the future
      return item

    cleaned_args = [make_serializable(arg) for arg in args]
    # Filter out __praxis_run_context__ from kwargs before serialization
    cleaned_kwargs = {
      k: make_serializable(v) for k, v in kwargs.items() if k != "__praxis_run_context__"
    }

    return json.dumps({"args": cleaned_args, "kwargs": cleaned_kwargs}, default=str)

  except TypeError as e:  # pragma: no cover
    warning_message = (
      f"Warning: Could not fully serialize arguments due to TypeError: {e}."
      " Storing partial/string representation."
    )
    logger.warning(warning_message)
    warnings.warn(warning_message, UserWarning, stacklevel=2)
    cleaned_kwargs_fallback = {
      k: str(v) for k, v in kwargs.items() if k != "__praxis_run_context__"
    }
    return json.dumps(
      {"args": [str(arg) for arg in args], "kwargs": cleaned_kwargs_fallback},
    )
