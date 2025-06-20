import json
import uuid
from unittest.mock import patch

import fakeredis
import pytest
import redis
from praxis.backend.services.state import PraxisState


@pytest.fixture
def mock_redis_client(mocker):
  """
  Fixture that patches redis.Redis to use a FakeRedis client.
  This provides a clean, in-memory redis for each test.
  """
  # Instantiate the fake client
  fake_client = fakeredis.FakeRedis(decode_responses=False)

  # Patch the redis.Redis class to return our fake client instance
  mocker.patch("redis.Redis", return_value=fake_client)

  # Yield the client so tests can interact with it directly if needed
  yield fake_client

  # Clean up the fake redis db after the test
  fake_client.flushall()


@pytest.fixture
def run_id() -> uuid.UUID:
  """Provides a consistent UUID for a test run."""
  return uuid.uuid4()


class TestPraxisState:
  """Test suite for the PraxisState class."""

  def test_initialization_success(self, mock_redis_client, run_id):
    """Test successful initialization of the PraxisState object."""
    state = PraxisState(run_accession_id=run_id)

    assert state.run_accession_id == run_id
    assert state.redis_key == f"praxis_state:{run_id}"
    assert state.redis_client is mock_redis_client
    assert state.to_dict() == {}

  def test_initialization_with_existing_redis_data(self, mock_redis_client, run_id):
    """Test that state is loaded from Redis on initialization."""
    redis_key = f"praxis_state:{run_id}"
    existing_data = {"key1": "value1", "count": 10}
    mock_redis_client.set(redis_key, json.dumps(existing_data))

    state = PraxisState(run_accession_id=run_id)

    assert state.to_dict() == existing_data
    assert state["key1"] == "value1"

  def test_initialization_with_invalid_json_in_redis(self, mock_redis_client, run_id):
    """Test graceful handling of malformed JSON data in Redis."""
    redis_key = f"praxis_state:{run_id}"
    mock_redis_client.set(redis_key, '{"key": "value"')  # Malformed JSON

    state = PraxisState(run_accession_id=run_id)

    # Should log an error and return an empty state, not crash
    assert state.to_dict() == {}

  def test_initialization_fails_with_invalid_uuid(self):
    """Test that initialization raises ValueError for a non-UUID run_accession_id."""
    with pytest.raises(ValueError, match="run_accession_id must be a valid UUID"):
      PraxisState(run_accession_id="not-a-uuid")  # type: ignore[arg-type]

  def test_initialization_connection_error(self, mocker):
    """Test that a ConnectionError is raised if Redis connection fails."""
    # Patch redis.Redis to raise a ConnectionError on ping
    mocker.patch(
      "redis.Redis.ping",
      side_effect=redis.ConnectionError("Failed to connect to Redis"),
    )
    mocker.patch("redis.Redis.__init__", return_value=None)  # prevent init error

    with pytest.raises(ConnectionError, match="Failed to connect to Redis"):
      PraxisState()

  def test_dict_interface_set_get_del(self, mock_redis_client, run_id):
    """Test the dictionary-style __setitem__, __getitem__, and __delitem__ methods."""
    state = PraxisState(run_accession_id=run_id)

    # Test __setitem__
    state["message"] = "hello"
    state["number"] = 123

    assert state._data == {"message": "hello", "number": 123}
    # Verify it was saved to Redis
    redis_data = json.loads(mock_redis_client.get(state.redis_key))
    assert redis_data == {"message": "hello", "number": 123}

    # Test __getitem__
    assert state["message"] == "hello"

    # Test __delitem__
    del state["message"]
    assert "message" not in state.to_dict()
    with pytest.raises(KeyError):
      _ = state["message"]

    # Verify deletion in Redis
    redis_data_after_del = json.loads(mock_redis_client.get(state.redis_key))
    assert redis_data_after_del == {"number": 123}

  def test_get_method(self, run_id):
    """Test the get() method for retrieving keys with a default value."""
    state = PraxisState(run_accession_id=run_id)
    state["existing_key"] = "exists"

    assert state.get("existing_key") == "exists"
    assert state.get("non_existent_key") is None
    assert state.get("non_existent_key", "default_val") == "default_val"

  def test_update_method(self, run_id):
    """Test updating the state with a dictionary."""
    state = PraxisState(run_accession_id=run_id)
    state["a"] = 1
    state["b"] = 2

    state.update({"b": 3, "c": 4})

    assert state.to_dict() == {"a": 1, "b": 3, "c": 4}

  def test_attribute_access(self, mock_redis_client, run_id):
    """Test getting and setting state via attribute access."""
    state = PraxisState(run_accession_id=run_id)

    # Test __setattr__
    state.foo = "bar"
    state.count = 99

    # Verify with __getattr__
    assert state.foo == "bar"

    # Verify with dict access
    assert state["count"] == 99

    # Verify in Redis
    redis_data = json.loads(mock_redis_client.get(state.redis_key))
    assert redis_data == {"foo": "bar", "count": 99}

    # Test that accessing a non-existent attribute raises AttributeError
    with pytest.raises(AttributeError):
      _ = state.non_existent_attr

  def test_clear_method(self, mock_redis_client, run_id):
    """Test that clear() removes all data from the object and Redis."""
    state = PraxisState(run_accession_id=run_id)
    state["a"] = 1

    # Verify data exists
    assert state.to_dict() == {"a": 1}
    assert mock_redis_client.exists(state.redis_key)

    state.clear()

    # Verify data is cleared
    assert state.to_dict() == {}
    assert not mock_redis_client.exists(state.redis_key)

  def test_setitem_type_validation(self, run_id):
    """Test that __setitem__ raises TypeError for non-serializable values."""
    state = PraxisState(run_accession_id=run_id)

    class NonSerializable:
      pass

    with pytest.raises(TypeError, match="must be a JSON-serializable type"):
      state["invalid"] = NonSerializable()

    with pytest.raises(TypeError, match="Key must be a string"):
      state[123] = "invalid_key"  # type: ignore[assignment]
