from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.resources.deck import Deck
from typing import Optional, Any, Literal, cast, Self, Set, Dict
from .protocol import WorkcellAssets

import asyncio
import json
import asyncio

from pylabrobot.utils.object_parsing import find_subclass
from pylabrobot.machines.machine import Machine
from pylabrobot.resources.resource import Resource
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.resources import Deck
from pylabrobot.pumps import Pump, PumpArray
from pylabrobot.plate_reading import PlateReader
from pylabrobot.heating_shaking import HeaterShaker
from pylabrobot.powder_dispensing import PowderDispenser
from pylabrobot.scales import Scale
from pylabrobot.shaking import Shaker
from pylabrobot.temperature_controlling import TemperatureController
from pylabrobot.serializer import serialize, deserialize

# TODO: make different resource types from inspection of PLR

from ..configure import PraxisConfiguration
from ..utils import DatabaseManager


class Workcell:
    def __init__(
        self,
        config: str | PraxisConfiguration,
        save_file: str,
        user: Optional[str] = None,
        using_machines: Optional[Literal["all"] | list[str]] = None,
        backup_interval: Optional[int] = 60,
        num_backups: Optional[int] = 3,
    ) -> None:
        if isinstance(config, str):
            config = PraxisConfiguration(config)
        if not isinstance(config, PraxisConfiguration):
            raise ValueError("Invalid configuration object.")
        self.config = config
        self.db: Optional[DatabaseManager] = None
        if save_file[-5:] != ".json":
            raise ValueError("Filepath must be a json file ending in .json")
        self.user = user
        self.using_machines = using_machines
        self.refs: dict[str, dict] = {
            "liquid_handlers": {},
            "pumps": {},
            "plate_readers": {},
            "heater_shakers": {},
            "powder_dispensers": {},
            "scales": {},
            "shakers": {},
            "temperature_controllers": {},
            "other_machines": {},
            "labware": {},
        }
        self._loaded_machines: dict[str, Machine] = {}
        self.children: list[Resource | Machine] = []
        self._asset_ids: Optional[list[str]] = None
        self.liquid_handlers = self.refs["liquid_handlers"]
        self.pumps = self.refs["pumps"]
        self.plate_readers = self.refs["plate_readers"]
        self.heater_shakers = self.refs["heater_shakers"]
        self.powder_dispensers = self.refs["powder_dispensers"]
        self.scales = self.refs["scales"]
        self.shakers = self.refs["shakers"]
        self.temperature_controllers = self.refs["temperature_controllers"]
        self.other_machines = self.refs["other_machines"]
        self.labware = self.refs["labware"]
        self.save_file = save_file
        self.backup_interval = backup_interval
        self.num_backups = num_backups
        self.backup_task: Optional[asyncio.Task] = None
        self._in_use_by: Dict[str, str] = {}  # resource_name -> protocol_name
        self._resource_states: Dict[str, Dict[str, Any]] = {}

    @property
    def all_machines(self) -> dict[str, Machine]:
        all_machines = {}
        all_machines.update(self.liquid_handlers)
        all_machines.update(self.pumps)
        all_machines.update(self.plate_readers)
        all_machines.update(self.heater_shakers)
        all_machines.update(self.powder_dispensers)
        all_machines.update(self.scales)
        all_machines.update(self.shakers)
        all_machines.update(self.temperature_controllers)
        all_machines.update(self.other_machines)
        return all_machines

    @property
    def asset_ids(self) -> list[str]:
        self.children = self.get_all_children()
        self._asset_ids = [
            child.name for child in self.children if isinstance(child, Resource)
        ]
        self._asset_ids += [
            id for id, _ in self.all_machines.items() if id not in self._asset_ids
        ]
        return self._asset_ids

    async def setup(self):
        for machine_id, machine in self.all_machines.items():
            await self._load_machine(machine_id=machine_id, machine=machine)
        await self._start_machines()

    async def initialize_dependencies(self) -> None:
        await self.unpack_machines(self.using_machines)

    @classmethod
    async def initialize(
        self,
        configuration: PraxisConfiguration,
        save_file: str,
        user: Optional[str] = None,
        using_machines: Optional[Literal["all"] | list[str]] = None,
        backup_interval: Optional[int] = 60,
        num_backups: Optional[int] = 3,
    ) -> Self:
        workcell = self(
            configuration, save_file, user, using_machines, backup_interval, num_backups
        )
        workcell.db = await DatabaseManager.initialize(
            praxis_dsn=configuration.database["praxis_dsn"],
            keycloak_dsn=configuration.database["keycloak_dsn"],
        )
        await workcell.unpack_machines(using_machines)
        return workcell

    async def stop(self):
        await self._stop_machines()

    def loaded_machines(self) -> dict[str, Machine]:
        return self._loaded_machines

    def __getitem__(self, key) -> list[Any] | dict[str, Any]:
        if key == "machines":
            return self.all_machines
        if key == "liquid_handlers":
            return self.refs["liquid_handlers"]
        if key == "pumps":
            return self.refs["pumps"]
        if key == "plate_readers":
            return self.refs["plate_readers"]
        if key == "heater_shakers":
            return self.refs["heater_shakers"]
        if key == "powder_dispensers":
            return self.refs["powder_dispensers"]
        if key == "scales":
            return self.refs["scales"]
        if key == "shakers":
            return self.refs["shakers"]
        if key == "temperature_controllers":
            return self.refs["temperature_controllers"]
        if key == "other_machines":
            return self.refs["other_machines"]
        if key == "labware":
            return self.refs["labware"]
        return self.refs[key]

    async def unpack_machines(
        self, using: Optional[Literal["all"] | list[str]]
    ) -> None:
        if self.db is None:
            raise ValueError("DatabaseManager not specified.")
        if using is None:
            return
        if using == "all":
            machines = await self.db.get_machines()
        else:
            machines = await self.db.get_machines(using)
        for machine_id, machine in machines.items():
            match machine.__class__:
                case LiquidHandler():
                    self.refs["liquid_handlers"][machine_id] = machine
                case Pump():
                    self.refs["pumps"][machine_id] = machine
                case PumpArray():
                    self.refs["pumps"][machine_id] = machine
                case PlateReader():
                    self.refs["plate_readers"][machine_id] = machine
                case HeaterShaker():
                    self.refs["heater_shakers"][machine_id] = machine
                case PowderDispenser():
                    self.refs["powder_dispensers"][machine_id] = machine
                case Scale():
                    self.refs["scales"][machine_id] = machine
                case Shaker():
                    self.refs["shakers"][machine_id] = machine
                case TemperatureController():
                    self.refs["temperature_controllers"][machine_id] = machine
                case Machine():
                    self.refs["other_machines"][machine_id] = machine
                case _:
                    raise ValueError(f"Machine does not have a valid type.")
        self.children.extend(list(self.all_machines.values()))

    def specify_deck(self, liquid_handler_id: str, deck: Deck) -> None:
        """
        Specify the deck for the liquid handler.
        """
        liquid_handler = cast(
            LiquidHandler, self.refs["liquid_handlers"][liquid_handler_id]
        )
        liquid_handler.deck = cast(Deck, deck)

    async def _load_machine(self, machine_id: str, machine: Machine) -> None:
        """
        Load machine to loaded machines.

        Args:
          machine (Machine): The machine.
        """
        self._loaded_machines[machine_id] = machine

    async def _start_machines(self) -> None:
        """
        Scaffold function. Eventually this should check that the machines in use are started by having
        the start method set a state in the PLR object.
        """
        for machine_id, machine in self._loaded_machines.items():
            await machine.setup()
        while not all(
            machine.setup_finished for machine in self._loaded_machines.values()
        ):
            await asyncio.sleep(1)

    async def _stop_machines(self) -> None:
        """
        Scaffold function. Eventually this should check that the machines in use are stopped by having
        the stop method set a state in the PLR object.
        """
        for machine_id, machine in self._loaded_machines.items():
            await machine.stop()
        while all(machine.setup_finished for machine in self._loaded_machines.values()):
            await asyncio.sleep(1)

    def serialize(self) -> dict:
        """Serialize this."""
        return {
            "config": self.config,
            "save_file": self.save_file,
            "user": self.user,
            "using_machines": self.using_machines,
            "backup_interval": self.backup_interval,
            "num_backups": self.num_backups,
        }

    def get_all_children(self) -> list[Resource | Machine]:
        """Recursively get all children of this resource."""
        children = self.children.copy()
        for child in self.children:
            if isinstance(child, Resource):
                children += child.get_all_children()
            else:
                children.append(child)
        return children

    def save(self, fn: str, indent: Optional[int] = None):
        """Save a resource to a JSON file.

        Args:
          fn: File name. Caution: file will be overwritten.
          indent: Same as `json.dump`'s `indent` argument (for json pretty printing).

        Examples:
          Saving to a json file:

          >>> from pylabrobot.resources.hamilton import STARLetDeck
          >>> deck = STARLetDeck()
          >>> deck.save("my_layout.json")
        """

        serialized = self.serialize()
        with open(fn, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=indent)

    @classmethod
    def deserialize(cls, data: dict) -> Self:
        """Deserialize a resource from a dictionary.

        Args:
          allow_marshal: If `True`, the `marshal` module will be used to deserialize functions. This
            can be a security risk if the data is not trusted. Defaults to `False`.

        Examples:
          Loading a resource from a json file:

          >>> from pylabrobot.resources import Resource
          >>> with open("my_resource.json", "r") as f:
          >>>   content = json.load(f)
          >>> resource = Resource.deserialize(content)
        """

        return cls(**data)

    @classmethod
    def load_from_json_file(cls, json_file: str) -> Self:  # type: ignore
        """Loads resources from a JSON file.

        Args:
          json_file: The path to the JSON file.

        Examples:
          Loading a resource from a json file:

          >>> from pylabrobot.resources import Resource
          >>> resource = Resource.deserialize("my_resource.json")
        """

        with open(json_file, "r", encoding="utf-8") as f:
            content = json.load(f)

        return cls.deserialize(content)

    def serialize_all_state(self) -> dict[str, dict[str, Any]]:
        """Serialize the state of all workcell children.


        Returns:
          A dictionary where the keys are the names of the resources and the values are the serialized
          states of the resources.
        """

        state = {}
        for child in self.children:
            if isinstance(child, Resource):
                state[child.name] = child.serialize_all_state()
        return state

    def load_all_state(self, state: dict[str, dict[str, Any]]) -> None:
        """Load state for this workcell and all children."""
        for child in self.children:
            if isinstance(child, Resource) and child.name in state:
                child.load_state(state[child.name])
                child.load_all_state(state)

    def save_state_to_file(self, fn: str, indent: Optional[int] = None):
        """Save the state of this workcell and all children to a JSON file.

        Args:
          fn: File name. Caution: file will be overwritten.
          indent: Same as `json.dump`'s `indent` argument (for json pretty printing).

        Examples:
          Saving to a json file:

          >>> deck.save_state_to_file("my_state.json")
        """

        serialized = self.serialize_all_state()
        with open(fn, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=indent)

    def load_state_from_file(self, fn: str) -> None:
        """Load the state of this workcell and all children from a JSON file.

        Args:
          fn: The file name to load the state from.

        Examples:
          Loading from a json file:

          >>> deck.load_state_from_file("my_state.json")
        """

        with open(fn, "r", encoding="utf-8") as f:
            content = json.load(f)
        self.load_all_state(content)

    async def continuous_backup(self, interval: int = 60, num_backups: int = 3) -> None:
        """Continuously save the state of the workcell to a file.

        Args:
          interval: The interval in seconds to save the state.
          num_backups: The number of backups to keep.
          backup_file: The file to save the state to.


        """
        self.save_state_to_file(self.save_file[:-5] + "_initial.json")
        backup_num = 0
        while True:
            self.save_state_to_file(self.save_file)
            self.save_state_to_file(self.save_file[:-5] + f"_{backup_num}.json")
            backup_num += 1
            await asyncio.sleep(interval)

    def __contains__(self, item: str) -> bool:
        return item in self.asset_ids

    async def __aenter__(self):
        await self.setup()
        await self._synchronize_resource_states()
        self.backup_task = asyncio.create_task(self.continuous_backup())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        # Ensure all resource states are saved before shutting down
        if self.db is not None:
            for resource_name, state in self._resource_states.items():
                await self.db.update_asset_state(resource_name, state)

        await self.save_state_to_file(self.save_file)
        if self.backup_task is not None:
            self.backup_task.cancel()
        await self.stop()

    async def is_resource_in_use(self, resource_name: str) -> bool:
        """Check if a resource is currently in use by any protocol."""
        if self.db is None:
            return resource_name in self._in_use_by
        # Check database first for resource lock
        is_locked = await self.db.is_resource_locked(resource_name)
        if is_locked:
            return True
        return resource_name in self._in_use_by

    async def mark_resource_in_use(
        self, resource_name: str, protocol_name: str
    ) -> None:
        """Mark a resource as being used by a protocol."""
        if self.db is not None:
            # Try to acquire lock in database
            lock_acquired = await self.db.acquire_lock(
                resource_name, protocol_name, str(id(self))
            )
            if not lock_acquired:
                raise RuntimeError(
                    f"Could not acquire lock for resource {resource_name}"
                )
        self._in_use_by[resource_name] = protocol_name

    async def mark_resource_released(
        self, resource_name: str, protocol_name: str
    ) -> None:
        """Mark a resource as no longer being used by a protocol."""
        if (
            resource_name in self._in_use_by
            and self._in_use_by[resource_name] == protocol_name
        ):
            if self.db is not None:
                await self.db.release_lock(resource_name, protocol_name, str(id(self)))
            del self._in_use_by[resource_name]

    def get_resource_state(self, resource_name: str) -> Dict[str, Any]:
        """Get the current state of a resource."""
        # First check local state cache
        if resource_name in self._resource_states:
            return self._resource_states[resource_name].copy()

        # Then check different resource types
        if resource_name in self.labware:
            state = self.labware[resource_name].get_state()
        elif resource_name in self.all_machines:
            state = self.all_machines[resource_name].get_state()
        else:
            raise KeyError(f"Resource {resource_name} not found")

        # Cache the state
        self._resource_states[resource_name] = state
        return state.copy()

    async def update_resource_state(
        self, resource_name: str, state: Dict[str, Any]
    ) -> None:
        """Update the state of a resource."""
        if self.db is not None:
            # Update state in database first
            await self.db.update_asset_state(resource_name, state)

        # Update local state
        if resource_name not in self._resource_states:
            self._resource_states[resource_name] = {}
        self._resource_states[resource_name].update(state)

        # Update actual resource
        if resource_name in self.labware:
            self.labware[resource_name].update_state(state)
        elif resource_name in self.all_machines:
            self.all_machines[resource_name].update_state(state)
        else:
            raise KeyError(f"Resource {resource_name} not found")

    async def _synchronize_resource_states(self) -> None:
        """Synchronize resource states with database."""
        if self.db is None:
            return

        for resource_name in self.asset_ids:
            db_state = await self.db.get_asset_state(resource_name)
            if db_state:
                await self.update_resource_state(resource_name, db_state)

    def get_resource_users(self, resource_name: str) -> Set[str]:
        """Get all protocols currently using a resource."""
        users = set()
        if resource_name in self._in_use_by:
            users.add(self._in_use_by[resource_name])
        return users

    async def __aenter__(self):
        await self.setup()
        await self._synchronize_resource_states()
        self.backup_task = asyncio.create_task(self.continuous_backup())
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        # Ensure all resource states are saved before shutting down
        if self.db is not None:
            for resource_name, state in self._resource_states.items():
                await self.db.update_asset_state(resource_name, state)

        await self.save_state_to_file(self.save_file)
        if self.backup_task is not None:
            self.backup_task.cancel()
        await self.stop()


