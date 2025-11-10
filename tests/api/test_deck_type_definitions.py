"""Tests for the deck type definitions API."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.helpers import create_workcell


@pytest.mark.asyncio
async def test_create_workcell(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test creating a workcell."""
    from sqlalchemy import select
    from praxis.backend.models.orm.workcell import WorkcellOrm

    workcell = await create_workcell(db_session, name="test_workcell")

    # DEBUG: Verify data is in session before API call
    result = await db_session.execute(select(WorkcellOrm).where(WorkcellOrm.accession_id == workcell.accession_id))
    found = result.scalars().first()
    print(f"DEBUG: Workcell in session before API call: {found}")
    print(f"DEBUG: Workcell ID: {workcell.accession_id}")
    print(f"DEBUG: Session ID: {id(db_session)}")

    # DEBUG: List all routes
    from main import app as main_app
    print("DEBUG: Available routes:")
    for route in main_app.routes:
        if hasattr(route, 'path') and 'workcell' in route.path.lower():
            print(f"  {route.path} - {route.methods if hasattr(route, 'methods') else 'N/A'}")

    response = await client.get(f"/api/v1/workcell//{workcell.accession_id}")
    print(f"DEBUG: Response status: {response.status_code}")
    print(f"DEBUG: Response body: {response.text}")
    assert response.status_code == 200
    assert response.json()["name"] == workcell.name


@pytest.mark.asyncio
async def test_create_deck_type_definition(client: AsyncClient) -> None:
    """Test creating a deck type definition."""
    response = await client.post(
        "/api/v1/decks/types",
        json={
            "name": "Test Deck Type",
            "fqn": "test.deck.type",
            "description": "A test deck type",
            "positioning_config": {
                "method_name": "slot_to_location",
                "arg_name": "slot",
                "arg_type": "int",
                "params": {},
            },
        },
    )
    assert response.status_code == 201
