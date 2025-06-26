import uuid
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from praxis.backend.models import (
  DeckPositionResourceOrm,
  MachineOrm,
  ResourceDefinitionCatalogOrm,
  ResourceOrm,
)
from praxis.backend.services.deck_instance import (
  create_deck_instance,
  delete_deck_instance,
  list_deck_instances,
  read_deck_instance,
  read_deck_instance_by_name,
  update_deck_instance,
)

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
async def setup_test_data(db: AsyncSession):
  """Set up initial data required for deck instance tests."""
  # 1. Create a resource definition for a deck
  deck_def = ResourceDefinitionCatalogOrm(
    name="test_deck_definition",
    python_fqn="pylabrobot.resources.hamilton.STARDeck",
    category="deck",
  )
  # 2. Create a resource definition for a plate
  plate_def = ResourceDefinitionCatalogOrm(
    name="corning_96_wellplate_360ul_flat",
    python_fqn="pylabrobot.resources.corning_96_wellplate_360ul_flat",
    category="plate",
  )
  db.add_all([deck_def, plate_def])
  await db.flush()

  # 3. Create a parent machine
  parent_machine = MachineOrm(
    name="TestLiquidHandler",
    python_fqn="pylabrobot.liquid_handling.liquid_handler.LiquidHandler",
    accession_id=uuid.uuid4(),
  )
  db.add(parent_machine)
  await db.flush()

  # 4. Create a resource instance for the deck itself
  deck_resource = ResourceOrm(
    name="PhysicalDeck1",
    resource_definition_name=deck_def.name,
    accession_id=uuid.uuid4(),
  )
  # 5. Create a resource instance for a plate
  plate_resource = ResourceOrm(
    name="PlateOnDeck1",
    resource_definition_name=plate_def.name,
    accession_id=uuid.uuid4(),
  )
  db.add_all([deck_resource, plate_resource])
  await db.commit()

  return {
    "parent_machine": parent_machine,
    "deck_resource": deck_resource,
    "plate_resource": plate_resource,
    "plate_def": plate_def,
  }


