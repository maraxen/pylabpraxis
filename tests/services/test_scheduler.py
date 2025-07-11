from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Import all required models
from praxis.backend.models import (
  AssetReservationStatusEnum,
  ProtocolRunOrm,
  ScheduleEntryOrm,
  ScheduleStatusEnum,
)

# Import the service functions to be tested
from praxis.backend.services.scheduler import (
  cleanup_expired_reservations,
  create_asset_reservation,
  create_schedule_entry,
  delete_schedule_entry,
  get_schedule_history,
  get_scheduling_metrics,
  list_asset_reservations,
  list_schedule_entries,
  log_schedule_event,
  read_asset_reservation,
  read_schedule_entry,
  read_schedule_entry_by_protocol_run,
  update_asset_reservation_status,
  update_schedule_entry_status,
)

# --- Pytest Fixtures ---


@pytest.fixture
async def protocol_run(db: AsyncSession) -> ProtocolRunOrm:
  """Fixture for a ProtocolRunOrm instance."""
  run = ProtocolRunOrm(name="Test Run for Scheduling")
  db.add(run)
  await db.commit()
  return run


@pytest.fixture
async def schedule_entry(
  db: AsyncSession, protocol_run: ProtocolRunOrm,
) -> ScheduleEntryOrm:
  """Fixture that creates a standard schedule entry for testing."""
  return await create_schedule_entry(db, protocol_run.accession_id, priority=5)


pytestmark = pytest.mark.asyncio

# --- Test Classes ---


class TestScheduleEntryService:
  """Tests for schedule entry management."""

  async def test_create_and_read_schedule_entry(
    self, db: AsyncSession, protocol_run: ProtocolRunOrm,
  ) -> None:
    """Test creating a schedule entry and reading it back."""
    entry = await create_schedule_entry(
      db, protocol_run_accession_id=protocol_run.accession_id, priority=10,
    )
    assert entry.protocol_run_accession_id == protocol_run.accession_id
    assert entry.status == ScheduleStatusEnum.QUEUED
    assert entry.priority == 10

    # Test read by ID
    read_by_id = await read_schedule_entry(db, entry.accession_id)
    assert read_by_id is not None
    assert read_by_id.priority == 10

    # Test read by protocol run ID
    read_by_run = await read_schedule_entry_by_protocol_run(
      db, protocol_run.accession_id,
    )
    assert read_by_run is not None
    assert read_by_run.accession_id == entry.accession_id

  async def test_create_duplicate_schedule_entry_fails(
    self, db: AsyncSession, schedule_entry: ScheduleEntryOrm,
  ) -> None:
    """Test that creating a schedule entry for an already scheduled run fails."""
    with pytest.raises(ValueError, match="already exists"):
      await create_schedule_entry(db, schedule_entry.protocol_run_accession_id)

  async def test_update_schedule_entry_status(
    self, db: AsyncSession, schedule_entry: ScheduleEntryOrm,
  ) -> None:
    """Test updating the status of a schedule entry."""
    updated_entry = await update_schedule_entry_status(
      db, schedule_entry.accession_id, new_status=ScheduleStatusEnum.RUNNING,
    )
    assert updated_entry is not None
    assert updated_entry.status == ScheduleStatusEnum.RUNNING

  async def test_list_schedule_entries_with_filters(
    self, db: AsyncSession, schedule_entry: ScheduleEntryOrm,
  ) -> None:
    """Test filtering and ordering when listing schedule entries."""
    # Create another entry to test filtering
    other_run = ProtocolRunOrm(name="Other Run")
    db.add(other_run)
    await db.commit()
    await create_schedule_entry(db, other_run.accession_id, priority=1)

    # Filter by priority
    high_prio_entries = await list_schedule_entries(db, priority_min=5)
    assert len(high_prio_entries) == 1
    assert high_prio_entries[0].accession_id == schedule_entry.accession_id

    # Test ordering
    all_entries_prio_asc = await list_schedule_entries(
      db, order_by="priority", order_desc=False,
    )
    assert len(all_entries_prio_asc) == 2
    assert all_entries_prio_asc[0].priority == 1
    assert all_entries_prio_asc[1].priority == 5

  async def test_delete_schedule_entry(
    self, db: AsyncSession, schedule_entry: ScheduleEntryOrm,
  ) -> None:
    """Test deleting a schedule entry."""
    entry_id = schedule_entry.accession_id
    result = await delete_schedule_entry(db, entry_id)
    assert result is True
    assert await read_schedule_entry(db, entry_id) is None


