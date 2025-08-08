"""Database utility functions and configuration for Praxis."""

import logging
import os
import uuid
from collections.abc import AsyncGenerator
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import UUID, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column
from sqlalchemy.schema import DDLElement
from sqlalchemy.sql import func
from sqlalchemy.sql.compiler import SQLCompiler
from sqlalchemy.sql.selectable import Select

from praxis.backend.utils.uuid import uuid7

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CONFIG_FILE_PATH = PROJECT_ROOT / "praxis.ini"

if not CONFIG_FILE_PATH.exists():
  logger.error("Configuration file praxis.ini not found at %s", CONFIG_FILE_PATH)
  msg = f"Configuration file praxis.ini not found at {CONFIG_FILE_PATH}"
  raise FileNotFoundError(msg)

config_parser = ConfigParser()
config_parser.read(CONFIG_FILE_PATH)

try:
  praxis_db_user = config_parser.get("database", "user", fallback="user")
  praxis_db_password = config_parser.get(
    "database",
    "password",
    fallback="password",
  )  # TODO(mar): Use a secure method for production # noqa: TD003
  praxis_db_host = config_parser.get("database", "host", fallback="localhost")
  praxis_db_port = config_parser.get("database", "port", fallback="5432")
  praxis_db_name = config_parser.get("database", "dbname", fallback="praxis_db")

  praxis_db_user = os.getenv("POSTGRES_USER", praxis_db_user)
  praxis_db_password = os.getenv(
    "POSTGRES_PASSWORD",
    praxis_db_password,
  )  # TODO(mar): Use a secure method for production # noqa: TD003
  praxis_db_host = os.getenv("POSTGRES_HOST", praxis_db_host)
  praxis_db_port = os.getenv("POSTGRES_PORT", praxis_db_port)
  praxis_db_name = os.getenv("POSTGRES_DB", praxis_db_name)

  praxis_database_url = (
    f"postgresql+asyncpg://{praxis_db_user}:{praxis_db_password}@"
    f"{praxis_db_host}:{praxis_db_port}/{praxis_db_name}"
  )
  logger.info(
    "Praxis Database URL configured: %s",
    praxis_database_url.replace(praxis_db_password, "****"),
  )

except Exception:
  logger.exception("Error reading Praxis database configuration from praxis.ini")
  praxis_database_url = "postgresql+asyncpg://user:password@localhost:5432/praxis_db"
  logger.warning(
    "Falling back to default praxis_database_url: %s",
    praxis_database_url.replace("password", "****"),
  )

keycloak_dsn_from_config = None
try:
  if config_parser.has_section("keycloak_database"):
    keycloak_db_user = config_parser.get(
      "keycloak_database",
      "user",
      fallback="keycloak_user",
    )
    keycloak_db_password = config_parser.get(
      "keycloak_database",
      "password",
      fallback="keycloak_password",
    )
    keycloak_db_host = config_parser.get(
      "keycloak_database",
      "host",
      fallback="localhost",
    )
    keycloak_db_port = config_parser.get("keycloak_database", "port", fallback="5433")
    keycloak_db_name = config_parser.get(
      "keycloak_database",
      "dbname",
      fallback="keycloak_db",
    )

    keycloak_db_user = os.getenv("KEYCLOAK_DB_USER", keycloak_db_user)
    keycloak_db_password = os.getenv("KEYCLOAK_DB_PASSWORD", keycloak_db_password)
    keycloak_db_host = os.getenv("KEYCLOAK_DB_HOST", keycloak_db_host)
    keycloak_db_port = os.getenv("KEYCLOAK_DB_PORT", keycloak_db_port)
    keycloak_db_name = os.getenv("KEYCLOAK_DB_NAME", keycloak_db_name)

    keycloak_dsn_from_config = (
      f"postgresql://{keycloak_db_user}:{keycloak_db_password}@"
      f"{keycloak_db_host}:{keycloak_db_port}/{keycloak_db_name}"
    )
    logger.info(
      "Keycloak DSN successfully parsed from config for PraxisDBService: %s",
      keycloak_dsn_from_config.replace(keycloak_db_password, "****"),
    )
  else:
    logger.info(
      "No [keycloak_database] section in praxis.ini; "
      "Keycloak DSN not available from this module for PraxisDBService.",
    )
