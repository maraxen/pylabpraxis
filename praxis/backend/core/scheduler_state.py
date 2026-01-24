# pylint: disable=too-many-arguments,fixme
"""Data structures representing the scheduler's state."""
import uuid
from datetime import datetime, timezone

from praxis.backend.models.pydantic_internals.runtime import RuntimeAssetRequirement


class ScheduleEntry:
  """Represents a scheduled protocol run with asset reservations."""

  def __init__(
    self,
    protocol_run_id: uuid.UUID,
    protocol_name: str,
    required_assets: list[RuntimeAssetRequirement],
    estimated_duration_ms: int | None = None,
    priority: int = 1,
  ) -> None:
    """Initialize a ScheduleEntry."""
    self.protocol_run_id = protocol_run_id
    self.protocol_name = protocol_name
    self.required_assets = required_assets
    self.estimated_duration_ms = estimated_duration_ms
    self.priority = priority
    self.scheduled_at = datetime.now(timezone.utc)
    self.status = "QUEUED"
    self.celery_task_id: str | None = None
