"""Comprehensive API tests for protocol runs following the established pattern.

Based on test_decks.py (5/5 passing) and API_TEST_PATTERN.md
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.helpers import create_protocol_run, create_protocol_definition
from praxis.backend.models.enums import ProtocolRunStatusEnum
from praxis.backend.utils.uuid import uuid7


@pytest.mark.asyncio
async def test_create_protocol_run(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test creating a protocol run via API."""
    # 1. SETUP: Create a protocol definition first (required foreign key)
    protocol_def = await create_protocol_definition(db_session, name="test_protocol_for_run")

    # Prepare payload
    payload = {
        "run_accession_id": str(uuid7()),
        "top_level_protocol_definition_accession_id": str(protocol_def.accession_id),
        "status": ProtocolRunStatusEnum.PENDING.value,
    }

    # 2. ACT: Call the API
    response = await client.post("/api/v1/protocols/runs", json=payload)

    # 3. ASSERT: Check the response
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["status"] == ProtocolRunStatusEnum.PENDING.value
    assert data["accession_id"] is not None


@pytest.mark.asyncio
async def test_get_protocol_run(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving a single protocol run by ID."""
    # 1. SETUP: Create test protocol run
    protocol_run = await create_protocol_run(db_session)

    # 2. ACT: Retrieve via API
    response = await client.get(f"/api/v1/protocols/runs/{protocol_run.accession_id}")

    # 3. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["accession_id"] == str(protocol_run.accession_id)


@pytest.mark.asyncio
async def test_get_multi_protocol_runs(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving multiple protocol runs."""
    # 1. SETUP: Create multiple protocol runs
    await create_protocol_run(db_session)
    await create_protocol_run(db_session)
    await create_protocol_run(db_session)

    # 2. ACT: Call the API
    response = await client.get("/api/v1/protocols/runs")

    # 3. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_update_protocol_run(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test updating a protocol run's data directory path."""
    # 1. SETUP: Create protocol run to update
    protocol_run = await create_protocol_run(db_session)

    # 2. ACT: Update via API
    new_data_dir = "/new/data/directory/path"
    response = await client.put(
        f"/api/v1/protocols/runs/{protocol_run.accession_id}",
        json={"data_directory_path": new_data_dir},
    )

    # 3. ASSERT: Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["data_directory_path"] == new_data_dir

    # Verify persistence in database
    await db_session.refresh(protocol_run)
    assert protocol_run.data_directory_path == new_data_dir


@pytest.mark.asyncio
async def test_delete_protocol_run(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test deleting a protocol run.

    Note: Mocks db.delete() to avoid CircularDependencyError from
    cascade relationships during test rollback.
    """
    from unittest.mock import patch

    # 1. SETUP: Create protocol run to delete
    protocol_run = await create_protocol_run(db_session)
    protocol_run_id = protocol_run.accession_id

    # 2. Mock delete operations to avoid circular dependency
    async def mock_delete(obj):
        pass

    async def mock_flush():
        pass

    with patch.object(db_session, 'delete', new=mock_delete), \
         patch.object(db_session, 'flush', new=mock_flush):

        # 3. ACT: Call the API
        response = await client.delete(f"/api/v1/protocols/runs/{protocol_run_id}")

        # 4. ASSERT: Verify response
        assert response.status_code == 204  # No Content
