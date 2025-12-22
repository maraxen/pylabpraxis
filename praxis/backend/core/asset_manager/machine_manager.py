# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements,logging-fstring-interpolation
"""Machine management logic for AssetManager."""

import importlib
import uuid
from typing import TYPE_CHECKING, Any

from pylabrobot.resources import Deck

from praxis.backend.models.orm.machine import MachineOrm, MachineStatusEnum
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.utils.errors import AssetAcquisitionError, AssetReleaseError
from praxis.backend.utils.logging import get_logger

if TYPE_CHECKING:
  from sqlalchemy.ext.asyncio import AsyncSession

  from praxis.backend.core.protocols.workcell_runtime import IWorkcellRuntime
  from praxis.backend.services.machine import MachineService
  from praxis.backend.services.resource_type_definition import (
    ResourceTypeDefinitionService,
  )

logger = get_logger(__name__)


class MachineManagerMixin:

  """Mixin for managing machine acquisition and release."""

  # Type hinting for dependencies expected on the main class
  db: "AsyncSession"
  workcell_runtime: "IWorkcellRuntime"
  machine_svc: "MachineService"
  resource_type_definition_svc: "ResourceTypeDefinitionService"

  async def acquire_machine(
    self,
    protocol_run_accession_id: uuid.UUID,
    requested_asset_name_in_protocol: str,
    fqn_constraint: str,
  ) -> tuple[Any, uuid.UUID, str]:
    """Acquire a Machine that is available or already in use by the current run."""
    logger.info(
      "AM_ACQUIRE_MACHINE: Acquiring machine '%s' (FQN: '%s') for run '%s'.",
      requested_asset_name_in_protocol,
      fqn_constraint,
      protocol_run_accession_id,
    )

    try:
      module_path, class_name = fqn_constraint.rsplit(".", 1)
      module = importlib.import_module(module_path)
      cls_obj = getattr(module, class_name)
      if issubclass(cls_obj, Deck):
        msg = f"Attempted to acquire Deck FQN '{fqn_constraint}' via acquire_machine. Use acquire_resource."
        raise AssetAcquisitionError(
          msg,
        )
    except (ImportError, AttributeError, ValueError) as e:
      logger.warning(
        f"Could not dynamically verify FQN '{fqn_constraint}' during machine acquisition safeguard: {e}",
      )
    potential_deck_def = await self.resource_type_definition_svc.get_by_name(
      self.db,
      fqn_constraint,
    )
    if potential_deck_def and (
      (potential_deck_def.plr_category and "Deck" in potential_deck_def.plr_category)
      or (potential_deck_def.fqn and "deck" in potential_deck_def.fqn.lower())
    ):
      msg = f"FQN '{fqn_constraint}' matches a cataloged Deck resource. Use acquire_resource."
      raise AssetAcquisitionError(
        msg,
      )

    selected_machine_orm: MachineOrm | None = None
    filters = SearchFilters(
      search_filters={
        "pylabrobot_class_filter": fqn_constraint,
        "status": MachineStatusEnum.IN_USE,
        "current_protocol_run_accession_id_filter": protocol_run_accession_id,
      },
    )
    in_use_by_this_run_list = await self.machine_svc.get_multi(
      self.db,
      filters=filters,
    )
    if in_use_by_this_run_list:
      selected_machine_orm = in_use_by_this_run_list[0]
    else:
      filters = SearchFilters(
        search_filters={
          "status": MachineStatusEnum.AVAILABLE,
          "pylabrobot_class_filter": fqn_constraint,
        },
      )
      available_machines_list = await self.machine_svc.get_multi(
        self.db,
        filters=filters,
      )
      if available_machines_list:
        selected_machine_orm = available_machines_list[0]
        if selected_machine_orm:
          logger.info(
            "AM_ACQUIRE_DEVICE: Found available machine '%s' (ID: %s).",
            selected_machine_orm.name,
            selected_machine_orm.accession_id,
          )
      else:
        msg = (
          f"No machine found for FQN '{fqn_constraint}' (Status: AVAILABLE or IN_USE by this run)."
        )
        raise AssetAcquisitionError(
          msg,
        )

    if not selected_machine_orm:
      msg = f"Machine selection failed for '{requested_asset_name_in_protocol}'."
      raise AssetAcquisitionError(
        msg,
      )

    live_plr_machine = await self.workcell_runtime.initialize_machine(
      selected_machine_orm,
    )
    if not live_plr_machine:
      await self.machine_svc.update_machine_status(
        self.db,
        selected_machine_orm.accession_id,
        MachineStatusEnum.ERROR,
        status_details=f"Backend init failed for run {protocol_run_accession_id}.",
      )
      msg = f"Failed to initialize backend for machine '{selected_machine_orm.name}'."
      raise AssetAcquisitionError(
        msg,
      )

    if (
      selected_machine_orm.status != MachineStatusEnum.IN_USE
      or selected_machine_orm.current_protocol_run_accession_id
      != uuid.UUID(str(protocol_run_accession_id))
    ):
      updated_machine_orm = await self.machine_svc.update_machine_status(
        self.db,
        selected_machine_orm.accession_id,
        MachineStatusEnum.IN_USE,
        current_protocol_run_accession_id=uuid.UUID(str(protocol_run_accession_id)),
        status_details=f"In use by run {protocol_run_accession_id}",
      )
      if not updated_machine_orm:
        msg = f"CRITICAL: Failed to update DB status for machine '{selected_machine_orm.name}'."
        raise AssetAcquisitionError(
          msg,
        )
      selected_machine_orm = updated_machine_orm

    logger.info(
      "AM_ACQUIRE_MACHINE: Machine '%s' acquired for run '%s'.",
      selected_machine_orm.name,
      protocol_run_accession_id,
    )
    return live_plr_machine, selected_machine_orm.accession_id, "machine"

  async def release_machine(
    self,
    machine_orm_accession_id: uuid.UUID,
    final_status: MachineStatusEnum = MachineStatusEnum.AVAILABLE,
    status_details: str | None = "Released from run",
  ) -> None:
    """Release a Machine (not a Deck)."""
    machine_to_release = await self.machine_svc.get(self.db, machine_orm_accession_id)
    if not machine_to_release:
      logger.warning(
        f"AM_RELEASE_MACHINE: Machine ID {machine_orm_accession_id} not found.",
      )
      return

    logger.info(
      "AM_RELEASE_MACHINE: Releasing machine '%s' (ID %s), final status: %s.",
      machine_to_release.name,
      machine_orm_accession_id,
      final_status.name,
    )
    if "deck" in machine_to_release.fqn.lower() or "Deck" in machine_to_release.fqn:
      logger.error(
        f"AM_RELEASE_MACHINE: Attempt to release Deck-like FQN "
        f"'{machine_to_release.fqn}' via release_machine. Use release_resource.",
      )
      return

    await self.workcell_runtime.shutdown_machine(machine_orm_accession_id)
    updated_machine = await self.machine_svc.update_machine_status(
      self.db,
      machine_orm_accession_id,
      final_status,
      status_details=status_details,
      current_protocol_run_accession_id=None,
    )
    if not updated_machine:
      msg = f"Failed to update DB status for machine ID {machine_orm_accession_id} after shutdown."
      raise AssetReleaseError(
        msg,
      )
    logger.info(
      "AM_RELEASE_MACHINE: Machine '%s' released, status %s.",
      updated_machine.name,
      final_status.name,
    )
