import configparser
import threading
import asyncio
import json
import os
from typing import Any, Dict, List, Optional, Type, TypeVar, cast
from celery import Celery  # type: ignore

from pylabrobot.resources import Coordinate, Deck, Resource
from praxis.core.deck import DeckManager
from praxis.protocol.protocol import Protocol
from praxis.protocol.parameter import ProtocolParameters
from praxis.configure import PraxisConfiguration
from praxis.protocol.config import ProtocolConfiguration
from praxis.utils.state import State
from praxis.utils.db import DatabaseManager

P = TypeVar("P", bound=Protocol)


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

    async def initialize_dependencies(self):
        print(self.config.database["praxis_dsn"])
        self.db = await DatabaseManager.initialize(praxis_dsn=self.config.database["praxis_dsn"],
                                             keycloak_dsn=self.config.database["keycloak_dsn"])

    async def get_user_info(self, username: str) -> Dict[str, Any]:
        """Retrieves user information for a given user identifier."""
        user_info = await self.db.get_user(username)
        return user_info

    async def create_protocol(
        self,
        protocol_class: Type[P],
        protocol_config_data: Dict[str, Any],
        protocol_deck_file: str,
        manual_check_list: List[str],
        user_info: Dict[str, Any],
        **kwargs,
    ) -> P:
        protocol_config = ProtocolConfiguration(protocol_config_data, self.config)

        # Get the deck from the DeckManager asynchronously
        try:
            deck = await self.deck_manager.get_deck(protocol_deck_file)
        except Exception as e:
            raise ValueError(f"Error getting deck: {e}")

        protocol = protocol_class(
            protocol_configuration=protocol_config,
            manual_check_list=manual_check_list,
            orchestrator=self,
            deck=deck,
            user_info=user_info,
            state=self.state,
        )

        self.protocols[protocol.name] = protocol
        return protocol

    async def create_and_start_protocol(
        self,
        protocol_class: Type[P],
        protocol_config_data: Dict[str, Any],
        protocol_deck_file: str,
        manual_check_list: List[str],
        user_info: Dict[str, Any],
    ):
        """
        Creates and starts a protocol.
        """
        protocol = await self.create_protocol(
            protocol_class,
            protocol_config_data,
            protocol_deck_file,
            manual_check_list,
            user_info,
        )
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
