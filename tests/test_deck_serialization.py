"""Test Pydantic serialization of DeckOrm to DeckResponse."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.pydantic_internals.deck import DeckResponse
from praxis.backend.services.deck import deck_service
from tests.helpers import create_deck


@pytest.mark.asyncio
async def test_deck_serialization(db_session: AsyncSession):
    """Test if we can serialize a DeckOrm to DeckResponse."""
    # Create a deck using helper
    deck_created = await create_deck(db_session, name="test_serialization")

    # Retrieve it using service (which loads relationships)
    deck = await deck_service.get(db_session, deck_created.accession_id)

    # Try to convert to Pydantic model
    try:
        deck_response = DeckResponse.model_validate(deck)

        # Try to dump to dict
        deck_response.model_dump()

    except Exception:
        raise
