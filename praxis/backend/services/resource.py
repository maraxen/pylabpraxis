# pylint: disable=broad-except, too-many-lines
"""Service layer for Resource  Management."""

import uuid
from functools import partial

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.attributes import flag_modified

from praxis.backend.models.resource_orm import ResourceOrm
from praxis.backend.models.resource_pydantic_models import (
  ResourceCreate,
  ResourceUpdate,
)
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

UUID = uuid.UUID

log_resource_data_service_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  exception_type=ValueError,
  raises=True,
  raises_exception=ValueError,
  return_=None,
)


@log_resource_data_service_errors(
  prefix="Resource Data Service: Creating resource - ",
  suffix=(
    " Please ensure the parameters are correct and the resource definition exists."
  ),
)
async def create_resource(
  db: AsyncSession,
  resource_create: ResourceCreate,
) -> ResourceOrm:
  """Create a new resource.

  Args:
      db: The database session.
      resource_create: Pydantic model with resource data.

  Returns:
      The created resource object.

  Raises:
      ValueError: If validation fails.
      Exception: For any other unexpected errors.

  """
  logger.info(
    "Attempting to create resource '%s' for parent ID %s.",
    resource_create.name,  # type: ignore
    resource_create.parent_accession_id,
  )

  resource_data = resource_create.model_dump(exclude={"plr_state"})
  resource_orm = ResourceOrm(**resource_data)

  if resource_create.plr_state:
    resource_orm.plr_state = resource_create.plr_state

  db.add(resource_orm)

  try:
    await db.commit()
    await db.refresh(resource_orm)
    logger.info(
      "Successfully created resource '%s' with ID %s.",
      resource_orm.name,  # type: ignore
      resource_orm.accession_id,
    )
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Resource with name '{resource_create.name}' already exists. Details: {e}"
    )
    logger.exception(error_message)
    raise ValueError(error_message) from e
  except Exception as e:  # Catch all for truly unexpected errors
    logger.exception(
      "Error creating resource '%s'. Rolling back.",
      resource_create.name,
    )
    await db.rollback()
    raise e

  return resource_orm


async def read_resource(
  db: AsyncSession,
  resource_accession_id: UUID,
) -> ResourceOrm | None:
  """Retrieve a specific resource by its ID.

  Args:
      db: The database session.
      resource_accession_id: The ID of the resource to retrieve.

  Returns:
      The resource object if found, otherwise None.

  """
  logger.info("Attempting to retrieve resource with ID: %s.", resource_accession_id)
  stmt = (
    select(ResourceOrm)
    .options(
      selectinload(ResourceOrm.children),
      joinedload(ResourceOrm.parent),
      joinedload(ResourceOrm.resource_definition),
    )
    .filter(ResourceOrm.accession_id == resource_accession_id)
  )
  result = await db.execute(stmt)
  resource = result.scalar_one_or_none()
  if resource:
    logger.info(
      "Successfully retrieved resource ID %s: '%s'.",
      resource_accession_id,  # type: ignore
      resource.name,  # type: ignore
    )
  else:
    logger.info("Resource with ID %s not found.", resource_accession_id)
  return resource


async def read_resources(
  db: AsyncSession,
  parent_accession_id: UUID | None = None,
  limit: int = 100,
  offset: int = 0,
) -> list[ResourceOrm]:
  """List all resources, with optional filtering by parent ID.

  Args:
      db: The database session.
      parent_accession_id: The ID of the parent asset to filter by.
      limit: The maximum number of results to return.
      offset: The number of results to skip.

  Returns:
      A list of resource objects.

  """
  logger.info(
    "Listing resources with parent ID filter: %s, limit: %s, offset: %s.",
    parent_accession_id,
    limit,
    offset,
  )
  stmt = select(ResourceOrm).options(
    joinedload(ResourceOrm.parent),
    selectinload(ResourceOrm.children),
    joinedload(ResourceOrm.resource_definition),
  )
  if parent_accession_id is not None:
    stmt = stmt.filter(ResourceOrm.parent_accession_id == parent_accession_id)
  stmt = stmt.order_by(ResourceOrm.name).limit(limit).offset(offset)
  result = await db.execute(stmt)
  resources = list(result.scalars().all())
  logger.info("Found %s resources.", len(resources))
  return resources


