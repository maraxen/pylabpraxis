"""FastAPI router for all resource-related endpoints.

This module defines endpoints for managing resource definitions and resources,
including creation, retrieval, updating, and deletion. It uses the service layer
to interact with the database and handle business logic.
"""

from fastapi import APIRouter

from praxis.backend.api.utils.crud_router_factory import create_crud_router
from praxis.backend.models.orm.resource import ResourceDefinitionOrm, ResourceOrm
from praxis.backend.models.pydantic.resource import (
  ResourceCreate,
  ResourceDefinitionCreate,
  ResourceDefinitionResponse,
  ResourceDefinitionUpdate,
  ResourceResponse,
  ResourceUpdate,
)
from praxis.backend.services.resource import ResourceService
from praxis.backend.services.resource_type_definition import ResourceTypeDefinitionCRUDService

router = APIRouter()

router.include_router(
  create_crud_router(
    service=ResourceService(ResourceOrm),
    prefix="/",
    tags=["Resources"],
    create_schema=ResourceCreate,
    update_schema=ResourceUpdate,
    response_schema=ResourceResponse,
  ),
)

router.include_router(
  create_crud_router(
    service=ResourceTypeDefinitionCRUDService(ResourceDefinitionOrm),
    prefix="/definitions",
    tags=["Resource Definitions"],
    create_schema=ResourceDefinitionCreate,
    update_schema=ResourceDefinitionUpdate,
    response_schema=ResourceDefinitionResponse,
  ),
)
