"""Configuration class for managing Praxis application settings."""

import configparser
import os
from typing import Any


class PraxisConfiguration:

  """Configuration class to handle Praxis configuration settings."""

  def __init__(self, config_file: str = "praxis.ini") -> None:
    """Initialize the PraxisConfiguration by loading the specified config file.

    Args:
        config_file (str): The path to the configuration file. Defaults to "praxis.ini".

    """
    self._config_file_path: str = config_file
    self._config_parser: configparser.ConfigParser = self._load_config(config_file)

  def _load_config(self, config_file: str) -> configparser.ConfigParser:
    """Load the configuration file.

    Args:
      config_file (str): The path to the configuration file.

    """
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

  def _get_section_dict(self, section_name: str) -> dict[str, str]:
    """Get a section from the config parser as a dictionary of strings.

    Args:
      section_name (str): The name of the section to retrieve.

    Returns:
      dict[str, str]: A dictionary of key-value pairs from the section.

    """
    if section_name not in self._config_parser:
      return {}
    return dict(self._config_parser[section_name])

  @property
  def _database_section(self) -> dict[str, str]:
    """Return the 'database' section as a dictionary."""
    return self._get_section_dict("database")

  @property
  def praxis_dsn(self) -> str:
    """Return the Praxis database DSN.

    Ensures the DSN starts with 'postgresql://' or 'postgres://'.

    Returns:
        str: The Praxis database connection string.

    """
    dsn = self._database_section.get(
      "praxis_dsn",
      "postgresql://praxis:praxis@localhost:5432/praxis_db",
    )
    if not dsn.startswith(("postgresql://", "postgres://")):
      return f"postgresql://{dsn}"
    return dsn

  @property
  def keycloak_dsn(self) -> str:
    """Return the Keycloak database DSN.

    Ensures the DSN starts with 'postgresql://' or 'postgres://'.

    Returns:
        str: The Keycloak database connection string.

    """
    dsn = self._database_section.get(
      "keycloak_dsn",
      "postgresql://keycloak:keycloak@localhost:5432/keycloak",
    )
    if not dsn.startswith(("postgresql://", "postgres://")):
      return f"postgresql://{dsn}"
    return dsn

  @property
  def _email_section(self) -> dict[str, str]:
    """Return the 'email' section as a dictionary."""
    return self._get_section_dict("email")

  @property
  def smtp_server(self) -> str:
    """Return the SMTP server address."""
    return self._email_section.get("smtp_server", "localhost")

  @property
  def smtp_port(self) -> int:
    """Return the SMTP server port."""
    return int(self._email_section.get("smtp_port", "25"))

  @property
  def smtp_username(self) -> str:
    """Return the SMTP username."""
    return self._email_section.get("smtp_username", "")

  @property
  def smtp_password(self) -> str:
    """Return the SMTP password."""
    return self._email_section.get("smtp_password", "")

  @property
  def _redis_section(self) -> dict[str, str]:
    """Return the 'redis' section as a dictionary."""
    return self._get_section_dict("redis")

  @property
  def redis_host(self) -> str:
    """Return the Redis host."""
    return self._redis_section.get("host", "127.0.0.1")

  @property
  def redis_port(self) -> int:
    """Return the Redis port."""
    return int(self._redis_section.get("port", "6379"))

  @property
  def redis_db(self) -> int:
    """Return the Redis database number."""
    return int(self._redis_section.get("db", "0"))

  @property
  def redis_url(self) -> str:
    """Return the Redis connection URL."""
    return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

  @property
  def _celery_section(self) -> dict[str, str]:
    """Return the 'celery' section as a dictionary."""
    return self._get_section_dict("celery")

  @property
  def celery_broker_url(self) -> str:
    """Return the Celery broker URL."""
    return self._celery_section.get("broker", "redis://127.0.0.1:6379/0")

  @property
  def celery_result_backend(self) -> str:
    """Return the Celery result backend URL."""
    return self._celery_section.get("backend", "redis://127.0.0.1:6379/0")

  @property
  def _logging_section(self) -> dict[str, str]:
    """Return the 'logging' section as a dictionary."""
    return self._get_section_dict("logging")

  @property
  def logging_level(self) -> str:
    """Return the logging level."""
    return self._logging_section.get("level", "INFO")

  @property
  def log_file(self) -> str:
    """Return the log file path."""
    return self._logging_section.get("logfile", "/var/log/praxis/praxis.log")

  def _output_directories_section(self) -> dict[str, str]:
    """Return the 'output_directories' section as a dictionary."""
    return self._get_section_dict("output_directories")

  @property
  def protocol_output_directory(self) -> str:
    """Return the protocol output directory path."""
    path = self._output_directories_section.get("protocol_output", "./protocol_output")
    os.makedirs(path, exist_ok=True)  # Ensure the directory exists
    return path

  @property
  def _admin_section(self) -> dict[str, str]:
    """Return the 'admin' section as a dictionary."""
    return self._get_section_dict("admin")

  @property
  def admin_credentials(self) -> dict[str, str]:
    """Return the admin credentials."""
    return self._admin_section

  @property
  def _protocol_directories_section(self) -> dict[str, str]:
    """Return the 'protocol_directories' section as a dictionary."""
    return self._get_section_dict("protocol_directories")

  @property
  def default_protocol_dir(self) -> str:
    """Return the default protocol directory path.

    Ensures the directory exists.
    """
    default_path = os.path.join(os.path.dirname(__file__), "protocol", "protocols")
    path = self._protocol_directories_section.get("default_directory", default_path)
    os.makedirs(
      path,
      exist_ok=True,
    )  # Use exist_ok=True to avoid error if it already exists
    return path

  @property
  def additional_directories(self) -> list[str]:
    """Return a list of additional protocol directories."""
    dirs_str = self._protocol_directories_section.get("additional_directories", "")
    return [d.strip() for d in dirs_str.split(",") if d.strip()]

  @property
  def _protocol_discovery_section(self) -> dict[str, str]:
    """Return the 'protocol_discovery' section as a dictionary."""
    return self._get_section_dict("protocol_discovery")

  @property
  def protocol_discovery_dirs(self) -> list[str]:
    """Return a list of protocol discovery directories."""
    dirs_str = self._protocol_discovery_section.get("directories", "")
    return [d.strip() for d in dirs_str.split(",") if d.strip()]

  @property
  def all_protocol_source_paths(self) -> list[str]:
    """Return a list of all directories where protocol source code can be found.

    Combines default, additional, and discovery directories, ensuring uniqueness
    and absolute paths.
    """
    all_paths = set()

    # Add default protocol directory
    all_paths.add(os.path.abspath(self.default_protocol_dir))

    # Add additional directories
    for d in self.additional_directories:
      all_paths.add(os.path.abspath(d))

    # Add protocol discovery directories
    for d in self.protocol_discovery_dirs:
      all_paths.add(os.path.abspath(d))

    return sorted(all_paths)

  @property
  def _keycloak_section(self) -> dict[str, str]:
    """Return the 'keycloak' section as a dictionary, handling its potential absence."""
    # This section might not exist initially, so handle it gracefully
    if not self._config_parser.has_section("keycloak"):
      return {}
    return self._get_section_dict("keycloak")

  def get_keycloak_config(self) -> dict[str, str | None]:
    """Get Keycloak configuration.

    Returns:
        dict[str, Optional[str]]: A dictionary containing Keycloak configuration
        details.

    """
    section = self._keycloak_section
    return {
      "server_url": section.get("server_url"),
      "realm_name": section.get("realm_name"),
      "client_id": section.get("client_id"),
      "client_secret": section.get("client_secret"),
      "client_initial_access_token": section.get("client_initial_access_token"),
    }

  def save_keycloak_config(self, client_id: str, client_secret: str) -> None:
    """Save Keycloak client credentials to the configuration file.

    Args:
      client_id (str): The Keycloak client ID.
      client_secret (str): The Keycloak client secret.

    """
    if not self._config_parser.has_section("keycloak"):
      self._config_parser.add_section("keycloak")

    self._config_parser.set("keycloak", "client_id", client_id)
    self._config_parser.set("keycloak", "client_secret", client_secret)

    with open(self._config_file_path, "w") as f:
      self._config_parser.write(f)

  @property
  def smtp_details(self) -> dict[str, Any]:
    """Get SMTP server details."""
    return {
      "smtp_server": self.smtp_server,
      "smtp_port": self.smtp_port,
      "smtp_username": self.smtp_username,
      "smtp_password": self.smtp_password,
    }
