# pylint: disable=too-many-arguments,broad-except,fixme
"""Redis-based Asset Lock Manager for Protocol Scheduling.

This module provides distributed asset locking and reservation management
using Redis as the coordination layer. It works alongside the database models
to provide robust asset conflict resolution for machines, resources, and decks.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import redis.asyncio as redis

from praxis.backend.models.asset_lock_manager_pydantic_models import AcquireAssetLock
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)


class AssetLockManager:
  """Redis-based distributed asset lock manager for protocol scheduling.

  This class provides atomic asset reservation operations using Redis
  distributed locks, ensuring no two protocol runs can reserve the same
  asset (machine, resource, or deck) simultaneously.
  """

  _ASSET_LOCK_KEY_PREFIX = "praxis:asset_lock"
  _PROTOCOL_LOCKS_KEY_PREFIX = "praxis:protocol_locks"
  _RESERVATION_DATA_KEY_PREFIX = "praxis:reservation"
  _REDIS_CLIENT_NOT_INITIALIZED_ERROR = "Redis client not initialized"
  _ASSET_KEY_PARTS_LENGTH = 4

  def __init__(
    self,
    redis_url: str = "redis://localhost:6379/0",
    lock_timeout_seconds: int = 3600,  # 1 hour default
    lock_retry_delay_ms: int = 100,
    max_lock_retries: int = 10,
  ) -> None:
    """Initialize the Asset Lock Manager.

    Args:
        redis_url: Redis connection URL
        lock_timeout_seconds: Default timeout for asset locks
        lock_retry_delay_ms: Delay between lock acquisition retries
        max_lock_retries: Maximum number of lock acquisition attempts

    """
    self.redis_url = redis_url
    self.lock_timeout_seconds = lock_timeout_seconds
    self.lock_retry_delay_ms = lock_retry_delay_ms
    self.max_lock_retries = max_lock_retries

    self._redis_pool: redis.ConnectionPool | None = None
    self._redis_client: redis.Redis | None = None

    logger.info("AssetLockManager initialized with Redis: %s", redis_url)

  async def initialize(self) -> None:
    """Initialize Redis connection pool."""
    try:
      self._redis_pool = redis.ConnectionPool.from_url(
        self.redis_url,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
      )
      self._redis_client = redis.Redis(connection_pool=self._redis_pool)

      # Test connection
      await self._redis_client.ping()
      logger.info("Redis connection established successfully")

    except Exception:
      logger.exception("Failed to initialize Redis connection")
      raise

  async def close(self) -> None:
    """Close Redis connections."""
    try:
      if self._redis_client:
        await self._redis_client.close()
      if self._redis_pool:
        await self._redis_pool.disconnect()
      logger.info("Redis connections closed")
    except Exception:
      logger.exception("Error closing Redis connections")

  def _get_asset_lock_key(self, asset_type: str, asset_name: str) -> str:
    """Generate Redis key for asset lock."""
    return f"{self._ASSET_LOCK_KEY_PREFIX}:{asset_type}:{asset_name}"

  def _get_protocol_locks_key(self, protocol_run_id: uuid.UUID) -> str:
    """Generate Redis key for tracking locks held by a protocol run."""
    return f"{self._PROTOCOL_LOCKS_KEY_PREFIX}:{protocol_run_id}"

  def _get_reservation_data_key(self, reservation_id: uuid.UUID) -> str:
    """Generate Redis key for reservation metadata."""
    return f"{self._RESERVATION_DATA_KEY_PREFIX}:{reservation_id}"

  async def acquire_asset_lock(
    self,
    lock_data: AcquireAssetLock,
  ) -> bool:
    """Acquire a distributed lock for an asset.

    Args:
        lock_data: Pydantic model containing asset lock data.

    Returns:
        True if lock was acquired, False otherwise

    """
    if not self._redis_client:
      raise RuntimeError(self._REDIS_CLIENT_NOT_INITIALIZED_ERROR)

    timeout = lock_data.timeout_seconds or self.lock_timeout_seconds
    lock_key = self._get_asset_lock_key(lock_data.asset_type, lock_data.asset_name)
    lock_value = str(lock_data.reservation_id)

    # Prepare reservation metadata
    reservation_data = {
      "reservation_id": str(lock_data.reservation_id),
      "protocol_run_id": str(lock_data.protocol_run_id),
      "asset_type": lock_data.asset_type,
      "asset_name": lock_data.asset_name,
      "locked_at": datetime.now(timezone.utc).isoformat(),
      "expires_at": (
        datetime.now(timezone.utc) + timedelta(seconds=timeout)
      ).isoformat(),
      "required_capabilities": lock_data.required_capabilities or {},
    }

    try:
      # Attempt to acquire lock with retries
      for _attempt in range(self.max_lock_retries):
        # Use SET with NX (only if not exists) and EX (expiration)
        lock_acquired = await self._redis_client.set(
          lock_key,
          lock_value,
          nx=True,  # Only set if key doesn't exist
          ex=timeout,  # Expiration in seconds
        )

        if lock_acquired:
          # Store reservation metadata
          reservation_key = self._get_reservation_data_key(lock_data.reservation_id)
          await self._redis_client.setex(
            reservation_key,
            timeout,
            json.dumps(reservation_data),
          )

          # Track locks held by this protocol run
          protocol_locks_key = self._get_protocol_locks_key(lock_data.protocol_run_id)
          await self._redis_client.sadd(protocol_locks_key, lock_key)
          await self._redis_client.expire(protocol_locks_key, timeout)

          logger.info(
            "Asset lock acquired: %s for protocol %s (reservation %s)",
            lock_key,
            lock_data.protocol_run_id,
            lock_data.reservation_id,
          )
          return True
        # Lock acquisition failed, wait and retry
        if _attempt < self.max_lock_retries - 1:
          await asyncio.sleep(self.lock_retry_delay_ms / 1000.0)
          logger.debug(
            "Lock acquisition attempt %d failed for %s, retrying...",
            _attempt + 1,
            lock_key,
          )

      logger.warning(
        "Failed to acquire asset lock after %d attempts: %s",
        self.max_lock_retries,
        lock_key,
      )
      return False

    except Exception:
      logger.exception("Error acquiring asset lock %s", lock_key)
      return False

  async def release_asset_lock(
    self,
    asset_type: str,
    asset_name: str,
    reservation_id: uuid.UUID,
    protocol_run_id: uuid.UUID | None = None,
  ) -> bool:
    """Release a distributed lock for an asset.

    Args:
        asset_type: Type of asset
        asset_name: Name/identifier of the asset
        reservation_id: Reservation ID that holds the lock
        protocol_run_id: Protocol run ID (for cleanup)

    Returns:
        True if lock was released, False otherwise

    """
    if not self._redis_client:
      raise RuntimeError(self._REDIS_CLIENT_NOT_INITIALIZED_ERROR)

    lock_key = self._get_asset_lock_key(asset_type, asset_name)
    lock_value = str(reservation_id)

    try:
      # Use Lua script for atomic check-and-delete
      lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """

      result = await self._redis_client.eval(lua_script, 1, lock_key, lock_value)

      if result:
        # Clean up reservation metadata
        reservation_key = self._get_reservation_data_key(reservation_id)
        await self._redis_client.delete(reservation_key)

        # Remove from protocol locks tracking
        if protocol_run_id:
          protocol_locks_key = self._get_protocol_locks_key(protocol_run_id)
          await self._redis_client.srem(protocol_locks_key, lock_key)

        logger.info(
          "Asset lock released: %s (reservation %s)",
          lock_key,
          reservation_id,
        )
        return True
      logger.warning(
        "Failed to release asset lock %s - lock not owned by reservation %s",
        lock_key,
        reservation_id,
      )
      return False

    except redis.exceptions.RedisError:
      logger.exception("Error releasing asset lock %s", lock_key)

  async def release_all_protocol_locks(self, protocol_run_id: uuid.UUID) -> int:
    """Release all locks held by a protocol run.

    Args:
        protocol_run_id: ID of the protocol run

    Returns:
        Number of locks released

    """
    if not self._redis_client:
      raise RuntimeError(self._REDIS_CLIENT_NOT_INITIALIZED_ERROR)

    protocol_locks_key = self._get_protocol_locks_key(protocol_run_id)
    released_count = 0

    try:
      # Get all locks held by this protocol
      lock_keys = await self._redis_client.smembers(protocol_locks_key)

      for lock_key in lock_keys:
        released = await self._release_single_protocol_lock(lock_key)
        if released:
          released_count += 1

      # Clean up protocol locks tracking
      await self._redis_client.delete(protocol_locks_key)

      logger.info(
        "Released %d locks for protocol %s",
        released_count,
        protocol_run_id,
      )
      return released_count

    except Exception:
      logger.exception("Error releasing all locks for protocol %s", protocol_run_id)
      return released_count

  async def _release_single_protocol_lock(self, lock_key: str) -> bool:
    """Release a single protocol lock."""
    try:
      current_value = await self._redis_client.get(lock_key)
      if not current_value:
        return False

      key_parts = lock_key.split(":")
      if len(key_parts) >= self._ASSET_KEY_PARTS_LENGTH:
        asset_type = key_parts[2]
        asset_name = key_parts[3]

        try:
          reservation_id = uuid.UUID(current_value)
          if await self.release_asset_lock(
            asset_type, asset_name, reservation_id,
          ):
            return True
        except ValueError:
          await self._redis_client.delete(lock_key)
          return True
    except redis.exceptions.RedisError:
      logger.exception(
            "Error releasing individual lock %s",
            lock_key,
          )
    return False

  async def check_asset_availability(
    self,
    asset_type: str,
    asset_name: str,
  ) -> dict[str, Any] | None:
    """Check if an asset is currently available.

    Args:
        asset_type: Type of asset
        asset_name: Name/identifier of the asset

    Returns:
        None if available, reservation data if locked

    """
    if not self._redis_client:
      raise RuntimeError(self._REDIS_CLIENT_NOT_INITIALIZED_ERROR)

    lock_key = self._get_asset_lock_key(asset_type, asset_name)

    try:
      lock_value = await self._redis_client.get(lock_key)
      if not lock_value:
        return None  # Asset is available

      # Get reservation metadata
      try:
        reservation_id = uuid.UUID(lock_value)
        reservation_key = self._get_reservation_data_key(reservation_id)
        reservation_data_str = await self._redis_client.get(reservation_key)

        if reservation_data_str:
          return json.loads(reservation_data_str)
        # Lock exists but no metadata, return basic info
        return {
          "reservation_id": lock_value,
          "asset_type": asset_type,
          "asset_name": asset_name,
          "status": "locked_no_metadata",
        }

      except (ValueError, json.JSONDecodeError):
        # Invalid lock value or metadata
        return {
          "reservation_id": lock_value,
          "asset_type": asset_type,
          "asset_name": asset_name,
          "status": "locked_invalid_data",
        }

    except Exception as e:
      logger.exception(
        "Error checking asset availability %s:%s",
        asset_type,
        asset_name,
      )
      # Return as unavailable on error to be safe
      return {
        "error": str(e),
        "status": "check_failed",
      }

  async def cleanup_expired_locks(self) -> int:
    """Clean up expired asset locks and orphaned data.

    This should be called periodically to clean up any locks that
    might have been left behind due to system failures.

    Returns:
        Number of locks cleaned up

    """
    if not self._redis_client:
      raise RuntimeError(self._REDIS_CLIENT_NOT_INITIALIZED_ERROR)

    cleaned_count = 0

    try:
      # Find all asset lock keys
      lock_pattern = "praxis:asset_lock:*"
      lock_keys = [key async for key in self._redis_client.scan_iter(match=lock_pattern)]

      logger.info("Found %d asset locks to check for expiration", len(lock_keys))

      for lock_key in lock_keys:
        cleaned = await self._cleanup_single_lock(lock_key)
        if cleaned:
          cleaned_count += 1

      if cleaned_count > 0:
        logger.info("Cleaned up %d expired/orphaned asset locks", cleaned_count)

      return cleaned_count

    except Exception:
      logger.exception("Error during lock cleanup")
      return cleaned_count

  async def _cleanup_single_lock(self, lock_key: str) -> bool:
    """Clean up a single expired or orphaned lock."""
    try:
      if not await self._redis_client.exists(lock_key):
        return False

      lock_value = await self._redis_client.get(lock_key)
      if not lock_value:
        return False

      try:
        reservation_id = uuid.UUID(lock_value)
        reservation_key = self._get_reservation_data_key(reservation_id)
        reservation_data_str = await self._redis_client.get(reservation_key)

        if reservation_data_str:
          reservation_data = json.loads(reservation_data_str)
          expires_at_str = reservation_data.get("expires_at")

          if expires_at_str:
            expires_at = datetime.fromisoformat(
              expires_at_str.replace("Z", "+00:00"),
            )
            if datetime.now(timezone.utc) > expires_at:
              await self._redis_client.delete(lock_key)
              await self._redis_client.delete(reservation_key)
              logger.debug(
                "Cleaned up expired lock: %s (expired at %s)",
                lock_key,
                expires_at,
              )
              return True
        else:
          ttl = await self._redis_client.ttl(lock_key)
          if ttl == -1:
            await self._redis_client.delete(lock_key)
            logger.debug("Cleaned up orphaned lock: %s", lock_key)
            return True

      except (ValueError, json.JSONDecodeError):
        await self._redis_client.delete(lock_key)
        logger.debug("Cleaned up invalid lock: %s", lock_key)
        return True

    except redis.exceptions.RedisError:
      logger.exception(
        "Error checking lock %s during cleanup",
        lock_key,
      )
    return False

  async def get_system_status(self) -> dict[str, Any]:
    """Get current system status for monitoring.

    Returns:
        Dictionary with system status information

    """
    if not self._redis_client:
      return {"error": "Redis client not initialized"}

    try:
      # Count active locks
      lock_pattern = "praxis:asset_lock:*"
      active_locks = [key async for key in self._redis_client.scan_iter(match=lock_pattern)]

      # Count reservations
      reservation_pattern = "praxis:reservation:*"
      active_reservations = [key async for key in self._redis_client.scan_iter(match=reservation_pattern)]

      # Count protocol lock tracking
      protocol_locks_pattern = "praxis:protocol_locks:*"
      tracked_protocols = [key async for key in self._redis_client.scan_iter(match=protocol_locks_pattern)]

      # Redis info
      redis_info = await self._redis_client.info()

      return {
        "active_asset_locks": active_locks,
        "active_reservations": active_reservations,
        "tracked_protocols": tracked_protocols,
        "redis_connected_clients": redis_info.get("connected_clients", 0),
        "redis_used_memory": redis_info.get("used_memory_human", "unknown"),
        "redis_uptime_seconds": redis_info.get("uptime_in_seconds", 0),
        "timestamp": datetime.now(timezone.utc).isoformat(),
      }

    except Exception as e:
      logger.exception("Error getting system status")
      return {
        "error": str(e),
        "timestamp": datetime.now(timezone.utc).isoformat(),
      }
