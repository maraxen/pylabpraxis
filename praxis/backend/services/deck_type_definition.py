"""Service for managing deck type definitions."""

from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.deck import DeckDefinitionOrm, DeckPositionDefinitionOrm
from praxis.backend.models.pydantic_internals.deck import (
  DeckTypeDefinitionCreate,
  DeckTypeDefinitionUpdate,
)
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.utils.uuid import uuid7


class DeckTypeDefinitionService(
  CRUDBase[DeckDefinitionOrm, DeckTypeDefinitionCreate, DeckTypeDefinitionUpdate],
):

  """Service for managing deck type definitions."""

  async def create(
    self,
    db: AsyncSession,
    *,
    obj_in: DeckTypeDefinitionCreate,
  ) -> DeckDefinitionOrm:
    """Create a new deck type definition."""
    obj_in_data = obj_in.model_dump()
    obj_in_data.pop("accession_id", None)
    obj_in_data.pop("created_at", None)
    obj_in_data.pop("updated_at", None)
    obj_in_data.pop("positioning_config", None)
    position_definitions = obj_in_data.pop("position_definitions", [])

    db_obj = self.model(**obj_in_data)
    db_obj.accession_id = uuid7()

    if position_definitions:
      for position_definition in position_definitions:
        # Map name to position_accession_id if missing
        if "position_accession_id" not in position_definition and "name" in position_definition:
          position_definition["position_accession_id"] = position_definition["name"]

        # Remove fields that are not accepted by ORM init
        position_definition.pop("accession_id", None)
        position_definition.pop("created_at", None)
        position_definition.pop("updated_at", None)

        db_obj.positions.append(
          DeckPositionDefinitionOrm(
            **position_definition,
            deck_type=db_obj,
            deck_type_id=db_obj.accession_id,
          ),
        )

    db.add(db_obj)
    await db.flush()
    await db.refresh(db_obj, ["positions", "resource_definition"])
    return db_obj
