# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Manage Praxis-related database interactions.

praxis/db_services/praxis_orm_service.py

Service layer for interacting with praxis-related data in the database.
This includes Protocol Runs, Protocol Definitions, Users (from Keycloak),
and Assets.

"""

import asyncio
import logging
import os
from collections.abc import AsyncIterator
from configparser import ConfigParser
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Optional

import asyncpg  # For Keycloak database
from sqlalchemy.ext.asyncio import (
  AsyncSession,
)

from praxis.backend.utils.db import (
  AsyncSessionLocal,
)  # This should be an async_sessionmaker

logger = logging.getLogger(__name__)


class PraxisDBService:
  """Provides a singleton service for Praxis database interactions.

  This class manages connections to the main Praxis database via SQLAlchemy
  and optionally to a Keycloak database via asyncpg. It ensures consistent
  database access patterns and resource management.

  """

  _instance: Optional["PraxisDBService"] = None
  _keycloak_pool: asyncpg.Pool[Any] | None = None
  _max_retries = 3
  _retry_delay = 1  # seconds

  def __new__(cls, *args, **kwargs):  # type: ignore
    """Implement the singleton pattern for PraxisDBService."""
    if cls._instance is None:
      cls._instance = super().__new__(cls)
    return cls._instance

  @classmethod
  async def initialize(
    cls,
    keycloak_dsn: str | None = None,
    min_kc_pool_size: int = 5,
    max_kc_pool_size: int = 10,
  ):
    """Initialize the PraxisDBService, including Keycloak database connection.

    This method sets up the singleton instance and, if a `keycloak_dsn` is
    provided, initializes an `asyncpg` connection pool to the Keycloak
    database. It includes retry logic for Keycloak connection attempts.

    Args:
        keycloak_dsn (Optional[str], optional): The DSN (Data Source Name)
            for the Keycloak PostgreSQL database. If None, the Keycloak
            pool will not be initialized. Defaults to None.
        min_kc_pool_size (int, optional): The minimum number of connections
            in the Keycloak pool. Defaults to 5.
        max_kc_pool_size (int, optional): The maximum number of connections
            in the Keycloak pool. Defaults to 10.

    Returns:
        PraxisDBService: The initialized singleton instance of the service.

    Raises:
        ValueError: If `keycloak_dsn` is provided but is not a valid
            PostgreSQL DSN.
        ConnectionError: If connection to the Keycloak database fails after
            multiple retries.
        Exception: For any other unexpected errors during initialization.

    """
    logger.info("Initializing PraxisDBService.")
    if not cls._instance:
      cls._instance = cls()

    if keycloak_dsn:
      if not keycloak_dsn.startswith(("postgresql://", "postgres://")):
        error_message = (
          "Invalid keycloak_dsn: must start with postgresql:// or postgres://."
        )
        logger.error(error_message)
        raise ValueError(error_message)

      retries = 0
      current_retry_delay = cls._retry_delay
      last_error = None

      while retries < cls._max_retries:
        try:
          if not cls._keycloak_pool or cls._keycloak_pool._closed:
            logger.info(
              "Attempting to connect to Keycloak database: %s",
              keycloak_dsn.split("@")[-1],
            )
            cls._keycloak_pool = await asyncpg.create_pool(
              dsn=keycloak_dsn,
              min_size=min_kc_pool_size,
              max_size=max_kc_pool_size,
              command_timeout=60,
              timeout=10.0,
            )
            assert (
              cls._keycloak_pool is not None
            ), "Failed to create Keycloak database pool"
            async with cls._keycloak_pool.acquire() as conn:  # type: ignore
              await conn.execute("SELECT 1")  # type: ignore
            logger.info("Successfully connected to Keycloak database.")
            break
        except (ConnectionRefusedError, asyncpg.PostgresError, OSError) as e:
          last_error = e
          retries += 1
          logger.warning(
            "Keycloak database connection attempt %d failed: %s",
            retries,
            str(e),
          )
          if retries < cls._max_retries:
            logger.info(
              "Retrying Keycloak connection in %d seconds...",
              current_retry_delay,
            )
            await asyncio.sleep(current_retry_delay)
            current_retry_delay *= 2
          else:
            logger.exception(
              "Failed to connect to Keycloak database after %d attempts.",
              cls._max_retries,
            )
            msg = f"Could not establish Keycloak database connection: {last_error}"
            raise ConnectionError(
              msg,
            ) from last_error
        except Exception:
          logger.exception("Unexpected error during Keycloak database initialization.")
          raise

      if not cls._keycloak_pool and keycloak_dsn:
        msg = f"Failed to initialize Keycloak pool. Last error: {last_error}"
        raise ConnectionError(
          msg,
        )
    else:
      logger.info(
        "Keycloak DSN not provided; Keycloak database pool will not be "
        "initialized by PraxisDBService.",
      )

    logger.info(
      "PraxisDBService initialized. Praxis DB uses SQLAlchemy async engine "
      "from praxis.utils.db.",
    )
    return cls._instance

  @asynccontextmanager
  async def get_praxis_session(self) -> AsyncIterator[AsyncSession]:
    """Provide an asynchronous database session for Praxis DB operations.

    This context manager yields an `AsyncSession` instance. The session
    will be committed upon successful exit from the `async with` block,
    or rolled back if an exception occurs.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session.

    Raises:
        Exception: Any exception raised within the context manager will
            trigger a rollback and be re-raised.

    """
    logger.debug("Acquiring Praxis database session.")
    async with AsyncSessionLocal() as session:
      try:
        yield session
        await session.commit()
        logger.debug("Praxis session committed.")
      except Exception:
        logger.exception("Praxis session encountered an error; rolling back.")
        await session.rollback()
        raise

  @asynccontextmanager
  async def get_keycloak_connection(
    self,
  ) -> AsyncIterator[asyncpg.Connection[Any]]:
    """Provide an asynchronous connection to the Keycloak database.

    This context manager yields an `asyncpg.Connection` instance from the
    Keycloak connection pool. The connection is automatically released
    back to the pool upon exiting the `async with` block.

    Yields:
        asyncpg.Connection[Any]: An asynchronous Keycloak database connection.

    Raises:
        RuntimeError: If the Keycloak database pool has not been initialized.
        ConnectionError: If acquiring a connection from the pool fails.

    """
    logger.debug("Acquiring Keycloak database connection.")
    if self._keycloak_pool is None:
      error_message = (
        "Keycloak database pool not initialized. Call initialize() with "
        "keycloak_dsn first."
      )
      logger.error(error_message)
      raise RuntimeError(error_message)

    conn = None
    try:
      conn = await self._keycloak_pool.acquire()
      if not isinstance(conn, asyncpg.Connection):  # type: ignore
        error_message = "Failed to acquire Keycloak connection from pool."
        logger.error(error_message)
        raise ConnectionError(error_message)
      yield conn  # type: ignore
      logger.debug("Keycloak connection released.")
    finally:
      if conn and self._keycloak_pool:
        await self._keycloak_pool.release(conn)

  async def get_all_users(self) -> dict[str, dict[str, Any]]:
    """Retrieve all active users from the Keycloak database.

    Returns:
        dict[str, dict[str, Any]]: A dictionary where keys are usernames
        and values are dictionaries containing user details (id, username,
        email, first_name, last_name, is_active). Returns an empty
        dictionary if the Keycloak pool is not initialized or no users are
        found.

    """
    logger.info("Attempting to retrieve all active users from Keycloak.")
    if not self._keycloak_pool:
      logger.warning("Keycloak pool not initialized. Cannot fetch users.")
      return {}
    async with self.get_keycloak_connection() as conn:
      records = await conn.fetch(
        """
                SELECT id, username, email, first_name, last_name, enabled
                FROM user_entity
                WHERE enabled = true
                ORDER BY username
            """,
      )
      users_dict = {
        record["username"]: {
          "id": record["id"],
          "username": record["username"],
          "email": record["email"],
          "first_name": record["first_name"],
          "last_name": record["last_name"],
          "is_active": record["enabled"],
        }
        for record in records
      }
      logger.info("Found %d active users from Keycloak.", len(users_dict))
      return users_dict

  async def execute_sql(self, sql_statement: str, params: dict | None = None) -> None:
    """Execute a raw SQL statement on the Praxis database.

    Args:
        sql_statement (str): The SQL statement to execute.
        params (Optional[dict], optional): A dictionary of parameters to
            bind to the SQL statement. Defaults to None.

    """
    logger.info("Executing raw SQL statement.")
    async with self.get_praxis_session() as session:
      from sqlalchemy.sql import text

      await session.execute(text(sql_statement), params)
      logger.debug("Raw SQL statement executed.")

  async def fetch_all_sql(
    self, sql_query: str, params: dict | None = None,
  ) -> list[dict[Any, Any]]:
    """Fetch all rows from a raw SQL query on the Praxis database.

    Args:
        sql_query (str): The SQL query to execute.
        params (Optional[dict], optional): A dictionary of parameters to
            bind to the SQL query. Defaults to None.

    Returns:
        list[dict[Any, Any]]: A list of dictionaries, where each dictionary
        represents a row from the query result.

    """
    logger.info("Fetching all rows from raw SQL query.")
    async with self.get_praxis_session() as session:
      from sqlalchemy.sql import text

      result = await session.execute(text(sql_query), params)
      rows = [dict(row._mapping) for row in result]
      logger.debug("Fetched %d rows.", len(rows))
      return rows

  async def fetch_one_sql(
    self, sql_query: str, params: dict | None = None,
  ) -> dict[Any, Any] | None:
    """Fetch a single row from a raw SQL query on the Praxis database.

    Args:
        sql_query (str): The SQL query to execute.
        params (Optional[dict], optional): A dictionary of parameters to
            bind to the SQL query. Defaults to None.

    Returns:
        Optional[dict[Any, Any]]: A dictionary representing the first row
        from the query result, or None if no rows are found.

    """
    logger.info("Fetching one row from raw SQL query.")
    async with self.get_praxis_session() as session:
      from sqlalchemy.sql import text

      result = await session.execute(text(sql_query), params)
      row = result.mappings().first()
      if row:
        logger.debug("Fetched one row.")
        return dict(row)
      logger.debug("No row found.")
      return None

  async def fetch_val_sql(self, sql_query: str, params: dict | None = None) -> Any:
    """Fetch a single scalar value from a raw SQL query on the Praxis database.

    Args:
        sql_query (str): The SQL query to execute.
        params (Optional[dict], optional): A dictionary of parameters to
            bind to the SQL query. Defaults to None.

    Returns:
        Any: The scalar value from the first column of the first row, or
        None if no value is found.

    """
    logger.info("Fetching scalar value from raw SQL query.")
    async with self.get_praxis_session() as session:
      from sqlalchemy.sql import text

      result = await session.execute(text(sql_query), params)
      value = result.scalar_one_or_none()
      logger.debug("Fetched scalar value: %s.", value)
      return value

  async def close(self) -> None:
    """Close the Keycloak database connection pool.

    This method should be called during application shutdown to ensure
    proper resource cleanup.

    """
    logger.info("Attempting to close PraxisDBService resources.")
    if self._keycloak_pool and not self._keycloak_pool._closed:  # type: ignore
      await self._keycloak_pool.close()  # type: ignore
      logger.info("Keycloak database pool closed.")
    # The SQLAlchemy engine (from which AsyncSessionLocal is derived) should
    # be dispositiond of at the application level if it's managed globally.
    # If AsyncSessionLocal is derived from create_async_engine(),
    # e.g. engine = create_async_engine(...); AsyncSessionLocal =
    # async_sessionmaker(engine) then engine.disposition() should be called
    # elsewhere (e.g., application shutdown).
    logger.info("PraxisDBService resources closed.")


def _get_keycloak_dsn_from_config() -> str | None:
  """Retrieve the Keycloak DSN from the praxis.ini configuration file.

  Returns:
      Optional[str]: The Keycloak DSN string if found and successfully parsed,
      otherwise None.

  """
  logger.info("Attempting to retrieve Keycloak DSN from configuration.")
  PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
  CONFIG_FILE_PATH = PROJECT_ROOT / "praxis.ini"

  if not CONFIG_FILE_PATH.exists():
    logger.warning(
      "praxis.ini not found at %s for Keycloak DSN lookup.", CONFIG_FILE_PATH,
    )
    return None

  config = ConfigParser()
  config.read(CONFIG_FILE_PATH)

  if config.has_section("keycloak_database"):
    try:
      user = os.getenv("KEYCLOAK_DB_USER", config.get("keycloak_database", "user"))
      password = os.getenv(
        "KEYCLOAK_DB_PASSWORD", config.get("keycloak_database", "password"),
      )
      host = os.getenv("KEYCLOAK_DB_HOST", config.get("keycloak_database", "host"))
      port = os.getenv("KEYCLOAK_DB_PORT", config.get("keycloak_database", "port"))
      dbname = os.getenv("KEYCLOAK_DB_NAME", config.get("keycloak_database", "dbname"))
      dsn = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
      logger.info("Successfully retrieved Keycloak DSN from config.")
      return dsn
    except Exception as e:
      logger.exception("Error reading Keycloak DSN from praxis.ini: %s", e)
      return None
  logger.info("Keycloak database section not found in praxis.ini.")
  return None
