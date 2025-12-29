"""Unit tests for in-memory storage adapters."""

import asyncio

import pytest

from praxis.backend.core.storage.memory_adapter import (
    InMemoryKeyValueStore,
    InMemoryPubSub,
    InMemoryTaskQueue,
)
from praxis.backend.core.storage.protocols import (
    KeyValueStore,
    PubSub,
    TaskQueue,
)


class TestInMemoryKeyValueStore:
    """Tests for InMemoryKeyValueStore."""

    @pytest.fixture
    def store(self) -> InMemoryKeyValueStore:
        """Create a fresh store for each test."""
        return InMemoryKeyValueStore()

    @pytest.mark.asyncio
    async def test_implements_protocol(self, store: InMemoryKeyValueStore) -> None:
        """Verify the store implements KeyValueStore protocol."""
        assert isinstance(store, KeyValueStore)

    @pytest.mark.asyncio
    async def test_set_and_get(self, store: InMemoryKeyValueStore) -> None:
        """Test basic set and get operations."""
        await store.set("key1", {"data": "value"})
        result = await store.get("key1")
        assert result == {"data": "value"}

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, store: InMemoryKeyValueStore) -> None:
        """Test getting a key that doesn't exist."""
        result = await store.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self, store: InMemoryKeyValueStore) -> None:
        """Test deleting a key."""
        await store.set("key1", "value")
        deleted = await store.delete("key1")
        assert deleted is True
        assert await store.get("key1") is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, store: InMemoryKeyValueStore) -> None:
        """Test deleting a key that doesn't exist."""
        deleted = await store.delete("nonexistent")
        assert deleted is False

    @pytest.mark.asyncio
    async def test_exists(self, store: InMemoryKeyValueStore) -> None:
        """Test checking if a key exists."""
        await store.set("key1", "value")
        assert await store.exists("key1") is True
        assert await store.exists("nonexistent") is False

    @pytest.mark.asyncio
    async def test_keys_pattern(self, store: InMemoryKeyValueStore) -> None:
        """Test listing keys with pattern matching."""
        await store.set("user:1", "alice")
        await store.set("user:2", "bob")
        await store.set("other", "data")

        user_keys = await store.keys("user:*")
        assert set(user_keys) == {"user:1", "user:2"}

        all_keys = await store.keys("*")
        assert set(all_keys) == {"user:1", "user:2", "other"}

    @pytest.mark.asyncio
    async def test_ttl_expiration(self, store: InMemoryKeyValueStore) -> None:
        """Test that keys with TTL expire."""
        await store.set("key1", "value", ttl_seconds=1)
        assert await store.get("key1") == "value"

        await asyncio.sleep(1.5)

        # Key should be expired
        assert await store.get("key1") is None

    @pytest.mark.asyncio
    async def test_close(self, store: InMemoryKeyValueStore) -> None:
        """Test closing the store."""
        await store.set("key1", "value")
        await store.close()
        # After close, data should be cleared
        # (store is not meant to be used after close)


