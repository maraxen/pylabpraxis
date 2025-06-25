"""Service layer for Function Data Output management.

This module provides comprehensive CRUD operations and specialized functions for
managing data outputs from protocol function calls, with support for resource
attribution, spatial context, and data visualization.
"""

import datetime
from functools import partial
from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from praxis.backend.models import (
  DataSearchFilters,
  FunctionDataOutputCreate,
  FunctionDataOutputUpdate,
)
from praxis.backend.models.function_data_output_orm import (
  FunctionDataOutputOrm,
)
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

log_data_output_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  exception_type=ValueError,
  raises=True,
  raises_exception=ValueError,
)


@log_data_output_errors(
  prefix="Data Output Service: Error creating function data output",
  suffix="Please ensure all required parameters are provided and valid.",
)
async def create_function_data_output(
  db: AsyncSession, data_output: FunctionDataOutputCreate
) -> FunctionDataOutputOrm:
  """Create a new function data output record.

  Args:
    db: Database session
    data_output: Data output creation model

  Returns:
    Created function data output ORM instance

  Raises:
    ValueError: If validation fails or required data is missing

  """
  log_prefix = (
    f"Data Output (Type: {data_output.data_type.value}, Key: '{data_output.data_key}'):"
  )
  logger.info("%s Creating new function data output.", log_prefix)

  # Create the ORM instance
  data_output_orm = FunctionDataOutputOrm(
    function_call_log_accession_id=data_output.function_call_log_accession_id,
    protocol_run_accession_id=data_output.protocol_run_accession_id,
    data_type=data_output.data_type,
    data_key=data_output.data_key,
    spatial_context=data_output.spatial_context,
    resource_instance_accession_id=data_output.resource_instance_accession_id,
    machine_accession_id=data_output.machine_accession_id,
    deck_instance_accession_id=data_output.deck_instance_accession_id,
    spatial_coordinates_json=data_output.spatial_coordinates_json,
    data_value_numeric=data_output.data_value_numeric,
    data_value_json=data_output.data_value_json,
    data_value_text=data_output.data_value_text,
    file_path=data_output.file_path,
    file_size_bytes=data_output.file_size_bytes,
    data_units=data_output.data_units,
    data_quality_score=data_output.data_quality_score,
    measurement_conditions_json=data_output.measurement_conditions_json,
    measurement_timestamp=data_output.measurement_timestamp
    or datetime.datetime.utcnow(),
    sequence_in_function=data_output.sequence_in_function,
    derived_from_data_output_accession_id=data_output.derived_from_data_output_accession_id,
    processing_metadata_json=data_output.processing_metadata_json,
  )

  db.add(data_output_orm)

  try:
    await db.commit()
    await db.refresh(data_output_orm)
    logger.info(
      "%s Successfully created function data output (ID: %s).",
      log_prefix,
      data_output_orm.accession_id,
    )
    return data_output_orm

  except IntegrityError as e:
    await db.rollback()
    error_message = f"{log_prefix} Database integrity error: {e}"
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error during creation.", log_prefix)
    raise e


async def read_function_data_output(
  db: AsyncSession, data_output_accession_id: UUID
) -> Optional[FunctionDataOutputOrm]:
  """Read a function data output by ID.

  Args:
    db: Database session
    data_output_accession_id: Data output ID

  Returns:
    Function data output ORM instance or None if not found

  """
  result = await db.execute(
    select(FunctionDataOutputOrm)
    .options(
      joinedload(FunctionDataOutputOrm.function_call_log),
      joinedload(FunctionDataOutputOrm.protocol_run),
      joinedload(FunctionDataOutputOrm.resource_instance),
      joinedload(FunctionDataOutputOrm.machine),
      joinedload(FunctionDataOutputOrm.deck_instance),
      selectinload(FunctionDataOutputOrm.well_data_outputs),
    )
    .filter(FunctionDataOutputOrm.accession_id == data_output_accession_id)
  )

  return result.scalar_one_or_none()


