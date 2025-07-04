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

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from . import AssetOrm, ProtocolRunOrm
from sqlalchemy import (
  UUID,
  Column,
  Computed,
  DateTime,
  Float,
  ForeignKey,
  Integer,
  Select,
  String,
  Table,
  Text,
  event,
  func,
  select,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from praxis.backend.models.enums.asset import AssetReservationStatusEnum, AssetType
from praxis.backend.models.enums.schedule import ScheduleHistoryEventEnum, ScheduleStatusEnum
from praxis.backend.utils.db import Base, CreateMaterializedView, DropMaterializedView


class ScheduleEntryOrm(Base):
  """SQLAlchemy ORM model for tracking scheduled protocol runs.

  This model represents a protocol run that has been scheduled for execution,
  including its priority, asset requirements, and current status.
  """

  __tablename__ = "schedule_entries"

  protocol_run_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("protocol_runs.accession_id"),
    nullable=False,
    unique=True,
    index=True,
    init=False,
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
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False,
    init=False,
  )
  asset_analysis_completed_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="Timestamp when asset analysis was completed for this schedule entry.",
    init=False,
  )
  assets_reserved_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    init=False,
  )
  execution_started_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="Timestamp when the protocol run execution started.",
    init=False,
  )
  execution_completed_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="Timestamp when the protocol run execution completed.",
    init=False,
  )

  # Asset requirements and analysis
  required_asset_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  asset_requirements_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
    comment="JSONB representation of asset requirements for the protocol run.",
  )
  estimated_duration_ms: Mapped[int | None] = mapped_column(
    Integer,
    nullable=True,
    comment="Estimated duration of the protocol run in milliseconds.",
    default=None,
  )

  # Celery integration
  celery_task_id: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    index=True,
    comment="Celery task ID for the protocol run execution.",
    default=None,
  )
  celery_queue_name: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    index=True,
    comment="Celery queue name for the protocol run execution.",
    default=None,
  )

  # Status tracking
  retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
  last_error_message: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    comment="Last error message encountered during execution.",
    default=None,
  )

  # Metadata
  user_params_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="User-defined parameters for the protocol run, if any.",
    default=None,
  )
  initial_state_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="Initial state of the protocol run, if applicable.",
    default=None,
  )

  # Timestamps
  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    nullable=False,
  )
  updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now(),
    onupdate=func.now(),
    nullable=False,
  )

  # Relationships
  protocol_run: Mapped["ProtocolRunOrm"] = relationship(
    "ProtocolRunOrm",
    back_populates="schedule_entries",
    uselist=False,
    init=False,
  )
  asset_reservations: Mapped[list["AssetReservationOrm"]] = relationship(
    "AssetReservationOrm",
    back_populates="schedule_entry",
    cascade="all, delete-orphan",
    default_factory=list,
  )
  schedule_history: Mapped[list["ScheduleHistoryOrm"]] = relationship(
    "ScheduleHistoryOrm",
    back_populates="schedule_entry",
    cascade="all, delete-orphan",
    default_factory=list,
  )


class AssetReservationOrm(Base):
  """SQLAlchemy ORM model for tracking asset reservations.

  This model tracks individual asset reservations for scheduled protocol runs,
  working in conjunction with Redis for distributed locking.
  """

  __tablename__ = "asset_reservations"

  schedule_entry_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("schedule_entries.accession_id"),
    nullable=False,
    index=True,
    comment="Foreign key to the schedule entry this reservation belongs to.",
    init=False,
  )

  # Asset identification
  asset_type: Mapped[AssetType] = mapped_column(
    SAEnum(AssetType, name="asset_type_enum"),
    nullable=False,
    index=True,
    comment="Type of asset being reserved, e.g., machine, asset, deck.",
    default=AssetType.ASSET,
  )

  asset_instance_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("assets.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the specific asset instance being reserved, if applicable.",
    init=False,
  )
  asset_instance: Mapped["AssetOrm"] = relationship(
    "Asset",
    back_populates="asset_reservations",
    foreign_keys="AssetReservationOrm.asset_instance_accession_id",
    uselist=False,
    init=False,
  )
  asset_name: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="Name of the asset being reserved.",
    init=False,
  )
  status: Mapped[AssetReservationStatusEnum] = mapped_column(
    SAEnum(AssetReservationStatusEnum, name="asset_reservation_status_enum"),
    default=AssetReservationStatusEnum.PENDING,
    nullable=False,
    index=True,
  )

  # Redis lock information
  redis_lock_key: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="Redis lock key for the asset reservation.",
    init=False,
  )
  redis_lock_value: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
    comment="Value of the Redis lock, if applicable.",
    init=False,
  )
  lock_timeout_seconds: Mapped[int] = mapped_column(
    Integer,
    default=3600,
    nullable=False,
    comment="Timeout for the Redis lock in seconds.",
    init=False,
  )

  # Timing
  reserved_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="Timestamp when the asset was reserved.",
    init=False,
  )
  released_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="Timestamp when the asset reservation was released.",
    init=False,
  )
  expires_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="Timestamp when the asset reservation expires.",
    init=False,
  )

  # Reservation metadata
  required_capabilities_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="JSONB representation of required capabilities for the asset reservation.",
    default=None,
  )
  estimated_usage_duration_ms: Mapped[int | None] = mapped_column(
    Integer,
    nullable=True,
    comment="Estimated usage duration for the asset reservation in milliseconds.",
    default=None,
  )

  # Relationships
  schedule_entry: Mapped["ScheduleEntryOrm"] = relationship(
    "ScheduleEntryOrm",
    back_populates="asset_reservations",
    uselist=False,
    init=False,
  )


