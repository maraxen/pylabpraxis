import os
from os import PathLike
import tomllib
import json
from typing import Literal, Any, Optional
import warnings

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

import asyncio

class Configuration:
  """
  Base for configuration objects.

  Attributes:
    configuration_file (PathLike): The path to the configuration json file.
    configuration (dict): The  configuration dictionary.
  """
  def __init__(self, configuration_file: PathLike):
    self.supported_extensions = [".json", ".txt", ".toml", ".cfg"]
    if not isinstance(configuration_file, PathLike):
      raise ValueError(f"configuration_file must be a PathLike object, \
                        not {type(configuration_file)}")
    if not os.path.exists(configuration_file):
      raise FileNotFoundError(f"configuration_file {configuration_file} does not exist")
    if os.path.isdir(configuration_file):
      raise IsADirectoryError(f"configuration_file {configuration_file} is a directory")
    self.configuration_file = configuration_file
    self.configuration = self.load_configuration(configuration_file)

  def load_configuration(self, configuration_file: PathLike) -> dict:
    """
    Load the configuration from a file.

    Args:
      configuration_file (PathLike): The path to the configuration file.

    Returns:
      dict: The configuration.
    """
    config_extension = os.path.splitext(configuration_file)[1]
    if config_extension not in self.supported_extensions:
      raise ValueError(f"configuration_file {configuration_file} must be a supported file type. \
                        Supported file types are {self.supported_extensions}")
    match config_extension:
      case ".json":
        return self.load_json(configuration_file)
      case _:
        return self.load_toml(configuration_file)

  def load_json(self, configuration_file: PathLike) -> dict:
    """
    Load the configuration from a json file.

    Args:
      configuration_file (PathLike): The path to the configuration file.

    Returns:
      dict: The configuration.
    """
    with open(configuration_file, "rb") as f:
      config = json.load(f)
      if not isinstance(config, dict):
        raise ValueError(f"configuration_file {configuration_file} must be a dictionary.")
      return config

  def load_toml(self, configuration_file: PathLike) -> dict:
    """
    Load the configuration from a toml file.

    Args:
      configuration_file (PathLike): The path to the configuration file.

    Returns:
      dict: The configuration.
    """
    with open(configuration_file, "rb") as f:
      return tomllib.load(f)

  def __getitem__(self, key):
    return self.configuration[key]

  def __contains__(self, key):
    return key in self.configuration


