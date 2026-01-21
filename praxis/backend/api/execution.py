from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from praxis.backend.core.protocol_execution_service import ProtocolExecutionService
from praxis.backend.api.container import get_protocol_execution_service

router = APIRouter()


@router.post("/runs/{run_id}/pause", status_code=204)
async def pause_run(
  run_id: UUID,
  execution_service: ProtocolExecutionService = Depends(get_protocol_execution_service),
):
  success = await execution_service.pause_protocol_run(run_id)
  if not success:
    raise HTTPException(status_code=500, detail="Failed to pause protocol run")


@router.post("/runs/{run_id}/resume", status_code=204)
async def resume_run(
  run_id: UUID,
  execution_service: ProtocolExecutionService = Depends(get_protocol_execution_service),
):
  success = await execution_service.resume_protocol_run(run_id)
  if not success:
    raise HTTPException(status_code=500, detail="Failed to resume protocol run")
