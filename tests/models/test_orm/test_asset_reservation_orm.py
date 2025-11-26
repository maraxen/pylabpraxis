"""Unit tests for AssetReservationOrm model.
"""
from collections.abc import Callable
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.enums import (
    AssetReservationStatusEnum,
    AssetType,
)
from praxis.backend.models.orm.machine import MachineOrm
from praxis.backend.models.orm.protocol import (
    FileSystemProtocolSourceOrm,
    FunctionProtocolDefinitionOrm,
    ProtocolRunOrm,
    ProtocolSourceRepositoryOrm,
)
from praxis.backend.models.orm.schedule import AssetReservationOrm, ScheduleEntryOrm
from praxis.backend.utils.uuid import uuid7


@pytest_asyncio.fixture
async def source_repository(db_session: AsyncSession) -> ProtocolSourceRepositoryOrm:
    """Create a ProtocolSourceRepositoryOrm for testing."""
    repo = ProtocolSourceRepositoryOrm(
        name="test-repo",
        git_url="https://github.com/test/repo.git",
    )
    db_session.add(repo)
    await db_session.flush()
    return repo


@pytest_asyncio.fixture
async def file_system_source(db_session: AsyncSession) -> FileSystemProtocolSourceOrm:
    """Create a FileSystemProtocolSourceOrm for testing."""
    source = FileSystemProtocolSourceOrm(
        name="test-fs-source",
        base_path="/tmp/protocols",
    )
    db_session.add(source)
    await db_session.flush()
    return source


@pytest_asyncio.fixture
async def protocol_definition(
    db_session: AsyncSession,
    source_repository: ProtocolSourceRepositoryOrm,
    file_system_source: FileSystemProtocolSourceOrm,
) -> FunctionProtocolDefinitionOrm:
    """Create a FunctionProtocolDefinitionOrm for testing."""
    protocol = FunctionProtocolDefinitionOrm(
        name="test_protocol",
        fqn="test.protocols.test_protocol",
        version="1.0.0",
        is_top_level=True,
        source_repository=source_repository,
        file_system_source=file_system_source,
    )
    db_session.add(protocol)
    await db_session.flush()
    return protocol


@pytest_asyncio.fixture
def protocol_run_factory(
    db_session: AsyncSession,
    protocol_definition: FunctionProtocolDefinitionOrm,
) -> Callable[[], ProtocolRunOrm]:
    """Create a ProtocolRunOrm factory for testing."""

    async def _factory() -> ProtocolRunOrm:
        run = ProtocolRunOrm(
            name="test_protocol_run",
            top_level_protocol_definition_accession_id=protocol_definition.accession_id,
        )
        db_session.add(run)
        await db_session.flush()
        return run

    return _factory


@pytest_asyncio.fixture
def schedule_entry_factory(
    db_session: AsyncSession,
) -> Callable[[ProtocolRunOrm], ScheduleEntryOrm]:
    """Create a ScheduleEntryOrm factory for testing."""

    async def _factory(protocol_run: ProtocolRunOrm) -> ScheduleEntryOrm:
        entry = ScheduleEntryOrm(
            protocol_run=protocol_run,
            name="test_schedule_entry",
            scheduled_at=datetime.now(timezone.utc),
            asset_analysis_completed_at=None,
            assets_reserved_at=None,
            execution_started_at=None,
            execution_completed_at=None,
        )
        db_session.add(entry)
        await db_session.flush()
        return entry

    return _factory


@pytest_asyncio.fixture
async def machine_asset(db_session: AsyncSession) -> MachineOrm:
    """Create a MachineOrm asset for reservation testing."""
    machine = MachineOrm(
        accession_id=uuid7(),
        name="test_machine_reservation",
        fqn="test.machines.TestMachine",
        asset_type=AssetType.MACHINE,
    )
    db_session.add(machine)
    await db_session.flush()
    return machine


