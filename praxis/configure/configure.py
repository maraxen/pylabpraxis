import os
from os import PathLike
import tomllib
import json
from typing import Literal, Any, Optional, cast
import warnings
import asyncio

from praxis.protocol.parameter import Parameter, ProtocolParameters

# TODO: add arms
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

from praxis.commons.overrides import patch_subclasses

overrides = patch_subclasses()

for cls_name, override in overrides.items():
  globals()[cls_name] = override


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
    if "lab_configuration" not in self.configuration:
      raise ValueError("Configuration file must have a lab_configuration key. Structure must be \
                        {\"lab_configuration\": {\"resources\": [], \"members\": {}, ...}}")
    self.configuration: dict[str, Any] = self.configuration["lab_configuration"]
    self.resources: list[dict[str, Any]] = self.configuration["resources"]
    self.machines: list[dict[str, Any]] = self.configuration["machines"]
    self.members: dict[str, dict] = self.configuration["members"]
    self.smtp_server: str = self.configuration["smtp_server"]
    self.smtp_port: int = self.configuration["smtp_port"]

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
                                                        "labware"] = "resources") \
                                                          -> Resource | Machine:
    """
    Get a resource by resource_type.

    Args:
      resource_type (str): The resource_type of resource.

    Returns:
      list[Resource]: The resources of the given resource_type.
    """
    for resource in self[resource_type]:
      if isinstance(resource, Resource | Machine) and getattr(resource, "name") == name:
        return resource
    raise ValueError(f"{resource_type.capitalize().replace('_', ' ')[:-1]} {name} not found.")

  async def get_resource(self, name: str) -> Resource | Machine:
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

  async def get_labware(self, name: str) -> Resource | Machine:
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
                                                        "labware"] = "resources") \
                                                          -> list[Resource | Machine]:
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

  async def select_resources(self, selection: list[str]) -> list[Resource | Machine]:
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

  async def select_labware(self, selection: list[str]) -> list[Resource | Machine]:
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

  async def save_configuration(self, configuration_file: PathLike) -> None:
    """
    Save the configuration to a file.

    Args:
      configuration_file (PathLike): The path to the configuration file.
    """
    with open(configuration_file, "ws") as f:
      json.dump(self.configuration, f, indent=4)

class ProtocolConfiguration(Configuration):
  """
  Protocol configuration denoting specific settings for a method.

  Attributes:
    configuration_file (PathLike): The path to the configuration toml or json file.
  """
  def __init__(self,
                configuration_file: PathLike):
    super().__init__(configuration_file)
    self.configuration = self["method_configuration"]
    self.machines: list[str | int] = cast(list, self["machines"])
    self.liquid_handler_ids = cast(list[str | int], self["liquid_handler_ids"])
    self._name: str = cast(str, self["name"])
    self._details: str = cast(str, self["details"])
    self._description: str = cast(str, self["description"])
    self._other_args: dict = cast(dict, self["other_args"])
    self._user: str = cast(str, self["user"])
    self._directory: str = self["directory"]
    self._deck: str = self["deck"]
    self._parameters: ProtocolParameters = ProtocolParameters(self["parameters"])
    self.deck = DeckManager(self._deck)

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
  def parameters(self) -> ProtocolParameters:
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