async def list_function_data_outputs(
  db: AsyncSession, filters: DataSearchFilters, limit: int = 100, offset: int = 0
) -> List[FunctionDataOutputOrm]:
  """List function data outputs with filtering.

  Args:
    db: Database session
    filters: Search and filter criteria
    limit: Maximum number of results
    offset: Number of results to skip

  Returns:
    List of function data output ORM instances

  """
  query = select(FunctionDataOutputOrm).options(
    joinedload(FunctionDataOutputOrm.function_call_log),
    joinedload(FunctionDataOutputOrm.resource_instance),
    joinedload(FunctionDataOutputOrm.machine),
  )

  # Apply filters
  conditions = []

  if filters.protocol_run_accession_id:
    conditions.append(
      FunctionDataOutputOrm.protocol_run_accession_id
      == filters.protocol_run_accession_id
    )

  if filters.function_call_log_accession_id:
    conditions.append(
      FunctionDataOutputOrm.function_call_log_accession_id
      == filters.function_call_log_accession_id
    )

  if filters.data_types:
    conditions.append(FunctionDataOutputOrm.data_type.in_(filters.data_types))

  if filters.spatial_contexts:
    conditions.append(
      FunctionDataOutputOrm.spatial_context.in_(filters.spatial_contexts)
    )

  if filters.machine_accession_id:
    conditions.append(
      FunctionDataOutputOrm.machine_accession_id == filters.machine_accession_id
    )

  if filters.resource_instance_accession_id:
    conditions.append(
      FunctionDataOutputOrm.resource_instance_accession_id
      == filters.resource_instance_accession_id
    )

  if filters.date_range_start:
    conditions.append(
      FunctionDataOutputOrm.measurement_timestamp >= filters.date_range_start
    )

  if filters.date_range_end:
    conditions.append(
      FunctionDataOutputOrm.measurement_timestamp <= filters.date_range_end
    )

  if filters.has_numeric_data is not None:
    if filters.has_numeric_data:
      conditions.append(FunctionDataOutputOrm.data_value_numeric.is_not(None))
    else:
      conditions.append(FunctionDataOutputOrm.data_value_numeric.is_(None))

  if filters.has_file_data is not None:
    if filters.has_file_data:
      conditions.append(FunctionDataOutputOrm.file_path.is_not(None))
    else:
      conditions.append(FunctionDataOutputOrm.file_path.is_(None))

  if filters.min_quality_score is not None:
    conditions.append(
      FunctionDataOutputOrm.data_quality_score >= filters.min_quality_score
    )

  if conditions:
    query = query.filter(and_(*conditions))

  query = (
    query.order_by(FunctionDataOutputOrm.measurement_timestamp.desc())
    .limit(limit)
    .offset(offset)
  )

  result = await db.execute(query)
  return list(result.scalars().all())


@log_data_output_errors(
  prefix="Data Output Service: Error updating function data output",
  suffix="Please ensure the update parameters are valid.",
)
async def update_function_data_output(
  db: AsyncSession,
  data_output_accession_id: UUID,
  data_output_update: FunctionDataOutputUpdate,
) -> Optional[FunctionDataOutputOrm]:
  """Update a function data output record.

  Args:
    db: Database session
    data_output_accession_id: ID of the data output to update
    data_output_update: Update model containing fields to update

  Returns:
    Updated function data output ORM instance or None if not found

  Raises:
    ValueError: If validation fails or required data is missing

  """
  log_prefix = f"Data Output (ID: {data_output_accession_id}):"
  logger.info("%s Updating function data output.", log_prefix)

  # Get the existing record
  data_output_orm = await read_function_data_output(db, data_output_accession_id)
  if not data_output_orm:
    logger.warning("%s Data output not found.", log_prefix)
    return None

  # Update only the fields that are provided
  update_data = data_output_update.model_dump(exclude_unset=True)
  for field, value in update_data.items():
    if hasattr(data_output_orm, field):
      setattr(data_output_orm, field, value)
      logger.debug("%s Updated field '%s' to: %s", log_prefix, field, value)

  try:
    await db.commit()
    await db.refresh(data_output_orm)
    logger.info("%s Successfully updated data output.", log_prefix)
    return data_output_orm
  except Exception as e:
    await db.rollback()
    error_msg = f"Failed to update data output: {str(e)}"
    logger.error("%s %s", log_prefix, error_msg)
    raise ValueError(error_msg) from e


@log_data_output_errors(
  prefix="Data Output Service: Error deleting function data output",
  suffix="Please ensure the ID is valid and the record exists.",
)
async def delete_function_data_output(
  db: AsyncSession, data_output_accession_id: UUID
) -> bool:
  """Delete a function data output record by ID.

  Args:
    db: Database session
    data_output_accession_id: ID of the data output to delete

  Returns:
    True if deletion was successful, False if not found

  Raises:
    ValueError: If an error occurs during deletion

  """
  log_prefix = f"Data Output (ID: {data_output_accession_id}):"
  logger.info("%s Deleting function data output.", log_prefix)

  # Attempt to delete the record
  try:
    result = await db.execute(
      delete(FunctionDataOutputOrm).where(
        FunctionDataOutputOrm.accession_id == data_output_accession_id
      )
    )
    await db.commit()

    if result.rowcount == 0:
      logger.warning("%s Data output not found for deletion.", log_prefix)
      return False

    logger.info("%s Successfully deleted data output.", log_prefix)
    return True

  except Exception as e:
    await db.rollback()
    error_msg = f"Failed to delete data output: {str(e)}"
    logger.error("%s %s", log_prefix, error_msg)
    raise ValueError(error_msg) from e
