# pylint: disable=redefined-outer-name, protected-access
"""Unit tests for Celery tasks."""

import uuid
from typing import TYPE_CHECKING
from unittest.mock import ANY, AsyncMock, MagicMock

import pytest

from praxis.backend.core.celery_tasks import (
    health_check,
)
from praxis.backend.models import ProtocolRunOrm, ProtocolRunStatusEnum
from praxis.backend.services.protocols import ProtocolRunService

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


@pytest.fixture
def mock_protocol_run_service():
    """Provides a mock ProtocolRunService."""
    service = MagicMock(spec=ProtocolRunService)
    service.get = AsyncMock()
    service.update_run_status = AsyncMock()
    return service


# --- Tests ---


@pytest.mark.asyncio
class TestExecuteProtocolRunTask:
    """Test suite for the main protocol execution Celery task."""

    async def test_async_helper_happy_path(
        self, mock_orchestrator, mock_db_session_factory, mock_protocol_run_service
    ) -> None:
        """Test the internal async execution logic for a successful run."""
        mock_run_orm = MagicMock(spec=ProtocolRunOrm)
        mock_run_orm.accession_id = TEST_RUN_ID
        mock_protocol_run_service.get.return_value = mock_run_orm

        from praxis.backend.core.celery_tasks import _execute_protocol_async

        result = await _execute_protocol_async(
            TEST_RUN_ID,
            {},
            None,
            TEST_CELERY_TASK_ID,
            mock_orchestrator,
            mock_db_session_factory,
            mock_protocol_run_service,
        )

        mock_protocol_run_service.get.assert_awaited_once_with(ANY, accession_id=TEST_RUN_ID)
        assert mock_protocol_run_service.update_run_status.await_count > 0
        mock_orchestrator.execute_existing_protocol_run.assert_awaited_once()
        assert result["success"]
        assert result["final_status"] == ProtocolRunStatusEnum.COMPLETED.value

    async def test_async_helper_orchestrator_fails(
        self, mock_orchestrator, mock_db_session_factory, mock_protocol_run_service
    ) -> None:
        """Test that a failure in the orchestrator is caught and handled."""
        mock_run_orm = MagicMock(spec=ProtocolRunOrm)
        mock_run_orm.accession_id = TEST_RUN_ID
        mock_protocol_run_service.get.return_value = mock_run_orm
        mock_orchestrator.execute_existing_protocol_run.side_effect = RuntimeError("Test Fail")

        from praxis.backend.core.celery_tasks import _execute_protocol_async

        with pytest.raises(RuntimeError, match="Test Fail"):
            await _execute_protocol_async(
                TEST_RUN_ID,
                {},
                None,
                TEST_CELERY_TASK_ID,
                mock_orchestrator,
                mock_db_session_factory,
                mock_protocol_run_service,
            )

        final_call = mock_protocol_run_service.update_run_status.call_args_list[-1]
        assert final_call.kwargs["new_status"] == ProtocolRunStatusEnum.FAILED


def test_health_check_task() -> None:
    """Test the simple health check task."""
    # Act
    result: EagerResult = health_check.s().apply()

    # Assert
    assert result.successful()
    assert result.result["status"] == "healthy"
    assert "timestamp" in result.result