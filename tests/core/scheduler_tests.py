"""Unit tests for the ProtocolScheduler."""

import uuid
from datetime import datetime
from unittest.mock import ANY, AsyncMock, MagicMock, patch

import pytest

from praxis.backend.core.scheduler import ProtocolScheduler, ScheduleEntry, TaskQueue
from praxis.backend.models.orm.protocol import (
    FunctionProtocolDefinitionOrm,
    ProtocolRunOrm,
)
from praxis.backend.models.pydantic_internals.protocol import (
    AssetRequirementModel,
    ProtocolRunStatusEnum,
)
from praxis.backend.models.pydantic_internals.runtime import (
    RuntimeAssetRequirement,
)
from praxis.backend.services.protocol_definition import ProtocolDefinitionCRUDService
from praxis.backend.services.protocols import ProtocolRunService


@pytest.fixture
def mock_db_session():
    """Fixture for a mock async database session."""
    session = AsyncMock()
    session.commit = AsyncMock()
    return session


@pytest.fixture
def db_session_factory(mock_db_session):
    """Fixture for a mock async session factory."""
    factory = MagicMock()
    factory.return_value.__aenter__.return_value = mock_db_session
    return factory


@pytest.fixture
def mock_task_queue():
    """Fixture for a mock TaskQueue."""
    return MagicMock(spec=TaskQueue)


@pytest.fixture
def mock_protocol_run_service():
    """Fixture for a mock ProtocolRunService."""
    return MagicMock(spec=ProtocolRunService)


@pytest.fixture
def mock_protocol_definition_service():
    """Fixture for a mock ProtocolDefinitionCRUDService."""
    return MagicMock(spec=ProtocolDefinitionCRUDService)


@pytest.fixture
def scheduler(
    db_session_factory,
    mock_task_queue,
    mock_protocol_run_service,
    mock_protocol_definition_service,
):
    """Fixture for a ProtocolScheduler instance."""
    return ProtocolScheduler(
        db_session_factory=db_session_factory,
        task_queue=mock_task_queue,
        protocol_run_service=mock_protocol_run_service,
        protocol_definition_service=mock_protocol_definition_service,
    )


@pytest.fixture
def protocol_def_orm():
    """Fixture for a mock FunctionProtocolDefinitionOrm."""
    asset_def = MagicMock(spec=AssetRequirementModel)
    asset_def.name = "test_asset"
    asset_def.fqn = "pylabrobot.resources.Resource"
    asset_def.accession_id = uuid.uuid4()
    asset_def.constraints = {}
    asset_def.location_constraints = {}
    asset_def.optional = False

    proto_def = MagicMock(spec=FunctionProtocolDefinitionOrm)
    proto_def.name = "test_protocol"
    proto_def.version = "1.0"
    proto_def.assets = [asset_def]
    proto_def.preconfigure_deck = True
    proto_def.deck_param_name = "deck"
    proto_def.accession_id = uuid.uuid4()
    return proto_def


@pytest.fixture
def protocol_run_orm(protocol_def_orm):
    """Fixture for a mock ProtocolRunOrm."""
    run = MagicMock(spec=ProtocolRunOrm)
    run.accession_id = uuid.uuid4()
    run.top_level_protocol_definition = protocol_def_orm
    run.top_level_protocol_definition_accession_id = protocol_def_orm.accession_id
    return run


@pytest.fixture
def runtime_asset_requirement():
    """Fixture for a mock RuntimeAssetRequirement."""
    req = MagicMock(spec=RuntimeAssetRequirement)
    req.asset_type = "asset"
    req.asset_definition.name = "test_asset"
    return req


def test_schedule_entry_init(runtime_asset_requirement) -> None:
    """Test ScheduleEntry initialization."""
    run_id = uuid.uuid4()
    assets = [runtime_asset_requirement]
    entry = ScheduleEntry(
        protocol_run_id=run_id,
        protocol_name="test_proto",
        required_assets=assets,
        estimated_duration_ms=1000,
        priority=5,
    )
    assert entry.protocol_run_id == run_id
    assert entry.protocol_name == "test_proto"
    assert entry.required_assets == assets
    assert entry.estimated_duration_ms == 1000
    assert entry.priority == 5
    assert entry.status == "QUEUED"
    assert isinstance(entry.scheduled_at, datetime)
    assert entry.celery_task_id is None


@pytest.mark.asyncio
async def test_analyze_protocol_requirements(scheduler, protocol_def_orm) -> None:
    """Test asset requirement analysis."""
    requirements = await scheduler.analyze_protocol_requirements(protocol_def_orm, {})

    assert len(requirements) == 2
    asset_req = requirements[0]
    assert asset_req.asset_definition.name == "test_asset"
    assert asset_req.asset_type == "asset"

    deck_req = requirements[1]
    assert deck_req.asset_definition.name == "deck"
    assert deck_req.asset_type == "deck"
    assert deck_req.asset_definition.fqn == "pylabrobot.resources.Deck"


