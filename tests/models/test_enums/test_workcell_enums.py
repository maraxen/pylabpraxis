"""Tests for workcell enum types in models/enums/workcell.py."""

import enum

from praxis.backend.models.enums.workcell import WorkcellStatusEnum


class TestWorkcellStatusEnum:

    """Tests for WorkcellStatusEnum."""

    def test_is_enum(self) -> None:
        """Test that WorkcellStatusEnum is an enum."""
        assert issubclass(WorkcellStatusEnum, enum.Enum)

    def test_has_active(self) -> None:
        """Test that enum has ACTIVE status."""
        assert WorkcellStatusEnum.ACTIVE.value == "active"

    def test_has_in_use(self) -> None:
        """Test that enum has IN_USE status."""
        assert WorkcellStatusEnum.IN_USE.value == "in_use"

    def test_has_reserved(self) -> None:
        """Test that enum has RESERVED status."""
        assert WorkcellStatusEnum.RESERVED.value == "reserved"

    def test_has_available(self) -> None:
        """Test that enum has AVAILABLE status."""
        assert WorkcellStatusEnum.AVAILABLE.value == "available"

    def test_has_error(self) -> None:
        """Test that enum has ERROR status."""
        assert WorkcellStatusEnum.ERROR.value == "error"

    def test_has_inactive(self) -> None:
        """Test that enum has INACTIVE status."""
        assert WorkcellStatusEnum.INACTIVE.value == "inactive"

    def test_has_maintenance(self) -> None:
        """Test that enum has MAINTENANCE status."""
        assert WorkcellStatusEnum.MAINTENANCE.value == "maintenance"

    def test_member_count(self) -> None:
        """Test that enum has exactly 7 members."""
        assert len(WorkcellStatusEnum) == 7

    def test_all_members_have_unique_values(self) -> None:
        """Test that all members have unique values."""
        values = [member.value for member in WorkcellStatusEnum]
        assert len(values) == len(set(values))

    def test_can_iterate_over_enum(self) -> None:
        """Test that enum can be iterated."""
        statuses = list(WorkcellStatusEnum)
        assert len(statuses) == 7
        assert WorkcellStatusEnum.ACTIVE in statuses

    def test_can_access_by_name(self) -> None:
        """Test that enum members can be accessed by name."""
        assert WorkcellStatusEnum["ACTIVE"] == WorkcellStatusEnum.ACTIVE
        assert WorkcellStatusEnum["IN_USE"] == WorkcellStatusEnum.IN_USE

    def test_can_access_by_value(self) -> None:
        """Test that enum members can be accessed by value."""
        assert WorkcellStatusEnum("active") == WorkcellStatusEnum.ACTIVE
        assert WorkcellStatusEnum("in_use") == WorkcellStatusEnum.IN_USE


class TestWorkcellStatusEnumChoices:

    """Tests for WorkcellStatusEnum.choices() classmethod."""

    def test_choices_classmethod_exists(self) -> None:
        """Test that choices() classmethod exists."""
        assert hasattr(WorkcellStatusEnum, "choices")
        assert callable(WorkcellStatusEnum.choices)

    def test_choices_returns_list(self) -> None:
        """Test that choices() returns a list."""
        result = WorkcellStatusEnum.choices()
        assert isinstance(result, list)

    def test_choices_returns_enum_members(self) -> None:
        """Test that choices() returns WorkcellStatusEnum members."""
        result = WorkcellStatusEnum.choices()
        assert all(isinstance(item, WorkcellStatusEnum) for item in result)

    def test_choices_includes_all_members(self) -> None:
        """Test that choices() includes all enum members."""
        result = WorkcellStatusEnum.choices()
        assert len(result) == 7

        expected_members = [
            WorkcellStatusEnum.ACTIVE,
            WorkcellStatusEnum.IN_USE,
            WorkcellStatusEnum.RESERVED,
            WorkcellStatusEnum.AVAILABLE,
            WorkcellStatusEnum.ERROR,
            WorkcellStatusEnum.INACTIVE,
            WorkcellStatusEnum.MAINTENANCE,
        ]

        for member in expected_members:
            assert member in result

    def test_choices_has_correct_order(self) -> None:
        """Test that choices() returns members in expected order."""
        result = WorkcellStatusEnum.choices()
        assert result[0] == WorkcellStatusEnum.ACTIVE
        assert result[1] == WorkcellStatusEnum.IN_USE
        assert result[2] == WorkcellStatusEnum.RESERVED
        assert result[3] == WorkcellStatusEnum.AVAILABLE
        assert result[4] == WorkcellStatusEnum.ERROR
        assert result[5] == WorkcellStatusEnum.INACTIVE
        assert result[6] == WorkcellStatusEnum.MAINTENANCE

    def test_choices_count_matches_enum_count(self) -> None:
        """Test that choices() count matches total enum member count."""
        choices_count = len(WorkcellStatusEnum.choices())
        enum_count = len(WorkcellStatusEnum)
        assert choices_count == enum_count


class TestWorkcellStatusEnumIntegration:

    """Integration tests for WorkcellStatusEnum."""

    def test_operational_statuses(self) -> None:
        """Test that enum has operational statuses."""
        operational_states = [
            WorkcellStatusEnum.ACTIVE,
            WorkcellStatusEnum.IN_USE,
            WorkcellStatusEnum.RESERVED,
            WorkcellStatusEnum.AVAILABLE,
        ]
        for state in operational_states:
            assert state in WorkcellStatusEnum

    def test_problematic_statuses(self) -> None:
        """Test that enum has problematic statuses."""
        problematic_states = [
            WorkcellStatusEnum.ERROR,
            WorkcellStatusEnum.MAINTENANCE,
        ]
        for state in problematic_states:
            assert state in WorkcellStatusEnum

    def test_inactive_status(self) -> None:
        """Test that enum has inactive status."""
        assert WorkcellStatusEnum.INACTIVE in WorkcellStatusEnum

    def test_status_transitions_make_sense(self) -> None:
        """Test that status values represent logical states."""
        # Available -> Reserved -> In Use is a logical flow
        assert WorkcellStatusEnum.AVAILABLE.value == "available"
        assert WorkcellStatusEnum.RESERVED.value == "reserved"
        assert WorkcellStatusEnum.IN_USE.value == "in_use"

    def test_can_use_enum_in_dict(self) -> None:
        """Test that enum can be used as dict keys."""
        status_mapping = {
            WorkcellStatusEnum.ACTIVE: "Workcell is active",
            WorkcellStatusEnum.ERROR: "Workcell has an error",
            WorkcellStatusEnum.MAINTENANCE: "Workcell is under maintenance",
        }
        assert status_mapping[WorkcellStatusEnum.ACTIVE] == "Workcell is active"
        assert status_mapping[WorkcellStatusEnum.ERROR] == "Workcell has an error"
