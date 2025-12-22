"""Tests for core/decorators/definition_builder.py."""

import pytest

from praxis.backend.core.decorators import (
    CreateProtocolDefinitionData,
    _create_protocol_definition,
)


class TestCreateProtocolDefinition:

    """Tests for _create_protocol_definition function."""

    def test_create_protocol_definition_basic(self) -> None:
        """Test creating a basic protocol definition."""

        def test_protocol():
            """Test protocol docstring."""

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
