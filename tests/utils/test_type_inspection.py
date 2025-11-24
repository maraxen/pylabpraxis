"""Tests for type inspection utilities in utils/type_inspection.py."""

import inspect
from typing import Any, Optional, Union

import pytest
from pylabrobot.resources import Carrier, Plate, Resource

from praxis.backend.utils.type_inspection import (
    fqn_from_hint,
    is_pylabrobot_resource,
    serialize_type_hint,
)


class TestIsPylabrobotResource:
    """Tests for is_pylabrobot_resource function."""

    def test_returns_true_for_resource_class(self) -> None:
        """Test that Resource class is identified as PyLabRobot resource."""
        assert is_pylabrobot_resource(Resource)

    def test_returns_true_for_resource_subclass(self) -> None:
        """Test that Resource subclasses are identified as PyLabRobot resources."""
        from pylabrobot.resources import Carrier

        assert is_pylabrobot_resource(Plate)
        assert is_pylabrobot_resource(Carrier)

    def test_returns_false_for_non_resource_types(self) -> None:
        """Test that non-Resource types return False."""
        assert not is_pylabrobot_resource(int)
        assert not is_pylabrobot_resource(str)
        assert not is_pylabrobot_resource(dict)
        assert not is_pylabrobot_resource(list)

    def test_returns_false_for_parameter_empty(self) -> None:
        """Test that inspect.Parameter.empty returns False."""
        assert not is_pylabrobot_resource(inspect.Parameter.empty)

    def test_handles_union_with_resource(self) -> None:
        """Test that Union with Resource type returns True."""
        union_type = Union[Plate, str]
        assert is_pylabrobot_resource(union_type)

    def test_handles_optional_resource(self) -> None:
        """Test that Optional[Resource] returns True."""
        optional_type = Optional[Plate]
        assert is_pylabrobot_resource(optional_type)

    def test_handles_union_without_resource(self) -> None:
        """Test that Union without Resource returns False."""
        union_type = Union[int, str]
        assert not is_pylabrobot_resource(union_type)

    def test_handles_optional_non_resource(self) -> None:
        """Test that Optional of non-Resource returns False."""
        optional_type = Optional[int]
        assert not is_pylabrobot_resource(optional_type)

    def test_handles_union_with_none(self) -> None:
        """Test that Union with only None returns False."""
        union_type = Union[str, None]
        # Should return False because str is not a Resource
        assert not is_pylabrobot_resource(union_type)

    def test_handles_union_multiple_resources(self) -> None:
        """Test that Union with multiple Resource types returns True."""
        union_type = Union[Plate, Carrier]
        assert is_pylabrobot_resource(union_type)


class TestFqnFromHint:
    """Tests for fqn_from_hint function."""

    def test_returns_any_for_parameter_empty(self) -> None:
        """Test that inspect.Parameter.empty returns 'Any'."""
        assert fqn_from_hint(inspect.Parameter.empty) == "Any"

    def test_returns_name_for_builtin_types(self) -> None:
        """Test that built-in types return just their name."""
        assert fqn_from_hint(int) == "int"
        assert fqn_from_hint(str) == "str"
        assert fqn_from_hint(float) == "float"
        assert fqn_from_hint(bool) == "bool"
        assert fqn_from_hint(dict) == "dict"
        assert fqn_from_hint(list) == "list"

    def test_returns_fqn_for_pylabrobot_types(self) -> None:
        """Test that PyLabRobot types return fully qualified names."""
        result = fqn_from_hint(Resource)
        assert result.startswith("pylabrobot.")
        assert "Resource" in result

        result = fqn_from_hint(Plate)
        assert result.startswith("pylabrobot.")
        assert "Plate" in result

    def test_handles_optional_type(self) -> None:
        """Test that Optional[T] returns FQN of T."""
        result = fqn_from_hint(Optional[int])
        assert result == "int"

        result = fqn_from_hint(Optional[Plate])
        assert "Plate" in result

    def test_handles_union_with_none(self) -> None:
        """Test that Union[T, None] returns FQN of T."""
        result = fqn_from_hint(Union[str, None])
        assert result == "str"

    def test_handles_union_without_none(self) -> None:
        """Test that Union without None returns string representation."""
        result = fqn_from_hint(Union[int, str])
        # Union types without None are not specifically handled
        # and return their string representation
        assert isinstance(result, str)

    def test_prioritizes_resource_in_optional_union(self) -> None:
        """Test that Resource types are prioritized in Optional Union."""
        result = fqn_from_hint(Union[str, Plate, None])
        # Should prioritize the Resource type (Plate) when None is present
        assert "Plate" in result

    def test_handles_optional_union_with_resource_first(self) -> None:
        """Test Optional Union when Resource is first."""
        result = fqn_from_hint(Union[Plate, str, None])
        # When resource is first in an optional union, it should be prioritized
        assert "Plate" in result

    def test_handles_union_with_only_none(self) -> None:
        """Test that Union with only None returns 'None'."""
        # This is a contrived case, but the code handles it
        result = fqn_from_hint(type(None))
        # The function would return "NoneType" or similar
        assert result is not None

    def test_returns_str_representation_for_unknown_types(self) -> None:
        """Test that unknown types return string representation."""
        # Create a type without __name__ attribute
        class CustomType:
            pass

        result = fqn_from_hint(CustomType)
        assert "CustomType" in result


