# pylint: disable=protected-access, redefined-outer-name, unused-argument
"""Unit tests for the AssetLockManager."""

import json
import uuid
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from freezegun import freeze_time

from praxis.backend.core.asset_lock_manager import AssetLockManager

# --- Test Constants ---
# Per the testing strategy, we use static, valid UUIDv7s for deterministic tests
# that align with the application's ID format.
TEST_REDIS_URL = "redis://mock-redis:6379/1"
TEST_PROTOCOL_RUN_ID = uuid.UUID("018f3da8-72b6-7e9b-81c8-355d9857a23c")
TEST_RESERVATION_ID = uuid.UUID("018f3da8-75c8-78c7-9721-6d73c7b7759c")
TEST_ASSET_TYPE = "machine"
TEST_ASSET_NAME = "ot2_1"
DEFAULT_LOCK_TIMEOUT = 3600


# --- Fixtures ---


@pytest.fixture
def mock_redis_pool():
  """Fixture for a mocked Redis connection pool."""
  pool = MagicMock()
  pool.disconnect = AsyncMock()
  return pool


@pytest.fixture
def mock_redis_client():
  """Fixture for a mocked async Redis client."""
  client = AsyncMock()
  client.ping = AsyncMock(return_value=True)
  client.close = AsyncMock()
  client.set = AsyncMock()
  client.setex = AsyncMock()
  client.get = AsyncMock()
  client.delete = AsyncMock()
  client.sadd = AsyncMock()
  client.srem = AsyncMock()
  client.smembers = AsyncMock(return_value=set())
  client.expire = AsyncMock()
  client.eval = AsyncMock()
  client.scan_iter = (
    MagicMock()
  )  # Needs to be a sync function returning an async iterator
  client.info = AsyncMock(return_value={})
  return client


@pytest.fixture
async def asset_lock_manager(mock_redis_client, mock_redis_pool):
  """Fixture for an initialized AssetLockManager with a mocked Redis client."""
  with patch("redis.asyncio.ConnectionPool.from_url", return_value=mock_redis_pool):
    with patch("redis.asyncio.Redis", return_value=mock_redis_client):
      manager = AssetLockManager(redis_url=TEST_REDIS_URL)
      await manager.initialize()
      yield manager
      await manager.close()


# --- Test Cases ---


@pytest.mark.asyncio
class TestAssetLockManagerInitialization:
  """Tests for initialization and connection handling."""

  def test_init(self):
    """Test constructor sets parameters correctly."""
    manager = AssetLockManager(
      redis_url="redis://test",
      lock_timeout_seconds=123,
      lock_retry_delay_ms=45,
      max_lock_retries=6,
    )
    assert manager.redis_url == "redis://test"
    assert manager.lock_timeout_seconds == 123
    assert manager.lock_retry_delay_ms == 45
    assert manager.max_lock_retries == 6
    assert manager._redis_client is None

  async def test_initialize_success(self, mock_redis_client):
    """Test successful initialization and connection."""
    manager = AssetLockManager(redis_url=TEST_REDIS_URL)
    with patch("redis.asyncio.ConnectionPool.from_url") as mock_from_url:
      with patch("redis.asyncio.Redis", return_value=mock_redis_client) as mock_redis:
        await manager.initialize()
        mock_from_url.assert_called_once_with(
          TEST_REDIS_URL,
          encoding="utf-8",
          decode_responses=True,
          max_connections=20,
        )
        mock_redis.assert_called_once()
        mock_redis_client.ping.assert_awaited_once()
        assert manager._redis_client is not None

  async def test_initialize_failure(self, mock_redis_client):
    """Test that initialization raises an error if Redis connection fails."""
    manager = AssetLockManager(redis_url=TEST_REDIS_URL)
    mock_redis_client.ping.side_effect = ConnectionError("Cannot connect")
    with patch("redis.asyncio.Redis", return_value=mock_redis_client):
      with pytest.raises(ConnectionError):
        await manager.initialize()

  async def test_close_success(
    self, asset_lock_manager, mock_redis_client, mock_redis_pool,
  ):
    """Test that close calls disconnect on the client and pool."""
    # The fixture handles initialization and close, so we just check the mocks
    # We need to re-await close to check the calls within this test's scope
    await asset_lock_manager.close()
    mock_redis_client.close.assert_awaited()
    mock_redis_pool.disconnect.assert_awaited()

  async def test_runtime_error_if_not_initialized(self):
    """Test that methods raise RuntimeError if the client is not initialized."""
    manager = AssetLockManager()
    with pytest.raises(RuntimeError, match="Redis client not initialized"):
      await manager.acquire_asset_lock(
        TEST_ASSET_TYPE, TEST_ASSET_NAME, TEST_PROTOCOL_RUN_ID, TEST_RESERVATION_ID,
      )


