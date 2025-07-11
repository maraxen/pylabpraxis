import uuid
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models import DeckDefinitionOrm, PositioningConfig
from praxis.backend.services.deck_type_definition import (
  create_deck_type_definition,
  delete_deck_type_definition,
  list_deck_type_definitions,
  read_deck_type_definition,
  read_deck_type_definition_by_fqn,
  update_deck_type_definition,
)

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio


@pytest.fixture
def base_deck_type_data() -> dict[str, Any]:
  """Provides a base dictionary of valid data for creating a deck type definition."""
  return {
    "fqn": f"pylabrobot.resources.hamilton.STARDeck_{uuid.uuid4()}",
    "deck_type": "Hamilton STAR Deck",
    "description": "Standard deck for Hamilton STAR series.",
    "manufacturer": "Hamilton",
    "model": "STAR",
    "notes": "Requires specific carrier types.",
    "default_size_x_mm": 1200.0,
    "default_size_y_mm": 600.0,
    "default_size_z_mm": 20.0,
  }


@pytest.fixture
async def existing_deck_type(
  db: AsyncSession,
  base_deck_type_data: dict[str, Any],
) -> DeckDefinitionOrm:
  """Creates a DeckTypeDefinitionOrm in the DB for tests that need a pre-existing record."""
  return await create_deck_type_definition(db=db, **base_deck_type_data)


