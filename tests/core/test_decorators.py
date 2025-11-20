"""Tests for core/decorators.py."""

import contextvars
import inspect
from typing import Optional
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pylabrobot.resources import Deck, Resource

from praxis.backend.core.decorators import (
    CreateProtocolDefinitionData,
    ProtocolRuntimeInfo,
    _create_protocol_definition,
    _prepare_function_arguments,
    _process_parameter,
    get_callable_fqn,
    praxis_run_context_cv,
    protocol_function,
)
from praxis.backend.core.run_context import PraxisRunContext
from praxis.backend.models.pydantic_internals.protocol import (
    FunctionProtocolDefinitionCreate,
    ParameterMetadataModel,
)
from praxis.backend.utils.uuid import uuid7


class TestCreateProtocolDefinitionData:
    """Tests for CreateProtocolDefinitionData dataclass."""

    def test_create_protocol_definition_data_initialization(self) -> None:
        """Test CreateProtocolDefinitionData can be initialized."""

        def sample_func():
            pass

        data = CreateProtocolDefinitionData(
            func=sample_func,
            name="test_protocol",
            version="1.0",
            description="Test description",
            solo=False,
            is_top_level=False,
            preconfigure_deck=False,
            deck_param_name="deck",
            deck_construction=None,
            state_param_name="state",
            param_metadata={},
            category="test",
            tags=["tag1"],
            top_level_name_format=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$",
        )

        assert data.func == sample_func
        assert data.name == "test_protocol"
        assert data.version == "1.0"


class TestProtocolRuntimeInfo:
    """Tests for ProtocolRuntimeInfo class."""

    def test_protocol_runtime_info_initialization(self) -> None:
        """Test ProtocolRuntimeInfo can be initialized."""

        def sample_func():
            pass

        pydantic_def = FunctionProtocolDefinitionCreate(
            accession_id=uuid7(),
            name="test_protocol",
            fqn="test.test_protocol",
            version="1.0",
            source_file_path="/test/path.py",
            module_name="test",
            function_name="test_protocol",
            parameters=[],
            assets=[],
        )

        runtime_info = ProtocolRuntimeInfo(
            pydantic_definition=pydantic_def,
            function_ref=sample_func,
            found_state_param_details=None,
        )

        assert runtime_info.pydantic_definition == pydantic_def
        assert runtime_info.function_ref == sample_func
        assert runtime_info.callable_wrapper is None
        assert runtime_info.db_accession_id is None
        assert runtime_info.found_state_param_details is None

    def test_protocol_runtime_info_with_state_param_details(self) -> None:
        """Test ProtocolRuntimeInfo with state parameter details."""

        def sample_func():
            pass

        pydantic_def = FunctionProtocolDefinitionCreate(
            accession_id=uuid7(),
            name="test_protocol",
            fqn="test.test_protocol",
            version="1.0",
            source_file_path="/test/path.py",
            module_name="test",
            function_name="test_protocol",
            parameters=[],
            assets=[],
        )

        state_details = {
            "name": "state",
            "expects_praxis_state": True,
            "expects_dict": False,
        }

        runtime_info = ProtocolRuntimeInfo(
            pydantic_definition=pydantic_def,
            function_ref=sample_func,
            found_state_param_details=state_details,
        )

        assert runtime_info.found_state_param_details == state_details


class TestGetCallableFqn:
    """Tests for get_callable_fqn function."""

    def test_get_callable_fqn_with_function(self) -> None:
        """Test getting FQN from a regular function."""

        def test_function():
            pass

        fqn = get_callable_fqn(test_function)
        assert fqn.endswith(".test_function")
        assert "tests.core.test_decorators" in fqn

    def test_get_callable_fqn_with_lambda(self) -> None:
        """Test getting FQN from a lambda function."""
        test_lambda = lambda x: x + 1
        fqn = get_callable_fqn(test_lambda)
        assert "<lambda>" in fqn

    def test_get_callable_fqn_with_class_method(self) -> None:
        """Test getting FQN from a class method."""

        class TestClass:
            def test_method(self):
                pass

        fqn = get_callable_fqn(TestClass.test_method)
        assert "TestClass.test_method" in fqn


