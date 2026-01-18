"""API endpoints for Machine Frontend Definitions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.api.dependencies import get_db
from praxis.backend.models.domain.filters import SearchFilters
from praxis.backend.models.domain.machine_backend import (
  MachineBackendDefinition,
  MachineBackendDefinitionRead,
)
from praxis.backend.models.domain.machine_frontend import (
  MachineFrontendDefinition,
  MachineFrontendDefinitionCreate,
  MachineFrontendDefinitionRead,
  MachineFrontendDefinitionUpdate,
)
from praxis.backend.services.machine_frontend_definition import (
  MachineFrontendDefinitionCRUDService,
)

router = APIRouter()

frontend_service = MachineFrontendDefinitionCRUDService(MachineFrontendDefinition)


@router.get("/", response_model=list[MachineFrontendDefinitionRead])
async def list_frontend_definitions(
  db: Annotated[AsyncSession, Depends(get_db)],
  skip: int = 0,
  limit: int = 100,
) -> list[MachineFrontendDefinitionRead]:
  """List all machine frontend definitions."""
  filters = SearchFilters(offset=skip, limit=limit)
  return await frontend_service.get_multi(db, filters=filters)


@router.get("/{accession_id}", response_model=MachineFrontendDefinitionRead)
async def get_frontend_definition(
  accession_id: UUID,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> MachineFrontendDefinitionRead:
  """Get a machine frontend definition by accession ID."""
  definition = await frontend_service.get(db, accession_id=accession_id)
  if not definition:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Machine frontend definition with ID {accession_id} not found",
    )
  return definition


@router.get("/{accession_id}/backends", response_model=list[MachineBackendDefinitionRead])
async def get_compatible_backends(
  accession_id: UUID,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> list[MachineBackendDefinitionRead]:
  """Get compatible backend definitions for a frontend definition."""
  stmt = select(MachineBackendDefinition).where(
    MachineBackendDefinition.frontend_definition_accession_id == accession_id
  )
  result = await db.execute(stmt)
  return list(result.scalars().all())


@router.post(
  "/",
  response_model=MachineFrontendDefinitionRead,
  status_code=status.HTTP_201_CREATED,
)
async def create_frontend_definition(
  data: MachineFrontendDefinitionCreate,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> MachineFrontendDefinitionRead:
  """Create a new machine frontend definition."""
  return await frontend_service.create(db, obj_in=data)


@router.put("/{accession_id}", response_model=MachineFrontendDefinitionRead)
async def update_frontend_definition(
  accession_id: UUID,
  data: MachineFrontendDefinitionUpdate,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> MachineFrontendDefinitionRead:
  """Update a machine frontend definition."""
  db_obj = await frontend_service.get(db, accession_id=accession_id)
  if not db_obj:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Machine frontend definition with ID {accession_id} not found",
    )
  return await frontend_service.update(db, db_obj=db_obj, obj_in=data)


@router.delete("/{accession_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_frontend_definition(
  accession_id: UUID,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
  """Delete a machine frontend definition."""
  db_obj = await frontend_service.get(db, accession_id=accession_id)
  if not db_obj:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Machine frontend definition with ID {accession_id} not found",
    )
  await frontend_service.remove(db, accession_id=accession_id)
