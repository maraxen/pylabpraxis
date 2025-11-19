"""Test Pydantic serialization of DeckOrm to DeckResponse."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from tests.helpers import create_deck
from praxis.backend.models.pydantic_internals.deck import DeckResponse
from praxis.backend.services.deck import deck_service

@pytest.mark.asyncio
async def test_deck_serialization(db_session: AsyncSession):
    """Test if we can serialize a DeckOrm to DeckResponse."""
    # Create a deck using helper
    deck_created = await create_deck(db_session, name="test_serialization")
    print(f"\nCreated deck: {deck_created.accession_id}")

    # Retrieve it using service (which loads relationships)
    deck = await deck_service.get(db_session, deck_created.accession_id)
    print(f"Retrieved via service: {deck.accession_id}")

    # Try to convert to Pydantic model
    try:
        deck_response = DeckResponse.model_validate(deck)
        print(f"SUCCESS: Serialization worked!")
        print(f"Response type: {type(deck_response)}")

        # Try to dump to dict
        deck_dict = deck_response.model_dump()
        print(f"Dict keys: {deck_dict.keys()}")

    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")
        raise
