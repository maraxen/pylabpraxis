# pylint: disable=broad-except, too-many-lines
"""Service layer for Resource  Management."""

import uuid
from functools import partial
from typing import Any, cast

from sqlalchemy import Column, and_, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.attributes import flag_modified

from praxis.backend.models.orm.resource import ResourceOrm
from praxis.backend.models.pydantic.filters import SearchFilters
from praxis.backend.models.pydantic.resource import (
  ResourceCreate,
  ResourceUpdate,
)
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.services.utils.query_builder import (
  apply_date_range_filters,
  apply_pagination,
  apply_property_filters,
  apply_specific_id_filters,
)
from praxis.backend.utils.db import Base
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


class ResourceService(CRUDBase[ResourceOrm, ResourceCreate, ResourceUpdate]):
  @log_resource_data_service_errors(
    prefix="Resource Data Service: Creating resource - ",
    suffix=(" Please ensure the parameters are correct and the resource definition exists."),
  )
  async def create(
    self,
    db: AsyncSession,
    *,
    obj_in: ResourceCreate,
  ) -> ResourceOrm:
    """Create a new resource."""
    logger.info(
      "Attempting to create resource '%s' for parent ID %s.",
      obj_in.name,
      obj_in.parent_accession_id,
    )

    resource_orm = await super().create(db=db, obj_in=obj_in)

    if obj_in.plr_state:
      resource_orm.plr_state = obj_in.plr_state
      flag_modified(resource_orm, "plr_state")

    try:
      await db.commit()
      await db.refresh(resource_orm)
      logger.info(
        "Successfully created resource '%s' with ID %s.",
        resource_orm.name,
        resource_orm.accession_id,
      )
    except IntegrityError as e:
      await db.rollback()
      error_message = f"Resource with name '{obj_in.name}' already exists. Details: {e}"
      logger.exception(error_message)
      raise ValueError(error_message) from e
    except Exception as e:  # Catch all for truly unexpected errors
      logger.exception(
        "Error creating resource '%s'. Rolling back.",
        obj_in.name,
      )
      await db.rollback()
      raise e

    return resource_orm

  async def get(
    self,
    db: AsyncSession,
    accession_id: UUID,
  ) -> ResourceOrm | None:
    """Retrieve a specific resource by its ID."""
    logger.info("Attempting to retrieve resource with ID: %s.", accession_id)
    stmt = (
      select(self.model)
      .options(
        selectinload(self.model.children),
        joinedload(self.model.parent),
        joinedload(self.model.resource_definition),
      )
      .filter(self.model.accession_id == accession_id)
    )
    result = await db.execute(stmt)
    resource = result.scalar_one_or_none()
    if resource:
      logger.info(
        "Successfully retrieved resource ID %s: '%s'.",
        accession_id,
        resource.name,
      )
    else:
      logger.info("Resource with ID %s not found.", accession_id)
    return resource

  async def get_multi(
    self,
    db: AsyncSession,
    *,
    filters: SearchFilters,
    fqn: str | None = None,  # Specific filter
    status: str | None = None,  # Specific filter
  ) -> list[ResourceOrm]:
    """List all resources, with optional filtering by parent ID."""
    logger.info(
      "Listing resources with filters: %s",
      filters.model_dump_json(),
    )
    stmt = select(self.model).options(
      joinedload(self.model.parent),
      selectinload(self.model.children),
      joinedload(self.model.resource_definition),
    )

    conditions = []

    if filters.parent_accession_id is not None:
      conditions.append(self.model.parent_accession_id == filters.parent_accession_id)

    if fqn:
      conditions.append(self.model.fqn == fqn)

    if status:
      conditions.append(self.model.status == status)

    if conditions:
      stmt = stmt.filter(and_(*conditions))

    # Apply generic filters from query_builder
    stmt = apply_specific_id_filters(stmt, filters, cast("Base", self.model))
    stmt = apply_date_range_filters(stmt, filters, cast("Column", self.model.created_at))
    stmt = apply_property_filters(
      stmt,
      filters,
      cast("Column[JSONB]", self.model.properties_json),
    )

    stmt = apply_pagination(stmt, filters)

    stmt = stmt.order_by(self.model.name)
    result = await db.execute(stmt)
    resources = list(result.scalars().all())
    logger.info("Found %s resources.", len(resources))
    return resources

  async def update(
    self,
    db: AsyncSession,
    *,
    db_obj: ResourceOrm,
    obj_in: ResourceUpdate | dict[str, Any],
  ) -> ResourceOrm:
    """Update an existing resource."""
    logger.info("Attempting to update resource with ID: %s.", db_obj.accession_id)

    updated_resource = await super().update(db=db, db_obj=db_obj, obj_in=obj_in)

    if "plr_state" in (
      obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
    ):
      flag_modified(updated_resource, "plr_state")

    try:
      await db.commit()
      await db.refresh(updated_resource)
      logger.info(
        "Successfully updated resource ID %s: '%s'.",
        updated_resource.accession_id,
        updated_resource.name,
      )
    except IntegrityError as e:
      await db.rollback()
      error_message = f"Integrity error updating resource ID {db_obj.accession_id}. Details: {e}"
      logger.exception(error_message)
      raise ValueError(error_message) from e
    except Exception as e:  # Catch all for truly unexpected errors
      await db.rollback()
      logger.exception(
        "Unexpected error updating resource ID %s. Rolling back.",
        db_obj.accession_id,
      )
      raise e

    return updated_resource

  async def remove(self, db: AsyncSession, *, accession_id: UUID) -> ResourceOrm | None:
    """Delete a specific resource by its ID."""
    logger.info("Attempting to delete resource with ID: %s.", accession_id)
    resource_orm = await super().remove(db, accession_id=accession_id)
    if not resource_orm:
      logger.warning("Resource with ID %s not found for deletion.", accession_id)
      return None

    try:
      await db.commit()
      logger.info(
        "Successfully deleted resource ID %s: '%s'.",
        accession_id,
        resource_orm.name,
      )
      return resource_orm
    except IntegrityError as e:
      await db.rollback()
      error_message = (
        f"Integrity error deleting resource ID {accession_id}. "
        f"This might be due to foreign key constraints. Details: {e}"
      )
      logger.exception(error_message)
      raise ValueError(error_message) from e
    except Exception as e:  # Catch all for truly unexpected errors
      await db.rollback()
      logger.exception(
        "Unexpected error deleting resource ID %s. Rolling back.",
        accession_id,
      )
      raise e


resource_service = ResourceService(ResourceOrm)