@pytest.mark.asyncio
async def test_reserve_assets_success(scheduler) -> None:
    """Test successful asset reservation."""
    run_id = uuid.uuid4()
    req = MagicMock(spec=RuntimeAssetRequirement)
    req.asset_type = "asset"
    req.asset_definition.name = "test_asset"
    requirements = [req]

    success = await scheduler.reserve_assets(requirements, run_id)

    assert success is True
    assert scheduler._asset_reservations["asset:test_asset"] == {run_id}
    assert req.reservation_id is not None


@pytest.mark.asyncio
async def test_reserve_assets_failure_and_rollback(scheduler) -> None:
    """Test failed asset reservation and rollback."""
    run_id_1 = uuid.uuid4()
    run_id_2 = uuid.uuid4()
    req = MagicMock(spec=RuntimeAssetRequirement)
    req.asset_type = "asset"
    req.asset_definition.name = "test_asset"
    requirements = [req]

    scheduler._asset_reservations["asset:test_asset"] = {run_id_1}

    success = await scheduler.reserve_assets(requirements, run_id_2)

    assert success is False
    assert scheduler._asset_reservations["asset:test_asset"] == {run_id_1}


@pytest.mark.asyncio
async def test_schedule_protocol_execution_success(
    scheduler, protocol_run_orm
) -> None:
    """Test successful scheduling of a protocol."""
    scheduler.task_queue.send_task.return_value = MagicMock(id="test_task_id")
    scheduler.analyze_protocol_requirements = AsyncMock(return_value=[])
    scheduler.reserve_assets = AsyncMock(return_value=True)

    success = await scheduler.schedule_protocol_execution(protocol_run_orm, {}, None)

    assert success is True
    scheduler.protocol_run_service.update.assert_called_with(
        db=ANY,
        db_obj=protocol_run_orm,
        obj_in=ANY,
    )
    scheduler.task_queue.send_task.assert_called_once()
    assert protocol_run_orm.accession_id in scheduler._active_schedules


@pytest.mark.asyncio
async def test_schedule_protocol_asset_failure(
    scheduler, protocol_run_orm
) -> None:
    """Test scheduling failure due to asset reservation."""
    scheduler.analyze_protocol_requirements = AsyncMock(return_value=[])
    scheduler.reserve_assets = AsyncMock(return_value=False)

    success = await scheduler.schedule_protocol_execution(protocol_run_orm, {}, None)

    assert success is False
    scheduler.protocol_run_service.update.assert_called_with(
        db=ANY,
        db_obj=protocol_run_orm,
        obj_in=ANY,
    )
    assert protocol_run_orm.accession_id not in scheduler._active_schedules


@pytest.mark.asyncio
async def test_cancel_scheduled_run(scheduler) -> None:
    """Test cancelling a scheduled run."""
    run_id = uuid.uuid4()
    req = MagicMock(spec=RuntimeAssetRequirement)
    req.asset_type = "asset"
    req.asset_definition.name = "cancellable_asset"
    entry = ScheduleEntry(
        protocol_run_id=run_id, protocol_name="test", required_assets=[req]
    )
    scheduler._active_schedules[run_id] = entry
    scheduler._asset_reservations["asset:cancellable_asset"] = {run_id}

    success = await scheduler.cancel_scheduled_run(run_id)

    assert success is True
    assert run_id not in scheduler._active_schedules
    assert "asset:cancellable_asset" not in scheduler._asset_reservations


@pytest.mark.asyncio
async def test_get_schedule_status(scheduler) -> None:
    """Test getting schedule status."""
    run_id = uuid.uuid4()
    entry = ScheduleEntry(
        protocol_run_id=run_id, protocol_name="test", required_assets=[]
    )
    scheduler._active_schedules[run_id] = entry

    status = await scheduler.get_schedule_status(run_id)
    assert status is not None
    assert status["protocol_run_id"] == str(run_id)

    non_existent_status = await scheduler.get_schedule_status(uuid.uuid4())
    assert non_existent_status is None


@pytest.mark.asyncio
async def test_list_active_schedules(scheduler) -> None:
    """Test listing active schedules."""
    run_id1 = uuid.uuid4()
    run_id2 = uuid.uuid4()
    scheduler._active_schedules[run_id1] = ScheduleEntry(
        protocol_run_id=run_id1, protocol_name="p1", required_assets=[]
    )
    scheduler._active_schedules[run_id2] = ScheduleEntry(
        protocol_run_id=run_id2, protocol_name="p2", required_assets=[]
    )

    schedules = await scheduler.list_active_schedules()
    assert len(schedules) == 2
    run_ids = {uuid.UUID(s["protocol_run_id"]) for s in schedules}
    assert {run_id1, run_id2} == run_ids