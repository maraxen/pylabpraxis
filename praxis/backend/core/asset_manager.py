# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements,logging-fstring-interpolation
"""Manages the lifecycle and allocation of physical laboratory assets."""

import importlib
import uuid
from functools import partial
from typing import Any

from pylabrobot.resources import Deck
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.core.protocols.asset_lock_manager import IAssetLockManager
from praxis.backend.core.protocols.workcell_runtime import IWorkcellRuntime
from praxis.backend.models.orm.deck import DeckOrm
from praxis.backend.models.orm.machine import MachineOrm, MachineStatusEnum
from praxis.backend.models.orm.resource import (
  ResourceDefinitionOrm,
  ResourceOrm,
  ResourceStatusEnum,
)
from praxis.backend.models.pydantic_internals.asset import (
    AcquireAsset,
    AcquireAssetLock,
)
from praxis.backend.models.pydantic_internals.filters import SearchFilters
from praxis.backend.models.pydantic_internals.protocol import AssetRequirementModel
from praxis.backend.models.pydantic_internals.resource import ResourceUpdate
from praxis.backend.services.deck import DeckService
from praxis.backend.services.machine import MachineService
from praxis.backend.services.resource import ResourceService
from praxis.backend.services.resource_type_definition import (
  ResourceTypeDefinitionService,
)
from praxis.backend.utils.errors import (
  AssetAcquisitionError,
  AssetReleaseError,
)
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors, log_runtime_errors

logger = get_logger(__name__)


async_asset_manager_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  raises_exception=AssetAcquisitionError,
)

asset_manager_errors = partial(
  log_runtime_errors,
  logger_instance=logger,
  raises_exception=AssetAcquisitionError,
)


