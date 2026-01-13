"""Service for managing deck type definitions."""

from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.domain.deck import (
  DeckDefinition as DeckDefinition,
  DeckPositionDefinition as DeckPositionDefinition,
  DeckDefinitionCreate as DeckTypeDefinitionCreate,
  DeckDefinitionUpdate as DeckTypeDefinitionUpdate,
)
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.utils.uuid import uuid7


class DeckTypeDefinitionService(
  CRUDBase[DeckDefinition, DeckTypeDefinitionCreate, DeckTypeDefinitionUpdate],
):
  """Service for managing deck type definitions."""

  async def create(
    self,
    db: AsyncSession,
    *,
    obj_in: DeckTypeDefinitionCreate,
  ) -> DeckDefinition:
    """Create a new deck type definition."""
    obj_in_data = obj_in.model_dump()
    obj_in_data.pop("accession_id", None)
    obj_in_data.pop("created_at", None)
    obj_in_data.pop("updated_at", None)
    obj_in_data.pop("positioning_config", None)
    # Normalize position_definitions: ensure None becomes empty list
    position_definitions = obj_in_data.pop("position_definitions", None) or []

    # Ensure we don't pass a None for the relationship-backed `positions`
    # attribute into the ORM initializer (SQLAlchemy rejects None for
    # collection relationships). Remove it if present.
    obj_in_data.pop("positions", None)

    db_obj = self.model(**obj_in_data)
    db_obj.accession_id = uuid7()

    if position_definitions:
      for position_definition in position_definitions:
        # Map name to position_accession_id if missing
        if not position_definition.get("position_accession_id") and position_definition.get("name"):
          position_definition["position_accession_id"] = position_definition["name"]

        # Remove fields that are not accepted by ORM init
        position_definition.pop("accession_id", None)
        position_definition.pop("created_at", None)
        position_definition.pop("updated_at", None)

        # Ensure deck_type_id is set for validation/ORM initialization
        position_definition["deck_type_id"] = db_obj.accession_id

        pos = DeckPositionDefinition(**position_definition)
        pos.deck_type = db_obj
        db_obj.positions.append(pos)

    db.add(db_obj)
    await db.flush()
    # Only refresh positions; `resource_definition` is not a mapped attribute
    # on DeckDefinition and asking SQLAlchemy to refresh it raises KeyError.
    await db.refresh(db_obj, ["positions"])
    return db_obj
