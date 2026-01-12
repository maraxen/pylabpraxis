"""Tests for core/celery_tasks.py."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest

from praxis.backend.core.celery_tasks import health_check
from praxis.backend.models import ProtocolRunStatusEnum
from praxis.backend.utils.uuid import uuid7


class TestHealthCheck:

    """Tests for health_check Celery task."""

    @pytest.mark.slow
    def test_health_check_returns_dict(self) -> None:
        """Test that health_check returns a dictionary."""
        result = health_check()
        assert isinstance(result, dict)

    @pytest.mark.slow
    def test_health_check_has_status(self) -> None:
        """Test that health_check returns status field."""
        result = health_check()
        assert "status" in result
        assert result["status"] == "healthy"

    @pytest.mark.slow
    def test_health_check_has_timestamp(self) -> None:
        """Test that health_check returns timestamp field."""
        result = health_check()
        assert "timestamp" in result
        assert isinstance(result["timestamp"], str)

    @pytest.mark.slow
    def test_health_check_timestamp_is_valid_iso_format(self) -> None:
        """Test that timestamp is valid ISO format."""
        result = health_check()
        # Should not raise exception
        datetime.fromisoformat(result["timestamp"])


class TestCeleryTaskRegistration:

    """Tests for Celery task registration."""

    @pytest.mark.slow
    def test_health_check_is_registered_task(self) -> None:
        """Test that health_check is registered as Celery task."""
        assert hasattr(health_check, "name")
        assert health_check.name == "health_check"

    @pytest.mark.slow
    def test_execute_protocol_run_task_is_registered(self) -> None:
        """Test that execute_protocol_run_task is registered."""
        from praxis.backend.core.celery_tasks import execute_protocol_run_task

        assert callable(execute_protocol_run_task)
        assert hasattr(execute_protocol_run_task, "name")
        assert execute_protocol_run_task.name == "execute_protocol_run"


class TestCeleryTasksModuleStructure:

    """Tests for module structure and exports."""

    @pytest.mark.slow
    def test_module_exports_execute_protocol_run_task(self) -> None:
        """Test that module exports execute_protocol_run_task."""
        from praxis.backend.core import celery_tasks

        assert hasattr(celery_tasks, "execute_protocol_run_task")

    @pytest.mark.slow
    def test_module_exports_health_check(self) -> None:
        """Test that module exports health_check."""
        from praxis.backend.core import celery_tasks

        assert hasattr(celery_tasks, "health_check")

    @pytest.mark.slow
    def test_module_has_task_logger(self) -> None:
        """Test that module defines task_logger."""
        from praxis.backend.core import celery_tasks

        assert hasattr(celery_tasks, "task_logger")

    @pytest.mark.slow
    def test_module_has_logger(self) -> None:
        """Test that module defines logger."""
        from praxis.backend.core import celery_tasks

        assert hasattr(celery_tasks, "logger")


class TestExecuteProtocolRunTaskStructure:

    """Tests for execute_protocol_run_task structure without DI complexity."""

    @pytest.mark.slow
    def test_execute_protocol_run_task_has_bind_parameter(self) -> None:
        """Test that execute_protocol_run_task is bound to task instance."""
        from praxis.backend.core.celery_tasks import execute_protocol_run_task

        # Celery bound tasks have bind=True
        assert hasattr(execute_protocol_run_task, "run")

    @pytest.mark.slow
    def test_execute_protocol_run_task_signature(self) -> None:
        """Test that execute_protocol_run_task has expected parameters."""
        import inspect

        from praxis.backend.core.celery_tasks import execute_protocol_run_task

        # Get function signature
        sig = inspect.signature(execute_protocol_run_task.run)
        params = list(sig.parameters.keys())

        # Should have key protocol parameters
        assert "protocol_run_id" in params
        assert "input_parameters" in params
        assert "initial_state" in params
        assert "orchestrator" in params


class TestUpdateRunStatusOnErrorInternal:

    """Tests for _update_run_status_on_error helper."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_update_run_status_on_error_basic_structure(self) -> None:
        """Test basic structure of _update_run_status_on_error."""
        from praxis.backend.core.celery_tasks import _update_run_status_on_error

        protocol_run_id = uuid7()
        error_message = "Test error"

        # Create async session mock
        mock_db_session = AsyncMock()
        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__.return_value = mock_db_session
        mock_session_ctx.__aexit__.return_value = None

        mock_session_factory = Mock(return_value=mock_session_ctx)

        mock_service = Mock()
        mock_service.update_run_status = AsyncMock()

        # Should not raise
        await _update_run_status_on_error(
            protocol_run_id,
            error_message,
            mock_session_factory,
            mock_service,
        )

        # Verify update was called
        mock_service.update_run_status.assert_called_once()

        # Verify FAILED status
        call_kwargs = mock_service.update_run_status.call_args[1]
        assert call_kwargs["new_status"] == ProtocolRunStatusEnum.FAILED

        # Verify commit
        mock_db_session.commit.assert_called_once()


class TestExecuteProtocolAsyncInternal:

    """Tests for _execute_protocol_async helper."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_execute_protocol_async_calls_orchestrator(self) -> None:
        """Test that _execute_protocol_async calls orchestrator."""
        from praxis.backend.core.celery_tasks import _execute_protocol_async

        protocol_run_id = uuid7()

        # Create async session mock
        mock_db_session = AsyncMock()
        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__.return_value = mock_db_session
        mock_session_ctx.__aexit__.return_value = None

        mock_session_factory = Mock(return_value=mock_session_ctx)

        mock_run_model = Mock()
        mock_run_model.accession_id = protocol_run_id
        mock_run_model.status = ProtocolRunStatusEnum.COMPLETED

        mock_service = Mock()
        mock_service.get = AsyncMock(return_value=mock_run_model)
        mock_service.update_run_status = AsyncMock()

        mock_orchestrator = Mock()
        mock_orchestrator.execute_existing_protocol_run = AsyncMock(
            return_value=mock_run_model,
        )

        result = await _execute_protocol_async(
            protocol_run_id,
            {"param": "value"},
            None,
            "task_id",
            mock_orchestrator,
            mock_session_factory,
            mock_service,
        )

        # Verify orchestrator was called
        mock_orchestrator.execute_existing_protocol_run.assert_called_once()

        # Verify success result
        assert result["success"] is True
        assert result["protocol_run_id"] == str(protocol_run_id)


class TestCeleryTaskIntegration:

    """Integration tests for Celery task module."""

    @pytest.mark.slow
    def test_celery_app_has_tasks_registered(self) -> None:
        """Test that celery_app has the tasks registered."""
        from praxis.backend.core.celery import celery_app

        # Check that tasks are in celery app registry
        task_names = [task.name for task in celery_app.tasks.values()]

        assert "execute_protocol_run" in task_names
        assert "health_check" in task_names

    @pytest.mark.slow
    def test_tasks_have_celery_app_reference(self) -> None:
        """Test that tasks reference the correct celery_app."""
        from praxis.backend.core.celery import celery_app
        from praxis.backend.core.celery_tasks import health_check

        # Task should have reference to the app
        assert hasattr(health_check, "app")
        assert health_check.app == celery_app
