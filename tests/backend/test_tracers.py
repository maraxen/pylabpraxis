"""Tests for tracers."""
from unittest.mock import Mock

import pytest

from praxis.backend.tracers import LinkedIndicesTracer
from praxis.backend.utils.errors import InvalidWellSetsError


class TestLinkedIndicesTracer:
    """Tests for LinkedIndicesTracer."""

    def test_validate_linked_indices_success(self) -> None:
        """Test that validate_linked_indices returns True for valid well sets."""
        tracer = LinkedIndicesTracer()
        source_wells = [Mock(index=0), Mock(index=1), Mock(index=2)]
        destination_wells = [Mock(index=0), Mock(index=1), Mock(index=2)]
        assert tracer.validate(source_wells, destination_wells)

    def test_validate_linked_indices_different_lengths(self) -> None:
        """Test that validate_linked_indices raises InvalidWellSetsError for different lengths."""
        tracer = LinkedIndicesTracer()
        source_wells = [Mock(index=0), Mock(index=1), Mock(index=2)]
        destination_wells = [Mock(index=0), Mock(index=1)]
        with pytest.raises(InvalidWellSetsError, match="Source and destination well sets have different lengths."):
            tracer.validate(source_wells, destination_wells)

    def test_validate_linked_indices_different_indices(self) -> None:
        """Test that validate_linked_indices raises InvalidWellSetsError for different indices."""
        tracer = LinkedIndicesTracer()
        source_wells = [Mock(index=0), Mock(index=1), Mock(index=2)]
        destination_wells = [Mock(index=0), Mock(index=1), Mock(index=3)]
        with pytest.raises(InvalidWellSetsError, match="Source well at index 2 has index 2, but destination well has index 3."):
            tracer.validate(source_wells, destination_wells)
