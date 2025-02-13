from typing import (
    Protocol as TypeProtocol,
    Dict,
    Any,
    Optional,
    AsyncContextManager,
    Coroutine,
)
from abc import ABC, abstractmethod


class WorkcellInterface(AsyncContextManager, TypeProtocol):
    """Interface for Workcell functionality."""

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
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...


class ProtocolBase(ABC):
    """Base class for Protocol functionality."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def status(self) -> str: ...

    @abstractmethod
    async def initialize(self, orchestrator: Any = None) -> None: ...

    @abstractmethod
    async def execute(self) -> None: ...


class WorkcellBase(ABC):
    """Base class for Workcell functionality."""

    @abstractmethod
    def get_state(self) -> Dict[str, Any]: ...

    @abstractmethod
    def update_state(self, state: Dict[str, Any]) -> None: ...
