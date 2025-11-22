"""Service for managing deck type definitions."""

from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.deck import DeckDefinitionOrm, DeckPositionDefinitionOrm
from praxis.backend.models.pydantic_internals.deck import (
  DeckTypeDefinitionCreate,
  DeckTypeDefinitionUpdate,
)
from praxis.backend.services.utils.crud_base import CRUDBase


class DeckTypeDefinitionService(
  CRUDBase[DeckDefinitionOrm, DeckTypeDefinitionCreate, DeckTypeDefinitionUpdate],
):

  """Service for managing deck type definitions."""

  async def create(
    self, db: AsyncSession, *, obj_in: DeckTypeDefinitionCreate,
  ) -> DeckDefinitionOrm:
    """Create a new deck type definition."""
    obj_in_data = obj_in.model_dump()
    obj_in_data.pop("accession_id", None)
    obj_in_data.pop("created_at", None)
    obj_in_data.pop("updated_at", None)
    obj_in_data.pop("positioning_config", None)
    position_definitions = obj_in_data.pop("position_definitions", [])

    db_obj = self.model(**obj_in_data)

    if position_definitions:
      for position_definition in position_definitions:
        db_obj.positions.append(DeckPositionDefinitionOrm(**position_definition))

    db.add(db_obj)
    await db.flush()
    await db.refresh(db_obj, ["positions", "resource_definition"])
    return db_obj
