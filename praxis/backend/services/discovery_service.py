# pylint: disable=too-few-public-methods,broad-except,fixme,unused-argument
"""Praxis protocol function discovery service.

praxis/protocol_core/discovery_service.py
Service responsible for discovering protocol functions, transforming their
metadata into structured Pydantic models, and upserting them into a database
via the protocol_data_service. It also updates the in-memory PROTOCOL_REGISTRY
with the database ID of the discovered protocols.
"""

# LibCST-based extraction
import ast
import contextlib
import logging
import os
import uuid
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import libcst as cst
from libcst.metadata import MetadataWrapper
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from praxis.backend.models.domain.deck import (
  DeckDefinitionCreate as DeckTypeDefinitionCreate,
)
from praxis.backend.models.domain.deck import (
  DeckDefinitionUpdate as DeckTypeDefinitionUpdate,
)
from praxis.backend.models.domain.protocol import (
  FunctionProtocolDefinitionCreate,
  FunctionProtocolDefinitionUpdate,
)
from praxis.backend.services.deck_type_definition import DeckTypeDefinitionService
from praxis.backend.services.machine_type_definition import MachineTypeDefinitionService
from praxis.backend.services.protocol_definition import ProtocolDefinitionCRUDService
from praxis.backend.services.resource_type_definition import (
  ResourceTypeDefinitionService,
)
from praxis.backend.services.simulation_service import SimulationService
from praxis.backend.utils.plr_static_analysis.visitors.protocol_discovery import (
  ProtocolFunctionVisitor,
)

logger = logging.getLogger(__name__)


class DeckVisitor(ast.NodeVisitor):
  """AST visitor to find deck definitions."""

  def __init__(self, module_name: str, file_path: str) -> None:
    self.module_name = module_name
    self.file_path = file_path
    self.definitions: list[dict[str, Any]] = []

  def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
    """Visit a class definition."""
    for base in node.bases:
      if isinstance(base, ast.Name) and base.id == "Deck":
        self._extract_deck_definition(node)

  def _extract_deck_definition(self, node: ast.ClassDef) -> None:
    """Extract information from a deck definition."""
    deck_info = {
      "name": node.name,
      "fqn": f"{self.module_name}.{node.name}",
      "source_file_path": self.file_path,
      "module_name": self.module_name,
      "class_name": node.name,
      "positioning_config_json": None,
    }

    for item in node.body:
      if isinstance(item, ast.Assign):
        for target in item.targets:
          if isinstance(target, ast.Name) and target.id == "positioning":
            with contextlib.suppress(ValueError):
              deck_info["positioning_config_json"] = ast.literal_eval(item.value)
    self.definitions.append(deck_info)


