"""Tests for the deck type definitions API."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from tests.helpers import create_workcell


@pytest.mark.asyncio
async def test_create_workcell(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test creating a workcell."""
    workcell = await create_workcell(db_session, name="test_workcell")

    response = await client.get(f"/api/v1/workcells/{workcell.accession_id}")
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
