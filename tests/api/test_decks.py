"""Tests for the decks API, covering the full CRUD lifecycle."""
import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from praxis.backend.models import DeckOrm
from tests.helpers import (
    create_workcell,
    create_machine,
    create_resource_definition,
    create_deck_definition,
    create_deck,
)


@pytest.mark.asyncio
async def test_create_deck(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test creating a deck."""
    # 1. SETUP: Create dependencies using async helpers
    workcell = await create_workcell(db_session)
    machine = await create_machine(db_session, workcell=workcell)
    resource_definition = await create_resource_definition(db_session)
    deck_type = await create_deck_definition(db_session, resource_definition=resource_definition)

    # 2. ACT: Call the API endpoint
    response = await client.post(
        "/api/v1/decks/",
        json={
            "name": "test_deck",
            "asset_type": "DECK",
            "deck_type_id": str(deck_type.accession_id),
            "parent_accession_id": str(machine.accession_id),
            "resource_definition_accession_id": str(
                resource_definition.accession_id
            ),
        },
    )

    # 3. ASSERT: Check the response
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test_deck"
    assert data["accession_id"] is not None
    # Note: parent_machine_accession_id is internal ORM field, not exposed in API response


@pytest.mark.asyncio
async def test_get_deck(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving a single deck by its ID."""
    # 1. SETUP: Create a deck to retrieve
    deck = await create_deck(db_session, name="test_deck_get")

    # 2. ACT: Call the API
    response = await client.get(f"/api/v1/decks/{deck.accession_id}")

    # 3. ASSERT: Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == deck.name
    assert data["accession_id"] == str(deck.accession_id)


@pytest.mark.asyncio
async def test_get_multi_decks(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test retrieving multiple decks."""
    # 1. SETUP: Create shared resources once to avoid constraint violations
    from tests.helpers import create_machine, create_deck_definition
    machine = await create_machine(db_session, name="shared_machine")
    deck_def = await create_deck_definition(db_session)

    # Create multiple decks sharing the same machine and deck definition
    await create_deck(db_session, name="deck_1", machine=machine, deck_definition=deck_def)
    await create_deck(db_session, name="deck_2", machine=machine, deck_definition=deck_def)
    await create_deck(db_session, name="deck_3", machine=machine, deck_definition=deck_def)

    # 2. ACT: Call the API
    response = await client.get("/api/v1/decks/")

    # 3. ASSERT: Check the response
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_update_deck(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test updating a deck's attributes."""
    # 1. SETUP: Create a deck to update
    deck = await create_deck(db_session, name="original_name")

    # 2. ACT: Call the API with new data
    new_name = "updated_deck_name"
    response = await client.put(
        f"/api/v1/decks/{deck.accession_id}",
        json={"name": new_name},
    )

    # 3. ASSERT: Check the response and database state
    if response.status_code != 200:
        print(f"DEBUG Response status: {response.status_code}")
        print(f"DEBUG Response body: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == new_name

    # Verify the change was persisted in the database
    await db_session.refresh(deck)
    assert deck.name == new_name


@pytest.mark.asyncio
async def test_delete_deck(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test deleting a deck."""
    # 1. SETUP: Create a deck to delete
    deck = await create_deck(db_session, name="deck_to_delete")
    deck_id = deck.accession_id

    # 2. ACT: Call the API to delete the deck
    response = await client.delete(f"/api/v1/decks/{deck_id}")

    # 3. ASSERT: Check the response and database state
    assert response.status_code == 200
    data = response.json()
    assert data["accession_id"] == str(deck_id)

    # Verify the deck is no longer in the database
    deleted_deck = await db_session.get(DeckOrm, deck_id)
    assert deleted_deck is None
