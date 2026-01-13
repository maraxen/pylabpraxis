"""Enumerated types for various Protocol model attributes.

Classes:
  FunctionCallStatusEnum (enum.Enum): Enum representing the outcome status of an individual
  function call within a protocol run, including SUCCESS and ERROR.
  ProtocolRunStatusEnum (enum.Enum): Enum representing the operational status of a protocol run,
  including QUEUED, PENDING, PREPARING, RUNNING, PAUSING, PAUSED, RESUMING, COMPLETED, FAILED,
  CANCELING, CANCELLED, INTERVENING, and REQUIRES_INTERVENTION.
  ProtocolSourceStatusEnum (enum.Enum): Enum representing the status of a protocol source
  (repository or file system), including ACTIVE, ARCHIVED, SYNC_ERROR, and PENDING_DELETION.
"""

import enum


class ProtocolSourceStatusEnum(str, enum.Enum):
  """Enumeration for the status of a protocol source (repository or file system)."""

  ACTIVE = "active"
  ARCHIVED = "archived"
  SYNCING = "syncing"
  INACTIVE = "inactive"
  SYNC_ERROR = "sync_error"
  PENDING_DELETION = "pending_deletion"


class ProtocolRunStatusEnum(str, enum.Enum):
  """Enumeration for the operational status of a protocol run."""

  QUEUED = "QUEUED"
  PENDING = "PENDING"
  PREPARING = "PREPARING"
  RUNNING = "RUNNING"
  PAUSING = "PAUSING"
  PAUSED = "PAUSED"
  RESUMING = "RESUMING"
  COMPLETED = "COMPLETED"
  FAILED = "FAILED"
  CANCELING = "CANCELING"
  CANCELLED = "CANCELLED"
  INTERVENING = "INTERVENING"
  REQUIRES_INTERVENTION = "REQUIRES_INTERVENTION"


class FunctionCallStatusEnum(str, enum.Enum):
  """Enumeration for the outcome status of an individual function call."""

  SUCCESS = "SUCCESS"
  ERROR = "ERROR"
  PENDING = "PENDING"
  IN_PROGRESS = "in_progress"
  SKIPPED = "skipped"
  CANCELED = "canceled"
  UNKNOWN = "unknown"
