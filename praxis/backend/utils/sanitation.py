# pylint: disable=too-many-branches
"""Sanitation and validation utilities for input data."""

import warnings
from functools import wraps
from typing import Any, Literal, TypeVar

from pylabrobot.resources import Plate, TipRack, TipSpot, Well

T = TypeVar("T")


async def well_to_int(well: Well, plate: Plate) -> int:
  """Convert a well object to its integer index on the plate.

  Args:
    well: The well object.
    plate: The plate object.

  Returns:
    The integer index of the well.

  """
  column, row = await parse_well_name(well)
  return int((column * plate.num_items_y) + row)


def liquid_handler_setup_check(func: Any) -> Any:  # noqa: ANN401
  """Check if a liquid handler is set up before executing the decorated function.

  Args:
    func: The function to be decorated.

  Raises:
    ValueError: If no liquid handler is provided.
    RuntimeError: If the liquid handler is not set up.

  Returns:
    The decorated function.

  """

  @wraps(func)
  async def wrapper(*args: Any, **kwargs: Any) -> Any:  # noqa: ANN401
    if len(args) == 0 and "liquid_handler" not in kwargs:
      msg = "No liquid handler provided"
      raise ValueError(msg)
    liquid_handler = args[0] if args else kwargs["liquid_handler"]
    if not liquid_handler.setup_finished:
      msg = "Liquid handler not set up"
      raise RuntimeError(msg)
    return await func(*args, **kwargs)

  return wrapper


async def coerce_to_list(items: list | tuple, target_length: int | None) -> list:
  """Coerces the given items into a list.

  Args:
    items (list | tuple): The items to be coerced into a list.
    target_length (int | None): The expected length of the list.

  Returns:
    list: The coerced list.

  """
  new_items: list = []
  if target_length is None:
    target_length = 1
  for item in items:
    if item is None:
      new_items.append(None)
    elif not isinstance(item, list | tuple):
      new_items.append([item] * target_length)
    elif len(item) == 1:
      new_items.append(item * target_length)
    elif len(item) == target_length:
      new_items.append(item)
    else:
      msg = f"Expected list of length {target_length} but got list of length \
          {len(item)}"
      raise ValueError(
        msg,
      )
  return new_items


async def fill_in_default(val: list[T] | None, default: list[T]) -> list[T]:
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
    msg = f"Value length must equal num operations ({len(default)}), but is {val}"
    raise ValueError(
      msg,
    )
  # if the val is a list of the correct length, the values must be of the right type.
  if not all(isinstance(v, t) for v in val):
    msg = f"Value must be a list of {t}, but is {val}"
    raise TypeError(msg)
  # the value is ready to be used.
  return val


async def fill_in_defaults(
  items: list[list[T] | None],
  defaults: list[list[T]],
) -> list[list[T]]:
  """Util for converting an argument to the appropriate format for low level methods."""
  return [
    await fill_in_default(val, default) for val, default in zip(items, defaults, strict=False)
  ]


async def type_check(items: list, types: list, *, in_list: bool = False) -> None:
  """Check the types of items in a list against a given list of types.

  Args:
    items (list): The list of items to check the types for.
    types (list): The list of types to compare against.
    in_list (bool, optional): Flag indicating whether the items are nested within another list.
      Defaults to False.

  Raises:
    TypeError: If the type of any item in the list does not match the corresponding type in the
    types list.

  """
  for item, item_type in zip(items, types, strict=False):
    if in_list and not all(isinstance(i, item_type) for i in item):
      msg = f"Expected {item_type} but got {type(item)}"
      raise TypeError(msg)
    if not isinstance(item, item_type):
      msg = f"Expected {item_type} but got {type(item)}"
      raise TypeError(msg)


def _check_coercion(
  items: list | Any,  # noqa: ANN401
  *,
  coerce_length: bool,
  target_length: int | None,
) -> list | None:
  """Check if items can be coerced to the target length."""
  if len(items) == 1 and coerce_length:
    if target_length is None:
      msg = "Expected target length to be provided"
      raise ValueError(msg)
    return items * target_length
  return None


async def check_list_length(
  items: list[Any] | list[list[Any]],
  *,
  coerce_length: bool = False,
  target_length: int | None = None,
) -> list[list[Any]]:
  """Check the length of a list or a list of lists.

  Args:
    items (list): The list or list of lists to check.
    coerce_length (bool, optional): Whether to coerce single items to lists of the target length.
      Defaults to False.
    target_length (Optional[int], optional): The expected length of the list(s). If not provided,
      the length of the first item in the list will be used. Defaults to None.

  Raises:
    ValueError: If the length of any item in the list(s) does not match the expected length.
    TypeError: If items are not lists.

  Returns:
    items list[list[Any]]: The list of items.

  """
  length = len(items[0]) if target_length is None else target_length

  if not isinstance(items[0], list) and len(items) != length:
    coerced = _check_coercion(
      items, coerce_length=coerce_length, target_length=target_length,
    )
    if coerced:
      return coerced
    msg = f"Expected list of length {length} but got list of length {len(items)}"
    raise ValueError(
      msg,
    )

  new_items = []
  for item in items:
    if not isinstance(item, list):
      msg = f"Expected list but got {type(item)}"
      raise TypeError(msg)
    if len(item) != length:
      coerced = _check_coercion(
        item, coerce_length=coerce_length, target_length=target_length,
      )
      if coerced:
        new_items.append(coerced)
      else:
        msg = f"Expected list of length {length} but got list of length {len(item)}"
        raise ValueError(
          msg,
        )
  if all(len(item) == length for item in items):
    return items
  return new_items


