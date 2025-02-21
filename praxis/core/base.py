from typing import (
    Protocol as TypeProtocol,
    Dict,
    Any,
    AsyncContextManager,
    Optional,
    Union,
    Mapping,
    Type,
)
from dataclasses import dataclass

from abc import ABC, abstractmethod
from pylabrobot.resources import Resource
from pylabrobot.machines import Machine


# Define a type alias for asset types
AssetType = Type[Union[Resource, Machine]]


@dataclass
class WorkcellAssetSpec:
    """Specification for a required workcell asset (resource or machine).

    Attributes:
        name: Name of the asset on the workcell
        type: Expected type of the asset (Resource or Machine)
        description: Optional description of what this asset is used for
        required: Whether this asset is required (defaults to True)
    """

    name: str
    type: AssetType
    description: Optional[str] = None
    required: bool = True


class WorkcellInterface(AsyncContextManager, TypeProtocol):
    """Interface for Workcell functionality."""

    @abstractmethod
    def __contains__(self, item: str) -> bool: ...

    @abstractmethod
    async def get_state(self) -> Dict[str, Any]: ...

    @abstractmethod
    async def update_state(self, state: Dict[str, Any]) -> None: ...

    @abstractmethod
    async def is_asset_in_use(self, asset_name: str) -> bool: ...

    @abstractmethod
    async def save_state_to_file(self, filepath: str) -> None: ...

    @abstractmethod
    async def load_state_from_file(self, filepath: str) -> None: ...

    @abstractmethod
    async def mark_asset_in_use(self, asset_name: str, protocol_name: str) -> None: ...

    @abstractmethod
    async def update_asset_state(
        self, asset_name: str, state: Dict[str, Any]
    ) -> None: ...

    @abstractmethod
    async def get_asset_state(self, asset_name: str) -> Dict[str, Any]: ...

    @abstractmethod
    async def mark_asset_released(
        self, asset_name: str, protocol_name: str
    ) -> None: ...

    @property
    @abstractmethod
    def _asset_states(self) -> Dict[str, Dict[str, Any]]: ...


class WorkcellAssetsInterface(TypeProtocol):
    """Interface for WorkcellAssets functionality."""

    @abstractmethod
    def __contains__(self, asset_name: str) -> bool: ...

    @abstractmethod
    def __iter__(self) -> Any: ...

    @abstractmethod
    def load_from_dict(
        self, assets: Mapping[str, Union[AssetType, Dict[str, Any]]]
    ) -> None: ...

    @abstractmethod
    def add(
        self,
        name: str,
        type_: AssetType,
        description: Optional[str] = None,
        required: bool = True,
    ) -> None: ...

    @abstractmethod
    def get_spec(self, id: str) -> WorkcellAssetSpec: ...

    @abstractmethod
    def validate(self, workcell: WorkcellInterface) -> None: ...


class ProtocolInterface(TypeProtocol):
    """Interface for Protocol functionality."""

    @property
    def name(self) -> str: ...

    @property
    def status(self) -> str: ...

    @property
    @abstractmethod
    def required_assets(self) -> WorkcellAssetsInterface: ...

    @classmethod
    @abstractmethod
    def __init__(
        self, config: Union[Dict[str, Any]]
    ) -> None: ...  # TODO: config interface?

    @abstractmethod
    async def initialize(
        self, workcell: Optional[WorkcellInterface] = None
    ) -> None: ...

    @abstractmethod
    async def execute(self) -> None: ...


class ProtocolBase(ABC):
    """Base class for Protocol functionality."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def status(self) -> str: ...

    @property
    @abstractmethod
    def required_assets(self) -> WorkcellAssetsInterface: ...

    @abstractmethod
    async def initialize(
        self, workcell: Optional[WorkcellInterface] = None
    ) -> None: ...
    @abstractmethod
    async def execute(self) -> None: ...