@pytest.mark.asyncio
class TestAcquireAssetLock:
  """Tests for the acquire_asset_lock method."""

  async def test_acquire_lock_success_first_try(
    self, asset_lock_manager, mock_redis_client,
  ):
    """Test successfully acquiring a lock on the first attempt."""
    mock_redis_client.set.return_value = True  # Simulate successful SET NX

    with freeze_time("2023-01-01 12:00:00 UTC") as frozen_time:
      result = await asset_lock_manager.acquire_asset_lock(
        TEST_ASSET_TYPE, TEST_ASSET_NAME, TEST_PROTOCOL_RUN_ID, TEST_RESERVATION_ID,
      )

      assert result is True
      lock_key = asset_lock_manager._get_asset_lock_key(
        TEST_ASSET_TYPE, TEST_ASSET_NAME,
      )
      mock_redis_client.set.assert_awaited_once_with(
        lock_key, str(TEST_RESERVATION_ID), nx=True, ex=DEFAULT_LOCK_TIMEOUT,
      )

      # Verify reservation metadata storage
      reservation_key = asset_lock_manager._get_reservation_data_key(
        TEST_RESERVATION_ID,
      )
      expected_expires_at = frozen_time.time_to_freeze + timedelta(
        seconds=DEFAULT_LOCK_TIMEOUT,
      )
      expected_data = {
        "reservation_id": str(TEST_RESERVATION_ID),
        "protocol_run_id": str(TEST_PROTOCOL_RUN_ID),
        "asset_type": TEST_ASSET_TYPE,
        "asset_name": TEST_ASSET_NAME,
        "locked_at": "2023-01-01T12:00:00+00:00",
        "expires_at": expected_expires_at.isoformat(),
        "required_capabilities": {},
      }
      mock_redis_client.setex.assert_awaited_once_with(
        reservation_key, DEFAULT_LOCK_TIMEOUT, json.dumps(expected_data),
      )

      # Verify protocol lock tracking
      protocol_locks_key = asset_lock_manager._get_protocol_locks_key(
        TEST_PROTOCOL_RUN_ID,
      )
      mock_redis_client.sadd.assert_awaited_once_with(protocol_locks_key, lock_key)
      mock_redis_client.expire.assert_awaited_once_with(
        protocol_locks_key, DEFAULT_LOCK_TIMEOUT,
      )

  async def test_acquire_lock_failure_contention(
    self, asset_lock_manager, mock_redis_client,
  ):
    """Test failing to acquire a lock because it's already held."""
    mock_redis_client.set.return_value = False  # Simulate lock is taken

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
      result = await asset_lock_manager.acquire_asset_lock(
        TEST_ASSET_TYPE, TEST_ASSET_NAME, TEST_PROTOCOL_RUN_ID, TEST_RESERVATION_ID,
      )

      assert result is False
      assert mock_redis_client.set.await_count == asset_lock_manager.max_lock_retries
      assert mock_sleep.await_count == asset_lock_manager.max_lock_retries - 1
      mock_redis_client.setex.assert_not_awaited()
      mock_redis_client.sadd.assert_not_awaited()

  async def test_acquire_lock_success_with_retry(
    self, asset_lock_manager, mock_redis_client,
  ):
    """Test acquiring a lock after a few failed attempts."""
    mock_redis_client.set.side_effect = [
      False,
      False,
      True,
    ]  # Fails twice, then succeeds

    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
      result = await asset_lock_manager.acquire_asset_lock(
        TEST_ASSET_TYPE, TEST_ASSET_NAME, TEST_PROTOCOL_RUN_ID, TEST_RESERVATION_ID,
      )

      assert result is True
      assert mock_redis_client.set.await_count == 3
      assert mock_sleep.await_count == 2
      mock_redis_client.setex.assert_awaited_once()
      mock_redis_client.sadd.assert_awaited_once()

  async def test_acquire_lock_redis_error(self, asset_lock_manager, mock_redis_client):
    """Test that an exception during lock acquisition returns False."""
    mock_redis_client.set.side_effect = Exception("Redis network error")

    result = await asset_lock_manager.acquire_asset_lock(
      TEST_ASSET_TYPE, TEST_ASSET_NAME, TEST_PROTOCOL_RUN_ID, TEST_RESERVATION_ID,
    )

    assert result is False


