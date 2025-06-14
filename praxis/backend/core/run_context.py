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
import warnings
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

import uuid
from pydantic import BaseModel
from pylabrobot.resources import Deck, Resource
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.utils.state import State as PraxisState

PROTOCOL_REGISTRY: Dict[str, Any] = {}
DeckInputType = Union[str, os.PathLike, io.IOBase, Deck]

logger = logging.getLogger(__name__)


@dataclass
class PraxisRunContext:
  """Context for a Praxis protocol run.

  It is progressively updated as calls are nested.

  """

  # Identifiers for the overall run
  run_accession_id: (
    uuid.UUID
  )  # User-facing unique ID (e.g. UUID) of the ProtocolRunOrm entry

  # Core shared objects for the run
  canonical_state: PraxisState
  current_db_session: AsyncSession  # SQLAlchemy session

  # For call logging - these track the *current* state of the call stack
  # This is the FunctionCallLogOrm.accession_id of the *currently executing* function's log entry.
  # For the next nested call, this becomes the parent_function_call_log_db_accession_id.
  current_call_log_db_accession_id: Optional[uuid.UUID] = None

  # Sequence counter for calls within this run_accession_id
  # This should be managed carefully to ensure it's unique and ordered for a given run.
  _call_sequence_next_val: int = 1  # Internal counter, starts at 1

  # TODO: CTX-1: Consider if user_accession_id, workcell_accession_id, etc., should be here.

  def get_and_increment_sequence_val(self) -> int:
    """Return the current sequence value and then increment it for the next call."""
    current_val = self._call_sequence_next_val
    self._call_sequence_next_val += 1
    return current_val

  def create_context_for_nested_call(
    self, new_parent_call_log_db_accession_id: Optional[uuid.UUID]
  ) -> "PraxisRunContext":
    """Prepare context for a nested function call.

    Set `current_call_log_db_accession_id` to represent the
    log ID of the *calling* function, which will be the parent for the nested call.
    The sequence counter continues from the current context.

    Args:
      new_parent_call_log_db_accession_id: The ID of the FunctionCallLogOrm entry for the calling
      function.

    Returns:
      A new `PraxisRunContext` instance for the nested call, with the updated parent
      call log ID.

    """
    nested_ctx = PraxisRunContext(
      run_accession_id=self.run_accession_id,
      canonical_state=self.canonical_state,
      current_db_session=self.current_db_session,
      current_call_log_db_accession_id=new_parent_call_log_db_accession_id,
    )
    nested_ctx._call_sequence_next_val = self._call_sequence_next_val
    return nested_ctx


def serialize_arguments(args: tuple, kwargs: dict) -> str:
  """Serialize positional and keyword arguments to a JSON string."""
  try:

    def make_serializable(item):
      if isinstance(item, BaseModel):  # Check for Pydantic models
        try:
          return item.model_dump()  # Use Pydantic v2 style
        except AttributeError:
          pass  # Not a Pydantic model, proceed to other checks

      if isinstance(item, (PraxisRunContext, PraxisState)):
        return f"<{type(item).__name__} object>"
      if isinstance(item, (Resource, Deck)):  # PLR objects
        return repr(item)  # repr() often includes name and key details

      # Add other custom non-serializable types here if needed in the future
      return item

    cleaned_args = [make_serializable(arg) for arg in args]
    # Filter out __praxis_run_context__ from kwargs before serialization
    cleaned_kwargs = {
      k: make_serializable(v)
      for k, v in kwargs.items()
      if k != "__praxis_run_context__"
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
      {"args": [str(arg) for arg in args], "kwargs": cleaned_kwargs_fallback}
    )
