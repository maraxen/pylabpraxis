# pylint: disable=broad-except, too-many-lines
"""Service layer for Deck  Management.

This service layer interacts with deck-related data in the database, providing
functions to create, read, update, and delete decks.
"""

import enum
import uuid

from sqlalchemy import and_, or_, select
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified

from praxis.backend.models import Machine, ResourceDefinition
from praxis.backend.models.domain.deck import (
  Deck as Deck,
)
from praxis.backend.models.domain.deck import (
  DeckCreate,
  DeckUpdate,
)
from praxis.backend.models.domain.filters import SearchFilters
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.services.utils.query_builder import (
  apply_date_range_filters,
  apply_pagination,
  apply_property_filters,
  apply_specific_id_filters,
)
from praxis.backend.utils.db_decorator import handle_db_transaction
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)

UUID = uuid.UUID


class DeckService(CRUDBase[Deck, DeckCreate, DeckUpdate]):
  """Service for deck-related operations."""

  def _prepare_deck_data(self, obj_in: DeckCreate) -> dict:
    """Prepare data for creating a new deck."""
    deck_data = obj_in.model_dump(
      exclude={
        "plr_state",
        "created_at",
        "updated_at",
        "children",
        "parent",
        "child_accession_ids",
        "machine_initial_status",
        "deck_initial_status",
      },
    )
    machine_id_to_use = deck_data.pop("machine_id", None) or deck_data.pop(
      "parent_accession_id",
      None,
    )
    if machine_id_to_use:
      deck_data["parent_machine_accession_id"] = machine_id_to_use
    return deck_data

  def _filter_and_convert_enums(self, deck_data: dict) -> dict:
    """Filter data and convert enums for ORM compatibility."""
    # Do not filter by __init__ signature; preserve all provided fields so
    # required values (like `name`) are not unintentionally dropped.
    filtered_data = dict(deck_data)

    for attr_name, column in sa_inspect(self.model).columns.items():
      if attr_name in filtered_data:
        value = filtered_data[attr_name]
        if value is None:
          continue

        # Handle Enum conversion
        enum_class = getattr(column.type, "enum_class", None)
        if enum_class and issubclass(enum_class, enum.Enum):
          if isinstance(value, str):
            # Try to match by value first
            matched = False
            for member in enum_class:
              if member.value.lower() == value.lower():
                filtered_data[attr_name] = member
                matched = True
                break
            # If not found by value, try by name
            if not matched:
              for name in enum_class.__members__:
                if name.lower() == value.lower():
                  filtered_data[attr_name] = enum_class[name]
                  matched = True
                  break
    return filtered_data

  async def _handle_relationships(
    self,
    db: AsyncSession,
    deck_model: Deck,
    filtered_data: dict,
  ) -> None:
    """Handle relationships for the deck."""
    if "resource_definition_accession_id" in filtered_data:
      res_def = await db.get(
        ResourceDefinition,
        filtered_data["resource_definition_accession_id"],
      )
      if res_def:
        deck_model.resource_definition = res_def
      else:
        deck_model.resource_definition_accession_id = filtered_data[
          "resource_definition_accession_id"
        ]

    if "parent_machine_accession_id" in filtered_data:
      machine = await db.get(
        Machine,
        filtered_data["parent_machine_accession_id"],
      )
      if machine:
        deck_model.parent_machine = machine

  @handle_db_transaction
  async def create(
    self,
    db: AsyncSession,
    *,
    obj_in: DeckCreate,
  ) -> Deck:
    """Create a new deck."""
    logger.info(
      "Attempting to create deck '%s' for parent ID %s.",
      obj_in.name,
      obj_in.parent_accession_id,
    )

    deck_data = self._prepare_deck_data(obj_in)
    filtered_data = self._filter_and_convert_enums(deck_data)
    deck_model = self.model(**filtered_data)
    await self._handle_relationships(db, deck_model, filtered_data)

    if obj_in.plr_state:
      deck_model.plr_state = obj_in.plr_state

    db.add(deck_model)
    await db.flush()
    await db.refresh(
      deck_model,
      [
        "deck_type",
        "parent_machine",
        "children",
        "resource_definition",
        "parent",
      ],
    )
    logger.info(
      "Successfully created deck '%s' with ID %s.",
      deck_model.name,
      deck_model.accession_id,
    )
    return deck_model

  async def get(
    self,
    db: AsyncSession,
    accession_id: str | UUID,
  ) -> Deck | None:
    """Retrieve a specific deck by its ID."""
    logger.info("Attempting to retrieve deck with ID: %s.", accession_id)
    stmt = (
      select(self.model)
      .options(
        selectinload(self.model.parent),
        selectinload(self.model.parent_machine),
        selectinload(self.model.deck_type),
        selectinload(self.model.children),
      )
      .filter(self.model.accession_id == accession_id)
    )
    result = await db.execute(stmt)
    deck = result.scalar_one_or_none()
    if deck:
      logger.info(
        "Successfully retrieved deck ID %s: '%s'.",
        accession_id,
        deck.name,
      )
    else:
      logger.info("Deck with ID %s not found.", accession_id)
    return deck

  async def get_multi(
    self,
    db: AsyncSession,
    *,
    filters: SearchFilters,
  ) -> list[Deck]:
    """List all decks, with optional filtering by parent ID."""
    logger.info(
      "Listing decks with filters: %s",
      filters.model_dump_json(),
    )
    stmt = select(self.model).options(
      selectinload(self.model.parent),
      selectinload(self.model.parent_machine),
      selectinload(self.model.deck_type),
      selectinload(self.model.children),
    )

    conditions = []

    if filters.parent_accession_id is not None:
      conditions.append(
        or_(
          self.model.parent_accession_id == filters.parent_accession_id,
          self.model.parent_machine_accession_id == filters.parent_accession_id,
        ),
      )

    if conditions:
      stmt = stmt.filter(and_(*conditions))

    stmt = apply_specific_id_filters(stmt, filters, self.model)
    stmt = apply_date_range_filters(stmt, filters, Deck.created_at)
    stmt = apply_property_filters(
      stmt,
      filters,
      self.model.properties_json,
    )

    stmt = stmt.order_by(self.model.name)
    stmt = apply_pagination(stmt, filters)

    result = await db.execute(stmt)
    decks = list(result.scalars().all())
    logger.info("Found %s decks.", len(decks))
    return decks

  @handle_db_transaction
  async def update(
    self,
    db: AsyncSession,
    *,
    db_obj: Deck,
    obj_in: DeckUpdate,
  ) -> Deck:
    """Update an existing deck."""
    logger.info(
      "Attempting to update deck with ID: %s.",
      db_obj.accession_id,
    )

    update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
      if hasattr(db_obj, key):
        setattr(db_obj, key, value)

    if "plr_state" in update_data:
      flag_modified(db_obj, "plr_state")

    await db.flush()
    await db.flush()
    await db.refresh(db_obj)
    logger.info(
      "Successfully updated deck ID %s: '%s'.",
      db_obj.accession_id,
      db_obj.name,
    )
    return db_obj

  async def remove(
    self,
    db: AsyncSession,
    *,
    accession_id: str | UUID,
  ) -> Deck | None:
    """Delete a specific deck by its ID."""
    logger.info("Attempting to delete deck with ID: %s.", accession_id)
    deck_model = await self.get(db, accession_id)
    if not deck_model:
      logger.warning(
        "Deck with ID %s not found for deletion.",
        accession_id,
      )
      return None

    await db.delete(deck_model)
    await db.flush()
    logger.info(
      "Successfully deleted deck ID %s: '%s'.",
      accession_id,
      deck_model.name,
    )
    return deck_model

  async def get_all_decks(self, db: AsyncSession) -> list[Deck]:
    """Retrieve all decks from the database."""
    logger.info("Retrieving all decks.")
    stmt = select(self.model).options(
      selectinload(self.model.parent),
      selectinload(self.model.parent_machine),
      selectinload(self.model.deck_type),
    )
    result = await db.execute(stmt)
    decks = list(result.scalars().all())
    logger.info("Found %d decks.", len(decks))
    return decks

  async def read_decks_by_machine_id(
    self,
    db: AsyncSession,
    machine_id: uuid.UUID,
  ) -> Deck | None:
    """Read a deck for a given machine."""
    stmt = select(self.model).filter(
      self.model.parent_machine_accession_id == machine_id,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


deck_service = DeckService(Deck)