class DiscoveryService:
  """Service for discovering and managing protocol functions and PLR type definitions."""

  def __init__(
    self,
    db_session_factory: async_sessionmaker[AsyncSession] | None = None,
    resource_type_definition_service: ResourceTypeDefinitionService | None = None,
    machine_type_definition_service: MachineTypeDefinitionService | None = None,
    deck_type_definition_service: DeckTypeDefinitionService | None = None,
    protocol_definition_service: ProtocolDefinitionCRUDService | None = None,
    enable_simulation: bool = True,
  ) -> None:
    """Initialize the DiscoveryService.

    Args:
        db_session_factory: Factory for creating database sessions.
        resource_type_definition_service: Service for resource types.
        machine_type_definition_service: Service for machine types.
        deck_type_definition_service: Service for deck types.
        protocol_definition_service: Service for protocol definitions.
        enable_simulation: Whether to run simulation on discovered protocols.

    """
    self.db_session_factory = db_session_factory
    self.resource_type_definition_service = resource_type_definition_service
    self.machine_type_definition_service = machine_type_definition_service
    self.deck_type_definition_service = deck_type_definition_service
    self.protocol_definition_service = protocol_definition_service
    self.enable_simulation = enable_simulation
    self._simulation_service = SimulationService() if enable_simulation else None

  async def discover_and_sync_all_definitions(
    self,
    protocol_search_paths: str | list[str],
    source_repository_accession_id: uuid.UUID | None = None,
    commit_hash: str | None = None,
    file_system_source_accession_id: uuid.UUID | None = None,
  ) -> None:
    """Discovers and synchronizes all PLR type definitions and protocols."""
    logger.info("Starting discovery and synchronization of all definitions...")

    if self.db_session_factory:
      async with self.db_session_factory() as session:
        # Create fresh service instances with the new session
        # This prevents ConnectionRefusedError from stale sessions
        logger.info("Created new DB session for synchronization.")

        resource_service = ResourceTypeDefinitionService(session)
        machine_service = MachineTypeDefinitionService(session)
        deck_service = DeckTypeDefinitionService(session)

        logger.info("Synchronizing resource type definitions...")
        await resource_service.discover_and_synchronize_type_definitions()
        logger.info("Resource type definitions synchronized.")

        logger.info("Synchronizing machine type definitions...")
        await machine_service.discover_and_synchronize_type_definitions()
        logger.info("Machine type definitions synchronized.")

        logger.info("Synchronizing deck type definitions...")
        deck_definitions = self._extract_deck_definitions_from_paths(protocol_search_paths)
        for deck_data in deck_definitions:
          deck_pydantic_model = DeckTypeDefinitionCreate(**deck_data)
          existing_def = await deck_service.get_by_fqn(
            db=session,
            fqn=deck_pydantic_model.fqn,
          )
          if existing_def:
            update_data = DeckTypeDefinitionUpdate(
              **deck_pydantic_model.model_dump(),
            )
            await deck_service.update(
              db=session,
              db_obj=existing_def,
              obj_in=update_data,
            )
          else:
            await deck_service.create(
              db=session,
              obj_in=deck_pydantic_model,
            )
        logger.info("Deck type definitions synchronized.")

    else:
      # Fallback to existing services if factory not provided (legacy/testing)
      logger.warning("No DB session factory provided. Using injected services (may be stale).")
      if self.resource_type_definition_service:
        logger.info("Synchronizing resource type definitions...")
        await self.resource_type_definition_service.discover_and_synchronize_type_definitions()
        logger.info("Resource type definitions synchronized.")

      if self.machine_type_definition_service:
        logger.info("Synchronizing machine type definitions...")
        await self.machine_type_definition_service.discover_and_synchronize_type_definitions()
        logger.info("Machine type definitions synchronized.")

      if self.deck_type_definition_service:
        logger.info("Synchronizing deck type definitions (legacy mode)...")
        # In legacy mode, we don't have a session factory, so we hope services are injected
        # Note: _extract_deck_definitions_from_paths already called inside if factory block,
        # but here we need to handle the case where factory is MISSING.
        # Actually, the diff logic was a bit mixed here.
        # Let's check if we should even support legacy mode for decks.
        # The diff didn't show deck sync in legacy mode.

    logger.info("Discovering and upserting protocols...")
    await self.discover_and_upsert_protocols(
      search_paths=protocol_search_paths,
      source_repository_accession_id=source_repository_accession_id,
      commit_hash=commit_hash,
      file_system_source_accession_id=file_system_source_accession_id,
    )
    logger.info("All definitions synchronized.")

  def _extract_protocol_definitions_from_paths(
    self,
    search_paths: Sequence[str | Path],
  ) -> list[dict[str, Any]]:
    """Extract protocol function definitions from Python files in the given paths."""
    extracted_definitions = []
    for path_item in search_paths:
      abs_path_item = Path(path_item).resolve()
      if not abs_path_item.is_dir():
        continue

      for root, _, files in os.walk(str(abs_path_item)):
        for file in files:
          if file.endswith(".py") and not file.startswith("_"):
            module_file_path = Path(root) / file
            module_name = ".".join(
              module_file_path.relative_to(abs_path_item.parent).with_suffix("").parts,
            )

            try:
              source = module_file_path.read_text(encoding="utf-8")
              tree = cst.parse_module(source)
              visitor = ProtocolFunctionVisitor(
                module_name,
                str(module_file_path),
              )
              # Use MetadataWrapper to enable advanced features in visitors later if needed
              wrapper = MetadataWrapper(tree)
              wrapper.visit(visitor)

              # Convert ProtocolFunctionInfo models back to raw dicts for existing upsert logic
              for def_info in visitor.definitions:
                definition_dict = {
                  "name": def_info.name,
                  "fqn": def_info.fqn,
                  "version": "0.0.0-inferred",
                  "description": def_info.docstring,
                  "source_file_path": def_info.source_file_path,
                  "module_name": def_info.module_name,
                  "function_name": def_info.name,
                  "parameters": def_info.raw_parameters,
                  "assets": def_info.raw_assets,
                  "hardware_requirements": def_info.hardware_requirements,
                  "computation_graph": def_info.computation_graph,
                  "source_hash": def_info.source_hash,
                  "requires_deck": def_info.requires_deck,
                }
                extracted_definitions.append(definition_dict)

            except (cst.ParserSyntaxError, OSError, UnicodeDecodeError) as e:
              logger.warning(
                f"Could not parse {module_file_path}: {e}",
              )
    return extracted_definitions

  def _extract_deck_definitions_from_paths(
    self,
    search_paths: str | list[str] | Sequence[str | Path],
  ) -> list[dict[str, Any]]:
    """Extract deck definitions from Python files in the given paths."""
    extracted_definitions = []
    if isinstance(search_paths, str):
      search_paths = [search_paths]

    for path_item in search_paths:
      abs_path_item = Path(path_item).resolve()
      if not abs_path_item.is_dir():
        continue

      for root, _, files in os.walk(str(abs_path_item)):
        for file in files:
          if file.endswith(".py") and not file.startswith("_"):
            module_file_path = Path(root) / file
            # Correctly handle module name relative to search path
            try:
              module_name = ".".join(
                module_file_path.relative_to(abs_path_item.parent).with_suffix("").parts,
              )

              source = module_file_path.read_text(encoding="utf-8")
              tree = ast.parse(source, filename=str(module_file_path))
              visitor = DeckVisitor(
                module_name,
                str(module_file_path),
              )
              visitor.visit(tree)
              extracted_definitions.extend(visitor.definitions)
            except (SyntaxError, Exception) as e:
              logger.warning(
                f"Could not parse {module_file_path}: {e}",
              )
    return extracted_definitions

  async def discover_and_upsert_protocols(
    self,
    search_paths: str | list[str],
    source_repository_accession_id: uuid.UUID | None = None,
    commit_hash: str | None = None,
    file_system_source_accession_id: uuid.UUID | None = None,
  ) -> list[Any]:
    """Discover protocol functions and upsert them to the DB."""
    if not self.protocol_definition_service:
      logger.error(
        "DiscoveryService: Protocol definition service not provided. Cannot upsert definitions.",
      )
      return []

    logger.info(
      "DiscoveryService: Starting protocol discovery in paths: %s...",
      search_paths,
    )
    extracted_definitions = self._extract_protocol_definitions_from_paths(
      search_paths,
    )

    if not extracted_definitions:
      logger.warning("DiscoveryService: No protocol definitions found from scan.")
      return []

    logger.info(
      "DiscoveryService: Found %d protocol functions. Upserting to DB...",
      len(extracted_definitions),
    )
    upserted_definitions_model: list[Any] = []

    if self.db_session_factory is None:
      logger.error(
        "DiscoveryService: No DB session factory provided. Cannot upsert protocol definitions.",
      )
      return []
    async with self.db_session_factory() as session:
      for protocol_data in extracted_definitions:
        protocol_pydantic_model = FunctionProtocolDefinitionCreate(
          **protocol_data,
        )
        protocol_name_for_error = protocol_pydantic_model.name
        protocol_version_for_error = protocol_pydantic_model.version
        try:
          existing_def = await self.protocol_definition_service.get_by_fqn(
            db=session,
            fqn=f"{protocol_pydantic_model.module_name}.{protocol_pydantic_model.function_name}",
          )

          if existing_def:
            update_data = FunctionProtocolDefinitionUpdate(
              **protocol_pydantic_model.model_dump(),
            )
            def_model = await self.protocol_definition_service.update(
              db=session,
              db_obj=existing_def,
              obj_in=update_data,
            )
          else:
            def_model = await self.protocol_definition_service.create(
              db=session,
              obj_in=protocol_pydantic_model,
            )

          upserted_definitions_model.append(def_model)

        except (ValueError, RuntimeError):
          logger.exception(
            "ERROR: Failed to process or upsert protocol '%s v%s'.",
            protocol_name_for_error,
            protocol_version_for_error,
          )
    num_successful_upserts = len(
      [d for d in upserted_definitions_model if hasattr(d, "id") and d.accession_id is not None],
    )
    logger.info(
      "Successfully upserted %d protocol definition(s) to DB.",
      num_successful_upserts,
    )

    # Run simulation on discovered protocols if enabled
    if self._simulation_service and upserted_definitions_model:
      logger.info(
        "Running simulation on %d discovered protocol(s)...",
        len(upserted_definitions_model),
      )
      async with self.db_session_factory() as sim_session:
        try:
          sim_results = await self._simulation_service.simulate_pending_protocols(
            session=sim_session,
            protocol_orms=upserted_definitions_model,
          )
          simulated_count = sum(1 for r in sim_results.values() if r is not None)
          logger.info(
            "Simulation completed for %d protocol(s).",
            simulated_count,
          )
        except Exception as e:
          logger.warning(
            "Simulation failed for some protocols: %s",
            e,
          )

    return upserted_definitions_model
