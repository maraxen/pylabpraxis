"""Enumerated types for various Machine model attributes.

Classes:
  MachineCategoryEnum (str, enum.Enum): Enum representing the different categories of machines, such
  as LIQUID_HANDLER, PLATE_READER, and INCUBATOR.
  MachineStatusEnum (str, enum.Enum): Enum representing the possible operational statuses of a
  machine, including AVAILABLE, IN_USE, ERROR, OFFLINE, INITIALIZING, and MAINTENANCE.
"""

import enum


class MachineStatusEnum(enum.Enum):
  """Enumeration for the possible operational statuses of a machine."""

  AVAILABLE = "available"
  IN_USE = "in_use"
  ERROR = "error"
  OFFLINE = "offline"
  INITIALIZING = "initializing"
  MAINTENANCE = "maintenance"


class MachineCategoryEnum(enum.Enum):
  """Enumeration for classifying machines into predefined categories.

  These categories help in broad classification of machines based on their
  functionality, mapping to PyLabRobot's machine types.
  """

  LIQUID_HANDLER = "LiquidHandler"
  PLATE_READER = "PlateReader"
  INCUBATOR = "Incubator"
  SHAKER = "Shaker"
  HEATER_SHAKER = "HeaterShaker"
  PUMP = "Pump"
  FAN = "Fan"
  TEMPERATURE_CONTROLLER = "TemperatureController"
  TILTING = "Tilting"
  THERMOCYCLER = "Thermocycler"
  SEALER = "Sealer"
  FLOW_CYTOMETER = "FlowCytometer"
  SCALE = "Scale"
  CENTRIFUGE = "Centrifuge"
  ARM = "Arm"
  GENERAL_AUTOMATION_DEVICE = "GeneralAutomationDevice"
  OTHER_INSTRUMENT = "OtherInstrument"
  UNKNOWN = "Unknown"

  @classmethod
  def resources(cls) -> list["MachineCategoryEnum"]:
    """Return a list of resource categories that map to this enum."""
    return [
      cls.PLATE_READER,
      cls.INCUBATOR,
      cls.SHAKER,
      cls.HEATER_SHAKER,
      cls.TEMPERATURE_CONTROLLER,
      cls.TILTING,
      cls.THERMOCYCLER,
      cls.FLOW_CYTOMETER,
      cls.SCALE,
      cls.CENTRIFUGE,
      cls.ARM,
      cls.GENERAL_AUTOMATION_DEVICE,
    ]
