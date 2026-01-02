"""In-memory implementations of storage protocols.

These adapters are designed for demo mode and testing. They provide
the same interface as the production Redis/Celery backends but store
everything in memory.

Features:
- InMemoryKeyValueStore: Dict-based storage with TTL support
- InMemoryPubSub: asyncio.Queue-based pub/sub
- InMemoryTaskQueue: asyncio.Queue-based task execution

Limitations:
- All data is lost on restart
- Single process only (no distributed support)
- Task chains and complex Celery features not supported
"""

import asyncio
import contextlib
import fnmatch
import logging
import time
import uuid
from collections.abc import AsyncIterator, Callable
from typing import Any

from praxis.backend.core.storage.protocols import (
  Subscription,
)

logger = logging.getLogger(__name__)


class InMemoryKeyValueStore:
  """In-memory key-value store with TTL support.

  Thread-safe via asyncio.Lock. Uses a background task for TTL expiration.
  """

  def __init__(self) -> None:
    """Initialize the in-memory store."""
    self._data: dict[str, tuple[Any, float | None]] = {}  # value, expiry time
    self._lock = asyncio.Lock()
    self._cleanup_task: asyncio.Task | None = None
    self._closed = False

  async def _start_cleanup_task(self) -> None:
    """Start the background TTL cleanup task."""
    if self._cleanup_task is None or self._cleanup_task.done():
      self._cleanup_task = asyncio.create_task(self._cleanup_expired_keys())

  async def _cleanup_expired_keys(self) -> None:
    """Periodically remove expired keys."""
    while not self._closed:
      try:
        await asyncio.sleep(1.0)  # Check every second
        now = time.time()
        async with self._lock:
          expired = [
            key for key, (_, expiry) in self._data.items() if expiry is not None and expiry <= now
          ]
          for key in expired:
            del self._data[key]
            logger.debug("TTL expired for key: %s", key)
      except asyncio.CancelledError:
        break
      except Exception:
        logger.exception("Error in TTL cleanup task")

  async def get(self, key: str) -> Any | None:
    """Retrieve a value by key."""
    await self._start_cleanup_task()
    async with self._lock:
      if key not in self._data:
        return None
      value, expiry = self._data[key]
      if expiry is not None and expiry <= time.time():
        del self._data[key]
        return None
      return value

  async def set(
    self,
    key: str,
    value: Any,
    ttl_seconds: int | None = None,
  ) -> None:
    """Store a value with optional TTL."""
    await self._start_cleanup_task()
    expiry = time.time() + ttl_seconds if ttl_seconds is not None else None
    async with self._lock:
      self._data[key] = (value, expiry)
    logger.debug("Set key: %s (TTL: %s)", key, ttl_seconds)

  async def delete(self, key: str) -> bool:
    """Delete a key."""
    async with self._lock:
      if key in self._data:
        del self._data[key]
        logger.debug("Deleted key: %s", key)
        return True
      return False

  async def exists(self, key: str) -> bool:
    """Check if a key exists."""
    async with self._lock:
      if key not in self._data:
        return False
      _, expiry = self._data[key]
      if expiry is not None and expiry <= time.time():
        del self._data[key]
        return False
      return True

  async def keys(self, pattern: str = "*") -> list[str]:
    """List keys matching a glob pattern."""
    now = time.time()
    async with self._lock:
      result = []
      for key, (_, expiry) in self._data.items():
        if (expiry is None or expiry > now) and fnmatch.fnmatch(key, pattern):
          result.append(key)
      return result

  async def close(self) -> None:
    """Close the store and stop cleanup task."""
    self._closed = True
    if self._cleanup_task is not None:
      self._cleanup_task.cancel()
      with contextlib.suppress(asyncio.CancelledError):
        await self._cleanup_task
    self._data.clear()
    logger.info("InMemoryKeyValueStore closed")


class InMemorySubscription:
  """A subscription to an in-memory pub/sub channel."""

  def __init__(self, channel: str, queue: asyncio.Queue[Any]) -> None:
    """Initialize the subscription.

    Args:
        channel: The channel name.
        queue: The queue to receive messages from.

    """
    self._channel = channel
    self._queue = queue
    self._closed = False

  def __aiter__(self) -> AsyncIterator[Any]:
    """Return self as async iterator."""
    return self

  async def __anext__(self) -> Any:
    """Get the next message."""
    if self._closed:
      raise StopAsyncIteration
    try:
      message = await self._queue.get()
      if message is StopAsyncIteration:
        raise StopAsyncIteration
      return message
    except asyncio.CancelledError:
      raise StopAsyncIteration from None

  async def unsubscribe(self) -> None:
    """Unsubscribe from the channel."""
    self._closed = True
    # Put sentinel to unblock waiting readers
    with contextlib.suppress(asyncio.QueueFull):
      self._queue.put_nowait(StopAsyncIteration)
    logger.debug("Unsubscribed from channel: %s", self._channel)


