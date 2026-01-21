"""Tests for core/run_context.py."""

import json
from unittest.mock import Mock, patch

from pydantic import BaseModel
from pylabrobot.resources import Plate

from praxis.backend.core.run_context import PraxisRunContext, serialize_arguments
from praxis.backend.utils.uuid import uuid7


class TestPraxisRunContext:

    """Tests for PraxisRunContext dataclass."""

    def test_praxis_run_context_initialization(self) -> None:
        """Test that PraxisRunContext can be initialized."""
        run_id = uuid7()
        mock_state = Mock()
        mock_session = Mock()

        context = PraxisRunContext(
            run_accession_id=run_id,
            canonical_state=mock_state,
            current_db_session=mock_session,
        )

        assert context.run_accession_id == run_id
        assert context.canonical_state == mock_state
        assert context.current_db_session == mock_session
        assert context.current_call_log_db_accession_id is None
        assert context._call_sequence_next_val == 1

    def test_praxis_run_context_with_call_log_id(self) -> None:
        """Test PraxisRunContext initialization with call_log_db_accession_id."""
        run_id = uuid7()
        call_log_id = uuid7()
        mock_state = Mock()
        mock_session = Mock()

        context = PraxisRunContext(
            run_accession_id=run_id,
            canonical_state=mock_state,
            current_db_session=mock_session,
            current_call_log_db_accession_id=call_log_id,
        )

        assert context.current_call_log_db_accession_id == call_log_id

    def test_praxis_run_context_is_dataclass(self) -> None:
        """Test that PraxisRunContext is a dataclass."""
        from dataclasses import is_dataclass

        assert is_dataclass(PraxisRunContext)


class TestGetAndIncrementSequenceVal:

    """Tests for PraxisRunContext.get_and_increment_sequence_val()."""

    def test_get_and_increment_returns_initial_value(self) -> None:
        """Test that first call returns 1."""
        context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )

        result = context.get_and_increment_sequence_val()
        assert result == 1

    def test_get_and_increment_increments_counter(self) -> None:
        """Test that calling increments the internal counter."""
        context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )

        context.get_and_increment_sequence_val()
        assert context._call_sequence_next_val == 2

    def test_get_and_increment_sequential_calls(self) -> None:
        """Test that sequential calls return incrementing values."""
        context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )

        val1 = context.get_and_increment_sequence_val()
        val2 = context.get_and_increment_sequence_val()
        val3 = context.get_and_increment_sequence_val()

        assert val1 == 1
        assert val2 == 2
        assert val3 == 3

    def test_get_and_increment_multiple_calls(self) -> None:
        """Test that counter continues incrementing correctly."""
        context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )

        values = [context.get_and_increment_sequence_val() for _ in range(10)]
        assert values == list(range(1, 11))


class TestCreateContextForNestedCall:

    """Tests for PraxisRunContext.create_context_for_nested_call()."""

    def test_create_nested_context_returns_new_instance(self) -> None:
        """Test that method returns a new PraxisRunContext instance."""
        original_context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )

        nested_context = original_context.create_context_for_nested_call(uuid7())

        assert isinstance(nested_context, PraxisRunContext)
        assert nested_context is not original_context

    def test_create_nested_context_preserves_run_id(self) -> None:
        """Test that nested context has same run_accession_id."""
        run_id = uuid7()
        original_context = PraxisRunContext(
            run_accession_id=run_id,
            canonical_state=Mock(),
            current_db_session=Mock(),
        )

        nested_context = original_context.create_context_for_nested_call(uuid7())
        assert nested_context.run_accession_id == run_id

    def test_create_nested_context_preserves_canonical_state(self) -> None:
        """Test that nested context shares canonical_state."""
        mock_state = Mock()
        original_context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=mock_state,
            current_db_session=Mock(),
        )

        nested_context = original_context.create_context_for_nested_call(uuid7())
        assert nested_context.canonical_state is mock_state

    def test_create_nested_context_preserves_db_session(self) -> None:
        """Test that nested context shares current_db_session."""
        mock_session = Mock()
        original_context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=mock_session,
        )

        nested_context = original_context.create_context_for_nested_call(uuid7())
        assert nested_context.current_db_session is mock_session

    def test_create_nested_context_sets_parent_call_log_id(self) -> None:
        """Test that nested context has new parent call log ID."""
        parent_call_id = uuid7()
        original_context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )

        nested_context = original_context.create_context_for_nested_call(parent_call_id)
        assert nested_context.current_call_log_db_accession_id == parent_call_id

    def test_create_nested_context_preserves_sequence_counter(self) -> None:
        """Test that nested context continues sequence counter."""
        original_context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )

        # Increment original context counter
        original_context.get_and_increment_sequence_val()
        original_context.get_and_increment_sequence_val()

        nested_context = original_context.create_context_for_nested_call(uuid7())
        assert nested_context._call_sequence_next_val == 3

    def test_create_nested_context_shares_sequence_state(self) -> None:
        """Test that nested context sequence counter is synchronized."""
        original_context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )

        original_context.get_and_increment_sequence_val()  # Now at 2
        nested_context = original_context.create_context_for_nested_call(uuid7())

        # Nested context should continue from 2
        assert nested_context.get_and_increment_sequence_val() == 2
        assert nested_context._call_sequence_next_val == 3

    def test_create_nested_context_with_none_parent_id(self) -> None:
        """Test creating nested context with None parent call ID."""
        original_context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )

        nested_context = original_context.create_context_for_nested_call(None)
        assert nested_context.current_call_log_db_accession_id is None


