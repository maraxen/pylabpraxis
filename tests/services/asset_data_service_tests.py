import pytest
from unittest.mock import MagicMock, patch, call, ANY
import datetime
import json  # For properties_json

# Import the service functions to be tested
from praxis.backend.services import asset_data_service

# Import ORM models (or mocks if preferred, but direct import is fine for type hints)
from praxis.backend.database_models.asset_management_orm import (
  ResourceInstanceOrm,
  ResourceDefinitionCatalogOrm,
  ResourceInstanceStatusEnum,
)

# Import Pydantic models from API layer for constructing test data
from praxis.backend.api.resources import ResourceInventoryDataIn

# For flag_modified
from sqlalchemy.orm.attributes import flag_modified


class TestResourceInstanceInventory:
  @pytest.fixture
  def mock_db_session(self):
    db_session = MagicMock()
    # If your service functions directly call db.add, db.commit, db.refresh
    db_session.add = MagicMock()
    db_session.commit = MagicMock()
    db_session.refresh = MagicMock()
    return db_session

  def test_add_resource_instance_with_inventory_properties(
    self, mock_db_session, caplog
  ):
    mock_resource_def = MagicMock(spec=ResourceDefinitionCatalogOrm)
    with patch(
      "praxis.backend.services.asset_data_service.get_resource_definition",
      return_value=mock_resource_def,
    ) as mock_get_def:
      sample_inventory_data = {
        "praxis_inventory_schema_version": "1.0",
        "reagents": [
          {
            "reagent_id": "R123",
            "initial_quantity": {"value": 100, "unit": "mL"},
            "current_quantity": {"value": 90, "unit": "mL"},
          }
        ],
        "item_count": {
          "item_type": "tip",
          "initial_max_items": 96,
          "current_available_items": 96,
        },
        "consumable_state": "new",
        "inventory_notes": "Fresh tips",
      }

      instance = asset_data_service.add_resource_instance(
        db=mock_db_session,
        user_assigned_name="TestLWInventory",
        name="test_plate_def",
        properties_json=sample_inventory_data,
        initial_status=ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
      )

      mock_get_def.assert_called_once_with(mock_db_session, "test_plate_def")

      # Check that db.add was called with an object that has the correct properties_json
      # The actual ResourceInstanceOrm object is created inside the function
      # So we need to check the object that db.add was called with.
      assert mock_db_session.add.call_count == 1
      added_instance_orm = mock_db_session.add.call_args[0][
        0
      ]  # Get the first positional argument of the first call

      assert isinstance(added_instance_orm, ResourceInstanceOrm)
      assert added_instance_orm.user_assigned_name == "TestLWInventory"
      assert added_instance_orm.name == "test_plate_def"
      assert added_instance_orm.properties_json == sample_inventory_data
      assert (
        added_instance_orm.current_status
        == ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE
      )

      mock_db_session.commit.assert_called_once()
      mock_db_session.refresh.assert_called_once_with(added_instance_orm)

      # Check log message
      assert (
        f"DEBUG: ADS: Setting properties_json for new resource instance 'TestLWInventory': {sample_inventory_data}"
        in caplog.text
      )

  @patch(
    "praxis.backend.services.asset_data_service.flag_modified"
  )  # Patch where it's used
  def test_update_resource_instance_properties_json(
    self, mock_flag_modified, mock_db_session, caplog
  ):
    mock_instance = MagicMock(spec=ResourceInstanceOrm)
    mock_instance.id = 1
    mock_instance.properties_json = {
      "existing_key": "old_value",
      "consumable_state": "used",
    }

    with patch(
      "praxis.backend.services.asset_data_service.get_resource_instance_by_id",
      return_value=mock_instance,
    ) as mock_get_instance:
      properties_update = {
        "reagents": [
          {
            "reagent_id": "R456",
            "initial_quantity": {"value": 50, "unit": "uL"},
            "current_quantity": {"value": 20, "unit": "uL"},
          }
        ],
        "consumable_state": "partially_used",  # This will overwrite
        "inventory_notes": "Updated notes",
      }

      updated_instance = (
        asset_data_service.update_resource_instance_location_and_status(
          db=mock_db_session,
          resource_instance_id=1,
          properties_json_update=properties_update,
        )
      )

      mock_get_instance.assert_called_once_with(mock_db_session, 1)

      # Assert that the properties_json attribute on the mock_instance was updated
      # The service function modifies the instance passed to it (which is our mock_instance)
      expected_merged_properties = {
        "existing_key": "old_value",  # Original key should remain
        "reagents": [
          {
            "reagent_id": "R456",
            "initial_quantity": {"value": 50, "unit": "uL"},
            "current_quantity": {"value": 20, "unit": "uL"},
          }
        ],
        "consumable_state": "partially_used",
        "inventory_notes": "Updated notes",
      }
      assert mock_instance.properties_json == expected_merged_properties

      mock_flag_modified.assert_called_once_with(mock_instance, "properties_json")

      mock_db_session.commit.assert_called_once()
      mock_db_session.refresh.assert_called_once_with(mock_instance)

      assert (
        updated_instance is mock_instance
      )  # Should return the same modified mock object

      # Check log message
      assert (
        f"DEBUG: ADS: Updating properties_json for resource instance ID 1: {properties_update}"
        in caplog.text
      )
