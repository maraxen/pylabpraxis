import uuid
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models import (
  DeckDefinitionOrm,
  DeckOrm,
  ResourceDefinitionOrm,
  ResourceOrm,
)
from praxis.backend.services.deck_position import (
  create_deck_position_definitions,
  create_deck_position_item,
  delete_deck_position_definition,
  delete_deck_position_item,
  read_deck_position_item,
  read_position_definitions_for_deck_type,
  update_deck_position_definition,
  update_deck_position_item,
)

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
async def setup_test_data_for_items(db: AsyncSession) -> dict[str, Any]:
  """Set up data for testing DeckPositionResourceOrm operations."""
  deck_def = ResourceDefinitionOrm(
    name="deck_def_for_pos_test",
    fqn="some.deck.def",
  )
  plate_def = ResourceDefinitionOrm(
    name="plate_def_for_pos_test",
    fqn="some.plate.def",
  )
  db.add_all([deck_def, plate_def])
  await db.flush()

  deck_resource = ResourceOrm(
    name="DeckResourceForPosTest",
    resource_definition_name=deck_def.name,
    accession_id=uuid.uuid4(),
  )
  plate_resource = ResourceOrm(
    name="PlateResourceForPosTest",
    resource_definition_name=plate_def.name,
    accession_id=uuid.uuid4(),
  )
  db.add_all([deck_resource, plate_resource])
  await db.flush()

  deck = DeckOrm(
    name="DeckForPosTest",
    deck_accession_id=deck_resource.accession_id,
    fqn="some.deck.fqn",
    accession_id=uuid.uuid4(),
  )
  db.add(deck)
  await db.commit()

  return {
    "deck": deck,
    "plate_resource": plate_resource,
    "plate_def": plate_def,
  }


@pytest.fixture
async def setup_test_data_for_definitions(db: AsyncSession) -> DeckDefinitionOrm:
  """Set up data for testing DeckPositionDefinitionOrm operations."""
  deck_type = DeckDefinitionOrm(
    pylabrobot_deck_fqn="pylabrobot.deck.for_def_test",
    display_name="Test Deck Type for Definitions",
    accession_id=uuid.uuid4(),
  )
  db.add(deck_type)
  await db.commit()
  return deck_type


class TestDeckPositionService:
  """Tests for functions managing DeckPositionResourceOrm (items on a deck)."""

  async def test_create_deck_position_item_success(
    self,
    db: AsyncSession,
    setup_test_data_for_items: dict[str, Any],
  ):
    """Test successfully creating a new position item on a deck instance."""
    deck = setup_test_data_for_items["deck"]
    plate_resource = setup_test_data_for_items["plate_resource"]
    plate_def = setup_test_data_for_items["plate_def"]

    pos_item = await create_deck_position_item(
      db=db,
      deck_accession_id=deck.accession_id,
      name="A1",
      resource_accession_id=plate_resource.accession_id,
      expected_resource_definition_name=plate_def.name,
    )

    assert pos_item is not None
    assert pos_item.deck_accession_id == deck.accession_id
    assert pos_item.position_name == "A1"
    assert pos_item.resource_accession_id == plate_resource.accession_id
    assert pos_item.expected_resource_definition_name == plate_def.name

  async def test_create_deck_position_item_fails_for_bad_deck_id(
    self,
    db: AsyncSession,
  ):
    """Test that creating a position item fails if the deck instance ID is invalid."""
    bad_deck_id = uuid.uuid4()
    with pytest.raises(ValueError, match="DeckOrm with id .* not found"):
      await create_deck_position_item(db, deck_accession_id=bad_deck_id, name="A1")

  async def test_read_deck_position_item(
    self,
    db: AsyncSession,
    setup_test_data_for_items: dict[str, Any],
  ):
    """Test reading a specific position item by its ID."""
    deck = setup_test_data_for_items["deck"]
    created_item = await create_deck_position_item(
      db,
      deck_accession_id=deck.accession_id,
      name="B2",
    )
    assert created_item is not None

    read_item = await read_deck_position_item(db, created_item.accession_id)
    assert read_item is not None
    assert read_item.accession_id == created_item.accession_id
    assert read_item.position_name == "B2"

  async def test_update_deck_position_item(
    self,
    db: AsyncSession,
    setup_test_data_for_items: dict[str, Any],
  ):
    """Test updating an existing position item."""
    deck = setup_test_data_for_items["deck"]
    plate_resource = setup_test_data_for_items["plate_resource"]
    created_item = await create_deck_position_item(
      db,
      deck_accession_id=deck.accession_id,
      name="C3",
    )
    assert created_item is not None
    assert created_item.resource_accession_id is None

    updated_item = await update_deck_position_item(
      db=db,
      position_item_accession_id=created_item.accession_id,
      resource_accession_id=plate_resource.accession_id,
    )

    assert updated_item is not None
    assert updated_item.accession_id == created_item.accession_id
    assert updated_item.resource_accession_id == plate_resource.accession_id

  async def test_delete_deck_position_item(
    self,
    db: AsyncSession,
    setup_test_data_for_items: dict[str, Any],
  ):
    """Test deleting a position item."""
    deck = setup_test_data_for_items["deck"]
    created_item = await create_deck_position_item(
      db,
      deck_accession_id=deck.accession_id,
      name="D4",
    )
    assert created_item is not None

    # Confirm it exists
    assert await read_deck_position_item(db, created_item.accession_id) is not None

    # Delete it
    result = await delete_deck_position_item(db, created_item.accession_id)
    assert result is True

    # Confirm it's gone
    assert await read_deck_position_item(db, created_item.accession_id) is None

  async def test_delete_non_existent_position_item(self, db: AsyncSession):
    """Test that deleting a non-existent position item returns False."""
    bad_id = uuid.uuid4()
    result = await delete_deck_position_item(db, bad_id)
    assert result is False


