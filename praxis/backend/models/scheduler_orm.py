# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""Scheduler ORM Models for Protocol Execution Scheduling and Asset Management.

This module defines ORM models for managing protocol scheduling, asset reservations,
and execution history. These models work alongside the existing protocol and asset
models to provide comprehensive scheduling capabilities.

Key Features:
- Protocol run scheduling and queuing
- Asset reservation tracking with Redis integration
- Schedule history and analytics
- Celery task management integration
- Asset conflict resolution
"""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
  pass

from sqlalchemy import (
  JSON,
  UUID,
  DateTime,
  Float,
  ForeignKey,
  Integer,
  String,
  Text,
  UniqueConstraint,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from praxis.backend.utils.db import Base


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


class AssetReservationStatusEnum(enum.Enum):
  """Enumeration for the status of a asset reservation."""

  RESERVED = "reserved"  # Asset successfully reserved
  PENDING = "pending"  # Reservation request pending
  ACTIVE = "active"  # Reservation is active
  RELEASED = "released"  # Reservation has been released
  EXPIRED = "expired"  # Reservation expired due to timeout
  FAILED = "failed"  # Reservation failed


class ScheduleEntryOrm(Base):
  """SQLAlchemy ORM model for tracking scheduled protocol runs.

  This model represents a protocol run that has been scheduled for execution,
  including its priority, asset requirements, and current status.
  """

  __tablename__ = "schedule_entries"

  accession_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  protocol_run_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("protocol_runs.accession_id"),
    nullable=False,
    unique=True,
    index=True,
  )
  status: Mapped[ScheduleStatusEnum] = mapped_column(
    SAEnum(ScheduleStatusEnum, name="schedule_status_enum"),
    default=ScheduleStatusEnum.QUEUED,
    nullable=False,
    index=True,
  )
  priority: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

  # Scheduling metadata
  scheduled_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), nullable=False
  )
  asset_analysis_completed_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  assets_reserved_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  execution_started_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  execution_completed_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )

  # Asset requirements and analysis
  required_asset_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  asset_requirements_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
  estimated_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

  # Celery integration
  celery_task_id: Mapped[Optional[str]] = mapped_column(
    String, nullable=True, index=True
  )
  celery_queue_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)

  # Status tracking
  retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
  last_error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

  # Metadata
  user_params_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
  initial_state_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

  # Timestamps
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), nullable=False
  )
  updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    nullable=False,
  )

  # Relationships
  protocol_run = relationship("ProtocolRunOrm", back_populates="schedule_entry")
  asset_reservations = relationship(
    "AssetReservationOrm", back_populates="schedule_entry", cascade="all, delete-orphan"
  )
  schedule_history = relationship(
    "ScheduleHistoryOrm", back_populates="schedule_entry", cascade="all, delete-orphan"
  )


class AssetReservationOrm(Base):
  """SQLAlchemy ORM model for tracking asset reservations.

  This model tracks individual asset reservations for scheduled protocol runs,
  working in conjunction with Redis for distributed locking.
  """

  __tablename__ = "asset_reservations"

  accession_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  schedule_entry_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID, ForeignKey("schedule_entries.accession_id"), nullable=False, index=True
  )

  # Asset identification
  asset_type: Mapped[str] = mapped_column(
    String, nullable=False, index=True
  )  # "machine", "asset", "deck"
  asset_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
  asset_instance_accession_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    UUID, ForeignKey("asset_instances.accession_id"), nullable=True, index=True
  )
  # Reservation details
  status: Mapped[AssetReservationStatusEnum] = mapped_column(
    SAEnum(AssetReservationStatusEnum, name="asset_reservation_status_enum"),
    default=AssetReservationStatusEnum.PENDING,
    nullable=False,
    index=True,
  )

  # Redis lock information
  redis_lock_key: Mapped[str] = mapped_column(String, nullable=False, index=True)
  redis_lock_value: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  lock_timeout_seconds: Mapped[int] = mapped_column(
    Integer, default=3600, nullable=False
  )  # 1 hour default

  # Timing
  reserved_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  released_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  expires_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )

  # Reservation metadata
  required_capabilities_json: Mapped[Optional[dict]] = mapped_column(
    JSON, nullable=True
  )
  estimated_usage_duration_ms: Mapped[Optional[int]] = mapped_column(
    Integer, nullable=True
  )

  # Timestamps
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), nullable=False
  )
  updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    nullable=False,
  )

  # Relationships
  schedule_entry = relationship("ScheduleEntryOrm", back_populates="asset_reservations")


class ScheduleHistoryOrm(Base):
  """SQLAlchemy ORM model for tracking schedule status changes and events.

  This model provides an audit trail of all scheduling events for analytics
  and debugging purposes.
  """

  __tablename__ = "schedule_history"

  accession_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  schedule_entry_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID, ForeignKey("schedule_entries.accession_id"), nullable=False, index=True
  )

  # Event details
  event_type: Mapped[str] = mapped_column(
    String, nullable=False, index=True
  )  # "status_change", "asset_reservation", "error", etc.
  from_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  to_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)

  # Event data
  event_data_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
  message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
  error_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

  # Performance metrics
  duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
  asset_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

  # Timestamp
  timestamp: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
  )

  # Relationships
  schedule_entry = relationship("ScheduleEntryOrm", back_populates="schedule_history")


class SchedulerMetricsOrm(Base):
  """SQLAlchemy ORM model for storing scheduler performance metrics.

  This model tracks aggregated metrics for scheduler performance analysis
  and optimization.
  """

  __tablename__ = "scheduler_metrics"

  accession_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)

  # Time period for metrics
  metric_date: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), nullable=False, index=True
  )
  hour_of_day: Mapped[int] = mapped_column(Integer, nullable=False, index=True)  # 0-23

  # Scheduling metrics
  protocols_scheduled: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  protocols_completed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  protocols_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  protocols_cancelled: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

  # Performance metrics
  avg_scheduling_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  avg_execution_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
  avg_queue_wait_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

  # Asset metrics
  asset_conflicts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  avg_asset_reservation_time_ms: Mapped[Optional[float]] = mapped_column(
    Float, nullable=True
  )
  max_concurrent_protocols: Mapped[int] = mapped_column(
    Integer, default=0, nullable=False
  )

  # System metrics
  celery_queue_length: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
  redis_operations_count: Mapped[int] = mapped_column(
    Integer, default=0, nullable=False
  )

  # Timestamps
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), nullable=False
  )
  updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    nullable=False,
  )

  # Constraints
  __table_args__ = (
    UniqueConstraint(
      "metric_date", "hour_of_day", name="uq_scheduler_metrics_date_hour"
    ),
  )


# Remove any legacy/obsolete fields, ensure docstrings and field types are consistent

# Add relationships to existing models (these would be added via alembic migration)
# This shows the integration points with existing models:

# In ProtocolRunOrm:
# schedule_entry = relationship("ScheduleEntryOrm", back_populates="protocol_run", uselist=False)

# In AssetInstanceOrm:
# asset_reservations = relationship("AssetReservationOrm", foreign_keys="AssetReservationOrm.asset_instance_accession_id")

# In MachineOrm:
# asset_reservations = relationship("AssetReservationOrm", foreign_keys="AssetReservationOrm.machine_accession_id")
