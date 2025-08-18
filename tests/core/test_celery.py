"""Unit tests for the Celery application factory."""

from celery import Celery

from praxis.backend.core.celery import create_celery_app


def test_celery_app_factory() -> None:
    """Test that the create_celery_app factory returns a correctly configured instance."""
    # Arrange
    broker_url = "redis://test-broker:6379/1"
    backend_url = "redis://test-backend:6379/2"

    # Act
    celery_app = create_celery_app(broker_url=broker_url, backend_url=backend_url)

    # Assert: Check that the app is an instance of Celery
    assert isinstance(celery_app, Celery)

    # Assert: Check key configuration values from the factory
    assert celery_app.main == "praxis_protocol_execution"
    assert celery_app.conf.broker_url == broker_url
    assert celery_app.conf.result_backend == backend_url

    # Assert: Check important performance and reliability settings from the update
    assert celery_app.conf.task_serializer == "json"
    assert celery_app.conf.worker_prefetch_multiplier == 1
    assert celery_app.conf.task_acks_late is True

    # Assert: Ensure the task module is included for discovery
    assert "praxis.backend.core.celery_tasks" in celery_app.conf.include
