# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument
"""Service layer for Workcell Data Management.

praxis/db_services/workcell_data_service.py

Service layer for interacting with workcell-related data in the database.
This includes Workcell configurations and their associated machines.

This module provides functions to create, read, update, and delete workcell entries.
"""

import datetime
import logging
from typing import Any, Dict, List, Optional


import uuid
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from praxis.backend.models import MachineOrm, WorkcellOrm
from praxis.backend.utils.uuid import uuid7

logger = logging.getLogger(__name__)


async def create_workcell(
  db: AsyncSession,
  name: str,
  description: Optional[str] = None,
  physical_location: Optional[str] = None,
  initial_state: Optional[dict] = None,
) -> WorkcellOrm:
  """Create a new workcell.

  Args:
    db (AsyncSession): The database session.
    name (str): The unique name of the workcell.
    description (Optional[str]): A description of the workcell.
    physical_location (Optional[str]): The physical location of the workcell.

  Returns:
    WorkcellOrm: The created workcell object.

  Raises:
    ValueError: If a workcell with the same name already exists.
    Exception: For any other unexpected errors during the process.

  """
  logger.info("Attempting to create workcell '%s'.", name)

  workcell_orm = WorkcellOrm(
    id=uuid7(),
    name=name,
    description=description,
    physical_location=physical_location,
    latest_state_json=initial_state,
    last_state_update_time=datetime.datetime.now(datetime.timezone.utc),
  )
  db.add(workcell_orm)

  try:
    await db.commit()
    await db.refresh(workcell_orm)
    logger.info(
      "Successfully created workcell '%s' with ID %s.", name, workcell_orm.accession_id
    )
    return workcell_orm
  except IntegrityError as e:
    await db.rollback()
    error_message = f"Workcell with name '{name}' already exists. Details: {e}"
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    logger.exception("Error creating workcell '%s'. Rolling back.", name)
    await db.rollback()
    raise e


async def read_workcell(
  db: AsyncSession, workcell_accession_id: uuid.UUID
) -> Optional[WorkcellOrm]:
  """Retrieve a specific workcell by its ID.

  Args:
    db (AsyncSession): The database session.
    workcell_accession_id (uuid.UUID): The ID of the workcell to retrieve.

  Returns:
    Optional[WorkcellOrm]: The workcell object if found, otherwise None.

  """
  logger.info("Attempting to retrieve workcell with ID: %s.", workcell_accession_id)
  stmt = (
    select(WorkcellOrm)
    .options(selectinload(WorkcellOrm.machines))
    .filter(WorkcellOrm.accession_id == workcell_accession_id)
  )
  result = await db.execute(stmt)
  workcell = result.scalar_one_or_none()
  if workcell:
    logger.info(
      "Successfully retrieved workcell ID %s: '%s'.",
      workcell_accession_id,
      workcell.name,
    )
  else:
    logger.info("Workcell with ID %s not found.", workcell_accession_id)
  return workcell


async def read_workcell_by_name(db: AsyncSession, name: str) -> Optional[WorkcellOrm]:
  """Retrieve a specific workcell by its name.

  Args:
    db (AsyncSession): The database session.
    name (str): The name of the workcell to retrieve.

  Returns:
    Optional[WorkcellOrm]: The workcell object if found, otherwise None.

  """
  logger.info("Attempting to retrieve workcell with name: '%s'.", name)
  stmt = (
    select(WorkcellOrm)
    .options(selectinload(WorkcellOrm.machines))
    .filter(WorkcellOrm.name == name)
  )
  result = await db.execute(stmt)
  workcell = result.scalar_one_or_none()
  if workcell:
    logger.info("Successfully retrieved workcell by name '%s'.", name)
  else:
    logger.info("Workcell with name '%s' not found.", name)
  return workcell


