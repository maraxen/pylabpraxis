"""Service layer for Protocol Definition management."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.protocol import FunctionProtocolDefinitionOrm
from praxis.backend.models.pydantic_internals.protocol import (
  FunctionProtocolDefinitionCreate,
  FunctionProtocolDefinitionUpdate,
)
from praxis.backend.services.utils.crud_base import CRUDBase


class ProtocolDefinitionCRUDService(
  CRUDBase[
    FunctionProtocolDefinitionOrm,
    FunctionProtocolDefinitionCreate,
    FunctionProtocolDefinitionUpdate,
  ],
):

  """CRUD service for protocol definitions."""

  async def get_by_fqn(self, db: AsyncSession, fqn: str) -> FunctionProtocolDefinitionOrm | None:
    """Retrieve a specific protocol definition by its fully qualified name."""
    stmt = select(self.model).filter(self.model.fqn == fqn)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

  async def get_by_name(
      self,
      db: AsyncSession,
      name: str,
      version: str | None = None,
      source_name: str | None = None,
      commit_hash: str | None = None,
  ) -> FunctionProtocolDefinitionOrm | None:
      """Retrieve a protocol definition by name and other optional criteria."""
      stmt = select(self.model).filter(self.model.name == name)
      if version:
          stmt = stmt.filter(self.model.version == version)
      if source_name:
          stmt = stmt.filter(self.model.source_name == source_name)
      if commit_hash:
          stmt = stmt.filter(self.model.commit_hash == commit_hash)
      result = await db.execute(stmt)
      return result.scalar_one_or_none()
