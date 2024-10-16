# pylint: disable=unused-import
# pyright: reportMissingImports=false
import warnings
from pylabrobot.liquid_handling import LiquidHandler
from pylabrobot.liquid_handling.backends.hamilton import STAR, Vantage
from pylabrobot.liquid_handling.backends.chatterbox_backend import ChatterBoxBackend
from pylabrobot.resources import (TIP_CAR_480_A00,
                                  PLT_CAR_L5AC_A00,
                                  Carrier,
                                  TipCarrier,
                                  Tip,
                                  Cos_96_EZWash,
                                  Cos_96_DW_2mL,
                                  HTF_L,
                                  Lid,
                                  ResourceStack,
                                  Deck,
                                  Resource,
                                  Coordinate,
                                  STARDeck,
                                  Plate,
                                  Container,
                                  Well,
                                  Trough
                                  )

from pylabrobot.resources.well import Well, WellBottomType, CrossSectionType
from pylabrobot.resources.utils import create_ordered_items_2d

from pylabrobot.resources.corning_costar.plates import _compute_volume_from_height_Cos_96_DW_2mL
from pylabrobot.liquid_handling.liquid_classes.hamilton.star import HighVolumeFilter_Water_DispenseSurface_Empty
from pylabrobot.pumps import (
  Pump,
  PumpArray,
  PumpCalibration,
  AgrowPumpArray,
  Masterflex
)
from pylabrobot.machines import Machine
from pylabrobot.utils.object_parsing import find_subclass
from pylabrobot.resources.hamilton.vantage_decks import VantageDeck
from pylabrobot.pumps.backend import PumpBackend, PumpArrayBackend
from typing import Union, Optional, Any, Sequence, Coroutine, Callable
import json
from praxis.utils.sanitation import fill_in_defaults
import asyncio

class NamedPumpArray(PumpArray):

  """
  A pump array with a name and channel names for clear coding.
  """
  def __init__(self,
                backend: PumpArrayBackend,
                size_x: float,
                size_y: float,
                size_z: float,
                name: str,
                category: Optional[str]=None,
                model: Optional[str]=None,
                calibration: Optional[PumpCalibration]=None,
                channel_names: Optional[list[str]]=None
                ):
    super().__init__(backend=backend,
                      size_x=size_x,
                      size_y=size_y,
                      size_z=size_z,
                      name=name,
                      category=category,
                      model=model)
    self.calibration = calibration
    self.channel_names = channel_names

  def __getitem__(self, item: str) -> int:
    """
    Get the channel index for a pump array based on the channel name.
    """
    if self.channel_names is None:
      raise ValueError("The pump array must have channel names.")
    if item not in self.channel_names:
      raise ValueError("The channel name is not in the pump array.")
    return int(self.channel_names.index(item))

  def __len__(self) -> int:
    """
    Get the size of the pump array in terms of the number of channels."""
    return self.num_channels

  def _validate_channel_names(self):
    """
    Helper function to validate the channel names.
    """
    if self.channel_names is None:
      return
    if not self._setup_finished:
      return
    if len(self.channel_names) != self.num_channels:
        raise ValueError("The number of channels does not match the length of channel_names.")

  def serialize(self):
    return {
      **super().serialize(),
      "channel_names": self.channel_names,
    }

  def get_channels(self, channels: int | str | list[int | str]):
    """
    Get the channels for a pump.

    Args:
      channels (int | str | list[int | str]): The channels to get.
    """
    if not isinstance(channels, list):
      channels = [channels]
    if not all(isinstance(channel, (str, int)) for channel in channels):
      raise ValueError("The channels must be a list of strings or integers.")
    return [self[channel] if isinstance(channel,str) else channel for channel in channels]

  async def setup(self):
    """
    Set up the pump array.
    """
    await super().setup()
    if self.channel_names is None:
      self.channel_names = [f"channel_{i}" for i in range(self.num_channels)]
    self._validate_channel_names()

