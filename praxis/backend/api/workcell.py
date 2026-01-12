"""Workcell API endpoints.

This file contains the FastAPI router for workcell-related endpoints,
including workcell CRUD operations and legacy orchestrator endpoints.
"""

from fastapi import APIRouter

from praxis.backend.api.utils.crud_router_factory import create_crud_router
from praxis.backend.models.domain.workcell import (
  WorkcellCreate,
  WorkcellRead,
  WorkcellUpdate,
)
from praxis.backend.models.domain.workcell import Workcell
from praxis.backend.services.workcell import WorkcellService

router = APIRouter()

router.include_router(
  create_crud_router(
    service=WorkcellService(Workcell),
    prefix="/",
    tags=["Workcells"],
    create_schema=WorkcellCreate,
    update_schema=WorkcellUpdate,
    read_schema=WorkcellRead,
  ),
)
