"""API Endpoints for Outputs and Well Data Outputs."""

from fastapi import APIRouter

from praxis.backend.api.utils.crud_router_factory import create_crud_router
from praxis.backend.models.orm.outputs import FunctionDataOutputOrm, WellDataOutputOrm
from praxis.backend.models.pydantic_internals.outputs import (
  FunctionDataOutputCreate,
  FunctionDataOutputResponse,
  FunctionDataOutputUpdate,
  WellDataOutputCreate,
  WellDataOutputResponse,
  WellDataOutputUpdate,
)
from praxis.backend.services.outputs import FunctionDataOutputCRUDService
from praxis.backend.services.well_outputs import WellDataOutputCRUDService

router = APIRouter()

router.include_router(
  create_crud_router(
    service=FunctionDataOutputCRUDService(FunctionDataOutputOrm),
    prefix="/outputs",
    tags=["Function Data Outputs"],
    create_schema=FunctionDataOutputCreate,
    update_schema=FunctionDataOutputUpdate,
    response_schema=FunctionDataOutputResponse,
  ),
)

router.include_router(
  create_crud_router(
    service=WellDataOutputCRUDService(WellDataOutputOrm),
    prefix="/well-outputs",
    tags=["Well Data Outputs"],
    create_schema=WellDataOutputCreate,
    update_schema=WellDataOutputUpdate,
    response_schema=WellDataOutputResponse,
  ),
)
