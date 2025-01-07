import configparser
import json
from typing import Dict, Any, List, cast
import os
from os import PathLike
from typing import Dict, Any, cast, Optional, List
from ..protocol import ProtocolParameters  # Assuming parameter.py is in the same protocol module
from pylabrobot.resources import Deck


class PraxisConfiguration:
  """
  Configuration class to handle Praxis configuration settings.
  """
  def __init__(self, config_file: str = "praxis.ini"):
      self.config_file = config_file
      self.config = configparser.ConfigParser()
      self.config.read(config_file)
      self.databases = self.get_section("database")
      self.redis = self.get_section("redis")
      self.email = self.get_section("email")
      self.celery = self.get_section("celery")
      self.logging = self.get_section("logging")
      self.deck_management = self.get_section("deck_management")
      self.baseline_decks = self.get_section("baseline_decks")
      self.registry_path = self.databases.get("registry_path", "registry.json")
      self.data_directory = self.databases.get("data_directory", "data")
      self.lab_inventory = self.databases.get("lab_inventory", "lab_inventory.json")
      self.users = self.databases.get("users", "users.json")
      self.smtp_server = self.email.get("smtp_server", "localhost")
      self.smtp_port = self.email.get("smtp_port", 25)
      self.redis_host = self.redis.get("host", "localhost")
      self.redis_port = self.redis.get("port", 6379)
      self.redis_db = self.redis.get("db", 0)
      self.broker_url = self.celery.get("broker_url", "redis://localhost:6379/0")
      self.result_backend = self.celery.get("result_backend", "redis://localhost:6379/0")
      self.deck_directory = self.deck_management.get("deck_directory", "decks")
      self.baseline_decks = self.baseline_decks or {}
      self.logging_level = self.logging.get("level", "INFO")
      self.log_file = self.logging.get("file", "/var/log/praxis/praxis.log")

  def get_section(self, section_name: str) -> Dict[str, Any]:
      """Gets a section from the config file."""
      if section_name not in self.config:
          return {}
      return dict(self.config[section_name])

  def add_lab_resource(self, resource_data: Dict[str, Any]):
      """Appends a new resource to the lab inventory file."""
      if not os.path.exists(self.inventory_file):
          with open(self.inventory_file, "w") as f:
              json.dump([], f)  # Create an empty list for the first entry

      with open(self.inventory_file, "r+") as f:
          try:
              data = json.load(f)
          except json.JSONDecodeError:
              data = []  # Initialize as an empty list if file is empty or invalid
          if not isinstance(data, list):
              raise ValueError("Invalid lab inventory file format. Must be a JSON list.")
          data.append(resource_data)
          f.seek(0)  # Go to the beginning of the file
          json.dump(data, f, indent=4)
          f.truncate()  # Remove any remaining old content

  def get_lab_resources(self) -> List[Dict[str, Any]]:
      """Retrieves all resources from the lab inventory file."""
      if not os.path.exists(self.inventory_file):
          return []
      with open(self.inventory_file, "r") as f:
          try:
              data = json.load(f)
          except json.JSONDecodeError:
              return []  # Return empty list if file is empty or invalid
          if not isinstance(data, list):
              raise ValueError("Invalid lab inventory file format. Must be a JSON list.")
          return data

  def get_lab_users(self) -> "PraxisUsers":
      """Creates and returns a PraxisUsers object."""
      return PraxisUsers(self.users)


class PraxisUsers:
    def __init__(self, config: configparser.ConfigParser):
        self.config = config
        self.members: Dict[str, Dict[str, Any]] = self._load_members()

    def _load_members(self) -> Dict[str, Dict[str, Any]]:
        """Loads user information from the config file."""
        members = {}
        if "users" in self.config:
            for user, user_config_str in self.config.items("users"):
                try:
                    user_config = json.loads(user_config_str)
                    members[user] = user_config
                except json.JSONDecodeError:
                    print(f"Warning: Invalid user configuration for '{user}'. Skipping.")
        return members

    def get_user_info(self, username: str) -> Dict[str, Any]:
        """Retrieves user information."""
        return self.members.get(username, {})

class ProtocolConfiguration:
    """
    Protocol configuration denoting specific settings for a method.
    """

    def __init__(self, config_data: Dict[str, Any], deck_directory: str):
        """
        Initializes the ProtocolConfiguration.

        Args:
            config_data: The configuration data for the protocol, typically loaded from a JSON file.
            deck_directory: The directory where deck layout files are stored.
        """
        self._config_data = config_data
        self.machines: list[str | int] = cast(list, config_data.get("machines", []))
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
        self.deck_directory = deck_directory

    def _parse_users(self, users_data: Any) -> str | list[str]:
        """Parses the users field from the config data."""
        if isinstance(users_data, str):
            return users_data  # Single user as a string
        elif isinstance(users_data, list):
            return [user for user in users_data if isinstance(user, str)]  # List of users
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
