"""Tests for the deck type definitions API."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_deck_type_definition(client: AsyncClient) -> None:
    """Test creating a deck type definition."""
    response = await client.post(
        "/api/v1/decks/types",
        json={
            "name": "Test Deck Type",
            "fqn": "test.deck.type",
            "description": "A test deck type",
            "plr_category": "deck",
            "default_size_x_mm": 1.0,
            "default_size_y_mm": 1.0,
            "default_size_z_mm": 1.0,
            "serialized_constructor_args_json": {},
            "serialized_assignment_methods_json": {},
            "serialized_constructor_hints_json": {},
            "additional_properties_json": {},
            "positioning_config": {
                "method_name": "slot_to_location",
                "arg_name": "slot",
                "arg_type": "int",
                "params": {},
            },
            "position_definitions": [
                {
                    "name": "A1",
                    "nominal_x_mm": 0.0,
                    "nominal_y_mm": 0.0,
                    "nominal_z_mm": 0.0,
                }
            ],
        },
    )
    print(response.json())
    assert response.status_code == 201