@pytest.mark.asyncio
class TestReleaseAssetLock:
  """Tests for the release_asset_lock method."""

  async def test_release_lock_success(self, asset_lock_manager, mock_redis_client):
    """Test successfully releasing a lock."""
    mock_redis_client.eval.return_value = 1  # Lua script returns 1 on success

    result = await asset_lock_manager.release_asset_lock(
      TEST_ASSET_TYPE, TEST_ASSET_NAME, TEST_RESERVATION_ID, TEST_PROTOCOL_RUN_ID,
    )

    assert result is True
    lock_key = asset_lock_manager._get_asset_lock_key(TEST_ASSET_TYPE, TEST_ASSET_NAME)
    reservation_key = asset_lock_manager._get_reservation_data_key(TEST_RESERVATION_ID)
    protocol_locks_key = asset_lock_manager._get_protocol_locks_key(
      TEST_PROTOCOL_RUN_ID,
    )

    # Verify atomic check-and-delete was called
    mock_redis_client.eval.assert_awaited_once()
    args = mock_redis_client.eval.await_args
    assert lock_key in args[0][1]  # Check KEYS[1]
    assert str(TEST_RESERVATION_ID) in args[0][2]  # Check ARGV[1]

    # Verify cleanup
    mock_redis_client.delete.assert_awaited_once_with(reservation_key)
    mock_redis_client.srem.assert_awaited_once_with(protocol_locks_key, lock_key)

  async def test_release_lock_failure_not_owner(
    self, asset_lock_manager, mock_redis_client,
  ):
    """Test failing to release a lock not owned by the reservation_id."""
    mock_redis_client.eval.return_value = (
      0  # Lua script returns 0 if value doesn't match
    )

    result = await asset_lock_manager.release_asset_lock(
      TEST_ASSET_TYPE, TEST_ASSET_NAME, TEST_RESERVATION_ID,
    )

    assert result is False
    mock_redis_client.eval.assert_awaited_once()
    mock_redis_client.delete.assert_not_awaited()
    mock_redis_client.srem.assert_not_awaited()

  async def test_release_lock_redis_error(self, asset_lock_manager, mock_redis_client):
    """Test that an exception during lock release returns False."""
    mock_redis_client.eval.side_effect = Exception("Redis script error")

    result = await asset_lock_manager.release_asset_lock(
      TEST_ASSET_TYPE, TEST_ASSET_NAME, TEST_RESERVATION_ID,
    )

    assert result is False


@pytest.mark.asyncio
class TestReleaseAllProtocolLocks:
  """Tests for the release_all_protocol_locks method."""

  async def test_release_all_success(self, asset_lock_manager, mock_redis_client):
    """Test releasing all locks for a protocol run."""
    lock_key1 = f"praxis:asset_lock:{TEST_ASSET_TYPE}:{TEST_ASSET_NAME}"
    lock_key2 = "praxis:asset_lock:resource:tip_box_1"
    res_id1 = uuid.UUID("018f3dd6-b413-75b1-9121-39a7b9e73b22")
    res_id2 = uuid.UUID("018f3dd6-b816-728b-8a4a-50f0c2999516")

    protocol_locks_key = asset_lock_manager._get_protocol_locks_key(
      TEST_PROTOCOL_RUN_ID,
    )
    mock_redis_client.smembers.return_value = {lock_key1, lock_key2}
    mock_redis_client.get.side_effect = [str(res_id1), str(res_id2)]

    # Patch release_asset_lock to simplify this test
    with patch.object(
      asset_lock_manager, "release_asset_lock", new_callable=AsyncMock,
    ) as mock_release:
      mock_release.return_value = True
      released_count = await asset_lock_manager.release_all_protocol_locks(
        TEST_PROTOCOL_RUN_ID,
      )

      assert released_count == 2
      mock_redis_client.smembers.assert_awaited_once_with(protocol_locks_key)
      # The order of get calls is not guaranteed due to set iteration
      assert mock_redis_client.get.await_count == 2
      assert mock_release.await_count == 2
      mock_redis_client.delete.assert_awaited_once_with(protocol_locks_key)

  async def test_release_all_with_invalid_lock_value(
    self, asset_lock_manager, mock_redis_client,
  ):
    """Test cleanup when a lock value is not a valid UUID."""
    lock_key = f"praxis:asset_lock:{TEST_ASSET_TYPE}:{TEST_ASSET_NAME}"
    protocol_locks_key = asset_lock_manager._get_protocol_locks_key(
      TEST_PROTOCOL_RUN_ID,
    )

    mock_redis_client.smembers.return_value = {lock_key}
    mock_redis_client.get.return_value = "invalid-uuid-string"

    released_count = await asset_lock_manager.release_all_protocol_locks(
      TEST_PROTOCOL_RUN_ID,
    )

    assert released_count == 1
    # It should just delete the lock key directly
    mock_redis_client.delete.assert_any_await(lock_key)
    # And also delete the protocol tracking key
    mock_redis_client.delete.assert_any_await(protocol_locks_key)

  async def test_release_all_no_locks(self, asset_lock_manager, mock_redis_client):
    """Test releasing when the protocol has no locks."""
    mock_redis_client.smembers.return_value = set()
    released_count = await asset_lock_manager.release_all_protocol_locks(
      TEST_PROTOCOL_RUN_ID,
    )
    assert released_count == 0
    mock_redis_client.delete.assert_awaited_once()  # Deletes the empty set


