"""FastAPI router for all resource-related endpoints.

This module defines endpoints for managing resource definitions and resources,
including creation, retrieval, updating, and deletion. It uses the service layer
to interact with the database and handle business logic.
"""

from fastapi import APIRouter

from praxis.backend.api.utils.crud_router_factory import create_crud_router
from praxis.backend.models.orm.resource import ResourceDefinitionOrm
from praxis.backend.models.pydantic_internals.resource import (
  ResourceCreate,
  ResourceDefinitionCreate,
  ResourceDefinitionResponse,
  ResourceDefinitionUpdate,
  ResourceResponse,
  ResourceUpdate,
)
from praxis.backend.services.resource import resource_service
from praxis.backend.services.resource_type_definition import ResourceTypeDefinitionCRUDService

router = APIRouter()

# IMPORTANT: Include /definitions router BEFORE / router to ensure
# more specific routes are matched first
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

router.include_router(
  create_crud_router(
    service=resource_service,
    prefix="/",
    tags=["Resources"],
    create_schema=ResourceCreate,
    update_schema=ResourceUpdate,
    response_schema=ResourceResponse,
  ),
)
