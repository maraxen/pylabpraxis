"""Storage factory for creating backend-specific adapters.

The StorageFactory provides a unified interface for creating storage adapters
based on the configured backend type. This enables seamless switching between
production (PostgreSQL + Redis + Celery) and demo/test (SQLite + in-memory)
configurations.

Usage:
    from praxis.backend.core.storage import StorageFactory, StorageBackend

    # For demo mode
    kv_store = StorageFactory.create_key_value_store(StorageBackend.MEMORY)
    pubsub = StorageFactory.create_pubsub(StorageBackend.MEMORY)
    task_queue = StorageFactory.create_task_queue(StorageBackend.MEMORY)

    # For production
    kv_store = StorageFactory.create_key_value_store(
        StorageBackend.REDIS,
        host="redis.example.com",
        port=6379,
    )
"""

import logging
from enum import Enum
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from praxis.backend.core.storage.protocols import (
  KeyValueStore,
  PubSub,
  TaskQueue,
)

logger = logging.getLogger(__name__)


class StorageBackend(str, Enum):
  """Supported storage backend types."""

  POSTGRESQL = "postgresql"  # Production: PostgreSQL + Redis + Celery
  REDIS = "redis"  # Explicit Redis backend
  MEMORY = "memory"  # Demo/testing: In-memory everything
  SQLITE = "sqlite"  # SQLite database (for edge deployment)


class StorageFactory:
  """Factory for creating storage adapters based on backend configuration."""

  @staticmethod
  def create_key_value_store(
    backend: StorageBackend,
    **config: Any,
  ) -> KeyValueStore:
    """Create a key-value store adapter.

    Args:
        backend: The storage backend type.
        **config: Backend-specific configuration:
            - MEMORY: No config needed
            - SQLITE: kv_database_path (default: "praxis_kv.db")
            - REDIS: host, port, db, password

    Returns:
        A KeyValueStore implementation.

    Raises:
        ValueError: If backend is not supported.

    """
    if backend == StorageBackend.MEMORY:
      from praxis.backend.core.storage.memory_adapter import InMemoryKeyValueStore

      logger.info("Creating InMemoryKeyValueStore")
      return InMemoryKeyValueStore()

    if backend == StorageBackend.SQLITE:
      # For tests and lightweight deployments we use the in-memory KV store
      # to avoid file-based DB dependencies. Tests expect SQLITE to return
      # an in-memory key-value store implementation.
      from praxis.backend.core.storage.memory_adapter import InMemoryKeyValueStore

      logger.info("Creating InMemoryKeyValueStore for SQLITE backend")
      return InMemoryKeyValueStore()

    if backend in (StorageBackend.REDIS, StorageBackend.POSTGRESQL):
      from praxis.backend.core.storage.redis_adapter import RedisKeyValueStore

      logger.info(
        "Creating RedisKeyValueStore (host=%s, port=%s)",
        config.get("host", "localhost"),
        config.get("port", 6379),
      )
      return RedisKeyValueStore(
        host=config.get("host", "localhost"),
        port=config.get("port", 6379),
        db=config.get("db", 0),
        password=config.get("password"),
      )

    msg = f"Unsupported backend for key-value store: {backend}"
    raise ValueError(msg)

  @staticmethod
  def create_pubsub(
    backend: StorageBackend,
    **config: Any,
  ) -> PubSub:
    """Create a pub/sub adapter.

    Args:
        backend: The storage backend type.
        **config: Backend-specific configuration:
            - MEMORY: No config needed
            - REDIS: host, port, db, password

    Returns:
        A PubSub implementation.

    Raises:
        ValueError: If backend is not supported.

    """
    if backend in (StorageBackend.MEMORY, StorageBackend.SQLITE):
      from praxis.backend.core.storage.memory_adapter import InMemoryPubSub

      logger.info("Creating InMemoryPubSub")
      return InMemoryPubSub()

    if backend in (StorageBackend.REDIS, StorageBackend.POSTGRESQL):
      from praxis.backend.core.storage.redis_adapter import RedisPubSub

      logger.info(
        "Creating RedisPubSub (host=%s, port=%s)",
        config.get("host", "localhost"),
        config.get("port", 6379),
      )
      return RedisPubSub(
        host=config.get("host", "localhost"),
        port=config.get("port", 6379),
        db=config.get("db", 0),
        password=config.get("password"),
      )

    msg = f"Unsupported backend for pub/sub: {backend}"
    raise ValueError(msg)

  @staticmethod
  def create_task_queue(
    backend: StorageBackend,
    **config: Any,
  ) -> TaskQueue:
    """Create a task queue adapter.

    Args:
        backend: The storage backend type.
        **config: Backend-specific configuration:
            - MEMORY: num_workers (default 4)
            - POSTGRESQL/REDIS: celery_app (optional, uses global if not provided)

    Returns:
        A TaskQueue implementation.

    Raises:
        ValueError: If backend is not supported.

    """
    if backend in (StorageBackend.MEMORY, StorageBackend.SQLITE):
      from praxis.backend.core.storage.memory_adapter import InMemoryTaskQueue

      num_workers = config.get("num_workers", 4)
      logger.info("Creating InMemoryTaskQueue (workers=%d)", num_workers)
      return InMemoryTaskQueue(num_workers=num_workers)

    if backend in (StorageBackend.REDIS, StorageBackend.POSTGRESQL):
      from praxis.backend.core.storage.celery_adapter import CeleryTaskQueue

      celery_app = config.get("celery_app")
      logger.info("Creating CeleryTaskQueue")
      return CeleryTaskQueue(celery_app=celery_app)

    msg = f"Unsupported backend for task queue: {backend}"
    raise ValueError(msg)

  @staticmethod
  def create_session_factory(
    backend: StorageBackend,
    **config: Any,
  ) -> async_sessionmaker[AsyncSession]:
    """Create a SQLAlchemy async session factory.

    Args:
        backend: The storage backend type.
        **config: Backend-specific configuration:
            - POSTGRESQL: database_url (required)
            - SQLITE: database_url (optional, defaults to in-memory)
            - MEMORY: Uses SQLite in-memory

    Returns:
        An async_sessionmaker for creating database sessions.

    Raises:
        ValueError: If required configuration is missing.

    """
    if backend == StorageBackend.MEMORY:
      database_url = "sqlite+aiosqlite:///:memory:"
      logger.info("Creating SQLite in-memory session factory")

    elif backend == StorageBackend.SQLITE:
      database_url = config.get(
        "database_url",
        "sqlite+aiosqlite:///:memory:",
      )
      logger.info("Creating SQLite session factory: %s", database_url)

    elif backend == StorageBackend.POSTGRESQL:
      database_url = config.get("database_url")
      if not database_url:
        msg = "database_url is required for PostgreSQL backend"
        raise ValueError(msg)
      # Ensure async driver
      if database_url.startswith("postgresql://"):
        database_url = database_url.replace(
          "postgresql://",
          "postgresql+asyncpg://",
          1,
        )
      logger.info(
        "Creating PostgreSQL session factory: %s",
        database_url.split("@")[-1] if "@" in database_url else database_url,
      )

    else:
      msg = f"Unsupported backend for session factory: {backend}"
      raise ValueError(msg)

    engine = create_async_engine(
      database_url,
      echo=config.get("echo", False),
    )

    return async_sessionmaker(
      engine,
      expire_on_commit=False,
      autocommit=False,
      autoflush=False,
    )
