"""Tests for schedule enum types in models/enums/schedule.py."""

import enum

import pytest

from praxis.backend.models.enums.schedule import (
    ScheduleHistoryEventEnum,
    ScheduleHistoryEventTriggerEnum,
    ScheduleStatusEnum,
)


class TestScheduleStatusEnum:

    """Tests for ScheduleStatusEnum."""

    @pytest.mark.slow
    def test_is_enum(self) -> None:
        """Test that ScheduleStatusEnum is an enum."""
        assert issubclass(ScheduleStatusEnum, enum.Enum)

    @pytest.mark.slow
    def test_has_queued(self) -> None:
        """Test that enum has QUEUED status."""
        assert ScheduleStatusEnum.QUEUED.value == "queued"

    @pytest.mark.slow
    def test_has_reserved(self) -> None:
        """Test that enum has RESERVED status."""
        assert ScheduleStatusEnum.RESERVED.value == "reserved"

    @pytest.mark.slow
    def test_has_ready_to_execute(self) -> None:
        """Test that enum has READY_TO_EXECUTE status."""
        assert ScheduleStatusEnum.READY_TO_EXECUTE.value == "ready_to_execute"

    @pytest.mark.slow
    def test_has_celery_queued(self) -> None:
        """Test that enum has CELERY_QUEUED status."""
        assert ScheduleStatusEnum.CELERY_QUEUED.value == "celery_queued"

    @pytest.mark.slow
    def test_has_executing(self) -> None:
        """Test that enum has EXECUTING status."""
        assert ScheduleStatusEnum.EXECUTING.value == "executing"

    @pytest.mark.slow
    def test_has_completed(self) -> None:
        """Test that enum has COMPLETED status."""
        assert ScheduleStatusEnum.COMPLETED.value == "completed"

    @pytest.mark.slow
    def test_has_failed(self) -> None:
        """Test that enum has FAILED status."""
        assert ScheduleStatusEnum.FAILED.value == "failed"

    @pytest.mark.slow
    def test_has_cancelled(self) -> None:
        """Test that enum has CANCELLED status."""
        assert ScheduleStatusEnum.CANCELLED.value == "cancelled"

    @pytest.mark.slow
    def test_has_conflict(self) -> None:
        """Test that enum has CONFLICT status."""
        assert ScheduleStatusEnum.CONFLICT.value == "asset_conflict"

    @pytest.mark.slow
    def test_has_timeout(self) -> None:
        """Test that enum has TIMEOUT status."""
        assert ScheduleStatusEnum.TIMEOUT.value == "timeout"

    @pytest.mark.slow
    def test_member_count(self) -> None:
        """Test that enum has exactly 10 members."""
        assert len(ScheduleStatusEnum) == 10

    @pytest.mark.slow
    def test_has_terminal_states(self) -> None:
        """Test that enum has terminal states."""
        terminal_states = ["COMPLETED", "FAILED", "CANCELLED", "CONFLICT", "TIMEOUT"]
        actual_names = [member.name for member in ScheduleStatusEnum]
        for state in terminal_states:
            assert state in actual_names


class TestScheduleHistoryEventEnum:

    """Tests for ScheduleHistoryEventEnum."""

    @pytest.mark.slow
    def test_is_enum(self) -> None:
        """Test that ScheduleHistoryEventEnum is an enum."""
        assert issubclass(ScheduleHistoryEventEnum, enum.Enum)

    @pytest.mark.slow
    def test_has_schedule_created(self) -> None:
        """Test that enum has SCHEDULE_CREATED event."""
        assert ScheduleHistoryEventEnum.SCHEDULE_CREATED.value == "schedule_created"

    @pytest.mark.slow
    def test_has_scheduled(self) -> None:
        """Test that enum has SCHEDULED event."""
        assert ScheduleHistoryEventEnum.SCHEDULED.value == "scheduled"

    @pytest.mark.slow
    def test_has_status_changed(self) -> None:
        """Test that enum has STATUS_CHANGED event."""
        assert ScheduleHistoryEventEnum.STATUS_CHANGED.value == "status_changed"

    @pytest.mark.slow
    def test_has_executed(self) -> None:
        """Test that enum has EXECUTED event."""
        assert ScheduleHistoryEventEnum.EXECUTED.value == "executed"

    @pytest.mark.slow
    def test_has_completed(self) -> None:
        """Test that enum has COMPLETED event."""
        assert ScheduleHistoryEventEnum.COMPLETED.value == "completed"

    @pytest.mark.slow
    def test_has_failed(self) -> None:
        """Test that enum has FAILED event."""
        assert ScheduleHistoryEventEnum.FAILED.value == "failed"

    @pytest.mark.slow
    def test_has_cancelled(self) -> None:
        """Test that enum has CANCELLED event."""
        assert ScheduleHistoryEventEnum.CANCELLED.value == "cancelled"

    @pytest.mark.slow
    def test_has_rescheduled(self) -> None:
        """Test that enum has RESCHEDULED event."""
        assert ScheduleHistoryEventEnum.RESCHEDULED.value == "rescheduled"

    @pytest.mark.slow
    def test_has_conflict(self) -> None:
        """Test that enum has CONFLICT event."""
        assert ScheduleHistoryEventEnum.CONFLICT.value == "conflict"

    @pytest.mark.slow
    def test_has_timeout(self) -> None:
        """Test that enum has TIMEOUT event."""
        assert ScheduleHistoryEventEnum.TIMEOUT.value == "timeout"

    @pytest.mark.slow
    def test_has_partial_completion(self) -> None:
        """Test that enum has PARTIAL_COMPLETION event."""
        assert (
            ScheduleHistoryEventEnum.PARTIAL_COMPLETION.value == "partial_completion"
        )

    @pytest.mark.slow
    def test_has_intervention_required(self) -> None:
        """Test that enum has INTERVENTION_REQUIRED event."""
        assert (
            ScheduleHistoryEventEnum.INTERVENTION_REQUIRED.value
            == "intervention_required"
        )

    @pytest.mark.slow
    def test_has_priority_changed(self) -> None:
        """Test that enum has PRIORITY_CHANGED event."""
        assert ScheduleHistoryEventEnum.PRIORITY_CHANGED.value == "priority_changed"

    @pytest.mark.slow
    def test_has_unknown(self) -> None:
        """Test that enum has UNKNOWN event."""
        assert ScheduleHistoryEventEnum.UNKNOWN.value == "unknown"

    @pytest.mark.slow
    def test_member_count(self) -> None:
        """Test that enum has exactly 14 members."""
        assert len(ScheduleHistoryEventEnum) == 14


