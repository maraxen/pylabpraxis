"""Tests for ProtocolExecutionService in praxis.backend.core.protocol_execution_service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from praxis.backend.core.protocol_execution_service import ProtocolExecutionService
from praxis.backend.models import ProtocolRunStatusEnum


@pytest.fixture
def db_session_factory():
  """Fixture for a mock database session factory."""
  return MagicMock()


@pytest.fixture
def asset_manager():
  """Fixture for a mock AssetManager."""
  return MagicMock()


@pytest.fixture
def workcell_runtime():
  """Fixture for a mock WorkcellRuntime."""
  return MagicMock()


@pytest.fixture
def scheduler():
  """Fixture for a mock ProtocolScheduler."""
  mock = MagicMock()
  mock.schedule_protocol_execution = AsyncMock(return_value=True)
  mock.get_schedule_status = AsyncMock(return_value={"status": "SCHEDULED"})
  mock.cancel_scheduled_run = AsyncMock(return_value=True)
  return mock


@pytest.fixture
def orchestrator():
  """Fixture for a mock Orchestrator."""
  mock = MagicMock()
  mock.execute_protocol = AsyncMock(return_value="protocol_run_result")
  return mock


@pytest.fixture
def service(
  db_session_factory, asset_manager, workcell_runtime, scheduler, orchestrator,
):
  """Fixture for ProtocolExecutionService with all dependencies mocked."""
  return ProtocolExecutionService(
    db_session_factory=db_session_factory,
    asset_manager=asset_manager,
    workcell_runtime=workcell_runtime,
    scheduler=scheduler,
    orchestrator=orchestrator,
  )


@pytest.mark.asyncio
async def test_execute_protocol_immediately(service, orchestrator) -> None:
  """Test immediate protocol execution bypassing the scheduler."""
  result = await service.execute_protocol_immediately(
    protocol_name="test_protocol",
    user_input_params={"foo": "bar"},
    initial_state_data={"state": 1},
    protocol_version="1.0.0",
    commit_hash="abc123",
    source_name="test_source",
  )
  orchestrator.execute_protocol.assert_awaited_once()
  assert result == "protocol_run_result"


@pytest.mark.asyncio
@patch("praxis.backend.core.protocol_execution_service.svc")
async def test_schedule_protocol_execution(mock_svc, service, scheduler) -> None:
  """Test scheduling a protocol for asynchronous execution."""
  protocol_def_orm = MagicMock()
  protocol_def_orm.accession_id = uuid.uuid4()
  mock_svc.read_protocol_definition_by_name = AsyncMock(return_value=protocol_def_orm)
  mock_svc.create_protocol_run = AsyncMock(return_value=MagicMock())
  db_session = MagicMock()
  db_session.flush = AsyncMock()
  db_session.refresh = AsyncMock()
  db_session.commit = AsyncMock()
  service.db_session_factory.return_value.__aenter__.return_value = db_session

  result = await service.schedule_protocol_execution(
    protocol_name="test_protocol",
    user_input_params={"foo": "bar"},
    initial_state_data={"state": 1},
    protocol_version="1.0.0",
    commit_hash="abc123",
    source_name="test_source",
  )
  assert result is not None
  scheduler.schedule_protocol_execution.assert_awaited_once()
  mock_svc.create_protocol_run.assert_awaited_once()


@pytest.mark.asyncio
@patch("praxis.backend.core.protocol_execution_service.svc")
async def test_get_protocol_run_status(mock_svc, service, scheduler) -> None:
  """Test getting the status of a protocol run."""
  protocol_run_id = uuid.uuid4()
  protocol_run_orm = MagicMock()
  protocol_run_orm.status = ProtocolRunStatusEnum.PREPARING
  protocol_run_orm.created_at = None
  protocol_run_orm.start_time = None
  protocol_run_orm.end_time = None
  protocol_run_orm.duration_ms = 123
  protocol_run_orm.top_level_protocol_definition = MagicMock()
  protocol_run_orm.top_level_protocol_definition.name = "test_protocol"
  protocol_run_orm.output_data_json = None
  mock_svc.read_protocol_run = AsyncMock(return_value=protocol_run_orm)
  db_session = MagicMock()
  service.db_session_factory.return_value.__aenter__.return_value = db_session

  status = await service.get_protocol_run_status(protocol_run_id)
  assert status["protocol_run_id"] == str(protocol_run_id)
  assert status["status"] == ProtocolRunStatusEnum.PREPARING.value
  assert status["schedule_info"] == {"status": "SCHEDULED"}


@pytest.mark.asyncio
@patch("praxis.backend.core.protocol_execution_service.svc")
async def test_cancel_protocol_run(mock_svc, service, scheduler) -> None:
  """Test cancelling a protocol run."""
  protocol_run_id = uuid.uuid4()
  mock_svc.update_protocol_run_status = AsyncMock()
  db_session = MagicMock()
  db_session.commit = AsyncMock()
  service.db_session_factory.return_value.__aenter__.return_value = db_session

  result = await service.cancel_protocol_run(protocol_run_id)
  scheduler.cancel_scheduled_run.assert_awaited_once_with(protocol_run_id)
  mock_svc.update_protocol_run_status.assert_awaited_once()
  db_session.commit.assert_awaited_once()
  assert result is True
