# tests/services/test_praxis_orm_service.py
import asyncio
import asyncpg
import pytest
import pytest_asyncio  # For async fixtures
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from unittest.mock import patch, AsyncMock

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Assuming Base is defined in praxis.backend.utils.db and accessible
# If Base is defined elsewhere, adjust the import path.
from praxis.backend.utils.db import (
  Base as PraxisBase,
)  # Renamed to avoid conflict if Base is used locally
from praxis.backend.services.praxis_orm_service import (
  PraxisDBService,
  _get_keycloak_dsn_from_config,
)
from praxis.backend.database_models import (
  ProtocolSourceRepositoryOrm,
  FunctionProtocolDefinitionOrm,
  ProtocolRunOrm,
  ProtocolRunStatusEnum,
  ResourceInstanceOrm,
  UserOrm,  # Assuming UserOrm is in praxis.backend.database_models
  ResourceDefinitionCatalogOrm,
  # If AssetDefinitionOrm is still used for other asset types, import it
)
from praxis.backend.database_models.asset_management_orm import (
  ResourceInstanceStatusEnum,
)

# In-memory SQLite database URL for testing
ASYNC_SQLITE_URL = "sqlite+aiosqlite:///:memory:"

# --- Fixtures ---


@pytest_asyncio.fixture(scope="function")
async def async_engine():
  """Creates an in-memory SQLite async engine for the duration of a test function."""
  engine = create_async_engine(ASYNC_SQLITE_URL)
  async with engine.begin() as conn:
    await conn.run_sync(PraxisBase.metadata.create_all)
  yield engine
  async with engine.begin() as conn:
    await conn.run_sync(PraxisBase.metadata.drop_all)
  await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(async_engine):
  """Provides a clean database session for each test function."""
  async_session_local = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
  )
  async with async_session_local() as session:  # type: ignore
    yield session
    await session.rollback()  # Ensure tests are isolated


@pytest_asyncio.fixture
async def mock_asyncpg_pool():
  """Mocks the asyncpg connection pool and its connections."""
  mock_pool = AsyncMock(spec=asyncpg.Pool)
  mock_conn = AsyncMock(spec=asyncpg.Connection)

  # Configure acquire to return an async context manager yielding mock_conn
  acquire_cm = AsyncMock()
  acquire_cm.__aenter__.return_value = mock_conn
  acquire_cm.__aexit__.return_value = None  # Or an AsyncMock if needed
  mock_pool.acquire.return_value = acquire_cm

  mock_pool.release = AsyncMock()
  mock_conn.execute = AsyncMock()
  mock_conn.fetch = AsyncMock(return_value=[])  # Default to empty list for fetch
  mock_pool._closed = False  # Simulate an open pool
  return mock_pool


@pytest_asyncio.fixture
async def praxis_db_service(db_session, mock_asyncpg_pool):
  """
  Provides an instance of PraxisDBService with a mocked AsyncSessionLocal
  and a mocked Keycloak pool.
  """
  # Patch AsyncSessionLocal to use our in-memory SQLite session for Praxis DB
  # Patch _get_keycloak_dsn_from_config to prevent file system access
  # Patch asyncpg.create_pool to use our mock_asyncpg_pool
  with patch(
    "praxis.backend.services.praxis_orm_service.AsyncSessionLocal",
    return_value=db_session,
  ), patch(
    "praxis.backend.services.praxis_orm_service._get_keycloak_dsn_from_config",
    return_value="postgresql://mock:mock@mock/mock",
  ) as mock_get_dsn, patch(
    "asyncpg.create_pool", return_value=mock_asyncpg_pool
  ) as mock_create_pg_pool:
    service_instance = await PraxisDBService.initialize(
      keycloak_dsn="postgresql://mock:mock@mock/mock"
    )
    # The initialize method should now use the mocked create_pool

    # Ensure the service instance actually got the mocked pool
    assert (
      service_instance._keycloak_pool is mock_asyncpg_pool
    ), "Service did not use the mocked Keycloak pool"

    yield service_instance
    await service_instance.close()


# --- Helper Function to Create Initial Data ---
async def create_test_user(
  session: AsyncSession, user_accession_id: str, username: str = "testuser"
) -> UserOrm:
  user = UserOrm(
    id=user_accession_id,
    username=username,
    email=f"{username}@example.com",
    first_name="Test",
    last_name="User",
  )
  session.add(user)
  await session.commit()
  await session.refresh(user)
  return user


