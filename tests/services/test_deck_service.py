"""Unit tests for DeckService."""
import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from praxis.backend.services.deck import deck_service
from praxis.backend.services.machine import machine_service
from praxis.backend.models.pydantic_internals.deck import DeckCreate, DeckUpdate
from praxis.backend.models.pydantic_internals.machine import MachineCreate
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.models.enums.asset import AssetType
from praxis.backend.models.enums.machine import MachineStatusEnum
from praxis.backend.models.orm.resource import ResourceDefinitionOrm, ResourceOrm
from praxis.backend.models.orm.deck import DeckOrm, DeckDefinitionOrm

async def create_resource_definition(db: AsyncSession, name: str) -> ResourceDefinitionOrm:
    """Helper to create a resource definition."""
    definition = ResourceDefinitionOrm(
        name=name,
        fqn="com.example.Resource",
        resource_type="Generic",
        is_consumable=False
    )
    db.add(definition)
    await db.flush()
    await db.refresh(definition)
    return definition

async def create_deck_definition(db: AsyncSession, name: str) -> DeckDefinitionOrm:
    """Helper to create a deck definition."""
    definition = DeckDefinitionOrm(
        name=name,
        fqn="pylabrobot.decks.Deck",
        plr_category="Deck"
    )
    db.add(definition)
    await db.flush()
    await db.refresh(definition)
    return definition

@pytest.mark.asyncio
async def test_create_deck(db_session: AsyncSession) -> None:
    """Test creating a new deck."""
    # Setup
    res_def = await create_resource_definition(db_session, "Test Resource Def")
    deck_def = await create_deck_definition(db_session, "Test Deck Def")

    machine_in = MachineCreate(name="Parent Machine", asset_type=AssetType.MACHINE, status=MachineStatusEnum.OFFLINE)
    machine = await machine_service.create(db=db_session, obj_in=machine_in)

    deck_in = DeckCreate(
        name="Test Deck",
        asset_type=AssetType.DECK,
        resource_definition_accession_id=res_def.accession_id,
        deck_type_id=deck_def.accession_id,
        machine_id=machine.accession_id, # Should be remapped to parent_machine_accession_id
    )

    deck = await deck_service.create(db=db_session, obj_in=deck_in)

    assert deck.name == "Test Deck"
    assert deck.accession_id is not None
    assert deck.parent_machine_accession_id == machine.accession_id
    assert deck.resource_definition_accession_id == res_def.accession_id
    assert deck.deck_type_id == deck_def.accession_id

@pytest.mark.asyncio
async def test_get_deck(db_session: AsyncSession) -> None:
    """Test retrieving a deck by ID."""
    res_def = await create_resource_definition(db_session, "Get Deck Res Def")
    deck_def = await create_deck_definition(db_session, "Get Deck Type Def")

    deck_in = DeckCreate(
        name="Get Deck",
        asset_type=AssetType.DECK,
        resource_definition_accession_id=res_def.accession_id,
        deck_type_id=deck_def.accession_id
    )
    created = await deck_service.create(db=db_session, obj_in=deck_in)

    retrieved = await deck_service.get(db=db_session, accession_id=created.accession_id)
    assert retrieved is not None
    assert retrieved.accession_id == created.accession_id
    assert retrieved.name == "Get Deck"

@pytest.mark.asyncio
async def test_get_multi_decks(db_session: AsyncSession) -> None:
    """Test listing multiple decks."""
    res_def = await create_resource_definition(db_session, "Multi Deck Res Def")
    deck_def = await create_deck_definition(db_session, "Multi Deck Type Def")

    await deck_service.create(db=db_session, obj_in=DeckCreate(
        name="Deck 1",
        asset_type=AssetType.DECK,
        resource_definition_accession_id=res_def.accession_id,
        deck_type_id=deck_def.accession_id
    ))
    await deck_service.create(db=db_session, obj_in=DeckCreate(
        name="Deck 2",
        asset_type=AssetType.DECK,
        resource_definition_accession_id=res_def.accession_id,
        deck_type_id=deck_def.accession_id
    ))

    filters = SearchFilters()
    decks = await deck_service.get_multi(db=db_session, filters=filters)

    names = [d.name for d in decks]
    assert "Deck 1" in names
    assert "Deck 2" in names