@pytest.mark.asyncio
async def test_asset_reservation_orm_creation_minimal(
    db_session: AsyncSession,
    protocol_run_factory: Callable[[], ProtocolRunOrm],
    schedule_entry_factory: Callable[[ProtocolRunOrm], ScheduleEntryOrm],
    machine_asset: MachineOrm,
) -> None:
    """Test creating AssetReservationOrm with minimal required fields."""
    protocol_run = await protocol_run_factory()
    schedule_entry = await schedule_entry_factory(protocol_run)
    reservation = AssetReservationOrm(
        name="test_reservation",
        protocol_run_accession_id=protocol_run.accession_id,
        schedule_entry_accession_id=schedule_entry.accession_id,
        asset_accession_id=machine_asset.accession_id,
        asset_name=machine_asset.name,
        redis_lock_key=f"lock:{machine_asset.accession_id}",
        released_at=None,
    )

    db_session.add(reservation)
    await db_session.flush()

    assert reservation.accession_id is not None
    assert reservation.protocol_run_accession_id == protocol_run.accession_id
    assert reservation.schedule_entry_accession_id == schedule_entry.accession_id
    assert reservation.asset_accession_id == machine_asset.accession_id
    assert reservation.asset_name == machine_asset.name
    assert reservation.redis_lock_key == f"lock:{machine_asset.accession_id}"
    assert reservation.asset_type == AssetType.ASSET
    assert reservation.status == AssetReservationStatusEnum.PENDING
    assert reservation.lock_timeout_seconds == 3600
    assert reservation.redis_lock_value is None
    assert reservation.reserved_at is not None
    assert reservation.released_at is None


@pytest.mark.asyncio
async def test_asset_reservation_orm_creation_with_all_fields(
    db_session: AsyncSession,
    protocol_run_factory: Callable[[], ProtocolRunOrm],
    schedule_entry_factory: Callable[[ProtocolRunOrm], ScheduleEntryOrm],
    machine_asset: MachineOrm,
) -> None:
    """Test creating AssetReservationOrm with all fields populated."""
    protocol_run = await protocol_run_factory()
    schedule_entry = await schedule_entry_factory(protocol_run)
    now = datetime.now(timezone.utc)
    reservation = AssetReservationOrm(
        name="test_reservation_all_fields",
        protocol_run_accession_id=protocol_run.accession_id,
        schedule_entry_accession_id=schedule_entry.accession_id,
        asset_accession_id=machine_asset.accession_id,
        asset_name=machine_asset.name,
        redis_lock_key=f"lock:{machine_asset.accession_id}",
        status=AssetReservationStatusEnum.RESERVED,
        redis_lock_value="test_lock_value",
        lock_timeout_seconds=60,
        released_at=now,
    )
    db_session.add(reservation)
    await db_session.flush()

    assert reservation.status == AssetReservationStatusEnum.RESERVED
    assert reservation.redis_lock_value == "test_lock_value"
    assert reservation.lock_timeout_seconds == 60
    assert reservation.released_at == now


@pytest.mark.asyncio
async def test_asset_reservation_orm_persist_to_database(
    db_session: AsyncSession,
    protocol_run_factory: Callable[[], ProtocolRunOrm],
    schedule_entry_factory: Callable[[ProtocolRunOrm], ScheduleEntryOrm],
    machine_asset: MachineOrm,
) -> None:
    """Test full persistence cycle for AssetReservationOrm."""
    protocol_run = await protocol_run_factory()
    schedule_entry = await schedule_entry_factory(protocol_run)
    reservation = AssetReservationOrm(
        name="test_reservation_persist",
        protocol_run_accession_id=protocol_run.accession_id,
        schedule_entry_accession_id=schedule_entry.accession_id,
        asset_accession_id=machine_asset.accession_id,
        asset_name=machine_asset.name,
        redis_lock_key=f"lock:{machine_asset.accession_id}",
        released_at=None,
    )
    db_session.add(reservation)
    await db_session.commit()

    result = await db_session.execute(
        select(AssetReservationOrm).where(
            AssetReservationOrm.accession_id == reservation.accession_id,
        ),
    )
    retrieved_reservation = result.scalar_one()

    assert retrieved_reservation is not None
    assert retrieved_reservation.accession_id == reservation.accession_id
    assert retrieved_reservation.asset_name == machine_asset.name


@pytest.mark.asyncio
async def test_asset_reservation_orm_status_transitions(
    db_session: AsyncSession,
    protocol_run_factory: Callable[[], ProtocolRunOrm],
    schedule_entry_factory: Callable[[ProtocolRunOrm], ScheduleEntryOrm],
    machine_asset: MachineOrm,
) -> None:
    """Test different status values for asset reservations."""
    for status in AssetReservationStatusEnum:
        protocol_run = await protocol_run_factory()
        schedule_entry = await schedule_entry_factory(protocol_run)
        reservation = AssetReservationOrm(
            name=f"test_reservation_{status.value}",
            protocol_run_accession_id=protocol_run.accession_id,
            schedule_entry_accession_id=schedule_entry.accession_id,
            asset_accession_id=machine_asset.accession_id,
            asset_name=machine_asset.name,
            redis_lock_key=f"lock:{machine_asset.accession_id}:{status.value}",
            status=status,
            released_at=None,
        )
        db_session.add(reservation)

    await db_session.flush()

    for status in AssetReservationStatusEnum:
        result = await db_session.execute(
            select(AssetReservationOrm).where(AssetReservationOrm.status == status),
        )
        reservation = result.scalar_one_or_none()
        assert reservation is not None
        assert reservation.status == status


