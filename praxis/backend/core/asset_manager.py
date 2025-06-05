# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-locals, too-many-branches, too-many-statements, E501, line-too-long
"""Manages the lifecycle and allocation of physical laboratory assets.

praxis/core/asset_manager.py

The AssetManager is responsible for managing the lifecycle and allocation
of physical laboratory assets (machines and resource instances). It interacts
with the AssetDataService for persistence and infers changes passed from
WorkcellRuntime to the database for live PyLabRobot object status updates.


"""

import importlib
import inspect
import pkgutil
from functools import partial
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union

import pylabrobot.resources

from pylabrobot.machines.machine import Machine
from pylabrobot.resources import (
  Carrier,
  Container,
  Coordinate,
  Deck,
  ItemizedResource,
  Lid,
  MFXCarrier,
  PetriDish,
  Plate,
  PlateAdapter,
  PlateCarrier,
  PlateHolder,
  Resource,
  ResourceHolder,
  ResourceStack,
  Tip,
  TipCarrier,
  TipRack,
  TipSpot,
  Trash,
  Trough,
  TroughCarrier,
  Tube,
  TubeCarrier,
  TubeRack,
  Well,
)
from sqlalchemy.ext.asyncio import AsyncSession

import praxis.backend.services as svc
from praxis.backend.core.workcell_runtime import WorkcellRuntime
from praxis.backend.models import (
  AssetRequirementModel,
  DeckConfigurationPositionItemOrm,
  DeckPositionDefinitionOrm,
  MachineCategoryEnum,
  MachineOrm,
  MachineStatusEnum,
  ResourceCategoryEnum,
  ResourceDefinitionCatalogOrm,
  ResourceInstanceOrm,
  ResourceInstanceStatusEnum,
)
from praxis.backend.utils.errors import AssetAcquisitionError
from praxis.backend.utils.logging import (
  get_logger,
  log_async_runtime_errors,
  log_runtime_errors,
)
from praxis.backend.utils.plr_inspection import get_constructor_params_with_defaults

logger = get_logger(__name__)

async_asset_manager_errors = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  raises_exception=AssetAcquisitionError,
)

asset_manager_errors = partial(
  log_runtime_errors,
  logger_instance=logger,
  raises_exception=AssetAcquisitionError,
)


