"""Tests for core/celery.py."""

import json
import uuid
from typing import Any

import pytest
from celery import Celery
from kombu.serialization import registry
from pydantic import BaseModel

from praxis.backend.core.celery import celery_app, configure_celery_app


class TestCeleryApp:

    """Tests for the global celery_app instance."""

    def test_celery_app_exists(self) -> None:
        """Test that celery_app is defined."""
        assert celery_app is not None

    def test_celery_app_is_celery_instance(self) -> None:
        """Test that celery_app is a Celery instance."""
        assert isinstance(celery_app, Celery)

    def test_celery_app_has_correct_name(self) -> None:
        """Test that celery_app has the correct application name."""
        assert celery_app.main == "praxis_protocol_execution"


class TestConfigureCeleryApp:

    """Tests for configure_celery_app function."""

    def test_configure_celery_app_sets_broker(self) -> None:
        """Test that configure_celery_app sets broker URL."""
        app = Celery("test_app")
        broker_url = "redis://localhost:6379/0"
        backend_url = "redis://localhost:6379/1"

        configure_celery_app(app, broker_url, backend_url)

        assert app.conf.broker == broker_url

    def test_configure_celery_app_sets_backend(self) -> None:
        """Test that configure_celery_app sets backend URL."""
        app = Celery("test_app")
        broker_url = "redis://localhost:6379/0"
        backend_url = "redis://localhost:6379/1"

        configure_celery_app(app, broker_url, backend_url)

        assert app.conf.backend == backend_url

    def test_configure_celery_app_sets_task_serializer(self) -> None:
        """Test that configure_celery_app sets task serializer to json."""
        app = Celery("test_app")
        broker_url = "redis://localhost:6379/0"
        backend_url = "redis://localhost:6379/1"

        configure_celery_app(app, broker_url, backend_url)

        assert app.conf.task_serializer == "json"

    def test_configure_celery_app_sets_accept_content(self) -> None:
        """Test that configure_celery_app sets accept_content to json."""
        app = Celery("test_app")
        broker_url = "redis://localhost:6379/0"
        backend_url = "redis://localhost:6379/1"

        configure_celery_app(app, broker_url, backend_url)

        assert app.conf.accept_content == ["json"]

    def test_configure_celery_app_sets_result_serializer(self) -> None:
        """Test that configure_celery_app sets result serializer to json."""
        app = Celery("test_app")
        broker_url = "redis://localhost:6379/0"
        backend_url = "redis://localhost:6379/1"

        configure_celery_app(app, broker_url, backend_url)

        assert app.conf.result_serializer == "json"

    def test_configure_celery_app_sets_timezone(self) -> None:
        """Test that configure_celery_app sets timezone to UTC."""
        app = Celery("test_app")
        broker_url = "redis://localhost:6379/0"
        backend_url = "redis://localhost:6379/1"

        configure_celery_app(app, broker_url, backend_url)

        assert app.conf.timezone == "UTC"

    def test_configure_celery_app_enables_utc(self) -> None:
        """Test that configure_celery_app enables UTC."""
        app = Celery("test_app")
        broker_url = "redis://localhost:6379/0"
        backend_url = "redis://localhost:6379/1"

        configure_celery_app(app, broker_url, backend_url)

        assert app.conf.enable_utc is True

    def test_configure_celery_app_enables_task_track_started(self) -> None:
        """Test that configure_celery_app enables task_track_started."""
        app = Celery("test_app")
        broker_url = "redis://localhost:6379/0"
        backend_url = "redis://localhost:6379/1"

        configure_celery_app(app, broker_url, backend_url)

        assert app.conf.task_track_started is True

    def test_configure_celery_app_sets_task_time_limit(self) -> None:
        """Test that configure_celery_app sets task_time_limit."""
        app = Celery("test_app")
        broker_url = "redis://localhost:6379/0"
        backend_url = "redis://localhost:6379/1"

        configure_celery_app(app, broker_url, backend_url)

        assert app.conf.task_time_limit == 3600

    def test_configure_celery_app_sets_task_soft_time_limit(self) -> None:
        """Test that configure_celery_app sets task_soft_time_limit."""
        app = Celery("test_app")
        broker_url = "redis://localhost:6379/0"
        backend_url = "redis://localhost:6379/1"

        configure_celery_app(app, broker_url, backend_url)

        assert app.conf.task_soft_time_limit == 3300

    def test_configure_celery_app_sets_worker_prefetch_multiplier(self) -> None:
        """Test that configure_celery_app sets worker_prefetch_multiplier."""
        app = Celery("test_app")
        broker_url = "redis://localhost:6379/0"
        backend_url = "redis://localhost:6379/1"

        configure_celery_app(app, broker_url, backend_url)

        assert app.conf.worker_prefetch_multiplier == 1

    def test_configure_celery_app_enables_task_acks_late(self) -> None:
        """Test that configure_celery_app enables task_acks_late."""
        app = Celery("test_app")
        broker_url = "redis://localhost:6379/0"
        backend_url = "redis://localhost:6379/1"

        configure_celery_app(app, broker_url, backend_url)

        assert app.conf.task_acks_late is True

    def test_configure_celery_app_disables_worker_rate_limits(self) -> None:
        """Test that configure_celery_app disables worker rate limits."""
        app = Celery("test_app")
        broker_url = "redis://localhost:6379/0"
        backend_url = "redis://localhost:6379/1"

        configure_celery_app(app, broker_url, backend_url)

        assert app.conf.worker_disable_rate_limits is True

    def test_configure_celery_app_sets_include(self) -> None:
        """Test that configure_celery_app sets include to celery_tasks."""
        app = Celery("test_app")
        broker_url = "redis://localhost:6379/0"
        backend_url = "redis://localhost:6379/1"

        configure_celery_app(app, broker_url, backend_url)

        assert app.conf.include == ["praxis.backend.core.celery_tasks"]


