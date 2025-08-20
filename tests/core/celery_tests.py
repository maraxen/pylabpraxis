"""Unit tests for the Celery application factory."""

from celery import Celery

from praxis.backend.core.celery import celery_app


def test_celery_app_instance() -> None:
  """Test that the celery_app is a correctly configured Celery instance."""
  # Assert: Check that the app is an instance of Celery
  assert isinstance(celery_app, Celery)

  # Assert: Check key configuration values
  assert celery_app.main == "praxis_protocol_execution"
  assert "redis://localhost:6379/0" in celery_app.conf.broker_url
  assert "redis://localhost:6379/0" in celery_app.conf.result_backend

  # Assert: Check important performance and reliability settings
  assert celery_app.conf.task_serializer == "json"
  assert celery_app.conf.worker_prefetch_multiplier == 1
  assert celery_app.conf.task_acks_late is True

  # Assert: Ensure the task module is included for discovery
  assert "praxis.backend.core.celery_tasks" in celery_app.conf.include
