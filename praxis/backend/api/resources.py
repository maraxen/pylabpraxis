# <filename>praxis/backend/api/resources.py</filename>
#
# This file contains the FastAPI router for all resource-related endpoints,
# including resource definitions (catalog) and resource instances.

import datetime
from functools import partial
from typing import Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Import the service layer, aliased as 'svc' for convenience
import praxis.backend.services as svc

# Import dependencies from the local 'api' package
from praxis.backend.api.dependencies import get_db

# Import all necessary Pydantic models from the central models package
from praxis.backend.models import (
  ResourceDefinitionCreate,
  ResourceDefinitionResponse,
  ResourceDefinitionUpdate,
  ResourceInstanceCreate,
  ResourceInstanceResponse,
  ResourceInstanceUpdate,
)
from praxis.backend.utils.accession_resolver import get_accession_id_from_accession
from praxis.backend.utils.errors import PraxisAPIError
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

# Initialize the FastAPI router
router = APIRouter()

log_resource_api_errors = partial(
  log_async_runtime_errors, logger_instance=logger, raises_exception=PraxisAPIError
)

resource_instance_resolve_accession = partial(
  get_accession_id_from_accession,
  get_func=svc.read_resource_instance,
  get_by_name_func=svc.read_resource_instance_by_name,
  entity_type_name="Resource Instance",
)


@log_resource_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to create resource definition: ",
  suffix="",
)
@router.post(
  "/definitions",
  response_model=ResourceDefinitionResponse,
  status_code=status.HTTP_201_CREATED,
  tags=["Resource Definitions"],
)
async def create_resource_definition(
  definition: ResourceDefinitionCreate, db: AsyncSession = Depends(get_db)
):
  """Create a new resource definition in the catalog."""
  try:
    created_def = await svc.create_resource_definition(db=db, **definition.model_dump())
    return created_def
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_resource_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to get resource definition: ",
  suffix="",
)
@router.get(
  "/definitions/{name}",
  response_model=ResourceDefinitionResponse,
  tags=["Resource Definitions"],
)
async def get_resource_definition(name: str, db: AsyncSession = Depends(get_db)):
  """Retrieve a resource definition by name."""
  db_def = await svc.read_resource_definition(db, name)
  if db_def is None:
    raise HTTPException(status_code=404, detail="Resource definition not found")
  return db_def


@log_resource_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to list resource definitions: ",
  suffix="",
)
@router.get(
  "/definitions",
  response_model=List[ResourceDefinitionResponse],
  tags=["Resource Definitions"],
)
async def list_resource_definitions(
  db: AsyncSession = Depends(get_db), limit: int = 100, offset: int = 0
):
  """List all available resource definitions."""
  return await svc.list_resource_definitions(db, limit=limit, offset=offset)


@log_resource_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to update resource definition: ",
  suffix="",
)
@router.put(
  "/definitions/{name}",
  response_model=ResourceDefinitionResponse,
  tags=["Resource Definitions"],
)
async def update_resource_definition(
  name: str,
  definition_update: ResourceDefinitionUpdate,
  db: AsyncSession = Depends(get_db),
):
  """Update an existing resource definition."""
  update_data = definition_update.model_dump(exclude_unset=True)
  try:
    updated_def = await svc.update_resource_definition(db=db, name=name, **update_data)
    if not updated_def:
      raise HTTPException(
        status_code=404, detail=f"Resource definition '{name}' not found."
      )
    return updated_def
  except ValueError as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@log_resource_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to delete resource definition: ",
  suffix="",
)
@router.delete(
  "/definitions/{name}",
  status_code=status.HTTP_204_NO_CONTENT,
  tags=["Resource Definitions"],
)
async def delete_resource_definition(name: str, db: AsyncSession = Depends(get_db)):
  """Delete a resource definition."""
  success = await svc.delete_resource_definition(db, name)
  if not success:
    raise HTTPException(
      status_code=404, detail=f"Resource definition '{name}' not found."
    )
  return None


# --- Resource Instance Endpoints ---


@log_resource_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to create resource instance: ",
  suffix="",
)
@router.post(
  "/",
  response_model=ResourceInstanceResponse,
  status_code=status.HTTP_201_CREATED,
  tags=["Resources"],
)
async def create_resource_instance(
  request: ResourceInstanceCreate, db: AsyncSession = Depends(get_db)
):
  """Create a new resource instance."""
  try:
    if request.resource_definition_accession_id is None:
      definition_orm = await svc.read_resource_definition_by_fqn(
        db=db, python_fqn=request.python_fqn
      )
      if not definition_orm:
        raise HTTPException(
          status_code=404,
          detail=f"Resource definition with FQN '{request.python_fqn}' not found.",
        )
      request.resource_definition_accession_id = definition_orm.accession_id
    resource_orm = await svc.create_resource_instance(
      db=db,
      python_fqn=request.python_fqn,
      resource_definition_accession_id=request.resource_definition_accession_id,
      user_assigned_name=request.user_assigned_name,
    )
    return ResourceInstanceResponse.model_validate(resource_orm)

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to create resource: {str(e)}")


@log_resource_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to list resource instances: ",
  suffix="",
)
@router.get(
  "/{name}",
  response_model=ResourceInstanceResponse,
  tags=["Resources"],
)
async def get_resource_instance(
  accession: str | UUID, db: AsyncSession = Depends(get_db)
):
  """Retrieve a resource instance."""
  try:
    accession_id = await resource_instance_resolve_accession(accession=accession, db=db)
    resource = await svc.read_resource_instance(db, instance_accession_id=accession_id)
    if not resource:
      raise HTTPException(status_code=404, detail="Resource not found")
    return ResourceInstanceResponse.model_validate(resource)
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to get resource: {str(e)}")


@log_resource_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to list resource instances: ",
  suffix="",
)
@router.put(
  "/{instance_accession_id}",
  response_model=ResourceInstanceResponse,
  tags=["Resources"],
)
async def update_resource(
  accession: str | UUID,
  request: ResourceInstanceUpdate,
  db: AsyncSession = Depends(get_db),
):
  """Update an existing resource instance."""
  try:
    accession_id = await resource_instance_resolve_accession(accession=accession, db=db)
    resource = await svc.read_resource_instance(db, instance_accession_id=accession_id)
    if resource is None:
      raise HTTPException(status_code=404, detail="Resource not found")
    update_data = request.model_dump(exclude_unset=True)
    updated_resource = await svc.update_resource_instance(
      db=db, instance_accession_id=accession_id, **update_data
    )
    return ResourceInstanceResponse.model_validate(updated_resource)

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to update resource: {str(e)}")


@log_resource_api_errors(
  exception_type=HTTPException,
  raises=True,
  prefix="Failed to delete resource instance: ",
  suffix="",
)
@router.delete(
  "/{instance_accession_id}",
  status_code=status.HTTP_204_NO_CONTENT,
  tags=["Resources"],
)
async def delete_resource(accession: str | UUID, db: AsyncSession = Depends(get_db)):
  """Delete a resource instance by name or ID."""
  try:
    success = False
    accession_id = await resource_instance_resolve_accession(accession=accession, db=db)
    resource = await svc.read_resource_instance(db, instance_accession_id=accession_id)
    if not resource:
      raise HTTPException(status_code=404, detail="Resource not found")
    success = await svc.delete_resource_instance(
      db, instance_accession_id=resource.accession_id
    )
    if not success:
      raise HTTPException(status_code=404, detail="Resource not found")
    return None
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Failed to delete resource: {str(e)}")
