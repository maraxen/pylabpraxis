"""Protocol preparation logic for the Orchestrator."""

import uuid
from collections.abc import Callable
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.core.protocol_code_manager import ProtocolCodeManager
from praxis.backend.core.run_context import PraxisRunContext
from praxis.backend.core.workcell_runtime import WorkcellRuntime
from praxis.backend.models import (
  FunctionProtocolDefinitionCreate,
  FunctionProtocolDefinitionOrm,
  ProtocolRunOrm,
)
from praxis.backend.services.protocol_definition import ProtocolDefinitionCRUDService
from praxis.backend.services.state import PraxisState
from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)


class ProtocolPreparationMixin:
  """Mixin for protocol preparation and argument processing."""

  # Type hints for dependencies expected from the main class
  protocol_code_manager: ProtocolCodeManager
  workcell_runtime: WorkcellRuntime
  protocol_definition_service: ProtocolDefinitionCRUDService

  async def _get_protocol_definition_orm_from_db(
    self,
    db_session: AsyncSession,
    protocol_name: str,
    version: str | None = None,
    commit_hash: str | None = None,
    source_name: str | None = None,
  ) -> FunctionProtocolDefinitionOrm | None:
    """Retrieve a protocol definition ORM from the database."""
    logger.debug(
      "Fetching protocol ORM: Name='%s', Version='%s', Commit='%s', Source='%s'",
      protocol_name,
      version,
      commit_hash,
      source_name,
    )
    return await self.protocol_definition_service.get_by_name(
      db=db_session,
      name=protocol_name,
      version=version,
      commit_hash=commit_hash,
    )

  async def _prepare_protocol_code(
    self,
    protocol_def_orm: FunctionProtocolDefinitionOrm,
  ) -> tuple[Callable, FunctionProtocolDefinitionCreate]:
    """Load the protocol code from its source using the ProtocolCodeManager."""
    return await self.protocol_code_manager.prepare_protocol_code(protocol_def_orm)

  async def _initialize_run_context(
    self,
    protocol_run_orm: ProtocolRunOrm,
    initial_state_data: dict[str, Any],
    db_session: AsyncSession,
  ) -> PraxisRunContext:
    """Initialize PraxisState and PraxisRunContext for a protocol run."""
    praxis_state = PraxisState(run_accession_id=protocol_run_orm.accession_id)
    if initial_state_data:
      praxis_state.update(initial_state_data)

    logger.debug(
      "Initializing PraxisState for run %s with initial data: %s",
      protocol_run_orm.accession_id,
      initial_state_data,
    )

    if praxis_state is None:
      error_msg = "Failed to initialize PraxisState for the protocol run."
      logger.error(error_msg)
      raise RuntimeError(error_msg)

    current_workcell_snapshot = self.workcell_runtime.get_state_snapshot()
    praxis_state.set(
      "workcell_last_successful_snapshot",
      current_workcell_snapshot,
    )
    logger.debug(
      "Workcell state snapshot captured and stored in PraxisState for run %s.",
      protocol_run_orm.accession_id,
    )

    return PraxisRunContext(
      run_accession_id=protocol_run_orm.accession_id,
      canonical_state=praxis_state,
      current_db_session=db_session,
      current_call_log_db_accession_id=None,
    )

  def _process_input_parameters(
    self,
    protocol_pydantic_def: FunctionProtocolDefinitionCreate,
    input_parameters: dict[str, Any],
    final_args: dict[str, Any],
  ) -> None:
    """Process input parameters and populate final_args."""
    for param_meta in protocol_pydantic_def.parameters:
      if param_meta.is_deck_param:
        continue
      if param_meta.name == protocol_pydantic_def.state_param_name:
        continue

      if param_meta.name in input_parameters:
        final_args[param_meta.name] = input_parameters[param_meta.name]
        logger.debug("Using user input for param '%s'.", param_meta.name)
      elif not param_meta.optional:
        error_msg = f"Mandatory parameter '{param_meta.name}' missing for protocol "
        f"'{protocol_pydantic_def.name}'."
        raise ValueError(error_msg)
      else:
        logger.debug("Optional param '%s' not provided by user.", param_meta.name)

  def _inject_praxis_state(
    self,
    protocol_pydantic_def: FunctionProtocolDefinitionCreate,
    praxis_state: PraxisState,
    final_args: dict[str, Any],
  ) -> dict[str, Any] | None:
    """Inject PraxisState object or its dictionary representation into final_args."""
    state_dict_to_pass: dict[str, Any] | None = None
    if protocol_pydantic_def.state_param_name:
      state_param_meta = next(
        (
          p
          for p in protocol_pydantic_def.parameters
          if p.name == protocol_pydantic_def.state_param_name
        ),
        None,
      )
      if state_param_meta:
        if "PraxisState" in state_param_meta.actual_type_str:
          final_args[protocol_pydantic_def.state_param_name] = praxis_state
          logger.debug(
            "Injecting PraxisState object for param '%s'.",
            protocol_pydantic_def.state_param_name,
          )
        elif "dict" in state_param_meta.actual_type_str.lower():
          state_dict_to_pass = praxis_state.to_dict()
          final_args[protocol_pydantic_def.state_param_name] = state_dict_to_pass
          logger.debug(
            "Injecting state dictionary for param '%s'.",
            protocol_pydantic_def.state_param_name,
          )
        else:
          final_args[protocol_pydantic_def.state_param_name] = praxis_state
          logger.debug(
            "Defaulting to injecting PraxisState object for param '%s'.",
            protocol_pydantic_def.state_param_name,
          )
    return state_dict_to_pass

  async def _prepare_arguments(
    self,
    db_session: AsyncSession,
    protocol_pydantic_def: FunctionProtocolDefinitionCreate,
    input_parameters: dict[str, Any],
    praxis_state: PraxisState,
    protocol_run_accession_id: uuid.UUID,
  ) -> tuple[dict[str, Any], dict[str, Any] | None, dict[uuid.UUID, Any]]:
    """Prepare arguments for protocol execution, including acquiring assets."""
    logger.info("Preparing arguments for protocol: %s", protocol_pydantic_def.name)
    final_args: dict[str, Any] = {}
    state_dict_to_pass: dict[str, Any] | None = None
    acquired_assets_details: dict[uuid.UUID, Any] = {}

    self._process_input_parameters(
      protocol_pydantic_def,
      input_parameters,
      final_args,
    )
    state_dict_to_pass = self._inject_praxis_state(
      protocol_pydantic_def,
      praxis_state,
      final_args,
    )
    # Expects _acquire_assets and _handle_deck_preconfiguration from AssetAcquisitionMixin
    if hasattr(self, "_acquire_assets"):
      await self._acquire_assets(  # type: ignore
        protocol_pydantic_def,
        protocol_run_accession_id,
        final_args,
        acquired_assets_details,
      )

    if hasattr(self, "_handle_deck_preconfiguration"):
      await self._handle_deck_preconfiguration(  # type: ignore
        db_session,
        protocol_pydantic_def,
        input_parameters,
        protocol_run_accession_id,
        final_args,
      )

    return final_args, state_dict_to_pass, acquired_assets_details
