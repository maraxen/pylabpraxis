# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument
"""Service layer for Workcell Data Management.

praxis/db_services/workcell_data_service.py

Service layer for interacting with workcell-related data in the database.
This includes Workcell configurations and their associated machines.

This module provides functions to create, read, update, and delete workcell entries.
"""

import logging
from typing import List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from praxis.backend.models import MachineOrm, WorkcellOrm

logger = logging.getLogger(__name__)


async def create_workcell(
  db: AsyncSession,
  name: str,
  description: Optional[str] = None,
  physical_location: Optional[str] = None,
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
    name=name, description=description, physical_location=physical_location
  )
  db.add(workcell_orm)

  try:
    await db.commit()
    await db.refresh(workcell_orm)
    logger.info("Successfully created workcell '%s' with ID %d.", name, workcell_orm.id)
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


async def get_workcell_by_id(
  db: AsyncSession, workcell_id: int
) -> Optional[WorkcellOrm]:
  """Retrieve a specific workcell by its ID.

  Args:
    db (AsyncSession): The database session.
    workcell_id (int): The ID of the workcell to retrieve.

  Returns:
    Optional[WorkcellOrm]: The workcell object if found, otherwise None.
  """
  logger.info("Attempting to retrieve workcell with ID: %d.", workcell_id)
  stmt = (
    select(WorkcellOrm)
    .options(selectinload(WorkcellOrm.machines))
    .filter(WorkcellOrm.id == workcell_id)
  )
  result = await db.execute(stmt)
  workcell = result.scalar_one_or_none()
  if workcell:
    logger.info(
      "Successfully retrieved workcell ID %d: '%s'.", workcell_id, workcell.name
    )
  else:
    logger.info("Workcell with ID %d not found.", workcell_id)
  return workcell


async def get_workcell_by_name(db: AsyncSession, name: str) -> Optional[WorkcellOrm]:
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
  workcell_id: int,
  name: Optional[str] = None,
  description: Optional[str] = None,
  physical_location: Optional[str] = None,
) -> Optional[WorkcellOrm]:
  """Update an existing workcell.

  Args:
    db (AsyncSession): The database session.
    workcell_id (int): The ID of the workcell to update.
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
  logger.info("Attempting to update workcell with ID: %d.", workcell_id)
  workcell_orm = await get_workcell_by_id(db, workcell_id)
  if not workcell_orm:
    logger.warning("Workcell with ID %d not found for update.", workcell_id)
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
      "No changes detected for workcell ID %d. No update performed.", workcell_id
    )
    return workcell_orm

  try:
    await db.commit()
    await db.refresh(workcell_orm)
    logger.info(
      "Successfully updated workcell ID %d: '%s'.", workcell_id, workcell_orm.name
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
      "Unexpected error updating workcell '%s' (ID: %d). Rolling back.",
      original_name,
      workcell_id,
    )
    raise e


async def delete_workcell(db: AsyncSession, workcell_id: int) -> bool:
  """Delete a specific workcell by its ID.

  This function deletes a workcell. Note that if there are machines
  linked to this workcell, the foreign key constraint might prevent deletion
  or require handling (e.g., setting `workcell_id` to NULL in `MachineOrm`).

  Args:
    db (AsyncSession): The database session.
    workcell_id (int): The ID of the workcell to delete.

  Returns:
    bool: True if the deletion was successful, False if the workcell was not found.

  Raises:
    Exception: For any unexpected errors during deletion.

  """
  logger.info("Attempting to delete workcell with ID: %s.", workcell_id)
  workcell_orm = await get_workcell_by_id(db, workcell_id)
  if not workcell_orm:
    logger.warning("Workcell with ID %s not found for deletion.", workcell_id)
    return False

  try:
    await db.delete(workcell_orm)
    await db.commit()
    logger.info(
      "Successfully deleted workcell ID %s: '%s'.", workcell_id, workcell_orm.name
    )
    return True
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error deleting workcell ID {workcell_id}. This might be due to"
      f" foreign key constraints, e.g., associated machines. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    return False
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error deleting workcell ID %s. Rolling back.", workcell_id
    )
    raise e
