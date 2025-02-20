import configparser
import threading
import asyncio
import json
import os
from typing import Any, Dict, List, Optional, Type, TypeVar, cast, Set, MutableMapping
from celery import Celery  # type: ignore
from dataclasses import dataclass, field

from pylabrobot.resources import Coordinate, Deck, Resource
from .deck import DeckManager
from ..protocol import (
    Protocol,
    ProtocolConfiguration,
    ProtocolParameters,
    WorkcellAssets,
)
from ..configure import PraxisConfiguration
from praxis.utils.state import State
from praxis.utils.db import DatabaseManager
from .deck import DeckManager
from .workcell import Workcell, WorkcellView
from .base import ProtocolInterface, WorkcellInterface, WorkcellAssetsInterface
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..protocol import Protocol, ProtocolConfiguration, WorkcellAssets

P = TypeVar("P", bound=ProtocolInterface)


@dataclass
class ValidationResult:
    """Validation result container with typed fields."""

    valid: bool = True
    errors: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    validated_config: Dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    def __init__(self, config: str | PraxisConfiguration):
        if isinstance(config, str):
            config = PraxisConfiguration(config)
        if not isinstance(config, PraxisConfiguration):
            raise ValueError("Invalid configuration object.")
        self.config = config

        self.protocols: Dict[str, Protocol] = {}

        # Deck Manager
        self.deck_manager = DeckManager(self.config)

        self.db = None

        self.state = State(
            redis_host=self.config.redis_host,
            redis_port=self.config.redis_port,
            redis_db=self.config.redis_db,
        )

        # Configure Celery
        self.celery_app = Celery(
            "tasks",
            broker=self.config["celery"]["broker"],
            backend=self.config["celery"]["backend"],
        )

        self._main_workcell: Optional[WorkcellInterface] = None
        self._workcell_views: Dict[str, WorkcellView] = {}
        self._active_resources: Dict[str, Set[str]] = (
            {}
        )  # resource_name -> set of protocol names
        self._validation_data: MutableMapping[str, Any] = {}

    async def initialize_dependencies(self):
        print(self.config.database["praxis_dsn"])
        self.db = await DatabaseManager.initialize(
            praxis_dsn=self.config.database["praxis_dsn"],
            keycloak_dsn=self.config.database["keycloak_dsn"],
        )
        # Initialize main workcell
        self._main_workcell = Workcell(
            config=self.config,
            save_file="workcell_state.json",  # TODO: find a more robust way to handle this
        )
        await self._main_workcell.initialize_dependencies()

    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """Retrieves user information for a given user identifier."""
        assert self.db is not None, "Database not initialized"
        user_info = await self.db.get_user(username)
        return user_info

    async def create_protocol(
        self,
        protocol_class: Type[P],
        protocol_config_data: Dict[str, Any],
    ) -> P:
        """Create a new protocol instance with orchestrator integration."""
        # Create protocol instance with config
        protocol = protocol_class(protocol_config_data)

        workcell_view = await self.create_workcell_view(
            protocol_name=protocol.name,
            required_assets=protocol.required_assets,
        )

        # Initialize with orchestrator
        await protocol.initialize(workcell=workcell_view)

        # Store protocol reference
        self.protocols[protocol.name] = cast(
            Protocol, protocol
        )  # TODO: check if this is appropriate

        return protocol

    async def create_and_start_protocol(
        self, protocol_class: Type[P], protocol_config_data: Dict[str, Any]
    ):
        """
        Creates and starts a protocol.
        """
        protocol = await self.create_protocol(protocol_class, protocol_config_data)
        await self.run_protocol(protocol.name)
        return protocol

    async def run_protocol(self, protocol_name):
        """
        Retrieves and runs a protocol in an asynchronous manner.
        """
        protocol = self.protocols.get(protocol_name)
        if protocol:
            asyncio.create_task(protocol.execute())
        else:
            raise ValueError(f"Protocol '{protocol_name}' not found.")

    def get_protocol(self, protocol_name: str) -> Optional[Protocol]:
        """Retrieves a protocol instance by name."""
        return self.protocols.get(protocol_name)

    def get_all_protocols(self) -> List[Protocol]:
        """Returns a list of all protocol instances."""
        return list(self.protocols.values())

    def get_running_protocols(self) -> List[str]:
        """Returns a list of the names of all currently running protocols."""
        return [
            protocol_name
            for protocol_name, protocol in self.protocols.items()
            if protocol.status == "running"
        ]

    def send_command(self, protocol_name, command):
        """Sends a command to a running protocol."""
        protocol = self.protocols.get(protocol_name)
        if protocol:
            if command == "start":
                asyncio.create_task(self.run_protocol(protocol_name))
            else:
                asyncio.create_task(protocol.intervene(command))
        else:
            raise ValueError(f"Protocol '{protocol_name}' not found.")

    def schedule_standalone_task(self, task_instance):
        """
        Schedules a standalone task to be run in a separate thread.
        """
        thread = threading.Thread(target=task_instance.run_task)
        thread.daemon = True
        thread.start()

    async def _run_protocol(self, protocol):
        """
        Internal method to run the protocol in an asyncio task.
        """
        try:
            await protocol.execute()
        except Exception as e:
            print(f"An error occurred while running protocol {protocol.name}: {e}")
            await protocol._cleanup()
        finally:
            if protocol.status in ["stopped", "completed", "errored"]:
                await protocol._cleanup()

    async def create_workcell_view(
        self, protocol_name: str, required_assets: WorkcellAssetsInterface
    ) -> WorkcellView:
        """Creates a view of the main workcell for a specific protocol."""
        if not self._main_workcell:
            raise RuntimeError("Main workcell not initialized")

        # Create new view
        view = WorkcellView(
            parent_workcell=self._main_workcell,
            protocol_name=protocol_name,
            required_assets=required_assets,
        )

        self._workcell_views[protocol_name] = view
        return view

    async def release_workcell_view(self, protocol_name: str):
        """Releases a protocol's workcell view."""
        if protocol_name in self._workcell_views:
            view = self._workcell_views.pop(protocol_name)
            await view.release()

    def get_resource_users(self, resource_name: str) -> Set[str]:
        """Get protocols currently using a resource."""
        return self._active_resources.get(resource_name, set())

    async def _cleanup_protocol(self, protocol_name: str):
        """Clean up protocol resources when it ends."""
        await self.release_workcell_view(protocol_name)
        # Remove protocol from active resources
        for users in self._active_resources.values():
            users.discard(protocol_name)

    async def match_assets_to_requirements(
        self, requirements: Dict[str, Any]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Match required assets to available assets in database."""
        if self.db is None:
            raise RuntimeError("Database not initialized")

        matches: Dict[str, List[Dict[str, Any]]] = {}

        for asset_name, asset_reqs in requirements["required_assets"].items():
            query = """
            SELECT
                name,
                type,
                metadata,
                CASE
                    WHEN type = $1 THEN 1.0
                    WHEN type LIKE $2 THEN 0.8
                    ELSE 0.5
                END as compatibility_score
            FROM assets
            WHERE is_available = true
                AND (type = $1 OR type LIKE $2)
                AND metadata @> $3
            ORDER BY compatibility_score DESC
            """

            asset_type = asset_reqs.get("type")
            metadata_requirements = asset_reqs.get("metadata", {})

            results = await self.db.fetch_all(
                query, asset_type, f"%{asset_type}%", json.dumps(metadata_requirements)
            )

            matches[asset_name] = [
                {
                    "asset_name": r["name"],
                    "asset_type": r["type"],
                    "compatibility_score": r["compatibility_score"],
                    "metadata": r["metadata"],
                }
                for r in results
            ]

        return matches

    async def validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a complete protocol configuration."""
        try:
            result = ValidationResult(validated_config=config.copy())

            # 1. Basic config validation
            required_fields = ["name", "protocol_path", "required_assets"]
            missing_fields = [f for f in required_fields if f not in config]
            if missing_fields:
                result.valid = False
                result.errors["missing_fields"] = missing_fields
                return result.__dict__

            # 2. Validate assets
            assets = WorkcellAssets(config.get("required_assets", {}))
            temp_view = None

            try:
                # Create temporary view
                temp_view = await self.create_workcell_view(
                    protocol_name=f"temp_{config['name']}", required_assets=assets
                )

                # Check asset availability
                unavailable: list[str] = []
                if self.db is None:
                    raise RuntimeError("Database not initialized")

                for asset in assets:
                    if await temp_view.parent.is_asset_in_use(asset.name):
                        unavailable.append(asset.name)
                    else:
                        # Verify asset exists
                        asset_info = await self.db.get_asset(asset.name)
                        if not asset_info:
                            unavailable.append(f"{asset.name} (not found)")

                if len(unavailable) > 0:
                    result.valid = False
                    result.errors["unavailable_assets"] = unavailable
                    return result.__dict__

                # 3. Validate parameters
                if "parameters" in config and self.db is not None:
                    try:
                        details = await self.db.get_protocol_details(
                            config["protocol_path"]
                        )
                        if details and details.get("parameters"):
                            validated_params = details["parameters"].validate(
                                config["parameters"]
                            )
                            result.validated_config["parameters"] = validated_params
                    except ValueError as e:
                        result.valid = False
                        result.errors["parameters"] = str(e)
                        return result.__dict__

                # Add warnings
                if self.get_running_protocols():
                    result.warnings.append("Other protocols are currently running")

                return result.__dict__

            finally:
                if temp_view:
                    await self.release_workcell_view(f"temp_{config['name']}")

        except Exception as e:
            return ValidationResult(
                valid=False, errors={"validation": str(e)}, validated_config=config
            ).__dict__
