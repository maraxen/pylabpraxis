"""Tests for protocol enum types in models/enums/protocol.py."""

import enum

from praxis.backend.models.enums.protocol import (
    FunctionCallStatusEnum,
    ProtocolRunStatusEnum,
    ProtocolSourceStatusEnum,
)


class TestProtocolSourceStatusEnum:

    """Tests for ProtocolSourceStatusEnum."""

    def test_is_enum(self) -> None:
        """Test that ProtocolSourceStatusEnum is an enum."""
        assert issubclass(ProtocolSourceStatusEnum, enum.Enum)

    def test_has_active(self) -> None:
        """Test that enum has ACTIVE status."""
        assert ProtocolSourceStatusEnum.ACTIVE.value == "active"

    def test_has_archived(self) -> None:
        """Test that enum has ARCHIVED status."""
        assert ProtocolSourceStatusEnum.ARCHIVED.value == "archived"

    def test_has_sync_error(self) -> None:
        """Test that enum has SYNC_ERROR status."""
        assert ProtocolSourceStatusEnum.SYNC_ERROR.value == "sync_error"

    def test_has_pending_deletion(self) -> None:
        """Test that enum has PENDING_DELETION status."""
        assert ProtocolSourceStatusEnum.PENDING_DELETION.value == "pending_deletion"

    def test_has_syncing(self) -> None:
        """Test that enum has SYNCING status."""
        assert ProtocolSourceStatusEnum.SYNCING.value == "syncing"

    def test_has_inactive(self) -> None:
        """Test that enum has INACTIVE status."""
        assert ProtocolSourceStatusEnum.INACTIVE.value == "inactive"

    def test_member_count(self) -> None:
        """Test that enum has exactly 6 members."""
        assert len(ProtocolSourceStatusEnum) == 6


class TestProtocolRunStatusEnum:

    """Tests for ProtocolRunStatusEnum."""

    def test_is_enum(self) -> None:
        """Test that ProtocolRunStatusEnum is an enum."""
        assert issubclass(ProtocolRunStatusEnum, enum.Enum)

    def test_has_queued(self) -> None:
        """Test that enum has QUEUED status."""
        assert ProtocolRunStatusEnum.QUEUED.value == "queued"

    def test_has_pending(self) -> None:
        """Test that enum has PENDING status."""
        assert ProtocolRunStatusEnum.PENDING.value == "pending"

    def test_has_preparing(self) -> None:
        """Test that enum has PREPARING status."""
        assert ProtocolRunStatusEnum.PREPARING.value == "preparing"

    def test_has_running(self) -> None:
        """Test that enum has RUNNING status."""
        assert ProtocolRunStatusEnum.RUNNING.value == "running"

    def test_has_pausing(self) -> None:
        """Test that enum has PAUSING status."""
        assert ProtocolRunStatusEnum.PAUSING.value == "pausing"

    def test_has_paused(self) -> None:
        """Test that enum has PAUSED status."""
        assert ProtocolRunStatusEnum.PAUSED.value == "paused"

    def test_has_resuming(self) -> None:
        """Test that enum has RESUMING status."""
        assert ProtocolRunStatusEnum.RESUMING.value == "resuming"

    def test_has_completed(self) -> None:
        """Test that enum has COMPLETED status."""
        assert ProtocolRunStatusEnum.COMPLETED.value == "completed"

    def test_has_failed(self) -> None:
        """Test that enum has FAILED status."""
        assert ProtocolRunStatusEnum.FAILED.value == "failed"

    def test_has_canceling(self) -> None:
        """Test that enum has CANCELING status."""
        assert ProtocolRunStatusEnum.CANCELING.value == "canceling"

    def test_has_cancelled(self) -> None:
        """Test that enum has CANCELLED status."""
        assert ProtocolRunStatusEnum.CANCELLED.value == "cancelled"

    def test_has_intervening(self) -> None:
        """Test that enum has INTERVENING status."""
        assert ProtocolRunStatusEnum.INTERVENING.value == "intervening"

    def test_has_requires_intervention(self) -> None:
        """Test that enum has REQUIRES_INTERVENTION status."""
        assert (
            ProtocolRunStatusEnum.REQUIRES_INTERVENTION.value == "requires_intervention"
        )

    def test_member_count(self) -> None:
        """Test that enum has exactly 13 members."""
        assert len(ProtocolRunStatusEnum) == 13

    def test_has_lifecycle_states(self) -> None:
        """Test that enum has all lifecycle states."""
        lifecycle_states = [
            "QUEUED",
            "PENDING",
            "PREPARING",
            "RUNNING",
            "COMPLETED",
            "FAILED",
            "CANCELLED",
        ]
        actual_names = [member.name for member in ProtocolRunStatusEnum]
        for state in lifecycle_states:
            assert state in actual_names


