# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Manage Praxis-related database interactions.

praxis/db_services/praxis_orm_service.py

Service layer for interacting with praxis-related data in the database.
This includes Protocol Runs, Protocol Definitions, Users (from Keycloak),
and Assets.

"""

import asyncio
import json
import logging
import os
import uuid  # For generating run_guid
from configparser import ConfigParser
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, AsyncIterator, Dict, List, Optional

import asyncpg  # For Keycloak database
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import (
  AsyncSession,
  async_sessionmaker,
  create_async_engine,
)
from sqlalchemy.orm import joinedload, selectinload

from praxis.backend.models import (
  AssetDefinitionOrm,
  FunctionProtocolDefinitionOrm,
  ProtocolRunOrm,
  ProtocolRunStatusEnum,
  ProtocolSourceRepositoryOrm,
  ResourceInstanceOrm,
  ResourceInstanceStatusEnum,
  UserOrm,
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
  _keycloak_pool: Optional[asyncpg.Pool[Any]] = None
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
    keycloak_dsn: Optional[str] = None,
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
          "Invalid keycloak_dsn: must start with postgresql:// or " "postgres://."
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
            logger.error(
              "Failed to connect to Keycloak database after %d attempts.",
              cls._max_retries,
            )
            raise ConnectionError(
              f"Could not establish Keycloak database connection: " f"{last_error}"
            ) from last_error
        except Exception as e:
          logger.exception("Unexpected error during Keycloak database initialization.")
          raise

      if not cls._keycloak_pool and keycloak_dsn:
        raise ConnectionError(
          f"Failed to initialize Keycloak pool. Last error: {last_error}"
        )
    else:
      logger.info(
        "Keycloak DSN not provided; Keycloak database pool will not be "
        "initialized by PraxisDBService."
      )

    logger.info(
      "PraxisDBService initialized. Praxis DB uses SQLAlchemy async engine "
      "from praxis.utils.db."
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

  async def register_protocol_run(
    self,
    protocol_definition_id: int,
    created_by_user_id: str,
    parameters: Optional[Dict[str, Any]] = None,
    status: ProtocolRunStatusEnum = ProtocolRunStatusEnum.PENDING,
    run_guid: Optional[str] = None,
  ) -> int:
    """Register a new protocol run in the database.

    This function creates a new `ProtocolRunOrm` entry, associating it with
    a protocol definition and a user. It generates a new GUID if one is not
    provided.

    Args:
        protocol_definition_id (int): The ID of the top-level protocol
            definition for this run.
        created_by_user_id (str): The ID of the user who created this run.
        parameters (Optional[Dict[str, Any]], optional): A dictionary of
            input parameters for the protocol run. Defaults to None.
        status (ProtocolRunStatusEnum, optional): The initial status of the
            protocol run. Defaults to `ProtocolRunStatusEnum.PENDING`.
        run_guid (Optional[str], optional): A pre-defined GUID for the run.
            If None, a new UUID will be generated. Defaults to None.

    Returns:
        int: The ID of the newly registered protocol run.

    Raises:
        ValueError: If the protocol run fails to be created and no ID is
            returned after flushing.
        Exception: For any unexpected errors during the process.

    """
    logger.info(
      "Registering new protocol run for protocol definition ID %d by user %s.",
      protocol_definition_id,
      created_by_user_id,
    )
    async with self.get_praxis_session() as session:
      if not run_guid:
        run_guid = str(uuid.uuid4())
        logger.debug("Generated new run GUID: %s.", run_guid)

      new_run = ProtocolRunOrm(
        run_guid=run_guid,
        top_level_protocol_definition_id=protocol_definition_id,
        created_by_user_id=created_by_user_id,
        status=status,
        input_parameters_json=parameters if parameters else {},
      )
      session.add(new_run)
      await session.flush()
      await session.refresh(new_run)

      if new_run.id is None:
        error_message = (
          f"Failed to create protocol run '{run_guid}': no ID returned "
          "after flush/refresh."
        )
        logger.error(error_message)
        raise ValueError(error_message)

      logger.info(
        "Registered new protocol run (ID: %d, GUID: %s).",
        new_run.id,
        new_run.run_guid,
      )
      assert isinstance(new_run.id, int), "Expected integer ID for ProtocolRunOrm"
      return new_run.id

  async def get_protocol_run_details(
    self, protocol_run_id: int
  ) -> Optional[Dict[str, Any]]:
    """Retrieve detailed information about a specific protocol run.

    This function fetches a `ProtocolRunOrm` by its ID, including details
    about the user who created it.

    Args:
        protocol_run_id (int): The ID of the protocol run to retrieve.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the protocol run
        details, or None if the run is not found.

    """
    logger.info("Retrieving details for protocol run ID: %d.", protocol_run_id)
    async with self.get_praxis_session() as session:
      stmt = (
        select(ProtocolRunOrm)
        .options(joinedload(ProtocolRunOrm.created_by_user))
        .where(ProtocolRunOrm.id == protocol_run_id)
      )
      result = await session.execute(stmt)
      run_orm = result.scalar_one_or_none()

      if run_orm:
        user_data = run_orm.created_by_user
        user_info = None
        if user_data:
          # Assuming UserOrm is an ORM object or has .get() if it's a dict
          user_info = {
            "id": getattr(user_data, "id", None),
            "username": getattr(user_data, "username", None),
            "email": getattr(user_data, "email", None),
            "first_name": getattr(user_data, "first_name", None),
            "last_name": getattr(user_data, "last_name", None),
          }
        logger.info("Found protocol run ID %d.", protocol_run_id)
        return {
          "protocol_run_id": run_orm.id,
          "run_guid": run_orm.run_guid,
          "protocol_definition_id": run_orm.top_level_protocol_definition_id,
          "start_time": (
            run_orm.start_time.isoformat() if run_orm.start_time else None
          ),
          "end_time": (run_orm.end_time.isoformat() if run_orm.end_time else None),
          "status": run_orm.status.name if run_orm.status else None,
          "user": user_info,
          "parameters": run_orm.input_parameters_json,
          "resolved_assets": run_orm.resolved_assets_json,
          "output_data": run_orm.output_data_json,
          "initial_state": run_orm.initial_state_json,
          "final_state": run_orm.final_state_json,
          "data_directory_path": run_orm.data_directory_path,
        }
      logger.info("Protocol run ID %d not found.", protocol_run_id)
      return None

  async def update_protocol_run_status(
    self, protocol_run_id: int, status: ProtocolRunStatusEnum
  ):
    """Update the status of a specific protocol run.

    If the new status indicates completion or failure, the `end_time` of
    the protocol run will also be set to the current UTC time.

    Args:
        protocol_run_id (int): The ID of the protocol run to update.
        status (ProtocolRunStatusEnum): The new status for the protocol run.

    """
    logger.info(
      "Updating status for protocol run ID %d to '%s'.",
      protocol_run_id,
      status.name,
    )
    async with self.get_praxis_session() as session:
      values_to_update: Dict[str, Any] = {"status": status}
      if status in (
        ProtocolRunStatusEnum.COMPLETED,
        ProtocolRunStatusEnum.FAILED,
        ProtocolRunStatusEnum.CANCELLED,
      ):
        values_to_update["end_time"] = func.now()
        logger.debug(
          "Setting end_time for protocol run ID %d due to status '%s'.",
          protocol_run_id,
          status.name,
        )

      stmt = (
        update(ProtocolRunOrm)
        .where(ProtocolRunOrm.id == protocol_run_id)
        .values(**values_to_update)
      )
      await session.execute(stmt)
      logger.info("Protocol run %d status updated to %s.", protocol_run_id, status.name)

  async def list_protocol_runs(
    self,
    status: Optional[ProtocolRunStatusEnum] = None,
    created_by_user_id: Optional[str] = None,
  ) -> List[Dict[str, Any]]:
    """List protocol runs with optional filtering by status and user.

    Args:
        status (Optional[ProtocolRunStatusEnum], optional): Filter runs by
            their current status. Defaults to None.
        created_by_user_id (Optional[str], optional): Filter runs by the ID
            of the user who created them. Defaults to None.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each representing a
        protocol run with its details.

    """
    logger.info(
      "Listing protocol runs with filters: status=%s, created_by_user_id=%s.",
      status,
      created_by_user_id,
    )
    async with self.get_praxis_session() as session:
      stmt = (
        select(ProtocolRunOrm)
        .options(joinedload(ProtocolRunOrm.created_by_user))
        .order_by(
          ProtocolRunOrm.start_time.desc()
          if ProtocolRunOrm.start_time is not None
          else ProtocolRunOrm.id.desc()
        )
      )

      if status:
        stmt = stmt.where(ProtocolRunOrm.status == status)
      if created_by_user_id:
        # Assuming created_by_user relationship points to a UserOrm-like object
        stmt = stmt.where(ProtocolRunOrm.created_by_user.has(id=created_by_user_id))

      result = await session.execute(stmt)
      runs_orm = result.scalars().all()

      runs_list = []
      for run_orm in runs_orm:
        user_data = run_orm.created_by_user
        user_info = None
        if user_data:
          user_info = {
            "id": getattr(user_data, "id", None),
            "username": getattr(user_data, "username", None),
            "email": getattr(user_data, "email", None),
            "first_name": getattr(user_data, "first_name", None),
            "last_name": getattr(user_data, "last_name", None),
          }
        runs_list.append(
          {
            "protocol_run_id": run_orm.id,
            "run_guid": run_orm.run_guid,
            "protocol_definition_id": (run_orm.top_level_protocol_definition_id),
            "start_time": (
              run_orm.start_time.isoformat() if run_orm.start_time else None
            ),
            "end_time": (run_orm.end_time.isoformat() if run_orm.end_time else None),
            "status": run_orm.status.name if run_orm.status else None,
            "user": user_info,
            "parameters": run_orm.input_parameters_json,
          }
        )
      logger.info("Found %d protocol runs.", len(runs_list))
      return runs_list

  async def add_asset_instance(
    self,
    user_assigned_name: str,
    pylabrobot_definition_name: str,
    properties_json: Optional[dict[str, Any]] = None,
    lot_number: Optional[str] = None,
    expiry_date: Optional[Any] = None,
    current_status: ResourceInstanceStatusEnum = ResourceInstanceStatusEnum.UNKNOWN,
  ) -> int:
    """Add a new resource asset instance or update an existing one.

    If an asset with the given `user_assigned_name` already exists, its
    details will be updated. Otherwise, a new asset instance will be created.

    Args:
        user_assigned_name (str): A unique, user-friendly name for the
            asset instance.
        pylabrobot_definition_name (str): The PyLabRobot definition name
            associated with this asset (e.g., "tip_rack_1000ul").
        properties_json (Optional[dict[str, Any]], optional): Additional
            properties for the asset stored as JSON. Defaults to None.
        lot_number (Optional[str], optional): The lot number of the asset.
            Defaults to None.
        expiry_date (Optional[Any], optional): The expiry date of the asset.
            Can be a `datetime` object. Defaults to None.
        current_status (ResourceInstanceStatusEnum, optional): The current
            status of the resource instance. Defaults to
            `ResourceInstanceStatusEnum.UNKNOWN`.

    Returns:
        int: The ID of the created or updated asset instance.

    Raises:
        ValueError: If the asset instance fails to be added/updated and no
            ID is returned after flushing.
        Exception: For any unexpected errors during the process.

    """
    log_prefix = (
      f"Asset Instance (Name: '{user_assigned_name}', "
      f"Def: '{pylabrobot_definition_name}'):"
    )
    logger.info("%s Attempting to add or update asset instance.", log_prefix)
    async with self.get_praxis_session() as session:
      existing_asset_stmt = select(ResourceInstanceOrm).where(
        ResourceInstanceOrm.user_assigned_name == user_assigned_name
      )
      result = await session.execute(existing_asset_stmt)
      asset_orm = result.scalar_one_or_none()

      if asset_orm:
        asset_orm.pylabrobot_definition_name = pylabrobot_definition_name
        asset_orm.properties_json = (
          properties_json if properties_json is not None else asset_orm.properties_json
        )
        asset_orm.lot_number = (
          lot_number if lot_number is not None else asset_orm.lot_number
        )
        asset_orm.expiry_date = (
          expiry_date if expiry_date is not None else asset_orm.expiry_date
        )
        asset_orm.current_status = current_status
        logger.info("%s Updating existing asset instance.", log_prefix)
      else:
        asset_orm = ResourceInstanceOrm(
          user_assigned_name=user_assigned_name,
          pylabrobot_definition_name=pylabrobot_definition_name,
          properties_json=properties_json if properties_json else {},
          lot_number=lot_number,
          expiry_date=expiry_date,
          current_status=current_status,
        )
        session.add(asset_orm)
        logger.info("%s Adding new asset instance.", log_prefix)

      await session.flush()
      await session.refresh(asset_orm)
      if asset_orm.id is None:
        error_message = (
          f"Failed to add/update resource instance '{user_assigned_name}': "
          "no ID returned."
        )
        logger.error(error_message)
        raise ValueError(error_message)
      logger.info("%s Operation completed. ID: %d.", log_prefix, asset_orm.id)
      return asset_orm.id

  async def get_asset_instance(
    self, user_assigned_name: str
  ) -> Optional[Dict[str, Any]]:
    """Retrieve details of a specific resource asset instance by its name.

    Args:
        user_assigned_name (str): The user-friendly name of the asset
            instance to retrieve.

    Returns:
        Optional[Dict[str, Any]]: A dictionary containing the asset instance
        details, or None if the asset is not found.

    """
    logger.info(
      "Retrieving asset instance with user_assigned_name: '%s'.",
      user_assigned_name,
    )
    async with self.get_praxis_session() as session:
      stmt = select(ResourceInstanceOrm).where(
        ResourceInstanceOrm.user_assigned_name == user_assigned_name
      )
      result = await session.execute(stmt)
      asset_orm = result.scalar_one_or_none()

      if asset_orm:
        logger.info("Found asset instance '%s'.", user_assigned_name)
        return {
          "id": asset_orm.id,
          "user_assigned_name": asset_orm.user_assigned_name,
          "pylabrobot_definition_name": (asset_orm.pylabrobot_definition_name),
          "lot_number": asset_orm.lot_number,
          "expiry_date": (
            asset_orm.expiry_date.isoformat() if asset_orm.expiry_date else None
          ),
          "date_added_to_inventory": (
            asset_orm.date_added_to_inventory.isoformat()
            if asset_orm.date_added_to_inventory
            else None
          ),
          "current_status": (
            asset_orm.current_status.name if asset_orm.current_status else None
          ),
          "status_details": asset_orm.status_details,
          "current_deck_position_name": asset_orm.current_deck_position_name,
          "location_machine_id": asset_orm.location_machine_id,
          "physical_location_description": (asset_orm.physical_location_description),
          "properties_json": asset_orm.properties_json,
          "is_permanent_fixture": asset_orm.is_permanent_fixture,
          "current_protocol_run_guid": (asset_orm.current_protocol_run_guid),
          "is_available": asset_orm.current_status
          in [
            ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
            ResourceInstanceStatusEnum.AVAILABLE_ON_DECK,
            ResourceInstanceStatusEnum.EMPTY,
            ResourceInstanceStatusEnum.PARTIALLY_FILLED,
            ResourceInstanceStatusEnum.FULL,
          ],
        }
      logger.info("Asset instance '%s' not found.", user_assigned_name)
      return None

  async def get_all_users(self) -> Dict[str, Dict[str, Any]]:
    """Retrieve all active users from the Keycloak database.

    Returns:
        Dict[str, Dict[str, Any]]: A dictionary where keys are usernames
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
            """
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

  async def execute_sql(self, sql_statement: str, params: Optional[dict] = None):
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
    self, sql_query: str, params: Optional[dict] = None
  ) -> List[Dict[Any, Any]]:
    """Fetch all rows from a raw SQL query on the Praxis database.

    Args:
        sql_query (str): The SQL query to execute.
        params (Optional[dict], optional): A dictionary of parameters to
            bind to the SQL query. Defaults to None.

    Returns:
        List[Dict[Any, Any]]: A list of dictionaries, where each dictionary
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
    self, sql_query: str, params: Optional[dict] = None
  ) -> Optional[Dict[Any, Any]]:
    """Fetch a single row from a raw SQL query on the Praxis database.

    Args:
        sql_query (str): The SQL query to execute.
        params (Optional[dict], optional): A dictionary of parameters to
            bind to the SQL query. Defaults to None.

    Returns:
        Optional[Dict[Any, Any]]: A dictionary representing the first row
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

  async def fetch_val_sql(self, sql_query: str, params: Optional[dict] = None) -> Any:
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

  async def close(self):
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


def _get_keycloak_dsn_from_config() -> Optional[str]:
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
      "praxis.ini not found at %s for Keycloak DSN lookup.", CONFIG_FILE_PATH
    )
    return None

  config = ConfigParser()
  config.read(CONFIG_FILE_PATH)

  if config.has_section("keycloak_database"):
    try:
      user = os.getenv("KEYCLOAK_DB_USER", config.get("keycloak_database", "user"))
      password = os.getenv(
        "KEYCLOAK_DB_PASSWORD", config.get("keycloak_database", "password")
      )
      host = os.getenv("KEYCLOAK_DB_HOST", config.get("keycloak_database", "host"))
      port = os.getenv("KEYCLOAK_DB_PORT", config.get("keycloak_database", "port"))
      dbname = os.getenv("KEYCLOAK_DB_NAME", config.get("keycloak_database", "dbname"))
      dsn = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
      logger.info("Successfully retrieved Keycloak DSN from config.")
      return dsn
    except Exception as e:
      logger.error("Error reading Keycloak DSN from praxis.ini: %s", e)
      return None
  logger.info("Keycloak database section not found in praxis.ini.")
  return None
