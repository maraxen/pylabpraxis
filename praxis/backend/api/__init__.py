"""API module for Praxis.

This module contains the FastAPI application and its routes.
It initializes the application, sets up middleware, and includes routers for
different API endpoints.
"""

from praxis.backend.api.function_data_outputs import (
  router as function_data_outputs_router,
)
from praxis.backend.api.resources import router as assets_router
from praxis.backend.api.workcell_api import router as workcell_router

__all__ = [
  "assets_router",
  "function_data_outputs_router",
  "workcell_router",
]
