"""Tests for core/decorators/protocol_decorator.py."""

import contextvars
from unittest.mock import Mock

import pytest
from praxis.backend.core.decorators import (
    ProtocolRuntimeInfo,
    _prepare_function_arguments,
    protocol_function,
)
from praxis.backend.core.run_context import PraxisRunContext
from praxis.backend.models.pydantic_internals.protocol import (
    FunctionProtocolDefinitionCreate,
)
from praxis.backend.utils.uuid import uuid7


class TestPrepareFunctionArguments:
    """Tests for _prepare_function_arguments function."""

    @pytest.mark.asyncio
    async def test_prepare_function_arguments_basic(self) -> None:
        """Test preparing basic function arguments."""

        def test_func(volume: int):
            pass

        mock_context = Mock(spec=PraxisRunContext)
        mock_context.run_accession_id = uuid7()

        kwargs = {"volume": 100}

        result = await _prepare_function_arguments(
            test_func,
            kwargs,
            mock_context,
            None,
            "state",
        )

        assert result == {"volume": 100}

    @pytest.mark.asyncio
    async def test_prepare_function_arguments_with_praxis_run_context_param(self) -> None:
        """Test preparing arguments with __praxis_run_context__ parameter."""

        def test_func(__praxis_run_context__: PraxisRunContext, volume: int):
            pass

        mock_context = Mock(spec=PraxisRunContext)
        mock_context.run_accession_id = uuid7()

        kwargs = {"volume": 100}

        result = await _prepare_function_arguments(
            test_func,
            kwargs,
            mock_context,
            None,
            "state",
        )

        assert result["volume"] == 100
        assert result["__praxis_run_context__"] == mock_context

    @pytest.mark.asyncio
    async def test_prepare_function_arguments_with_state_param(self) -> None:
        """Test preparing arguments with state parameter."""

        def test_func(state: PraxisRunContext, volume: int):
            pass

        mock_context = Mock(spec=PraxisRunContext)
        mock_context.run_accession_id = uuid7()

        state_details = {
            "name": "state",
            "expects_praxis_state": True,
            "expects_dict": False,
        }

        kwargs = {"volume": 100}

        result = await _prepare_function_arguments(
            test_func,
            kwargs,
            mock_context,
            state_details,
            "state",
        )

        assert result["volume"] == 100
        assert result["state"] == mock_context


class TestProtocolFunctionDecorator:
    """Tests for protocol_function decorator."""

    def test_protocol_function_basic_decoration(self) -> None:
        """Test basic protocol function decoration."""

        @protocol_function(name="test_protocol", version="1.0")
        def my_protocol():
            pass

        assert hasattr(my_protocol, "_protocol_definition")
        assert hasattr(my_protocol, "_protocol_runtime_info")
        assert isinstance(my_protocol._protocol_definition, FunctionProtocolDefinitionCreate)
        assert my_protocol._protocol_definition.name == "test_protocol"
        assert my_protocol._protocol_definition.version == "1.0"

    def test_protocol_function_with_description(self) -> None:
        """Test protocol function with description."""

        @protocol_function(description="This is a test protocol")
        def my_protocol():
            pass

        assert my_protocol._protocol_definition.description == "This is a test protocol"

    def test_protocol_function_uses_function_name_if_not_provided(self) -> None:
        """Test that decorator uses function name if name not provided."""

        @protocol_function()
        def my_custom_protocol():
            pass

        assert my_custom_protocol._protocol_definition.name == "my_custom_protocol"

    def test_protocol_function_with_tags_and_category(self) -> None:
        """Test protocol function with tags and category."""

        @protocol_function(category="testing", tags=["unit", "test"])
        def my_protocol():
            pass

        assert my_protocol._protocol_definition.category == "testing"
        assert my_protocol._protocol_definition.tags == ["unit", "test"]

    def test_protocol_function_with_parameters(self) -> None:
        """Test protocol function with parameters."""

        @protocol_function(
            param_metadata={
                "volume": {"description": "Volume in microliters"},
            }
        )
        def my_protocol(volume: int):
            pass

        assert len(my_protocol._protocol_definition.parameters) == 1
        assert my_protocol._protocol_definition.parameters[0].name == "volume"
        assert my_protocol._protocol_definition.parameters[0].description == "Volume in microliters"

    def test_protocol_function_solo_execution(self) -> None:
        """Test protocol function with solo execution flag."""

        @protocol_function(solo=True)
        def my_protocol():
            pass

        assert my_protocol._protocol_definition.solo_execution is True


