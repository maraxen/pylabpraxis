"""Tests for core/scheduler.py."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from praxis.backend.core.scheduler import ProtocolScheduler, ScheduleEntry
from praxis.backend.models.pydantic_internals.protocol import (
    AssetRequirementModel,
)
from praxis.backend.models.pydantic_internals.runtime import RuntimeAssetRequirement
from praxis.backend.utils.errors import AssetAcquisitionError
from praxis.backend.utils.uuid import uuid7


class TestScheduleEntry:

    """Tests for ScheduleEntry class."""

    def test_schedule_entry_initialization(self) -> None:
        """Test that ScheduleEntry initializes correctly."""
        protocol_run_id = uuid7()
        protocol_name = "test_protocol"
        required_assets = []

        entry = ScheduleEntry(
            protocol_run_id=protocol_run_id,
            protocol_name=protocol_name,
            required_assets=required_assets,
        )

        assert entry.protocol_run_id == protocol_run_id
        assert entry.protocol_name == protocol_name
        assert entry.required_assets == required_assets
        assert entry.estimated_duration_ms is None
        assert entry.priority == 1
        assert entry.status == "QUEUED"
        assert entry.celery_task_id is None

    def test_schedule_entry_with_custom_values(self) -> None:
        """Test ScheduleEntry with custom parameters."""
        protocol_run_id = uuid7()
        required_assets = []

        entry = ScheduleEntry(
            protocol_run_id=protocol_run_id,
            protocol_name="custom_protocol",
            required_assets=required_assets,
            estimated_duration_ms=5000,
            priority=5,
        )

        assert entry.estimated_duration_ms == 5000
        assert entry.priority == 5

    def test_schedule_entry_has_scheduled_at_timestamp(self) -> None:
        """Test that ScheduleEntry sets scheduled_at timestamp."""
        entry = ScheduleEntry(
            protocol_run_id=uuid7(),
            protocol_name="test",
            required_assets=[],
        )

        assert isinstance(entry.scheduled_at, datetime)


class TestProtocolSchedulerInit:

    """Tests for ProtocolScheduler initialization."""

    def test_protocol_scheduler_initialization(self) -> None:
        """Test that ProtocolScheduler initializes correctly."""
        mock_session_factory = Mock()
        mock_task_queue = Mock()
        mock_protocol_run_service = Mock()
        mock_protocol_definition_service = Mock()

        scheduler = ProtocolScheduler(
            db_session_factory=mock_session_factory,
            task_queue=mock_task_queue,
            protocol_run_service=mock_protocol_run_service,
            protocol_definition_service=mock_protocol_definition_service,
        )

        assert scheduler.db_session_factory is mock_session_factory
        assert scheduler.task_queue is mock_task_queue
        assert scheduler.protocol_run_service is mock_protocol_run_service
        assert scheduler.protocol_definition_service is mock_protocol_definition_service

    def test_protocol_scheduler_initializes_empty_schedules(self) -> None:
        """Test that ProtocolScheduler initializes with empty schedules."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        assert isinstance(scheduler._active_schedules, dict)
        assert len(scheduler._active_schedules) == 0

    def test_protocol_scheduler_initializes_empty_reservations(self) -> None:
        """Test that ProtocolScheduler initializes with empty reservations."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        assert isinstance(scheduler._asset_reservations, dict)
        assert len(scheduler._asset_reservations) == 0


class TestAnalyzeProtocolRequirements:

    """Tests for analyze_protocol_requirements method."""

    @pytest.mark.asyncio
    async def test_analyze_protocol_requirements_basic(self) -> None:
        """Test basic protocol requirements analysis."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        # Create mock protocol definition with no assets
        mock_protocol_def = Mock()
        mock_protocol_def.name = "test_protocol"
        mock_protocol_def.version = "1.0.0"
        mock_protocol_def.assets = []
        mock_protocol_def.preconfigure_deck = False
        mock_protocol_def.deck_param_name = None

        requirements = await scheduler.analyze_protocol_requirements(
            mock_protocol_def, {},
        )

        assert isinstance(requirements, list)
        assert len(requirements) == 0

    @pytest.mark.asyncio
    async def test_analyze_protocol_requirements_returns_list(self) -> None:
        """Test that analyze_protocol_requirements returns a list."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        mock_protocol_def = Mock()
        mock_protocol_def.name = "test_protocol"
        mock_protocol_def.version = "1.0.0"
        mock_protocol_def.assets = []
        mock_protocol_def.preconfigure_deck = False

        requirements = await scheduler.analyze_protocol_requirements(
            mock_protocol_def, {},
        )

        assert isinstance(requirements, list)


class TestReserveAssets:

    """Tests for reserve_assets method."""

    @pytest.mark.asyncio
    async def test_reserve_assets_empty_list_succeeds(self) -> None:
        """Test that reserving empty asset list succeeds."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        protocol_run_id = uuid7()
        result = await scheduler.reserve_assets([], protocol_run_id)

        assert result is True

    @pytest.mark.asyncio
    async def test_reserve_assets_single_asset_succeeds(self) -> None:
        """Test that reserving a single available asset succeeds."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        asset_requirement = AssetRequirementModel(
            accession_id=uuid7(),
            name="test_asset",
            fqn="test.Asset",
            type_hint_str="Asset",
        )
        runtime_requirement = RuntimeAssetRequirement(
            asset_definition=asset_requirement,
            asset_type="asset",
            estimated_duration_ms=None,
            priority=1,
        )

        protocol_run_id = uuid7()
        result = await scheduler.reserve_assets([runtime_requirement], protocol_run_id)

        assert result is True
        assert runtime_requirement.reservation_id is not None

    @pytest.mark.asyncio
    async def test_reserve_assets_already_reserved_fails(self) -> None:
        """Test that reserving an already-reserved asset fails."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        asset_requirement = AssetRequirementModel(
            accession_id=uuid7(),
            name="test_asset",
            fqn="test.Asset",
            type_hint_str="Asset",
        )
        runtime_requirement = RuntimeAssetRequirement(
            asset_definition=asset_requirement,
            asset_type="asset",
            estimated_duration_ms=None,
            priority=1,
        )

        # Reserve for first run
        first_run_id = uuid7()
        result1 = await scheduler.reserve_assets([runtime_requirement], first_run_id)
        assert result1 is True

        # Try to reserve for second run - should raise AssetAcquisitionError
        second_run_id = uuid7()
        with pytest.raises(AssetAcquisitionError):
            await scheduler.reserve_assets([runtime_requirement], second_run_id)

    @pytest.mark.asyncio
    async def test_reserve_assets_multiple_assets_succeeds(self) -> None:
        """Test that reserving multiple available assets succeeds."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        requirements = [
            RuntimeAssetRequirement(
                asset_definition=AssetRequirementModel(
                    accession_id=uuid7(),
                    name=f"asset{i}",
                    fqn="test.Asset",
                    type_hint_str="Asset",
                ),
                asset_type="asset",
                estimated_duration_ms=None,
                priority=1,
            )
            for i in range(3)
        ]

        protocol_run_id = uuid7()
        result = await scheduler.reserve_assets(requirements, protocol_run_id)

        assert result is True
        for req in requirements:
            assert req.reservation_id is not None


class TestCancelScheduledRun:

    """Tests for cancel_scheduled_run method."""

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_run_returns_false(self) -> None:
        """Test that canceling nonexistent run returns False."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        nonexistent_id = uuid7()
        result = await scheduler.cancel_scheduled_run(nonexistent_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_cancel_scheduled_run_removes_from_active(self) -> None:
        """Test that canceling a run removes it from active schedules."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        protocol_run_id = uuid7()
        schedule_entry = ScheduleEntry(
            protocol_run_id=protocol_run_id,
            protocol_name="test",
            required_assets=[],
        )
        scheduler._active_schedules[protocol_run_id] = schedule_entry

        result = await scheduler.cancel_scheduled_run(protocol_run_id)

        assert result is True
        assert protocol_run_id not in scheduler._active_schedules

    @pytest.mark.asyncio
    async def test_cancel_scheduled_run_releases_assets(self) -> None:
        """Test that canceling a run releases asset reservations."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        # Create and reserve an asset
        asset_requirement = AssetRequirementModel(
            accession_id=uuid7(),
            name="test_asset",
            fqn="test.Asset",
            type_hint_str="Asset",
        )
        runtime_requirement = RuntimeAssetRequirement(
            asset_definition=asset_requirement,
            asset_type="asset",
            estimated_duration_ms=None,
            priority=1,
        )

        protocol_run_id = uuid7()
        await scheduler.reserve_assets([runtime_requirement], protocol_run_id)

        # Create schedule entry
        schedule_entry = ScheduleEntry(
            protocol_run_id=protocol_run_id,
            protocol_name="test",
            required_assets=[runtime_requirement],
        )
        scheduler._active_schedules[protocol_run_id] = schedule_entry

        # Cancel should release reservations
        result = await scheduler.cancel_scheduled_run(protocol_run_id)

        assert result is True
        asset_key = "asset:test_asset"
        assert asset_key not in scheduler._asset_reservations


class TestGetScheduleStatus:

    """Tests for get_schedule_status method."""

    @pytest.mark.asyncio
    async def test_get_schedule_status_nonexistent_returns_none(self) -> None:
        """Test that getting status for nonexistent run returns None."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        nonexistent_id = uuid7()
        result = await scheduler.get_schedule_status(nonexistent_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_schedule_status_returns_dict(self) -> None:
        """Test that get_schedule_status returns status dictionary."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        protocol_run_id = uuid7()
        schedule_entry = ScheduleEntry(
            protocol_run_id=protocol_run_id,
            protocol_name="test_protocol",
            required_assets=[],
            estimated_duration_ms=5000,
            priority=3,
        )
        scheduler._active_schedules[protocol_run_id] = schedule_entry

        result = await scheduler.get_schedule_status(protocol_run_id)

        assert result is not None
        assert result["protocol_run_id"] == str(protocol_run_id)
        assert result["protocol_name"] == "test_protocol"
        assert result["status"] == "QUEUED"
        assert result["asset_count"] == 0
        assert result["estimated_duration_ms"] == 5000
        assert result["priority"] == 3
        assert "scheduled_at" in result


class TestListActiveSchedules:

    """Tests for list_active_schedules method."""

    @pytest.mark.asyncio
    async def test_list_active_schedules_empty(self) -> None:
        """Test that list_active_schedules returns empty list initially."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        result = await scheduler.list_active_schedules()

        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_list_active_schedules_returns_all_schedules(self) -> None:
        """Test that list_active_schedules returns all active schedules."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        # Add multiple schedule entries
        for i in range(3):
            protocol_run_id = uuid7()
            schedule_entry = ScheduleEntry(
                protocol_run_id=protocol_run_id,
                protocol_name=f"protocol_{i}",
                required_assets=[],
            )
            scheduler._active_schedules[protocol_run_id] = schedule_entry

        result = await scheduler.list_active_schedules()

        assert len(result) == 3
        assert all(isinstance(item, dict) for item in result)

    @pytest.mark.asyncio
    async def test_list_active_schedules_sorted_by_time(self) -> None:
        """Test that list_active_schedules returns schedules sorted by time."""
        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=Mock(),
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        # Add schedule entries
        for i in range(3):
            protocol_run_id = uuid7()
            schedule_entry = ScheduleEntry(
                protocol_run_id=protocol_run_id,
                protocol_name=f"protocol_{i}",
                required_assets=[],
            )
            scheduler._active_schedules[protocol_run_id] = schedule_entry

        result = await scheduler.list_active_schedules()

        # Verify sorted by scheduled_at
        for i in range(len(result) - 1):
            assert result[i]["scheduled_at"] <= result[i + 1]["scheduled_at"]


class TestQueueExecutionTask:

    """Tests for _queue_execution_task method."""

    @pytest.mark.asyncio
    async def test_queue_execution_task_success(self) -> None:
        """Test successful queueing of execution task."""
        mock_task_result = Mock()
        mock_task_result.id = "celery_task_123"

        mock_task_queue = Mock()
        mock_task_queue.send_task = Mock(return_value=mock_task_result)

        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=mock_task_queue,
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        protocol_run_id = uuid7()
        result = await scheduler._queue_execution_task(
            protocol_run_id, {"param": "value"}, None,
        )

        assert result is True
        mock_task_queue.send_task.assert_called_once()

    @pytest.mark.asyncio
    async def test_queue_execution_task_sets_celery_id_in_schedule(self) -> None:
        """Test that queueing sets celery_task_id in schedule entry."""
        mock_task_result = Mock()
        mock_task_result.id = "celery_task_456"

        mock_task_queue = Mock()
        mock_task_queue.send_task = Mock(return_value=mock_task_result)

        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=mock_task_queue,
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        protocol_run_id = uuid7()
        schedule_entry = ScheduleEntry(
            protocol_run_id=protocol_run_id,
            protocol_name="test",
            required_assets=[],
        )
        scheduler._active_schedules[protocol_run_id] = schedule_entry

        result = await scheduler._queue_execution_task(protocol_run_id, {}, None)

        assert result is True
        assert schedule_entry.celery_task_id == "celery_task_456"

    @pytest.mark.asyncio
    async def test_queue_execution_task_handles_exception(self) -> None:
        """Test that queueing handles exceptions gracefully."""
        mock_task_queue = Mock()
        mock_task_queue.send_task = Mock(side_effect=Exception("Queue error"))

        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=mock_task_queue,
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        protocol_run_id = uuid7()
        result = await scheduler._queue_execution_task(protocol_run_id, {}, None)

        assert result is False


class TestProtocolSchedulerIntegration:

    """Integration tests for ProtocolScheduler."""

    @pytest.mark.asyncio
    async def test_complete_scheduling_workflow(self) -> None:
        """Test complete workflow: analyze, reserve, schedule."""
        mock_task_result = Mock()
        mock_task_result.id = "task_id"

        mock_task_queue = Mock()
        mock_task_queue.send_task = Mock(return_value=mock_task_result)

        scheduler = ProtocolScheduler(
            db_session_factory=Mock(),
            task_queue=mock_task_queue,
            protocol_run_service=Mock(),
            protocol_definition_service=Mock(),
        )

        # Create mock protocol definition
        mock_protocol_def = Mock()
        mock_protocol_def.name = "test_protocol"
        mock_protocol_def.version = "1.0.0"
        mock_protocol_def.assets = []
        mock_protocol_def.preconfigure_deck = False
        mock_protocol_def.deck_param_name = None

        # Analyze requirements
        requirements = await scheduler.analyze_protocol_requirements(
            mock_protocol_def, {},
        )

        # Reserve assets
        protocol_run_id = uuid7()
        reserve_result = await scheduler.reserve_assets(requirements, protocol_run_id)
        assert reserve_result is True

        # Queue execution
        queue_result = await scheduler._queue_execution_task(
            protocol_run_id, {}, None,
        )
        assert queue_result is True