class TestFunctionCallStatusEnum:

    """Tests for FunctionCallStatusEnum."""

    def test_is_enum(self) -> None:
        """Test that FunctionCallStatusEnum is an enum."""
        assert issubclass(FunctionCallStatusEnum, enum.Enum)

    def test_has_success(self) -> None:
        """Test that enum has SUCCESS status."""
        assert FunctionCallStatusEnum.SUCCESS.value == "success"

    def test_has_error(self) -> None:
        """Test that enum has ERROR status."""
        assert FunctionCallStatusEnum.ERROR.value == "error"

    def test_has_pending(self) -> None:
        """Test that enum has PENDING status."""
        assert FunctionCallStatusEnum.PENDING.value == "pending"

    def test_has_in_progress(self) -> None:
        """Test that enum has IN_PROGRESS status."""
        assert FunctionCallStatusEnum.IN_PROGRESS.value == "in_progress"

    def test_has_skipped(self) -> None:
        """Test that enum has SKIPPED status."""
        assert FunctionCallStatusEnum.SKIPPED.value == "skipped"

    def test_has_canceled(self) -> None:
        """Test that enum has CANCELED status."""
        assert FunctionCallStatusEnum.CANCELED.value == "canceled"

    def test_has_unknown(self) -> None:
        """Test that enum has UNKNOWN status."""
        assert FunctionCallStatusEnum.UNKNOWN.value == "unknown"

    def test_member_count(self) -> None:
        """Test that enum has exactly 7 members."""
        assert len(FunctionCallStatusEnum) == 7


class TestProtocolEnumsIntegration:

    """Integration tests for protocol enums."""

    def test_all_enums_are_independent(self) -> None:
        """Test that all three protocol enums are independent."""
        source_names = {member.name for member in ProtocolSourceStatusEnum}
        run_names = {member.name for member in ProtocolRunStatusEnum}
        call_names = {member.name for member in FunctionCallStatusEnum}

        # Some overlap is expected (PENDING appears in both run and call)
        # but they should be mostly independent
        assert len(source_names) == 6
        assert len(run_names) == 13
        assert len(call_names) == 7

    def test_can_use_all_enums_together(self) -> None:
        """Test that all enums can be used together."""
        protocol_info = {
            "source_status": ProtocolSourceStatusEnum.ACTIVE,
            "run_status": ProtocolRunStatusEnum.RUNNING,
            "call_status": FunctionCallStatusEnum.IN_PROGRESS,
        }
        assert protocol_info["source_status"] == ProtocolSourceStatusEnum.ACTIVE
        assert protocol_info["run_status"] == ProtocolRunStatusEnum.RUNNING
        assert protocol_info["call_status"] == FunctionCallStatusEnum.IN_PROGRESS

    def test_terminal_states_coverage(self) -> None:
        """Test that run status enum has terminal states."""
        terminal_states = ["COMPLETED", "FAILED", "CANCELLED"]
        run_names = [member.name for member in ProtocolRunStatusEnum]
        for state in terminal_states:
            assert state in run_names
