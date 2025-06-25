import enum


class AssetType(str, enum.Enum):
  """Enum for the different types of assets."""

  MACHINE = "MACHINE"
  RESOURCE = "RESOURCE"
  MACHINE_RESOURCE = "MACHINE_RESOURCE"
  DECK = "DECK"
