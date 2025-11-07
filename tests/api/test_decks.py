"""Tests for the decks API."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from tests.factories import (
    DeckDefinitionFactory,
    MachineFactory,
    WorkcellFactory,
    ResourceDefinitionFactory,
)


@pytest.mark.asyncio
async def test_create_deck(client: tuple[AsyncClient, sessionmaker[AsyncSession]]) -> None:
    """Test creating a deck."""
    http_client, Session = client
    async with Session() as session:
        WorkcellFactory._meta.sqlalchemy_session = session
        MachineFactory._meta.sqlalchemy_session = session
        DeckDefinitionFactory._meta.sqlalchemy_session = session
        ResourceDefinitionFactory._meta.sqlalchemy_session = session
        resource_definition = ResourceDefinitionFactory()
        workcell = WorkcellFactory()
        machine = MachineFactory(workcell=workcell)
        deck_type = DeckDefinitionFactory(resource_definition=resource_definition)
        session.add_all([workcell, machine, deck_type, resource_definition])
        await session.commit()

    response = await http_client.post(
        "/api/v1/decks/",
        json={
            "name": "test_deck",
                "asset_type": "DECK",
            "deck_type_id": str(deck_type.accession_id),
            "machine_id": str(machine.accession_id),
            "resource_definition_accession_id": str(
                deck_type.resource_definition.accession_id
            ),
        },
    )
    assert response.status_code == 201
    assert response.json()["name"] == "test_deck"
