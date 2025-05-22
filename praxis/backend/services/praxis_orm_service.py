# pyright: reportUnusedImport=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportMissingTypeArgument=false
import asyncio
import asyncpg # For Keycloak database
import json
import logging
import os
from typing import Optional, Dict, List, Any, Union, cast, TYPE_CHECKING, AsyncIterator
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from configparser import ConfigParser

# SQLAlchemy imports
from sqlalchemy.future import select # For SQLAlchemy 1.4 style, or just `from sqlalchemy import select` for 2.0
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import update, delete, func

# Pylabrobot imports (ensure these are compatible with your ORM storage if needed)
from pylabrobot.resources import Resource
from pylabrobot.machines import Machine
from pylabrobot.utils import find_subclass
import importlib.util

# Praxis specific imports
# Assuming this file will be in the 'praxis' directory, adjust paths if it's in 'praxis/utils'
from praxis.backend.utils.db import AsyncSessionLocal, get_async_db_session, Base as PraxisBase # Core SQLAlchemy setup for Praxis DB
from praxis.backend.database_models import (
    ProtocolSourceStatusEnum, ProtocolRunStatusEnum,
    FunctionCallStatusEnum, ProtocolSourceRepositoryOrm, FileSystemProtocolSourceOrm,
    FunctionProtocolDefinitionOrm, ParameterDefinitionOrm, AssetDefinitionOrm,
    ProtocolRunOrm, FunctionCallLogOrm, ManagedDeviceOrm, LabwareInstanceOrm, LabwareDefinitionCatalogOrm,
    ManagedDeviceStatusEnum, LabwareInstanceStatusEnum, LabwareCategoryEnum, AssetInstanceOrm
)
# from .configure import PraxisConfiguration # If still needed for other configs
# from .interfaces import WorkcellAssetsInterface # If used by methods
# from .protocol.parameter import ProtocolParameters # If used by methods

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    # from .interfaces import ProtocolInterface # If used by methods

logger = logging.getLogger(__name__)


