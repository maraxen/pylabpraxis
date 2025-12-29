"""Unit tests for AsyncPraxisState."""

import uuid

import pytest

from praxis.backend.core.storage.memory_adapter import InMemoryKeyValueStore
from praxis.backend.services.async_state import AsyncPraxisState, create_async_state


class TestAsyncPraxisState:
  """Tests for AsyncPraxisState."""

  @pytest.fixture
  def store(self) -> InMemoryKeyValueStore:
    """Create a fresh in-memory store for each test."""
    return InMemoryKeyValueStore()

  @pytest.fixture
  def run_id(self) -> uuid.UUID:
    """Create a fixed run ID for testing."""
    return uuid.UUID("12345678-1234-5678-1234-567812345678")

  @pytest.mark.asyncio
  async def test_initialize(
    self,
    store: InMemoryKeyValueStore,
    run_id: uuid.UUID,
  ) -> None:
    """Test state initialization."""
    state = AsyncPraxisState(store=store, run_accession_id=run_id)
    await state.initialize()
    assert state._initialized is True
    assert state.run_accession_id == run_id

  @pytest.mark.asyncio
  async def test_factory_function(self, store: InMemoryKeyValueStore) -> None:
    """Test the create_async_state factory function."""
    state = await create_async_state(store=store)
    assert state._initialized is True
    assert state.run_accession_id is not None

  @pytest.mark.asyncio
  async def test_set_and_get(
    self,
    store: InMemoryKeyValueStore,
    run_id: uuid.UUID,
  ) -> None:
    """Test setting and getting values."""
    state = await create_async_state(store=store, run_accession_id=run_id)

    await state.set_async("key1", "value1")
    assert state.get("key1") == "value1"
    assert state["key1"] == "value1"

  @pytest.mark.asyncio
  async def test_get_with_default(
    self,
    store: InMemoryKeyValueStore,
    run_id: uuid.UUID,
  ) -> None:
    """Test getting a non-existent key with a default."""
    state = await create_async_state(store=store, run_accession_id=run_id)

    assert state.get("nonexistent") is None
    assert state.get("nonexistent", "default") == "default"

  @pytest.mark.asyncio
  async def test_getitem_raises_keyerror(
    self,
    store: InMemoryKeyValueStore,
    run_id: uuid.UUID,
  ) -> None:
    """Test that __getitem__ raises KeyError for missing keys."""
    state = await create_async_state(store=store, run_accession_id=run_id)

    with pytest.raises(KeyError):
      _ = state["nonexistent"]

  @pytest.mark.asyncio
  async def test_delete(
    self,
    store: InMemoryKeyValueStore,
    run_id: uuid.UUID,
  ) -> None:
    """Test deleting values."""
    state = await create_async_state(store=store, run_accession_id=run_id)

    await state.set_async("key1", "value1")
    await state.delete_async("key1")
    assert "key1" not in state

  @pytest.mark.asyncio
  async def test_update(
    self,
    store: InMemoryKeyValueStore,
    run_id: uuid.UUID,
  ) -> None:
    """Test updating multiple values."""
    state = await create_async_state(store=store, run_accession_id=run_id)

    await state.update_async({"a": 1, "b": 2, "c": 3})
    assert state.get("a") == 1
    assert state.get("b") == 2
    assert state.get("c") == 3

  @pytest.mark.asyncio
  async def test_clear(
    self,
    store: InMemoryKeyValueStore,
    run_id: uuid.UUID,
  ) -> None:
    """Test clearing state."""
    state = await create_async_state(store=store, run_accession_id=run_id)

    await state.update_async({"a": 1, "b": 2})
    await state.clear_async()
    assert len(state) == 0

  @pytest.mark.asyncio
  async def test_persistence(
    self,
    store: InMemoryKeyValueStore,
    run_id: uuid.UUID,
  ) -> None:
    """Test that state persists across instances."""
    # Create first instance and set data
    state1 = await create_async_state(store=store, run_accession_id=run_id)
    await state1.set_async("persistent_key", "persistent_value")

    # Create second instance with same store and run_id
    state2 = await create_async_state(store=store, run_accession_id=run_id)
    assert state2.get("persistent_key") == "persistent_value"

  @pytest.mark.asyncio
  async def test_to_dict(
    self,
    store: InMemoryKeyValueStore,
    run_id: uuid.UUID,
  ) -> None:
    """Test to_dict returns a copy."""
    state = await create_async_state(store=store, run_accession_id=run_id)

    await state.update_async({"a": 1, "b": 2})
    data = state.to_dict()

    # Modify the returned dict
    data["c"] = 3

    # Original should be unchanged
    assert "c" not in state

  @pytest.mark.asyncio
  async def test_contains(
    self,
    store: InMemoryKeyValueStore,
    run_id: uuid.UUID,
  ) -> None:
    """Test __contains__ method."""
    state = await create_async_state(store=store, run_accession_id=run_id)

    await state.set_async("key1", "value1")
    assert "key1" in state
    assert "nonexistent" not in state

  @pytest.mark.asyncio
  async def test_len(
    self,
    store: InMemoryKeyValueStore,
    run_id: uuid.UUID,
  ) -> None:
    """Test __len__ method."""
    state = await create_async_state(store=store, run_accession_id=run_id)

    assert len(state) == 0
    await state.update_async({"a": 1, "b": 2, "c": 3})
    assert len(state) == 3

  @pytest.mark.asyncio
  async def test_keys_values_items(
    self,
    store: InMemoryKeyValueStore,
    run_id: uuid.UUID,
  ) -> None:
    """Test keys(), values(), and items() methods."""
    state = await create_async_state(store=store, run_accession_id=run_id)

    await state.update_async({"a": 1, "b": 2})
    assert set(state.keys()) == {"a", "b"}
    assert set(state.values()) == {1, 2}
    assert set(state.items()) == {("a", 1), ("b", 2)}

  @pytest.mark.asyncio
  async def test_repr(
    self,
    store: InMemoryKeyValueStore,
    run_id: uuid.UUID,
  ) -> None:
    """Test __repr__ method."""
    state = await create_async_state(store=store, run_accession_id=run_id)

    repr_str = repr(state)
    assert "AsyncPraxisState" in repr_str
    assert str(run_id) in repr_str

  @pytest.mark.asyncio
  async def test_set_empty_key_raises(
    self,
    store: InMemoryKeyValueStore,
    run_id: uuid.UUID,
  ) -> None:
    """Test that setting an empty key raises ValueError."""
    state = await create_async_state(store=store, run_accession_id=run_id)

    with pytest.raises(ValueError, match="empty string"):
      await state.set_async("", "value")

  @pytest.mark.asyncio
  async def test_delete_nonexistent_raises(
    self,
    store: InMemoryKeyValueStore,
    run_id: uuid.UUID,
  ) -> None:
    """Test that deleting a non-existent key raises KeyError."""
    state = await create_async_state(store=store, run_accession_id=run_id)

    with pytest.raises(KeyError):
      await state.delete_async("nonexistent")
