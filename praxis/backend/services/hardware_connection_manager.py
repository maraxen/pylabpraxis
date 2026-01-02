"""Hardware connection state manager with persistent storage.

This service manages hardware device connection states using a pluggable
KeyValueStore backend. Connection states are persisted in Redis (production)
or SQLite (lite mode), ensuring they survive server restarts.

Features:
- Connection state persistence across restarts
- TTL-based heartbeat for automatic cleanup of stale connections
- Multi-worker safe (via Redis or SQLite file locking)
- Mode-agnostic (works with both Redis and SQLite backends)

Key Patterns:
- "hw:conn:{device_id}" -> ConnectionState JSON
- "hw:conn:index" -> JSON list of active device IDs

Usage:
    manager = HardwareConnectionManager(kv_store)
    state = await manager.connect("device-123", "Backend", {"port": "/dev/ttyUSB0"})
    await manager.heartbeat("device-123")
    connections = await manager.list_connections()
    await manager.disconnect("device-123")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
  from praxis.backend.core.storage.protocols import KeyValueStore

logger = logging.getLogger(__name__)

# Key patterns for KV store
KEY_PREFIX = "hw:conn:"
KEY_INDEX = "hw:conn:index"

# Connection TTL (seconds) - connections without heartbeat are considered stale
CONNECTION_TTL = 120  # 2 minutes


@dataclass
class ConnectionState:
  """Represents the state of a hardware device connection.

  Attributes:
      device_id: Unique identifier for the device (e.g., "serial-/dev/ttyUSB0").
      status: Current connection status.
      connected_at: Timestamp when connection was established.
      last_heartbeat: Timestamp of last heartbeat/activity.
      backend_class: PyLabRobot backend class name (e.g., "STAR").
      config: Backend-specific configuration (port, baud rate, etc.).
      error_message: Error details if status is "error".

  """

  device_id: str
  status: Literal["connecting", "connected", "disconnected", "error"]
  connected_at: datetime | None
  last_heartbeat: datetime
  backend_class: str | None
  config: dict[str, Any]
  error_message: str | None = None

  def to_dict(self) -> dict[str, Any]:
    """Convert to JSON-serializable dictionary."""
    return {
      "device_id": self.device_id,
      "status": self.status,
      "connected_at": self.connected_at.isoformat() if self.connected_at else None,
      "last_heartbeat": self.last_heartbeat.isoformat(),
      "backend_class": self.backend_class,
      "config": self.config,
      "error_message": self.error_message,
    }

  @classmethod
  def from_dict(cls, data: dict[str, Any]) -> ConnectionState:
    """Create ConnectionState from dictionary."""
    return cls(
      device_id=data["device_id"],
      status=data["status"],
      connected_at=datetime.fromisoformat(data["connected_at"]) if data["connected_at"] else None,
      last_heartbeat=datetime.fromisoformat(data["last_heartbeat"]),
      backend_class=data.get("backend_class"),
      config=data.get("config", {}),
      error_message=data.get("error_message"),
    )


class HardwareConnectionManager:
  """Manages hardware connection states using KeyValueStore.

  This service provides persistent storage for hardware connection states,
  allowing connection status to survive server restarts. It uses a heartbeat
  mechanism with TTL to automatically clean up stale connections.

  Example:
      kv_store = StorageFactory.create_key_value_store(backend)
      manager = HardwareConnectionManager(kv_store)

      # Connect to a device
      state = await manager.connect(
          device_id="serial-/dev/ttyUSB0",
          backend_class="STAR",
          config={"baud_rate": 9600}
      )

      # Keep connection alive
      await manager.heartbeat("serial-/dev/ttyUSB0")

      # List all connections
      connections = await manager.list_connections()

      # Disconnect
      await manager.disconnect("serial-/dev/ttyUSB0")

  """

  def __init__(
    self,
    kv_store: KeyValueStore,
    ttl_seconds: int = CONNECTION_TTL,
  ) -> None:
    """Initialize the connection manager.

    Args:
        kv_store: KeyValueStore instance for persistence.
        ttl_seconds: Time-to-live for connections without heartbeat.
            Connections that don't receive a heartbeat within this
            time are considered stale.

    """
    self._kv = kv_store
    self._ttl = ttl_seconds

  def _get_key(self, device_id: str) -> str:
    """Get the KV store key for a device."""
    return f"{KEY_PREFIX}{device_id}"

  async def _add_to_index(self, device_id: str) -> None:
    """Add device to the index of active connections."""
    index_data = await self._kv.get(KEY_INDEX)
    index: list[str] = index_data if isinstance(index_data, list) else []
    if device_id not in index:
      index.append(device_id)
      await self._kv.set(KEY_INDEX, index)

  async def _remove_from_index(self, device_id: str) -> None:
    """Remove device from the index of active connections."""
    index_data = await self._kv.get(KEY_INDEX)
    index: list[str] = index_data if isinstance(index_data, list) else []
    if device_id in index:
      index.remove(device_id)
      await self._kv.set(KEY_INDEX, index)

  async def connect(
    self,
    device_id: str,
    backend_class: str | None,
    config: dict[str, Any] | None = None,
  ) -> ConnectionState:
    """Register a device as connecting/connected.

    Args:
        device_id: Unique identifier for the device.
        backend_class: PyLabRobot backend class name.
        config: Backend-specific configuration.

    Returns:
        The connection state after registration.

    """
    now = datetime.now(UTC)
    state = ConnectionState(
      device_id=device_id,
      status="connected",
      connected_at=now,
      last_heartbeat=now,
      backend_class=backend_class,
      config=config or {},
      error_message=None,
    )

    # Store with TTL
    key = self._get_key(device_id)
    await self._kv.set(key, state.to_dict(), ttl_seconds=self._ttl)
    await self._add_to_index(device_id)

    logger.info(
      "Device connected: %s (backend: %s, TTL: %ds)",
      device_id,
      backend_class,
      self._ttl,
    )
    return state

  async def set_connecting(
    self,
    device_id: str,
    backend_class: str | None,
    config: dict[str, Any] | None = None,
  ) -> ConnectionState:
    """Mark a device as connecting (in progress).

    Args:
        device_id: Unique identifier for the device.
        backend_class: PyLabRobot backend class name.
        config: Backend-specific configuration.

    Returns:
        The connection state.

    """
    now = datetime.now(UTC)
    state = ConnectionState(
      device_id=device_id,
      status="connecting",
      connected_at=None,
      last_heartbeat=now,
      backend_class=backend_class,
      config=config or {},
      error_message=None,
    )

    key = self._get_key(device_id)
    await self._kv.set(key, state.to_dict(), ttl_seconds=self._ttl)
    await self._add_to_index(device_id)

    logger.info("Device connecting: %s (backend: %s)", device_id, backend_class)
    return state

  async def disconnect(self, device_id: str) -> bool:
    """Disconnect a device and remove its state.

    Args:
        device_id: Unique identifier for the device.

    Returns:
        True if the device was disconnected, False if it wasn't connected.

    """
    key = self._get_key(device_id)
    existed = await self._kv.delete(key)
    await self._remove_from_index(device_id)

    if existed:
      logger.info("Device disconnected: %s", device_id)
    return existed

  async def heartbeat(self, device_id: str) -> ConnectionState | None:
    """Update the heartbeat timestamp for a connection.

    This should be called periodically to keep the connection alive.
    Connections without heartbeats will expire after TTL.

    Args:
        device_id: Unique identifier for the device.

    Returns:
        The updated connection state, or None if not connected.

    """
    key = self._get_key(device_id)
    data = await self._kv.get(key)

    if data is None:
      logger.warning("Heartbeat for unknown device: %s", device_id)
      return None

    state = ConnectionState.from_dict(data)
    state.last_heartbeat = datetime.now(UTC)

    # Refresh TTL
    await self._kv.set(key, state.to_dict(), ttl_seconds=self._ttl)
    logger.debug("Heartbeat received: %s", device_id)
    return state

  async def get_connection(self, device_id: str) -> ConnectionState | None:
    """Get the connection state for a device.

    Args:
        device_id: Unique identifier for the device.

    Returns:
        The connection state, or None if not connected.

    """
    key = self._get_key(device_id)
    data = await self._kv.get(key)

    if data is None:
      return None

    return ConnectionState.from_dict(data)

  async def set_error(
    self,
    device_id: str,
    error_message: str,
  ) -> ConnectionState | None:
    """Mark a connection as having an error.

    Args:
        device_id: Unique identifier for the device.
        error_message: Description of the error.

    Returns:
        The updated connection state, or None if not connected.

    """
    key = self._get_key(device_id)
    data = await self._kv.get(key)

    if data is None:
      logger.warning("Set error for unknown device: %s", device_id)
      return None

    state = ConnectionState.from_dict(data)
    state.status = "error"
    state.error_message = error_message
    state.last_heartbeat = datetime.now(UTC)

    # Keep TTL active so error state is visible
    await self._kv.set(key, state.to_dict(), ttl_seconds=self._ttl)
    logger.error("Device error: %s - %s", device_id, error_message)
    return state

  async def list_connections(self) -> list[ConnectionState]:
    """List all active connections.

    Returns:
        List of all current connection states.

    """
    # Get device IDs from index
    index_data = await self._kv.get(KEY_INDEX)
    index: list[str] = index_data if isinstance(index_data, list) else []

    connections: list[ConnectionState] = []
    stale_ids: list[str] = []

    for device_id in index:
      state = await self.get_connection(device_id)
      if state is not None:
        connections.append(state)
      else:
        # Connection expired, mark for cleanup
        stale_ids.append(device_id)

    # Clean up stale entries from index
    for device_id in stale_ids:
      await self._remove_from_index(device_id)

    logger.debug(
      "Listed %d connections (%d stale removed)",
      len(connections),
      len(stale_ids),
    )
    return connections

  async def clear_all(self) -> int:
    """Clear all connection states.

    Returns:
        Number of connections cleared.

    """
    connections = await self.list_connections()
    count = len(connections)

    for state in connections:
      await self._kv.delete(self._get_key(state.device_id))

    await self._kv.delete(KEY_INDEX)
    logger.info("Cleared %d connections", count)
    return count
