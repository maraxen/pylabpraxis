"""Tests for core/asset_lock_manager.py."""


import pytest

from praxis.backend.core.asset_lock_manager import AssetLockManager
from praxis.backend.models.pydantic_internals.runtime import AcquireAssetLock
from praxis.backend.utils.uuid import uuid7


class TestAssetLockManagerInit:

    """Tests for AssetLockManager initialization."""

    def test_init_creates_empty_locks_dict(self) -> None:
        """Test that __init__ creates empty locks dictionary."""
        manager = AssetLockManager()
        assert hasattr(manager, "_locks")
        assert isinstance(manager._locks, dict)
        assert len(manager._locks) == 0

    def test_init_creates_manager_instance(self) -> None:
        """Test that __init__ creates AssetLockManager instance."""
        manager = AssetLockManager()
        assert isinstance(manager, AssetLockManager)


class TestAcquireAssetLock:

    """Tests for AssetLockManager.acquire_asset_lock()."""

    @pytest.mark.asyncio
    async def test_acquire_lock_on_free_asset_succeeds(self) -> None:
        """Test that acquiring lock on free asset succeeds."""
        manager = AssetLockManager()
        lock_data = AcquireAssetLock(
            asset_type="MACHINE",
            asset_name="machine1",
            protocol_run_id=uuid7(),
            reservation_id=uuid7(),
        )

        result = await manager.acquire_asset_lock(lock_data)
        assert result is True

    @pytest.mark.asyncio
    async def test_acquire_lock_stores_lock_data(self) -> None:
        """Test that acquiring lock stores lock data."""
        manager = AssetLockManager()
        lock_data = AcquireAssetLock(
            asset_type="RESOURCE",
            asset_name="resource1",
            protocol_run_id=uuid7(),
            reservation_id=uuid7(),
        )

        await manager.acquire_asset_lock(lock_data)
        assert len(manager._locks) == 1
        assert "RESOURCE:resource1" in manager._locks
        assert manager._locks["RESOURCE:resource1"] == lock_data

    @pytest.mark.asyncio
    async def test_acquire_lock_on_locked_asset_fails(self) -> None:
        """Test that acquiring lock on already locked asset fails."""
        manager = AssetLockManager()
        lock_data1 = AcquireAssetLock(
            asset_type="MACHINE",
            asset_name="machine1",
            protocol_run_id=uuid7(),
            reservation_id=uuid7(),
        )
        lock_data2 = AcquireAssetLock(
            asset_type="MACHINE",
            asset_name="machine1",
            protocol_run_id=uuid7(),
            reservation_id=uuid7(),
        )

        # First acquisition succeeds
        result1 = await manager.acquire_asset_lock(lock_data1)
        assert result1 is True

        # Second acquisition fails
        result2 = await manager.acquire_asset_lock(lock_data2)
        assert result2 is False

    @pytest.mark.asyncio
    async def test_acquire_lock_uses_composite_key(self) -> None:
        """Test that lock key is composite of asset_type and asset_name."""
        manager = AssetLockManager()
        lock_data = AcquireAssetLock(
            asset_type="DECK",
            asset_name="deck1",
            protocol_run_id=uuid7(),
            reservation_id=uuid7(),
        )

        await manager.acquire_asset_lock(lock_data)
        assert "DECK:deck1" in manager._locks

    @pytest.mark.asyncio
    async def test_acquire_different_assets_both_succeed(self) -> None:
        """Test that acquiring locks on different assets both succeed."""
        manager = AssetLockManager()
        lock_data1 = AcquireAssetLock(
            asset_type="MACHINE",
            asset_name="machine1",
            protocol_run_id=uuid7(),
            reservation_id=uuid7(),
        )
        lock_data2 = AcquireAssetLock(
            asset_type="MACHINE",
            asset_name="machine2",
            protocol_run_id=uuid7(),
            reservation_id=uuid7(),
        )

        result1 = await manager.acquire_asset_lock(lock_data1)
        result2 = await manager.acquire_asset_lock(lock_data2)

        assert result1 is True
        assert result2 is True
        assert len(manager._locks) == 2


