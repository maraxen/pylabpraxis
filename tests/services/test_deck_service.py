import pytest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.services.deck import deck_service
from praxis.backend.models.pydantic_internals.deck import DeckCreate
from tests.factories import uuid7


@pytest.mark.asyncio
async def test_create_deck_remaps_machine_id():
    """
    Tests that the DeckService.create method correctly remaps
    the `machine_id` from the Pydantic model to the
    `parent_machine_accession_id` on the ORM model.
    """
    # 1. Create a mock for the input schema
    test_machine_id = uuid7()
    mock_deck_create = DeckCreate(
        name="test_deck",
        asset_type="DECK",
        deck_type_id=uuid7(),
        machine_id=test_machine_id,  # This is what we're testing
        resource_definition_accession_id=uuid7()
    )

    # 2. Configure the mock DB session
    mock_db = AsyncMock(spec=AsyncSession)

    # Configure .add() as a SYNCHRONOUS mock to avoid RuntimeWarning
    mock_db.add = MagicMock()
    # Configure .flush() and .refresh() as ASYNCHRONOUS mocks
    mock_db.flush = AsyncMock()
    mock_db.refresh = AsyncMock()

    # 3. Call the service
    # We use the real DeckOrm model, so no need to mock the class.
    # We will inspect the object passed to db.add() to verify the fields were set correctly.

    await deck_service.create(db=mock_db, obj_in=mock_deck_create)

    # 4. Assertions

    # Assert the synchronous DB call was made
    mock_db.add.assert_called_once()
    # Assert the asynchronous DB calls were awaited
    mock_db.flush.assert_awaited_once()
    mock_db.refresh.assert_awaited_once()

    # Get the object passed to add
    args, _ = mock_db.add.call_args
    added_deck = args[0]

    # Check that the remapping was successful
    # Note: DeckOrm uses parent_machine_accession_id, not machine_id
    assert added_deck.parent_machine_accession_id == test_machine_id
    assert added_deck.name == "test_deck"
