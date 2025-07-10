"""Service layer for Deck Type Definition Management."""

import inspect

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.deck import DeckDefinitionOrm
from praxis.backend.models.pydantic.deck import (
    DeckTypeDefinitionCreate,
    DeckTypeDefinitionUpdate,
    PositioningConfig,
)
from praxis.backend.services.plr_type_base import DiscoverableTypeServiceBase
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.plr_inspection import get_deck_classes

logger = get_logger(__name__)


class DeckTypeDefinitionService(
    DiscoverableTypeServiceBase[
        DeckDefinitionOrm, DeckTypeDefinitionCreate, DeckTypeDefinitionUpdate
    ]
):
    """Service for discovering and syncing deck type definitions."""

    def __init__(self, db: AsyncSession):
        """Initialize the DeckTypeDefinitionService."""
        super().__init__(db)

    @property
    def _orm_model(self) -> type[DeckDefinitionOrm]:
        """The SQLAlchemy ORM model for the type definition."""
        return DeckDefinitionOrm

    async def discover_and_synchronize_type_definitions(
        self,
    ) -> list[DeckDefinitionOrm]:
        """
        Discovers all deck type definitions from pylabrobot and synchronizes them with the database.
        """
        logger.info("Discovering deck types...")
        discovered_decks = get_deck_classes()
        logger.info(f"Discovered {len(discovered_decks)} deck types.")

        synced_definitions = []
        for fqn, plr_class_obj in discovered_decks.items():
            existing_deck_def_result = await self.db.execute(
                select(self._orm_model).filter(self._orm_model.fqn == fqn)
            )
            existing_deck_def = existing_deck_def_result.scalar_one_or_none()

            if existing_deck_def:
                update_data = DeckTypeDefinitionUpdate(
                    name=plr_class_obj.__name__,
                    description=inspect.getdoc(plr_class_obj),
                )
                for key, value in update_data.model_dump(exclude_unset=True).items():
                    setattr(existing_deck_def, key, value)
                self.db.add(existing_deck_def)
                logger.debug("Updated deck definition: %s", fqn)
                synced_definitions.append(existing_deck_def)
            else:
                create_data = DeckTypeDefinitionCreate(
                    name=plr_class_obj.__name__,
                    fqn=fqn,
                    description=inspect.getdoc(plr_class_obj),
                    positioning_config=PositioningConfig(
                        method_name="slot_to_location",
                        arg_name="slot",
                        arg_type="str",
                        params=None,
                    ),
                )
                new_deck_def = self._orm_model(**create_data.model_dump())
                self.db.add(new_deck_def)
                logger.debug("Added new deck definition: %s", fqn)
                synced_definitions.append(new_deck_def)

        await self.db.commit()
        logger.info(f"Synchronized {len(synced_definitions)} deck definitions.")
        return synced_definitions


class DeckTypeDefinitionCRUDService(
    CRUDBase[DeckDefinitionOrm, DeckTypeDefinitionCreate, DeckTypeDefinitionUpdate]
):
    """CRUD service for deck type definitions."""

    pass