class LabConfiguration(Configuration):
  """
  Lab configuration denoting specific set-  up for a lab.

  Attributes:
    configuration_file (PathLike): The path to the configuration json file.
    configuration (dict): The  configuration dictionary.
  """
  def __init__(self, configuration_file: PathLike):
    super().__init__(configuration_file)
    self.configuration = self.configuration["lab_configuration"]
    self.resources: list[dict[str, Any]] = self.configuration["resources"]
    self._members: dict[str, dict] = self.configuration["members"]
    self.smtp_server: str = self.configuration["smtp_server"]
    self.smtp_port: int = self.configuration["smtp_port"]
    self.refs: dict[str, list] = {
      "liquid_handlers": [],
      "pumps": [],
      "plate_readers": [],
      "plate_hotels": [],
      "heater_shakers": [],
      "powder_dispensers": [],
      "scales": [],
      "shakers": [],
      "temperature_controllers": [],
      "other_machines": [],
      "labware": []
    }
    self._loaded_machines: list[Machine] = []

  @property
  def liquid_handlers(self) -> list[LiquidHandler]:
    return self["liquid_handlers"] # type: ignore

  @property
  def pumps(self) -> list[Pump]:
    return self["pumps"] # type: ignore

  @property
  def plate_readers(self) -> list[PlateReader]:
    return self["plate_readers"] # type: ignore

  @property
  def plate_hotels(self) -> list[Resource]:
    return self["plate_hotels"] # type: ignore

  @property
  def heater_shakers(self) -> list[HeaterShaker]:
    return self["heater_shakers"] # type: ignore

  @property
  def powder_dispensers(self) -> list[PowderDispenser]:
    return self["powder_dispensers"] # type: ignore

  @property
  def scales(self) -> list[Scale]:
    return self["scales"] # type: ignore

  @property
  def shakers(self) -> list[Shaker]:
    return self["shakers"] # type: ignore

  @property
  def temperature_controllers(self) -> list[TemperatureController]:
    return self["temperature_controllers"] # type: ignore

  @property
  def other_machines(self) -> list[Machine]:
    return self["other_machines"] # type: ignore

  @property
  def labware(self) -> list[Resource]:
    return self["labware"] # type: ignore

  @property
  def machines(self) -> list[Machine]:
    return self.liquid_handlers + self.pumps + self.plate_readers + self.heater_shakers + \
            self.powder_dispensers + self.scales + self.shakers + self.temperature_controllers + \
            self.other_machines

  @property
  def ordered_resources(self) -> list[Resource]:
    return self.liquid_handlers + self.pumps + self.plate_readers + \
            self.plate_hotels + self.heater_shakers + self.powder_dispensers + self.scales + \
            self.shakers + self.temperature_controllers + self.other_machines + self.labware

  @property
  def loaded_machines(self) -> list[Machine]:
    return self._loaded_machines

  @property
  def members(self) -> dict[str, dict]:
    return self._members

  def __getitem__(self, key) -> list[Any] | dict[str, Any]:
    if key == "resources":
      return self.resources
    if key == "members":
      return self.members
    if key == "liquid_handlers":
      return self.refs["liquid_handlers"]
    if key == "pumps":
      return self.refs["pumps"]
    if key == "plate_readers":
      return self.refs["plate_readers"]
    if key == "plate_hotels":
      return self.refs["plate_hotels"]
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

  def _is_machine(self, resource_type: str) -> bool:
    subclass = find_subclass(resource_type, cls=Resource)
    if subclass is None:
      return False
    return issubclass(subclass, Machine)

  def using(self,
            using: Optional[Literal["all"] | list[str]] = None) -> None:
    self.unpack_resources(using=using)

  def specify_deck(self, deck: Deck) -> None:
    """
    Specify the deck for the liquid handler.
    """
    self.specified_deck = True
    self.deck = deck

  def unpack_resources(self, using: Optional[Literal["all"] | list[str]]) -> None:
    """
    Unpacks the resources in the configuration file.
    """
    if using is None:
      return
    for resource in self.resources:
      if not using == "all" and resource["name"] not in using:
        continue
      resource_class = find_subclass(resource["type"], cls=Resource)
      if resource_class is None:
        raise ValueError(f"Resource {resource['name']} does not have a valid type.")
      match resource_class:
        case LiquidHandler():
          self.refs["liquid_handlers"].append(LiquidHandler.deserialize(**resource))
        case Pump():
          self.refs["pumps"].append(Pump.deserialize(**resource))
        case PumpArray():
          self.refs["pumps"].append(PumpArray.deserialize(**resource))
        case PlateReader():
          self.refs["plate_readers"].append(PlateReader.deserialize(**resource))
        #case PlateHotel():
          #self.plate_hotels.append((resource["name"], index))
        case HeaterShaker():
          self.refs["heater_shakers"].append(HeaterShaker.deserialize(**resource))
        case PowderDispenser():
          self.refs["powder_dispensers"].append(PowderDispenser.deserialize(**resource))
        case Scale():
          self.refs["scales"].append(Scale.deserialize(**resource))
        case Shaker():
          self.refs["shakers"].append(Shaker.deserialize(**resource))
        case TemperatureController():
          self.refs["temperature_controllers"].append(TemperatureController.deserialize(**resource))
        case Machine():
          self.refs["other_machines"].append(Machine.deserialize(**resource))
        case _:
          self.refs["labware"].append(Resource.deserialize(**resource))

  async def _get_by_resource_type(self, name: str,
                                  resource_type: Literal["resources",
                                                        "liquid_handlers",
                                                        "pumps",
                                                        "plate_readers",
                                                        "heater_shakers",
                                                        "powder_dispensers",
                                                        "scales",
                                                        "shakers",
                                                        "temperature_controllers",
                                                        "other_machines",
                                                        "labware"] = "resources") -> Resource:
    """
    Get a resource by resource_type.

    Args:
      resource_type (str): The resource_type of resource.

    Returns:
      list[Resource]: The resources of the given resource_type.
    """
    for resource in self[resource_type]:
      if isinstance(resource, Resource) and resource.name == name:
        return resource
    raise ValueError(f"{resource_type.capitalize().replace('_', ' ')[:-1]} {name} not found.")

  async def get_resource(self, name: str) -> Resource:
    """
    Get a resource by name.

    Args:
      name (str): The name of the resource.

    Returns:
      Resource: The resource.
    """
    return await self._get_by_resource_type(name=name)

  async def get_liquid_handler(self, name: str) -> LiquidHandler:
    """
    Get a liquid handler by name.

    Args:
      name (str): The name of the liquid handler.

    Returns:
      LiquidHandler: The liquid handler.
    """
    resource = await self._get_by_resource_type(resource_type="liquid_handlers", name=name)
    if isinstance(resource, LiquidHandler):
      return resource
    raise ValueError(f"Liquid handler {name} not found.")

  async def get_pump(self, name: str) -> Pump | PumpArray:
    """
    Get a pump by name.

    Args:
      name (str): The name of the pump.

    Returns:
      Pump | PumpArray: The pump.
    """
    resource = await self._get_by_resource_type(resource_type="pumps", name=name)
    if isinstance(resource, (Pump, PumpArray)):
      return resource
    raise ValueError(f"Pump {name} not found.")

  async def get_plate_reader(self, name: str) -> PlateReader:
    """
    Get a plate reader by name.

    Args:
      name (str): The name of the plate reader.

    Returns:
      PlateReader: The plate reader.
    """
    resource = await self._get_by_resource_type(resource_type="plate_readers", name=name)
    if isinstance(resource, PlateReader):
      return resource
    raise ValueError(f"Plate reader {name} not found.")

  async def get_heater_shaker(self, name: str) -> HeaterShaker:
    """
    Get a heater shaker by name.

    Args:
      name (str): The name of the heater shaker.

    Returns:
      HeaterShaker: The heater shaker.
    """
    resource = await self._get_by_resource_type(resource_type="heater_shakers", name=name)
    if isinstance(resource, HeaterShaker):
      return resource
    raise ValueError(f"Heater shaker {name} not found.")

  async def get_powder_dispenser(self, name: str) -> PowderDispenser:
    """
    Get a powder dispenser by name.

    Args:
      name (str): The name of the powder dispenser.

    Returns:
      PowderDispenser: The powder dispenser.
    """
    resource = await self._get_by_resource_type(resource_type="powder_dispensers", name=name)
    if isinstance(resource, PowderDispenser):
      return resource
    raise ValueError(f"Powder dispenser {name} not found.")

  async def get_scale(self, name: str) -> Scale:
    """
    Get a scale by name.

    Args:
      name (str): The name of the scale.

    Returns:
      Scale: The scale.
    """
    resource = await self._get_by_resource_type(resource_type="scales", name=name)
    if isinstance(resource, Scale):
      return resource
    raise ValueError(f"Scale {name} not found.")

  async def get_shaker(self, name: str) -> Shaker:
    """
    Get a shaker by name.

    Args:
      name (str): The name of the shaker.

    Returns:
      Shaker: The shaker.
    """
    resource = await self._get_by_resource_type(resource_type="shakers", name=name)
    if isinstance(resource, Shaker):
      return resource
    raise ValueError(f"Shaker {name} not found.")

  async def get_temperature_controller(self, name: str) -> TemperatureController:
    """
    Get a temperature controller by name.

    Args:
      name (str): The name of the temperature controller.

    Returns:
      TemperatureController: The temperature controller.
    """
    resource = await self._get_by_resource_type(resource_type="temperature_controllers", name=name)
    if isinstance(resource, TemperatureController):
      return resource
    raise ValueError(f"Temperature controller {name} not found.")

  async def get_other_machine(self, name: str) -> Machine:
    """
    Get an other machine by name.

    Args:
      name (str): The name of the other machine.

    Returns:
      Machine: The other machine.
    """
    resource = await self._get_by_resource_type(resource_type="other_machines", name=name)
    if isinstance(resource, Machine):
      return resource
    raise ValueError(f"Machine {name} not found.")

  async def get_labware(self, name: str) -> Resource:
    """
    Get a labware by name.

    Args:
      name (str): The name of the labware.

    Returns:
      Labware: The labware.
    """
    return await self._get_by_resource_type(resource_type="labware", name=name)

  async def get_member_info(self, name: str) -> dict:
    """
    Get member information by name.

    Args:
      name (str): The name of the member.

    Returns:
      dict: The member information.
    """
    for member_name, member_info in self.members.items():
      if member_name == name:
        return member_info
    raise ValueError(f"Member {name} not found.")


  async def select_resource_of_type(self,
                                    selection: list[str],
                                    resource_type: Literal["resources",
                                                        "liquid_handlers",
                                                        "pumps",
                                                        "plate_readers",
                                                        "heater_shakers",
                                                        "powder_dispensers",
                                                        "scales",
                                                        "shakers",
                                                        "temperature_controllers",
                                                        "other_machines",
                                                        "labware"] = "resources") -> list[Resource]:
    """
    Select resources by name.

    Args:
      resource_type (str): The resource_type of the resources.
      selection (list[str]): The names of the resources.

    Returns:
      list[Resource]: The selected resources.
    """
    return [await self._get_by_resource_type(resource_type=resource_type, name=name) for name in \
            selection]

  async def select_resources(self, selection: list[str]) -> list[Resource]:
    """
    Select resources by name.

    Args:
      selection (list[str]): The names of the resources.

    Returns:
      list[Resource]: The selected resources.
    """
    return [await self.get_resource(name) for name in selection]

  async def select_liquid_handlers(self, selection: list[str]) -> list[LiquidHandler]:
    """
    Select liquid handlers by name.

    Args:
      selection (list[str]): The names of the liquid handlers.

    Returns:
      list[LiquidHandler]: The selected liquid handlers.
    """
    return [await self.get_liquid_handler(name) for name in selection]


  async def select_pumps(self, selection: list[str]) -> list[Pump | PumpArray]:
    """
    Select pumps by name.

    Args:
      selection (list[str]): The names of the pumps.

    Returns:
      list[Pump]: The selected pumps.
    """
    return [await self.get_pump(name) for name in selection]

  async def select_plate_readers(self, selection: list[str]) -> list[PlateReader]:
    """
    Select plate readers by name.

    Args:
      selection (list[str]): The names of the plate readers.

    Returns:
      list[PlateReader]: The selected plate readers.
    """
    return [await self.get_plate_reader(name) for name in selection]

  async def select_heater_shakers(self, selection: list[str]) -> list[HeaterShaker]:
    """
    Select heater shakers by name.

    Args:
      selection (list[str]): The names of the heater shakers.

    Returns:
      list[HeaterShaker]: The selected heater shakers.
    """
    return [await self.get_heater_shaker(name) for name in selection]

  async def select_powder_dispensers(self, selection: list[str]) -> list[PowderDispenser]:
    """
    Select powder dispensers by name.

    Args:
      selection (list[str]): The names of the powder dispensers.

    Returns:
      list[PowderDispenser]: The selected powder dispensers.
    """
    return [await self.get_powder_dispenser(name) for name in selection]

  async def select_scales(self, selection: list[str]) -> list[Scale]:
    """
    Select scales by name.

    Args:
      selection (list[str]): The names of the scales.

    Returns:
      list[Scale]: The selected scales.
    """
    return [await self.get_scale(name) for name in selection]

  async def select_shakers(self, selection: list[str]) -> list[Shaker]:
    """
    Select shakers by name.

    Args:
      selection (list[str]): The names of the shakers.

    Returns:
      list[Shaker]: The selected shakers.
    """
    return [await self.get_shaker(name) for name in selection]

  async def select_temperature_controllers(self, selection: list[str]) \
    -> list[TemperatureController]:
    """
    Select temperature controllers by name.

    Args:
      selection (list[str]): The names of the temperature controllers.

    Returns:
      list[TemperatureController]: The selected temperature controllers.
    """
    return [await self.get_temperature_controller(name) for name in selection]

  async def select_other_machines(self, selection: list[str]) -> list[Machine]:
    """
    Select other machines by name.

    Args:
      selection (list[str]): The names of the other machines.

    Returns:
      list[Machine]: The selected other machines.
    """
    return [await self.get_other_machine(name) for name in selection]

  async def select_labware(self, selection: list[str]) -> list[Resource]:
    """
    Select labware by name.

    Args:
      selection (list[str]): The names of the labware.

    Returns:
      list[Labware]: The selected labware.
    """
    return [await self.get_labware(name) for name in selection]

  def has_all_specified_resources(self, resources: list[str]) -> bool:
    """
    Checks that all specified resources are in the lab configuration.
    """
    return all(resource in self.resources for resource in resources)

  async def _load_machine(self, machine: Machine) -> None:
    """
    Load machine to loaded machines.

    Args:
      machine (Machine): The machine.
    """
    self._loaded_machines.append(machine)

  async def save_configuration(self, configuration_file: PathLike) -> None:
    """
    Save the configuration to a file.

    Args:
      configuration_file (PathLike): The path to the configuration file.
    """
    with open(configuration_file, "ws") as f:
      json.dump(self.configuration, f, indent=4)


  async def align_states(self) -> None:
    """
    Scaffold function. Eventually this should check that the machines in use are aligned by having
    the align method set a state in the PLR object.
    """
    for machine in self._loaded_machines:
      if machine == self.liquid_handlers[0]:
        continue
      machine_state = self.liquid_handlers[0].get_resource(machine.name)
      for attr in machine_state.__dict__:
        if getattr(machine, attr) != getattr(machine_state, attr):
          machine.__dict__[attr] = machine_state.__dict__[attr]

  async def _start_machines(self) -> None:
    """
    Scaffold function. Eventually this should check that the machines in use are started by having
    the start method set a state in the PLR object.
    """
    for machine in self._loaded_machines:
      await machine.setup()
    while not all(machine.setup_finished for machine in self._loaded_machines):
      await asyncio.sleep(1)
    self.liquid_handler = self.liquid_handlers[0]

  async def _stop_machines(self) -> None:
    """
    Scaffold function. Eventually this should check that the machines in use are stopped by having
    the stop method set a state in the PLR object.
    """
    for machine in self._loaded_machines:
      await machine.stop()
    while all(machine.setup_finished for machine in self._loaded_machines):
      await asyncio.sleep(1)

  async def __aenter__(self):
    if len(self.liquid_handlers) > 1:
      raise ValueError("Only one liquid handler is supported at a time currently.")
    for liquid_handler in self.liquid_handlers:
      if self.specified_deck:
        liquid_handler.deck = self.deck
      for machine in self.machines:
        if machine.name == liquid_handler.name:
          machine = liquid_handler
          await self._load_machine(machine)
          continue
        for resource in liquid_handler.deck.get_all_resources():
          if machine.name == resource:
            machine = resource if isinstance(resource, Machine) else machine
            await self._load_machine(machine)
    await self._start_machines()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self._stop_machines()