except Exception:
  logger.exception("Error reading Keycloak database DSN from praxis.ini")

KEYCLOAK_DSN_FROM_CONFIG = keycloak_dsn_from_config
PRAXIS_DATABASE_URL = praxis_database_url

async_engine = create_async_engine(
  PRAXIS_DATABASE_URL,
  echo=False,  # Set to True for debugging SQL queries
)

AsyncSessionLocal = async_sessionmaker(
  async_engine,
  expire_on_commit=False,
  autocommit=False,
  autoflush=False,
)


class Base(MappedAsDataclass, DeclarativeBase):

  """Base class for all ORM models."""

  accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    primary_key=True,
    index=True,
    default_factory=uuid7,
    init=False,
  )

  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    comment="Timestamp when the record was created.",
    init=False,
  )
  updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    init=False,
  )
  properties_json: Mapped[dict[str, Any]] = mapped_column(
    JSONB,
    nullable=True,
    comment="Arbitrary metadata.",
    default={},
  )

  name: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="Unique, human-readable name for the object.",
    kw_only=True,
  )


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
  """Yield an asynchronous database session.

  Ensure the session is closed after use.
  """
  async_session = AsyncSessionLocal()
  try:
    yield async_session
  except Exception:
    await async_session.rollback()
    raise
  finally:
    await async_session.close()


async def init_praxis_db_schema() -> None:
  """Initialize the Praxis database schema.

  Create all tables defined by ORM models inheriting from `Base`.
  """
  logger.info("Importing ORM models for Praxis database schema initialization...")
  logger.info(
    "Initializing Praxis database tables at %s...",
    PRAXIS_DATABASE_URL.replace(praxis_db_password, "****"),
  )
  try:
    async with async_engine.begin() as conn:
      await conn.run_sync(Base.metadata.create_all)
    logger.info(
      "Praxis database tables created successfully (if they didn't already exist).",
    )
  except Exception:
    # Use logging.exception instead of logging.error.
    logger.exception("Error creating Praxis database tables")
    raise

class CreateMaterializedView(DDLElement):

  """SQLAlchemy DDL element to create a materialized view."""

  def __init__(self, name: str, selectable: Select) -> None:
    """Initialize the CreateMaterializedView element."""
    self.name = name
    self.selectable = selectable


class DropMaterializedView(DDLElement):

  """SQLAlchemy DDL element to drop a materialized view."""

  def __init__(self, name: str) -> None:
    """Initialize the DropMaterializedView element."""
    self.name = name


@compiles(CreateMaterializedView)
def compile_create_materialized_view(
  element: CreateMaterializedView,
  compiler: SQLCompiler,
  **kw: Any,  # noqa: ARG001, ANN401
) -> str:
  """Compiler for the CreateMaterializedView DDL element.

  Args:
    element (CreateMaterializedView): The DDL element to compile.
    compiler (SQLCompiler): The SQL compiler instance.
    **kw: Additional keyword arguments (not used, for future proofing).

  Returns:
    str: The SQL statement to create the materialized view.

  """
  return f"CREATE MATERIALIZED VIEW {element.name} AS \
    {compiler.sql_compiler.process(element.selectable, literal_binds=True)}"


@compiles(DropMaterializedView)
def compile_drop_materialized_view(
  element: DropMaterializedView,
  compiler: SQLCompiler,  # noqa: ARG001
  **kw: Any,  # noqa: ARG001, ANN401
) -> str:
  """Compiler for the DropMaterializedView DDL element.

  Args:
    element (DropMaterializedView): The DDL element to compile.
    compiler (SQLCompiler): The SQL compiler instance.
    **kw: Additional keyword arguments (not used, for future proofing).

  Returns:
    str: The SQL statement to drop the materialized view.

  """
  return f"DROP MATERIALIZED VIEW IF EXISTS {element.name}"
