import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from configparser import ConfigParser
from pathlib import Path
from typing import AsyncGenerator
import logging # For logging database setup

# Standard library logger
logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO) # REMOVED: BasicConfig should be called once in main.py

# --- Configuration Loading ---
# Determine the base directory of the project (pylabpraxis)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_FILE_PATH = PROJECT_ROOT / "praxis.ini"

if not CONFIG_FILE_PATH.exists():
    logger.error(f"Configuration file praxis.ini not found at {CONFIG_FILE_PATH}")
    raise FileNotFoundError(
        f"Configuration file praxis.ini not found at {CONFIG_FILE_PATH}"
    )

config_parser = ConfigParser()
config_parser.read(CONFIG_FILE_PATH)

# --- Praxis Database Configuration ---
try:
    praxis_db_user = config_parser.get("database", "user", fallback="user")
    praxis_db_password = config_parser.get("database", "password", fallback="password")
    praxis_db_host = config_parser.get("database", "host", fallback="localhost")
    praxis_db_port = config_parser.get("database", "port", fallback="5432")
    praxis_db_name = config_parser.get("database", "dbname", fallback="praxis_db")

    praxis_db_user = os.getenv("POSTGRES_USER", praxis_db_user)
    praxis_db_password = os.getenv("POSTGRES_PASSWORD", praxis_db_password)
    praxis_db_host = os.getenv("POSTGRES_HOST", praxis_db_host)
    praxis_db_port = os.getenv("POSTGRES_PORT", praxis_db_port)
    praxis_db_name = os.getenv("POSTGRES_DB", praxis_db_name)

    praxis_database_url = (
        f"postgresql+asyncpg://{praxis_db_user}:{praxis_db_password}@"
        f"{praxis_db_host}:{praxis_db_port}/{praxis_db_name}"
    )
    logger.info(f"Praxis Database URL configured: {praxis_database_url.replace(praxis_db_password, '****')}")

except Exception as e:
    logger.error(f"Error reading Praxis database configuration from praxis.ini: {e}")
    praxis_database_url = "postgresql+asyncpg://user:password@localhost:5432/praxis_db"
    logger.warning(f"Falling back to default praxis_database_url: {praxis_database_url.replace('password', '****')}")

# --- Keycloak Database Configuration (for PraxisDBService to use) ---
keycloak_dsn_from_config = None
try:
    if config_parser.has_section("keycloak_database"):
        keycloak_db_user = config_parser.get("keycloak_database", "user", fallback="keycloak_user")
        keycloak_db_password = config_parser.get("keycloak_database", "password", fallback="keycloak_password")
        keycloak_db_host = config_parser.get("keycloak_database", "host", fallback="localhost")
        keycloak_db_port = config_parser.get("keycloak_database", "port", fallback="5433")
        keycloak_db_name = config_parser.get("keycloak_database", "dbname", fallback="keycloak_db")

        keycloak_db_user = os.getenv("KEYCLOAK_DB_USER", keycloak_db_user)
        keycloak_db_password = os.getenv("KEYCLOAK_DB_PASSWORD", keycloak_db_password)
        keycloak_db_host = os.getenv("KEYCLOAK_DB_HOST", keycloak_db_host)
        keycloak_db_port = os.getenv("KEYCLOAK_DB_PORT", keycloak_db_port)
        keycloak_db_name = os.getenv("KEYCLOAK_DB_NAME", keycloak_db_name)

        keycloak_dsn_from_config = (
            f"postgresql://{keycloak_db_user}:{keycloak_db_password}@" # asyncpg uses postgresql://
            f"{keycloak_db_host}:{keycloak_db_port}/{keycloak_db_name}"
        )
        logger.info(f"Keycloak DSN successfully parsed from config for PraxisDBService: {keycloak_dsn_from_config.replace(keycloak_db_password, '****')}")
    else:
        logger.info("No [keycloak_database] section in praxis.ini; Keycloak DSN not available from this module for PraxisDBService.")
except Exception as e:
    logger.error(f"Error reading Keycloak database DSN from praxis.ini: {e}")

KEYCLOAK_DSN_FROM_CONFIG = keycloak_dsn_from_config
PRAXIS_DATABASE_URL = praxis_database_url

# --- SQLAlchemy Async Engine for Praxis Database ---
async_engine = create_async_engine(
    PRAXIS_DATABASE_URL,
    echo=False, # Set to True for debugging SQL queries
)

# --- SQLAlchemy Async Session Factory for Praxis Database ---
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# --- Base for ORM Models ---
Base = declarative_base()

# --- Dependency for FastAPI Routes to Get an Async DB Session ---
async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an asynchronous database session.
    Ensures the session is closed after use.
    """
    async_session = AsyncSessionLocal()
    try:
        yield async_session
    except Exception:
        await async_session.rollback()
        raise
    finally:
        await async_session.close()


# --- Database Initialization Function (for Praxis DB Schema) ---
async def init_praxis_db_schema():
    """
    Initializes the Praxis database schema by creating all tables
    defined by ORM models inheriting from `Base`.
    """
    logger.info("Importing ORM models for Praxis database schema initialization...")
    import praxis.backend.database_models # type: ignore

    logger.info(f"Initializing Praxis database tables at {PRAXIS_DATABASE_URL.replace(praxis_db_password, '****')}...")
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Praxis database tables created successfully (if they didn't already exist).")
    except Exception as e:
        logger.error(f"Error creating Praxis database tables: {e}")
        raise
