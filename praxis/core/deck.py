import os
import json
from typing import Dict, List
from pylabrobot.resources import Deck
import configparser

class DeckManager:
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.deck_directory = config["deck_management"]["deck_directory"]
        self.baseline_decks: Dict[str, Deck] = self._load_baseline_decks()

    def _load_baseline_decks(self) -> Dict[str, Deck]:
        """Loads the baseline deck layouts specified in the config file."""
        baseline_decks = {}
        if "baseline_decks" in self.config:
            for liquid_handler_name, deck_file in self.config["baseline_decks"].items():
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

    def get_deck(self, deck_file: str) -> Deck:
        """Loads and returns the specified deck file from the deck directory."""
        deck_path = os.path.join(self.deck_directory, deck_file)
        if not os.path.exists(deck_path):
            raise FileNotFoundError(f"Deck file not found: {deck_path}")
        return Deck.load_from_json_file(deck_path)

    def get_available_deck_files(self) -> List[str]:
        """Returns a list of available deck layout files (relative paths from deck_directory)."""
        deck_files = []
        for filename in os.listdir(self.deck_directory):
            if filename.endswith(".json"):
                deck_files.append(filename)  # Store only the filename
        return deck_files

    def get_baseline_deck(self, liquid_handler_name: str) -> Deck:
        """Returns the baseline deck for the specified liquid handler."""
        baseline_deck = self.baseline_decks.get(liquid_handler_name)
        if not baseline_deck:
            raise ValueError(f"Liquid handler '{liquid_handler_name}' not found in baseline decks.")
        return baseline_deck
