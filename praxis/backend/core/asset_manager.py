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

# Import Machine base class for future use in machine discovery
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

# Setup logger for this module
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
    resource_class: Type[Resource],  # For logging context
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
        f"AM_EXTRACT_NUM: Extracted from details['num_items'] for "
        f"{resource_class.__name__}"
      )
      num_items_value = int(details["num_items"])
    elif "items" in details and isinstance(details["items"], list):
      logger.debug(
        f"AM_EXTRACT_NUM: Extracted from len(details['items']) for "
        f"{resource_class.__name__}"
      )
      num_items_value = len(details["items"])
    elif "wells" in details and isinstance(
      details["wells"], list
    ):  # Common for plates/racks
      logger.debug(
        f"AM_EXTRACT_NUM: Extracted from len(details['wells']) for "
        f"{resource_class.__name__}"
      )
      num_items_value = len(details["wells"])
    elif "capacity " in details and isinstance(details["capacity"], int):
      logger.debug(
        f"AM_EXTRACT_NUM: Extracted from details['capacity'] for "
        f"{resource_class.__name__}"
      )
      num_items_value = int(details["capacity"])

    if num_items_value is None:
      logger.debug(
        f"AM_EXTRACT_NUM: Number of items not found in details for "
        f"{resource_class.__name__}."
      )

    return num_items_value

  @asset_manager_errors(
    prefix="AM_EXTRACT_ORDER: ", suffix=" - Error extracting ordering"
  )
  def _extract_ordering(
    self,
    resource_class: Type[Resource],  # For logging context
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
      # Check if 'ordering' is directly provided (less common in standard PLR serialize)
      if "ordering" in details and isinstance(details["ordering"], str):
        logger.debug(
          f"AM_EXTRACT_ORDER: Extracted from details['ordering'] for "
          f"{resource_class.__name__}"
        )
        ordering_value = details["ordering"]
      # If 'wells' (or 'items') are detailed as a list of dicts, each with a 'name'
      elif "wells" in details and isinstance(details["wells"], list):
        if all(isinstance(w, dict) and "name" in w for w in details["wells"]):
          logger.debug(
            f"AM_EXTRACT_ORDER: Extracted from names in details['wells'] for "
            f"{resource_class.__name__}"
          )
          ordering_value = ",".join([w["name"] for w in details["wells"]])
      elif "items" in details and isinstance(
        details["items"], list
      ):  # General case for ItemizedResource
        if all(isinstance(i, dict) and "name" in i for i in details["items"]):
          logger.debug(
            f"AM_EXTRACT_ORDER: Extracted from names in details['items'] for "
            f"{resource_class.__name__}"
          )
          ordering_value = ",".join([i["name"] for i in details["items"]])

      if ordering_value is None:
        logger.debug(
          f"AM_EXTRACT_ORDER: Ordering not found in details for "
          f"{resource_class.__name__}."
        )
    except Exception as e:  # pylint: disable=broad-except
      logger.exception(
        f"AM_EXTRACT_ORDER: Error extracting ordering for {resource_class.__name__}: "
        f"{e}"
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
      return False  # should be redundant with the above
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
      f"AM_SYNC: Starting PyLabRobot resource definition sync from package: "
      f"{plr_resources_package.__name__}"
    )

    added_count = 0
    updated_count = 0
    processed_fqns: Set[str] = set()

    for _, modname, _ in pkgutil.walk_packages(
      path=plr_resources_package.__path__,  # type: ignore
      prefix=plr_resources_package.__name__ + ".",
      onerror=lambda x: logger.error(f"AM_SYNC: Error walking package {x}"),
    ):
      try:
        module = importlib.import_module(modname)
      except ImportError as e:
        logger.warning(f"AM_SYNC: Could not import module {modname} during sync: {e}")
        continue

      for class_name, plr_class_obj in inspect.getmembers(module, inspect.isclass):
        fqn = f"{modname}.{class_name}"
        if fqn in processed_fqns:
          continue
        processed_fqns.add(fqn)

        logger.debug(f"AM_SYNC: Found class {fqn}. Checking if catalogable resource...")

        if not self._can_catalog_resource(plr_class_obj):
          logger.debug(f"AM_SYNC: Skipping {fqn} - not a catalogable resource class.")
          continue

        logger.debug(f"AM_SYNC: Processing potential resource class: {fqn}")
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
            ]:  # 'name' is handled, category/model come from serialize
              continue
            if param_info["required"] and param_info["default"] is None:
              param_type_str = param_info["type"].lower()
              # Sensible defaults for common types
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
                  f"AM_SYNC: Cannot auto-default required parameter "
                  f"'{param_name}' of type '{param_info['type']}' for {fqn}. "
                  f"Instantiation might fail or be skipped."
                )
          if can_instantiate:
            logger.debug(
              f"AM_SYNC: Attempting instantiation of {fqn} with kwargs: "
              f"{kwargs_for_instantiation}"
            )
            temp_instance = plr_class_obj(**kwargs_for_instantiation)
            if temp_instance is None:
              logger.warning(
                f"AM_SYNC: Instantiation of {fqn} returned None. This might"
                f" indicate an issue with the class or its constructor."
              )
              can_instantiate = False
            else:
              logger.debug(
                f"AM_SYNC: Successfully instantiated {fqn} with name: "
                f"{temp_instance.name}"
              )
              serialized_data = temp_instance.serialize()
              if "name" in serialized_data:  # Remove the temporary name
                del serialized_data["name"]
        except Exception as inst_err:  # pylint: disable=broad-except
          logger.warning(
            f"AM_SYNC: Instantiation or serialization of {fqn} failed: {inst_err}. "
            f"Will attempt to proceed with class-level data if possible, but some "
            f"attributes might be missing.",
            exc_info=True,
          )
          temp_instance = None  # Ensure it's None if instantiation failed
          serialized_data = None

        # --- Extract data primarily from serialized_data ---
        size_x = serialized_data.get("size_x") if serialized_data else None
        size_y = serialized_data.get("size_y") if serialized_data else None
        size_z = serialized_data.get("size_z") if serialized_data else None

        nominal_volume_ul: Optional[float] = None
        if serialized_data:
          if "max_volume" in serialized_data:  # e.g. for a single Well or Tube
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
          ):  # for TipRacks
            first_item = serialized_data["items"][0]
            if (
              isinstance(first_item, dict) and "volume" in first_item
            ):  # Tips have 'volume'
              nominal_volume_ul = float(first_item["volume"])

        model_name = serialized_data.get("model") if serialized_data else None
        if not model_name and serialized_data and serialized_data.get("type"):
          model_name = serialized_data.get(
            "type"
          )  # Use class name as model if no explicit model
        elif not model_name:  # Fallback if no serialized_data or model/type in it
          model_name = class_name

        # pylabrobot_def_name: Unique identifier for the resource type in Praxis.
        # Prioritize model, then type (class name from serialization), then FQN.
        pylabrobot_def_name = (
          model_name  # Start with model_name (which might be class_name)
        )
        if (
          not pylabrobot_def_name
        ):  # Should not happen if model_name has fallback to class_name
          pylabrobot_def_name = fqn
          logger.warning(
            f"AM_SYNC: Using FQN '{fqn}' as pylabrobot_def_name for {class_name} "
            f"due to missing model/type."
          )

        # Category: Directly from serialized_data['category'] if available
        category = serialized_data.get("category") if serialized_data else None
        if not category:  # Fallback if not in serialized data
          category = ResourceCategoryEnum.OTHER.value  # Default to OTHER
          logger.debug(f"AM_SYNC: Used fallback category '{category}' for {fqn}")

        # Num items and Ordering (for ItemizedResources)
        num_items = self._extract_num_items(plr_class_obj, serialized_data)
        ordering_str = self._extract_ordering(plr_class_obj, serialized_data)

        details_for_db = serialized_data if serialized_data is not None else {}
        if num_items is not None and "praxis_extracted_num_items" not in details_for_db:
          details_for_db["praxis_extracted_num_items"] = num_items
        if (
          ordering_str is not None and "praxis_extracted_ordering" not in details_for_db
        ):
          details_for_db["praxis_extracted_ordering"] = ordering_str

        # Description
        description = inspect.getdoc(plr_class_obj) or fqn

        # Is consumable
        is_consumable = category in ResourceCategoryEnum.consumables()

        praxis_type_name = model_name

        logger.debug(
          f"AM_SYNC: Preparing to save/update {pylabrobot_def_name} (FQN: {fqn}): "
          f"Category={category}, Model={model_name}, Vol={nominal_volume_ul}, "
          f"X={size_x}, Y={size_y}, Z={size_z}, NumItems={num_items}, "
          f"Ordering={'Present' if ordering_str else 'N/A'}..."
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
              f"AM_SYNC: Added new resource definition: {pylabrobot_def_name}"
            )
          else:
            updated_count += 1
            logger.info(
              f"AM_SYNC: Updated existing resource definition: {pylabrobot_def_name}"
            )

        except Exception as e_proc:  # pylint: disable=broad-except
          logger.exception(
            f"AM_SYNC: Could not process or save PLR class '{fqn}' (Def Name: "
            f"{pylabrobot_def_name}): {e_proc}"
          )
        finally:
          if temp_instance:
            del temp_instance
            del serialized_data

    logger.info(
      f"AM_SYNC: Resource definition sync complete. Added: {added_count}, Updated: "
      f"{updated_count}"
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
      f"AM_DECK_CONFIG: Applying deck configuration for '{deck_orm_id}', run_guid: "
      f"{protocol_run_guid}"
    )

    deck_orm = await svc.get_deck_by_id(self.db, deck_orm_id)
    if not deck_orm:
      raise AssetAcquisitionError(f"Deck '{deck_orm_id}' not found in database.")

    deck_machines_orm = await svc.list_machines(self.db)

    # Filter for actual decks
    actual_deck_machine_orm: Optional[MachineOrm] = None
    for dev_orm in deck_machines_orm:
      # This check might be too simplistic if the FQN is for a generic Deck
      # and the actual instance is, e.g., a HamiltonStarDeck.
      # TODO: Refine deck identification.
      if "Deck" in dev_orm.python_fqn:  # Basic check
        # Check if it's a PLR Deck or subclass by trying to import and check inheritance
        try:
          module_path, class_n = dev_orm.python_fqn.rsplit(".", 1)
          module = importlib.import_module(module_path)
          cls_obj = getattr(module, class_n)
          if issubclass(cls_obj, Deck):
            actual_deck_machine_orm = dev_orm
            break
        except (ImportError, AttributeError, ValueError) as e:
          logger.warning(
            f"Could not verify class for machine {dev_orm.user_friendly_name} (FQN: "
            f"{dev_orm.python_fqn}): {e}"
          )

    if not actual_deck_machine_orm:
      raise AssetAcquisitionError(
        f"No Machine found and verified as a PLR Deck for deck name '{deck_name}'."
      )

    deck_machine_orm = actual_deck_machine_orm

    if (
      deck_machine_orm.current_status == MachineStatusEnum.IN_USE
      and deck_machine_orm.current_protocol_run_guid != protocol_run_guid
    ):
      raise AssetAcquisitionError(
        f"Deck machine '{deck_name}' (ID: {deck_machine_orm.id}) is already in use by "
        f"another run '{deck_machine_orm.current_protocol_run_guid}'."
      )

    # Initialize the deck through WorkcellRuntime
    live_plr_deck_object = self.workcell_runtime.initialize_machine(deck_machine_orm)
    if not live_plr_deck_object or not isinstance(live_plr_deck_object, Deck):
      raise AssetAcquisitionError(
        f"Failed to initialize backend for deck '{deck_name}' (ID: {deck_machine_orm.id}) or it's not a Deck. Check WorkcellRuntime."
      )

    await svc.update_machine_status(
      self.db,
      deck_machine_orm.id,
      MachineStatusEnum.IN_USE,
      current_protocol_run_guid=protocol_run_guid,
      status_details=f"Deck '{deck_name}' in use by run {protocol_run_guid}",
    )
    logger.info(
      f"AM_DECK_CONFIG: Deck machine '{deck_name}' (ID: {deck_machine_orm.id}) backend initialized and marked IN_USE."
    )

    # Get DeckSlotOrm entries associated with the DeckLayoutOrm
    deck_slots_orm = await svc.get_deckpositions_for_layout(self.db, deck_layout_orm.id)
    logger.info(
      f"AM_DECK_CONFIG: Found {len(deck_slots_orm)} slots for deck layout '{deck_name}' (Layout ID: {deck_layout_orm.id})."
    )

    for slot_orm in deck_slots_orm:
      if slot_orm.pre_assigned_resource_instance_id:
        resource_instance_id = slot_orm.pre_assigned_resource_instance_id
        logger.info(
          f"AM_DECK_CONFIG: Slot '{slot_orm.slot_name}' (Slot ID: {slot_orm.id}) has pre-assigned resource instance ID: {resource_instance_id}."
        )

        resource_instance_orm = await svc.get_resource_instance_by_id(
          self.db, resource_instance_id
        )
        if not resource_instance_orm:
          logger.error(
            f"Resource instance ID {resource_instance_id} for slot '{slot_orm.slot_name}' not found. Skipping assignment."
          )
          continue  # Or raise error, depending on desired strictness

        # Check resource status
        if (
          resource_instance_orm.current_status == ResourceInstanceStatusEnum.IN_USE
          and resource_instance_orm.current_protocol_run_guid == protocol_run_guid
          and resource_instance_orm.location_machine_id == deck_machine_orm.id
          and resource_instance_orm.current_deck_slot_name == slot_orm.slot_name
        ):
          logger.warning(
            f"AM_DECK_CONFIG: Resource instance {resource_instance_id} in slot '{slot_orm.slot_name}' is already IN_USE by this run and at this location. Assuming already configured."
          )
          # Ensure it's in WorkcellRuntime's view of the deck
          # This might involve re-asserting the assignment in WorkcellRuntime if it clears state.
          # For now, we assume if DB state is correct, WCR will reflect it or re-establish.
          continue

        if resource_instance_orm.current_status not in [
          ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
          ResourceInstanceStatusEnum.AVAILABLE_ON_DECK,
        ]:
          raise AssetAcquisitionError(
            f"Resource instance ID {resource_instance_id} for slot '{slot_orm.slot_name}' is not available "
            f"(status: {resource_instance_orm.current_status}, run: {resource_instance_orm.current_protocol_run_guid})."
          )

        resource_def_orm = await svc.get_resource_definition(
          self.db, resource_instance_orm.name
        )
        if not resource_def_orm or not resource_def_orm.python_fqn:
          raise AssetAcquisitionError(
            f"Python FQN not found for resource definition '{resource_instance_orm.name}' (instance ID {resource_instance_id})."
          )

        live_plr_resource = self.workcell_runtime.create_or_get_resource_plr_object(
          resource_instance_orm=resource_instance_orm,
          resource_definition_fqn=resource_def_orm.python_fqn,
        )
        if not live_plr_resource:
          raise AssetAcquisitionError(
            f"Failed to create PLR object for resource instance ID {resource_instance_id} in slot '{slot_orm.slot_name}'."
          )

        logger.info(
          f"AM_DECK_CONFIG: Assigning resource '{live_plr_resource.name}' (Instance ID: {resource_instance_id}) to deck '{deck_name}' slot '{slot_orm.slot_name}'."
        )
        # Assign to PLR Deck object via WorkcellRuntime
        self.workcell_runtime.assign_resource_to_deck_slot(
          deck_machine_orm_id=deck_machine_orm.id,  # Pass the MachineOrm ID of the deck
          slot_name=slot_orm.slot_name,
          resource_plr_object=live_plr_resource,
          resource_instance_orm_id=resource_instance_id,
        )
        # Update ResourceInstanceOrm status and location
        await svc.update_resource_instance_location_and_status(
          db=self.db,
          resource_instance_id=resource_instance_id,
          new_status=ResourceInstanceStatusEnum.IN_USE,
          current_protocol_run_guid=protocol_run_guid,
          location_machine_id=deck_machine_orm.id,  # Its location is now this deck
          current_deck_slot_name=slot_orm.slot_name,
          deck_slot_orm_id=slot_orm.id,
          status_details=f"On deck '{deck_name}' slot '{slot_orm.slot_name}' for run {protocol_run_guid}",
        )
        logger.info(
          f"AM_DECK_CONFIG: Resource instance ID {resource_instance_id} marked IN_USE on slot '{slot_orm.slot_name}'."
        )

    logger.info(
      f"AM_DECK_CONFIG: Deck configuration for '{deck_name}' applied successfully."
    )
    return live_plr_deck_object

  async def acquire_machine(
    self,
    protocol_run_guid: str,
    requested_asset_name_in_protocol: str,
    python_fqn_constraint: str,  # This should be the FQN of the PLR Machine class
    constraints: Optional[Dict[str, Any]] = None,
  ) -> Tuple[Any, int, str]:
    """
    Acquires a machine (PLR Machine) that is available or already in use by the current run.

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
      f"AM_ACQUIRE_DEVICE: Acquiring machine '{requested_asset_name_in_protocol}' "
      f"(PLR Class FQN: '{python_fqn_constraint}') for run '{protocol_run_guid}'. "
      f"Constraints: {constraints}"
    )

    # TODO: Implement constraint matching if `constraints` are provided (e.g., serial_number)
    # For now, we pick the first available or one already in use by this run.

    selected_machine_orm: Optional[MachineOrm] = None

    # 1. Check if a suitable machine is already in use by this run
    in_use_by_this_run_list = await svc.list_machines(
      self.db,
      pylabrobot_class_filter=python_fqn_constraint,
      status=MachineStatusEnum.IN_USE,
      current_protocol_run_guid_filter=protocol_run_guid,
    )
    if in_use_by_this_run_list:
      selected_machine_orm = in_use_by_this_run_list[
        0
      ]  # Assuming one machine of this type per run for now
      logger.info(
        f"AM_ACQUIRE_DEVICE: Device '{selected_machine_orm.user_friendly_name}' (ID: {selected_machine_orm.id}) "
        f"is already IN_USE by this run '{protocol_run_guid}'. Re-acquiring."
      )
    else:
      # 2. If not, find an available one
      available_machines_list = await svc.list_machines(
        self.db,
        status=MachineStatusEnum.AVAILABLE,
        pylabrobot_class_filter=python_fqn_constraint,
      )
      if available_machines_list:
        selected_machine_orm = available_machines_list[0]  # Pick the first available
        logger.info(
          f"AM_ACQUIRE_DEVICE: Found available machine '{selected_machine_orm.user_friendly_name}' (ID: {selected_machine_orm.id})."
        )
      else:
        raise AssetAcquisitionError(
          f"No machine found matching PLR class FQN '{python_fqn_constraint}' with status AVAILABLE, "
          "nor already in use by this run."
        )

    if (
      not selected_machine_orm
    ):  # Should be caught by the logic above, but as a safeguard.
      raise AssetAcquisitionError(
        f"Device selection failed for '{requested_asset_name_in_protocol}'."
      )

    logger.info(
      f"AM_ACQUIRE_DEVICE: Attempting to initialize backend for selected machine '{selected_machine_orm.user_friendly_name}' "
      f"(ID: {selected_machine_orm.id}) via WorkcellRuntime."
    )
    live_plr_machine = self.workcell_runtime.initialize_machine_backend(
      selected_machine_orm
    )

    if not live_plr_machine:
      error_msg = (
        f"Failed to initialize backend for machine '{selected_machine_orm.user_friendly_name}' "
        f"(ID: {selected_machine_orm.id}). Check WorkcellRuntime logs and machine status in DB."
      )
      logger.error(error_msg)
      # Optionally set machine status to ERROR in DB here
      await svc.update_machine_status(
        self.db,
        selected_machine_orm.id,
        MachineStatusEnum.ERROR,
        status_details=f"Backend initialization failed for run {protocol_run_guid}: {error_msg[:200]}",
      )
      raise AssetAcquisitionError(error_msg)

    logger.info(
      f"AM_ACQUIRE_DEVICE: Backend for machine '{selected_machine_orm.user_friendly_name}' initialized. "
      f"Marking as IN_USE for run '{protocol_run_guid}' (if not already)."
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
        # Potentially try to shut down the backend if DB update fails?
        raise AssetAcquisitionError(critical_error_msg)
      logger.info(
        f"AM_ACQUIRE_DEVICE: Device '{updated_machine_orm.user_friendly_name}' (ID: {updated_machine_orm.id}) "
        f"successfully acquired and backend initialized for run '{protocol_run_guid}'."
      )
    else:
      logger.info(
        f"AM_ACQUIRE_DEVICE: Device '{selected_machine_orm.user_friendly_name}' (ID: {selected_machine_orm.id}) "
        f"was already correctly marked IN_USE by this run."
      )

    return live_plr_machine, selected_machine_orm.id, "machine"

  async def acquire_resource(
    self,
    protocol_run_guid: str,
    requested_asset_name_in_protocol: str,
    name_constraint: str,  # Key from ResourceDefinitionCatalogOrm
    user_choice_instance_id: Optional[int] = None,
    location_constraints: Optional[
      Dict[str, Any]
    ] = None,  # e.g., {"deck_name": "deck1", "slot_name": "A1"}
    property_constraints: Optional[Dict[str, Any]] = None,  # e.g., {"is_sterile": True}
  ) -> Tuple[Any, int, str]:
    """
    Acquires a resource instance that is available or already in use by the current run.

    Args:
        protocol_run_guid: GUID of the protocol run.
        requested_asset_name_in_protocol: Name of the asset as requested in the protocol.
        name_constraint: The `name` from `ResourceDefinitionCatalogOrm`.
        user_choice_instance_id: Optional specific ID of the resource instance to acquire.
        location_constraints: Optional constraints on where the resource should be (primarily for deck assignment).
        property_constraints: Optional constraints on resource properties.

    Returns:
        A tuple (live_plr_resource_object, resource_instance_orm_id, "resource").

    Raises:
        AssetAcquisitionError: If no suitable resource can be acquired or initialized.
    """
    logger.info(
      f"AM_ACQUIRE_LABWARE: Acquiring resource '{requested_asset_name_in_protocol}' "
      f"(PLR Def Name Constraint: '{name_constraint}') for run '{protocol_run_guid}'. "
      f"User Choice ID: {user_choice_instance_id}, Location Constraints: {location_constraints}, Property Constraints: {property_constraints}"
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
          f"Chosen resource instance ID {user_choice_instance_id} (Definition: '{instance_orm.name}') "
          f"does not match definition constraint '{name_constraint}'."
        )
      # Check status for user_choice_instance_id
      if instance_orm.current_status == ResourceInstanceStatusEnum.IN_USE:
        if instance_orm.current_protocol_run_guid != protocol_run_guid:
          raise AssetAcquisitionError(
            f"Chosen resource instance ID {user_choice_instance_id} is IN_USE by another run ('{instance_orm.current_protocol_run_guid}')."
          )
        logger.info(
          f"AM_ACQUIRE_LABWARE: Resource instance ID {user_choice_instance_id} is already IN_USE by this run '{protocol_run_guid}'. Re-acquiring."
        )
        resource_instance_to_acquire = instance_orm
      elif instance_orm.current_status not in [
        ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
        ResourceInstanceStatusEnum.AVAILABLE_ON_DECK,
      ]:
        raise AssetAcquisitionError(
          f"Chosen resource instance ID {user_choice_instance_id} is not available (status: {instance_orm.current_status.name})."
        )
      else:
        resource_instance_to_acquire = instance_orm  # It's available
    else:
      # 1. Check if already in use by this run
      in_use_list = await svc.list_resource_instances(
        self.db,
        name=name_constraint,
        status=ResourceInstanceStatusEnum.IN_USE,
        current_protocol_run_guid_filter=protocol_run_guid,
        property_filters=property_constraints,  # Apply property filters if any
      )
      if in_use_list:
        resource_instance_to_acquire = in_use_list[0]  # Assuming one for now
        logger.info(
          f"AM_ACQUIRE_LABWARE: Resource instance '{resource_instance_to_acquire.user_assigned_name}' (ID: {resource_instance_to_acquire.id}) "
          f"is already IN_USE by this run '{protocol_run_guid}'. Re-acquiring."
        )
      else:
        # 2. Check if available on deck
        on_deck_list = await svc.list_resource_instances(
          self.db,
          name=name_constraint,
          status=ResourceInstanceStatusEnum.AVAILABLE_ON_DECK,
          property_filters=property_constraints,
        )
        if on_deck_list:
          resource_instance_to_acquire = on_deck_list[0]
        else:
          # 3. Check if available in storage
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
          f"and properties {property_constraints} that is available or already in use by this run."
        )

    # At this point, resource_instance_to_acquire should be set if one was found
    if not resource_instance_to_acquire:  # Safeguard, should be caught above
      raise AssetAcquisitionError(
        f"Resource acquisition failed for {requested_asset_name_in_protocol}."
      )

    resource_def_orm = await svc.get_resource_definition(
      self.db, resource_instance_to_acquire.name
    )
    if not resource_def_orm or not resource_def_orm.python_fqn:
      error_msg = (
        f"Python FQN not found for resource definition '{resource_instance_to_acquire.name}' "
        f"for instance ID {resource_instance_to_acquire.id}."
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
      f"AM_ACQUIRE_LABWARE: Attempting to create/get PLR object for resource instance "
      f"'{resource_instance_to_acquire.user_assigned_name}' (ID: {resource_instance_to_acquire.id}) using FQN '{resource_fqn}'."
    )
    live_plr_resource = self.workcell_runtime.create_or_get_resource_plr_object(
      resource_instance_orm=resource_instance_to_acquire,
      resource_definition_fqn=resource_fqn,
    )
    if not live_plr_resource:
      error_msg = (
        f"Failed to create/get PLR object for resource '{resource_instance_to_acquire.user_assigned_name}' "
        f"(ID: {resource_instance_to_acquire.id}). Check WorkcellRuntime logs."
      )
      logger.error(error_msg)
      # Optionally set resource status to ERROR
      await svc.update_resource_instance_location_and_status(
        db=self.db,
        resource_instance_id=resource_instance_to_acquire.id,
        new_status=ResourceInstanceStatusEnum.ERROR,
        status_details=f"PLR object creation failed: {error_msg[:150]}",
      )
      raise AssetAcquisitionError(error_msg)

    logger.info(
      f"AM_ACQUIRE_LABWARE: PLR object for resource '{resource_instance_to_acquire.user_assigned_name}' created/retrieved. "
      f"Updating status to IN_USE (if not already by this run) and handling location."
    )

    target_deck_orm_id: Optional[int] = None
    target_slot_name: Optional[str] = None
    final_status_details = f"In use by run {protocol_run_guid}"

    if location_constraints and isinstance(location_constraints, dict):
      deck_name = location_constraints.get("deck_name")
      slot_name = location_constraints.get("slot_name")
      if deck_name and slot_name:
        logger.info(
          f"AM_ACQUIRE_LABWARE: Location constraint: place '{live_plr_resource.name}' on deck '{deck_name}' slot '{slot_name}'."
        )
        # Find the deck ORM
        deck_machines = await svc.list_machines(
          self.db, user_friendly_name_filter=deck_name
        )  # Assuming deck name is unique for Machine
        if not deck_machines:
          raise AssetAcquisitionError(
            f"Deck machine '{deck_name}' specified in location_constraints not found."
          )
        deck_machine_orm = deck_machines[0]  # Assuming first one is correct if multiple
        target_deck_orm_id = deck_machine_orm.id
        target_slot_name = slot_name

        # Assign to PLR Deck object via WorkcellRuntime
        self.workcell_runtime.assign_resource_to_deck_slot(
          deck_machine_orm_id=target_deck_orm_id,
          slot_name=target_slot_name,
          resource_plr_object=live_plr_resource,
          resource_instance_orm_id=resource_instance_to_acquire.id,
        )
        final_status_details = (
          f"On deck '{deck_name}' slot '{slot_name}' for run {protocol_run_guid}"
        )
        logger.info(
          f"AM_ACQUIRE_LABWARE: Resource assigned to deck '{deck_name}' slot '{slot_name}' in WorkcellRuntime."
        )
      elif deck_name or slot_name:  # Partial constraint
        raise AssetAcquisitionError(
          f"Partial location constraint for '{requested_asset_name_in_protocol}'. Both 'deck_name' and 'slot_name' required if placing on deck."
        )

    # Update ResourceInstanceOrm status and location, only if it's not already correctly set
    if not (
      resource_instance_to_acquire.current_status == ResourceInstanceStatusEnum.IN_USE
      and resource_instance_to_acquire.current_protocol_run_guid == protocol_run_guid
      and (
        not target_deck_orm_id
        or resource_instance_to_acquire.location_machine_id == target_deck_orm_id
      )
      and (
        not target_slot_name
        or resource_instance_to_acquire.current_deck_slot_name == target_slot_name
      )
    ):
      updated_resource_instance_orm = await svc.update_resource_instance_location_and_status(
        self.db,
        resource_instance_id=resource_instance_to_acquire.id,
        new_status=ResourceInstanceStatusEnum.IN_USE,
        current_protocol_run_guid=protocol_run_guid,
        location_machine_id=target_deck_orm_id,  # Null if not placed on a specific deck
        current_deck_slot_name=target_slot_name,  # Null if not in a specific slot
        status_details=final_status_details,
      )
      if not updated_resource_instance_orm:
        critical_error_msg = (
          f"CRITICAL: Resource '{resource_instance_to_acquire.user_assigned_name}' PLR object created/assigned, "
          f"but FAILED to update its DB status/location for run '{protocol_run_guid}'."
        )
        logger.error(critical_error_msg)
        raise AssetAcquisitionError(critical_error_msg)
      logger.info(
        f"AM_ACQUIRE_LABWARE: Resource '{updated_resource_instance_orm.user_assigned_name}' (ID: {updated_resource_instance_orm.id}) "
        f"successfully acquired for run '{protocol_run_guid}'. Status: IN_USE. Location Device ID: {target_deck_orm_id}, Slot: {target_slot_name}."
      )
    else:
      logger.info(
        f"AM_ACQUIRE_LABWARE: Resource '{resource_instance_to_acquire.user_assigned_name}' (ID: {resource_instance_to_acquire.id}) "
        f"was already correctly set as IN_USE by this run, and at the target location if specified."
      )

    return live_plr_resource, resource_instance_to_acquire.id, "resource"

  async def release_machine(
    self,
    machine_orm_id: int,
    final_status: MachineStatusEnum = MachineStatusEnum.AVAILABLE,
    status_details: Optional[str] = "Released from run",
  ):
    """
    Releases a machine, updating its status and shutting down its backend via WorkcellRuntime.
    """
    logger.info(
      f"AM_RELEASE_DEVICE: Releasing machine ID {machine_orm_id}. Target status: {final_status.name}. Details: {status_details}"
    )
    # Call WorkcellRuntime to shut down the backend first
    self.workcell_runtime.shutdown_machine_backend(machine_orm_id)
    logger.info(
      f"AM_RELEASE_DEVICE: WorkcellRuntime shutdown initiated for machine ID {machine_orm_id}."
    )

    # Update the status in the database
    updated_machine = await svc.update_machine_status(
      self.db,
      machine_orm_id,
      final_status,
      status_details=status_details,
      current_protocol_run_guid=None,  # Clear the run GUID
    )
    if not updated_machine:
      logger.error(
        f"AM_RELEASE_DEVICE: Failed to update status for machine ID {machine_orm_id} in DB after backend shutdown."
      )
      # Potentially raise an error or handle this case (e.g., machine backend might be down, but DB state is inconsistent)
    else:
      logger.info(
        f"AM_RELEASE_DEVICE: Device ID {machine_orm_id} status updated to {final_status.name} in DB."
      )

  async def release_resource(
    self,
    resource_instance_orm_id: int,
    final_status: ResourceInstanceStatusEnum,
    final_properties_json_update: Optional[Dict[str, Any]] = None,
    clear_from_deck_machine_id: Optional[int] = None,  # ID of the deck MachineOrm
    clear_from_slot_name: Optional[str] = None,
    status_details: Optional[str] = "Released from run",
  ):
    """
    Releases a resource instance, updating its status and properties,
    and clearing it from a deck slot via WorkcellRuntime if specified.
    """
    logger.info(
      f"AM_RELEASE_LABWARE: Releasing resource ID {resource_instance_orm_id}. Target status: {final_status.name}. Details: {status_details}"
    )
    if final_properties_json_update:
      logger.info(
        f"AM_RELEASE_LABWARE: Update properties for instance ID {resource_instance_orm_id}: {final_properties_json_update}"
      )

    # If the resource was on a deck, clear it from WorkcellRuntime's view of that deck
    if clear_from_deck_machine_id is not None and clear_from_slot_name is not None:
      logger.info(
        f"AM_RELEASE_LABWARE: Clearing resource ID {resource_instance_orm_id} from deck ID {clear_from_deck_machine_id}, slot '{clear_from_slot_name}' via WorkcellRuntime."
      )
      self.workcell_runtime.clear_deck_slot(
        deck_machine_orm_id=clear_from_deck_machine_id,
        slot_name=clear_from_slot_name,
        resource_instance_orm_id=resource_instance_orm_id,
      )
    else:
      # If not clearing from a specific deck, ensure it's cleared from any WCR internal cache if it was a general acquisition
      self.workcell_runtime.clear_general_resource_instance(resource_instance_orm_id)

    # Determine final location for DB update
    final_location_machine_id_for_ads: Optional[int] = None
    final_deck_slot_name_for_ads: Optional[str] = None
    # If final status is AVAILABLE_ON_DECK, it implies it remains on 'clear_from_deck_machine_id'
    if final_status == ResourceInstanceStatusEnum.AVAILABLE_ON_DECK:
      final_location_machine_id_for_ads = clear_from_deck_machine_id
      final_deck_slot_name_for_ads = clear_from_slot_name
    # If AVAILABLE_IN_STORAGE or CONSUMED, location is cleared.

    updated_resource = await svc.update_resource_instance_location_and_status(
      self.db,
      resource_instance_id=resource_instance_orm_id,
      new_status=final_status,
      properties_json_update=final_properties_json_update,
      location_machine_id=final_location_machine_id_for_ads,
      current_deck_slot_name=final_deck_slot_name_for_ads,
      current_protocol_run_guid=None,  # Clear the run GUID
      status_details=status_details,
    )
    if not updated_resource:
      logger.error(
        f"AM_RELEASE_LABWARE: Failed to update final status/location for resource ID {resource_instance_orm_id} in DB."
      )
    else:
      logger.info(
        f"AM_RELEASE_LABWARE: Resource ID {resource_instance_orm_id} status updated to {final_status.name} in DB."
      )

  async def acquire_asset(
    self, protocol_run_guid: str, asset_requirement: AssetRequirementModel
  ) -> Tuple[Any, int, str]:
    """
    Dispatches asset acquisition to either acquire_machine or acquire_resource based on the asset type.
    The `asset_requirement.actual_type_str` is key:
    - If it matches a `name` in `ResourceDefinitionCatalogOrm`, it's resource.
    - Otherwise, it's assumed to be a PLR Machine FQN (machine).
    """
    logger.info(
      f"AM_ACQUIRE_ASSET: Acquiring asset '{asset_requirement.name}' "
      f"(Type/Def Name: '{asset_requirement.actual_type_str}') for run '{protocol_run_guid}'. "
      f"Constraints: {asset_requirement.constraints_json}"
    )

    # Check if actual_type_str corresponds to a known resource definition name
    resource_def_check = await svc.get_resource_definition(
      self.db, asset_requirement.actual_type_str
    )

    if resource_def_check:
      logger.debug(
        f"AM_ACQUIRE_ASSET: Identified '{asset_requirement.actual_type_str}' as LABWARE "
        f"(matches ResourceDefinitionCatalog). Dispatching to acquire_resource for '{asset_requirement.name}'."
      )
      return await self.acquire_resource(
        protocol_run_guid=protocol_run_guid,
        requested_asset_name_in_protocol=asset_requirement.name,
        name_constraint=asset_requirement.actual_type_str,  # This is the key for ResourceDefinitionCatalogOrm
        property_constraints=asset_requirement.constraints_json,  # Pass all constraints as property constraints for resource
        location_constraints=asset_requirement.location_constraints_json,  # Specific for resource placement
      )
    else:
      # Assume it's a machine/machine FQN
      logger.debug(
        f"AM_ACQUIRE_ASSET: Did not find '{asset_requirement.actual_type_str}' in ResourceDefinitionCatalog. "
        f"Assuming it's a DEVICE (PLR Machine FQN). Dispatching to acquire_machine for '{asset_requirement.name}'."
      )
      # For machines, constraints_json are general constraints.
      return await self.acquire_machine(
        protocol_run_guid=protocol_run_guid,
        requested_asset_name_in_protocol=asset_requirement.name,
        python_fqn_constraint=asset_requirement.actual_type_str,  # This is the FQN for the PLR Machine class
        constraints=asset_requirement.constraints_json,
      )
