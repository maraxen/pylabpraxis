"""Service layer for Function Data Output management.

This module provides comprehensive CRUD operations and specialized functions for
managing data outputs from protocol function calls, with support for resource
attribution, spatial context, and data visualization.
"""

from functools import partial
from uuid import UUID

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from praxis.backend.models.orm.outputs import (
  DataOutputTypeEnum,
  FunctionDataOutputOrm,
  WellDataOutputOrm,
)
from praxis.backend.models.pydantic.outputs import (
  WellDataOutputCreate,
  WellDataOutputUpdate,
)
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

from .plate_parsing import (
  calculate_well_index,
  parse_well_name,
  read_plate_dimensions,
)

logger = get_logger(__name__)

log_well_data_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  exception_type=ValueError,
  raises=True,
  raises_exception=ValueError,
)


class WellDataOutputCRUDService(
  CRUDBase[WellDataOutputOrm, WellDataOutputCreate, WellDataOutputUpdate],
):
  """CRUD service for well data outputs."""

  async def create(
    self,
    db: AsyncSession,
    *,
    obj_in: WellDataOutputCreate,
  ) -> WellDataOutputOrm:
    """Create a single well data output."""
    log_prefix = (
      f"Well Data (Plate: {obj_in.plate_resource_accession_id}, Well: {obj_in.well_name}):"
    )
    logger.info("%s Creating well data output.", log_prefix)

    # Parse well name to get row/column indices
    try:
      row_idx, col_idx = parse_well_name(obj_in.well_name)
    except ValueError as e:
      error_msg = f"Invalid well name format: {e}"
      logger.error("%s %s", log_prefix, error_msg)
      raise ValueError(error_msg) from e

    # Get plate dimensions for well index calculation
    plate_dimensions = await read_plate_dimensions(
      db,
      obj_in.plate_resource_accession_id,
    )
    num_cols = plate_dimensions["columns"] if plate_dimensions else 12  # Default fallback

    # Create the ORM instance
    well_output = WellDataOutputOrm(
      function_data_output_accession_id=obj_in.function_data_output_accession_id,
      plate_resource_accession_id=obj_in.plate_resource_accession_id,
      well_name=obj_in.well_name,
      well_row=row_idx,
      well_column=col_idx,
      well_index=calculate_well_index(row_idx, col_idx, num_cols),
      data_value=obj_in.data_value,
    )

    db.add(well_output)

    try:
      await db.commit()
      await db.refresh(well_output)
      logger.info(
        "%s Successfully created well data output (ID: %s).",
        log_prefix,
        well_output.accession_id,
      )
      return well_output
    except Exception as e:
      await db.rollback()
      error_msg = f"Failed to create well data output: {e!s}"
      logger.error("%s %s", log_prefix, error_msg)
      raise ValueError(error_msg) from e

  async def get(
    self,
    db: AsyncSession,
    accession_id: UUID,
  ) -> WellDataOutputOrm | None:
    """Read a well data output by ID."""
    log_prefix = f"Well Data (ID: {accession_id}):"
    logger.info("%s Reading well data output.", log_prefix)

    query = (
      select(self.model)
      .options(
        joinedload(self.model.function_data_output),
        joinedload(self.model.plate_resource),
      )
      .filter(self.model.accession_id == accession_id)
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()

  async def get_multi(
    self,
    db: AsyncSession,
    *,
    plate_resource_id: UUID | None = None,
    function_call_id: UUID | None = None,
    protocol_run_id: UUID | None = None,
    data_type: DataOutputTypeEnum | None = None,
    well_row: int | None = None,
    well_column: int | None = None,
    skip: int = 0,
    limit: int = 100,
  ) -> list[WellDataOutputOrm]:
    """List well data outputs with filtering."""
    log_prefix = "Well Data Outputs:"
    logger.info("%s Listing well data outputs with filters.", log_prefix)

    query = select(self.model).options(
      joinedload(self.model.function_data_output),
      joinedload(self.model.plate_resource),
    )

    # Build filters
    conditions = []

    if plate_resource_id:
      conditions.append(
        self.model.plate_resource_accession_id == plate_resource_id,
      )

    if function_call_id or protocol_run_id or data_type:
      query = query.join(self.model.function_data_output)

      if function_call_id:
        conditions.append(
          FunctionDataOutputOrm.function_call_log_accession_id == function_call_id,
        )

      if protocol_run_id:
        conditions.append(
          FunctionDataOutputOrm.protocol_run_accession_id == protocol_run_id,
        )

      if data_type:
        conditions.append(FunctionDataOutputOrm.data_type == data_type)

    if well_row is not None:
      conditions.append(self.model.well_row == well_row)

    if well_column is not None:
      conditions.append(self.model.well_column == well_column)

    if conditions:
      query = query.filter(and_(*conditions))

    # Apply sorting and pagination
    query = (
      query.order_by(
        self.model.plate_resource_accession_id,
        self.model.well_row,
        self.model.well_column,
      )
      .offset(skip)
      .limit(limit)
    )

    result = await db.execute(query)
    well_data_list = list(result.scalars().all())
    logger.info(
      "%s Found %d well data outputs.",
      log_prefix,
      len(well_data_list),
    )
    return well_data_list

  @log_well_data_errors(
    prefix="Data Output Service: Error updating well data output",
    suffix="Please ensure the update parameters are valid.",
  )
  async def update(
    self,
    db: AsyncSession,
    *,
    db_obj: WellDataOutputOrm,
    obj_in: WellDataOutputUpdate,
  ) -> WellDataOutputOrm | None:
    """Update a well data output."""
    log_prefix = f"Well Data (ID: {db_obj.accession_id}):"
    logger.info("%s Updating well data output.", log_prefix)

    # Update only the fields that are provided
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
      if hasattr(db_obj, field):
        setattr(db_obj, field, value)
        logger.debug("%s Updated field '%s' to: %s", log_prefix, field, value)

    try:
      await db.commit()
      await db.refresh(db_obj)
      logger.info("%s Successfully updated well data output.", log_prefix)
      return db_obj
    except Exception as e:
      await db.rollback()
      error_msg = f"Failed to update well data output: {e!s}"
      logger.error("%s %s", log_prefix, error_msg)
      raise ValueError(error_msg) from e

  @log_well_data_errors(
    prefix="Data Output Service: Error deleting well data output",
    suffix="Please ensure the well data output exists and can be deleted.",
  )
  async def remove(self, db: AsyncSession, *, accession_id: UUID) -> bool:
    """Delete a well data output by ID."""
    log_prefix = f"Well Data (ID: {accession_id}):"
    logger.info("%s Deleting well data output.", log_prefix)

    # First check if the record exists
    well_output = await self.get(db, accession_id=accession_id)
    if not well_output:
      logger.warning("%s Well data output not found for deletion.", log_prefix)
      return False

    # Delete the record
    delete_stmt = delete(self.model).where(
      self.model.accession_id == accession_id,
    )
    result = await db.execute(delete_stmt)

    try:
      await db.commit()
      deleted_count = result.rowcount
      logger.info(
        "%s Successfully deleted well data output (affected rows: %d).",
        log_prefix,
        deleted_count,
      )
      return deleted_count > 0
    except Exception as e:
      await db.rollback()
      error_msg = f"Failed to delete well data output: {e!s}"
      logger.error("%s %s", log_prefix, error_msg)
      raise ValueError(error_msg) from e


@log_well_data_errors(
  prefix="Data Output Service: Error creating well data outputs",
  suffix="Please ensure plate and well information is valid.",
)
async def create_well_data_outputs(
  db: AsyncSession,
  function_data_output_accession_id: UUID,
  plate_resource_accession_id: UUID,
  well_data: dict[str, float],
) -> list[WellDataOutputOrm]:
  """Create well-specific data outputs for a plate."""
  log_prefix = f"Well Data Outputs (Plate: {plate_resource_accession_id}):"
  logger.info("%s Creating %d well data outputs.", log_prefix, len(well_data))

  # Get plate dimensions for validation
  plate_dimensions = await read_plate_dimensions(
    db,
    plate_resource_accession_id,
  )

  if not plate_dimensions:
    logger.warning(
      "%s Could not determine plate dimensions, using defaults",
      log_prefix,
    )
    num_cols = 12  # Default fallback
  else:
    num_cols = plate_dimensions["columns"]

  well_outputs = []

  for well_name, value in well_data.items():
    # Parse well name to get row/column indices
    row_idx, col_idx = parse_well_name(well_name)

    well_output = WellDataOutputOrm(
      function_data_output_accession_id=function_data_output_accession_id,
      plate_resource_accession_id=plate_resource_accession_id,
      well_name=well_name,
      well_row=row_idx,
      well_column=col_idx,
      well_index=calculate_well_index(row_idx, col_idx, num_cols),
      data_value=value,
    )

    well_outputs.append(well_output)
    db.add(well_output)

  try:
    await db.commit()

    # Refresh all instances
    for well_output in well_outputs:
      await db.refresh(well_output)

    logger.info(
      "%s Successfully created %d well data outputs.",
      log_prefix,
      len(well_outputs),
    )
    return well_outputs

  except Exception as e:
    await db.rollback()
    logger.exception("%s Error creating well data outputs.", log_prefix)
    raise e


async def create_well_data_outputs_from_flat_array(
  db: AsyncSession,
  function_data_output_accession_id: UUID,
  plate_resource_accession_id: UUID,
  data_array: list[float],
) -> list[WellDataOutputOrm]:
  """Create well-specific data outputs from a flat array of data."""
  log_prefix = f"Well Data Outputs (Plate: {plate_resource_accession_id}):"
  logger.info(
    "%s Creating well data outputs from flat array of %d values.",
    log_prefix,
    len(data_array),
  )

  # Get plate dimensions from resource definition
  plate_dimensions = await read_plate_dimensions(
    db,
    plate_resource_accession_id,
  )

  if not plate_dimensions:
    error_msg = f"Could not determine plate dimensions for resource {plate_resource_accession_id}"
    raise ValueError(error_msg)

  num_rows, num_cols = plate_dimensions["rows"], plate_dimensions["columns"]
  expected_wells = num_rows * num_cols

  if len(data_array) != expected_wells:
    logger.warning(
      "%s Data array length (%d) doesn't match expected wells (%d)",
      log_prefix,
      len(data_array),
      expected_wells,
    )

  well_outputs = []

  for idx, value in enumerate(data_array):
    # Convert flat index to row/column (assuming row-major order)
    row_idx = idx // num_cols
    col_idx = idx % num_cols

    # Generate well name (A1, A2, ..., H12, etc.)
    well_name = f"{chr(ord('A') + row_idx)}{col_idx + 1}"

    well_output = WellDataOutputOrm(
      function_data_output_accession_id=function_data_output_accession_id,
      plate_resource_accession_id=plate_resource_accession_id,
      well_name=well_name,
      well_row=row_idx,
      well_column=col_idx,
      well_index=idx,
      data_value=value,
    )

    well_outputs.append(well_output)
    db.add(well_output)

  try:
    await db.commit()

    # Refresh all instances
    for well_output in well_outputs:
      await db.refresh(well_output)

    logger.info(
      "%s Successfully created %d well data outputs.",
      log_prefix,
      len(well_outputs),
    )
    return well_outputs

  except Exception as e:
    await db.rollback()
    logger.exception("%s Error creating well data outputs.", log_prefix)
    raise e
