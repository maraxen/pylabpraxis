"""State management utility."""

import json
import uuid
from typing import Any, Dict, Optional

import redis
from redis.exceptions import ConnectionError

from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.uuid import uuid7

logger = get_logger(__name__)


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
    _data (Dict[str, Any]): The internal dictionary holding the state data.

  Methods:
    __init__(self, redis_host="localhost", redis_port=6379, redis_db=0, run_accession_id=uuid7()):
      Initializes a new State instance, connecting to Redis and loading any existing state.
    _load_from_redis(self) -> Dict[str, Any]:
      Loads the state data from Redis.
    _save_to_redis(self):
      Saves the current state data to Redis.
    __getitem__(self, key: str) -> Any:
      Retrieves a value from the state data using the given key.
    __setitem__(self, key: str, value: Any):
      Sets a value in the state data using the given key.
    __delitem__(self, key: str):
      Deletes a key-value pair from the state data.
    get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
      Retrieves a value from the state data, returning a default value if the key is not found.
    update(self, data_dict: Dict[str, Any]):
      Updates the state data with the key-value pairs from the given dictionary.
    to_dict(self) -> Dict[str, Any]:
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
    redis_host: str = "localhost",
    redis_port: int = 6379,
    redis_db: int = 0,
    run_accession_id: uuid.UUID = uuid7(),
  ):
    """Initialize the State instance."""
    if not isinstance(run_accession_id, uuid.UUID):
      raise ValueError("run_accession_id must be a valid UUID.")

      self.run_accession_id: uuid.UUID = run_accession_id
      self.redis_key: str = f"praxis_state:{self.run_accession_id}"

    try:
      self.redis_client = redis.Redis(
        host=redis_host, port=redis_port, db=redis_db, decode_responses=False
      )
      self.redis_client.ping()
      logger.info(
        "Redis client connected for PraxisState (run_accession_id: %s) at %s:%s/%s",
        self.run_accession_id,
        redis_host,
        redis_port,
        redis_db,
      )
    except ConnectionError as e:
      logger.error(
        "Failed to connect to Redis for PraxisState (run_accession_id: %s) at %s:%s/%s: %s",
        self.run_accession_id,
        redis_host,
        redis_port,
        redis_db,
        e,
      )
      raise ConnectionError(f"PraxisState: Failed to connect to Redis - {e}") from e

    self._data: Dict[str, Any] = self._load_from_redis()

  def _load_from_redis(self) -> Dict[str, Any]:
    serialized_state = None
    try:
      serialized_state = self.redis_client.get(self.redis_key)
      if serialized_state:
        if isinstance(serialized_state, bytes):
          return json.loads(serialized_state.decode("utf-8"))
        elif isinstance(serialized_state, str):
          return json.loads(serialized_state)
      return {}
    except json.JSONDecodeError as e:
      if serialized_state is None:
        logger.warning(
          "No state found for run %s in Redis. Returning empty state.",
          self.run_accession_id,
        )
        return {}
      else:
        logger.error(
          "JSONDecodeError while loading state for run %s from Redis: %s. Raw data: %s",
          self.run_accession_id,
          e,
          serialized_state,
        )
        return {}
    except Exception as e:
      logger.error(
        "Failed to load state for run %s from Redis: %s",
        self.run_accession_id,
        e,
      )
      return {}

  def _save_to_redis(self):
    try:
      serialized_state = json.dumps(self._data)
      self.redis_client.set(self.redis_key, serialized_state.encode("utf-8"))
    except TypeError as e:
      logger.error(
        "TypeError during JSON serialization for run %s: %s. State data may not be "
        "fully JSON serializable.",
        self.run_accession_id,
        e,
      )
      raise
    except Exception as e:
      logger.error(
        "Failed to save state for run %s to Redis: %s",
        self.run_accession_id,
        e,
      )
      raise

  def __getitem__(self, key: str) -> Any:
    """Retrieve a value from the state data using the given key."""
    if key not in self._data:
      raise KeyError(
        f"Key '{key}' not found in state data for run {self.run_accession_id}."
      )
    logger.debug(
      "Retrieving key '%s' from state for run %s", key, self.run_accession_id
    )
    return self._data[key]

  def __setitem__(self, key: str, value: Any):
    """Set a value in the state data using the given key."""
    if not isinstance(key, str):
      raise TypeError(f"Key must be a string, got {type(key).__name__}.")
    if not key:
      raise ValueError("Key cannot be an empty string.")
    if not isinstance(value, (str, int, float, bool, dict, list, type(None))):
      raise TypeError(
        f"Value must be a JSON-serializable type, got {type(value).__name__}."
      )
    logger.debug("Setting key '%s' in state for run %s", key, self.run_accession_id)
    if "_data" not in self.__dict__:
      # If _data is not initialized, initialize it
      self._data = {}
    self._data[key] = value
    self._save_to_redis()

  def __delitem__(self, key: str):
    """Delete a value from the state data using the given key."""
    if key not in self._data:
      raise KeyError(
        f"Key '{key}' not found in state data for run {self.run_accession_id}."
      )
    logger.debug("Deleting key '%s' from state for run %s", key, self.run_accession_id)
    del self._data[key]
    self._save_to_redis()

  def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
    """Retrieve a value from the state data using the given key."""
    return self._data.get(key, default)

  def update(self, data_dict: Dict[str, Any]):
    """Update the state data with the given dictionary."""
    if not isinstance(data_dict, dict):
      raise TypeError(
        "data_dict must be a dictionary, got %s", type(data_dict).__name__
      )
    self._data.update(data_dict)
    self._save_to_redis()

  def to_dict(self) -> Dict[str, Any]:
    """Return a copy of the internal state data dictionary."""
    logger.debug("Converting state to dict for run %s", self.run_accession_id)
    return self._data.copy()

  def clear(self):
    """Clear the state data and delete it from Redis."""
    self._data.clear()
    try:
      self.redis_client.delete(self.redis_key)
    except Exception as e:
      logger.error(
        f"Failed to delete state for run {self.run_accession_id} from Redis: {e}"
      )

  def __getattr__(self, name: str) -> Any:
    """Access state data as attributes."""
    if name == "_data":
      if "_data" in self.__dict__:
        return self.__dict__["_data"]
      else:
        raise AttributeError(
          f"'{type(self).__name__}' object's internal '_data' attribute not found."
        )
    if "_data" in self.__dict__ and name in self._data:
      return self._data[name]
    if name in self.__dict__:
      return self.__dict__[name]
    raise AttributeError(
      f"'{type(self).__name__}' object has no attribute '{name}' and no key '{name}' in"
      f" state data"
    )

  def __setattr__(self, name: str, value: Any):
    """Set state data as attributes."""
    if name in ["run_accession_id", "redis_key", "redis_client", "_data"]:
      super().__setattr__(name, value)
    else:
      if "_data" not in self.__dict__:
        super().__setattr__(name, value)
      else:
        self._data[name] = value
        self._save_to_redis()

  def __repr__(self) -> str:
    """Return a string representation of the State instance."""
    return f"<State(run_accession_id='{self.run_accession_id}', data={self._data})>"
