"""Storage abstraction layer for PyLabPraxis.

This module provides protocol definitions and implementations for abstracting
storage dependencies, allowing the application to run with different backends:
- Production: PostgreSQL + Redis + Celery
- Demo/Test: SQLite + In-Memory adapters

Usage:
    from praxis.backend.core.storage import StorageFactory, StorageBackend

    kv_store = StorageFactory.create_key_value_store(StorageBackend.MEMORY)
    pubsub = StorageFactory.create_pubsub(StorageBackend.MEMORY)
    task_queue = StorageFactory.create_task_queue(StorageBackend.MEMORY)
"""

from praxis.backend.core.storage.factory import (
    StorageBackend,
    StorageFactory,
)
from praxis.backend.core.storage.protocols import (
    KeyValueStore,
    PubSub,
    Subscription,
    TaskQueue,
)

__all__ = [
    "KeyValueStore",
    "PubSub",
    "StorageBackend",
    "StorageFactory",
    "Subscription",
    "TaskQueue",
]