class TestReleaseAssetLock:

    """Tests for AssetLockManager.release_asset_lock()."""

    @pytest.mark.asyncio
    async def test_release_existing_lock_succeeds(self) -> None:
        """Test that releasing an existing lock succeeds."""
        manager = AssetLockManager()
        protocol_run_id = uuid7()
        reservation_id = uuid7()

        # First acquire a lock
        lock_data = AcquireAssetLock(
            asset_type="MACHINE",
            asset_name="machine1",
            protocol_run_id=protocol_run_id,
            reservation_id=reservation_id,
        )
        await manager.acquire_asset_lock(lock_data)

        # Then release it
        result = await manager.release_asset_lock(
            "MACHINE", "machine1", reservation_id, protocol_run_id,
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_release_removes_lock_from_dict(self) -> None:
        """Test that releasing a lock removes it from the locks dict."""
        manager = AssetLockManager()
        protocol_run_id = uuid7()
        reservation_id = uuid7()

        # Acquire a lock
        lock_data = AcquireAssetLock(
            asset_type="RESOURCE",
            asset_name="resource1",
            protocol_run_id=protocol_run_id,
            reservation_id=reservation_id,
        )
        await manager.acquire_asset_lock(lock_data)
        assert len(manager._locks) == 1

        # Release the lock
        await manager.release_asset_lock(
            "RESOURCE", "resource1", reservation_id, protocol_run_id,
        )
        assert len(manager._locks) == 0
        assert "RESOURCE:resource1" not in manager._locks

    @pytest.mark.asyncio
    async def test_release_nonexistent_lock_returns_false(self) -> None:
        """Test that releasing a nonexistent lock returns False."""
        manager = AssetLockManager()
        protocol_run_id = uuid7()
        reservation_id = uuid7()

        result = await manager.release_asset_lock(
            "MACHINE", "nonexistent", reservation_id, protocol_run_id,
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_release_uses_composite_key(self) -> None:
        """Test that release uses composite key of asset_type and asset_name."""
        manager = AssetLockManager()
        protocol_run_id = uuid7()
        reservation_id = uuid7()

        # Acquire a lock
        lock_data = AcquireAssetLock(
            asset_type="DECK",
            asset_name="deck1",
            protocol_run_id=protocol_run_id,
            reservation_id=reservation_id,
        )
        await manager.acquire_asset_lock(lock_data)

        # Release using same composite key
        result = await manager.release_asset_lock(
            "DECK", "deck1", reservation_id, protocol_run_id,
        )
        assert result is True
        assert "DECK:deck1" not in manager._locks


class TestGetLockStatus:

    """Tests for AssetLockManager.get_lock_status()."""

    @pytest.mark.asyncio
    async def test_get_lock_status_returns_lock_data_for_locked_asset(self) -> None:
        """Test that get_lock_status returns lock data for locked asset."""
        manager = AssetLockManager()
        lock_data = AcquireAssetLock(
            asset_type="MACHINE",
            asset_name="machine1",
            protocol_run_id=uuid7(),
            reservation_id=uuid7(),
        )
        await manager.acquire_asset_lock(lock_data)

        result = await manager.get_lock_status("MACHINE", "machine1")
        assert result == lock_data

    @pytest.mark.asyncio
    async def test_get_lock_status_returns_none_for_unlocked_asset(self) -> None:
        """Test that get_lock_status returns None for unlocked asset."""
        manager = AssetLockManager()

        result = await manager.get_lock_status("MACHINE", "machine1")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_lock_status_uses_composite_key(self) -> None:
        """Test that get_lock_status uses composite key."""
        manager = AssetLockManager()
        lock_data = AcquireAssetLock(
            asset_type="RESOURCE",
            asset_name="resource1",
            protocol_run_id=uuid7(),
            reservation_id=uuid7(),
        )
        await manager.acquire_asset_lock(lock_data)

        result = await manager.get_lock_status("RESOURCE", "resource1")
        assert result is not None
        assert result.asset_type == "RESOURCE"
        assert result.asset_name == "resource1"

    @pytest.mark.asyncio
    async def test_get_lock_status_after_release_returns_none(self) -> None:
        """Test that get_lock_status returns None after lock is released."""
        manager = AssetLockManager()
        protocol_run_id = uuid7()
        reservation_id = uuid7()

        # Acquire lock
        lock_data = AcquireAssetLock(
            asset_type="MACHINE",
            asset_name="machine1",
            protocol_run_id=protocol_run_id,
            reservation_id=reservation_id,
        )
        await manager.acquire_asset_lock(lock_data)

        # Release lock
        await manager.release_asset_lock(
            "MACHINE", "machine1", reservation_id, protocol_run_id,
        )

        # Get status should return None
        result = await manager.get_lock_status("MACHINE", "machine1")
        assert result is None


class TestAssetLockManagerIntegration:

    """Integration tests for AssetLockManager."""

    @pytest.mark.asyncio
    async def test_complete_lock_lifecycle(self) -> None:
        """Test complete lock lifecycle: acquire, check, release, check."""
        manager = AssetLockManager()
        protocol_run_id = uuid7()
        reservation_id = uuid7()

        # Initially no lock
        status = await manager.get_lock_status("MACHINE", "machine1")
        assert status is None

        # Acquire lock
        lock_data = AcquireAssetLock(
            asset_type="MACHINE",
            asset_name="machine1",
            protocol_run_id=protocol_run_id,
            reservation_id=reservation_id,
        )
        acquire_result = await manager.acquire_asset_lock(lock_data)
        assert acquire_result is True

        # Check lock exists
        status = await manager.get_lock_status("MACHINE", "machine1")
        assert status is not None
        assert status.asset_name == "machine1"

        # Release lock
        release_result = await manager.release_asset_lock(
            "MACHINE", "machine1", reservation_id, protocol_run_id,
        )
        assert release_result is True

        # Check lock is gone
        status = await manager.get_lock_status("MACHINE", "machine1")
        assert status is None

    @pytest.mark.asyncio
    async def test_multiple_assets_independent_locks(self) -> None:
        """Test that multiple assets can have independent locks."""
        manager = AssetLockManager()

        # Acquire locks on multiple assets
        lock_data1 = AcquireAssetLock(
            asset_type="MACHINE",
            asset_name="machine1",
            protocol_run_id=uuid7(),
            reservation_id=uuid7(),
        )
        lock_data2 = AcquireAssetLock(
            asset_type="RESOURCE",
            asset_name="resource1",
            protocol_run_id=uuid7(),
            reservation_id=uuid7(),
        )
        lock_data3 = AcquireAssetLock(
            asset_type="DECK",
            asset_name="deck1",
            protocol_run_id=uuid7(),
            reservation_id=uuid7(),
        )

        await manager.acquire_asset_lock(lock_data1)
        await manager.acquire_asset_lock(lock_data2)
        await manager.acquire_asset_lock(lock_data3)

        # All should be locked
        assert await manager.get_lock_status("MACHINE", "machine1") is not None
        assert await manager.get_lock_status("RESOURCE", "resource1") is not None
        assert await manager.get_lock_status("DECK", "deck1") is not None

        # Release one
        await manager.release_asset_lock(
            "RESOURCE",
            "resource1",
            lock_data2.reservation_id,
            lock_data2.protocol_run_id,
        )

        # Others should still be locked
        assert await manager.get_lock_status("MACHINE", "machine1") is not None
        assert await manager.get_lock_status("RESOURCE", "resource1") is None
        assert await manager.get_lock_status("DECK", "deck1") is not None

    @pytest.mark.asyncio
    async def test_acquire_release_acquire_same_asset(self) -> None:
        """Test that an asset can be re-acquired after release."""
        manager = AssetLockManager()
        protocol_run_id1 = uuid7()
        reservation_id1 = uuid7()
        protocol_run_id2 = uuid7()
        reservation_id2 = uuid7()

        # First acquisition
        lock_data1 = AcquireAssetLock(
            asset_type="MACHINE",
            asset_name="machine1",
            protocol_run_id=protocol_run_id1,
            reservation_id=reservation_id1,
        )
        result1 = await manager.acquire_asset_lock(lock_data1)
        assert result1 is True

        # Release
        await manager.release_asset_lock(
            "MACHINE", "machine1", reservation_id1, protocol_run_id1,
        )

        # Second acquisition (different protocol run)
        lock_data2 = AcquireAssetLock(
            asset_type="MACHINE",
            asset_name="machine1",
            protocol_run_id=protocol_run_id2,
            reservation_id=reservation_id2,
        )
        result2 = await manager.acquire_asset_lock(lock_data2)
        assert result2 is True

        # Check it's the new lock
        status = await manager.get_lock_status("MACHINE", "machine1")
        assert status.protocol_run_id == protocol_run_id2
