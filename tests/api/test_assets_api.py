import pytest
from unittest.mock import MagicMock, patch, ANY
import json
import datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

# Router to be tested
from praxis.backend.api.assets import router as assets_router

# Pydantic models for request/response validation and constructing test data
from praxis.backend.api.assets import LabwareInventoryDataIn, LabwareInventoryDataOut

# ORM Model mock for service layer
from praxis.backend.database_models.asset_management_orm import LabwareInstanceOrm


# Setup FastAPI app and TestClient
app = FastAPI()
app.include_router(assets_router) # Assuming default prefix, adjust if /api/assets is used in main app

client = TestClient(app)

# --- Test Class for Labware Instance Inventory API Endpoints ---
class TestLabwareInstanceInventoryAPI:
    MOCK_INSTANCE_ID = 123
    MOCK_USER_ID = "test_user_api"

    @pytest.fixture(autouse=True)
    def patch_dependencies(self, monkeypatch):
        # Mock the get_db dependency to avoid actual DB calls
        self.mock_db_session = MagicMock()
        mock_get_db = MagicMock(return_value=self.mock_db_session)
        monkeypatch.setattr("praxis.backend.api.assets.get_db", mock_get_db)

        # Mock the asset_data_service functions used by the API
        self.mock_get_labware_by_id = MagicMock()
        self.mock_update_lw_status = MagicMock()
        
        monkeypatch.setattr("praxis.backend.api.assets.asset_data_service.get_labware_instance_by_id", self.mock_get_labware_by_id)
        monkeypatch.setattr("praxis.backend.api.assets.asset_data_service.update_labware_instance_location_and_status", self.mock_update_lw_status)

    def test_get_labware_instance_inventory_success(self):
        mock_instance_orm = MagicMock(spec=LabwareInstanceOrm)
        inventory_dict = {
            "praxis_inventory_schema_version": "1.0",
            "reagents": [{"reagent_id": "R1", "initial_quantity": {"value": 10, "unit": "ml"}, "current_quantity": {"value": 5, "unit": "ml"}}],
            "item_count": {"initial_max_items": 96, "current_available_items": 90},
            "consumable_state": "partially_used",
            "last_updated_by": "user1",
            "inventory_notes": "Some notes",
            "last_updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        mock_instance_orm.properties_json = inventory_dict
        self.mock_get_labware_by_id.return_value = mock_instance_orm

        response = client.get(f"/labware_instances/{self.MOCK_INSTANCE_ID}/inventory")

        assert response.status_code == 200
        self.mock_get_labware_by_id.assert_called_once_with(self.mock_db_session, self.MOCK_INSTANCE_ID)
        
        # Validate against LabwareInventoryDataOut model structure
        expected_data = LabwareInventoryDataOut(**inventory_dict).model_dump() # Pydantic v2
        # For Pydantic v1: expected_data = LabwareInventoryDataOut(**inventory_dict).dict()
        assert response.json() == expected_data

    def test_get_labware_instance_inventory_not_found(self):
        self.mock_get_labware_by_id.return_value = None
        response = client.get(f"/labware_instances/{self.MOCK_INSTANCE_ID}/inventory")
        assert response.status_code == 404
        self.mock_get_labware_by_id.assert_called_once_with(self.mock_db_session, self.MOCK_INSTANCE_ID)

    def test_get_labware_instance_inventory_empty(self):
        mock_instance_orm = MagicMock(spec=LabwareInstanceOrm)
        mock_instance_orm.properties_json = None # Or {}
        self.mock_get_labware_by_id.return_value = mock_instance_orm

        response = client.get(f"/labware_instances/{self.MOCK_INSTANCE_ID}/inventory")
        assert response.status_code == 200
        # Expecting LabwareInventoryDataOut default values (all None)
        expected_empty_data = LabwareInventoryDataOut().model_dump() # Pydantic v2
        # For Pydantic v1: expected_empty_data = LabwareInventoryDataOut().dict()
        assert response.json() == expected_empty_data
        self.mock_get_labware_by_id.assert_called_once_with(self.mock_db_session, self.MOCK_INSTANCE_ID)

    def test_update_labware_instance_inventory_success(self):
        mock_instance_orm_initial = MagicMock(spec=LabwareInstanceOrm)
        mock_instance_orm_initial.id = self.MOCK_INSTANCE_ID
        mock_instance_orm_initial.properties_json = {"praxis_inventory_schema_version": "1.0", "consumable_state": "new"}
        self.mock_get_labware_by_id.return_value = mock_instance_orm_initial

        # This is what the service function should return
        mock_instance_orm_updated = MagicMock(spec=LabwareInstanceOrm)
        mock_instance_orm_updated.id = self.MOCK_INSTANCE_ID
        
        request_payload_dict = {
            "praxis_inventory_schema_version": "1.0",
            "consumable_state": "partially_used",
            "last_updated_by": self.MOCK_USER_ID,
            "inventory_notes": "Updated by API test"
        }
        request_payload_model = LabwareInventoryDataIn(**request_payload_dict)

        # Simulate what properties_json will look like after service update
        # (service adds last_updated_at)
        final_properties_from_service = request_payload_model.model_dump(exclude_unset=True) # Pydantic v2
        # For Pydantic v1: final_properties_from_service = request_payload_model.dict(exclude_unset=True) 
        final_properties_from_service["last_updated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat() # This needs to be consistent
        mock_instance_orm_updated.properties_json = final_properties_from_service
        
        self.mock_update_lw_status.return_value = mock_instance_orm_updated

        with patch("praxis.backend.api.assets.datetime") as mock_dt:
            mock_now = datetime.datetime.now(datetime.timezone.utc)
            mock_dt.datetime.now.return_value = mock_now
            iso_now = mock_now.isoformat()
            
            response = client.put(f"/labware_instances/{self.MOCK_INSTANCE_ID}/inventory", json=request_payload_dict)

        assert response.status_code == 200
        self.mock_get_labware_by_id.assert_called_once_with(self.mock_db_session, self.MOCK_INSTANCE_ID)
        
        # Check what update_labware_instance_location_and_status was called with
        expected_properties_for_service = request_payload_model.model_dump(exclude_unset=True) #Pydantic v2
        # For Pydantic v1: expected_properties_for_service = request_payload_model.dict(exclude_unset=True)
        expected_properties_for_service["last_updated_at"] = iso_now
        self.mock_update_lw_status.assert_called_once_with(
            self.mock_db_session,
            labware_instance_id=self.MOCK_INSTANCE_ID,
            properties_json_update=expected_properties_for_service
        )
        
        # Check the response from the API
        expected_response_data = LabwareInventoryDataOut(**final_properties_from_service).model_dump() # Pydantic v2
        # For Pydantic v1: expected_response_data = LabwareInventoryDataOut(**final_properties_from_service).dict()
        assert response.json() == expected_response_data


    def test_update_labware_instance_inventory_not_found(self):
        self.mock_get_labware_by_id.return_value = None
        request_payload_dict = {"consumable_state": "used", "last_updated_by": self.MOCK_USER_ID}
        response = client.put(f"/labware_instances/{self.MOCK_INSTANCE_ID}/inventory", json=request_payload_dict)
        assert response.status_code == 404
        self.mock_get_labware_by_id.assert_called_once_with(self.mock_db_session, self.MOCK_INSTANCE_ID)
        self.mock_update_lw_status.assert_not_called()
