# pylint: disable=fixme
"""Celery application factory. # broad-except is handled in celery_tasks.py.

This module provides the configured Celery application instance
for use by worker and application code.
"""
from celery import Celery

# Celery application configuration
# The 'include' argument tells Celery where to find task modules.
celery_app = Celery(
  "praxis_protocol_execution",
  broker="redis://localhost:6379/0",
  backend="redis://localhost:6379/0",
  include=["praxis.backend.core.celery_tasks"],
)

# Celery configuration
celery_app.conf.update(
  task_serializer="json",
  accept_content=["json"],
  result_serializer="json",
  timezone="UTC",
  enable_utc=True,
  task_track_started=True,
  task_time_limit=3600,  # 1 hour timeout
  task_soft_time_limit=3300,  # 55 minutes soft timeout
  worker_prefetch_multiplier=1,  # Important for long-running tasks
  task_acks_late=True,
  worker_disable_rate_limits=True,
)

# Celery beat schedule for periodic tasks (if needed)
celery_app.conf.beat_schedule = {
  # Example: Clean up old completed tasks
  # "cleanup-completed-runs": {
  #     "task": "praxis.backend.core.celery_tasks.cleanup_completed_protocol_runs",
  #     "schedule": crontab(minute=0, hour=2),  # Daily at 2 AM
  # },
}
