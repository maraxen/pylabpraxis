"""Dependencies for FastAPI application."""

from collections.abc import AsyncGenerator

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.core.orchestrator import Orchestrator
from praxis.backend.core.workcell_runtime import (
  WorkcellRuntime,  # Added for get_workcell_runtime
)
from praxis.backend.utils.db import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
  """Dependency to get an async database session."""
  async with AsyncSessionLocal() as session:
    # Services are expected to handle their own commit/rollback.
    yield session


def get_orchestrator(request: Request) -> Orchestrator:
  """Get orchestrator instance from request state."""
  app = request.app
  orchestrator: Orchestrator | None = getattr(app.state, "orchestrator", None)
  if orchestrator is None:
    raise HTTPException(
      status_code=500,
      detail="Orchestrator not initialized. Application startup may have failed.",
    )
  return orchestrator


def get_workcell_runtime(request: Request) -> WorkcellRuntime:
  """Get WorkcellRuntime instance from request state."""
  app = request.app
  workcell_runtime: WorkcellRuntime | None = getattr(
    app.state,
    "workcell_runtime",
    None,
  )
  if workcell_runtime is None:
    raise HTTPException(
      status_code=500,
      detail="WorkcellRuntime not initialized. Application startup may have failed.",
    )
  return workcell_runtime


def get_protocol_execution_service(request: Request):
  """Get ProtocolExecutionService instance from request state."""
  from praxis.backend.core.protocol_execution_service import ProtocolExecutionService
  
  app = request.app
  execution_service: ProtocolExecutionService | None = getattr(
    app.state,
    "protocol_execution_service",
    None,
  )
  if execution_service is None:
    raise HTTPException(
      status_code=500,
      detail="ProtocolExecutionService not initialized. Application startup may have failed.",
    )
  return execution_service
