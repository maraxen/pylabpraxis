# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Service layer for Machine Data Management.

praxis/db_services/machine_data_service.py

Service layer for interacting with machine-related data in the database.
This includes Machine Definitions, Machine Instances, and Machine configurations.
"""

import datetime
import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.attributes import flag_modified

from praxis.backend.models import (
  MachineOrm,
  MachineStatusEnum,
)

logger = logging.getLogger(__name__)


async def add_or_update_machine(
  db: AsyncSession,
  user_friendly_name: str,
  pylabrobot_class_name: str,
  backend_config_json: Optional[Dict[str, Any]] = None,
  current_status: MachineStatusEnum = MachineStatusEnum.OFFLINE,
  status_details: Optional[str] = None,
  workcell_id: Optional[int] = None,
  physical_location_description: Optional[str] = None,
  properties_json: Optional[Dict[str, Any]] = None,
  device_id: Optional[int] = None,
) -> MachineOrm:
  """Add a new machine or updates an existing one.

  This function creates a new `MachineOrm` if `device_id` is not provided and
  no existing machine matches `user_friendly_name`. If `device_id` is provided,
  it attempts to update the existing machine.

  Args:
      db (AsyncSession): The database session.
      user_friendly_name (str): A human-readable name for the machine.
      pylabrobot_class_name (str): The fully qualified name of the PyLabRobot
          class for this machine (e.g., "pylabrobot.resources.LiquidHandler").
      backend_config_json (Optional[Dict[str, Any]], optional): JSON configuration
          for the PyLabRobot backend. Defaults to None.
      current_status (MachineStatusEnum, optional): The current operational
          status of the machine. Defaults to `MachineStatusEnum.OFFLINE`.
      status_details (Optional[str], optional): Additional details about the
          current status. Defaults to None.
      workcell_id (Optional[int], optional): The ID of the workcell this machine
          belongs to. Defaults to None.
      physical_location_description (Optional[str], optional): A description of
          the machine's physical location. Defaults to None.
      properties_json (Optional[Dict[str, Any]], optional): Additional properties
          for the machine stored as JSON. Defaults to None.
      device_id (Optional[int], optional): The ID of an existing machine to update.
          If None, a new machine will be created or an existing one looked up by
          `user_friendly_name`. Defaults to None.

  Returns:
      MachineOrm: The created or updated machine object.

  Raises:
      ValueError: If `device_id` is provided but no matching machine is found,
          or if a machine with the same `user_friendly_name` already exists
          during creation.
      Exception: For any other unexpected errors during the process.

  """
  log_prefix = f"Machine (Name: '{user_friendly_name}', ID: {device_id or 'new'}):"
  logger.info("%s Attempting to add or update machine.", log_prefix)

  device_orm: Optional[MachineOrm] = None

  if device_id:
    result = await db.execute(select(MachineOrm).filter(MachineOrm.id == device_id))
    device_orm = result.scalar_one_or_none()
    if not device_orm:
      error_message = (
        f"{log_prefix} MachineOrm with id {device_id} not found for update."
      )
      logger.error(error_message)
      raise ValueError(error_message)
    logger.info("%s Found existing machine for update.", log_prefix)
  else:
    result = await db.execute(
      select(MachineOrm).filter(MachineOrm.user_friendly_name == user_friendly_name)
    )
    device_orm = result.scalar_one_or_none()
    if device_orm:
      logger.info(
        "%s Found existing machine by name, updating instead of creating.",
        log_prefix,
      )
    else:
      logger.info("%s No existing machine found, creating new.", log_prefix)
      device_orm = MachineOrm(user_friendly_name=user_friendly_name)
      db.add(device_orm)

  # This check should ideally not be needed if logic above is sound, but kept as a safeguard
  if device_orm is None:
    error_message = (
      f"{log_prefix} Failed to initialize MachineOrm. This indicates a logic error."
    )
    logger.critical(error_message)
    raise ValueError(error_message)

  device_orm.pylabrobot_class_name = pylabrobot_class_name
  device_orm.backend_config_json = backend_config_json
  device_orm.current_status = current_status
  device_orm.status_details = status_details
  device_orm.workcell_id = workcell_id
  device_orm.physical_location_description = physical_location_description
  device_orm.properties_json = properties_json

  try:
    await db.commit()
    await db.refresh(device_orm)
    logger.info("%s Successfully committed changes.", log_prefix)
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"{log_prefix} A device with name '{user_friendly_name}' might already "
      f"exist or other integrity constraint violated. Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error. Rolling back.", log_prefix)
    raise e
  logger.info("%s Operation completed.", log_prefix)
  return device_orm


async def get_machine_by_id(db: AsyncSession, device_id: int) -> Optional[MachineOrm]:
  """Retrieve a specific machine by its ID.

  Args:
      db (AsyncSession): The database session.
      device_id (int): The ID of the machine to retrieve.

  Returns:
      Optional[MachineOrm]: The machine object if found, otherwise None.

  """
  logger.info("Attempting to retrieve machine with ID: %d.", device_id)
  result = await db.execute(select(MachineOrm).filter(MachineOrm.id == device_id))
  machine = result.scalar_one_or_none()
  if machine:
    logger.info(
      "Successfully retrieved machine ID %d: '%s'.",
      device_id,
      machine.user_friendly_name,
    )
  else:
    logger.info("Machine with ID %d not found.", device_id)
  return machine


async def get_machine_by_name(db: AsyncSession, name: str) -> Optional[MachineOrm]:
  """Retrieve a specific machine by its user-friendly name.

  Args:
      db (AsyncSession): The database session.
      name (str): The user-friendly name of the machine to retrieve.

  Returns:
      Optional[MachineOrm]: The machine object if found, otherwise None.

  """
  logger.info("Attempting to retrieve machine with name: '%s'.", name)
  result = await db.execute(
    select(MachineOrm).filter(MachineOrm.user_friendly_name == name)
  )
  machine = result.scalar_one_or_none()
  if machine:
    logger.info("Successfully retrieved machine by name '%s'.", name)
  else:
    logger.info("Machine with name '%s' not found.", name)
  return machine


async def list_machines(
  db: AsyncSession,
  status: Optional[MachineStatusEnum] = None,
  pylabrobot_class_filter: Optional[str] = None,
  workcell_id: Optional[int] = None,
  current_protocol_run_guid_filter: Optional[int] = None,
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
      current_protocol_run_guid_filter (Optional[int], optional): Filter machines
          by the GUID of the protocol run they are currently associated with.
          Defaults to None.
      limit (int): The maximum number of results to return. Defaults to 100.
      offset (int): The number of results to skip before returning. Defaults to 0.

  Returns:
      List[MachineOrm]: A list of machine objects matching the criteria.

  """
  logger.info(
    "Listing machines with filters: status=%s, pylabrobot_class_filter='%s', "
    "workcell_id=%s, protocol_run_guid_filter=%s, limit=%d, offset=%d.",
    status,
    pylabrobot_class_filter,
    workcell_id,
    current_protocol_run_guid_filter,
    limit,
    offset,
  )
  stmt = select(MachineOrm)
  if status:
    stmt = stmt.filter(MachineOrm.current_status == status)
  if pylabrobot_class_filter:
    stmt = stmt.filter(
      MachineOrm.pylabrobot_class_name.like(f"%{pylabrobot_class_filter}%")
    )
  if workcell_id:
    stmt = stmt.filter(MachineOrm.workcell_id == workcell_id)
  if current_protocol_run_guid_filter:
    stmt = stmt.filter(
      MachineOrm.current_protocol_run_guid == current_protocol_run_guid_filter
    )
  stmt = stmt.order_by(MachineOrm.user_friendly_name).limit(limit).offset(offset)
  result = await db.execute(stmt)
  machines = list(result.scalars().all())
  logger.info("Found %d machines.", len(machines))
  return machines


