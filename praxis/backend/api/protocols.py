"""Protocol API endpoints.

This file contains the FastAPI router for all protocol-related endpoints,
including protocol definitions, protocol runs, and protocol execution.
"""

from functools import partial
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Import dependencies from the local 'api' package
from praxis.backend.api.dependencies import get_db

# Import all necessary Pydantic models from the central models package
from praxis.backend.models import (
  FunctionProtocolDefinitionOrm,
  ProtocolDefinitionFilters,
  ProtocolRunOrm,
  ProtocolRunStatusEnum,
  ProtocolStartRequest,
  SearchFilters,
)

# Import the service layer, aliased as 'svc' for convenience
from praxis.backend.services.protocols import (
  protocol_definition_service,
  protocol_run_service,
)
from praxis.backend.utils.accession_resolver import get_accession_id_from_accession
from praxis.backend.utils.errors import PraxisAPIError
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

# Initialize the FastAPI router
router = APIRouter()

log_protocol_api_errors = partial(
  log_async_runtime_errors, logger_instance=logger, raises_exception=PraxisAPIError,
)

protocol_definition_accession_resolver = partial(
  get_accession_id_from_accession,
  get_func=protocol_definition_service.get,
  get_by_name_func=protocol_definition_service.get_by_name,
  entity_type_name="Protocol Definition",
)

protocol_run_accession_resolver = partial(
  get_accession_id_from_accession,
  get_func=protocol_run_service.get,
  get_by_name_func=protocol_run_service.get_by_name,
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
  response_model=list[FunctionProtocolDefinitionOrm],
  tags=["Protocol Definitions"],
)
async def list_protocol_definitions(
  filters: Annotated[ProtocolDefinitionFilters, Depends()],
  db: Annotated[AsyncSession, Depends(get_db)],
):
  """List all available protocol definitions."""
  return await protocol_definition_service.get_multi(
    db=db,
    filters=filters.search_filters,
    source_name=filters.source_name,
    is_top_level=filters.is_top_level,
    category=filters.category,
    tags=filters.tags,
    include_deprecated=filters.include_deprecated,
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
async def get_protocol_definition(
    accession: str, db: Annotated[AsyncSession, Depends(get_db)],
):
  """Retrieve a protocol definition by accession ID or name."""
  definition_id = await protocol_definition_accession_resolver(
    db=db, accession=accession,
  )

  db_definition = await protocol_definition_service.get(
    db, id=definition_id,
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
  db: Annotated[AsyncSession, Depends(get_db)],
  version: str | None = None,
  source_name: str | None = None,
  commit_hash: str | None = None,
):
  """Retrieve detailed protocol definition by name with optional filters."""
  db_definition = await protocol_definition_service.get_by_name(
    db, name=name, version=version, source_name=source_name, commit_hash=commit_hash,
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
  protocol_start: ProtocolStartRequest,
  db: Annotated[AsyncSession, Depends(get_db)],
):
  """Create a new protocol run."""
  if not protocol_start.protocol_definition_accession_id:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="protocol_definition_accession_id is required",
    )

  try:
    # Let the service layer handle UUID generation
    created_run = await protocol_run_service.create(
      db=db,
      obj_in=protocol_start,
    )
    return created_run
  except ValueError as e:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST, detail=str(e),
    ) from e


@log_protocol_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to list protocol runs: ",
  suffix="",
)
@router.get(
  "/runs",
  response_model=list[ProtocolRunOrm],
  tags=["Protocol Runs"],
)
async def list_protocol_runs(
  db: Annotated[AsyncSession, Depends(get_db)],
  filters: Annotated[SearchFilters, Depends()],
  protocol_definition_accession_id: UUID | None = None,
  protocol_name: str | None = None,
  status: ProtocolRunStatusEnum | None = None,
):
  """List all protocol runs with optional filtering."""
  return await protocol_run_service.get_multi(
    db=db,
    filters=filters,
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
async def get_protocol_run(accession: str, db: Annotated[AsyncSession, Depends(get_db)]):
  """Retrieve a protocol run by accession ID or name."""
  run_id = await protocol_run_accession_resolver(db=db, accession=accession)

  db_run = await protocol_run_service.get(db, id=run_id)
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
  db: Annotated[AsyncSession, Depends(get_db)],
  output_data_json: str | None = None,
  final_state_json: str | None = None,
):
  """Update the status of a protocol run."""
  run_id = await protocol_run_accession_resolver(db=db, accession=accession)

  try:
    updated_run = await protocol_run_service.update_protocol_run_status(
      db=db,
      protocol_run_accession_id=run_id,
      new_status=new_status,
      output_data_json=output_data_json,
      final_state_json=final_state_json,
    )
    if not updated_run:
      raise HTTPException(
        status_code=404, detail=f"Protocol run '{accession}' not found.",
      )
    return updated_run
  except ValueError as e:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST, detail=str(e),
    ) from e
