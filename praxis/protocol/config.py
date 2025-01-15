import os
import json
from typing import Dict, Any, Optional, cast
from .protocol import ProtocolParameters
from ..utils import AsyncAssetDatabase
from ..configure import PraxisConfiguration
from pylabrobot.resources import Deck


class ProtocolConfiguration:
    """
    Protocol configuration denoting specific settings for a method.
    """

    def __init__(self, protocol_config: str | Dict[str, Any], praxis_config: str | PraxisConfiguration):
        """
        Initializes the ProtocolConfiguration.

        Args:
            protocol_config (str | Dict[str, Any]): The protocol configuration filepath or data.
            praxis_config (str | PraxisConfiguration): The Praxis configuration filepath or object.
        """
        if isinstance(praxis_config, str):
            praxis_config = PraxisConfiguration(praxis_config)
        if not isinstance(praxis_config, PraxisConfiguration):
            raise ValueError("Invalid configuration object.")
        if isinstance(protocol_config, str):
            with open(protocol_config, "r") as f:
                config_data = json.load(f)
        elif isinstance(protocol_config, dict):
            config_data = protocol_config
        self._config_data = config_data
        self.praxis_config = praxis_config
        self.deck_directory = praxis_config.deck_directory
        self.asset_db_file = praxis_config.asset_db
        self.asset_database = AsyncAssetDatabase(self.asset_db_file)
        self._machines: list[str | int] = cast(list, config_data.get("machines", []))
        self.liquid_handler_id: str = cast(str, config_data.get("liquid_handler_ids",
                                                                              []))
        self.name: str = cast(str, config_data.get("name", ""))
        self.details: str = cast(str, config_data.get("details", ""))
        self.description: str = cast(str, config_data.get("description", ""))
        self.other_args: dict[str, Any] = cast(dict, config_data.get("other_args", {}))
        self.users: str | list[str] = self._parse_users(config_data.get("users", []))
        self.directory: str = cast(str, config_data.get("directory", ""))
        self._deck: str = cast(str, config_data.get("deck", ""))
        self.parameters = ProtocolParameters(config_data.get("parameters", {}))

    def _parse_users(self, users_data: Any) -> str | list[str]:
        """Parses the users field from the config data."""
        if isinstance(users_data, str):
            return users_data  # Single user as a string
        elif isinstance(users_data, list):
            return [user for user in users_data if isinstance(user, str)]  # List of users
        elif isinstance(users_data, dict):
            return [user for user in users_data.keys() if isinstance(user, str)]
        else:
            return []  # Default to empty list if invalid format

    @property
    def deck(self) -> Optional[Deck]:
        """
        Loads and returns the deck layout for each liquid handler specified in the configuration.
        """
        if not self.deck_directory:
            return None

        deck_path = os.path.join(self.deck_directory, self._deck)
        if not os.path.exists(deck_path):
            raise FileNotFoundError(f"Deck file not found: {deck_path}")
        return Deck.load_from_json_file(deck_path)
