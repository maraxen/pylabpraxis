import aiosqlite
import json
import datetime
import os
import asyncio
import redis
import time
from typing import Optional, List, Dict
from praxis.utils import AsyncAssetDatabase
from praxis.configure import PraxisConfiguration


async def initialize_registry(config: str | PraxisConfiguration = "config.ini"):
    """
    Asynchronously creates and initializes a Registry instance.

    Args:
        config_file: The path to the configuration file.
    """
    if isinstance(config, str):
        config = PraxisConfiguration(config)
    if not isinstance(config, PraxisConfiguration):
        raise ValueError("Invalid configuration object.")

    db_file = config.registry_db
    data_dir = config.data_directory

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    conn = await aiosqlite.connect(db_file)  # Connect asynchronously

    redis_client = redis.Redis(
        host=config.redis_host, port=config.redis_port, db=config.redis_db
    )

    registry = Registry(db_file, data_dir, conn, redis_client)
    await registry._create_tables()  # Now an async method

    return registry


class Registry:
    """
    A class that provides a registry for storing and managing protocol metadata and
    asset usage.

    Attributes:
        db_file: The path to the SQLite database file.
        data_dir: The path to the directory where data files are stored.
        conn: An aiosqlite.Connection object.
        redis_client: A redis.Redis object.

    Methods:
        _create_tables: Asynchronously creates the necessary tables in the database.
        register_protocol: Asynchronously registers a new protocol.
        update_protocol_status: Asynchronously updates the status of a protocol.
        get_protocol_metadata: Asynchronously retrieves metadata for a protocol.
        list_protocols: Asynchronously lists all protocols.
        store_substep_timing: Asynchronously stores the timing of a substep.
        set_next_plate_reader_use: Asynchronously sets the estimated time for the next plate reader
          use.
        get_next_plate_reader_use: Asynchronously retrieves the estimated time for the next plate
          reader use.
        add_asset: Asynchronously adds a new asset to the registry.
        is_asset_available: Asynchronously checks if a asset is available.
        acquire_lock: Asynchronously acquires a lock on a asset.
        release_lock: Asynchronously releases a lock on a asset.
        asset_exists: Asynchronously checks if a asset exists in the registry.
        close: Asynchronously closes the connection to the database.
    """

    def __init__(
        self,
        db_file: str,
        data_dir: str,
        conn: aiosqlite.Connection,
        redis_client: redis.Redis,
    ):
        self.db_file = db_file
        self.data_dir = data_dir
        self.conn = conn
        self.redis_client = redis_client

    async def _create_tables(self):
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS protocols_metadata (
                    protocol_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    protocol_name TEXT UNIQUE NOT NULL,
                    start_time DATETIME,
                    end_time DATETIME,
                    user TEXT,
                    status TEXT,
                    data_directory TEXT,
                    database_file TEXT,
                    parameters TEXT,
                    estimated_plate_reader_time DATETIME,
                    UNIQUE(protocol_name)
                )
            """
            )
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS substep_timings (
                    timing_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    protocol_name TEXT,
                    func_hash TEXT,
                    func_name TEXT,
                    duration REAL,
                    caller_name TEXT,
                    task_id TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (protocol_name) REFERENCES protocols_metadata(protocol_name)
                )
            """
            )
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS plate_reader_usage (
                    usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    protocol_name TEXT,
                    plate_name TEXT,
                    measurement_type TEXT,
                    wells TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (protocol_name) REFERENCES protocols_metadata(protocol_name)
                )
            """
            )
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS assets (
                    asset_int_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_id TEXT UNIQUE NOT NULL,
                    is_available BOOLEAN DEFAULT 1,
                    locked_by_protocol TEXT,
                    locked_by_task TEXT,
                    lock_acquired_at DATETIME,
                    lock_expires_at DATETIME,
                    FOREIGN KEY (locked_by_protocol) REFERENCES protocols_metadata(protocol_name)
                )
            """
            )
            await self.conn.commit()

    async def register_protocol(
        self,
        protocol_name: str,
        user: str,
        data_directory: str,
        database_file: str,
        parameters: dict,
    ) -> int:
        """
        Asynchronously registers a new protocol.

        Args:
          protocol_name: The name of the protocol.
          user: The user who is registering the protocol.
          data_directory: The directory where data files are stored.
          database_file: The path to the database file.
          parameters: A dictionary of parameters for the protocol.

        Returns:
          The protocol_id of the newly registered protocol.
        """
        start_time = datetime.datetime.now(datetime.timezone.utc)
        status = "initializing"
        parameters_json = json.dumps(parameters)
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
              INSERT INTO protocols_metadata (
                  protocol_name, start_time, user, status, data_directory, database_file, parameters
              ) VALUES (?, ?, ?, ?, ?, ?, ?)
          """,
                (
                    protocol_name,
                    start_time,
                    user,
                    status,
                    data_directory,
                    database_file,
                    parameters_json,
                ),
            )
            await self.conn.commit()
            if cursor.lastrowid is None:
                raise RuntimeError("Failed to get protocol_id after insert")
            return cursor.lastrowid  # Return the protocol_id

    async def update_protocol_status(self, protocol_name, status):
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE protocols_metadata SET status = ? WHERE protocol_name = ?",
                (status, protocol_name),
            )
            await self.conn.commit()

    async def get_protocol_metadata(self, protocol_name):
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM protocols_metadata WHERE protocol_name = ?",
                (protocol_name,),
            )
            row = await cursor.fetchone()
            if row:
                metadata = {
                    "protocol_id": row[0],
                    "protocol_name": row[1],
                    "start_time": row[2],
                    "end_time": row[3],
                    "user": row[4],
                    "status": row[5],
                    "data_directory": row[6],
                    "database_file": row[7],
                    "parameters": json.loads(row[8]),
                    "estimated_plate_reader_time": row[9],
                }
                return metadata
            else:
                return None

    async def list_protocols(self, status: Optional[str] = None) -> List[Dict]:
        async with self.conn.cursor() as cursor:
            if status:
                await cursor.execute(
                    "SELECT * FROM protocols_metadata WHERE status = ?", (status,)
                )
            else:
                await cursor.execute("SELECT * FROM protocols_metadata")
            rows = await cursor.fetchall()
            protocols = []
            for row in rows:
                protocols.append(
                    {
                        "protocol_id": row[0],
                        "protocol_name": row[1],
                        "start_time": row[2],
                        "end_time": row[3],
                        "user": row[4],
                        "status": row[5],
                        "data_directory": row[6],
                        "database_file": row[7],
                        "parameters": json.loads(row[8]),
                        "estimated_plate_reader_time": row[9],
                    }
                )
            return protocols

    async def store_substep_timing(
        self, func_hash, func_name, duration, caller_name, task_id, protocol_name
    ):
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO substep_timings (func_hash, func_name, duration, caller_name, task_id, protocol_name)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (func_hash, func_name, duration, caller_name, task_id, protocol_name),
            )
            await self.conn.commit()

    async def set_next_plate_reader_use(self, protocol_name, timestamp):
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE protocols_metadata SET estimated_plate_reader_time = ? WHERE protocol_name = ?",
                (timestamp, protocol_name),
            )
            await self.conn.commit()

    async def get_next_plate_reader_use(self, protocol_name):
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT estimated_plate_reader_time FROM protocols_metadata WHERE protocol_name = ?",
                (protocol_name,),
            )
            row = await cursor.fetchone()
            if row and row[0]:
                return datetime.datetime.fromisoformat(
                    row[0]
                )  # Parse ISO format string
            else:
                return None

    async def add_asset(self, asset_id: str):
        """Adds a new asset to the registry."""
        async with self.conn.cursor() as cursor:
            try:
                await cursor.execute(
                    "INSERT INTO assets (asset_id) VALUES (?)", (asset_id,)
                )
                await self.conn.commit()
            except aiosqlite.IntegrityError:
                print(f"Resource '{asset_id}' already exists.")

    async def is_asset_available(self, asset_id: str) -> bool:
        """Checks if a asset is currently available."""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT is_available FROM assets WHERE asset_id = ?", (asset_id,)
            )
            row = await cursor.fetchone()
            if row:
                return bool(row[0])  # Convert from integer (SQLite) to boolean
            else:
                raise ValueError(f"Resource '{asset_id}' not found.")

    async def acquire_lock(
        self,
        asset_id: str,
        protocol_name: str,
        task_id: str,
        lock_timeout: int = 60,
        acquire_timeout: Optional[int] = None,
    ) -> bool:
        """
        Acquires a lock on a asset using both Redis and the database.

        Args:
            asset_id: The name of the asset to lock.
            protocol_name: The name of the protocol acquiring the lock.
            task_id: The ID of the task acquiring the lock.
            lock_timeout: The duration of the lock in seconds.
            acquire_timeout: The maximum time to wait to acquire the lock (in seconds).

        Returns:
            True if the lock was acquired, False otherwise.
        """
        lock_name = f"lock:{asset_id}"
        identifier = f"{protocol_name}:{task_id}"

        # Check if the asset exists
        if not await self.asset_exists(asset_id):
            await self.add_asset(asset_id)  # Add the asset if it doesn't exist

        start_time = time.time()
        while True:
            try:
                async with self.conn.cursor() as cursor:
                    await cursor.execute(
                        "BEGIN EXCLUSIVE TRANSACTION"
                    )  # Use an exclusive transaction

                    # Check if the asset is available or if the lock has expired
                    await cursor.execute(
                        """
                        SELECT is_available, lock_expires_at
                        FROM assets
                        WHERE asset_id = ?
                    """,
                        (asset_id,),
                    )
                    row = await cursor.fetchone()
                    if not row:
                        raise ValueError(f"Resource '{asset_id}' not found.")

                    is_available, lock_expires_at_str = row

                    if is_available or (
                        lock_expires_at_str
                        and datetime.datetime.fromisoformat(lock_expires_at_str)
                        < datetime.datetime.now(datetime.timezone.utc)
                    ):
                        # Acquire the lock using Redis
                        if self.redis_client.set(
                            lock_name, identifier, ex=lock_timeout, nx=True
                        ):
                            lock_expires_at = datetime.datetime.now(
                                datetime.timezone.utc
                            ) + datetime.timedelta(seconds=lock_timeout)
                            await cursor.execute(
                                """
                                UPDATE assets
                                SET is_available = 0, locked_by_protocol = ?, locked_by_task = ?, lock_acquired_at = ?, lock_expires_at = ?
                                WHERE asset_id = ?
                            """,
                                (
                                    protocol_name,
                                    task_id,
                                    datetime.datetime.now(datetime.timezone.utc),
                                    lock_expires_at,
                                    asset_id,
                                ),
                            )
                            await self.conn.commit()
                            return True
                        else:
                            await self.conn.commit()  # Release the transaction lock
                            if acquire_timeout is not None and (
                                time.time() - start_time > acquire_timeout
                            ):
                                return False  # Timeout
                            else:
                                await asyncio.sleep(
                                    0.1
                                )  # Wait for a short time before retrying
                    else:
                        await self.conn.commit()  # Release the transaction lock
                        if acquire_timeout is not None and (
                            time.time() - start_time > acquire_timeout
                        ):
                            return False  # Timeout
                        else:
                            await asyncio.sleep(
                                1
                            )  # Wait for a short time before retrying

            except aiosqlite.OperationalError:
                # Another process has an exclusive lock, wait and try again
                await self.conn.rollback()  # Roll back the transaction
                if acquire_timeout is not None and (
                    time.time() - start_time > acquire_timeout
                ):
                    return False  # Timeout
                else:
                    await asyncio.sleep(0.1)  # Wait for a short time before retrying

            except Exception as e:
                await self.conn.rollback()
                raise e

    async def release_lock(self, asset_id: str, protocol_name: str, task_id: str):
        """Releases a lock on a asset."""
        lock_name = f"lock:{asset_id}"
        async with self.conn.cursor() as cursor:
            try:
                await cursor.execute("BEGIN EXCLUSIVE TRANSACTION")
                # Verify that the lock is held by the requesting protocol and task
                await cursor.execute(
                    """
                    SELECT 1
                    FROM assets
                    WHERE asset_id = ? AND locked_by_protocol = ? AND locked_by_task = ?
                """,
                    (asset_id, protocol_name, task_id),
                )

                if await cursor.fetchone():
                    # Release the lock in Redis and the database
                    redis_value = await self.redis_client.get(lock_name)
                    if (
                        redis_value
                        and redis_value.decode("utf-8") == f"{protocol_name}:{task_id}"
                    ):
                        await self.redis_client.delete(lock_name)
                        await cursor.execute(
                            """
                            UPDATE assets
                            SET is_available = 1, locked_by_protocol = NULL, locked_by_task = NULL, lock_acquired_at = NULL, lock_expires_at = NULL
                            WHERE asset_id = ?
                        """,
                            (asset_id,),
                        )
                        await self.conn.commit()
                    else:
                        await self.conn.commit()  # Release the transaction lock
                        raise ValueError(
                            f"Inconsistent lock state for asset '{asset_id}'. Lock held by another protocol or task."
                        )
                else:
                    await self.conn.commit()  # Release the transaction lock
                    raise ValueError(
                        f"Lock on asset '{asset_id}' is not held by protocol '{protocol_name}' and task '{task_id}'."
                    )

            except Exception as e:
                await self.conn.rollback()
                raise e

    async def asset_exists(self, asset_id: str) -> bool:
        """Checks if a asset exists in the registry."""
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT 1 FROM assets WHERE asset_id = ?", (asset_id,))
            return await cursor.fetchone() is not None

    async def close(self):
        await self.conn.close()
