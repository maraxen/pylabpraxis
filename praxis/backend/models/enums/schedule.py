"""Enumerated attributes related to schedule status.

Classes:
  ScheduleStatusEnum (enum.Enum): Enum representing the possible statuses of a scheduled protocol
  run, including QUEUED, RESERVED, READY_TO_EXECUTE, CELERY_QUEUED, EXECUTING, COMPLETED, FAILED,
  CANCELLED, CONFLICT, and TIMEOUT.
"""

import enum


class ScheduleStatusEnum(enum.Enum):
  """Enumeration for the status of a scheduled protocol run."""

  QUEUED = "queued"  # Waiting for assets
  RESERVED = "reserved"  # Assets successfully reserved
  READY_TO_EXECUTE = "ready_to_execute"  # Ready to be sent to Celery
  CELERY_QUEUED = "celery_queued"  # Queued in Celery
  EXECUTING = "executing"  # Currently running
  COMPLETED = "completed"  # Successfully completed
  FAILED = "failed"  # Failed during execution
  CANCELLED = "cancelled"  # Cancelled by user or system
  CONFLICT = "asset_conflict"  # Failed due to asset unavailability
  TIMEOUT = "timeout"  # Timed out waiting for assets


class ScheduleHistoryEventEnum(enum.Enum):
  """Enumeration for the types of events in schedule history."""

  SCHEDULED = "scheduled"  # Scheduled for execution
  EXECUTED = "executed"  # Execution started
  COMPLETED = "completed"  # Execution completed successfully
  FAILED = "failed"  # Execution failed
  CANCELLED = "cancelled"  # Execution cancelled
  RESCHEDULED = "rescheduled"  # Rescheduled due to changes
  CONFLICT = "conflict"  # Conflict detected during scheduling
  TIMEOUT = "timeout"  # Execution timed out
  PARTIAL_COMPLETION = "partial_completion"  # Partially completed execution
  INTERVENTION_REQUIRED = "intervention_required"  # Requires user intervention
  UNKNOWN = "unknown"  # Unknown event type
