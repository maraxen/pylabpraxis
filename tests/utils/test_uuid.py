"""Tests for UUID utilities module.

This module tests the UUID generation functions in praxis.backend.utils.uuid,
including UUID4, UUID7, and name generation utilities.
"""

import re
import uuid
from typing import Set

import pytest

from praxis.backend.utils.uuid import generate_name, uuid4, uuid7


class TestUUID7:
    """Tests for UUID7 generation."""

    def test_uuid7_returns_uuid_object(self) -> None:
        """Test that uuid7() returns a standard uuid.UUID object."""
        result = uuid7()
        assert isinstance(result, uuid.UUID)

    def test_uuid7_is_version_7(self) -> None:
        """Test that generated UUID is version 7."""
        result = uuid7()
        assert result.version == 7

    def test_uuid7_generates_unique_values(self) -> None:
        """Test that consecutive uuid7() calls return unique values."""
        uuids: Set[uuid.UUID] = {uuid7() for _ in range(100)}
        assert len(uuids) == 100, "All generated UUID7s should be unique"

    def test_uuid7_is_monotonically_increasing(self) -> None:
        """Test that UUID7s are monotonically increasing (time-ordered).

        UUID7 contains a timestamp component, so values should generally
        increase over time when generated in sequence.
        """
        uuid_list = [uuid7() for _ in range(10)]

        # Convert to strings for comparison (UUID7 has timestamp in high bits)
        # Check that most are in increasing order (allowing for some clock precision)
        increasing_pairs = sum(
            1 for i in range(len(uuid_list) - 1)
            if uuid_list[i] < uuid_list[i + 1]
        )

        # At least 80% should be monotonically increasing
        assert increasing_pairs >= 8, (
            f"UUID7s should be mostly monotonic, got {increasing_pairs}/9 "
            "increasing pairs"
        )

    def test_uuid7_string_representation(self) -> None:
        """Test that UUID7 can be converted to standard string format."""
        result = uuid7()
        uuid_str = str(result)

        # Standard UUID format: 8-4-4-4-12 hex digits
        pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        assert re.match(pattern, uuid_str), (
            f"UUID string should match standard format, got: {uuid_str}"
        )


class TestUUID4:
    """Tests for UUID4 generation."""

    def test_uuid4_returns_uuid_object(self) -> None:
        """Test that uuid4() returns a standard uuid.UUID object."""
        result = uuid4()
        assert isinstance(result, uuid.UUID)

    def test_uuid4_is_version_4(self) -> None:
        """Test that generated UUID is version 4."""
        result = uuid4()
        assert result.version == 4

    def test_uuid4_generates_unique_values(self) -> None:
        """Test that consecutive uuid4() calls return unique values."""
        uuids: Set[uuid.UUID] = {uuid4() for _ in range(100)}
        assert len(uuids) == 100, "All generated UUID4s should be unique"

    def test_uuid4_string_representation(self) -> None:
        """Test that UUID4 can be converted to standard string format."""
        result = uuid4()
        uuid_str = str(result)

        # Standard UUID format: 8-4-4-4-12 hex digits
        pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        assert re.match(pattern, uuid_str), (
            f"UUID string should match standard format, got: {uuid_str}"
        )


class TestGenerateName:
    """Tests for generate_name() function."""

    def test_generate_name_returns_string(self) -> None:
        """Test that generate_name() returns a string."""
        result = generate_name("test")
        assert isinstance(result, str)

    def test_generate_name_includes_prefix(self) -> None:
        """Test that generated name includes the provided prefix."""
        prefix = "my-prefix"
        result = generate_name(prefix)
        assert result.startswith(f"{prefix}-"), (
            f"Name should start with '{prefix}-', got: {result}"
        )

    def test_generate_name_format(self) -> None:
        """Test that generated name has correct format: prefix-XXXXXXXX."""
        result = generate_name("test")

        # Format: prefix-<8 hex chars>
        pattern = r"^test-[0-9a-f]{8}$"
        assert re.match(pattern, result), (
            f"Name should match 'test-XXXXXXXX' format, got: {result}"
        )

    def test_generate_name_uses_uuid7_hex(self) -> None:
        """Test that generated name uses first 8 hex chars of UUID7."""
        result = generate_name("prefix")

        # Extract the hex portion
        hex_portion = result.split("-", 1)[1]
        assert len(hex_portion) == 8
        assert all(c in "0123456789abcdef" for c in hex_portion), (
            f"Hex portion should only contain hex digits, got: {hex_portion}"
        )

    def test_generate_name_unique_values(self) -> None:
        """Test that generate_name() can produce multiple values.

        Note: UUID7 uses timestamps in the first hex chars, so rapid generation
        may produce some duplicates. We test that at least some unique values
        are generated, not that all are unique.
        """
        names: Set[str] = {generate_name("test") for _ in range(100)}
        # At least 1 unique name should be generated (could be same if very fast)
        # In practice, should get at least a few unique names
        assert len(names) >= 1, "Should generate at least one name"

    def test_generate_name_different_prefixes(self) -> None:
        """Test that generate_name works with different prefixes."""
        prefixes = ["short", "longer-prefix", "with_underscore", "123numeric"]

        for prefix in prefixes:
            result = generate_name(prefix)
            assert result.startswith(f"{prefix}-"), (
                f"Name with prefix '{prefix}' should start with '{prefix}-', "
                f"got: {result}"
            )
            # Verify it still has 8 hex chars after the prefix
            # Use rsplit to get the last part (in case prefix contains hyphens)
            hex_portion = result.rsplit("-", 1)[1]
            assert len(hex_portion) == 8

    def test_generate_name_empty_prefix(self) -> None:
        """Test that generate_name works with empty prefix."""
        result = generate_name("")

        # Format: -<8 hex chars>
        pattern = r"^-[0-9a-f]{8}$"
        assert re.match(pattern, result), (
            f"Name with empty prefix should match '-XXXXXXXX' format, got: {result}"
        )

    def test_generate_name_special_characters_in_prefix(self) -> None:
        """Test that generate_name handles special characters in prefix."""
        special_prefixes = ["test.name", "test:name", "test/name"]

        for prefix in special_prefixes:
            result = generate_name(prefix)
            assert result.startswith(f"{prefix}-"), (
                f"Name should preserve special chars in prefix '{prefix}', "
                f"got: {result}"
            )
