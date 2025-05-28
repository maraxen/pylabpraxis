"""
This module is the PRANCE protocol. It is a complex protocol that requires a lot of setup and teardown.
It uses the liquid handler to move liquids around, pumps to pump bacteria, water, and bleach onto the robot and more.

Attributes:


"""

from typing import Optional, List
from datetime import datetime as dt, timedelta
from itertools import product

from praxis.protocol.protocol import Protocol
from praxis.protocol.config import ProtocolConfiguration
from praxis.protocol.required_assets import WorkcellAssets
from praxis.protocol.parameter import ProtocolParameters
from pylabrobot.resources import Plate, TipRack, Resource
from pylabrobot.plate_reading import PlateReader
from pylabrobot.pumps import PumpArray

# Initialize protocol parameters with default values
baseline_parameters = ProtocolParameters(
    {
        "tips_staged": {
            "type": bool,
            "description": "Whether tips have been staged on the deck",
            "default": False,
        },
        "bacteria_ids": {
            "type": list,
            "description": "List of bacteria IDs to use",
            "default": [],
        },
        "phage_ids": {
            "type": list,
            "description": "List of phage IDs to use",
            "default": [],
        },
        "no_phage_control": {
            "type": int,
            "description": "Number of no-phage control wells",
            "default": 0,
        },
        "cycle_time": {
            "type": int,
            "description": "Time between cycles in minutes",
            "default": 60,
            "constraints": {"min_value": 1},
        },
        "sampling_interval": {
            "type": int,
            "description": "Time between samples in minutes",
            "default": 30,
            "constraints": {"min_value": 1},
        },
        "mixing": {
            "type": bool,
            "description": "Whether to mix samples",
            "default": True,
        },
        "mixing_volume": {
            "type": float,
            "description": "Volume to use for mixing in µL",
            "default": 100.0,
            "constraints": {"min_value": 10.0, "max_value": 1000.0},
        },
        "mixing_speed": {
            "type": float,
            "description": "Speed to use for mixing in µL/s",
            "default": 100.0,
            "constraints": {"min_value": 10.0, "max_value": 1000.0},
        },
        "mixing_cycles": {
            "type": int,
            "description": "Number of mixing cycles",
            "default": 3,
            "constraints": {"min_value": 1, "max_value": 10},
        },
        "lagoon_flow_rate": {
            "type": float,
            "description": "Flow rate for lagoon operations in mL/min",
            "default": 0.5,
            "constraints": {"min_value": 0.1, "max_value": 5.0},
        },
        "washer_volume": {
            "type": float,
            "description": "Volume to use for washing in µL",
            "default": 1000.0,
            "constraints": {"min_value": 100.0, "max_value": 5000.0},
        },
        "basin_refill_frequency": {
            "type": int,
            "description": "How often to refill the basin in hours",
            "default": 24,
            "constraints": {"min_value": 1, "max_value": 72},
        },
        "inducer_volume": {
            "type": float,
            "description": "Volume of inducer to add in µL",
            "default": 50.0,
            "constraints": {"min_value": 1.0, "max_value": 1000.0},
        },
    }
)

# Initialize deck assets with a dictionary
required_assets = WorkcellAssets(
    {
        "pumps1": {"type": PumpArray, "description": "Fluidic pump 1"},
        "pumps2": {"type": PumpArray, "description": "Fluidic pump 2"},
        "tip_washer": {"type": Resource, "description": "Washer for tip cleaning"},
        "sample_reservoir": {
            "type": Resource,
            "description": "Reservoir for samples",
        },
        "holding": {"type": Plate, "description": "Plate for holding samples"},
        "induced": {"type": Plate, "description": "Plate for induced samples"},
        "lagoons": {"type": Plate, "description": "Plate for lagoon samples"},
        "holding_tip_rack": {
            "type": TipRack,
            "description": "Tip rack for holding operations",
        },
        "induced_tip_rack": {
            "type": TipRack,
            "description": "Tip rack for induction operations",
        },
        "lagoon_tip_rack_1": {
            "type": TipRack,
            "description": "First tip rack for lagoon operations",
        },
        "plate_reader": {
            "type": PlateReader,
            "description": "Reader for plate measurements",
        },
    }
)


class Prance(Protocol):
    """Prance is a complex protocol that requires a lot of setup and teardown. It uses the liquid handler
    to move liquids around, pumps to pump bacteria, water, and bleach onto the robot and more.
    """

    def __init__(self, config: ProtocolConfiguration):
        """Initialize the Prance protocol."""
        super().__init__(
            config,
        )
        self.baseline_parameters = baseline_parameters
        # Initialize instance attributes
        self.cycle_n: int = 0
        self.cycle_start_time: dt = dt.now()
        self.reader_plate_stack_in_use: Optional[str] = None

        # Validate and get parameters from configuration
        params = config.parameters
        params.validate_parameters(self.baseline_parameters._values)

        # Store parameters as instance attributes with proper type hints
        self.tips_staged: bool = params.get("tips_staged", False)
        self.bacteria_ids: List[str] = params.get("bacteria_ids", [])
        self.phage_ids: List[str] = params.get("phage_ids", [])
        self.no_phage_control: int = params.get("no_phage_control", 0)
        self.cycle_time: timedelta = timedelta(minutes=params.get("cycle_time", 60))
        self.sampling_interval: timedelta = timedelta(
            minutes=params.get("sampling_interval", 30)
        )
        self.mixing: bool = params.get("mixing", True)
        self.mixing_volume: float = params.get("mixing_volume", 100.0)
        self.mixing_speed: float = params.get("mixing_speed", 100.0)
        self.mixing_cycles: int = params.get("mixing_cycles", 3)
        self.lagoon_flow_rate: float = params.get("lagoon_flow_rate", 0.5)
        self.washer_volume: float = params.get("washer_volume", 1000.0)
        self.basin_refill_frequency: timedelta = timedelta(
            hours=params.get("basin_refill_frequency", 24)
        )
        self.inducer_volume: float = params.get("inducer_volume", 50.0)

        # Initialize state
        self._status = "initialized"

        # Generate variable combinations
        self.variable_combinations = list(product(self.bacteria_ids, self.phage_ids))

        if (
            len(self.variable_combinations)
            + (self.no_phage_control * len(self.bacteria_ids))
            > 48
        ):
            raise ValueError(
                "Too many variable combinations. A maximum of 48 are supported."
            )

    def _check_deck_resources(self, workcell_assets: WorkcellAssets) -> None:
        """Check that the deck has all the resources needed for the protocol."""
        pass

    def _check_parameters(self, parameters: dict[str, type]) -> None:
        """Check the parameters for the protocol bounded by method specific constraints."""
        # The parameter validation is now handled by the ProtocolParameters class
        pass
