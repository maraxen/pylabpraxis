"""Integration tests for Asset polymorphic inheritance hierarchy."""
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.asset import AssetOrm
from praxis.backend.models.orm.deck import DeckOrm
from praxis.backend.models.orm.machine import MachineOrm
from praxis.backend.models.enums import AssetType
from tests.helpers import create_machine, create_deck


@pytest.mark.asyncio
async def test_polymorphic_query_returns_correct_types(db_session: AsyncSession):
    """Test querying AssetOrm returns correct subclass instances."""
    # Create a machine and a deck
    machine = await create_machine(db_session, name="test_machine_poly")
    deck = await create_deck(db_session, name="test_deck_poly")

    # Query all assets
    result = await db_session.execute(
        select(AssetOrm).where(
            AssetOrm.accession_id.in_([machine.accession_id, deck.accession_id])
        )
    )
    assets = result.scalars().all()

    # Verify we got the right types back
    assert len(assets) == 2

    # Find machine and deck in results
    machine_result = next(a for a in assets if a.accession_id == machine.accession_id)
    deck_result = next(a for a in assets if a.accession_id == deck.accession_id)

    # Verify actual Python types (not just asset_type field)
    assert isinstance(machine_result, MachineOrm)
    assert isinstance(deck_result, DeckOrm)
    assert machine_result.asset_type == AssetType.MACHINE
    assert deck_result.asset_type == AssetType.DECK


@pytest.mark.asyncio
async def test_type_discrimination_filtering(db_session: AsyncSession):
    """Test filtering by asset_type returns correct subclass instances."""
    # Create a machine and a deck
    machine = await create_machine(db_session, name="test_machine_filter")
    deck = await create_deck(db_session, name="test_deck_filter")

    # Query for the specific machine by type and name
    result_machine = await db_session.execute(
        select(AssetOrm).where(
            AssetOrm.asset_type == AssetType.MACHINE,
            AssetOrm.name == "test_machine_filter",
        )
    )
    machines = result_machine.scalars().all()

    # Query for the specific deck by type and name
    result_deck = await db_session.execute(
        select(AssetOrm).where(
            AssetOrm.asset_type == AssetType.DECK, AssetOrm.name == "test_deck_filter"
        )
    )
    decks = result_deck.scalars().all()

    # Verify we got only the machine
    assert len(machines) == 1
    assert machines[0].accession_id == machine.accession_id
    assert isinstance(machines[0], MachineOrm)

    # Verify we got only the deck
    assert len(decks) == 1
    assert decks[0].accession_id == deck.accession_id
    assert isinstance(decks[0], DeckOrm)


@pytest.mark.asyncio
async def test_inherited_fields_are_accessible(db_session: AsyncSession):
    """Verify inherited fields (name, fqn) work at all levels."""
    # Create a machine with specific name and fqn
    machine = await create_machine(
        db_session,
        name="test_machine_inherited",
        fqn="pylabrobot.machines.Machine",
    )
    # Create a deck with specific name and fqn
    deck = await create_deck(
        db_session,
        name="test_deck_inherited",
        fqn="pylabrobot.decks.Deck",
    )

    # Query them back directly
    machine_result = await db_session.get(MachineOrm, machine.accession_id)
    deck_result = await db_session.get(DeckOrm, deck.accession_id)

    # Verify fields are correctly set
    assert machine_result.name == "test_machine_inherited"
    assert machine_result.fqn == "pylabrobot.machines.Machine"
    assert deck_result.name == "test_deck_inherited"
    assert deck_result.fqn == "pylabrobot.decks.Deck"

    # Verify via the base class query
    asset_result = await db_session.get(AssetOrm, machine.accession_id)
    assert asset_result.name == "test_machine_inherited"
    assert asset_result.fqn == "pylabrobot.machines.Machine"


from praxis.backend.models.orm.resource import ResourceOrm


@pytest.mark.xfail(
    reason="Circular dependency in DeckOrm relationships causes flush error on delete."
)
@pytest.mark.asyncio
async def test_delete_asset_cascades(db_session: AsyncSession):
    """Verify that deleting an AssetOrm cascades to the subclass table."""
    # Create a machine and a deck
    machine = await create_machine(db_session, name="test_machine_cascade")
    deck = await create_deck(db_session, name="test_deck_cascade")
    machine_id = machine.accession_id
    deck_id = deck.accession_id

    # Fetch and delete the machine as an Asset
    machine_as_asset = await db_session.get(AssetOrm, machine_id)
    assert machine_as_asset is not None
    await db_session.delete(machine_as_asset)
    await db_session.flush()

    # Verify the machine is gone from both tables
    assert await db_session.get(AssetOrm, machine_id) is None
    assert await db_session.get(MachineOrm, machine_id) is None

    # Fetch and delete the deck as an Asset
    deck_as_asset = await db_session.get(AssetOrm, deck_id)
    assert deck_as_asset is not None
    await db_session.delete(deck_as_asset)
    await db_session.flush()

    # Verify the deck is gone from all tables in the hierarchy
    assert await db_session.get(AssetOrm, deck_id) is None
    assert await db_session.get(ResourceOrm, deck_id) is None
    assert await db_session.get(DeckOrm, deck_id) is None
