import asyncio
import json
from typing import Any, Dict, Literal, Optional, Self, Set, cast, runtime_checkable
from typing import Protocol as TypeProtocol

from pylabrobot.heating_shaking import HeaterShaker
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.machines.machine import Machine
from pylabrobot.plate_reading import PlateReader
from pylabrobot.powder_dispensing import PowderDispenser
from pylabrobot.pumps import Pump, PumpArray
from pylabrobot.resources import Deck
from pylabrobot.resources.resource import Resource
from pylabrobot.scales import Scale
from pylabrobot.shaking import Shaker
from pylabrobot.temperature_controlling import TemperatureController

# TODO: make different asset types from inspection of PLR
from ..configure import PraxisConfiguration
from ..interfaces import WorkcellAssetsInterface, WorkcellInterface
from ..utils import DatabaseManager, db


@runtime_checkable
class StateManaged(TypeProtocol):  # Protocol from the typing library not praxis.
  """Type protocol for objects that support state management."""

  def get_state(self) -> Dict[str, Any]: ...
  def update_state(self, state: Dict[str, Any]) -> None: ...


class Workcell(WorkcellInterface):
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
    self.db: DatabaseManager = db
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
      "resource": {},
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
    self.resource = self.refs["resource"]
    self.save_file = save_file
    self.backup_interval = backup_interval
    self.num_backups = num_backups
    self.backup_task: Optional[asyncio.Task] = None
    self._in_use_by: Dict[str, str] = {}  # asset_name -> protocol_name
    self._asset_states: Dict[str, Dict[str, Any]] = {}

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

  @property
  def asset_states(self) -> dict[str, dict[str, Any]]:
    return self._asset_states.copy()

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
    if key == "resource":
      return self.refs["resource"]
    return self.refs[key]

  async def unpack_machines(self, using: Optional[Literal["all"] | list[str]]) -> None:
    if self.db is None:
      raise ValueError("DatabaseManager not specified.")
    if using is None:
      return
    if using == "all":
      machines = await self.db.get_all_machines()
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
          raise ValueError("Machine does not have a valid type.")
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
    while not all(machine.setup_finished for machine in self._loaded_machines.values()):
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
    """Recursively get all children of this asset."""
    children = self.children.copy()
    for child in self.children:
      if isinstance(child, Resource):
        children += child.get_all_children()
      else:
        children.append(child)
    return children

  def save(self, fn: str, indent: Optional[int] = None):
    """Save a asset to a JSON file.

    Args:
      fn: File name. Caution: file will be overwritten.
      indent: Same as `json.dump`'s `indent` argument (for json pretty printing).

    Examples:
      Saving to a json file:

      >>> from pylabrobot.assets.hamilton import STARLetDeck
      >>> deck = STARLetDeck()
      >>> deck.save("my_layout.json")
    """

    serialized = self.serialize()
    with open(fn, "w", encoding="utf-8") as f:
      json.dump(serialized, f, indent=indent)

  @classmethod
  def deserialize(cls, data: dict) -> Self:
    """Deserialize a asset from a dictionary.

    Args:
      allow_marshal: If `True`, the `marshal` module will be used to deserialize functions. This
        can be a security risk if the data is not trusted. Defaults to `False`.

    Examples:
      Loading a asset from a json file:

      >>> from pylabrobot.assets import Resource
      >>> with open("my_asset.json", "r") as f:
      >>>   content = json.load(f)
      >>> asset = Resource.deserialize(content)
    """

    return cls(**data)

  @classmethod
  def load_from_json_file(cls, json_file: str) -> Self:  # type: ignore
    """Loads assets from a JSON file.

    Args:
      json_file: The path to the JSON file.

    Examples:
      Loading a asset from a json file:

      >>> from pylabrobot.assets import Resource
      >>> asset = Resource.deserialize("my_asset.json")
    """

    with open(json_file, "r", encoding="utf-8") as f:
      content = json.load(f)

    return cls.deserialize(content)

  def serialize_all_state(self) -> dict[str, dict[str, Any]]:
    """Serialize the state of all workcell children.


    Returns:
      A dictionary where the keys are the names of the assets and the values are the serialized
      states of the assets.
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

  async def load_state_from_file(self, fn: str) -> None:
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
    await self._synchronize_asset_states()
    self.backup_task = asyncio.create_task(self.continuous_backup())
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    # Ensure all asset states are saved before shutting down
    if self.db is not None:
      for asset_name, state in self._asset_states.items():
        await self.db.update_asset_state(asset_name, state)

    await self.save_state_to_file(self.save_file)
    if self.backup_task is not None:
      self.backup_task.cancel()
    await self.stop()

  async def is_asset_in_use(self, asset_name: str) -> bool:
    """Check if a asset is currently in use by any protocol."""
    if self.db is None:
      return asset_name in self._in_use_by
    # Check database first for asset lock
    is_locked = await self.db.is_asset_locked(asset_name)
    if is_locked:
      return True
    return asset_name in self._in_use_by

  async def validate_asset_requirements(self, assets: dict) -> None:
    """Validate all asset requirements including deck layout."""
    if not hasattr(self, "deck"):
      return

    for asset_name, asset_spec in assets.items():
      if not await self.validate_asset_placement(asset_name, asset_spec):
        raise ValueError(f"Asset placement validation failed for {asset_name}")

  async def validate_asset_placement(self, asset_name: str, asset_spec: dict) -> bool:
    """Validate if an asset can be placed according to its specifications."""
    if not hasattr(self, "deck"):
      return True

    # Check carrier compatibility if specified
    if "carrier_compatibility" in asset_spec:
      if not await self._check_carrier_compatibility(asset_spec):
        return False

    # Check stackable flag and slot requirements
    if not asset_spec.get("stackable", False):
      if not await self._check_single_slot_available(asset_spec):
        return False

    return True

  async def _check_carrier_compatibility(self, asset_spec: dict) -> bool:
    """Check if compatible carriers are available with enough slots."""
    required_slots = asset_spec.get("min_slots", 1)
    compatible_carriers = asset_spec.get("carrier_compatibility", [])

    for carrier_type in compatible_carriers:
      carriers = [
        r for r in self.deck.get_all_children() if r.__class__.__name__ == carrier_type
      ]

      for carrier in carriers:
        available_slots = len(
          [
            s
            for s in carrier.get_all_children()
            if not s.has_children()  # Empty slot
          ]
        )
        if available_slots >= required_slots:
          return True
    return False

  async def _check_single_slot_available(self, asset_spec: dict) -> bool:
    """Check if at least one slot is available for non-stackable assets."""
    # Check deck position if specified
    if "deck_position" in asset_spec:
      position = asset_spec["deck_position"]
      if not self.deck.is_position_available(position):
        return False

    # Count available slots
    available_slots = len(
      [
        r
        for r in self.deck.get_all_children()
        if not r.has_children()  # Empty slot
      ]
    )
    return available_slots > 0

  async def mark_asset_in_use(self, asset_name: str, protocol_name: str) -> None:
    """Mark a asset as being used by a protocol."""
    if self.db is not None:
      try:
        lock_acquired = await self.db.acquire_lock(
          asset_name, protocol_name, str(id(self))
        )
        if not lock_acquired:
          raise RuntimeError(f"Could not acquire lock for asset {asset_name}")
      except Exception as e:
        raise RuntimeError(f"Failed to acquire lock: {str(e)}")
    self._in_use_by[asset_name] = protocol_name

  async def mark_asset_released(self, asset_name: str, protocol_name: str) -> None:
    """Mark a asset as no longer being used by a protocol."""
    if asset_name in self._in_use_by and self._in_use_by[asset_name] == protocol_name:
      if self.db is not None:
        await self.db.release_lock(asset_name, protocol_name, str(id(self)))
      del self._in_use_by[asset_name]

  async def get_asset_state(self, asset_name: str) -> Dict[str, Any]:
    """Get the current state of a asset."""
    if asset_name in self._asset_states:
      return self._asset_states[asset_name].copy()

    asset = None
    if asset_name in self.resource:
      asset = self.resource[asset_name]
    elif asset_name in self.all_machines:
      asset = self.all_machines[asset_name]
    else:
      raise KeyError(f"Asset {asset_name} not found")

    if isinstance(asset, StateManaged):
      state = asset.get_state()
      self._asset_states[asset_name] = state
      return state.copy()
    return {}

  async def update_asset_state(self, asset_name: str, state: Dict[str, Any]) -> None:
    """Update the state of a asset."""
    try:
      if self.db is not None:
        await self.db.update_asset_state(asset_name, state)

      if asset_name not in self._asset_states:
        self._asset_states[asset_name] = {}
      self._asset_states[asset_name].update(state)

      asset = None
      if asset_name in self.resource:
        asset = self.resource[asset_name]
      elif asset_name in self.all_machines:
        asset = self.all_machines[asset_name]

      if asset is not None and isinstance(asset, StateManaged):
        asset.update_state(state)
    except Exception as e:
      raise RuntimeError(f"Failed to update asset state: {str(e)}")

  async def _synchronize_asset_states(self) -> None:
    """Synchronize asset states with database."""
    if self.db is None:
      return

    for asset_name in self.asset_ids:
      db_state = await self.db.get_asset_state(asset_name)
      if db_state:
        await self.update_asset_state(asset_name, db_state)

  def get_asset_users(self, asset_name: str) -> Set[str]:
    """Get all protocols currently using a asset."""
    users = set()
    if asset_name in self._in_use_by:
      users.add(self._in_use_by[asset_name])
    return users

  async def get_state(self) -> Dict[str, Any]:
    """Get the current state of all assets."""
    return self._asset_states.copy()

  async def update_state(self, state: Dict[str, Any]) -> None:
    """Update the current state."""
    self._asset_states.update(state)


class WorkcellView(
  WorkcellInterface
):  # TODO: long term we want to be able to more granularly check for subprotocols
  """A protocol's view into a shared workcell, managing asset access."""

  def __init__(
    self,
    parent_workcell: WorkcellInterface,
    protocol_name: str,
    required_assets: WorkcellAssetsInterface,
  ):
    self.parent = parent_workcell
    self.protocol_name = protocol_name
    self.required_assets = required_assets
    self._active_assets: Set[str] = set()
    self._asset_states: Dict[str, Dict[str, Any]] = {}

  def __contains__(self, asset_name: str) -> bool:
    """Check if a asset is declared in required assets."""
    return asset_name in self.required_assets

  async def __aenter__(self):
    """Acquire access to required assets."""
    # Check asset availability
    unavailable = []
    for asset in self.required_assets:
      if self.parent.is_asset_in_use(asset.name):
        unavailable.append(asset.name)

    if unavailable:
      raise RuntimeError(
        f"Resources currently in use by other protocols: {', '.join(unavailable)}"
      )

    # Mark assets as in use
    for asset in self.required_assets:
      await self.parent.mark_asset_in_use(asset.name, self.protocol_name)
      self._active_assets.add(asset.name)

    return self

  async def __aexit__(self, exc_type, exc_val, exc_tb):
    """Release acquired assets."""
    for asset in self._active_assets:
      # Sync any state changes back to parent
      if asset in self._asset_states:
        await self.parent.update_asset_state(asset, self._asset_states[asset])
      await self.parent.mark_asset_released(asset, self.protocol_name)
    self._active_assets.clear()
    self._asset_states.clear()

  async def update_asset_state(
    self, asset_name: str, state_update: Dict[str, Any]
  ) -> None:
    """Update the state of a asset."""
    if asset_name not in self._active_assets:
      raise RuntimeError(f"Resource {asset_name} not currently acquired")

    # Track state changes locally until context exit
    if asset_name not in self._asset_states:
      self._asset_states[asset_name] = {}
    self._asset_states[asset_name].update(state_update)

  async def get_asset_state(self, asset_name: str) -> Dict[str, Any]:
    """Get the current state of a asset."""
    if asset_name not in self.required_assets:
      raise RuntimeError(f"Resource {asset_name} not declared in required assets")

    # Combine parent state with any local changes
    state = await self.parent.get_asset_state(asset_name)
    state = state.copy()
    if asset_name in self._asset_states:
      state.update(self._asset_states[asset_name])
    return state

  async def release(self):
    """Explicitly release all assets."""
    if self._active_assets:
      async with self:
        pass  # This will trigger __aexit__ and release assets

  def __getattr__(self, name: str) -> Any:
    """Delegate attribute access to parent workcell for declared assets."""
    # Only allow access to declared assets
    if name not in self.required_assets and not name.startswith("_"):
      raise AttributeError(
        f"Resource '{name}' not declared in required assets for protocol {self.protocol_name}"
      )
    return getattr(self.parent, name)

  @property
  def active_assets(self) -> Set[str]:
    """Get the set of currently active assets."""
    return self._active_assets.copy()

  @property
  def asset_states(self) -> Dict[str, Dict[str, Any]]:
    """Get the current state of all assets."""
    return self._asset_states.copy()

  def is_asset_active(self, asset_name: str) -> bool:
    """Check if a asset is currently active."""
    return asset_name in self._active_assets

  async def get_state(self) -> Dict[str, Any]:
    """Get state from parent."""
    return await self.parent.get_state()

  async def update_state(self, state: Dict[str, Any]) -> None:
    """Update state in parent."""
    await self.parent.update_state(state)

  async def is_asset_in_use(self, asset_name: str) -> bool:
    """Check if asset is in use."""
    return await self.parent.is_asset_in_use(asset_name)

  async def save_state_to_file(self, filepath: str) -> None:
    """Save state to file."""
    await self.parent.save_state_to_file(filepath)

  async def load_state_from_file(self, filepath: str) -> None:
    """Load state from file."""
    await self.parent.load_state_from_file(filepath)

  async def mark_asset_in_use(self, asset_name: str, protocol_name: str) -> None:
    """Mark asset in use."""
    await self.parent.mark_asset_in_use(asset_name, protocol_name)

  async def mark_asset_released(self, asset_name: str, protocol_name: str) -> None:
    """Mark asset released."""
    await self.parent.mark_asset_released(asset_name, protocol_name)
