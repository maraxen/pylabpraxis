from typing import (
    Protocol as TypeProtocol,
    Dict,
    Any,
    Union,
    Type,
)

from pylabrobot.resources import Resource
from pylabrobot.machines import Machine


# Define a type alias for asset types
AssetType = Type[Union[Resource, Machine]]


class DatabaseInterface(TypeProtocol):
    """Interface for database operations"""

    async def get_protocol_details(self, protocol_path: str) -> Dict[str, Any]: ...
    async def discover_protocols(self, directories: list[str]) -> list[dict]: ...
    async def get_user(self, user: str) -> dict[str, Any]: ...
    async def fetch_all(self, query: str, *args) -> list[dict]: ...
    async def get_asset(self, asset_name: str) -> dict: ...
    async def close(self) -> None: ...
