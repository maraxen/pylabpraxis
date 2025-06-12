from typing import Optional, Literal
from pylabrobot.resources import Plate, Well, TipRack, Coordinate
from pylabrobot.liquid_handling import LiquidHandler
from praxis.utils.errors import ExperimentError
from pylabrobot.resources.errors import ResourceNotFoundError
from pylabrobot.plate_reading import PlateReader
from pylabrobot.resources import CarrierSite
from pylabrobot.liquid_handling.standard import GripDirection
import numpy as np

from praxis.utils.sanitation import liquid_handler_setup_check, parse_well_name

# take advantage of traverse and snake


async def plate_accession_idx_to_well(plate: Plate, index: int | str | Well) -> Well:
  if isinstance(index, str):
    well = plate[index][0]
  elif isinstance(index, int):
    well = plate[index][0]
  elif isinstance(index, Well):
    well = index
  else:
    raise ValueError("Invalid index type")
  return well


def get_all_wells(plate: Plate) -> list[Well]:
  return [well for well in plate.get_wells(range(plate.num_items))]


async def well_to_int(well: Well, plate: Plate) -> int:
  column, row = await parse_well_name(well)
  return int((column * plate.num_items_y) + row)


async def well_axes(
  wells: list[Well], axis: Optional[Literal[0, 1]] = None
) -> list[int | tuple[int, int]]:
  if not all(isinstance(well, Well) for well in wells):
    raise ValueError("Invalid well type.")
  if axis is None:
    return [
      (int(well.name.split("_")[-2]), int(well.name.split("_")[-1])) for well in wells
    ]
  else:
    return [int(well.name.split("_")[-1 - axis]) for well in wells]


async def wells_along_axis(wells: list[Well], axis: int) -> bool:
  if not all(isinstance(well, Well) for well in wells):
    raise ValueError("Invalid well type.")
  return len(set(well.name.split("_")[-1 - axis] for well in wells)) == 1


async def plate_sufficient_for_transfer(
  wells: list[list[Well]],
  target_plate: Plate,
  offset: int,
  n_replicates: int,
  replicate_axis: int,
):
  if replicate_axis == 0:
    if any(target_plate.num_items_x < n_replicates * len(wells) for wells in wells):
      raise ExperimentError(
        "Number of replicates exceeds number of wells per row in target plate"
      )
    if any(
      target_plate.num_items_y < len(wells) + (offset * len(wells)) for wells in wells
    ):
      raise ExperimentError("Number of wells exceeds number of columns in target plate")
  else:
    if any(target_plate.num_items_y < n_replicates * len(wells) for wells in wells):
      raise ExperimentError(
        "Number of replicates exceeds number of wells per column in target \
        plate"
      )
    if any(
      target_plate.num_items_x < len(wells) + (offset * len(wells)) for wells in wells
    ):
      raise ExperimentError("Number of wells exceeds number of columns in target plate")
  return True


async def group_wells_by_variables(
  wells: list[Well], key: str, variables: list[str]
) -> list[list[Well]]:
  if not all(isinstance(well, Well) for well in wells):
    raise ValueError("Invalid well type.")
  return [
    [well for well in wells if getattr(well, key, None) == var] for var in variables
  ]


async def well_check(
  wells: list[int | str | Well] | list[Well],
  plate: Plate,
  replicate_axis: Optional[int] = None,
) -> list[Well]:
  _wells: list[Well] = [
    await plate_accession_idx_to_well(plate, well) for well in wells
  ]
  if not all(isinstance(well, Well) for well in _wells):
    raise ValueError("Invalid well type.")
  if not all(well in plate.get_wells(range(plate.num_items)) for well in _wells):
    raise ResourceNotFoundError("Well not in source plate")
  if replicate_axis is not None:
    if not await wells_along_axis(_wells, int(not replicate_axis)):
      raise ExperimentError("Wells not along specified axis")
  return _wells


async def split_wells_along_columns(wells: list[Well]) -> list[list[Well]]:
  if not all(isinstance(well, Well) for well in wells):
    raise ValueError("Invalid well type.")
  columns = [(await parse_well_name(well))[0] for well in wells]
  return [
    [well for column, well in zip(columns, wells) if column == i]
    for i in range(max(columns) + 1)
  ]


