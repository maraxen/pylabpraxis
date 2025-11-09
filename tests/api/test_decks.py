"""Tests for the decks API, covering the full CRUD lifecycle."""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from praxis.backend.models import DeckOrm
from tests.factories import (
    DeckDefinitionFactory,
    MachineFactory,
    WorkcellFactory,
    ResourceDefinitionFactory,
    DeckFactory,
)


@pytest.mark.asyncio
async def test_create_deck(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test creating a deck."""
    # 1. SETUP: Create dependencies using factories.
    # The `client` fixture has already bound the factories to `db_session`.
    workcell = WorkcellFactory()
    machine = MachineFactory(workcell=workcell)
    resource_definition = ResourceDefinitionFactory()
    deck_type = DeckDefinitionFactory(resource_definition=resource_definition)

    # Flush the session to ensure generated IDs are available for the payload.
    await db_session.flush()

    # 2. ACT: Call the API endpoint.
    response = await client.post(
        "/api/v1/decks/",
        json={
            "name": "test_deck",
            "asset_type": "DECK",
            "deck_type_id": str(deck_type.accession_id),
            "machine_id": str(machine.accession_id),
            "resource_definition_accession_id": str(
                resource_definition.accession_id
            ),
        },
    )

    # 3. ASSERT: Check the response.
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test_deck"
    assert data["parent_accession_id"] == str(machine.accession_id)


@pytest.mark.asyncio
async def test_get_deck(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving a single deck by its ID."""
    # 1. SETUP: Create a deck to retrieve.
    deck = DeckFactory()
    await db_session.flush()

    # 2. ACT: Call the API.
    response = await client.get(f"/api/v1/decks/{deck.accession_id}")

    # 3. ASSERT: Check the response.
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == deck.name
    assert data["accession_id"] == str(deck.accession_id)


@pytest.mark.asyncio
async def test_get_multi_decks(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving multiple decks."""
    # 1. SETUP: Create multiple decks.
    DeckFactory.create_batch(3)
    await db_session.flush()

    # 2. ACT: Call the API.
    response = await client.get("/api/v1/decks/")

    # 3. ASSERT: Check the response.
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_update_deck(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test updating a deck's attributes."""
    # 1. SETUP: Create a deck to update.
    deck = DeckFactory(name="original_name")
    await db_session.flush()

    # 2. ACT: Call the API with new data.
    new_name = "updated_deck_name"
    response = await client.patch(
        f"/api/v1/decks/{deck.accession_id}",
        json={"name": new_name},
    )

    # 3. ASSERT: Check the response and database state.
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_name

    # Verify the change was persisted in the database.
    updated_deck = await db_session.get(DeckOrm, deck.accession_id)
    assert updated_deck.name == new_name


@pytest.mark.asyncio
async def test_delete_deck(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test deleting a deck."""
    # 1. SETUP: Create a deck to delete.
    deck = DeckFactory()
    deck_id = deck.accession_id
    await db_session.flush()

    # 2. ACT: Call the API to delete the deck.
    response = await client.delete(f"/api/v1/decks/{deck_id}")

    # 3. ASSERT: Check the response and database state.
    assert response.status_code == 200
    data = response.json()
    assert data["accession_id"] == str(deck_id)

    # Verify the deck is no longer in the database.
    deleted_deck = await db_session.get(DeckOrm, deck_id)
    assert deleted_deck is None
