"""Service layer for Machine Backend Definition Management."""

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.domain.machine_backend import (
  MachineBackendDefinition,
  MachineBackendDefinitionCreate,
  MachineBackendDefinitionUpdate,
)
from praxis.backend.models.domain.machine_frontend import MachineFrontendDefinition
from praxis.backend.models.enums import BackendTypeEnum
from praxis.backend.services.plr_type_base import DiscoverableTypeServiceBase
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.utils.logging import get_logger
from praxis.backend.utils.plr_static_analysis import (
  BACKEND_TYPE_TO_FRONTEND_FQN,
  PLRSourceParser,
  find_plr_source_root,
)

logger = get_logger(__name__)


class MachineBackendDefinitionService(
  DiscoverableTypeServiceBase[
    MachineBackendDefinition,
    MachineBackendDefinitionCreate,
    MachineBackendDefinitionUpdate,
  ],
):
  """Service for discovering and syncing machine backend definitions.

  Uses static analysis to discover backends from PyLabRobot source.
  """

  def __init__(self, db: AsyncSession, plr_source_path: Path | None = None) -> None:
    """Initialize the MachineBackendDefinitionService.

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
  def _orm_model(self) -> type[MachineBackendDefinition]:
    """The SQLAlchemy ORM model for the type definition."""
    return MachineBackendDefinition

  async def discover_and_synchronize_type_definitions(self) -> list[MachineBackendDefinition]:
    """Discover all machine backend definitions from pylabrobot and sync with the database."""
    logger.info("Discovering machine backend types via static analysis...")

    # Use static analysis to discover backends
    all_discovered = self.parser.discover_backend_classes()
    logger.info("Discovered %d backend classes total.", len(all_discovered))

    synced_definitions = []

    for cls in all_discovered:
      if cls.is_abstract:
        continue

      definition = await self._upsert_backend(cls)
      if definition:
        synced_definitions.append(definition)

    await self.db.commit()
    logger.info("Synchronized %d machine backend definitions.", len(synced_definitions))
    return synced_definitions

  async def _upsert_backend(self, cls) -> MachineBackendDefinition | None:
    """Create or update a machine backend definition from discovered class."""
    # Lookup frontend FQN from backend class_type
    frontend_fqn = BACKEND_TYPE_TO_FRONTEND_FQN.get(cls.class_type)
    if not frontend_fqn:
      logger.debug("No frontend FQN mapping found for backend class type: %s", cls.class_type)
      return None

    # Query MachineFrontendDefinition by fqn
    frontend_result = await self.db.execute(
      select(MachineFrontendDefinition).filter(MachineFrontendDefinition.fqn == frontend_fqn)
    )
    frontend_def = frontend_result.scalar_one_or_none()
    if not frontend_def:
      logger.warning("No MachineFrontendDefinition found for FQN: %s", frontend_fqn)
      return None

    # Determine backend_type
    backend_type = self._determine_backend_type(cls)

    # Query by fqn to find existing backend
    existing_result = await self.db.execute(
      select(MachineBackendDefinition).filter(MachineBackendDefinition.fqn == cls.fqn)
    )
    existing_backend = existing_result.scalar_one_or_none()

    if existing_backend:
      update_data = MachineBackendDefinitionUpdate(
        name=cls.name,
        fqn=cls.fqn,
        description=cls.docstring,
        backend_type=backend_type,
        connection_config=cls.connection_config.model_dump() if cls.connection_config else None,
        manufacturer=cls.manufacturer,
        model=cls.model_name,
        frontend_definition_accession_id=frontend_def.accession_id,
      )
      for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(existing_backend, key, value)
      self.db.add(existing_backend)
      logger.debug("Updated machine backend definition: %s", cls.fqn)
      return existing_backend

    create_data = MachineBackendDefinitionCreate(
      name=cls.name,
      fqn=cls.fqn,
      description=cls.docstring,
      backend_type=backend_type,
      connection_config=cls.connection_config.model_dump() if cls.connection_config else None,
      manufacturer=cls.manufacturer,
      model=cls.model_name,
      frontend_definition_accession_id=frontend_def.accession_id,
    )
    obj_in_data = create_data.model_dump()
    # Remove fields that are not accepted by ORM init
    for field in ("accession_id", "created_at", "updated_at"):
      obj_in_data.pop(field, None)

    new_backend = MachineBackendDefinition(**obj_in_data)
    self.db.add(new_backend)
    logger.debug("Added new machine backend definition: %s", cls.fqn)
    return new_backend

  def _determine_backend_type(self, cls) -> BackendTypeEnum:
    """Determine backend type based on class properties and naming."""
    name_lower = cls.name.lower()
    if "chatterbox" in name_lower:
      return BackendTypeEnum.CHATTERBOX
    if "mock" in name_lower:
      return BackendTypeEnum.MOCK
    if "simulator" in name_lower or cls.is_simulated():
      return BackendTypeEnum.SIMULATOR
    return BackendTypeEnum.REAL_HARDWARE


class MachineBackendDefinitionCRUDService(
  CRUDBase[
    MachineBackendDefinition,
    MachineBackendDefinitionCreate,
    MachineBackendDefinitionUpdate,
  ],
):
  """CRUD service for machine backend definitions."""
