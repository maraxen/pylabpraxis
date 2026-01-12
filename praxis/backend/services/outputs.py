"""Service layer for Function Data Output management.

This module provides comprehensive CRUD operations and specialized functions for
managing data outputs from protocol function calls, with support for resource
attribution, spatial context, and data visualization.
"""

import datetime
from functools import partial
from typing import Any
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from praxis.backend.models.domain.outputs import (
  FunctionDataOutput as FunctionDataOutput,
  FunctionDataOutputCreate,
  FunctionDataOutputUpdate,
)
from praxis.backend.models.enums import DataOutputTypeEnum
from praxis.backend.models.domain.filters import SearchFilters
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.services.utils.query_builder import (
  apply_date_range_filters,
  apply_pagination,
  apply_specific_id_filters,
)
from praxis.backend.utils.db_decorator import handle_db_transaction
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

log_data_output_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  exception_type=ValueError,
  raises=True,
  raises_exception=ValueError,
)


class FunctionDataOutputCRUDService(
  CRUDBase[
    FunctionDataOutput,
    FunctionDataOutputCreate,
    FunctionDataOutputUpdate,
  ],
):
  """CRUD service for function data outputs."""

  @handle_db_transaction
  async def create(
    self,
    db: AsyncSession,
    *,
    obj_in: FunctionDataOutputCreate,
  ) -> FunctionDataOutput:
    """Create a new function data output record."""
    data_type_enum = DataOutputTypeEnum(obj_in.data_type)
    log_prefix = f"Data Output (Type: {data_type_enum.value}, Key: '{obj_in.data_key}'):"
    logger.info("%s Creating new function data output.", log_prefix)

    # Create the ORM instance
    dumped_obj = obj_in.model_dump(
      exclude={"measurement_timestamp", "accession_id", "created_at", "updated_at"},
    )
    data_output_model = FunctionDataOutput(
      **dumped_obj,
      measurement_timestamp=obj_in.measurement_timestamp
      or datetime.datetime.now(datetime.timezone.utc),
    )

    db.add(data_output_model)
    await db.flush()
    await db.refresh(data_output_model)
    logger.info(
      "%s Successfully created function data output (ID: %s).",
      log_prefix,
      data_output_model.accession_id,
    )
    return data_output_model

  async def get(
    self,
    db: AsyncSession,
    accession_id: UUID,
  ) -> FunctionDataOutput | None:
    """Read a function data output by ID."""
    result = await db.execute(select(self.model).filter(self.model.accession_id == accession_id))

    return result.scalar_one_or_none()

  async def get_multi(
    self,
    db: AsyncSession,
    *,
    filters: SearchFilters,
  ) -> list[FunctionDataOutput]:
    """List function data outputs with filtering."""
    query = select(self.model).options(
      joinedload(self.model.function_call_log),
      joinedload(self.model.resource),
      joinedload(self.model.machine),
    )

    conditions = []

    if conditions:
      query = query.filter(and_(*conditions))

    query = apply_specific_id_filters(query, filters, self.model)
    query = apply_date_range_filters(
      query,
      filters,
      self.model.measurement_timestamp,
    )
    query = apply_pagination(query, filters)
    query = query.order_by(self.model.measurement_timestamp.desc())

    result = await db.execute(query)
    return list(result.scalars().all())

  @handle_db_transaction
  async def update(
    self,
    db: AsyncSession,
    *,
    db_obj: FunctionDataOutput,
    obj_in: FunctionDataOutputUpdate | dict[str, Any],
  ) -> FunctionDataOutput:
    """Update a function data output record."""
    log_prefix = f"Data Output (ID: {db_obj.accession_id}):"
    logger.info("%s Updating function data output.", log_prefix)

    update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
      if hasattr(db_obj, field):
        setattr(db_obj, field, value)
        logger.debug("%s Updated field '%s' to: %s", log_prefix, field, value)

    await db.flush()
    await db.refresh(db_obj)
    logger.info("%s Successfully updated data output.", log_prefix)
    return db_obj

  @handle_db_transaction
  async def remove(self, db: AsyncSession, *, accession_id: UUID) -> FunctionDataOutput | None:
    """Delete a function data output record by ID."""
    log_prefix = f"Data Output (ID: {accession_id}):"
    logger.info("%s Deleting function data output.", log_prefix)

    data_output_model = await super().remove(db, accession_id=accession_id)
    if not data_output_model:
      logger.warning("%s Data output not found for deletion.", log_prefix)
      return None
    logger.info("%s Successfully deleted data output.", log_prefix)
    return data_output_model