class AssetManager:

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

  async def _get_and_validate_deck_orms(
    self, deck_orm_accession_id: uuid.UUID,
  ) -> tuple[DeckOrm, ResourceOrm, ResourceDefinitionOrm]:
    deck_orm = await self.deck_svc.get(self.db, deck_orm_accession_id)
    if not deck_orm:
      msg = f"Deck ID '{deck_orm_accession_id}' not found."
      raise AssetAcquisitionError(msg)

    deck_resource_orm = await self.resource_svc.get(self.db, deck_orm.accession_id)
    if not deck_resource_orm:
      msg = f"Deck Resource ID '{deck_orm.accession_id}' (from Deck '{deck_orm.name}') not found."
      raise AssetAcquisitionError(
        msg,
      )

    deck_def_orm = await self.resource_type_definition_svc.get_by_name(
        self.db, deck_resource_orm.name,
    )
    if not deck_def_orm or not deck_def_orm.fqn:
      msg = f"Resource definition for deck '{deck_resource_orm.name}' not found or FQN missing."
      raise AssetAcquisitionError(
        msg,
      )
    return deck_orm, deck_resource_orm, deck_def_orm

  async def apply_deck(
    self,
    deck_orm_accession_id: uuid.UUID,
    protocol_run_accession_id: uuid.UUID,
  ) -> Deck:
    """Apply a deck instanceuration."""
    logger.info(
      "AM_DECK_CONFIG: Applying deck instanceuration ID '%s', for run_accession_id: %s",
      deck_orm_accession_id,
      protocol_run_accession_id,
    )

    deck_orm, deck_resource_orm, deck_def_orm = await self._get_and_validate_deck_orms(
      deck_orm_accession_id,
    )

    if (
      deck_resource_orm.status == ResourceStatusEnum.IN_USE
      and deck_resource_orm.current_protocol_run_accession_id != protocol_run_accession_id
    ):
      msg = f"Deck resource '{deck_resource_orm.name}' is IN_USE by another run."
      raise AssetAcquisitionError(
        msg,
      )

    live_plr_deck_object = await self.workcell_runtime.create_or_get_resource(
      resource_orm=deck_resource_orm,
      resource_definition_fqn=deck_def_orm.fqn,
    )
    if not isinstance(live_plr_deck_object, Deck):
      msg = f"Failed to initialize PLR Deck for '{deck_resource_orm.name}'."
      raise AssetAcquisitionError(
        msg,
      )

    parent_machine_accession_id_for_deck: uuid.UUID | None = None
    parent_machine_name_for_log = "N/A (standalone or not specified)"

    update_data = ResourceUpdate(
        status=ResourceStatusEnum.IN_USE,
        current_protocol_run_accession_id=protocol_run_accession_id,
        status_details=f"Deck '{deck_resource_orm.name}' "
        f"(parent machine: {parent_machine_name_for_log}) in use for config "
        f"'{deck_orm.name}' by run {protocol_run_accession_id}",
        machine_location_accession_id=parent_machine_accession_id_for_deck,
        current_deck_position_name=None,
    )
    await self.resource_svc.update(
      db=self.db,
      db_obj=deck_resource_orm,
      obj_in=update_data,
    )
    logger.info(
      "AM_DECK_CONFIG: Deck resource '%s' PLR object initialized and IN_USE.",
      deck_resource_orm.name,
    )

    for resource_on_deck_orm in deck_orm.resources or []:
      await self._process_deck_resource_item(
        resource_on_deck_orm,
        protocol_run_accession_id,
        deck_orm_accession_id,
        deck_resource_orm,
      )

    logger.info(
      "AM_DECK_CONFIG: Deck configuration for '%s' applied.",
      deck_orm.name,
    )
    assert isinstance(
      live_plr_deck_object,
      Deck,
    ), f"Expected live PLR Deck object, got {type(live_plr_deck_object)}"
    return live_plr_deck_object

  async def _process_deck_resource_item(
    self,
    item_to_place_orm: ResourceOrm,
    protocol_run_accession_id: uuid.UUID,
    deck_orm_accession_id: uuid.UUID,
    deck_resource_orm: Any,
  ) -> None:
    position_name = item_to_place_orm.current_deck_position_name
    if not position_name:
      logger.warning(
        f"Resource {item_to_place_orm.name} is on deck but has no position name, skipping.",
      )
      return

    if (
      item_to_place_orm.status == ResourceStatusEnum.IN_USE
      and item_to_place_orm.current_protocol_run_accession_id == protocol_run_accession_id
      and item_to_place_orm.machine_location_accession_id
      == deck_resource_orm.accession_id
      and item_to_place_orm.current_deck_position_name == position_name
    ):
      logger.info(
        "Resource %s already configured at '%s' on this deck for this run.",
        item_to_place_orm.name,
        position_name,
      )
      return

    if item_to_place_orm.status not in [
      ResourceStatusEnum.AVAILABLE_IN_STORAGE,
      ResourceStatusEnum.AVAILABLE_ON_DECK,
    ]:
      msg = (
        f"Resource {item_to_place_orm.name} for position "
        f"'{position_name}' unavailable (status: "
        f"{item_to_place_orm.status})."
      )
      raise AssetAcquisitionError(
        msg,
      )

    item_def_orm = await self.resource_type_definition_svc.get_by_name(
      self.db,
      name=item_to_place_orm.fqn,
    )
    if not item_def_orm or not item_def_orm.fqn:
      msg = f"FQN not found for resource definition '{item_to_place_orm.fqn}'."
      raise AssetAcquisitionError(
        msg,
      )

    await self.workcell_runtime.create_or_get_resource(
      resource_orm=item_to_place_orm,
      resource_definition_fqn=item_def_orm.fqn,
    )
    await self.workcell_runtime.assign_resource_to_deck(
      resource_orm_accession_id=item_to_place_orm.accession_id,
      target=deck_orm_accession_id,
      position_accession_id=position_name,
    )
    update_data = ResourceUpdate(
        status=ResourceStatusEnum.IN_USE,
        current_protocol_run_accession_id=protocol_run_accession_id,
        machine_location_accession_id=deck_resource_orm.accession_id,
        current_deck_position_name=position_name,
        status_details=f"On deck '{deck_resource_orm.name}' "
        f"pos '{position_name}' for run {protocol_run_accession_id}",
    )
    await self.resource_svc.update(
      db=self.db,
      db_obj=item_to_place_orm,
      obj_in=update_data,
    )
    logger.info(
      "Resource %s configured at '%s' on deck '%s'.",
      item_to_place_orm.name,
      position_name,
      deck_resource_orm.name,
    )

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
        }
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
          }
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
        msg = f"No machine found for FQN '{fqn_constraint}' (Status: AVAILABLE or IN_USE by this run)."
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

  async def _find_resource_to_acquire(
    self,
    protocol_run_accession_id: uuid.UUID,
    fqn: str,
    user_choice_instance_accession_id: uuid.UUID | None,
    property_constraints: dict[str, Any] | None,
  ) -> ResourceOrm | None:
    if user_choice_instance_accession_id:
      instance_orm = await self.resource_svc.get(
        self.db,
        user_choice_instance_accession_id,
      )
      if not instance_orm:
        msg = f"Specified resource ID {user_choice_instance_accession_id} not found."
        raise AssetAcquisitionError(
          msg,
        )
      if instance_orm.fqn != fqn:
        msg = (
          f"Chosen instance {user_choice_instance_accession_id} (Def: {instance_orm.fqn}) "
          f"mismatches constraint {fqn}."
        )
        raise AssetAcquisitionError(
          msg,
        )
      if instance_orm.status == ResourceStatusEnum.IN_USE:
        if instance_orm.current_protocol_run_accession_id != uuid.UUID(
          str(protocol_run_accession_id),
        ):
          msg = f" {user_choice_instance_accession_id} IN_USE by another run."
          raise AssetAcquisitionError(
            msg,
          )
      elif instance_orm.status not in [
        ResourceStatusEnum.AVAILABLE_IN_STORAGE,
        ResourceStatusEnum.AVAILABLE_ON_DECK,
      ]:
        msg = (
          f"Chosen instance {user_choice_instance_accession_id} not available (Status: "
          f"{instance_orm.status.name})."
        )
        raise AssetAcquisitionError(
          msg,
        )
      return instance_orm
    filters = SearchFilters(
        search_filters={
            "fqn": fqn,
            "status": ResourceStatusEnum.IN_USE,
            "current_protocol_run_accession_id_filter": str(protocol_run_accession_id),
        },
        property_filters=property_constraints,
    )
    in_use_list = await self.resource_svc.get_multi(
      self.db,
      filters=filters,
    )
    if in_use_list:
      return in_use_list[0]
    filters = SearchFilters(
        search_filters={"fqn": fqn, "status": ResourceStatusEnum.AVAILABLE_ON_DECK},
        property_filters=property_constraints,
    )
    on_deck_list = await self.resource_svc.get_multi(
      self.db,
      filters=filters,
    )
    if on_deck_list:
      return on_deck_list[0]
    filters = SearchFilters(
        search_filters={"fqn": fqn, "status": ResourceStatusEnum.AVAILABLE_IN_STORAGE},
        property_filters=property_constraints,
    )
    in_storage_list = await self.resource_svc.get_multi(
      self.db,
      filters=filters,
    )
    if in_storage_list:
      return in_storage_list[0]
    return None

  async def _update_resource_acquisition_status(
    self,
    resource_to_acquire: ResourceOrm,
    protocol_run_accession_id: uuid.UUID,
    target_deck_resource_accession_id: uuid.UUID | None,
    target_position_name: str | None,
    final_status_details: str,
  ) -> ResourceOrm:
    update_data = ResourceUpdate(
        status=ResourceStatusEnum.IN_USE,
        current_protocol_run_accession_id=protocol_run_accession_id,
        machine_location_accession_id=target_deck_resource_accession_id,
        current_deck_position_name=target_position_name,
        status_details=final_status_details,
    )
    updated_resource = await self.resource_svc.update(
      db=self.db,
      db_obj=resource_to_acquire,
      obj_in=update_data,
    )
    if not updated_resource:
      msg = f"CRITICAL: Failed to update DB status for resource '{resource_to_acquire.name}'."
      raise AssetAcquisitionError(
        msg,
      )
    return updated_resource

  async def acquire_resource(
    self,
    resource_data: AcquireAsset,
  ) -> tuple[Any, uuid.UUID, str]:
    """Acquire a resource instance that is available."""
    logger.info(
      "AM_ACQUIRE_RESOURCE: Acquiring '%s' (Def: '%s') for run '%s'. Loc: %s",
      resource_data.requested_asset_name_in_protocol,
      resource_data.fqn,
      resource_data.protocol_run_accession_id,
      resource_data.location_constraints,
    )

    resource_to_acquire = await self._find_resource_to_acquire(
      resource_data.protocol_run_accession_id,
      resource_data.fqn,
      resource_data.user_choice_instance_accession_id,
      resource_data.property_constraints,
    )

    if not resource_to_acquire:
      msg = f"No instance found for definition '{resource_data.fqn}' matching criteria for run '{resource_data.protocol_run_accession_id}'."
      raise AssetAcquisitionError(
        msg,
      )

    resource_def_orm = await self.resource_type_definition_svc.get_by_name(
      self.db,
      name=resource_to_acquire.fqn,
    )
    if not resource_def_orm or not resource_def_orm.fqn:
      update_data = ResourceUpdate(
          status=ResourceStatusEnum.ERROR,
          status_details=f"FQN missing for def {resource_to_acquire.fqn}",
      )
      await self.resource_svc.update(
        db=self.db,
        db_obj=resource_to_acquire,
        obj_in=update_data,
      )
      msg = f"FQN not found for resource definition '{resource_to_acquire.fqn}'."
      raise AssetAcquisitionError(
        msg,
      )

    live_plr_resource = await self.workcell_runtime.create_or_get_resource(
      resource_orm=resource_to_acquire,
      resource_definition_fqn=resource_def_orm.fqn,
    )
    if not live_plr_resource:
      update_data = ResourceUpdate(
          status=ResourceStatusEnum.ERROR,
          status_details="PLR object creation failed.",
      )
      await self.resource_svc.update(
        db=self.db,
        db_obj=resource_to_acquire,
        obj_in=update_data,
      )
      msg = f"Failed to create/get PLR object for '{resource_to_acquire.name}'."
      raise AssetAcquisitionError(
        msg,
      )

    target_deck_resource_accession_id: uuid.UUID | None = None
    target_position_name: str | None = None
    final_status_details = f"In use by run {resource_data.protocol_run_accession_id}"
    is_acquiring_a_deck_resource = isinstance(live_plr_resource, Deck)

    (
      target_deck_resource_accession_id,
      target_position_name,
      final_status_details,
    ) = await self._handle_location_constraints(
      is_acquiring_a_deck_resource,
      resource_data.location_constraints,
      resource_to_acquire,
      resource_data.protocol_run_accession_id,
    )

    needs_db_update = not (
      resource_to_acquire.status == ResourceStatusEnum.IN_USE
      and resource_to_acquire.current_protocol_run_accession_id
      == uuid.UUID(str(resource_data.protocol_run_accession_id))
      and (
        is_acquiring_a_deck_resource
        or (
          resource_to_acquire.machine_location_accession_id == target_deck_resource_accession_id
          and resource_to_acquire.current_deck_position_name == target_position_name
        )
      )
    )

    if needs_db_update:
      resource_to_acquire = await self._update_resource_acquisition_status(
        resource_to_acquire=resource_to_acquire,
        protocol_run_accession_id=resource_data.protocol_run_accession_id,
        target_deck_resource_accession_id=target_deck_resource_accession_id,
        target_position_name=target_position_name,
        final_status_details=final_status_details,
      )

    logger.info(
      "AM_ACQUIRE_RESOURCE: Resource '%s' (ID: %s) acquired. Status: IN_USE.",
      resource_to_acquire.name,
      resource_to_acquire.accession_id,
    )
    return live_plr_resource, resource_to_acquire.accession_id, "resource"

  async def _handle_location_constraints(
    self,
    is_acquiring_a_deck_resource: bool,
    location_constraints: dict[str, Any] | None,
    resource_to_acquire: ResourceOrm,
    protocol_run_accession_id: uuid.UUID,
  ) -> tuple[uuid.UUID | None, str | None, str]:
    target_deck_resource_accession_id: uuid.UUID | None = None
    target_position_name: str | None = None
    final_status_details = f"In use by run {protocol_run_accession_id}"

    if not is_acquiring_a_deck_resource and location_constraints:
      deck_user_name = location_constraints.get("deck_name")
      position_on_deck = location_constraints.get("position_name")
      if deck_user_name and position_on_deck:
        target_deck = await self.resource_svc.get_by_name(
          self.db,
          name=deck_user_name,
        )
        if not target_deck:
          msg = f"Target deck resource '{deck_user_name}' not found."
          raise AssetAcquisitionError(
            msg,
          )
        target_deck_def = await self.resource_type_definition_svc.get_by_name(
          self.db,
          name=target_deck.fqn,
        )
        if not target_deck_def or not (
          (target_deck_def.plr_category and "Deck" in target_deck_def.plr_category)
          or issubclass(
            importlib.import_module(
              target_deck_def.fqn.rsplit(".", 1)[0],
            ).__getattribute__(target_deck_def.fqn.rsplit(".", 1)[1]),
            Deck,
          )
        ):
          msg = f"Target '{deck_user_name}' is not a deck type."
          raise AssetAcquisitionError(msg)
        target_deck_resource_accession_id = target_deck.accession_id
        target_position_name = position_on_deck
        await self.workcell_runtime.assign_resource_to_deck(
          resource_orm_accession_id=resource_to_acquire.accession_id,
          target=target_deck_resource_accession_id,
          position_accession_id=target_position_name,
        )
        final_status_details = f"On deck '{deck_user_name}' pos '{target_position_name}' for run {protocol_run_accession_id}"
      elif deck_user_name or position_on_deck:
        msg = "Partial location constraint: 'deck_name' and 'position_name' required."
        raise AssetAcquisitionError(
          msg,
        )
    elif is_acquiring_a_deck_resource and location_constraints:
      logger.warning(
        "AM_ACQUIRE_RESOURCE: Location constraints ignored for acquiring a Deck resource '%s'.",
        resource_to_acquire.name,
      )
      target_deck_resource_accession_id = None
      target_position_name = None

    return target_deck_resource_accession_id, target_position_name, final_status_details

  def _is_deck_resource(self, resource_def_orm: ResourceDefinitionOrm | None) -> bool:
    if not resource_def_orm or not resource_def_orm.fqn:
      return False
    try:
      module_path, class_name = resource_def_orm.fqn.rsplit(".", 1)
      plr_class = getattr(importlib.import_module(module_path), class_name)
      return issubclass(plr_class, Deck)
    except (ImportError, AttributeError):
      return False

  async def _handle_resource_release_location(
    self,
    is_releasing_a_deck_resource: bool,
    resource_to_release: ResourceOrm,
    resource_orm_accession_id: uuid.UUID,
    clear_from_accession_id: uuid.UUID | None,
    clear_from_position_name: str | None,
  ) -> tuple[uuid.UUID | None, str | None]:
    if is_releasing_a_deck_resource:
      logger.info(
        "AM_RELEASE_RESOURCE: '%s' is a Deck resource. Clearing its WCR state.",
        resource_to_release.name,
      )
      await self.workcell_runtime.clear_resource(
        resource_orm_accession_id,
      )
      return None, None
    if clear_from_accession_id and clear_from_position_name:
      logger.info(
        "AM_RELEASE_RESOURCE: Clearing '%s' from deck ID %s, pos '%s'.",
        resource_to_release.name,
        clear_from_accession_id,
        clear_from_position_name,
      )
      await self.workcell_runtime.clear_deck_position(
        deck_orm_accession_id=clear_from_accession_id,
        position_name=clear_from_position_name,
        resource_orm_accession_id=resource_orm_accession_id,
      )
      return clear_from_accession_id, clear_from_position_name
    await self.workcell_runtime.clear_resource(
      resource_orm_accession_id,
    )
    return None, None

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

  async def release_resource(
    self,
    resource_orm_accession_id: uuid.UUID,
    final_status: ResourceStatusEnum,
    final_properties_json_update: dict[str, Any] | None = None,
    clear_from_accession_id: uuid.UUID | None = None,
    clear_from_position_name: str | None = None,
    status_details: str | None = "Released from run",
  ) -> None:
    """Release a resource instance."""
    resource_to_release = await self.resource_svc.get(
      self.db,
      resource_orm_accession_id,
    )
    if not resource_to_release:
      logger.warning(
        "AM_RELEASE_RESOURCE: Resource instance ID %s not found.",
        resource_orm_accession_id,
      )
      return
    logger.info(
      "AM_RELEASE_RESOURCE: Releasing '%s' (ID %s, Type %s), final status: %s.",
      resource_to_release.name,
      resource_orm_accession_id,
      resource_to_release.fqn,
      final_status.name,
    )

    resource_def_orm = await self.resource_type_definition_svc.get_by_name(
      self.db,
      name=resource_to_release.fqn,
    )
    is_releasing_a_deck_resource = self._is_deck_resource(resource_def_orm)

    (
      clear_from_accession_id,
      clear_from_position_name,
    ) = await self._handle_resource_release_location(
      is_releasing_a_deck_resource,
      resource_to_release,
      resource_orm_accession_id,
      clear_from_accession_id,
      clear_from_position_name,
    )

    final_loc_accession_id_for_ads: uuid.UUID | None = None
    final_pos_for_ads: str | None = None
    if not is_releasing_a_deck_resource and final_status == ResourceStatusEnum.AVAILABLE_ON_DECK:
      final_loc_accession_id_for_ads = clear_from_accession_id
      final_pos_for_ads = clear_from_position_name

    update_data = ResourceUpdate(
        status=final_status,
        machine_location_accession_id=final_loc_accession_id_for_ads,
        current_deck_position_name=final_pos_for_ads,
        current_protocol_run_accession_id=None,
        status_details=status_details,
    )
    if final_properties_json_update:
        update_data.properties_json = resource_to_release.properties_json or {}
        update_data.properties_json.update(final_properties_json_update)

    updated_resource = await self.resource_svc.update(
      db=self.db,
      db_obj=resource_to_release,
      obj_in=update_data,
    )
    if not updated_resource:
      msg = f"Failed to update DB for resource ID {resource_orm_accession_id} on release."
      raise AssetReleaseError(
        msg,
      )
    logger.info(
      "AM_RELEASE_RESOURCE: Resource '%s' released, status %s.",
      updated_resource.name,
      final_status.name,
    )

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

    resource_def_check = await self.resource_type_definition_svc.get_by_name(self.db, name=asset_fqn)

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
          location_constraints=dict(asset_requirement.location_constraints or {}),
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
