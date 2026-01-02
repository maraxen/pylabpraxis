"""Base class for type definition services."""

from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession


class TypeDefinitionServiceBase(ABC):
  """Base class for services that discover and sync type definitions."""

  def __init__(self, db_session: AsyncSession) -> None:
    """Initialize the TypeDefinitionServiceBase."""
    self.db = db_session

  @abstractmethod
  async def discover_types(self) -> list[dict[str, Any]]:
    """Discover type definitions from the source."""
    raise NotImplementedError

  @abstractmethod
  async def sync_with_source(self) -> tuple[int, int]:
    """Sync the discovered types with the database."""
    raise NotImplementedError
