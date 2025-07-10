"""Service layer for Protocol Definition management."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from praxis.backend.models.orm.protocol import FunctionProtocolDefinitionOrm
from praxis.backend.models.pydantic.protocol import (
    FunctionProtocolDefinitionCreate,
    FunctionProtocolDefinitionUpdate,
)
from praxis.backend.services.utils.crud_base import CRUDBase


class ProtocolDefinitionCRUDService(
    CRUDBase[
        FunctionProtocolDefinitionOrm,
        FunctionProtocolDefinitionCreate,
        FunctionProtocolDefinitionUpdate,
    ]
):
    """CRUD service for protocol definitions."""

    async def get_by_fqn(self, db: AsyncSession, fqn: str) -> FunctionProtocolDefinitionOrm | None:
        """Retrieve a specific protocol definition by its fully qualified name."""
        stmt = select(self.model).filter(self.model.fqn == fqn)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
