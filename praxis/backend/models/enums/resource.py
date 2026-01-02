"""Enumerated attributes related to resource status and categories.

Classes:
  ResourceStatusEnum (enum.Enum): Enum representing the possible operational statuses of a resource
  instance, including AVAILABLE_IN_STORAGE, AVAILABLE_ON_DECK, IN_USE, EMPTY, PARTIALLY_FILLED,
  FULL, NEEDS_REFILL, TO_BE_DISPOSED, DISPOSED, TO_BE_CLEANED, CLEANED, ERROR, and UNKNOWN.
  ResourceCategoryEnum (enum.Enum): Enum representing the categories of resources in the catalog,
  including ARM, CARRIER, CONTAINER, DECK, ITEMIZED_RESOURCE, RESOURCE_HOLDER, LID, PLATE_ADAPTER,
  RESOURCE_STACK, OTHER, MFX_CARRIER, PLATE_CARRIER, TIP_CARRIER, TROUGH_CARRIER, TUBE_CARRIER,
  PETRI_DISH, TROUGH, TUBE, WELL, OT_DECK, HAMILTON_DECK, TECAN_DECK, PLATE, TIP_RACK, TUBE_RACK,
  PLATE_HOLDER, SHAKER, HEATERSHAKER, PLATE_READER, TEMPERATURE_CONTROLLER, CENTRIFUGE, INCUBATOR,
  TILTER, THERMOCYCLER, and SCALE.
"""

import enum


class ResourceStatusEnum(enum.Enum):
  """Enumeration for the possible operational statuses of a resource instance."""

  AVAILABLE_IN_STORAGE = "available_in_storage"
  AVAILABLE_ON_DECK = "available_on_deck"
  IN_USE = "in_use"
  EMPTY = "empty"
  PARTIALLY_FILLED = "partially_filled"
  FULL = "full"
  NEEDS_REFILL = "needs_refill"
  TO_BE_DISPOSED = "to_be_disposed"
  DISPOSED = "disposed"
  TO_BE_CLEANED = "to_be_cleaned"
  CLEANED = "cleaned"
  ERROR = "error"
  UNKNOWN = "unknown"


class ResourceCategoryEnum(enum.Enum):
  """Enumeration for the categories of resources in the catalog.

  This enum defines the main categories of lab resources based on a hierarchical
  classification, used to classify resources in the catalog.
  """

  # Top-level categories
  ARM = "Arm"
  CARRIER = "Carrier"
  CONTAINER = "Container"
  DECK = "Deck"
  ITEMIZED_RESOURCE = "ItemizedResource"
  RESOURCE_HOLDER = "ResourceHolder"
  LID = "Lid"
  PLATE_ADAPTER = "PlateAdapter"
  RESOURCE_STACK = "ResourceStack"
  # General catch-all for resources not fitting specific categories
  OTHER = "Other"

  # Subcategories (can be used for more granular classification if needed)
  # Arm

  # Carrier
  MFX_CARRIER = "MFXCarrier"
  PLATE_CARRIER = "PlateCarrier"
  TIP_CARRIER = "TipCarrier"
  TROUGH_CARRIER = "TroughCarrier"
  TUBE_CARRIER = "TubeCarrier"

  # Container
  PETRI_DISH = "PetriDish"
  TROUGH = "Trough"
  TUBE = "Tube"
  WELL = "Well"

  # Deck
  OT_DECK = "OTDeck"
  HAMILTON_DECK = "HamiltonDeck"
  TECAN_DECK = "TecanDeck"

  # ItemizedResource
  PLATE = "Plate"
  TIP_RACK = "TipRack"
  TUBE_RACK = "TubeRack"

  # ResourceHolder
  PLATE_HOLDER = "PlateHolder"

  # Machines
  SHAKER = "Shaker"
  HEATERSHAKER = "HeaterShaker"
  PLATE_READER = "PlateReader"
  TEMPERATURE_CONTROLLER = "TemperatureController"
  CENTRIFUGE = "Centrifuge"
  INCUBATOR = "Incubator"
  TILTER = "Tilter"
  THERMOCYCLER = "Thermocycler"  # not yet available in standard PLR
  SCALE = "Scale"

  @classmethod
  def choices(cls) -> list[str]:
    """Return a list of valid top-level category choices."""
    # This method returns the top-level categories, similar to how
    # the original `choices` might have been used for a general filter.
    return [
      cls.ARM.value,
      cls.CARRIER.value,
      cls.CONTAINER.value,
      cls.DECK.value,
      cls.ITEMIZED_RESOURCE.value,
      cls.RESOURCE_HOLDER.value,
      cls.LID.value,
      cls.PLATE_ADAPTER.value,
      cls.RESOURCE_STACK.value,
      cls.OTHER.value,
    ]

  @classmethod
  def consumables(cls) -> list[str]:
    """Return a list of common consumable categories.

    This list might need refinement based on how 'consumable' is strictly
    defined for each new category.
    """
    return [
      cls.PETRI_DISH.value,
      cls.TROUGH.value,
      cls.TUBE.value,
      cls.WELL.value,  # Individual wells might be considered consumable parts
      cls.PLATE.value,  # Plates are typically consumables
      cls.TIP_RACK.value,
      cls.TUBE_RACK.value,
      cls.LID.value,
    ]

  @classmethod
  def machines(cls) -> list[str]:
    """Return a list of resources that are also machines."""
    return [
      cls.ARM.value,
      cls.SHAKER.value,
      cls.HEATERSHAKER.value,
      cls.PLATE_READER.value,
      cls.TEMPERATURE_CONTROLLER.value,
      cls.CENTRIFUGE.value,
      cls.INCUBATOR.value,
      cls.TILTER.value,
      cls.THERMOCYCLER.value,  # not yet pulled in PLR
      cls.SCALE.value,
    ]
