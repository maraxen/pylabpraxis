"""Service layer for Machine Type Definition Management."""

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.domain.machine import (
  MachineDefinition as MachineDefinition,
  MachineDefinitionCreate,
  MachineDefinitionRead as MachineDefinitionResponse,
  MachineDefinitionUpdate,
)
from praxis.backend.services.plr_type_base import DiscoverableTypeServiceBase
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.plr_static_analysis import (
  BACKEND_TYPE_TO_FRONTEND_FQN,
  DiscoveredClass,
  PLRSourceParser,
  find_plr_source_root,
)

logger = get_logger(__name__)


class MachineTypeDefinitionService(
  DiscoverableTypeServiceBase[
    MachineDefinition,
    MachineDefinitionCreate,
    MachineDefinitionUpdate,
  ],
):
  """Service for discovering and syncing machine type definitions.

  Uses LibCST-based static analysis to discover machine types from PyLabRobot
  source without runtime imports.

  """

  def __init__(self, db: AsyncSession, plr_source_path: Path | None = None) -> None:
    """Initialize the MachineDefinitionService.

    Args:
      db: The database session.
      plr_source_path: Optional path to PLR source. Auto-detected if not provided.

    """
    self.db = db
    self._plr_source_path = plr_source_path
    self._parser: PLRSourceParser | None = None

  @property
  def parser(self) -> PLRSourceParser:
    """Get or create the PLR source parser."""
    if self._parser is None:
      plr_path = self._plr_source_path or find_plr_source_root()
      self._parser = PLRSourceParser(plr_path)
    return self._parser

  @property
  def _orm_model(self) -> type[MachineDefinition]:
    """The SQLAlchemy ORM model for the type definition."""
    return MachineDefinition

  async def discover_and_synchronize_type_definitions(self) -> list[MachineDefinition]:
    """Discover all machine type definitions from pylabrobot and synchronizes with the database.

    Uses LibCST-based static analysis for safe, import-free discovery.

    """
    logger.info("Discovering machine types via static analysis...")

    # Use static analysis to discover machines
    all_discovered = self.parser.discover_machine_classes()
    logger.info("Discovered %d machine types total.", len(all_discovered))

    # Enforce singleton pattern for simulated frontends/backends per category
    # to avoid UI noise and potential DB clobbering.
    simulated_seen = set()
    discovered_machines = []

    for cls in all_discovered:
      if cls.is_simulated():
        # Identify category (either from backend mapping or class type itself)
        category = BACKEND_TYPE_TO_FRONTEND_FQN.get(cls.class_type) or cls.class_type
        if category in simulated_seen:
          continue
        simulated_seen.add(category)
      discovered_machines.append(cls)

    logger.info("Kept %d machine types after deduplication.", len(discovered_machines))

    synced_definitions = []
    for cls in discovered_machines:
      definition = await self._upsert_definition(cls)
      synced_definitions.append(definition)

    await self.db.commit()
    logger.info("Synchronized %d machine definitions.", len(synced_definitions))
    return synced_definitions

  async def _upsert_definition(self, cls: DiscoveredClass) -> MachineDefinition:
    """Create or update a machine definition from discovered class.

    Args:
      cls: The discovered class from static analysis.

    Returns:
      The created or updated ORM object.

    """
    existing_result = await self.db.execute(
      select(MachineDefinition).filter(MachineDefinition.fqn == cls.fqn),
    )
    existing_def = existing_result.scalar_one_or_none()

    # Convert capabilities to the expected format
    capabilities = cls.to_capabilities_dict()

    # Lookup frontend FQN from class_type
    frontend_fqn = BACKEND_TYPE_TO_FRONTEND_FQN.get(cls.class_type)

    if existing_def:
      update_data = MachineDefinitionUpdate(
        fqn=cls.fqn,
        name=cls.name,
        description=cls.docstring,
        manufacturer=cls.manufacturer,
        capabilities=capabilities,
        compatible_backends=cls.compatible_backends,
        capabilities_config=cls.capabilities_config.model_dump()
        if cls.capabilities_config
        else None,
        connection_config=cls.connection_config.model_dump() if cls.connection_config else None,
        frontend_fqn=frontend_fqn,
      )
      for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(existing_def, key, value)
      self.db.add(existing_def)
      logger.debug("Updated machine definition: %s", cls.fqn)
      return existing_def

    create_data = MachineDefinitionCreate(
      name=cls.name,
      fqn=cls.fqn,
      description=cls.docstring,
      manufacturer=cls.manufacturer,
      capabilities=capabilities,
      compatible_backends=cls.compatible_backends,
      capabilities_config=cls.capabilities_config.model_dump() if cls.capabilities_config else None,
      connection_config=cls.connection_config.model_dump() if cls.connection_config else None,
      frontend_fqn=frontend_fqn,
    )
    obj_in_data = create_data.model_dump()
    # Remove fields that are not accepted by ORM init
    for field in (
      "accession_id",
      "created_at",
      "updated_at",
      "nominal_volume_ul",
      "ordering",
      "has_deck",
    ):
      obj_in_data.pop(field, None)

    new_def = MachineDefinition(**obj_in_data)
    self.db.add(new_def)
    logger.debug("Added new machine definition: %s", cls.fqn)
    return new_def


class MachineTypeDefinitionCRUDService(
  CRUDBase[
    MachineDefinition,
    MachineDefinitionCreate,
    MachineDefinitionUpdate,
  ],
):
  """CRUD service for machine type definitions."""
