"""Protocol API endpoints.

This file contains the FastAPI router for all protocol-related endpoints,
including protocol definitions, protocol runs, and protocol execution.
"""

from functools import partial
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Import the service layer, aliased as 'svc' for convenience
import praxis.backend.services as svc

# Import dependencies from the local 'api' package
from praxis.backend.api.dependencies import get_db

# Import all necessary Pydantic models from the central models package
from praxis.backend.models import (
  FunctionProtocolDefinitionOrm,
  ProtocolRunOrm,
  ProtocolRunStatusEnum,
  ProtocolStartRequest,
)
from praxis.backend.utils.accession_resolver import get_accession_id_from_accession
from praxis.backend.utils.errors import PraxisAPIError
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

# Initialize the FastAPI router
router = APIRouter()

log_protocol_api_errors = partial(
  log_async_runtime_errors, logger_instance=logger, raises_exception=PraxisAPIError
)

protocol_definition_accession_resolver = partial(
  get_accession_id_from_accession,
  get_func=svc.read_protocol_definition,
  get_by_name_func=svc.read_protocol_definition_by_name,
  entity_type_name="Protocol Definition",
)

protocol_run_accession_resolver = partial(
  get_accession_id_from_accession,
  get_func=svc.read_protocol_run,
  get_by_name_func=svc.read_protocol_run_by_name,
  entity_type_name="Protocol Run",
)

# Protocol Definition Endpoints


@log_protocol_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to list protocol definitions: ",
  suffix="",
)
@router.get(
  "/definitions",
  response_model=List[FunctionProtocolDefinitionOrm],
  tags=["Protocol Definitions"],
)
async def list_protocol_definitions(
  db: AsyncSession = Depends(get_db),
  limit: int = 100,
  offset: int = 0,
  source_name: Optional[str] = None,
  is_top_level: Optional[bool] = None,
  category: Optional[str] = None,
  tags: Optional[List[str]] = None,
  include_deprecated: bool = False,
):
  """List all available protocol definitions."""
  return await svc.list_protocol_definitions(
    db,
    limit=limit,
    offset=offset,
    source_name=source_name,
    is_top_level=is_top_level,
    category=category,
    tags=tags,
    include_deprecated=include_deprecated,
  )


@log_protocol_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to get protocol definition: ",
  suffix="",
)
@router.get(
  "/definitions/{accession}",
  response_model=FunctionProtocolDefinitionOrm,
  tags=["Protocol Definitions"],
)
async def get_protocol_definition(accession: str, db: AsyncSession = Depends(get_db)):
  """Retrieve a protocol definition by accession ID or name."""
  definition_id = await protocol_definition_accession_resolver(
    db=db, accession=accession
  )

  db_definition = await svc.read_protocol_definition(
    db, definition_accession_id=definition_id
  )
  if db_definition is None:
    raise HTTPException(status_code=404, detail="Protocol definition not found")
  return db_definition


@log_protocol_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to get protocol definition details: ",
  suffix="",
)
@router.get(
  "/definitions/details/{name}",
  response_model=FunctionProtocolDefinitionOrm,
  tags=["Protocol Definitions"],
)
async def get_protocol_definition_details(
  name: str,
  db: AsyncSession = Depends(get_db),
  version: Optional[str] = None,
  source_name: Optional[str] = None,
  commit_hash: Optional[str] = None,
):
  """Retrieve detailed protocol definition by name with optional filters."""
  db_definition = await svc.read_protocol_definition_by_name(
    db, name=name, version=version, source_name=source_name, commit_hash=commit_hash
  )
  if db_definition is None:
    raise HTTPException(status_code=404, detail="Protocol definition not found")
  return db_definition


# Protocol Run Endpoints


@log_protocol_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to create protocol run: ",
  suffix="",
)
@router.post(
  "/runs",
  response_model=ProtocolRunOrm,
  status_code=status.HTTP_201_CREATED,
  tags=["Protocol Runs"],
)
async def create_protocol_run(
  protocol_start: ProtocolStartRequest, db: AsyncSession = Depends(get_db)
):
  """Create a new protocol run."""
  if not protocol_start.protocol_definition_accession_id:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="protocol_definition_accession_id is required",
    )

  try:
    # Let the service layer handle UUID generation
    created_run = await svc.create_protocol_run(
      db=db,
      top_level_protocol_definition_accession_id=(
        protocol_start.protocol_definition_accession_id
      ),
      input_parameters_json=(
        str(protocol_start.parameters) if protocol_start.parameters else None
      ),
    )
    return created_run
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_protocol_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to list protocol runs: ",
  suffix="",
)
@router.get(
  "/runs",
  response_model=List[ProtocolRunOrm],
  tags=["Protocol Runs"],
)
async def list_protocol_runs(
  db: AsyncSession = Depends(get_db),
  limit: int = 100,
  offset: int = 0,
  protocol_definition_accession_id: Optional[UUID] = None,
  protocol_name: Optional[str] = None,
  status: Optional[ProtocolRunStatusEnum] = None,
):
  """List all protocol runs with optional filtering."""
  return await svc.list_protocol_runs(
    db,
    limit=limit,
    offset=offset,
    protocol_definition_accession_id=protocol_definition_accession_id,
    protocol_name=protocol_name,
    status=status,
  )


@log_protocol_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to get protocol run: ",
  suffix="",
)
@router.get(
  "/runs/{accession}",
  response_model=ProtocolRunOrm,
  tags=["Protocol Runs"],
)
async def get_protocol_run(accession: str, db: AsyncSession = Depends(get_db)):
  """Retrieve a protocol run by accession ID or name."""
  run_id = await protocol_run_accession_resolver(db=db, accession=accession)

  db_run = await svc.read_protocol_run(db, run_accession_id=run_id)
  if db_run is None:
    raise HTTPException(status_code=404, detail="Protocol run not found")
  return db_run


@log_protocol_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to update protocol run status: ",
  suffix="",
)
@router.patch(
  "/runs/{accession}/status",
  response_model=ProtocolRunOrm,
  tags=["Protocol Runs"],
)
async def update_protocol_run_status(
  accession: str,
  new_status: ProtocolRunStatusEnum,
  output_data_json: Optional[str] = None,
  final_state_json: Optional[str] = None,
  db: AsyncSession = Depends(get_db),
):
  """Update the status of a protocol run."""
  run_id = await protocol_run_accession_resolver(db=db, accession=accession)

  try:
    updated_run = await svc.update_protocol_run_status(
      db=db,
      protocol_run_accession_id=run_id,
      new_status=new_status,
      output_data_json=output_data_json,
      final_state_json=final_state_json,
    )
    if not updated_run:
      raise HTTPException(
        status_code=404, detail=f"Protocol run '{accession}' not found."
      )
    return updated_run
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
