"""Service layer for Resource Type Definition Management."""

import importlib
import inspect
import pkgutil
import types
from typing import Any

import pylabrobot.resources
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.domain.resource import (
    ResourceDefinition,
    ResourceDefinitionCreate,
    ResourceDefinitionUpdate,
)
from praxis.backend.services.plr_type_base import DiscoverableTypeServiceBase
from praxis.backend.services.resource_type_validation import (
    can_catalog_resource,
    extract_ordering_from_plr_class,
    extract_vendor_from_fqn,
    get_category_from_plr_class,
    get_description_from_plr_class,
    get_metadata_from_factory_function,
    get_nominal_volume_ul_from_plr_class,
    get_short_name_from_plr_class,
    get_size_x_mm_from_plr_class,
    get_size_y_mm_from_plr_class,
    get_size_z_mm_from_plr_class,
    is_resource_factory_function,
)
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)

# Module patterns for vendor-specific resources (these are concrete implementations)
VENDOR_MODULE_PATTERNS = (
    # Original vendors
    "pylabrobot.resources.hamilton",
    "pylabrobot.resources.opentrons",
    "pylabrobot.resources.tecan",
    "pylabrobot.resources.corning",
    "pylabrobot.resources.azenta",
    "pylabrobot.resources.alpaqua",
    "pylabrobot.resources.boekel",
    "pylabrobot.resources.greiner",
    "pylabrobot.resources.thermo",
    "pylabrobot.resources.revvity",
    "pylabrobot.resources.porvair",
    # Additional vendors discovered in PLR
    "pylabrobot.resources.agenbio",
    "pylabrobot.resources.agilent",
    "pylabrobot.resources.bioer",
    "pylabrobot.resources.biorad",
    "pylabrobot.resources.celltreat",
    "pylabrobot.resources.cellvis",
    "pylabrobot.resources.diy",
    "pylabrobot.resources.eppendorf",
    "pylabrobot.resources.falcon",
    "pylabrobot.resources.imcs",
    "pylabrobot.resources.nest",
    "pylabrobot.resources.perkin_elmer",
    "pylabrobot.resources.sergi",
    "pylabrobot.resources.stanley",
    "pylabrobot.resources.thermo_fisher",
    "pylabrobot.resources.vwr",
)


