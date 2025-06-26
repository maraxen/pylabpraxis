# pylint: disable=broad-except, too-many-lines
"""Service layer for Deck  Management.

This service layer interacts with deck-related data in the database, providing
functions to create, read, update, and delete decks.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import flag_modified

from praxis.backend.models import DeckOrm
from praxis.backend.models.deck_pydantic_models import DeckCreate, DeckUpdate
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)

UUID = uuid.UUID


async def create_deck(db: AsyncSession, deck_create: DeckCreate) -> DeckOrm:
  """Create a new deck.

  Args:
      db: The database session.
      deck_create: Pydantic model with deck data.

  Returns:
      The created deck object.

  Raises:
      ValueError: If validation fails.
      Exception: For any other unexpected errors.

  """
  logger.info(
    "Attempting to create deck '%s' for parent ID %s.",
    deck_create.name,
    deck_create.parent_accession_id,
  )

  deck_data = deck_create.model_dump(exclude={"plr_state"})
  deck_orm = DeckOrm(**deck_data)

  if deck_create.plr_state:
    deck_orm.plr_state = deck_create.plr_state

  db.add(deck_orm)

  try:
    await db.commit()
    await db.refresh(deck_orm)
    logger.info(
      "Successfully created deck '%s' with ID %s.",
      deck_orm.name,
      deck_orm.accession_id,
    )
  except IntegrityError as e:
    await db.rollback()
    error_message = f"Deck with name '{deck_create.name}' already exists. Details: {e}"
    logger.exception(error_message)
    raise ValueError(error_message) from e
  except Exception as e:  # Catch all for truly unexpected errors
    logger.exception("Error creating deck '%s'. Rolling back.", deck_create.name)
    await db.rollback()
    raise e

  return deck_orm


async def read_deck(db: AsyncSession, deck_accession_id: UUID) -> DeckOrm | None:
  """Retrieve a specific deck by its ID.

  Args:
      db: The database session.
      deck_accession_id: The ID of the deck to retrieve.

  Returns:
      The deck object if found, otherwise None.

  """
  logger.info("Attempting to retrieve deck with ID: %s.", deck_accession_id)
  stmt = (
    select(DeckOrm)
    .options(
      joinedload(DeckOrm.parent),
      joinedload(DeckOrm.deck_type),
    )
    .filter(DeckOrm.accession_id == deck_accession_id)
  )
  result = await db.execute(stmt)
  deck = result.scalar_one_or_none()
  if deck:
    logger.info(
      "Successfully retrieved deck ID %s: '%s'.",
      deck_accession_id,
      deck.name,
    )
  else:
    logger.info("Deck with ID %s not found.", deck_accession_id)
  return deck


async def read_decks(
  db: AsyncSession,
  parent_accession_id: UUID | None = None,
  limit: int = 100,
  offset: int = 0,
) -> list[DeckOrm]:
  """List all decks, with optional filtering by parent ID.

  Args:
      db: The database session.
      parent_accession_id: The ID of the parent asset to filter by.
      limit: The maximum number of results to return.
      offset: The number of results to skip.

  Returns:
      A list of deck objects.

  """
  logger.info(
    "Listing decks with parent ID filter: %s, limit: %s, offset: %s.",
    parent_accession_id,
    limit,
    offset,
  )
  stmt = select(DeckOrm).options(
    joinedload(DeckOrm.parent),
    joinedload(DeckOrm.deck_type),
  )
  if parent_accession_id is not None:
    stmt = stmt.filter(DeckOrm.parent_accession_id == parent_accession_id)
  stmt = stmt.order_by(DeckOrm.name).limit(limit).offset(offset)
  result = await db.execute(stmt)
  decks = list(result.scalars().all())
  logger.info("Found %s decks.", len(decks))
  return decks


async def read_decks_by_machine_id(
  db: AsyncSession,
  machine_accession_id: UUID,
  limit: int = 100,
  offset: int = 0,
) -> list[DeckOrm]:
  """List all decks associated with a specific machine ID.

  Args:
      db: The database session.
      machine_accession_id: The ID of the machine to filter by.
      limit: The maximum number of results to return.
      offset: The number of results to skip.

  Returns:
      A list of deck objects.

  """
  logger.info(
    "Listing decks for machine ID: %s, limit: %s, offset: %s.",
    machine_accession_id,
    limit,
    offset,
  )
  stmt = select(DeckOrm).filter(DeckOrm.machine_id == machine_accession_id)
  stmt = stmt.order_by(DeckOrm.name).limit(limit).offset(offset)
  result = await db.execute(stmt)
  decks = list(result.scalars().all())
  logger.info("Found %s decks for machine ID %s.", len(decks), machine_accession_id)
  return decks


async def read_deck_by_name(db: AsyncSession, name: str) -> DeckOrm | None:
  """Retrieve a specific deck by its name.

  Args:
      db: The database session.
      name: The name of the deck to retrieve.

  Returns:
      The deck object if found, otherwise None.

  """
  logger.info("Attempting to retrieve deck with name: '%s'.", name)
  stmt = (
    select(DeckOrm)
    .options(
      joinedload(DeckOrm.parent),
      joinedload(DeckOrm.deck_type),
    )
    .filter(DeckOrm.name == name)
  )
  result = await db.execute(stmt)
  deck = result.scalar_one_or_none()
  if deck:
    logger.info("Successfully retrieved deck by name '%s'.", name)
  else:
    logger.info("Deck with name '%s' not found.", name)
  return deck


async def update_deck(
  db: AsyncSession,
  deck_accession_id: UUID,
  deck_update: DeckUpdate,
) -> DeckOrm | None:
  """Update an existing deck.

  Args:
      db: The database session.
      deck_accession_id: The ID of the deck to update.
      deck_update: Pydantic model with updated data.

  Returns:
      The updated deck object if successful, otherwise None.

  """
  logger.info("Attempting to update deck with ID: %s.", deck_accession_id)
  deck_orm = await read_deck(db, deck_accession_id)
  if not deck_orm:
    logger.warning("Deck with ID %s not found for update.", deck_accession_id)
    return None

  update_data = deck_update.model_dump(exclude_unset=True)
  for key, value in update_data.items():
    if hasattr(deck_orm, key):
      setattr(deck_orm, key, value)

  if "plr_state" in update_data:
    flag_modified(deck_orm, "plr_state")

  try:
    await db.commit()
    await db.refresh(deck_orm)
    logger.info(
      "Successfully updated deck ID %s: '%s'.",
      deck_accession_id,
      deck_orm.name,
    )
    return await read_deck(db, deck_accession_id)
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error while updating deck ID {deck_accession_id}. Details: {e}"
    )
    logger.exception(error_message)
    raise ValueError(error_message) from e
  except Exception as e:  # Catch all for truly unexpected errors
    await db.rollback()
    logger.exception(
      "Unexpected error updating deck ID %s. Rolling back.",
      deck_accession_id,
    )
    raise e


async def delete_deck(db: AsyncSession, deck_accession_id: UUID) -> bool:
  """Delete a specific deck by its ID.

  Args:
      db: The database session.
      deck_accession_id: The ID of the deck to delete.

  Returns:
      True if the deletion was successful, False if the deck was not found.

  """
  logger.info("Attempting to delete deck with ID: %s.", deck_accession_id)
  deck_orm = await read_deck(db, deck_accession_id)
  if not deck_orm:
    logger.warning("Deck with ID %s not found for deletion.", deck_accession_id)
    return False

  try:
    await db.delete(deck_orm)
    await db.commit()
    logger.info(
      "Successfully deleted deck ID %s: '%s'.",
      deck_accession_id,
      deck_orm.name,
    )
    return True
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error deleting deck ID {deck_accession_id}. "
      f"This might be due to foreign key constraints. Details: {e}"
    )
    logger.exception(error_message)
    raise ValueError(error_message) from e
  except Exception as e:  # Catch all for truly unexpected errors
    await db.rollback()
    logger.exception(
      "Unexpected error deleting deck ID %s. Rolling back.",
      deck_accession_id,
    )
    raise e
