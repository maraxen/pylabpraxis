import pytest # type: ignore
import inspect
from typing import Optional, Dict, Any, Union, List
from dataclasses import is_dataclass

from praxis.backend.core.decorators import protocol_function
from praxis.backend.core.run_context import PraxisRunContext, PraxisState, PlrResource
from praxis.backend.protocol_core.protocol_definition_models import (
    FunctionProtocolDefinitionModel, ParameterMetadataModel, AssetRequirementModel, UIHint
)

# Dummy PLR-like classes for type hinting in tests
class DummyPipette(PlrResource): # Assuming PlrResource can be instantiated like this for test
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, size_x=1, size_y=1, size_z=1, category="dummy_pipette", **kwargs) # Provide dummy sizes

class DummyPlate(PlrResource):
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, size_x=1, size_y=1, size_z=1, category="dummy_plate", **kwargs)


@pytest.fixture
def minimal_protocol_function_def():
    @protocol_function(name="TestMinimal", version="1.0")
    def _minimal_func(state: PraxisState):
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
            "count": {"description": "Number of times.", "ui_hints": {"widget_type": "slider", "min_value": 1, "max_value": 10}},
            "name": {"constraints_json": {"max_length": 50}}
        }
    )
    def _complex_func(
        state: PraxisState,
        pipette: DummyPipette,
        count: int = 5,
        name: Optional[str] = None,
        target_plate: Optional[DummyPlate] = None
    ):
        '''Docstring for complex func.'''
        return f"ran {count} times for {name or 'default'} with {pipette.name} and {target_plate.name if target_plate else 'no plate'}"
    return _complex_func

class TestProtocolFunctionDecoratorMetadata:

    def test_decorator_attaches_pydantic_model(self, minimal_protocol_function_def):
        assert hasattr(minimal_protocol_function_def, '_protocol_definition')
        assert isinstance(minimal_protocol_function_def._protocol_definition, FunctionProtocolDefinitionModel)

    def test_minimal_definition_attributes(self, minimal_protocol_function_def):
        model = minimal_protocol_function_def._protocol_definition
        assert model.name == "TestMinimal"
        assert model.version == "1.0"
        assert model.description == "No description provided." # Default from decorator
        assert model.function_name == "_minimal_func"
        assert model.module_name == __name__ # Test runs in this module
        assert not model.is_top_level
        assert model.state_param_name == "state" # Default

        assert len(model.parameters) == 1
        state_param = model.parameters[0]
        assert state_param.name == "state"
        assert "PraxisState" in state_param.actual_type_str
        assert not state_param.optional

        assert len(model.assets) == 0

    def test_complex_definition_attributes(self, complex_protocol_function_def):
        model = complex_protocol_function_def._protocol_definition
        assert model.name == "TestComplex"
        assert model.version == "1.1"
        assert model.description == "A complex test protocol." # Explicit description
        assert model.is_top_level
        assert model.category == "testing"
        assert model.tags == ["complex", "example"]

        assert len(model.parameters) == 3 # state, count, name
        param_names = {p.name for p in model.parameters}
        assert param_names == {"state", "count", "name"}

        count_param = next(p for p in model.parameters if p.name == "count")
        assert count_param.actual_type_str == "int"
        assert count_param.optional # Has default value
        assert count_param.default_value_repr == "5"
        assert count_param.description == "Number of times."
        assert count_param.ui_hints is not None
        assert count_param.ui_hints.widget_type == "slider"
        assert count_param.ui_hints.min_value == 1

        name_param = next(p for p in model.parameters if p.name == "name")
        assert "str" in name_param.actual_type_str # Optional[str]
        assert name_param.optional
        assert name_param.default_value_repr is None # Optional without explicit default
        assert name_param.constraints_json == {"max_length": 50}


        assert len(model.assets) == 2 # pipette, target_plate
        asset_names = {a.name for a in model.assets}
        assert asset_names == {"pipette", "target_plate"}

        pipette_asset = next(a for a in model.assets if a.name == "pipette")
        assert "DummyPipette" in pipette_asset.actual_type_str
        assert not pipette_asset.optional

        plate_asset = next(a for a in model.assets if a.name == "target_plate")
        assert "DummyPlate" in plate_asset.actual_type_str
        assert plate_asset.optional

    def test_default_name_from_function(self):
        @protocol_function(version="0.1") # Name not provided
        def _my_actual_func_name(state: PraxisState): pass

        model = _my_actual_func_name._protocol_definition
        assert model.name == "_my_actual_func_name"

    def test_docstring_as_description(self):
        @protocol_function()
        def _func_with_docstring(state: PraxisState):
            '''This is the docstring.'''
            pass
        model = _func_with_docstring._protocol_definition
        assert model.description == "This is the docstring."