@pytest.mark.asyncio
async def test_asset_reservation_orm_redis_lock_fields(
    db_session: AsyncSession,
    protocol_run_factory: Callable[[], ProtocolRunOrm],
    schedule_entry_factory: Callable[[ProtocolRunOrm], ScheduleEntryOrm],
    machine_asset: MachineOrm,
) -> None:
    """Test Redis lock tracking fields."""
    protocol_run = await protocol_run_factory()
    schedule_entry = await schedule_entry_factory(protocol_run)
    reservation = AssetReservationOrm(
        name="test_reservation_redis",
        protocol_run_accession_id=protocol_run.accession_id,
        schedule_entry_accession_id=schedule_entry.accession_id,
        asset_accession_id=machine_asset.accession_id,
        asset_name=machine_asset.name,
        redis_lock_key="test_lock_key",
        redis_lock_value="test_lock_value",
        lock_timeout_seconds=120,
        released_at=None,
    )
    db_session.add(reservation)
    await db_session.flush()

    assert reservation.redis_lock_key == "test_lock_key"
    assert reservation.redis_lock_value == "test_lock_value"
    assert reservation.lock_timeout_seconds == 120


@pytest.mark.asyncio
async def test_asset_reservation_orm_timing_fields(
    db_session: AsyncSession,
    protocol_run_factory: Callable[[], ProtocolRunOrm],
    schedule_entry_factory: Callable[[ProtocolRunOrm], ScheduleEntryOrm],
    machine_asset: MachineOrm,
) -> None:
    """Test reservation timing fields."""
    protocol_run = await protocol_run_factory()
    schedule_entry = await schedule_entry_factory(protocol_run)
    now = datetime.now(timezone.utc)
    reservation = AssetReservationOrm(
        name="test_reservation_timing",
        protocol_run_accession_id=protocol_run.accession_id,
        schedule_entry_accession_id=schedule_entry.accession_id,
        asset_accession_id=machine_asset.accession_id,
        asset_name=machine_asset.name,
        redis_lock_key=f"lock:{machine_asset.accession_id}",
        released_at=now,
    )
    db_session.add(reservation)
    await db_session.flush()

    assert reservation.reserved_at is not None
    assert reservation.released_at == now


@pytest.mark.asyncio
async def test_asset_reservation_orm_asset_type_field(
    db_session: AsyncSession,
    protocol_run_factory: Callable[[], ProtocolRunOrm],
    schedule_entry_factory: Callable[[ProtocolRunOrm], ScheduleEntryOrm],
    machine_asset: MachineOrm,
) -> None:
    """Test asset_type field for different asset types."""
    for asset_type in list(AssetType):
        protocol_run = await protocol_run_factory()
        schedule_entry = await schedule_entry_factory(protocol_run)
        reservation = AssetReservationOrm(
            name=f"test_reservation_{asset_type.value}",
            protocol_run_accession_id=protocol_run.accession_id,
            schedule_entry_accession_id=schedule_entry.accession_id,
            asset_accession_id=machine_asset.accession_id,
            asset_name=machine_asset.name,
            redis_lock_key=f"lock:{machine_asset.accession_id}:{asset_type.value}",
            asset_type=asset_type,
            released_at=None,
        )
        db_session.add(reservation)

    await db_session.flush()

    for asset_type in list(AssetType):
        result = await db_session.execute(
            select(AssetReservationOrm).where(
                AssetReservationOrm.asset_type == asset_type,
            ),
        )
        reservation = result.scalars().first()
        assert reservation is not None
        assert reservation.asset_type == asset_type


@pytest.mark.asyncio
async def test_asset_reservation_orm_relationship_to_protocol_run(
    db_session: AsyncSession,
    protocol_run_factory: Callable[[], ProtocolRunOrm],
    schedule_entry_factory: Callable[[ProtocolRunOrm], ScheduleEntryOrm],
    machine_asset: MachineOrm,
) -> None:
    """Test relationship between AssetReservationOrm and ProtocolRunOrm."""
    protocol_run = await protocol_run_factory()
    schedule_entry = await schedule_entry_factory(protocol_run)
    reservation = AssetReservationOrm(
        name="test_reservation_relationship_run",
        protocol_run_accession_id=protocol_run.accession_id,
        schedule_entry_accession_id=schedule_entry.accession_id,
        asset_accession_id=machine_asset.accession_id,
        asset_name=machine_asset.name,
        redis_lock_key=f"lock:{machine_asset.accession_id}",
        released_at=None,
    )
    reservation.protocol_run = protocol_run
    db_session.add(reservation)
    await db_session.flush()

    assert reservation.protocol_run_accession_id == protocol_run.accession_id
    assert reservation.protocol_run == protocol_run
    await db_session.refresh(protocol_run, ["asset_reservations"])
    assert reservation in protocol_run.asset_reservations


