# pylint: disable=broad-except, too-many-lines
"""Service layer for Deck  Management.

This service layer interacts with deck-related data in the database, providing
functions to create, read, update, and delete decks.
"""

import uuid

from sqlalchemy import and_, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import flag_modified

from praxis.backend.models import DeckOrm
from praxis.backend.models.deck_pydantic_models import DeckCreate, DeckUpdate
from praxis.backend.models.pydantic.filters import SearchFilters
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.services.utils.query_builder import (
  apply_date_range_filters,
  apply_pagination,
  apply_property_filters,
  apply_specific_id_filters,
)
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)

UUID = uuid.UUID


class DeckService(CRUDBase[DeckOrm, DeckCreate, DeckUpdate]):
    """Service for deck-related operations."""

    async def create(self, db: AsyncSession, *, obj_in: DeckCreate) -> DeckOrm:
        """Create a new deck."""
        logger.info(
            "Attempting to create deck '%s' for parent ID %s.",
            obj_in.name,
            obj_in.parent_accession_id,
        )

        deck_data = obj_in.model_dump(exclude={"plr_state"})
        deck_orm = self.model(**deck_data)

        if obj_in.plr_state:
            deck_orm.plr_state = obj_in.plr_state

        db.add(deck_orm)

        try:
            await db.commit()
            await db.refresh(deck_orm)
            logger.info(
                "Successfully created deck '%s' with ID %s.",
                deck_orm.name,
                deck_orm.accession_id,
            )
        except IntegrityError as e:
            await db.rollback()
            error_message = (
                f"Deck with name '{obj_in.name}' already exists. Details: {e}"
            )
            logger.exception(error_message)
            raise ValueError(error_message) from e
        except Exception as e:  # Catch all for truly unexpected errors
            logger.exception(
                "Error creating deck '%s'. Rolling back.", obj_in.name,
            )
            await db.rollback()
            raise e

        return deck_orm

    async def get(self, db: AsyncSession, accession_id: UUID) -> DeckOrm | None:
        """Retrieve a specific deck by its ID."""
        logger.info("Attempting to retrieve deck with ID: %s.", accession_id)
        stmt = (
            select(self.model)
            .options(
                joinedload(self.model.parent),
                joinedload(self.model.deck_type),
            )
            .filter(self.model.accession_id == accession_id)
        )
        result = await db.execute(stmt)
        deck = result.scalar_one_or_none()
        if deck:
            logger.info(
                "Successfully retrieved deck ID %s: '%s'.",
                accession_id,
                deck.name,
            )
        else:
            logger.info("Deck with ID %s not found.", accession_id)
        return deck

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        filters: SearchFilters,
    ) -> list[DeckOrm]:
        """List all decks, with optional filtering by parent ID."""
        logger.info(
            "Listing decks with filters: %s",
            filters.model_dump_json(),
        )
        stmt = select(self.model).options(
            joinedload(self.model.parent),
            joinedload(self.model.deck_type),
        )

        conditions = []

        if filters.parent_accession_id is not None:
            conditions.append(self.model.parent_accession_id == filters.parent_accession_id)

        if conditions:
            stmt = stmt.filter(and_(*conditions))

        # Apply generic filters from query_builder
        stmt = apply_specific_id_filters(stmt, filters, self.model)
        stmt = apply_date_range_filters(stmt, filters, self.model.created_at)
        stmt = apply_property_filters(
            stmt, filters, self.model.properties_json.cast(JSONB),
        )

        stmt = stmt.order_by(self.model.name)
        stmt = apply_pagination(stmt, filters)

        result = await db.execute(stmt)
        decks = list(result.scalars().all())
        logger.info("Found %s decks.", len(decks))
        return decks

    async def get_by_name(self, db: AsyncSession, name: str) -> DeckOrm | None:
        """Retrieve a specific deck by its name."""
        logger.info("Attempting to retrieve deck with name: '%s'.", name)
        stmt = (
            select(self.model)
            .options(
                joinedload(self.model.parent),
                joinedload(self.model.deck_type),
            )
            .filter(self.model.name == name)
        )
        result = await db.execute(stmt)
        deck = result.scalar_one_or_none()
        if deck:
            logger.info("Successfully retrieved deck by name '%s'.", name)
        else:
            logger.info("Deck with name '%s' not found.", name)
        return deck

    async def update(
        self, db: AsyncSession, *, db_obj: DeckOrm, obj_in: DeckUpdate,
    ) -> DeckOrm | None:
        """Update an existing deck."""
        logger.info("Attempting to update deck with ID: %s.", db_obj.accession_id)

        update_data = obj_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)

        if "plr_state" in update_data:
            flag_modified(db_obj, "plr_state")

        try:
            await db.commit()
            await db.refresh(db_obj)
            logger.info(
                "Successfully updated deck ID %s: '%s'.",
                db_obj.accession_id,
                db_obj.name,
            )
            return await self.get(db, db_obj.accession_id)
        except IntegrityError as e:
            await db.rollback()
            error_message = f"Integrity error while updating deck ID {db_obj.accession_id}. Details: {e}"
            logger.exception(error_message)
            raise ValueError(error_message) from e
        except Exception as e:  # Catch all for truly unexpected errors
            await db.rollback()
            logger.exception(
                "Unexpected error updating deck ID %s. Rolling back.",
                db_obj.accession_id,
            )
            raise e

    async def remove(self, db: AsyncSession, *, accession_id: UUID) -> bool:
        """Delete a specific deck by its ID."""
        logger.info("Attempting to delete deck with ID: %s.", accession_id)
        deck_orm = await self.get(db, accession_id)
        if not deck_orm:
            logger.warning("Deck with ID %s not found for deletion.", accession_id)
            return False

        try:
            await db.delete(deck_orm)
            await db.commit()
            logger.info(
                "Successfully deleted deck ID %s: '%s'.",
                accession_id,
                deck_orm.name,
            )
            return True
        except IntegrityError as e:
            await db.rollback()
            error_message = (
                f"Integrity error deleting deck ID {id}. "
                f"This might be due to foreign key constraints. Details: {e}"
            )
            logger.exception(error_message)
            raise ValueError(error_message) from e
        except Exception as e:  # Catch all for truly unexpected errors
            await db.rollback()
            logger.exception(
                "Unexpected error deleting deck ID %s. Rolling back.",
                accession_id,
            )
            raise e

    async def get_all_decks(self, db: AsyncSession) -> list[DeckOrm]:
        """Retrieve all decks from the database."""
        logger.info("Retrieving all decks.")
        stmt = select(self.model).options(
            joinedload(self.model.parent),
            joinedload(self.model.deck_type),
        )
        result = await db.execute(stmt)
        decks = list(result.scalars().all())
        logger.info("Found %d decks.", len(decks))
        return decks


deck_service = DeckService(DeckOrm)