async def create_test_protocol_source_repo(
  session: AsyncSession, name: str = "TestRepo"
) -> ProtocolSourceRepositoryOrm:
  repo = ProtocolSourceRepositoryOrm(
    name=name, git_url="http://example.com/repo.git", default_ref="main"
  )
  session.add(repo)
  await session.commit()
  await session.refresh(repo)
  return repo


async def create_test_protocol_definition(
  session: AsyncSession,
  source_repo_accession_id: int,
  name: str = "TestProtocolDef",
  version: str = "1.0.0",
  is_top_level: bool = True,
) -> FunctionProtocolDefinitionOrm:
  proto_def = FunctionProtocolDefinitionOrm(
    name=name,
    version=version,
    source_file_path=f"protocols/{name.lower()}.py",
    module_name=f"protocols.{name.lower()}",
    function_name="run_protocol",
    source_repository_accession_id=source_repo_accession_id,
    is_top_level=is_top_level,
  )
  session.add(proto_def)
  await session.commit()
  await session.refresh(proto_def)
  return proto_def


async def create_test_resource_definition(
  session: AsyncSession, name: str = "test_plate_def_96"
) -> ResourceDefinitionCatalogOrm:
  lw_def = ResourceDefinitionCatalogOrm(
    name=name,
    python_fqn=f"pylabrobot.resources.{name}.{name.capitalize()}",
    plr_category="Plate",
    size_x_mm=127.76,
    size_y_mm=85.48,
    size_z_mm=14.24,
  )
  session.add(lw_def)
  await session.commit()
  await session.refresh(lw_def)
  return lw_def


# --- Test Classes ---


