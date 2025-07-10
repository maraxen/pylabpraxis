# filepath: praxis/backend/api/outputs.py
#
# This file contains the FastAPI router for all function data output endpoints,
# including data outputs from protocol function calls and plate visualization data.

from fastapi import APIRouter

from praxis.backend.api.utils.crud_router_factory import create_crud_router
from praxis.backend.models.orm.outputs import FunctionDataOutputOrm, WellDataOutputOrm
from praxis.backend.models.pydantic.outputs import (
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
    )
)

router.include_router(
    create_crud_router(
        service=WellDataOutputCRUDService(WellDataOutputOrm),
        prefix="/well-outputs",
        tags=["Well Data Outputs"],
        create_schema=WellDataOutputCreate,
        update_schema=WellDataOutputUpdate,
        response_schema=WellDataOutputResponse,
    )
)
