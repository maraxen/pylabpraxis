"""Synchronization API for PyLabRobot Definitions."""

from typing import TYPE_CHECKING

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

if TYPE_CHECKING:
  from praxis.backend.services.discovery_service import DiscoveryService

router = APIRouter()


@router.post("/sync-all", status_code=status.HTTP_200_OK)
async def sync_all_definitions(
  request: Request,
) -> JSONResponse:
  """Synchronize all PyLabRobot type definitions and protocol definitions with the database.

  This endpoint triggers a full discovery and synchronization process for all
  known PyLabRobot resources, machines, decks, and protocol definitions.
  It should be used to ensure the database reflects the latest available
  definitions from the connected PyLabRobot environment and protocol sources.
  """
  discovery_service: DiscoveryService = request.app.state.discovery_service

  try:
    await discovery_service.discover_and_sync_all_definitions(
      protocol_search_paths=request.app.state.praxis_config.all_protocol_source_paths,
    )
    return JSONResponse(
      status_code=status.HTTP_200_OK,
      content={"message": "Discovery and synchronization initiated successfully."},
    )
  except Exception as e:
    return JSONResponse(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      content={"message": f"Failed to initiate discovery and synchronization: {e}"},
    )
