"""Unit tests for the StorageFactory."""

import pytest

from praxis.backend.core.storage import (
    StorageBackend,
    StorageFactory,
)
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


class TestStorageFactory:
    """Tests for StorageFactory methods."""

    def test_create_key_value_store_memory(self) -> None:
        """Test creating an in-memory key-value store."""
        store = StorageFactory.create_key_value_store(StorageBackend.MEMORY)
        assert isinstance(store, InMemoryKeyValueStore)
        assert isinstance(store, KeyValueStore)

    def test_create_key_value_store_sqlite(self) -> None:
        """Test that SQLite backend creates in-memory KV store."""
        store = StorageFactory.create_key_value_store(StorageBackend.SQLITE)
        assert isinstance(store, InMemoryKeyValueStore)

    def test_create_pubsub_memory(self) -> None:
        """Test creating an in-memory pub/sub."""
        pubsub = StorageFactory.create_pubsub(StorageBackend.MEMORY)
        assert isinstance(pubsub, InMemoryPubSub)
        assert isinstance(pubsub, PubSub)

    def test_create_task_queue_memory(self) -> None:
        """Test creating an in-memory task queue."""
        queue = StorageFactory.create_task_queue(StorageBackend.MEMORY)
        assert isinstance(queue, InMemoryTaskQueue)
        assert isinstance(queue, TaskQueue)

    def test_create_task_queue_with_workers(self) -> None:
        """Test creating task queue with custom worker count."""
        queue = StorageFactory.create_task_queue(
            StorageBackend.MEMORY,
            num_workers=8,
        )
        assert isinstance(queue, InMemoryTaskQueue)
        assert queue._num_workers == 8

    def test_create_session_factory_memory(self) -> None:
        """Test creating an in-memory SQLite session factory."""
        session_factory = StorageFactory.create_session_factory(
            StorageBackend.MEMORY,
        )
        # Should return an async_sessionmaker
        assert session_factory is not None

    def test_create_session_factory_postgresql_requires_url(self) -> None:
        """Test that PostgreSQL backend requires database_url."""
        with pytest.raises(ValueError, match="database_url is required"):
            StorageFactory.create_session_factory(StorageBackend.POSTGRESQL)

    def test_create_session_factory_postgresql(self) -> None:
        """Test creating PostgreSQL session factory."""
        session_factory = StorageFactory.create_session_factory(
            StorageBackend.POSTGRESQL,
            database_url="postgresql://user:pass@localhost/db",
        )
        assert session_factory is not None


class TestStorageBackendEnum:
    """Tests for StorageBackend enum."""

    def test_values(self) -> None:
        """Test that all expected backends exist."""
        assert StorageBackend.POSTGRESQL.value == "postgresql"
        assert StorageBackend.REDIS.value == "redis"
        assert StorageBackend.MEMORY.value == "memory"
        assert StorageBackend.SQLITE.value == "sqlite"

    def test_string_enum(self) -> None:
        """Test that StorageBackend is a string enum."""
        assert str(StorageBackend.MEMORY) == "StorageBackend.MEMORY"
        assert StorageBackend.MEMORY == "memory"
