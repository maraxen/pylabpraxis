import configparser
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
        self.database = self.get_section("database")
        self.redis = self.get_section("redis")
        self.email = self.get_section("email")
        self.celery = self.get_section("celery")
        self.logging = self.get_section("logging")
        self.deck_management = self.get_section("deck_management")
        self.baseline_decks = self.get_section("baseline_decks")
        self.smtp_server = self.email.get("smtp_server", "localhost")
        self.smtp_port = self.email.get("smtp_port", 25)
        self.smtp_username = self.email.get("smtp_username", "")
        self.smtp_password = self.email.get("smtp_password", "")
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
        self.log_file = self.logging.get("logfile", "/var/log/praxis/praxis.log")
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

        # Add default Keycloak configuration
        if not self.config.has_section("keycloak"):
            self.config.add_section("keycloak")
            self.config.set("keycloak", "server_url", "http://localhost:8080")
            self.config.set("keycloak", "realm_name", "praxis")
            self.config.set("keycloak", "client_id", "praxis-client")
            self.config.set(
                "keycloak", "client_secret", ""
            )  # TODO: see if this is deprecated

        # Update database configuration handling
        self.database = self.get_section("database")
        if "praxis_dsn" not in self.database:
            self.database["praxis_dsn"] = (
                "postgresql://praxis:praxis@localhost:5432/praxis_db"
            )
        if "keycloak_dsn" not in self.database:
            self.database["keycloak_dsn"] = (
                "postgresql://keycloak:keycloak@localhost:5432/keycloak"
            )

        # Ensure DSNs have proper scheme
        for key in ["praxis_dsn", "keycloak_dsn"]:
            if self.database[key] and not self.database[key].startswith(
                ("postgresql://", "postgres://")
            ):
                self.database[key] = f"postgresql://{self.database[key]}"

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

    def get_keycloak_config(self):
        """Get Keycloak configuration."""
        if not self.config.has_section("keycloak"):
            raise ValueError("Keycloak configuration not found")

        return {
            "server_url": self.config.get("keycloak", "server_url"),
            "realm_name": self.config.get("keycloak", "realm_name"),
            "client_id": self.config.get("keycloak", "client_id"),
            "client_secret": self.config.get("keycloak", "client_secret"),
            "client_initial_access_token": self.config.get(
                "keycloak", "client_initial_access_token", fallback=None
            ),
        }

    def save_keycloak_config(self, client_id: str, client_secret: str) -> None:
        """Save Keycloak client credentials."""
        if not self.config.has_section("keycloak"):
            self.config.add_section("keycloak")

        self.config.set("keycloak", "client_id", client_id)
        self.config.set("keycloak", "client_secret", client_secret)

        with open(self.config_file, "w") as f:
            self.config.write(f)

    def smtp_details(self):
        return {
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
            "smtp_username": self.smtp_username,
            "smtp_password": self.smtp_password,
        }

    def _get_protocol_discovery_dirs(self) -> List[str]:
        """Get the protocol discovery directories."""
        protocol_discovery_dirs = self.get_section("protocol_discovery")
        dirs = protocol_discovery_dirs.get("directories", "")
        return [d.strip() for d in dirs.split(",") if d.strip()]