@pytest.mark.asyncio
class TestProtocolRunManagement:
  """Tests for protocol run management methods in PraxisDBService."""

  async def test_register_protocol_run(
    self, praxis_db_service: PraxisDBService, db_session: AsyncSession
  ):
    """Test registering a new protocol run."""
    test_user_accession_id = str(uuid.uuid4())
    await create_test_user(db_session, user_accession_id=test_user_accession_id)

    repo = await create_test_protocol_source_repo(db_session)
    proto_def = await create_test_protocol_definition(
      db_session, source_repo_accession_id=repo.accession_id
    )

    run_params = {"param1": "value1", "count": 10}

    run_accession_id = await praxis_db_service.register_protocol_run(
      protocol_definition_accession_id=proto_def.accession_id,
      created_by_user_accession_id=test_user_accession_id,
      parameters=run_params,
      status=ProtocolRunStatusEnum.PENDING,
    )
    assert isinstance(run_accession_id, int)

    # Verify in DB
    async with praxis_db_service.get_praxis_session() as verify_session:  # Use service's session getter
      stmt = select(ProtocolRunOrm).where(
        ProtocolRunOrm.accession_id == run_accession_id
      )
      result = await verify_session.execute(stmt)
      run_orm = result.scalar_one_or_none()

    assert run_orm is not None
    assert run_orm.top_level_protocol_definition_accession_id == proto_def.accession_id
    assert run_orm.created_by_user is not None
    assert run_orm.created_by_user.get("id") == test_user_accession_id
    assert run_orm.status == ProtocolRunStatusEnum.PENDING
    assert run_orm.input_parameters_json == run_params
    assert run_orm.run_accession_id is not None

  async def test_get_protocol_run_details_exists(
    self, praxis_db_service: PraxisDBService, db_session: AsyncSession
  ):
    """Test retrieving details of an existing protocol run."""
    test_user_accession_id = str(uuid.uuid4())
    user = await create_test_user(
      db_session, user_accession_id=test_user_accession_id, username="details_user"
    )
    repo = await create_test_protocol_source_repo(db_session)
    proto_def = await create_test_protocol_definition(
      db_session, source_repo_accession_id=repo.accession_id
    )
    run_params = {"sample_accession_id": "S001"}

    run_accession_id = await praxis_db_service.register_protocol_run(
      protocol_definition_accession_id=proto_def.accession_id,
      created_by_user_accession_id=test_user_accession_id,
      parameters=run_params,
    )

    details = await praxis_db_service.get_protocol_run_details(run_accession_id)

    assert details is not None
    assert details["protocol_run_accession_id"] == run_accession_id
    assert details["protocol_definition_accession_id"] == proto_def.accession_id
    assert details["parameters"] == run_params
    assert details["status"] == ProtocolRunStatusEnum.PENDING.name
    assert details["user"] is not None
    assert details["user"]["id"] == test_user_accession_id
    assert details["user"]["username"] == "details_user"

  async def test_get_protocol_run_details_not_exists(
    self, praxis_db_service: PraxisDBService
  ):
    """Test retrieving details for a non-existent protocol run."""
    details = await praxis_db_service.get_protocol_run_details(99999)  # Non-existent ID
    assert details is None

  async def test_update_protocol_run_status(
    self, praxis_db_service: PraxisDBService, db_session: AsyncSession
  ):
    """Test updating the status of a protocol run."""
    test_user_accession_id = str(uuid.uuid4())
    await create_test_user(db_session, user_accession_id=test_user_accession_id)
    repo = await create_test_protocol_source_repo(db_session)
    proto_def = await create_test_protocol_definition(
      db_session, source_repo_accession_id=repo.accession_id
    )

    run_accession_id = await praxis_db_service.register_protocol_run(
      protocol_definition_accession_id=proto_def.accession_id,
      created_by_user_accession_id=test_user_accession_id,
    )

    await praxis_db_service.update_protocol_run_status(
      run_accession_id, ProtocolRunStatusEnum.RUNNING
    )

    details_after_update = await praxis_db_service.get_protocol_run_details(
      run_accession_id
    )
    assert details_after_update is not None
    assert details_after_update["status"] == ProtocolRunStatusEnum.RUNNING.name
    assert details_after_update["end_time"] is None  # Should not be set for RUNNING

    await praxis_db_service.update_protocol_run_status(
      run_accession_id, ProtocolRunStatusEnum.COMPLETED
    )
    details_completed = await praxis_db_service.get_protocol_run_details(
      run_accession_id
    )
    assert details_completed is not None
    assert details_completed["status"] == ProtocolRunStatusEnum.COMPLETED.name
    assert details_completed["end_time"] is not None  # Should be set for COMPLETED

  async def test_list_protocol_runs(
    self, praxis_db_service: PraxisDBService, db_session: AsyncSession
  ):
    """Test listing protocol runs with various filters."""
    user1accession_id = str(uuid.uuid4())
    user2accession_id = str(uuid.uuid4())
    await create_test_user(
      db_session, user_accession_id=user1accession_id, username="user1_runs"
    )
    await create_test_user(
      db_session, user_accession_id=user2accession_id, username="user2_runs"
    )

    repo = await create_test_protocol_source_repo(db_session)
    proto_def1 = await create_test_protocol_definition(
      db_session, source_repo_accession_id=repo.accession_id, name="ProtoDef1"
    )

    # Run 1 (User1, Pending)
    await praxis_db_service.register_protocol_run(
      proto_def1.accession_id,
      user1accession_id,
      {"p": 1},
      ProtocolRunStatusEnum.PENDING,
    )
    # Run 2 (User1, Running)
    await praxis_db_service.register_protocol_run(
      proto_def1.accession_id,
      user1accession_id,
      {"p": 2},
      ProtocolRunStatusEnum.RUNNING,
    )
    # Run 3 (User2, Completed)
    await praxis_db_service.register_protocol_run(
      proto_def1.accession_id,
      user2accession_id,
      {"p": 3},
      ProtocolRunStatusEnum.COMPLETED,
    )

    all_runs = await praxis_db_service.list_protocol_runs()
    assert len(all_runs) == 3

    user1_runs = await praxis_db_service.list_protocol_runs(
      created_by_user_accession_id=user1accession_id
    )
    assert len(user1_runs) == 2
    assert all(run["user"]["id"] == user1accession_id for run in user1_runs)

    pending_runs = await praxis_db_service.list_protocol_runs(
      status=ProtocolRunStatusEnum.PENDING
    )
    assert len(pending_runs) == 1
    assert pending_runs[0]["status"] == ProtocolRunStatusEnum.PENDING.name

    user2_completed_runs = await praxis_db_service.list_protocol_runs(
      status=ProtocolRunStatusEnum.COMPLETED,
      created_by_user_accession_id=user2accession_id,
    )
    assert len(user2_completed_runs) == 1
    assert user2_completed_runs[0]["user"]["id"] == user2accession_id
    assert user2_completed_runs[0]["status"] == ProtocolRunStatusEnum.COMPLETED.name

    empty_runs = await praxis_db_service.list_protocol_runs(
      status=ProtocolRunStatusEnum.FAILED
    )
    assert len(empty_runs) == 0