@liquid_handler_setup_check
async def simple_interplate_transfer(
  liquid_handler: LiquidHandler,
  tips: TipRack,
  source_plate: Plate,
  target_plate: Plate,
  transfer_volume: float,
  source_wells: list[int | str | Well],
  offset: int = 0,
  n_replicates: Optional[int] = None,
  mix_cycles: int = 1,
  replicate_axis: Literal["x", "y", 0, 1] = "x",
  use_96: bool = False,
  return_tips: bool = False,
):
  # TODO: add transfer_volumes checking
  _source_wells: list[Well] = [
    await plate_accession_idx_to_well(source_plate, well) for well in source_wells
  ]
  assert all(isinstance(well, Well) for well in source_wells)
  if use_96:
    if n_replicates:
      if target_plate.num_items < n_replicates * len(source_wells):
        raise ValueError("Target plate does not have enough wells")
      if n_replicates * 96 > target_plate.num_items:
        raise ValueError("Target plate does not have enough wells")
      if not all(tip.has_tip for tip in liquid_handler.head96.values()):
        await liquid_handler.pick_up_tips96(tip_rack=tips)
      for i in range(n_replicates):
        target_wells = target_plate.get_quadrant(i + 1)
        await liquid_handler.aspirate96(resource=source_plate, volume=transfer_volume)
        await liquid_handler.dispense96(resource=target_wells, volume=transfer_volume)
        for target_well, source_well in zip(
          target_wells, source_plate.get_wells(range(96))
        ):
          for attr in vars(source_well):
            if not hasattr(target_well, attr):
              setattr(target_well, attr, vars(source_well)[attr])
          setattr(target_well, "replicate", f"{i}")
      if return_tips:
        await liquid_handler.drop_tips96(resource=tips)
    else:
      assert target_plate.num_items == source_plate.num_items
      if not all(tip.has_tip for tip in liquid_handler.head96.values()):
        await liquid_handler.pick_up_tips96(tip_rack=tips)
      await liquid_handler.aspirate96(resource=source_plate, volume=transfer_volume)
      await liquid_handler.dispense96(resource=target_plate, volume=transfer_volume)
      for target_well, source_well in zip(
        target_plate.get_wells(range(target_plate.num_items)),
        source_plate.get_wells(range(target_plate.num_items)),
      ):
        for attr in vars(source_well):
          if not hasattr(target_well, attr):
            setattr(target_well, attr, vars(source_well)[attr])
      if return_tips:
        await liquid_handler.drop_tips96(resource=tips)
  else:
    raise NotImplementedError("Use of 8 channel not implemented")


async def read_plate(
  liquid_handler: LiquidHandler,
  plate_reader: PlateReader,
  plate: Plate,
  wavelength: int = 580,
  final_location: Optional[CarrierSite | Coordinate] = None,
):
  """
  Reads the optical density of a plate at a specified wavelength using a plate reader.

  Parameters:
    liquid_handler (LiquidHandler): The liquid handler used to move the plate.
    plate_reader (PlateReader): The plate reader used to read the plate.
    plate (Plate): The plate to be read.
    wavelength (int, optional): The wavelength at which to read the plate. Defaults to 580.
    final_location (Optional[CarrierSite], optional): The final location where the plate will be
    moved after reading.  If not specified, the plate will be moved to its parent location. Defaults to None.

  Returns:
    numpy.ndarray: An array containing the optical density readings of the plate at the specified wavelength.

  Raises:
    ValueError: If the final location is not a valid CarrierSite.
  """
  if final_location is None:
    if not isinstance(plate.parent, CarrierSite):
      final_location = plate.get_absolute_location()
    else:
      final_location = plate.parent

  if not isinstance(final_location, (CarrierSite, Coordinate)):
    raise ValueError("Invalid final location")

  await plate_reader.open()
  await liquid_handler.move_plate(
    plate,
    plate_reader,
    pickup_distance_from_top=12.2,
    get_direction=GripDirection.FRONT,
    put_direction=GripDirection.LEFT,
  )

  await plate_reader.close()

  # read the optical depth at 580 nm
  plate_reading = await plate_reader.read_absorbance(wavelength=wavelength, report="OD")
  plate_reading = np.asarray(plate_reading)

  await plate_reader.open()

  # move plate out of the plate reader
  await liquid_handler.move_plate(
    plate_reader.get_plate(),
    final_location,
    pickup_distance_from_top=12.2,
    get_direction=GripDirection.LEFT,
    put_direction=GripDirection.FRONT,
  )

  return plate_reading
