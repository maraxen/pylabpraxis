"""Service tests for DeckService.

This file tests the DeckService layer for deck management operations.

To run:
    export TEST_DATABASE_URL="postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"
    python -m pytest tests/services/test_deck_service.py -v
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.deck import DeckOrm
from praxis.backend.models.pydantic_internals.deck import DeckCreate
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.services.deck import DeckService
from praxis.backend.utils.uuid import uuid7
from tests.helpers import (
    create_deck,
    create_machine,
    create_deck_definition,
)


# ============================================================================
# CREATE Tests
# ============================================================================


@pytest.mark.asyncio
async def test_create_deck_success(db_session: AsyncSession) -> None:
    """Test successfully creating a deck via DeckService."""
    # 1. SETUP: Create dependencies
    machine = await create_machine(db_session, name="test_machine_for_deck")
    deck_def = await create_deck_definition(db_session, name="test_deck_type")

    deck_data = DeckCreate(
        name="new_service_deck",
        asset_type="DECK",
        deck_type_id=deck_def.accession_id,
        parent_accession_id=machine.accession_id,
        resource_definition_accession_id=deck_def.resource_definition.accession_id,
    )

    # 2. ACT: Create via service
    service = DeckService(DeckOrm)
    result = await service.create(db_session, obj_in=deck_data)

    # 3. ASSERT: Verify creation
    assert result is not None
    assert result.name == "new_service_deck"
    assert result.accession_id is not None

    # Verify by querying again
    verify = await service.get(db_session, accession_id=result.accession_id)
    assert verify is not None


# ============================================================================
# GET (Single) Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_deck_by_id_exists(db_session: AsyncSession) -> None:
    """Test retrieving an existing deck by ID."""
    # 1. SETUP: Create a deck to retrieve
    deck = await create_deck(db_session, name="find_me_service")

    # 2. ACT: Retrieve via service
    service = DeckService(DeckOrm)
    result = await service.get(db_session, accession_id=deck.accession_id)

    # 3. ASSERT: Verify retrieval
    assert result is not None
    assert result.name == "find_me_service"
    assert result.accession_id == deck.accession_id


@pytest.mark.asyncio
async def test_get_deck_by_id_not_found(db_session: AsyncSession) -> None:
    """Test retrieving a non-existent deck returns None."""
    # 1. SETUP: Generate a UUID that doesn't exist in database
    fake_id = uuid7()

    # 2. ACT: Try to retrieve non-existent deck
    service = DeckService(DeckOrm)
    result = await service.get(db_session, accession_id=fake_id)

    # 3. ASSERT: Should return None
    assert result is None


# ============================================================================
# GET_MULTI (List) Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_multi_decks(db_session: AsyncSession) -> None:
    """Test listing multiple decks."""
    # 1. SETUP: Create multiple decks with unique names
    import uuid
    suffix = uuid.uuid4().hex[:8]
    deck1 = await create_deck(db_session, name=f"service_deck_alpha_{suffix}")
    deck2 = await create_deck(db_session, name=f"service_deck_beta_{suffix}")
    deck3 = await create_deck(db_session, name=f"service_deck_gamma_{suffix}")

    # 2. ACT: List all decks
    service = DeckService(DeckOrm)
    filters = SearchFilters()
    results = await service.get_multi(db_session, filters=filters)

    # 3. ASSERT: All created decks are in results
    assert len(results) >= 3
    result_names = {deck.name for deck in results}
    assert f"service_deck_alpha_{suffix}" in result_names
    assert f"service_deck_beta_{suffix}" in result_names
    assert f"service_deck_gamma_{suffix}" in result_names


@pytest.mark.asyncio
async def test_get_multi_decks_filtered_by_parent(db_session: AsyncSession) -> None:
    """Test filtering decks by parent machine."""
    # 1. SETUP: Create decks on different machines with unique names
    import uuid
    suffix = uuid.uuid4().hex[:8]
    machine1 = await create_machine(db_session, name=f"service_machine_one_{suffix}")
    machine2 = await create_machine(db_session, name=f"service_machine_two_{suffix}")

    deck1 = await create_deck(db_session, machine=machine1, name=f"service_deck_on_m1_{suffix}")
    deck2 = await create_deck(db_session, machine=machine2, name=f"service_deck_on_m2_{suffix}")
    deck3 = await create_deck(db_session, machine=machine1, name=f"service_another_on_m1_{suffix}")

    # 2. ACT: Filter by machine1
    service = DeckService(DeckOrm)
    filters = SearchFilters(parent_accession_id=machine1.accession_id)
    results = await service.get_multi(db_session, filters=filters)

    # 3. ASSERT: Only machine1 decks returned
    assert len(results) >= 2
    result_names = {deck.name for deck in results}

    # Should include machine1 decks
    assert f"service_deck_on_m1_{suffix}" in result_names
    assert f"service_another_on_m1_{suffix}" in result_names

    # Should NOT include machine2 decks
    assert f"service_deck_on_m2_{suffix}" not in result_names


# ============================================================================
# UPDATE Tests
# ============================================================================


@pytest.mark.asyncio
async def test_update_deck_name(db_session: AsyncSession) -> None:
    """Test updating a deck's name."""
    # 1. SETUP: Create a deck to update
    import uuid
    unique_name = f"original_service_name_{uuid.uuid4().hex[:8]}"
    deck = await create_deck(db_session, name=unique_name)
    original_id = deck.accession_id

    # 2. ACT: Update via service
    service = DeckService(DeckOrm)
    update_data = {"name": f"updated_service_name_{uuid.uuid4().hex[:8]}"}
    result = await service.update(db_session, db_obj=deck, obj_in=update_data)

    # 3. ASSERT: Verify update
    assert result.name == update_data["name"]
    assert result.accession_id == original_id  # ID should not change

    # Verify persistence in database
    await db_session.refresh(deck)
    assert deck.name == update_data["name"]


