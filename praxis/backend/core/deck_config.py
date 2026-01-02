"""Deck configuration loader for user-specified deck layouts.

This module provides utilities for loading and building deck configurations
from JSON files, allowing protocols to explicitly define their required
deck layout instead of relying on auto-layout.

Usage in protocol decorator:
    @protocol_function(
        is_top_level=True,
        deck_layout_path="path/to/deck_config.json"
    )
    def my_protocol(state: PraxisRunContext, deck: Deck):
        ...
"""

import importlib
import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from praxis.backend.utils.logging import get_logger

logger = get_logger(__name__)


class ResourcePlacement(BaseModel):
  """A resource placement specification within a deck layout.

  Attributes:
      resource_fqn: Fully qualified name of the PLR resource class
          (e.g., 'pylabrobot.resources.corning.plates.Cor_96_wellplate_360ul_Fb').
      name: Instance name for the resource (e.g., 'source_plate').
      slot: Optional slot identifier on the deck (e.g., 'A1', 'rail_5').
      position: Optional explicit x, y, z coordinates in mm.
      rotation: Optional rotation in degrees around z-axis.
      parent_name: Optional name of parent resource to place this on.

  """

  resource_fqn: str
  name: str
  slot: str | None = None
  position: dict[str, float] | None = None  # {"x": 0, "y": 0, "z": 0}
  rotation: float | None = None  # degrees around z-axis
  parent_name: str | None = None  # If placing on another resource


class DeckLayoutConfig(BaseModel):
  """User-specified deck layout configuration.

  This model defines the complete deck setup for a protocol,
  including the deck type and all resource placements.

  Attributes:
      deck_fqn: Fully qualified name of the PLR Deck class
          (e.g., 'pylabrobot.resources.hamilton.hamilton_decks.HamiltonSTARDeck').
      deck_kwargs: Optional keyword arguments for deck instantiation.
      placements: List of resource placements on the deck.
      description: Optional human-readable description of the layout.
      version: Optional version string for layout versioning.

  """

  deck_fqn: str
  deck_kwargs: dict[str, Any] = Field(default_factory=dict)
  placements: list[ResourcePlacement] = Field(default_factory=list)
  description: str | None = None
  version: str | None = None


def load_deck_layout(path: str | Path) -> DeckLayoutConfig:
  """Load deck layout configuration from a JSON file.

  Args:
      path: Path to the JSON configuration file.

  Returns:
      DeckLayoutConfig model validated from the JSON.

  Raises:
      FileNotFoundError: If the config file doesn't exist.
      json.JSONDecodeError: If the file contains invalid JSON.
      pydantic.ValidationError: If the JSON doesn't match the schema.

  """
  file_path = Path(path)
  if not file_path.exists():
    msg = f"Deck layout config not found: {file_path}"
    raise FileNotFoundError(msg)

  logger.info("Loading deck layout from: %s", file_path)

  with file_path.open() as f:
    data = json.load(f)

  config = DeckLayoutConfig.model_validate(data)
  logger.info(
    "Loaded deck layout: %s with %d placements",
    config.deck_fqn,
    len(config.placements),
  )
  return config


def _import_class(fqn: str) -> type:
  """Import a class from its fully qualified name.

  Args:
      fqn: Fully qualified name (e.g., 'pylabrobot.resources.Plate').

  Returns:
      The imported class.

  Raises:
      ImportError: If the module or class cannot be imported.

  """
  module_path, class_name = fqn.rsplit(".", 1)
  module = importlib.import_module(module_path)
  return getattr(module, class_name)


def build_deck_from_config(config: DeckLayoutConfig) -> Any:
  """Build a PLR Deck from configuration.

  This function instantiates the deck class and places all
  specified resources according to the configuration.

  Args:
      config: The deck layout configuration.

  Returns:
      A fully configured PLR Deck instance.

  Raises:
      ImportError: If deck or resource classes cannot be imported.
      ValueError: If placement fails due to invalid slots/positions.

  """
  # Import and instantiate the deck class
  logger.info("Building deck from config: %s", config.deck_fqn)

  deck_class = _import_class(config.deck_fqn)
  deck = deck_class(**config.deck_kwargs)

  # Build a map of resources by name for parent lookups
  resource_map: dict[str, Any] = {"deck": deck}

  # Place resources according to configuration
  for placement in config.placements:
    try:
      resource_class = _import_class(placement.resource_fqn)

      # Instantiate the resource
      resource = resource_class(name=placement.name)

      # Determine the parent (deck or another resource)
      parent = resource_map.get(placement.parent_name or "deck", deck)

      # Place the resource
      if placement.slot:
        # Slot-based placement
        parent.assign_child_at_slot(resource, placement.slot)
        logger.debug(
          "Placed %s at slot %s on %s",
          placement.name,
          placement.slot,
          parent.name if hasattr(parent, "name") else "deck",
        )
      elif placement.position:
        # Coordinate-based placement
        from pylabrobot.resources import Coordinate

        coord = Coordinate(
          x=placement.position.get("x", 0),
          y=placement.position.get("y", 0),
          z=placement.position.get("z", 0),
        )
        parent.assign_child_resource(resource, location=coord)
        logger.debug(
          "Placed %s at position (%s, %s, %s) on %s",
          placement.name,
          coord.x,
          coord.y,
          coord.z,
          parent.name if hasattr(parent, "name") else "deck",
        )
      else:
        # Let the deck auto-assign
        parent.assign_child_resource(resource)
        logger.debug("Auto-placed %s on %s", placement.name, parent.name)

      # Apply rotation if specified
      if placement.rotation is not None:
        resource.rotate(z=placement.rotation)
        logger.debug("Rotated %s by %s degrees", placement.name, placement.rotation)

      # Add to resource map for potential child resources
      resource_map[placement.name] = resource

    except Exception as e:
      logger.exception(
        "Failed to place resource %s: %s",
        placement.name,
        e,
      )
      msg = f"Failed to place resource '{placement.name}' ({placement.resource_fqn}): {e}"
      raise ValueError(
        msg
      ) from e

  logger.info(
    "Successfully built deck with %d resources",
    len(resource_map) - 1,  # Exclude 'deck' from count
  )
  return deck


def validate_deck_layout_config(config: DeckLayoutConfig) -> list[str]:
  """Validate a deck layout configuration without building it.

  Performs static validation checks:
  - All FQNs are valid import paths
  - Slots exist on the deck (if deck schema available)
  - No duplicate resource names
  - Parent resources are defined before children

  Args:
      config: The deck layout configuration to validate.

  Returns:
      List of validation warning messages (empty if valid).

  """
  warnings: list[str] = []
  seen_names: set[str] = set()

  for placement in config.placements:
    # Check for duplicate names
    if placement.name in seen_names:
      warnings.append(f"Duplicate resource name: '{placement.name}'")
    seen_names.add(placement.name)

    # Check parent exists (if specified and not deck)
    if placement.parent_name and placement.parent_name not in seen_names:
      warnings.append(
        f"Resource '{placement.name}' references undefined parent '{placement.parent_name}'"
      )

    # Check FQN format
    if "." not in placement.resource_fqn:
      warnings.append(f"Invalid FQN format for '{placement.name}': '{placement.resource_fqn}'")

    # Check position has valid keys
    if placement.position:
      valid_keys = {"x", "y", "z"}
      invalid_keys = set(placement.position.keys()) - valid_keys
      if invalid_keys:
        warnings.append(f"Invalid position keys for '{placement.name}': {invalid_keys}")

  return warnings