class TaskConfiguration(Configuration):
  """
  Task configuration denoting specific settings for a task.

  Attributes:
    configuration_file (PathLike): The path to the configuration json file.
    configuration (dict): The  configuration dictionary.
  """
  def __init__(self, configuration_file: PathLike):
    super().__init__(configuration_file)
    self.configuration = self.configuration["task_configuration"]

class ExperimentConfiguration(Configuration):
  """
  Experiment configuration denoting specific settings for an experiment.

  Attributes:
    configuration_file (PathLike): The path to the configuration toml or json file.
  """
  def __init__(self,
                configuration_file: PathLike):
    super().__init__(configuration_file)
    self.configuration = self["experiment_configuration"]
    self._liquid_handler: str = self["liquid_handler"]
    if self._liquid_handler not in self["machines"]:
      self["machines"].append(self._liquid_handler)
    self._machines: list[str] = self["machines"]
    self._parameters: dict = self["parameters"]
    self._name: str = self["name"]
    self._details: str = self["details"]
    self._description: str = self["description"]
    self._other_args: dict = self["other_args"]
    self._user: str = self["user"]
    self._directory: str = self["directory"]
    self._deck: str = self["deck"]
    self.deck = Deck.load_from_json_file(self._deck)

  @property
  def liquid_handler(self) -> str:
    return self._liquid_handler

  @property
  def machines(self) -> list[str]:
    return self._machines

  @property
  def name(self) -> str:
    return self._name

  @property
  def details(self) -> str:
    return self._details

  @property
  def description(self) -> str:
    return self._description

  @property
  def parameters(self) -> dict:
    return self._parameters

  @property
  def other_args(self) -> dict:
    return self._other_args

  @property
  def directory(self) -> str:
    return self._directory

  @property
  def data_directory(self) -> str:
    return os.path.join(self._directory, "data")

  @property
  def user(self) -> str:
    return self._user