async def list_workcells(
  db: AsyncSession, limit: int = 100, offset: int = 0
) -> List[WorkcellOrm]:
  """List all workcells with pagination.

  Args:
    db (AsyncSession): The database session.
    limit (int): The maximum number of results to return.
    offset (int): The number of results to skip before returning.

  Returns:
    List[WorkcellOrm]: A list of workcell objects.
  """
  logger.info("Listing workcells with limit: %d, offset: %d.", limit, offset)
  stmt = (
    select(WorkcellOrm)
    .options(selectinload(WorkcellOrm.machines))
    .order_by(WorkcellOrm.name)
    .limit(limit)
    .offset(offset)
  )
  result = await db.execute(stmt)
  workcells = list(result.scalars().all())
  logger.info("Found %d workcells.", len(workcells))
  return workcells


async def update_workcell(
  db: AsyncSession,
  workcell_accession_id: uuid.UUID,
  name: Optional[str] = None,
  description: Optional[str] = None,
  physical_location: Optional[str] = None,
) -> Optional[WorkcellOrm]:
  """Update an existing workcell.

  Args:
    db (AsyncSession): The database session.
    workcell_accession_id (uuid.UUID): The ID of the workcell to update.
    name (Optional[str]): The new name for the workcell.
    description (Optional[str]): The new description for the workcell.
    physical_location (Optional[str]): The new physical location for the workcell.

  Returns:
    Optional[WorkcellOrm]: The updated workcell object if successful,
    otherwise None if the workcell was not found.

  Raises:
    ValueError: If a workcell with the new name already exists.
    Exception: For any other unexpected errors during the process.

  """
  logger.info("Attempting to update workcell with ID: %s.", workcell_accession_id)
  workcell_orm = await read_workcell(db, workcell_accession_id)
  if not workcell_orm:
    logger.warning("Workcell with ID %s not found for update.", workcell_accession_id)
    return None

  original_name = workcell_orm.name
  updates_made = False

  if name is not None and workcell_orm.name != name:
    logger.debug("Updating name from '%s' to '%s'.", workcell_orm.name, name)
    workcell_orm.name = name
    updates_made = True
  if description is not None and workcell_orm.description != description:
    logger.debug("Updating description for workcell '%s'.", original_name)
    workcell_orm.description = description
    updates_made = True
  if (
    physical_location is not None
    and workcell_orm.physical_location != physical_location
  ):
    logger.debug("Updating physical location for workcell '%s'.", original_name)
    workcell_orm.physical_location = physical_location
    updates_made = True

  if not updates_made:
    logger.info(
      "No changes detected for workcell ID %s. No update performed.",
      workcell_accession_id,
    )
    return workcell_orm

  try:
    await db.commit()
    await db.refresh(workcell_orm)
    logger.info(
      "Successfully updated workcell ID %s: '%s'.",
      workcell_accession_id,
      workcell_orm.name,
    )
    return workcell_orm
  except IntegrityError as e:
    await db.rollback()
    error_message = f"Workcell with name '{name}' already exists. Details: {e}"
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error updating workcell '%s' (ID: %s). Rolling back.",
      original_name,
      workcell_accession_id,
    )
    raise e


async def delete_workcell(db: AsyncSession, workcell_accession_id: uuid.UUID) -> bool:
  """Delete a specific workcell by its ID.

  This function deletes a workcell. Note that if there are machines
  linked to this workcell, the foreign key constraint might prevent deletion
  or require handling (e.g., setting `workcell_accession_id` to NULL in `MachineOrm`).

  Args:
    db (AsyncSession): The database session.
    workcell_accession_id (uuid.UUID): The ID of the workcell to delete.

  Returns:
    bool: True if the deletion was successful, False if the workcell was not found.

  Raises:
    Exception: For any unexpected errors during deletion.

  """
  logger.info("Attempting to delete workcell with ID: %s.", workcell_accession_id)
  workcell_orm = await read_workcell(db, workcell_accession_id)
  if not workcell_orm:
    logger.warning("Workcell with ID %s not found for deletion.", workcell_accession_id)
    return False

  try:
    await db.delete(workcell_orm)
    await db.commit()
    logger.info(
      "Successfully deleted workcell ID %s: '%s'.",
      workcell_accession_id,
      workcell_orm.name,
    )
    return True
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error deleting workcell ID {workcell_accession_id}. This might be due to"
      f" foreign key constraints, e.g., associated machines. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    return False
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error deleting workcell ID %s. Rolling back.", workcell_accession_id
    )
    raise e


