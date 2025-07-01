"""Generic CRUD base class for SQLAlchemy models.
"""
from typing import Any, Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from praxis.backend.models.filters import SearchFilters
from praxis.backend.services.utils.query_builder import (
    apply_date_range_filters,
    apply_pagination,
    apply_search_filters,
    apply_sorting,
)

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic CRUD base class for SQLAlchemy models.
    """

    def __init__(self, model: type[ModelType]):
        """CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """Get a single object by its primary key.
        """
        statement = select(self.model).where(self.model.id == id)
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, filters: SearchFilters,
    ) -> list[ModelType]:
        """Get multiple objects with filtering, sorting, and pagination.
        """
        statement = select(self.model)
        statement = apply_search_filters(statement, self.model, filters.search_filters)
        statement = apply_date_range_filters(
            statement, self.model, filters.date_range_filters,
        )
        statement = apply_sorting(statement, self.model, filters.sort_by)
        statement = apply_pagination(statement, filters.offset, filters.limit)
        result = await db.execute(statement)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new object.
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any],
    ) -> ModelType:
        """Update an existing object.
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> ModelType | None:
        """Delete an object by its primary key.
        """
        statement = select(self.model).where(self.model.id == id)
        result = await db.execute(statement)
        obj = result.scalars().first()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
