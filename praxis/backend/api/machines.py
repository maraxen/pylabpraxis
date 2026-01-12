"""Machine API endpoints.

This file contains the FastAPI router for all machine-related endpoints,
including machine creation, retrieval, updates, and deletion.
"""

from functools import partial
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.api.dependencies import get_db
from praxis.backend.api.utils.crud_router_factory import create_crud_router
from praxis.backend.models.domain.machine import (
  MachineCreate,
  MachineDefinitionCreate,
  MachineDefinitionRead,
  MachineDefinitionUpdate,
  MachineRead,
  MachineUpdate,
)
from praxis.backend.models.orm.machine import MachineDefinitionOrm, MachineOrm, MachineStatusEnum
from praxis.backend.services.machine import MachineService
from praxis.backend.services.machine_type_definition import MachineTypeDefinitionCRUDService
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


@router.get(
  "/definitions/facets",
  tags=["Machine Definitions"],
  summary="Get facet values with counts for machine filtering",
  response_model=dict[str, list[dict[str, Any]]],
)
async def get_machine_definition_facets(
  db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, list[dict[str, Any]]]:
  """Return unique values and counts for filterable machine definition fields.

  Returns facets for: machine_category, manufacturer.
  """
  from sqlalchemy import func, select

  # machine_definition_orm is imported above, but we keep local import if needed or use top-level
  # We'll use the top-level import now.

  facets: dict[str, list[dict[str, Any]]] = {}

  # Machine category facet (enum values)
  stmt = (
    select(MachineDefinitionOrm.machine_category, func.count().label("count"))
    .where(MachineDefinitionOrm.machine_category.isnot(None))
    .group_by(MachineDefinitionOrm.machine_category)
    .order_by(func.count().desc())
  )
  result = await db.execute(stmt)
  rows = result.all()
  facets["machine_category"] = [{"value": row[0].value, "count": row[1]} for row in rows]

  # Manufacturer facet
  stmt = (
    select(MachineDefinitionOrm.manufacturer, func.count().label("count"))
    .where(MachineDefinitionOrm.manufacturer.isnot(None))
    .group_by(MachineDefinitionOrm.manufacturer)
    .order_by(func.count().desc())
  )
  result = await db.execute(stmt)
  rows = result.all()
  facets["manufacturer"] = [{"value": row[0], "count": row[1]} for row in rows]

  return facets


# Include Machine Definition CRUD Router
# MUST be included after specific /definitions endpoints (like /facets)
router.include_router(
  create_crud_router(
    service=MachineTypeDefinitionCRUDService(MachineDefinitionOrm),
    prefix="/definitions",
    tags=["Machine Definitions"],
    create_schema=MachineDefinitionCreate,
    update_schema=MachineDefinitionUpdate,
    read_schema=MachineDefinitionRead,
  ),
)


router.include_router(
  create_crud_router(
    service=machine_service,
    prefix="/",
    tags=["Machines"],
    create_schema=MachineCreate,
    update_schema=MachineUpdate,
    read_schema=MachineRead,
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
  response_model=MachineRead,
  tags=["Machines"],
)
async def update_machine_status(
  accession: str,
  new_status: MachineStatusEnum,
  db: Annotated[AsyncSession, Depends(get_db)],
  status_details: str | None = None,
  current_protocol_run_accession_id: UUID | None = None,
) -> MachineRead:
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
    return MachineRead.model_validate(updated_machine)
