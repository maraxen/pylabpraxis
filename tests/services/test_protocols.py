import asyncio
import json
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models import (
  AssetRequirementModel,
  FileSystemProtocolSourceOrm,
  FunctionCallStatusEnum,
  FunctionProtocolDefinitionModel,
  FunctionProtocolDefinitionOrm,
  ParameterMetadataModel,
  ProtocolRunOrm,
  ProtocolRunStatusEnum,
  ProtocolSourceRepositoryOrm,
)

# Import the service functions to be tested
from praxis.backend.services.protocols import (
  create_file_system_protocol_source,
  create_protocol_run,
  create_protocol_source_repository,
  list_protocol_runs,
  list_protocol_source_repositories,
  log_function_call_end,
  log_function_call_start,
  read_function_call_logs_for_run,
  read_protocol_run,
  read_protocol_source_repository,
  update_protocol_run_status,
  update_protocol_source_repository,
  upsert_function_protocol_definition,
)

# --- Fixtures ---


@pytest.fixture
async def git_source(db: AsyncSession) -> ProtocolSourceRepositoryOrm:
  """Fixture for a git protocol source repository."""
  return await create_protocol_source_repository(
    db, name=f"TestGitRepo_{uuid.uuid4()}", git_url="https://github.com/test/repo.git",
  )


@pytest.fixture
async def fs_source(db: AsyncSession) -> FileSystemProtocolSourceOrm:
  """Fixture for a filesystem protocol source."""
  return await create_file_system_protocol_source(
    db, name=f"TestFSSource_{uuid.uuid4()}", base_path="/tmp/protocols",
  )


@pytest.fixture
def pydantic_protocol() -> FunctionProtocolDefinitionModel:
  """Fixture providing a valid Pydantic model for a function protocol definition."""
  return FunctionProtocolDefinitionModel(
    accession_id=uuid.uuid4(),
    name="TestUpsertProtocol",
    version="1.0.0",
    description="A test protocol for upsert.",
    source_file_path="protocols/test_upsert.py",
    module_name="protocols.test_upsert",
    function_name="run_upsert_test",
    parameters=[
      ParameterMetadataModel(
        name="param1",
        type_hint_str="int",
        actual_type_str="int",
        optional=False,
        description="First param",
      ),
    ],
    assets=[
      AssetRequirementModel(
        accession_id=uuid.uuid4(),
        name="plate1",
        fqn="pylabrobot.resources.Plate",
        description="A 96-well plate",
      ),
    ],
  )


@pytest.fixture
async def protocol_def(
  db: AsyncSession,
  git_source: ProtocolSourceRepositoryOrm,
  pydantic_protocol: FunctionProtocolDefinitionModel,
) -> FunctionProtocolDefinitionOrm:
  """Fixture for an existing protocol definition in the DB."""
  return await upsert_function_protocol_definition(
    db,
    protocol_pydantic=pydantic_protocol,
    source_repository_accession_id=git_source.accession_id,
    commit_hash="abc1234",
  )


@pytest.fixture
async def protocol_run(
  db: AsyncSession, protocol_def: FunctionProtocolDefinitionOrm,
) -> ProtocolRunOrm:
  """Fixture for an existing protocol run in the DB."""
  return await create_protocol_run(
    db, top_level_protocol_definition_accession_id=protocol_def.accession_id,
  )


pytestmark = pytest.mark.asyncio

# --- Test Classes ---


class TestProtocolSourceRepositoryService:
  """Tests for Git-based protocol source repositories."""

  async def test_create_and_read_git_repo(self, db: AsyncSession):
    name = f"MyGitRepo_{uuid.uuid4()}"
    repo = await create_protocol_source_repository(
      db, name=name, git_url="http://git.test/repo",
    )
    assert repo.name == name

    read_repo = await read_protocol_source_repository(db, repo.accession_id)
    assert read_repo is not None
    assert read_repo.name == name

  async def test_update_git_repo(
    self, db: AsyncSession, git_source: ProtocolSourceRepositoryOrm,
  ):
    new_ref = "develop"
    updated_repo = await update_protocol_source_repository(
      db, source_accession_id=git_source.accession_id, default_ref=new_ref,
    )
    assert updated_repo.default_ref == new_ref

  async def test_list_git_repos_by_sync_status(
    self, db: AsyncSession, git_source: ProtocolSourceRepositoryOrm,
  ):
    """Test filtering repositories by their auto_sync_enabled status."""
    # Create a second repo to have a distinct set
    await create_protocol_source_repository(
      db,
      name=f"NoSyncRepo_{uuid.uuid4()}",
      git_url="http://git.test/repo2",
      auto_sync_enabled=False,
    )

    # Default is True, so git_source should be in this list
    synced_repos = await list_protocol_source_repositories(db, auto_sync_enabled=True)
    assert len(synced_repos) >= 1
    assert any(r.accession_id == git_source.accession_id for r in synced_repos)

    # Test for non-synced repos
    not_synced_repos = await list_protocol_source_repositories(
      db, auto_sync_enabled=False,
    )
    assert len(not_synced_repos) == 1
    assert not any(r.accession_id == git_source.accession_id for r in not_synced_repos)


