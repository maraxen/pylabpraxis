"""End-to-End API tests simulating a user journey.

This test file verifies the API contract for the frontend developers by simulating
a complete user flow: uploading a protocol, creating a run, and monitoring its progress.
"""
import asyncio
import os
import tempfile
from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.enums import ProtocolRunStatusEnum
from praxis.backend.utils.uuid import uuid7


@pytest.fixture
def temp_protocol_file() -> AsyncGenerator[str, None]:
    """Create a temporary protocol file for testing."""
    content = """
from pylabrobot.resources import Deck

def test_protocol(deck: Deck, state: dict) -> None:
    \"\"\"A simple test protocol.\"\"\"
    print("Protocol started")
    return "success"
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    yield tmp_path

    if os.path.exists(tmp_path):
        os.remove(tmp_path)


@pytest.mark.asyncio
async def test_e2e_protocol_lifecycle(
    client: AsyncClient,
    db_session: AsyncSession,
    temp_protocol_file: str,
) -> None:
    """Test the complete lifecycle of a protocol run.

    Steps:
    1. Upload/Create a protocol definition.
    2. Verify the definition details.
    3. Start a protocol run (create run).
    4. Simulate execution (update status).
    5. Poll for completion.
    """
    # -------------------------------------------------------------------------
    # 1. Upload Protocol (Create Definition)
    # -------------------------------------------------------------------------
    protocol_name = f"e2e_protocol_{uuid7()}"
    definition_payload = {
        "name": protocol_name,
        "fqn": f"tests.e2e.{protocol_name}",
        "source_file_path": temp_protocol_file,
        "module_name": "tests.e2e.protocol",
        "function_name": "test_protocol",
        "version": "1.0.0",
        "description": "E2E Test Protocol",
        "parameters": [],
        "assets": []
    }

    response = await client.post("/api/v1/protocols/definitions", json=definition_payload)
    assert response.status_code == 201, f"Create definition failed: {response.text}"
    def_data = response.json()
    def_id = def_data["accession_id"]

    # -------------------------------------------------------------------------
    # 2. Get Protocol Details
    # -------------------------------------------------------------------------
    response = await client.get(f"/api/v1/protocols/definitions/{def_id}")
    assert response.status_code == 200
    assert response.json()["name"] == protocol_name

    # -------------------------------------------------------------------------
    # 3. Start Run (Create Protocol Run)
    # -------------------------------------------------------------------------
    run_id = str(uuid7())
    run_payload = {
        "run_accession_id": run_id,
        "top_level_protocol_definition_accession_id": def_id,
        "status": ProtocolRunStatusEnum.PENDING.value,
    }

    response = await client.post("/api/v1/protocols/runs", json=run_payload)
    assert response.status_code == 201, f"Create run failed: {response.text}"
    run_data = response.json()
    assert run_data["status"] == ProtocolRunStatusEnum.PENDING.value
    assert run_data["accession_id"] == run_id

    # -------------------------------------------------------------------------
    # 4. Simulate Execution Engine (Update Status)
    # -------------------------------------------------------------------------
    # In a real system, the scheduler/orchestrator would pick this up.
    # For this API contract test, we verify that the frontend can observe state changes.

    # Simulate transition to RUNNING
    update_payload = {"status": ProtocolRunStatusEnum.RUNNING.value}
    response = await client.put(f"/api/v1/protocols/runs/{run_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["status"] == ProtocolRunStatusEnum.RUNNING.value

    # Simulate transition to COMPLETED
    update_payload = {
        "status": ProtocolRunStatusEnum.COMPLETED.value,
        "output_data_json": {"result": "success"}
    }
    response = await client.put(f"/api/v1/protocols/runs/{run_id}", json=update_payload)
    assert response.status_code == 200

    # -------------------------------------------------------------------------
    # 5. Poll for Completion
    # -------------------------------------------------------------------------
    # Frontend polls the endpoint
    max_retries = 5
    for _ in range(max_retries):
        response = await client.get(f"/api/v1/protocols/runs/{run_id}")
        assert response.status_code == 200
        data = response.json()

        if data["status"] == ProtocolRunStatusEnum.COMPLETED.value:
            assert data["output_data_json"]["result"] == "success"
            break

        await asyncio.sleep(0.1)
    else:
        pytest.fail("Protocol run did not complete in time")