@pytest.mark.asyncio
class TestAssetInstanceManagement:
  """Tests for asset (ResourceInstanceOrm) management methods."""

  async def test_add_asset_instance_new(
    self, praxis_db_service: PraxisDBService, db_session: AsyncSession
  ):
    """Test adding a new resource instance."""
    lw_def_name = "my_test_plate_def"
    await create_test_resource_definition(db_session, name=lw_def_name)

    asset_name = "TestPlate001"
    properties = {"color": "blue", "well_count": 96}

    asset_accession_id = await praxis_db_service.add_asset_instance(
      user_assigned_name=asset_name,
      name=lw_def_name,
      properties_json=properties,
      current_status=ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
    )
    assert isinstance(asset_accession_id, int)

    # Verify in DB
    async with praxis_db_service.get_praxis_session() as verify_session:
      stmt = select(ResourceInstanceOrm).where(
        ResourceInstanceOrm.accession_id == asset_accession_id
      )
      result = await verify_session.execute(stmt)
      asset_orm = result.scalar_one_or_none()

    assert asset_orm is not None
    assert asset_orm.user_assigned_name == asset_name
    assert asset_orm.name == lw_def_name
    assert asset_orm.properties_json == properties
    assert asset_orm.current_status == ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE

  async def test_add_asset_instance_update(
    self, praxis_db_service: PraxisDBService, db_session: AsyncSession
  ):
    """Test updating an existing resource instance."""
    lw_def_name = "update_plate_def"
    await create_test_resource_definition(db_session, name=lw_def_name)
    asset_name = "UpdatablePlate002"

    # Initial add
    await praxis_db_service.add_asset_instance(
      user_assigned_name=asset_name,
      name=lw_def_name,
      properties_json={"initial": "data"},
      current_status=ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
    )

    # Update
    updated_properties = {"updated": "info", "initial": "overwritten"}
    updated_accession_id = await praxis_db_service.add_asset_instance(
      user_assigned_name=asset_name,  # Same name
      name=lw_def_name,  # Can be same or different if type changes
      properties_json=updated_properties,
      current_status=ResourceInstanceStatusEnum.IN_USE,
      lot_number="LOT123",
    )

    details = await praxis_db_service.get_asset_instance(asset_name)
    assert details is not None
    assert details["id"] == updated_accession_id  # Should be the same ID
    assert details["properties_json"] == updated_properties
    assert details["current_status"] == ResourceInstanceStatusEnum.IN_USE.name
    assert details["lot_number"] == "LOT123"

  async def test_get_asset_instance_exists(
    self, praxis_db_service: PraxisDBService, db_session: AsyncSession
  ):
    """Test retrieving an existing resource instance."""
    lw_def_name = "get_plate_def"
    await create_test_resource_definition(db_session, name=lw_def_name)
    asset_name = "GettablePlate003"
    properties = {"feature": "readable"}

    await praxis_db_service.add_asset_instance(
      user_assigned_name=asset_name,
      name=lw_def_name,
      properties_json=properties,
      current_status=ResourceInstanceStatusEnum.AVAILABLE_ON_DECK,
    )

    details = await praxis_db_service.get_asset_instance(asset_name)
    assert details is not None
    assert details["user_assigned_name"] == asset_name
    assert details["name"] == lw_def_name
    assert details["properties_json"] == properties
    assert (
      details["current_status"] == ResourceInstanceStatusEnum.AVAILABLE_ON_DECK.name
    )
    assert details["is_available"] is True

  async def test_get_asset_instance_not_exists(
    self, praxis_db_service: PraxisDBService
  ):
    """Test retrieving a non-existent resource instance."""
    details = await praxis_db_service.get_asset_instance("NonExistentPlate999")
    assert details is None

  async def test_asset_availability_logic(
    self, praxis_db_service: PraxisDBService, db_session: AsyncSession
  ):
    """Test the is_available logic in get_asset_instance."""
    lw_def_name = "availability_plate_def"
    await create_test_resource_definition(db_session, name=lw_def_name)

    asset_available_names = ["PlateAvail1", "PlateAvail2", "PlateAvail3"]
    asset_unavailable_names = ["PlateUnavail1", "PlateUnavail2"]

    # Available statuses
    await praxis_db_service.add_asset_instance(
      asset_available_names[0],
      lw_def_name,
      current_status=ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
    )
    await praxis_db_service.add_asset_instance(
      asset_available_names[1],
      lw_def_name,
      current_status=ResourceInstanceStatusEnum.AVAILABLE_ON_DECK,
    )
    await praxis_db_service.add_asset_instance(
      asset_available_names[2],
      lw_def_name,
      current_status=ResourceInstanceStatusEnum.EMPTY,
    )  # Assuming EMPTY is available

    # Unavailable statuses
    await praxis_db_service.add_asset_instance(
      asset_unavailable_names[0],
      lw_def_name,
      current_status=ResourceInstanceStatusEnum.IN_USE,
    )
    await praxis_db_service.add_asset_instance(
      asset_unavailable_names[1],
      lw_def_name,
      current_status=ResourceInstanceStatusEnum.ERROR,
    )

    for name in asset_available_names:
      details = await praxis_db_service.get_asset_instance(name)
      assert details is not None, f"Details for {name} should not be None"
      assert (
        details["is_available"] is True
      ), f"Asset {name} with status {details['current_status']} should be available"

    for name in asset_unavailable_names:
      details = await praxis_db_service.get_asset_instance(name)
      assert details is not None, f"Details for {name} should not be None"
      assert (
        details["is_available"] is False
      ), f"Asset {name} with status {details['current_status']} should NOT be available"


