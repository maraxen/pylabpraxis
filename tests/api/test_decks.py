"""Tests for the decks API."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import (
    DeckDefinitionFactory,
    MachineFactory,
    WorkcellFactory,
)


@pytest.mark.asyncio
async def test_create_deck(client: AsyncClient, db: AsyncSession) -> None:
    """Test creating a deck."""
    workcell = WorkcellFactory()
    machine = MachineFactory(workcell=workcell)
    deck_type = DeckDefinitionFactory()

    response = await client.post(
        "/api/v1/decks/",
        json={
            "name": "test_deck",
            "deck_type_id": str(deck_type.accession_id),
            "machine_id": str(machine.accession_id),
            "resource_definition_accession_id": str(
                deck_type.resource_definition.accession_id
            ),
        },
    )
    assert response.status_code == 201
    assert response.json()["name"] == "test_deck"