class MachineManager(Resource):
  """
  A class to handle multiple of the same machine type.
  """
  def __init__(self,
                machines: list[Machine],
                accepted_types: Optional[type[Machine] | tuple[type[Machine]]] = None):
    if not all(isinstance(machine, Machine) for machine in machines):
      raise ValueError("All loaded resources must be of type machine.")
    if accepted_types is None:
      accepted_types = type(machines[0])
    if accepted_types is not None:
      if not isinstance(accepted_types, tuple):
        accepted_types = (accepted_types)
      if not all(isinstance(machine, accepted_types)for machine in machines):
        raise ValueError("All loaded resources must be of the accepted types.")
    self.machines = machines
    self.accepted_types = accepted_types
    self._names = [machine.name for machine in machines]
    self._check_names()

  def __repr__(self) -> str:
    return f"MachineManager(machines={self.machines})"

  def __getitem__(self, item: str) -> Machine:
    """
    Get a machine by name.
    """
    fetched_machine = list(filter(lambda machine: machine.name == item, self.machines))[0]
    assert fetched_machine is not None, f"Machine {item} not found"
    assert isinstance(fetched_machine, Machine), "Machine is not a machine."
    return fetched_machine

  def __len__(self) -> int:
    return len(self.machines)

  @property
  def names(self) -> list[str]:
    """
    Get the names of the machines.
    """
    return self._names

  async def setup(self):
    """
    Set up the machines.
    """
    for machine in self.machines:
      if machine.setup_finished:
        continue
      await machine.setup()

  def _check_names(self):
    """
    Check the names of the machines for duplicates.
    """
    if len(self.names) != len(set(self.names)):
      raise ValueError("Machine names are not unique.")

  def serialize(self) -> dict:
    return {"machines": [machine.serialize() for machine in self.machines],
            "accepted_types": self.accepted_types}

  @classmethod
  def deserialize(cls, data: dict[str, Any], allow_marshal: bool = False) -> "MachineManager":
    accepted_types = data.get("accepted_types", Machine)
    for machine_data in data["machines"]:
      if not isinstance(machine_data, dict):
        raise ValueError("Machine data must be a dictionary.")
      if "type" not in machine_data:
        raise ValueError("Machine data must have a type.")
    machine_subclasses = [find_subclass(machine_data["type"], Machine) \
      for machine_data in data["machines"]]
    if any(machine_subclass is None for machine_subclass in machine_subclasses):
      raise ValueError("All machines must be of type Machine.")
    machines = [machine_subclass.deserialize(machine_data) \
      for machine_subclass, machine_data in zip(data["machines"], machine_subclasses)]
    return cls(machines = machines, accepted_types = accepted_types)

  async def __aenter__(self):
    tasks = [asyncio.create_task(machine.setup() for machine in self.machines)]
    await asyncio.gather(*tasks)
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    tasks = [asyncio.create_task(machine.stop() for machine in self.machines)]
    await asyncio.gather(*tasks)


