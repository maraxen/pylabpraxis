from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from praxis.utils.db import db

router = APIRouter()


class AssetBase(BaseModel):
    name: str
    type: str
    metadata: dict = {}


class AssetResponse(AssetBase):
    is_available: bool
    description: Optional[str] = None


@router.get("/types/{asset_type}", response_model=List[AssetResponse])
async def list_assets_by_type(asset_type: str):
    """
    Get all assets of a specific type.
    Examples of asset_type: 'labware', 'machine', 'resource'
    """
    try:
        query = """
            SELECT
                name,
                type,
                metadata,
                is_available,
                metadata->>'description' as description
            FROM assets
            WHERE type LIKE $1
            ORDER BY name
        """
        assets = await db.fetch_all(query, f"%{asset_type}%")
        return assets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch assets: {str(e)}")


@router.get("/available/{asset_type}", response_model=List[AssetResponse])
async def list_available_assets_by_type(asset_type: str):
    """
    Get all available (unlocked) assets of a specific type
    """
    try:
        query = """
            SELECT
                name,
                type,
                metadata,
                is_available,
                metadata->>'description' as description
            FROM assets
            WHERE type LIKE $1
                AND is_available = true
                AND (lock_expires_at IS NULL OR lock_expires_at < CURRENT_TIMESTAMP)
            ORDER BY name
        """
        assets = await db.fetch_all(query, f"%{asset_type}%")
        return assets
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch available assets: {str(e)}"
        )


@router.get("/{asset_name}", response_model=AssetResponse)
async def get_asset_details(asset_name: str):
    """
    Get detailed information about a specific asset
    """
    asset = await db.get_asset(asset_name)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_name} not found")
    return asset


@router.get("/search/{query}", response_model=List[AssetResponse])
async def search_assets(query: str):
    """
    Search for assets by name or type
    """
    try:
        sql_query = """
            SELECT
                name,
                type,
                metadata,
                is_available,
                metadata->>'description' as description
            FROM assets
            WHERE
                name ILIKE $1
                OR type ILIKE $1
                OR metadata->>'description' ILIKE $1
            ORDER BY name
        """
        assets = await db.fetch_all(sql_query, f"%{query}%")
        return assets
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to search assets: {str(e)}"
        )
