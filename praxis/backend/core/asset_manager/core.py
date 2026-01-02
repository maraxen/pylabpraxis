# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements,logging-fstring-interpolation
"""Core AssetManager class."""

import importlib
import uuid
from typing import Any

from pylabrobot.resources import Deck
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.core.protocols.asset_lock_manager import IAssetLockManager
from praxis.backend.core.protocols.workcell_runtime import IWorkcellRuntime
from praxis.backend.models.pydantic_internals.asset import (
  AcquireAsset,
  AcquireAssetLock,
)
from praxis.backend.models.pydantic_internals.protocol import AssetRequirementModel
from praxis.backend.services.deck import DeckService
from praxis.backend.services.machine import MachineService
from praxis.backend.services.resource import ResourceService
from praxis.backend.services.resource_type_definition import (
  ResourceTypeDefinitionService,
)
from praxis.backend.utils.errors import AssetAcquisitionError
from praxis.backend.utils.logging import get_logger

from .deck_manager import DeckManagerMixin
from .location_handler import LocationHandlerMixin
from .machine_manager import MachineManagerMixin
from .resource_manager import ResourceManagerMixin

logger = get_logger(__name__)


class AssetManager(
  MachineManagerMixin,
  ResourceManagerMixin,
  DeckManagerMixin,
  LocationHandlerMixin,
):
  """Manages the lifecycle and allocation of assets."""

  def __init__(
    self,
    db_session: AsyncSession,
    workcell_runtime: IWorkcellRuntime,
    deck_service: DeckService,
    machine_service: MachineService,
    resource_service: ResourceService,
    resource_type_definition_service: ResourceTypeDefinitionService,
    asset_lock_manager: IAssetLockManager,
  ) -> None:
    """Initialize the AssetManager."""
    self.db: AsyncSession = db_session
    self.workcell_runtime = workcell_runtime
    self.deck_svc = deck_service
    self.machine_svc = machine_service
    self.resource_svc = resource_service
    self.resource_type_definition_svc = resource_type_definition_service
    self.asset_lock_manager = asset_lock_manager

  async def acquire_asset(
    self,
    protocol_run_accession_id: uuid.UUID,
    asset_requirement: AssetRequirementModel,
  ) -> tuple[Any, uuid.UUID, str]:
    """Dispatch asset acquisition to either acquire_machine or acquire_resource."""
    asset_fqn = asset_requirement.fqn
    logger.info(
      "AM_ACQUIRE_ASSET: Acquiring '%s' (Type/Def: '%s') for run '%s'.",
      asset_requirement.name,
      asset_fqn,
      protocol_run_accession_id,
    )

    resource_def_check = await self.resource_type_definition_svc.get_by_name(
      self.db,
      name=asset_fqn,
    )

    if resource_def_check:
      logger.debug(
        "AM_ACQUIRE_ASSET: '%s' is a cataloged resource. Using acquire_resource.",
        asset_fqn,
      )
      return await self.acquire_resource(
        resource_data=AcquireAsset(
          protocol_run_accession_id=protocol_run_accession_id,
          requested_asset_name_in_protocol=asset_requirement.name,
          fqn=asset_fqn,
          property_constraints=dict(asset_requirement.constraints or {}),
          location_constraints=dict(
            asset_requirement.location_constraints or {},
          ),
          instance_accession_id=getattr(
            asset_requirement,
            "instance_accession_id",
            None,
          ),
        ),
      )
    logger.debug(
      "AM_ACQUIRE_ASSET: '%s' not in ResourceCatalog. Assuming Machine FQN. Using acquire_machine.",
      asset_fqn,
    )
    if "deck" in asset_fqn.lower() or "Deck" in asset_fqn:
      try:
        module_path, class_name = asset_fqn.rsplit(".", 1)
        cls_obj = getattr(importlib.import_module(module_path), class_name)
        if issubclass(cls_obj, Deck):
          msg = f"Asset type '{asset_fqn}' appears to be a Deck but not found in ResourceCatalog. Ensure it's synced."
          raise AssetAcquisitionError(
            msg,
          )
      except (ImportError, AttributeError):
        pass

    return await self.acquire_machine(
      protocol_run_accession_id=protocol_run_accession_id,
      requested_asset_name_in_protocol=asset_requirement.name,
      fqn_constraint=asset_fqn,
    )

  async def lock_asset(
    self,
    asset_type: str,
    asset_name: str,
    protocol_run_id: uuid.UUID,
    reservation_id: uuid.UUID,
  ) -> bool:
    """Lock an asset."""
    lock_data = AcquireAssetLock(
      asset_type=asset_type,
      asset_name=asset_name,
      protocol_run_id=protocol_run_id,
      reservation_id=reservation_id,
    )
    return await self.asset_lock_manager.acquire_asset_lock(lock_data)

  async def unlock_asset(
    self,
    asset_type: str,
    asset_name: str,
    protocol_run_id: uuid.UUID,
    reservation_id: uuid.UUID,
  ) -> bool:
    """Unlock an asset."""
    return await self.asset_lock_manager.release_asset_lock(
      asset_type=asset_type,
      asset_name=asset_name,
      protocol_run_id=protocol_run_id,
      reservation_id=reservation_id,
    )
