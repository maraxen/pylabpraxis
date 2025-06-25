import datetime
import json
from unittest.mock import ANY, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Pydantic models for request/response validation and constructing test data
from praxis.backend.api.resources import (
  ResourceInventoryDataIn,
  ResourceInventoryDataOut,
)

# Router to be tested
from praxis.backend.api.resources import router as assets_router

# ORM Model mock for service layer
from praxis.backend.database_models.asset_management_orm import ResourceInstanceOrm

# Setup FastAPI app and TestClient
app = FastAPI()
app.include_router(
  assets_router
)  # Assuming default prefix, adjust if /api/assets is used in main app

client = TestClient(app)


# --- Test Class for Resource Instance Inventory API Endpoints ---
class TestResourceInstanceInventoryAPI:
  MOCK_INSTANCE_ID = 123
  MOCK_USER_ID = "test_user_api"

  @pytest.fixture(autouse=True)
  def patch_dependencies(self, monkeypatch):
    # Mock the get_db dependency to avoid actual DB calls
    self.mock_db_session = MagicMock()
    mock_get_db = MagicMock(return_value=self.mock_db_session)
    monkeypatch.setattr("praxis.backend.api.assets.get_db", mock_get_db)

    # Mock the asset_data_service functions used by the API
    self.mock_get_resource = MagicMock()
    self.mock_update_lw_status = MagicMock()

    monkeypatch.setattr(
      "praxis.backend.api.assets.asset_data_service.get_resource_instance",
      self.mock_get_resource,
    )
    monkeypatch.setattr(
      "praxis.backend.api.assets.asset_data_service.update_resource_instance_location_and_status",
      self.mock_update_lw_status,
    )

  def test_get_resource_instance_inventory_success(self):
    mock_instance_orm = MagicMock(spec=ResourceInstanceOrm)
    inventory_dict = {
      "praxis_inventory_schema_version": "1.0",
      "reagents": [
        {
          "reagent_accession_id": "R1",
          "initial_quantity": {"value": 10, "unit": "ml"},
          "current_quantity": {"value": 5, "unit": "ml"},
        }
      ],
      "item_count": {"initial_max_items": 96, "current_available_items": 90},
      "consumable_state": "partially_used",
      "last_updated_by": "user1",
      "inventory_notes": "Some notes",
      "last_updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    mock_instance_orm.properties_json = inventory_dict
    self.mock_get_resource.return_value = mock_instance_orm

    response = client.get(f"/resource_instances/{self.MOCK_INSTANCE_ID}/inventory")

    assert response.status_code == 200
    self.mock_get_resource.assert_called_once_with(
      self.mock_db_session, self.MOCK_INSTANCE_ID
    )

    # Validate against ResourceInventoryDataOut model structure
    expected_data = ResourceInventoryDataOut(
      **inventory_dict
    ).model_dump()  # Pydantic v2
    # For Pydantic v1: expected_data = ResourceInventoryDataOut(**inventory_dict).dict()
    assert response.json() == expected_data

  def test_get_resource_instance_inventory_not_found(self):
    self.mock_get_resource.return_value = None
    response = client.get(f"/resource_instances/{self.MOCK_INSTANCE_ID}/inventory")
    assert response.status_code == 404
    self.mock_get_resource.assert_called_once_with(
      self.mock_db_session, self.MOCK_INSTANCE_ID
    )

  def test_get_resource_instance_inventory_empty(self):
    mock_instance_orm = MagicMock(spec=ResourceInstanceOrm)
    mock_instance_orm.properties_json = None  # Or {}
    self.mock_get_resource.return_value = mock_instance_orm

    response = client.get(f"/resource_instances/{self.MOCK_INSTANCE_ID}/inventory")
    assert response.status_code == 200
    # Expecting ResourceInventoryDataOut default values (all None)
    expected_empty_data = ResourceInventoryDataOut().model_dump()  # Pydantic v2
    # For Pydantic v1: expected_empty_data = ResourceInventoryDataOut().dict()
    assert response.json() == expected_empty_data
    self.mock_get_resource.assert_called_once_with(
      self.mock_db_session, self.MOCK_INSTANCE_ID
    )

  def test_update_resource_instance_inventory_success(self):
    mock_instance_orm_initial = MagicMock(spec=ResourceInstanceOrm)
    mock_instance_orm_initial.accession_id = self.MOCK_INSTANCE_ID
    mock_instance_orm_initial.properties_json = {
      "praxis_inventory_schema_version": "1.0",
      "consumable_state": "new",
    }
    self.mock_get_resource.return_value = mock_instance_orm_initial

    # This is what the service function should return
    mock_instance_orm_updated = MagicMock(spec=ResourceInstanceOrm)
    mock_instance_orm_updated.accession_id = self.MOCK_INSTANCE_ID

    request_payload_dict = {
      "praxis_inventory_schema_version": "1.0",
      "consumable_state": "partially_used",
      "last_updated_by": self.MOCK_USER_ID,
      "inventory_notes": "Updated by API test",
    }
    request_payload_model = ResourceInventoryDataIn(**request_payload_dict)

    # Simulate what properties_json will look like after service update
    # (service adds last_updated_at)
    final_properties_from_service = request_payload_model.model_dump(
      exclude_unset=True
    )  # Pydantic v2
    # For Pydantic v1: final_properties_from_service = request_payload_model.dict(exclude_unset=True)
    final_properties_from_service["last_updated_at"] = datetime.datetime.now(
      datetime.timezone.utc
    ).isoformat()  # This needs to be consistent
    mock_instance_orm_updated.properties_json = final_properties_from_service

    self.mock_update_lw_status.return_value = mock_instance_orm_updated

    with patch("praxis.backend.api.assets.datetime") as mock_dt:
      mock_now = datetime.datetime.now(datetime.timezone.utc)
      mock_dt.datetime.now.return_value = mock_now
      iso_now = mock_now.isoformat()

      response = client.put(
        f"/resource_instances/{self.MOCK_INSTANCE_ID}/inventory",
        json=request_payload_dict,
      )

    assert response.status_code == 200
    self.mock_get_resource.assert_called_once_with(
      self.mock_db_session, self.MOCK_INSTANCE_ID
    )

    # Check what update_resource_instance_location_and_status was called with
    expected_properties_for_service = request_payload_model.model_dump(
      exclude_unset=True
    )  # Pydantic v2
    # For Pydantic v1: expected_properties_for_service = request_payload_model.dict(exclude_unset=True)
    expected_properties_for_service["last_updated_at"] = iso_now
    self.mock_update_lw_status.assert_called_once_with(
      self.mock_db_session,
      resource_instance_accession_id=self.MOCK_INSTANCE_ID,
      properties_json_update=expected_properties_for_service,
    )

    # Check the response from the API
    expected_response_data = ResourceInventoryDataOut(
      **final_properties_from_service
    ).model_dump()  # Pydantic v2
    # For Pydantic v1: expected_response_data = ResourceInventoryDataOut(**final_properties_from_service).dict()
    assert response.json() == expected_response_data

  def test_update_resource_instance_inventory_not_found(self):
    self.mock_get_resource.return_value = None
    request_payload_dict = {
      "consumable_state": "used",
      "last_updated_by": self.MOCK_USER_ID,
    }
    response = client.put(
      f"/resource_instances/{self.MOCK_INSTANCE_ID}/inventory",
      json=request_payload_dict,
    )
    assert response.status_code == 404
    self.mock_get_resource.assert_called_once_with(
      self.mock_db_session, self.MOCK_INSTANCE_ID
    )
    self.mock_update_lw_status.assert_not_called()
