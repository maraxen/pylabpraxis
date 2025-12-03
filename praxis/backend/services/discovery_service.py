# pylint: disable=too-few-public-methods,broad-except,fixme,unused-argument
"""Praxis protocol function discovery service.

praxis/protocol_core/discovery_service.py
Service responsible for discovering protocol functions, transforming their
metadata into structured Pydantic models, and upserting them into a database
via the protocol_data_service. It also updates the in-memory PROTOCOL_REGISTRY
with the database ID of the discovered protocols.
"""

import ast
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from praxis.backend.models.pydantic_internals.protocol import (
    FunctionProtocolDefinitionCreate,
    FunctionProtocolDefinitionUpdate,
)
from praxis.backend.services.machine_type_definition import MachineTypeDefinitionService
from praxis.backend.services.protocol_definition import ProtocolDefinitionCRUDService
from praxis.backend.services.resource_type_definition import (
    ResourceTypeDefinitionService,
)
from praxis.common.type_inspection import is_pylabrobot_resource, serialize_type_hint

logger = logging.getLogger(__name__)


class ProtocolVisitor(ast.NodeVisitor):
    """AST visitor to find protocol functions."""

    def __init__(self, module_name: str, file_path: str):
        self.module_name = module_name
        self.file_path = file_path
        self.definitions = []

    def visit_FunctionDef(self, node: ast.FunctionDef):  # pylint: disable=invalid-name
        """Visit a function definition."""
        params_list = []
        assets_list = []

        num_args = len(node.args.args)
        num_defaults = len(node.args.defaults)
        defaults = [None] * (num_args - num_defaults) + [
            ast.unparse(d) for d in node.args.defaults
        ]

        for arg, default in zip(node.args.args, defaults):
            annotation = ast.unparse(arg.annotation) if arg.annotation else "Any"

            common_args = {
                "name": arg.arg,
                "fqn": f"{self.module_name}.{node.name}.{arg.arg}",
                "type_hint": annotation,
                "optional": default is not None,
                "default_value_repr": default,
            }

            if is_pylabrobot_resource(annotation):
                assets_list.append(common_args)
            else:
                params_list.append(common_args)

        inferred_model = {
            "name": node.name,
            "fqn": f"{self.module_name}.{node.name}",
            "version": "0.0.0-inferred",
            "description": ast.get_docstring(node) or "Inferred from code.",
            "source_file_path": self.file_path,
            "module_name": self.module_name,
            "function_name": node.name,
            "parameters": params_list,
            "assets": assets_list,
        }
        self.definitions.append(inferred_model)


class DiscoveryService:
    """Service for discovering and managing protocol functions and PLR type definitions."""

    def __init__(
        self,
        db_session_factory: async_sessionmaker[AsyncSession] | None = None,
        resource_type_definition_service: ResourceTypeDefinitionService | None = None,
        machine_type_definition_service: MachineTypeDefinitionService | None = None,
        protocol_definition_service: ProtocolDefinitionCRUDService | None = None,
    ) -> None:
        """Initialize the DiscoveryService."""
        self.db_session_factory = db_session_factory
        self.resource_type_definition_service = resource_type_definition_service
        self.machine_type_definition_service = machine_type_definition_service
        self.protocol_definition_service = protocol_definition_service

    async def discover_and_sync_all_definitions(
        self,
        protocol_search_paths: str | list[str],
        source_repository_accession_id: uuid.UUID | None = None,
        commit_hash: str | None = None,
        file_system_source_accession_id: uuid.UUID | None = None,
    ) -> None:
        """Discovers and synchronizes all PLR type definitions and protocols."""
        logger.info("Starting discovery and synchronization of all definitions...")

        if self.resource_type_definition_service:
            logger.info("Synchronizing resource type definitions...")
            await self.resource_type_definition_service.discover_and_synchronize_type_definitions()
            logger.info("Resource type definitions synchronized.")

        if self.machine_type_definition_service:
            logger.info("Synchronizing machine type definitions...")
            await self.machine_type_definition_service.discover_and_synchronize_type_definitions()
            logger.info("Machine type definitions synchronized.")

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

            for root, _, files in os.walk(abs_path_item):
                for file in files:
                    if file.endswith(".py") and not file.startswith("_"):
                        module_file_path = Path(root) / file
                        module_name = ".".join(
                            module_file_path.relative_to(abs_path_item.parent)
                            .with_suffix("")
                            .parts
                        )

                        with open(module_file_path, "r", encoding="utf-8") as f:
                            source = f.read()
                            try:
                                tree = ast.parse(source, filename=str(module_file_path))
                                visitor = ProtocolVisitor(
                                    module_name, str(module_file_path)
                                )
                                visitor.visit(tree)
                                extracted_definitions.extend(visitor.definitions)
                            except SyntaxError as e:
                                logger.warning(
                                    f"Could not parse {module_file_path}: {e}"
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
            search_paths
        )

        if not extracted_definitions:
            logger.warning("DiscoveryService: No protocol definitions found from scan.")
            return []

        logger.info(
            "DiscoveryService: Found %d protocol functions. Upserting to DB...",
            len(extracted_definitions),
        )
        upserted_definitions_orm: list[Any] = []

        if self.db_session_factory is None:
            logger.error(
                "DiscoveryService: No DB session factory provided. Cannot upsert protocol definitions.",
            )
            return []
        async with self.db_session_factory() as session:
            for protocol_data in extracted_definitions:
                protocol_pydantic_model = FunctionProtocolDefinitionCreate(
                    **protocol_data
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
                            **protocol_pydantic_model.model_dump()
                        )
                        def_orm = await self.protocol_definition_service.update(
                            db=session,
                            db_obj=existing_def,
                            obj_in=update_data,
                        )
                    else:
                        def_orm = await self.protocol_definition_service.create(
                            db=session,
                            obj_in=protocol_pydantic_model,
                        )

                    upserted_definitions_orm.append(def_orm)

                except (ValueError, RuntimeError):
                    logger.exception(
                        "ERROR: Failed to process or upsert protocol '%s v%s'.",
                        protocol_name_for_error,
                        protocol_version_for_error,
                    )
        num_successful_upserts = len(
            [d for d in upserted_definitions_orm if hasattr(d, "id") and d.accession_id is not None],
        )
        logger.info(
            "Successfully upserted %d protocol definition(s) to DB.",
            num_successful_upserts,
        )
        return upserted_definitions_orm