class PraxisDBService:
    _instance: Optional["PraxisDBService"] = None
    _keycloak_pool: Optional[asyncpg.Pool[Any]] = None # For Keycloak DB TODO: establish if this should be Any
    _max_retries = 3
    _retry_delay = 1  # seconds

    def __new__(cls, *args, **kwargs): # type: ignore for generic method
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def initialize(
        cls, keycloak_dsn: Optional[str] = None, min_kc_pool_size: int = 5, max_kc_pool_size: int = 10
    ):
        """
        Initializes the database service.
        - The Praxis DB (SQLAlchemy async engine & session) is initialized by praxis.utils.db.
        - This method focuses on initializing the asyncpg pool for the Keycloak database if a DSN is provided.
        """
        if not cls._instance:
            # In case initialize is called before the first __new__ (e.g. directly on class)
            cls._instance = cls()

        # --- Keycloak Database Pool Initialization (using asyncpg) ---
        if keycloak_dsn:
            if not keycloak_dsn.startswith(("postgresql://", "postgres://")):
                logger.error("Invalid keycloak_dsn: must start with postgresql:// or postgres://")
                raise ValueError("Invalid keycloak_dsn")

            retries = 0
            current_retry_delay = cls._retry_delay
            last_error = None

            while retries < cls._max_retries:
                try:
                    if not cls._keycloak_pool or cls._keycloak_pool._closed: # Check if pool needs creation/recreation
                        logger.info(f"Attempting to connect to Keycloak database: {keycloak_dsn.split('@')[-1]}")
                        cls._keycloak_pool = await asyncpg.create_pool(
                            dsn=keycloak_dsn,
                            min_size=min_kc_pool_size,
                            max_size=max_kc_pool_size,
                            command_timeout=60,
                            timeout=10.0,  # Connection timeout
                        )
                        assert cls._keycloak_pool is not None, "Failed to create Keycloak database pool"
                        # Test Keycloak connection
                        async with cls._keycloak_pool.acquire() as conn:
                            await conn.execute("SELECT 1")
                        logger.info("Successfully connected to Keycloak database.")
                        break # Exit loop on success
                except (ConnectionRefusedError, asyncpg.PostgresError, OSError) as e: # Added OSError for broader network issues
                    last_error = e
                    retries += 1
                    logger.warning(f"Keycloak database connection attempt {retries} failed: {str(e)}")
                    if retries < cls._max_retries:
                        logger.info(f"Retrying Keycloak connection in {current_retry_delay} seconds...")
                        await asyncio.sleep(current_retry_delay)
                        current_retry_delay *= 2  # Exponential backoff
                    else:
                        logger.error(f"Failed to connect to Keycloak database after {cls._max_retries} attempts.")
                        # Decide error handling: raise, or proceed without Keycloak pool if optional
                        # For now, let's raise if DSN was provided but connection failed
                        raise ConnectionError(f"Could not establish Keycloak database connection: {last_error}") from last_error
                except Exception as e:
                    logger.error(f"Unexpected error during Keycloak database initialization: {str(e)}")
                    raise # Re-raise unexpected errors

            if not cls._keycloak_pool and keycloak_dsn: # Should be caught by the loop's else, but as a safeguard
                 raise ConnectionError(f"Failed to initialize Keycloak pool. Last error: {last_error}")

        else:
            logger.info("Keycloak DSN not provided; Keycloak database pool will not be initialized by PraxisDBService.")

        logger.info("PraxisDBService initialized. Praxis DB uses SQLAlchemy async engine from praxis.utils.db.")
        return cls._instance

    # --- Context Managers for Connections ---
    @asynccontextmanager
    async def get_praxis_session(self) -> AsyncIterator[AsyncSession]:
        """Provides an SQLAlchemy AsyncSession for the Praxis database."""
        # This uses the session factory from praxis.utils.db
        session = AsyncSessionLocal()
        try:
            yield session
            await session.commit() # Commit if no exceptions
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @asynccontextmanager
    async def get_keycloak_connection(self) -> AsyncIterator[asyncpg.Connection[Any]]: # TODO: refine type
        """Provides an asyncpg connection for the Keycloak database."""
        if self._keycloak_pool is None:
            logger.error("Keycloak database pool not initialized. Call initialize() with keycloak_dsn first.")
            raise RuntimeError("Keycloak database pool not initialized.")

        conn = None
        try:
            conn = await self._keycloak_pool.acquire()
            if not isinstance(conn, asyncpg.Connection):
                logger.error("Failed to acquire Keycloak connection from pool.")
                raise ConnectionError("Failed to acquire Keycloak connection from pool.") # TODO: decide whether to raise or return None
            yield conn
        finally:
            if conn:
                await self._keycloak_pool.release(conn)

    # --- Protocol Management Methods (Ported to SQLAlchemy ORM for Praxis DB) ---
    async def register_protocol_run(
        self,
        protocol_name: str, # This likely refers to the name of the FunctionProtocolDefinitionOrm
        user_id: str, # UUID of the UserOrm
        protocol_definition_id: int, # FK to FunctionProtocolDefinitionOrm
        parameters: Optional[Dict[str, Any]] = None,
        # required_assets: Optional[Dict[str, Any]] = None, # This seems more like definition metadata
        # data_directory: Optional[str] = None, # Potentially part of ProtocolRunOrm
        # database_file: Optional[str] = None # Potentially part of ProtocolRunOrm
        status: str = "initializing",
    ) -> int:
        """
        Registers a new protocol run in the database.
        This corresponds to creating a ProtocolRunOrm instance.
        """
        async with self.get_praxis_session() as session:
            new_run = ProtocolRunOrm(
                function_protocol_definition_id=protocol_definition_id,
                user_id=user_id, # Assuming user_id is the UUID string from Keycloak/UserOrm
                run_status=status,
                # protocol_name=protocol_name, # If you want to store the human-readable name here too
                # parameters_json=parameters if parameters else {}, # Storing actual run parameters
                # data_directory=data_directory,
                # database_file=database_file,
                # start_time will be set by default in the ORM or DB
            )
            session.add(new_run)
            await session.flush() # To get the new_run.id before commit

            if parameters:
                for key, value in parameters.items():
                    # Find the corresponding ProtocolParameterDefinitionOrm to link if needed,
                    # or just store the key-value pair.
                    # For simplicity, assuming direct storage for now.
                    run_param = ParameterDefinitionOrm(
                        protocol_run_id=new_run.id,
                        parameter_key=key,
                        parameter_value_json=value # Ensure value is JSON serializable
                    )
                    session.add(run_param)

            await session.commit() # Commit all changes
            await session.refresh(new_run) # Refresh to get all DB-generated fields like ID, timestamps

            if new_run.id is None: # type: ignore
                raise ValueError("Failed to create protocol run: no ID returned after commit.")

            logger.info(f"Registered new protocol run: {protocol_name} (ID: {new_run.id})")
            assert isinstance(new_run.id, int), "Expected integer ID for ProtocolRunOrm" # TODO: validate
            return new_run.id

    async def get_protocol_run_details(self, protocol_run_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieves details for a specific protocol run, including user info and parameters.
        """
        async with self.get_praxis_session() as session:
            stmt = (
                select(ProtocolRunOrm)
                .options(
                    selectinload(ProtocolRunOrm.parameters), # Eager load parameters
                    joinedload(ProtocolRunOrm.user) # Eager load user via relationship
                )
                .where(ProtocolRunOrm.id == protocol_run_id)
            )
            result = await session.execute(stmt)
            run_orm = result.scalar_one_or_none()

            if run_orm:
                # Convert parameters from list of ORM objects to a dict
                params_dict = {p.parameter_key: p.parameter_value_json for p in run_orm.parameters}

                user_info = None
                if run_orm.user: # If UserOrm is loaded
                    user_info = {
                        "id": run_orm.user.id,
                        "username": run_orm.user.username,
                        "email": run_orm.user.email,
                        "first_name": run_orm.user.first_name,
                        "last_name": run_orm.user.last_name,
                    }
                # If UserOrm is not populated via SQLAlchemy relation from PraxisDB,
                # you might need a separate call to Keycloak DB using run_orm.user_id
                elif run_orm.user_id:
                     # This assumes UserOrm is populated by a separate sync process or direct FK.
                     # If user_id is Keycloak's ID, you'd fetch from Keycloak here.
                    logger.warning(f"UserOrm not loaded for ProtocolRun {run_orm.id}, user_id: {run_orm.user_id}. Fetching from Keycloak if needed.")
                    # Example: user_info = await self.get_user_by_id(run_orm.user_id) # Keycloak call

                return {
                    "protocol_run_id": run_orm.id,
                    "protocol_definition_id": run_orm.function_protocol_definition_id,
                    # "protocol_name": run_orm.protocol_name, # if stored on ProtocolRunOrm
                    "start_time": run_orm.start_time.isoformat() if run_orm.start_time else None, # type:ignore # TODO: check if timezone-aware and see if better None check method
                    "end_time": run_orm.end_time.isoformat() if run_orm.end_time else None, # type:ignore # TODO: check if timezone-aware and see if better None check method
                    "status": run_orm.run_status,
                    "user": user_info,
                    # "data_directory": run_orm.data_directory,
                    # "database_file": run_orm.database_file,
                    "parameters": params_dict,
                    # "assets": json.loads(run_orm.assets_json) if run_orm.assets_json else {}, # If you store assigned assets here
                }
            return None

    async def update_protocol_run_status(self, protocol_run_id: int, status: str):
        """Update the status of a protocol run and set end_time if completed/failed/cancelled."""
        async with self.get_praxis_session() as session:
            stmt = (
                update(ProtocolRunOrm)
                .where(ProtocolRunOrm.id == protocol_run_id)
                .values(run_status=status)
            )
            if status.lower() in ('completed', 'failed', 'cancelled'):
                stmt = stmt.values(end_time=func.now()) # Use database's current time

            await session.execute(stmt)
            # No need to fetch, just commit. If you need the updated object, query it.
            # logger.info(f"Protocol run {protocol_run_id} status updated to {status}.")

    async def list_protocol_runs(self, status: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict]: # type: ignore # TODO: refine type
        """List all protocol runs, optionally filtered by status and/or user_id."""
        async with self.get_praxis_session() as session:
            stmt = select(ProtocolRunOrm).options(
                selectinload(ProtocolRunOrm.parameters),
                joinedload(ProtocolRunOrm.user) # Or selectinload if UserOrm is simple
            ).order_by(ProtocolRunOrm.start_time.desc()) # Example ordering

            if status:
                stmt = stmt.where(ProtocolRunOrm.run_status == status)
            if user_id:
                stmt = stmt.where(ProtocolRunOrm.user_id == user_id)

            result = await session.execute(stmt)
            runs_orm = result.scalars().all()

            runs_list = []
            for run_orm in runs_orm:
                params_dict = {p.parameter_key: p.parameter_value_json for p in run_orm.parameters}
                user_info = None
                if run_orm.user:
                     user_info = {
                        "id": run_orm.user.id, "username": run_orm.user.username,
                        "email": run_orm.user.email, "first_name": run_orm.user.first_name,
                        "last_name": run_orm.user.last_name
                    }
                runs_list.append({ # type: ignore
                    "protocol_run_id": run_orm.id,
                    "protocol_definition_id": run_orm.function_protocol_definition_id,
                    "start_time": run_orm.start_time.isoformat() if run_orm.start_time else None, # type:ignore # TODO: check if timezone-aware and see if better None check method
                    "end_time": run_orm.end_time.isoformat() if run_orm.end_time else None, # type:ignore # TODO: check if timezone-aware and see if better None check method
                    "status": run_orm.run_status,
                    "user": user_info,
                    "parameters": params_dict,
                })
            return runs_list # type: ignore

    # --- Asset Management Methods (To be ported) ---
    async def add_asset_instance(
        self,
        name: str,
        asset_definition_id: int, # FK to AssetDefinitionOrm
        asset_type: str, # e.g. 'LabwareInstanceOrm', 'DeviceInstanceOrm'
        metadata: Optional[dict[str, str]] = None, # TODO: refine type
        plr_serialized: Optional[dict[str, Any]] = None # TODO: refine type
    ) -> int:
        """Adds or updates an asset instance in the database."""
        async with self.get_praxis_session() as session:
            # Determine the correct ORM class based on asset_type or other logic
            # For now, assuming a generic AssetInstanceOrm. You might have specific tables.
            # This example uses AssetInstanceOrm. You'll need to adapt if using LabwareInstanceOrm etc.

            # Check if asset exists by name to update or insert
            existing_asset_stmt = select(AssetInstanceOrm).where(AssetInstanceOrm.name == name)
            result = await session.execute(existing_asset_stmt)
            asset_orm = result.scalar_one_or_none()

            if asset_orm: # Update existing
                asset_orm.asset_definition_id = asset_definition_id
                asset_orm.metadata_json = metadata if metadata else asset_orm.metadata_json # type: ignore # TODO: see if a problem
                asset_orm.pylabrobot_configuration_json = plr_serialized if plr_serialized else asset_orm.pylabrobot_configuration_json
                # asset_orm.asset_type_discriminator = asset_type # if you have a discriminator
                logger.info(f"Updating existing asset instance: {name}")
            else: # Insert new
                asset_orm = AssetInstanceOrm(
                    name=name,
                    asset_definition_id=asset_definition_id,
                    # asset_type_discriminator=asset_type, # if using joined table inheritance
                    metadata_json=metadata if metadata else {},
                    pylabrobot_configuration_json=plr_serialized if plr_serialized else {}
                )
                session.add(asset_orm)
                logger.info(f"Adding new asset instance: {name}")

            await session.commit()
            await session.refresh(asset_orm)
            if asset_orm.id is None: # type: ignore
                raise ValueError(f"Failed to add/update asset instance '{name}': no ID returned.")
            return asset_orm.id # type: ignore # TODO: check if this is correct

    async def get_asset_instance(self, name: str) -> Optional[Dict]: # type: ignore # TODO: refine type
        """Retrieves an asset instance by name."""
        async with self.get_praxis_session() as session:
            # This will fetch the base AssetInstanceOrm.
            # If using joined-table inheritance, you might need to load specific types.
            stmt = select(AssetInstanceOrm).where(AssetInstanceOrm.name == name)
            # To load specific types with joined table inheritance:
            # stmt = select(AssetInstanceOrm).options(
            #     selectinload(AssetInstanceOrm.labware_instance_specific), # if LabwareInstanceOrm.asset_instance is the backref
            #     selectinload(AssetInstanceOrm.device_instance_specific)
            # ).where(AssetInstanceOrm.name == name)

            result = await session.execute(stmt)
            asset_orm = result.scalar_one_or_none()

            if asset_orm:
                # Here, you would check asset_orm.asset_type_discriminator or related specific tables
                # to return the correct type of data.
                # For now, returning generic fields:
                return {
                    "id": asset_orm.id,
                    "name": asset_orm.name,
                    "asset_definition_id": asset_orm.asset_definition_id,
                    "metadata": asset_orm.metadata_json,
                    "plr_serialized": asset_orm.pylabrobot_configuration_json,
                    "is_available": asset_orm.is_available, # Assuming this field exists on AssetInstanceOrm
                    # "locked_by_protocol_run_id": asset_orm.locked_by_protocol_run_id,
                    # "lock_acquired_at": asset_orm.lock_acquired_at,
                    # "lock_expires_at": asset_orm.lock_expires_at,
                } # type: ignore # TODO: check if this is correct, figure out data to return
            return None

    # ... (Other asset methods like instantiate_asset, get_all_machines, etc. to be ported) ...
    # ... (Locking methods to be ported, using AssetLockOrm or fields on AssetInstanceOrm) ...

    # --- User Management Methods (Using Keycloak asyncpg pool) ---
    async def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        """Get all users from Keycloak as a dictionary keyed by username."""
        async with self.get_keycloak_connection() as conn:
            records = await conn.fetch(
                """
                SELECT id, username, email, first_name, last_name, enabled, roles --, phone_number (if exists)
                FROM user_entity -- Common table name in Keycloak, adjust if different
                WHERE enabled = true
                ORDER BY username
            """
            ) # Note: Table and column names (e.g. user_entity, roles) might vary based on Keycloak version/config
            return {
                record["username"]: {
                    "id": record["id"], "username": record["username"],
                    "email": record["email"], "first_name": record["first_name"],
                    "last_name": record["last_name"],
                    # "roles": json.loads(record["roles"]) if record["roles"] else [], # Roles might be in a separate table or JSON
                    "is_active": record["enabled"],
                }
                for record in records
            }

    # ... (Other Keycloak user methods: get_user, list_users, get_user_by_id, search_users - adapt SQL if needed) ...

    # --- Generic Data Methods (for Praxis DB using SQLAlchemy) ---
    async def execute_sql(self, sql_statement: str, params: Optional[dict] = None):
        """Executes a raw SQL statement. Use with caution."""
        async with self.get_praxis_session() as session:
            from sqlalchemy.sql import text
            await session.execute(text(sql_statement), params)
            # For DML that doesn't return rows, commit is handled by context manager

    async def fetch_all_sql(self, sql_query: str, params: Optional[dict] = None) -> List[Dict]:
        """Fetches all rows from a raw SQL query."""
        async with self.get_praxis_session() as session:
            from sqlalchemy.sql import text
            result = await session.execute(text(sql_query), params)
            return [dict(row) for row in result.mappings()] # .mappings() gives dict-like rows

    async def fetch_one_sql(self, sql_query: str, params: Optional[dict] = None) -> Optional[Dict]:
        """Fetches one row from a raw SQL query."""
        async with self.get_praxis_session() as session:
            from sqlalchemy.sql import text
            result = await session.execute(text(sql_query), params)
            row = result.mappings().first()
            return dict(row) if row else None

    async def fetch_val_sql(self, sql_query: str, params: Optional[dict] = None) -> Any:
        """Fetches a single scalar value from a raw SQL query."""
        async with self.get_praxis_session() as session:
            from sqlalchemy.sql import text
            result = await session.execute(text(sql_query), params)
            return result.scalar_one_or_none()

    # --- Cleanup Method ---
    async def close(self):
        """Closes any active pools."""
        if self._keycloak_pool and not self._keycloak_pool._closed:
            await self._keycloak_pool.close()
            logger.info("Keycloak database pool closed.")
        # SQLAlchemy engine (async_engine from praxis.utils.db) can be disposed if needed,
        # typically on application shutdown.
        # from .utils.db import async_engine as praxis_async_engine
        # await praxis_async_engine.dispose()
        # logger.info("Praxis SQLAlchemy engine disposed.")


# --- Helper to get Keycloak DSN from praxis.ini (similar to praxis.utils.db) ---
def _get_keycloak_dsn_from_config() -> Optional[str]:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent # Assumes this file is in 'praxis/'
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

# --- Global instance (optional, depends on how you manage service instances) ---
# db_service = PraxisDBService()
# You would typically initialize it in your application startup:
# await PraxisDBService.initialize(keycloak_dsn=_get_keycloak_dsn_from_config())


# --- Example Usage (if run directly) ---
async def example_main():
    # Initialize Praxis DB schema (from praxis.utils.db)
    from praxis.backend.utils.db import init_praxis_db_schema as init_praxis_db
    await init_praxis_db()

    # Initialize the service, including Keycloak pool
    keycloak_dsn = _get_keycloak_dsn_from_config()
    service = await PraxisDBService.initialize(keycloak_dsn=keycloak_dsn)

    if not service:
        logger.error("Failed to initialize PraxisDBService.")
        return

    try:
        # Example: Register a protocol definition (simplified)
        # First, ensure a UserOrm and FunctionProtocolDefinitionOrm exist or create them.
        # This is more involved than the old register_protocol.
        # Let's assume a user and protocol definition ID for now.
        user_uuid_for_run = "some-user-uuid" # Replace with actual user ID
        protocol_def_id_for_run = 1 # Replace with actual protocol definition ID

        # Create a dummy UserOrm if it doesn't exist for the example (in real app, users come from Keycloak sync)
        async with service.get_praxis_session() as temp_session:
            user_exists = await temp_session.get(UserOrm, user_uuid_for_run) # TODO: define UserOrm in database models
            if not user_exists:
                temp_session.add(UserOrm(id=user_uuid_for_run, username="test_runner_user"))
                # logger.info(f"Added dummy user {user_uuid_for_run} for example.")
            # Create a dummy FunctionProtocolDefinitionOrm
            proto_def_exists = await temp_session.get(FunctionProtocolDefinitionOrm, protocol_def_id_for_run)
            if not proto_def_exists:
                 # Need a source first
                source_repo = ProtocolSourceRepositoryOrm(repository_url="http://example.com/repo.git", default_branch="main")
                temp_session.add(source_repo)
                await temp_session.flush()

                dummy_protocol_def = FunctionProtocolDefinitionOrm(
                    id=protocol_def_id_for_run, # Manual ID for example
                    name="ExampleProtocolRunDef",
                    version_commit_hash="abc123example",
                    protocol_source_repository_id=source_repo.id, # Link to source
                    is_top_level=True
                )
                temp_session.add(dummy_protocol_def)
                # logger.info(f"Added dummy protocol definition {protocol_def_id_for_run} for example.")
            await temp_session.commit()


        logger.info("Registering a new protocol run...")
        run_id = await service.register_protocol_run(
            protocol_name="MyTestProtocolRun", # This name might be redundant if using def_id
            user_id=user_uuid_for_run,
            protocol_definition_id=protocol_def_id_for_run,
            parameters={"sample_count": 10, "target_volume": 50.5},
            status="pending"
        )
        logger.info(f"Registered protocol run ID: {run_id}")

        logger.info(f"Fetching protocol run details for ID: {run_id}...")
        run_details = await service.get_protocol_run_details(run_id)
        if run_details:
            logger.info(f"Protocol Run Details: {json.dumps(run_details, indent=2)}")
        else:
            logger.error(f"Could not fetch details for protocol run ID: {run_id}")

        logger.info("Updating protocol run status...")
        await service.update_protocol_run_status(run_id, "completed")
        updated_details = await service.get_protocol_run_details(run_id)
        logger.info(f"Updated Protocol Run Details: {json.dumps(updated_details, indent=2)}")

        logger.info("Listing protocol runs...")
        all_runs = await service.list_protocol_runs(user_id=user_uuid_for_run)
        logger.info(f"Found {len(all_runs)} runs for user {user_uuid_for_run}:")
        for r in all_runs:
            logger.info(f"  Run ID: {r['protocol_run_id']}, Status: {r['status']}")

        # Example for asset
        asset_def_id = 1 # Assume a definition exists
        async with service.get_praxis_session() as temp_session:
            asset_def_exists = await temp_session.get(AssetDefinitionOrm, asset_def_id)
            if not asset_def_exists:
                temp_session.add(AssetDefinitionOrm(id=asset_def_id, name="GenericPlateDef", definition_type="labware"))
                await temp_session.commit()

        asset_id = await service.add_asset_instance(
            name="MyTestPlate001",
            asset_definition_id=asset_def_id,
            asset_type="LabwareInstanceOrm", # Or a discriminator value
            metadata={"wells": 96, "material": "polystyrene"}, # type: ignore # TODO: have methods cast and unpack to appropriate types
            plr_serialized={"pylabrobot_resource_name": "plate_96_well_pcr"}
        )
        logger.info(f"Added/Updated asset instance ID: {asset_id}")
        asset_details = await service.get_asset_instance("MyTestPlate001")
        logger.info(f"Asset MyTestPlate001 details: {asset_details}")


        # Example Keycloak call (if DSN provided and pool initialized)
        if service._keycloak_pool:
            logger.info("Fetching all Keycloak users...")
            # users = await service.get_all_users() # Adapt SQL in get_all_users if needed
            # logger.info(f"Keycloak users: {users}")
        else:
            logger.info("Skipping Keycloak user fetch as pool is not initialized.")

    except Exception as e:
        logger.error(f"An error occurred in example_main: {e}", exc_info=True)
    finally:
        if service: # Ensure service was initialized
            await service.close()

if __name__ == "__main__":
    # This setup is for running this file directly for testing.
    # In a real application, logger config and service init would be part of app startup.
    LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
    LOG_DIR.mkdir(exist_ok=True)
    log_file_path = LOG_DIR / "praxis_orm_service.log"

    # Setup file logging for the example
    file_handler = logging.FileHandler(log_file_path)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    # Add file handler to the root logger or specific loggers
    logging.getLogger().addHandler(file_handler) # Add to root to catch all
    logging.getLogger().setLevel(logging.INFO) # Ensure root logger level is appropriate

    logger.info(f"Example main started. Logging to: {log_file_path}")
    asyncio.run(example_main())
