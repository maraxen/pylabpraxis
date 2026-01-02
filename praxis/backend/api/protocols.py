"""Protocol API endpoints.

This file contains the FastAPI router for all protocol-related endpoints,
including protocol definitions, protocol runs, and protocol execution.
"""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from praxis.backend.api.dependencies import get_db, get_protocol_execution_service
from praxis.backend.api.utils.crud_router_factory import create_crud_router
from praxis.backend.core.protocol_execution_service import ProtocolExecutionService
from praxis.backend.models.orm.protocol import FunctionProtocolDefinitionOrm, ProtocolRunOrm
from praxis.backend.models.pydantic_internals.protocol import (
  FunctionProtocolDefinitionCreate,
  FunctionProtocolDefinitionResponse,
  FunctionProtocolDefinitionUpdate,
  ProtocolRunCreate,
  ProtocolRunResponse,
  ProtocolRunUpdate,
)
from praxis.backend.services.protocol_definition import ProtocolDefinitionCRUDService
from praxis.backend.services.protocols import ProtocolRunService

router = APIRouter()


class StartRunRequest(BaseModel):
  """Request body for starting a protocol run."""

  protocol_definition_accession_id: str = Field(
    ..., description="Accession ID of the protocol definition"
  )
  name: str | None = Field(None, description="Name for the run")
  parameters: dict[str, Any] | None = Field(None, description="Input parameters for the protocol")
  simulation_mode: bool = Field(True, description="If True, run in simulation mode")


class StartRunResponse(BaseModel):
  """Response body for starting a protocol run."""

  run_id: str


@router.post(
  "/runs",
  response_model=StartRunResponse,
  status_code=status.HTTP_201_CREATED,
  tags=["Protocol Runs"],
)
async def start_protocol_run(
  request: StartRunRequest,
  execution_service: Annotated[ProtocolExecutionService, Depends(get_protocol_execution_service)],
) -> StartRunResponse:
  """Start a new protocol run.

  Creates a protocol run record and begins execution. If simulation_mode is True,
  the protocol will run without triggering actual hardware actions.
  """
  try:
    # Get protocol definition to extract name
    protocol_run = await execution_service.schedule_protocol_execution(
      protocol_name=request.protocol_definition_accession_id,  # TODO: Lookup by ID
      user_input_params=request.parameters,
      is_simulation=request.simulation_mode,
    )
    return StartRunResponse(run_id=str(protocol_run.accession_id))
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
  except Exception as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


class CancelRunResponse(BaseModel):
  """Response body for cancelling a protocol run."""

  success: bool
  message: str


class QueuedRunResponse(BaseModel):
  """Response body for a queued run."""

  accession_id: str
  name: str | None
  status: str
  created_at: str
  protocol_name: str | None = None


@router.post(
  "/runs/{run_id}/cancel",
  response_model=CancelRunResponse,
  status_code=status.HTTP_200_OK,
  tags=["Protocol Runs"],
)
async def cancel_protocol_run(
  run_id: UUID,
  execution_service: Annotated[ProtocolExecutionService, Depends(get_protocol_execution_service)],
) -> CancelRunResponse:
  """Cancel a running or queued protocol run.

  Releases reserved assets and updates the run status to CANCELLED.

  TODO: Add permission check - only admin or run owner can cancel.
  """
  try:
    success = await execution_service.cancel_protocol_run(run_id)
    if success:
      return CancelRunResponse(success=True, message=f"Run {run_id} cancelled successfully")
    return CancelRunResponse(success=False, message=f"Run {run_id} could not be cancelled")
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Failed to cancel run: {e!s}",
    ) from e