async def update_machine_status(
  db: AsyncSession,
  device_id: int,
  new_status: MachineStatusEnum,
  status_details: Optional[str] = None,
  current_protocol_run_guid: Optional[str] = None,
) -> Optional[MachineOrm]:
  """Update the status of a specific machine.

  Args:
      db (AsyncSession): The database session.
      device_id (int): The ID of the machine to update.
      new_status (MachineStatusEnum): The new status to set for the machine.
      status_details (Optional[str], optional): Optional details about the status.
          Defaults to None.
      current_protocol_run_guid (Optional[str], optional): The GUID of the
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
    "Attempting to update status for machine ID %d to '%s'.",
    device_id,
    new_status.value,
  )
  device_orm = await get_machine_by_id(db, device_id)
  if not device_orm:
    logger.warning("Machine with ID %d not found for status update.", device_id)
    return None

  logger.debug(
    "Machine '%s' (ID: %d) status changing from '%s' to '%s'.",
    device_orm.user_friendly_name,
    device_id,
    device_orm.current_status.value,
    new_status.value,
  )
  device_orm.current_status = new_status
  device_orm.status_details = status_details

  if new_status == MachineStatusEnum.IN_USE:
    device_orm.current_protocol_run_guid = current_protocol_run_guid
    logger.debug(
      "Machine '%s' (ID: %d) set to IN_USE with protocol run GUID: %s.",
      device_orm.user_friendly_name,
      device_id,
      current_protocol_run_guid,
    )
  elif device_orm.current_protocol_run_guid == current_protocol_run_guid:
    # Clear GUID only if it matches the one that put it in use
    device_orm.current_protocol_run_guid = None
    logger.debug(
      "Machine '%s' (ID: %d) protocol run GUID cleared as it matches the "
      "current one and status is no longer IN_USE.",
      device_orm.user_friendly_name,
      device_id,
    )

  if new_status != MachineStatusEnum.OFFLINE:
    device_orm.last_seen_online = datetime.datetime.now(datetime.timezone.utc)
    logger.debug(
      "Machine '%s' (ID: %d) last seen online updated.",
      device_orm.user_friendly_name,
      device_id,
    )

  try:
    await db.commit()
    await db.refresh(device_orm)
    logger.info(
      "Successfully updated status for machine ID %d to '%s'.",
      device_id,
      new_status.value,
    )
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error updating status for machine ID %d. Rolling back.",
      device_id,
    )
    raise e
  return device_orm


async def delete_machine(db: AsyncSession, device_id: int) -> bool:
  """Delete a specific machine by its ID.

  Args:
      db (AsyncSession): The database session.
      device_id (int): The ID of the machine to delete.

  Returns:
      bool: True if the deletion was successful, False if the machine was not found.

  Raises:
      ValueError: If the machine cannot be deleted due to existing foreign
          key references (IntegrityError).
      Exception: For any other unexpected errors during deletion.

  """
  logger.info("Attempting to delete machine with ID: %d.", device_id)
  device_orm = await get_machine_by_id(db, device_id)
  if not device_orm:
    logger.warning("Machine with ID %d not found for deletion.", device_id)
    return False
  try:
    await db.delete(device_orm)
    await db.commit()
    logger.info(
      "Successfully deleted machine ID %d: '%s'.",
      device_id,
      device_orm.user_friendly_name,
    )
    return True
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Cannot delete machine ID {device_id} due to existing references. "
      f"Details: {e}"
    )
    logger.error(error_message, exc_info=True)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error deleting machine ID %d. Rolling back.", device_id
    )
    raise e
