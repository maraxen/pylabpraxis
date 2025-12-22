import json
from unittest.mock import MagicMock, patch

import pytest
from redis.exceptions import ConnectionError, RedisError

from praxis.backend.configure import PraxisConfiguration
from praxis.backend.services.state import PraxisState


@pytest.fixture
def mock_redis():
    with patch("praxis.backend.services.state.redis.Redis") as mock:
        client = MagicMock()
        mock.return_value = client
        yield mock

@pytest.fixture
def config():
    mock_config = MagicMock(spec=PraxisConfiguration)
    mock_config.redis_host = "localhost"
    mock_config.redis_port = 6379
    mock_config.redis_db = 0
    return mock_config

def test_init_state_success(mock_redis, config):
    state = PraxisState(config=config)
    assert state.redis_client is not None
    mock_redis.assert_called_once()
    state.redis_client.ping.assert_called_once()

def test_init_state_connection_error(mock_redis, config):
    mock_redis.return_value.ping.side_effect = ConnectionError("Connection failed")
    with pytest.raises(ConnectionError):
        PraxisState(config=config)

def test_state_operations(mock_redis, config):
    client = mock_redis.return_value
    # Mock get to return empty dict (json dumped)
    client.get.return_value = json.dumps({}).encode("utf-8")

    state = PraxisState(config=config)

    # Set
    state["key1"] = "value1"
    assert state["key1"] == "value1"
    # Assert save called
    client.set.assert_called()

    # Get
    val = state.get("key1")
    assert val == "value1"

    # Update
    state.update({"key2": "value2"})
    assert state["key2"] == "value2"

    # Delete
    del state["key1"]
    assert "key1" not in state

    # Clear
    state.clear()
    assert len(state) == 0
    client.delete.assert_called_with(state.redis_key)

def test_load_from_redis(mock_redis, config):
    client = mock_redis.return_value
    data = {"existing": "data"}
    client.get.return_value = json.dumps(data).encode("utf-8")

    state = PraxisState(config=config)
    assert state["existing"] == "data"

def test_attribute_access(mock_redis, config):
    client = mock_redis.return_value
    client.get.return_value = json.dumps({}).encode("utf-8")

    state = PraxisState(config=config)
    state.new_attr = "value"
    assert state["new_attr"] == "value"
    assert state.new_attr == "value"

def test_invalid_value_type(mock_redis, config):
    client = mock_redis.return_value
    client.get.return_value = json.dumps({}).encode("utf-8")
    state = PraxisState(config=config)

    class Unserializable:
        pass

    with pytest.raises(TypeError):
        state["key"] = Unserializable()

def test_load_json_error(mock_redis, config):
    client = mock_redis.return_value
    client.get.return_value = b"invalid json"

    state = PraxisState(config=config)
    assert len(state) == 0 # Should handle error and return empty

def test_load_redis_error(mock_redis, config):
    client = mock_redis.return_value
    client.get.side_effect = RedisError("Fail")

    state = PraxisState(config=config)
    assert len(state) == 0