async def parse_well_name(well: Well) -> tuple:
  """Parse the name of a well into a tuple of the row and column.

  Args:
    well (Well): The well object.

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
    well (str): The name of the well.
    plate (Plate): The plate object.

  Returns:
    tuple: A tuple of the row and column of the well.

  """
  return plate[well]


def _validate_tips(tips: Any) -> list[TipSpot]:  # noqa: ANN401
  if isinstance(tips, list):
    if all(isinstance(tip, TipSpot) for tip in tips):
      return [tip for tip in tips if isinstance(tip, TipSpot)]
    msg = "Invalid type for tip. Must be a list of TipSpot objects or TipRack."
    raise TypeError(msg)
  if isinstance(tips, TipRack):
    # This branch is just for type checking, logic for TipRack is handled in caller
    return []
  msg = "Invalid type for tip. Must be a list of TipSpot objects or single TipRack."
  raise TypeError(msg)


async def _get_tips_from_rack(
  tips: TipRack, map_onto: list[Well], source_plate: Plate,
) -> list[TipSpot]:
  output_tips = []
  if not all(isinstance(item, Well) for item in map_onto):
    msg = "Cannot map between source or target containers and tip rack. Specify \
      tips as list[TipSpot]."
    raise ValueError(msg)
  for well in map_onto:
    if not isinstance(well, Well):
      msg = "Expected Well object"
      raise TypeError(msg)
    well_number = await well_to_int(well, source_plate)
    if not tips[well_number][0].has_tip():
      msg = "Tip rack does not have tip at specified location."
      raise ValueError(msg)
    output_tips.append(tips[well_number][0])
  return output_tips


async def tip_mapping(
  tips: TipRack | list[TipSpot],
  sources: list[Well],
  source_plate: Plate,
  _target_plate: Plate | None = None,
  targets: list[Well] | None = None,
  map_tips: Literal["source", "target"] | None = None,
) -> list[TipSpot]:
  """Check if tips can be mapped between either source or destination containers.

  This is based on if they are wells, and that the number of tips is sufficient for the number of
  sources and targets.

  Args:
    tips (TipRack | list[TipSpot]): The list of tips to be mapped.
    sources (list[Well]): The list of source containers.
    source_plate (Plate): The source plate.
    _target_plate (Plate | None): The target plate (unused).
    targets (list[Well]): The list of destination containers.
    map_tips (Literal["source", "target"] | None): Which containers to map tips to.

  Raises:
    ValueError: If the tips cannot be mapped between either the source and target containers.
    NotImplementedError: If multiple tip racks are used to map between source or target containers.
    ValueError: If the tip rack does not have a tip at the specified location.
    TypeError: If the type of the tip is not a list of Tip objects or a single TipRack.
    ValueError: If the value of map_tips is not "source" or "target".
    ValueError: If the number of tips is insufficient for the number of sources or targets.

  Returns:
    tips: The list of tips, either from the input or from mapping between source, target, and
    tip rack.

  """
  if isinstance(tips, list):
    return _validate_tips(tips)

  if map_tips is None:
    map_tips = "source"
  if map_tips not in ["source", "target"]:
    msg = "Invalid value for map_tips. Must be either 'source' or 'target'."
    raise ValueError(msg)
  if targets is None and map_tips == "target":
    warnings.warn(
      "No target containers provided, mapping tips to source containers."
      "Please set map_tips to 'source' to map to source containers.",
      stacklevel=2,
    )
    targets = sources
  map_onto = sources if map_tips == "source" else targets
  if map_onto is None:
    msg = "Expected map_onto to be provided"
    raise ValueError(msg)

  if not isinstance(tips, TipRack):
    msg = "Invalid type for tip. Must be a list of TipSpot objects or single TipRack."
    raise TypeError(msg)

  tip_number = tips.num_items
  if tip_number < len(map_onto):
    msg = "Insufficient number of tips for the number of sources or targets."
    raise ValueError(msg)

  return await _get_tips_from_rack(tips, map_onto, source_plate)


def boolean_slice(nested_dict: dict, key: Any, value: Any) -> dict:  # noqa: ANN401
  """Return a new dictionary containing only the key-value pairs from the nested dictionary.

  This filters where the key matches the given key and the value matches the given value.

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
