import configparser
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select, text

from praxis.backend.models import UserOrm

# Adjust the import path for the service and its helper
from praxis.backend.services.praxis_orm_service import (
  PraxisDBService,
  _get_keycloak_dsn_from_config,
)

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def cleanup_singleton():
  """Fixture to reset the singleton instance before and after each test."""
  # Reset before test
  if PraxisDBService._instance:
    PraxisDBService._instance._keycloak_pool = None
  PraxisDBService._instance = None
  yield
  # Reset after test
  if PraxisDBService._instance:
    PraxisDBService._instance._keycloak_pool = None
  PraxisDBService._instance = None


class TestPraxisDBService:
  """Test suite for the PraxisDBService class."""

  def test_singleton_pattern(self) -> None:
    """Test that the singleton pattern is correctly implemented."""
    instance1 = PraxisDBService()
    instance2 = PraxisDBService()
    assert instance1 is instance2

  async def test_initialize_no_keycloak(self) -> None:
    """Test initialization without a Keycloak DSN."""
    service = await PraxisDBService.initialize()
    assert service._keycloak_pool is None

  async def test_initialize_invalid_dsn_raises_value_error(self) -> None:
    """Test that initialization with an invalid DSN format raises ValueError."""
    with pytest.raises(ValueError, match="must start with postgresql://"):
      await PraxisDBService.initialize(keycloak_dsn="http://invalid-dsn")

  @patch("asyncpg.create_pool", new_callable=AsyncMock)
  async def test_initialize_keycloak_success(self, mock_create_pool) -> None:
    """Test successful initialization with a mocked Keycloak connection pool."""
    mock_pool = AsyncMock()
    mock_create_pool.return_value = mock_pool

    service = await PraxisDBService.initialize(
      keycloak_dsn="postgresql://user:pass@host/db",
    )

    mock_create_pool.assert_called_once()
    assert service._keycloak_pool is not None
    # Test that initializing again does not create a new pool
    await PraxisDBService.initialize(keycloak_dsn="postgresql://user:pass@host/db")
    mock_create_pool.assert_called_once()  # Should still be 1

  @patch(
    "asyncpg.create_pool",
    new_callable=AsyncMock,
    side_effect=ConnectionRefusedError("Test refuse"),
  )
  async def test_initialize_keycloak_connection_fails(self, mock_create_pool) -> None:
    """Test that initialization raises ConnectionError after retries."""
    # Patch sleep to speed up the test
    with patch("asyncio.sleep", new_callable=AsyncMock), pytest.raises(
      ConnectionError, match="Could not establish Keycloak database connection",
    ):
      await PraxisDBService.initialize(keycloak_dsn="postgresql://user:pass@host/db")
    assert mock_create_pool.call_count == 3  # _max_retries = 3

  async def test_get_praxis_session_commit_and_rollback(self, db_session_factory) -> None:
    """Test the get_praxis_session context manager for commit and rollback."""
    service = PraxisDBService()

    # Patch the service's session provider to use our test factory
    with patch(
      "praxis.backend.services.praxis_orm_service.AsyncSessionLocal", db_session_factory,
    ):
      # Test successful commit
      async with service.get_praxis_session() as session:
        user = UserOrm(
          accession_id=uuid.uuid4(), username="test_commit", email="commit@test.com",
        )
        session.add(user)

      # Verify in a new session
      async with db_session_factory() as session:
        result = await session.execute(
          select(UserOrm).where(UserOrm.username == "test_commit"),
        )
        assert result.scalar_one_or_none() is not None

      # Test rollback on exception
      try:
        async with service.get_praxis_session() as session:
          user_rollback = UserOrm(
            accession_id=uuid.uuid4(),
            username="test_rollback",
            email="rollback@test.com",
          )
          session.add(user_rollback)
          msg = "Test Rollback"
          raise ValueError(msg)
      except ValueError:
        pass  # Expected

      # Verify in a new session that the user was not added
      async with db_session_factory() as session:
        result = await session.execute(
          select(UserOrm).where(UserOrm.username == "test_rollback"),
        )
        assert result.scalar_one_or_none() is None

  @patch("asyncpg.create_pool", new_callable=AsyncMock)
  async def test_get_all_users_success(self, mock_create_pool) -> None:
    """Test fetching all users from a mocked Keycloak DB."""
    # Mock the connection and its fetch method
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [
      {
        "id": "1",
        "username": "user1",
        "email": "u1@test.com",
        "first_name": "A",
        "last_name": "User",
        "enabled": True,
      },
      {
        "id": "2",
        "username": "user2",
        "email": "u2@test.com",
        "first_name": "B",
        "last_name": "User",
        "enabled": True,
      },
    ]

    # Mock the pool and its acquire method
    mock_pool = AsyncMock()
    mock_pool.acquire.return_value = mock_conn
    mock_create_pool.return_value = mock_pool

    service = await PraxisDBService.initialize(keycloak_dsn="postgresql://mock")

    users = await service.get_all_users()
    assert len(users) == 2
    assert "user1" in users
    assert users["user2"]["email"] == "u2@test.com"
    assert users["user1"]["is_active"] is True

  async def test_get_all_users_no_pool(self) -> None:
    """Test that get_all_users returns an empty dict if pool is not initialized."""
    service = PraxisDBService()
    users = await service.get_all_users()
    assert users == {}

  async def test_raw_sql_methods(self, db_session_factory) -> None:
    """Test execute, fetch_all, fetch_one, and fetch_val SQL methods."""
    service = PraxisDBService()

    # Setup: create a table and insert data
    async with db_session_factory() as session:
      await session.execute(text("CREATE TABLE sql_test (id INTEGER, name TEXT)"))
      await session.execute(
        text("INSERT INTO sql_test VALUES (1, 'alpha'), (2, 'beta')"),
      )
      await session.commit()

    with patch(
      "praxis.backend.services.praxis_orm_service.AsyncSessionLocal", db_session_factory,
    ):
      # Test fetch_all
      rows = await service.fetch_all_sql("SELECT * FROM sql_test ORDER BY id")
      assert len(rows) == 2
      assert rows[0]["name"] == "alpha"

      # Test fetch_one
      row = await service.fetch_one_sql(
        "SELECT * FROM sql_test WHERE id = :id", params={"id": 2},
      )
      assert row is not None
      assert row["name"] == "beta"

      # Test fetch_val
      count = await service.fetch_val_sql("SELECT COUNT(*) FROM sql_test")
      assert count == 2

      # Test execute
      await service.execute_sql("UPDATE sql_test SET name = 'gamma' WHERE id = 1")
      new_name = await service.fetch_val_sql("SELECT name FROM sql_test WHERE id = 1")
      assert new_name == "gamma"

  @patch("asyncpg.create_pool", new_callable=AsyncMock)
  async def test_close(self, mock_create_pool) -> None:
    """Test that the close method closes the Keycloak pool."""
    mock_pool = AsyncMock()
    mock_pool._closed = False  # Simulate it's open
    mock_create_pool.return_value = mock_pool

    service = await PraxisDBService.initialize(keycloak_dsn="postgresql://mock")
    await service.close()

    mock_pool.close.assert_called_once()


def test_get_keycloak_dsn_from_config(mocker) -> None:
  """Test the helper function for reading Keycloak DSN from praxis.ini."""
  # Mock file system and config parser
  mocker.patch("pathlib.Path.exists", return_value=True)
  mock_config = configparser.ConfigParser()
  mocker.patch("configparser.ConfigParser", return_value=mock_config)

  # Test success case
  mock_config.read_dict(
    {
      "keycloak_database": {
        "user": "testuser",
        "password": "testpassword",
        "host": "localhost",
        "port": "5432",
        "dbname": "keycloak_db",
      },
    },
  )
  dsn = _get_keycloak_dsn_from_config()
  assert dsn == "postgresql://testuser:testpassword@localhost:5432/keycloak_db"

  # Test with env var override
  mocker.patch.dict(
    "os.environ",
    {"KEYCLOAK_DB_USER": "env_user", "KEYCLOAK_DB_PASSWORD": "env_password"},
  )
  dsn_env = _get_keycloak_dsn_from_config()
  assert dsn_env == "postgresql://env_user:env_password@localhost:5432/keycloak_db"

  # Test file not found
  mocker.patch("pathlib.Path.exists", return_value=False)
  assert _get_keycloak_dsn_from_config() is None
