"""API Endpoints for Outputs and Well Data Outputs."""

from fastapi import APIRouter

from praxis.backend.api.utils.crud_router_factory import create_crud_router
from praxis.backend.models.domain.outputs import (
  FunctionDataOutputCreate,
  FunctionDataOutputRead,
  FunctionDataOutputUpdate,
  WellDataOutputCreate,
  WellDataOutputRead,
  WellDataOutputUpdate,
)
from praxis.backend.models.domain.outputs import FunctionDataOutput, WellDataOutput
from praxis.backend.services.outputs import FunctionDataOutputCRUDService
from praxis.backend.services.well_outputs import WellDataOutputCRUDService

router = APIRouter()

router.include_router(
  create_crud_router(
    service=FunctionDataOutputCRUDService(FunctionDataOutput),
    prefix="/outputs",
    tags=["Function Data Outputs"],
    create_schema=FunctionDataOutputCreate,
    update_schema=FunctionDataOutputUpdate,
    read_schema=FunctionDataOutputRead,
  ),
)

router.include_router(
  create_crud_router(
    service=WellDataOutputCRUDService(WellDataOutput),
    prefix="/well-outputs",
    tags=["Well Data Outputs"],
    create_schema=WellDataOutputCreate,
    update_schema=WellDataOutputUpdate,
    read_schema=WellDataOutputRead,
  ),
)
