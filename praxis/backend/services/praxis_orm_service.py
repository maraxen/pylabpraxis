# pyright: reportUnusedImport=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportMissingTypeArgument=false
import asyncio
import asyncpg # For Keycloak database
import json
import logging
import os
import uuid # For generating run_guid
from typing import Optional, Dict, List, Any, TYPE_CHECKING, AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from configparser import ConfigParser
from sqlalchemy import select, update, func
from sqlalchemy.orm import joinedload, selectinload

from praxis.backend.utils.db import AsyncSessionLocal
from praxis.backend.database_models import (
    ProtocolSourceRepositoryOrm,
    FunctionProtocolDefinitionOrm,
    # ParameterDefinitionOrm, # Not used directly for ProtocolRunOrm parameters
    AssetDefinitionOrm,
    ProtocolRunOrm,
    ProtocolRunStatusEnum, # Import the enum
    LabwareInstanceOrm, # Changed from AssetInstanceOrm for concrete asset operations
    # AssetInstanceOrm, # Keep if abstract usage is still needed elsewhere, but for these methods, LabwareInstanceOrm is used.
    UserOrm # Assuming UserOrm is defined in your database_models
)
from praxis.backend.database_models.asset_management_orm import LabwareInstanceStatusEnum # For asset status

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class PraxisDBService:
    _instance: Optional["PraxisDBService"] = None
    _keycloak_pool: Optional[asyncpg.Pool[Any]] = None
    _max_retries = 3
    _retry_delay = 1  # seconds

    def __new__(cls, *args, **kwargs): # type: ignore
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def initialize(
        cls, keycloak_dsn: Optional[str] = None, min_kc_pool_size: int = 5, max_kc_pool_size: int = 10
    ):
        if not cls._instance:
            cls._instance = cls()

        if keycloak_dsn:
            if not keycloak_dsn.startswith(("postgresql://", "postgres://")):
                logger.error("Invalid keycloak_dsn: must start with postgresql:// or postgres://")
                raise ValueError("Invalid keycloak_dsn")

            retries = 0
            current_retry_delay = cls._retry_delay
            last_error = None

            while retries < cls._max_retries:
                try:
                    if not cls._keycloak_pool or cls._keycloak_pool._closed:
                        logger.info(f"Attempting to connect to Keycloak database: {keycloak_dsn.split('@')[-1]}")
                        cls._keycloak_pool = await asyncpg.create_pool(
                            dsn=keycloak_dsn,
                            min_size=min_kc_pool_size,
                            max_size=max_kc_pool_size,
                            command_timeout=60,
                            timeout=10.0,
                        )
                        assert cls._keycloak_pool is not None, "Failed to create Keycloak database pool"
                        async with cls._keycloak_pool.acquire() as conn:
                            await conn.execute("SELECT 1")
                        logger.info("Successfully connected to Keycloak database.")
                        break
                except (ConnectionRefusedError, asyncpg.PostgresError, OSError) as e:
                    last_error = e
                    retries += 1
                    logger.warning(f"Keycloak database connection attempt {retries} failed: {str(e)}")
                    if retries < cls._max_retries:
                        logger.info(f"Retrying Keycloak connection in {current_retry_delay} seconds...")
                        await asyncio.sleep(current_retry_delay)
                        current_retry_delay *= 2
                    else:
                        logger.error(f"Failed to connect to Keycloak database after {cls._max_retries} attempts.")
                        raise ConnectionError(f"Could not establish Keycloak database connection: {last_error}") from last_error
                except Exception as e:
                    logger.error(f"Unexpected error during Keycloak database initialization: {str(e)}")
                    raise

            if not cls._keycloak_pool and keycloak_dsn:
                  raise ConnectionError(f"Failed to initialize Keycloak pool. Last error: {last_error}")
        else:
            logger.info("Keycloak DSN not provided; Keycloak database pool will not be initialized by PraxisDBService.")

        logger.info("PraxisDBService initialized. Praxis DB uses SQLAlchemy async engine from praxis.utils.db.")
        return cls._instance

    @asynccontextmanager
    async def get_praxis_session(self) -> AsyncIterator[AsyncSession]:
        session = AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @asynccontextmanager
    async def get_keycloak_connection(self) -> AsyncIterator[asyncpg.Connection[Any]]:
        if self._keycloak_pool is None:
            logger.error("Keycloak database pool not initialized. Call initialize() with keycloak_dsn first.")
            raise RuntimeError("Keycloak database pool not initialized.")

        conn = None
        try:
            conn = await self._keycloak_pool.acquire()
            if not isinstance(conn, asyncpg.Connection):
                logger.error("Failed to acquire Keycloak connection from pool.")
                raise ConnectionError("Failed to acquire Keycloak connection from pool.")
            yield conn
        finally:
            if conn:
                await self._keycloak_pool.release(conn)

    async def register_protocol_run(
        self,
        protocol_definition_id: int, # FK to FunctionProtocolDefinitionOrm
        created_by_user_id: str, # UUID of the UserOrm
        parameters: Optional[Dict[str, Any]] = None,
        status: ProtocolRunStatusEnum = ProtocolRunStatusEnum.PENDING, # Use Enum
        run_guid: Optional[str] = None, # Optional: if not provided, will be generated
    ) -> int:
        """
        Registers a new protocol run in the database.
        Corresponds to creating a ProtocolRunOrm instance.
        """
        async with self.get_praxis_session() as session:
            if not run_guid:
                run_guid = str(uuid.uuid4())

            new_run = ProtocolRunOrm(
                run_guid=run_guid,
                top_level_protocol_definition_id=protocol_definition_id,
                created_by_user_id=created_by_user_id,
                status=status,
                input_parameters_json=parameters if parameters else {},
                # start_time will be set by default in the ORM or DB if applicable, or set explicitly when run starts
            )
            session.add(new_run)
            await session.flush() # To get the new_run.id before commit
            await session.commit()
            await session.refresh(new_run)

            if new_run.id is None:
                raise ValueError("Failed to create protocol run: no ID returned after commit.")

            logger.info(f"Registered new protocol run (ID: {new_run.id}, GUID: {new_run.run_guid})")
            assert isinstance(new_run.id, int), "Expected integer ID for ProtocolRunOrm"
            return new_run.id

    async def get_protocol_run_details(self, protocol_run_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves details for a specific protocol run, including user info and parameters.
        """
        async with self.get_praxis_session() as session:
            stmt = (
                select(ProtocolRunOrm)
                .options(
                    joinedload(ProtocolRunOrm.created_by_user) # Eager load user via relationship
                )
                .where(ProtocolRunOrm.id == protocol_run_id)
            )
            result = await session.execute(stmt)
            run_orm = result.scalar_one_or_none()

            if run_orm:
                user_info = None
                if run_orm.created_by_user: # If UserOrm is loaded
                    user_info = {
                        "id": run_orm.created_by_user.get("id", None),
                        "username": run_orm.created_by_user.get("username", None),
                        "email": run_orm.created_by_user.get("email", None),
                        "first_name": run_orm.created_by_user.get("first_name", None),
                        "last_name": run_orm.created_by_user.get("last_name", None),
                    }

                return {
                    "protocol_run_id": run_orm.id,
                    "run_guid": run_orm.run_guid,
                    "protocol_definition_id": run_orm.top_level_protocol_definition_id,
                    "start_time": run_orm.start_time.isoformat() if run_orm.start_time else None,
                    "end_time": run_orm.end_time.isoformat() if run_orm.end_time else None,
                    "status": run_orm.status.name if run_orm.status else None, # Access enum name
                    "user": user_info,
                    "parameters": run_orm.input_parameters_json,
                    "resolved_assets": run_orm.resolved_assets_json,
                    "output_data": run_orm.output_data_json,
                    "initial_state": run_orm.initial_state_json,
                    "final_state": run_orm.final_state_json,
                    "data_directory_path": run_orm.data_directory_path,
                }
            return None

    async def update_protocol_run_status(self, protocol_run_id: int, status: ProtocolRunStatusEnum):
        """Update the status of a protocol run and set end_time if completed/failed/cancelled."""
        async with self.get_praxis_session() as session:
            values_to_update: Dict[str, Any] = {"status": status}
            if status in (ProtocolRunStatusEnum.COMPLETED, ProtocolRunStatusEnum.FAILED, ProtocolRunStatusEnum.CANCELLED):
                values_to_update["end_time"] = func.now() # Use database's current time

            stmt = (
                update(ProtocolRunOrm)
                .where(ProtocolRunOrm.id == protocol_run_id)
                .values(**values_to_update)
            )
            await session.execute(stmt)
            logger.info(f"Protocol run {protocol_run_id} status updated to {status.name}.")


    async def list_protocol_runs(self,
                                  status: Optional[ProtocolRunStatusEnum] = None,
                                  created_by_user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all protocol runs, optionally filtered by status and/or user_id.
        Parameters:
            status (Optional[ProtocolRunStatusEnum]): Filter by run status.
            created_by_user_id (Optional[str]): Filter by user ID who created the run.
        Returns:
            List[Dict[str, Any]]: A list of protocol run details.
        """
        async with self.get_praxis_session() as session:
            stmt = select(ProtocolRunOrm).options(
                joinedload(ProtocolRunOrm.created_by_user)
            ).order_by(ProtocolRunOrm.start_time.desc() if ProtocolRunOrm.start_time is not None else ProtocolRunOrm.id.desc())


            if status:
                stmt = stmt.where(ProtocolRunOrm.status == status)
            if created_by_user_id:
                stmt = stmt.where(ProtocolRunOrm.created_by_user.id == created_by_user_id)

            result = await session.execute(stmt)
            runs_orm = result.scalars().all()

            runs_list = []
            for run_orm in runs_orm:
                user_info = None
                if run_orm.created_by_user:
                  user_info = {
                      "id": run_orm.created_by_user.get("id"),
                      "username": run_orm.created_by_user.get("username"),
                      "email": run_orm.created_by_user.get("email"),
                      "first_name": run_orm.created_by_user.get("first_name"),
                      "last_name": run_orm.created_by_user.get("last_name")
                  }
                runs_list.append({
                  "protocol_run_id": run_orm.id,
                  "run_guid": run_orm.run_guid,
                  "protocol_definition_id": run_orm.top_level_protocol_definition_id,
                  "start_time": run_orm.start_time.isoformat() if run_orm.start_time else None,
                  "end_time": run_orm.end_time.isoformat() if run_orm.end_time else None,
                  "status": run_orm.status.name if run_orm.status else None,
                  "user": user_info,
                  "parameters": run_orm.input_parameters_json,
                })
            return runs_list

    async def add_asset_instance(
        self,
        user_assigned_name: str, # This is the primary identifier for LabwareInstanceOrm
        pylabrobot_definition_name: str, # FK to LabwareDefinitionCatalogOrm
        # asset_type: str, # This is implicit with LabwareInstanceOrm
        properties_json: Optional[dict[str, Any]] = None, # For instance-specific state
        lot_number: Optional[str] = None,
        expiry_date: Optional[Any] = None, # Can be date or datetime
        current_status: LabwareInstanceStatusEnum = LabwareInstanceStatusEnum.UNKNOWN,
        # plr_serialized: Optional[dict[str, Any]] = None # This seems more like a definition detail
    ) -> int:
        """Adds or updates a labware instance in the database."""
        async with self.get_praxis_session() as session:
            # Check if asset exists by user_assigned_name to update or insert
            existing_asset_stmt = select(LabwareInstanceOrm).where(LabwareInstanceOrm.user_assigned_name == user_assigned_name)
            result = await session.execute(existing_asset_stmt)
            asset_orm = result.scalar_one_or_none()

            if asset_orm: # Update existing
                asset_orm.pylabrobot_definition_name = pylabrobot_definition_name
                asset_orm.properties_json = properties_json if properties_json is not None else asset_orm.properties_json
                asset_orm.lot_number = lot_number if lot_number is not None else asset_orm.lot_number
                asset_orm.expiry_date = expiry_date if expiry_date is not None else asset_orm.expiry_date
                asset_orm.current_status = current_status
                logger.info(f"Updating existing labware instance: {user_assigned_name}")
            else: # Insert new
                asset_orm = LabwareInstanceOrm(
                    user_assigned_name=user_assigned_name,
                    pylabrobot_definition_name=pylabrobot_definition_name,
                    properties_json=properties_json if properties_json else {},
                    lot_number=lot_number,
                    expiry_date=expiry_date,
                    current_status=current_status
                    # date_added_to_inventory will be set by default
                )
                session.add(asset_orm)
                logger.info(f"Adding new labware instance: {user_assigned_name}")

            await session.commit()
            await session.refresh(asset_orm)
            if asset_orm.id is None:
                raise ValueError(f"Failed to add/update labware instance '{user_assigned_name}': no ID returned.")
            return asset_orm.id

    async def get_asset_instance(self, user_assigned_name: str) -> Optional[Dict[str, Any]]:
        """Retrieves a labware instance by its user_assigned_name."""
        async with self.get_praxis_session() as session:
            stmt = select(LabwareInstanceOrm).where(LabwareInstanceOrm.user_assigned_name == user_assigned_name)
            result = await session.execute(stmt)
            asset_orm = result.scalar_one_or_none()

            if asset_orm:
                return {
                    "id": asset_orm.id,
                    "user_assigned_name": asset_orm.user_assigned_name,
                    "pylabrobot_definition_name": asset_orm.pylabrobot_definition_name,
                    "lot_number": asset_orm.lot_number,
                    "expiry_date": asset_orm.expiry_date.isoformat() if asset_orm.expiry_date else None,
                    "date_added_to_inventory": asset_orm.date_added_to_inventory.isoformat() if asset_orm.date_added_to_inventory else None,
                    "current_status": asset_orm.current_status.name if asset_orm.current_status else None,
                    "status_details": asset_orm.status_details,
                    "current_deck_slot_name": asset_orm.current_deck_slot_name,
                    "location_device_id": asset_orm.location_device_id,
                    "physical_location_description": asset_orm.physical_location_description,
                    "properties_json": asset_orm.properties_json,
                    "is_permanent_fixture": asset_orm.is_permanent_fixture,
                    "current_protocol_run_guid": asset_orm.current_protocol_run_guid,
                    # For availability, you might infer it from current_status or add a specific field if needed
                    "is_available": asset_orm.current_status in [
                        LabwareInstanceStatusEnum.AVAILABLE_IN_STORAGE,
                        LabwareInstanceStatusEnum.AVAILABLE_ON_DECK,
                        LabwareInstanceStatusEnum.EMPTY, # Depending on context, empty might mean available for use
                        LabwareInstanceStatusEnum.PARTIALLY_FILLED, # Depending on context
                        LabwareInstanceStatusEnum.FULL # Depending on context (e.g. full source plate)
                    ]
                }
            return None

    async def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        async with self.get_keycloak_connection() as conn:
            records = await conn.fetch(
                """
                SELECT id, username, email, first_name, last_name, enabled
                FROM user_entity
                WHERE enabled = true
                ORDER BY username
            """
            )
            return {
                record["username"]: {
                    "id": record["id"], "username": record["username"],
                    "email": record["email"], "first_name": record["first_name"],
                    "last_name": record["last_name"],
                    "is_active": record["enabled"],
                }
                for record in records
            }

    async def execute_sql(self, sql_statement: str, params: Optional[dict] = None):
        async with self.get_praxis_session() as session:
            from sqlalchemy.sql import text
            await session.execute(text(sql_statement), params)

    async def fetch_all_sql(self, sql_query: str, params: Optional[dict] = None) -> List[Dict[Any, Any]]:
        async with self.get_praxis_session() as session:
            from sqlalchemy.sql import text
            result = await session.execute(text(sql_query), params)
            return [dict(row) for row in result.mappings()]

    async def fetch_one_sql(self, sql_query: str, params: Optional[dict] = None) -> Optional[Dict[Any, Any]]:
        async with self.get_praxis_session() as session:
            from sqlalchemy.sql import text
            result = await session.execute(text(sql_query), params)
            row = result.mappings().first()
            return dict(row) if row else None

    async def fetch_val_sql(self, sql_query: str, params: Optional[dict] = None) -> Any:
        async with self.get_praxis_session() as session:
            from sqlalchemy.sql import text
            result = await session.execute(text(sql_query), params)
            return result.scalar_one_or_none()

    async def close(self):
        if self._keycloak_pool and not self._keycloak_pool._closed:
            await self._keycloak_pool.close()
            logger.info("Keycloak database pool closed.")


def _get_keycloak_dsn_from_config() -> Optional[str]:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent # Adjusted to be project root
    CONFIG_FILE_PATH = PROJECT_ROOT / "praxis.ini"

    if not CONFIG_FILE_PATH.exists():
        logger.warning(f"praxis.ini not found at {CONFIG_FILE_PATH} for Keycloak DSN lookup.")
        return None

    config = ConfigParser()
    config.read(CONFIG_FILE_PATH)

    if config.has_section("keycloak_database"):
        try:
            user = os.getenv("KEYCLOAK_DB_USER", config.get("keycloak_database", "user"))
            password = os.getenv("KEYCLOAK_DB_PASSWORD", config.get("keycloak_database", "password"))
            host = os.getenv("KEYCLOAK_DB_HOST", config.get("keycloak_database", "host"))
            port = os.getenv("KEYCLOAK_DB_PORT", config.get("keycloak_database", "port"))
            dbname = os.getenv("KEYCLOAK_DB_NAME", config.get("keycloak_database", "dbname"))
            return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        except Exception as e:
            logger.error(f"Error reading Keycloak DSN from praxis.ini: {e}")
            return None
    return None
