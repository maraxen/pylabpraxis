"""Generic CRUD router factory for creating FastAPI routers with standard CRUD endpoints."""

from typing import Annotated, Any, TypeVar
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.api.dependencies import get_db
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.utils.db import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)


def create_crud_router(
  *,
  service: CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType],
  prefix: str,
  tags: list[str | Any],
  create_schema: type[CreateSchemaType],
  update_schema: type[UpdateSchemaType],
  response_schema: type[ResponseSchemaType],
) -> APIRouter:
  """Create a FastAPI router with standard CRUD endpoints."""
  router = APIRouter()

  @router.post(
    prefix,
    response_model=response_schema,
    status_code=status.HTTP_201_CREATED,
    tags=tags,
  )
  async def create(
    request: Request,
    db: AsyncSession = Depends(get_db),
  ) -> ModelType:
    obj_in_data = await request.json()
    obj_in = create_schema.model_validate(obj_in_data)
    return await service.create(db=db, obj_in=obj_in)

  @router.get(prefix, response_model=list[ResponseSchemaType], tags=tags)
  async def get_multi(
    db: Annotated[AsyncSession, Depends(get_db)],
    filters: Annotated[SearchFilters, Depends()],
  ) -> list[ModelType]:
    return await service.get_multi(db, filters=filters)

  @router.get(f"{prefix}/{{accession_id}}", response_model=ResponseSchemaType, tags=tags)
  async def get(
    accession_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
  ) -> ModelType:
    db_obj = await service.get(db, accession_id=accession_id)
    if db_obj is None:
      raise HTTPException(status_code=404, detail="Not found")
    return db_obj

  @router.put(f"{prefix}/{{accession_id}}", response_model=ResponseSchemaType, tags=tags)
  async def update(
    accession_id: UUID,
    obj_in: UpdateSchemaType,
    db: Annotated[AsyncSession, Depends(get_db)],
  ) -> ModelType:
    db_obj = await service.get(db, accession_id=accession_id)
    if db_obj is None:
      raise HTTPException(status_code=404, detail="Not found")
    return await service.update(
      db=db, db_obj=db_obj, obj_in=obj_in.model_dump(exclude_unset=True)
    )

  @router.delete(f"{prefix}/{{accession_id}}", status_code=status.HTTP_204_NO_CONTENT, tags=tags)
  async def delete(
    accession_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
  ) -> None:
    db_obj = await service.remove(db, accession_id=accession_id)
    if db_obj is None:
      raise HTTPException(status_code=404, detail="Not found")

  return router
