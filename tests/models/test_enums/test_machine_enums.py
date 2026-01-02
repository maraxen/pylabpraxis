"""Tests for machine enum types in models/enums/machine.py."""

import enum

from praxis.backend.models.enums.machine import MachineCategoryEnum, MachineStatusEnum


class TestMachineStatusEnum:

    """Tests for MachineStatusEnum."""

    def test_machine_status_is_enum(self) -> None:
        """Test that MachineStatusEnum is an enum."""
        assert issubclass(MachineStatusEnum, enum.Enum)

    def test_has_available_status(self) -> None:
        """Test that enum has AVAILABLE status."""
        assert MachineStatusEnum.AVAILABLE.value == "AVAILABLE"

    def test_has_in_use_status(self) -> None:
        """Test that enum has IN_USE status."""
        assert MachineStatusEnum.IN_USE.value == "IN_USE"

    def test_has_error_status(self) -> None:
        """Test that enum has ERROR status."""
        assert MachineStatusEnum.ERROR.value == "ERROR"

    def test_has_offline_status(self) -> None:
        """Test that enum has OFFLINE status."""
        assert MachineStatusEnum.OFFLINE.value == "OFFLINE"

    def test_has_initializing_status(self) -> None:
        """Test that enum has INITIALIZING status."""
        assert MachineStatusEnum.INITIALIZING.value == "INITIALIZING"

    def test_has_maintenance_status(self) -> None:
        """Test that enum has MAINTENANCE status."""
        assert MachineStatusEnum.MAINTENANCE.value == "MAINTENANCE"

    def test_all_members_count(self) -> None:
        """Test that enum has exactly 6 members."""
        assert len(MachineStatusEnum) == 6


class TestMachineCategoryEnum:

    """Tests for MachineCategoryEnum."""

    def test_machine_category_is_enum(self) -> None:
        """Test that MachineCategoryEnum is an enum."""
        assert issubclass(MachineCategoryEnum, enum.Enum)

    def test_has_liquid_handler(self) -> None:
        """Test that enum has LIQUID_HANDLER category."""
        assert MachineCategoryEnum.LIQUID_HANDLER.value == "LiquidHandler"

    def test_has_plate_reader(self) -> None:
        """Test that enum has PLATE_READER category."""
        assert MachineCategoryEnum.PLATE_READER.value == "PlateReader"

    def test_has_incubator(self) -> None:
        """Test that enum has INCUBATOR category."""
        assert MachineCategoryEnum.INCUBATOR.value == "Incubator"

    def test_has_unknown(self) -> None:
        """Test that enum has UNKNOWN category."""
        assert MachineCategoryEnum.UNKNOWN.value == "Unknown"

    def test_all_categories_present(self) -> None:
        """Test that all expected categories are present."""
        expected_categories = [
            "LIQUID_HANDLER",
            "PLATE_READER",
            "INCUBATOR",
            "SHAKER",
            "HEATER_SHAKER",
            "PUMP",
            "FAN",
            "TEMPERATURE_CONTROLLER",
            "TILTING",
            "THERMOCYCLER",
            "SEALER",
            "FLOW_CYTOMETER",
            "SCALE",
            "CENTRIFUGE",
            "ARM",
            "GENERAL_AUTOMATION_DEVICE",
            "OTHER_INSTRUMENT",
            "UNKNOWN",
        ]
        actual_names = [member.name for member in MachineCategoryEnum]
        for expected in expected_categories:
            assert expected in actual_names

    def test_resources_classmethod_returns_list(self) -> None:
        """Test that resources() returns a list."""
        result = MachineCategoryEnum.resources()
        assert isinstance(result, list)

    def test_resources_classmethod_returns_enum_members(self) -> None:
        """Test that resources() returns MachineCategoryEnum members."""
        result = MachineCategoryEnum.resources()
        assert all(isinstance(item, MachineCategoryEnum) for item in result)

    def test_resources_includes_plate_reader(self) -> None:
        """Test that resources() includes PLATE_READER."""
        result = MachineCategoryEnum.resources()
        assert MachineCategoryEnum.PLATE_READER in result

    def test_resources_excludes_liquid_handler(self) -> None:
        """Test that resources() excludes LIQUID_HANDLER."""
        result = MachineCategoryEnum.resources()
        assert MachineCategoryEnum.LIQUID_HANDLER not in result

    def test_resources_includes_expected_categories(self) -> None:
        """Test that resources() includes all expected resource categories."""
        result = MachineCategoryEnum.resources()
        expected_in_resources = [
            MachineCategoryEnum.PLATE_READER,
            MachineCategoryEnum.INCUBATOR,
            MachineCategoryEnum.SHAKER,
            MachineCategoryEnum.HEATER_SHAKER,
            MachineCategoryEnum.TEMPERATURE_CONTROLLER,
            MachineCategoryEnum.CENTRIFUGE,
        ]
        for category in expected_in_resources:
            assert category in result

    def test_resources_count(self) -> None:
        """Test that resources() returns expected number of categories."""
        result = MachineCategoryEnum.resources()
        assert len(result) == 12

    def test_all_members_are_unique(self) -> None:
        """Test that all enum members have unique values."""
        values = [member.value for member in MachineCategoryEnum]
        assert len(values) == len(set(values))


class TestMachineEnumsIntegration:

    """Integration tests for machine enums."""

    def test_status_and_category_are_independent(self) -> None:
        """Test that status and category enums are independent."""
        status_names = {member.name for member in MachineStatusEnum}
        category_names = {member.name for member in MachineCategoryEnum}
        # No overlap between status and category names
        assert len(status_names.intersection(category_names)) == 0

    def test_can_use_both_enums_together(self) -> None:
        """Test that both enums can be used together."""
        machine_info = {
            "category": MachineCategoryEnum.PLATE_READER,
            "status": MachineStatusEnum.AVAILABLE,
        }
        assert machine_info["category"] == MachineCategoryEnum.PLATE_READER
        assert machine_info["status"] == MachineStatusEnum.AVAILABLE
