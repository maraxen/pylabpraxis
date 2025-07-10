"""Base model for CRUD operations specifically as they relate to PyLabRobot type definitions."""

from typing import Any, Generic, TypeVar, cast
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from praxis.backend.models.pydantic.filters import SearchFilters
from praxis.backend.services.utils.query_builder import (
  apply_date_range_filters,
  apply_pagination,
  apply_property_filters,
  apply_search_filters,
  apply_sorting,
  apply_specific_id_filters,
)
from praxis.backend.utils.db import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class PLRTypeCRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
  """Generic CRUD base class for SQLAlchemy models."""

  def __init__(self, model: type[ModelType]) -> None:
    """CRUD object with default methods to Create, Read, Update, Delete (CRUD).

    Args:
        model (type[ModelType]): The SQLAlchemy model class for which CRUD operations are defined.

    """
    self.model = model

  async def get(self, db: AsyncSession, accession_id: str | UUID) -> ModelType | None:
    """Get a single object by its primary key.

    Args:
        db (AsyncSession): The database session.
        accession_id (str | UUID): The primary key of the object to retrieve.

    Returns:
        ModelType | None: The retrieved object or None if not found.

    """
    statement = select(self.model).where(self.model.accession_id == accession_id)
    result = await db.execute(statement)
    return result.scalars().first()

  async def get_multi(
    self,
    db: AsyncSession,
    *,
    filters: SearchFilters,
  ) -> list[ModelType]:
    """Get multiple objects with filtering, sorting, and pagination."""
    statement = select(self.model)
    if filters.search_filters:
      statement = apply_search_filters(statement, cast("Base", self.model), filters)
      statement = apply_date_range_filters(
        statement,
        filters,
        cast("Column[DateTime]", self.model.created_at),
      )
      statement = apply_property_filters(
        statement,
        filters,
        cast("Column[JSONB]", self.model.properties_json),
      )
    if filters.sort_by:
      statement = apply_sorting(statement, cast("Base", self.model), filters.sort_by)
    statement = apply_specific_id_filters(statement, filters, cast("Base", self.model))
    statement = apply_pagination(statement, filters)
    result = await db.execute(statement)
    return list(result.scalars().all())

  async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
    """Create a new object."""
    obj_in_data = jsonable_encoder(obj_in)
    db_obj = self.model(**obj_in_data)
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
    """Update an existing object."""
    obj_data = jsonable_encoder(db_obj)
    update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
    for field in obj_data:
      if field in update_data:
        setattr(db_obj, field, update_data[field])
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

  async def remove(self, db: AsyncSession, *, accession_id: str | UUID) -> ModelType | None:
    """Delete an object by its primary key."""
    statement = select(self.model).where(self.model.accession_id == accession_id)
    result = await db.execute(statement)
    obj = result.scalars().first()
    if obj:
      await db.delete(obj)
      await db.commit()
    return obj
