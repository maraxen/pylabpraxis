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


class ProtocolSourceStatusEnum(enum.Enum):

  """Enumeration for the status of a protocol source (repository or file system)."""

  ACTIVE = "active"
  ARCHIVED = "archived"
  SYNCING = "syncing"
  INACTIVE = "inactive"
  SYNC_ERROR = "sync_error"
  PENDING_DELETION = "pending_deletion"


class ProtocolRunStatusEnum(enum.Enum):

  """Enumeration for the operational status of a protocol run."""

  QUEUED = "queued"
  PENDING = "pending"
  PREPARING = "preparing"
  RUNNING = "running"
  PAUSING = "pausing"
  PAUSED = "paused"
  RESUMING = "resuming"
  COMPLETED = "completed"
  FAILED = "failed"
  CANCELING = "canceling"
  CANCELLED = "cancelled"
  INTERVENING = "intervening"
  REQUIRES_INTERVENTION = "requires_intervention"


class FunctionCallStatusEnum(enum.Enum):

  """Enumeration for the outcome status of an individual function call."""

  SUCCESS = "success"
  ERROR = "error"
  PENDING = "pending"
  IN_PROGRESS = "in_progress"
  SKIPPED = "skipped"
  CANCELED = "canceled"
  UNKNOWN = "unknown"
