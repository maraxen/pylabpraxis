"""Generic CRUD base class for SQLAlchemy models."""

import contextlib
import enum
import inspect as py_inspect
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import Enum as SAEnumType
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from praxis.backend.models.domain.filters import SearchFilters
from praxis.backend.services.utils.query_builder import (
  apply_date_range_filters,
  apply_pagination,
  apply_property_filters,
  apply_search_filters,
  apply_sorting,
  apply_specific_id_filters,
)
from praxis.backend.utils.db import Base
from praxis.backend.utils.logging import get_logger

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


logger = get_logger(__name__)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
  """Generic CRUD base class for SQLAlchemy models."""

  def __init__(self, model: type[ModelType]) -> None:
    """CRUD object with default methods to Create, Read, Update, Delete (CRUD).

    Args:
        model (type[ModelType]): The SQLAlchemy model class for which CRUD operations are defined.

    """
    self.model = model

  async def get(self, db: AsyncSession, accession_id: UUID) -> ModelType | None:
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
      statement = apply_search_filters(statement, self.model, filters)
      statement = apply_date_range_filters(
        statement,
        filters,
        self.model.created_at,
      )
      if self.model.properties_json:
        statement = apply_property_filters(
          statement,
          filters,
          self.model.properties_json,
        )
    if filters.sort_by:
      statement = apply_sorting(statement, self.model, filters.sort_by)
    statement = apply_specific_id_filters(statement, filters, self.model)
    statement = apply_pagination(statement, filters)
    result = await db.execute(statement)
    return list(result.scalars().all())

  async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
    """Create a new object."""
    # Check if the model supports SQLModel-style validation
    if hasattr(self.model, "model_validate"):
      # SQLModel / Pydantic v2 style
      # We still dump to dict first because model_validate usually expects a dict or object,
      # but for SQLModel table=True models, model_validate is the standard entry point.
      # However, if obj_in is a schema and self.model is a TableModel, we can often just do:
      db_obj = self.model.model_validate(obj_in)
    else:
      # Legacy SQLAlchemy ORM style
      obj_in_data = obj_in.model_dump()

      # Get the valid constructor parameters for the ORM model
      init_signature = py_inspect.signature(self.model.__init__)
      valid_params = {p.name for p in init_signature.parameters.values()}

      # Filter the input data to include only keys that are valid constructor parameters
      filtered_data = {key: value for key, value in obj_in_data.items() if key in valid_params}

      # Smart Enum conversion:
      # 1. If value is Enum but column is NOT SAEnum (e.g. String), convert to value.
      # 2. If value is NOT Enum (e.g. String) but column IS SAEnum, convert back to Enum object.
      mapper = inspect(self.model)
      for key, value in filtered_data.items():
        col = mapper.columns.get(key)
        if col is None:
          continue

        is_enum_col = isinstance(col.type, SAEnumType)
        is_enum_val = isinstance(value, enum.Enum)

        if is_enum_val and not is_enum_col:
          # Convert Enum object to value (for String columns)
          filtered_data[key] = value.value
        elif not is_enum_val and is_enum_col:
          # Convert value to Enum object (for SAEnum columns)
          # Pydantic may have converted it to a string/int due to use_enum_values=True
          enum_class = getattr(col.type, "enum_class", None)
          if enum_class:
            with contextlib.suppress(ValueError, TypeError):
              filtered_data[key] = enum_class(value)

      db_obj = self.model(**filtered_data)

    db.add(db_obj)
    await db.flush()
    await db.refresh(db_obj)
    return db_obj

  async def update(
    self,
    db: AsyncSession,
    *,
    db_obj: ModelType,
    obj_in: UpdateSchemaType,
  ) -> ModelType:
    """Update an existing object."""
    update_data = obj_in.model_dump(exclude_unset=True)

    if hasattr(db_obj, "sqlmodel_update"):
      # SQLModel style update
      db_obj.sqlmodel_update(update_data)
    else:
      # Legacy ORM style update
      # Smart Enum conversion for updates
      mapper = inspect(self.model)
      for key, value in update_data.items():
        col = mapper.columns.get(key)
        if col is None:
          continue

        is_enum_col = isinstance(col.type, SAEnumType)
        is_enum_val = isinstance(value, enum.Enum)

        if is_enum_val and not is_enum_col:
          update_data[key] = value.value
        elif not is_enum_val and is_enum_col:
          enum_class = getattr(col.type, "enum_class", None)
          if enum_class:
            with contextlib.suppress(ValueError, TypeError):
              update_data[key] = enum_class(value)

      # Filter update_data to only include valid model attributes
      # This prevents issues with relationships being set to None/invalid types
      mapper = inspect(self.model)
      valid_fields = set(mapper.columns.keys())

      for field, value in update_data.items():
        if field in valid_fields:
          setattr(db_obj, field, value)
        else:
          logger.debug("Skipping update for non-column field: %s", field)

    db.add(db_obj)
    await db.flush()
    await db.refresh(db_obj)
    return db_obj

  async def remove(self, db: AsyncSession, *, accession_id: UUID) -> ModelType | None:
    """Delete an object by its primary key."""
    statement = select(self.model).where(self.model.accession_id == accession_id)
    result = await db.execute(statement)
    obj = result.scalars().first()
    if obj:
      await db.delete(obj)
      await db.flush()
    return obj

  async def get_by_name(self, db: AsyncSession, name: str) -> ModelType | None:
    """Retrieve a specific object by its name."""
    statement = select(self.model).filter(self.model.name == name)
    result = await db.execute(statement)
    return result.scalars().first()
