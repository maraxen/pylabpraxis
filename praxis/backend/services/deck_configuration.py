# pylint: disable=broad-except
"""Service layer for Deck Configuration Management.

This service layer interacts with deck-related data in the database, providing
functions to calculate deck positions based on the positioning configuration.
"""

from typing import Any


class DeckConfigurationService:
  """Service for deck configuration-related operations."""

  def get_slot_coordinates(self, positioning_config: dict[str, Any], slot: str) -> dict[str, float]:
    """Calculate the coordinates of a given slot based on the positioning configuration.

    Args:
        positioning_config: The positioning configuration from the DeckDefinitionOrm.
        slot: The slot to calculate the coordinates for.

    Returns:
        A dictionary with the x, y, and z coordinates of the slot.

    """
    positioning_type = positioning_config.get("type")

    if positioning_type == "cartesian":
      return self._get_cartesian_coordinates(positioning_config, slot)
    if positioning_type == "rails":
      return self._get_rails_coordinates(positioning_config, slot)

    msg = f"Unsupported positioning type: {positioning_type}"
    raise ValueError(msg)

  def _get_cartesian_coordinates(
    self,
    positioning_config: dict[str, Any],
    slot: str,
  ) -> dict[str, float]:
    """Calculate coordinates for a cartesian system."""
    slots = positioning_config.get("slots", {})
    slot_coords = slots.get(slot)

    if not slot_coords:
      msg = f"Slot {slot} not found in positioning configuration."
      raise ValueError(msg)

    return {
      "x": slot_coords.get("x", 0.0),
      "y": slot_coords.get("y", 0.0),
      "z": slot_coords.get("z", 0.0),
    }

  def _get_rails_coordinates(
    self,
    positioning_config: dict[str, Any],
    slot: str,
  ) -> dict[str, float]:
    """Calculate coordinates for a rail-based system."""
    try:
      slot_number = int(slot)
    except ValueError as e:
      msg = f"Invalid slot number: {slot}"
      raise ValueError(msg) from e

    rail_length = positioning_config.get("rail_length", 1000.0)
    slot_width = positioning_config.get("slot_width", 100.0)
    slot_gap = positioning_config.get("slot_gap", 10.0)
    y_offset = positioning_config.get("y_offset", 50.0)
    z_offset = positioning_config.get("z_offset", 100.0)

    x_coord = (slot_number - 1) * (slot_width + slot_gap)

    if x_coord > rail_length:
      msg = f"Slot {slot} is outside the rail length."
      raise ValueError(msg)

    return {
      "x": x_coord,
      "y": y_offset,
      "z": z_offset,
    }


deck_configuration_service = DeckConfigurationService()