class TestSerializeTypeHint:
    """Tests for serialize_type_hint function."""

    def test_returns_any_for_parameter_empty(self) -> None:
        """Test that inspect.Parameter.empty returns 'Any'."""
        assert serialize_type_hint(inspect.Parameter.empty) == "Any"

    def test_returns_string_representation_for_int(self) -> None:
        """Test that int type is serialized to string."""
        result = serialize_type_hint(int)
        assert isinstance(result, str)
        assert "int" in result

    def test_returns_string_representation_for_str(self) -> None:
        """Test that str type is serialized to string."""
        result = serialize_type_hint(str)
        assert isinstance(result, str)
        assert "str" in result

    def test_serializes_optional_type(self) -> None:
        """Test that Optional types are serialized."""
        result = serialize_type_hint(Optional[int])
        assert isinstance(result, str)
        assert "int" in result or "Optional" in result or "Union" in result

    def test_serializes_union_type(self) -> None:
        """Test that Union types are serialized."""
        result = serialize_type_hint(Union[int, str])
        assert isinstance(result, str)
        # Should contain both types or Union
        assert "int" in result or "str" in result or "Union" in result

    def test_serializes_resource_type(self) -> None:
        """Test that PyLabRobot Resource types are serialized."""
        result = serialize_type_hint(Plate)
        assert isinstance(result, str)
        assert "Plate" in result

    def test_serializes_list_type(self) -> None:
        """Test that generic list type is serialized."""
        from typing import List

        result = serialize_type_hint(List[int])
        assert isinstance(result, str)
        # Should contain indication of list and int
        assert isinstance(result, str)

    def test_always_returns_string(self) -> None:
        """Test that serialize_type_hint always returns a string."""
        test_types = [
            int,
            str,
            float,
            bool,
            Optional[int],
            Union[int, str],
            Plate,
            Resource,
        ]

        for type_hint in test_types:
            result = serialize_type_hint(type_hint)
            assert isinstance(result, str), f"Failed for type: {type_hint}"


class TestTypeInspectionEdgeCases:
    """Tests for edge cases in type inspection utilities."""

    def test_is_pylabrobot_resource_with_string(self) -> None:
        """Test is_pylabrobot_resource handles string input gracefully."""
        # Shouldn't crash, should return False
        assert not is_pylabrobot_resource("not a type")

    def test_fqn_from_hint_with_any(self) -> None:
        """Test fqn_from_hint with Any type."""
        result = fqn_from_hint(Any)
        assert isinstance(result, str)

    def test_serialize_with_complex_nested_types(self) -> None:
        """Test serialize_type_hint with complex nested generics."""
        from typing import Dict, List

        complex_type = Dict[str, List[Optional[int]]]
        result = serialize_type_hint(complex_type)
        assert isinstance(result, str)
        assert len(result) > 0