class WorkcellView:
    """A protocol's view into a shared workcell, managing resource access."""

    def __init__(
        self,
        parent_workcell: Workcell,
        protocol_name: str,
        required_assets: WorkcellAssets,
    ):
        self.parent = parent_workcell
        self.protocol_name = protocol_name
        self.required_assets = required_assets
        self._active_resources: Set[str] = set()
        self._resource_states: Dict[str, Dict[str, Any]] = {}

    async def __aenter__(self):
        """Acquire access to required resources."""
        # Check resource availability
        unavailable = []
        for asset in self.required_assets:
            if self.parent.is_resource_in_use(asset.name):
                unavailable.append(asset.name)

        if unavailable:
            raise RuntimeError(
                f"Resources currently in use by other protocols: {', '.join(unavailable)}"
            )

        # Mark resources as in use
        for asset in self.required_assets:
            self.parent.mark_resource_in_use(asset.name, self.protocol_name)
            self._active_resources.add(asset.name)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Release acquired resources."""
        for resource in self._active_resources:
            # Sync any state changes back to parent
            if resource in self._resource_states:
                self.parent.update_resource_state(
                    resource, self._resource_states[resource]
                )
            self.parent.mark_resource_released(resource, self.protocol_name)
        self._active_resources.clear()
        self._resource_states.clear()

    def update_resource_state(
        self, resource_name: str, state_update: Dict[str, Any]
    ) -> None:
        """Update the state of a resource."""
        if resource_name not in self._active_resources:
            raise RuntimeError(f"Resource {resource_name} not currently acquired")

        # Track state changes locally until context exit
        if resource_name not in self._resource_states:
            self._resource_states[resource_name] = {}
        self._resource_states[resource_name].update(state_update)

    def get_resource_state(self, resource_name: str) -> Dict[str, Any]:
        """Get the current state of a resource."""
        if resource_name not in self.required_assets:
            raise RuntimeError(
                f"Resource {resource_name} not declared in required assets"
            )

        # Combine parent state with any local changes
        state = self.parent.get_resource_state(resource_name).copy()
        if resource_name in self._resource_states:
            state.update(self._resource_states[resource_name])
        return state

    async def release(self):
        """Explicitly release all resources."""
        if self._active_resources:
            async with self:
                pass  # This will trigger __aexit__ and release resources

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to parent workcell for declared resources."""
        # Only allow access to declared resources
        if name not in self.required_assets and not name.startswith("_"):
            raise AttributeError(
                f"Resource '{name}' not declared in required assets for protocol {self.protocol_name}"
            )
        return getattr(self.parent, name)

    @property
    def active_resources(self) -> Set[str]:
        """Get the set of currently active resources."""
        return self._active_resources.copy()

    def is_resource_active(self, resource_name: str) -> bool:
        """Check if a resource is currently active."""
        return resource_name in self._active_resources
