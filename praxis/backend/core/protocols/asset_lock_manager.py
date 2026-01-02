from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
  from pydantic import UUID7

  from praxis.backend.models.pydantic_internals.asset import AcquireAssetLock


class IAssetLockManager(Protocol):
  """A protocol for the asset lock manager."""

  async def acquire_asset_lock(
    self,
    lock_data: AcquireAssetLock,
  ) -> bool:
    """Acquire a distributed lock for an asset."""
    ...

  async def release_asset_lock(
    self,
    asset_type: str,
    asset_name: str,
    reservation_id: UUID7,
    protocol_run_id: UUID7 | None = None,
  ) -> bool:
    """Release a distributed lock for an asset."""
    ...

  async def release_all_protocol_locks(self, protocol_run_id: UUID7) -> int:
    """Release all locks held by a protocol run."""
    ...

  async def check_asset_availability(
    self,
    asset_type: str,
    asset_name: str,
  ) -> dict[str, Any] | None:
    """Check if an asset is currently available."""
    ...
