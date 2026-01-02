from datetime import datetime
from typing import Literal

from pydantic import BaseModel

MaintenanceType = Literal["daily", "weekly", "monthly", "quarterly", "yearly", "custom"]


class MaintenanceInterval(BaseModel):
  """Single maintenance interval definition."""

  type: MaintenanceType
  interval_days: int
  description: str | None = None
  checklist: list[str] | None = None  # Optional checklist items
  required: bool = True


class MaintenanceSchedule(BaseModel):
  """Complete maintenance schedule for an asset."""

  intervals: list[MaintenanceInterval]
  enabled: bool = True
  notes: str | None = None


class MaintenanceRecord(BaseModel):
  """Record of a completed maintenance."""

  type: MaintenanceType
  completed_at: datetime
  completed_by: str | None = None
  notes: str | None = None


class MaintenanceHistory(BaseModel):
  """All maintenance records for an asset."""

  records: dict[MaintenanceType, MaintenanceRecord]  # Last maintenance by type


# Category defaults
MAINTENANCE_DEFAULTS: dict[str, MaintenanceSchedule] = {
  "LiquidHandler": MaintenanceSchedule(
    intervals=[
      MaintenanceInterval(
        type="daily", interval_days=1, description="Daily deck cleaning and tip waste check"
      ),
      MaintenanceInterval(
        type="weekly", interval_days=7, description="Weekly channel calibration check"
      ),
      MaintenanceInterval(
        type="quarterly", interval_days=90, description="Quarterly preventive maintenance"
      ),
      MaintenanceInterval(
        type="yearly", interval_days=365, description="Annual deep service and validation"
      ),
    ]
  ),
  "PlateReader": MaintenanceSchedule(
    intervals=[
      MaintenanceInterval(
        type="yearly", interval_days=365, description="Annual optical calibration"
      ),
    ]
  ),
  "HeaterShaker": MaintenanceSchedule(
    intervals=[
      MaintenanceInterval(
        type="quarterly", interval_days=90, description="Quarterly temperature verification"
      ),
    ]
  ),
  "Centrifuge": MaintenanceSchedule(
    intervals=[
      MaintenanceInterval(
        type="yearly", interval_days=365, description="Annual rotor inspection and balancing check"
      ),
    ]
  ),
  "DEFAULT": MaintenanceSchedule(
    intervals=[
      MaintenanceInterval(
        type="yearly", interval_days=365, description="Annual general inspection"
      ),
    ]
  ),
}
