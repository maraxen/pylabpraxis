"""Enumerated attributes related to assets and their reservation statuses.

Classes:
  AssetType (str, enum.Enum): Enum representing the different types of assets, such as MACHINE,
  RESOURCE, MACHINE_RESOURCE, and DECK.
  AssetReservationStatusEnum (enum.Enum): Enum representing the possible statuses of an asset
  reservation, including RESERVED, PENDING, ACTIVE, RELEASED, EXPIRED, and FAILED.
"""

import enum


class AssetType(str, enum.Enum):
  """Enum for the different types of assets."""

  MACHINE = "MACHINE"
  RESOURCE = "RESOURCE"
  MACHINE_RESOURCE = "MACHINE_RESOURCE"
  DECK = "DECK"
  ASSET = "GENERIC_ASSET"  # Generic asset type for any physical asset


class AssetReservationStatusEnum(enum.Enum):
  """Enumeration for the status of a asset reservation."""

  RESERVED = "reserved"  # Asset successfully reserved
  PENDING = "pending"  # Reservation request pending
  ACTIVE = "active"  # Reservation is active
  RELEASED = "released"  # Reservation has been released
  EXPIRED = "expired"  # Reservation expired due to timeout
  FAILED = "failed"  # Reservation failed