class TestProtocolDefinitionService:
  """Tests for creating and managing protocol definitions."""

  async def test_upsert_protocol_create(
    self,
    db: AsyncSession,
    git_source: ProtocolSourceRepositoryOrm,
    pydantic_protocol: FunctionProtocolDefinitionModel,
  ):
    """Test creating a new protocol definition via upsert."""
    created_def = await upsert_function_protocol_definition(
      db,
      protocol_pydantic=pydantic_protocol,
      source_repository_accession_id=git_source.accession_id,
      commit_hash="def123",
    )
    assert created_def is not None
    assert created_def.name == "TestUpsertProtocol"
    assert len(created_def.parameters) == 1
    assert created_def.parameters[0].name == "param1"
    assert len(created_def.assets) == 1
    assert created_def.assets[0].name == "plate1"

  async def test_upsert_protocol_update_and_sync(
    self,
    db: AsyncSession,
    protocol_def: FunctionProtocolDefinitionOrm,
    pydantic_protocol: FunctionProtocolDefinitionModel,
  ):
    """Test updating an existing protocol, syncing params and assets."""
    pydantic_protocol.parameters[0].description = "Updated description"
    pydantic_protocol.parameters.append(
      ParameterMetadataModel(
        name="param2", type_hint_str="str", actual_type_str="str", optional=True,
      ),
    )
    pydantic_protocol.assets = [
      AssetRequirementModel(
        accession_id=uuid.uuid4(), name="tip_rack", fqn="pylabrobot.resources.TipRack",
      ),
    ]

    updated_def = await upsert_function_protocol_definition(
      db,
      protocol_pydantic=pydantic_protocol,
      source_repository_accession_id=protocol_def.source_repository_accession_id,
      commit_hash=protocol_def.commit_hash,
    )

    assert updated_def.accession_id == protocol_def.accession_id
    assert len(updated_def.parameters) == 2
    assert updated_def.parameters[0].description == "Updated description"
    assert len(updated_def.assets) == 1
    assert updated_def.assets[0].name == "tip_rack"


class TestProtocolRunService:
  """Tests for creating and managing protocol runs."""

  async def test_create_and_read_protocol_run(
    self, db: AsyncSession, protocol_def: FunctionProtocolDefinitionOrm,
  ):
    """Test creating a new protocol run and reading it back."""
    run = await create_protocol_run(db, protocol_def.accession_id)
    assert run is not None
    assert run.status == ProtocolRunStatusEnum.PENDING

    read_run = await read_protocol_run(db, run.run_accession_id)
    assert read_run is not None
    assert read_run.accession_id == run.accession_id

  async def test_update_protocol_run_status(
    self, db: AsyncSession, protocol_run: ProtocolRunOrm,
  ):
    """Test updating the status of a protocol run through its lifecycle."""
    assert protocol_run.start_time is None

    await update_protocol_run_status(
      db, protocol_run.accession_id, ProtocolRunStatusEnum.RUNNING,
    )
    await db.refresh(protocol_run)
    assert protocol_run.status == ProtocolRunStatusEnum.RUNNING
    assert protocol_run.start_time is not None

    await asyncio.sleep(0.01)

    await update_protocol_run_status(
      db, protocol_run.accession_id, ProtocolRunStatusEnum.COMPLETED,
    )
    await db.refresh(protocol_run)
    assert protocol_run.status == ProtocolRunStatusEnum.COMPLETED
    assert protocol_run.end_time is not None
    assert protocol_run.duration_ms is not None and protocol_run.duration_ms > 0

  async def test_list_protocol_runs(
    self, db: AsyncSession, protocol_run: ProtocolRunOrm,
  ):
    """Test listing protocol runs with filters."""
    pending_runs = await list_protocol_runs(db, status=ProtocolRunStatusEnum.PENDING)
    assert len(pending_runs) >= 1

    completed_runs = await list_protocol_runs(
      db, status=ProtocolRunStatusEnum.COMPLETED,
    )
    assert len(completed_runs) == 0

    runs_by_name = await list_protocol_runs(db, protocol_name="TestUpsertProtocol")
    assert len(runs_by_name) >= 1


class TestFunctionCallLogService:
  """Tests for logging function calls within a protocol run."""

  async def test_log_start_and_end(
    self,
    db: AsyncSession,
    protocol_run: ProtocolRunOrm,
    protocol_def: FunctionProtocolDefinitionOrm,
  ):
    """Test logging the start and end of a function call."""
    start_log = await log_function_call_start(
      db,
      protocol_run_orm_accession_id=protocol_run.accession_id,
      function_definition_accession_id=protocol_def.accession_id,
      sequence_in_run=1,
      input_args_json=json.dumps({"param1": 10}),
    )
    assert start_log is not None
    assert start_log.status == FunctionCallStatusEnum.SUCCESS
    assert start_log.end_time is None

    return_val = {"result": "ok"}
    end_log = await log_function_call_end(
      db,
      function_call_log_accession_id=start_log.accession_id,
      status=FunctionCallStatusEnum.SUCCESS,
      return_value_json=json.dumps(return_val),
    )
    assert end_log is not None
    assert end_log.status == FunctionCallStatusEnum.SUCCESS
    assert end_log.end_time is not None
    assert end_log.return_value_json == return_val

  async def test_read_function_call_logs_for_run(
    self,
    db: AsyncSession,
    protocol_run: ProtocolRunOrm,
    protocol_def: FunctionProtocolDefinitionOrm,
  ):
    """Test retrieving all function call logs for a specific run."""
    await log_function_call_start(
      db, protocol_run.accession_id, protocol_def.accession_id, 1, "{}",
    )
    await log_function_call_start(
      db, protocol_run.accession_id, protocol_def.accession_id, 2, "{}",
    )

    logs = await read_function_call_logs_for_run(db, protocol_run.accession_id)
    assert len(logs) == 2
    assert logs[0].sequence_in_run == 1
    assert logs[1].sequence_in_run == 2
