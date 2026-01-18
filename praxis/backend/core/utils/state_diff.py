"""State diffing and patching utilities.

This module provides functions to calculate the difference between two nested
dictionaries and apply those differences to a base dictionary. This is used
to store incremental state changes instead of full snapshots, reducing
database storage requirements while maintaining full history.
"""

from typing import Any


def calculate_diff(old: Any, new: Any) -> Any:
  """Calculate the difference between two objects.

  Returns a dictionary representing the changes needed to transform 'old' into 'new'.
  If no changes are needed, returns None.

  Nested dictionaries are diffed recursively. Lists and other types are
  treated as atomic values and replaced entirely if they differ.
  """
  if old == new:
    return None

  if not isinstance(old, dict) or not isinstance(new, dict):
    return new

  diff = {}

  # Check for changes and additions
  for key, value in new.items():
    if key not in old:
      diff[key] = value
    else:
      nested_diff = calculate_diff(old[key], value)
      if nested_diff is not None:
        diff[key] = nested_diff

  # Check for removals
  for key in old:
    if key not in new:
      diff[key] = "__DELETED__"

  return diff if diff else None


def apply_diff(base: Any, diff: Any) -> Any:
  """Apply a diff to a base object to reconstruct the target state.

  Reverses the process of calculate_diff.
  """
  if diff is None:
    return base

  if not isinstance(base, dict) or not isinstance(diff, dict):
    return diff

  result = base.copy()

  for key, value in diff.items():
    if value == "__DELETED__":
      if key in result:
        del result[key]
    elif key in result:
      result[key] = apply_diff(result[key], value)
    else:
      result[key] = value

  return result