class TestDeckTypeDefinitionService:
  """Test suite for deck type definition service functions."""

  async def test_create_deck_type_definition_success(
    self,
    db: AsyncSession,
    base_deck_type_data: dict[str, Any],
  ) -> None:
    """Test successful creation of a deck type definition with minimal data."""
    created_deck_type = await create_deck_type_definition(
      db=db,
      fqn=base_deck_type_data["fqn"],
      deck_type=base_deck_type_data["deck_type"],
    )

    assert created_deck_type is not None
    assert created_deck_type.pylabrobot_deck_fqn == base_deck_type_data["fqn"]
    assert created_deck_type.display_name == base_deck_type_data["deck_type"]
    assert created_deck_type.accession_id is not None

  async def test_create_deck_type_with_all_args_and_positions(
    self,
    db: AsyncSession,
    base_deck_type_data: dict[str, Any],
  ) -> None:
    """Test creating a deck type with all optional arguments, including positions."""
    position_data = [
      {"position_name": "Slot1", "location_x_mm": 10.0},
      {"position_name": "Slot2", "location_y_mm": 100.0},
    ]
    # FIX: Explicitly provide arg_type to satisfy linter/constructor requirements.
    pos_config = PositioningConfig(
      method_name="get_slot",
      arg_name="slot_name",
      arg_type="str",
      params={},
    )
    base_deck_type_data["position_definitions_data"] = position_data
    base_deck_type_data["positioning_config"] = pos_config

    created_deck_type = await create_deck_type_definition(db=db, **base_deck_type_data)

    assert created_deck_type is not None
    # FIX: Assert the json blob is not None before accessing, and access via subscript.
    assert created_deck_type.additional_properties_json is not None
    assert created_deck_type.additional_properties_json["manufacturer"] == "Hamilton"
    assert created_deck_type.positioning_config_json is not None
    assert created_deck_type.positioning_config_json["method_name"] == "get_slot"
    assert len(created_deck_type.position_definitions) == 2
    # FIX: The attribute on the ORM model is 'name', not 'position_name'.
    assert {p.name for p in created_deck_type.position_definitions} == {
      "Slot1",
      "Slot2",
    }

  async def test_create_deck_type_fails_on_duplicate_fqn(
    self,
    db: AsyncSession,
    existing_deck_type: DeckDefinitionOrm,
  ) -> None:
    """Test that creating a deck type with a duplicate FQN raises ValueError."""
    with pytest.raises(ValueError, match="already exists"):
      await create_deck_type_definition(
        db=db,
        fqn=existing_deck_type.pylabrobot_deck_fqn,
        deck_type="Another Deck",
      )

  async def test_read_deck_type_definition(
    self,
    db: AsyncSession,
    existing_deck_type: DeckDefinitionOrm,
  ) -> None:
    """Test reading a deck type definition by its ID."""
    read_deck = await read_deck_type_definition(db, existing_deck_type.accession_id)
    assert read_deck is not None
    assert read_deck.accession_id == existing_deck_type.accession_id
    assert read_deck.display_name == existing_deck_type.display_name

  async def test_read_deck_type_definition_by_fqn(
    self,
    db: AsyncSession,
    existing_deck_type: DeckDefinitionOrm,
  ) -> None:
    """Test reading a deck type definition by its FQN."""
    read_deck = await read_deck_type_definition_by_fqn(
      db,
      existing_deck_type.pylabrobot_deck_fqn,
    )
    assert read_deck is not None
    assert read_deck.pylabrobot_deck_fqn == existing_deck_type.pylabrobot_deck_fqn

  async def test_read_non_existent_deck_type(self, db: AsyncSession) -> None:
    """Test that reading a non-existent deck type returns None."""
    bad_id = uuid.uuid4()
    assert await read_deck_type_definition(db, bad_id) is None
    assert await read_deck_type_definition_by_fqn(db, "non.existent.fqn") is None

  async def test_update_deck_type_definition(
    self,
    db: AsyncSession,
    existing_deck_type: DeckDefinitionOrm,
  ) -> None:
    """Test updating attributes of an existing deck type."""
    updated_data = {
      "deck_type_accession_id": existing_deck_type.accession_id,
      "fqn": existing_deck_type.pylabrobot_deck_fqn,
      "deck_type": "Updated Deck Name",
      "notes": "These are updated notes.",
    }

    updated_deck = await update_deck_type_definition(db=db, **updated_data)

    assert updated_deck is not None
    assert updated_deck.display_name == "Updated Deck Name"
    # FIX: Assert the json blob is not None before accessing, and access via subscript.
    assert updated_deck.additional_properties_json is not None
    assert updated_deck.additional_properties_json["notes"] == "These are updated notes."
    assert existing_deck_type.additional_properties_json is not None
    assert (
      updated_deck.additional_properties_json["manufacturer"]
      == existing_deck_type.additional_properties_json["manufacturer"]
    )

  async def test_update_deck_type_replaces_positions(
    self,
    db: AsyncSession,
    existing_deck_type: DeckDefinitionOrm,
  ) -> None:
    """Test that updating with new position data replaces the old positions."""
    # Add initial positions
    await update_deck_type_definition(
      db,
      deck_type_accession_id=existing_deck_type.accession_id,
      fqn=existing_deck_type.pylabrobot_deck_fqn,
      deck_type=existing_deck_type.display_name,
      position_definitions_data=[{"position_name": "OldSlot"}],
    )

    refreshed_deck = await read_deck_type_definition(
      db,
      existing_deck_type.accession_id,
    )
    # FIX: Add assertion to guard against None type.
    assert refreshed_deck is not None
    assert len(refreshed_deck.position_definitions) == 1
    # FIX: The attribute on the ORM model is 'name', not 'position_name'.
    assert refreshed_deck.position_definitions[0].name == "OldSlot"

    # Update with new positions
    new_position_data = [
      {"position_name": "NewSlot1"},
      {"position_name": "NewSlot2"},
    ]
    await update_deck_type_definition(
      db,
      deck_type_accession_id=existing_deck_type.accession_id,
      fqn=existing_deck_type.pylabrobot_deck_fqn,
      deck_type=existing_deck_type.display_name,
      position_definitions_data=new_position_data,
    )

    final_deck = await read_deck_type_definition(db, existing_deck_type.accession_id)
    # FIX: Add assertion to guard against None type.
    assert final_deck is not None
    assert len(final_deck.position_definitions) == 2
    # FIX: The attribute on the ORM model is 'name', not 'position_name'.
    assert {p.name for p in final_deck.position_definitions} == {
      "NewSlot1",
      "NewSlot2",
    }

  async def test_update_fails_on_fqn_conflict(
    self,
    db: AsyncSession,
    base_deck_type_data: dict[str, Any],
  ) -> None:
    """Test that updating an FQN to one that already exists fails."""
    deck1_data = base_deck_type_data.copy()
    deck2_data = base_deck_type_data.copy()
    deck2_data["fqn"] = f"pylabrobot.resources.deck_{uuid.uuid4()}"

    deck1 = await create_deck_type_definition(db, **deck1_data)
    deck2 = await create_deck_type_definition(db, **deck2_data)

    with pytest.raises(ValueError, match="already exists for another"):
      await update_deck_type_definition(
        db=db,
        deck_type_accession_id=deck2.accession_id,
        fqn=deck1.pylabrobot_deck_fqn,  # Try to change deck2's fqn to deck1's
        deck_type=deck2.display_name,
      )

  async def test_list_deck_type_definitions(
    self,
    db: AsyncSession,
    base_deck_type_data: dict[str, Any],
  ) -> None:
    """Test listing deck type definitions with pagination."""
    # Ensure at least 2 exist
    await create_deck_type_definition(db, **base_deck_type_data)
    base_deck_type_data["fqn"] = f"another.fqn.{uuid.uuid4()}"
    await create_deck_type_definition(db, **base_deck_type_data)

    all_defs = await list_deck_type_definitions(db, limit=10)
    assert len(all_defs) >= 2

    limited_defs = await list_deck_type_definitions(db, limit=1)
    assert len(limited_defs) == 1

    offset_defs = await list_deck_type_definitions(db, limit=1, offset=1)
    assert len(offset_defs) == 1
    assert offset_defs[0].accession_id != limited_defs[0].accession_id

  async def test_delete_deck_type_definition(
    self,
    db: AsyncSession,
    existing_deck_type: DeckDefinitionOrm,
  ) -> None:
    """Test deleting a deck type definition."""
    deck_type_id = existing_deck_type.accession_id

    # Confirm it exists
    assert await read_deck_type_definition(db, deck_type_id) is not None

    # Delete it
    await delete_deck_type_definition(db, deck_type_id)

    # Confirm it's gone
    assert await read_deck_type_definition(db, deck_type_id) is None

  async def test_delete_non_existent_deck_type_fails(self, db: AsyncSession) -> None:
    """Test that deleting a non-existent deck type raises ValueError."""
    bad_id = uuid.uuid4()
    with pytest.raises(ValueError, match="not found"):
      await delete_deck_type_definition(db, bad_id)
