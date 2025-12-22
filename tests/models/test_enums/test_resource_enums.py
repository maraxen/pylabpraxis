"""Tests for resource enum types in models/enums/resource.py."""

import enum

from praxis.backend.models.enums.resource import (
    ResourceCategoryEnum,
    ResourceStatusEnum,
)


class TestResourceStatusEnum:

    """Tests for ResourceStatusEnum."""

    def test_is_enum(self) -> None:
        """Test that ResourceStatusEnum is an enum."""
        assert issubclass(ResourceStatusEnum, enum.Enum)

    def test_has_available_in_storage(self) -> None:
        """Test that enum has AVAILABLE_IN_STORAGE."""
        assert ResourceStatusEnum.AVAILABLE_IN_STORAGE.value == "available_in_storage"

    def test_has_available_on_deck(self) -> None:
        """Test that enum has AVAILABLE_ON_DECK."""
        assert ResourceStatusEnum.AVAILABLE_ON_DECK.value == "available_on_deck"

    def test_has_in_use(self) -> None:
        """Test that enum has IN_USE."""
        assert ResourceStatusEnum.IN_USE.value == "in_use"

    def test_has_empty(self) -> None:
        """Test that enum has EMPTY."""
        assert ResourceStatusEnum.EMPTY.value == "empty"

    def test_has_full(self) -> None:
        """Test that enum has FULL."""
        assert ResourceStatusEnum.FULL.value == "full"

    def test_has_disposed(self) -> None:
        """Test that enum has DISPOSED."""
        assert ResourceStatusEnum.DISPOSED.value == "disposed"

    def test_has_error(self) -> None:
        """Test that enum has ERROR."""
        assert ResourceStatusEnum.ERROR.value == "error"

    def test_has_unknown(self) -> None:
        """Test that enum has UNKNOWN."""
        assert ResourceStatusEnum.UNKNOWN.value == "unknown"

    def test_member_count(self) -> None:
        """Test that enum has exactly 13 members."""
        assert len(ResourceStatusEnum) == 13