async def read_or_create_workcell_orm(
  db_session: AsyncSession,
  workcell_name: str,
  initial_state: Optional[Dict[str, Any]] = None,
) -> WorkcellOrm:
  """Retrieve a WorkcellOrm by name, or create it if it doesn't exist.

  Args:
    db_session (AsyncSession): The database session.
    workcell_name (str): The name of the workcell to retrieve or create.
    initial_state (Optional[Dict[str, Any]]): Initial state JSON to set if creating.

  Returns:
    WorkcellOrm: The retrieved or newly created WorkcellOrm.

  Raises:
    Exception: If there is an error during the database operation.

  """
  try:
    stmt = select(WorkcellOrm).filter_by(name=workcell_name)
    result = await db_session.execute(stmt)
    workcell_orm = result.scalar_one_or_none()

    if workcell_orm:
      logger.info(f"WorkcellOrm '{workcell_name}' found in DB.")
      return workcell_orm
    else:
      logger.info(f"WorkcellOrm '{workcell_name}' not found, creating new entry.")
      new_workcell = WorkcellOrm(
        id=uuid7(),
        name=workcell_name,
        latest_state_json=initial_state,
      )
      db_session.add(new_workcell)
      await db_session.flush()
      await db_session.refresh(new_workcell)
      return new_workcell
  except Exception as e:
    logger.error(
      f"Failed to get or create WorkcellOrm '{workcell_name}': {e}", exc_info=True
    )
    raise


async def read_workcell_state(
  db_session: AsyncSession, workcell_accession_id: uuid.UUID
) -> Optional[Dict[str, Any]]:
  """Retrieve the latest JSON-serialized state of a workcell from the database.

  Args:
    db_session (AsyncSession): The database session.
    workcell_accession_id (uuid.UUID): The ID of the workcell to retrieve the state for.

  Returns:
    Optional[Dict[str, Any]]: The latest state JSON if found, otherwise None.

  Raises:
    Exception: If there is an error during the database operation.

  """
  try:
    workcell_orm = await db_session.get(WorkcellOrm, workcell_accession_id)
    if workcell_orm and workcell_orm.latest_state_json:
      logger.debug(f"Retrieved workcell state from DB for ID {workcell_accession_id}.")
      return workcell_orm.latest_state_json
    logger.info(f"No state found for workcell ID {workcell_accession_id} in DB.")
    return None
  except Exception as e:
    logger.error(
      f"Failed to retrieve workcell state from DB for ID {workcell_accession_id}: {e}",
      exc_info=True,
    )
    raise


async def update_workcell_state(
  db_session: AsyncSession, workcell_accession_id: uuid.UUID, state_json: Dict[str, Any]
) -> WorkcellOrm:
  """Update the latest_state_json for a specific WorkcellOrm entry.

  Args:
    db_session (AsyncSession): The database session.
    workcell_accession_id (uuid.UUID): The ID of the workcell to update.
    state_json (Dict[str, Any]): The new state JSON to set.

  Returns:
    WorkcellOrm: The updated WorkcellOrm object.

  Raises:
    ValueError: If the workcell with the given ID does not exist.
    Exception: For any other unexpected errors during the update process.

  """
  try:
    workcell_orm = await db_session.get(WorkcellOrm, workcell_accession_id)
    if not workcell_orm:
      raise ValueError(
        f"WorkcellOrm with ID {workcell_accession_id} not found for state update."
      )

    workcell_orm.latest_state_json = state_json
    workcell_orm.last_state_update_time = datetime.datetime.now(datetime.timezone.utc)
    await db_session.merge(workcell_orm)
    await db_session.flush()
    logger.debug(f"Workcell state for ID {workcell_accession_id} updated in DB.")
    return workcell_orm
  except Exception as e:
    logger.error(
      f"Failed to update workcell state in DB for ID {workcell_accession_id}: {e}",
      exc_info=True,
    )
    raise
