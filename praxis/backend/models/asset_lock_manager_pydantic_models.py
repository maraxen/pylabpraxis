# pylint: disable=too-few-public-methods
"""Pydantic models for the AssetLockManager.

This module provides Pydantic models for the AssetLockManager,
enabling proper validation and serialization for asset lock management.
"""

from typing import Any
from uuid import UUID

from pydantic import BaseModel


class AcquireAssetLock(BaseModel):
    """Model for acquiring an asset lock."""

    asset_type: str
    asset_name: str
    protocol_run_id: UUID
    reservation_id: UUID
    timeout_seconds: int | None = None
    required_capabilities: dict[str, Any] | None = None
