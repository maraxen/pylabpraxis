"""Machine API endpoints.

This file contains the FastAPI router for all machine-related endpoints,
including machine creation, retrieval, updates, and deletion.
"""

from functools import partial
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.api.dependencies import get_db
from praxis.backend.api.utils.crud_router_factory import create_crud_router
from praxis.backend.models.orm.machine import MachineOrm, MachineStatusEnum
from praxis.backend.models.pydantic_internals.machine import (
  MachineCreate,
  MachineResponse,
  MachineUpdate,
)
from praxis.backend.services.machine import MachineService
from praxis.backend.utils.accession_resolver import get_accession_id_from_accession
from praxis.backend.utils.errors import PraxisAPIError
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

# Initialize the FastAPI router
router = APIRouter()

log_machine_api_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  raises_exception=PraxisAPIError,
)

machine_service = MachineService(MachineOrm)

machine_accession_resolver = partial(
  get_accession_id_from_accession,
  get_func=machine_service.get,
  get_by_name_func=machine_service.get_by_name,
  entity_type_name="Machine",
)

router.include_router(
  create_crud_router(
    service=machine_service,
    prefix="/",
    tags=["Machines"],
    create_schema=MachineCreate,
    update_schema=MachineUpdate,
    response_schema=MachineResponse,
  ),
)


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
  db: Annotated[AsyncSession, Depends(get_db)],
  status_details: str | None = None,
  current_protocol_run_accession_id: UUID | None = None,
) -> MachineResponse:
  """Update the status of a machine."""
  machine_id = await machine_accession_resolver(
    db=db,
    accession=accession,
  )

  try:
    updated_machine = await machine_service.update_machine_status(
      db=db,
      machine_accession_id=machine_id,
      new_status=new_status,
      status_details=status_details,
      current_protocol_run_accession_id=current_protocol_run_accession_id,
    )
    if not updated_machine:
      raise HTTPException(status_code=404, detail=f"Machine '{accession}' not found.")
  except ValueError as e:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail=str(e),
    ) from e
  else:
    logger.info(
      "Machine '%s' (ID: %s) status updated to '%s'.",
      updated_machine.name,
      updated_machine.accession_id,
      new_status.value,
    )
    return MachineResponse.model_validate(updated_machine)
