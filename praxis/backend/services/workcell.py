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
from sqlalchemy.orm import selectinload

from praxis.backend.models import WorkcellCreate, WorkcellOrm, WorkcellUpdate
from praxis.backend.models.filters import SearchFilters
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.services.utils.query_builder import (
  apply_date_range_filters,
  apply_pagination,
)
from praxis.backend.utils.uuid import uuid7

logger = logging.getLogger(__name__)


class WorkcellService(CRUDBase[WorkcellOrm, WorkcellCreate, WorkcellUpdate]):
    """Service for workcell-related operations.
    """

    async def create(self, db: AsyncSession, *, obj_in: WorkcellCreate) -> WorkcellOrm:
        """Create a new workcell."""
        logger.info("Attempting to create workcell '%s'.", obj_in.name)

        workcell_orm = self.model(
            id=uuid7(),
            name=obj_in.name,
            description=obj_in.description,
            physical_location=obj_in.physical_location,
            latest_state_json=obj_in.initial_state,
            last_state_update_time=datetime.datetime.now(datetime.timezone.utc),
        )
        db.add(workcell_orm)

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
            error_message = (
                f"Workcell with name '{obj_in.name}' already exists. Details: {e}"
            )
            logger.error(error_message, exc_info=True)
            raise ValueError(error_message) from e
        except Exception as e:
            logger.exception("Error creating workcell '%s'. Rolling back.", obj_in.name)
            await db.rollback()
            raise e

    async def get(self, db: AsyncSession, id: uuid.UUID) -> WorkcellOrm | None:
        """Retrieve a specific workcell by its ID."""
        logger.info("Attempting to retrieve workcell with ID: %s.", id)
        stmt = (
            select(self.model)
            .options(selectinload(self.model.machines))
            .filter(self.model.accession_id == id)
        )
        result = await db.execute(stmt)
        workcell = result.scalar_one_or_none()
        if workcell:
            logger.info(
                "Successfully retrieved workcell ID %s: '%s'.",
                id,
                workcell.name,
            )
        else:
            logger.info("Workcell with ID %s not found.", id)
        return workcell

    async def get_by_name(self, db: AsyncSession, name: str) -> WorkcellOrm | None:
        """Retrieve a specific workcell by its name."""
        logger.info("Attempting to retrieve workcell with name: '%s'.", name)
        stmt = (
            select(self.model)
            .options(selectinload(self.model.machines))
            .filter(self.model.name == name)
        )
        result = await db.execute(stmt)
        workcell = result.scalar_one_or_none()
        if workcell:
            logger.info("Successfully retrieved workcell by name '%s'.", name)
        else:
            logger.info("Workcell with name '%s' not found.", name)
        return workcell

    async def get_multi(
        self, db: AsyncSession, *, filters: SearchFilters,
    ) -> list[WorkcellOrm]:
        """List all workcells with pagination."""
        logger.info("Listing workcells with filters: %s", filters.model_dump_json())
        stmt = (
            select(self.model)
            .options(selectinload(self.model.machines))
            .order_by(self.model.name)
        )
        stmt = apply_date_range_filters(stmt, filters, self.model.created_at)
        stmt = apply_pagination(stmt, filters)
        stmt = stmt.order_by(self.model.name)
        result = await db.execute(stmt)
        workcells = list(result.scalars().all())
        logger.info("Found %d workcells.", len(workcells))
        return workcells

    async def update(
        self, db: AsyncSession, *, db_obj: WorkcellOrm, obj_in: WorkcellUpdate,
    ) -> WorkcellOrm | None:
        """Update an existing workcell."""
        logger.info("Attempting to update workcell with ID: %s.", db_obj.accession_id)

        original_name = db_obj.name
        update_data = obj_in.model_dump(exclude_unset=True)
        updates_made = False

        for key, value in update_data.items():
            if hasattr(db_obj, key) and getattr(db_obj, key) != value:
                setattr(db_obj, key, value)
                updates_made = True

        if not updates_made:
            logger.info(
                "No changes detected for workcell ID %s. No update performed.",
                db_obj.accession_id,
            )
            return db_obj

        try:
            await db.commit()
            await db.refresh(db_obj)
            logger.info(
                "Successfully updated workcell ID %s: '%s'.",
                db_obj.accession_id,
                db_obj.name,
            )
            return db_obj
        except IntegrityError as e:
            await db.rollback()
            error_message = f"Workcell with name '{obj_in.name}' already exists. Details: {e}"
            logger.error(error_message, exc_info=True)
            raise ValueError(error_message) from e
        except Exception as e:
            await db.rollback()
            logger.exception(
                "Unexpected error updating workcell '%s' (ID: %s). Rolling back.",
                original_name,
                db_obj.accession_id,
            )
            raise e

    async def remove(self, db: AsyncSession, *, id: uuid.UUID) -> bool:
        """Delete a specific workcell by its ID."""
        logger.info("Attempting to delete workcell with ID: %s.", id)
        workcell_orm = await self.get(db, id)
        if not workcell_orm:
            logger.warning("Workcell with ID %s not found for deletion.", id)
            return False

        try:
            await db.delete(workcell_orm)
            await db.commit()
            logger.info(
                "Successfully deleted workcell ID %s: '%s'.",
                id,
                workcell_orm.name,
            )
            return True
        except IntegrityError as e:
            await db.rollback()
            error_message = (
                f"Integrity error deleting workcell ID {id}. This might be due to"
                f" foreign key constraints, e.g., associated machines. Details: {e}"
            )
            logger.error(error_message, exc_info=True)
            return False
        except Exception as e:
            await db.rollback()
            logger.exception(
                "Unexpected error deleting workcell ID %s. Rolling back.",
                id,
            )
            raise e

    async def read_workcell_state(
        self, db_session: AsyncSession, workcell_accession_id: uuid.UUID,
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

    async def get_all_workcells(self, db: AsyncSession) -> list[WorkcellOrm]:
        """Retrieve all workcells from the database."""
        logger.info("Retrieving all workcells.")
        stmt = (
            select(self.model)
            .options(selectinload(self.model.machines))
            .order_by(self.model.name)
        )
        result = await db.execute(stmt)
        workcells = list(result.scalars().all())
        logger.info("Found %d workcells.", len(workcells))
        return workcells


workcell_service = WorkcellService(WorkcellOrm)