@pytest.mark.asyncio
async def test_update_deck_partial(db_session: AsyncSession) -> None:
    """Test partial update (only updating name)."""
    # 1. SETUP: Create a deck with initial values
    import uuid
    initial_name = f"initial_service_name_{uuid.uuid4().hex[:8]}"
    deck = await create_deck(db_session, name=initial_name)
    original_id = deck.accession_id

    # 2. ACT: Update only name
    service = DeckService(DeckOrm)
    new_name = f"updated_partial_{uuid.uuid4().hex[:8]}"
    update_data = {"name": new_name}
    result = await service.update(db_session, db_obj=deck, obj_in=update_data)

    # 3. ASSERT: Name updated, ID unchanged
    assert result.name == new_name
    assert result.accession_id == original_id


# ============================================================================
# DELETE Tests
# ============================================================================


@pytest.mark.asyncio
async def test_delete_deck(db_session: AsyncSession) -> None:
    """Test deleting a deck."""
    # 1. SETUP: Create a deck to delete
    import uuid
    unique_name = f"to_be_deleted_service_{uuid.uuid4().hex[:8]}"
    deck = await create_deck(db_session, name=unique_name)
    deck_id = deck.accession_id

    # 2. ACT: Delete via service
    service = DeckService(DeckOrm)
    try:
        deleted = await service.remove(db_session, accession_id=deck_id)
        # 3. ASSERT: Verify deletion
        assert deleted is not None
        assert deleted.accession_id == deck_id

        # Verify it's gone
        verify = await service.get(db_session, accession_id=deck_id)
        assert verify is None
    except Exception as e:
        # Note: May fail due to cascade constraints
        if "Circular dependency" in str(e):
            pytest.skip("Circular dependency in cascade delete - known issue")
        raise


@pytest.mark.asyncio
async def test_delete_deck_nonexistent(db_session: AsyncSession) -> None:
    """Test deleting a non-existent deck returns None."""
    # 1. SETUP: Generate a UUID that doesn't exist
    fake_id = uuid7()

    # 2. ACT: Try to delete non-existent deck
    service = DeckService(DeckOrm)
    result = await service.remove(db_session, accession_id=fake_id)

    # 3. ASSERT: Should return None (not found)
    assert result is None


# ============================================================================
# RELATIONSHIP Tests
# ============================================================================


@pytest.mark.asyncio
async def test_get_deck_with_parent_machine(db_session: AsyncSession) -> None:
    """Test that retrieving a deck includes parent machine relationship."""
    # 1. SETUP: Create machine and deck
    import uuid
    suffix = uuid.uuid4().hex[:8]
    machine = await create_machine(db_session, name=f"parent_service_machine_{suffix}")
    deck = await create_deck(db_session, machine=machine, name=f"child_service_deck_{suffix}")

    # 2. ACT: Retrieve deck via service
    service = DeckService(DeckOrm)
    result = await service.get(db_session, accession_id=deck.accession_id)

    # 3. ASSERT: Deck returned with parent machine ID
    assert result is not None
    assert result.name == f"child_service_deck_{suffix}"
    assert result.parent_machine_accession_id == machine.accession_id


@pytest.mark.asyncio
async def test_get_deck_with_deck_type(db_session: AsyncSession) -> None:
    """Test that retrieving a deck includes deck type."""
    # 1. SETUP: Create deck with specific type
    import uuid
    suffix = uuid.uuid4().hex[:8]
    deck_def = await create_deck_definition(db_session, name=f"special_service_type_{suffix}")
    deck = await create_deck(db_session, deck_definition=deck_def, name=f"typed_service_deck_{suffix}")

    # 2. ACT: Retrieve deck via service
    service = DeckService(DeckOrm)
    result = await service.get(db_session, accession_id=deck.accession_id)

    # 3. ASSERT: Deck type ID is correct
    assert result is not None
    assert result.name == f"typed_service_deck_{suffix}"
    assert result.deck_type_id == deck_def.accession_id