class ResourceTypeDefinitionService(
    CRUDBase[
        ResourceDefinition,
        ResourceDefinitionCreate,
        ResourceDefinitionUpdate,
    ],
    DiscoverableTypeServiceBase[
        ResourceDefinition,
        ResourceDefinitionCreate,
        ResourceDefinitionUpdate,
    ],
):
    """Service for discovering and syncing resource type definitions.

    This service discovers PyLabRobot resource definitions and syncs them to the database.
    It excludes generic base classes (like Plate, TipRack) and includes:
    1. Vendor-specific concrete classes (TecanPlate, HamiltonSTARDeck, etc.)
    2. Factory functions that create resource instances (Cor_96_wellplate_360ul_Fb, etc.)
    """

    def __init__(self, db: AsyncSession) -> None:
        """Initialize the ResourceTypeDefinitionService."""
        super().__init__(ResourceDefinition)
        self.db = db

    @property
    def _orm_model(self) -> type[ResourceDefinition]:
        """The SQLAlchemy ORM model for the type definition."""
        return ResourceDefinition

    async def discover_and_synchronize_type_definitions(
        self,
        plr_resources_package: types.ModuleType = pylabrobot,
    ) -> list[ResourceDefinition]:
        """Discover all pylabrobot resource type definitions and synchronize them with the database.

        This method discovers both:
        1. Resource subclasses (vendor-specific classes like TecanPlate, HamiltonSTARDeck)
        2. Factory functions that create Resource instances (like Cor_96_wellplate_360ul_Fb)
        """
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
            except Exception as e:  # Catch all exceptions including deprecation warnings
                logger.warning("Could not import module %s during sync: %s", modname, e)
                continue

            # 1. Discover class-based resource definitions
            for class_name, plr_class_obj in inspect.getmembers(module, inspect.isclass):
                fqn = f"{modname}.{class_name}"
                if fqn in processed_fqns:
                    continue
                processed_fqns.add(fqn)

                if not can_catalog_resource(plr_class_obj):
                    continue

                # Extract metadata
                category = get_category_from_plr_class(plr_class_obj)
                ordering = extract_ordering_from_plr_class(plr_class_obj)
                short_name = get_short_name_from_plr_class(plr_class_obj)
                description = get_description_from_plr_class(plr_class_obj)
                size_x_mm = get_size_x_mm_from_plr_class(plr_class_obj)
                size_y_mm = get_size_y_mm_from_plr_class(plr_class_obj)
                size_z_mm = get_size_z_mm_from_plr_class(plr_class_obj)
                nominal_volume_ul = get_nominal_volume_ul_from_plr_class(
                    plr_class_obj
                )

                synced_def = await self._sync_definition(
                    fqn=fqn,
                    short_name=short_name,
                    description=description,
                    category=category,
                    ordering=ordering,
                    size_x_mm=size_x_mm,
                    size_y_mm=size_y_mm,
                    size_z_mm=size_z_mm,
                    nominal_volume_ul=nominal_volume_ul,
                )
                synced_definitions.append(synced_def)

            # 2. Discover factory function-based resource definitions from vendor modules
            is_vendor_module = any(
                modname.startswith(p) for p in VENDOR_MODULE_PATTERNS
            )
            if is_vendor_module:
                for func_name, func_obj in inspect.getmembers(
                    module, inspect.isfunction
                ):
                    fqn = f"{modname}.{func_name}"
                    if fqn in processed_fqns:
                        continue
                    processed_fqns.add(fqn)

                    if not is_resource_factory_function(func_obj):
                        continue

                    # Only include functions defined in this module (not imported)
                    if func_obj.__module__ != modname:
                        continue

                    metadata = get_metadata_from_factory_function(func_obj, fqn)

                    synced_def = await self._sync_definition(
                        fqn=fqn,
                        short_name=metadata["name"],
                        description=metadata["description"],
                        category=metadata["category"],
                        ordering=metadata["ordering"],
                        size_x_mm=metadata["size_x_mm"],
                        size_y_mm=metadata["size_y_mm"],
                        size_z_mm=metadata["size_z_mm"],
                        nominal_volume_ul=metadata["nominal_volume_ul"],
                        num_items=metadata["num_items"],
                        plate_type=metadata["plate_type"],
                        well_volume_ul=metadata["well_volume_ul"],
                        tip_volume_ul=metadata["tip_volume_ul"],
                        vendor=metadata["vendor"],
                        properties_json=metadata.get("properties_json"),
                    )
                    synced_definitions.append(synced_def)

        await self.db.commit()
        logger.info("Synchronized %d resource definitions.", len(synced_definitions))
        return synced_definitions

    async def _sync_definition(
        self,
        *,
        fqn: str,
        short_name: str,
        description: str | None,
        category: str | None,
        ordering: str | None,
        size_x_mm: float | None,
        size_y_mm: float | None,
        size_z_mm: float | None,
        nominal_volume_ul: float | None,
        num_items: int | None = None,
        plate_type: str | None = None,
        well_volume_ul: float | None = None,
        tip_volume_ul: float | None = None,
        vendor: str | None = None,
        properties_json: dict[str, Any] | None = None,
    ) -> ResourceDefinition:
        """Sync a single resource definition to the database (create or update)."""
        # Extract vendor from FQN if not provided
        if vendor is None:
            vendor = extract_vendor_from_fqn(fqn)

        existing_resource_def_result = await self.db.execute(
            select(ResourceDefinition).filter(ResourceDefinition.fqn == fqn),
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
                num_items=num_items,
                plate_type=plate_type,
                well_volume_ul=well_volume_ul,
                tip_volume_ul=tip_volume_ul,
                vendor=vendor,
            )
            for key, value in update_data.model_dump(exclude_unset=True).items():
                setattr(existing_resource_def, key, value)
            # Store properties_json directly (not in Pydantic model)
            if properties_json is not None:
                existing_resource_def.properties_json = properties_json
            self.db.add(existing_resource_def)
            logger.debug("Updated resource definition: %s", fqn)
            return existing_resource_def
        new_resource_def = ResourceDefinition(
            name=short_name,
            fqn=fqn,
            description=description,
            plr_category=category,
            ordering=ordering,
            size_x_mm=size_x_mm,
            size_y_mm=size_y_mm,
            size_z_mm=size_z_mm,
            nominal_volume_ul=nominal_volume_ul,
            num_items=num_items,
            plate_type=plate_type,
            well_volume_ul=well_volume_ul,
            tip_volume_ul=tip_volume_ul,
            vendor=vendor,
        )
        # Set properties_json after creation (init=False in ORM model)
        if properties_json is not None:
            new_resource_def.properties_json = properties_json
        self.db.add(new_resource_def)
        logger.debug("Added new resource definition: %s", fqn)
        return new_resource_def
