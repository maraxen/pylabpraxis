# <filename>praxis/backend/api/machines.py</filename>
"""Machine API endpoints.

This file contains the FastAPI router for all machine-related endpoints,
including machine creation, retrieval, updates, and deletion.
"""

from functools import partial
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Import the service layer, aliased as 'svc' for convenience
import praxis.backend.services as svc

# Import dependencies from the local 'api' package
from praxis.backend.api.dependencies import get_db

# Import all necessary Pydantic models from the central models package
from praxis.backend.models import (
  MachineCreate,
  MachineResponse,
  MachineStatusEnum,
  MachineUpdate,
  SearchFilters,
)
from praxis.backend.utils.accession_resolver import get_accession_id_from_accession
from praxis.backend.utils.errors import PraxisAPIError
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

# Initialize the FastAPI router
router = APIRouter()

log_machine_api_errors = partial(
  log_async_runtime_errors, logger_instance=logger, raises_exception=PraxisAPIError,
)

machine_accession_resolver = partial(
  get_accession_id_from_accession,
  get_func=svc.read_machine,
  get_by_name_func=svc.read_machine_by_name,
  entity_type_name="Machine",
)


@log_machine_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to create machine: ",
  suffix="",
)
@router.post(
  "/",
  response_model=MachineResponse,
  status_code=status.HTTP_201_CREATED,
  tags=["Machines"],
)
async def create_machine(machine: MachineCreate, db: AsyncSession = Depends(get_db)):
  """Create a new machine."""
  try:
    created_machine = await svc.create_machine(db=db, machine_create=machine)
    return created_machine
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_machine_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to get machine: ",
  suffix="",
)
@router.get(
  "/{accession}",
  response_model=MachineResponse,
  tags=["Machines"],
)
async def get_machine(accession: str, db: AsyncSession = Depends(get_db)):
  """Retrieve a machine by accession ID or name."""
  machine_id = await machine_accession_resolver(db=db, accession=accession)

  db_machine = await svc.read_machine(db, machine_id)
  if db_machine is None:
    raise HTTPException(status_code=404, detail="Machine not found")
  return db_machine


@log_machine_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to list machines: ",
  suffix="",
)
@router.get(
  "/",
  response_model=list[MachineResponse],
  tags=["Machines"],
)
async def list_machines(
  db: AsyncSession = Depends(get_db),
  filters: SearchFilters = Depends(),
  status: MachineStatusEnum | None = None,
  pylabrobot_class_filter: str | None = None,
  name_filter: str | None = None,
):
  """List all machines with optional filtering."""
  return await svc.list_machines(
    db,
    filters=filters,
    status=status,
    pylabrobot_class_filter=pylabrobot_class_filter,
    name_filter=name_filter,
  )


@log_machine_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to update machine: ",
  suffix="",
)
@router.put(
  "/{accession}",
  response_model=MachineResponse,
  tags=["Machines"],
)
async def update_machine(
  accession: str,
  machine_update: MachineUpdate,
  db: AsyncSession = Depends(get_db),
):
  """Update an existing machine."""
  machine_id = await machine_accession_resolver(db=db, accession=accession)

  try:
    updated_machine = await svc.update_machine(
      db=db, machine_accession_id=machine_id, machine_update=machine_update,
    )
    if not updated_machine:
      raise HTTPException(status_code=404, detail=f"Machine '{accession}' not found.")
    return updated_machine
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_machine_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to update machine status: ",
  suffix="",
)
@router.patch(
  "/{accession}/status",
  response_model=MachineResponse,
  tags=["Machines"],
)
async def update_machine_status(
  accession: str,
  new_status: MachineStatusEnum,
  status_details: str | None = None,
  current_protocol_run_accession_id: UUID | None = None,
  db: AsyncSession = Depends(get_db),
):
  """Update the status of a machine."""
  machine_id = await machine_accession_resolver(db=db, accession=accession)

  try:
    updated_machine = await svc.update_machine_status(
      db=db,
      machine_accession_id=machine_id,
      new_status=new_status,
      status_details=status_details,
      current_protocol_run_accession_id=current_protocol_run_accession_id,
    )
    if not updated_machine:
      raise HTTPException(status_code=404, detail=f"Machine '{accession}' not found.")
    return updated_machine
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_machine_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to delete machine: ",
  suffix="",
)
@router.delete(
  "/{accession}",
  status_code=status.HTTP_204_NO_CONTENT,
  tags=["Machines"],
)
async def delete_machine(accession: str, db: AsyncSession = Depends(get_db)):
  """Delete a machine."""
  machine_id = await machine_accession_resolver(db=db, accession=accession)

  success = await svc.delete_machine(db, machine_id)
  if not success:
    raise HTTPException(
      status_code=404,
      detail=f"Machine '{accession}' not found or could not be deleted.",
    )
