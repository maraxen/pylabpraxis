"""Tests for the Scheduler API router.

This module tests the scheduler API endpoints, including CRUD operations
(via crud_router_factory) and custom endpoints for status and priority updates.
"""

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.enums import ScheduleStatusEnum
from praxis.backend.models.orm.protocol import (
    FileSystemProtocolSourceOrm,
    FunctionProtocolDefinitionOrm,
    ProtocolRunOrm,
    ProtocolSourceRepositoryOrm,
)
from praxis.backend.models.orm.schedule import ScheduleEntryOrm
from praxis.backend.utils.uuid import uuid7

# ============================================================================
# Fixtures
# ============================================================================


@pytest_asyncio.fixture
async def source_repository(db_session: AsyncSession) -> ProtocolSourceRepositoryOrm:
    """Create a source repository for testing."""
    repo = ProtocolSourceRepositoryOrm(
        accession_id=uuid7(),
        name=f"test_repo_{uuid4().hex[:8]}",
    )
    db_session.add(repo)
    await db_session.commit()
    await db_session.refresh(repo)
    return repo


@pytest_asyncio.fixture
async def file_system_source(db_session: AsyncSession) -> FileSystemProtocolSourceOrm:
    """Create a file system source for testing."""
    source = FileSystemProtocolSourceOrm(
        accession_id=uuid7(),
        name=f"test_source_{uuid4().hex[:8]}",
        base_path="/test/path",
    )
    db_session.add(source)
    await db_session.commit()
    await db_session.refresh(source)
    return source


@pytest_asyncio.fixture
async def protocol_definition(
    db_session: AsyncSession,
    source_repository: ProtocolSourceRepositoryOrm,
    file_system_source: FileSystemProtocolSourceOrm,
) -> FunctionProtocolDefinitionOrm:
    """Create a protocol definition for testing."""
    definition = FunctionProtocolDefinitionOrm(
        accession_id=uuid7(),
        name=f"test_protocol_{uuid4().hex[:8]}",
        source_repository_accession_id=source_repository.accession_id,
        file_system_source_accession_id=file_system_source.accession_id,
        function_name="test_function",
        fqn="test.protocol.fqn",
        version="1.0.0",
    )
    db_session.add(definition)
    await db_session.commit()
    await db_session.refresh(definition)
    return definition


@pytest_asyncio.fixture
async def protocol_run(
    db_session: AsyncSession,
    protocol_definition: FunctionProtocolDefinitionOrm,
) -> ProtocolRunOrm:
    """Create a protocol run for testing."""
    run = ProtocolRunOrm(
        accession_id=uuid7(),
        name=f"test_run_{uuid4().hex[:8]}",
        top_level_protocol_definition_accession_id=protocol_definition.accession_id,
    )
    db_session.add(run)
    await db_session.commit()
    await db_session.refresh(run)
    return run


@pytest_asyncio.fixture
async def schedule_entry(
    db_session: AsyncSession,
    protocol_run: ProtocolRunOrm,
) -> ScheduleEntryOrm:
    """Create a schedule entry for testing."""
    entry = ScheduleEntryOrm(
        accession_id=uuid7(),
        name=f"test_entry_{uuid4().hex[:8]}",
        protocol_run_accession_id=protocol_run.accession_id,
        status=ScheduleStatusEnum.QUEUED,
        priority=10,
        scheduled_at=None,
        asset_analysis_completed_at=None,
        assets_reserved_at=None,
        execution_started_at=None,
        execution_completed_at=None,
        protocol_run=protocol_run,
    )
    db_session.add(entry)
    await db_session.commit()
    await db_session.refresh(entry)
    return entry


# ============================================================================
# CRUD Router Tests (via crud_router_factory)
# ============================================================================