@pytest.mark.asyncio
class TestCheckAssetAvailability:
  """Tests for check_asset_availability method."""

  async def test_check_available(self, asset_lock_manager, mock_redis_client):
    """Test checking an asset that is available (not locked)."""
    lock_key = asset_lock_manager._get_asset_lock_key(TEST_ASSET_TYPE, TEST_ASSET_NAME)
    mock_redis_client.get.return_value = None
    result = await asset_lock_manager.check_asset_availability(
      TEST_ASSET_TYPE, TEST_ASSET_NAME,
    )
    assert result is None
    mock_redis_client.get.assert_awaited_once_with(lock_key)

  async def test_check_locked_with_metadata(
    self, asset_lock_manager, mock_redis_client,
  ):
    """Test checking a locked asset with valid metadata."""
    reservation_data = {"reservation_id": str(TEST_RESERVATION_ID), "status": "ok"}
    lock_key = asset_lock_manager._get_asset_lock_key(TEST_ASSET_TYPE, TEST_ASSET_NAME)
    reservation_key = asset_lock_manager._get_reservation_data_key(TEST_RESERVATION_ID)

    mock_redis_client.get.side_effect = [
      str(TEST_RESERVATION_ID),  # First call for lock key
      json.dumps(reservation_data),  # Second call for reservation data
    ]

    result = await asset_lock_manager.check_asset_availability(
      TEST_ASSET_TYPE, TEST_ASSET_NAME,
    )
    assert result == reservation_data
    assert mock_redis_client.get.await_args_list[0].args == (lock_key,)
    assert mock_redis_client.get.await_args_list[1].args == (reservation_key,)

  async def test_check_locked_no_metadata(self, asset_lock_manager, mock_redis_client):
    """Test a locked asset where metadata is missing."""
    lock_key = asset_lock_manager._get_asset_lock_key(TEST_ASSET_TYPE, TEST_ASSET_NAME)
    mock_redis_client.get.side_effect = [str(TEST_RESERVATION_ID), None]

    result = await asset_lock_manager.check_asset_availability(
      TEST_ASSET_TYPE, TEST_ASSET_NAME,
    )
    assert result == {
      "reservation_id": str(TEST_RESERVATION_ID),
      "asset_type": TEST_ASSET_TYPE,
      "asset_name": TEST_ASSET_NAME,
      "status": "locked_no_metadata",
    }

  async def test_check_locked_invalid_data(self, asset_lock_manager, mock_redis_client):
    """Test a locked asset with an invalid reservation ID."""
    lock_key = asset_lock_manager._get_asset_lock_key(TEST_ASSET_TYPE, TEST_ASSET_NAME)
    mock_redis_client.get.return_value = "not-a-uuid"

    result = await asset_lock_manager.check_asset_availability(
      TEST_ASSET_TYPE, TEST_ASSET_NAME,
    )
    assert result == {
      "reservation_id": "not-a-uuid",
      "asset_type": TEST_ASSET_TYPE,
      "asset_name": TEST_ASSET_NAME,
      "status": "locked_invalid_data",
    }


