"""Asset lock manager for Praxis."""

import uuid

from praxis.backend.core.protocols.asset_lock_manager import IAssetLockManager
from praxis.backend.models.pydantic_internals.asset import AcquireAssetLock


class AssetLockManager(IAssetLockManager):
    """A simple in-memory asset lock manager."""

    def __init__(self) -> None:
        """Initialize the AssetLockManager."""
        self._locks: dict[str, AcquireAssetLock] = {}

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
        protocol_run_id: uuid.UUID,
        reservation_id: uuid.UUID,
    ) -> bool:
        """Release a lock on an asset."""
        lock_key = f"{asset_type}:{asset_name}"
        if lock_key in self._locks:
            del self._locks[lock_key]
            return True
        return False

    async def get_lock_status(
        self, asset_type: str, asset_name: str
    ) -> AcquireAssetLock | None:
        """Get the lock status of an asset."""
        lock_key = f"{asset_type}:{asset_name}"
        return self._locks.get(lock_key)
