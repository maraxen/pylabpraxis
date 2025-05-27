# pylint: disable=too-few-public-methods,duplicate-code
"""
praxis/protocol_core/definitions.py

Core definitions, type aliases, and global registries for the PylabPraxis protocol system.
Version 4: Refines PraxisRunContext for better call sequence and parent tracking.
"""

import io
import os
from typing import Dict, Any, Union, Optional, TypeVar
from dataclasses import dataclass, field
import json
from pydantic import BaseModel # type: ignore
from pylabrobot.resources import Resource as PlrResource
from pylabrobot.resources import Deck as PlrDeck
from praxis.backend.utils.state import State as PraxisState

PROTOCOL_REGISTRY: Dict[str, Dict[str, Any]] = {}
DeckInputType = Union[str, os.PathLike, io.IOBase, PlrDeck]
@dataclass
class PraxisRunContext:
    """
    Context object passed through protocol function calls during an orchestrated run.
    It is progressively updated as calls are nested.
    """
    # Identifiers for the overall run
    protocol_run_db_id: int  # Integer PK of the ProtocolRunOrm entry
    run_guid: str            # User-facing unique ID (e.g. UUID) of the ProtocolRunOrm entry

    # Core shared objects for the run
    canonical_state: PraxisState
    current_db_session: Any  # SQLAlchemy session

    # For call logging - these track the *current* state of the call stack
    # This is the FunctionCallLogOrm.id of the *currently executing* function's log entry.
    # For the next nested call, this becomes the parent_function_call_log_db_id.
    current_call_log_db_id: Optional[int] = None

    # Sequence counter for calls within this run_guid
    # This should be managed carefully to ensure it's unique and ordered for a given run.
    _call_sequence_next_val: int = 1 # Internal counter, starts at 1

    # TODO: CTX-1: Consider if user_id, workcell_id, etc., should be here.

    def get_and_increment_sequence_val(self) -> int:
        """Returns the current sequence value and then increments it for the next call."""
        current_val = self._call_sequence_next_val
        self._call_sequence_next_val += 1
        return current_val

    def create_context_for_nested_call(self, new_parent_call_log_db_id: Optional[int]) -> 'PraxisRunContext':
        """
        Prepares a context object to be passed to a nested function call.
        The key change is setting the `current_call_log_db_id` to represent the
        log ID of the *calling* function, which will be the parent for the nested call.
        The sequence counter continues from the current context.
        """
        # The `current_function_definition_db_id` is specific to the function being called,
        # so it's not part of this shared context object but rather retrieved from metadata
        # by the wrapper of the function being called.
        nested_ctx = PraxisRunContext(
            protocol_run_db_id=self.protocol_run_db_id,
            run_guid=self.run_guid,
            canonical_state=self.canonical_state,
            current_db_session=self.current_db_session,
            current_call_log_db_id=new_parent_call_log_db_id # This IS the parent for the *next* call
        )
        # The sequence counter is effectively shared by managing it through this method
        nested_ctx._call_sequence_next_val = self._call_sequence_next_val
        return nested_ctx


def serialize_arguments(args: tuple, kwargs: dict) -> str:
    """Serializes positional and keyword arguments to a JSON string."""
    try:
        def make_serializable(item):
            if isinstance(item, BaseModel): # Check for Pydantic models first
                try:
                    return item.dict() # Pydantic v1 style
                except AttributeError: # Fallback for Pydantic v2 or if .dict() is not available
                    try:
                        return item.model_dump() # Pydantic v2 style
                    except AttributeError:
                        pass # Not a Pydantic model with dict/model_dump, proceed to other checks
            
            if isinstance(item, (PraxisRunContext, PraxisState)): # Context/State should ideally not be logged as simple args
                return f"<{type(item).__name__} object>"
            if isinstance(item, (PlrResource, PlrDeck)): # PLR objects
                return repr(item) # repr() often includes name and key details
            
            # Add other custom non-serializable types here if needed in the future
            return item

        cleaned_args = [make_serializable(arg) for arg in args]
        # Filter out __praxis_run_context__ from kwargs before serialization
        cleaned_kwargs = {k: make_serializable(v) for k, v in kwargs.items() if k != '__praxis_run_context__'}

        return json.dumps({"args": cleaned_args, "kwargs": cleaned_kwargs}, default=str)
    except TypeError as e: # pragma: no cover
        print(f"Warning: Could not fully serialize arguments due to TypeError: {e}. Storing partial/string representation.")
        # Fallback serialization: convert everything to string
        cleaned_kwargs_fallback = {k: str(v) for k, v in kwargs.items() if k != '__praxis_run_context__'}
        return json.dumps({"args": [str(arg) for arg in args], "kwargs": cleaned_kwargs_fallback})


# Example Placeholder Asset Types
# TODO: ASSET-1: Replace with actual implementations or imports from the relevant modules.
# These are just placeholders to illustrate the concept.
class Pipette(PlrResource):
    def __init__(self, name: str, num_channels: int = 1, **kwargs): super().__init__(name=name, **kwargs); self.num_channels = num_channels
    def aspirate(self, volume: float, location: Any = None): print(f"{self.name} aspirating {volume}uL" + (f" from {location}" if location else ""))
    def dispense(self, volume: float, location: Any = None): print(f"{self.name} dispensing {volume}uL" + (f" to {location}" if location else ""))
    def __repr__(self): return f"Pipette(name='{self.name}', num_channels={self.num_channels})"
class Plate(PlrResource):
    def __init__(self, name: str, num_wells: int = 96, **kwargs): super().__init__(name=name, **kwargs); self.num_wells = num_wells
    def get_well(self, well_name: str) -> Any: print(f"{self.name} getting well {well_name}"); return f"Well_{well_name}"
    def __repr__(self): return f"Plate(name='{self.name}', num_wells={self.num_wells})"
class HeaterShaker(PlrResource):
    def set_temperature(self, temp_celsius: float): print(f"{self.name} setting temp to {temp_celsius}°C")
    def set_shake_rpm(self, rpm: int): print(f"{self.name} setting shake to {rpm} RPM")
    def __repr__(self): return f"HeaterShaker(name='{self.name}')"

