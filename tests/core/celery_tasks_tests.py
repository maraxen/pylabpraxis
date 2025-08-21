# pylint: disable=redefined-outer-name, protected-access
"""Unit tests for Celery tasks."""

import uuid
from typing import TYPE_CHECKING
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from praxis.backend.core.celery_tasks import (
  execute_protocol_run_task,
  health_check,
)
from praxis.backend.models import ProtocolRunOrm, ProtocolRunStatusEnum

if TYPE_CHECKING:
  from celery.result import EagerResult

# --- Test Constants ---
TEST_RUN_ID = uuid.uuid4()
TEST_CELERY_TASK_ID = "celery-task-id-123"

# --- Fixtures ---


@pytest.fixture
def mock_orchestrator():
  """Provides a mock Orchestrator."""
  orc = AsyncMock()
  orc.execute_existing_protocol_run = AsyncMock(
    return_value=MagicMock(spec=ProtocolRunOrm, status=ProtocolRunStatusEnum.COMPLETED),
  )
  return orc


@pytest.fixture
def mock_db_session_factory():
  """Provides a mock async session factory."""
  factory = MagicMock()
  factory.return_value.__aenter__.return_value = AsyncMock()
  factory.return_value.__aexit__.return_value = None
  return factory


# --- Tests ---


@pytest.mark.asyncio
class TestExecuteProtocolRunTask:

  """Test suite for the main protocol execution Celery task."""

  def test_task_happy_path(self, mock_orchestrator, mock_db_session_factory) -> None:
    """Test the successful execution path of the Celery task."""
    # Arrange
    mock_task = MagicMock()
    mock_task.request.id = TEST_CELERY_TASK_ID
    expected_result = {"success": True, "message": "Async part finished."}

    with patch("asyncio.run", return_value=expected_result) as mock_asyncio_run:
      # Act
      result = execute_protocol_run_task(
          self=mock_task,
          protocol_run_id=str(TEST_RUN_ID),
          input_parameters={"volume": 50},
          initial_state=None,
          orchestrator=mock_orchestrator,
          db_session_factory=mock_db_session_factory,
      )

      # Assert
      mock_asyncio_run.assert_called_once()
      assert result == expected_result

  def test_task_catches_general_exception(self, mock_orchestrator, mock_db_session_factory) -> None:
    """Test that the main task function catches exceptions from the async runner."""
    # Arrange
    error_message = "Orchestrator exploded"

    with patch("asyncio.run") as mock_asyncio_run:
      mock_asyncio_run.side_effect = [
        Exception(error_message),
        None,
      ]

      # Act
      result = execute_protocol_run_task(
        self=MagicMock(),
        protocol_run_id=str(TEST_RUN_ID),
        input_parameters={},
        orchestrator=mock_orchestrator,
        db_session_factory=mock_db_session_factory,
      )

      # Assert
      assert not result["success"]
      assert error_message in result["error"]
      assert mock_asyncio_run.call_count == 2

  async def test_async_helper_happy_path(self, mock_orchestrator, mock_db_session_factory) -> None:
    """Test the internal async execution logic for a successful run."""
    # Arrange
    mock_run_orm = ProtocolRunOrm(accession_id=TEST_RUN_ID)
    with patch(
      "praxis.backend.services.protocols.protocol_run_service.read_protocol_run",
      new_callable=AsyncMock,
      return_value=mock_run_orm,
    ) as mock_read, patch(
      "praxis.backend.services.protocols.protocol_run_service.update_protocol_run_status", new_callable=AsyncMock,
    ) as mock_update:
      # Act
      from praxis.backend.core.celery_tasks import _execute_protocol_async

      result = await _execute_protocol_async(
        TEST_RUN_ID, {}, None, TEST_CELERY_TASK_ID, mock_orchestrator, mock_db_session_factory
      )

      # Assert
      mock_read.assert_awaited_once()
      mock_update.assert_awaited_once()
      mock_orchestrator.execute_existing_protocol_run.assert_awaited_once()
      assert result["success"]
      assert result["final_status"] == ProtocolRunStatusEnum.COMPLETED.value

  async def test_async_helper_orchestrator_fails(self, mock_orchestrator, mock_db_session_factory) -> None:
    """Test that a failure in the orchestrator is caught and handled."""
    # Arrange
    mock_run_orm = ProtocolRunOrm(accession_id=TEST_RUN_ID)
    mock_orchestrator.execute_existing_protocol_run.side_effect = (
      RuntimeError("Test Fail")
    )

    with patch(
      "praxis.backend.services.protocols.protocol_run_service.read_protocol_run",
      new_callable=AsyncMock,
      return_value=mock_run_orm,
    ), patch(
      "praxis.backend.services.protocols.protocol_run_service.update_protocol_run_status", new_callable=AsyncMock,
    ) as mock_update:
      # Act & Assert
      from praxis.backend.core.celery_tasks import _execute_protocol_async

      with pytest.raises(RuntimeError, match="Test Fail"):
        await _execute_protocol_async(TEST_RUN_ID, {}, None, TEST_CELERY_TASK_ID, mock_orchestrator, mock_db_session_factory)

      # Assert the final status update was to FAILED
      final_call = mock_update.call_args_list[-1]
      assert final_call.kwargs["new_status"] == ProtocolRunStatusEnum.FAILED


def test_health_check_task() -> None:
  """Test the simple health check task."""
  # Act
  result: EagerResult = health_check.s().apply()

  # Assert
  assert result.successful()
  assert result.result["status"] == "healthy"
  assert "timestamp" in result.result
