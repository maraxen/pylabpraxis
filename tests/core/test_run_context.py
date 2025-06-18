"""Unit tests for praxis.backend.core.run_context."""

import json
import uuid
from unittest.mock import MagicMock, patch

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.core.run_context import PraxisRunContext, serialize_arguments
from praxis.backend.services.state import PraxisState


class DummyResource:
    """Dummy Resource for testing."""

    def __repr__(self):
        """Return a string representation."""
        return "<DummyResource name=resource1>"


class DummyDeck:
    """Dummy Deck for testing."""

    def __repr__(self):
        """Return a string representation."""
        return "<DummyDeck name=deck1>"


class DummyModel(BaseModel):
    """Dummy Pydantic model for testing."""

    foo: int
    bar: str


def test_praxis_run_context_init():
    """Test PraxisRunContext initialization."""
    run_id = uuid.uuid4()
    state = MagicMock(spec=PraxisState)
    session = MagicMock(spec=AsyncSession)
    ctx = PraxisRunContext(
        run_accession_id=run_id,
        canonical_state=state,
        current_db_session=session,
    )
    assert ctx.run_accession_id == run_id
    assert ctx.canonical_state is state
    assert ctx.current_db_session is session
    assert ctx.current_call_log_db_accession_id is None
    assert ctx._call_sequence_next_val == 1


def test_get_and_increment_sequence_val():
    """Test get_and_increment_sequence_val increments and returns correctly."""
    ctx = PraxisRunContext(
        run_accession_id=uuid.uuid4(),
        canonical_state=MagicMock(spec=PraxisState),
        current_db_session=MagicMock(spec=AsyncSession),
    )
    assert ctx.get_and_increment_sequence_val() == 1
    assert ctx._call_sequence_next_val == 2
    assert ctx.get_and_increment_sequence_val() == 2
    assert ctx._call_sequence_next_val == 3


def test_create_context_for_nested_call():
    """Test create_context_for_nested_call returns a new context with new parent ID."""
    parent_id = uuid.uuid4()
    ctx = PraxisRunContext(
        run_accession_id=uuid.uuid4(),
        canonical_state=MagicMock(spec=PraxisState),
        current_db_session=MagicMock(spec=AsyncSession),
    )
    ctx._call_sequence_next_val = 42
    nested_ctx = ctx.create_context_for_nested_call(parent_id)
    assert nested_ctx.run_accession_id == ctx.run_accession_id
    assert nested_ctx.canonical_state is ctx.canonical_state
    assert nested_ctx.current_db_session is ctx.current_db_session
    assert nested_ctx.current_call_log_db_accession_id == parent_id
    assert nested_ctx._call_sequence_next_val == 42
    # Changing nested_ctx sequence does not affect parent
    nested_ctx.get_and_increment_sequence_val()
    assert ctx._call_sequence_next_val == 42


def test_serialize_arguments_basic_types():
    """Test serialize_arguments with basic types."""
    args = (1, "foo", 3.14)
    kwargs = {"a": 2, "b": "bar"}
    result = serialize_arguments(args, kwargs)
    assert "1" in result and "foo" in result and "3.14" in result
    assert "a" in result and "bar" in result


def test_serialize_arguments_pydantic_model():
    """Test serialize_arguments with a Pydantic model."""
    model = DummyModel(foo=123, bar="baz")
    args = (model,)
    kwargs = {"x": model}
    result = serialize_arguments(args, kwargs)
    assert "foo" in result and "bar" in result and "123" in result and "baz" in result


def test_serialize_arguments_custom_types():
    """Test serialize_arguments with custom types.

    This covers PraxisRunContext, PraxisState, Resource, and Deck objects.
    """
    ctx = PraxisRunContext(
        run_accession_id=uuid.uuid4(),
        canonical_state=MagicMock(spec=PraxisState),
        current_db_session=MagicMock(spec=AsyncSession),
    )
    state = MagicMock(spec=PraxisState)
    resource = DummyResource()
    deck = DummyDeck()
    args = (ctx, state, resource, deck)
    kwargs = {"ctx": ctx, "state": state, "resource": resource, "deck": deck}
    result = serialize_arguments(args, kwargs)
    assert "PraxisRunContext object" in result
    assert "PraxisState object" in result
    assert "<DummyResource name=resource1>" in result
    assert "<DummyDeck name=deck1>" in result


def test_serialize_arguments_excludes_praxis_run_context_kwarg():
    """Test that __praxis_run_context__ is excluded from kwargs in serialization."""
    args = (1,)
    kwargs = {"foo": 2, "__praxis_run_context__": "should be excluded"}
    result = serialize_arguments(args, kwargs)
    assert "__praxis_run_context__" not in result
    assert "foo" in result


def test_serialize_arguments_typeerror_fallback():
    """Test serialize_arguments fallback when TypeError is raised."""
    class Unserializable:
        """A class that is not serializable by default."""

    args = (Unserializable(),)
    kwargs = {"x": Unserializable()}
    # Patch json.dumps to raise TypeError on first call, then work on fallback
    orig_json_dumps = json.dumps
    call_count = {'n': 0}
    def fake_json_dumps(*a, **kw):
        if call_count['n'] == 0:
            call_count['n'] += 1
            raise TypeError("fail")
        return orig_json_dumps(*a, **kw)
    with patch("json.dumps", side_effect=fake_json_dumps):
        result = serialize_arguments(args, kwargs)
        assert "Unserializable object" in result or "Unserializable" in result
