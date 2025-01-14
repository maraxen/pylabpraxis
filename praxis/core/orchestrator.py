
import configparser
import threading
import asyncio
import json
import os
from typing import Optional, Dict, Any, List, cast
from celery import Celery

from pylabrobot.resources import Deck, Resource, Coordinate
from praxis.core.deck import DeckManager
from praxis.protocol.protocol import Protocol
from praxis.protocol.registry import Registry, initialize_registry
from praxis.protocol.parameter import ProtocolParameters
from praxis.configure import PraxisConfiguration, ProtocolConfiguration
from praxis.utils.assets import AsyncAssetDatabase
from praxis.utils.data import initialize_data, Data

class Orchestrator:
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.configuration = PraxisConfiguration(config_file)

        self.protocols: Dict[str, Protocol] = {}
        self.data_instance = None
        self.registry = None

        # Deck Manager
        self.deck_manager = DeckManager(self.config)

        self.asset_db_file = self.config["database"]["lab_inventory"]
        self.asset_database = AsyncAssetDatabase(self.asset_db_file)

        # Configure Celery
        self.celery_app = Celery(
            "tasks",
            broker=self.config["celery"]["broker"],
            backend=self.config["celery"]["backend"],
        )

    async def initialize_dependencies(self):
        self.registry = await initialize_registry(config_file=self.config_file)
        self.data_instance = await initialize_data(db_file=self.config["database"]["data_dir"])

    def get_user_info(self, user_identifier: str) -> Dict[str, Any]:
        """Retrieves user information for a given user identifier."""
        users = self.configuration.get_lab_users()
        return users.get_user_info(user_identifier)

    def create_protocol(self, protocol_config_data, protocol_deck_file, liquid_handler_name, manual_check_list, user_info):
        protocol_config = ProtocolConfiguration(
            protocol_config_data, self.deck_manager.deck_directory
        )

        # Get the deck from the DeckManager
        try:
            deck = self.deck_manager.get_deck(protocol_deck_file)
        except Exception as e:
            raise ValueError(f"Error getting deck: {e}")

        protocol = Protocol(
            protocol_configuration=protocol_config,
            manual_check_list=manual_check_list,
            orchestrator=self,
            deck=deck,
            user_info=user_info,
        )
        self.protocols[protocol.name] = protocol
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

    def create_and_start_protocol(self, protocol_config, protocol_deck_file, liquid_handler_name, manual_check_list, user_info):
        """
        Creates and starts a protocol.
        """
        protocol = self.create_protocol(protocol_config, protocol_deck_file, liquid_handler_name, manual_check_list, user_info)
        asyncio.create_task(self.run_protocol(protocol.name))
        return protocol

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

    def schedule_plate_reader_task(self, experiment_name, plate_name, measurement_type, wells, estimated_duration):
        """
        Schedules a plate reader task.
        """
        # Create a PlateReaderTask instance (which is a StandaloneTask)
        task = PlateReaderTask(experiment_name, plate_name, measurement_type, wells, estimated_duration, self.protocol_registry, self._data)

        # Schedule the task using the generic method
        self.schedule_standalone_task(task)

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