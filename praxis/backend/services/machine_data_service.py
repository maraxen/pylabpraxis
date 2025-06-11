# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Service layer for Machine Data Management.

praxis/db_services/machine_data_service.py

Service layer for interacting with machine-related data in the database.
This includes Machine Definitions, Machine Instances, and Machine configurations.
"""

import datetime
from functools import partial
from typing import Any, Dict, List, Optional, Sequence, TYPE_CHECKING

import uuid_utils as uuid
from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import flag_modified

if TYPE_CHECKING:
  from praxis.backend.models.resource_orm import ResourceInstanceStatusEnum

from praxis.backend.models import MachineOrm, MachineStatusEnum
from praxis.backend.services.entity_linking import (
  _create_or_link_resource_counterpart_for_machine,
)
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)

machine_data_service_log = partial(
  log_async_runtime_errors,
  logger_instance=logger,
  exception_type=Exception,
  raises=True,
  raises_exception=ValueError,
  return_=None,
)


@machine_data_service_log(
  prefix="Machine Data Service: Creating machine - ",
  suffix=" - Ensure the machine data is valid and unique.",
)
async def create_machine(
  db: AsyncSession,
  user_friendly_name: str,
  python_fqn: str,
  backend_config_json: Optional[Dict[str, Any]] = None,
  current_status: "MachineStatusEnum" = MachineStatusEnum.OFFLINE,
  status_details: Optional[str] = None,
  workcell_id: Optional[uuid.UUID] = None,
  physical_location_description: Optional[str] = None,
  properties_json: Optional[Dict[str, Any]] = None,
  is_resource: bool = False,
  resource_counterpart_id: Optional[uuid.UUID] = None,
  resource_def_name: Optional[str] = None,
  resource_properties_json: Optional[Dict[str, Any]] = None,
  resource_initial_status: Optional["ResourceInstanceStatusEnum"] = None,
) -> MachineOrm:
  """Add a new machine.

  This function creates a new `MachineOrm`.

  Args:
      db (AsyncSession): The database session.
      user_friendly_name (str): A human-readable name for the machine.
      python_fqn (str): The fully qualified name of the PyLabRobot
          class for this machine (e.g., "pylabrobot.resources.LiquidHandler").
      backend_config_json (Optional[Dict[str, Any]], optional): JSON configuration
          for the PyLabRobot backend. Defaults to None.
      current_status (MachineStatusEnum, optional): The current operational
          status of the machine. Defaults to `MachineStatusEnum.OFFLINE`.
      status_details (Optional[str], optional): Additional details about the
          current status. Defaults to None.
      workcell_id (Optional[uuid.UUID], optional): The ID of the workcell this machine
          belongs to. Defaults to None.
      physical_location_description (Optional[str], optional): A description of
          the machine's physical location. Defaults to None.
      properties_json (Optional[Dict[str, Any]], optional): Additional properties
          for the machine stored as JSON. Defaults to None.
      is_resource (bool, optional): Indicates if this machine is also a resource
          instance. Defaults to False.
      resource_counterpart_id (Optional[uuid.UUID], optional): If `is_resource` is True,
          and you want to link to an existing resource, this is the ID of the associated
          `ResourceInstanceOrm`. Defaults to None.
      resource_def_name (Optional[str]): Required if creating a new ResourceInstanceOrm.
      resource_properties_json (Optional[Dict[str, Any]]): Optional properties for a new
      ResourceInstanceOrm.
      resource_initial_status (Optional[ResourceInstanceStatusEnum]): Initial status for
      a new ResourceInstanceOrm.


  Returns:
      MachineOrm: The created machine object.

  Raises:
      ValueError: If a machine with the same `user_friendly_name` already exists.
      Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"Machine (Name: '{user_friendly_name}', creating new):"
  logger.info("%s Attempting to create new machine.", log_prefix)

  # Check if a machine with this user_friendly_name already exists
  result = await db.execute(
    select(MachineOrm).filter(MachineOrm.user_friendly_name == user_friendly_name)
  )
  if result.scalar_one_or_none():
    error_message = (
      f"{log_prefix} A machine with user-friendly name "
      f"'{user_friendly_name}' already exists. Use the update function for existing "
      f"machines."
    )
    logger.error(error_message)
    raise ValueError(error_message)

  # Create a new MachineOrm
  machine_orm = MachineOrm(
    user_friendly_name=user_friendly_name,
    python_fqn=python_fqn,
    backend_config_json=backend_config_json,
    current_status=current_status,
    status_details=status_details,
    workcell_id=workcell_id,
    physical_location_description=physical_location_description,
    properties_json=properties_json,
    is_resource=is_resource,
  )
  db.add(machine_orm)
  logger.info("%s Initialized new machine for creation.", log_prefix)

  try:
    await db.flush()  # Flush to get machine_orm.id if needed by resource linking
    logger.debug("%s Flushed new machine to get ID.", log_prefix)

    await _create_or_link_resource_counterpart_for_machine(
      db=db,
      machine_orm=machine_orm,
      is_resource=is_resource,
      resource_counterpart_id=resource_counterpart_id,
      resource_def_name=resource_def_name,
      resource_properties_json=resource_properties_json,
      resource_initial_status=resource_initial_status,
    )

    await db.commit()
    await db.refresh(machine_orm)
    if machine_orm.resource_counterpart:
      await db.refresh(machine_orm.resource_counterpart)
    logger.info("%s Successfully committed new machine.", log_prefix)

  except IntegrityError as e:
    await db.rollback()
    # Check for specific unique constraint violations if applicable
    if "uq_machines_user_friendly_name" in str(
      e.orig
    ):  # Placeholder for actual constraint name
      error_message = (
        f"{log_prefix} A machine with user-friendly name "
        f"'{user_friendly_name}' already exists (integrity check failed). Details: {e}"
      )
      logger.error(error_message, exc_info=True)
      raise ValueError(error_message) from e
    error_message = (
      f"{log_prefix} Database integrity error during creation. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error during creation. Rolling back.", log_prefix)
    raise e

  logger.info("%s Creation operation completed.", log_prefix)
  return machine_orm


