"""SQLite-backed key-value store for lite mode deployment.

This adapter provides persistent key-value storage using SQLite, enabling
the lite mode to survive restarts without requiring Redis. It implements
the KeyValueStore protocol with full TTL support.

Features:
- Persistent storage (survives process restarts)
- TTL support with lazy expiration
- fnmatch-based pattern matching for keys()
- Single file database (no external dependencies)

Usage:
    store = SqliteKeyValueStore("praxis_kv.db")
    await store.set("hw:conn:device-1", {"status": "connected"}, ttl_seconds=120)
    state = await store.get("hw:conn:device-1")
"""

import asyncio
import contextlib
import fnmatch
import json
import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class SqliteKeyValueStore:
  """SQLite-backed key-value store with TTL support.

  Stores JSON-serializable values in a SQLite database with optional
  expiration times. Expired entries are cleaned up lazily on access
  and periodically via a background task.
  """

  def __init__(self, path: str = "praxis_kv.db") -> None:
    """Initialize the SQLite key-value store.

    Args:
        path: Path to the SQLite database file. Use ":memory:" for
            in-memory storage (useful for testing).

    """
    self._path = path
    self._conn: Any | None = None  # aiosqlite.Connection
    self._lock = asyncio.Lock()
    self._cleanup_task: asyncio.Task | None = None
    self._closed = False

  async def _ensure_connection(self) -> Any:
    """Ensure database connection is established and schema exists.

    Returns:
        The aiosqlite connection object.

    """
    if self._conn is None:
      try:
        import aiosqlite
      except ImportError:
        msg = "aiosqlite is required for SqliteKeyValueStore. Install with: pip install aiosqlite"
        raise ImportError(msg)  # noqa: B904

      self._conn = await aiosqlite.connect(self._path)
      # Enable WAL mode for better concurrent access
      await self._conn.execute("PRAGMA journal_mode=WAL")
      # Create table if not exists
      await self._conn.execute("""
        CREATE TABLE IF NOT EXISTS kv_store (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL,
          expires_at REAL
        )
      """)
      # Create index for expiration cleanup
      await self._conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_kv_expires
        ON kv_store(expires_at)
        WHERE expires_at IS NOT NULL
      """)
      await self._conn.commit()
      logger.info("SQLite KeyValueStore initialized: %s", self._path)

      # Start background cleanup
      if self._cleanup_task is None or self._cleanup_task.done():
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_keys())

    return self._conn

  async def _cleanup_expired_keys(self) -> None:
    """Periodically remove expired keys from the database."""
    while not self._closed:
      try:
        await asyncio.sleep(60.0)  # Check every minute
        async with self._lock:
          conn = await self._ensure_connection()
          now = time.time()
          cursor = await conn.execute(
            "DELETE FROM kv_store WHERE expires_at IS NOT NULL AND expires_at <= ?",
            (now,),
          )
          await conn.commit()
          if cursor.rowcount > 0:
            logger.debug("Cleaned up %d expired keys", cursor.rowcount)
      except asyncio.CancelledError:
        break
      except Exception:
        logger.exception("Error in TTL cleanup task")

  async def get(self, key: str) -> Any | None:
    """Retrieve a value by key.

    Args:
        key: The key to look up.

    Returns:
        The stored value (deserialized from JSON), or None if the key
        doesn't exist or has expired.

    """
    async with self._lock:
      conn = await self._ensure_connection()
      now = time.time()

      cursor = await conn.execute(
        """
        SELECT value, expires_at FROM kv_store
        WHERE key = ?
        """,
        (key,),
      )
      row = await cursor.fetchone()

      if row is None:
        return None

      value_json, expires_at = row

      # Check if expired
      if expires_at is not None and expires_at <= now:
        # Lazy cleanup
        await conn.execute("DELETE FROM kv_store WHERE key = ?", (key,))
        await conn.commit()
        logger.debug("Lazy cleanup of expired key: %s", key)
        return None

      return json.loads(value_json)

  async def set(
    self,
    key: str,
    value: Any,
    ttl_seconds: int | None = None,
  ) -> None:
    """Store a value with optional TTL.

    Args:
        key: The key to store under.
        value: The value to store (must be JSON-serializable).
        ttl_seconds: Optional time-to-live in seconds. If None, the key
            persists until explicitly deleted.

    """
    async with self._lock:
      conn = await self._ensure_connection()

      expires_at = time.time() + ttl_seconds if ttl_seconds is not None else None
      value_json = json.dumps(value)

      await conn.execute(
        """
        INSERT OR REPLACE INTO kv_store (key, value, expires_at)
        VALUES (?, ?, ?)
        """,
        (key, value_json, expires_at),
      )
      await conn.commit()
      logger.debug("Set key: %s (TTL: %s)", key, ttl_seconds)

  async def delete(self, key: str) -> bool:
    """Delete a key.

    Args:
        key: The key to delete.

    Returns:
        True if the key was deleted, False if it didn't exist.

    """
    async with self._lock:
      conn = await self._ensure_connection()

      cursor = await conn.execute(
        "DELETE FROM kv_store WHERE key = ?",
        (key,),
      )
      await conn.commit()

      deleted = cursor.rowcount > 0
      if deleted:
        logger.debug("Deleted key: %s", key)
      return deleted

  async def exists(self, key: str) -> bool:
    """Check if a key exists.

    Args:
        key: The key to check.

    Returns:
        True if the key exists and hasn't expired.

    """
    async with self._lock:
      conn = await self._ensure_connection()
      now = time.time()

      cursor = await conn.execute(
        """
        SELECT 1 FROM kv_store
        WHERE key = ?
        AND (expires_at IS NULL OR expires_at > ?)
        """,
        (key, now),
      )
      row = await cursor.fetchone()
      return row is not None

  async def keys(self, pattern: str = "*") -> list[str]:
    """List keys matching a glob pattern.

    Args:
        pattern: Glob-style pattern (e.g., "user:*"). Default "*" matches all.

    Returns:
        List of matching keys.

    """
    async with self._lock:
      conn = await self._ensure_connection()
      now = time.time()

      # Fetch all non-expired keys
      cursor = await conn.execute(
        """
        SELECT key FROM kv_store
        WHERE expires_at IS NULL OR expires_at > ?
        """,
        (now,),
      )
      rows = await cursor.fetchall()

      # Filter by pattern using fnmatch
      result = []
      for (key,) in rows:
        if fnmatch.fnmatch(key, pattern):
          result.append(key)

      return result

  async def close(self) -> None:
    """Close the database connection and release resources.

    Should be called during application shutdown.
    """
    self._closed = True

    if self._cleanup_task is not None:
      self._cleanup_task.cancel()
      with contextlib.suppress(asyncio.CancelledError):
        await self._cleanup_task

    if self._conn is not None:
      await self._conn.close()
      self._conn = None

    logger.info("SqliteKeyValueStore closed: %s", self._path)
