from typing import Optional, Literal, cast
from pylabrobot.resources import Plate, Well, TipRack, Coordinate
from pylabrobot.liquid_handling import LiquidHandler
from praxis.utils.errors import ExperimentError
from pylabrobot.resources.errors import ResourceNotFoundError

from praxis.utils.sanitation import liquid_handler_setup_check, coerce_to_list, type_check, \
  tip_mapping, check_list_length, parse_well_name

from pylabrobot.utils.positions import string_to_index

async def plate_idx_to_well(plate: Plate, index: int | str | Well) -> Well:
  if isinstance(index, str):
    well = plate[index][0]
  elif isinstance(index, int):
    well = plate[index][0]
  elif isinstance(index, Well):
    well = index
  else:
    raise ValueError("Invalid index type")
  return well

async def well_to_int(well: Well, plate: Plate) -> int:
  column, row = await parse_well_name(well)
  return int((column * plate.num_items_y) + row)

async def well_axes (wells: list[Well], axis: Optional[Literal[0,1]] = None) \
  -> list[int | tuple[int, int]]:
  if not all(isinstance(well, Well) for well in wells):
    raise ValueError("Invalid well type.")
  if axis is None:
    return [(int(well.name.split("_")[-2]), int(well.name.split("_")[-1])) for well in wells]
  else:
    return [int(well.name.split("_")[-1 - axis]) for well in wells]

async def wells_along_axis(wells: list[Well], axis: int) -> bool:
  if not all(isinstance(well, Well) for well in wells):
    raise ValueError("Invalid well type.")
  return len(set(well.name.split("_")[-1 - axis] for well in wells)) == 1

async def plate_sufficient_for_transfer(wells: list[list[Well]], target_plate: Plate,
                                        offset: int, n_replicates: int, replicate_axis: int):
  if replicate_axis == 0:
    if any(target_plate.num_items_x < n_replicates * len(wells) for wells in wells):
      raise ExperimentError("Number of replicates exceeds number of wells per row in target plate")
    if any(target_plate.num_items_y < len(wells) + (offset * len(wells)) for wells in wells):
      raise ExperimentError("Number of wells exceeds number of columns in target plate")
  else:
    if any(target_plate.num_items_y < n_replicates * len(wells) for wells in wells):
      raise ExperimentError("Number of replicates exceeds number of wells per column in target \
        plate")
    if any(target_plate.num_items_x < len(wells) + (offset * len(wells)) for wells in wells):
      raise ExperimentError("Number of wells exceeds number of columns in target plate")
  return True

async def well_check(wells: list[int | str | Well] | list[Well],
                      plate: Plate,
                      replicate_axis: Optional[int] = None) -> list[Well]:
  _wells: list[Well] = [await plate_idx_to_well(plate, well) for well in wells]
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
  return [[well for column, well in zip(columns, wells) if column == i] for i in \
    range(max(columns)+1)]

@liquid_handler_setup_check
async def simple_interplate_transfer(
    liquid_handler: LiquidHandler,
    tips: TipRack,
    source_plate: Plate,
    target_plate: Plate,
    transfer_volume: float,
    source_wells: list[int | str | Well],
    offset: int = 0,
    n_replicates: int = 1,
    mix_cycles: int = 1,
    replicate_axis: Literal['x', 'y', 0, 1] = 'x',
    use_96: bool = False):
  # TODO: add transfer_volumes checking
  _source_wells: list[Well] = [await plate_idx_to_well(source_plate, well) for well in source_wells]
  assert all(isinstance(well, Well) for well in source_wells)
  if target_plate.num_items < n_replicates * len(source_wells):
    raise ValueError("Target plate does not have enough wells")
  if use_96:
    if n_replicates * 96 > target_plate.num_items:
      raise ValueError("Target plate does not have enough wells")
    await liquid_handler.pick_up_tips96(tip_rack=tips)
    for i in range(n_replicates):
      target_wells = target_plate.get_quadrant(i + 1)
      await liquid_handler.aspirate96(resource=source_plate, volume=transfer_volume)
      await liquid_handler.dispense96(resource=target_wells, volume=transfer_volume)
      for target_well, source_well in zip(target_wells, source_plate.get_wells(range(96))):
            for attr in vars(source_well):
              if not hasattr(target_well, attr):
                setattr(target_well, attr, vars(source_well)[attr])
            setattr(target_well, "replicate", f"{i}")
    await liquid_handler.drop_tips96(resource=tips)
  else:
    if replicate_axis not in ['x', 'y', 0, 1]:
      raise ValueError("Invalid replicate axis")
    if not isinstance(replicate_axis, int):
      replicate_axis = 0 if replicate_axis == 'x' else 1
    well_cycle_size = target_plate.num_items_y if replicate_axis == 0 else target_plate.num_items_x
    source_wells_split = await split_wells_along_columns(_source_wells)
    source_wells_split_indexes = [[await well_to_int(well, source_plate) for well in wells] \
      async for wells in source_wells_split]
    transfer_volumes = [[transfer_volume] * len(wells) for wells in source_wells_split]
    target_well_indexes = [[well_index + (offset * i) \
      + (n_replicates * j * target_plate.num_items_y) for i,well_index in enumerate(well_indexes)] \
        for j,well_indexes in enumerate(source_wells_split_indexes)]
    target_wells: list[list[Well]] = [target_plate[well_indexes] \
        for well_indexes in target_well_indexes]
    print(target_well_indexes)
    if not await plate_sufficient_for_transfer(wells = source_wells_split,
                                        target_plate = target_plate,
                                        offset = offset,
                                        n_replicates = n_replicates,
                                        replicate_axis = replicate_axis):
      raise RuntimeError("Target plate not sufficient for transfer")
    for i, wells in enumerate(source_wells_split):
      tips_location = await tip_mapping(tips = tips,
                                        sources = wells,
                                        targets = target_wells[i],
                                        map_tips = "source")
      await liquid_handler.pick_up_tips(tip_spots = tips_location)
      for k in range(n_replicates):
        for target_well, source_well in zip(target_wells[i], wells):
          for attr in vars(source_well):
            if not hasattr(target_well, attr):
              setattr(target_well, attr, vars(source_well)[attr])
          setattr(target_well, "replicate", f"{k}")
        await liquid_handler.aspirate(wells,
                                      vols = transfer_volumes[i],
                                      mix_vols = transfer_volumes[i] * 10,
                                      mix_cycles = [mix_cycles])
        await liquid_handler.dispense(target_wells[i],
                                      vols = transfer_volumes[i],
                                      mix_vols = [transfer_volumes[i] * 10],
                                      mix_cycles = [mix_cycles])
      if i < len(source_wells) - 1:
        next_target_wells = [await well_to_int(well, target_plate) for well in target_wells[i]]
        next_target_wells = [well + well_cycle_size for well in next_target_wells]
        target_wells[i] = [await plate_idx_to_well(target_plate, well) for well in next_target_wells]
      await liquid_handler.drop_tips(tip_spots = tips_location)