class TestAssetReservationService:
  """Tests for asset reservation management."""

  async def test_create_and_read_asset_reservation(
    self, db: AsyncSession, schedule_entry: ScheduleEntryOrm,
  ) -> None:
    """Test creating and reading an asset reservation."""
    reservation = await create_asset_reservation(
      db,
      schedule_entry.accession_id,
      asset_type="machine",
      asset_name="Hamilton_STAR_1",
    )
    assert reservation.schedule_entry_accession_id == schedule_entry.accession_id
    assert reservation.status == AssetReservationStatusEnum.PENDING

    read_res = await read_asset_reservation(db, reservation.accession_id)
    assert read_res is not None
    assert read_res.asset_name == "Hamilton_STAR_1"

  async def test_update_asset_reservation_status(
    self, db: AsyncSession, schedule_entry: ScheduleEntryOrm,
  ) -> None:
    """Test updating the status of an asset reservation."""
    reservation = await create_asset_reservation(
      db, schedule_entry.accession_id, "plate", "plate_1",
    )
    updated_res = await update_asset_reservation_status(
      db, reservation.accession_id, new_status=AssetReservationStatusEnum.RESERVED,
    )
    assert updated_res is not None
    assert updated_res.status == AssetReservationStatusEnum.RESERVED

  async def test_cleanup_expired_reservations(
    self, db: AsyncSession, schedule_entry: ScheduleEntryOrm,
  ) -> None:
    """Test cleaning up reservations that have expired."""
    now = datetime.now(timezone.utc)
    # Create one expired and one non-expired reservation
    await create_asset_reservation(
      db,
      schedule_entry.accession_id,
      "expiring_asset",
      "asset1",
      expires_at=now - timedelta(minutes=1),
    )
    await create_asset_reservation(
      db,
      schedule_entry.accession_id,
      "active_asset",
      "asset2",
      expires_at=now + timedelta(minutes=10),
    )
    await db.commit()

    cleaned_count = await cleanup_expired_reservations(db)
    await db.commit()
    assert cleaned_count == 1

    reservations = await list_asset_reservations(
      db, schedule_entry_accession_id=schedule_entry.accession_id, limit=10,
    )
    expired_found = False
    active_found = False
    for res in reservations:
      if res.asset_name == "asset1":
        assert res.status == AssetReservationStatusEnum.EXPIRED
        expired_found = True
      elif res.asset_name == "asset2":
        assert res.status == AssetReservationStatusEnum.PENDING
        active_found = True
    assert expired_found
    assert active_found


class TestScheduleHistoryService:
  """Tests for schedule history and metrics."""

  async def test_log_schedule_event_and_get_history(
    self, db: AsyncSession, schedule_entry: ScheduleEntryOrm,
  ) -> None:
    """Test that events are logged and can be retrieved."""
    # The 'create' call already logged one event. Now log another.
    await log_schedule_event(
      db, schedule_entry.accession_id, "TEST_EVENT", message="A custom test event.",
    )
    await db.commit()

    history = await get_schedule_history(db, schedule_entry.accession_id)
    assert len(history) == 2
    # Check ordering (most recent first)
    assert history[0].event_type == "TEST_EVENT"
    assert history[1].event_type == "SCHEDULE_CREATED"

  async def test_get_scheduling_metrics(
    self, db: AsyncSession, schedule_entry: ScheduleEntryOrm,
  ) -> None:
    """Test the aggregation of scheduling metrics."""
    start_time = datetime.now(timezone.utc) - timedelta(seconds=1)

    # Create some history
    await update_schedule_entry_status(
      db, schedule_entry.accession_id, ScheduleStatusEnum.DISPATCHED,
    )
    await update_schedule_entry_status(
      db,
      schedule_entry.accession_id,
      ScheduleStatusEnum.FAILED,
      error_details="Test error",
    )
    # Manually log an event with duration
    await log_schedule_event(
      db, schedule_entry.accession_id, "ANALYSIS_COMPLETE", duration_ms=150,
    )
    await db.commit()

    end_time = datetime.now(timezone.utc) + timedelta(seconds=1)
    metrics = await get_scheduling_metrics(db, start_time, end_time)

    assert metrics is not None
    # status_counts includes the initial create, plus the 2 updates
    assert metrics["status_counts"]["QUEUED"] == 1
    assert metrics["status_counts"]["DISPATCHED"] == 1
    assert metrics["status_counts"]["FAILED"] == 1
    assert metrics["total_events"] == 3
    assert metrics["error_count"] == 1
    assert metrics["avg_duration_ms"] == 150
