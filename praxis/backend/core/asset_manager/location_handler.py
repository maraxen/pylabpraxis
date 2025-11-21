# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements,logging-fstring-interpolation
# ruff: noqa: E501, FBT001
"""Location constraint handling logic for AssetManager."""

import importlib
import uuid
from typing import TYPE_CHECKING, Any

from pylabrobot.resources import Deck

from praxis.backend.models.orm.resource import ResourceOrm
from praxis.backend.utils.errors import AssetAcquisitionError
from praxis.backend.utils.logging import get_logger

if TYPE_CHECKING:
  from sqlalchemy.ext.asyncio import AsyncSession

  from praxis.backend.core.protocols.workcell_runtime import IWorkcellRuntime
  from praxis.backend.services.resource import ResourceService
  from praxis.backend.services.resource_type_definition import (
    ResourceTypeDefinitionService,
  )

logger = get_logger(__name__)


class LocationHandlerMixin:

  """Mixin for handling location constraints during asset acquisition."""

  # Type hinting for dependencies expected on the main class
  db: "AsyncSession"
  workcell_runtime: "IWorkcellRuntime"
  resource_svc: "ResourceService"
  resource_type_definition_svc: "ResourceTypeDefinitionService"

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

    return (
      target_deck_resource_accession_id,
      target_position_name,
      final_status_details,
    )
