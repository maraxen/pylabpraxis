"""Service layer for Resource Type Definition Management."""

import importlib
import inspect
import pkgutil
from typing import Any

import pylabrobot.resources
from pylabrobot.resources import (
  Carrier,
  Container,
  Deck,
  ItemizedResource,
  Lid,
  PlateAdapter,
  PlateHolder,
  Resource,
  ResourceHolder,
  ResourceStack,
  TipSpot,
  Well,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.resource import ResourceDefinitionOrm
from praxis.backend.models.pydantic.resource import (
  ResourceDefinitionCreate,
  ResourceDefinitionUpdate,
)
from praxis.backend.services.plr_type_base import DiscoverableTypeServiceBase
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)


class ResourceTypeDefinitionService(
  DiscoverableTypeServiceBase[
    ResourceDefinitionOrm,
    ResourceDefinitionCreate,
    ResourceDefinitionUpdate,
  ],
):

  """Service for discovering and syncing resource type definitions."""

  EXCLUDED_BASE_CLASSES: tuple[type[Resource], ...] = (
    Carrier,
    Container,
    Deck,
    ItemizedResource,
    Lid,
    PlateAdapter,
    PlateHolder,
    Resource,
    ResourceHolder,
    ResourceStack,
    TipSpot,
    Well,
  )

  def __init__(self, db: AsyncSession) -> None:
    """Initialize the ResourceTypeDefinitionService."""
    super().__init__(db)

  @property
  def _orm_model(self) -> type[ResourceDefinitionOrm]:
    """The SQLAlchemy ORM model for the type definition."""
    return ResourceDefinitionOrm

  def _can_catalog_resource(self, plr_class: type[Any]) -> bool:
    """Determine if a PyLabRobot class represents a resource definition to catalog."""
    if not inspect.isclass(plr_class) or not issubclass(plr_class, Resource):
      return False
    if inspect.isabstract(plr_class):
      return False
    if plr_class in self.EXCLUDED_BASE_CLASSES:
      return False
    return plr_class.__module__.startswith("pylabrobot.resources")

  def _get_category_from_plr_class(self, plr_class: type[Any]) -> str | None:
    """Extract the category from a PyLabRobot class."""
    if hasattr(plr_class, "category"):
      return plr_class.category
    return None

  def _extract_ordering_from_plr_class(self, plr_class: type[Any]) -> str | None:
    """Extract ordering information from a PyLabRobot class."""
    if hasattr(plr_class, "ordering") and isinstance(plr_class.ordering, list):
      return ",".join(plr_class.ordering)
    return None

  def _get_short_name_from_plr_class(self, plr_class: type[Any]) -> str:
    """Extract the short name from a PyLabRobot class."""
    return plr_class.__name__

  def _get_description_from_plr_class(self, plr_class: type[Any]) -> str | None:
    """Extract the description from a PyLabRobot class."""
    return inspect.getdoc(plr_class)

  def _get_size_x_mm_from_plr_class(self, plr_class: type[Any]) -> float | None:
    """Extract the size_x_mm from a PyLabRobot class."""
    if hasattr(plr_class, "size_x"):
      return plr_class.size_x
    return None

  def _get_size_y_mm_from_plr_class(self, plr_class: type[Any]) -> float | None:
    """Extract the size_y_mm from a PyLabRobot class."""
    if hasattr(plr_class, "size_y"):
      return plr_class.size_y
    return None

  def _get_size_z_mm_from_plr_class(self, plr_class: type[Any]) -> float | None:
    """Extract the size_z_mm from a PyLabRobot class."""
    if hasattr(plr_class, "size_z"):
      return plr_class.size_z
    return None

  def _get_nominal_volume_ul_from_plr_class(self, plr_class: type[Any]) -> float | None:
    """Extract the nominal_volume_ul from a PyLabRobot class."""
    if hasattr(plr_class, "nominal_volume"):
      return plr_class.nominal_volume
    return None

  async def discover_and_synchronize_type_definitions(
    self,
    plr_resources_package: type[Any] = pylabrobot,
  ) -> list[ResourceDefinitionOrm]:
    """Discover all pylabrobot resource type definitions and synchronize them with the database."""
    logger.info(
      "Starting PyLabRobot resource definition sync from package: %s",
      plr_resources_package.__name__,
    )
    synced_definitions = []
    processed_fqns: set[str] = set()

    for _, modname, _ in pkgutil.walk_packages(
      path=plr_resources_package.__path__,
      prefix=plr_resources_package.__name__ + ".",
      onerror=lambda x: logger.error("Error walking package %s", x),
    ):
      try:
        module = importlib.import_module(modname)
      except ImportError as e:
        logger.warning("Could not import module %s during sync: %s", modname, e)
        continue

      for class_name, plr_class_obj in inspect.getmembers(module, inspect.isclass):
        fqn = f"{modname}.{class_name}"
        if fqn in processed_fqns:
          continue
        processed_fqns.add(fqn)

        if not self._can_catalog_resource(plr_class_obj):
          continue

        # Extract metadata
        category = self._get_category_from_plr_class(plr_class_obj)
        ordering = self._extract_ordering_from_plr_class(plr_class_obj)
        short_name = self._get_short_name_from_plr_class(plr_class_obj)
        description = self._get_description_from_plr_class(plr_class_obj)
        size_x_mm = self._get_size_x_mm_from_plr_class(plr_class_obj)
        size_y_mm = self._get_size_y_mm_from_plr_class(plr_class_obj)
        size_z_mm = self._get_size_z_mm_from_plr_class(plr_class_obj)
        nominal_volume_ul = self._get_nominal_volume_ul_from_plr_class(plr_class_obj)

        existing_resource_def_result = await self.db.execute(
          select(ResourceDefinitionOrm).filter(ResourceDefinitionOrm.fqn == fqn),
        )
        existing_resource_def = existing_resource_def_result.scalar_one_or_none()

        if existing_resource_def:
          update_data = ResourceDefinitionUpdate(
            name=short_name,
            fqn=fqn,
            description=description,
            plr_category=category,
            ordering=ordering,
            size_x_mm=size_x_mm,
            size_y_mm=size_y_mm,
            size_z_mm=size_z_mm,
            nominal_volume_ul=nominal_volume_ul,
          )
          for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(existing_resource_def, key, value)
          self.db.add(existing_resource_def)
          logger.debug("Updated resource definition: %s", fqn)
          synced_definitions.append(existing_resource_def)
        else:
          new_resource_def = ResourceDefinitionOrm(
            name=short_name,
            fqn=fqn,
            description=description,
            plr_category=category,
            ordering=ordering,
            size_x_mm=size_x_mm,
            size_y_mm=size_y_mm,
            size_z_mm=size_z_mm,
            nominal_volume_ul=nominal_volume_ul,
          )
          self.db.add(new_resource_def)
          logger.debug("Added new resource definition: %s", fqn)
          synced_definitions.append(new_resource_def)

    await self.db.commit()
    logger.info("Synchronized %d resource definitions.", len(synced_definitions))
    return synced_definitions


class ResourceTypeDefinitionCRUDService(
  CRUDBase[
    ResourceDefinitionOrm,
    ResourceDefinitionCreate,
    ResourceDefinitionUpdate,
  ],
):

  """CRUD service for resource type definitions."""
