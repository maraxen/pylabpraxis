"""Protocol API endpoints.

This file contains the FastAPI router for all protocol-related endpoints,
including protocol definitions, protocol runs, and protocol execution.
"""

from fastapi import APIRouter

from praxis.backend.api.utils.crud_router_factory import create_crud_router
from praxis.backend.models.orm.protocol import FunctionProtocolDefinitionOrm, ProtocolRunOrm
from praxis.backend.models.pydantic.protocol import (
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

router.include_router(
  create_crud_router(
    service=ProtocolRunService(ProtocolRunOrm),
    prefix="/runs",
    tags=["Protocol Runs"],
    create_schema=ProtocolRunCreate,
    update_schema=ProtocolRunUpdate,
    response_schema=ProtocolRunResponse,
  ),
)
