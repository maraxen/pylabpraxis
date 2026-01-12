"""Asset lock manager for Praxis."""

import uuid
from typing import Any

from praxis.backend.core.protocols.asset_lock_manager import IAssetLockManager
from praxis.backend.models.pydantic_internals.runtime import AcquireAssetLock


class AssetLockManager(IAssetLockManager):
  """A simple in-memory asset lock manager."""

  def __init__(self, redis_url: str | None = None) -> None:
    """Initialize the AssetLockManager."""
    self._locks: dict[str, AcquireAssetLock] = {}
    # Redis URL is ignored for in-memory implementation

  async def initialize(self) -> None:
    """Initialize the asset lock manager."""
    # No-op for in-memory implementation

  async def acquire_asset_lock(self, lock_data: AcquireAssetLock) -> bool:
    """Acquire a lock on an asset."""
    lock_key = f"{lock_data.asset_type}:{lock_data.asset_name}"
    if lock_key in self._locks:
      return False
    self._locks[lock_key] = lock_data
    return True

  async def release_asset_lock(
    self,
    asset_type: str,
    asset_name: str,
    reservation_id: uuid.UUID,
    protocol_run_id: uuid.UUID | None = None,
  ) -> bool:
    """Release a lock on an asset."""
    lock_key = f"{asset_type}:{asset_name}"
    if lock_key in self._locks:
      del self._locks[lock_key]
      return True
    return False

  async def release_all_protocol_locks(self, protocol_run_id: uuid.UUID) -> int:
    """Release all locks held by a protocol run."""
    keys_to_release = []
    for key, lock in self._locks.items():
      if lock.protocol_run_id == protocol_run_id:
        keys_to_release.append(key)

    count = 0
    for key in keys_to_release:
      del self._locks[key]
      count += 1
    return count

  async def check_asset_availability(
    self,
    asset_type: str,
    asset_name: str,
  ) -> dict[str, Any] | None:
    """Check if an asset is currently available."""
    lock_key = f"{asset_type}:{asset_name}"
    lock = self._locks.get(lock_key)
    if lock:
      return lock.model_dump(mode="json")
    return None

  async def get_lock_status(
    self,
    asset_type: str,
    asset_name: str,
  ) -> AcquireAssetLock | None:
    """Get the lock status of an asset."""
    lock_key = f"{asset_type}:{asset_name}"
    return self._locks.get(lock_key)