@pytest.mark.asyncio
async def test_asset_reservation_orm_relationship_to_schedule_entry(
    db_session: AsyncSession,
    protocol_run_factory: Callable[[], ProtocolRunOrm],
    schedule_entry_factory: Callable[[ProtocolRunOrm], ScheduleEntryOrm],
    machine_asset: MachineOrm,
) -> None:
    """Test relationship between AssetReservationOrm and ScheduleEntryOrm."""
    protocol_run = await protocol_run_factory()
    schedule_entry = await schedule_entry_factory(protocol_run)
    reservation = AssetReservationOrm(
        name="test_reservation_relationship_schedule",
        protocol_run_accession_id=protocol_run.accession_id,
        schedule_entry_accession_id=schedule_entry.accession_id,
        asset_accession_id=machine_asset.accession_id,
        asset_name=machine_asset.name,
        redis_lock_key=f"lock:{machine_asset.accession_id}",
        released_at=None,
    )
    reservation.schedule_entry = schedule_entry
    db_session.add(reservation)
    await db_session.flush()

    assert reservation.schedule_entry_accession_id == schedule_entry.accession_id
    assert reservation.schedule_entry == schedule_entry
    await db_session.refresh(schedule_entry, ["asset_reservations"])
    assert reservation in schedule_entry.asset_reservations


@pytest.mark.asyncio
async def test_asset_reservation_orm_relationship_to_asset(
    db_session: AsyncSession,
    protocol_run_factory: Callable[[], ProtocolRunOrm],
    schedule_entry_factory: Callable[[ProtocolRunOrm], ScheduleEntryOrm],
    machine_asset: MachineOrm,
) -> None:
    """Test relationship between AssetReservationOrm and AssetOrm."""
    protocol_run = await protocol_run_factory()
    schedule_entry = await schedule_entry_factory(protocol_run)
    reservation = AssetReservationOrm(
        name="test_reservation_relationship_asset",
        protocol_run_accession_id=protocol_run.accession_id,
        schedule_entry_accession_id=schedule_entry.accession_id,
        asset_accession_id=machine_asset.accession_id,
        asset_name=machine_asset.name,
        redis_lock_key=f"lock:{machine_asset.accession_id}",
        released_at=None,
    )
    reservation.asset = machine_asset
    db_session.add(reservation)
    await db_session.flush()

    assert reservation.asset_accession_id == machine_asset.accession_id
    assert reservation.asset == machine_asset
    await db_session.refresh(machine_asset, ["asset_reservations"])
    assert reservation in machine_asset.asset_reservations


@pytest.mark.asyncio
async def test_asset_reservation_orm_query_by_status(
    db_session: AsyncSession,
    protocol_run_factory: Callable[[], ProtocolRunOrm],
    schedule_entry_factory: Callable[[ProtocolRunOrm], ScheduleEntryOrm],
    machine_asset: MachineOrm,
) -> None:
    """Test querying asset reservations by status."""
    statuses = [
        AssetReservationStatusEnum.PENDING,
        AssetReservationStatusEnum.RESERVED,
        AssetReservationStatusEnum.PENDING,
    ]
    for i, status in enumerate(statuses):
        run = await protocol_run_factory()
        entry = await schedule_entry_factory(run)
        reservation = AssetReservationOrm(
            name=f"test_reservation_{i}",
            protocol_run_accession_id=run.accession_id,
            schedule_entry_accession_id=entry.accession_id,
            asset_accession_id=machine_asset.accession_id,
            asset_name=machine_asset.name,
            redis_lock_key=f"lock:{machine_asset.accession_id}:{i}",
            status=status,
            released_at=None,
        )
        db_session.add(reservation)
    await db_session.flush()

    result = await db_session.execute(
        select(AssetReservationOrm).where(
            AssetReservationOrm.status == AssetReservationStatusEnum.PENDING,
        ),
    )
    pending_reservations = result.scalars().all()
    assert len(pending_reservations) == 2

    result = await db_session.execute(
        select(AssetReservationOrm).where(
            AssetReservationOrm.status == AssetReservationStatusEnum.RESERVED,
        ),
    )
    reserved_reservations = result.scalars().all()
    assert len(reserved_reservations) == 1


