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

    # 3. Call the service, mocking the DeckOrm model to capture its constructor args
    with MagicMock() as mock_deck_orm_class:
        # Temporarily replace the service's model with our mock
        original_model = deck_service.model
        deck_service.model = mock_deck_orm_class

        await deck_service.create(db=mock_db, obj_in=mock_deck_create)

        # Restore the original model
        deck_service.model = original_model

    # 4. Assertions

    # Assert the synchronous DB call was made
    mock_db.add.assert_called_once()
    # Assert the asynchronous DB calls were awaited
    mock_db.flush.assert_awaited_once()
    mock_db.refresh.assert_awaited_once()

    # Get the keyword args passed to the DeckOrm constructor
    _, kwargs = mock_deck_orm_class.call_args

    # Check that the remapping was successful
    assert "machine_id" not in kwargs
    assert kwargs["parent_machine_accession_id"] == test_machine_id
    assert kwargs["name"] == "test_deck"