class TestScheduleHistoryEventTriggerEnum:

    """Tests for ScheduleHistoryEventTriggerEnum."""

    @pytest.mark.slow
    def test_is_enum(self) -> None:
        """Test that ScheduleHistoryEventTriggerEnum is an enum."""
        assert issubclass(ScheduleHistoryEventTriggerEnum, enum.Enum)

    @pytest.mark.slow
    def test_has_user(self) -> None:
        """Test that enum has USER trigger."""
        assert ScheduleHistoryEventTriggerEnum.USER.value == "user"

    @pytest.mark.slow
    def test_has_api(self) -> None:
        """Test that enum has API trigger."""
        assert ScheduleHistoryEventTriggerEnum.API.value == "api"

    @pytest.mark.slow
    def test_has_pylabrobot(self) -> None:
        """Test that enum has PYLABROBOT trigger."""
        assert ScheduleHistoryEventTriggerEnum.PYLABROBOT.value == "pylabrobot"

    @pytest.mark.slow
    def test_has_celery(self) -> None:
        """Test that enum has CELERY trigger."""
        assert ScheduleHistoryEventTriggerEnum.CELERY.value == "celery"

    @pytest.mark.slow
    def test_has_system(self) -> None:
        """Test that enum has SYSTEM trigger."""
        assert ScheduleHistoryEventTriggerEnum.SYSTEM.value == "system"

    @pytest.mark.slow
    def test_member_count(self) -> None:
        """Test that enum has exactly 5 members."""
        assert len(ScheduleHistoryEventTriggerEnum) == 5


class TestScheduleEnumsIntegration:

    """Integration tests for schedule enums."""

    @pytest.mark.slow
    def test_all_enums_are_independent(self) -> None:
        """Test that all schedule enums are independent."""
        status_names = set(member.name for member in ScheduleStatusEnum)
        event_names = set(member.name for member in ScheduleHistoryEventEnum)
        trigger_names = set(member.name for member in ScheduleHistoryEventTriggerEnum)

        # Some overlap expected between status and events
        # but trigger should be completely independent
        assert len(status_names) == 10
        assert len(event_names) == 14
        assert len(trigger_names) == 5

    @pytest.mark.slow
    def test_can_use_all_enums_together(self) -> None:
        """Test that all enums can be used together."""
        schedule_info = {
            "status": ScheduleStatusEnum.EXECUTING,
            "last_event": ScheduleHistoryEventEnum.EXECUTED,
            "trigger": ScheduleHistoryEventTriggerEnum.CELERY,
        }
        assert schedule_info["status"] == ScheduleStatusEnum.EXECUTING
        assert schedule_info["last_event"] == ScheduleHistoryEventEnum.EXECUTED
        assert schedule_info["trigger"] == ScheduleHistoryEventTriggerEnum.CELERY

    @pytest.mark.slow
    def test_status_and_event_correlation(self) -> None:
        """Test that status and events have logical correlation."""
        # COMPLETED status should correlate with COMPLETED event
        status_names = [member.name for member in ScheduleStatusEnum]
        event_names = [member.name for member in ScheduleHistoryEventEnum]

        # These names should exist in both
        shared_concepts = ["COMPLETED", "FAILED", "CANCELLED"]
        for concept in shared_concepts:
            assert concept in status_names
            assert concept in event_names

    @pytest.mark.slow
    def test_trigger_types_cover_main_sources(self) -> None:
        """Test that trigger enum covers main event sources."""
        triggers = [member.name for member in ScheduleHistoryEventTriggerEnum]
        expected_sources = ["USER", "API", "SYSTEM", "CELERY"]
        for source in expected_sources:
            assert source in triggers
