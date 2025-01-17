from typing import Any, Dict, Optional, cast, Union, Type
from datetime import datetime as dt, timedelta
from itertools import product
import asyncio

from praxis.protocol.protocol import Protocol
from praxis.protocol.config import ProtocolConfiguration
from praxis.utils.state import State
from praxis.core.orchestrator import Orchestrator
from pylabrobot.resources import (
    Deck,
    Plate,
    TipRack,
    TipSpot,
    Well,
    Resource,
    Lid,
)
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.plate_reading import PlateReader
from praxis.commons.commons import (
    PumpManager,
    TipWasher,
    SampleReservoir,
)

needed_parameters: Dict[str, type] = {
    "tips_staged": bool,
    "bacteria_ids": list,
    "phage_ids": list,
    "no_phage_control": int,
    "cycle_time": int,
    "sampling_interval": int,
    "mixing": bool,
    "mixing_volume": float,
    "mixing_speed": float,
    "mixing_cycles": int,
    "lagoon_flow_rate": float,
    "washer_volume": float,
    "basin_refill_frequency": timedelta,
    "inducer_volume": float,
}

needed_deck_resources: Dict[str, type] = {
    "pump_manager": PumpManager,
    "tip_washer": TipWasher,
    "sample_reservoir": SampleReservoir,
    "holding": Plate,
    "induced": Plate,
    "lagoons": Plate,
    "holding_tip_rack": TipRack,
    "induced_tip_rack": TipRack,
    "lagoon_tip_rack_1": TipRack,
    "plate_reader": PlateReader,
}

deck_resource_types: Dict[str | int, Dict[str, type]] = {
    str(i): {"type": resource_type}
    for i, (_, resource_type) in enumerate(needed_deck_resources.items())
}


