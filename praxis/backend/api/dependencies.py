from typing import Optional
from fastapi import HTTPException, Request
from ..core.orchestrator import Orchestrator


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