@machine_data_service_log(
  prefix="Machine Data Service: Updating machine - ",
  suffix=" - Ensure the machine data is valid and unique.",
)
async def update_machine(
  db: AsyncSession,
  machine_id: uuid.UUID,
  user_friendly_name: Optional[str] = None,  # Made optional for updates
  python_fqn: Optional[str] = None,  # Made optional for updates
  backend_config_json: Optional[Dict[str, Any]] = None,
  current_status: Optional["MachineStatusEnum"] = None,  # Made optional for updates
  status_details: Optional[str] = None,
  workcell_id: Optional[uuid.UUID] = None,
  physical_location_description: Optional[str] = None,
  properties_json: Optional[Dict[str, Any]] = None,
  is_resource: Optional[bool] = None,  # Made optional for updates
  resource_counterpart_id: Optional[uuid.UUID] = None,
  resource_def_name: Optional[str] = None,  # Only used if creating a new resource
  resource_properties_json: Optional[Dict[str, Any]] = None,
  resource_initial_status: Optional[
    "ResourceInstanceStatusEnum"
  ] = None,  # Only used if creating a new resource
) -> MachineOrm:
  """Update an existing machine.

  Args:
      db (AsyncSession): The database session.
      machine_id (uuid.UUID): The ID of the existing machine to update.
      user_friendly_name (Optional[str], optional): A human-readable name for the
          machine. Defaults to None.
      python_fqn (Optional[str], optional): The fully qualified name of the PyLabRobot
          class for this machine. Defaults to None.
      backend_config_json (Optional[Dict[str, Any]], optional): JSON configuration
          for the PyLabRobot backend. Defaults to None.
      current_status (Optional[MachineStatusEnum], optional): The current operational
          status of the machine. Defaults to None.
      status_details (Optional[str], optional): Additional details about the
          current status. Defaults to None.
      workcell_id (Optional[uuid.UUID], optional): The ID of the workcell this machine
          belongs to. Defaults to None.
      physical_location_description (Optional[str], optional): A description of
          the machine's physical location. Defaults to None.
      properties_json (Optional[Dict[str, Any]], optional): Additional properties
          for the machine stored as JSON. Defaults to None.
      is_resource (Optional[bool], optional): Indicates if this machine is also a
          resource instance. Defaults to None.
      resource_counterpart_id (Optional[uuid.UUID], optional): If `is_resource` is True,
          and you want to link to an existing resource, this is the ID of the associated
          `ResourceInstanceOrm`. Defaults to None.
      resource_def_name (Optional[str]): Only used if creating a new
      ResourceInstanceOrm. resource_properties_json (Optional[Dict[str, Any]]):
      Optional properties for a new ResourceInstanceOrm.
      resource_initial_status (Optional[ResourceInstanceStatusEnum]): Initial status for
      a new ResourceInstanceOrm.

  Returns:
      MachineOrm: The updated machine object.

  Raises:
      ValueError: If `machine_id` is provided but no matching machine is found,
          or if the updated `user_friendly_name` conflicts with an existing one.
      Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"Machine (ID: {machine_id}, updating):"
  logger.info("%s Attempting to update machine.", log_prefix)

  # Fetch the existing machine
  result = await db.execute(select(MachineOrm).filter(MachineOrm.id == machine_id))
  machine_orm = result.scalar_one_or_none()
  if not machine_orm:
    error_message = (
      f"{log_prefix} MachineOrm with id {machine_id} not found for update."
    )
    logger.error(error_message)
    raise ValueError(error_message)
  logger.info("%s Found existing machine for update.", log_prefix)

  # Check for user_friendly_name conflict if it's being changed
  if (
    user_friendly_name is not None
    and machine_orm.user_friendly_name != user_friendly_name
  ):
    existing_name_check = await db.execute(
      select(MachineOrm)
      .filter(MachineOrm.user_friendly_name == user_friendly_name)
      .filter(MachineOrm.id != machine_id)  # Exclude the current record
    )
    if existing_name_check.scalar_one_or_none():
      error_message = (
        f"{log_prefix} Cannot update user_friendly_name to '{user_friendly_name}' as it"
        f" already exists for another machine."
      )
      logger.error(error_message)
      raise ValueError(error_message)
    machine_orm.user_friendly_name = user_friendly_name

  # Update attributes if provided
  if python_fqn is not None:
    machine_orm.python_fqn = python_fqn
  if backend_config_json is not None:
    machine_orm.backend_config_json = backend_config_json
  if current_status is not None:
    machine_orm.current_status = current_status
  if status_details is not None:
    machine_orm.status_details = status_details
  if workcell_id is not None:
    machine_orm.workcell_id = workcell_id
  if physical_location_description is not None:
    machine_orm.physical_location_description = physical_location_description
  if properties_json is not None:
    machine_orm.properties_json = properties_json

  # Handle `is_resource` update and potential resource counterpart linking
  effective_is_resource = (
    is_resource if is_resource is not None else machine_orm.is_resource
  )

  try:
    await _create_or_link_resource_counterpart_for_machine(
      db=db,
      machine_orm=machine_orm,
      is_resource=effective_is_resource,
      resource_counterpart_id=resource_counterpart_id,
      resource_def_name=resource_def_name,
      resource_properties_json=resource_properties_json,
      resource_initial_status=resource_initial_status,
    )
    # Only update machine_orm.is_resource after successful resource linking/unlinking
    if is_resource is not None:
      machine_orm.is_resource = is_resource

    await db.commit()
    await db.refresh(machine_orm)
    if machine_orm.resource_counterpart:
      await db.refresh(machine_orm.resource_counterpart)
    logger.info("%s Successfully committed updated machine.", log_prefix)
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"{log_prefix} Database integrity error during update. "
      f"This might occur if a unique constraint is violated. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error during update. Rolling back.", log_prefix)
    raise e

  logger.info("%s Update operation completed.", log_prefix)
  return machine_orm


async def read_machine(db: AsyncSession, machine_id: uuid.UUID) -> Optional[MachineOrm]:
  """Retrieve a specific machine by its ID.

  Args:
      db (AsyncSession): The database session.
      machine_id (int): The ID of the machine to retrieve.

  Returns:
      Optional[MachineOrm]: The machine object if found, otherwise None.

  """
  logger.info("Attempting to retrieve machine with ID: %d.", machine_id)
  result = await db.execute(
    select(MachineOrm)
    .options(joinedload(MachineOrm.resource_counterpart))
    .filter(MachineOrm.id == machine_id)
  )
  machine = result.scalar_one_or_none()
  if machine:
    logger.info(
      "Successfully retrieved machine ID %d: '%s'.",
      machine_id,
      machine.user_friendly_name,
    )
  else:
    logger.info("Machine with ID %d not found.", machine_id)
  return machine


async def read_machine_by_name(db: AsyncSession, name: str) -> Optional[MachineOrm]:
  """Retrieve a specific machine by its user-friendly name.

  Args:
      db (AsyncSession): The database session.
      name (str): The user-friendly name of the machine to retrieve.

  Returns:
      Optional[MachineOrm]: The machine object if found, otherwise None.

  """
  logger.info("Attempting to retrieve machine with name: '%s'.", name)
  result = await db.execute(
    select(MachineOrm)
    .options(joinedload(MachineOrm.resource_counterpart))
    .filter(MachineOrm.user_friendly_name == name)
  )
  machine = result.scalar_one_or_none()
  if machine:
    logger.info("Successfully retrieved machine by name '%s'.", name)
  else:
    logger.info("Machine with name '%s' not found.", name)
  return machine


async def read_machines_by_workcell_id(
  db: AsyncSession, workcell_id: int
) -> Sequence[MachineOrm]:
  """Retrieve all machines associated with a specific workcell ID.

  Args:
      db (AsyncSession): The database session.
      workcell_id (int): The ID of the workcell to filter machines by.

  Returns:
      Sequence[MachineOrm]: A sequence of machine objects associated with the workcell.

  """
  logger.info("Retrieving machines for workcell ID: %d.", workcell_id)
  stmt = (
    select(MachineOrm)
    .options(joinedload(MachineOrm.resource_counterpart))
    .filter(MachineOrm.workcell_id == workcell_id)
    .order_by(MachineOrm.user_friendly_name)
  )
  result = await db.execute(stmt)
  machines = result.scalars().all()
  logger.info("Found %d machines for workcell ID %d.", len(machines), workcell_id)
  return machines


async def list_machines(
  db: AsyncSession,
  status: Optional[MachineStatusEnum] = None,
  pylabrobot_class_filter: Optional[str] = None,
  workcell_id: Optional[int] = None,
  current_protocol_run_guid_filter: Optional[uuid.UUID] = None,
  user_friendly_name_filter: Optional[str] = None,  # Added parameter
  limit: int = 100,
  offset: int = 0,
) -> List[MachineOrm]:
  """List all machines with optional filtering and pagination.

  Args:
      db (AsyncSession): The database session.
      status (Optional[MachineStatusEnum], optional): Filter machines by their
          current status. Defaults to None.
      pylabrobot_class_filter (Optional[str], optional): Filter machines by a
          substring of their PyLabRobot class name. Defaults to None.
      workcell_id (Optional[int], optional): Filter machines by the ID of the
          workcell they belong to. Defaults to None.
      current_protocol_run_guid_filter (Optional[str], optional): Filter machines
          by the GUID of the protocol run they are currently associated with.
          Defaults to None.
      user_friendly_name_filter (Optional[str], optional): Filter machines by a
          substring of their user-friendly name (case-insensitive partial match).
          Defaults to None.
      limit (int): The maximum number of results to return. Defaults to 100.
      offset (int): The number of results to skip before returning. Defaults to 0.

  Returns:
      List[MachineOrm]: A list of machine objects matching the criteria.

  """
  logger.info(
    "Listing machines with filters: status=%s, pylabrobot_class_filter='%s', "
    "workcell_id=%s, protocol_run_guid_filter=%s, user_friendly_name_filter='%s', "
    "limit=%d, offset=%d.",
    status,
    pylabrobot_class_filter,
    workcell_id,
    current_protocol_run_guid_filter,
    user_friendly_name_filter,
    limit,
    offset,
  )
  stmt = select(MachineOrm).options(joinedload(MachineOrm.resource_counterpart))
  if status:
    stmt = stmt.filter(MachineOrm.current_status == status)
  if pylabrobot_class_filter:
    stmt = stmt.filter(MachineOrm.python_fqn.like(f"%{pylabrobot_class_filter}%"))
  if workcell_id:
    stmt = stmt.filter(MachineOrm.workcell_id == workcell_id)
  if current_protocol_run_guid_filter:
    stmt = stmt.filter(
      MachineOrm.current_protocol_run_guid == current_protocol_run_guid_filter
    )
  if user_friendly_name_filter:
    stmt = stmt.filter(
      MachineOrm.user_friendly_name.ilike(f"%{user_friendly_name_filter}%")
    )
  stmt = stmt.order_by(MachineOrm.user_friendly_name).limit(limit).offset(offset)
  result = await db.execute(stmt)
  machines = list(result.scalars().all())
  logger.info("Found %d machines.", len(machines))
  return machines


async def update_machine_status(
  db: AsyncSession,
  machine_id: uuid.UUID,
  new_status: MachineStatusEnum,
  status_details: Optional[str] = None,
  current_protocol_run_guid: Optional[uuid.UUID] = None,
) -> Optional[MachineOrm]:
  """Update the status of a specific machine.

  Args:
      db (AsyncSession): The database session.
      machine_id (uuid.UUID): The ID of the machine to update.
      new_status (MachineStatusEnum): The new status to set for the machine.
      status_details (Optional[str], optional): Optional details about the status.
          Defaults to None.
      current_protocol_run_guid (Optional[uuid.UUID], optional): The GUID of the
          protocol run if the machine is becoming `IN_USE`. If the machine's
          status is changing from `IN_USE` and this GUID matches, it will be
          cleared. Defaults to None.

  Returns:
      Optional[MachineOrm]: The updated machine object if successful, otherwise
      None if the machine was not found.

  Raises:
      Exception: For any unexpected errors during the update process.

  """
  logger.info(
    "Attempting to update status for machine ID %s to '%s'.",
    machine_id,
    new_status.value,
  )
  machine_orm = await read_machine(db, machine_id)
  if not machine_orm:
    logger.warning("Machine with ID %d not found for status update.", machine_id)
    return None

  logger.debug(
    "Machine '%s' (ID: %d) status changing from '%s' to '%s'.",
    machine_orm.user_friendly_name,
    machine_id,
    machine_orm.current_status.value,
    new_status.value,
  )
  machine_orm.current_status = new_status
  machine_orm.status_details = status_details

  if new_status == MachineStatusEnum.IN_USE:
    machine_orm.current_protocol_run_guid = current_protocol_run_guid
    logger.debug(
      "Machine '%s' (ID: %d) set to IN_USE with protocol run GUID: %s.",
      machine_orm.user_friendly_name,
      machine_id,
      current_protocol_run_guid,
    )
  elif machine_orm.current_protocol_run_guid == current_protocol_run_guid:
    machine_orm.current_protocol_run_guid = None
    logger.debug(
      "Machine '%s' (ID: %d) protocol run GUID cleared as it matches the "
      "current one and status is no longer IN_USE.",
      machine_orm.user_friendly_name,
      machine_id,
    )

  if new_status != MachineStatusEnum.OFFLINE:
    machine_orm.last_seen_online = datetime.datetime.now(datetime.timezone.utc)
    logger.debug(
      "Machine '%s' (ID: %d) last seen online updated.",
      machine_orm.user_friendly_name,
      machine_id,
    )

  try:
    await db.commit()
    await db.refresh(machine_orm)
    logger.info(
      "Successfully updated status for machine ID %d to '%s'.",
      machine_id,
      new_status.value,
    )
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error updating status for machine ID %d. Rolling back.",
      machine_id,
    )
    raise e
  return machine_orm


async def delete_machine(db: AsyncSession, machine_id: uuid.UUID) -> bool:
  """Delete a specific machine by its ID.

  Args:
      db (AsyncSession): The database session.
      machine_id (int): The ID of the machine to delete.

  Returns:
      bool: True if the deletion was successful, False if the machine was not found.

  Raises:
      ValueError: If the machine cannot be deleted due to existing foreign
          key references (IntegrityError).
      Exception: For any other unexpected errors during deletion.

  """
  logger.info("Attempting to delete machine with ID: %d.", machine_id)
  machine_orm = await read_machine(db, machine_id)
  if not machine_orm:
    logger.warning("Machine with ID %d not found for deletion.", machine_id)
    return False
  try:
    await db.delete(machine_orm)
    await db.commit()
    logger.info(
      "Successfully deleted machine ID %d: '%s'.",
      machine_id,
      machine_orm.user_friendly_name,
    )
    return True
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Cannot delete machine ID {machine_id} due to existing references. "
      f"Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error deleting machine ID %d. Rolling back.", machine_id
    )
    raise e
