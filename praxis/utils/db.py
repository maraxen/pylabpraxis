import asyncpg
import pandas as pd
import json
from typing import Optional, Dict, List, Any, Union, cast, TYPE_CHECKING
from contextlib import asynccontextmanager
from datetime import datetime
from pylabrobot.resources import Resource
from pylabrobot.machines import Machine
from pylabrobot.utils import find_subclass
import importlib.util
from pathlib import Path
import asyncio
import os
from ..interfaces import WorkcellAssetsInterface
from ..protocol.parameter import ProtocolParameters

if TYPE_CHECKING:
    from ..interfaces import ProtocolInterface

import logging

from ..configure import PraxisConfiguration

config = PraxisConfiguration("praxis.ini")
logging.basicConfig(
    filename=config.log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    _instance: Optional["DatabaseManager"] = None
    _pool: Optional[asyncpg.Pool] = None
    _keycloak_pool: Optional[asyncpg.Pool] = None
    _max_retries = 3
    _retry_delay = 1  # seconds

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def initialize(
        cls, praxis_dsn: str, keycloak_dsn: str, min_size: int = 5, max_size: int = 10
    ):
        if not cls._instance:
            cls._instance = cls()

        # Validate DSNs
        if not praxis_dsn.startswith(("postgresql://", "postgres://")):
            raise ValueError(
                "Invalid praxis_dsn: must start with postgresql:// or postgres://"
            )
        if not keycloak_dsn.startswith(("postgresql://", "postgres://")):
            raise ValueError(
                "Invalid keycloak_dsn: must start with postgresql:// or postgres://"
            )

        retries = 0
        last_error = None

        while retries < cls._max_retries:
            try:
                if not cls._pool:
                    cls._pool = await asyncpg.create_pool(
                        dsn=praxis_dsn,
                        min_size=min_size,
                        max_size=max_size,
                        command_timeout=60,
                        timeout=10.0,  # Connection timeout in seconds
                    )
                    assert cls._pool is not None, "Failed to create database pool"
                    # Test the connection
                    async with cls._pool.acquire() as conn:
                        await conn.execute("SELECT 1")

                if not cls._keycloak_pool:
                    cls._keycloak_pool = await asyncpg.create_pool(
                        dsn=keycloak_dsn,
                        min_size=min_size,
                        max_size=max_size,
                        command_timeout=60,
                        timeout=10.0,  # Connection timeout in seconds
                    )
                    # Test the connection
                    assert (
                        cls._keycloak_pool is not None
                    ), "Failed to create keycloak pool"
                    async with cls._keycloak_pool.acquire() as conn:
                        await conn.execute("SELECT 1")

                print("Successfully connected to databases")
                return cls._instance

            except (ConnectionError, asyncpg.PostgresError) as e:
                last_error = e
                retries += 1
                if retries < cls._max_retries:
                    print(f"Database connection attempt {retries} failed: {str(e)}")
                    print(f"Retrying in {cls._retry_delay} seconds...")
                    await asyncio.sleep(cls._retry_delay)
                    cls._retry_delay *= 2  # Exponential backoff
                continue
            except Exception as e:
                print(f"Unexpected error during database initialization: {str(e)}")
                raise

        # If we get here, all retries failed
        print(f"Failed to connect to database after {cls._max_retries} attempts")
        print(f"Last error: {str(last_error)}")
        raise ConnectionError(
            f"Could not establish database connection: {str(last_error)}"
        )

    # Context managers for connections
    @asynccontextmanager
    async def praxis_connection(self):
        if self._pool is None:
            raise RuntimeError(
                "Database pool not initialized. Call initialize() first."
            )
        async with self._pool.acquire() as connection:
            yield connection

    @asynccontextmanager
    async def keycloak_connection(self):
        if self._keycloak_pool is None:
            raise RuntimeError(
                "Database pool not initialized. Call initialize() first."
            )
        async with self._keycloak_pool.acquire() as connection:
            yield connection

    # Protocol management methods
    async def register_protocol(
        self, protocol_name: str, user_id: str, **kwargs
    ) -> int:  # TODO: change to UUID
        async with self.praxis_connection() as conn:
            protocol_id = await conn.fetchval(
                """
                INSERT INTO protocols_metadata
                (protocol_name, user_id, status, data_directory, database_file, parameters, required_assets)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                RETURNING protocol_id
            """,
                protocol_name,
                user_id,
                "initializing",
                kwargs.get("data_directory"),
                kwargs.get("database_file"),
                json.dumps(kwargs.get("parameters", {})),
                json.dumps(kwargs.get("assets", {})),
            )
            if protocol_id is None:
                raise ValueError("Failed to create protocol: no protocol_id returned")
            return int(protocol_id)

    async def get_protocol(self, protocol_name: str) -> Optional[Dict]:
        async with self.praxis_connection() as conn:
            record = await conn.fetchrow(
                """
                SELECT p.*, k.username, k.email, k.first_name, k.last_name
                FROM protocols_metadata p
                LEFT JOIN keycloak_users k ON p.user_id = k.id
                WHERE p.protocol_name = $1
            """,
                protocol_name,
            )

            if record:
                return {
                    "protocol_id": record["protocol_id"],
                    "protocol_name": record["protocol_name"],
                    "start_time": record["start_time"],
                    "end_time": record["end_time"],
                    "status": record["status"],
                    "user": {
                        "id": record["user_id"],
                        "username": record["username"],
                        "email": record["email"],
                        "first_name": record["first_name"],
                        "last_name": record["last_name"],
                    },
                    "data_directory": record["data_directory"],
                    "database_file": record["database_file"],
                    "parameters": json.loads(record["parameters"]),
                    "assets": json.loads(record["assets"]),
                }
            return None

    async def update_protocol_status(self, protocol_name: str, status: str):
        """Update the status of a protocol and set end_time if completed."""
        async with self.praxis_connection() as conn:
            await conn.execute(
                """
                UPDATE protocols_metadata
                SET status = $1,
                    end_time = CASE
                        WHEN $1 IN ('completed', 'failed', 'cancelled')
                        THEN CURRENT_TIMESTAMP
                        ELSE end_time
                    END
                WHERE protocol_name = $2
            """,
                status,
                protocol_name,
            )

    async def list_protocols(self, status: Optional[str] = None) -> List[Dict]:
        """List all protocols, optionally filtered by status."""
        async with self.praxis_connection() as conn:
            query = """
                SELECT
                    p.*,
                    k.username,
                    k.email,
                    k.first_name,
                    k.last_name
                FROM protocols_metadata p
                LEFT JOIN keycloak_users k ON p.user_id = k.id
            """
            params = []
            if status:
                query += " WHERE p.status = $1"
                params.append(status)

            records = await conn.fetch(query, *params)
            return [
                {
                    "protocol_id": r["protocol_id"],
                    "protocol_name": r["protocol_name"],
                    "start_time": r["start_time"],
                    "end_time": r["end_time"],
                    "status": r["status"],
                    "user": {
                        "id": r["user_id"],
                        "username": r["username"],
                        "email": r["email"],
                        "first_name": r["first_name"],
                        "last_name": r["last_name"],
                    },
                    "data_directory": r["data_directory"],
                    "database_file": r["database_file"],
                    "parameters": json.loads(r["parameters"]),
                    "assets": json.loads(r["assets"]),
                }
                for r in records
            ]

    async def store_substep_timing(
        self,
        func_hash: str,
        func_name: str,
        duration: float,
        caller_name: str,
        task_id: str,
        protocol_name: str,
    ):
        """Store timing information for a protocol substep."""
        async with self.praxis_connection() as conn:
            await conn.execute(
                """
                INSERT INTO substep_timings
                (func_hash, func_name, duration, caller_name, task_id, protocol_name)
                VALUES ($1, $2, $3, $4, $5, $6)
            """,
                func_hash,
                func_name,
                duration,
                caller_name,
                task_id,
                protocol_name,
            )

    async def get_protocol_timing(self, protocol_name: str) -> List[Dict]:
        """Get timing information for a protocol."""
        async with self.praxis_connection() as conn:
            records = await conn.fetch(
                """
                SELECT * FROM substep_timings
                WHERE protocol_name = $1
                ORDER BY timestamp
            """,
                protocol_name,
            )
            return [dict(r) for r in records]

    async def export_protocol_data(self, protocol_name: str, backup_path: str) -> None:
        """Export all data related to a specific protocol to a SQLite database file."""
        try:
            async with self.praxis_connection() as conn:
                # Get protocol metadata
                protocol_data = await conn.fetch(
                    """
                    SELECT *
                    FROM protocols_metadata
                    WHERE protocol_name = $1
                """,
                    protocol_name,
                )

                # Get protocol timing data
                timing_data = await conn.fetch(
                    """
                    SELECT *
                    FROM substep_timings
                    WHERE protocol_name = $1
                """,
                    protocol_name,
                )

                # Get asset usage data
                asset_data = await conn.fetch(
                    """
                    SELECT a.*
                    FROM assets a
                    JOIN protocol_asset_usage pau ON a.asset_id = pau.asset_id
                    WHERE pau.protocol_name = $1
                """,
                    protocol_name,
                )

                # Create SQLite backup
                import sqlite3
                import aiosqlite

                async with aiosqlite.connect(backup_path) as sqlite_conn:
                    # Create tables
                    await sqlite_conn.execute(
                        """
                        CREATE TABLE IF NOT EXISTS protocol_metadata (
                            protocol_id INTEGER PRIMARY KEY,
                            protocol_name TEXT,
                            user_id TEXT,
                            start_time TIMESTAMP,
                            end_time TIMESTAMP,
                            status TEXT,
                            data_directory TEXT,
                            database_file TEXT,
                            parameters JSON,
                            required_assets JSON
                        )
                    """
                    )

                    await sqlite_conn.execute(
                        """
                        CREATE TABLE IF NOT EXISTS substep_timings (
                            timing_id INTEGER PRIMARY KEY,
                            protocol_name TEXT,
                            func_hash TEXT,
                            func_name TEXT,
                            duration FLOAT,
                            caller_name TEXT,
                            task_id TEXT,
                            timestamp TIMESTAMP
                        )
                    """
                    )

                    await sqlite_conn.execute(
                        """
                        CREATE TABLE IF NOT EXISTS assets (
                            asset_id INTEGER PRIMARY KEY,
                            name TEXT UNIQUE,
                            type TEXT,
                            metadata JSON,
                            plr_serialized JSON,
                            is_available BOOLEAN,
                            locked_by_protocol TEXT,
                            locked_by_task TEXT,
                            lock_acquired_at TIMESTAMP,
                            lock_expires_at TIMESTAMP
                        )
                    """
                    )

                    # Insert data
                    await sqlite_conn.executemany(
                        "INSERT INTO protocol_metadata VALUES (?,?,?,?,?,?,?,?,?,?)",
                        [
                            (
                                p["protocol_id"],
                                p["protocol_name"],
                                p["user_id"],
                                p["start_time"],
                                p["end_time"],
                                p["status"],
                                p["data_directory"],
                                p["database_file"],
                                json.dumps(p["parameters"]),
                                json.dumps(p["required_assets"]),
                            )
                            for p in protocol_data
                        ],
                    )

                    await sqlite_conn.executemany(
                        "INSERT INTO substep_timings VALUES (?,?,?,?,?,?,?,?)",
                        [
                            (
                                t["timing_id"],
                                t["protocol_name"],
                                t["func_hash"],
                                t["func_name"],
                                t["duration"],
                                t["caller_name"],
                                t["task_id"],
                                t["timestamp"],
                            )
                            for t in timing_data
                        ],
                    )

                    await sqlite_conn.executemany(
                        "INSERT INTO assets VALUES (?,?,?,?,?,?,?,?,?,?)",
                        [
                            (
                                a["asset_id"],
                                a["name"],
                                a["type"],
                                json.dumps(a["metadata"]),
                                json.dumps(a["plr_serialized"]),
                                a["is_available"],
                                a["locked_by_protocol"],
                                a["locked_by_task"],
                                a["lock_acquired_at"],
                                a["lock_expires_at"],
                            )
                            for a in asset_data
                        ],
                    )

                    await sqlite_conn.commit()

        except Exception as e:
            raise RuntimeError(f"Failed to export protocol data: {str(e)}")

    # Asset management methods
    async def add_asset(
        self, name: str, asset_type: str, metadata: dict, plr_serialized: dict
    ) -> int:
        """Add an asset to the database with validation."""
        if not name or not asset_type:
            raise ValueError("Asset name and type are required")

        async with self.praxis_connection() as conn:
            result = await conn.fetchval(
                """
                INSERT INTO assets (name, type, metadata, plr_serialized)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (name)
                DO UPDATE SET
                    type = EXCLUDED.type,
                    metadata = EXCLUDED.metadata,
                    plr_serialized = EXCLUDED.plr_serialized
                RETURNING asset_id
            """,
                name,
                asset_type,
                json.dumps(metadata),
                json.dumps(plr_serialized),
            )
            if result is None:
                raise ValueError("Failed to add asset: no asset_id returned")
            return int(result)

    async def get_asset(self, name: str) -> Optional[Dict]:
        async with self.praxis_connection() as conn:
            record = await conn.fetchrow("SELECT * FROM assets WHERE name = $1", name)
            if record:
                return {
                    "asset_id": record["asset_id"],
                    "name": record["name"],
                    "type": record["type"],
                    "metadata": json.loads(record["metadata"]),
                    "plr_serialized": json.loads(record["plr_serialized"]),
                    "is_available": record["is_available"],
                    "locked_by_protocol": record["locked_by_protocol"],
                    "locked_by_task": record["locked_by_task"],
                    "lock_acquired_at": record["lock_acquired_at"],
                    "lock_expires_at": record["lock_expires_at"],
                }
            return None

    async def instantiate_asset(self, name: str) -> Union[Resource, Machine]:
        """Retrieves and instantiates an asset from the database."""
        async with self.praxis_connection() as conn:
            record = await conn.fetchrow(
                """
                SELECT type, plr_serialized
                FROM assets
                WHERE name = $1
            """,
                name,
            )

            if not record:
                raise ValueError(f"Asset {name} not found")

            return self.deserialize_asset(record["plr_serialized"])

    async def get_all_machines(self) -> dict[str, Machine]:
        """Get all machines from the database."""
        async with self.praxis_connection() as conn:
            records = await conn.fetch(
                """
                SELECT name, plr_serialized
                FROM assets
                WHERE type LIKE '%Machine%'
            """
            )
            return {
                record["name"]: self.deserialize_asset(record["plr_serialized"])  # type: ignore
                for record in records
            }

    async def get_all_resources(self) -> dict[str, Resource]:
        """Get all resources from the database."""
        async with self.praxis_connection() as conn:
            records = await conn.fetch(
                """
                SELECT name, plr_serialized
                FROM assets
                WHERE type LIKE '%Resource%'
            """
            )
            return {
                record["name"]: self.deserialize_asset(record["plr_serialized"])  # type: ignore
                for record in records
            }

    async def get_resources(self, resource_ids: list[str]) -> dict[str, Resource]:
        """Get specific resources by their IDs."""
        async with self.praxis_connection() as conn:
            records = await conn.fetch(
                """
                SELECT name, plr_serialized
                FROM assets
                WHERE name = ANY($1) AND type LIKE '%Resource%'
            """,
                resource_ids,
            )
            return {
                record["name"]: self.deserialize_asset(record["plr_serialized"])  # type: ignore
                for record in records
            }

    async def get_machines(self, machine_ids: list[str]) -> dict[str, Machine]:
        """Get specific machines by their IDs."""
        async with self.praxis_connection() as conn:
            records = await conn.fetch(
                """
                SELECT name, plr_serialized
                FROM assets
                WHERE name = ANY($1) AND type LIKE '%Machine%'
            """,
                machine_ids,
            )
            return {
                record["name"]: self.deserialize_asset(record["plr_serialized"])  # type: ignore
                for record in records
            }

    async def add_machine(self, machine: Machine) -> int:
        """Add a machine to the database."""
        if not self.validate_asset(machine) or not isinstance(machine, Machine):
            raise ValueError("Asset must be an instance of Machine")
        return await self.add_asset(
            name=self.get_asset_id(machine),
            asset_type=machine.__class__.__name__,
            metadata={},
            plr_serialized=self.serialize_asset(machine),
        )

    async def add_resource(self, resource: Resource) -> int:
        """Add a resource to the database."""
        if not self.validate_asset(resource) or not isinstance(resource, Resource):
            raise ValueError("Asset must be an instance of Resource")
        return await self.add_asset(
            name=self.get_asset_id(resource),
            asset_type=resource.__class__.__name__,
            metadata={},
            plr_serialized=self.serialize_asset(resource),
        )

    # User management methods
    async def get_all_users(self) -> Dict[str, Dict[str, Any]]:
        """Get all users as a dictionary keyed by username."""
        async with self.keycloak_connection() as conn:
            records = await conn.fetch(
                """
                SELECT
                    id,
                    username,
                    email,
                    first_name,
                    last_name,
                    enabled,
                    roles,
                    phone_number
                FROM keycloak_users
                WHERE enabled = true
                ORDER BY username
            """
            )
            return {
                record["username"]: {
                    "id": record["id"],
                    "username": record["username"],
                    "email": record["email"],
                    "first_name": record["first_name"],
                    "last_name": record["last_name"],
                    "roles": record["roles"],
                    "phone_number": record["phone_number"],
                    "is_active": record["enabled"],
                }
                for record in records
            }

    async def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user information by username."""
        async with self.keycloak_connection() as conn:
            record = await conn.fetchrow(
                """
                SELECT
                    id,
                    username,
                    email,
                    first_name,
                    last_name,
                    enabled,
                    roles,
                    phone_number
                FROM keycloak_users
                WHERE username = $1
            """,
                username,
            )

            if record:
                return {
                    "id": record["id"],
                    "username": record["username"],
                    "email": record["email"],
                    "first_name": record["first_name"],
                    "last_name": record["last_name"],
                    "roles": record["roles"],
                    "phone_number": record["phone_number"],
                    "is_active": record["enabled"],
                }
            return None

    async def list_users(self) -> List[str]:
        """Get a list of all usernames."""
        async with self.keycloak_connection() as conn:
            records = await conn.fetch(
                """
                SELECT username
                FROM keycloak_users
                WHERE enabled = true
                ORDER BY username
            """
            )
            return [record["username"] for record in records]

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information by UUID."""
        async with self.keycloak_connection() as conn:
            record = await conn.fetchrow(
                """
                SELECT
                    id,
                    username,
                    email,
                    first_name,
                    last_name,
                    enabled,
                    roles,
                    phone_number
                FROM keycloak_users
                WHERE id = $1
            """,
                user_id,
            )

            if record:
                return {
                    "id": record["id"],
                    "username": record["username"],
                    "email": record["email"],
                    "first_name": record["first_name"],
                    "last_name": record["last_name"],
                    "roles": record["roles"],
                    "phone_number": record["phone_number"],
                    "is_active": record["enabled"],
                }
            return None

    async def search_users(self, query: str) -> List[Dict[str, Any]]:
        """Search users by username, email, or name."""
        async with self.keycloak_connection() as conn:
            records = await conn.fetch(
                """
                SELECT
                    id,
                    username,
                    email,
                    first_name,
                    last_name,
                    enabled,
                    roles,
                    phone_number
                FROM keycloak_users
                WHERE
                    enabled = true
                    AND (
                        username ILIKE $1
                        OR email ILIKE $1
                        OR first_name ILIKE $1
                        OR last_name ILIKE $1
                    )
                ORDER BY username
            """,
                f"%{query}%",
            )

            return [
                {
                    "id": r["id"],
                    "username": r["username"],
                    "email": r["email"],
                    "first_name": r["first_name"],
                    "last_name": r["last_name"],
                    "roles": r["roles"],
                    "phone_number": r["phone_number"],
                    "is_active": r["enabled"],
                }
                for r in records
            ]

    # Generic data methods
    async def execute_query(self, query: str, *args):
        async with self.praxis_connection() as conn:
            return await conn.execute(query, *args)

    async def fetch_all(self, query: str, *args) -> List[Dict]:
        async with self.praxis_connection() as conn:
            records = await conn.fetch(query, *args)
            return [dict(r) for r in records]

    async def fetch_one(self, query: str, *args) -> Optional[Dict]:
        async with self.praxis_connection() as conn:
            record = await conn.fetchrow(query, *args)
            return dict(record) if record else None

    async def fetch_val(self, query: str, *args):
        async with self.praxis_connection() as conn:
            return await conn.fetchval(query, *args)

    # DataFrame operations
    async def query_to_df(self, query: str, *args) -> pd.DataFrame:
        async with self.praxis_connection() as conn:
            records = await conn.fetch(query, *args)
            return pd.DataFrame(records)

    # Asset locking methods
    async def acquire_lock(
        self, asset_name: str, protocol_name: str, task_id: str, lock_timeout: int = 60
    ) -> bool:
        async with self.praxis_connection() as conn:
            async with conn.transaction():
                result = await conn.fetchrow(
                    """
                    UPDATE assets
                    SET is_available = false,
                        locked_by_protocol = $1,
                        locked_by_task = $2,
                        lock_acquired_at = CURRENT_TIMESTAMP,
                        lock_expires_at = CURRENT_TIMESTAMP + interval '1 second' * $3
                    WHERE name = $4
                        AND (is_available = true OR lock_expires_at < CURRENT_TIMESTAMP)
                    RETURNING asset_id
                """,
                    protocol_name,
                    task_id,
                    lock_timeout,
                    asset_name,
                )
                return result is not None

    async def release_lock(self, asset_name: str, protocol_name: str, task_id: str):
        async with self.praxis_connection() as conn:
            await conn.execute(
                """
                UPDATE assets
                SET is_available = true,
                    locked_by_protocol = null,
                    locked_by_task = null,
                    lock_acquired_at = null,
                    lock_expires_at = null
                WHERE name = $1
                    AND locked_by_protocol = $2
                    AND locked_by_task = $3
            """,
                asset_name,
                protocol_name,
                task_id,
            )

    # Cleanup method
    async def close(self):
        if self._pool:
            await self._pool.close()
        if self._keycloak_pool:
            await self._keycloak_pool.close()

    # Asset utility methods
    def serialize_asset(self, asset: Union[Resource, Machine]) -> Dict[str, Any]:
        """Serialize an asset to a dictionary."""
        if isinstance(asset, (Resource, Machine)):
            serialized = asset.serialize()
            # Add type information for proper deserialization
            serialized["type"] = asset.__class__.__name__
            return serialized
        raise ValueError("Asset must be an instance of Resource or Machine")

    def deserialize_asset(self, data: Dict[str, Any]) -> Union[Resource, Machine]:
        """Deserialize an asset from a dictionary."""
        resource_type = data.get("type")
        if not resource_type:
            raise ValueError("Asset type is missing")

        # Try to find the class in Machine first, then Resource
        machine_cls = find_subclass(str(Machine), resource_type)
        if machine_cls is not None:
            return cast(Union[Resource, Machine], machine_cls.deserialize(data))

        resource_cls = find_subclass(str(Resource), resource_type)
        if resource_cls is not None:
            return cast(Union[Resource, Machine], resource_cls.deserialize(data))

        raise ValueError(f"Unknown asset type: {resource_type}")

    def get_asset_id(self, asset: Union[Resource, Machine]) -> str:
        """Extract a unique identifier for the asset."""
        if isinstance(asset, Resource):
            return asset.name
        elif isinstance(asset, Machine):
            return cast(
                str,
                getattr(asset, "name", None)
                or getattr(asset, "device_id", None)
                or getattr(asset, "serial_number", None)
                or getattr(asset, "port", None),
            )
        else:
            raise ValueError("Asset must be an instance of Resource or Machine")

    def validate_asset(self, asset: Any) -> bool:
        """Validate that an object is a valid asset."""
        return isinstance(asset, (Resource, Machine))

    async def discover_protocols(self, directories: list[str]) -> list[dict]:
        """Discover available protocols in the given directories."""
        protocols = []

        for directory in directories:
            path = Path(directory)
            if not path.exists():
                continue

            for file in path.rglob("*.py"):
                try:
                    # Skip __init__.py files
                    if file.name == "__init__.py":
                        continue

                    spec = importlib.util.spec_from_file_location(file.stem, str(file))
                    if spec is None or spec.loader is None:
                        continue

                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for item_name in dir(module):
                        item = getattr(module, item_name)
                        if (
                            isinstance(item, type)
                            and hasattr(
                                item, "execute"
                            )  # Check for ProtocolInterface methods
                            and hasattr(item, "initialize")
                            and hasattr(item, "required_assets")
                            and not item.__name__.startswith("_")
                            and not item.__name__ == "Protocol"
                        ):

                            # Get WorkcellAssets and ProtocolParameters if they exist
                            assets = getattr(module, "required_assets", None)
                            parameters = getattr(module, "baseline_parameters", None)

                            protocols.append(
                                {
                                    "name": item.__name__,
                                    "path": str(file),
                                    "module": module.__name__,
                                    "description": item.__doc__
                                    or "No description available",
                                    "has_assets": assets is not None,
                                    "has_parameters": parameters is not None,
                                }
                            )

                except Exception as e:
                    print(f"Error loading protocol from {file}: {e}")

        return protocols

    async def get_protocol_details(
        self, protocol_path: str
    ) -> Optional[Dict[str, Any]]:
        """Get details about a protocol including its assets and parameters."""
        try:
            # Import protocol module
            protocol_module = await self.import_protocol_module(protocol_path)
            if not protocol_module:
                return None

            logger.info(f"=== Protocol Details Request ===")
            logger.info(f"Protocol path: {protocol_path}")
            logger.info(f"Protocol module attributes: {dir(protocol_module)}")

            # Get baseline parameters and assets
            baseline_parameters = getattr(protocol_module, "baseline_parameters", {})
            required_assets = getattr(protocol_module, "required_assets", {})

            # Log raw data for debugging
            logger.info(f"Protocol module baseline_parameters: {baseline_parameters}")
            logger.info(f"Protocol module required_assets: {required_assets}")

            # Handle serialization if needed
            if isinstance(baseline_parameters, ProtocolParameters):
                baseline_parameters = baseline_parameters.serialize()
            if isinstance(required_assets, WorkcellAssetsInterface):
                required_assets = required_assets.serialize()

            # Ensure we have dictionaries
            if not isinstance(baseline_parameters, dict):
                baseline_parameters = {}
            if not isinstance(required_assets, dict):
                required_assets = {}

            # Convert parameters to frontend format
            parameters = {}
            for name, config in baseline_parameters.items():
                param_type = config.get("type", str)
                param_type_name = (
                    param_type.__name__
                    if hasattr(param_type, "__name__")
                    else str(param_type)
                )

                parameters[name] = {
                    "type": self._map_python_type_to_frontend(param_type_name),
                    "required": config.get("required", False),
                    "default": config.get("default"),
                    "description": config.get("description", ""),
                    "constraints": config.get("constraints", {}),
                }

            # Convert assets to list format
            assets = []
            for name, config in required_assets.items():
                asset_type = config.get("type", str)
                assets.append(
                    {
                        "name": name,
                        "type": (
                            asset_type.__name__
                            if hasattr(asset_type, "__name__")
                            else str(asset_type)
                        ),
                        "description": config.get("description", ""),
                        "required": config.get("required", True),
                    }
                )

            details: Dict[str, Any] = {
                "name": getattr(protocol_module, "__name__", ""),
                "path": protocol_path,
                "description": getattr(
                    protocol_module, "__doc__", "No documentation found"
                ),
                "parameters": parameters,  # Using frontend-expected key name
                "assets": assets,
                "has_assets": bool(assets),
                "has_parameters": bool(parameters),
                "requires_config": not (bool(parameters) or bool(assets)),
            }

            logger.info(f"Returning serialized details: {details}")
            return details

        except Exception as e:
            logger.error(f"Error getting protocol details: {e}", exc_info=True)
            return None

    def _map_python_type_to_frontend(self, python_type: str) -> str:
        """Map Python type names to frontend type names."""
        type_mapping = {
            "str": "string",
            "int": "number",
            "float": "number",
            "bool": "boolean",
            "list": "enum",  # Assuming lists are used for enum choices
        }
        return type_mapping.get(python_type, "string")

    async def import_protocol_module(self, protocol_path: str) -> Optional[Any]:
        """Import a protocol module from its file path."""
        try:
            logger.info("=== Protocol Details Request ===")
            logger.info(f"Raw protocol path: {protocol_path}")

            # Get absolute path relative to project root
            project_root = str(Path(__file__).parent.parent.parent)
            logger.info(f"Project root: {project_root}")

            full_path = os.path.join(project_root, protocol_path)
            full_path = os.path.abspath(full_path)
            logger.info(f"Trying path: {full_path}")

            if os.path.exists(full_path):
                logger.info(f"Found protocol at: {full_path}")
                spec = importlib.util.spec_from_file_location(
                    Path(protocol_path).stem, full_path
                )
                if spec is None or spec.loader is None:
                    logger.error(f"Could not create spec for {full_path}")
                    return None

                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module

            else:
                logger.error(f"Protocol file not found at {full_path}")
                return None

        except Exception as e:
            logger.error(f"Error importing protocol module: {e}", exc_info=True)
            return None

    async def update_asset_state(self, asset_name: str, state: Dict[str, Any]) -> None:
        """Update the state of an asset in the database."""
        async with self.praxis_connection() as conn:
            await conn.execute(
                """
                UPDATE assets
                SET metadata = jsonb_set(metadata, '{state}', $1::jsonb)
                WHERE name = $2
                """,
                json.dumps(state),
                asset_name,
            )

    async def get_asset_state(self, asset_name: str) -> Optional[Dict[str, Any]]:
        """Get the current state of an asset from the database."""
        async with self.praxis_connection() as conn:
            result = await conn.fetchval(
                """
                SELECT metadata->'state'
                FROM assets
                WHERE name = $1
                """,
                asset_name,
            )
            return json.loads(result) if result else None

    async def is_asset_locked(self, asset_name: str) -> bool:
        """Check if an asset is currently locked."""
        async with self.praxis_connection() as conn:
            result = await conn.fetchval(
                """
                SELECT NOT is_available AND lock_expires_at > CURRENT_TIMESTAMP
                FROM assets
                WHERE name = $1
                """,
                asset_name,
            )
            return bool(result)


# Global instance
db = DatabaseManager()
