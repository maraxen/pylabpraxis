# pylint: disable=redefined-outer-name, protected-access, too-many-arguments
"""Unit tests for the AssetManager."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pylabrobot.resources import Plate

from praxis.backend.models import (
  AssetRequirementModel,
  MachineStatusEnum,
  ResourceStatusEnum,
)
from praxis.backend.utils.errors import AssetAcquisitionError

# Import test constants from conftest
from .conftest import (
  TEST_DECK_RESOURCE_ID,
  TEST_MACHINE_ID,
  TEST_PROTOCOL_RUN_ID,
  TEST_RESOURCE_ID,
)


@pytest.mark.asyncio
class TestAssetManagerPrivateHelpers:
  """Tests for private helper methods in AssetManager."""

  @pytest.mark.parametrize(
    "details, expected",
    [({"num_items": 96}, 96), ({"items": [1, 2, 3]}, 3)],
  )
  def test_extract_num_items(self, asset_manager, details, expected):
    """Test _extract_num_items extracts item counts correctly."""
    result = asset_manager._extract_num_items(MagicMock(), details)
    assert result == expected

  @pytest.mark.parametrize(
    "details, expected",
    [({"ordering": "A1,B1,C1"}, "A1,B1,C1")],
  )
  def test_extract_ordering(self, asset_manager, details, expected):
    """Test _extract_ordering extracts ordering strings correctly."""
    result = asset_manager._extract_ordering(MagicMock(), details)
    assert result == expected

  @pytest.mark.parametrize(
    "plr_class, module_name, is_abstract, expected",
    [(Plate, "pylabrobot.resources.plate", False, True)],
  )
  def test_can_catalog_resource(
    self,
    asset_manager,
    plr_class,
    module_name,
    is_abstract,
    expected,
  ):
    """Test _can_catalog_resource logic for identifying catalogable resources."""
    mock_class = plr_class
    mock_class.__module__ = module_name
    with patch("inspect.isabstract", return_value=is_abstract):
      result = asset_manager._can_catalog_resource(mock_class)
      assert result == expected


@pytest.mark.asyncio
class TestAcquireMachine:
  """Tests for the acquire_machine method."""

  MACHINE_FQN = "pylabrobot.liquid_handling.ot_2.OT_2"

  async def test_acquire_available_machine_succeeds(
    self,
    asset_manager,
    mock_workcell_runtime,
    machine_orm_factory,
  ):
    machine_orm = machine_orm_factory()
    mock_plr_machine = MagicMock()
    mock_workcell_runtime.initialize_machine.return_value = mock_plr_machine
    with (
      patch("praxis.backend.services.list_machines") as mock_list,
      patch(
        "praxis.backend.services.update_machine_status",
      ) as mock_update,
    ):
      mock_list.side_effect = [[], [machine_orm]]
      mock_update.return_value = machine_orm
      result, obj_id, obj_type = await asset_manager.acquire_machine(
        TEST_PROTOCOL_RUN_ID,
        "my_robot",
        self.MACHINE_FQN,
      )
      assert obj_id == TEST_MACHINE_ID
      mock_update.assert_awaited_once()

  async def test_acquire_machine_fails_if_none_available(self, asset_manager):
    with patch("praxis.backend.services.list_machines", return_value=[]):
      with pytest.raises(AssetAcquisitionError):
        await asset_manager.acquire_machine(
          TEST_PROTOCOL_RUN_ID,
          "my_robot",
          self.MACHINE_FQN,
        )


@pytest.mark.asyncio
class TestAcquireResource:
  """Tests for the acquire_resource method."""

  RESOURCE_DEF_NAME = "some_plate_def"

  async def test_acquire_resource_from_storage_succeeds(
    self,
    asset_manager,
    mock_workcell_runtime,
    resource_definition_factory,
    resource_instance_factory,
  ):
    res_def = resource_definition_factory(name=self.RESOURCE_DEF_NAME)
    res_inst = resource_instance_factory(python_fqn=self.RESOURCE_DEF_NAME)
    mock_workcell_runtime.create_or_get_resource.return_value = MagicMock()
    with (
      patch("praxis.backend.services.list_resource_instances") as mock_list,
      patch(
        "praxis.backend.services.read_resource_definition",
        return_value=res_def,
      ),
      patch(
        "praxis.backend.services.update_resource_instance_location_and_status",
      ) as mock_update,
    ):
      mock_list.side_effect = [[], [], [res_inst]]
      mock_update.return_value = res_inst
      result, obj_id, obj_type = await asset_manager.acquire_resource(
        TEST_PROTOCOL_RUN_ID,
        "my_plate",
        self.RESOURCE_DEF_NAME,
      )
      assert obj_id == TEST_RESOURCE_ID
      mock_update.assert_awaited_once()

  async def test_acquire_resource_fails_if_none_found(self, asset_manager):
    with patch("praxis.backend.services.list_resource_instances", return_value=[]):
      with pytest.raises(AssetAcquisitionError):
        await asset_manager.acquire_resource(
          TEST_PROTOCOL_RUN_ID,
          "my_plate",
          self.RESOURCE_DEF_NAME,
        )


@pytest.mark.asyncio
class TestReleaseAssets:
  """Tests for release_machine and release_resource."""

  async def test_release_machine_succeeds(self, asset_manager, machine_orm_factory):
    machine_orm = machine_orm_factory(current_status=MachineStatusEnum.IN_USE)
    with (
      patch("praxis.backend.services.read_machine", return_value=machine_orm),
      patch(
        "praxis.backend.services.update_machine_status",
        return_value=machine_orm,
      ) as mock_update,
    ):
      await asset_manager.release_machine(TEST_MACHINE_ID)
      mock_update.assert_awaited_once()

  async def test_release_resource_succeeds(
    self,
    asset_manager,
    resource_instance_factory,
    resource_definition_factory,
  ):
    res_inst = resource_instance_factory(
      current_status=ResourceStatusEnum.IN_USE,
    )
    res_def = resource_definition_factory()
    with (
      patch(
        "praxis.backend.services.read_resource_instance",
        return_value=res_inst,
      ),
      patch(
        "praxis.backend.services.update_resource_instance_location_and_status",
        return_value=res_inst,
      ) as mock_update,
      patch(
        "praxis.backend.services.read_resource_definition",
        return_value=res_def,
      ),
    ):
      await asset_manager.release_resource(
        TEST_RESOURCE_ID,
        ResourceStatusEnum.AVAILABLE_IN_STORAGE,
      )
      mock_update.assert_awaited_once()


@pytest.mark.asyncio
class TestAcquireAssetDispatcher:
  """Tests for the high-level acquire_asset dispatcher method."""

  async def test_acquire_asset_dispatches_to_machine(self, asset_manager):
    """Test acquire_asset calls acquire_machine for an unknown type."""
    machine_fqn = "pylabrobot.some_machine.SomeMachine"
    # FIX: Instantiate with 'fqn' and remove old/incorrect fields.
    asset_req = AssetRequirementModel(
      accession_id=TEST_MACHINE_ID,
      name="my_robot",
      fqn=machine_fqn,
      optional=False,
    )
    with (
      patch(
        "praxis.backend.services.read_resource_definition",
        return_value=None,
      ),
      patch.object(
        asset_manager,
        "acquire_machine",
        new_callable=AsyncMock,
      ) as mock_acquire_machine,
    ):
      await asset_manager.acquire_asset(TEST_PROTOCOL_RUN_ID, asset_req)
      mock_acquire_machine.assert_awaited_once()

  async def test_acquire_asset_dispatches_to_resource(
    self,
    asset_manager,
    resource_definition_factory,
  ):
    """Test acquire_asset calls acquire_resource for a known resource definition."""
    resource_def_name = "my_plate_def"
    res_def = resource_definition_factory(name=resource_def_name)
    # FIX: Instantiate with 'fqn' and remove old/incorrect fields.
    asset_req = AssetRequirementModel(
      accession_id=TEST_RESOURCE_ID,
      name="my_plate",
      fqn=resource_def_name,
      optional=False,
    )
    with (
      patch(
        "praxis.backend.services.read_resource_definition",
        return_value=res_def,
      ),
      patch.object(
        asset_manager,
        "acquire_resource",
        new_callable=AsyncMock,
      ) as mock_acquire_resource,
    ):
      await asset_manager.acquire_asset(TEST_PROTOCOL_RUN_ID, asset_req)
      mock_acquire_resource.assert_awaited_once()

  async def test_acquire_asset_safeguard_for_uncataloged_deck(self, asset_manager):
    """Test acquire_asset raises an error if a Deck FQN is not in the resource catalog."""
    deck_fqn = "pylabrobot.resources.deck.Deck"
    # FIX: Instantiate with 'fqn' and remove old/incorrect fields.
    asset_req = AssetRequirementModel(
      accession_id=TEST_DECK_RESOURCE_ID,
      name="my_deck",
      fqn=deck_fqn,
      optional=False,
    )
    with (
      patch(
        "praxis.backend.services.read_resource_definition",
        return_value=None,
      ),
      patch("importlib.import_module"),
      patch(
        "builtins.issubclass",
        return_value=True,
      ),
    ):
      with pytest.raises(
        AssetAcquisitionError,
        match="appears to be a Deck but not found",
      ):
        await asset_manager.acquire_asset(TEST_PROTOCOL_RUN_ID, asset_req)
