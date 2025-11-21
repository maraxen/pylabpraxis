"""Tests for core/decorators/models.py."""

import contextvars
from praxis.backend.core.decorators import (
    CreateProtocolDefinitionData,
    ProtocolRuntimeInfo,
    get_callable_fqn,
    praxis_run_context_cv,
)
from praxis.backend.models.pydantic_internals.protocol import (
    FunctionProtocolDefinitionCreate,
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
        assert "test_models" in fqn

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


class TestProtocolContextVar:
    """Tests for praxis_run_context_cv context variable."""

    def test_context_var_is_context_var(self) -> None:
        """Test that praxis_run_context_cv is a ContextVar."""
        assert isinstance(praxis_run_context_cv, contextvars.ContextVar)

    def test_context_var_name(self) -> None:
        """Test that context var has correct name."""
        assert praxis_run_context_cv.name == "praxis_run_context"
