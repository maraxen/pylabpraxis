import pytest  # type: ignore
import json
from unittest.mock import patch, MagicMock

from praxis.backend.services.state import (
  PraxisState as PraxisState,
)  # Assuming State is aliased as PraxisState typically
import redis  # For mocking redis.exceptions.ConnectionError


# Mock Redis client for all tests in this file
@pytest.fixture(autouse=True)
def mock_redis_client():
  # This mock will replace redis.Redis globally for the duration of tests in this module.
  # Individual tests can then .return_value on specific methods like get, set, delete, ping.
  with patch("redis.Redis") as mock_redis_constructor:
    mock_instance = MagicMock()
    mock_redis_constructor.return_value = mock_instance
    yield mock_instance  # Provide the instance for tests to configure


class TestPraxisState:
  def test_init_requires_run_accession_id(self):
    with pytest.raises(ValueError, match="run_accession_id must be a non-empty string"):
      PraxisState(run_accession_id="")  # type: ignore
    with pytest.raises(ValueError, match="run_accession_id must be a non-empty string"):
      PraxisState(run_accession_id="   ")  # type: ignore

  def test_init_connects_to_redis_and_loads_initial_state(
    self, mock_redis_client: MagicMock
  ):
    mock_redis_client.get.return_value = json.dumps(
      {"initial_key": "initial_value"}
    ).encode("utf-8")

    state = PraxisState(run_accession_id="test_run_123")

    mock_redis_client.ping.assert_called_once()
    mock_redis_client.get.assert_called_once_with("praxis_state:test_run_123")
    assert state.to_dict() == {"initial_key": "initial_value"}
    assert state._data == {
      "initial_key": "initial_value"
    }  # Check internal representation too

  def test_init_handles_empty_state_from_redis(self, mock_redis_client: MagicMock):
    mock_redis_client.get.return_value = (
      None  # No state in Redis for this run_accession_id
    )

    state = PraxisState(run_accession_id="test_run_new")

    mock_redis_client.ping.assert_called_once()
    mock_redis_client.get.assert_called_once_with("praxis_state:test_run_new")
    assert state.to_dict() == {}
    assert state._data == {}

  def test_init_handles_redis_connection_error(self, mock_redis_client: MagicMock):
    # Configure the constructor mock to make ping raise ConnectionError
    mock_redis_client.ping.side_effect = redis.exceptions.ConnectionError(
      "Test connection error"
    )

    with pytest.raises(
      ConnectionError,
      match="PraxisState: Failed to connect to Redis - Test connection error",
    ):
      PraxisState(run_accession_id="test_run_conn_error")

  def test_init_handles_json_decode_error(self, mock_redis_client: MagicMock, caplog):
    mock_redis_client.get.return_value = b"this is not json"

    state = PraxisState(run_accession_id="test_run_json_error")

    assert state.to_dict() == {}  # Should default to empty dict
    assert "JSONDecodeError while loading state" in caplog.text
    assert "Raw data: b'this is not json'" in caplog.text

  def test_setitem_saves_to_redis_and_updates_data(self, mock_redis_client: MagicMock):
    mock_redis_client.get.return_value = None  # Start with empty state
    state = PraxisState(run_accession_id="test_run_set")

    state["my_key"] = "my_value"

    assert state._data["my_key"] == "my_value"
    mock_redis_client.set.assert_called_once_with(
      "praxis_state:test_run_set", json.dumps({"my_key": "my_value"}).encode("utf-8")
    )

    state["another_key"] = {"nested": 123}
    mock_redis_client.set.assert_called_with(
      "praxis_state:test_run_set",
      json.dumps({"my_key": "my_value", "another_key": {"nested": 123}}).encode(
        "utf-8"
      ),
    )
    assert state._data["another_key"] == {"nested": 123}

  def test_getitem_retrieves_from_data(self, mock_redis_client: MagicMock):
    initial_data = {"key1": "val1"}
    mock_redis_client.get.return_value = json.dumps(initial_data).encode("utf-8")
    state = PraxisState(run_accession_id="test_run_get")

    assert state["key1"] == "val1"
    with pytest.raises(KeyError):
      _ = state["non_existent_key"]  # pylint: disable=pointless-statement

  def test_delitem_saves_to_redis_and_updates_data(self, mock_redis_client: MagicMock):
    initial_data = {"key1": "val1", "key_to_del": "delete_me"}
    mock_redis_client.get.return_value = json.dumps(initial_data).encode("utf-8")
    state = PraxisState(run_accession_id="test_run_del")

    del state["key_to_del"]

    assert "key_to_del" not in state._data
    mock_redis_client.set.assert_called_once_with(
      "praxis_state:test_run_del", json.dumps({"key1": "val1"}).encode("utf-8")
    )

  def test_get_method(self, mock_redis_client: MagicMock):
    initial_data = {"key1": "val1"}
    mock_redis_client.get.return_value = json.dumps(initial_data).encode("utf-8")
    state = PraxisState(run_accession_id="test_run_get_method")

    assert state.get("key1") == "val1"
    assert state.get("non_existent_key") is None
    assert state.get("non_existent_key", "default_val") == "default_val"

  def test_update_method_saves_to_redis(self, mock_redis_client: MagicMock):
    mock_redis_client.get.return_value = json.dumps({"key1": "val1_orig"}).encode(
      "utf-8"
    )
    state = PraxisState(run_accession_id="test_run_update")

    state.update({"key1": "val1_new", "key2": "val2"})

    expected_data = {"key1": "val1_new", "key2": "val2"}
    assert state.to_dict() == expected_data
    mock_redis_client.set.assert_called_once_with(
      "praxis_state:test_run_update", json.dumps(expected_data).encode("utf-8")
    )

  def test_to_dict_returns_copy(self, mock_redis_client: MagicMock):
    initial_data = {"key1": "val1"}
    mock_redis_client.get.return_value = json.dumps(initial_data).encode("utf-8")
    state = PraxisState(run_accession_id="test_run_to_dict")

    state_dict = state.to_dict()
    assert state_dict == initial_data
    state_dict["new_key_local_only"] = "not_in_state_object"
    assert "new_key_local_only" not in state._data  # Ensure it's a copy

  def test_clear_clears_data_and_deletes_from_redis(self, mock_redis_client: MagicMock):
    initial_data = {"key1": "val1"}
    mock_redis_client.get.return_value = json.dumps(initial_data).encode("utf-8")
    state = PraxisState(run_accession_id="test_run_clear")

    assert state.to_dict() == initial_data  # Ensure it's loaded
    state.clear()

    assert state.to_dict() == {}
    assert state._data == {}
    mock_redis_client.delete.assert_called_once_with("praxis_state:test_run_clear")

  def test_attribute_access_set_and_get(self, mock_redis_client: MagicMock):
    mock_redis_client.get.return_value = None
    state = PraxisState(run_accession_id="test_run_attr")

    state.my_attr = "attr_value"  # Tests __setattr__
    assert state.my_attr == "attr_value"  # Tests __getattr__
    assert state["my_attr"] == "attr_value"  # Verify via __getitem__ too

    expected_data = {"my_attr": "attr_value"}
    mock_redis_client.set.assert_called_once_with(
      "praxis_state:test_run_attr", json.dumps(expected_data).encode("utf-8")
    )

  def test_attribute_access_get_non_existent(self, mock_redis_client: MagicMock):
    mock_redis_client.get.return_value = None
    state = PraxisState(run_accession_id="test_run_attr_get_fail")
    with pytest.raises(AttributeError):
      _ = state.non_existent_attr  # pylint: disable=pointless-statement

  def test_set_internal_attribute(self, mock_redis_client: MagicMock):
    mock_redis_client.get.return_value = None
    state = PraxisState(run_accession_id="test_run_internal_attr")

    # These should not go into _data or trigger Redis save
    state.run_accession_id = (
      "new_accession_id"  # Should be handled by super().__setattr__
    )
    state._data = {
      "internal_override": "danger"
    }  # Should be handled by super().__setattr__

    assert state.run_accession_id == "new_accession_id"
    assert state._data == {"internal_override": "danger"}
    mock_redis_client.set.assert_not_called()  # No save should happen for these internal attrs
