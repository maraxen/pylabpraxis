"""Diagnostic test for deck retrieval issue."""
import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models import DeckOrm
from praxis.backend.services.deck import DeckService, deck_service
from tests.helpers import create_deck


@pytest.mark.asyncio
async def test_deck_service_direct(db_session: AsyncSession):
    """Test if deck service can find a deck created by helper."""
    # Create a deck using the helper
    deck = await create_deck(db_session, name="diagnostic_deck")

    # Check if deck exists in database using raw query
    result = await db_session.execute(
        text("SELECT accession_id FROM decks WHERE accession_id = :id"),
        {"id": str(deck.accession_id)},
    )
    result.first()

    # Check with SQLAlchemy select
    stmt = select(DeckOrm).filter(DeckOrm.accession_id == deck.accession_id)
    result2 = await db_session.execute(stmt)
    result2.scalar_one_or_none()

    # Try with a NEW service instance (like the API does)
    new_service = DeckService(DeckOrm)
    await new_service.get(db_session, deck.accession_id)

    # Try to retrieve it using the singleton service
    try:
        retrieved = await deck_service.get(db_session, deck.accession_id)
    except Exception:
        raise

    if retrieved:
        pass
    else:
        pass

    assert retrieved is not None, "Deck should be found"