async def read_resource_by_name(db: AsyncSession, name: str) -> ResourceOrm | None:
  """Retrieve a specific resource by its name.

  Args:
      db: The database session.
      name: The name of the resource to retrieve.

  Returns:
      The resource object if found, otherwise None.

  """
  logger.info("Attempting to retrieve resource with name: '%s'.", name)
  stmt = (
    select(ResourceOrm)
    .options(
      selectinload(ResourceOrm.children),
      joinedload(ResourceOrm.parent),
      joinedload(ResourceOrm.resource_definition),
    )
    .filter(ResourceOrm.name == name)
  )
  result = await db.execute(stmt)
  resource = result.scalar_one_or_none()
  if resource:
    logger.info("Successfully retrieved resource by name '%s'.", name)
  else:
    logger.info("Resource with name '%s' not found.", name)  # type: ignore
  return resource


async def update_resource(
  db: AsyncSession,
  resource_accession_id: UUID,
  resource_update: ResourceUpdate,
) -> ResourceOrm | None:
  """Update an existing resource.

  Args:
      db: The database session.
      resource_accession_id: The ID of the resource to update.
      resource_update: Pydantic model with updated data.

  Returns:
      The updated resource object if successful, otherwise None.

  """
  logger.info("Attempting to update resource with ID: %s.", resource_accession_id)
  resource_orm = await read_resource(db, resource_accession_id)
  if not resource_orm:
    logger.warning("Resource with ID %s not found for update.", resource_accession_id)
    return None

  update_data = resource_update.model_dump(exclude_unset=True)
  for key, value in update_data.items():
    if hasattr(resource_orm, key):
      setattr(resource_orm, key, value)

  if "plr_state" in update_data:
    flag_modified(resource_orm, "plr_state")

  try:
    await db.commit()
    await db.refresh(resource_orm)
    logger.info(
      "Successfully updated resource ID %s: '%s'.",
      resource_accession_id,  # type: ignore
      resource_orm.name,  # type: ignore
    )
    return await read_resource(db, resource_accession_id)
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error updating resource ID {resource_accession_id}. Details: {e}"
    )
    logger.exception(error_message)
    raise ValueError(error_message) from e
  except Exception as e:  # Catch all for truly unexpected errors
    await db.rollback()
    logger.exception(
      "Unexpected error updating resource ID %s. Rolling back.",
      resource_accession_id,
    )
    raise e


async def delete_resource(db: AsyncSession, resource_accession_id: UUID) -> bool:
  """Delete a specific resource by its ID.

  Args:
      db: The database session.
      resource_accession_id: The ID of the resource to delete.

  Returns:
      True if the deletion was successful, False if the resource was not found.

  """
  logger.info("Attempting to delete resource with ID: %s.", resource_accession_id)
  resource_orm = await read_resource(db, resource_accession_id)
  if not resource_orm:
    logger.warning("Resource with ID %s not found for deletion.", resource_accession_id)
    return False

  try:
    await db.delete(resource_orm)
    await db.commit()
    logger.info(
      "Successfully deleted resource ID %s: '%s'.",
      resource_accession_id,  # type: ignore
      resource_orm.name,  # type: ignore
    )
    return True
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Integrity error deleting resource ID {resource_accession_id}. "
      f"This might be due to foreign key constraints. Details: {e}"
    )
    logger.exception(error_message)
    raise ValueError(error_message) from e
  except Exception as e:  # Catch all for truly unexpected errors
    await db.rollback()
    logger.exception(
      "Unexpected error deleting resource ID %s. Rolling back.",
      resource_accession_id,
    )
    raise e