class TestCreateProtocolDefinition:
    """Tests for _create_protocol_definition function."""

    def test_create_protocol_definition_basic(self) -> None:
        """Test creating a basic protocol definition."""

        def test_protocol():
            """Test protocol docstring."""
            pass

        data = CreateProtocolDefinitionData(
            func=test_protocol,
            name=None,  # Will use function name
            version="1.0",
            description=None,  # Will use docstring
            solo=False,
            is_top_level=False,
            preconfigure_deck=False,
            deck_param_name="deck",
            deck_construction=None,
            state_param_name="state",
            param_metadata={},
            category=None,
            tags=[],
            top_level_name_format=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$",
        )

        protocol_def, state_details = _create_protocol_definition(data)

        assert protocol_def.name == "test_protocol"
        assert protocol_def.version == "1.0"
        assert "Test protocol docstring" in protocol_def.description
        assert protocol_def.is_top_level is False
        assert state_details is None

    def test_create_protocol_definition_with_name(self) -> None:
        """Test creating protocol definition with explicit name."""

        def my_func():
            pass

        data = CreateProtocolDefinitionData(
            func=my_func,
            name="custom_protocol_name",
            version="2.0",
            description="Custom description",
            solo=True,
            is_top_level=False,
            preconfigure_deck=False,
            deck_param_name="deck",
            deck_construction=None,
            state_param_name="state",
            param_metadata={},
            category="testing",
            tags=["test", "custom"],
            top_level_name_format=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$",
        )

        protocol_def, _ = _create_protocol_definition(data)

        assert protocol_def.name == "custom_protocol_name"
        assert protocol_def.version == "2.0"
        assert protocol_def.description == "Custom description"
        assert protocol_def.solo_execution is True
        assert protocol_def.category == "testing"
        assert protocol_def.tags == ["test", "custom"]

    def test_create_protocol_definition_with_parameters(self) -> None:
        """Test creating protocol definition with parameters."""

        def test_protocol(volume: int, name: str = "default"):
            pass

        data = CreateProtocolDefinitionData(
            func=test_protocol,
            name=None,
            version="1.0",
            description=None,
            solo=False,
            is_top_level=False,
            preconfigure_deck=False,
            deck_param_name="deck",
            deck_construction=None,
            state_param_name="state",
            param_metadata={
                "volume": {"description": "Volume in microliters"},
                "name": {"description": "Sample name"},
            },
            category=None,
            tags=[],
            top_level_name_format=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$",
        )

        protocol_def, _ = _create_protocol_definition(data)

        assert len(protocol_def.parameters) == 2
        assert protocol_def.parameters[0].name == "volume"
        assert protocol_def.parameters[0].description == "Volume in microliters"
        assert protocol_def.parameters[1].name == "name"
        assert protocol_def.parameters[1].optional is True

    def test_create_protocol_definition_top_level_without_state_raises_error(self) -> None:
        """Test that top-level protocol without state parameter raises error."""

        def test_protocol():
            pass

        data = CreateProtocolDefinitionData(
            func=test_protocol,
            name="test_protocol",
            version="1.0",
            description=None,
            solo=False,
            is_top_level=True,  # Requires state parameter
            preconfigure_deck=False,
            deck_param_name="deck",
            deck_construction=None,
            state_param_name="state",
            param_metadata={},
            category=None,
            tags=[],
            top_level_name_format=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$",
        )

        with pytest.raises(TypeError, match="must define a 'state' parameter"):
            _create_protocol_definition(data)

    def test_create_protocol_definition_invalid_top_level_name_raises_error(self) -> None:
        """Test that invalid top-level protocol name raises error."""

        def test_protocol(state: dict):
            pass

        data = CreateProtocolDefinitionData(
            func=test_protocol,
            name="invalid name with spaces",
            version="1.0",
            description=None,
            solo=False,
            is_top_level=True,
            preconfigure_deck=False,
            deck_param_name="deck",
            deck_construction=None,
            state_param_name="state",
            param_metadata={},
            category=None,
            tags=[],
            top_level_name_format=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$",
        )

        with pytest.raises(ValueError, match="does not match format"):
            _create_protocol_definition(data)


class TestProcessParameter:
    """Tests for _process_parameter function."""

    def test_process_parameter_basic(self) -> None:
        """Test processing a basic parameter."""

        def test_func(volume: int):
            pass

        sig = inspect.signature(test_func)
        param = sig.parameters["volume"]

        data = CreateProtocolDefinitionData(
            func=test_func,
            name="test",
            version="1.0",
            description=None,
            solo=False,
            is_top_level=False,
            preconfigure_deck=False,
            deck_param_name="deck",
            deck_construction=None,
            state_param_name="state",
            param_metadata={},
            category=None,
            tags=[],
            top_level_name_format=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$",
        )

        params_list, assets_list, found_deck, state_details = _process_parameter(
            "volume",
            param,
            data,
            [],
            [],
            found_deck_param=False,
            found_state_param_details=None,
        )

        assert len(params_list) == 1
        assert params_list[0].name == "volume"
        assert params_list[0].optional is False
        assert len(assets_list) == 0
        assert found_deck is False
        assert state_details is None

    def test_process_parameter_optional(self) -> None:
        """Test processing an optional parameter."""

        def test_func(volume: Optional[int] = None):
            pass

        sig = inspect.signature(test_func)
        param = sig.parameters["volume"]

        data = CreateProtocolDefinitionData(
            func=test_func,
            name="test",
            version="1.0",
            description=None,
            solo=False,
            is_top_level=False,
            preconfigure_deck=False,
            deck_param_name="deck",
            deck_construction=None,
            state_param_name="state",
            param_metadata={},
            category=None,
            tags=[],
            top_level_name_format=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$",
        )

        params_list, _, _, _ = _process_parameter(
            "volume",
            param,
            data,
            [],
            [],
            found_deck_param=False,
            found_state_param_details=None,
        )

        assert params_list[0].optional is True

    def test_process_parameter_state_param(self) -> None:
        """Test processing a state parameter."""

        def test_func(state: dict):
            pass

        sig = inspect.signature(test_func)
        param = sig.parameters["state"]

        data = CreateProtocolDefinitionData(
            func=test_func,
            name="test",
            version="1.0",
            description=None,
            solo=False,
            is_top_level=True,
            preconfigure_deck=False,
            deck_param_name="deck",
            deck_construction=None,
            state_param_name="state",
            param_metadata={},
            category=None,
            tags=[],
            top_level_name_format=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$",
        )

        _, _, _, state_details = _process_parameter(
            "state",
            param,
            data,
            [],
            [],
            found_deck_param=False,
            found_state_param_details=None,
        )

        assert state_details is not None
        assert state_details["name"] == "state"
        assert state_details["expects_dict"] is True


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


class TestProtocolContextVar:
    """Tests for praxis_run_context_cv context variable."""

    def test_context_var_is_context_var(self) -> None:
        """Test that praxis_run_context_cv is a ContextVar."""
        assert isinstance(praxis_run_context_cv, contextvars.ContextVar)

    def test_context_var_name(self) -> None:
        """Test that context var has correct name."""
        assert praxis_run_context_cv.name == "praxis_run_context"


class TestDecoratorsModuleStructure:
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
