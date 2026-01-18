"""Service for discovering and syncing machine frontend definitions."""

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.domain.machine_frontend import (
  MachineFrontendDefinition,
  MachineFrontendDefinitionCreate,
  MachineFrontendDefinitionUpdate,
)
from praxis.backend.models.enums import MachineCategoryEnum
from praxis.backend.services.plr_type_base import DiscoverableTypeServiceBase
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.plr_static_analysis import (
  MACHINE_FRONTEND_TYPES,
  DiscoveredClass,
  PLRSourceParser,
  find_plr_source_root,
)

logger = get_logger(__name__)


class MachineFrontendDefinitionService(
  DiscoverableTypeServiceBase[
    MachineFrontendDefinition,
    MachineFrontendDefinitionCreate,
    MachineFrontendDefinitionUpdate,
  ],
):
  """Service for discovering and syncing machine frontend definitions.

  Discovers frontend definitions from PyLabRobot source and synchronizes them
  to the database.
  """

  def __init__(self, db: AsyncSession, plr_source_path: Path | None = None) -> None:
    """Initialize the MachineFrontendDefinitionService.

    Args:
      db: The database session.
      plr_source_path: Optional path to PLR source. Auto-detected if not provided.

    """
    self.db = db
    self._plr_source_path = plr_source_path
    self._parser: PLRSourceParser | None = None

  @property
  def parser(self) -> PLRSourceParser:
    """Get or create the PLR source parser lazily."""
    if self._parser is None:
      plr_path = self._plr_source_path or find_plr_source_root()
      self._parser = PLRSourceParser(plr_path)
    return self._parser

  @property
  def _orm_model(self) -> type[MachineFrontendDefinition]:
    """The SQLAlchemy ORM model for the type definition."""
    return MachineFrontendDefinition

  async def discover_and_synchronize_type_definitions(self) -> list[MachineFrontendDefinition]:
    """Discover frontend classes from PLR source and sync to DB.

    Uses static analysis to find classes filtered to MACHINE_FRONTEND_TYPES.
    """
    logger.info("Discovering machine frontend types via static analysis...")

    # Assumes discover_frontend_classes() exists or is added to parser
    all_discovered = self.parser.discover_frontend_classes()
    logger.info("Discovered %d machine frontend types total.", len(all_discovered))

    synced_definitions = []
    for cls in all_discovered:
      if not cls.is_abstract:
        definition = await self._upsert_frontend(cls)
        synced_definitions.append(definition)

    await self.db.commit()
    logger.info("Synchronized %d machine frontend definitions.", len(synced_definitions))
    return synced_definitions

  async def _upsert_frontend(self, cls: DiscoveredClass) -> MachineFrontendDefinition:
    """Create or update a MachineFrontendDefinition record from discovered class.

    Args:
      cls: The discovered class from static analysis.

    Returns:
      The created or updated ORM object.

    """
    existing_result = await self.db.execute(
      select(MachineFrontendDefinition).filter(MachineFrontendDefinition.fqn == cls.fqn),
    )
    existing_def = existing_result.scalar_one_or_none()

    # Map class_type to MachineCategoryEnum
    # Convert snake_case to PascalCase for mapping
    category_name = "".join(word.capitalize() for word in cls.class_type.value.split("_"))
    try:
      machine_category = MachineCategoryEnum(category_name)
    except ValueError:
      machine_category = MachineCategoryEnum.UNKNOWN

    capabilities = cls.to_capabilities_dict()

    if existing_def:
      update_data = MachineFrontendDefinitionUpdate(
        name=cls.name,
        fqn=cls.fqn,
        description=cls.docstring,
        plr_category=cls.category,
        machine_category=machine_category,
        capabilities=capabilities,
        capabilities_config=cls.capabilities_config.model_dump()
        if cls.capabilities_config
        else None,
        has_deck=getattr(cls, "has_deck", False),
        manufacturer=cls.manufacturer,
        model=cls.model_name,
      )
      for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(existing_def, key, value)
      self.db.add(existing_def)
      logger.debug("Updated machine frontend definition: %s", cls.fqn)
      return existing_def

    create_data = MachineFrontendDefinitionCreate(
      name=cls.name,
      fqn=cls.fqn,
      description=cls.docstring,
      plr_category=cls.category,
      machine_category=machine_category,
      capabilities=capabilities,
      capabilities_config=cls.capabilities_config.model_dump() if cls.capabilities_config else None,
      has_deck=getattr(cls, "has_deck", False),
      manufacturer=cls.manufacturer,
      model=cls.model_name,
    )
    obj_in_data = create_data.model_dump()

    new_def = MachineFrontendDefinition(**obj_in_data)
    self.db.add(new_def)
    logger.debug("Added new machine frontend definition: %s", cls.fqn)
    return new_def


class MachineFrontendDefinitionCRUDService(
  CRUDBase[
    MachineFrontendDefinition,
    MachineFrontendDefinitionCreate,
    MachineFrontendDefinitionUpdate,
  ],
):
  """CRUD service for machine frontend definitions."""
