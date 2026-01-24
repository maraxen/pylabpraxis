"""CRUD service for resource type definitions."""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.domain.resource import (
  ResourceDefinition,
  ResourceDefinitionCreate,
  ResourceDefinitionUpdate,
)
from praxis.backend.services.utils.crud_base import CRUDBase


class ResourceTypeDefinitionCRUDService(
  CRUDBase[
    ResourceDefinition,
    ResourceDefinitionCreate,
    ResourceDefinitionUpdate,
  ],
):
  """CRUD service for resource type definitions."""

  async def update(
    self,
    db: AsyncSession,
    *,
    db_obj: ResourceDefinition,
    obj_in: ResourceDefinitionUpdate | dict[str, Any],
  ) -> ResourceDefinition:
    """Update an existing resource definition."""
    obj_in_model = ResourceDefinitionUpdate(**obj_in) if isinstance(obj_in, dict) else obj_in
    return await super().update(db=db, db_obj=db_obj, obj_in=obj_in_model)
