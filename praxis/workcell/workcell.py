from praxis.configure import LabConfiguration, ExperimentConfiguration
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.resources.deck import Deck
from typing import Optional, Any, Literal, cast, Self, Callable

import asyncio
import json

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

from praxis.configure import PraxisConfiguration
from praxis.utils import Registry, AsyncAssetDatabase

class Workcell:
  def __init__(self,
              configuration: PraxisConfiguration,
              user: Optional[str] = None,
              using_machines: Optional[Literal["all"] | list[str | int]] = None,
              using_resources: Optional[Literal["all"] | list[str | int]] = None) -> None:
      self.configuration = configuration
      self.registry = Registry(configuration)
      self.asset_database = AsyncAssetDatabase(configuration.asset_dir)
      self.user = user
      self.using_machines = using_machines
      self.using_resources = using_resources
      self.refs: dict[str, list] = {
      "liquid_handlers": [],
      "pumps": [],
      "plate_readers": [],
      "heater_shakers": [],
      "powder_dispensers": [],
      "scales": [],
      "shakers": [],
      "temperature_controllers": [],
      "other_machines": [],
      "labware": []
      }
      self._loaded_machines: list[Machine] = []
      self.children: list[Resource | Machine] = []
      self._assets = []
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

  @property
  def all_machines(self) -> list[Machine]:
    return self.liquid_handlers + self.pumps + self.plate_readers + self.heater_shakers + \
            self.powder_dispensers + self.scales + self.shakers + self.temperature_controllers + \
            self.other_machines

  async def setup(self):
    for machine in self.all_machines:
      await self._load_machine(machine)
    await self._start_machines()

  async def initialize_dependencies(self,
                                    using_machines: Optional[Literal["all"] | list[str | int]] = None,
                                    using_resources: Optional[Literal["all"] | list[str | int]] = None) -> None:
    await self.unpack_machines(using_machines)
    await self.unpack_resources(using_resources)

  @classmethod
  async def initialize(self, configuration: PraxisConfiguration, user: Optional[str] = None,
                        using_machines: Optional[Literal["all"] | list[str | int]] = None,
                        using_resources: Optional[Literal["all"] | list[str | int]] = None) -> Self:
    workcell = Workcell(configuration, user, using_machines)
    await workcell.unpack_machines(using_machines)
    await workcell.unpack_resources(using_resources)
    return workcell

  async def stop(self):
    await self._stop_machines()

  def loaded_machines(self) -> list[Machine]:
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

  async def unpack_machines(self, using: Optional[Literal["all"] | list[str | int]]) -> None:
    if using is None:
      return
    if using == "all":
      machines = await self.asset_database.get_all_machines()
    else:
      machines = await self.asset_database.get_machines(using)
    for machine in machines:
      match machine.__class__:
        case LiquidHandler():
          self.refs["liquid_handlers"].append(machine)
        case Pump():
          self.refs["pumps"].append(machine)
        case PumpArray():
          self.refs["pumps"].append(machine)
        case PlateReader():
          self.refs["plate_readers"].append(machine)
        case HeaterShaker():
          self.refs["heater_shakers"].append(machine)
        case PowderDispenser():
          self.refs["powder_dispensers"].append(machine)
        case Scale():
          self.refs["scales"].append(machine)
        case Shaker():
          self.refs["shakers"].append(machine)
        case TemperatureController():
          self.refs["temperature_controllers"].append(machine)
        case Machine():
          self.refs["other_machines"].append(machine)
        case _:
          raise ValueError(f"Machine does not have a valid type.")
    self.children.extend(self.all_machines)

  def specify_deck(self, liquid_handler: LiquidHandler, deck: Deck) -> None:
    """
    Specify the deck for the liquid handler.
    """
    liquid_handler.deck = deck

  async def unpack_resources(self, using: Optional[Literal["all"] | list[str]]) -> None:
    """
    Unpacks the resources in the configuration file.
    """
    if using is None:
      return
    elif using == "all":
      self.refs["labware"].extend(await self.asset_database.get_all_resources())
    else:
      self.refs["labware"].append(await self.asset_database.get_resources(using))
    self.children.extend(self.refs["labware"])

  async def _load_machine(self, machine: Machine) -> None:
    """
    Load machine to loaded machines.

    Args:
      machine (Machine): The machine.
    """
    self._loaded_machines.append(machine)

  async def _start_machines(self) -> None:
    """
    Scaffold function. Eventually this should check that the machines in use are started by having
    the start method set a state in the PLR object.
    """
    for machine in self._loaded_machines:
      await machine.setup()
    while not all(machine.setup_finished for machine in self._loaded_machines):
      await asyncio.sleep(1)

  async def _stop_machines(self) -> None:
    """
    Scaffold function. Eventually this should check that the machines in use are stopped by having
    the stop method set a state in the PLR object.
    """
    for machine in self._loaded_machines:
      await machine.stop()
    while all(machine.setup_finished for machine in self._loaded_machines):
      await asyncio.sleep(1)

  def serialize(self) -> dict:
    """Serialize this."""
    return {
      "configuration": self.configuration,
      "user": self.user,
      "using_machines": self.using_machines
    }

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

  async def __aenter__(self):
    await self.setup()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.stop()