class TestResourceCategoryEnum:

    """Tests for ResourceCategoryEnum."""

    def test_is_enum(self) -> None:
        """Test that ResourceCategoryEnum is an enum."""
        assert issubclass(ResourceCategoryEnum, enum.Enum)

    def test_has_top_level_categories(self) -> None:
        """Test that enum has all top-level categories."""
        top_level = [
            "ARM",
            "CARRIER",
            "CONTAINER",
            "DECK",
            "ITEMIZED_RESOURCE",
            "RESOURCE_HOLDER",
            "LID",
            "PLATE_ADAPTER",
            "RESOURCE_STACK",
            "OTHER",
        ]
        actual_names = [member.name for member in ResourceCategoryEnum]
        for category in top_level:
            assert category in actual_names

    def test_has_carrier_subcategories(self) -> None:
        """Test that enum has carrier subcategories."""
        carrier_subcats = [
            "MFX_CARRIER",
            "PLATE_CARRIER",
            "TIP_CARRIER",
            "TROUGH_CARRIER",
            "TUBE_CARRIER",
        ]
        actual_names = [member.name for member in ResourceCategoryEnum]
        for subcat in carrier_subcats:
            assert subcat in actual_names

    def test_has_container_subcategories(self) -> None:
        """Test that enum has container subcategories."""
        container_subcats = ["PETRI_DISH", "TROUGH", "TUBE", "WELL"]
        actual_names = [member.name for member in ResourceCategoryEnum]
        for subcat in container_subcats:
            assert subcat in actual_names

    def test_has_deck_subcategories(self) -> None:
        """Test that enum has deck subcategories."""
        deck_subcats = ["OT_DECK", "HAMILTON_DECK", "TECAN_DECK"]
        actual_names = [member.name for member in ResourceCategoryEnum]
        for subcat in deck_subcats:
            assert subcat in actual_names

    def test_has_itemized_resource_subcategories(self) -> None:
        """Test that enum has itemized resource subcategories."""
        itemized_subcats = ["PLATE", "TIP_RACK", "TUBE_RACK"]
        actual_names = [member.name for member in ResourceCategoryEnum]
        for subcat in itemized_subcats:
            assert subcat in actual_names

    def test_has_machine_categories(self) -> None:
        """Test that enum has machine categories."""
        machine_cats = [
            "SHAKER",
            "HEATERSHAKER",
            "PLATE_READER",
            "TEMPERATURE_CONTROLLER",
            "CENTRIFUGE",
            "INCUBATOR",
            "TILTER",
            "THERMOCYCLER",
            "SCALE",
        ]
        actual_names = [member.name for member in ResourceCategoryEnum]
        for cat in machine_cats:
            assert cat in actual_names

    def test_choices_classmethod_returns_list(self) -> None:
        """Test that choices() returns a list."""
        result = ResourceCategoryEnum.choices()
        assert isinstance(result, list)

    def test_choices_returns_strings(self) -> None:
        """Test that choices() returns string values."""
        result = ResourceCategoryEnum.choices()
        assert all(isinstance(choice, str) for choice in result)

    def test_choices_includes_top_level_categories(self) -> None:
        """Test that choices() includes all top-level categories."""
        result = ResourceCategoryEnum.choices()
        assert "Arm" in result
        assert "Carrier" in result
        assert "Deck" in result
        assert "Other" in result

    def test_choices_count(self) -> None:
        """Test that choices() returns exactly 10 categories."""
        result = ResourceCategoryEnum.choices()
        assert len(result) == 10

    def test_consumables_classmethod_returns_list(self) -> None:
        """Test that consumables() returns a list."""
        result = ResourceCategoryEnum.consumables()
        assert isinstance(result, list)

    def test_consumables_includes_expected_categories(self) -> None:
        """Test that consumables() includes expected consumable categories."""
        result = ResourceCategoryEnum.consumables()
        expected_consumables = ["Plate", "TipRack", "Trough", "Lid"]
        for consumable in expected_consumables:
            assert consumable in result

    def test_consumables_excludes_machines(self) -> None:
        """Test that consumables() doesn't include machine categories."""
        result = ResourceCategoryEnum.consumables()
        machine_values = [cat.value for cat in [
            ResourceCategoryEnum.PLATE_READER,
            ResourceCategoryEnum.CENTRIFUGE,
            ResourceCategoryEnum.SHAKER,
        ]]
        for machine_val in machine_values:
            assert machine_val not in result

    def test_machines_classmethod_returns_list(self) -> None:
        """Test that machines() returns a list."""
        result = ResourceCategoryEnum.machines()
        assert isinstance(result, list)

    def test_machines_includes_expected_categories(self) -> None:
        """Test that machines() includes expected machine categories."""
        result = ResourceCategoryEnum.machines()
        expected_machines = [
            "Arm",
            "Shaker",
            "HeaterShaker",
            "PlateReader",
            "Centrifuge",
            "Incubator",
        ]
        for machine in expected_machines:
            assert machine in result

    def test_machines_count(self) -> None:
        """Test that machines() returns expected number of categories."""
        result = ResourceCategoryEnum.machines()
        assert len(result) == 10

    def test_machines_excludes_consumables(self) -> None:
        """Test that machines() doesn't include consumable categories."""
        result = ResourceCategoryEnum.machines()
        consumable_values = [
            ResourceCategoryEnum.PLATE.value,
            ResourceCategoryEnum.TIP_RACK.value,
            ResourceCategoryEnum.TROUGH.value,
        ]
        for consumable_val in consumable_values:
            assert consumable_val not in result


class TestResourceEnumsIntegration:

    """Integration tests for resource enums."""

    def test_status_and_category_are_independent(self) -> None:
        """Test that status and category enums are independent."""
        status_names = set(member.name for member in ResourceStatusEnum)
        category_names = set(member.name for member in ResourceCategoryEnum)
        # No overlap expected
        assert len(status_names.intersection(category_names)) == 0

    def test_can_use_both_enums_together(self) -> None:
        """Test that both enums can be used together."""
        resource_info = {
            "category": ResourceCategoryEnum.PLATE,
            "status": ResourceStatusEnum.AVAILABLE_ON_DECK,
        }
        assert resource_info["category"] == ResourceCategoryEnum.PLATE
        assert resource_info["status"] == ResourceStatusEnum.AVAILABLE_ON_DECK

    def test_category_classmethods_are_mutually_exclusive(self) -> None:
        """Test that machines and consumables lists don't overlap."""
        machines = set(ResourceCategoryEnum.machines())
        consumables = set(ResourceCategoryEnum.consumables())
        # These should not overlap
        assert len(machines.intersection(consumables)) == 0

    def test_all_top_level_categories_covered_by_choices(self) -> None:
        """Test that choices() covers all top-level categories."""
        choices_set = set(ResourceCategoryEnum.choices())
        top_level_values = [
            ResourceCategoryEnum.ARM.value,
            ResourceCategoryEnum.CARRIER.value,
            ResourceCategoryEnum.CONTAINER.value,
            ResourceCategoryEnum.DECK.value,
            ResourceCategoryEnum.ITEMIZED_RESOURCE.value,
            ResourceCategoryEnum.RESOURCE_HOLDER.value,
            ResourceCategoryEnum.LID.value,
            ResourceCategoryEnum.PLATE_ADAPTER.value,
            ResourceCategoryEnum.RESOURCE_STACK.value,
            ResourceCategoryEnum.OTHER.value,
        ]
        for value in top_level_values:
            assert value in choices_set
