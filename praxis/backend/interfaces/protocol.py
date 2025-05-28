from typing import (
    Protocol as TypeProtocol,
    Dict,
    Any,
    Optional,
    Union,
)

from abc import ABC, abstractmethod
from .workcell import WorkcellAssetsInterface, WorkcellInterface


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