class TestConfigureCeleryAppIntegration:

    """Integration tests for configure_celery_app."""

    def test_configure_celery_app_with_different_urls(self) -> None:
        """Test configure_celery_app with different broker and backend URLs."""
        app = Celery("test_app")
        broker_url = "amqp://guest:guest@localhost:5672//"
        backend_url = "db+postgresql://user:pass@localhost/dbname"

        configure_celery_app(app, broker_url, backend_url)

        assert app.conf.broker == broker_url
        assert app.conf.backend == backend_url

    def test_configure_celery_app_multiple_times(self) -> None:
        """Test that configure_celery_app can be called multiple times."""
        app = Celery("test_app")

        # First configuration
        configure_celery_app(app, "redis://localhost:6379/0", "redis://localhost:6379/1")
        assert app.conf.broker == "redis://localhost:6379/0"

        # Second configuration (reconfigure)
        configure_celery_app(app, "redis://localhost:6379/2", "redis://localhost:6379/3")
        assert app.conf.broker == "redis://localhost:6379/2"
        assert app.conf.backend == "redis://localhost:6379/3"

    def test_configure_celery_app_preserves_all_settings(self) -> None:
        """Test that all settings are preserved after configuration."""
        app = Celery("test_app")
        broker_url = "redis://localhost:6379/0"
        backend_url = "redis://localhost:6379/1"

        configure_celery_app(app, broker_url, backend_url)

        # Verify all settings are configured
        expected_settings = {
            "broker": broker_url,
            "backend": backend_url,
            "task_serializer": "json",
            "accept_content": ["json"],
            "result_serializer": "json",
            "timezone": "UTC",
            "enable_utc": True,
            "task_track_started": True,
            "task_time_limit": 3600,
            "task_soft_time_limit": 3300,
            "worker_prefetch_multiplier": 1,
            "task_acks_late": True,
            "worker_disable_rate_limits": True,
            "include": ["praxis.backend.core.celery_tasks"],
        }

        for key, value in expected_settings.items():
            assert getattr(app.conf, key) == value, f"Setting {key} not configured correctly"


class TestCelerySerialization:

    """Tests for Celery task serialization."""

    def test_verify_kombu_json_serialization_handles_uuid(self) -> None:
        """Test that Kombu JSON serializer handles UUIDs correctly."""
        data = {"id": uuid.uuid4()}

        # Serialize
        content_type, content_encoding, dumps = registry.dumps(data, serializer="json")
        assert isinstance(dumps, str)

        # Deserialize
        loads = registry.loads(dumps, content_type, content_encoding)
        assert isinstance(loads["id"], uuid.UUID)
        assert loads["id"] == data["id"]

    def test_verify_kombu_serialization_fails_for_pydantic(self) -> None:
        """Test that Kombu JSON serializer fails for Pydantic models (without to_dict).

        This confirms we must convert Pydantic models to dicts before passing them to tasks.
        """
        class TestModel(BaseModel):
            foo: str

        data = TestModel(foo="bar")

        # Should raise TypeError or similar because TestModel is not JSON serializable
        with pytest.raises(Exception):
             registry.dumps(data, serializer="json")

    def test_verify_task_args_serialization(self) -> None:
        """Simulate passing args to a task to verify compatibility."""
        # Mimic execute_protocol_run_task args
        protocol_run_id = uuid.uuid4()
        input_parameters = {"param1": "value1", "param2": 100}
        initial_state = {"state1": "foo"}

        args = (protocol_run_id, input_parameters, initial_state)

        content_type, content_encoding, dumps = registry.dumps(args, serializer="json")

        loads = registry.loads(dumps, content_type, content_encoding)

        assert loads[0] == protocol_run_id
        assert loads[1] == input_parameters
        assert loads[2] == initial_state
