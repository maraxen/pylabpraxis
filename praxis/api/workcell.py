import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from ..utils.db import db
from ..workcell import Workcell, WorkcellView
from ..protocol import WorkcellAssets
from ..core.orchestrator import Orchestrator
from ..configure import PraxisConfiguration
from .dependencies import get_orchestrator

router = APIRouter()

config = PraxisConfiguration("praxis.ini")


# Asset request/response models
class WorkcellAssetRequest(BaseModel):
    """Request model for matching assets to requirements."""

    protocol_name: str
    required_assets: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AssetMatchResponse(BaseModel):
    """Response model for matched assets."""

    asset_name: str
    asset_type: str
    compatibility_score: float
    metadata: Dict[str, Any]


class WorkcellStateResponse(BaseModel):
    """Response model for workcell state."""

    assets: Dict[str, Dict[str, Any]]
    running_protocols: List[str]
    available_resources: List[str]


@router.get("/state", response_model=WorkcellStateResponse)
async def get_workcell_state(orchestrator: Orchestrator = Depends(get_orchestrator)):
    """Get current workcell state including assets and protocols."""
    if not orchestrator._main_workcell:
        raise HTTPException(status_code=503, detail="Workcell not initialized")

    try:
        return WorkcellStateResponse(
            assets=orchestrator._main_workcell._asset_states,
            running_protocols=orchestrator.get_running_protocols(),
            available_resources=[
                asset
                for asset in orchestrator._main_workcell.asset_ids
                if not orchestrator._main_workcell.is_asset_in_use(asset)
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match_assets")
async def match_assets_to_requirements(
    requirements: WorkcellAssetRequest,
    orchestrator: Orchestrator = Depends(get_orchestrator),
) -> Dict[str, List[AssetMatchResponse]]:
    """Match required assets to available assets in database."""
    try:
        matches = await orchestrator.match_assets_to_requirements(requirements.dict())
        return {
            asset_name: [AssetMatchResponse(**match) for match in asset_matches]
            for asset_name, asset_matches in matches.items()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to match assets: {str(e)}")


@router.post("/validate_configuration")
async def validate_configuration(
    config: Dict[str, Any], orchestrator: Orchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """Validate a complete protocol configuration."""
    try:
        result = await orchestrator.validate_configuration(config)
        if not result["valid"]:
            return {"valid": False, "errors": result["errors"], "config": config}
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Configuration validation failed: {str(e)}"
        )


@router.post("/release/{protocol_name}")
async def release_workcell_view(
    protocol_name: str, orchestrator: Orchestrator = Depends(get_orchestrator)
):
    """Release a protocol's workcell view."""
    try:
        await orchestrator.release_workcell_view(protocol_name)
        return {
            "status": "success",
            "message": f"Released workcell view for {protocol_name}",
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to release workcell view: {str(e)}"
        )