class PumpManager(MachineManager):
  """
  A class to handle pumps.

  Args:
    pumps (list[NamedPump, NamedPumpArray]): The pumps to manage.

  """
  def __init__(self,
                pumps: list[Pump | NamedPumpArray]):
    assert all(isinstance(pump, Pump | NamedPumpArray) for pump in pumps),\
      "All pumps must be pumps or pump arrays."
    super().__init__(machines=pumps, accepted_types=Machine) # type: ignore
    self._pumps = pumps

  def __repr__(self) -> str:
    return f"PumpManager(pumps={self.pumps})"

  def __getitem__(self, item) -> Pump | NamedPumpArray:
    fetched_pump = list(filter(lambda pump: pump.name == item, self.pumps))[0]
    assert fetched_pump is not None, f"Pump {item} not found"
    assert isinstance(fetched_pump, (Pump, PumpArray)), "Pump is not a pump or pump array."
    return fetched_pump

  @property
  def pumps(self) -> list[Pump | NamedPumpArray]:
    """
    Get the pumps.
    """
    return self._pumps

  def __len__(self) -> int:
    return len(self.pumps)

  async def pump_volume(self,
                        pump_name: str,
                        volume: float,
                        use_channels: Optional[int | str | list[int | str]] = None,
                        speed: float = 1.0):
    """
    Dispense a volume of liquid from a pump."""
    pump = self[pump_name]
    await self._process_pump_command(pump=pump,
                                command=pump.pump_volume,
                                volume=volume,
                                use_channels=use_channels,
                                speed=speed)

  async def run_for_duration(self,
                            pump_name: str,
                            duration: float,
                            use_channels: Optional[int | str | list[int | str]] = None,
                            speed: float = 1.0):
    """
    Run a pump for a duration."""
    pump = self[pump_name]
    await self._process_pump_command(pump=pump,
                              command=pump.run_for_duration,
                              duration=duration,
                              use_channels=use_channels,
                              speed=speed)

  async def run_continuously(self,
                      pump_name: str,
                      use_channels: Optional[int | str | list[int | str]] = None,
                      speed: float = 1.0):
    """
    Run a pump continuously."""
    pump = self[pump_name]
    await self._process_pump_command(pump=pump,
                              command=pump.run_continuously,
                              use_channels=use_channels,
                              speed=speed)

  async def stop_pump(self,
                      pump_name: str,
                      use_channels: Optional[int | str | list[int | str]] = None):
    """
    Stop a pump."""
    pump = self[pump_name]
    await self._process_pump_command(pump=pump,
                              command=pump.run_continuously,
                              speed=0,
                              use_channels=use_channels)

  async def halt_pump(self,
                      pump_name: str):
    """
    Stop a pump."""
    await self[pump_name].halt()

  async def halt_all_pumps(self):
    """
    Stop all the pumps."""
    for pump in self.pumps:
      await pump.halt()

  async def recalibrate_pump(self,
                            pump_name: str,
                            calibration: PumpCalibration):
    """
    Recalibrate a pump.

    Args:
      pump_name (str): The name of the pump to recalibrate.
      calibration (PumpCalibration): The calibration to recalibrate the pump with.
    """
    self[pump_name].calibration = calibration

  async def _process_pump_command(self,
                            pump: Pump | NamedPumpArray,
                            command: Callable,
                            **kwargs) -> None:
    """
    Handle the pump command and check if the pump is a pump or a pump array.
    """
    match pump:
      case Pump():
        kwargs.pop("use_channels", None)
        await command(**kwargs)
      case NamedPumpArray():
        kwargs["use_channels"] = pump.get_channels(kwargs["use_channels"])
        await command(**kwargs)
      case _:
        raise ValueError("The pump must be a pump or a pump array.")

  async def _load_pump(self,
                        name: str,
                        backend: PumpBackend | PumpArrayBackend,
                        size_x: float = 0,
                        size_y: float = 0,
                        size_z: float = 0,
                        calibration: Optional[PumpCalibration]=None,
                        model: Optional[str]=None,
                        category: Optional[str]=None,
                        channel_names: Optional[list[str]]=None):
    """
    Load the pump.
    """
    if name in self.names:
      raise ValueError(f"The pump {name} already exists.")
    if isinstance(backend, PumpBackend):
      return Pump(backend=backend,
                  size_x=size_x,
                  size_y=size_y,
                  size_z=size_z,
                  calibration=calibration,
                  name=name,
                  model=model,
                  category=category)
    else:
      return NamedPumpArray(backend=backend,
                            size_x=size_x,
                            size_y=size_y,
                            size_z=size_z,
                            calibration=calibration,
                            name=name,
                            model=model,
                            category=category,
                            channel_names=channel_names)