@pytest.mark.asyncio
class TestKeycloakUserManagement:
  """Tests for Keycloak user management methods (mocked)."""

  async def test_get_all_users_success(
    self, praxis_db_service: PraxisDBService, mock_asyncpg_pool: AsyncMock
  ):
    """Test fetching all users from Keycloak successfully."""
    mock_users_data = [
      {
        "id": "user-id-1",
        "username": "kuser1",
        "email": "kuser1@example.com",
        "first_name": "Keycloak",
        "last_name": "UserOne",
        "enabled": True,
      },
      {
        "id": "user-id-2",
        "username": "kuser2",
        "email": "kuser2@example.com",
        "first_name": "Keycloak",
        "last_name": "UserTwo",
        "enabled": True,
      },
    ]
    # The mock_conn is part of mock_asyncpg_pool.acquire().__aenter__
    mock_conn = mock_asyncpg_pool.acquire.return_value.__aenter__.return_value
    mock_conn.fetch.return_value = mock_users_data

    users = await praxis_db_service.get_all_users()

    assert len(users) == 2
    assert "kuser1" in users
    assert users["kuser1"]["email"] == "kuser1@example.com"
    assert users["kuser1"]["is_active"] is True
    assert "kuser2" in users

    # Verify that the correct SQL was 'executed' by the mock
    # The actual SQL string is in the method, this just checks if fetch was called.
    mock_conn.fetch.assert_called_once()

  async def test_get_all_users_no_keycloak_pool(self, db_session: AsyncSession):
    """Test behavior when Keycloak pool is not initialized (e.g., DSN not provided)."""
    # Create a service instance without initializing Keycloak pool properly
    # This requires a bit more direct instantiation or specific mocking for this one test
    with patch(
      "praxis.backend.services.praxis_orm_service.AsyncSessionLocal",
      return_value=db_session,
    ), patch(
      "praxis.backend.services.praxis_orm_service._get_keycloak_dsn_from_config",
      return_value=None,
    ), patch(
      "asyncpg.create_pool",
      AsyncMock(side_effect=RuntimeError("Simulated pool creation failure")),
    ):  # Ensure create_pool is not called or fails
      service_no_kc = (
        PraxisDBService()
      )  # Create instance without classmethod initialize
      service_no_kc._keycloak_pool = None  # Explicitly set to None

      with pytest.raises(RuntimeError, match="Keycloak database pool not initialized."):
        await service_no_kc.get_all_users()


# Note: Tests for raw SQL methods (execute_sql, fetch_all_sql, etc.) are omitted
# as they directly pass through to SQLAlchemy and their correct functioning
# depends heavily on the SQL provided and the database state.
# Testing them thoroughly would involve more complex DB state setup for each specific SQL query.
