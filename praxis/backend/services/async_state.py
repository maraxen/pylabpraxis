"""Async state management utility using KeyValueStore protocol.

This module provides an async-compatible state management service that uses
the KeyValueStore protocol, enabling both Redis-backed (production) and
in-memory (demo) backends.
"""

import json
import uuid
from collections.abc import ItemsView, KeysView, ValuesView
from typing import Any, TypeVar

from praxis.backend.core.storage.protocols import KeyValueStore
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.uuid import uuid7

logger = get_logger(__name__)

T = TypeVar("T")


class AsyncPraxisState:
  """Manages application state using the KeyValueStore protocol.

  This class provides a dictionary-like interface for storing and retrieving
  application state, with the data being automatically serialized and stored
  via the injected KeyValueStore backend. It uses a unique run identifier
  (UUID) to isolate state for different application runs.

  Unlike the sync PraxisState, this class:
  - Uses async methods for persistence
  - Accepts a KeyValueStore protocol (can be Redis or in-memory)
  - Supports both sync access to cached data and async persistence

  Attributes:
    run_accession_id (uuid.UUID): A unique identifier for the application run.
    store_key (str): The key used to store the state in the KeyValueStore.
    _store (KeyValueStore): The storage backend.
    _data (dict[str, Any]): The internal dictionary holding the state data.

  """

  def __init__(
    self,
    store: KeyValueStore,
    run_accession_id: uuid.UUID | None = None,
    key_prefix: str = "praxis_state",
  ) -> None:
    """Initialize the AsyncPraxisState instance.

    Args:
      store: The KeyValueStore backend to use for persistence.
      run_accession_id: A unique identifier for this run. Generated if None.
      key_prefix: Prefix for the storage key.

    """
    self._store = store
    self.run_accession_id: uuid.UUID = run_accession_id or uuid7()
    self.store_key: str = f"{key_prefix}:{self.run_accession_id}"
    self._data: dict[str, Any] = {}
    self._initialized = False

  async def initialize(self) -> "AsyncPraxisState":
    """Load the state from the KeyValueStore.

    This must be called before using the state. Returns self for chaining.
    """
    await self._load_from_store()
    self._initialized = True
    return self

  async def _load_from_store(self) -> None:
    """Load the state data from the KeyValueStore."""
    try:
      stored_data = await self._store.get(self.store_key)
      if stored_data is not None:
        if isinstance(stored_data, dict):
          self._data = stored_data
        elif isinstance(stored_data, str):
          self._data = json.loads(stored_data)
        else:
          logger.warning(
            "Unexpected data type from store for run %s: %s",
            self.run_accession_id,
            type(stored_data),
          )
          self._data = {}
      else:
        self._data = {}
    except json.JSONDecodeError:
      logger.exception(
        "JSONDecodeError while loading state for run %s",
        self.run_accession_id,
      )
      self._data = {}
    except Exception:
      logger.exception(
        "Failed to load state for run %s from store",
        self.run_accession_id,
      )
      self._data = {}

  async def _save_to_store(self) -> None:
    """Save the current state data to the KeyValueStore."""
    try:
      await self._store.set(self.store_key, self._data)
    except TypeError:
      logger.exception(
        "TypeError during JSON serialization for run %s. State data may not be "
        "fully JSON serializable.",
        self.run_accession_id,
      )
    except Exception:
      logger.exception(
        "Failed to save state for run %s to store",
        self.run_accession_id,
      )
      raise

  def __getitem__(self, key: str) -> Any:
    """Retrieve a value from the state data using the given key."""
    if key not in self._data:
      msg = f"Key '{key}' not found in state data for run {self.run_accession_id}."
      raise KeyError(msg)
    return self._data[key]

  async def set_async(self, key: str, value: Any) -> None:
    """Set a value in the state data and persist asynchronously."""
    if not key:
      msg = "Key cannot be an empty string."
      raise ValueError(msg)
    self._data[key] = value
    await self._save_to_store()

  async def delete_async(self, key: str) -> None:
    """Delete a value from the state data and persist asynchronously."""
    if key not in self._data:
      msg = f"Key '{key}' not found in state data for run {self.run_accession_id}."
      raise KeyError(msg)
    del self._data[key]
    await self._save_to_store()

  def get(self, key: str, default: T | None = None) -> T | None:
    """Retrieve a value from the state data using the given key."""
    return self._data.get(key, default)

  async def update_async(self, data_dict: dict[str, Any]) -> None:
    """Update the state data with the given dictionary and persist."""
    self._data.update(data_dict)
    await self._save_to_store()

  def to_dict(self) -> dict[str, Any]:
    """Return a copy of the internal state data dictionary."""
    return self._data.copy()

  async def clear_async(self) -> None:
    """Clear the state data and delete it from the store."""
    self._data.clear()
    try:
      await self._store.delete(self.store_key)
    except Exception:
      logger.exception(
        "Failed to delete state for run %s from store",
        self.run_accession_id,
      )

  def __contains__(self, key: str) -> bool:
    """Check if a key exists in the state data."""
    return key in self._data

  def __len__(self) -> int:
    """Return the number of items in the state data."""
    return len(self._data)

  def keys(self) -> KeysView:
    """Return the keys of the state data."""
    return self._data.keys()

  def values(self) -> ValuesView:
    """Return the values of the state data."""
    return self._data.values()

  def items(self) -> ItemsView:
    """Return the items (key-value pairs) of the state data."""
    return self._data.items()

  def __repr__(self) -> str:
    """Return a string representation of the AsyncPraxisState instance."""
    return f"<AsyncPraxisState(run_accession_id='{self.run_accession_id}', keys={list(self._data.keys())})>"


async def create_async_state(
  store: KeyValueStore,
  run_accession_id: uuid.UUID | None = None,
) -> AsyncPraxisState:
  """Factory function to create and initialize an AsyncPraxisState.

  Args:
    store: The KeyValueStore backend to use.
    run_accession_id: Optional run ID to use.

  Returns:
    An initialized AsyncPraxisState instance.

  """
  state = AsyncPraxisState(store=store, run_accession_id=run_accession_id)
  await state.initialize()
  return state
