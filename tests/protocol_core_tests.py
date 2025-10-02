import pytest
from unittest.mock import MagicMock, patch
import uuid

from praxis.backend.core.decorators import protocol_function
from praxis.backend.core.run_context import PraxisRunContext, PraxisState, Resource
from praxis.backend.models.pydantic_internals.protocol import (
    FunctionProtocolDefinitionCreate as FunctionProtocolDefinitionModel,
)


@pytest.fixture(autouse=True)
def mock_redis_client():
    """Mock the redis client used by the PraxisState service."""
    with patch("praxis.backend.services.state.redis") as mock_redis_module:
        mock_instance = MagicMock()
        # When PraxisState tries to connect, it will get this mock instance
        mock_redis_module.Redis.from_url.return_value = mock_instance
        # When PraxisState tries to ping, it will succeed
        mock_instance.ping.return_value = True
        # When PraxisState tries to get initial state, return None
        mock_instance.get.return_value = None
        yield mock_instance


# Dummy PLR-like classes for type hinting in tests
class DummyPipette(Resource):
    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(
            name=name, size_x=1, size_y=1, size_z=1, category="dummy_pipette", **kwargs
        )


class DummyPlate(Resource):
    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(
            name=name, size_x=1, size_y=1, size_z=1, category="dummy_plate", **kwargs
        )


@pytest.fixture
def minimal_protocol_function_def():
    @protocol_function(name="TestMinimal", version="1.0")
    def _minimal_func(state: PraxisState) -> str:
        return "done"

    return _minimal_func


@pytest.fixture
def complex_protocol_function_def():
    @protocol_function(
        name="TestComplex",
        version="1.1",
        description="A complex test protocol.",
        is_top_level=True,
        category="testing",
        tags=["complex", "example"],
        param_metadata={
            "count": {
                "description": "Number of times.",
                "ui_hints": {"widget_type": "slider", "min_value": 1, "max_value": 10},
            },
            "name": {"constraints_json": {"max_length": 50}},
        },
    )
    def _complex_func(
        state: PraxisState,
        pipette: DummyPipette,
        count: int = 5,
        name: str | None = None,
        target_plate: DummyPlate | None = None,
    ) -> str:
        """Docstring for complex func."""
        return f"ran {count} times for {name or 'default'} with {pipette.name} and {target_plate.name if target_plate else 'no plate'}"

    return _complex_func


class TestProtocolFunctionDecoratorMetadata:
    def test_decorator_attaches_pydantic_model(self, minimal_protocol_function_def) -> None:
        assert hasattr(minimal_protocol_function_def, "_protocol_definition")
        assert isinstance(
            minimal_protocol_function_def._protocol_definition,
            FunctionProtocolDefinitionModel,
        )

    def test_minimal_definition_attributes(self, minimal_protocol_function_def) -> None:
        model = minimal_protocol_function_def._protocol_definition
        assert model.name == "TestMinimal"
        assert model.version == "1.0"
        assert model.description == "No description provided."
        assert model.function_name == "_minimal_func"
        assert model.module_name == __name__
        assert not model.is_top_level
        assert model.state_param_name == "state"

        assert len(model.parameters) == 1
        state_param = model.parameters[0]
        assert state_param.name == "state"
        assert "PraxisState" in state_param.type_hint
        assert not state_param.optional
        assert len(model.assets) == 0

    def test_complex_definition_attributes(self, complex_protocol_function_def) -> None:
        model = complex_protocol_function_def._protocol_definition
        assert model.name == "TestComplex"
        assert model.version == "1.1"
        assert model.description == "A complex test protocol."
        assert model.is_top_level
        assert model.category == "testing"
        assert model.tags == ["complex", "example"]

        assert len(model.parameters) == 3
        param_names = {p.name for p in model.parameters}
        assert param_names == {"state", "count", "name"}

        count_param = next(p for p in model.parameters if p.name == "count")
        assert count_param.type_hint == "int"
        assert count_param.optional
        assert count_param.default_value_repr == "5"
        assert count_param.description == "Number of times."

        name_param = next(p for p in model.parameters if p.name == "name")
        assert "str" in name_param.type_hint
        assert name_param.optional
        assert name_param.default_value_repr is None

        assert len(model.assets) == 2
        asset_names = {a.name for a in model.assets}
        assert asset_names == {"pipette", "target_plate"}

        pipette_asset = next(a for a in model.assets if a.name == "pipette")
        assert "DummyPipette" in pipette_asset.type_hint_str
        assert not pipette_asset.optional

        plate_asset = next(a for a in model.assets if a.name == "target_plate")
        assert "DummyPlate" in plate_asset.type_hint_str
        assert plate_asset.optional

    def test_default_name_from_function(self) -> None:
        @protocol_function(version="0.1")
        def _my_actual_func_name(state: PraxisState) -> None:
            pass

        model = _my_actual_func_name._protocol_definition
        assert model.name == "_my_actual_func_name"

    def test_docstring_as_description(self) -> None:
        @protocol_function()
        def _func_with_docstring(state: PraxisState) -> None:
            """This is the docstring."""

        model = _func_with_docstring._protocol_definition
        assert model.description == "This is the docstring."


