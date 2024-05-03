import os
from os import PathLike
import json
from typing import Union
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
import importlib
import sys

from praxis.experiment.experiment import Experiment


class Configuration:
  """
  Base for configuration objects.

  Attributes:
    configuration_file (PathLike): The path to the configuration json file.
    configuration (dict): The  configuration dictionary.
  """
  def __init__(self, configuration_file: PathLike):
    self.configuration_file = configuration_file
    if not isinstance(configuration_file, PathLike):
      raise ValueError(f"configuration_file must be a PathLike object, \
                        not {type(configuration_file)}")
    if not configuration_file.exists():
      raise FileNotFoundError(f"configuration_file {configuration_file} does not exist")
    if configuration_file.is_dir():
      raise IsADirectoryError(f"configuration_file {configuration_file} is a directory")
    if configuration_file.suffix != ".json":
      raise ValueError(f"configuration_file {configuration_file} must be a .json file")
    self.configuration_file = configuration_file
    with open(self.configuration_file, "rb") as f:
      self.configuration = json.load(f)

  def __getitem__(self, key):
    return self.configuration[key]


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
    self.resources = self.configuration["resources"]
    self.refs = {
      "liquid_handlers": [],
      "decks": [],
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
    self._loaded_machines = []
    self.unpack_resources()

  @property
  def liquid_handlers(self):
    return self["liquid_handlers"]

  @property
  def decks(self):
    return self["decks"]

  @property
  def pumps(self):
    return self["pumps"]

  @property
  def plate_readers(self):
    return self["plate_readers"]

  @property
  def plate_hotels(self):
    return self["plate_hotels"]

  @property
  def heater_shakers(self):
    return self["heater_shakers"]

  @property
  def powder_dispensers(self):
    return self["powder_dispensers"]

  @property
  def scales(self):
    return self["scales"]

  @property
  def shakers(self):
    return self["shakers"]

  @property
  def temperature_controllers(self):
    return self["temperature_controllers"]

  @property
  def other_machines(self):
    return self["other_machines"]

  @property
  def labware(self):
    return self["labware"]

  @property
  def machines(self):
    return self.liquid_handlers + self.pumps + self.plate_readers + self.heater_shakers + \
            self.powder_dispensers + self.scales + self.shakers + self.temperature_controllers + \
            self.other_machines

  @property
  def ordered_resources(self):
    return self.liquid_handlers + self.decks + self.pumps + self.plate_readers + \
            self.plate_hotels + self.heater_shakers + self.powder_dispensers + self.scales + \
            self.shakers + self.temperature_controllers + self.other_machines + self.labware

  @property
  def liquid_handlers_to_use(self):
    return [resource for resource in self.liquid_handlers if resource["to_use"]]

  @property
  def decks_to_use(self):
    return [resource for resource in self.decks if resource["to_use"]]

  @property
  def pumps_to_use(self):
    return [resource for resource in self.pumps if resource["to_use"]]

  @property
  def plate_readers_to_use(self):
    return [resource for resource in self.plate_readers if resource["to_use"]]

  @property
  def plate_hotels_to_use(self):
    return [resource for resource in self.plate_hotels if resource["to_use"]]

  @property
  def heater_shakers_to_use(self):
    return [resource for resource in self.heater_shakers if resource["to_use"]]

  @property
  def powder_dispensers_to_use(self):
    return [resource for resource in self.powder_dispensers if resource["to_use"]]

  @property
  def scales_to_use(self):
    return [resource for resource in self.scales if resource["to_use"]]

  @property
  def shakers_to_use(self):
    return [resource for resource in self.shakers if resource["to_use"]]

  @property
  def temperature_controllers_to_use(self):
    return [resource for resource in self.temperature_controllers if resource["to_use"]]

  @property
  def other_machines_to_use(self):
    return [resource for resource in self.other_machines if resource["to_use"]]

  @property
  def labware_to_use(self):
    return [resource for resource in self.labware if resource["to_use"]]

  @property
  def machines_to_use(self):
    return self.liquid_handlers_to_use + self.pumps_to_use + self.plate_readers_to_use + \
            self.heater_shakers_to_use + self.powder_dispensers_to_use + self.scales_to_use + \
            self.shakers_to_use + self.temperature_controllers_to_use + self.other_machines_to_use

  @property
  def ordered_resources_to_use(self):
    return self.liquid_handlers_to_use + self.decks_to_use + self.pumps_to_use + \
            self.plate_readers_to_use + self.plate_hotels_to_use + self.heater_shakers_to_use + \
            self.powder_dispensers_to_use + self.scales_to_use + self.shakers_to_use + \
            self.temperature_controllers_to_use + self.other_machines_to_use + \
            self.labware_to_use

  @property
  def loaded_machines(self):
    return self._loaded_machines

  def __getitem__(self, key):
    if key == "resources":
      return self.resources
    return self.refs[key][0]

  def _is_machine(self, resource_type: str):
    return issubclass(find_subclass(resource_type, cls=Resource), Machine)

  def unpack_resources(self):
    """
    Unpacks the resources in the configuration file.
    """
    for index,resource in enumerate(self.resources):
      resource_class = find_subclass(resource["type"], cls=Resource)
      match resource_class():
        case LiquidHandler():
          self.refs["liquid_handlers"].extend((resource["name"], index))
        case Deck():
          self.refs["decks"].extend((resource["name"], index))
        case Pump():
          self.refs["pumps"].extend((resource["name"], index))
        case PumpArray():
          self.refs["pumps"].extend((resource["name"], index))
        case PlateReader():
          self.refs["plate_readers"].extend((resource["name"], index))
        #case PlateHotel():
          #self.plate_hotels.append((resource["name"], index))
        case HeaterShaker():
          self.refs["heater_shakers"].extend((resource["name"], index))
        case PowderDispenser():
          self.refs["powder_dispensers"].extend((resource["name"], index))
        case Scale():
          self.refs["scales"].extend((resource["name"], index))
        case Shaker():
          self.refs["shakers"].extend((resource["name"], index))
        case TemperatureController():
          self.refs["temperature_controllers"].extend((resource["name"], index))
        case issubclass(resource_class, Machine()):
          self.refs["other_machines"].extend((resource["name"], index))
        case _:
          self.refs["labware"].extend((resource["name"], index))

  async def _get_by_resource_type(self, name: str, resource_type: str = "resources"):
    """
    Get a resource by resource_type.

    Args:
      resource_type (str): The resource_type of resource.

    Returns:
      list[Resource]: The resources of the given resource_type.
    """
    for resource in self[resource_type]:
      if resource["name"] == name:
        return resource
    raise ValueError(f"{resource_type.capitalize().replace('_', ' ')[:-1]} {name} not found.")

  async def get_resource(self, name: str):
    """
    Get a resource by name.

    Args:
      name (str): The name of the resource.

    Returns:
      Resource: The resource.
    """
    return await self._get_by_resource_type(name=name)

  async def get_liquid_handler(self, name: str):
    """
    Get a liquid handler by name.

    Args:
      name (str): The name of the liquid handler.

    Returns:
      LiquidHandler: The liquid handler.
    """
    return await self._get_by_resource_type(resource_type="liquid_handlers", name=name)

  async def get_deck(self, name: str):
    """
    Get a deck by name.

    Args:
      name (str): The name of the deck.

    Returns:
      Deck: The deck.
    """
    return await self._get_by_resource_type(resource_type="decks", name=name)

  async def get_pump(self, name: str):
    """
    Get a pump by name.

    Args:
      name (str): The name of the pump.

    Returns:
      Pump: The pump.
    """
    return await self._get_by_resource_type(resource_type="pumps", name=name)

  async def get_plate_reader(self, name: str):
    """
    Get a plate reader by name.

    Args:
      name (str): The name of the plate reader.

    Returns:
      PlateReader: The plate reader.
    """
    return await self._get_by_resource_type(resource_type="plate_readers", name=name)

  async def get_plate_hotel(self, name: str):
    """
    Get a plate hotel by name.

    Args:
      name (str): The name of the plate hotel.

    Returns:
      PlateHotel: The plate hotel.
    """
    return await self._get_by_resource_type(resource_type="plate_hotels", name=name)

  async def get_heater_shaker(self, name: str):
    """
    Get a heater shaker by name.

    Args:
      name (str): The name of the heater shaker.

    Returns:
      HeaterShaker: The heater shaker.
    """
    return await self._get_by_resource_type(resource_type="heater_shakers", name=name)

  async def get_powder_dispenser(self, name: str):
    """
    Get a powder dispenser by name.

    Args:
      name (str): The name of the powder dispenser.

    Returns:
      PowderDispenser: The powder dispenser.
    """
    return await self._get_by_resource_type(resource_type="powder_dispensers", name=name)

  async def get_scale(self, name: str):
    """
    Get a scale by name.

    Args:
      name (str): The name of the scale.

    Returns:
      Scale: The scale.
    """
    return await self._get_by_resource_type(resource_type="scales", name=name)

  async def get_shaker(self, name: str):
    """
    Get a shaker by name.

    Args:
      name (str): The name of the shaker.

    Returns:
      Shaker: The shaker.
    """
    return await self._get_by_resource_type(resource_type="shakers", name=name)

  async def get_temperature_controller(self, name: str):
    """
    Get a temperature controller by name.

    Args:
      name (str): The name of the temperature controller.

    Returns:
      TemperatureController: The temperature controller.
    """
    return await self._get_by_resource_type(resource_type="temperature_controllers", name=name)

  async def get_other_machine(self, name: str):
    """
    Get an other machine by name.

    Args:
      name (str): The name of the other machine.

    Returns:
      Machine: The other machine.
    """
    return await self._get_by_resource_type(resource_type="other_machines", name=name)

  async def get_labware(self, name: str):
    """
    Get a labware by name.

    Args:
      name (str): The name of the labware.

    Returns:
      Labware: The labware.
    """
    return await self._get_by_resource_type(resource_type="labware", name=name)

  async def select_resource_of_type(self, selection: list[str], resource_type: str = "resources"):
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

  async def select_resources(self, selection: list[str]):
    """
    Select resources by name.

    Args:
      selection (list[str]): The names of the resources.

    Returns:
      list[Resource]: The selected resources.
    """
    return [await self.get_resource(name) for name in selection]

  async def select_liquid_handlers(self, selection: list[str]):
    """
    Select liquid handlers by name.

    Args:
      selection (list[str]): The names of the liquid handlers.

    Returns:
      list[LiquidHandler]: The selected liquid handlers.
    """
    return [await self.get_liquid_handler(name) for name in selection]

  async def select_decks(self, selection: list[str]):
    """
    Select decks by name.

    Args:
      selection (list[str]): The names of the decks.

    Returns:
      list[Deck]: The selected decks.
    """
    return [await self.get_deck(name) for name in selection]

  async def select_pumps(self, selection: list[str]):
    """
    Select pumps by name.

    Args:
      selection (list[str]): The names of the pumps.

    Returns:
      list[Pump]: The selected pumps.
    """
    return [await self.get_pump(name) for name in selection]

  async def select_plate_readers(self, selection: list[str]):
    """
    Select plate readers by name.

    Args:
      selection (list[str]): The names of the plate readers.

    Returns:
      list[PlateReader]: The selected plate readers.
    """
    return [await self.get_plate_reader(name) for name in selection]

  async def select_plate_hotels(self, selection: list[str]):
    """
    Select plate hotels by name.

    Args:
      selection (list[str]): The names of the plate hotels.

    Returns:
      list[PlateHotel]: The selected plate hotels.
    """
    return [await self.get_plate_hotel(name) for name in selection]

  async def select_heater_shakers(self, selection: list[str]):
    """
    Select heater shakers by name.

    Args:
      selection (list[str]): The names of the heater shakers.

    Returns:
      list[HeaterShaker]: The selected heater shakers.
    """
    return [await self.get_heater_shaker(name) for name in selection]

  async def select_powder_dispensers(self, selection: list[str]):
    """
    Select powder dispensers by name.

    Args:
      selection (list[str]): The names of the powder dispensers.

    Returns:
      list[PowderDispenser]: The selected powder dispensers.
    """
    return [await self.get_powder_dispenser(name) for name in selection]

  async def select_scales(self, selection: list[str]):
    """
    Select scales by name.

    Args:
      selection (list[str]): The names of the scales.

    Returns:
      list[Scale]: The selected scales.
    """
    return [await self.get_scale(name) for name in selection]

  async def select_shakers(self, selection: list[str]):
    """
    Select shakers by name.

    Args:
      selection (list[str]): The names of the shakers.

    Returns:
      list[Shaker]: The selected shakers.
    """
    return [await self.get_shaker(name) for name in selection]

  async def select_temperature_controllers(self, selection: list[str]):
    """
    Select temperature controllers by name.

    Args:
      selection (list[str]): The names of the temperature controllers.

    Returns:
      list[TemperatureController]: The selected temperature controllers.
    """
    return [await self.get_temperature_controller(name) for name in selection]

  async def select_other_machines(self, selection: list[str]):
    """
    Select other machines by name.

    Args:
      selection (list[str]): The names of the other machines.

    Returns:
      list[Machine]: The selected other machines.
    """
    return [await self.get_other_machine(name) for name in selection]

  async def select_labware(self, selection: list[str]):
    """
    Select labware by name.

    Args:
      selection (list[str]): The names of the labware.

    Returns:
      list[Labware]: The selected labware.
    """
    return [await self.get_labware(name) for name in selection]

  async def _to_be_used(self, resource_type: str, name: str):
    """
    Use a resource by name.

    Args:
      resource_type (str): The resource_type of the resource.
      name (str): The name of the resource.
    """
    resource = self._get_by_resource_type(resource_type=resource_type, name=name)
    resource["to_use"] = True

  async def specify_resources_to_use(self,
                            selection: Union[list[str], Resource],
                            resource_types: Union[list[str], str] = "resources"):
    """
    Use resources by name.

    Args:
      resource_types (Union[list[str], str]): The resource_types of the resources.
      selection (list[str]): The names of the resources.
    """
    if isinstance(resource_types, str):
      resource_types = [resource_types] * len(selection)
    if len(selection) != len(resource_types):
      raise ValueError("selection and resource_types must have the same length")
    if isinstance(selection, Resource):
      selection = [selection.name]
    for name, resource_type in zip(selection, resource_types):
      await self._to_be_used(resource_type=resource_type, name=name)

  async def specify_liquid_handlers_to_use(self, selection: Union[list[str], LiquidHandler]):
    """
    Use liquid handlers by name.

    Args:
      selection (list[str]): The names of the liquid handlers.
    """
    await self.specify_resources_to_use(selection=selection, resource_types="liquid_handlers")

  async def specify_decks_to_use(self, selection: Union[list[str], Deck]):
    """
    Use decks by name.

    Args:
      selection (list[str]): The names of the decks.
    """
    await self.specify_resources_to_use(selection=selection, resource_types="decks")

  async def specify_pumps_to_use(self, selection: Union[list[str], Pump]):
    """
    Use pumps by name.

    Args:
      selection (list[str]): The names of the pumps.
    """
    await self.specify_resources_to_use(selection=selection, resource_types="pumps")

  async def specify_plate_readers_to_use(self, selection: Union[list[str], PlateReader]):
    """
    Use plate readers by name.

    Args:
      selection (list[str]): The names of the plate readers.
    """
    await self.specify_resources_to_use(selection=selection, resource_types="plate_readers")

  async def specify_heater_shakers_to_use(self, selection: Union[list[str], HeaterShaker]):
    """
    Use heater shakers by name.

    Args:
      selection (list[str]): The names of the heater shakers.
    """
    await self.specify_resources_to_use(selection=selection, resource_types="heater_shakers")

  async def specify_powder_dispensers_to_use(self, selection: Union[list[str], PowderDispenser]):
    """
    Use powder dispensers by name.

    Args:
      selection (list[str]): The names of the powder dispensers.
    """
    await self.specify_resources_to_use(selection=selection, resource_types="powder_dispensers")

  async def specify_scales_to_use(self, selection: Union[list[str], Scale]):
    """
    Use scales by name.

    Args:
      selection (list[str]): The names of the scales.
    """
    await self.specify_resources_to_use(selection=selection, resource_types="scales")

  async def specify_shakers_to_use(self, selection: Union[list[str], Shaker]):
    """
    Use shakers by name.

    Args:
      selection (list[str]): The names of the shakers.
    """
    await self.specify_resources_to_use(selection=selection, resource_types="shakers")

  async def specify_temperature_controllers_to_use(self,
                                                    selection: Union[
                                                      list[str],
                                                      TemperatureController
                                                      ]):
    """
    Use temperature controllers by name.

    Args:
      selection (list[str]): The names of the temperature controllers.
    """
    await self.specify_resources_to_use(
      selection=selection,
      resource_types="temperature_controllers"
      )

  async def specify_other_machines_to_use(self, selection: Union[list[str], Machine]):
    """
    Use other machines by name.

    Args:
      selection (list[str]): The names of the other machines.
    """
    await self.specify_resources_to_use(selection=selection, resource_types="other_machines")

  async def specify_labware_to_use(self, selection: Union[list[str], Resource]):
    """
    Use labware by name.

    Args:
      selection (list[str]): The names of the labware.
    """
    await self.specify_resources_to_use(selection=selection, resource_types="labware")

  async def _assign_used_resources_to_deck(self, deck: Deck):
    """
    Assign used resources to a deck.

    Args:
      deck (Deck): The deck.
    """
    for deck_layout in self.decks:
      for resource in deck_layout.get_all_resources():
        if resource["location"] is None:
          if not self._is_machine(resource["type"]):
            raise ValueError(f"Resource {resource['name']} is not a machine and must have a \
                              location specified.")
          continue
        deck_resource = deck.get_resource(resource["name"])
        config_resource = await self._get_by_resource_type(resource["name"], resource["type"])
        for attr in resource.__dict__:
          if attr == "location":
            continue
          setattr(deck_resource, attr, config_resource[attr])

  async def _load_machine(self, machine: Machine):
    """
    Load machine to loaded machines.

    Args:
      machine (Machine): The machine.
    """
    self._loaded_machines.append(machine)

  async def update_deck_layouts(self):
    """
    Update the deck layouts. Use this after you update resources referenced in the deck layouts in
    the configuration file.
    """
    for deck in self.decks:
      await self._assign_used_resources_to_deck(deck)

  async def save_configuration(self, configuration_file: PathLike):
    """
    Save the configuration to a file.

    Args:
      configuration_file (PathLike): The path to the configuration file.
    """
    with open(configuration_file, "wb") as f:
      json.dump(self.configuration, f, indent=4)

  async def _start_machines(self):
    """
    Scaffold function. Eventually this should check that the machines in use are started by having
    the start method set a state in the PLR object.
    """
    for machine in self._loaded_machines:
      await machine.setup()
    while not all(machine.setup_finished for machine in self._loaded_machines):
      await asyncio.sleep(1)

  async def _stop_machines(self):
    """
    Scaffold function. Eventually this should check that the machines in use are stopped by having
    the stop method set a state in the PLR object.
    """
    for machine in self._loaded_machines:
      await machine.stop()
    while all(machine.setup_finished for machine in self._loaded_machines):
      await asyncio.sleep(1)

  async def __aenter__(self):
    for resource in self.resources:
      if "to_use" not in resource:
        resource["to_use"] = False
    if len(self.liquid_handlers_to_use) > 1:
      raise ValueError("Only one liquid handler is supported at a time.")
    if len(self.decks_to_use) > 1:
      raise ValueError("Only one deck is supported at a time.")
    for liquid_handler in self.liquid_handlers_to_use:
      liquid_handler = LiquidHandler.deserialize(**liquid_handler)
      if len(liquid_handler.deck.get_all_resources()) != 0:
        warnings.warn(
          message = f"Liquid handler {liquid_handler.name} is not empty. Please load in liquid \
                      handlers without any resources assigned to the Deck and maintain deck \
                      layouts separately. This will be deprecated in future versions.",
          category = ResourceWarning
          )
        self.decks_in_use = [liquid_handler.deck]
      else:
        liquid_handler.deck = self.decks_to_use[0]
        await self._assign_used_resources_to_deck(liquid_handler.deck)
      for machine in self.machines_to_use:
        if machine.name == liquid_handler.name:
          machine = liquid_handler
          self._load_machine(machine)
          continue
        machine_class = find_subclass(machine.type, cls=Machine)
        machine = machine_class.deserialize(**machine)
        self._load_machine(machine)
        self._start_machines()
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
  Exeriment configuration denoting specific settings for an experiment.
  """
  def __init__(self,
                configuration_file: PathLike,
                lab_configuration: Union[PathLike, LabConfiguration]):
    super().__init__(configuration_file)
    self.configuration = self.configuration["experiment_configuration"]
    if isinstance(lab_configuration, PathLike):
      lab_configuration = LabConfiguration(lab_configuration)
    if not isinstance(lab_configuration, LabConfiguration):
      raise ValueError(f"lab_configuration must be a LabConfiguration object, not \
                        {type(lab_configuration)}")
    self.lab_configuration = lab_configuration
    self.resources_to_use = self.configuration["resources_to_use"]
    self.experiment_parameters = self.configuration["experiment_parameters"]
    self.experiment_name = self.configuration["experiment_name"]
    self.experiment_details = self.configuration["experiment_details"]
    self.experiment_module_path = self.configuration["experiment_module_path"]
    self.experiment_module_name = self.configuration["experiment_module_name"]
    self.experiment_args = self.configuration["experiment_args"]
    self._experiment_directory = None
    self._experiment = None
    self._paused = False
    self._failed = False

  @property
  def paused(self) -> bool:
    return self._paused

  @property
  def failed(self) -> bool:
    return self._failed

  @property
  def experiment(self) -> Experiment:
    return self._experiment

  @property
  def experiment_directory(self) -> PathLike:
    return self._experiment_directory

  async def execute_experiment(self):
    """
    Execute the experiment.

    Args:
      lab (LabConfiguration): The lab configuration.
    """
    async with self.lab_configuration as lab: # ensures safety using machines
      try:
        spec = importlib.util.spec_from_file_location(
          name = self.experiment_module_name,
          location = self.experiment_script_path
          )
        module = importlib.util.module_from_spec(spec)
        sys.modules["plr_experiment"] = module
        spec.loader.exec_module(module)
        self._experiment_directory = os.path.realpath(os.path.dirname(self.configuration_file))
        self._experiment = module.Experiment(lab = lab,
                          experiment_directory = self.experiment_directory,
                          experiment_parameters = self.experiment_parameters,
                          experiment_name = self.experiment_name,
                          experiment_details = self.experiment_details
                          **self.kwargs)
        await self.experiment.start()
      except ModuleNotFoundError as e:
        print(f"ModuleNotFoundError: {e}")
        self._failed = True
      except KeyboardInterrupt:
        await self.pause_experiment()
      except Exception as e: # pylint: disable=broad-except
        print(f"An error occurred: {e}")
        print("")
      finally:
        if self.failed:
          print("Experiment failed.")
        else:
          print("Experiment completed.")

  async def shut_down_experiment(self):
    """
    Shut down the experiment.
    """
    pass

  async def pause_experiment(self):
    """
    Pause the experiment.
    """
    if not self.paused:
      self._paused = True
      self.experiment.pause()
      print("Experiment paused.")
      user_input = input("Type command or press enter to continue. Input 'help' to see available \
                          commands.")
    if user_input:
      try:
        self.experiment.intervene(input)
      except Exception as e: # pylint: disable=broad-except
        print(f"An error occurred attempting to execute user input: {e}")
        user_input = input("Reinput command or press enter to continue...")
      finally:
        if user_input:
          await self.pause_experiment()
        else:
          await self.resume_experiment()
    else:
      await self.resume_experiment()

  async def resume_experiment(self):
    """
    Resume the experiment.
    """
    self._paused = False
    print("Experiment resumed.")

  async def __aenter__(self):
    await self.lab_configuration.specify_resources_to_use(self.resources_to_use)
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.shut_down_experiment()
