"""Redis implementations of storage protocols.

These adapters wrap the existing Redis client to conform to the storage
protocols, enabling interchangeable usage with in-memory adapters.

Uses redis.asyncio for async operations.
"""

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from praxis.backend.core.storage.protocols import (
  Subscription,
)

logger = logging.getLogger(__name__)


class RedisKeyValueStore:
  """Redis-backed key-value store.

  Wraps redis.asyncio.Redis to conform to the KeyValueStore protocol.
  """

  def __init__(
    self,
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: str | None = None,
  ) -> None:
    """Initialize the Redis connection.

    Args:
        host: Redis host.
        port: Redis port.
        db: Redis database number.
        password: Redis password (optional).

    """
    self._host = host
    self._port = port
    self._db = db
    self._password = password
    self._client: Any = None  # redis.asyncio.Redis

  async def _get_client(self) -> Any:
    """Get or create the Redis client."""
    if self._client is None:
      try:
        import redis.asyncio as aioredis
      except ImportError:
        msg = "redis package not installed. Install with: pip install redis"
        raise ImportError(msg) from None

      self._client = aioredis.Redis(
        host=self._host,
        port=self._port,
        db=self._db,
        password=self._password,
        decode_responses=False,
      )
      logger.info(
        "Connected to Redis at %s:%s/%s",
        self._host,
        self._port,
        self._db,
      )
    return self._client

  async def get(self, key: str) -> Any | None:
    """Retrieve a value by key."""
    client = await self._get_client()
    data = await client.get(key)
    if data is None:
      return None
    try:
      return json.loads(data)
    except json.JSONDecodeError:
      # Return raw bytes/string if not JSON
      return data.decode() if isinstance(data, bytes) else data

  async def set(
    self,
    key: str,
    value: Any,
    ttl_seconds: int | None = None,
  ) -> None:
    """Store a value with optional TTL."""
    client = await self._get_client()
    serialized = json.dumps(value)
    if ttl_seconds is not None:
      await client.setex(key, ttl_seconds, serialized)
    else:
      await client.set(key, serialized)

  async def delete(self, key: str) -> bool:
    """Delete a key."""
    client = await self._get_client()
    result = await client.delete(key)
    return result > 0

  async def exists(self, key: str) -> bool:
    """Check if a key exists."""
    client = await self._get_client()
    return await client.exists(key) > 0

  async def keys(self, pattern: str = "*") -> list[str]:
    """List keys matching a pattern."""
    client = await self._get_client()
    # Redis KEYS command returns bytes
    raw_keys = await client.keys(pattern)
    return [k.decode() if isinstance(k, bytes) else k for k in raw_keys]

  async def close(self) -> None:
    """Close the Redis connection."""
    if self._client is not None:
      await self._client.aclose()
      self._client = None
      logger.info("Redis connection closed")


class RedisSubscription:
  """A subscription to a Redis pub/sub channel."""

  def __init__(self, pubsub: Any, channel: str) -> None:
    """Initialize the subscription.

    Args:
        pubsub: The redis.asyncio.PubSub instance.
        channel: The channel name.

    """
    self._pubsub = pubsub
    self._channel = channel
    self._closed = False

  def __aiter__(self) -> AsyncIterator[Any]:
    """Return self as async iterator."""
    return self

  async def __anext__(self) -> Any:
    """Get the next message."""
    if self._closed:
      raise StopAsyncIteration

    try:
      while True:
        message = await self._pubsub.get_message(
          ignore_subscribe_messages=True,
          timeout=1.0,
        )
        if message is not None:
          data = message.get("data")
          if data is not None:
            try:
              return json.loads(data)
            except (json.JSONDecodeError, TypeError):
              return data.decode() if isinstance(data, bytes) else data
        if self._closed:
          raise StopAsyncIteration
    except asyncio.CancelledError:
      raise StopAsyncIteration from None

  async def unsubscribe(self) -> None:
    """Unsubscribe from the channel."""
    self._closed = True
    await self._pubsub.unsubscribe(self._channel)
    logger.debug("Unsubscribed from Redis channel: %s", self._channel)


