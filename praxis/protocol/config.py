import os
import json
from typing import Dict, Any, Optional, cast, Mapping
from ..configure import PraxisConfiguration
from ..interfaces import WorkcellInterface, WorkcellAssetsInterface
from .parameter import ProtocolParameters, Parameter
from .required_assets import WorkcellAssets, WorkcellAssetSpec
from ..utils import db


class ProtocolConfiguration:
    """
    Protocol configuration denoting specific settings for a method.
    """

    def __init__(
        self,
        protocol_config: str | Dict[str, Any],
        praxis_config: Optional[str | PraxisConfiguration] = None,
    ):
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
        self.config_data = config_data
        self.praxis_config = praxis_config
        self.deck_directory = praxis_config.deck_directory
        self.db = db
        self._machines: list[str | int] = cast(list, config_data.get("machines", []))
        self.liquid_handler_ids: list[str] = cast(
            list[str], config_data.get("liquid_handler_ids", [])
        )
        self.name: str = cast(str, config_data.get("name", ""))
        self.details: str = cast(str, config_data.get("details", ""))
        self.description: str = cast(str, config_data.get("description", ""))
        self.other_args: dict[str, Any] = cast(dict, config_data.get("other_args", {}))
        self.users: str | list[str] = self._parse_users(config_data.get("users", []))
        self.directory: str = cast(str, config_data.get("directory", ""))
        self._decks: dict[str, str] = cast(dict[str, str], config_data.get("decks", ""))

        # Add workcell configuration options
        self.workcell_file: Optional[str] = cast(
            Optional[str], config_data.get("workcell_file")
        )
        self.workcell: Optional[WorkcellInterface] = None

        # Initialize parameters
        self._parameters = ProtocolParameters()
        params_data = config_data.get("parameters", {})
        for name, value in params_data.items():
            if isinstance(value, dict) and "type" in value:
                # Parameter specification with metadata
                self._parameters.add_parameter_from_dict(name, value)
            else:
                # Simple parameter value
                param = Parameter(name=name, datatype=type(value), default=value)
                self._parameters.add_parameter(param)

        # Parse required assets
        self._required_assets = WorkcellAssets()
        assets_data = config_data.get("required_assets", {})
        if isinstance(assets_data, Mapping):
            self._required_assets.load_from_dict(assets_data)

        self.user_info: dict[str, Any] = cast(
            dict, config_data.get("user_info", {})
        )  # TODO: check structure

    @property
    def machines(self) -> list[str | int]:
        """Get the machines."""
        return self._machines

    def _parse_users(self, users: str | list[str] | None) -> str | list[str]:
        """Parse user information from configuration."""
        if users is None:
            return []
        if isinstance(users, str):
            return [users]
        return users

    @property
    def parameters(self) -> ProtocolParameters:
        """Get the protocol parameters."""
        return self._parameters

    @property
    def required_assets(self) -> WorkcellAssets:
        """Get the required workcell assets."""
        return self._required_assets

    @property
    def decks(self) -> dict[str, str]:
        """Get the deck names specified for a given liquid handler."""
        return self._decks

    @property
    def decks_unspecified(self) -> bool:
        """See if decks are assigned to liquid handlers. This can be bypassed if a workcell is loaded
        directly with the decks initialized."""
        return self._decks == {}

    def __getitem__(self, key: Any) -> Any | None:
        return self.config_data.get(key, None)
