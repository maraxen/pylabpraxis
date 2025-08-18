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
from praxis.backend.models.enums.schedule import (
  ScheduleHistoryEventEnum,
  ScheduleHistoryEventTriggerEnum,
  ScheduleStatusEnum,
)
from praxis.backend.utils.db import Base, CreateMaterializedView, DropMaterializedView
from praxis.backend.utils.uuid import uuid7


class ScheduleEntryOrm(Base):

  """SQLAlchemy ORM model for tracking scheduled protocol runs.

  This model represents a protocol run that has been scheduled for execution,
  including its priority, asset requirements, and current status.
  """

  __tablename__ = "schedule_entries"
  __table_args__ = ({'extend_existing': True},)

  protocol_run_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("protocol_runs.accession_id"),
    nullable=False,
    unique=True,
    index=True,
    default_factory=uuid7,
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
    kw_only=True,
  )
  asset_analysis_completed_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    kw_only=True,
  )
  assets_reserved_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    kw_only=True,
  )
  execution_started_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    kw_only=True,
  )
  execution_completed_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    kw_only=True,
  )

  # Asset requirements and analysis
  required_asset_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  asset_requirements_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )
  estimated_duration_ms: Mapped[int | None] = mapped_column(
    Integer,
    nullable=True,
    default=None,
  )

  # Celery integration
  celery_task_id: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    index=True,
    default=None,
  )
  celery_queue_name: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    index=True,
    default=None,
  )

  # Status tracking
  retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
  max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
  last_error_message: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    default=None,
  )

  # Metadata
  user_params_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )
  initial_state_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )

  # Relationships
  protocol_run: Mapped["ProtocolRunOrm"] = relationship(
    "ProtocolRunOrm",
    back_populates="schedule_entries",
    uselist=False,
    kw_only=True,
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
  __table_args__ = ({'extend_existing': True},)

  protocol_run_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("protocol_runs.accession_id"),
    nullable=False,
    unique=True,
    index=True,
    kw_only=True,
  )

  protocol_run: Mapped["ProtocolRunOrm"] = relationship(
    "ProtocolRunOrm",
    back_populates="asset_reservations",
    uselist=False,
    init=False,
    foreign_keys=[protocol_run_accession_id],
  )

  schedule_entry_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("schedule_entries.accession_id"),
    nullable=False,
    index=True,
    kw_only=True,
  )

  # Asset identification
  asset_type: Mapped[AssetType] = mapped_column(
    SAEnum(AssetType, name="asset_type_enum"),
    nullable=False,
    index=True,
    default=AssetType.ASSET,
  )

  asset_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("assets.accession_id"),
    nullable=True,
    index=True,
    kw_only=True,
  )
  asset: Mapped["AssetOrm"] = relationship(
    "Asset",
    back_populates="asset_reservations",
    foreign_keys=[asset_accession_id],
    uselist=False,
    init=False,
  )
  asset_name: Mapped[str] = mapped_column(
    String,
    ForeignKey("assets.name"),
    nullable=False,
    index=True,
    kw_only=True,
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
    kw_only=True,
  )
  redis_lock_value: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
  )
  lock_timeout_seconds: Mapped[int] = mapped_column(
    Integer,
    default=3600,
    nullable=False,
    kw_only=True,
  )

  # Timing
  reserved_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    server_default=func.now(),
    init=False,
  )
  released_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    kw_only=True,
  )
  expires_at: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    default=None,
  )

  # Reservation metadata
  required_capabilities_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )
  estimated_usage_duration_ms: Mapped[int | None] = mapped_column(
    Integer,
    nullable=True,
    default=None,
  )

  # Relationships
  schedule_entry: Mapped["ScheduleEntryOrm"] = relationship(
    "ScheduleEntryOrm",
    back_populates="asset_reservations",
    uselist=False,
    init=False,
    foreign_keys=[schedule_entry_accession_id],
  )


