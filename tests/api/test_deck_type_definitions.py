"""Tests for the deck type definitions API."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from tests.factories import DeckDefinitionFactory, WorkcellFactory


@pytest.mark.asyncio
async def test_create_workcell(client: tuple[AsyncClient, sessionmaker[AsyncSession]]) -> None:
    """Test creating a workcell."""
    http_client, Session = client
    async with Session() as session:
        WorkcellFactory._meta.sqlalchemy_session = session
        workcell = WorkcellFactory()
        session.add(workcell)
        await session.commit()
    response = await http_client.get(f"/api/v1/workcells/{workcell.accession_id}")
    assert response.status_code == 200
    assert response.json()["name"] == workcell.name


@pytest.mark.asyncio
async def test_create_deck_type_definition(client: tuple[AsyncClient, sessionmaker[AsyncSession]]) -> None:
    """Test creating a deck type definition."""
    http_client, _ = client
    response = await http_client.post(
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