class TestProtocolFunctionDecoratorErrors:
    """Tests for protocol_function decorator error cases."""

    def test_protocol_function_top_level_without_state_raises_error(self) -> None:
        """Test that top-level protocol without state raises error."""
        with pytest.raises(TypeError, match="must define a 'state' parameter"):

            @protocol_function(is_top_level=True)
            def my_protocol():
                pass

    def test_protocol_function_invalid_top_level_name_raises_error(self) -> None:
        """Test that invalid top-level name raises error."""
        with pytest.raises(ValueError, match="does not match format"):

            @protocol_function(name="invalid name!", is_top_level=True)
            def my_protocol(state: dict):
                pass

    def test_protocol_function_preconfigure_deck_without_deck_param_raises_error(self) -> None:
        """Test that preconfigure_deck without deck param raises error."""
        with pytest.raises(TypeError, match="missing 'deck' param"):

            @protocol_function(preconfigure_deck=True)
            def my_protocol():
                pass


class TestDecoratorIntegration:
    """Integration tests for decorator functionality."""

    def test_decorated_function_retains_original_attributes(self) -> None:
        """Test that decorated function retains original attributes."""

        @protocol_function()
        def my_protocol():
            """My protocol docstring."""
            pass

        # Should retain name and docstring
        assert my_protocol.__name__ == "my_protocol"
        assert "My protocol docstring" in my_protocol.__doc__

    def test_decorated_function_has_runtime_info(self) -> None:
        """Test that decorated function has runtime info."""

        @protocol_function()
        def my_protocol():
            pass

        assert hasattr(my_protocol, "_protocol_runtime_info")
        runtime_info = my_protocol._protocol_runtime_info
        assert isinstance(runtime_info, ProtocolRuntimeInfo)
        assert runtime_info.function_ref == my_protocol.__wrapped__

    def test_multiple_decorations_work_independently(self) -> None:
        """Test that multiple functions can be decorated independently."""

        @protocol_function(name="protocol_one", version="1.0")
        def protocol_one():
            pass

        @protocol_function(name="protocol_two", version="2.0")
        def protocol_two():
            pass

        assert protocol_one._protocol_definition.name == "protocol_one"
        assert protocol_two._protocol_definition.name == "protocol_two"
        assert protocol_one._protocol_definition.version == "1.0"
        assert protocol_two._protocol_definition.version == "2.0"


class TestDecoratorsPackageStructure:
    """Tests for module structure and exports."""

    def test_module_exports_protocol_function(self) -> None:
        """Test that module exports protocol_function."""
        from praxis.backend.core import decorators

        assert hasattr(decorators, "protocol_function")

    def test_module_exports_create_protocol_definition_data(self) -> None:
        """Test that module exports CreateProtocolDefinitionData."""
        from praxis.backend.core import decorators

        assert hasattr(decorators, "CreateProtocolDefinitionData")

    def test_module_exports_protocol_runtime_info(self) -> None:
        """Test that module exports ProtocolRuntimeInfo."""
        from praxis.backend.core import decorators

        assert hasattr(decorators, "ProtocolRuntimeInfo")

    def test_module_has_logger(self) -> None:
        """Test that module defines logger."""
        from praxis.backend.core import decorators

        assert hasattr(decorators, "logger")

    def test_module_defines_constants(self) -> None:
        """Test that module defines expected constants."""
        from praxis.backend.core import decorators

        assert hasattr(decorators, "DEFAULT_DECK_PARAM_NAME")
        assert decorators.DEFAULT_DECK_PARAM_NAME == "deck"
        assert hasattr(decorators, "DEFAULT_STATE_PARAM_NAME")
        assert decorators.DEFAULT_STATE_PARAM_NAME == "state"
        assert hasattr(decorators, "TOP_LEVEL_NAME_REGEX")