class ScheduleHistoryOrm(Base):

  """SQLAlchemy ORM model for tracking schedule status changes and events.

  This model provides an audit trail of all scheduling events for analytics
  and debugging purposes.
  """

  __tablename__ = "schedule_history"
  __table_args__ = ({'extend_existing': True},)

  schedule_entry_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("schedule_entries.accession_id"),
    nullable=False,
    index=True,
    kw_only=True,
  )

  schedule_entry: Mapped["ScheduleEntryOrm"] = relationship(
    "ScheduleEntryOrm",
    back_populates="schedule_history",
    uselist=False,
    init=False,
    foreign_keys=[schedule_entry_accession_id],
  )

  # Event details
  event_type: Mapped[ScheduleHistoryEventEnum] = mapped_column(
    SAEnum(ScheduleHistoryEventEnum, name="schedule_history_event_enum"),
    nullable=False,
    index=True,
    kw_only=True,
  )
  from_status: Mapped[ScheduleStatusEnum | None] = mapped_column(
    SAEnum(ScheduleStatusEnum, name="schedule_status_enum"),
    nullable=True,
    default=None,
  )
  to_status: Mapped[ScheduleStatusEnum | None] = mapped_column(
    SAEnum(ScheduleStatusEnum, name="schedule_status_enum"),
    nullable=True,
    default=None,
  )

  # Event data
  event_data_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )
  message: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    default=None,
  )
  error_details: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    default=None,
  )

  # Performance metrics
  event_start: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    server_default=func.now(),
    init=False,
  )
  event_end: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    default=None,
  )
  completed_duration_ms: Mapped[int | None] = mapped_column(
    Integer,
    Computed(
      "(EXTRACT(EPOCH FROM (event_end - event_start)) * 1000)",
      persisted=True,
    ),
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
    nullable=True,
    init=False,
  )
  override_duration_ms: Mapped[int | None] = mapped_column(
    Integer,
    nullable=True,
    default=None,
    kw_only=True,
  )
  asset_count: Mapped[int | None] = mapped_column(
    Integer,
    nullable=True,
    default=None,
  )

  # Relationships

  triggered_by: Mapped[ScheduleHistoryEventTriggerEnum] = mapped_column(
    String,
    nullable=False,
    default=ScheduleHistoryEventTriggerEnum.SYSTEM,
    kw_only=True,
  )


# metrics_query: Select = select(
#   func.date_trunc("hour", ScheduleEntryOrm.created_at).label("metric_timestamp"),
#   func.count(ScheduleEntryOrm.accession_id).label("protocols_scheduled"),
#   func.count()
#   .filter(ScheduleEntryOrm.status == ScheduleStatusEnum.COMPLETED)
#   .label("protocols_completed"),
#   func.count()
#   .filter(ScheduleEntryOrm.status == ScheduleStatusEnum.FAILED)
#   .label("protocols_failed"),
#   func.count()
#   .filter(ScheduleEntryOrm.status == ScheduleStatusEnum.CANCELLED)
#   .label("protocols_cancelled"),
#   (
#     func.avg(
#       func.extract("epoch", ScheduleEntryOrm.execution_started_at - ScheduleEntryOrm.scheduled_at),
#     )
#     * 1000
#   ).label("avg_queue_wait_time_ms"),
#   (
#     func.avg(
#       func.extract(
#         "epoch",
#         ScheduleEntryOrm.execution_completed_at - ScheduleEntryOrm.execution_started_at,
#       ),
#     )
#     * 1000
#   ).label("avg_execution_time_ms"),
# ).group_by(func.date_trunc("hour", ScheduleEntryOrm.created_at))


# scheduler_metrics_mv = Table(
#   "scheduler_metrics_mv",
#   Base.metadata,
#   Column("metric_timestamp", DateTime(timezone=True), primary_key=True),
#   Column("protocols_scheduled", Integer),
#   Column("protocols_completed", Integer),
#   Column("protocols_failed", Integer),
#   Column("protocols_cancelled", Integer),
#   Column("avg_queue_wait_time_ms", Float),
#   Column("avg_execution_time_ms", Float),
#   extend_existing=True,
# )

# event.listen(
#   Base.metadata,
#   "after_create",
#   CreateMaterializedView("scheduler_metrics_mv", metrics_query),
# )
# event.listen(Base.metadata, "before_drop", DropMaterializedView("scheduler_metrics_mv"))


# class SchedulerMetricsView(Base):

#   """Read-only ORM class mapped to the scheduler_metrics_mv materialized view."""

#   __table__ = scheduler_metrics_mv
