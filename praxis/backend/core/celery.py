"""Celery application factory.

This module provides a global Celery application instance for use by
decorators, and a configuration function to be called at application startup.
"""
from celery import Celery

# Global, unconfigured Celery app instance for decorators
celery_app = Celery("praxis_protocol_execution")


def configure_celery_app(app: Celery, broker_url: str, backend_url: str) -> None:
    """Configure the Celery application instance."""
    app.conf.update(
        broker=broker_url,
        backend=backend_url,
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=3600,
        task_soft_time_limit=3300,
        worker_prefetch_multiplier=1,
        task_acks_late=True,
        worker_disable_rate_limits=True,
        include=["praxis.backend.core.celery_tasks"],
    )
