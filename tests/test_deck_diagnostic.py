"""Diagnostic test for deck retrieval issue."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from tests.helpers import create_deck
from praxis.backend.services.deck import deck_service, DeckService
from praxis.backend.models import DeckOrm

@pytest.mark.asyncio
async def test_deck_service_direct(db_session: AsyncSession):
    """Test if deck service can find a deck created by helper."""
    # Create a deck using the helper
    deck = await create_deck(db_session, name="diagnostic_deck")
    print(f"\nCreated deck with ID: {deck.accession_id}")
    print(f"Deck name: {deck.name}")
    print(f"Session ID: {id(db_session)}")

    # Check if deck exists in database using raw query
    result = await db_session.execute(
        text("SELECT accession_id, name FROM decks WHERE accession_id = :id"),
        {"id": str(deck.accession_id)}
    )
    row = result.first()
    print(f"Raw SQL query result: {row}")

    # Check with SQLAlchemy select
    stmt = select(DeckOrm).filter(DeckOrm.accession_id == deck.accession_id)
    result2 = await db_session.execute(stmt)
    deck_query = result2.scalar_one_or_none()
    print(f"SQLAlchemy select result: {deck_query}")

    # Try with a NEW service instance (like the API does)
    new_service = DeckService(DeckOrm)
    retrieved_new = await new_service.get(db_session, deck.accession_id)
    print(f"NEW service instance retrieved: {retrieved_new}")

    # Try to retrieve it using the singleton service
    try:
        retrieved = await deck_service.get(db_session, deck.accession_id)
        print(f"Singleton service retrieved: {type(retrieved) if retrieved else None}")
    except Exception as e:
        print(f"ERROR during get: {e}")
        raise

    if retrieved:
        print("SUCCESS: Deck was found!")
    else:
        print("FAILURE: Deck was NOT found")

    assert retrieved is not None, "Deck should be found"
