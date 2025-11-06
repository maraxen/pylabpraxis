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
from sqlalchemy.orm import joinedload, selectinload

from praxis.backend.models.orm.outputs import FunctionDataOutputOrm
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.models.pydantic_internals.outputs import (
  FunctionDataOutputCreate,
  FunctionDataOutputUpdate,
)
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
    FunctionDataOutputOrm,
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
  ) -> FunctionDataOutputOrm:
    """Create a new function data output record."""
    from praxis.backend.models.enums.outputs import DataOutputTypeEnum
    data_type_enum = DataOutputTypeEnum(obj_in.data_type)
    log_prefix = f"Data Output (Type: {data_type_enum.value}, Key: '{obj_in.data_key}'):"
    logger.info("%s Creating new function data output.", log_prefix)

    # Create the ORM instance
    dumped_obj = obj_in.model_dump(exclude={"measurement_timestamp", "accession_id", "created_at", "updated_at"})
    data_output_orm = FunctionDataOutputOrm(
      **dumped_obj,
      measurement_timestamp=obj_in.measurement_timestamp
      or datetime.datetime.now(datetime.timezone.utc),
    )

    db.add(data_output_orm)
    await db.flush()
    await db.refresh(data_output_orm)
    logger.info(
      "%s Successfully created function data output (ID: %s).",
      log_prefix,
      data_output_orm.accession_id,
    )
    return data_output_orm

  async def get(
    self,
    db: AsyncSession,
    accession_id: UUID,
  ) -> FunctionDataOutputOrm | None:
    """Read a function data output by ID."""
    result = await db.execute(
        select(self.model).filter(self.model.accession_id == accession_id)
    )

    return result.scalar_one_or_none()

  async def get_multi(
    self,
    db: AsyncSession,
    *,
    filters: SearchFilters,
  ) -> list[FunctionDataOutputOrm]:
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
    db_obj: FunctionDataOutputOrm,
    obj_in: FunctionDataOutputUpdate | dict[str, Any],
  ) -> FunctionDataOutputOrm:
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
  async def remove(self, db: AsyncSession, *, accession_id: UUID) -> FunctionDataOutputOrm | None:
    """Delete a function data output record by ID."""
    log_prefix = f"Data Output (ID: {accession_id}):"
    logger.info("%s Deleting function data output.", log_prefix)

    data_output_orm = await super().remove(db, accession_id=accession_id)
    if not data_output_orm:
      logger.warning("%s Data output not found for deletion.", log_prefix)
      return None
    logger.info("%s Successfully deleted data output.", log_prefix)
    return data_output_orm
