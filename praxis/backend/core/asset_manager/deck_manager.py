# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements,logging-fstring-interpolation
# ruff: noqa: G004, S101, ANN401
"""Deck management logic for AssetManager."""

import uuid
from typing import TYPE_CHECKING, Any

from pylabrobot.resources import Deck

from praxis.backend.models.orm.deck import DeckOrm
from praxis.backend.models.orm.resource import (
  ResourceDefinitionOrm,
  ResourceOrm,
  ResourceStatusEnum,
)
from praxis.backend.models.pydantic_internals.resource import ResourceUpdate
from praxis.backend.utils.errors import AssetAcquisitionError
from praxis.backend.utils.logging import get_logger

if TYPE_CHECKING:
  from sqlalchemy.ext.asyncio import AsyncSession

  from praxis.backend.core.protocols.workcell_runtime import IWorkcellRuntime
  from praxis.backend.services.deck import DeckService
  from praxis.backend.services.resource import ResourceService
  from praxis.backend.services.resource_type_definition import (
    ResourceTypeDefinitionService,
  )

logger = get_logger(__name__)


class DeckManagerMixin:

  """Mixin for managing deck application and validation."""

  # Type hinting for dependencies expected on the main class
  db: "AsyncSession"
  workcell_runtime: "IWorkcellRuntime"
  deck_svc: "DeckService"
  resource_svc: "ResourceService"
  resource_type_definition_svc: "ResourceTypeDefinitionService"

  async def _get_and_validate_deck_orms(
    self,
    deck_orm_accession_id: uuid.UUID,
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
      self.db,
      deck_resource_orm.name,
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
      and item_to_place_orm.machine_location_accession_id == deck_resource_orm.accession_id
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