class TestSerializeArguments:

    """Tests for serialize_arguments function."""

    def test_serialize_simple_args(self) -> None:
        """Test serialization of simple positional arguments."""
        result = serialize_arguments((1, "test", 3.14), {})
        data = json.loads(result)

        assert data["args"] == [1, "test", 3.14]
        assert data["kwargs"] == {}

    def test_serialize_simple_kwargs(self) -> None:
        """Test serialization of simple keyword arguments."""
        result = serialize_arguments((), {"key1": "value1", "key2": 42})
        data = json.loads(result)

        assert data["args"] == []
        assert data["kwargs"] == {"key1": "value1", "key2": 42}

    def test_serialize_mixed_args_and_kwargs(self) -> None:
        """Test serialization of both args and kwargs."""
        result = serialize_arguments((1, 2), {"key": "value"})
        data = json.loads(result)

        assert data["args"] == [1, 2]
        assert data["kwargs"] == {"key": "value"}

    def test_serialize_filters_praxis_run_context(self) -> None:
        """Test that __praxis_run_context__ is filtered from kwargs."""
        mock_context = Mock()
        result = serialize_arguments(
            (), {"regular_arg": "value", "__praxis_run_context__": mock_context},
        )
        data = json.loads(result)

        assert "__praxis_run_context__" not in data["kwargs"]
        assert data["kwargs"] == {"regular_arg": "value"}

    def test_serialize_pydantic_model(self) -> None:
        """Test serialization of Pydantic models."""

        class TestModel(BaseModel):
            field1: str
            field2: int

        model = TestModel(field1="test", field2=42)
        result = serialize_arguments((model,), {})
        data = json.loads(result)

        assert data["args"][0] == {"field1": "test", "field2": 42}

    def test_serialize_praxis_run_context_as_placeholder(self) -> None:
        """Test that PraxisRunContext is serialized as placeholder."""
        context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )

        result = serialize_arguments((context,), {})
        data = json.loads(result)

        assert data["args"][0] == "<PraxisRunContext object>"

    def test_serialize_praxis_state_as_placeholder(self) -> None:
        """Test that PraxisState is serialized as placeholder."""
        from praxis.backend.services.state import PraxisState

        # Create actual PraxisState instance with mocked Redis
        with patch("praxis.backend.services.state.redis.Redis"):
            state = PraxisState()

        result = serialize_arguments((state,), {})
        data = json.loads(result)

        assert data["args"][0] == "<PraxisState object>"

    def test_serialize_resource_uses_repr(self) -> None:
        """Test that PyLabRobot Resource uses repr()."""
        from collections import OrderedDict

        plate = Plate(
            "test_plate", size_x=127.76, size_y=85.48, size_z=14.0, ordering=OrderedDict(),
        )
        result = serialize_arguments((plate,), {})
        data = json.loads(result)

        # Should contain repr output
        assert "Plate" in data["args"][0]
        assert "test_plate" in data["args"][0]

    def test_serialize_returns_json_string(self) -> None:
        """Test that function returns valid JSON string."""
        result = serialize_arguments((1, 2), {"key": "value"})

        assert isinstance(result, str)
        # Should be valid JSON
        json.loads(result)  # Should not raise

    def test_serialize_nested_structures(self) -> None:
        """Test serialization of nested data structures."""
        nested_data = {"list": [1, 2, 3], "dict": {"inner": "value"}}
        result = serialize_arguments((), nested_data)
        data = json.loads(result)

        assert data["kwargs"]["list"] == [1, 2, 3]
        assert data["kwargs"]["dict"] == {"inner": "value"}

    def test_serialize_empty_args_and_kwargs(self) -> None:
        """Test serialization with no arguments."""
        result = serialize_arguments((), {})
        data = json.loads(result)

        assert data["args"] == []
        assert data["kwargs"] == {}


