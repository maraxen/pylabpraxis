"""Workcell API endpoints.

This file contains the FastAPI router for workcell-related endpoints,
including workcell CRUD operations and legacy orchestrator endpoints.
"""

from functools import partial

from fastapi import (
  APIRouter,
  Depends,
  HTTPException,
  status,
)
from sqlalchemy.ext.asyncio import AsyncSession

import praxis.backend.services as svc
from praxis.backend.api.dependencies import get_db
from praxis.backend.models import (
  SearchFilters,
  WorkcellCreate,
  WorkcellResponse,
  WorkcellUpdate,
)
from praxis.backend.utils.accession_resolver import get_accession_id_from_accession
from praxis.backend.utils.errors import PraxisAPIError
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

router = APIRouter()

logger = get_logger(__name__)

log_workcell_api_errors = partial(
  log_async_runtime_errors, logger_instance=logger, raises_exception=PraxisAPIError,
)

workcell_accession_resolver = partial(
  get_accession_id_from_accession,
  get_func=svc.read_workcell,
  get_by_name_func=svc.read_workcell_by_name,
  entity_type_name="Workcell",
)


# Workcell CRUD Endpoints


@log_workcell_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to create workcell: ",
  suffix="",
)
@router.post(
  "/",
  response_model=WorkcellResponse,
  status_code=status.HTTP_201_CREATED,
  tags=["Workcells"],
)
async def create_workcell(workcell: WorkcellCreate, db: AsyncSession = Depends(get_db)):
  """Create a new workcell."""
  try:
    created_workcell = await svc.create_workcell(db=db, **workcell.model_dump())
    return created_workcell
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_workcell_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to get workcell: ",
  suffix="",
)
@router.get(
  "/{accession}",
  response_model=WorkcellResponse,
  tags=["Workcells"],
)
async def get_workcell(accession: str, db: AsyncSession = Depends(get_db)):
  """Retrieve a workcell by accession ID or name."""
  workcell_id = await workcell_accession_resolver(db=db, accession=accession)

  db_workcell = await svc.read_workcell(db, workcell_id)
  if db_workcell is None:
    raise HTTPException(status_code=404, detail="Workcell not found")
  return db_workcell


@log_workcell_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to list workcells: ",
  suffix="",
)
@router.get(
  "/",
  response_model=list[WorkcellResponse],
  tags=["Workcells"],
)
async def list_workcells( # pylint: disable=too-many-arguments
  db: AsyncSession = Depends(get_db), # pylint: disable=too-many-arguments
  filters: SearchFilters = Depends(), # pylint: disable=too-many-arguments
):
  """List all workcells."""
  return await svc.list_workcells(db, filters=filters)


@log_workcell_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to update workcell: ",
  suffix="",
)
@router.put(
  "/{accession}",
  response_model=WorkcellResponse,
  tags=["Workcells"],
)
async def update_workcell(
  accession: str,
  workcell_update: WorkcellUpdate,
  db: AsyncSession = Depends(get_db),
):
  """Update an existing workcell."""
  workcell_id = await workcell_accession_resolver(db=db, accession=accession)

  update_data = workcell_update.model_dump(exclude_unset=True)
  try:
    updated_workcell = await svc.update_workcell(
      db=db, workcell_accession_id=workcell_id, **update_data,
    )
    if not updated_workcell:
      raise HTTPException(status_code=404, detail=f"Workcell '{accession}' not found.")
    return updated_workcell
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_workcell_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to delete workcell: ",
  suffix="",
)
@router.delete(
  "/{accession}",
  status_code=status.HTTP_204_NO_CONTENT,
  tags=["Workcells"],
)
async def delete_workcell(accession: str, db: AsyncSession = Depends(get_db)):
  """Delete a workcell."""
  workcell_id = await workcell_accession_resolver(db=db, accession=accession)

  success = await svc.delete_workcell(db, workcell_id)
  if not success:
    raise HTTPException(
      status_code=404,
      detail=f"Workcell '{accession}' not found or could not be deleted.",
    )
