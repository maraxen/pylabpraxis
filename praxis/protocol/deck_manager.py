import json
from typing import Dict, List
from pylabrobot.resources import Deck, Resource, Coordinate
import os
import configparser

class DeckManager:
    def __init__(self, config: configparser.ConfigParser, config_file: str):
        self.config = config
        self.config_file = config_file
        self.deck_directory = self.config["deck_management"]["deck_directory"]
        self.baseline_decks: Dict[str, Deck] = self._load_baseline_decks()
        self.active_decks: Dict[str, Deck] = {}

    def _load_baseline_decks(self) -> Dict[str, Deck]:
        """
        Loads the baseline deck layouts specified in the config file.
        """
        baseline_decks = {}
        if 'baseline_decks' in self.config:
            for liquid_handler_name, deck_file in self.config['baseline_decks'].items():
                if not os.path.exists(deck_file):
                    raise FileNotFoundError(f"Baseline deck file not found: {deck_file}")
                try:
                    deck = Deck.load_from_json_file(deck_file)
                    baseline_decks[liquid_handler_name] = deck
                except Exception as e:
                    raise ValueError(f"Error loading baseline deck from {deck_file}: {e}")
        else:
            print("Warning: No baseline_decks section found in config file.")
        return baseline_decks

    def select_deck(self, protocol_name: str, protocol_deck_file: str, liquid_handler_name: str) -> Deck:
        """
        Selects the appropriate deck layout for a given protocol, merging with the baseline.
        """
        # Check if a deck is already active for the liquid handler
        if liquid_handler_name in self.active_decks:
            active_deck = self.active_decks[liquid_handler_name]

            # Attempt to merge the new protocol's deck with the active deck
            merged_deck = self._merge_decks(active_deck, protocol_deck_file, liquid_handler_name)

            # If successful, update the active deck and return it
            self.active_decks[liquid_handler_name] = merged_deck
            return merged_deck
        else:
            # If no deck is active, merge with the baseline deck
            baseline_deck = self.baseline_decks.get(liquid_handler_name)
            if not baseline_deck:
                raise ValueError(f"Liquid handler '{liquid_handler_name}' not found in baseline decks.")

            merged_deck = self._merge_decks(baseline_deck.copy(), protocol_deck_file, liquid_handler_name)

            # Set the merged deck as the active deck for the liquid handler
            self.active_decks[liquid_handler_name] = merged_deck
            return merged_deck

    def _merge_decks(self, base_deck: Deck, protocol_deck_file: str, liquid_handler_name: str) -> Deck:
        """
        Merges the protocol-specific deck with the given base deck (either baseline or active),
        checking for conflicts.
        """
        if not os.path.exists(protocol_deck_file):
            raise FileNotFoundError(f"Protocol deck file not found: {protocol_deck_file}")
        try:
            protocol_deck = Deck.load_from_json_file(protocol_deck_file)
        except Exception as e:
            raise ValueError(f"Error loading protocol deck from {protocol_deck_file}: {e}")

        # Remove resources that are also in the baseline deck
        self._remove_baseline_resources(protocol_deck, liquid_handler_name)

        # Attempt to merge the decks
        merged_deck = base_deck.copy()
        for resource in protocol_deck.get_resources():
            location = protocol_deck.get_parent_resource(resource)
            try:
                merged_deck.assign_child_resource(resource, location)
            except Exception as e:
                raise ValueError(f"Error merging decks: {e}")

        return merged_deck

    def _remove_baseline_resources(self, deck: Deck, liquid_handler_name: str):
        """Removes resources from the given deck that are also present in the baseline deck."""
        baseline_deck = self.baseline_decks.get(liquid_handler_name)
        if baseline_deck:
            for resource_name in baseline_deck.get_resource_names():
                if deck.has_resource(resource_name):
                    deck.unassign_child_resource(deck.get_resource(resource_name))

    def release_deck(self, liquid_handler_name: str):
        """
        Releases the deck associated with a liquid handler.
        """
        if liquid_handler_name in self.active_decks:
            del self.active_decks[liquid_handler_name]

    def get_available_deck_files(self) -> List[str]:
        """
        Returns a list of available deck layout files (relative paths from deck_directory).
        """
        deck_files = []
        for filename in os.listdir(self.deck_directory):
            if filename.endswith(".json"):
                deck_files.append(filename)  # Store only the filename
        return deck_files

    def validate_deck_layout(self, protocol_deck_file: str, liquid_handler_name: str) -> List[str]:
        """
        Validates a protocol deck layout against the baseline deck.
        Returns a list of conflicts found.
        """
        conflicts = []
        baseline_deck = self.baseline_decks.get(liquid_handler_name)

        if not baseline_deck:
            conflicts.append(f"Liquid handler '{liquid_handler_name}' not found in baseline decks.")
            return conflicts

        if not os.path.exists(protocol_deck_file):
            conflicts.append(f"Protocol deck file not found: {protocol_deck_file}")
            return conflicts

        try:
            protocol_deck = Deck.load_from_json_file(protocol_deck_file)
        except Exception as e:
            conflicts.append(f"Error loading protocol deck from {protocol_deck_file}: {e}")
            return conflicts

        # Check for conflicts with the baseline deck
        conflicts.extend(self._find_deck_conflicts(baseline_deck, protocol_deck))

        return conflicts

    def _find_deck_conflicts(self, deck1: Deck, deck2: Deck) -> List[str]:
        """
        Compares two Deck objects and returns a list of conflicts.
        """
        conflicts = []
        # Iterate over resources in deck2
        for resource_name in deck2.get_resource_names():
            resource1 = deck1.get_resource(resource_name)
            resource2 = deck2.get_resource(resource_name)

            if resource1 is not None and resource2 is not None:
                # Resource exists on both decks. Check for differences
                if resource1 != resource2:
                    conflicts.append(f"Conflict: Resource '{resource_name}' is defined differently in the two decks.")
            elif resource1 is not None or resource2 is not None:
                # Resource exists on only one deck. This could be a potential issue.
                conflicts.append(f"Conflict: Resource '{resource_name}' exists in one deck but not the other.")

        return conflicts
