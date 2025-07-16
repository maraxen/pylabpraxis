"""Service layer for Machine Type Definition Management."""

import inspect

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.machine import MachineDefinitionOrm
from praxis.backend.models.pydantic.machine import (
  MachineDefinitionCreate,
  MachineDefinitionUpdate,
)
from praxis.backend.services.plr_type_base import DiscoverableTypeServiceBase
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.plr_inspection import get_machine_classes

logger = get_logger(__name__)


class MachineTypeDefinitionService(
  DiscoverableTypeServiceBase[
    MachineDefinitionOrm,
    MachineDefinitionCreate,
    MachineDefinitionUpdate,
  ],
):
  """Service for discovering and syncing machine type definitions."""

  def __init__(self, db: AsyncSession) -> None:
    """Initialize the MachineDefinitionService."""
    super().__init__(db)

  @property
  def _orm_model(self) -> type[MachineDefinitionOrm]:
    """The SQLAlchemy ORM model for the type definition."""
    return MachineDefinitionOrm

  async def discover_and_synchronize_type_definitions(self) -> list[MachineDefinitionOrm]:
    """Discover all machine type definitions from pylabrobot and synchronizes with the database."""
    logger.info("Discovering machine types...")
    discovered_machines = get_machine_classes()
    logger.info("Discovered %d machine types.", len(discovered_machines))

    synced_definitions = []
    for fqn, plr_class_obj in discovered_machines.items():
      existing_machine_def_result = await self.db.execute(
        select(MachineDefinitionOrm).filter(MachineDefinitionOrm.fqn == fqn),
      )
      existing_machine_def = existing_machine_def_result.scalar_one_or_none()

      if existing_machine_def:
        update_data = MachineDefinitionUpdate(
          fqn=fqn,
          name=plr_class_obj.__name__,
          description=inspect.getdoc(plr_class_obj),
        )
        for key, value in update_data.model_dump(exclude_unset=True).items():
          setattr(existing_machine_def, key, value)
        self.db.add(existing_machine_def)
        logger.debug("Updated machine definition: %s", fqn)
        synced_definitions.append(existing_machine_def)
      else:
        create_data = MachineDefinitionCreate(
          name=plr_class_obj.__name__,
          fqn=fqn,
          description=inspect.getdoc(plr_class_obj),
        )
        new_machine_def = MachineDefinitionOrm(**create_data.model_dump())
        self.db.add(new_machine_def)
        logger.debug("Added new machine definition: %s", fqn)
        synced_definitions.append(new_machine_def)

    await self.db.commit()
    logger.info("Synchronized %d machine definitions.", len(synced_definitions))
    return synced_definitions