@pytest.mark.asyncio
async def test_list_schedule_entries(
    client: AsyncClient,
    schedule_entry: ScheduleEntryOrm,
):
    """Test listing schedule entries via GET /entries."""
    response = await client.get("/api/v1/scheduler/entries")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check our fixture entry is present
    ids = [item["accession_id"] for item in data]
    assert str(schedule_entry.accession_id) in ids


@pytest.mark.asyncio
async def test_get_schedule_entry_by_id(
    client: AsyncClient,
    schedule_entry: ScheduleEntryOrm,
):
    """Test getting a single schedule entry via GET /entries/{id}."""
    response = await client.get(
        f"/api/v1/scheduler/entries/{schedule_entry.accession_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["accession_id"] == str(schedule_entry.accession_id)
    assert data["status"] == ScheduleStatusEnum.QUEUED.value


@pytest.mark.asyncio
async def test_get_schedule_entry_not_found(client: AsyncClient):
    """Test getting a non-existent schedule entry returns 404."""
    fake_id = uuid7()
    response = await client.get(f"/api/v1/scheduler/entries/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_schedule_entry(
    client: AsyncClient,
    protocol_run: ProtocolRunOrm,
):
    """Test creating a schedule entry via POST /entries."""
    payload = {
        "name": f"api_test_entry_{uuid4().hex[:8]}",
        "protocol_run_accession_id": str(protocol_run.accession_id),
        "priority": 5,
        "status": ScheduleStatusEnum.QUEUED.value, # Explicitly valid status
    }
    # Remove trailing slash
    response = await client.post("/api/v1/scheduler/entries", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["priority"] == 5
    assert data["status"] == ScheduleStatusEnum.QUEUED.value

# ...

@pytest.mark.asyncio
async def test_update_schedule_entry_status(
    client: AsyncClient,
    schedule_entry: ScheduleEntryOrm,
):
    """Test updating schedule entry status via PUT /{id}/status."""
    # Ensure payload matches ScheduleEntryUpdate schema
    payload = {"status": ScheduleStatusEnum.EXECUTING.value}
    response = await client.put(
        f"/api/v1/scheduler/{schedule_entry.accession_id}/status",
        json=payload,
    )
    # If 422 persists, it might be due to Pydantic validation of Enum
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == ScheduleStatusEnum.EXECUTING.value


@pytest.mark.asyncio
async def test_update_schedule_entry_status_missing_status(
    client: AsyncClient,
    schedule_entry: ScheduleEntryOrm,
):
    """Test that updating status without providing status returns 400."""
    payload = {}  # Missing status
    response = await client.put(
        f"/api/v1/scheduler/{schedule_entry.accession_id}/status",
        json=payload,
    )
    assert response.status_code == 400
    assert "Status must be provided" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_schedule_entry_status_not_found(client: AsyncClient):
    """Test updating status of non-existent entry returns 404/422."""
    fake_id = uuid7()
    payload = {"status": ScheduleStatusEnum.EXECUTING.value}
    response = await client.put(
        f"/api/v1/scheduler/{fake_id}/status",
        json=payload,
    )
    # Note: If the ID is invalid in a way that validation catches (though uuid7 should be valid UUID),
    # it might be 422. But here we send a valid UUID that doesn't exist.
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_schedule_entry_priority(
    client: AsyncClient,
    schedule_entry: ScheduleEntryOrm,
):
    """Test updating schedule entry priority via PUT /{id}/priority."""
    payload = {"new_priority": 99, "reason": "Urgent request"}
    response = await client.put(
        f"/api/v1/scheduler/{schedule_entry.accession_id}/priority",
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["priority"] == 99


@pytest.mark.asyncio
async def test_update_schedule_entry_priority_not_found(client: AsyncClient):
    """Test updating priority of non-existent entry returns 404."""
    fake_id = uuid7()
    payload = {"new_priority": 50, "reason": "Test"}
    response = await client.put(
        f"/api/v1/scheduler/{fake_id}/priority",
        json=payload,
    )
    assert response.status_code == 404
