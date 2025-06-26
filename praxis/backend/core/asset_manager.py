# pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements,logging-fstring-interpolation
# broad-except is disabled at method level where justified, not globally.
"""Manages the lifecycle and allocation of physical laboratory assets.

praxis/core/asset_manager.py

The AssetManager is responsible for managing the lifecycle and allocation
of physical laboratory assets (machines and resource instances, including decks).
It interacts with data services for persistence and infers changes
passed from WorkcellRuntime to the database for live PyLabRobot object status updates.

Decks are treated as ResourceOrm entities, potentially parented by a MachineOrm.
"""

import importlib
import inspect
import pkgutil
import uuid
from functools import partial
from typing import Any

import pylabrobot.resources
from pylabrobot.resources import (
  Carrier,
  Container,
  Coordinate,
  Deck,
  ItemizedResource,
  Lid,
  PetriDish,
  Plate,
  PlateAdapter,
  PlateHolder,
  Resource,
  ResourceHolder,
  ResourceStack,
  Tip,
  TipRack,
  TipSpot,
  Tube,
  TubeRack,
  Well,
)
from sqlalchemy.ext.asyncio import AsyncSession

import praxis.backend.services as svc
from praxis.backend.core.workcell_runtime import WorkcellRuntime
from praxis.backend.models import (
  AssetRequirementModel,
  MachineOrm,
  MachineStatusEnum,
  ResourceCategoryEnum,  # Not directly used here, but good for context
  ResourceOrm,
  ResourceStatusEnum,
)
from praxis.backend.utils.errors import AssetAcquisitionError, AssetReleaseError
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

    self.EXCLUDED_BASE_CLASSES: list[
      type[Resource]
    ] = [  # TODO: maybe just inspect if it's abstract?
      Carrier,
      Container,
      Deck,
      ItemizedResource,
      Lid,
      PlateAdapter,
      PlateHolder,
      Resource,
      ResourceHolder,
      ResourceStack,
      TipSpot,
      Well,
    ]

  @asset_manager_errors(
    prefix="AM_EXTRACT_NUM: ",
    suffix=" - Error extracting num_items",
  )
  def _extract_num_items(
    self,
    resource_class: type[Resource],
    details: dict[str, Any] | None,
  ) -> int | None:
    """Extract the number of items (e.g., tips, wells, tubes) from serialized details.

    Relevant for ItemizedResource types.
    It checks for 'num_items', 'items', 'capacity', or 'wells' in serialized details.

    Args:
        resource_class: The class of the resource being processed, for logging context.
        details: The serialized details of the resource instance.

    Returns:
        An integer representing the number of items, or None.

    """
    num_items_value: int | None = None
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
    prefix="AM_EXTRACT_ORDER: ",
    suffix=" - Error extracting ordering",
  )
  def _extract_ordering(
    self,
    resource_class: type[Resource],
    details: dict[str, Any] | None,
  ) -> str | None:
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
    except (
      TypeError,
      KeyError,
      ValueError,
      IndexError,
    ) as e:  # More specific exceptions
      logger.exception(
        "AM_EXTRACT_ORDER: Error extracting ordering for %s: %s",
        resource_class.__name__,
        e,
      )
    return ordering_value

  @asset_manager_errors(
    prefix="AM_GET_CATEGORY: ",
    suffix=" - Error getting category from PLR object",
  )
  def _can_catalog_resource(self, plr_class: type[Any]) -> bool:
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
      return False  # Generic base classes listed are explicitly excluded.
    if not plr_class.__module__.startswith("pylabrobot.resources"):
      return False
    return True

  @async_asset_manager_errors(
    prefix="AM_SYNC: ",
    suffix=" - Error syncing PyLabRobot definitions",
  )
  async def sync_pylabrobot_definitions(
    self,
    plr_resources_package=pylabrobot.resources,
  ) -> tuple[int, int]:
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
    processed_fqns: set[str] = set()

    for _, modname, _ in pkgutil.walk_packages(
      path=plr_resources_package.__path__,
      prefix=plr_resources_package.__name__ + ".",
      onerror=lambda x: logger.error("AM_SYNC: Error walking package %s", x),
    ):
      try:
        module = importlib.import_module(modname)
      except ImportError as e:
        logger.warning(
          "AM_SYNC: Could not import module %s during sync: %s",
          modname,
          e,
        )
        continue

      for class_name, plr_class_obj in inspect.getmembers(module, inspect.isclass):
        fqn = f"{modname}.{class_name}"
        if fqn in processed_fqns:
          continue
        processed_fqns.add(fqn)

        logger.debug(
          "AM_SYNC: Found class %s. Checking if catalogable resource...",
          fqn,
        )

        if not self._can_catalog_resource(plr_class_obj):
          logger.debug("AM_SYNC: Skipping %s - not a catalogable resource class.", fqn)
          continue

        logger.debug("AM_SYNC: Processing potential resource class: %s", fqn)
        temp_instance: Resource | None = None
        serialized_data: dict[str, Any] | None = None
        kwargs_for_instantiation: dict[str, Any] = {
          "name": f"praxis_sync_temp_{class_name}",
        }

        try:
          constructor_params = get_constructor_params_with_defaults(plr_class_obj)
          for param_name, param_info in constructor_params.items():
            if param_name in [
              "self",
              "name",
              "category",
              "model",
              "size_x",
              "size_y",
              "size_z",
            ]:
              continue
            if (
              param_info["required"]
              and param_info["default"] is inspect.Parameter.empty
            ):
              param_type_str = str(param_info["type"]).lower()
              if "optional" in param_type_str:
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
              elif "coordinate" in param_type_str:
                kwargs_for_instantiation[param_name] = Coordinate(0, 0, 0)
              else:
                logger.info(
                  "AM_SYNC: Cannot auto-default required param '%s' (%s) for %s.",
                  param_name,
                  param_info["type"],
                  fqn,
                )
        # pylint: disable-next=broad-except
        except Exception as e_param:
          logger.warning(
            "AM_SYNC: Error inspecting constructor for %s: %s.",
            fqn,
            e_param,
          )

        try:
          temp_instance = plr_class_obj(**kwargs_for_instantiation)
          if temp_instance:
            serialized_data = temp_instance.serialize()
            if "name" in serialized_data:
              del serialized_data["name"]
          else:  # Should not happen if constructor is standard
            logger.warning("AM_SYNC: Instantiation of %s returned None.", fqn)
            serialized_data = {}
        # pylint: disable-next=broad-except
        except Exception as inst_err:
          logger.warning(
            "AM_SYNC: Instantiation/serialization of %s failed: %s. Kwargs: %s",
            fqn,
            inst_err,
            kwargs_for_instantiation,
          )
          temp_instance = None
          serialized_data = {}

        size_x = serialized_data.get("size_x")
        size_y = serialized_data.get("size_y")
        size_z = serialized_data.get("size_z")
        nominal_volume_ul: float | None = None
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

        model_name_from_data = (
          serialized_data.get("model") or serialized_data.get("type") or class_name
        )
        resource_definition_name = class_name

        # Determine plr_category (e.g., "Deck", "Plate", "TipRack")
        plr_category_val = plr_class_obj.__name__  # Default to class name
        if (
          temp_instance
          and hasattr(temp_instance, "category")
          and temp_instance.category
        ):
          plr_category_val = temp_instance.category
        elif issubclass(plr_class_obj, Deck):
          plr_category_val = "Deck"
        elif issubclass(plr_class_obj, Plate):
          plr_category_val = "Plate"
        elif issubclass(plr_class_obj, TipRack):
          plr_category_val = "TipRack"
        # ... (add more specific PLR category mappings if needed) ...

        num_items = self._extract_num_items(plr_class_obj, serialized_data)
        ordering_str = self._extract_ordering(plr_class_obj, serialized_data)
        details_for_db = dict(serialized_data)  # Make a copy
        if num_items is not None:
          details_for_db["praxis_extracted_num_items"] = num_items
        if ordering_str is not None:
          details_for_db["praxis_extracted_ordering"] = ordering_str

        description = inspect.getdoc(plr_class_obj) or fqn
        # ResourceDefinitionCatalogOrm.resource_type is a user-friendly type/model name
        praxis_display_type_name = model_name_from_data

        is_consumable_flag = any(
          issubclass(plr_class_obj, consumable_base)
          for consumable_base in (Plate, TipRack, Tube, TubeRack, PetriDish, Lid, Tip)
        )
        if plr_category_val in ResourceCategoryEnum.consumables():
          is_consumable_flag = True
        if issubclass(plr_class_obj, Deck):
          is_consumable_flag = False  # Decks are not consumable

        logger.debug(
          "AM_SYNC: DB Prep: DefName=%s, FQN=%s, PLRCategory=%s, DisplayType=%s,"
          "Consumable=%s",
          resource_definition_name,
          fqn,
          plr_category_val,
          praxis_display_type_name,
          is_consumable_flag,
        )

        try:
          existing_def_orm = await svc.read_resource_definition(
            self.db,
            resource_definition_name,
          )
          if not existing_def_orm:
            added_count += 1
            logger.info(
              "AM_SYNC: Added new resource definition: %s",
              resource_definition_name,
            )
            await svc.create_resource_definition(
              db=self.db,
              name=resource_definition_name,  # PK
              python_fqn=fqn,
              resource_type=praxis_display_type_name,
              description=description,
              is_consumable=is_consumable_flag,
              nominal_volume_ul=nominal_volume_ul,
              plr_definition_details_json=details_for_db,
              # size_x_mm=size_x,
              # size_y_mm=size_y,
              # size_z_mm=size_z,
              # For ResourceDefinitionCatalogOrm.plr_category
              # plr_category=plr_category_val,
              # For ResourceDefinitionCatalogOrm.model
              # model=model_name_from_data,
            )
          else:
            await svc.update_resource_definition(
              db=self.db,
              name=resource_definition_name,
              python_fqn=fqn,
              resource_type=praxis_display_type_name,
              description=description,
              is_consumable=is_consumable_flag,
              nominal_volume_ul=nominal_volume_ul,
              plr_definition_details_json=details_for_db,
              # size_x_mm=size_x,
              # size_y_mm=size_y,
              # size_z_mm=size_z,
              # For ResourceDefinitionCatalogOrm.plr_category
              # plr_category=plr_category_val,
              # For ResourceDefinitionCatalogOrm.model
              # model=model_name_from_data,
            )
            updated_count += 1
            logger.info(
              "AM_SYNC: Updated existing resource definition: %s",
              resource_definition_name,
            )

        except Exception as e_proc:
          logger.exception(
            "AM_SYNC: DB save error for %s (Def Name: %s): %s",
            fqn,
            resource_definition_name,
            e_proc,
          )
        finally:
          if temp_instance:
            del temp_instance
          if serialized_data:
            del serialized_data

    # The broad-except disable is justified here because this is a sync function
    # that should attempt to process all items, logging errors for individual
    # failures rather than stopping the entire sync operation.
    logger.info(
      "AM_SYNC: Sync complete. Added: %d, Updated: %d",
      added_count,
      updated_count,
    )
    return added_count, updated_count

  async def apply_deck_instance(
    self,
    deck_orm_accession_id: uuid.UUID,
    protocol_run_accession_id: uuid.UUID,
  ) -> Deck:
    """Apply a deck instanceuration.

    Initialize the deck and assign pre-configured resources.

    Args:
        deck_orm_accession_id: The ORM ID of the deck.
        protocol_run_accession_id: The GUID of the current protocol run.

    Returns:
        The live PyLabRobot Deck object.

    Raises:
        AssetAcquisitionError: If the deck or its components cannot be configured.

    """
    logger.info(
      "AM_DECK_CONFIG: Applying deck instanceuration ID '%s', for run_accession_id: %s",
      deck_orm_accession_id,
      protocol_run_accession_id,
    )

    deck_orm = await svc.read_deck_instance(
      self.db,
      deck_orm_accession_id,
    )
    if not deck_orm:
      raise AssetAcquisitionError(
        f"Deck ID '{deck_orm_accession_id}' not found.",
      )

    deck_resource_orm = await svc.read_resource_instance(
      self.db,
      deck_orm.deck_accession_id,
    )  # TODO: make sure these are synced
    if not deck_resource_orm:
      raise AssetAcquisitionError(
        f"Deck Resource ID '{deck_orm.deck_accession_id}' (from Deck "
        f"'{deck_orm.name}') not found.",
      )

    deck_def_catalog_orm = await svc.read_resource_definition(
      self.db,
      deck_resource_orm.python_fqn,
    )
    if not deck_def_catalog_orm or not deck_def_catalog_orm.python_fqn:
      raise AssetAcquisitionError(
        f"Resource definition for deck "
        f"'{deck_resource_orm.user_assigned_name}' not found or FQN missing.",
      )

    if (
      deck_resource_orm.current_status == ResourceStatusEnum.IN_USE
      and deck_resource_orm.current_protocol_run_accession_id
      != protocol_run_accession_id
    ):
      raise AssetAcquisitionError(
        f"Deck resource '{deck_resource_orm.user_assigned_name}' is IN_USE by"
        f" another run.",
      )

    live_plr_deck_object = await self.workcell_runtime.create_or_get_resource(
      resource_orm=deck_resource_orm,
      resource_definition_fqn=deck_def_catalog_orm.python_fqn,
    )
    if not isinstance(live_plr_deck_object, Deck):
      raise AssetAcquisitionError(
        f"Failed to initialize PLR Deck for "
        f"'{deck_resource_orm.user_assigned_name}'.",
      )

    # Determine parent machine for location of the deck resource itself
    parent_machine_accession_id_for_deck: uuid.UUID | None = None
    parent_machine_name_for_log = "N/A (standalone or not specified)"
    # To access deck_orm.deck_parent_machine, it must be loaded by
    # read_deck_instance
    # For now, assuming it might not be loaded and rely on an explicit FK if it existed,
    # or leave None.
    # If DeckOrm has deck_parent_machine_accession_id FK:
    # if hasattr(deck_orm, 'deck_parent_machine_accession_id') and
    # deck_orm.deck_parent_machine_accession_id:
    #    parent_machine_accession_id_for_deck = deck_orm.deck_parent_machine_accession_id
    #    # Potentially log parent machine name
    # elif deck_orm.deck_parent_machine: # If relationship is loaded
    #    parent_machine_accession_id_for_deck = deck_orm.deck_parent_machine.accession_id
    #    parent_machine_name_for_log =
    # deck_orm.deck_parent_machine.user_friendly_name

    await svc.update_resource_instance_location_and_status(
      db=self.db,
      resource_instance_accession_id=deck_resource_orm.accession_id,
      new_status=ResourceStatusEnum.IN_USE,
      current_protocol_run_accession_id=protocol_run_accession_id,
      status_details=f"Deck '{deck_resource_orm.user_assigned_name}' "
      f"(parent machine: {parent_machine_name_for_log}) in use for config "
      f"'{deck_orm.name}' by run {protocol_run_accession_id}",
      location_machine_accession_id=parent_machine_accession_id_for_deck,
      current_deck_position_name=None,
    )
    logger.info(
      "AM_DECK_CONFIG: Deck resource '%s' PLR object initialized and IN_USE.",
      deck_resource_orm.user_assigned_name,
    )

    for position_item_orm in deck_orm.position_items or []:
      if position_item_orm.resource_instance_accession_id:
        item_to_place_accession_id = position_item_orm.resource_instance_accession_id
        item_to_place_orm = await svc.read_resource_instance(
          self.db,
          item_to_place_accession_id,
        )
        if not item_to_place_orm:
          logger.error(
            "Resource instance %s for position '%s' not found. Skipping.",
            item_to_place_accession_id,
            position_item_orm.position_accession_id,
          )
          continue

        # Idempotency check
        if (
          item_to_place_orm.current_status == ResourceStatusEnum.IN_USE
          and item_to_place_orm.current_protocol_run_accession_id
          == protocol_run_accession_id
          and item_to_place_orm.location_machine_accession_id
          == deck_resource_orm.accession_id  # Located on this deck
          and item_to_place_orm.current_deck_position_name
          == position_item_orm.position_accession_id
        ):
          logger.info(
            "Resource %s already configured at '%s' on this deck for this run.",
            item_to_place_accession_id,
            position_item_orm.position_accession_id,
          )
          continue

        if item_to_place_orm.current_status not in [
          ResourceStatusEnum.AVAILABLE_IN_STORAGE,
          ResourceStatusEnum.AVAILABLE_ON_DECK,
        ]:
          raise AssetAcquisitionError(
            f"Resource {item_to_place_accession_id} for position "
            f"'{position_item_orm.position_accession_id}' unavailable (status: "
            f"{item_to_place_orm.current_status}).",
          )

        item_def_orm = await svc.read_resource_definition(
          self.db,
          item_to_place_orm.python_fqn,
        )
        if not item_def_orm or not item_def_orm.python_fqn:
          raise AssetAcquisitionError(
            f"FQN not found for resource definition '{item_to_place_orm.python_fqn}'.",
          )

        await self.workcell_runtime.create_or_get_resource(
          resource_orm=item_to_place_orm,
          resource_definition_fqn=item_def_orm.python_fqn,
        )
        await self.workcell_runtime.assign_resource_to_deck(
          resource_orm_accession_id=item_to_place_accession_id,
          target=deck_orm_accession_id,
          position_accession_id=position_item_orm.position_accession_id,
        )
        await svc.update_resource_instance_location_and_status(
          db=self.db,
          resource_instance_accession_id=item_to_place_accession_id,
          new_status=ResourceStatusEnum.IN_USE,
          current_protocol_run_accession_id=protocol_run_accession_id,
          location_machine_accession_id=deck_resource_orm.accession_id,
          current_deck_position_name=position_item_orm.position_accession_id,
          status_details=f"On deck '{deck_resource_orm.user_assigned_name}' "
          f"pos '{position_item_orm.position_accession_id}' for run {protocol_run_accession_id}",
        )
        logger.info(
          "Resource %s configured at '%s' on deck '%s'.",
          item_to_place_orm.user_assigned_name,
          position_item_orm.position_accession_id,
          deck_resource_orm.user_assigned_name,
        )

    logger.info(
      "AM_DECK_CONFIG: Deck configuration for '%s' applied.",
      deck_orm.name,
    )
    assert isinstance(
      live_plr_deck_object,
      Deck,
    ), f"Expected live PLR Deck object, got {type(live_plr_deck_object)}"
    return live_plr_deck_object

  async def acquire_machine(
    self,
    protocol_run_accession_id: uuid.UUID,
    requested_asset_name_in_protocol: str,
    python_fqn_constraint: str,
    constraints: dict[str, Any] | None = None,
  ) -> tuple[Any, uuid.UUID, str]:
    """Acquire a Machine that is available or already in use by the current run.

    Args:
        protocol_run_accession_id: GUID of the protocol run.
        requested_asset_name_in_protocol: Name of the asset as requested in the
        protocol.
        python_fqn_constraint: The FQN of the PyLabRobot Machine class.
        constraints: Optional dictionary of constraints (e.g., specific serial number).

    Returns:
        A tuple (live_plr_machine_object, machine_orm_accession_id, "machine").

    Raises:
        AssetAcquisitionError: If no suitable machine can be acquired or initialized.

    """
    logger.info(
      "AM_ACQUIRE_MACHINE: Acquiring machine '%s' (FQN: '%s') for run '%s'.",
      requested_asset_name_in_protocol,
      python_fqn_constraint,
      protocol_run_accession_id,
    )

    # Safeguard: Check if FQN might be a Deck type mistakenly passed here
    try:
      module_path, class_name = python_fqn_constraint.rsplit(".", 1)
      module = importlib.import_module(module_path)
      cls_obj = getattr(module, class_name)
      if issubclass(cls_obj, Deck):  # Direct check against Deck
        raise AssetAcquisitionError(
          f"Attempted to acquire Deck FQN '{python_fqn_constraint}' via "
          f"acquire_machine. Use acquire_resource.",
        )
    except (ImportError, AttributeError, ValueError) as e:
      logger.warning(
        f"Could not dynamically verify FQN '{python_fqn_constraint}' during machine "
        f"acquisition safeguard: {e}",
      )
    # Also check against resource definitions just in case it's cataloged as a deck
    potential_deck_def = await svc.read_resource_definition_by_fqn(
      self.db,
      python_fqn_constraint,
    )
    if potential_deck_def and (
      (potential_deck_def.plr_category and "Deck" in potential_deck_def.plr_category)
      or (
        potential_deck_def.python_fqn
        and "deck" in potential_deck_def.python_fqn.lower()
      )
    ):
      raise AssetAcquisitionError(
        f"FQN '{python_fqn_constraint}' matches a cataloged Deck resource. "
        f"Use acquire_resource.",
      )

    selected_machine_orm: MachineOrm | None = None
    in_use_by_this_run_list = await svc.list_machines(
      self.db,
      pylabrobot_class_filter=python_fqn_constraint,
      status=MachineStatusEnum.IN_USE,
      current_protocol_run_accession_id_filter=protocol_run_accession_id,
    )
    if in_use_by_this_run_list:
      selected_machine_orm = in_use_by_this_run_list[0]
    else:
      available_machines_list = await svc.list_machines(
        self.db,
        status=MachineStatusEnum.AVAILABLE,
        pylabrobot_class_filter=python_fqn_constraint,
      )
      if available_machines_list:
        selected_machine_orm = available_machines_list[0]
        logger.info(
          "AM_ACQUIRE_DEVICE: Found available machine '%s' (ID: %s).",
          selected_machine_orm.user_friendly_name,
          selected_machine_orm.accession_id,
        )
      else:
        raise AssetAcquisitionError(
          f"No machine found for FQN '{python_fqn_constraint}' (Status: AVAILABLE or "
          f"IN_USE by this run).",
        )

    if not selected_machine_orm:
      raise AssetAcquisitionError(
        f"Machine selection failed for '{requested_asset_name_in_protocol}'.",
      )

    live_plr_machine = await self.workcell_runtime.initialize_machine(
      selected_machine_orm,
    )
    if not live_plr_machine:
      await svc.update_machine_status(
        self.db,
        selected_machine_orm.accession_id,
        MachineStatusEnum.ERROR,
        status_details=f"Backend init failed for run {protocol_run_accession_id}.",
      )
      raise AssetAcquisitionError(
        f"Failed to initialize backend for machine "
        f"'{selected_machine_orm.user_friendly_name}'.",
      )

    if (
      selected_machine_orm.current_status != MachineStatusEnum.IN_USE
      or selected_machine_orm.current_protocol_run_accession_id
      != uuid.UUID(str(protocol_run_accession_id))
    ):
      updated_machine_orm = await svc.update_machine_status(
        self.db,
        selected_machine_orm.accession_id,
        MachineStatusEnum.IN_USE,
        current_protocol_run_accession_id=uuid.UUID(str(protocol_run_accession_id)),
        status_details=f"In use by run {protocol_run_accession_id}",
      )
      if not updated_machine_orm:
        raise AssetAcquisitionError(
          f"CRITICAL: Failed to update DB status for machine "
          f"'{selected_machine_orm.user_friendly_name}'.",
        )
      selected_machine_orm = updated_machine_orm  # Use the updated ORM

    logger.info(
      "AM_ACQUIRE_MACHINE: Machine '%s' acquired for run '%s'.",
      selected_machine_orm.user_friendly_name,
      protocol_run_accession_id,
    )
    return live_plr_machine, selected_machine_orm.accession_id, "machine"

  async def acquire_resource(
    self,
    protocol_run_accession_id: uuid.UUID,
    requested_asset_name_in_protocol: str,
    python_fqn: str,  # ResourceDefinitionCatalogOrm.name
    user_choice_instance_accession_id: uuid.UUID | None = None,
    location_constraints: dict[str, Any] | None = None,
    property_constraints: dict[str, Any] | None = None,
  ) -> tuple[Any, uuid.UUID, str]:
    """Acquire a resource instance that is available.

    Args:
        protocol_run_accession_id: GUID of the protocol run.
        requested_asset_name_in_protocol: Name of the asset as requested in the
        protocol.
        python_fqn: The `name` from `ResourceDefinitionCatalogOrm`.
        user_choice_instance_accession_id: Optional specific ID of the resource instance to
        acquire.
        location_constraints: Optional constraints on where the resource should be
        (primarily for deck assignment).
        property_constraints: Optional constraints on resource properties.

    Returns:
        A tuple (live_plr_resource_object, resource_orm_accession_id, "resource").

    Raises:
        AssetAcquisitionError: If no suitable resource can be acquired or initialized.

    """
    logger.info(
      "AM_ACQUIRE_RESOURCE: Acquiring '%s' (Def: '%s') for run '%s'. Loc: %s",
      requested_asset_name_in_protocol,
      python_fqn,
      protocol_run_accession_id,
      location_constraints,
    )

    resource_instance_to_acquire: ResourceOrm | None = None
    if user_choice_instance_accession_id:
      instance_orm = await svc.read_resource_instance(
        self.db,
        user_choice_instance_accession_id,
      )
      if not instance_orm:
        raise AssetAcquisitionError(
          f"Specified resource ID {user_choice_instance_accession_id} not found.",
        )
      if instance_orm.python_fqn != python_fqn:
        raise AssetAcquisitionError(
          f"Chosen instance {user_choice_instance_accession_id} (Def: {instance_orm.python_fqn}) "
          f"mismatches constraint {python_fqn}.",
        )
      if instance_orm.current_status == ResourceStatusEnum.IN_USE:
        if instance_orm.current_protocol_run_accession_id != uuid.UUID(
          str(protocol_run_accession_id),
        ):
          raise AssetAcquisitionError(
            f" {user_choice_instance_accession_id} IN_USE by another run.",
          )
      elif instance_orm.current_status not in [
        ResourceStatusEnum.AVAILABLE_IN_STORAGE,
        ResourceStatusEnum.AVAILABLE_ON_DECK,
      ]:
        raise AssetAcquisitionError(
          f"Chosen instance {user_choice_instance_accession_id} not available (Status: "
          f"{instance_orm.current_status.name}).",
        )
      resource_instance_to_acquire = instance_orm
    else:
      in_use_list = await svc.list_resource_instances(
        self.db,
        python_fqn=python_fqn,
        status=ResourceStatusEnum.IN_USE,
        current_protocol_run_accession_id_filter=str(protocol_run_accession_id),
        property_filters=property_constraints,
      )
      if in_use_list:
        resource_instance_to_acquire = in_use_list[0]
      else:
        on_deck_list = await svc.list_resource_instances(
          self.db,
          python_fqn=python_fqn,
          status=ResourceStatusEnum.AVAILABLE_ON_DECK,
          property_filters=property_constraints,
        )
        if on_deck_list:
          resource_instance_to_acquire = on_deck_list[0]
        else:
          in_storage_list = await svc.list_resource_instances(
            self.db,
            python_fqn=python_fqn,
            status=ResourceStatusEnum.AVAILABLE_IN_STORAGE,
            property_filters=property_constraints,
          )
          if in_storage_list:
            resource_instance_to_acquire = in_storage_list[0]

    if not resource_instance_to_acquire:
      raise AssetAcquisitionError(
        f"No instance found for definition '{python_fqn}' matching criteria for "
        f"run '{protocol_run_accession_id}'.",
      )

    resource_def_orm = await svc.read_resource_definition(
      self.db,
      resource_instance_to_acquire.python_fqn,
    )
    if not resource_def_orm or not resource_def_orm.python_fqn:
      await svc.update_resource_instance_location_and_status(
        db=self.db,
        resource_instance_accession_id=resource_instance_to_acquire.accession_id,
        new_status=ResourceStatusEnum.ERROR,
        status_details=f"FQN missing for def {resource_instance_to_acquire.python_fqn}",
      )
      raise AssetAcquisitionError(
        f"FQN not found for resource definition '{resource_instance_to_acquire.python_fqn}'.",
      )

    live_plr_resource = await self.workcell_runtime.create_or_get_resource(
      resource_orm=resource_instance_to_acquire,
      resource_definition_fqn=resource_def_orm.python_fqn,
    )
    if not live_plr_resource:
      await svc.update_resource_instance_location_and_status(
        db=self.db,
        resource_instance_accession_id=resource_instance_to_acquire.accession_id,
        new_status=ResourceStatusEnum.ERROR,
        status_details="PLR object creation failed.",
      )
      raise AssetAcquisitionError(
        f"Failed to create/get PLR object for "
        f"'{resource_instance_to_acquire.user_assigned_name}'.",
      )

    target_deck_resource_accession_id: uuid.UUID | None = None
    target_position_name: str | None = None
    final_status_details = f"In use by run {protocol_run_accession_id}"
    is_acquiring_a_deck_resource = isinstance(live_plr_resource, Deck)

    if not is_acquiring_a_deck_resource and location_constraints:
      deck_user_name = location_constraints.get(
        "deck_name",
      )  # User-assigned name of the target deck resource
      position_on_deck = location_constraints.get("position_name")
      if deck_user_name and position_on_deck:
        target_deck_instance = await svc.read_resource_instance_by_name(
          self.db,
          deck_user_name,
        )
        if not target_deck_instance:
          raise AssetAcquisitionError(
            f"Target deck resource '{deck_user_name}' not found.",
          )
        # Verify target_deck_instance is a deck
        target_deck_def = await svc.read_resource_definition(
          self.db,
          target_deck_instance.python_fqn,
        )
        if not target_deck_def or not (
          (target_deck_def.plr_category and "Deck" in target_deck_def.plr_category)
          or issubclass(
            importlib.import_module(
              target_deck_def.python_fqn.rsplit(".", 1)[0],
            ).__getattribute__(target_deck_def.python_fqn.rsplit(".", 1)[1]),
            Deck,
          )
        ):
          raise AssetAcquisitionError(f"Target '{deck_user_name}' is not a deck type.")
        target_deck_resource_accession_id = target_deck_instance.accession_id
        target_position_name = position_on_deck
        await self.workcell_runtime.assign_resource_to_deck(
          resource_orm_accession_id=resource_instance_to_acquire.accession_id,
          target=target_deck_resource_accession_id,
          position_accession_id=target_position_name,
        )
        final_status_details = f"On deck '{deck_user_name}' pos \
          '{target_position_name}' for run {protocol_run_accession_id}"
      elif deck_user_name or position_on_deck:
        raise AssetAcquisitionError(
          "Partial location constraint: 'deck_name' and 'position_name' required.",
        )
    elif is_acquiring_a_deck_resource and location_constraints:
      logger.warning(
        "AM_ACQUIRE_RESOURCE: Location constraints ignored for acquiring a Deck "
        "resource '%s'.",
        resource_instance_to_acquire.user_assigned_name,
      )
      # A deck itself is not located *on* another deck via these constraints. Its parent
      # machine is handled differently if applicable.
      # If this deck resource instance should be associated with a parent MachineOrm
      # (e.g. an integrated deck),
      # that association would typically be part of its definition or a higher-level
      # configuration.
      # For now, its location_machine_accession_id will be set if it was part of a
      # DeckOrm that had a parent machine.
      # If acquired standalone, and it's a deck, its location_machine_accession_id might remain
      # None unless other logic sets it.
      target_deck_resource_accession_id = (
        None  # Explicitly not on another deck resource
      )
      target_position_name = None

    # Idempotency check for DB update
    needs_db_update = not (
      resource_instance_to_acquire.current_status == ResourceStatusEnum.IN_USE
      and resource_instance_to_acquire.current_protocol_run_accession_id
      == uuid.UUID(str(protocol_run_accession_id))
      and (
        is_acquiring_a_deck_resource
        or (  # For non-decks, location must match
          resource_instance_to_acquire.location_machine_accession_id
          == target_deck_resource_accession_id
          and resource_instance_to_acquire.current_deck_position_name
          == target_position_name
        )
      )
    )

    if needs_db_update:
      updated_resource_instance = (
        await svc.update_resource_instance_location_and_status(
          self.db,
          resource_instance_to_acquire.accession_id,
          new_status=ResourceStatusEnum.IN_USE,
          current_protocol_run_accession_id=uuid.UUID(str(protocol_run_accession_id)),
          location_machine_accession_id=target_deck_resource_accession_id,
          current_deck_position_name=target_position_name,
          status_details=final_status_details,
        )
      )
      if not updated_resource_instance:
        raise AssetAcquisitionError(
          f"CRITICAL: Failed to update DB for resource "
          f"'{resource_instance_to_acquire.user_assigned_name}'.",
        )
      resource_instance_to_acquire = updated_resource_instance  # Use updated ORM

    logger.info(
      "AM_ACQUIRE_RESOURCE: Resource '%s' (ID: %s) acquired. Status: IN_USE.",
      resource_instance_to_acquire.user_assigned_name,
      resource_instance_to_acquire.accession_id,
    )
    return live_plr_resource, resource_instance_to_acquire.accession_id, "resource"

  async def release_machine(
    self,
    machine_orm_accession_id: uuid.UUID,
    final_status: MachineStatusEnum = MachineStatusEnum.AVAILABLE,
    status_details: str | None = "Released from run",
  ):
    """Release a Machine (not a Deck)."""
    machine_to_release = await svc.read_machine(self.db, machine_orm_accession_id)
    if not machine_to_release:
      logger.warning(
        f"AM_RELEASE_MACHINE: Machine ID {machine_orm_accession_id} not found.",
      )
      return

    logger.info(
      "AM_RELEASE_MACHINE: Releasing machine '%s' (ID %s), final status: %s.",
      machine_to_release.user_friendly_name,
      machine_orm_accession_id,
      final_status.name,
    )
    # Safeguard against releasing Deck FQNs
    if (
      "deck" in machine_to_release.python_fqn.lower()
      or "Deck" in machine_to_release.python_fqn
    ):
      logger.error(
        f"AM_RELEASE_MACHINE: Attempt to release Deck-like FQN "
        f"'{machine_to_release.python_fqn}' via release_machine. Use release_resource.",
      )
      return  # Avoid proceeding

    await self.workcell_runtime.shutdown_machine(machine_orm_accession_id)
    updated_machine = await svc.update_machine_status(
      self.db,
      machine_orm_accession_id,
      final_status,
      status_details=status_details,
      current_protocol_run_accession_id=None,
    )
    if not updated_machine:
      raise AssetReleaseError(
        f"Failed to update DB status for machine ID {machine_orm_accession_id} after shutdown.",
      )
    logger.info(
      "AM_RELEASE_MACHINE: Machine '%s' released, status %s.",
      updated_machine.user_friendly_name,
      final_status.name,
    )

  async def release_resource(
    self,
    resource_orm_accession_id: uuid.UUID,
    final_status: ResourceStatusEnum,
    final_properties_json_update: dict[str, Any] | None = None,
    clear_from_deck_accession_id: uuid.UUID | None = None,
    clear_from_position_name: str | None = None,
    status_details: str | None = "Released from run",
  ):
    """Release a resource instance.

    Release resource, updating its status and properties,
    and clearing it from a deck position via WorkcellRuntime if specified.

    Args:
        resource_orm_accession_id: The ORM ID of the resource instance to release.
        final_status: The status to set after release (e.g., AVAILABLE_IN_STORAGE).
        final_properties_json_update: Optional properties to update in JSON format.
        clear_from_deck_accession_id: Optional ID of the deck DeckConfigOrm to clear from.
        clear_from_position_name: Optional position name on the deck to clear from.
        status_details: Optional details about the release.

    Raises:
        AssetReleaseError: If the resource cannot be released or updated in the DB.

    """
    resource_to_release = await svc.read_resource_instance(
      self.db,
      resource_orm_accession_id,
    )
    if not resource_to_release:
      logger.warning(
        "AM_RELEASE_RESOURCE: Resource instance ID %s not found.",
        resource_orm_accession_id,
      )
      return
    logger.info(
      "AM_RELEASE_RESOURCE: Releasing '%s' (ID %s, Type %s), final status: %s.",
      resource_to_release.user_assigned_name,
      resource_orm_accession_id,
      resource_to_release.python_fqn,
      final_status.name,
    )

    resource_def_orm = await svc.read_resource_definition(
      self.db,
      resource_to_release.python_fqn,
    )
    is_releasing_a_deck_resource = False
    if resource_def_orm and resource_def_orm.python_fqn:
      try:  # Check if it's a Deck subclass
        module_path, class_name = resource_def_orm.python_fqn.rsplit(".", 1)
        plr_class = getattr(importlib.import_module(module_path), class_name)
        if issubclass(plr_class, Deck):
          is_releasing_a_deck_resource = True
      except Exception:
        pass  # Ignore import/check errors, rely on category

    if is_releasing_a_deck_resource:
      logger.info(
        "AM_RELEASE_RESOURCE: '%s' is a Deck resource. Clearing its WCR state.",
        resource_to_release.user_assigned_name,
      )
      await self.workcell_runtime.clear_resource_instance(
        resource_orm_accession_id,
      )
      clear_from_deck_accession_id = None  # Not applicable for the deck itself
      clear_from_position_name = None
    elif clear_from_deck_accession_id and clear_from_position_name:
      logger.info(
        "AM_RELEASE_RESOURCE: Clearing '%s' from deck ID %s, pos '%s'.",
        resource_to_release.user_assigned_name,
        clear_from_deck_accession_id,
        clear_from_position_name,
      )
      await self.workcell_runtime.clear_deck_position(
        deck_orm_accession_id=clear_from_deck_accession_id,
        position_name=clear_from_position_name,
        resource_orm_accession_id=resource_orm_accession_id,
      )
    else:  # Generic resource not on a specific deck or deck not specified
      await self.workcell_runtime.clear_resource_instance(
        resource_orm_accession_id,
      )

    final_loc_accession_id_for_ads: uuid.UUID | None = None
    final_pos_for_ads: str | None = None
    if (
      not is_releasing_a_deck_resource
      and final_status == ResourceStatusEnum.AVAILABLE_ON_DECK
    ):
      final_loc_accession_id_for_ads = clear_from_deck_accession_id
      final_pos_for_ads = clear_from_position_name

    updated_resource = await svc.update_resource_instance_location_and_status(
      self.db,
      resource_orm_accession_id,
      final_status,
      properties_json_update=final_properties_json_update,
      location_machine_accession_id=final_loc_accession_id_for_ads,
      current_deck_position_name=final_pos_for_ads,
      current_protocol_run_accession_id=None,
      status_details=status_details,
    )
    if not updated_resource:
      raise AssetReleaseError(
        f"Failed to update DB for resource ID {resource_orm_accession_id} on release.",
      )
    logger.info(
      "AM_RELEASE_RESOURCE: Resource '%s' released, status %s.",
      updated_resource.user_assigned_name,
      final_status.name,
    )

  async def acquire_asset(
    self,
    protocol_run_accession_id: uuid.UUID,
    asset_requirement: AssetRequirementModel,
  ) -> tuple[Any, uuid.UUID, str]:
    """Dispatch asset acquisition to either acquire_machine or acquire_resource.

    The `asset_requirement.actual_type_str` is key:
    - If it matches a `name` in `ResourceDefinitionCatalogOrm`, it's resource.
    - Otherwise, it's assumed to be a PLR Machine FQN (machine).

    Args:
        protocol_run_accession_id: GUID of the protocol run.
        asset_requirement: The asset requirement model containing details.

    Returns:
        A tuple (live_plr_object, asset_orm_accession_id, "machine" or "resource").

    """
    asset_fqn = asset_requirement.fqn
    logger.info(
      "AM_ACQUIRE_ASSET: Acquiring '%s' (Type/Def: '%s') for run '%s'.",
      asset_requirement.name,
      asset_fqn,
      protocol_run_accession_id,
    )

    resource_def_check = await svc.read_resource_definition(self.db, asset_fqn)

    if resource_def_check:
      logger.debug(
        "AM_ACQUIRE_ASSET: '%s' is a cataloged resource. Using acquire_resource.",
        asset_fqn,
      )
      return await self.acquire_resource(
        protocol_run_accession_id=protocol_run_accession_id,
        requested_asset_name_in_protocol=asset_requirement.name,
        python_fqn=asset_fqn,  # ResourceDefinitionCatalog.name
        property_constraints=dict(asset_requirement.constraints or {}),
        location_constraints=dict(asset_requirement.location_constraints or {}),
        user_choice_instance_accession_id=getattr(
          asset_requirement,
          "user_choice_instance_accession_id",
          None,
        ),
      )
    # Assume it's a Machine FQN
    logger.debug(
      "AM_ACQUIRE_ASSET: '%s' not in ResourceCatalog. Assuming Machine FQN. Using "
      "acquire_machine.",
      asset_fqn,
    )
    # Final safeguard: if it looks like a Deck FQN but wasn't cataloged, raise error.
    if "deck" in asset_fqn.lower() or "Deck" in asset_fqn:
      try:
        module_path, class_name = asset_fqn.rsplit(".", 1)
        cls_obj = getattr(importlib.import_module(module_path), class_name)
        if issubclass(cls_obj, Deck):
          raise AssetAcquisitionError(
            f"Asset type '{asset_fqn}' appears to be a Deck but not "
            f"found in ResourceCatalog. Ensure it's synced.",
          )
      except Exception:
        pass

    return await self.acquire_machine(
      protocol_run_accession_id=protocol_run_accession_id,
      requested_asset_name_in_protocol=asset_requirement.name,
      python_fqn_constraint=asset_fqn,
      constraints=dict(asset_requirement.constraints or {}),
    )