class ScheduleHistoryOrm(Base):
  """SQLAlchemy ORM model for tracking schedule status changes and events.

  This model provides an audit trail of all scheduling events for analytics
  and debugging purposes.
  """

  __tablename__ = "schedule_history"

  schedule_entry_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("schedule_entries.accession_id"),
    nullable=False,
    index=True,
    comment="Foreign key to the schedule entry this history record belongs to.",
    init=False,
  )

  # Event details
  event_type: Mapped[ScheduleHistoryEventEnum] = mapped_column(
    SAEnum(ScheduleHistoryEventEnum, name="schedule_history_event_enum"),
    nullable=False,
    index=True,
    comment="Type of event being recorded in the schedule history.",
    default=ScheduleHistoryEventEnum.UNKNOWN,
  )
  from_status: Mapped[ScheduleStatusEnum | None] = mapped_column(
    SAEnum(ScheduleStatusEnum, name="schedule_status_enum"),
    nullable=True,
    comment="Previous status of the schedule entry before this event.",
    default=None,
  )
  to_status: Mapped[ScheduleStatusEnum | None] = mapped_column(
    SAEnum(ScheduleStatusEnum, name="schedule_status_enum"),
    nullable=True,
    comment="New status of the schedule entry after this event.",
    default=None,
  )

  # Event data
  event_data_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
    comment="Additional event data.",
  )
  message: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    comment="Human-readable message describing the event.",
    default=None,
  )
  error_details: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    comment="Details of any error that occurred during the event.",
    default=None,
  )

  # Performance metrics
  event_start: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="Timestamp when the event started.",
    server_default=func.now(),
    init=False,
  )
  event_end: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="Timestamp when the event ended.",
    default=None,
  )
  completed_duration_ms: Mapped[int | None] = mapped_column(
    Integer,
    Computed(
      "(EXTRACT(EPOCH FROM (event_end - event_start)) * 1000)",
      persisted=True,
    ),
    comment="Stored duration in milliseconds, computed by the DB when a run completes.",
    nullable=True,
    init=False,
  )
  current_duration_ms: Mapped[int | None] = mapped_column(
    Integer,
    Computed(
      """CASE
              WHEN start_time IS NULL THEN NULL
              WHEN end_time IS NOT NULL THEN (EXTRACT(EPOCH FROM (end_time - start_time)) * 1000)
              ELSE (EXTRACT(EPOCH FROM (NOW() - start_time)) * 1000)
           END
        """,
      persisted=False,  # This column is VIRTUAL
    ),
    comment="Virtual duration in ms. For ongoing runs, it's calculated on-the-fly against the"
        "current time.",
    nullable=True,
    init=False,
  )
  asset_count: Mapped[int | None] = mapped_column(
    Integer,
    nullable=True,
    default=None,
    comment="Number of assets involved in the event.",
  )

  # Relationships
  schedule_entry: Mapped["ScheduleEntryOrm"] = relationship(
    "ScheduleEntryOrm",
    back_populates="schedule_history",
    uselist=False,
    init=False,
    foreign_keys=[schedule_entry_accession_id],
    comment="Back-reference to the schedule entry this history record belongs to.",
  )


metrics_query: Select = select(
  func.date_trunc("hour", ScheduleEntryOrm.created_at).label("metric_timestamp"),
  func.count(ScheduleEntryOrm.accession_id).label("protocols_scheduled"),
  func.count()
  .filter(ScheduleEntryOrm.status == ScheduleStatusEnum.COMPLETED)
  .label("protocols_completed"),
  func.count()
  .filter(ScheduleEntryOrm.status == ScheduleStatusEnum.FAILED)
  .label("protocols_failed"),
  func.count()
  .filter(ScheduleEntryOrm.status == ScheduleStatusEnum.CANCELLED)
  .label("protocols_cancelled"),
  (
    func.avg(
      func.extract("epoch", ScheduleEntryOrm.execution_started_at - ScheduleEntryOrm.scheduled_at),
    )
    * 1000
  ).label("avg_queue_wait_time_ms"),
  (
    func.avg(
      func.extract(
        "epoch",
        ScheduleEntryOrm.execution_completed_at - ScheduleEntryOrm.execution_started_at,
      ),
    )
    * 1000
  ).label("avg_execution_time_ms"),
).group_by(func.date_trunc("hour", ScheduleEntryOrm.created_at))


scheduler_metrics_mv = Table(
  "scheduler_metrics_mv",
  Base.metadata,
  Column("metric_timestamp", DateTime(timezone=True), primary_key=True),
  Column("protocols_scheduled", Integer),
  Column("protocols_completed", Integer),
  Column("protocols_failed", Integer),
  Column("protocols_cancelled", Integer),
  Column("avg_queue_wait_time_ms", Float),
  Column("avg_execution_time_ms", Float),
)

event.listen(
  Base.metadata,
  "after_create",
  CreateMaterializedView("scheduler_metrics_mv", metrics_query),
)
event.listen(Base.metadata, "before_drop", DropMaterializedView("scheduler_metrics_mv"))


class SchedulerMetricsView(Base):
  """Read-only ORM class mapped to the scheduler_metrics_mv materialized view."""

  __table__ = scheduler_metrics_mv
  __tablename__ = "scheduler_metrics_mv"
