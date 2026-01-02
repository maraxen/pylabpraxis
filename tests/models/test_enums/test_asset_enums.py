"""Tests for asset enum types in models/enums/asset.py."""

import enum

from praxis.backend.models.enums.asset import AssetReservationStatusEnum, AssetType


class TestAssetType:

    """Tests for AssetType enum."""

    def test_asset_type_is_enum(self) -> None:
        """Test that AssetType is an enum."""
        assert issubclass(AssetType, enum.Enum)

    def test_asset_type_is_str_enum(self) -> None:
        """Test that AssetType inherits from str."""
        assert issubclass(AssetType, str)

    def test_asset_type_has_machine(self) -> None:
        """Test that AssetType has MACHINE member."""
        assert hasattr(AssetType, "MACHINE")
        assert AssetType.MACHINE.value == "MACHINE"

    def test_asset_type_has_resource(self) -> None:
        """Test that AssetType has RESOURCE member."""
        assert hasattr(AssetType, "RESOURCE")
        assert AssetType.RESOURCE.value == "RESOURCE"

    def test_asset_type_has_machine_resource(self) -> None:
        """Test that AssetType has MACHINE_RESOURCE member."""
        assert hasattr(AssetType, "MACHINE_RESOURCE")
        assert AssetType.MACHINE_RESOURCE.value == "MACHINE_RESOURCE"

    def test_asset_type_has_deck(self) -> None:
        """Test that AssetType has DECK member."""
        assert hasattr(AssetType, "DECK")
        assert AssetType.DECK.value == "DECK"

    def test_asset_type_has_asset(self) -> None:
        """Test that AssetType has ASSET member."""
        assert hasattr(AssetType, "ASSET")
        assert AssetType.ASSET.value == "GENERIC_ASSET"

    def test_asset_type_all_members(self) -> None:
        """Test that AssetType has exactly 5 members."""
        assert len(AssetType) == 5

    def test_asset_type_members_are_unique(self) -> None:
        """Test that all AssetType members have unique values."""
        values = [member.value for member in AssetType]
        assert len(values) == len(set(values))

    def test_asset_type_can_be_compared(self) -> None:
        """Test that AssetType members can be compared."""
        assert AssetType.MACHINE == AssetType.MACHINE
        assert AssetType.MACHINE != AssetType.RESOURCE

    def test_asset_type_can_be_used_as_string(self) -> None:
        """Test that AssetType can be used as string."""
        assert AssetType.MACHINE == "MACHINE"
        assert AssetType.DECK.value == "DECK"


class TestAssetReservationStatusEnum:

    """Tests for AssetReservationStatusEnum."""

    def test_asset_reservation_status_is_enum(self) -> None:
        """Test that AssetReservationStatusEnum is an enum."""
        assert issubclass(AssetReservationStatusEnum, enum.Enum)

    def test_has_reserved_status(self) -> None:
        """Test that enum has RESERVED status."""
        assert hasattr(AssetReservationStatusEnum, "RESERVED")
        assert AssetReservationStatusEnum.RESERVED.value == "reserved"

    def test_has_pending_status(self) -> None:
        """Test that enum has PENDING status."""
        assert hasattr(AssetReservationStatusEnum, "PENDING")
        assert AssetReservationStatusEnum.PENDING.value == "pending"

    def test_has_active_status(self) -> None:
        """Test that enum has ACTIVE status."""
        assert hasattr(AssetReservationStatusEnum, "ACTIVE")
        assert AssetReservationStatusEnum.ACTIVE.value == "active"

    def test_has_released_status(self) -> None:
        """Test that enum has RELEASED status."""
        assert hasattr(AssetReservationStatusEnum, "RELEASED")
        assert AssetReservationStatusEnum.RELEASED.value == "released"

    def test_has_expired_status(self) -> None:
        """Test that enum has EXPIRED status."""
        assert hasattr(AssetReservationStatusEnum, "EXPIRED")
        assert AssetReservationStatusEnum.EXPIRED.value == "expired"

    def test_has_failed_status(self) -> None:
        """Test that enum has FAILED status."""
        assert hasattr(AssetReservationStatusEnum, "FAILED")
        assert AssetReservationStatusEnum.FAILED.value == "failed"

    def test_all_members_count(self) -> None:
        """Test that enum has exactly 6 members."""
        assert len(AssetReservationStatusEnum) == 6

    def test_members_are_unique(self) -> None:
        """Test that all members have unique values."""
        values = [member.value for member in AssetReservationStatusEnum]
        assert len(values) == len(set(values))

    def test_can_iterate_over_enum(self) -> None:
        """Test that enum can be iterated."""
        statuses = list(AssetReservationStatusEnum)
        assert len(statuses) == 6
        assert AssetReservationStatusEnum.RESERVED in statuses

    def test_can_access_by_name(self) -> None:
        """Test that enum members can be accessed by name."""
        assert AssetReservationStatusEnum["RESERVED"] == AssetReservationStatusEnum.RESERVED
        assert AssetReservationStatusEnum["ACTIVE"] == AssetReservationStatusEnum.ACTIVE

    def test_can_access_by_value(self) -> None:
        """Test that enum members can be accessed by value."""
        assert AssetReservationStatusEnum("reserved") == AssetReservationStatusEnum.RESERVED
        assert AssetReservationStatusEnum("active") == AssetReservationStatusEnum.ACTIVE


class TestAssetEnumsIntegration:

    """Integration tests for asset enums."""

    def test_asset_type_and_reservation_status_are_independent(self) -> None:
        """Test that AssetType and AssetReservationStatusEnum are independent."""
        # They should have different members
        asset_types = {member.name for member in AssetType}
        reservation_statuses = {
            member.name for member in AssetReservationStatusEnum
        }
        assert len(asset_types.intersection(reservation_statuses)) == 0

    def test_enums_can_be_used_together(self) -> None:
        """Test that both enums can be used in the same context."""
        asset_info = {
            "type": AssetType.MACHINE,
            "status": AssetReservationStatusEnum.RESERVED,
        }
        assert asset_info["type"] == AssetType.MACHINE
        assert asset_info["status"] == AssetReservationStatusEnum.RESERVED