class InMemoryPubSub:
  """In-memory pub/sub implementation using asyncio queues."""

  def __init__(self) -> None:
    """Initialize the pub/sub system."""
    self._channels: dict[str, list[asyncio.Queue[Any]]] = {}
    self._lock = asyncio.Lock()
    self._closed = False

  async def publish(self, channel: str, message: Any) -> int:
    """Publish a message to a channel."""
    async with self._lock:
      if channel not in self._channels:
        return 0
      subscribers = self._channels[channel]
      count = 0
      for queue in subscribers:
        try:
          queue.put_nowait(message)
          count += 1
        except asyncio.QueueFull:
          logger.warning("Queue full for channel: %s", channel)
      return count

  def subscribe(self, channel: str) -> Subscription:
    """Subscribe to a channel."""
    queue: asyncio.Queue[Any] = asyncio.Queue(maxsize=100)
    # Synchronously add to channels (will be locked by caller if needed)
    if channel not in self._channels:
      self._channels[channel] = []
    self._channels[channel].append(queue)
    logger.debug("Subscribed to channel: %s", channel)
    return InMemorySubscription(channel, queue)

  async def close(self) -> None:
    """Close all subscriptions."""
    self._closed = True
    async with self._lock:
      for queues in self._channels.values():
        for queue in queues:
          with contextlib.suppress(asyncio.QueueFull):
            queue.put_nowait(StopAsyncIteration)
      self._channels.clear()
    logger.info("InMemoryPubSub closed")


class TaskResult:
  """Wrapper for a task result with status tracking."""

  def __init__(self, task_id: str) -> None:
    """Initialize the task result."""
    self.task_id = task_id
    self.status: str = "PENDING"
    self.result: Any = None
    self.exception: BaseException | None = None
    self._event = asyncio.Event()

  def set_success(self, result: Any) -> None:
    """Mark the task as successful."""
    self.status = "SUCCESS"
    self.result = result
    self._event.set()

  def set_failure(self, exc: BaseException) -> None:
    """Mark the task as failed."""
    self.status = "FAILURE"
    self.exception = exc
    self._event.set()

  async def wait(self, timeout: float | None = None) -> None:
    """Wait for the task to complete."""
    await asyncio.wait_for(self._event.wait(), timeout=timeout)


class InMemoryTaskQueue:
  """In-memory task queue using asyncio.

  Tasks are executed in the order they are received by a pool of worker
  coroutines.
  """

  def __init__(self, num_workers: int = 4) -> None:
    """Initialize the task queue.

    Args:
        num_workers: Number of concurrent worker tasks.

    """
    self._queue: asyncio.Queue[tuple[str, str, list, dict]] = asyncio.Queue()
    self._results: dict[str, TaskResult] = {}
    self._tasks: dict[str, Callable[..., Any]] = {}
    self._workers: list[asyncio.Task] = []
    self._num_workers = num_workers
    self._closed = False
    self._started = False

  def register_task(self, name: str, func: Callable[..., Any]) -> None:
    """Register a task function.

    Args:
        name: The task name.
        func: The callable to execute.

    """
    self._tasks[name] = func
    logger.debug("Registered task: %s", name)

  async def _start_workers(self) -> None:
    """Start worker coroutines if not already running."""
    if self._started:
      return
    self._started = True
    for i in range(self._num_workers):
      worker = asyncio.create_task(self._worker(i))
      self._workers.append(worker)
    logger.info("Started %d task queue workers", self._num_workers)

  async def _worker(self, worker_id: int) -> None:
    """Worker coroutine that processes tasks from the queue."""
    while not self._closed:
      try:
        task_id, name, args, kwargs = await asyncio.wait_for(
          self._queue.get(),
          timeout=1.0,
        )
      except asyncio.TimeoutError:
        continue
      except asyncio.CancelledError:
        break

      result = self._results.get(task_id)
      if result is None:
        continue

      logger.debug("Worker %d executing task: %s (%s)", worker_id, name, task_id)
      result.status = "STARTED"

      try:
        func = self._tasks.get(name)
        if func is None:
          msg = f"Unknown task: {name}"
          raise ValueError(msg)

        # Execute the task
        if asyncio.iscoroutinefunction(func):
          task_result = await func(*args, **kwargs)
        else:
          task_result = func(*args, **kwargs)

        result.set_success(task_result)
        logger.debug("Task completed: %s", task_id)
      except Exception as e:
        result.set_failure(e)
        logger.exception("Task failed: %s", task_id)

  async def send_task(
    self,
    name: str,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
  ) -> str:
    """Dispatch a task for async execution."""
    await self._start_workers()

    if name not in self._tasks:
      msg = f"Unknown task: {name}. Did you forget to register it?"
      raise ValueError(msg)

    task_id = str(uuid.uuid4())
    result = TaskResult(task_id)
    self._results[task_id] = result

    await self._queue.put(
      (
        task_id,
        name,
        args or [],
        kwargs or {},
      )
    )
    logger.debug("Queued task: %s (%s)", name, task_id)
    return task_id

  async def get_result(
    self,
    task_id: str,
    timeout: float | None = None,
  ) -> Any:
    """Wait for and retrieve a task result."""
    result = self._results.get(task_id)
    if result is None:
      msg = f"Unknown task ID: {task_id}"
      raise ValueError(msg)

    await result.wait(timeout=timeout)

    if result.exception is not None:
      raise result.exception

    return result.result

  async def revoke(self, task_id: str) -> None:
    """Cancel a pending task.

    Note: Cannot cancel tasks already being executed.
    """
    result = self._results.get(task_id)
    if result is not None and result.status == "PENDING":
      result.set_failure(asyncio.CancelledError("Task revoked"))
      logger.info("Revoked task: %s", task_id)

  async def close(self) -> None:
    """Shut down the task queue."""
    self._closed = True
    for worker in self._workers:
      worker.cancel()
    await asyncio.gather(*self._workers, return_exceptions=True)
    self._workers.clear()
    self._results.clear()
    logger.info("InMemoryTaskQueue closed")