class TestProtocolFunctionWrapperInvocation:

    def test_wrapper_calls_original_function(self, minimal_protocol_function_def):
        # For unit testing the wrapper's basic call, mock the PraxisRunContext and db logging.
        # This test focuses on the metadata part being mostly done.
        # The existing wrapper in decorators.py is complex and handles logging.
        # We'll assume for now the wrapper structure (how it gets context) is as per decorators.py.

        # Create a dummy context (as the wrapper expects it)
        # The wrapper in decorators.py creates a dummy if none is passed and logs to console.
        # So, calling without __praxis_run_context__ should still work.
        result = minimal_protocol_function_def() # Call without context
        assert result == "done"

        # Test with a simplified dummy context (if needed for specific checks not covered by no-context call)
        # More detailed wrapper testing (with DB logging mocks) will be in integration or later unit tests.


class TestPraxisRunContext:
    def test_praxis_run_context_creation_and_attributes(self):
        # Assuming PraxisState can be instantiated (even if it's the Redis-backed one, for type hint)
        # For unit test, we assume PraxisState from definitions is usable without full Redis.
        # If PraxisState from definitions is an alias to utils.state.State, it requires run_guid.
        mock_state = PraxisState(run_guid="test-run-guid-ctx")
        mock_db_session = object() # Dummy object for session

        context = PraxisRunContext(
            protocol_run_db_id=1,
            run_guid="test-run-guid-ctx",
            canonical_state=mock_state,
            current_db_session=mock_db_session,
            current_call_log_db_id=None
        )
        assert context.protocol_run_db_id == 1
        assert context.run_guid == "test-run-guid-ctx"
        assert context.canonical_state is mock_state
        assert context.current_db_session is mock_db_session
        assert context.current_call_log_db_id is None
        assert context._call_sequence_next_val == 1

    def test_get_and_increment_sequence_val(self):
        context = PraxisRunContext(1, "guid-seq", PraxisState(run_guid="guid-seq"), object(), None)
        assert context.get_and_increment_sequence_val() == 1
        assert context.get_and_increment_sequence_val() == 2
        assert context._call_sequence_next_val == 3

    def test_create_context_for_nested_call(self):
        mock_state = PraxisState(run_guid="test-run-guid-parent")
        mock_db_session = object()

        parent_context = PraxisRunContext(
            protocol_run_db_id=1, run_guid="test-run-guid-parent",
            canonical_state=mock_state, current_db_session=mock_db_session,
            current_call_log_db_id=100 # Parent's own log ID (becomes parent_id for nested)
        )
        parent_context._call_sequence_next_val = 5 # Simulate some calls happened

        # This new_parent_call_log_db_id is the log ID of the function that is *creating* this nested context.
        # So, for the nested function, this ID will be its parent's log ID.
        nested_context = parent_context.create_context_for_nested_call(new_parent_call_log_db_id=100)

        assert nested_context.protocol_run_db_id == parent_context.protocol_run_db_id
        assert nested_context.run_guid == parent_context.run_guid
        assert nested_context.canonical_state == parent_context.canonical_state
        assert nested_context.current_db_session == parent_context.current_db_session
        # The 'current_call_log_db_id' of the nested context IS the parent's log ID.
        assert nested_context.current_call_log_db_id == 100
        assert nested_context._call_sequence_next_val == 5 # Sequence counter continues