@pytest.mark.asyncio
async def test_asset_reservation_orm_query_active_reservations(
    db_session: AsyncSession,
    protocol_run_factory: Callable[[], ProtocolRunOrm],
    schedule_entry_factory: Callable[[ProtocolRunOrm], ScheduleEntryOrm],
    machine_asset: MachineOrm,
) -> None:
    """Test querying currently active asset reservations."""
    statuses = [
        AssetReservationStatusEnum.ACTIVE,
        AssetReservationStatusEnum.RESERVED,
        AssetReservationStatusEnum.PENDING,
    ]
    for i, status in enumerate(statuses):
        run = await protocol_run_factory()
        entry = await schedule_entry_factory(run)
        reservation = AssetReservationOrm(
            name=f"test_reservation_{i}",
            protocol_run_accession_id=run.accession_id,
            schedule_entry_accession_id=entry.accession_id,
            asset_accession_id=machine_asset.accession_id,
            asset_name=machine_asset.name,
            redis_lock_key=f"lock:{machine_asset.accession_id}:{i}",
            status=status,
            released_at=None,
        )
        db_session.add(reservation)
    await db_session.flush()

    result = await db_session.execute(
        select(AssetReservationOrm).where(
            AssetReservationOrm.status.in_(
                [
                    AssetReservationStatusEnum.ACTIVE,
                    AssetReservationStatusEnum.RESERVED,
                ],
            ),
        ),
    )
    active_reservations = result.scalars().all()
    assert len(active_reservations) == 2


@pytest.mark.asyncio
async def test_asset_reservation_orm_query_by_asset(
    db_session: AsyncSession,
    protocol_run_factory: Callable[[], ProtocolRunOrm],
    schedule_entry_factory: Callable[[ProtocolRunOrm], ScheduleEntryOrm],
    machine_asset: MachineOrm,
) -> None:
    """Test querying reservations for a specific asset."""
    for i in range(3):
        run = await protocol_run_factory()
        entry = await schedule_entry_factory(run)
        reservation = AssetReservationOrm(
            name=f"test_reservation_{i}",
            protocol_run_accession_id=run.accession_id,
            schedule_entry_accession_id=entry.accession_id,
            asset_accession_id=machine_asset.accession_id,
            asset_name=machine_asset.name,
            redis_lock_key=f"lock:{machine_asset.accession_id}:{i}",
            released_at=None,
        )
        db_session.add(reservation)
    await db_session.flush()

    result = await db_session.execute(
        select(AssetReservationOrm).where(
            AssetReservationOrm.asset_accession_id == machine_asset.accession_id,
        ),
    )
    reservations = result.scalars().all()
    assert len(reservations) == 3


@pytest.mark.asyncio
async def test_multiple_reservations_for_same_run(
    db_session: AsyncSession,
    protocol_run_factory: Callable[[], ProtocolRunOrm],
    schedule_entry_factory: Callable[[ProtocolRunOrm], ScheduleEntryOrm],
    machine_asset: MachineOrm,
) -> None:
    """Test that multiple asset reservations can be created for the same protocol run."""
    protocol_run = await protocol_run_factory()
    schedule_entry = await schedule_entry_factory(protocol_run)

    reservation1 = AssetReservationOrm(
        name="test_reservation_1",
        protocol_run_accession_id=protocol_run.accession_id,
        schedule_entry_accession_id=schedule_entry.accession_id,
        asset_accession_id=machine_asset.accession_id,
        asset_name=machine_asset.name,
        redis_lock_key=f"lock:{machine_asset.accession_id}:1",
        released_at=None,
    )
    db_session.add(reservation1)

    # Create another asset to reserve
    machine2 = MachineOrm(
        accession_id=uuid7(),
        name="test_machine_reservation_2",
        fqn="test.machines.TestMachine2",
        asset_type=AssetType.MACHINE,
    )
    db_session.add(machine2)
    await db_session.flush()

    reservation2 = AssetReservationOrm(
        name="test_reservation_2",
        protocol_run_accession_id=protocol_run.accession_id,
        schedule_entry_accession_id=schedule_entry.accession_id,
        asset_accession_id=machine2.accession_id,
        asset_name=machine2.name,
        redis_lock_key=f"lock:{machine2.accession_id}:2",
        released_at=None,
    )
    db_session.add(reservation2)
    await db_session.flush()

    result = await db_session.execute(
        select(AssetReservationOrm).where(
            AssetReservationOrm.protocol_run_accession_id == protocol_run.accession_id,
        ),
    )
    reservations = result.scalars().all()
    assert len(reservations) == 2