@pytest.mark.asyncio
class TestProtocolFunctionWrapperInvocation:
    async def test_wrapper_calls_original_function(self, minimal_protocol_function_def) -> None:
        with patch("praxis.backend.core.decorators.praxis_run_context_cv") as mock_cv:
            mock_context = MagicMock()
            mock_context.run_accession_id = uuid.uuid4()
            mock_context.current_db_session = AsyncMock()
            mock_context.current_call_log_db_accession_id = None
            mock_cv.get.return_value = mock_context

            with patch(
                "praxis.backend.core.decorators.log_function_call_start",
                new_callable=AsyncMock,
            ) as mock_log_start:
                mock_log_start.return_value = MagicMock(accession_id=uuid.uuid4())
                result = await minimal_protocol_function_def()
                assert result == "done"


@pytest.mark.asyncio
class TestPraxisRunContext:
    def test_praxis_run_context_creation_and_attributes(self) -> None:
        mock_state = PraxisState(run_accession_id="test-run-accession_id-ctx")
        mock_db_session = object()

        context = PraxisRunContext(
            run_accession_id=uuid.uuid4(),
            canonical_state=mock_state,
            current_db_session=mock_db_session,
            current_call_log_db_accession_id=None,
        )
        assert context.run_accession_id is not None
        assert context.canonical_state is mock_state
        assert context.current_db_session is mock_db_session
        assert context.current_call_log_db_accession_id is None
        assert context._call_sequence_next_val == 1

    def test_get_and_increment_sequence_val(self) -> None:
        context = PraxisRunContext(
            run_accession_id=uuid.uuid4(),
            canonical_state=PraxisState(run_accession_id="accession_id-seq"),
            current_db_session=object(),
            current_call_log_db_accession_id=None,
        )
        assert context.get_and_increment_sequence_val() == 1
        assert context.get_and_increment_sequence_val() == 2
        assert context._call_sequence_next_val == 3

    def test_create_context_for_nested_call(self) -> None:
        mock_state = PraxisState(run_accession_id="test-run-accession_id-parent")
        mock_db_session = object()

        parent_context = PraxisRunContext(
            run_accession_id=uuid.uuid4(),
            canonical_state=mock_state,
            current_db_session=mock_db_session,
            current_call_log_db_accession_id=uuid.uuid4(),
        )
        parent_context._call_sequence_next_val = 5

        nested_context = parent_context.create_context_for_nested_call(
            new_parent_call_log_db_accession_id=parent_context.current_call_log_db_accession_id
        )

        assert nested_context.run_accession_id == parent_context.run_accession_id
        assert nested_context.canonical_state == parent_context.canonical_state
        assert nested_context.current_db_session == parent_context.current_db_session
        assert (
            nested_context.current_call_log_db_accession_id
            == parent_context.current_call_log_db_accession_id
        )
        assert nested_context._call_sequence_next_val == 5