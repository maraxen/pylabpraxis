# pylint: disable=fixme
"""Celery application factory. # broad-except is handled in celery_tasks.py.

This module provides a factory function for creating and configuring a Celery
application instance. This approach supports dependency injection and centralized
configuration management.
"""
from celery import Celery


def create_celery_app(broker_url: str, backend_url: str) -> Celery:
    """Create and configure a Celery application instance.

    Args:
        broker_url: The URL for the Celery message broker.
        backend_url: The URL for the Celery result backend.

    Returns:
        A configured Celery application instance.

    """
    celery_app = Celery(
        "praxis_protocol_execution",
        broker=broker_url,
        backend=backend_url,
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
    celery_app.conf.beat_schedule = {}

    return celery_app