class AssetManager:
  """Manages the lifecycle and allocation of assets."""

  def __init__(self, db_session: AsyncSession, workcell_runtime: WorkcellRuntime):
    """Initialize the AssetManager.

    Args:
        db_session: The SQLAlchemy async session.
        workcell_runtime: The WorkcellRuntime instance for live PLR object interaction.

    """
    self.db: AsyncSession = db_session
    self.workcell_runtime = workcell_runtime

    self.EXCLUDED_BASE_CLASSES: List[Type[Resource]] = [
      Carrier,
      Container,
      Deck,
      ItemizedResource,
      Lid,
      MFXCarrier,
      PetriDish,
      Plate,
      PlateAdapter,
      PlateCarrier,
      PlateHolder,
      Resource,
      ResourceHolder,
      ResourceStack,
      TipCarrier,
      TipRack,
      TipSpot,
      Trash,
      Trough,
      TroughCarrier,
      Tube,
      TubeCarrier,
      TubeRack,
      Well,
    ]

  @asset_manager_errors(
    prefix="AM_EXTRACT_NUM: ", suffix=" - Error extracting num_items"
  )
  def _extract_num_items(
    self,
    resource_class: Type[Resource],
    details: Optional[Dict[str, Any]],
  ) -> Optional[int]:
    """Extract the number of items (e.g., tips, wells, tubes) from serialized details.

    Relevant for ItemizedResource types.
    It checks for 'num_items', 'items', 'capacity', or 'wells' in serialized details.

    Args:
        resource_class: The class of the resource being processed, for logging context.
        details: The serialized details of the resource instance.

    Returns:
        An integer representing the number of items, or None.

    """
    num_items_value: Optional[int] = None
    if not details:
      logger.debug("AM_EXTRACT_NUM: No details provided for extraction.")
      return None
    if "num_items" in details and isinstance(details["num_items"], int):
      logger.debug(
        "AM_EXTRACT_NUM: Extracted from details['num_items'] for %s",
        resource_class.__name__,
      )
      num_items_value = int(details["num_items"])
    elif "items" in details and isinstance(details["items"], list):
      logger.debug(
        "AM_EXTRACT_NUM: Extracted from len(details['items']) for %s",
        resource_class.__name__,
      )
      num_items_value = len(details["items"])
    elif "wells" in details and isinstance(details["wells"], list):
      logger.debug(
        "AM_EXTRACT_NUM: Extracted from len(details['wells']) for %s",
        resource_class.__name__,
      )
      num_items_value = len(details["wells"])
    elif "capacity " in details and isinstance(details["capacity"], int):
      logger.debug(
        "AM_EXTRACT_NUM: Extracted from details['capacity'] for %s",
        resource_class.__name__,
      )
      num_items_value = int(details["capacity"])

    if num_items_value is None:
      logger.debug(
        "AM_EXTRACT_NUM: Number of items not found in details for %s.",
        resource_class.__name__,
      )

    return num_items_value

  @asset_manager_errors(
    prefix="AM_EXTRACT_ORDER: ", suffix=" - Error extracting ordering"
  )
  def _extract_ordering(
    self,
    resource_class: Type[Resource],
    details: Optional[Dict[str, Any]],
  ) -> Optional[str]:
    """Extract item names if ordered (e.g., wells in a plate) from serialized details.

    Args:
        resource_class: The class of the resource being processed, for logging context.
        details: The serialized details of the resource instance.

    Returns:
        A comma-separated string of item names if ordered, or an empty string if
        not found.

    """
    ordering_value = None
    if not details:
      logger.debug("AM_EXTRACT_ORDER: No details provided for extraction.")
      return None
    try:
      if "ordering" in details and isinstance(details["ordering"], str):
        logger.debug(
          "AM_EXTRACT_ORDER: Extracted from details['ordering'] for %s",
          resource_class.__name__,
        )
        ordering_value = details["ordering"]
      elif "wells" in details and isinstance(details["wells"], list):
        if all(isinstance(w, dict) and "name" in w for w in details["wells"]):
          logger.debug(
            "AM_EXTRACT_ORDER: Extracted from names in details['wells'] for %s",
            resource_class.__name__,
          )
          ordering_value = ",".join([w["name"] for w in details["wells"]])
      elif "items" in details and isinstance(details["items"], list):
        if all(isinstance(i, dict) and "name" in i for i in details["items"]):
          logger.debug(
            "AM_EXTRACT_ORDER: Extracted from names in details['items'] for %s",
            resource_class.__name__,
          )
          ordering_value = ",".join([i["name"] for i in details["items"]])

      if ordering_value is None:
        logger.debug(
          "AM_EXTRACT_ORDER: Ordering not found in details for %s.",
          resource_class.__name__,
        )
    except Exception as e:
      logger.exception(
        "AM_EXTRACT_ORDER: Error extracting ordering for %s: %s",
        resource_class.__name__,
        e,
      )
    return ordering_value

  @asset_manager_errors(
    prefix="AM_GET_CATEGORY: ", suffix=" - Error getting category from PLR object"
  )
  def _can_catalog_resource(self, plr_class: Type[Any]) -> bool:
    """Determine if a PyLabRobot class represents a resource definition to catalog.

    Args:
        plr_class: The class to check.

    Returns:
        True if the class should be cataloged, False otherwise.

    """
    if not inspect.isclass(plr_class) or not issubclass(plr_class, Resource):
      return False
    if inspect.isabstract(plr_class):
      return False
    if plr_class in self.EXCLUDED_BASE_CLASSES:
      return False
    if not plr_class.__module__.startswith("pylabrobot.resources"):
      return False
    return True

  @async_asset_manager_errors(
    prefix="AM_SYNC: ", suffix=" - Error syncing PyLabRobot definitions"
  )
  async def sync_pylabrobot_definitions(
    self, plr_resources_package=pylabrobot.resources
  ) -> Tuple[int, int]:
    """Scan and sync PyLabRobot resource definitions.

    Scan PyLabRobot's resources by introspecting modules and classes,
    then populate/update the ResourceDefinitionCatalogOrm.
    This method focuses on PLR Resources (resource). Machine discovery is separate.

    Args:
        plr_resources_package: The base PyLabRobot package to scan
        (default: pylabrobot.resources).

    Returns:
        A tuple (added_count, updated_count) of resource definitions.

    """
    logger.info(
      "AM_SYNC: Starting PyLabRobot resource definition sync from package: %s",
      plr_resources_package.__name__,
    )

    added_count = 0
    updated_count = 0
    processed_fqns: Set[str] = set()

    for _, modname, _ in pkgutil.walk_packages(
      path=plr_resources_package.__path__,  # type: ignore
      prefix=plr_resources_package.__name__ + ".",
      onerror=lambda x: logger.error("AM_SYNC: Error walking package %s", x),
    ):
      try:
        module = importlib.import_module(modname)
      except ImportError as e:
        logger.warning(
          "AM_SYNC: Could not import module %s during sync: %s", modname, e
        )
        continue

      for class_name, plr_class_obj in inspect.getmembers(module, inspect.isclass):
        fqn = f"{modname}.{class_name}"
        if fqn in processed_fqns:
          continue
        processed_fqns.add(fqn)

        logger.debug(
          "AM_SYNC: Found class %s. Checking if catalogable resource...", fqn
        )

        if not self._can_catalog_resource(plr_class_obj):
          logger.debug("AM_SYNC: Skipping %s - not a catalogable resource class.", fqn)
          continue

        logger.debug("AM_SYNC: Processing potential resource class: %s", fqn)
        temp_instance: Optional[Resource] = None
        serialized_data: Optional[Dict[str, Any]] = None
        can_instantiate = True

        kwargs_for_instantiation: Dict[str, Any] = {
          "name": f"praxis_sync_temp_{class_name}"
        }
        try:
          constructor_params = get_constructor_params_with_defaults(plr_class_obj)
          for param_name, param_info in constructor_params.items():
            if param_name in [
              "self",
              "name",
              "category",
              "model",
            ]:
              continue
            if param_info["required"] and param_info["default"] is None:
              param_type_str = param_info["type"].lower()
              if "optional[" in param_type_str:
                kwargs_for_instantiation[param_name] = None
              elif "str" in param_type_str:
                kwargs_for_instantiation[param_name] = f"default_{param_name}"
              elif "int" in param_type_str:
                kwargs_for_instantiation[param_name] = 0
              elif "float" in param_type_str:
                kwargs_for_instantiation[param_name] = 0.0
              elif "bool" in param_type_str:
                kwargs_for_instantiation[param_name] = False
              elif "list" in param_type_str:
                kwargs_for_instantiation[param_name] = []
              elif "dict" in param_type_str:
                kwargs_for_instantiation[param_name] = {}
              else:
                logger.info(
                  "AM_SYNC: Cannot auto-default required parameter '%s' of type '%s' for %s. "
                  "Instantiation might fail or be skipped.",
                  param_name,
                  param_info["type"],
                  fqn,
                )
          if can_instantiate:
            logger.debug(
              "AM_SYNC: Attempting instantiation of %s with kwargs: %s",
              fqn,
              kwargs_for_instantiation,
            )
            temp_instance = plr_class_obj(**kwargs_for_instantiation)
            if temp_instance is None:
              logger.warning(
                "AM_SYNC: Instantiation of %s returned None. This might"
                " indicate an issue with the class or its constructor.",
                fqn,
              )
              can_instantiate = False
            else:
              logger.debug(
                "AM_SYNC: Successfully instantiated %s with name: %s",
                fqn,
                temp_instance.name,
              )
              serialized_data = temp_instance.serialize()
              if "name" in serialized_data:
                del serialized_data["name"]
        except Exception as inst_err:
          logger.warning(
            "AM_SYNC: Instantiation or serialization of %s failed: %s. "
            "Will attempt to proceed with class-level data if possible, but some "
            "attributes might be missing.",
            fqn,
            inst_err,
            exc_info=True,
          )
          temp_instance = None
          serialized_data = None

        size_x = serialized_data.get("size_x") if serialized_data else None
        size_y = serialized_data.get("size_y") if serialized_data else None
        size_z = serialized_data.get("size_z") if serialized_data else None

        nominal_volume_ul: Optional[float] = None
        if serialized_data:
          if "max_volume" in serialized_data:
            nominal_volume_ul = float(serialized_data["max_volume"])
          elif (
            "wells" in serialized_data
            and isinstance(serialized_data["wells"], list)
            and serialized_data["wells"]
          ):
            first_well = serialized_data["wells"][0]
            if isinstance(first_well, dict) and "max_volume" in first_well:
              nominal_volume_ul = float(first_well["max_volume"])
          elif (
            "items" in serialized_data
            and isinstance(serialized_data["items"], list)
            and serialized_data["items"]
          ):
            first_item = serialized_data["items"][0]
            if isinstance(first_item, dict) and "volume" in first_item:
              nominal_volume_ul = float(first_item["volume"])

        model_name = serialized_data.get("model") if serialized_data else None
        if not model_name and serialized_data and serialized_data.get("type"):
          model_name = serialized_data.get("type")
        elif not model_name:
          model_name = class_name

        pylabrobot_def_name = model_name
        if not pylabrobot_def_name:
          pylabrobot_def_name = fqn
          logger.warning(
            "AM_SYNC: Using FQN '%s' as pylabrobot_def_name for %s due to missing model/type.",
            fqn,
            class_name,
          )

        category = serialized_data.get("category") if serialized_data else None
        if not category:
          category = ResourceCategoryEnum.OTHER.value
          logger.debug("AM_SYNC: Used fallback category '%s' for %s", category, fqn)

        num_items = self._extract_num_items(plr_class_obj, serialized_data)
        ordering_str = self._extract_ordering(plr_class_obj, serialized_data)

        details_for_db = serialized_data if serialized_data is not None else {}
        if num_items is not None and "praxis_extracted_num_items" not in details_for_db:
          details_for_db["praxis_extracted_num_items"] = num_items
        if (
          ordering_str is not None and "praxis_extracted_ordering" not in details_for_db
        ):
          details_for_db["praxis_extracted_ordering"] = ordering_str

        description = inspect.getdoc(plr_class_obj) or fqn

        is_consumable = category in ResourceCategoryEnum.consumables()

        praxis_type_name = model_name

        logger.debug(
          "AM_SYNC: Preparing to save/update %s (FQN: %s): Category=%s, Model=%s, Vol=%s, "
          "X=%s, Y=%s, Z=%s, NumItems=%s, Ordering=%s...",
          pylabrobot_def_name,
          fqn,
          category,
          model_name,
          nominal_volume_ul,
          size_x,
          size_y,
          size_z,
          num_items,
          "Present" if ordering_str else "N/A",
        )

        try:
          existing_def_orm = await svc.get_resource_definition(
            self.db, pylabrobot_def_name
          )
          await svc.add_or_update_resource_definition(
            db=self.db,
            name=pylabrobot_def_name,
            python_fqn=fqn,
            resource_type=praxis_type_name,
            description=description,
            is_consumable=is_consumable,
            nominal_volume_ul=nominal_volume_ul,
            # TODO: Add material and manufacturer if discoverable from PLR or config
            plr_definition_details_json=details_for_db,
          )
          if not existing_def_orm:
            added_count += 1
            logger.info(
              "AM_SYNC: Added new resource definition: %s", pylabrobot_def_name
            )
          else:
            updated_count += 1
            logger.info(
              "AM_SYNC: Updated existing resource definition: %s", pylabrobot_def_name
            )

        except Exception as e_proc:
          logger.exception(
            "AM_SYNC: Could not process or save PLR class '%s' (Def Name: %s): %s",
            fqn,
            pylabrobot_def_name,
            e_proc,
          )
        finally:
          if temp_instance:
            del temp_instance
            del serialized_data

    logger.info(
      "AM_SYNC: Resource definition sync complete. Added: %d, Updated: %d",
      added_count,
      updated_count,
    )
    return added_count, updated_count

  async def apply_deck_configuration(
    self, deck_orm_id: int, protocol_run_guid: str
  ) -> Deck:
    """Apply a deck configuration.

    Initialize the deck and assign pre-configured resources.

    Args:
        deck_orm_id: The ORM ID of the deck.
        protocol_run_guid: The GUID of the current protocol run.

    Returns:
        The live PyLabRobot Deck object.

    Raises:
        AssetAcquisitionError: If the deck or its components cannot be configured.

    """
    logger.info(
      "AM_DECK_CONFIG: Applying deck configuration for '%s', run_guid: %s",
      deck_orm_id,
      protocol_run_guid,
    )

    deck_orm = await svc.get_deck_by_id(self.db, deck_orm_id)
    if not deck_orm:
      raise AssetAcquisitionError(f"Deck '{deck_orm_id}' not found in database.")

    deck_machines_orm = await svc.list_machines(self.db)

    actual_deck_machine_orm: Optional[MachineOrm] = None
    for dev_orm in deck_machines_orm:
      # TODO: Refine deck identification.
      if "Deck" in dev_orm.python_fqn:
        try:
          module_path, class_n = dev_orm.python_fqn.rsplit(".", 1)
          module = importlib.import_module(module_path)
          cls_obj = getattr(module, class_n)
          if issubclass(cls_obj, Deck):
            actual_deck_machine_orm = dev_orm
            break
        except (ImportError, AttributeError, ValueError) as e:
          logger.warning(
            "Could not verify class for machine %s (FQN: %s): %s",
            dev_orm.user_friendly_name,
            dev_orm.python_fqn,
            e,
          )

    if not actual_deck_machine_orm:
      raise AssetAcquisitionError(
        f"No Machine found and verified as a PLR Deck for deck name '{deck_orm.name}'."
      )

    deck_machine_orm = actual_deck_machine_orm

    if (
      deck_machine_orm.current_status == MachineStatusEnum.IN_USE
      and deck_machine_orm.current_protocol_run_guid != protocol_run_guid
    ):
      raise AssetAcquisitionError(
        f"Deck machine '{deck_orm.name}' (ID: {deck_machine_orm.id}) is already in use by "
        f"another run '{deck_machine_orm.current_protocol_run_guid}'."
      )

    live_plr_deck_object = await self.workcell_runtime.initialize_machine(
      deck_machine_orm
    )
    if not live_plr_deck_object or not isinstance(live_plr_deck_object, Deck):
      raise AssetAcquisitionError(
        f"Failed to initialize backend for deck '{deck_orm.name}' (ID: "
        f"{deck_machine_orm.id}) or it's not a Deck. Check WorkcellRuntime."
      )

    await svc.update_machine_status(
      self.db,
      deck_machine_orm.id,
      MachineStatusEnum.IN_USE,
      current_protocol_run_guid=protocol_run_guid,
      status_details=f"Deck '{deck_orm.name}' in use by run {protocol_run_guid}",
    )
    logger.info(
      "AM_DECK_CONFIG: Deck machine '%s' (ID: %s) backend initialized and marked IN_USE.",
      deck_orm.name,
      deck_machine_orm.id,
    )

    deck_positions_orm = await svc.get_position_definitions_for_deck_type(
      self.db, deck_orm.id
    )
    logger.info(
      "AM_DECK_CONFIG: Found %d positions for deck layout '%s' (Layout ID: %s).",
      len(deck_positions_orm),
      deck_orm.name,
      deck_orm.id,
    )

    for position_orm in deck_positions_orm:
      # Pylance reports "resource_instance_id" is unknown on DeckPositionDefinitionOrm.
      # Assuming it should exist and is used for linking.
      if position_orm.resource_instance_id:  # type: ignore
        resource_instance_id = position_orm.resource_instance_id  # type: ignore
        logger.info(
          "AM_DECK_CONFIG: Processing position '%s' with pre-assigned resource ID: %s.",
          position_orm.position_id,
          resource_instance_id,
        )

        resource_instance_orm = await svc.get_resource_instance_by_id(
          self.db, resource_instance_id
        )
        if not resource_instance_orm:
          logger.error(
            "Resource instance %s for position '%s' not found. Skipping.",
            resource_instance_id,
            position_orm.position_id,
          )
          continue

        if (
          resource_instance_orm.current_status == ResourceInstanceStatusEnum.IN_USE
          and resource_instance_orm.current_protocol_run_guid == protocol_run_guid
          and resource_instance_orm.location_machine_id == deck_machine_orm.id
          and resource_instance_orm.current_deck_position_name
          == position_orm.position_id
        ):
          logger.info(
            "Resource %s already configured at '%s' for this run.",
            resource_instance_id,
            position_orm.position_id,
          )
          continue

        if resource_instance_orm.current_status not in [
          ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
          ResourceInstanceStatusEnum.AVAILABLE_ON_DECK,
        ]:
          raise AssetAcquisitionError(
            f"Resource {resource_instance_id} for position '{position_orm.position_id}' "
            f"unavailable (status: {resource_instance_orm.current_status})."
          )

        resource_def_orm = await svc.get_resource_definition(
          self.db, resource_instance_orm.name
        )
        if not resource_def_orm or not resource_def_orm.python_fqn:
          raise AssetAcquisitionError(
            f"Python FQN not found for resource definition '{resource_instance_orm.name}' "
            f"(instance {resource_instance_id})."
          )

        live_plr_resource = await self.workcell_runtime.create_or_get_resource(
          resource_instance_orm=resource_instance_orm,
          resource_definition_fqn=resource_def_orm.python_fqn,
        )
        if not live_plr_resource:
          raise AssetAcquisitionError(
            f"Failed to create PLR object for resource {resource_instance_id} "
            f"at '{position_orm.position_id}'."
          )

        logger.info(
          "Assigning resource '%s' to position '%s'.",
          live_plr_resource.name,
          position_orm.position_id,
        )

        await self.workcell_runtime.assign_resource_to_deck(
          resource_instance_orm_id=resource_instance_id,
          target=deck_machine_orm.id,  # Ensured target is int
          position_id=position_orm.position_id,
        )

        await svc.update_resource_instance_location_and_status(
          db=self.db,
          resource_instance_id=resource_instance_id,
          new_status=ResourceInstanceStatusEnum.IN_USE,
          current_protocol_run_guid=protocol_run_guid,
          location_machine_id=deck_machine_orm.id,
          current_deck_position_name=position_orm.position_id,
          status_details=f"On deck '{deck_orm.name}' position "
          f"'{position_orm.position_id}' for run {protocol_run_guid}",
        )
        logger.info(
          "Resource %s configured at '%s'.",
          resource_instance_id,
          position_orm.position_id,
        )

    logger.info(
      "AM_DECK_CONFIG: Deck configuration for '%s' applied successfully.", deck_orm.name
    )
    return live_plr_deck_object

  async def acquire_machine(
    self,
    protocol_run_guid: str,
    requested_asset_name_in_protocol: str,
    python_fqn_constraint: str,
    constraints: Optional[Dict[str, Any]] = None,
  ) -> Tuple[Any, int, str]:
    """Acquire a Machine that is available or already in use by the current run.

    Args:
        protocol_run_guid: GUID of the protocol run.
        requested_asset_name_in_protocol: Name of the asset as requested in the protocol.
        python_fqn_constraint: The FQN of the PyLabRobot Machine class.
        constraints: Optional dictionary of constraints (e.g., specific serial number).

    Returns:
        A tuple (live_plr_machine_object, machine_orm_id, "machine").

    Raises:
        AssetAcquisitionError: If no suitable machine can be acquired or initialized.
    """
    logger.info(
      "AM_ACQUIRE_DEVICE: Acquiring machine '%s' (PLR Class FQN: '%s') for run '%s'. "
      "Constraints: %s",
      requested_asset_name_in_protocol,
      python_fqn_constraint,
      protocol_run_guid,
      constraints,
    )

    # TODO: Implement constraint matching if `constraints` are provided (e.g., serial_number)

    selected_machine_orm: Optional[MachineOrm] = None

    # 1. Check if a suitable machine is already in use by this run
    in_use_by_this_run_list = await svc.list_machines(
      self.db,
      pylabrobot_class_filter=python_fqn_constraint,
      status=MachineStatusEnum.IN_USE,
      current_protocol_run_guid_filter=protocol_run_guid,
      # property_filters is not supported on svc.list_machines currently
    )
    if in_use_by_this_run_list:
      selected_machine_orm = in_use_by_this_run_list[0]
      logger.info(
        "AM_ACQUIRE_DEVICE: Device '%s' (ID: %s) is already IN_USE by this run '%s'. Re-acquiring.",
        selected_machine_orm.user_friendly_name,
        selected_machine_orm.id,
        protocol_run_guid,
      )
    else:
      # 2. If not, find an available one
      available_machines_list = await svc.list_machines(
        self.db,
        status=MachineStatusEnum.AVAILABLE,
        pylabrobot_class_filter=python_fqn_constraint,
        # property_filters is not supported on svc.list_machines currently
      )
      if available_machines_list:
        selected_machine_orm = available_machines_list[0]
        logger.info(
          "AM_ACQUIRE_DEVICE: Found available machine '%s' (ID: %s).",
          selected_machine_orm.user_friendly_name,
          selected_machine_orm.id,
        )
      else:
        raise AssetAcquisitionError(
          f"No machine found matching PLR class FQN '{python_fqn_constraint}' with status AVAILABLE, "
          "nor already in use by this run."
        )

    if not selected_machine_orm:  # Pylance might still warn here, but logic handles it
      raise AssetAcquisitionError(
        f"Device selection failed for '{requested_asset_name_in_protocol}'."
      )

    logger.info(
      "AM_ACQUIRE_DEVICE: Attempting to initialize backend for selected machine '%s' "
      "(ID: %s) via WorkcellRuntime.",
      selected_machine_orm.user_friendly_name,
      selected_machine_orm.id,
    )
    live_plr_machine = await self.workcell_runtime.initialize_machine(
      selected_machine_orm
    )

    if not live_plr_machine:
      error_msg = (
        f"Failed to initialize backend for machine '{selected_machine_orm.user_friendly_name}' "
        f"(ID: {selected_machine_orm.id}). Check WorkcellRuntime logs and machine status in DB."
      )
      logger.error(error_msg)
      await svc.update_machine_status(
        self.db,
        selected_machine_orm.id,
        MachineStatusEnum.ERROR,
        status_details=f"Backend initialization failed for run {protocol_run_guid}: {error_msg[:200]}",
      )
      raise AssetAcquisitionError(error_msg)

    logger.info(
      "AM_ACQUIRE_DEVICE: Backend for machine '%s' initialized. "
      "Marking as IN_USE for run '%s' (if not already).",
      selected_machine_orm.user_friendly_name,
      protocol_run_guid,
    )

    if (
      selected_machine_orm.current_status != MachineStatusEnum.IN_USE
      or selected_machine_orm.current_protocol_run_guid != protocol_run_guid
    ):
      updated_machine_orm = await svc.update_machine_status(
        self.db,
        selected_machine_orm.id,
        MachineStatusEnum.IN_USE,
        current_protocol_run_guid=protocol_run_guid,
        status_details=f"In use by run {protocol_run_guid}",
      )
      if not updated_machine_orm:
        critical_error_msg = (
          f"CRITICAL: Device '{selected_machine_orm.user_friendly_name}' backend is live, "
          f"but FAILED to update its DB status to IN_USE for run '{protocol_run_guid}'."
        )
        logger.error(critical_error_msg)
        raise AssetAcquisitionError(critical_error_msg)
      logger.info(
        "AM_ACQUIRE_DEVICE: Device '%s' (ID: %s) successfully acquired and backend initialized for run '%s'.",
        updated_machine_orm.user_friendly_name,
        updated_machine_orm.id,
        protocol_run_guid,
      )
    else:
      logger.info(
        "AM_ACQUIRE_DEVICE: Device '%s' (ID: %s) was already correctly marked IN_USE by this run.",
        selected_machine_orm.user_friendly_name,
        selected_machine_orm.id,
      )

    return live_plr_machine, selected_machine_orm.id, "machine"

  async def acquire_resource(
    self,
    protocol_run_guid: str,
    requested_asset_name_in_protocol: str,
    name_constraint: str,
    user_choice_instance_id: Optional[int] = None,
    location_constraints: Optional[Dict[str, Any]] = None,
    property_constraints: Optional[Dict[str, Any]] = None,
  ) -> Tuple[Any, int, str]:
    """Acquire a resource instance that is available or in use by the current run.

    Args:
        protocol_run_guid: GUID of the protocol run.
        requested_asset_name_in_protocol: Name of the asset as requested in the
        protocol.
        name_constraint: The `name` from `ResourceDefinitionCatalogOrm`.
        user_choice_instance_id: Optional specific ID of the resource instance to
        acquire.
        location_constraints: Optional constraints on where the resource should be
        (primarily for deck assignment).
        property_constraints: Optional constraints on resource properties.

    Returns:
        A tuple (live_plr_resource_object, resource_instance_orm_id, "resource").

    Raises:
        AssetAcquisitionError: If no suitable resource can be acquired or initialized.

    """
    logger.info(
      "AM_ACQUIRE_LABWARE: Acquiring resource '%s' (PLR Def Name Constraint: '%s') for run '%s'. "
      "User Choice ID: %s, Location Constraints: %s, Property Constraints: %s",
      requested_asset_name_in_protocol,
      name_constraint,
      protocol_run_guid,
      user_choice_instance_id,
      location_constraints,
      property_constraints,
    )

    resource_instance_to_acquire: Optional[ResourceInstanceOrm] = None

    if user_choice_instance_id:
      instance_orm = await svc.get_resource_instance_by_id(
        self.db, user_choice_instance_id
      )
      if not instance_orm:
        raise AssetAcquisitionError(
          f"Specified resource instance ID {user_choice_instance_id} not found."
        )
      if instance_orm.name != name_constraint:
        raise AssetAcquisitionError(
          f"Chosen resource instance ID {user_choice_instance_id} (Definition: "
          f"'{instance_orm.name}') does not match definition constraint "
          f"'{name_constraint}'."
        )
      if instance_orm.current_status == ResourceInstanceStatusEnum.IN_USE:
        if instance_orm.current_protocol_run_guid != protocol_run_guid:
          raise AssetAcquisitionError(
            f"Chosen resource instance ID {user_choice_instance_id} is IN_USE by "
            f"another run ('{instance_orm.current_protocol_run_guid}')."
          )
        logger.info(
          "AM_ACQUIRE_LABWARE: Resource instance ID %s is already IN_USE by this run '%s'. Re-acquiring.",
          user_choice_instance_id,
          protocol_run_guid,
        )
        resource_instance_to_acquire = instance_orm
      elif instance_orm.current_status not in [
        ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
        ResourceInstanceStatusEnum.AVAILABLE_ON_DECK,
      ]:
        raise AssetAcquisitionError(
          f"Chosen resource instance ID {user_choice_instance_id} is not available "
          f"(status: {instance_orm.current_status.name})."
        )
      else:
        resource_instance_to_acquire = instance_orm
    else:
      in_use_list = await svc.list_resource_instances(
        self.db,
        name=name_constraint,
        status=ResourceInstanceStatusEnum.IN_USE,
        current_protocol_run_guid_filter=protocol_run_guid,
        property_filters=property_constraints,
      )
      if in_use_list:
        resource_instance_to_acquire = in_use_list[0]
        logger.info(
          "AM_ACQUIRE_LABWARE: Resource instance '%s' (ID: %s) is already IN_USE by this run '%s'. Re-acquiring.",
          resource_instance_to_acquire.user_assigned_name,
          resource_instance_to_acquire.id,
          protocol_run_guid,
        )
      else:
        on_deck_list = await svc.list_resource_instances(
          self.db,
          name=name_constraint,
          status=ResourceInstanceStatusEnum.AVAILABLE_ON_DECK,
          property_filters=property_constraints,
        )
        if on_deck_list:
          resource_instance_to_acquire = on_deck_list[0]
        else:
          in_storage_list = await svc.list_resource_instances(
            self.db,
            name=name_constraint,
            status=ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
            property_filters=property_constraints,
          )
          if in_storage_list:
            resource_instance_to_acquire = in_storage_list[0]

      if not resource_instance_to_acquire:
        raise AssetAcquisitionError(
          f"No resource instance found matching definition '{name_constraint}' "
          f"and properties {property_constraints} that is available or already in use "
          f"by this run."
        )

    # Assert that resource_instance_to_acquire is not None after selection logic
    assert (
      resource_instance_to_acquire is not None
    ), f"Resource acquisition failed for {requested_asset_name_in_protocol} after selection."

    resource_def_orm = await svc.get_resource_definition(
      self.db, resource_instance_to_acquire.name
    )
    if not resource_def_orm or not resource_def_orm.python_fqn:
      error_msg = (
        f"Python FQN not found for resource definition "
        f"'{resource_instance_to_acquire.name}' for instance ID "
        f"{resource_instance_to_acquire.id}."
      )
      logger.error(error_msg)
      await svc.update_resource_instance_location_and_status(
        db=self.db,
        resource_instance_id=resource_instance_to_acquire.id,
        new_status=ResourceInstanceStatusEnum.ERROR,
        status_details=error_msg[:200],
      )
      raise AssetAcquisitionError(error_msg)
    resource_fqn = resource_def_orm.python_fqn

    logger.info(
      "AM_ACQUIRE_LABWARE: Attempting to create/get PLR object for resource instance '%s' (ID: %s) using FQN '%s'.",
      resource_instance_to_acquire.user_assigned_name,
      resource_instance_to_acquire.id,
      resource_fqn,
    )
    live_plr_resource = await self.workcell_runtime.create_or_get_resource(
      resource_instance_orm=resource_instance_to_acquire,
      resource_definition_fqn=resource_fqn,
    )
    if not live_plr_resource:
      error_msg = (
        f"Failed to create/get PLR object for resource "
        f"'{resource_instance_to_acquire.user_assigned_name}' (ID: "
        f"{resource_instance_to_acquire.id}). Check WorkcellRuntime logs."
      )
      logger.error(error_msg)
      await svc.update_resource_instance_location_and_status(
        db=self.db,
        resource_instance_id=resource_instance_to_acquire.id,
        new_status=ResourceInstanceStatusEnum.ERROR,
        status_details=f"PLR object creation failed: {error_msg[:150]}",
      )
      raise AssetAcquisitionError(error_msg)

    logger.info(
      "AM_ACQUIRE_LABWARE: PLR object for resource '%s' created/retrieved. "
      "Updating status to IN_USE (if not already by this run) and handling location.",
      resource_instance_to_acquire.user_assigned_name,
    )

    target_deck_orm_id: Optional[int] = None
    target_position_name: Optional[str] = None
    final_status_details = f"In use by run {protocol_run_guid}"

    if location_constraints and isinstance(location_constraints, dict):
      deck_name = location_constraints.get("deck_name")
      position_name = location_constraints.get("position_name")
      if deck_name and position_name:
        logger.info(
          "AM_ACQUIRE_LABWARE: Location constraint: place '%s' on deck '%s' position '%s'.",
          live_plr_resource.name,
          deck_name,
          position_name,
        )
        deck_machines = await svc.list_machines(
          self.db, user_friendly_name_filter=deck_name
        )
        if not deck_machines:
          raise AssetAcquisitionError(
            f"Deck machine '{deck_name}' specified in location_constraints not found."
          )
        deck_machine_orm = deck_machines[0]
        target_deck_orm_id = deck_machine_orm.id
        target_position_name = position_name

        await self.workcell_runtime.assign_resource_to_deck(
          resource_instance_orm_id=resource_instance_to_acquire.id,
          target=target_deck_orm_id,
          position_id=target_position_name,
        )
        final_status_details = f"On deck '{deck_name}' position '{position_name}' for \
          run {protocol_run_guid}"
        logger.info(
          "AM_ACQUIRE_LABWARE: Resource assigned to deck '%s' position '%s' in "
          "WorkcellRuntime.",
          deck_name,
          position_name,
        )
      elif deck_name or position_name:
        raise AssetAcquisitionError(
          f"Partial location constraint for '{requested_asset_name_in_protocol}'. Both "
          f"'deck_name' and 'position_name' required if placing on deck."
        )

    if not (
      resource_instance_to_acquire.current_status == ResourceInstanceStatusEnum.IN_USE
      and resource_instance_to_acquire.current_protocol_run_guid == protocol_run_guid
      and (
        not target_deck_orm_id
        or resource_instance_to_acquire.location_machine_id == target_deck_orm_id
      )
      and (
        not target_position_name
        or resource_instance_to_acquire.current_deck_position_name
        == target_position_name
      )
    ):
      updated_resource_instance_orm = (
        await svc.update_resource_instance_location_and_status(
          self.db,
          resource_instance_id=resource_instance_to_acquire.id,
          new_status=ResourceInstanceStatusEnum.IN_USE,
          current_protocol_run_guid=protocol_run_guid,
          location_machine_id=target_deck_orm_id,
          current_deck_position_name=target_position_name,
          status_details=final_status_details,
        )
      )
      if not updated_resource_instance_orm:
        critical_error_msg = (
          f"CRITICAL: Resource '{resource_instance_to_acquire.user_assigned_name}' PLR "
          f"object created/assigned, "
          f"but FAILED to update its DB status/location for run '{protocol_run_guid}'."
        )
        logger.error(critical_error_msg)
        raise AssetAcquisitionError(critical_error_msg)
      logger.info(
        "AM_ACQUIRE_LABWARE: Resource '%s' (ID: %s) successfully acquired for run '%s'."
        "Status: IN_USE. "
        "Location Device ID: %s, Slot: %s.",
        updated_resource_instance_orm.user_assigned_name,
        updated_resource_instance_orm.id,
        protocol_run_guid,
        target_deck_orm_id,
        target_position_name,
      )
    else:
      logger.info(
        "AM_ACQUIRE_LABWARE: Resource '%s' (ID: %s) was already correctly set as "
        "IN_USE by this run, "
        "and at the target location if specified.",
        resource_instance_to_acquire.user_assigned_name,
        resource_instance_to_acquire.id,
      )

    return live_plr_resource, resource_instance_to_acquire.id, "resource"

  async def release_machine(
    self,
    machine_orm_id: int,
    final_status: MachineStatusEnum = MachineStatusEnum.AVAILABLE,
    status_details: Optional[str] = "Released from run",
  ):
    """Release a machine, update status, and shut down its backend via WorkcellRuntime.

    Args:
        machine_orm_id: The ORM ID of the machine to release.
        final_status: The status to set after release (default: AVAILABLE).
        status_details: Optional details about the release.

    Raises:
        AssetReleaseError: If the machine cannot be released or updated in the DB.

    """
    logger.info(
      "AM_RELEASE_DEVICE: Releasing machine ID %s. Target status: %s. Details: %s",
      machine_orm_id,
      final_status.name,
      status_details,
    )
    await self.workcell_runtime.shutdown_machine(machine_orm_id)
    logger.info(
      "AM_RELEASE_DEVICE: WorkcellRuntime shutdown initiated for machine ID %s.",
      machine_orm_id,
    )

    updated_machine = await svc.update_machine_status(
      self.db,
      machine_orm_id,
      final_status,
      status_details=status_details,
      current_protocol_run_guid=None,
    )
    if not updated_machine:
      logger.error(
        "AM_RELEASE_DEVICE: Failed to update status for machine ID %s in DB after "
        "backend shutdown.",
        machine_orm_id,
      )
    else:
      logger.info(
        "AM_RELEASE_DEVICE: Device ID %s status updated to %s in DB.",
        machine_orm_id,
        final_status.name,
      )

  async def release_resource(
    self,
    resource_instance_orm_id: int,
    final_status: ResourceInstanceStatusEnum,
    final_properties_json_update: Optional[Dict[str, Any]] = None,
    clear_from_deck_machine_id: Optional[int] = None,
    clear_from_position_name: Optional[str] = None,
    status_details: Optional[str] = "Released from run",
  ):
    """Release a resource instance.

    Release resource, updating its status and properties,
    and clearing it from a deck position via WorkcellRuntime if specified.

    Args:
        resource_instance_orm_id: The ORM ID of the resource instance to release.
        final_status: The status to set after release (e.g., AVAILABLE_IN_STORAGE).
        final_properties_json_update: Optional properties to update in JSON format.
        clear_from_deck_machine_id: Optional ID of the deck MachineOrm to clear from.
        clear_from_position_name: Optional position name on the deck to clear from.
        status_details: Optional details about the release.

    Raises:
        AssetReleaseError: If the resource cannot be released or updated in the DB.

    """
    logger.info(
      "AM_RELEASE_LABWARE: Releasing resource ID %s. Target status: %s. Details: %s",
      resource_instance_orm_id,
      final_status.name,
      status_details,
    )
    if final_properties_json_update:
      logger.info(
        "AM_RELEASE_LABWARE: Update properties for instance ID %s: %s",
        resource_instance_orm_id,
        final_properties_json_update,
      )

    if clear_from_deck_machine_id is not None and clear_from_position_name is not None:
      logger.info(
        "AM_RELEASE_LABWARE: Clearing resource ID %s from deck ID %s, position '%s' "
        "via WorkcellRuntime.",
        resource_instance_orm_id,
        clear_from_deck_machine_id,
        clear_from_position_name,
      )
      await self.workcell_runtime.clear_deck_position(
        deck_machine_orm_id=clear_from_deck_machine_id,
        position_name=clear_from_position_name,
        resource_instance_orm_id=resource_instance_orm_id,
      )
    else:
      await self.workcell_runtime.clear_resource_instance(resource_instance_orm_id)

    final_location_machine_id_for_ads: Optional[int] = None
    final_deck_position_name_for_ads: Optional[str] = None
    if final_status == ResourceInstanceStatusEnum.AVAILABLE_ON_DECK:
      final_location_machine_id_for_ads = clear_from_deck_machine_id
      final_deck_position_name_for_ads = clear_from_position_name

    updated_resource = await svc.update_resource_instance_location_and_status(
      self.db,
      resource_instance_id=resource_instance_orm_id,
      new_status=final_status,
      properties_json_update=final_properties_json_update,
      location_machine_id=final_location_machine_id_for_ads,
      current_deck_position_name=final_deck_position_name_for_ads,
      current_protocol_run_guid=None,
      status_details=status_details,
    )
    if not updated_resource:
      logger.error(
        "AM_RELEASE_LABWARE: Failed to update final status/location for resource ID %s "
        "in DB.",
        resource_instance_orm_id,
      )
    else:
      logger.info(
        "AM_RELEASE_LABWARE: Resource ID %s status updated to %s in DB.",
        resource_instance_orm_id,
        final_status.name,
      )

  async def acquire_asset(
    self, protocol_run_guid: str, asset_requirement: AssetRequirementModel
  ) -> Tuple[Any, int, str]:
    """Dispatch asset acquisition to either acquire_machine or acquire_resource.

    The `asset_requirement.actual_type_str` is key:
    - If it matches a `name` in `ResourceDefinitionCatalogOrm`, it's resource.
    - Otherwise, it's assumed to be a PLR Machine FQN (machine).

    Args:
        protocol_run_guid: GUID of the protocol run.
        asset_requirement: The asset requirement model containing details.

    Returns:
        A tuple (live_plr_object, asset_orm_id, "machine" or "resource").

    """
    logger.info(
      "AM_ACQUIRE_ASSET: Acquiring asset '%s' (Type/Def Name: '%s') for run '%s'. "
      "Constraints: %s",
      asset_requirement.name,
      asset_requirement.actual_type_str,
      protocol_run_guid,
      asset_requirement.constraints.model_dump()
      if hasattr(asset_requirement.constraints, "model_dump")
      else dict(asset_requirement.constraints),
    )

    resource_def_check = await svc.get_resource_definition(
      self.db, asset_requirement.actual_type_str
    )

    if resource_def_check:
      logger.debug(
        "AM_ACQUIRE_ASSET: Identified '%s' as LABWARE (matches "
        "ResourceDefinitionCatalog). Dispatching to acquire_resource for '%s'.",
        asset_requirement.actual_type_str,
        asset_requirement.name,
      )
      return await self.acquire_resource(
        protocol_run_guid=protocol_run_guid,
        requested_asset_name_in_protocol=asset_requirement.name,
        name_constraint=asset_requirement.actual_type_str,
        property_constraints=asset_requirement.constraints.model_dump()
        if hasattr(asset_requirement.constraints, "model_dump")
        else dict(asset_requirement.constraints),
        location_constraints=asset_requirement.location_constraints.model_dump()
        if hasattr(asset_requirement.location_constraints, "model_dump")
        else dict(asset_requirement.location_constraints),
      )
    else:
      logger.debug(
        "AM_ACQUIRE_ASSET: Did not find '%s' in ResourceDefinitionCatalog. "
        "Assuming it's a Machine. Dispatching to acquire_machine for '%s'.",
        asset_requirement.actual_type_str,
        asset_requirement.name,
      )
      return await self.acquire_machine(
        protocol_run_guid=protocol_run_guid,
        requested_asset_name_in_protocol=asset_requirement.name,
        python_fqn_constraint=asset_requirement.actual_type_str,
        constraints=asset_requirement.constraints.model_dump()
        if hasattr(asset_requirement.constraints, "model_dump")
        else dict(asset_requirement.constraints),
      )
