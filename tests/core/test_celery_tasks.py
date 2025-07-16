# pylint: disable=redefined-outer-name, protected-access
"""Unit tests for Celery tasks."""

import uuid
from typing import TYPE_CHECKING
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from praxis.backend.core.celery_tasks import (
  ProtocolExecutionContext,
  execute_protocol_run_task,
  health_check,
  initialize_celery_context,
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
  # The factory returns an async context manager which in turn returns a mock session
  factory.return_value.__aenter__.return_value = AsyncMock()
  factory.return_value.__aexit__.return_value = None
  return factory


@pytest.fixture
def execution_context(mock_orchestrator, mock_db_session_factory):
  """Provides a mock ProtocolExecutionContext."""
  return ProtocolExecutionContext(
    db_session_factory=mock_db_session_factory, orchestrator=mock_orchestrator,
  )


# --- Tests ---


@pytest.mark.asyncio
class TestExecuteProtocolRunTask:

  """Test suite for the main protocol execution Celery task."""

  def test_initialize_celery_context(self, mock_orchestrator, mock_db_session_factory) -> None:
    """Test that the context initialization function works correctly."""
    # Arrange
    with patch("praxis.backend.core.celery_tasks._execution_context", None):
      # Act
      initialize_celery_context(mock_db_session_factory, mock_orchestrator)
      # Assert that the global context is now set
      from praxis.backend.core.celery_tasks import _execution_context

      assert _execution_context is not None
      assert _execution_context.orchestrator is mock_orchestrator

  def test_task_happy_path(self, execution_context) -> None:
    """Test the successful execution path of the Celery task."""
    # Arrange
    mock_task = MagicMock()
    mock_task.request.id = TEST_CELERY_TASK_ID
    expected_result = {"success": True, "message": "Async part finished."}

    # Patch the global context and the asyncio runner
    with patch(
      "praxis.backend.core.celery_tasks._execution_context", execution_context,
    ), patch("asyncio.run", return_value=expected_result) as mock_asyncio_run:
      # Act
      result = (
        execute_protocol_run_task.s(  # type: ignore
          protocol_run_id=str(TEST_RUN_ID),
          user_params={"volume": 50},
          initial_state=None,
        )
        .apply(task_id=TEST_CELERY_TASK_ID)
        .get()
      )  # .apply().get() simulates a sync call

      # Assert
      mock_asyncio_run.assert_called_once()
      assert result == expected_result

  def test_task_no_context(self) -> None:
    """Test that the task fails gracefully if the context is not initialized."""
    # Arrange: Ensure context is None
    with patch("praxis.backend.core.celery_tasks._execution_context", None):
      # Act
      result = execute_protocol_run_task(
        self=MagicMock(),
        protocol_run_id=str(TEST_RUN_ID),
        user_params={},
      )

      # Assert
      assert not result["success"]
      assert "context is not initialized" in result["error"]

  def test_task_catches_general_exception(self, execution_context) -> None:
    """Test that the main task function catches exceptions from the async runner."""
    # Arrange
    error_message = "Orchestrator exploded"

    # Patch the global context and have asyncio.run raise an exception
    with patch(
      "praxis.backend.core.celery_tasks._execution_context", execution_context,
    ), patch("asyncio.run") as mock_asyncio_run:
      mock_asyncio_run.side_effect = [
        Exception(error_message),
        None,
      ]  # First for try, second for except

      # Act
      result = execute_protocol_run_task(
        self=MagicMock(),
        protocol_run_id=str(TEST_RUN_ID),
        user_params={},
      )

      # Assert
      assert not result["success"]
      assert error_message in result["error"]
      # Check that the fallback error handler was called
      assert mock_asyncio_run.call_count == 2

  async def test_async_helper_happy_path(self, execution_context) -> None:
    """Test the internal async execution logic for a successful run."""
    # Arrange
    mock_run_orm = ProtocolRunOrm(id=TEST_RUN_ID, accession_id=TEST_RUN_ID)
    with patch(
      "praxis.backend.services.read_protocol_run",
      new_callable=AsyncMock,
      return_value=mock_run_orm,
    ) as mock_read, patch(
      "praxis.backend.services.update_protocol_run_status", new_callable=AsyncMock,
    ) as mock_update:
      # Act
      from praxis.backend.core.celery_tasks import _execute_protocol_async

      with patch(
        "praxis.backend.core.celery_tasks._execution_context", execution_context,
      ):
        result = await _execute_protocol_async(
          TEST_RUN_ID, {}, None, TEST_CELERY_TASK_ID,
        )

      # Assert
      mock_read.assert_awaited_once_with(
        execution_context.db_session_factory().__aenter__(),
        run_accession_id=TEST_RUN_ID,
      )
      mock_update.assert_awaited_once_with(
        db=execution_context.db_session_factory().__aenter__(),
        protocol_run_accession_id=TEST_RUN_ID,
        new_status=ProtocolRunStatusEnum.RUNNING,
        output_data_json=ANY,
      )
      execution_context.orchestrator.execute_existing_protocol_run.assert_awaited_once()
      assert result["success"]
      assert result["final_status"] == ProtocolRunStatusEnum.COMPLETED.value

  async def test_async_helper_orchestrator_fails(self, execution_context) -> None:
    """Test that a failure in the orchestrator is caught and handled."""
    # Arrange
    mock_run_orm = ProtocolRunOrm(id=TEST_RUN_ID, accession_id=TEST_RUN_ID)
    execution_context.orchestrator.execute_existing_protocol_run.side_effect = (
      RuntimeError("Test Fail")
    )

    with patch(
      "praxis.backend.services.read_protocol_run",
      new_callable=AsyncMock,
      return_value=mock_run_orm,
    ), patch(
      "praxis.backend.services.update_protocol_run_status", new_callable=AsyncMock,
    ) as mock_update:
      # Act & Assert
      from praxis.backend.core.celery_tasks import _execute_protocol_async

      with patch(
        "praxis.backend.core.celery_tasks._execution_context", execution_context,
      ), pytest.raises(RuntimeError, match="Test Fail"):
        await _execute_protocol_async(TEST_RUN_ID, {}, None, TEST_CELERY_TASK_ID)

      # Assert the final status update was to FAILED
      final_call = mock_update.call_args_list[-1]
      assert final_call.kwargs["new_status"] == ProtocolRunStatusEnum.FAILED


def test_health_check_task() -> None:
  """Test the simple health check task."""
  # Act
  result: EagerResult = health_check.s().apply()  # type: ignore

  # Assert
  assert result.successful()
  assert result.result["status"] == "healthy"
  assert "timestamp" in result.result
