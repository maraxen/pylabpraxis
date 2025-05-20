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

# Attempt to import PyLabRobot base classes and PraxisState.
try:
    from pylabrobot.resources import Resource as PlrResource
    from pylabrobot.resources import Deck as PlrDeck
except ImportError:
    print("Warning: PyLabRobot classes (Resource, Deck) not found. Using placeholders for type hinting.")
    class PlrResource: # type: ignore
        """Placeholder for pylabrobot.resources.Resource."""
        def __init__(self, name: str, **kwargs):
            self.name = name
            for key, value in kwargs.items():
                setattr(self, key, value)
        def __repr__(self): return f"PlrResource(name='{self.name}')"

    class PlrDeck(PlrResource): # type: ignore
        """Placeholder for pylabrobot.resources.Deck."""
        def __init__(self, name: str = "deck", **kwargs): super().__init__(name=name, **kwargs)
        def __repr__(self): return f"PlrDeck(name='{self.name}')"

try:
    from praxis.utils.state import State as PraxisState
except ImportError:
    print("Warning: praxis.utils.state.State (PraxisState) not found. Using placeholder.")
    @dataclass
    class PraxisState: # type: ignore
        """Placeholder for praxis.utils.state.State."""
        data: Dict[str, Any] = field(default_factory=dict)
        def update_from_dict(self, data_dict: Dict[str, Any]): self.data.update(data_dict)
        def get(self, key: str, default: Any = None) -> Any: return self.data.get(key, default)
        def set(self, key: str, value: Any): self.data[key] = value
        def __repr__(self): return f"PraxisState(data={self.data})"


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
    # TODO: ARGS-SERIALIZE-1: Handle non-serializable objects more gracefully.
    try:
        def make_serializable(item):
            if isinstance(item, (PlrResource, PraxisState, PlrDeck, PraxisRunContext)): # Exclude context itself
                return repr(item)
            # Add other custom non-serializable types here
            return item

        cleaned_args = [make_serializable(arg) for arg in args]
        # Filter out __praxis_run_context__ from kwargs before serialization
        cleaned_kwargs = {k: make_serializable(v) for k, v in kwargs.items() if k != '__praxis_run_context__'}

        return json.dumps({"args": cleaned_args, "kwargs": cleaned_kwargs}, default=str)
    except TypeError as e:
        print(f"Warning: Could not fully serialize arguments due to TypeError: {e}. Storing partial/string representation.")
        # Fallback for args, ensure kwargs doesn't include context if it was problematic
        cleaned_kwargs_fallback = {k: str(v) for k, v in kwargs.items() if k != '__praxis_run_context__'}
        return json.dumps({"args": [str(arg) for arg in args], "kwargs": cleaned_kwargs_fallback})


# Example Placeholder Asset Types
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

