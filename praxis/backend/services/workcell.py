# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument
"""Service layer for Workcell Data Management.

praxis/db_services/workcell_data_service.py

Service layer for interacting with workcell-related data in the database.
This includes Workcell configurations and their associated machines.

This module provides functions to create, read, update, and delete workcell entries.
"""

import datetime
import logging
import uuid
from typing import Any, cast

from sqlalchemy import Column, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from praxis.backend.models.orm.workcell import WorkcellOrm
from praxis.backend.models.pydantic.filters import SearchFilters
from praxis.backend.models.pydantic.workcell import WorkcellCreate, WorkcellUpdate
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.services.utils.query_builder import (
  apply_date_range_filters,
  apply_pagination,
)

logger = logging.getLogger(__name__)


class WorkcellService(CRUDBase[WorkcellOrm, WorkcellCreate, WorkcellUpdate]):
  """Service for workcell-related operations."""

  async def create(self, db: AsyncSession, *, obj_in: WorkcellCreate) -> WorkcellOrm:
    """Create a new workcell."""
    logger.info("Attempting to create workcell '%s'.", obj_in.name)

    workcell_orm = await super().create(db=db, obj_in=obj_in)

    try:
      await db.commit()
      await db.refresh(workcell_orm)
      logger.info(
        "Successfully created workcell '%s' with ID %s.",
        obj_in.name,
        workcell_orm.accession_id,
      )
      return workcell_orm
    except IntegrityError as e:
      await db.rollback()
      error_message = f"Workcell with name '{obj_in.name}' already exists. Details: {e}"
      logger.error(error_message, exc_info=True)
      raise ValueError(error_message) from e
    except Exception as e:
      logger.exception("Error creating workcell '%s'. Rolling back.", obj_in.name)
      await db.rollback()
      raise e

  async def get(self, db: AsyncSession, accession_id: uuid.UUID) -> WorkcellOrm | None:
    """Retrieve a specific workcell by its ID."""
    logger.info("Attempting to retrieve workcell with ID: %s.", accession_id)
    stmt = (
      select(self.model)
      .options(selectinload(self.model.machines))
      .filter(self.model.accession_id == accession_id)
    )
    result = await db.execute(stmt)
    workcell = result.scalar_one_or_none()
    if workcell:
      logger.info(
        "Successfully retrieved workcell ID %s: '%s'.",
        accession_id,
        workcell.name,
      )
    else:
      logger.info("Workcell with ID %s not found.", accession_id)
    return workcell

  async def get_multi(
    self,
    db: AsyncSession,
    *,
    filters: SearchFilters,
  ) -> list[WorkcellOrm]:
    """List all workcells with pagination."""
    logger.info("Listing workcells with filters: %s", filters.model_dump_json())
    stmt = select(self.model).options(selectinload(self.model.machines)).order_by(self.model.name)
    stmt = apply_date_range_filters(stmt, filters, cast("Column", self.model.created_at))
    stmt = apply_pagination(stmt, filters)
    stmt = stmt.order_by(self.model.name)
    result = await db.execute(stmt)
    workcells = list(result.scalars().all())
    logger.info("Found %d workcells.", len(workcells))
    return workcells

  async def update(
    self,
    db: AsyncSession,
    *,
    db_obj: WorkcellOrm,
    obj_in: WorkcellUpdate | dict[str, Any],
  ) -> WorkcellOrm:
    """Update an existing workcell."""
    logger.info("Attempting to update workcell with ID: %s.", db_obj.accession_id)

    # Ensure obj_in is a WorkcellUpdate Pydantic model
    if isinstance(obj_in, dict):
      update_data = obj_in
      obj_in_model = WorkcellUpdate(**obj_in)
    else:
      update_data = obj_in.model_dump(exclude_unset=True)
      obj_in_model = obj_in

    name = update_data.get("name", db_obj.name)  # Safely get name for logging

    updated_workcell = await super().update(db=db, db_obj=db_obj, obj_in=obj_in_model)

    try:
      await db.commit()
      await db.refresh(updated_workcell)
      logger.info(
        "Successfully updated workcell ID %s: '%s'.",
        updated_workcell.accession_id,
        updated_workcell.name,
      )
      return updated_workcell
    except IntegrityError as e:
      await db.rollback()
      error_message = f"Workcell with name '{name}' already exists. Details: {e}"
      logger.error(error_message, exc_info=True)
      raise ValueError(error_message) from e
    except Exception as e:
      await db.rollback()
      logger.exception(
        "Unexpected error updating workcell '%s' (ID: %s). Rolling back.",
        db_obj.name,
        db_obj.accession_id,
      )
      raise e

  async def remove(self, db: AsyncSession, *, accession_id: uuid.UUID) -> WorkcellOrm | None:
    """Delete a specific workcell by its ID."""
    logger.info("Attempting to delete workcell with ID: %s.", accession_id)
    workcell_orm = await super().remove(db, accession_id=accession_id)
    if not workcell_orm:
      logger.warning("Workcell with ID %s not found for deletion.", accession_id)
      return None

    try:
      await db.commit()
      logger.info(
        "Successfully deleted workcell ID %s: '%s'.",
        accession_id,
        workcell_orm.name,
      )
      return workcell_orm
    except IntegrityError as e:
      await db.rollback()
      error_message = (
        f"Integrity error deleting workcell ID {accession_id}. This might be due to"
        f" foreign key constraints, e.g., associated machines. Details: {e}"
      )
      logger.error(error_message, exc_info=True)
      return None
    except Exception as e:
      await db.rollback()
      logger.exception(
        "Unexpected error deleting workcell ID %s. Rolling back.",
        accession_id,
      )
      raise e

  async def read_workcell_state(
    self,
    db_session: AsyncSession,
    workcell_accession_id: uuid.UUID,
  ) -> dict[str, Any] | None:
    """Retrieve the latest JSON-serialized state of a workcell from the database."""
    try:
      workcell_orm = await db_session.get(self.model, workcell_accession_id)
      if workcell_orm and workcell_orm.latest_state_json:
        logger.debug(
          f"Retrieved workcell state from DB for ID {workcell_accession_id}.",
        )
        return workcell_orm.latest_state_json
      logger.info(
        f"No state found for workcell ID {workcell_accession_id} in DB.",
      )
      return None
    except Exception as e:
      logger.error(
        f"Failed to retrieve workcell state from DB for ID {workcell_accession_id}: {e}",
        exc_info=True,
      )
      raise

  async def update_workcell_state(
    self,
    db_session: AsyncSession,
    workcell_accession_id: uuid.UUID,
    state_json: dict[str, Any],
  ) -> WorkcellOrm:
    """Update the latest_state_json for a specific WorkcellOrm entry."""
    try:
      workcell_orm = await db_session.get(self.model, workcell_accession_id)
      if not workcell_orm:
        raise ValueError(
          f"WorkcellOrm with ID {workcell_accession_id} not found for state update.",
        )

      workcell_orm.latest_state_json = state_json
      workcell_orm.last_state_update_time = datetime.datetime.now(
        datetime.timezone.utc,
      )
      await db_session.merge(workcell_orm)
      await db_session.flush()
      logger.debug(
        f"Workcell state for ID {workcell_accession_id} updated in DB.",
      )
      return workcell_orm
    except Exception as e:
      logger.error(
        f"Failed to update workcell state in DB for ID {workcell_accession_id}: {e}",
        exc_info=True,
      )
      raise


workcell_service = WorkcellService(WorkcellOrm)