class RedisPubSub:
  """Redis-backed pub/sub implementation."""

  def __init__(
    self,
    host: str = "localhost",
    port: int = 6379,
    db: int = 0,
    password: str | None = None,
  ) -> None:
    """Initialize the Redis pub/sub connection.

    Args:
        host: Redis host.
        port: Redis port.
        db: Redis database number.
        password: Redis password (optional).

    """
    self._host = host
    self._port = port
    self._db = db
    self._password = password
    self._client: Any = None
    self._subscriptions: list[RedisSubscription] = []

  async def _get_client(self) -> Any:
    """Get or create the Redis client."""
    if self._client is None:
      try:
        import redis.asyncio as aioredis
      except ImportError:
        msg = "redis package not installed. Install with: pip install redis"
        raise ImportError(msg) from None

      self._client = aioredis.Redis(
        host=self._host,
        port=self._port,
        db=self._db,
        password=self._password,
      )
    return self._client

  async def publish(self, channel: str, message: Any) -> int:
    """Publish a message to a channel."""
    client = await self._get_client()
    serialized = json.dumps(message)
    return await client.publish(channel, serialized)

  def subscribe(self, channel: str) -> Subscription:
    """Subscribe to a channel.

    Note: This creates a new pubsub connection for each subscription
    to avoid blocking issues.
    """
    # Create synchronously but the actual subscription happens on first iteration
    # We need to wrap this properly for async
    return _DeferredRedisSubscription(
      host=self._host,
      port=self._port,
      db=self._db,
      password=self._password,
      channel=channel,
    )

  async def close(self) -> None:
    """Close all connections."""
    for sub in self._subscriptions:
      await sub.unsubscribe()
    self._subscriptions.clear()
    if self._client is not None:
      await self._client.aclose()
      self._client = None
    logger.info("Redis pub/sub closed")


class _DeferredRedisSubscription:
  """A subscription that defers connection until first iteration."""

  def __init__(
    self,
    host: str,
    port: int,
    db: int,
    password: str | None,
    channel: str,
  ) -> None:
    """Initialize the deferred subscription."""
    self._host = host
    self._port = port
    self._db = db
    self._password = password
    self._channel = channel
    self._client: Any = None
    self._pubsub: Any = None
    self._closed = False

  async def _ensure_subscribed(self) -> None:
    """Create the connection and subscribe."""
    if self._client is None:
      try:
        import redis.asyncio as aioredis
      except ImportError:
        msg = "redis package not installed"
        raise ImportError(msg) from None

      self._client = aioredis.Redis(
        host=self._host,
        port=self._port,
        db=self._db,
        password=self._password,
      )
      self._pubsub = self._client.pubsub()
      await self._pubsub.subscribe(self._channel)
      logger.debug("Subscribed to Redis channel: %s", self._channel)

  def __aiter__(self) -> AsyncIterator[Any]:
    """Return self as async iterator."""
    return self

  async def __anext__(self) -> Any:
    """Get the next message."""
    if self._closed:
      raise StopAsyncIteration

    await self._ensure_subscribed()

    try:
      while True:
        message = await self._pubsub.get_message(
          ignore_subscribe_messages=True,
          timeout=1.0,
        )
        if message is not None:
          data = message.get("data")
          if data is not None:
            try:
              return json.loads(data)
            except (json.JSONDecodeError, TypeError):
              return data.decode() if isinstance(data, bytes) else data
        if self._closed:
          raise StopAsyncIteration
    except asyncio.CancelledError:
      raise StopAsyncIteration from None

  async def unsubscribe(self) -> None:
    """Unsubscribe and close the connection."""
    self._closed = True
    if self._pubsub is not None:
      await self._pubsub.unsubscribe(self._channel)
    if self._client is not None:
      await self._client.aclose()
    logger.debug("Unsubscribed from Redis channel: %s", self._channel)
