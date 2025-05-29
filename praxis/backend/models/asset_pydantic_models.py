from pydantic import BaseModel
from typing import Optional


class AssetBase(BaseModel):  # Used for response, not directly for DB interaction now
    name: str
    type: str
    metadata: dict = {}


class AssetResponse(AssetBase):  # Used for response
    is_available: bool
    description: Optional[str] = None