class StabilizedWells(ResourceStack):
  """
  A stack of resources that are used to stabilize the plate.
  """
  def __init__(self, name: str, **kwargs):
    super().__init__(f"{name}_stack", "z", [
      Plate(
    name=name,
    size_x=127.0,
    size_y=86.0,
    size_z=43.5,
    lid=None,
    model="StabilizedWells",
    ordered_items=create_ordered_items_2d(Well,
      num_items_x=12,
      num_items_y=8,
      dx=10.0,
      dy=7.5,
      dz=1.0,
      item_dx=9.0,
      item_dy=9.0,
      size_x=8.0,
      size_y=8.0,
      size_z=42.0,
      bottom_type=WellBottomType.U,
      cross_section_type=CrossSectionType.CIRCLE,
      compute_volume_from_height=_compute_volume_from_height_Cos_96_DW_2mL,
    ),
  ),
      Lid(f"{name}_lid", size_x=127.0, size_y=86.0, size_z=9, nesting_z_height=1.0),
    ])

class BlueBucket(Resource):
  """
  A blue bucket resource for buckets that hold liquid statically on the deck."""
  def __init__(self, name: str, **kwargs):
    super().__init__(name, size_x=123, size_y=82, size_z=75, category="bucket")

class TipWasherBasin(Container):
  """
  A tip washer basin.

  Args:
    name (str): The name of the tip washer basin.
    max_volume (float): The maximum volume of the tip washer basin.
  """
  def __init__(self, name: str,
                max_volume: float = 500,
                pump_lines: list[str] = ["0", "1"]):
    super().__init__(name,
                      size_x=111.0,
                      size_y=70.0,
                      size_z=77.0, #bottom starts 19 above chassis
                      max_volume=max_volume
                      )
    self.max_volume = 500
    self.pump_lines = pump_lines


class TipWasherChassis(Resource):
  """
  A tip washer basin.

  Args:
    name (str): The name of the tip washer basin.
    max_volume (float): The maximum volume of the tip washer basin.
  """
  def __init__(self, name: str):
    super().__init__(name,
                      size_x=135.0,
                      size_y=179.0,
                      size_z=22.0, # really 19  mm is the top of the bottom, but I want to allow for a little extra
                      category="basin_chassis")

class DualTipWasherBasin(ResourceStack):
  """
  Two back to back tip washer basins.

  Args:
    name (str): The name of the dual tip washer stack.
  """
  def __init__(self, name: str):
    super().__init__(name, "y", [
      Resource(f"{name}_spacer_dual_front", size_x=111.0, size_y=18.0, size_z=77.0),
      TipWasherBasin(f"{name}_basin1"),
      Resource(f"{name}_spacer_dual_middle", size_x=111.0, size_y=3.0, size_z=77.0),
      TipWasherBasin(f"{name}_basin2"),
      Resource(f"{name}_spacer_dual_back", size_x=111.0, size_y=18.0, size_z=77.0)
    ])

class CenteredDualTipWasherBasin(ResourceStack):
  """
  Two back to back tip washer basins.

  Args:
    name (str): The name of the dual tip washer stack.
  """
  def __init__(self, name: str):
    super().__init__(name, "x", [
      Resource(f"{name}_spacer_dual_left", size_x=12.0, size_y=64.0, size_z=77.0),
      DualTipWasherBasin(name),
      Resource(f"{name}_spacer_dual_right", size_x=12.0, size_y=64.0, size_z=77.0)
    ])

class TipWasher(ResourceStack):
  """
  A tip washer resource for washing tips.
  """
  def __init__(self, name: str):
    super().__init__(name, "z", [
      CenteredDualTipWasherBasin(name),
      TipWasherChassis(f"{name}_chassis")])


class SampleReservoir(Container):
  """
  A sample reservoir for holding liquid.
  """
  def __init__(self, name: str, max_volume: float = 1000):
    super().__init__(name, size_x=50, size_y=100, size_z=120, max_volume=1000, category="sample_reservoir")
    # TODO: figure out how to specify pickup location as in the middle since it is sloped
    self._is_empty = True

  @property
  def is_empty(self):
    return self._is_empty
