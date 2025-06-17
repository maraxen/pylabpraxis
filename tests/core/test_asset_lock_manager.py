"""Unit tests for the AssetLockManager component."""

from unittest.mock import MagicMock, patch

import pytest
import redis.asyncio as redis  # Import for patching

# Assuming AssetLockManager is in praxis.backend.core.asset_lock_manager
# Adjust the import path if necessary
from praxis.backend.core.asset_lock_manager import AssetLockManager


@pytest.fixture
def mock_redis_client():
  """Fixture for a mocked Redis client."""
  client = MagicMock(spec=redis.Redis)  # Use spec for better mocking
  return client


@pytest.fixture
@patch("redis.asyncio.from_url")  # Patch where it's looked up
def asset_lock_manager(mock_from_url, mock_redis_client):
  """Fixture for AssetLockManager instance with a mocked Redis client."""
  mock_from_url.return_value = mock_redis_client  # from_url returns our mock client
  return AssetLockManager(redis_url="redis://mock_host:1234/0")


class TestAssetLockManager:
  """Test suite for the AssetLockManager."""

  def test_acquire_lock_success(self, asset_lock_manager, mock_redis_client):
    """Test successful lock acquisition."""
    asset_id = "plate_reader_1"
    run_id = "run_123"
    lock_key = f"lock:asset:{asset_id}"

    mock_redis_client.set.return_value = True

    acquired = asset_lock_manager.acquire_lock(asset_id, run_id, timeout_seconds=60)

    assert acquired is True
    mock_redis_client.set.assert_called_once_with(lock_key, run_id, ex=60, nx=True)

  def test_acquire_lock_failure_already_locked(
    self, asset_lock_manager, mock_redis_client
  ):
    """Test lock acquisition failure when asset is already locked."""
    asset_id = "plate_reader_1"
    run_id = "run_123"
    lock_key = f"lock:asset:{asset_id}"

    mock_redis_client.set.return_value = False

    acquired = asset_lock_manager.acquire_lock(asset_id, run_id, timeout_seconds=60)

    assert acquired is False
    mock_redis_client.set.assert_called_once_with(lock_key, run_id, ex=60, nx=True)

  def test_acquire_lock_redis_error(self, asset_lock_manager, mock_redis_client):
    """Test lock acquisition failure due to Redis error."""
    asset_id = "plate_reader_1"
    run_id = "run_123"
    lock_key = f"lock:asset:{asset_id}"

    mock_redis_client.set.side_effect = redis.RedisError("Redis connection error")

    acquired = asset_lock_manager.acquire_lock(asset_id, run_id, timeout_seconds=60)
    assert acquired is False

    mock_redis_client.set.assert_called_once_with(lock_key, run_id, ex=60, nx=True)

  def test_release_lock_success(self, asset_lock_manager, mock_redis_client):
    """Test successful lock release."""
    asset_id = "plate_reader_1"
    run_id = "run_456"
    lock_key = f"lock:asset:{asset_id}"

    # Redis client returns bytes
    mock_redis_client.get.return_value = run_id.encode("utf-8")
    mock_redis_client.delete.return_value = 1  # 1 key deleted

    released = asset_lock_manager.release_lock(asset_id, run_id)

    assert released is True
    mock_redis_client.get.assert_called_once_with(lock_key)
    mock_redis_client.delete.assert_called_once_with(lock_key)

  def test_release_lock_not_holder(self, asset_lock_manager, mock_redis_client):
    """Test lock release failure when not the lock holder."""
    asset_id = "plate_reader_1"
    current_holder_run_id = "run_789"
    attempting_run_id = "run_000"
    lock_key = f"lock:asset:{asset_id}"

    mock_redis_client.get.return_value = current_holder_run_id.encode("utf-8")

    released = asset_lock_manager.release_lock(asset_id, attempting_run_id)

    assert released is False
    mock_redis_client.get.assert_called_once_with(lock_key)
    mock_redis_client.delete.assert_not_called()

  def test_release_lock_not_locked(self, asset_lock_manager, mock_redis_client):
    """Test lock release when asset is not locked."""
    asset_id = "plate_reader_1"
    run_id = "run_123"
    lock_key = f"lock:asset:{asset_id}"

    mock_redis_client.get.return_value = None

    released = asset_lock_manager.release_lock(asset_id, run_id)

    assert released is True
    mock_redis_client.get.assert_called_once_with(lock_key)
    mock_redis_client.delete.assert_not_called()

  def test_release_lock_redis_get_error(self, asset_lock_manager, mock_redis_client):
    """Test lock release failure due to Redis error on GET."""
    asset_id = "plate_reader_1"
    run_id = "run_123"
    lock_key = f"lock:asset:{asset_id}"

    mock_redis_client.get.side_effect = redis.RedisError("Redis GET error")

    released = asset_lock_manager.release_lock(asset_id, run_id)
    assert released is False

    mock_redis_client.get.assert_called_once_with(lock_key)
    mock_redis_client.delete.assert_not_called()

  def test_release_lock_redis_delete_error(self, asset_lock_manager, mock_redis_client):
    """Test lock release failure due to Redis error on DELETE."""
    asset_id = "plate_reader_1"
    run_id = "run_123"
    lock_key = f"lock:asset:{asset_id}"

    mock_redis_client.get.return_value = run_id.encode("utf-8")
    mock_redis_client.delete.side_effect = redis.RedisError("Redis DELETE error")

    released = asset_lock_manager.release_lock(asset_id, run_id)
    assert released is False

    mock_redis_client.get.assert_called_once_with(lock_key)
    mock_redis_client.delete.assert_called_once_with(lock_key)
