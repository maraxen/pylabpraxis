"""Protocol definitions for pluggable storage backends.

This module defines the abstract interfaces (Protocols) for storage components
that can have multiple implementations:

- KeyValueStore: Redis replacement for caching and state storage
- PubSub/Subscription: Redis pub/sub replacement for event broadcasting
- TaskQueue: Celery replacement for async task execution

Each protocol uses @runtime_checkable to allow isinstance() checks.
"""

from collections.abc import AsyncIterator
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class KeyValueStore(Protocol):
  """Abstract key-value storage interface.

  Provides Redis-like operations for storing and retrieving data.
  Implementations must handle JSON-serializable values.

  Example:
      store = InMemoryKeyValueStore()
      await store.set("user:123", {"name": "Alice"}, ttl_seconds=3600)
      user = await store.get("user:123")

  """

  async def get(self, key: str) -> Any | None:
    """Retrieve a value by key.

    Args:
        key: The key to look up.

    Returns:
        The stored value, or None if the key doesn't exist or has expired.

    """
    ...

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
        ttl_seconds: Optional time-to-live in seconds. If None, the key persists
            until explicitly deleted.

    """
    ...

  async def delete(self, key: str) -> bool:
    """Delete a key.

    Args:
        key: The key to delete.

    Returns:
        True if the key was deleted, False if it didn't exist.

    """
    ...

  async def exists(self, key: str) -> bool:
    """Check if a key exists.

    Args:
        key: The key to check.

    Returns:
        True if the key exists and hasn't expired.

    """
    ...

  async def keys(self, pattern: str = "*") -> list[str]:
    """List keys matching a pattern.

    Args:
        pattern: Glob-style pattern (e.g., "user:*"). Default "*" matches all.

    Returns:
        List of matching keys.

    """
    ...

  async def close(self) -> None:
    """Close the connection and release resources.

    Should be called during application shutdown.
    """
    ...


@runtime_checkable
class Subscription(Protocol):
  """A pub/sub subscription that can be async-iterated.

  Represents an active subscription to a channel. Messages are received
  by iterating over the subscription.

  Example:
      subscription = pubsub.subscribe("events")
      async for message in subscription:
          print(f"Received: {message}")

  """

  def __aiter__(self) -> AsyncIterator[Any]:
    """Return self as an async iterator."""
    ...

  async def __anext__(self) -> Any:
    """Get the next message from the subscription.

    Returns:
        The next message received on the subscribed channel.

    Raises:
        StopAsyncIteration: When the subscription is closed.

    """
    ...

  async def unsubscribe(self) -> None:
    """Unsubscribe from the channel and stop receiving messages.

    After calling this, iteration will raise StopAsyncIteration.
    """
    ...


@runtime_checkable
class PubSub(Protocol):
  """Abstract pub/sub interface for event broadcasting.

  Provides Redis-like publish/subscribe operations for real-time
  message passing between components.

  Example:
      pubsub = InMemoryPubSub()
      subscription = pubsub.subscribe("protocol:run:123")

      # In another task
      await pubsub.publish("protocol:run:123", {"status": "completed"})

  """

  async def publish(self, channel: str, message: Any) -> int:
    """Publish a message to a channel.

    Args:
        channel: The channel name to publish to.
        message: The message to send (must be JSON-serializable).

    Returns:
        The number of subscribers that received the message.

    """
    ...

  def subscribe(self, channel: str) -> Subscription:
    """Subscribe to a channel.

    Args:
        channel: The channel name to subscribe to.

    Returns:
        A Subscription object that can be async-iterated to receive messages.

    """
    ...

  async def close(self) -> None:
    """Close all subscriptions and release resources.

    Should be called during application shutdown.
    """
    ...


@runtime_checkable
class TaskQueue(Protocol):
  """Abstract task queue interface for async job execution.

  Provides Celery-like operations for dispatching and tracking
  background tasks.

  Example:
      queue = InMemoryTaskQueue()
      task_id = await queue.send_task(
          "execute_protocol",
          args=[run_id],
          kwargs={"simulation_mode": True}
      )
      result = await queue.get_result(task_id, timeout=300.0)

  """

  async def send_task(
    self,
    name: str,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
  ) -> str:
    """Dispatch a task for async execution.

    Args:
        name: The registered task name.
        args: Positional arguments to pass to the task.
        kwargs: Keyword arguments to pass to the task.

    Returns:
        A unique task ID for tracking the task.

    Raises:
        ValueError: If the task name is not registered.

    """
    ...

  async def get_result(
    self,
    task_id: str,
    timeout: float | None = None,
  ) -> Any:
    """Wait for and retrieve a task result.

    Args:
        task_id: The task ID returned by send_task.
        timeout: Maximum seconds to wait. None means wait indefinitely.

    Returns:
        The task's return value.

    Raises:
        TimeoutError: If timeout is reached before task completes.
        Exception: If the task raised an exception during execution.

    """
    ...

  async def revoke(self, task_id: str) -> None:
    """Cancel a pending or running task.

    Args:
        task_id: The task ID to cancel.

    Note:
        Cancellation is best-effort. Tasks already executing may not
        be interrupted immediately.

    """
    ...

  async def close(self) -> None:
    """Shut down the task queue and release resources.

    Should be called during application shutdown. May wait for
    running tasks to complete.
    """
    ...
