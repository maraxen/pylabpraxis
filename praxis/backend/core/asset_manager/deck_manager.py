# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements,logging-fstring-interpolation
# ruff: noqa: S101
"""Deck management logic for AssetManager."""

import uuid
from typing import TYPE_CHECKING, Any

from pylabrobot.resources import Deck as PLRDeck

from praxis.backend.models.domain.deck import Deck
from praxis.backend.models.domain.resource import (
  Resource,
  ResourceDefinition,
  ResourceStatusEnum,
  ResourceUpdate,
)
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
  ) -> tuple[Deck, Resource, ResourceDefinition]:
    deck_model = await self.deck_svc.get(self.db, deck_orm_accession_id)
    if not deck_model:
      msg = f"Deck ID '{deck_orm_accession_id}' not found."
      raise AssetAcquisitionError(msg)

    deck_resource_model = await self.resource_svc.get(self.db, deck_model.accession_id)
    if not deck_resource_model:
      msg = (
        f"Deck Resource ID '{deck_model.accession_id}' (from Deck '{deck_model.name}') not found."
      )
      raise AssetAcquisitionError(
        msg,
      )

    deck_def_model = await self.resource_type_definition_svc.get_by_name(
      self.db,
      deck_resource_model.name,
    )
    if not deck_def_model or not deck_def_model.fqn:
      msg = f"Resource definition for deck '{deck_resource_model.name}' not found or FQN missing."
      raise AssetAcquisitionError(
        msg,
      )
    return deck_model, deck_resource_model, deck_def_model

  async def apply_deck(
    self,
    deck_orm_accession_id: uuid.UUID,
    protocol_run_accession_id: uuid.UUID,
  ) -> tuple[PLRDeck, Deck]:
    """Apply a deck instanceuration."""
    logger.info(
      "AM_DECK_CONFIG: Applying deck instanceuration ID '%s', for run_accession_id: %s",
      deck_orm_accession_id,
      protocol_run_accession_id,
    )

    deck_model, deck_resource_model, deck_def_model = await self._get_and_validate_deck_orms(
      deck_orm_accession_id,
    )

    if (
      deck_resource_model.status == ResourceStatusEnum.IN_USE
      and deck_resource_model.current_protocol_run_accession_id != protocol_run_accession_id
    ):
      msg = f"Deck resource '{deck_resource_model.name}' is IN_USE by another run."
      raise AssetAcquisitionError(
        msg,
      )

    live_plr_deck_object = await self.workcell_runtime.create_or_get_resource(
      resource_model=deck_resource_model,
      resource_definition_fqn=deck_def_model.fqn,
    )
    if not isinstance(live_plr_deck_object, PLRDeck):
      msg = f"Failed to initialize PLR Deck for '{deck_resource_model.name}'."
      raise AssetAcquisitionError(
        msg,
      )

    parent_machine_accession_id_for_deck: uuid.UUID | None = None
    parent_machine_name_for_log = "N/A (standalone or not specified)"

    update_data = ResourceUpdate(
      status=ResourceStatusEnum.IN_USE,
      current_protocol_run_accession_id=protocol_run_accession_id,
      status_details=f"Deck '{deck_resource_model.name}' "
      f"(parent machine: {parent_machine_name_for_log}) in use for config "
      f"'{deck_model.name}' by run {protocol_run_accession_id}",
      machine_location_accession_id=parent_machine_accession_id_for_deck,
      current_deck_position_name=None,
    )
    await self.resource_svc.update(
      db=self.db,
      db_obj=deck_resource_model,
      obj_in=update_data,
    )
    logger.info(
      "AM_DECK_CONFIG: Deck resource '%s' PLR object initialized and IN_USE.",
      deck_resource_model.name,
    )

    for resource_on_deck_model in deck_model.resources or []:
      await self._process_deck_resource_item(
        resource_on_deck_model,
        protocol_run_accession_id,
        deck_orm_accession_id,
        deck_resource_model,
      )

    logger.info(
      "AM_DECK_CONFIG: Deck configuration for '%s' applied.",
      deck_model.name,
    )
    assert isinstance(
      live_plr_deck_object,
      PLRDeck,
    ), f"Expected live PLR Deck object, got {type(live_plr_deck_object)}"
    return live_plr_deck_object, deck_model

  async def _process_deck_resource_item(
    self,
    item_to_place_model: Resource,
    protocol_run_accession_id: uuid.UUID,
    deck_orm_accession_id: uuid.UUID,
    deck_resource_model: Any,
  ) -> None:
    position_name = item_to_place_model.current_deck_position_name
    if not position_name:
      logger.warning(
        f"Resource {item_to_place_model.name} is on deck but has no position name, skipping.",
      )
      return

    if (
      item_to_place_model.status == ResourceStatusEnum.IN_USE
      and item_to_place_model.current_protocol_run_accession_id == protocol_run_accession_id
      and item_to_place_model.machine_location_accession_id == deck_resource_model.accession_id
      and item_to_place_model.current_deck_position_name == position_name
    ):
      logger.info(
        "Resource %s already configured at '%s' on this deck for this run.",
        item_to_place_model.name,
        position_name,
      )
      return

    if item_to_place_model.status not in [
      ResourceStatusEnum.AVAILABLE_IN_STORAGE,
      ResourceStatusEnum.AVAILABLE_ON_DECK,
    ]:
      msg = (
        f"Resource {item_to_place_model.name} for position "
        f"'{position_name}' unavailable (status: "
        f"{item_to_place_model.status})."
      )
      raise AssetAcquisitionError(
        msg,
      )

    item_def_model = await self.resource_type_definition_svc.get_by_name(
      self.db,
      name=item_to_place_model.fqn,
    )
    if not item_def_model or not item_def_model.fqn:
      msg = f"FQN not found for resource definition '{item_to_place_model.fqn}'."
      raise AssetAcquisitionError(
        msg,
      )

    await self.workcell_runtime.create_or_get_resource(
      resource_model=item_to_place_model,
      resource_definition_fqn=item_def_model.fqn,
    )
    await self.workcell_runtime.assign_resource_to_deck(
      resource_orm_accession_id=item_to_place_model.accession_id,
      target=deck_orm_accession_id,
      position_accession_id=position_name,
    )
    update_data = ResourceUpdate(
      status=ResourceStatusEnum.IN_USE,
      current_protocol_run_accession_id=protocol_run_accession_id,
      machine_location_accession_id=deck_resource_model.accession_id,
      current_deck_position_name=position_name,
      status_details=f"On deck '{deck_resource_model.name}' "
      f"pos '{position_name}' for run {protocol_run_accession_id}",
    )
    await self.resource_svc.update(
      db=self.db,
      db_obj=item_to_place_model,
      obj_in=update_data,
    )
    logger.info(
      "Resource %s configured at '%s' on deck '%s'.",
      item_to_place_model.name,
      position_name,
      deck_resource_model.name,
    )