class TestDeckPositionDefinitionService:
  """Tests for functions managing DeckPositionDefinitionOrm (definitions for a deck type)."""

  async def test_create_deck_position_definitions_success(
    self,
    db: AsyncSession,
    setup_test_data_for_definitions: DeckDefinitionOrm,
  ):
    """Test successfully creating multiple position definitions for a deck type."""
    deck_type = setup_test_data_for_definitions
    new_positions_data = [
      {"name": "Slot1", "location_x_mm": 10.0},
      {
        "name": "Trash",
        "location_y_mm": 200.0,
        "notes": "For waste disposal",
        "allowed_resource_categories": ["trash_bin"],
      },
    ]

    created_defs = await create_deck_position_definitions(
      db,
      deck_type.accession_id,
      new_positions_data,
    )

    assert len(created_defs) == 2
    assert created_defs[0].name == "Slot1"
    assert created_defs[0].nominal_x_mm == 10.0
    assert created_defs[1].name == "Trash"
    assert created_defs[1].accepted_resource_categories_json == ["trash_bin"]

  async def test_create_deck_position_definitions_fails_for_bad_deck_type(
    self,
    db: AsyncSession,
  ):
    """Test failure when creating definitions for a non-existent deck type."""
    bad_deck_type_id = uuid.uuid4()
    with pytest.raises(ValueError, match="DeckTypeDefinitionOrm with id .* not found"):
      await create_deck_position_definitions(db, bad_deck_type_id, [{"name": "Slot1"}])

  async def test_read_position_definitions_for_deck_type(
    self,
    db: AsyncSession,
    setup_test_data_for_definitions: DeckDefinitionOrm,
  ):
    """Test reading all position definitions for a specific deck type."""
    deck_type = setup_test_data_for_definitions
    new_positions_data = [{"name": "PosA"}, {"name": "PosB"}]
    await create_deck_position_definitions(
      db,
      deck_type.accession_id,
      new_positions_data,
    )

    read_defs = await read_position_definitions_for_deck_type(
      db,
      deck_type.accession_id,
    )

    assert len(read_defs) == 2
    assert {d.name for d in read_defs} == {"PosA", "PosB"}

  async def test_update_deck_position_definition(
    self,
    db: AsyncSession,
    setup_test_data_for_definitions: DeckDefinitionOrm,
  ):
    """Test updating an existing position definition."""
    deck_type = setup_test_data_for_definitions
    await create_deck_position_definitions(
      db,
      deck_type.accession_id,
      [{"name": "UpdatableSlot"}],
    )

    updated_def = await update_deck_position_definition(
      db=db,
      deck_type_id=deck_type.accession_id,
      name="UpdatableSlot",
      location_z_mm=5.5,
      notes="This slot has been updated.",
    )

    assert updated_def is not None
    assert updated_def.name == "UpdatableSlot"
    assert updated_def.nominal_z_mm == 5.5
    assert updated_def.position_specific_details_json is not None
    assert updated_def.position_specific_details_json.get("notes") == "This slot has been updated."

  async def test_update_non_existent_position_definition_fails(
    self,
    db: AsyncSession,
    setup_test_data_for_definitions: DeckDefinitionOrm,
  ):
    """Test that updating a non-existent position definition raises ValueError."""
    deck_type = setup_test_data_for_definitions
    with pytest.raises(ValueError, match="Position definition not found for update"):
      await update_deck_position_definition(
        db,
        deck_type.accession_id,
        "NonExistentSlot",
        location_x_mm=1.0,
      )

  async def test_delete_deck_position_definition(
    self,
    db: AsyncSession,
    setup_test_data_for_definitions: DeckDefinitionOrm,
  ):
    """Test deleting a specific position definition."""
    deck_type = setup_test_data_for_definitions
    await create_deck_position_definitions(
      db,
      deck_type.accession_id,
      [{"name": "DeletableSlot"}],
    )

    # Confirm it exists
    defs_before = await read_position_definitions_for_deck_type(
      db,
      deck_type.accession_id,
    )
    assert len(defs_before) == 1

    # Delete it
    await delete_deck_position_definition(db, deck_type.accession_id, "DeletableSlot")

    # Confirm it's gone
    defs_after = await read_position_definitions_for_deck_type(
      db,
      deck_type.accession_id,
    )
    assert len(defs_after) == 0

  async def test_delete_non_existent_position_definition_fails(
    self,
    db: AsyncSession,
    setup_test_data_for_definitions: DeckDefinitionOrm,
  ):
    """Test that deleting a non-existent position definition raises ValueError."""
    deck_type = setup_test_data_for_definitions
    with pytest.raises(ValueError, match="Position definition not found for deletion"):
      await delete_deck_position_definition(
        db,
        deck_type.accession_id,
        "NonExistentSlot",
      )
