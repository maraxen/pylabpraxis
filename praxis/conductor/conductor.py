
import configparser
import threading
import asyncio
import json
import os
from typing import Optional, Dict
from celery import Celery

from pylabrobot.resources import Deck, Resource, Coordinate

from praxis.protocol import Protocol, initialize_registry, Registry
from praxis.utils import acquire_lock, release_lock, Data, initialize_data

class Conductor:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.protocols: Dict[str, Protocol] = {}
        self.registry = Registry(config_file=config_file)

        self.lab_configuration = self.config["lab_configuration"]

        # Load baseline decks
        self.baseline_decks: Dict[str, Deck] = {}
        self._load_baseline_decks()

        # Configure Celery
        self.celery_app = Celery('tasks', broker=self.config['celery']['broker'], backend=self.config['celery']['backend'])

    async def initialize_dependencies(self):
        self.registry = await initialize_registry(config_file=self.config_file)
        self.data_instance = await initialize_data(db_file=self.config["database"]["data_dir"])

    async def _load_baseline_decks(self):
        """Loads the baseline deck layouts from the config file."""
        if 'baseline_decks' in self.config:
            for liquid_handler_name, deck_file in self.config['baseline_decks'].items():
                if not os.path.exists(deck_file):
                    raise FileNotFoundError(f"Baseline deck file not found: {deck_file}")
                try:
                    deck = Deck.load_from_json_file(deck_file)
                    self.baseline_decks[liquid_handler_name] = deck
                except Exception as e:
                    raise ValueError(f"Error loading baseline deck from {deck_file}: {e}")
        else:
            print("Warning: No baseline_decks section found in config file.")

    async def attempt_merge_with_running_protocol(self, new_protocol_config, new_protocol_deck_file: str) -> Deck:
      """
        Attempts to merge the new protocol's deck with the deck of the currently running protocol.
        This assumes only one protocol is running at a time.

        Args:
            new_protocol_config: The configuration of the new protocol.
            new_protocol_deck_file: Path to the new protocol-specific deck file.

        Returns:
            The merged Deck object if successful.

        Raises:
            ValueError: If there are conflicts between the decks or if no protocol is running.
            FileNotFoundError: If the new protocol deck file is not found.
      """
      raise NotImplementedError("This method is not yet implemented.")
      # 1. Get the running protocol's deck
      running_protocols = await self.get_running_protocols()



      if not running_protocols:
          raise ValueError("No protocol is currently running.")
      if len(running_protocols) > 1:
          raise NotImplementedError("Multiple protocols are currently running on a single deck." + \
                            " This functionality only supports one running protocol.")

      running_protocol_name = running_protocols[0]
      running_protocol = self.get_protocol(running_protocol_name)
      if not running_protocol:
          raise ValueError("Running protocol instance not found in Conductor.")

      current_deck = running_protocol.deck
      if not current_deck:
          raise ValueError("Running protocol's deck is not set.")

      # 2. Load and pre-process the new protocol's deck
      if not os.path.exists(new_protocol_deck_file):
          raise FileNotFoundError(f"New protocol deck file not found: {new_protocol_deck_file}")
      try:
          new_deck = Deck.load_from_json_file(new_protocol_deck_file)
      except Exception as e:
          raise ValueError(f"Error loading new protocol deck from {new_protocol_deck_file}: {e}")

      # Remove resources that are also in the baseline deck
      self._remove_baseline_resources(new_deck, running_protocol.liquid_handler_name)

      # 3. Attempt to merge the decks
      merged_deck = current_deck.copy()  # Start with a copy of the current deck
      for resource in new_deck.get_all_resources():
          location = new_deck.get_absolute_location(resource)
          try:
              merged_deck.assign_child_resource(resource, location) #try to assign resources
          except Exception as e:
              raise ValueError(f"Error merging decks: {e}")

      return merged_deck

    async def _remove_baseline_resources(self, deck: Deck, liquid_handler_name: str):
        """Removes resources from the given deck that are also present in the baseline deck."""
        raise NotImplementedError("This method is not yet implemented.")
        baseline_deck = self.baseline_decks.get(liquid_handler_name)
        if baseline_deck:
            for resource in baseline_deck.get_all_resources():
                if deck.has_resource(resource.name):
                    deck.unassign_child_resource(deck.get_resource(resource_name))

    async def create_and_start_protocol_with_merge_check(self, protocol_config, protocol_deck_file, liquid_handler_name):
      """
      Attempts to merge the new protocol's deck with the running protocol's deck,
      creates a new Protocol instance with the merged deck, and starts it.
      """
      raise NotImplementedError("This method is not yet implemented.")
      try:
          merged_deck = self.attempt_merge_with_running_protocol(protocol_config, protocol_deck_file)
      except Exception as e:
          raise ValueError(f"Error merging decks: {e}")

      # Create Protocol instance with the merged deck
      protocol = Protocol(# ... other config ...,
                          deck=merged_deck,
                          registry=self.registry,
                          conductor=self,
                          liquid_handler_name=liquid_handler_name)
      self.protocols[protocol.name] = protocol

      # Start the protocol
      self.start_protocol(protocol.name)

      return protocol


    def create_protocol(self, protocol_config):
        """
        Creates a new Protocol instance based on the provided configuration.
        """
        protocol = Protocol(experiment_configuration=protocol_config, #TODO: adapt to new config
                             lab_configuration=protocol_config,
                             needed_deck_resources=protocol_config,
                             check_list=protocol_config,
                             experiment_registry=self.protocol_registry)
        self.protocols[protocol.name] = protocol
        return protocol

    def start_protocol(self, protocol_name):
        """
        Starts a protocol in a separate thread.
        """
        protocol = self.protocols.get(protocol_name)
        if protocol:
            thread = threading.Thread(target=self.run_protocol, args=(protocol_name,))
            thread.daemon = True
            thread.start()
        else:
            raise ValueError(f"Protocol '{protocol_name}' not found.")

    def run_protocol(self, protocol_name):
        """
        Retrieves and runs a protocol in an asynchronous manner.
        """
        protocol = self.protocols.get(protocol_name)
        if protocol:
            asyncio.run(protocol.execute())
        else:
            raise ValueError(f"Protocol '{protocol_name}' not found.")

    def create_and_start_protocol(self, protocol_config):
        """
        Creates and starts a protocol.
        """
        protocol = self.create_protocol(protocol_config)
        self.start_protocol(protocol.name)

    def get_protocol(self, protocol_name):
        """
        Retrieves a protocol instance by name.
        """
        return self.protocols.get(protocol_name)

    def get_all_protocols(self):
        """
        Returns a list of all protocol instances.
        """
        return list(self.protocols.values())

    def get_running_protocols(self):
        """
        Returns a list of the names of all currently running protocols.
        """
        running_protocols = []
        for protocol_name, protocol in self.protocols.items():
            if protocol.status == "running":
              if protocol.uses_deck:
                running_protocols.append(protocol_name, protocol.deck)
        return running_protocols

    def send_command(self, protocol_name, command):
        """
        Sends a command to a running protocol.
        """
        protocol = self.protocols.get(protocol_name)
        if protocol:
            if command == "start":
                self.start_protocol(protocol_name)
            else:
                asyncio.run(protocol.intervene(command))
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