"""State management utility."""

import json
import uuid
from collections.abc import ItemsView, KeysView, ValuesView
from typing import Any, TypeVar

import redis
from redis.exceptions import ConnectionError

from praxis.backend.configure import PraxisConfiguration
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.uuid import uuid7

logger = get_logger(__name__)

T = TypeVar("T")


class PraxisState:
  """Manages application state, persisting it to a Redis server.

  This class provides a dictionary-like interface for storing and retrieving
  application state, with the data being automatically serialized and stored
  in a Redis database. It uses a unique run identifier (UUID) to isolate
  state for different application runs.

  Attributes:
    run_accession_id (uuid.UUID): A unique identifier for the application run.
    redis_key (str): The key used to store the state in Redis.
    redis_client (redis.Redis): The Redis client instance.
    _data (dict[str, Any]): The internal dictionary holding the state data.

  Methods:
    __init__(
      self,
      config: PraxisConfiguration | None = None,
      run_accession_id: uuid.UUID | None = None,
      redis_host: str | None = None,
      redis_port: int | None = None,
      redis_db: int | None = None,
    ):
      Initializes a new State instance, connecting to Redis and loading any existing state.
    _load_from_redis(self) -> dict[str, Any]:
      Loads the state data from Redis.
    _save_to_redis(self):
      Saves the current state data to Redis.
    __getitem__(self, key: str) -> Any:
      Retrieves a value from the state data using the given key.
    __setitem__(self, key: str, value: Any):
      Sets a value in the state data using the given key.
    __delitem__(self, key: str):
      Deletes a key-value pair from the state data.
    get(self, key: str, default: Any | None = None) -> Any | None:
      Retrieves a value from the state data, returning a default value if the key is not found.
    update(self, data_dict: dict[str, Any]):
      Updates the state data with the key-value pairs from the given dictionary.
    to_dict(self) -> dict[str, Any]:
      Returns a copy of the internal state data dictionary.
    clear(self):
      Clears all state data and deletes the Redis key associated with this state.
    __getattr__(self, name: str) -> Any:
      Allows accessing state data as attributes.
    __setattr__(self, name: str, value: Any):
      Allows setting state data as attributes.
    __repr__(self) -> str:
      Returns a string representation of the State instance.

  """

  def __init__(
    self,
    config: PraxisConfiguration | None = None,
    run_accession_id: uuid.UUID | None = None,
    redis_host: str | None = None,
    redis_port: int | None = None,
    redis_db: int | None = None,
  ) -> None:
    """Initialize the State instance."""
    if config is None:
      config = PraxisConfiguration()

    if run_accession_id is None:
      run_accession_id = uuid7()

    self.run_accession_id: uuid.UUID = run_accession_id
    self.redis_key: str = f"praxis_state:{self.run_accession_id}"

    _redis_host = redis_host if redis_host is not None else config.redis_host
    _redis_port = redis_port if redis_port is not None else config.redis_port
    _redis_db = redis_db if redis_db is not None else config.redis_db

    try:
      self.redis_client = redis.Redis(
        host=_redis_host,
        port=_redis_port,
        db=_redis_db,
        decode_responses=False,
      )
      self.redis_client.ping()
    except ConnectionError as e:
      logger.exception(
        "Failed to connect to Redis for PraxisState (run_accession_id: %s) at %s:%s/%s",
        self.run_accession_id,
        _redis_host,
        _redis_port,
        _redis_db,
      )
      msg = f"PraxisState: Failed to connect to Redis - {e}"
      raise ConnectionError(msg) from e
    else:
      logger.info(
        "Redis client connected for PraxisState (run_accession_id: %s) at %s:%s/%s",
        self.run_accession_id,
        _redis_host,
        _redis_port,
        _redis_db,
      )

    self._data: dict[str, Any] = self._load_from_redis()

  def _load_from_redis(self) -> dict[str, Any]:
    serialized_state = None
    try:
      serialized_state = self.redis_client.get(self.redis_key)
      if serialized_state and isinstance(serialized_state, bytes):
        return json.loads(serialized_state.decode("utf-8"))
      return {}  # noqa: TRY300
    except json.JSONDecodeError:
      if serialized_state is None:
        logger.warning(
          "No state found for run %s in Redis. Returning empty state.",
          self.run_accession_id,
        )
        return {}
      logger.exception(
        "JSONDecodeError while loading state for run %s from Redis. Raw data: %s",
        self.run_accession_id,
        serialized_state,
      )
      return {}
    except redis.RedisError:
      logger.exception(
        "Failed to load state for run %s from Redis",
        self.run_accession_id,
      )
      return {}

  def _save_to_redis(self) -> None:
    try:
      serialized_state = json.dumps(self._data)
      self.redis_client.set(self.redis_key, serialized_state.encode("utf-8"))
    except TypeError:
      logger.exception(
        "TypeError during JSON serialization for run %s. State data may not be "
        "fully JSON serializable.",
        self.run_accession_id,
      )
    except redis.RedisError:
      logger.exception(
        "Failed to save state for run %s to Redis",
        self.run_accession_id,
      )
      raise

  def __getitem__(self, key: str) -> Any:  # noqa: ANN401
    """Retrieve a value from the state data using the given key."""
    if key not in self._data:
      msg = f"Key '{key}' not found in state data for run {self.run_accession_id}."
      raise KeyError(msg)
    logger.debug(
      "Retrieving key '%s' from state for run %s",
      key,
      self.run_accession_id,
    )
    return self._data[key]

  def __setitem__(self, key: str, value: Any) -> None:  # noqa: ANN401
    """Set a value in the state data using the given key."""
    if not key:
      msg = "Key cannot be an empty string."
      raise ValueError(msg)
    if not isinstance(value, str | int | float | bool | dict | list | None):
      msg = f"Value must be a JSON-serializable type, got {type(value).__name__}."
      raise TypeError(msg)
    logger.debug("Setting key '%s' in state for run %s", key, self.run_accession_id)
    self._data[key] = value
    self._save_to_redis()

  def __delitem__(self, key: str) -> None:
    """Delete a value from the state data using the given key."""
    if key not in self._data:
      msg = f"Key '{key}' not found in state data for run {self.run_accession_id}."
      raise KeyError(msg)
    logger.debug("Deleting key '%s' from state for run %s", key, self.run_accession_id)
    del self._data[key]
    self._save_to_redis()

  def set(self, key: str, value: Any) -> None:  # noqa: ANN401
    """Set a value in the state data. Alias for state[key] = value."""
    self.__setitem__(key, value)

  def delete(self, key: str) -> None:
    """Delete a value from the state data. Alias for del state[key]."""
    self.__delitem__(key)

  def get(self, key: str, default: T | None = None) -> T | None:
    """Retrieve a value from the state data using the given key."""
    return self._data.get(key, default)

  def update(self, data_dict: dict[str, Any]) -> None:
    """Update the state data with the given dictionary."""
    self._data.update(data_dict)
    self._save_to_redis()

  def to_dict(self) -> dict[str, Any]:
    """Return a copy of the internal state data dictionary."""
    logger.debug("Converting state to dict for run %s", self.run_accession_id)
    return self._data.copy()

  def clear(self) -> None:
    """Clear the state data and delete it from Redis."""
    self._data.clear()
    try:
      self.redis_client.delete(self.redis_key)
    except redis.RedisError:
      logger.exception(
        "Failed to delete state for run %s from Redis",
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

  def __getattr__(self, name: str) -> Any:  # noqa: ANN401
    """Access state data as attributes."""
    if name == "_data":
      if "_data" in self.__dict__:
        return self.__dict__["_data"]
      msg = f"'{type(self).__name__}' object's internal '_data' attribute not found."
      raise AttributeError(msg)
    if "_data" in self.__dict__ and name in self._data:
      return self._data[name]
    if name in self.__dict__:
      return self.__dict__[name]
    msg = (
      f"'{type(self).__name__}' object has no attribute '{name}' and no key '{name}' in state data"
    )
    raise AttributeError(msg)

  def __setattr__(self, name: str, value: Any) -> None:  # noqa: ANN401
    """Set state data as attributes."""
    if name in ["run_accession_id", "redis_key", "redis_client", "_data"]:
      super().__setattr__(name, value)
    else:
      self._data[name] = value
      self._save_to_redis()

  def __repr__(self) -> str:
    """Return a string representation of the State instance."""
    return f"<State(run_accession_id='{self.run_accession_id}', data={self._data})>"
