"""Tests for core/decorators/parameter_processor.py."""

import inspect

from praxis.backend.core.decorators import (
    CreateProtocolDefinitionData,
    _process_parameter,
)


class TestProcessParameter:

    """Tests for _process_parameter function."""

    def test_process_parameter_basic(self) -> None:
        """Test processing a basic parameter."""

        def test_func(volume: int):
            pass

        sig = inspect.signature(test_func)
        param = sig.parameters["volume"]

        data = CreateProtocolDefinitionData(
            func=test_func,
            name="test",
            version="1.0",
            description=None,
            solo=False,
            is_top_level=False,
            preconfigure_deck=False,
            requires_deck=None,
            deck_param_name="deck",
            deck_construction=None,
            deck_layout_path=None,
            data_views=None,
            setup_instructions=None,
            state_param_name="state",
            param_metadata={},
            category=None,
            tags=[],
            top_level_name_format=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$",
        )

        params_list, assets_list, found_deck, state_details = _process_parameter(
            "volume",
            param,
            data,
            [],
            [],
            found_deck_param=False,
            found_state_param_details=None,
        )

        assert len(params_list) == 1
        assert params_list[0].name == "volume"
        assert params_list[0].optional is False
        assert len(assets_list) == 0
        assert found_deck is False
        assert state_details is None

    def test_process_parameter_optional(self) -> None:
        """Test processing an optional parameter."""

        def test_func(volume: int | None = None):
            pass

        sig = inspect.signature(test_func)
        param = sig.parameters["volume"]

        data = CreateProtocolDefinitionData(
            func=test_func,
            name="test",
            version="1.0",
            description=None,
            solo=False,
            is_top_level=False,
            preconfigure_deck=False,
            requires_deck=None,
            deck_param_name="deck",
            deck_construction=None,
            deck_layout_path=None,
            data_views=None,
            setup_instructions=None,
            state_param_name="state",
            param_metadata={},
            category=None,
            tags=[],
            top_level_name_format=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$",
        )

        params_list, _, _, _ = _process_parameter(
            "volume",
            param,
            data,
            [],
            [],
            found_deck_param=False,
            found_state_param_details=None,
        )

        assert params_list[0].optional is True

    def test_process_parameter_state_param(self) -> None:
        """Test processing a state parameter."""

        def test_func(state: dict):
            pass

        sig = inspect.signature(test_func)
        param = sig.parameters["state"]

        data = CreateProtocolDefinitionData(
            func=test_func,
            name="test",
            version="1.0",
            description=None,
            solo=False,
            is_top_level=True,
            preconfigure_deck=False,
            requires_deck=None,
            deck_param_name="deck",
            deck_construction=None,
            deck_layout_path=None,
            data_views=None,
            setup_instructions=None,
            state_param_name="state",
            param_metadata={},
            category=None,
            tags=[],
            top_level_name_format=r"^[a-zA-Z0-9](?:[a-zA-Z0-9._-]*[a-zA-Z0-9])?$",
        )

        _, _, _, state_details = _process_parameter(
            "state",
            param,
            data,
            [],
            [],
            found_deck_param=False,
            found_state_param_details=None,
        )

        assert state_details is not None
        assert state_details["name"] == "state"
        assert state_details["expects_dict"] is True
