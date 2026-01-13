"""Enumerated attributes related to schedule status.

Classes:
  ScheduleStatusEnum (enum.Enum): Enum representing the possible statuses of a scheduled protocol
  run, including QUEUED, RESERVED, READY_TO_EXECUTE, CELERY_QUEUED, EXECUTING, COMPLETED, FAILED,
  CANCELLED, CONFLICT, and TIMEOUT.
"""

import enum


class ScheduleStatusEnum(str, enum.Enum):
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


class ScheduleHistoryEventEnum(str, enum.Enum):
  """Enumeration for the types of events in schedule history."""

  SCHEDULE_CREATED = "schedule_created"  # Initial creation of the schedule
  SCHEDULED = "scheduled"  # Scheduled for execution
  STATUS_CHANGED = "status_changed"  # Status changed
  EXECUTED = "executed"  # Execution started
  COMPLETED = "completed"  # Execution completed successfully
  FAILED = "failed"  # Execution failed
  CANCELLED = "cancelled"  # Execution cancelled
  RESCHEDULED = "rescheduled"  # Rescheduled due to changes
  CONFLICT = "conflict"  # Conflict detected during scheduling
  TIMEOUT = "timeout"  # Execution timed out
  PARTIAL_COMPLETION = "partial_completion"  # Partially completed execution
  INTERVENTION_REQUIRED = "intervention_required"  # Requires user intervention
  PRIORITY_CHANGED = "priority_changed"  # Priority of the schedule changed
  UNKNOWN = "unknown"  # Unknown event type


class ScheduleHistoryEventTriggerEnum(str, enum.Enum):
  """Enumeration for the types of events in schedule history."""

  USER = "user"  # Triggered by a user action
  API = "api"  # Triggered by an API call
  PYLABROBOT = "pylabrobot"  # Triggered by PylabRobot
  CELERY = "celery"  # Triggered by a Celery task
  SYSTEM = "system"  # Triggered by the system
