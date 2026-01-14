"""Canonical PLR Category definitions.

This is the SINGLE SOURCE OF TRUTH for PLR categories used throughout the application.
These map directly to the `category` attribute on PyLabRobot classes.
"""

from enum import Enum


class PLRCategory(str, Enum):
    """PLR resource/machine categories.

    These values match the `category` attribute on PyLabRobot classes exactly.
    This enum is the single source of truth - ALL category logic should reference this.

    Examples from PyLabRobot:
        - Plate.category = "Plate"
        - TipRack.category = "TipRack"
        - Carrier.category = "Carrier"
        - LiquidHandler.category = "LiquidHandler"
    """

    # Resource categories
    PLATE = "Plate"
    TIP_RACK = "TipRack"
    TROUGH = "Trough"
    CARRIER = "Carrier"
    TUBE = "Tube"
    TUBE_RACK = "TubeRack"
    CONTAINER = "Container"
    LID = "Lid"
    DECK = "Deck"

    # Machine frontend categories
    LIQUID_HANDLER = "LiquidHandler"
    PLATE_READER = "PlateReader"
    HEATER_SHAKER = "HeaterShaker"
    SHAKER = "Shaker"
    TEMPERATURE_CONTROLLER = "TemperatureController"
    CENTRIFUGE = "Centrifuge"
    THERMOCYCLER = "Thermocycler"
    PUMP = "Pump"
    INCUBATOR = "Incubator"

    # Machine backend categories (less common in asset requirements)
    LIQUID_HANDLER_BACKEND = "LiquidHandlerBackend"
    PLATE_READER_BACKEND = "PlateReaderBackend"
    HEATER_SHAKER_BACKEND = "HeaterShakerBackend"
    SHAKER_BACKEND = "ShakerBackend"
    TEMPERATURE_CONTROLLER_BACKEND = "TemperatureControllerBackend"
    CENTRIFUGE_BACKEND = "CentrifugeBackend"
    THERMOCYCLER_BACKEND = "ThermocyclerBackend"
    PUMP_BACKEND = "PumpBackend"
    INCUBATOR_BACKEND = "IncubatorBackend"


# Type hints for common categories
RESOURCE_CATEGORIES = frozenset({
    PLRCategory.PLATE,
    PLRCategory.TIP_RACK,
    PLRCategory.TROUGH,
    PLRCategory.CARRIER,
    PLRCategory.TUBE,
    PLRCategory.TUBE_RACK,
    PLRCategory.CONTAINER,
    PLRCategory.LID,
    PLRCategory.DECK,
})

MACHINE_CATEGORIES = frozenset({
    PLRCategory.LIQUID_HANDLER,
    PLRCategory.PLATE_READER,
    PLRCategory.HEATER_SHAKER,
    PLRCategory.SHAKER,
    PLRCategory.TEMPERATURE_CONTROLLER,
    PLRCategory.CENTRIFUGE,
    PLRCategory.THERMOCYCLER,
    PLRCategory.PUMP,
    PLRCategory.INCUBATOR,
})

BACKEND_CATEGORIES = frozenset({
    PLRCategory.LIQUID_HANDLER_BACKEND,
    PLRCategory.PLATE_READER_BACKEND,
    PLRCategory.HEATER_SHAKER_BACKEND,
    PLRCategory.SHAKER_BACKEND,
    PLRCategory.TEMPERATURE_CONTROLLER_BACKEND,
    PLRCategory.CENTRIFUGE_BACKEND,
    PLRCategory.THERMOCYCLER_BACKEND,
    PLRCategory.PUMP_BACKEND,
    PLRCategory.INCUBATOR_BACKEND,
})


def get_category_from_class(cls: type) -> PLRCategory | None:
    """Extract PLR category from a class using its category attribute.

    Args:
        cls: The PLR class to get category from

    Returns:
        The PLRCategory if found, None otherwise

    Examples:
        >>> from pylabrobot.resources import Plate
        >>> get_category_from_class(Plate)
        PLRCategory.PLATE

    """
    if not hasattr(cls, "category"):
        return None

    category_value = cls.category
    if not isinstance(category_value, str):
        return None

    try:
        return PLRCategory(category_value)
    except ValueError:
        return None


def infer_category_from_name(name: str) -> PLRCategory | None:
    """Infer category from class/type name as a FALLBACK ONLY.

    This should ONLY be used when the actual class with its category attribute
    is not available (e.g., during parsing of type annotations in strings).

    Prefer using get_category_from_class() with actual class objects.

    Args:
        name: Class name or FQN

    Returns:
        The inferred PLRCategory if detectable, None otherwise

    """
    name_lower = name.lower()

    # Check for exact enum matches first
    try:
        return PLRCategory(name)
    except ValueError:
        pass

    # Pattern matching as fallback (BRITTLE - avoid when possible)
    if "plate" in name_lower and "carrier" not in name_lower and "reader" not in name_lower:
        return PLRCategory.PLATE
    if "tiprack" in name_lower or ("tip" in name_lower and "rack" in name_lower):
        return PLRCategory.TIP_RACK
    if "trough" in name_lower or "reservoir" in name_lower:
        return PLRCategory.TROUGH
    if "carrier" in name_lower:
        return PLRCategory.CARRIER
    if "tube" in name_lower and "rack" not in name_lower:
        return PLRCategory.TUBE
    if "tuberack" in name_lower or ("tube" in name_lower and "rack" in name_lower):
        return PLRCategory.TUBE_RACK
    if "deck" in name_lower:
        return PLRCategory.DECK
    if "liquidhandler" in name_lower or "liquid_handler" in name_lower:
        return PLRCategory.LIQUID_HANDLER
    if "platereader" in name_lower or "plate_reader" in name_lower:
        return PLRCategory.PLATE_READER
    if "heater" in name_lower and "shaker" in name_lower:
        return PLRCategory.HEATER_SHAKER
    if "shaker" in name_lower:
        return PLRCategory.SHAKER
    if "temperature" in name_lower and "control" in name_lower:
        return PLRCategory.TEMPERATURE_CONTROLLER
    if "centrifuge" in name_lower:
        return PLRCategory.CENTRIFUGE
    if "thermocycler" in name_lower:
        return PLRCategory.THERMOCYCLER
    if "pump" in name_lower:
        return PLRCategory.PUMP
    if "incubator" in name_lower:
        return PLRCategory.INCUBATOR

    return None
