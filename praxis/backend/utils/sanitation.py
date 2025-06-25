import warnings
from functools import wraps
from typing import Any, Literal, Optional, TypeVar

from pylabrobot.resources import Plate, TipRack, TipSpot, Well

T = TypeVar("T")


async def well_to_int(well: Well, plate: Plate) -> int:
  column, row = await parse_well_name(well)
  return int((column * plate.num_items_y) + row)


def liquid_handler_setup_check(func):
  """A decorator function that checks if a liquid handler is set up before executing the decorated
  function.

  Args:
    func: The function to be decorated.

  Raises:
    ValueError: If no liquid handler is provided.
    RuntimeError: If the liquid handler is not set up.

  Returns:
    The decorated function.

  """

  @wraps(func)
  async def wrapper(*args, **kwargs):
    if len(args) == 0 and "liquid_handler" not in kwargs:
      raise ValueError("No liquid handler provided")
    elif args:
      liquid_handler = args[0]
    else:
      liquid_handler = kwargs["liquid_handler"]
    if not liquid_handler.setup_finished:
      raise RuntimeError("Liquid handler not set up")
    return await func(*args, **kwargs)

  return wrapper


async def coerce_to_list(items: list | tuple, target_length: Optional[int]) -> list:
  """Coerces the given items into a list.

  Args:
    items (list | tuple): The items to be coerced into a list.

  Returns:
    list: The coerced list.

  """
  new_items: list = []
  if target_length is None:
    target_length = 1
  for item in items:
    if item is None:
      new_items.append(None)
    elif not isinstance(item, (list, tuple)):
      new_items.append([item] * target_length)
    else:
      if len(item) == 1:
        new_items.append(item * target_length)
      elif len(item) == target_length:
        new_items.append(item)
      else:
        raise ValueError(
          f"Expected list of length {target_length} but got list of length \
          {len(item)}"
        )
  return new_items


async def fill_in_default(val: Optional[list[T]], default: list[T]) -> list[T]:
  """Util for converting an argument to the appropriate format for low level methods."""
  t = type(default[0])
  # if the val is None, use the default.
  if val is None:
    return default
  # repeat val if it is not a list.
  if not isinstance(val, list):
    return [val] * len(default)
  # if the val is a list, it must be of the correct length.
  if len(val) != len(default):
    raise ValueError(
      f"Value length must equal num operations ({len(default)}), but is {val}"
    )
  # if the val is a list of the correct length, the values must be of the right type.
  if not all(isinstance(v, t) for v in val):
    raise ValueError(f"Value must be a list of {t}, but is {val}")
  # the value is ready to be used.
  return val


async def fill_in_defaults(
  items: list[Optional[list[T]]], defaults: list[list[T]]
) -> list[list[T]]:
  """Util for converting an argument to the appropriate format for low level methods."""
  return [await fill_in_default(val, default) for val, default in zip(items, defaults)]


async def type_check(items: list, types: list, in_list: bool = False) -> None:
  """Check the types of items in a list against a given list of types.

  Args:
    items (list): The list of items to check the types for.
    types (list): The list of types to compare against.
    in_list (bool, optional): Flag indicating whether the items are nested within another list.
      Defaults to False.

  Raises:
    ValueError: If the type of any item in the list does not match the corresponding type in the
    types list.

  """
  for item, item_type in zip(items, types):
    if in_list:
      if not all(isinstance(i, item_type) for i in item):
        raise ValueError(f"Expected {item_type} but got {type(item)}")
    if not isinstance(item, item_type):
      raise ValueError(f"Expected {item_type} but got {type(item)}")


async def check_list_length(
  items: list[Any] | list[list[Any]],
  coerce_length: bool = False,
  target_length: Optional[int] = None,
) -> list[list[Any]]:
  """Check the length of a list or a list of lists.

  Args:
    items (list): The list or list of lists to check.
    length (Optional[int], optional): The expected length of the list(s). If not provided, the
    length of the first item in the list will be used. Defaults to None.

  Raises:
    ValueError: If the length of any item in the list(s) does not match the expected length.

  Returns:
    items list[list[Any]]: The list of items.

  """
  if target_length is None:
    length = len(items[0])
  if not isinstance(items[0], list):
    if len(items) != target_length:
      if len(items) == 1 and coerce_length:
        assert target_length is not None, "Expected target length to be provided"
        return items * target_length
      else:
        raise ValueError(
          f"Expected list of length {length} but got list of length {len(items)}"
        )
  new_items = []
  for item in items:
    if not isinstance(item, list):
      raise ValueError(f"Expected list but got {type(item)}")
    if len(item) != target_length:
      if len(item) == 1 and coerce_length:
        assert target_length is not None, (
          "Expected target length to be provided"
        )  # mypy assert
        new_items.append(item * target_length)
      else:
        raise ValueError(
          f"Expected list of length {length} but got list of length {len(item)}"
        )
  if all(len(item) == target_length for item in items):
    return items
  return new_items


