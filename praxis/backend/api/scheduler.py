# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument
"""FastAPI router for all scheduler-related endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.api.dependencies import get_db
from praxis.backend.api.utils.crud_router_factory import create_crud_router
from praxis.backend.models.enums import ScheduleStatusEnum
from praxis.backend.models.orm.schedule import ScheduleEntryOrm
from praxis.backend.models.pydantic_internals.scheduler import (
  ScheduleEntryCreate,
  ScheduleEntryResponse,
  ScheduleEntryUpdate,
  SchedulePriorityUpdateRequest,
)
from praxis.backend.services.scheduler import schedule_entry_service

router = APIRouter()

router.include_router(
  create_crud_router(
    service=schedule_entry_service,
    prefix="/entries",
    tags=["Scheduler"],
    create_schema=ScheduleEntryCreate,
    update_schema=ScheduleEntryUpdate,
    response_schema=ScheduleEntryResponse,
  ),
)


@router.put(
  "/{schedule_entry_accession_id}/status",
  response_model=ScheduleEntryResponse,
  status_code=status.HTTP_200_OK,
  tags=["Scheduler"],
)
async def update_status(
  schedule_entry_accession_id: UUID,
  status_update: ScheduleEntryUpdate,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> ScheduleEntryOrm:
  """Update the status of a schedule entry."""
  if status_update.status is None:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Status must be provided",
    )
  updated_entry = await schedule_entry_service.update_status(
    db=db,
    schedule_entry_accession_id=schedule_entry_accession_id,
    new_status=ScheduleStatusEnum(status_update.status.value),
    error_details=status_update.last_error_message,
  )
  if not updated_entry:
    raise HTTPException(status_code=404, detail="Schedule entry not found")
  return updated_entry


@router.put(
  "/{schedule_entry_accession_id}/priority",
  response_model=ScheduleEntryResponse,
  status_code=status.HTTP_200_OK,
  tags=["Scheduler"],
)
async def update_priority(
  schedule_entry_accession_id: UUID,
  priority_update: SchedulePriorityUpdateRequest,
  db: Annotated[AsyncSession, Depends(get_db)],
) -> ScheduleEntryOrm:
  """Update the priority of a schedule entry."""
  updated_entry = await schedule_entry_service.update_priority(
    db=db,
    schedule_entry_accession_id=schedule_entry_accession_id,
    new_priority=priority_update.new_priority,
    reason=priority_update.reason,
  )
  if not updated_entry:
    raise HTTPException(status_code=404, detail="Schedule entry not found")
  return updated_entry
