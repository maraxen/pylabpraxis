"""API module for Praxis.
This module contains the FastAPI application and its routes.
It initializes the application, sets up middleware, and includes routers for different API
endpoints.
"""
from praxis.api.assets import router as assets_router
from praxis.api.protocols import router as protocols_router

__all__ = [
    "assets_router",
    "protocols_router",
]
