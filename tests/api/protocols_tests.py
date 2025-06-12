import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import redis.exceptions

# Import the router from the module where it's defined
from praxis.backend.api.protocols import router as protocols_router
from praxis.backend.utils.run_control import ALLOWED_COMMANDS

# Setup FastAPI app and TestClient
app = FastAPI()
app.include_router(
  protocols_router, prefix="/api/protocols"
)  # Match the prefix used in tests

client = TestClient(app)

# A valid run_accession_id for testing
TEST_RUN_GUID = "test-run-accession_id-123"


class TestProtocolCommandsAPI:
  @patch("praxis.backend.api.protocols.send_control_command_to_redis")
  def test_send_pause_command_success(self, mock_send_control_command_redis):
    mock_send_control_command_redis.return_value = True
    response = client.post(
      f"/api/protocols/{TEST_RUN_GUID}/command", params={"command": "PAUSE"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
      "message": f"Command 'PAUSE' sent to run '{TEST_RUN_GUID}'"
    }
    mock_send_control_command_redis.assert_called_once_with(TEST_RUN_GUID, "PAUSE")

  @patch("praxis.backend.api.protocols.send_control_command_to_redis")
  def test_send_resume_command_success(self, mock_send_control_command_redis):
    mock_send_control_command_redis.return_value = True
    response = client.post(
      f"/api/protocols/{TEST_RUN_GUID}/command", params={"command": "RESUME"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
      "message": f"Command 'RESUME' sent to run '{TEST_RUN_GUID}'"
    }
    mock_send_control_command_redis.assert_called_once_with(TEST_RUN_GUID, "RESUME")

  @patch("praxis.backend.api.protocols.send_control_command_to_redis")
  def test_send_cancel_command_success(self, mock_send_control_command_redis):
    mock_send_control_command_redis.return_value = True
    response = client.post(
      f"/api/protocols/{TEST_RUN_GUID}/command", params={"command": "CANCEL"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
      "message": f"Command 'CANCEL' sent to run '{TEST_RUN_GUID}'"
    }
    mock_send_control_command_redis.assert_called_once_with(TEST_RUN_GUID, "CANCEL")

  @patch("praxis.backend.api.protocols.send_control_command_to_redis")
  def test_send_invalid_command(self, mock_send_control_command_redis):
    invalid_command = "INVALID_COMMAND"
    response = client.post(
      f"/api/protocols/{TEST_RUN_GUID}/command", params={"command": invalid_command}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.json()
    assert f"Invalid command: {invalid_command}" in response.json()["detail"]
    assert f"Allowed commands are: {ALLOWED_COMMANDS}" in response.json()["detail"]
    mock_send_control_command_redis.assert_not_called()

  @patch("praxis.backend.api.protocols.send_control_command_to_redis")
  def test_send_command_redis_error(self, mock_send_control_command_redis):
    mock_send_control_command_redis.side_effect = redis.exceptions.RedisError(
      "Test Redis Error"
    )
    response = client.post(
      f"/api/protocols/{TEST_RUN_GUID}/command", params={"command": "PAUSE"}
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "detail" in response.json()
    assert (
      "An unexpected error occurred while sending command" in response.json()["detail"]
    )
    mock_send_control_command_redis.assert_called_once_with(TEST_RUN_GUID, "PAUSE")

  @patch("praxis.backend.api.protocols.send_control_command_to_redis")
  def test_send_command_failure_from_redis_false(self, mock_send_control_command_redis):
    mock_send_control_command_redis.return_value = (
      False  # Simulate Redis command sending failure
    )
    response = client.post(
      f"/api/protocols/{TEST_RUN_GUID}/command", params={"command": "PAUSE"}
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "detail" in response.json()
    assert (
      f"Failed to send command to run '{TEST_RUN_GUID}' using Redis."
      in response.json()["detail"]
    )
    mock_send_control_command_redis.assert_called_once_with(TEST_RUN_GUID, "PAUSE")
