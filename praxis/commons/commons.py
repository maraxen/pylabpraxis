# pylint: disable=unused-import
# pyright: reportMissingImports=false
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
                                  STARDeck
                                  )
from pylabrobot.liquid_handling.liquid_classes.hamilton.star import HighVolumeFilter_Water_DispenseSurface_Empty
from pylabrobot.pumps import (
  Pump,
  PumpArray,
  PumpCalibration,
  AgrowPumpArray,
  Masterflex
)
from pylabrobot.resources.hamilton.vantage_decks import VantageDeck
from pylabrobot.pumps.backend import PumpBackend, PumpArrayBackend
from typing import Union, Optional, Literal
import json

class NamedPump(Pump):
  """
  A pump with a name.
  """
  def __init__(self,
                backend: PumpBackend,
                size_x: float,
                size_y: float,
                size_z: float,
                name: str,
                category: Optional[str]=None,
                model: Optional[str]=None,
                calibration: Optional[PumpCalibration]=None
                ):
    super().__init__(backend=backend,
                      size_x=size_x,
                      size_y=size_y,
                      size_z=size_z,
                      name=name,
                      category=category,
                      model=model) #calibration=calibration)
    self.calibration = calibration

  def __size__(self):
    return 1

class NamedPumpArray(PumpArray):

  """
  A pump array with a name and channel names for clear coding.
  """
  def __init__(self,
                backend: PumpBackend,
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
    return self.channel_names.index(item)

  def __size__(self) -> int:
    """
    Get the size of the pump array in terms of the number of channels."""
    size = self.get("num_channels", None)
    if size is None:
      if self.channel_names is None:
        return 0
      return len(self.channel_names)
    return size

  async def serialize(self):
    return {
      **super().serialize(),
      "calibration": self.calibration,
      "channel_names": self.channel_names,
    }

  def get_channels(self, channels: Union[int, str, list[int, str]]):
    """
    Get the channels for a pump.

    Args:
      channels (Union[int, str, list[int, str]]): The channels to get.
    """
    if not isinstance(channels, list):
      channels = [channels]
    if not all(isinstance(channel, (str, int)) for channel in channels):
      raise ValueError("The channels must be a list of strings or integers.")
    return [self[channel] if isinstance(channel,str) else channel for channel in channels]

class PumpManager:
  """
  A class to handle pumps.

  Args:
    pumps (list[NamedPump, NamedPumpArray]): The pumps to manage.

  Example:
  ```python
  agrow_backend = AgrowPumpArray(port="/dev/tty.usbserial-DN02MMWP",unit=1)
  masterflex_backend = Masterflex(port="/dev/tty.usbserial-DN02MMWP",unit=2)
  agrow_calibration = PumpCalibration([1]*6)
  masterflex_calibration = PumpCalibration([1])
  agrow_channel_names = ["water_in","bleach_in","water_bleach_out","air","bacteria 1","bacteria 2"]
  pump_handler = PumpHandler(
                  pumps=[NamedPump(backend=agrow_backend,
                                  calibration=agrow_calibration,
                                  name="agrow"),
                          NamedPump(backend=masterflex_backend,
                                  calibration=masterflex_calibration,
                                  name="masterflex")],
                  )
  pump_handler.setup_pumps()

  ```

  """
  def __init__(self, pumps: list[NamedPump, NamedPumpArray]):
    self.pumps = pumps
    self._len = len(self.backends)

  async def __aenter__(self):
    await self.setup_pumps()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    for pump in self.pumps:
      await pump.close()

  def __repr__(self) -> str:
    return f"PumpManager(pumps={self.pumps})"

  def __getitem__(self, item) -> Union[Pump, PumpArray]:
    return list(filter(lambda pump: pump.name == item, self.pumps))[0]

  @classmethod
  def from_dict(cls, pump_dict: dict[str,list]) -> "PumpManager":
    """
    Create a pump handler from a dictionary.

    Args:
      pump_dict (dict): A dictionary with keys that are either "pumps" or "backends". If both are
      included, an error will be raised. If "pumps", the NamedPump and NamedPumpArray objects should
      be included in a list to be loaded directly. If "backends" is included as a key,
      "calibrations", "names", and "channel_names" will also be called, with handling for cases
      where they are not present.
    """
    if "backends" in pump_dict.keys() and "pumps" in pump_dict.keys():
      raise NotImplementedError("Keys include both 'pumps' and 'backends'. \
                                One or the other is allowed.")
    if "backends" in pump_dict.keys():
      calibrations = pump_dict.get("calibrations", [None]*len(pump_dict["backends"]))
      names = pump_dict.get("names", [str(i) for i in range(len(pump_dict["backends"]))])
      channel_names = pump_dict.get("channel_names", [None]*len(pump_dict["backends"]))
      categories = pump_dict.get("categories", [None]*len(pump_dict["backends"]))
      models = pump_dict.get("models", [None]*len(pump_dict["backends"]))
      size_xs = pump_dict.get("size_xs", [0]*len(pump_dict["backends"]))
      size_ys = pump_dict.get("size_ys", [0]*len(pump_dict["backends"]))
      size_zs = pump_dict.get("size_zs", [0]*len(pump_dict["backends"]))
      return cls.load_from_lists(backends=pump_dict["backends"],
                  calibrations=calibrations,
                  names=names,
                  channel_names=channel_names,
                  size_xs=size_xs,
                  size_ys=size_ys,
                  size_zs=size_zs,
                  categories=categories,
                  models=models)
    if "pumps" in dict.keys():
      return cls(pumps=pump_dict["pumps"])
    else:
      raise ValueError("The dictionary must include either 'pumps' or 'backends'.")

  @classmethod
  def from_json(cls, pump_json: str = "pump_handler.json") -> "PumpManager":
    """
    Create a pump handler from a json string.
    """
    with open(pump_json, "rb") as f:
      return cls.from_dict(pump_dict=json.loads(f))

  @classmethod
  def load_from_lists(cls,
                    backends:list[PumpBackend, PumpArrayBackend],
                    calibrations: Optional[list[PumpCalibration]] = None ,
                    names: Optional[list[str]] = None,
                    channel_names: Optional[list[list[str]]]=None,
                    size_xs: Optional[list[float]] = None,
                    size_ys: Optional[list[float]] = None,
                    size_zs: Optional[list[float]] = None,
                    models: Optional[list[str]] = None,
                    categories: Optional[list[str]] = None,
                    ) -> "PumpManager":
    """
    Load the pump handler from lists.
    Args:
      backends (list[PumpBackend, PumpArrayBackend]): The pumps to be handled.
        This can be a single pump, a pump array, or a list of pumps or pump arrays.
        These should be initialized backends.
      calibrations (Union[PumpCalibration, list[PumpCalibration]]): The pump calibration.
        This can be a single pump calibration or a list of pump calibrations.
      names (Optional[list[str]]): The names of the pumps. This is an optional parameter
        and should be a list of strings.
      channel_names (Optional[list[list[str]]]): The names to assign to of the pump channels.
        This is an optional parameter and can be a list of strings or integers, or a dictionary
        mapping strings or integers to lists or dictionaries of strings or integers.
        Ultimately, this should map pump names and individual pump"""
    if calibrations is None:
      calibrations = [None]*len(backends)
    if names is None:
      names = [str(i) for i in range(len(backends))]
    if channel_names is None:
      channel_names = [None]*len(backends)
    if size_xs is None:
      size_xs = [0]*len(backends)
    if size_ys is None:
      size_ys = [0]*len(backends)
    if size_zs is None:
      size_zs = [0]*len(backends)
    if models is None:
      models = [None]*len(backends)
    if categories is None:
      categories = [None]*len(backends)
    if len(backends) != len(calibrations) != len(names) != len(channel_names) != len(size_xs) != \
      len(size_ys) != len(size_zs) != len(models) != len(categories):
      raise ValueError("Lengths of inputs do not match.")
    if len(names) != len(set(names)):
      raise ValueError("The pump names must be unique.")
    return cls(pumps=[NamedPumpArray(backend=backends[i],
                                calibration=calibrations[i],
                                name=names[i],
                                size_x=size_xs[i],
                                size_y=size_ys[i],
                                size_z=size_zs[i],
                                channel_names=channel_names[i],
                                model=models[i],
                                category=categories[i])
                                if isinstance(backends[i], PumpArrayBackend)
                                else NamedPump(backend=backends[i],
                                calibration=calibrations[i],
                                name=names[i],
                                size_x=size_xs[i],
                                size_y=size_ys[i],
                                size_z=size_zs[i],
                                model=models[i],
                                category=categories[i]) for i in range(len(backends))])

  def save_to_json(self, filepath: str = "pump_handler.json"):
    """
    Convert the pump handler to a json string and save it.
    """
    with open(filepath, "wb") as f:
      f.write(self._to_json())

  def to_dict(self, as_pump_attributes: bool = False) \
    -> dict[str, Union[list[NamedPump, NamedPumpArray], dict[str, list]]]:
    """
    Convert the pump handler to a dictionary.
    """
    if as_pump_attributes:
      backends, calibrations, names, channel_names, size_xs, size_ys, size_zs, models, \
        categories = zip(*[(pump.backend, pump.calibration, pump.name, pump.channel_names, \
                            pump.size_x, pump.size_y, pump.size_z, pump.model, pump.category)
                for pump in self.pumps])
      return {"backends": backends,
      "calibrations": calibrations,
      "names": names,
      "channel_names": channel_names,
      "size_xs": size_xs,
      "size_ys": size_ys,
      "size_zs": size_zs,
      "models": models,
      "categories": categories}
    else:
      return {"pumps": self.pumps}

  def _to_json(self) -> str:
    """
    Convert the pump handler to a json string."""
    return json.dumps(self.to_dict())

  @property
  def pumps(self) -> list[NamedPump, NamedPumpArray]:
    """
    Get the pumps.
    """
    return self._pumps.values()

  def __len__(self) -> int:
    return len(self.pumps)

  def __size__(self) -> tuple[str,int]:
    return ((pump.name, pump.size) for pump in self.pumps)

  async def setup_pumps(self):
    """
    Set up the pumps.
    """
    for pump in self.pumps:
      if pump.setup_finished:
        continue
      pump.setup()

  async def pump_volume(self,
                        pump_name: str,
                        volume: float,
                        use_channels: Optional[Union[int, str, list[int, str]]] = None,
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
                            use_channels: Optional[Union[int, str, list[int, str]]] = None,
                            speed: float = 1.0):
    """
    Run a pump for a duration."""
    pump = self[pump_name]
    await self._process_pump_command(pump=pump,
                              command=pump.run_for_duration,
                              duration=duration,
                              use_channels=use_channels,
                              speed=speed)

  async def run_continously(self,
                      pump_name: str,
                      use_channels: Optional[Union[int, str, list[int, str]]] = None,
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
                      use_channels: Optional[Union[int, str, list[int, str]]] = None):
    """
    Stop a pump."""
    pump = self[pump_name]
    await self._process_pump_command(pump=pump,
                              command=pump.run_continously,
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
                            pump: Union[NamedPump, NamedPumpArray],
                            command: callable,
                            **kwargs) -> callable:
    """
    Handle the pump command and check if the pump is a pump or a pump array.
    """

    match pump:
      case NamedPump():
        kwargs.pop("use_channels", None)
        await command(**kwargs)
      case NamedPumpArray():
        kwargs["use_channels"] = pump.get_channels(kwargs["use_channels"])
        await command(**kwargs)
      case _:
        raise ValueError("The pump must be a pump or a pump array.")

  async def _load_pump(self,
                        backend: Union[PumpBackend,PumpArrayBackend],
                        calibration: Optional[PumpCalibration]=None,
                        name: Optional[str]=None,
                        channel_names: Optional[list[str]]=None):
    """
    Load the pump.
    """
    if isinstance(backend, PumpBackend):
      return NamedPump(backend=backend,
                        calibration=calibration,
                        name=name)
    else:
      return NamedPumpArray(backend=backend,
                            calibration=calibration,
                            name=name,
                            channel_names=channel_names)

class StabilizedWells(ResourceStack):
  """
  A stack of resources that are used to stabilize the plate.
  """
  def __init__(self, name: str):
    super().__init__(f"{name}_stack", "z", [
      Cos_96_DW_2mL(name),
      Lid(f"{name}_lid", size_x=127.0, size_y=86.0, size_z=9),
    ])

class BlueBucket(Resource):
  """
  A blue bucket resource for buckets that hold liquid statically on the deck."""
  def __init__(self, name: str):
    super().__init__(name, size_x=123, size_y=82, size_z=75, category="bucket")

class TipWasher(Resource):
  """
  A tip washer resource for washing tips.
  """
  def __init__(self, name: str):
    super().__init__(name, size_x=1, size_y=1, size_z=1, category="tip_washer")  # TODO: Update the size of the tip washer resource. pylint: disable=line-too-long