class Prance(Protocol):
    """Prance is a complex protocol that requires a lot of setup and teardown. It uses the liquid handler
    to move liquids around, pumps to pump bacteria, water, and bleach onto the robot and more.
    """

    def __init__(
        self,
        protocol_configuration: ProtocolConfiguration,
        state: State,
        manual_check_list: list[str],
        orchestrator: Orchestrator,
        deck: Optional[Deck] = None,
        user_info: Optional[Dict[str, Dict]] = None,
        **kwargs,
    ):
        """Initialize the Prance protocol.

        Args:
            protocol_configuration: Protocol configuration object
            state: State object for storing protocol state
            manual_check_list: List of manual checks to perform
            orchestrator: Orchestrator instance
            deck: Optional deck configuration
            user_info: Optional user information
            **kwargs: Additional keyword arguments
        """
        super().__init__(
            protocol_configuration=protocol_configuration,
            state=state,
            manual_check_list=manual_check_list,
            orchestrator=orchestrator,
            deck=deck,
            user_info=user_info,
            **kwargs,
        )

        # Initialize instance attributes
        self.cycle_n: int = 0
        self.cycle_start_time: dt = dt.now()
        self.reader_plate_stack_in_use: Optional[str] = None
        self.cycle_time: timedelta = timedelta(minutes=60)  # Default value

        # Get parameters with defaults
        params = protocol_configuration.parameters
        tips_staged = False
        bacteria_ids = []
        phage_ids = []
        no_phage_control = 0
        cycle_time_minutes = 60

        # Try to get parameters from configuration
        try:
            tips_staged = bool(params.tips_staged)
            bacteria_ids = list(params.bacteria_ids)
            phage_ids = list(params.phage_ids)
            no_phage_control = int(params.no_phage_control)
            cycle_time_minutes = int(params.cycle_time)
        except AttributeError:
            pass

        self.cycle_time = timedelta(minutes=cycle_time_minutes)

        if not tips_staged:
            raise ValueError(
                "Tips are not staged. Run tip_staging.py with PRANCE specified."
            )

        self._available_commands["add_phage"] = "Add phage to the phage control wells."

        # Load state if already ran
        if self.state[self.name].get("cycle_n") is not None:
            self.cycle_n = self.state[self.name]["cycle_n"]
            self.cycle_start_time = self.state[self.name]["cycle_start_time"]
            self.reader_plate_stack_in_use = self.state[self.name][
                "reader_plate_stack_in_use"
            ]
        else:
            self.reader_plate_stack_in_use = self.state[self.name].get(
                "to_read_plate_stack"
            )

        # Generate variable combinations
        self.variable_combinations = list(product(bacteria_ids, phage_ids))

        if (
            len(self.variable_combinations) + (no_phage_control * len(bacteria_ids))
            > 48
        ):
            raise ValueError(
                "Too many variable combinations. A maximum of 48 are supported."
            )

    async def _setup(self) -> None:
        """Setup the protocol."""
        print("Setting up Prance protocol...")

        # Initialize resources and verify configuration
        await self.check_protocol_configuration(needed_parameters)
        await self._check_deck_resources(deck_resource_types)

        # Initialize protocol state
        self._status = "initializing"
        self.cycle_n = 0
        self.cycle_start_time = dt.now()

        print("Prance protocol setup complete.")

    async def _execute(self) -> None:
        """Execute the protocol."""
        print("Starting Prance protocol execution...")

        try:
            self._status = "running"
            while not self.failed and not self.paused:
                print(f"Starting cycle {self.cycle_n}")
                await self.run_cycle()
                self.cycle_n += 1
                await asyncio.sleep(self.cycle_time.total_seconds())
        except Exception as e:
            self._status = "failed"
            print(f"Protocol failed: {str(e)}")
            raise

    async def _pause(self) -> None:
        """Pause the protocol."""
        print("Pausing Prance protocol...")
        self._status = "paused"
        await self.save_state()

    async def _resume(self) -> None:
        """Resume the protocol."""
        print("Resuming Prance protocol...")
        self._status = "resuming"
        await self.load_state()
        self._status = "running"

    async def run_cycle(self) -> None:
        """Run one cycle of the protocol."""
        print(f"Running cycle {self.cycle_n}")
        # Implementation here
        pass

    def _check_parameters(self, parameters: Dict[str, Any]) -> None:
        """Check protocol parameters."""
        for param_name, param_type in needed_parameters.items():
            if param_name not in parameters:
                raise ValueError(f"Missing required parameter: {param_name}")
            if not isinstance(parameters[param_name], param_type):
                raise TypeError(
                    f"Parameter {param_name} must be of type {param_type}, "
                    f"got {type(parameters[param_name])}"
                )

    def _check_deck_resources(
        self, needed_deck_resources: Dict[str | int, Dict[str, type]]
    ) -> None:
        """Check deck resources."""
        if not self.deck:
            raise ValueError("Deck is not initialized")

        for resource_name, resource_info in needed_deck_resources.items():
            if not hasattr(self.deck, str(resource_name)):
                raise ValueError(f"Missing required deck resource: {resource_name}")
            resource = getattr(self.deck, str(resource_name))
            if not isinstance(resource, resource_info["type"]):
                raise TypeError(
                    f"Resource {resource_name} must be of type {resource_info['type']}, "
                    f"got {type(resource)}"
                )

    async def _save_state(self) -> None:
        """Save the protocol state."""
        print("Saving protocol state...")
        state = {
            "cycle_n": self.cycle_n,
            "cycle_start_time": self.cycle_start_time,
            "reader_plate_stack_in_use": self.reader_plate_stack_in_use,
            "status": self._status,
        }
        self.state[self.name].update(state)
        print("Protocol state saved.")

    async def _load_state(self) -> None:
        """Load the protocol state."""
        print("Loading protocol state...")
        state = self.state[self.name]
        self.cycle_n = state.get("cycle_n", 0)
        self.cycle_start_time = state.get("cycle_start_time", dt.now())
        self.reader_plate_stack_in_use = state.get("reader_plate_stack_in_use")
        self._status = state.get("status", "initializing")
        print("Protocol state loaded.")

    async def _intervene(self, user_input: str) -> None:
        """Handle user intervention.

        Args:
            user_input: The command from the user
        """
        print(f"Handling user intervention: {user_input}")
        if user_input == "add_phage":
            print("Adding phage to control wells...")
            # Implementation for adding phage
            pass
        else:
            print(f"Unknown command: {user_input}")
            await super()._intervene(user_input)

    async def _stop(self) -> None:
        """Stop the protocol."""
        print("Stopping Prance protocol...")
        self._status = "stopping"
        # Cleanup implementation here
        self._status = "stopped"
        print("Prance protocol stopped.")

    async def _abort(self) -> None:
        """Abort the protocol."""
        print("Aborting Prance protocol...")
        self._status = "aborting"
        # Abort implementation here
        self._status = "aborted"
        print("Prance protocol aborted.")
