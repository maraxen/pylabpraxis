from typing import Optional, AsyncGenerator
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.core.orchestrator import Orchestrator
from praxis.backend.utils.db import AsyncSessionLocal
from praxis.backend.core.workcell_runtime import WorkcellRuntime # Added for get_workcell_runtime


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get an async database session."""
    async with AsyncSessionLocal() as session:
        # Services are expected to handle their own commit/rollback.
        yield session

def get_orchestrator(request: Request) -> Orchestrator:
    """Get orchestrator instance from request state."""
    app = request.app
    orchestrator: Optional[Orchestrator] = getattr(app.state, "orchestrator", None)
    if orchestrator is None:
        raise HTTPException(
            status_code=500,
            detail="Orchestrator not initialized. Application startup may have failed.",
        )
    return orchestrator

def get_workcell_runtime(request: Request) -> WorkcellRuntime:
    """Get WorkcellRuntime instance from request state."""
    app = request.app
    workcell_runtime: Optional[WorkcellRuntime] = getattr(app.state, "workcell_runtime", None)
    if workcell_runtime is None:
        raise HTTPException(
            status_code=500,
            detail="WorkcellRuntime not initialized. Application startup may have failed.",
        )
    return workcell_runtime
  