class TestInMemoryPubSub:
    """Tests for InMemoryPubSub."""

    @pytest.fixture
    def pubsub(self) -> InMemoryPubSub:
        """Create a fresh pubsub for each test."""
        return InMemoryPubSub()

    @pytest.mark.asyncio
    async def test_implements_protocol(self, pubsub: InMemoryPubSub) -> None:
        """Verify the pubsub implements PubSub protocol."""
        assert isinstance(pubsub, PubSub)

    @pytest.mark.asyncio
    async def test_publish_no_subscribers(self, pubsub: InMemoryPubSub) -> None:
        """Test publishing when there are no subscribers."""
        count = await pubsub.publish("channel", {"event": "test"})
        assert count == 0

    @pytest.mark.asyncio
    async def test_subscribe_and_receive(self, pubsub: InMemoryPubSub) -> None:
        """Test subscribing and receiving messages."""
        subscription = pubsub.subscribe("events")

        # Publish a message
        await pubsub.publish("events", {"type": "test"})

        # Receive the message
        message = await asyncio.wait_for(subscription.__anext__(), timeout=1.0)
        assert message == {"type": "test"}

    @pytest.mark.asyncio
    async def test_multiple_subscribers(self, pubsub: InMemoryPubSub) -> None:
        """Test that multiple subscribers receive the same message."""
        sub1 = pubsub.subscribe("events")
        sub2 = pubsub.subscribe("events")

        await pubsub.publish("events", "hello")

        msg1 = await asyncio.wait_for(sub1.__anext__(), timeout=1.0)
        msg2 = await asyncio.wait_for(sub2.__anext__(), timeout=1.0)

        assert msg1 == "hello"
        assert msg2 == "hello"

    @pytest.mark.asyncio
    async def test_unsubscribe(self, pubsub: InMemoryPubSub) -> None:
        """Test unsubscribing from a channel."""
        subscription = pubsub.subscribe("events")
        await subscription.unsubscribe()

        # After unsubscribe, iteration should stop
        with pytest.raises(StopAsyncIteration):
            await asyncio.wait_for(subscription.__anext__(), timeout=0.5)


class TestInMemoryTaskQueue:
    """Tests for InMemoryTaskQueue."""

    @pytest.fixture
    def queue(self) -> InMemoryTaskQueue:
        """Create a fresh queue for each test."""
        return InMemoryTaskQueue(num_workers=2)

    @pytest.mark.asyncio
    async def test_implements_protocol(self, queue: InMemoryTaskQueue) -> None:
        """Verify the queue implements TaskQueue protocol."""
        assert isinstance(queue, TaskQueue)

    @pytest.mark.asyncio
    async def test_register_and_execute_task(self, queue: InMemoryTaskQueue) -> None:
        """Test registering and executing a task."""

        def add(a: int, b: int) -> int:
            return a + b

        queue.register_task("add", add)
        task_id = await queue.send_task("add", args=[2, 3])

        result = await queue.get_result(task_id, timeout=5.0)
        assert result == 5

    @pytest.mark.asyncio
    async def test_async_task(self, queue: InMemoryTaskQueue) -> None:
        """Test executing an async task."""

        async def async_multiply(a: int, b: int) -> int:
            await asyncio.sleep(0.1)
            return a * b

        queue.register_task("multiply", async_multiply)
        task_id = await queue.send_task("multiply", args=[4, 5])

        result = await queue.get_result(task_id, timeout=5.0)
        assert result == 20

    @pytest.mark.asyncio
    async def test_task_with_kwargs(self, queue: InMemoryTaskQueue) -> None:
        """Test task execution with keyword arguments."""

        def greet(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        queue.register_task("greet", greet)
        task_id = await queue.send_task(
            "greet",
            args=["World"],
            kwargs={"greeting": "Hi"},
        )

        result = await queue.get_result(task_id, timeout=5.0)
        assert result == "Hi, World!"

    @pytest.mark.asyncio
    async def test_unknown_task_raises(self, queue: InMemoryTaskQueue) -> None:
        """Test that sending an unknown task raises ValueError."""
        with pytest.raises(ValueError, match="Unknown task"):
            await queue.send_task("nonexistent")

    @pytest.mark.asyncio
    async def test_task_exception(self, queue: InMemoryTaskQueue) -> None:
        """Test that task exceptions are properly raised."""

        def failing_task() -> None:
            msg = "Task failed!"
            raise RuntimeError(msg)

        queue.register_task("fail", failing_task)
        task_id = await queue.send_task("fail")

        with pytest.raises(RuntimeError, match="Task failed"):
            await queue.get_result(task_id, timeout=5.0)

    @pytest.mark.asyncio
    async def test_close(self, queue: InMemoryTaskQueue) -> None:
        """Test closing the queue."""
        queue.register_task("noop", lambda: None)
        await queue.send_task("noop")
        await asyncio.sleep(0.1)  # Let task start
        await queue.close()
