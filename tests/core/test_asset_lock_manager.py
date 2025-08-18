import asyncio
import uuid
from datetime import timedelta

import pytest
from fakeredis import aioredis

from praxis.backend.core.asset_lock_manager import AssetLockManager
from praxis.backend.models.pydantic.asset import AcquireAssetLock


@pytest.fixture
async def fake_redis_client():
    """Provides a fake Redis client for testing."""
    client = aioredis.FakeRedis()
    yield client
    await client.flushall()
    await client.close()


@pytest.fixture
async def asset_lock_manager(fake_redis_client):
    """Provides an AssetLockManager instance with a fake Redis client."""
    manager = AssetLockManager(redis_client=fake_redis_client)
    return manager


@pytest.mark.asyncio
async def test_acquire_and_release_lock(asset_lock_manager: AssetLockManager):
    """Test basic lock acquisition and release."""
    protocol_run_id = uuid.uuid4()
    reservation_id = uuid.uuid4()
    lock_data = AcquireAssetLock(
        protocol_run_id=protocol_run_id,
        reservation_id=reservation_id,
        asset_type="machine",
        asset_name="robot1",
        required_capabilities={},
    )

    # Acquire the lock
    acquired = await asset_lock_manager.acquire_asset_lock(lock_data)
    assert acquired is True

    # Check availability
    availability = await asset_lock_manager.check_asset_availability(
        "machine", "robot1"
    )
    assert availability is not None
    assert availability["reservation_id"] == str(reservation_id)

    # Try to acquire again (should fail)
    new_reservation_id = uuid.uuid4()
    new_lock_data = lock_data.copy(update={"reservation_id": new_reservation_id})
    acquired_again = await asset_lock_manager.acquire_asset_lock(new_lock_data)
    assert acquired_again is False

    # Release the lock
    released = await asset_lock_manager.release_asset_lock(
        "machine", "robot1", reservation_id
    )
    assert released is True

    # Check availability again
    availability_after_release = await asset_lock_manager.check_asset_availability(
        "machine", "robot1"
    )
    assert availability_after_release is None


@pytest.mark.asyncio
async def test_release_all_protocol_locks(asset_lock_manager: AssetLockManager):
    """Test releasing all locks associated with a protocol run."""
    protocol_run_id = uuid.uuid4()

    # Acquire multiple locks for the same protocol
    lock_data1 = AcquireAssetLock(
        protocol_run_id=protocol_run_id,
        reservation_id=uuid.uuid4(),
        asset_type="machine",
        asset_name="robot1",
        required_capabilities={},
    )
    lock_data2 = AcquireAssetLock(
        protocol_run_id=protocol_run_id,
        reservation_id=uuid.uuid4(),
        asset_type="resource",
        asset_name="plate1",
        required_capabilities={},
    )
    await asset_lock_manager.acquire_asset_lock(lock_data1)
    await asset_lock_manager.acquire_asset_lock(lock_data2)

    # Verify locks are held
    assert (
        await asset_lock_manager.check_asset_availability("machine", "robot1")
        is not None
    )
    assert (
        await asset_lock_manager.check_asset_availability("resource", "plate1")
        is not None
    )

    # Release all locks for the protocol
    released_count = await asset_lock_manager.release_all_protocol_locks(
        protocol_run_id
    )
    assert released_count == 2

    # Verify locks are released
    assert (
        await asset_lock_manager.check_asset_availability("machine", "robot1") is None
    )
    assert (
        await asset_lock_manager.check_asset_availability("resource", "plate1") is None
    )


@pytest.mark.asyncio
async def test_lock_timeout(asset_lock_manager: AssetLockManager, fake_redis_client):
    """Test that locks expire after the specified timeout."""
    protocol_run_id = uuid.uuid4()
    reservation_id = uuid.uuid4()
    lock_data = AcquireAssetLock(
        protocol_run_id=protocol_run_id,
        reservation_id=reservation_id,
        asset_type="machine",
        asset_name="robot1",
        timeout_seconds=1,  # Short timeout
        required_capabilities={},
    )

    # Acquire the lock
    await asset_lock_manager.acquire_asset_lock(lock_data)
    assert (
        await asset_lock_manager.check_asset_availability("machine", "robot1")
        is not None
    )

    # Wait for the lock to expire
    await asyncio.sleep(1.1)

    # Check availability again, should be None
    assert (
        await asset_lock_manager.check_asset_availability("machine", "robot1") is None
    )


@pytest.mark.asyncio
async def test_cleanup_expired_locks(
    asset_lock_manager: AssetLockManager, fake_redis_client
):
    """Test the cleanup of expired locks."""
    # Manually set an expired lock
    lock_key = asset_lock_manager._get_asset_lock_key("machine", "robot_expired")
    await fake_redis_client.set(lock_key, str(uuid.uuid4()), ex=1)
    await asyncio.sleep(1.1)

    # Manually set a lock with no expiration (orphaned)
    orphan_lock_key = asset_lock_manager._get_asset_lock_key("machine", "robot_orphan")
    await fake_redis_client.set(orphan_lock_key, str(uuid.uuid4()))

    # Run cleanup
    cleaned_count = await asset_lock_manager.cleanup_expired_locks()
    assert cleaned_count == 2

    # Check that the locks are gone
    assert await fake_redis_client.get(lock_key) is None
    assert await fake_redis_client.get(orphan_lock_key) is None


@pytest.mark.asyncio
async def test_get_system_status(asset_lock_manager: AssetLockManager):
    """Test getting the system status."""
    protocol_run_id = uuid.uuid4()
    lock_data = AcquireAssetLock(
        protocol_run_id=protocol_run_id,
        reservation_id=uuid.uuid4(),
        asset_type="machine",
        asset_name="robot1",
        required_capabilities={},
    )
    await asset_lock_manager.acquire_asset_lock(lock_data)

    status = await asset_lock_manager.get_system_status()

    assert "active_asset_locks" in status
    assert "active_reservations" in status
    assert "tracked_protocols" in status
    assert len(status["active_asset_locks"]) == 1
    assert len(status["active_reservations"]) == 1
    assert len(status["tracked_protocols"]) == 1
