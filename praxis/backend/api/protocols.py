"""Protocol API endpoints.

This file contains the FastAPI router for all protocol-related endpoints,
including protocol definitions, protocol runs, protocol execution, and simulation.
"""

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from praxis.backend.api.dependencies import get_db, get_protocol_execution_service
from praxis.backend.api.utils.crud_router_factory import create_crud_router
from praxis.backend.core.protocol_execution_service import ProtocolExecutionService
from praxis.backend.core.simulation import (
  GraphReplayEngine,
  GraphReplayResult,
)
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


# =============================================================================
# Protocol Simulation (Backend Fallback for Browser Mode)
# =============================================================================


class SimulationRequest(BaseModel):
  """Request body for protocol simulation.

  This endpoint serves as a backend fallback for browser-mode simulation
  when the browser can't execute the graph replay directly.
  """

  computation_graph: dict[str, Any] | None = Field(
    None,
    description="Pre-extracted computation graph. If not provided, "
    "will use the graph from the protocol definition.",
  )


class SimulationViolationResponse(BaseModel):
  """A violation detected during simulation."""

  operation_id: str = Field(description="ID of the operation that caused violation")
  operation_index: int = Field(description="Index in execution order")
  method_name: str = Field(description="Method that failed")
  receiver: str = Field(description="Variable receiving the call")
  violation_type: str = Field(description="Type of violation")
  message: str = Field(description="Human-readable error message")
  suggested_fix: str | None = Field(default=None, description="How to fix this")
  line_number: int | None = Field(default=None, description="Source line if available")


class SimulationResponse(BaseModel):
  """Response body for protocol simulation."""

  passed: bool = Field(description="Whether simulation passed without violations")
  violations: list[SimulationViolationResponse] = Field(
    default_factory=list, description="All violations found during simulation"
  )
  operations_executed: int = Field(default=0, description="Number of operations replayed")
  replay_mode: str = Field(default="graph", description="Replay mode used")
  errors: list[str] = Field(
    default_factory=list, description="Non-violation errors (parse errors, etc.)"
  )
  final_state_summary: dict[str, Any] = Field(
    default_factory=dict, description="Summary of final state"
  )


@router.post(
  "/definitions/{accession_id}/simulate",
  response_model=SimulationResponse,
  status_code=status.HTTP_200_OK,
  tags=["Protocol Simulation"],
)
async def simulate_protocol(
  accession_id: UUID,
  request: SimulationRequest | None = None,
  db: Annotated[Any, Depends(get_db)] = None,
) -> SimulationResponse:
  """Simulate a protocol using graph replay.

  This endpoint provides backend simulation for browser-mode fallback.
  It replays the computation graph with state tracking to detect violations
  like missing tips, incorrect deck placement, or liquid handling errors.

  The simulation uses boolean-level state tracking which catches:
  - Tips not loaded before aspiration
  - Resources not on deck
  - Liquid operations on empty wells

  This is useful when the browser can't run Pyodide-based simulation
  directly, or when you want to use the backend's full simulation
  capabilities.

  Returns clear error messages to help fix protocol issues.
  """
  # Fetch protocol definition
  protocol = await db.get(FunctionProtocolDefinitionOrm, accession_id)
  if not protocol:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Protocol definition {accession_id} not found",
    )

  # Get computation graph
  graph_dict = None
  if request and request.computation_graph:
    graph_dict = request.computation_graph
  elif protocol.computation_graph_json:
    graph_dict = protocol.computation_graph_json
  else:
    return SimulationResponse(
      passed=False,
      errors=[
        f"No computation graph available for protocol '{protocol.name}'. "
        "The protocol may not have been analyzed yet. "
        "Run protocol discovery to extract the computation graph."
      ],
      replay_mode="graph",
    )

  # Run graph replay
  try:
    engine = GraphReplayEngine()
    result: GraphReplayResult = engine.replay(graph_dict)

    # Convert violations to response format
    violations = [
      SimulationViolationResponse(
        operation_id=v.operation_id,
        operation_index=v.operation_index,
        method_name=v.method_name,
        receiver=v.receiver,
        violation_type=v.violation_type,
        message=v.message,
        suggested_fix=v.suggested_fix,
        line_number=v.line_number,
      )
      for v in result.violations
    ]

    return SimulationResponse(
      passed=result.passed,
      violations=violations,
      operations_executed=result.operations_executed,
      replay_mode=result.replay_mode,
      errors=result.errors,
      final_state_summary=result.final_state_summary,
    )

  except Exception as e:
    # Return clear error for debugging
    return SimulationResponse(
      passed=False,
      errors=[
        f"Simulation failed with error: {type(e).__name__}: {e!s}. "
        "This may indicate an invalid computation graph or internal error."
      ],
      replay_mode="graph",
    )


@router.get(
  "/definitions/{accession_id}/simulation-status",
  response_model=dict[str, Any],
  status_code=status.HTTP_200_OK,
  tags=["Protocol Simulation"],
)
async def get_simulation_status(
  accession_id: UUID,
  db: Annotated[Any, Depends(get_db)] = None,
) -> dict[str, Any]:
  """Get simulation status and cached results for a protocol.

  Returns information about:
  - Whether simulation results are cached
  - Cache validity (version, timestamp)
  - Summary of cached results if available
  """
  protocol = await db.get(FunctionProtocolDefinitionOrm, accession_id)
  if not protocol:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Protocol definition {accession_id} not found",
    )

  has_simulation = protocol.simulation_result_json is not None
  has_graph = protocol.computation_graph_json is not None
  has_bytecode = protocol.cached_bytecode is not None

  result: dict[str, Any] = {
    "protocol_name": protocol.name,
    "protocol_fqn": protocol.fqn,
    "has_simulation_cache": has_simulation,
    "has_computation_graph": has_graph,
    "has_bytecode_cache": has_bytecode,
  }

  if has_simulation:
    result["simulation_version"] = protocol.simulation_version
    result["simulation_cached_at"] = (
      protocol.simulation_cached_at.isoformat() if protocol.simulation_cached_at else None
    )
    # Include summary from cached result
    if protocol.simulation_result_json:
      cached = protocol.simulation_result_json
      result["cached_result_summary"] = {
        "passed": cached.get("passed", False),
        "violation_count": len(cached.get("violations", [])),
        "failure_mode_count": len(cached.get("failure_modes", [])),
        "level": cached.get("level", "unknown"),
      }

  if has_bytecode:
    result["bytecode_python_version"] = protocol.bytecode_python_version
    result["bytecode_cache_version"] = protocol.bytecode_cache_version
    result["bytecode_cached_at"] = (
      protocol.bytecode_cached_at.isoformat() if protocol.bytecode_cached_at else None
    )

  return result
