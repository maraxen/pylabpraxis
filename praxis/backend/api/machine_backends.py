"""API endpoints for Machine Backend Definitions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.api.dependencies import get_db
from praxis.backend.models.domain.filters import SearchFilters
from praxis.backend.models.domain.machine_backend import (
  MachineBackendDefinition,
  MachineBackendDefinitionCreate,
  MachineBackendDefinitionRead,
  MachineBackendDefinitionUpdate,
)
from praxis.backend.services.machine_backend_definition import (
  MachineBackendDefinitionCRUDService,
)

router = APIRouter()

# Initialize service
machine_backend_service = MachineBackendDefinitionCRUDService(MachineBackendDefinition)


@router.get(
  "/",
  response_model=list[MachineBackendDefinitionRead],
  summary="List machine backend definitions",
)
async def list_backend_definitions(
  db: Annotated[AsyncSession, Depends(get_db)],
  skip: int = 0,
  limit: int = 100,
) -> list[MachineBackendDefinitionRead]:
  """Retrieve a list of machine backend definitions."""
  filters = SearchFilters(offset=skip, limit=limit)
  definitions = await machine_backend_service.get_multi(db, filters=filters)
  return definitions


@router.get(
  "/{accession_id}",
  response_model=MachineBackendDefinitionRead,
  summary="Get machine backend definition by ID",
)
async def get_backend_definition(
  accession_id: UUID,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> MachineBackendDefinitionRead:
  """Retrieve a specific machine backend definition by its accession ID."""
  definition = await machine_backend_service.get(db, accession_id=accession_id)
  if not definition:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Machine backend definition with ID '{accession_id}' not found",
    )
  return definition


@router.post(
  "/",
  response_model=MachineBackendDefinitionRead,
  status_code=status.HTTP_201_CREATED,
  summary="Create machine backend definition",
)
async def create_backend_definition(
  data: MachineBackendDefinitionCreate,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> MachineBackendDefinitionRead:
  """Create a new machine backend definition."""
  return await machine_backend_service.create(db, obj_in=data)


@router.put(
  "/{accession_id}",
  response_model=MachineBackendDefinitionRead,
  summary="Update machine backend definition",
)
async def update_backend_definition(
  accession_id: UUID,
  data: MachineBackendDefinitionUpdate,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> MachineBackendDefinitionRead:
  """Update an existing machine backend definition."""
  db_obj = await machine_backend_service.get(db, accession_id=accession_id)
  if not db_obj:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Machine backend definition with ID '{accession_id}' not found",
    )
  return await machine_backend_service.update(db, db_obj=db_obj, obj_in=data)


@router.delete(
  "/{accession_id}",
  status_code=status.HTTP_204_NO_CONTENT,
  summary="Delete machine backend definition",
)
async def delete_backend_definition(
  accession_id: UUID,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
  """Delete a machine backend definition."""
  definition = await machine_backend_service.remove(db, accession_id=accession_id)
  if not definition:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Machine backend definition with ID '{accession_id}' not found",
    )