class TestDeckService:
  """Test suite for deck instance service functions."""

  async def test_create_deck_instance_success(
    self,
    db: AsyncSession,
    setup_test_data: dict[str, Any],
  ):
    """Test successful creation of a deck instance without position items."""
    deck_resource = setup_test_data["deck_resource"]
    deck_name = "MyTestDeck"
    python_fqn = "pylabrobot.resources.hamilton.STARDeck"

    created_deck = await create_deck_instance(
      db=db,
      name=deck_name,
      deck_accession_id=deck_resource.accession_id,
      python_fqn=python_fqn,
      description="A test description.",
    )

    assert created_deck is not None
    assert created_deck.name == deck_name
    assert created_deck.python_fqn == python_fqn
    assert created_deck.deck_accession_id == deck_resource.accession_id
    assert created_deck.description == "A test description."
    assert len(created_deck.position_items) == 0

  async def test_create_deck_instance_with_positions(
    self,
    db: AsyncSession,
    setup_test_data: dict[str, Any],
  ):
    """Test successful creation of a deck instance with position items."""
    deck_resource = setup_test_data["deck_resource"]
    plate_resource = setup_test_data["plate_resource"]
    plate_def = setup_test_data["plate_def"]

    position_data = [
      {
        "position_name": "A1",
        "resource_instance_accession_id": plate_resource.accession_id,
        "expected_resource_definition_name": plate_def.name,
      },
      {
        "position_name": "B1",
        "expected_resource_definition_name": plate_def.name,
      },
    ]

    created_deck = await create_deck_instance(
      db=db,
      name="DeckWithPositions",
      deck_accession_id=deck_resource.accession_id,
      python_fqn="pylabrobot.resources.hamilton.STARDeck",
      position_items_data=position_data,
    )

    assert created_deck is not None
    assert len(created_deck.position_items) == 2

    pos_a1 = next(
      (p for p in created_deck.position_items if p.position_name == "A1"),
      None,
    )
    pos_b1 = next(
      (p for p in created_deck.position_items if p.position_name == "B1"),
      None,
    )

    assert pos_a1 is not None
    assert pos_a1.resource_instance_accession_id == plate_resource.accession_id
    assert pos_a1.expected_resource_definition_name == plate_def.name

    assert pos_b1 is not None
    assert pos_b1.resource_instance_accession_id is None
    assert pos_b1.expected_resource_definition_name == plate_def.name

  async def test_create_deck_instance_duplicate_name_fails(
    self,
    db: AsyncSession,
    setup_test_data: dict[str, Any],
  ):
    """Test that creating a deck instance with a duplicate name raises ValueError."""
    deck_resource = setup_test_data["deck_resource"]
    deck_name = "DuplicateDeck"

    await create_deck_instance(
      db=db,
      name=deck_name,
      deck_accession_id=deck_resource.accession_id,
      python_fqn="fqn.1",
    )

    with pytest.raises(ValueError, match="already exists"):
      await create_deck_instance(
        db=db,
        name=deck_name,
        deck_accession_id=deck_resource.accession_id,
        python_fqn="fqn.2",
      )

  async def test_create_deck_instance_invalid_deck_id_fails(self, db: AsyncSession):
    """Test that creating a deck instance with a non-existent deck ID fails."""
    non_existent_id = uuid.uuid4()
    with pytest.raises(ValueError, match="ResourceOrm.*not found"):
      await create_deck_instance(
        db=db,
        name="InvalidDeck",
        deck_accession_id=non_existent_id,
        python_fqn="fqn.1",
      )

  async def test_read_deck_instance(
    self,
    db: AsyncSession,
    setup_test_data: dict[str, Any],
  ):
    """Test reading a deck instance by its accession_id."""
    deck_resource = setup_test_data["deck_resource"]
    deck = await create_deck_instance(
      db=db,
      name="ReadableDeck",
      deck_accession_id=deck_resource.accession_id,
      python_fqn="fqn.read",
    )

    fetched_deck = await read_deck_instance(db, deck.accession_id)
    assert fetched_deck is not None
    assert fetched_deck.accession_id == deck.accession_id
    assert fetched_deck.name == "ReadableDeck"

  async def test_read_deck_instance_not_found(self, db: AsyncSession):
    """Test that reading a non-existent deck instance returns None."""
    non_existent_id = uuid.uuid4()
    fetched_deck = await read_deck_instance(db, non_existent_id)
    assert fetched_deck is None

  async def test_read_deck_instance_by_name(
    self,
    db: AsyncSession,
    setup_test_data: dict[str, Any],
  ):
    """Test reading a deck instance by its unique name."""
    deck_resource = setup_test_data["deck_resource"]
    deck_name = "NamedDeck"
    await create_deck_instance(
      db=db,
      name=deck_name,
      deck_accession_id=deck_resource.accession_id,
      python_fqn="fqn.name",
    )

    fetched_deck = await read_deck_instance_by_name(db, deck_name)
    assert fetched_deck is not None
    assert fetched_deck.name == deck_name

  async def test_list_deck_instances(
    self,
    db: AsyncSession,
    setup_test_data: dict[str, Any],
  ):
    """Test listing deck instances."""
    deck_resource = setup_test_data["deck_resource"]
    await create_deck_instance(
      db,
      "DeckList1",
      deck_resource.accession_id,
      "fqn.list.1",
    )
    await create_deck_instance(
      db,
      "DeckList2",
      deck_resource.accession_id,
      "fqn.list.2",
    )

    all_decks = await list_deck_instances(db)
    assert len(all_decks) >= 2  # GTE to account for other tests' data

    # Test filtering
    filtered_decks = await list_deck_instances(
      db,
      deck_accession_id=deck_resource.accession_id,
    )
    assert len(filtered_decks) >= 2

    # Test limit
    limited_decks = await list_deck_instances(db, limit=1)
    assert len(limited_decks) == 1

    # Test offset
    offset_decks = await list_deck_instances(db, limit=1, offset=1)
    assert len(offset_decks) == 1
    assert offset_decks[0].name != limited_decks[0].name

  async def test_update_deck_instance(
    self,
    db: AsyncSession,
    setup_test_data: dict[str, Any],
  ):
    """Test updating various attributes of a deck instance."""
    deck_resource = setup_test_data["deck_resource"]
    plate_resource = setup_test_data["plate_resource"]

    deck = await create_deck_instance(
      db=db,
      name="DeckToUpdate",
      deck_accession_id=deck_resource.accession_id,
      python_fqn="fqn.update.initial",
    )

    updated_name = "DeckHasBeenUpdated"
    updated_description = "This is the new description."

    updated_deck = await update_deck_instance(
      db=db,
      deck_accession_id=deck.accession_id,
      name=updated_name,
      description=updated_description,
    )

    assert updated_deck is not None
    assert updated_deck.name == updated_name
    assert updated_deck.description == updated_description
    assert updated_deck.accession_id == deck.accession_id

    # Test updating position items (replace all)
    new_position_data = [
      {
        "position_name": "C3",
        "resource_instance_accession_id": plate_resource.accession_id,
      },
    ]

    final_deck = await update_deck_instance(
      db=db,
      deck_accession_id=deck.accession_id,
      position_items_data=new_position_data,
    )

    assert final_deck is not None
    assert len(final_deck.position_items) == 1
    assert final_deck.position_items[0].position_name == "C3"
    assert (
      final_deck.position_items[0].resource_instance_accession_id
      == plate_resource.accession_id
    )

  async def test_update_deck_instance_not_found(self, db: AsyncSession):
    """Test that updating a non-existent deck instance returns None."""
    non_existent_id = uuid.uuid4()
    result = await update_deck_instance(
      db,
      deck_accession_id=non_existent_id,
      name="NewName",
    )
    assert result is None

  async def test_delete_deck_instance(
    self,
    db: AsyncSession,
    setup_test_data: dict[str, Any],
  ):
    """Test deleting a deck instance."""
    deck_resource = setup_test_data["deck_resource"]
    plate_resource = setup_test_data["plate_resource"]

    position_data = [
      {
        "position_name": "A1",
        "resource_instance_accession_id": plate_resource.accession_id,
      },
    ]

    deck = await create_deck_instance(
      db=db,
      name="DeckToDelete",
      deck_accession_id=deck_resource.accession_id,
      python_fqn="fqn.delete",
      position_items_data=position_data,
    )
    deck_id = deck.accession_id

    # Ensure it's in the DB before deleting
    assert await read_deck_instance(db, deck_id) is not None
    pos_item_result = await db.execute(
      select(DeckPositionResourceOrm).filter_by(deck_accession_id=deck_id),
    )
    assert pos_item_result.scalar_one_or_none() is not None

    # Delete
    result = await delete_deck_instance(db, deck_id)
    assert result is True

    # Verify it's gone
    assert await read_deck_instance(db, deck_id) is None

    # Verify position items are also gone (due to cascade)
    pos_item_result = await db.execute(
      select(DeckPositionResourceOrm).filter_by(deck_accession_id=deck_id),
    )
    assert pos_item_result.scalar_one_or_none() is None

  async def test_delete_deck_instance_not_found(self, db: AsyncSession):
    """Test that deleting a non-existent deck instance returns False."""
    non_existent_id = uuid.uuid4()
    result = await delete_deck_instance(db, non_existent_id)
    assert result is False
