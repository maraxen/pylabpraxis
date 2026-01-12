"""Asset acquisition logic for the Orchestrator."""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.core.asset_manager import AssetManager
from praxis.backend.models import (
  FunctionProtocolDefinitionCreate,
)
from praxis.backend.utils.errors import AssetAcquisitionError
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)


class AssetAcquisitionMixin:
  """Mixin for asset acquisition and deck configuration."""

  # Type hints for dependencies
  asset_manager: AssetManager

  async def _acquire_assets(
    self,
    protocol_pydantic_def: FunctionProtocolDefinitionCreate,
    protocol_run_accession_id: uuid.UUID,
    final_args: dict[str, Any],
    acquired_assets_details: dict[uuid.UUID, Any],
  ) -> None:
    """Acquire assets required by the protocol."""
    for asset_req_model in protocol_pydantic_def.assets:
      try:
        logger.info(
          "ORCH-ACQUIRE: Acquiring asset '%s' (Type: '%s', Optional: %s) for run '%s'.",
          asset_req_model.name,
          asset_req_model.fqn,
          asset_req_model.optional,
          protocol_run_accession_id,
        )
        (
          live_obj,
          model_accession_id,
          asset_kind_str,
        ) = await self.asset_manager.acquire_asset(
          protocol_run_accession_id=protocol_run_accession_id,
          asset_requirement=asset_req_model,
        )
        final_args[asset_req_model.name] = live_obj
        acquired_assets_details[model_accession_id] = {
          "type": asset_kind_str,
          "model_accession_id": model_accession_id,
          "name_in_protocol": asset_req_model.name,
        }
        logger.info(
          "ORCH-ACQUIRE: Asset '%s' (Kind: %s, ORM ID: %s) acquired: %s",
          asset_req_model.name,
          asset_kind_str,
          model_accession_id,
          live_obj,
        )
      except AssetAcquisitionError as e:
        if asset_req_model.optional:
          logger.warning(
            "ORCH-ACQUIRE: Optional asset '%s' could not be acquired: %s. Proceeding as it's optional.",
            asset_req_model.name,
            e,
          )
          final_args[asset_req_model.name] = None
        else:
          error_msg = (
            f"Failed to acquire mandatory asset '{asset_req_model.name}' for "
            f"protocol '{protocol_pydantic_def.name}': {e}"
          )
          logger.exception(error_msg)
          raise ValueError(error_msg) from e
      except Exception as e_general:
        error_msg = (
          f"Unexpected error acquiring asset '{asset_req_model.name}' for "
          f"protocol '{protocol_pydantic_def.name}': {e_general}"
        )
        logger.exception(error_msg)
        raise ValueError(error_msg) from e_general

  async def _handle_deck_preconfiguration(
    self,
    db_session: AsyncSession,
    protocol_pydantic_def: FunctionProtocolDefinitionCreate,
    input_parameters: dict[str, Any],
    protocol_run_accession_id: uuid.UUID,
    final_args: dict[str, Any],
  ) -> None:
    """Handle deck preconfiguration if specified in the protocol definition."""
    if protocol_pydantic_def.preconfigure_deck and protocol_pydantic_def.deck_param_name:
      deck_param_name = protocol_pydantic_def.deck_param_name
      deck_accession_identifier_from_user = input_parameters.get(deck_param_name)

      if deck_accession_identifier_from_user is None and not next(
        (p for p in protocol_pydantic_def.parameters if p.name == deck_param_name and p.optional),
        False,
      ):
        error_msg = (
          f"Mandatory deck parameter '{deck_param_name}' for preconfiguration not provided."
        )
        raise ValueError(error_msg)

      if deck_accession_identifier_from_user is not None:
        if not isinstance(deck_accession_identifier_from_user, str | uuid.UUID):
          error_msg = (
            f"Deck identifier for preconfiguration ('{deck_param_name}') must be "
            f"a string (name) or UUID (ID), got {type(deck_accession_identifier_from_user)}."
          )
          raise ValueError(error_msg)

        logger.info(
          "ORCH-DECK: Applying deck instantiation '%s' for run '%s'.",
          deck_accession_identifier_from_user,
          protocol_run_accession_id,
        )

        deck_config_orm_accession_id_to_apply: uuid.UUID | None = None
        if isinstance(deck_accession_identifier_from_user, str):
          deck_config_model = await self.asset_manager.deck_svc.get_by_name(
            db_session,
            deck_accession_identifier_from_user,
          )
          if not deck_config_model:
            error_msg = (
              f"Deck configuration named '{deck_accession_identifier_from_user}' not found."
            )
            raise ValueError(error_msg)
          deck_config_orm_accession_id_to_apply = deck_config_model.accession_id
        elif isinstance(deck_accession_identifier_from_user, uuid.UUID):
          deck_config_orm_accession_id_to_apply = deck_accession_identifier_from_user

        if deck_config_orm_accession_id_to_apply is None:
          msg = "Internal error: Deck accession ID not resolved."
          raise RuntimeError(msg)

        live_deck_object = await self.asset_manager.apply_deck(
          deck_orm_accession_id=deck_config_orm_accession_id_to_apply,
          protocol_run_accession_id=protocol_run_accession_id,
        )
        final_args[deck_param_name] = live_deck_object
        logger.info(
          "ORCH-DECK: Deck '%s' configured and injected as '%s'.",
          live_deck_object.name,
          deck_param_name,
        )
      elif deck_param_name in final_args:
        logger.warning(
          "Deck parameter '%s' was already processed (e.g., as an asset). Review protocol definition.",
          deck_param_name,
        )
