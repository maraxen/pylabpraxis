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
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from praxis.backend.models.orm.machine import MachineOrm
from sqlalchemy.orm import selectinload

from praxis.backend.models.orm.workcell import WorkcellOrm
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.models.pydantic_internals.workcell import WorkcellCreate, WorkcellUpdate
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.services.utils.query_builder import (
  apply_date_range_filters,
  apply_pagination,
)
from praxis.backend.utils.db_decorator import handle_db_transaction

logger = logging.getLogger(__name__)


class WorkcellService(CRUDBase[WorkcellOrm, WorkcellCreate, WorkcellUpdate]):

  """Service for workcell-related operations."""

  @handle_db_transaction
  async def create(self, db: AsyncSession, *, obj_in: WorkcellCreate) -> WorkcellOrm:
    """Create a new workcell."""
    logger.info("Attempting to create workcell '%s'.", obj_in.name)

    result = await db.execute(select(self.model).filter(self.model.name == obj_in.name))
    if result.scalar_one_or_none():
        raise IntegrityError(f"Workcell with name '{obj_in.name}' already exists.", params=None, orig=None)

    workcell_orm = await super().create(db=db, obj_in=obj_in)

    await db.flush()
    await db.refresh(workcell_orm)
    logger.info(
      "Successfully created workcell '%s' with ID %s.",
      obj_in.name,
      workcell_orm.accession_id,
    )
    return workcell_orm

  async def get(self, db: AsyncSession, accession_id: uuid.UUID) -> WorkcellOrm | None:
    """Retrieve a specific workcell by its ID."""
    logger.info("Attempting to retrieve workcell with ID: %s.", accession_id)
    stmt = (
      select(self.model)
      .options(
        selectinload(self.model.machines),
        selectinload(self.model.resources),
        selectinload(self.model.decks)
      )
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
    stmt = (
      select(self.model)
      .options(
        selectinload(self.model.machines),
        selectinload(self.model.resources),
        selectinload(self.model.decks)
      )
      .order_by(self.model.name)
    )
    stmt = apply_date_range_filters(stmt, filters, self.model.created_at)
    stmt = apply_pagination(stmt, filters)
    stmt = stmt.order_by(self.model.name)
    result = await db.execute(stmt)
    workcells = list(result.scalars().all())
    logger.info("Found %d workcells.", len(workcells))
    return workcells

  @handle_db_transaction
  async def update(
    self,
    db: AsyncSession,
    *,
    db_obj: WorkcellOrm,
    obj_in: WorkcellUpdate | dict[str, Any],
  ) -> WorkcellOrm:
    """Update an existing workcell."""
    logger.info("Attempting to update workcell with ID: %s.", db_obj.accession_id)

    obj_in_model = WorkcellUpdate(**obj_in) if isinstance(obj_in, dict) else obj_in

    updated_workcell = await super().update(db=db, db_obj=db_obj, obj_in=obj_in_model)

    await db.flush()
    await db.refresh(updated_workcell)
    logger.info(
      "Successfully updated workcell ID %s: '%s'.",
      updated_workcell.accession_id,
      updated_workcell.name,
    )
    return updated_workcell

  @handle_db_transaction
  async def remove(self, db: AsyncSession, *, accession_id: uuid.UUID) -> WorkcellOrm | None:
    """Delete a specific workcell by its ID."""
    logger.info("Attempting to delete workcell with ID: %s.", accession_id)
    workcell_orm = await super().remove(db, accession_id=accession_id)
    if not workcell_orm:
      logger.warning("Workcell with ID %s not found for deletion.", accession_id)
      return None

    machines = await db.execute(
        select(MachineOrm).filter(MachineOrm.workcell_accession_id == accession_id)
    )
    if machines.scalars().first():
        raise ValueError(f"Cannot delete workcell {accession_id}: it has associated machines")

    await db.delete(workcell_orm)
    await db.flush()
    return workcell_orm

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
          "Retrieved workcell state from DB for ID %s.",
          workcell_accession_id,
        )
        return workcell_orm.latest_state_json
      logger.info(
        "No state found for workcell ID %s in DB.",
        workcell_accession_id,
      )
    except Exception:
      logger.exception(
        "Failed to retrieve workcell state from DB for ID %s.",
        workcell_accession_id,
      )
      raise
    else:
      return None

  @handle_db_transaction
  async def update_workcell_state(
    self,
    db_session: AsyncSession,
    workcell_accession_id: uuid.UUID,
    state_json: dict[str, Any],
  ) -> WorkcellOrm:
    """Update the latest_state_json for a specific WorkcellOrm entry."""
    workcell_orm = await db_session.get(self.model, workcell_accession_id)
    if not workcell_orm:
      msg = f"WorkcellOrm with ID {workcell_accession_id} not found for state update."
      raise ValueError(
        msg,
      )

    workcell_orm.latest_state_json = state_json
    workcell_orm.last_state_update_time = datetime.datetime.now(
      datetime.timezone.utc,
    )
    await db_session.merge(workcell_orm)
    await db_session.flush()
    logger.debug(
      "Workcell state for ID %s updated in DB.",
      workcell_accession_id,
    )
    return workcell_orm


workcell_service = WorkcellService(WorkcellOrm)