@router.get(
  "/runs/queue",
  response_model=list[QueuedRunResponse],
  status_code=status.HTTP_200_OK,
  tags=["Protocol Runs"],
)
async def get_protocol_queue(
  execution_service: Annotated[ProtocolExecutionService, Depends(get_protocol_execution_service)],
) -> list[QueuedRunResponse]:
  """Get list of active/queued protocol runs.

  Returns runs with status: PENDING, PREPARING, QUEUED, RUNNING.
  """
  from sqlalchemy import select
  from sqlalchemy.orm import selectinload

  from praxis.backend.models.enums import ProtocolRunStatusEnum

  async with execution_service.db_session_factory() as db_session:
    active_statuses = [
      ProtocolRunStatusEnum.PENDING,
      ProtocolRunStatusEnum.PREPARING,
      ProtocolRunStatusEnum.QUEUED,
      ProtocolRunStatusEnum.RUNNING,
    ]

    stmt = (
      select(ProtocolRunOrm)
      .options(selectinload(ProtocolRunOrm.top_level_protocol_definition))
      .where(ProtocolRunOrm.status.in_(active_statuses))
      .order_by(ProtocolRunOrm.created_at.desc())
    )
    result = await db_session.execute(stmt)
    runs = result.scalars().all()

    return [
      QueuedRunResponse(
        accession_id=str(run.accession_id),
        name=run.name,
        status=run.status.value if run.status else "unknown",
        created_at=run.created_at.isoformat() if run.created_at else "",
        protocol_name=run.top_level_protocol_definition.name
        if run.top_level_protocol_definition
        else None,
      )
      for run in runs
    ]


router.include_router(
  create_crud_router(
    service=ProtocolDefinitionCRUDService(FunctionProtocolDefinitionOrm),
    prefix="/definitions",
    tags=["Protocol Definitions"],
    create_schema=FunctionProtocolDefinitionCreate,
    update_schema=FunctionProtocolDefinitionUpdate,
    response_schema=FunctionProtocolDefinitionResponse,
  ),
)

# Note: The /runs CRUD endpoints are kept for direct record management,
# but the POST /runs endpoint above handles starting actual execution.
router.include_router(
  create_crud_router(
    service=ProtocolRunService(ProtocolRunOrm),
    prefix="/runs/records",
    tags=["Protocol Runs"],
    create_schema=ProtocolRunCreate,
    update_schema=ProtocolRunUpdate,
    response_schema=ProtocolRunResponse,
  ),
)


# =============================================================================
# Capability Matching
# =============================================================================


@router.get(
  "/{accession_id}/compatibility",
  response_model=list[dict[str, Any]],  # TODO: Use proper Pydantic model
  status_code=status.HTTP_200_OK,
  tags=["Protocol Capability Matching"],
)
async def get_protocol_compatibility(
  accession_id: UUID,
  db: Annotated[Any, Depends(get_db)],
) -> Any:
  """Check protocol compatibility against all machines.

  Returns a list of compatibility results for each available machine.
  """
  from sqlalchemy import select
  from sqlalchemy.orm import selectinload

  from praxis.backend.models.orm.machine import MachineOrm
  from praxis.backend.services.capability_matcher import capability_matcher

  # 1. Fetch protocol
  protocol = await db.get(FunctionProtocolDefinitionOrm, accession_id)
  if not protocol:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Protocol {accession_id} not found",
    )

  # 2. Fetch all machines with definitions
  stmt = select(MachineOrm).options(selectinload(MachineOrm.definition))
  result = await db.execute(stmt)
  machines = result.scalars().all()

  # 3. Match
  machine_tuples = []
  for m in machines:
    machine_tuples.append((m, m.definition))

  results = capability_matcher.find_compatible_machines(protocol, machine_tuples)

  # 4. Format response
  # Note: CapabilityMatchResult is a Pydantic model, so we can return it directly if we want
  # But we also want to return the machine details for the UI.
  response = []
  for machine, match_result in results:
    response.append(
      {
        "machine": {
          "accession_id": str(machine.accession_id),
          "name": machine.name,
          "machine_type": machine.definition.plr_category if machine.definition else "unknown",
          # Add other machine details as needed
        },
        "compatibility": match_result.model_dump(),
      }
    )

  return response