@pytest.mark.asyncio
class TestCleanupExpiredLocks:
  """Tests for the cleanup_expired_locks method."""

  async def test_cleanup_expired_lock(self, asset_lock_manager, mock_redis_client):
    """Test that an expired lock and its data are cleaned up."""
    lock_key = "praxis:asset_lock:machine:old_machine"
    res_id = uuid.UUID("018f3dd8-f682-747d-8182-45a2a223f6d7")
    res_key = asset_lock_manager._get_reservation_data_key(res_id)

    async def mock_scan_iter(*args, **kwargs):
      yield lock_key

    mock_redis_client.scan_iter.return_value = mock_scan_iter()
    mock_redis_client.exists.return_value = True
    mock_redis_client.get.side_effect = [
      str(res_id),
      json.dumps({"expires_at": "2020-01-01T00:00:00+00:00"}),  # Expired
    ]

    with freeze_time("2023-01-01 12:00:00 UTC"):
      count = await asset_lock_manager.cleanup_expired_locks()
      assert count == 1
      mock_redis_client.delete.assert_any_await(lock_key)
      mock_redis_client.delete.assert_any_await(res_key)

  async def test_cleanup_active_lock(self, asset_lock_manager, mock_redis_client):
    """Test that an active (not expired) lock is not cleaned up."""
    lock_key = "praxis:asset_lock:machine:active_machine"
    res_id = uuid.UUID("018f3dd9-ec12-705a-8ead-38a4d4a04d2c")

    async def mock_scan_iter(*args, **kwargs):
      yield lock_key

    mock_redis_client.scan_iter.return_value = mock_scan_iter()
    mock_redis_client.exists.return_value = True
    mock_redis_client.get.side_effect = [
      str(res_id),
      json.dumps({"expires_at": "2025-01-01T00:00:00+00:00"}),  # Not expired
    ]

    with freeze_time("2023-01-01 12:00:00 UTC"):
      count = await asset_lock_manager.cleanup_expired_locks()
      assert count == 0
      mock_redis_client.delete.assert_not_awaited()

  async def test_cleanup_orphaned_lock(self, asset_lock_manager, mock_redis_client):
    """Test that a lock without metadata and no TTL is cleaned up."""
    lock_key = "praxis:asset_lock:machine:orphaned_machine"
    res_id = uuid.UUID("018f3dda-0975-7b58-9a67-b7159c98a58e")

    async def mock_scan_iter(*args, **kwargs):
      yield lock_key

    mock_redis_client.scan_iter.return_value = mock_scan_iter()
    mock_redis_client.exists.return_value = True
    mock_redis_client.get.side_effect = [str(res_id), None]  # No metadata
    mock_redis_client.ttl = AsyncMock(return_value=-1)  # No TTL

    count = await asset_lock_manager.cleanup_expired_locks()
    assert count == 1
    mock_redis_client.delete.assert_awaited_once_with(lock_key)


@pytest.mark.asyncio
class TestSystemStatus:
  """Tests for the get_system_status method."""

  async def test_get_system_status_success(self, asset_lock_manager, mock_redis_client):
    """Test getting system status successfully."""

    async def mock_scan_iter_locks(*args, **kwargs):
      for i in range(5):
        yield f"lock_{i}"

    async def mock_scan_iter_res(*args, **kwargs):
      for i in range(4):
        yield f"res_{i}"

    async def mock_scan_iter_proto(*args, **kwargs):
      for i in range(2):
        yield f"proto_{i}"

    mock_redis_client.scan_iter.side_effect = [
      mock_scan_iter_locks(),
      mock_scan_iter_res(),
      mock_scan_iter_proto(),
    ]
    mock_redis_client.info.return_value = {
      "connected_clients": 10,
      "used_memory_human": "1.23M",
      "uptime_in_seconds": 86400,
    }

    with freeze_time("2023-01-01 12:00:00 UTC") as frozen_time:
      status = await asset_lock_manager.get_system_status()
      assert status == {
        "active_asset_locks": 5,
        "active_reservations": 4,
        "tracked_protocols": 2,
        "redis_connected_clients": 10,
        "redis_used_memory": "1.23M",
        "redis_uptime_seconds": 86400,
        "timestamp": "2023-01-01T12:00:00+00:00",
      }

  async def test_get_system_status_redis_error(
    self, asset_lock_manager, mock_redis_client,
  ):
    """Test system status returning an error on Redis failure."""
    mock_redis_client.scan_iter.side_effect = Exception("Redis is down")
    status = await asset_lock_manager.get_system_status()
    assert "error" in status
    assert status["error"] == "Redis is down"
