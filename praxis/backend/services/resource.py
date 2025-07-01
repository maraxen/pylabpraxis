# pylint: disable=broad-except, too-many-lines
"""Service layer for Resource  Management."""

import uuid
from functools import partial

from sqlalchemy import and_, select
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.attributes import flag_modified

from praxis.backend.models.filters import SearchFilters
from praxis.backend.models.resource_orm import ResourceOrm
from praxis.backend.models.resource_pydantic_models import (
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
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

UUID = uuid.UUID


class ResourceService(CRUDBase[ResourceOrm, ResourceCreate, ResourceUpdate]):
    """Service for resource-related operations.
    """

    def __init__(self, model: type[ResourceOrm]):
        super().__init__(model)
        self.log_resource_data_service_errors = partial(
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
    async def create(
        self, db: AsyncSession, *, obj_in: ResourceCreate,
    ) -> ResourceOrm:
        """Create a new resource."""
        logger.info(
            "Attempting to create resource '%s' for parent ID %s.",
            obj_in.name,
            obj_in.parent_accession_id,
        )

        resource_data = obj_in.model_dump(exclude={"plr_state"})
        resource_orm = self.model(**resource_data)

        if obj_in.plr_state:
            resource_orm.plr_state = obj_in.plr_state

        db.add(resource_orm)

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
            error_message = (
                f"Resource with name '{obj_in.name}' already exists. Details: {e}"
            )
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
        self, db: AsyncSession, id: UUID,
    ) -> ResourceOrm | None:
        """Retrieve a specific resource by its ID."""
        logger.info("Attempting to retrieve resource with ID: %s.", id)
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.children),
                joinedload(self.model.parent),
                joinedload(self.model.resource_definition),
            )
            .filter(self.model.accession_id == id)
        )
        result = await db.execute(stmt)
        resource = result.scalar_one_or_none()
        if resource:
            logger.info(
                "Successfully retrieved resource ID %s: '%s'.",
                id,
                resource.name,
            )
        else:
            logger.info("Resource with ID %s not found.", id)
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
            conditions.append(self.model.current_status == status)

        if conditions:
            stmt = stmt.filter(and_(*conditions))

        # Apply generic filters from query_builder
        stmt = apply_specific_id_filters(stmt, filters, self.model)
        stmt = apply_date_range_filters(stmt, filters, self.model.created_at)
        stmt = apply_property_filters(
            stmt, filters, self.model.properties_json.cast(JSONB),
        )

        stmt = apply_pagination(stmt, filters)

        stmt = stmt.order_by(self.model.name)
        result = await db.execute(stmt)
        resources = list(result.scalars().all())
        logger.info("Found %s resources.", len(resources))
        return resources

    async def get_by_name(self, db: AsyncSession, name: str) -> ResourceOrm | None:
        """Retrieve a specific resource by its name."""
        logger.info("Attempting to retrieve resource with name: '%s'.", name)
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.children),
                joinedload(self.model.parent),
                joinedload(self.model.resource_definition),
            )
            .filter(self.model.name == name)
        )
        result = await db.execute(stmt)
        resource = result.scalar_one_or_none()
        if resource:
            logger.info("Successfully retrieved resource by name '%s'.", name)
        else:
            logger.info("Resource with name '%s' not found.", name)
        return resource

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ResourceOrm,
        obj_in: ResourceUpdate,
    ) -> ResourceOrm | None:
        """Update an existing resource."""
        logger.info("Attempting to update resource with ID: %s.", db_obj.accession_id)

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
                "Successfully updated resource ID %s: '%s'.",
                db_obj.accession_id,
                db_obj.name,
            )
            return await self.get(db, db_obj.accession_id)
        except IntegrityError as e:
            await db.rollback()
            error_message = (
                f"Integrity error updating resource ID {db_obj.accession_id}. Details: {e}"
            )
            logger.exception(error_message)
            raise ValueError(error_message) from e
        except Exception as e:  # Catch all for truly unexpected errors
            await db.rollback()
            logger.exception(
                "Unexpected error updating resource ID %s. Rolling back.",
                db_obj.accession_id,
            )
            raise e

    async def remove(self, db: AsyncSession, *, id: UUID) -> bool:
        """Delete a specific resource by its ID."""
        logger.info("Attempting to delete resource with ID: %s.", id)
        resource_orm = await self.get(db, id)
        if not resource_orm:
            logger.warning("Resource with ID %s not found for deletion.", id)
            return False

        try:
            await db.delete(resource_orm)
            await db.commit()
            logger.info(
                "Successfully deleted resource ID %s: '%s'.",
                id,
                resource_orm.name,
            )
            return True
        except IntegrityError as e:
            await db.rollback()
            error_message = (
                f"Integrity error deleting resource ID {id}. "
                f"This might be due to foreign key constraints. Details: {e}"
            )
            logger.exception(error_message)
            raise ValueError(error_message) from e
        except Exception as e:  # Catch all for truly unexpected errors
            await db.rollback()
            logger.exception(
                "Unexpected error deleting resource ID %s. Rolling back.",
                id,
            )
            raise e

    async def get_all_resources(self, db: AsyncSession) -> list[ResourceOrm]:
        """Retrieve all resources from the database."""
        logger.info("Retrieving all resources.")
        stmt = select(self.model).options(
            joinedload(self.model.parent),
            selectinload(self.model.children),
            joinedload(self.model.resource_definition),
        )
        result = await db.execute(stmt)
        resources = list(result.scalars().all())
        logger.info("Found %d resources.", len(resources))
        return resources


resource_service = ResourceService(ResourceOrm)
