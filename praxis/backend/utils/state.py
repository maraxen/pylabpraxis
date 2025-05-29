# praxis/backend/utils/state.py
import redis
from redis.exceptions import ConnectionError
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class State: # This will be aliased as PraxisState
    def __init__(self,
                  redis_host: str = "localhost",
                  redis_port: int = 6379,
                  redis_db: int = 0,
                  run_guid: Optional[str] = None):
        if run_guid is not None:
            if not isinstance(run_guid, str) or not run_guid.strip():
                raise ValueError("run_guid must be a non-empty string.")

            self.run_guid: str = run_guid
            self.redis_key: str = f"praxis_state:{self.run_guid}"
        else:
          run_guid = "default"
          self.run_guid: str = run_guid

        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=False
            )
            self.redis_client.ping()
            logger.info(f"Redis client connected for PraxisState (run_guid: {self.run_guid}) at {redis_host}:{redis_port}/{redis_db}")
        except ConnectionError as e:
            logger.error(f"Failed to connect to Redis for PraxisState (run_guid: {self.run_guid}) at {redis_host}:{redis_port}/{redis_db}: {e}")
            raise ConnectionError(f"PraxisState: Failed to connect to Redis - {e}") from e

        self._data: Dict[str, Any] = self._load_from_redis()

    def _load_from_redis(self) -> Dict[str, Any]:
        serialized_state = None
        try:
            serialized_state = self.redis_client.get(self.redis_key)
            if serialized_state:
                if isinstance(serialized_state, bytes):
                    return json.loads(serialized_state.decode('utf-8'))
                elif isinstance(serialized_state, str):
                    return json.loads(serialized_state)
            return {}
        except json.JSONDecodeError as e:
          if serialized_state is None:
            logger.warning(f"No state found for run {self.run_guid} in Redis. Returning empty state.")
            return {}
          else:
            logger.error(f"JSONDecodeError while loading state for run {self.run_guid} from Redis: \
              {e}. Raw data: {serialized_state!r}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load state for run {self.run_guid} from Redis: {e}")
            return {}

    def _save_to_redis(self):
        try:
            serialized_state = json.dumps(self._data)
            self.redis_client.set(self.redis_key, serialized_state.encode('utf-8'))
        except TypeError as e:
            logger.error(f"TypeError during JSON serialization for run {self.run_guid}: {e}. State data may not be fully JSON serializable.")
            raise
        except Exception as e:
            logger.error(f"Failed to save state for run {self.run_guid} to Redis: {e}")
            raise

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any):
        self._data[key] = value
        self._save_to_redis()

    def __delitem__(self, key: str):
        del self._data[key]
        self._save_to_redis()

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        return self._data.get(key, default)

    def update(self, data_dict: Dict[str, Any]):
        self._data.update(data_dict)
        self._save_to_redis()

    def to_dict(self) -> Dict[str, Any]:
        return self._data.copy()

    def clear(self):
        self._data.clear()
        try:
            self.redis_client.delete(self.redis_key)
        except Exception as e:
            logger.error(f"Failed to delete state for run {self.run_guid} from Redis: {e}")

    def __getattr__(self, name: str) -> Any:
        if name == '_data':
            if '_data' in self.__dict__:
                 return self.__dict__['_data']
            else:
                 raise AttributeError(f"'{type(self).__name__}' object's internal '_data' attribute not found.")
        if '_data' in self.__dict__ and name in self._data:
            return self._data[name]
        if name in self.__dict__:
            return self.__dict__[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}' and no key '{name}' in state data")

    def __setattr__(self, name: str, value: Any):
        if name in ['run_guid', 'redis_key', 'redis_client', '_data']:
            super().__setattr__(name, value)
        else:
            if '_data' not in self.__dict__:
                super().__setattr__(name, value)
            else:
                self._data[name] = value
                self._save_to_redis()

    def __repr__(self) -> str:
        return f"<State(run_guid='{self.run_guid}', data={self._data})>"
