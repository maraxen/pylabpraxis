from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from uuid_utils import uuid7

from praxis.backend.models.orm import ResourceOrm
from praxis.backend.models.pydantic_internals.resource import (
    ResourceUpdate,
)
from praxis.backend.api.resources import router as resource_router

app = FastAPI()
app.include_router(resource_router, prefix="/resources")

client = TestClient(app)


@pytest.fixture
def mock_resource_service():
    """Fixture to mock the resource service."""
    with patch(
        "praxis.backend.services.resource.resource_service",
        autospec=True,
    ) as mock_service:
        yield mock_service


class TestResourceApi:
    """Test suite for the resource API endpoints."""

    def test_get_resource_with_inventory(self, mock_resource_service):
        """Test retrieving a resource with inventory data."""
        resource_id = uuid7()
        inventory_data = {"items": 23, "status": "full"}
        mock_resource = ResourceOrm(
            accession_id=resource_id,
            name="test_resource",
            properties_json=inventory_data,
            fqn="test.fqn",
            resource_definition_accession_id=uuid7(),
        )
        mock_resource_service.get.return_value = mock_resource

        response = client.get(f"/resources/{resource_id}")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["accession_id"] == str(resource_id)
        assert response_data["properties_json"] == inventory_data
        mock_resource_service.get.assert_called_once()

    def test_update_resource_inventory(self, mock_resource_service):
        """Test updating a resource's inventory data."""
        resource_id = uuid7()
        initial_inventory = {"items": 23, "status": "full"}
        updated_inventory = {"items": 22, "status": "partially_used"}

        mock_initial_resource = ResourceOrm(
            accession_id=resource_id,
            name="test_resource",
            properties_json=initial_inventory,
            fqn="test.fqn",
            resource_definition_accession_id=uuid7(),
        )
        mock_updated_resource = ResourceOrm(
            accession_id=resource_id,
            name="test_resource",
            properties_json=updated_inventory,
            fqn="test.fqn",
            resource_definition_accession_id=uuid7(),
        )

        mock_resource_service.get.return_value = mock_initial_resource
        mock_resource_service.update.return_value = mock_updated_resource

        update_payload = ResourceUpdate(properties_json=updated_inventory)

        response = client.put(
            f"/resources/{resource_id}",
            json=update_payload.model_dump(exclude_unset=True),
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["properties_json"] == updated_inventory
        mock_resource_service.update.assert_called_once()

    def test_get_resource_not_found(self, mock_resource_service):
        """Test retrieving a non-existent resource."""
        resource_id = uuid7()
        mock_resource_service.get.return_value = None

        response = client.get(f"/resources/{resource_id}")

        assert response.status_code == 404
        mock_resource_service.get.assert_called_once()

    def test_get_resource_with_empty_inventory(self, mock_resource_service):
        """Test retrieving a resource with empty inventory data."""
        resource_id = uuid7()
        mock_resource = ResourceOrm(
            accession_id=resource_id,
            name="test_resource",
            properties_json=None,
            fqn="test.fqn",
            resource_definition_accession_id=uuid7(),
        )
        mock_resource_service.get.return_value = mock_resource

        response = client.get(f"/resources/{resource_id}")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["accession_id"] == str(resource_id)
        assert response_data["properties_json"] is None
        mock_resource_service.get.assert_called_once()