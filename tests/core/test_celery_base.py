"""Tests for core/celery_base.py."""

from unittest.mock import Mock

from celery import Task

from praxis.backend.core.celery_base import PraxisTask


class TestPraxisTask:

    """Tests for PraxisTask class."""

    def test_praxis_task_inherits_from_task(self) -> None:
        """Test that PraxisTask inherits from Celery Task."""
        assert issubclass(PraxisTask, Task)

    def test_praxis_task_has_container_property(self) -> None:
        """Test that PraxisTask has container property."""
        assert hasattr(PraxisTask, "container")
        # Verify it's a property
        assert isinstance(PraxisTask.container, property)

    def test_praxis_task_has_call_method(self) -> None:
        """Test that PraxisTask has __call__ method."""
        assert callable(PraxisTask)
        assert callable(PraxisTask.__call__)

    def test_container_property_definition(self) -> None:
        """Test that container property is properly defined."""
        # The property should be defined at the class level
        assert "container" in PraxisTask.__dict__
        prop = PraxisTask.__dict__["container"]
        assert isinstance(prop, property)
        # Should have a getter
        assert prop.fget is not None


class TestPraxisTaskContainerProperty:

    """Tests for PraxisTask.container property."""

    def test_container_property_accesses_app_container(self) -> None:
        """Test that container property accesses app.container."""
        # We can't easily instantiate PraxisTask due to Celery metaclass complexity
        # Instead, test that the property getter would access app.container
        container_getter = PraxisTask.container.fget

        # Create a mock object with an app attribute
        mock_self = Mock()
        mock_container = Mock()
        mock_self.app = Mock()
        mock_self.app.container = mock_container

        # Call the getter with our mock
        result = container_getter(mock_self)
        assert result is mock_container

    def test_container_property_returns_container_from_app(self) -> None:
        """Test that container property returns the container from app."""
        container_getter = PraxisTask.container.fget

        mock_self = Mock()
        expected_container = {"test": "container"}
        mock_self.app = Mock()
        mock_self.app.container = expected_container

        result = container_getter(mock_self)
        assert result == expected_container


class TestPraxisTaskCall:

    """Tests for PraxisTask.__call__() method."""

    def test_call_method_exists(self) -> None:
        """Test that __call__ method is defined."""
        assert "__call__" in PraxisTask.__dict__
        assert callable(PraxisTask.__call__)

    def test_call_method_accepts_args_and_kwargs(self) -> None:
        """Test that __call__ method signature accepts args and kwargs."""
        import inspect

        sig = inspect.signature(PraxisTask.__call__)
        params = list(sig.parameters.keys())

        # Should accept self, args, and kwargs
        assert "self" in params
        assert "args" in params or any("*" in str(p) for p in sig.parameters.values())
        assert "kwargs" in params or any("**" in str(p) for p in sig.parameters.values())


class TestPraxisTaskIntegration:

    """Integration tests for PraxisTask."""

    def test_praxis_task_class_structure(self) -> None:
        """Test that PraxisTask has correct class structure."""
        # Verify class hierarchy
        assert PraxisTask.__bases__[0] is Task

        # Verify it has the container property
        assert hasattr(PraxisTask, "container")

        # Verify it overrides __call__
        assert "__call__" in PraxisTask.__dict__

    def test_praxis_task_inherits_task_attributes(self) -> None:
        """Test that PraxisTask inherits Task attributes."""
        # Check that it has access to Task class attributes
        assert hasattr(Task, "app")
        assert hasattr(Task, "name")

        # PraxisTask should have these too (inherited)
        # Note: We can't instantiate to check instances due to metaclass complexity
        assert PraxisTask.__mro__[1] is Task

    def test_call_method_uses_context_manager(self) -> None:
        """Test that __call__ implementation uses context manager pattern."""
        import inspect

        # Get the source code of the __call__ method
        source = inspect.getsource(PraxisTask.__call__)

        # Verify it uses 'with' statement (context manager pattern)
        assert "with" in source
        assert "container" in source
        assert "db_session" in source
        assert "override" in source

    def test_call_method_calls_super(self) -> None:
        """Test that __call__ implementation calls super().__call__."""
        import inspect

        source = inspect.getsource(PraxisTask.__call__)

        # Verify it calls the parent class __call__
        assert "super().__call__" in source


class TestPraxisTaskDocumentation:

    """Tests for PraxisTask documentation and structure."""

    def test_praxis_task_has_docstring(self) -> None:
        """Test that PraxisTask class has a docstring."""
        assert PraxisTask.__doc__ is not None
        assert len(PraxisTask.__doc__) > 0

    def test_container_property_has_docstring(self) -> None:
        """Test that container property has a docstring."""
        prop = PraxisTask.__dict__["container"]
        assert prop.fget.__doc__ is not None
        assert "container" in prop.fget.__doc__.lower()

    def test_call_method_has_docstring(self) -> None:
        """Test that __call__ method has a docstring."""
        call_method = PraxisTask.__call__
        assert call_method.__doc__ is not None
        assert len(call_method.__doc__) > 0