async def parse_well_name(well: Well) -> tuple:
  """Parse the name of a well into a tuple of the row and column.

  Args:
    well_name (str): The name of the well.

  Returns:
    tuple: A tuple of the row and column of the well.

  """
  well_name = well.name.split("_")
  row = int(well_name[-2])
  column = int(well_name[-1])
  return row, column


async def parse_well_str_accession_id(well: str, plate: Plate) -> list[Well]:
  """Parse the name of a well into a tuple of the row and column.

  Args:
    well_name (str): The name of the well.

  Returns:
    tuple: A tuple of the row and column of the well.

  """
  return plate[well]


async def tip_mapping(
  tips: TipRack | list[TipSpot],
  sources: list[Well],
  source_plate: Plate,
  target_plate: Optional[Plate] = None,
  targets: Optional[list[Well]] = None,
  map_tips: Optional[Literal["source", "target"]] = None,
) -> list[TipSpot]:
  """Check if tips can be mapped between either source or destination containers based on if they
  are wells, and that the number of tips is sufficient for the number of sources and targets.

  Args:
    tips (TipRack | list[TipSpot]): The list of tips to be mapped.
    sources (list[Well]): The list of source containers.
    targets (list[Well]): The list of destination containers.

  Raises:
    ValueError: If the tips cannot be mapped between either the source and target containers.
    NotImplementedError: If multiple tip racks are used to map between source or target containers.
    ValueError: If the tip rack does not have a tip at the specified location.
    ValueError: If the type of the tip is not a list of Tip objects or a single TipRack.
    ValueError: If the value of map_tips is not "source" or "target".
    ValueError: If the number of tips is insufficient for the number of sources or targets.

  Returns:
    tips: The list of tips, either from the input or from mapping between source, target, and
    tip rack.

  """
  if isinstance(tips, list):
    if all(isinstance(tip, TipSpot) for tip in tips):
      return [tip for tip in tips if isinstance(tip, TipSpot)]  # mypy compatible return
    else:
      raise ValueError(
        "Invalid type for tip. Must be a list of TipSpot objects or TipRack."
      )
  if map_tips is None:
    map_tips = "source"
  if map_tips not in ["source", "target"]:
    raise ValueError("Invalid value for map_tips. Must be either 'source' or 'target'.")
  if targets is None and map_tips == "target":
    warnings.warn(
      "No target containers provided, mapping tips to source containers."
      "Please set map_tips to 'source' to map to source containers."
    )
    targets = sources
  map_onto = sources if map_tips == "source" else targets
  assert map_onto is not None, "Expected map_onto to be provided"  # mypy assert
  if isinstance(tips, TipRack):
    tip_number = tips.num_items
  else:
    raise ValueError(
      "Invalid type for tip. Must be a list of TipSpot objects or single TipRack."
    )
  if tip_number < len(map_onto):
    raise ValueError(
      "Insufficient number of tips for the number of sources or targets."
    )
  if isinstance(tips, TipRack):
    output_tips = []
    if not all(isinstance(item, Well) for item in map_onto):
      raise ValueError(
        "Cannot map between source or target containers and tip rack. Specify \
        tips as list[TipSpot]."
      )
    for well in map_onto:
      assert isinstance(well, Well), "Expected Well object"  # mypy compatible assert
      well_number = await well_to_int(well, source_plate)
      if not tips[well_number][0].has_tip():
        raise ValueError("Tip rack does not have tip at specified location.")
      else:
        output_tips.append(tips[well_number][0])
  return output_tips


def boolean_slice(nested_dict: dict, key: Any, value: Any) -> dict:
  """Returns a new dictionary containing only the key-value pairs from the nested dictionary where \
    the key matches the given key and the value matches the given value.

  Args:
    nested_dict (dict): The nested dictionary to be sliced.
    key (Any): The key to be matched.
    value (Any): The value to be matched.

  Returns:
    dict: The new dictionary containing only the key-value pairs that match the given key and value.

  """
  new_dict = {}
  for k, v in nested_dict.items():
    if k == key and v == value:
      new_dict[k] = v
    elif isinstance(v, dict):
      new_dict[k] = boolean_slice(v, key, value)
  return new_dict