class TestPraxisRunContextSimulation:
    """Tests for simulation-related features in PraxisRunContext."""

    def test_simulation_defaults(self) -> None:
        """Test default simulation values."""
        context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )
        assert context.is_simulation is False
        assert context.simulation_state == {}

    def test_get_simulation_state(self) -> None:
        """Test get_simulation_state method."""
        context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )
        state = context.get_simulation_state()
        assert state == {}
        assert state is context.simulation_state

    def test_update_simulation_state(self) -> None:
        """Test update_simulation_state method."""
        context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )
        context.update_simulation_state({"foo": "bar", "count": 42})
        assert context.simulation_state == {"foo": "bar", "count": 42}

        context.update_simulation_state({"foo": "baz"})
        assert context.simulation_state == {"foo": "baz", "count": 42}

    def test_nested_context_preserves_simulation_flags(self) -> None:
        """Test that nested contexts inherit simulation flags and state."""
        original = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
            is_simulation=True,
        )
        original.update_simulation_state({"shared": True})

        nested = original.create_context_for_nested_call(uuid7())

        assert nested.is_simulation is True
        assert nested.simulation_state == {"shared": True}
        assert nested.simulation_state is original.simulation_state


class TestRunContextIntegration:

    """Integration tests for PraxisRunContext."""

    def test_complete_nested_call_workflow(self) -> None:
        """Test complete workflow of creating nested contexts."""
        # Create root context
        root_context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )

        # Get sequence value in root
        seq1 = root_context.get_and_increment_sequence_val()
        assert seq1 == 1

        # Create nested context
        parent_call_id = uuid7()
        nested_context = root_context.create_context_for_nested_call(parent_call_id)

        # Nested context should continue sequence
        seq2 = nested_context.get_and_increment_sequence_val()
        assert seq2 == 2

        # Nested context should have parent call ID
        assert nested_context.current_call_log_db_accession_id == parent_call_id

    def test_multiple_nested_levels(self) -> None:
        """Test multiple levels of nested contexts."""
        root = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )

        level1 = root.create_context_for_nested_call(uuid7())
        level2 = level1.create_context_for_nested_call(uuid7())
        level3 = level2.create_context_for_nested_call(uuid7())

        # All should share same run ID
        assert root.run_accession_id == level1.run_accession_id
        assert level1.run_accession_id == level2.run_accession_id
        assert level2.run_accession_id == level3.run_accession_id

        # All should share same state
        assert root.canonical_state is level1.canonical_state
        assert level1.canonical_state is level2.canonical_state
        assert level2.canonical_state is level3.canonical_state


class TestSerializeArgumentsEdgeCases:

    """Edge case tests for serialize_arguments function."""

    def test_serialize_with_none_values(self) -> None:
        """Test serialization with None values."""
        result = serialize_arguments((None,), {"key": None})
        data = json.loads(result)

        assert data["args"][0] is None
        assert data["kwargs"]["key"] is None

    def test_serialize_with_boolean_values(self) -> None:
        """Test serialization with boolean values."""
        result = serialize_arguments((True, False), {"flag": True})
        data = json.loads(result)

        assert data["args"] == [True, False]
        assert data["kwargs"]["flag"] is True

    def test_serialize_with_uuid(self) -> None:
        """Test serialization with UUID (uses default=str)."""
        test_uuid = uuid7()
        result = serialize_arguments((test_uuid,), {"id": test_uuid})
        data = json.loads(result)

        # UUID should be converted to string
        assert isinstance(data["args"][0], str)
        assert isinstance(data["kwargs"]["id"], str)

    def test_serialize_complex_mixed_types(self) -> None:
        """Test serialization with complex mix of types."""
        from collections import OrderedDict

        plate = Plate("plate1", size_x=127.76, size_y=85.48, size_z=14.0, ordering=OrderedDict())
        context = PraxisRunContext(
            run_accession_id=uuid7(),
            canonical_state=Mock(),
            current_db_session=Mock(),
        )

        result = serialize_arguments(
            (1, "test", plate, context),
            {"normal": "value", "id": uuid7(), "__praxis_run_context__": context},
        )
        data = json.loads(result)

        # Check args
        assert data["args"][0] == 1
        assert data["args"][1] == "test"
        assert "Plate" in data["args"][2]  # plate repr
        assert data["args"][3] == "<PraxisRunContext object>"

        # Check kwargs
        assert data["kwargs"]["normal"] == "value"
        assert "__praxis_run_context__" not in data["kwargs"]
        assert isinstance(data["kwargs"]["id"], str)  # UUID converted to string
