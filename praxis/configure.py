import configparser
import json
from typing import Dict, Any, List, cast
import os


class PraxisConfiguration:
    """
    Configuration class to handle Praxis configuration settings.
    """

    def __init__(self, config_file: str = "praxis.ini"):
        self.config_file = config_file
        self.config = self._load_config(config_file)
        self.protocol_discovery_dirs = self._get_protocol_discovery_dirs()
        self.output_dirs = self._get_output_dirs()
        self.databases = self.get_section("database")
        self.redis = self.get_section("redis")
        self.email = self.get_section("email")
        self.celery = self.get_section("celery")
        self.logging = self.get_section("logging")
        self.deck_management = self.get_section("deck_management")
        self.baseline_decks = self.get_section("baseline_decks")
        self.registry_db = self.databases.get("registry_path", "protocol_registry.db")
        self.data_directory = self.databases.get("data_directory", "data")
        self.asset_db = self.databases.get("asset_db", "lab_inventory.json")
        self.users = self.databases.get("users", "users.json")
        self.smtp_server = self.email.get("smtp_server", "localhost")
        self.smtp_port = self.email.get("smtp_port", 25)
        self.redis_host = self.redis.get("host", "localhost")
        self.redis_port = self.redis.get("port", 6379)
        self.redis_db = self.redis.get("db", 0)
        self.broker_url = self.celery.get("broker_url", "redis://localhost:6379/0")
        self.result_backend = self.celery.get(
            "result_backend", "redis://localhost:6379/0"
        )
        self.deck_directory = self.deck_management.get("deck_directory", "decks")
        self.baseline_decks = cast(dict[str, str], self.baseline_decks) or {}
        self.logging_level = self.logging.get("level", "INFO")
        self.log_file = self.logging.get("file", "/var/log/praxis/praxis.log")
        self.admin_credentials = self.get_section("admin")
        self.protocol_directories = self.get_section("protocol_directories")
        self.default_protocol_dir = self.protocol_directories.get(
            "default_directory",
            os.path.join(os.path.dirname(__file__), "protocol", "protocols"),
        )
        self.additional_directories = self.protocol_directories.get(
            "additional_directories", ""
        )
        if not os.path.exists(self.default_protocol_dir):
            os.makedirs(self.default_protocol_dir)

    def _load_config(self, config_file: str) -> configparser.ConfigParser:
        """Loads the configuration file."""
        config = configparser.ConfigParser()
        config.read(config_file)
        return config

    def __getitem__(self, key: str) -> Any:
        return self.config[key]

    def get_section(self, section_name: str) -> Dict[str, Any]:
        """Gets a section from the config file."""
        if section_name not in self.config:
            return {}
        return dict(self.config[section_name])

    def add_lab_resource(self, resource_data: Dict[str, Any]):
        """Appends a new resource to the lab inventory file."""
        if not os.path.exists(self.asset_db):
            with open(self.asset_db, "w") as f:
                json.dump([], f)  # Create an empty list for the first entry

        with open(self.asset_db, "r+") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []  # Initialize as an empty list if file is empty or invalid
            if not isinstance(data, list):
                raise ValueError(
                    "Invalid lab inventory file format. Must be a JSON list."
                )
            data.append(resource_data)
            f.seek(0)  # Go to the beginning of the file
            json.dump(data, f, indent=4)
            f.truncate()  # Remove any remaining old content

    def get_lab_resources(self) -> List[Dict[str, Any]]:
        """Retrieves all resources from the lab inventory file."""
        if not os.path.exists(self.asset_db):
            return []
        with open(self.asset_db, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return []  # Return empty list if file is empty or invalid
            if not isinstance(data, list):
                raise ValueError(
                    "Invalid lab inventory file format. Must be a JSON list."
                )
            return data

    def get_lab_users(self) -> "PraxisUsers":
        """Creates and returns a PraxisUsers object."""
        return PraxisUsers(self.users)

    def get_user_info(self, username: str) -> Dict[str, Any]:
        """Retrieves user information."""
        return self.get_lab_users().get_user_info(username)

    def get_protocol_directories(self) -> List[str]:
        """Get list of additional protocol directories."""
        dirs_str = self.config.get(
            "protocol_directories", "additional_directories", fallback=""
        ).strip()
        return [d.strip() for d in dirs_str.split(",") if d.strip()] if dirs_str else []

    def remove_protocol_directory(self, directory: str) -> None:
        """Remove a directory from the protocol search paths."""
        dirs = self.get_protocol_directories()
        if directory in dirs:
            dirs.remove(directory)
            self.config.set(
                "protocol_directories", "additional_directories", ",".join(dirs)
            )
            with open(self.config_file, "w") as f:
                self.config.write(f)

    def add_protocol_directory(self, directory: str) -> None:
        """Add a directory to protocol search paths."""
        dirs = self.get_protocol_directories()
        if directory not in dirs:
            dirs.append(directory)
            self.config.set(
                "protocol_directories", "additional_directories", ",".join(dirs)
            )
            with open(self.config_file, "w") as f:
                self.config.write(f)

    def _get_protocol_discovery_dirs(self) -> List[str]:
        """Get protocol discovery directories from config."""
        if "protocol_discovery" not in self.config:
            return ["./protocols"]
        directories = self.config["protocol_discovery"].get(
            "directories", fallback="./protocols"
        )
        if not isinstance(directories, str):
            return ["./protocols"]
        return [d.strip() for d in directories.split(",") if d.strip()]

    def _get_output_dirs(self) -> Dict[str, str]:
        """Get output directories from config."""
        if "output_directories" not in self.config:
            return {
                "protocol_output": "./protocol_output",
                "workcell_save": "./workcell_saves",
                "data_backup": "./data_backups",
            }
        return {
            "protocol_output": self.config["output_directories"].get(
                "protocol_output", "./protocol_output"
            ),
            "workcell_save": self.config["output_directories"].get(
                "workcell_save", "./workcell_saves"
            ),
            "data_backup": self.config["output_directories"].get(
                "data_backup", "./data_backups"
            ),
        }


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
                    print(
                        f"Warning: Invalid user configuration for '{user}'. Skipping."
                    )
        return members

    def get_user_info(self, username: str) -> Dict[str, Any]:
        """Retrieves user information."""
        return self.members.get(username, {})