@pytest.mark.asyncio
async def test_update_deck(db_session: AsyncSession) -> None:
    """Test updating deck information."""
    res_def = await create_resource_definition(db_session, "Update Deck Res Def")
    deck_def = await create_deck_definition(db_session, "Update Deck Type Def")

    deck_in = DeckCreate(
        name="Update Deck",
        asset_type=AssetType.DECK,
        resource_definition_accession_id=res_def.accession_id,
        deck_type_id=deck_def.accession_id
    )
    created = await deck_service.create(db=db_session, obj_in=deck_in)

    update_data = DeckUpdate(name="Updated Deck Name", asset_type=AssetType.DECK)
    updated = await deck_service.update(db=db_session, db_obj=created, obj_in=update_data)

    assert updated.name == "Updated Deck Name"

    refetched = await deck_service.get(db=db_session, accession_id=created.accession_id)
    assert refetched.name == "Updated Deck Name"

@pytest.mark.asyncio
@pytest.mark.xfail(reason="Circular dependency on cascade delete for DeckOrm")
async def test_remove_deck(db_session: AsyncSession) -> None:
    """Test deleting a deck."""
    res_def = await create_resource_definition(db_session, "Remove Deck Res Def")
    deck_def = await create_deck_definition(db_session, "Remove Deck Type Def")

    deck_in = DeckCreate(
        name="Remove Deck",
        asset_type=AssetType.DECK,
        resource_definition_accession_id=res_def.accession_id,
        deck_type_id=deck_def.accession_id
    )
    created = await deck_service.create(db=db_session, obj_in=deck_in)

    removed = await deck_service.remove(db=db_session, accession_id=created.accession_id)
    assert removed is not None

    retrieved = await deck_service.get(db=db_session, accession_id=created.accession_id)
    assert retrieved is None

@pytest.mark.asyncio
async def test_read_decks_by_machine_id(db_session: AsyncSession) -> None:
    """Test reading decks for a given machine."""
    res_def = await create_resource_definition(db_session, "Machine Deck Res Def")
    deck_def = await create_deck_definition(db_session, "Machine Deck Type Def")

    machine_in = MachineCreate(name="Deck Machine", asset_type=AssetType.MACHINE, status=MachineStatusEnum.OFFLINE)
    machine = await machine_service.create(db=db_session, obj_in=machine_in)

    deck_in = DeckCreate(
        name="Machine Deck",
        asset_type=AssetType.DECK,
        resource_definition_accession_id=res_def.accession_id,
        deck_type_id=deck_def.accession_id,
        machine_id=machine.accession_id
    )
    await deck_service.create(db=db_session, obj_in=deck_in)

    deck = await deck_service.read_decks_by_machine_id(db=db_session, machine_id=machine.accession_id)
    assert deck is not None
    assert deck.name == "Machine Deck"
    assert deck.parent_machine_accession_id == machine.accession_id

@pytest.mark.asyncio
async def test_get_all_decks(db_session: AsyncSession) -> None:
    """Test retrieving all decks."""
    res_def = await create_resource_definition(db_session, "All Decks Res Def")
    deck_def = await create_deck_definition(db_session, "All Decks Type Def")

    await deck_service.create(db=db_session, obj_in=DeckCreate(
        name="Deck A",
        asset_type=AssetType.DECK,
        resource_definition_accession_id=res_def.accession_id,
        deck_type_id=deck_def.accession_id
    ))

    decks = await deck_service.get_all_decks(db=db_session)
    assert len(decks) >= 1
    assert "Deck A" in [d.name for d in decks]
