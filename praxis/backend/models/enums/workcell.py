"""Enumerated attributes related to workcell status.

Classes:
  WorkcellStatusEnum (enum.Enum): Enum representing the possible statuses of a workcell, including
  ACTIVE, IN_USE, RESERVED, AVAILABLE, ERROR, INACTIVE, and MAINTENANCE.
"""

import enum


class WorkcellStatusEnum(str, enum.Enum):
  """Enumeration for workcell status.

  This enum defines the possible statuses a workcell can have.
  """

  ACTIVE = "active"
  IN_USE = "in_use"
  RESERVED = "reserved"
  AVAILABLE = "available"
  ERROR = "error"
  INACTIVE = "inactive"
  MAINTENANCE = "maintenance"

  @classmethod
  def choices(cls) -> list["WorkcellStatusEnum"]:
    """Return a list of valid status choices."""
    return [
      cls.ACTIVE,
      cls.IN_USE,
      cls.RESERVED,
      cls.AVAILABLE,
      cls.ERROR,
      cls.INACTIVE,
      cls.MAINTENANCE,
    ]
