# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Service layer for Machine Data Management.

praxis/db_services/machine_data_service.py

Service layer for interacting with machine-related data in the database.
This includes Machine Definitions, Machine s, and Machine configurations.
"""

import datetime
import uuid
from collections.abc import Sequence
from functools import partial

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from praxis.backend.models import MachineCreate, MachineUpdate
from praxis.backend.models.enums import AssetType
from praxis.backend.models.machine_orm import MachineOrm, MachineStatusEnum
from praxis.backend.services.entity_linking import (
  _create_or_link_resource_counterpart_for_machine,
  synchronize_machine_resource_names,
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
  machine_create: MachineCreate,
) -> MachineOrm:
  """Add a new machine.
  # type: ignore
   This function creates a new `MachineOrm` based on the provided Pydantic model.

  Args:
       db (AsyncSession): The database session.
       machine_create (MachineCreate): The Pydantic model containing the data for the
           new machine.

  Returns:
       MachineOrm: The created machine object.

  Raises:
       ValueError: If a machine with the same `name` already exists.
       Exception: For any other unexpected errors during the process.

  """
  create_data = machine_create.model_dump()
  name = create_data["name"]
  log_prefix = f"Machine (Name: '{name}', creating new):"  # type: ignore
  logger.info("%s Attempting to create new machine.", log_prefix)

  # Check if a machine with this name already exists
  result = await db.execute(select(MachineOrm).filter(MachineOrm.name == name))
  if result.scalar_one_or_none():
    error_message = (
      f"{log_prefix} A machine with name '{name}' already exists. Use the update "
      f"function for existing machines."
    )
    logger.error(error_message)
    raise ValueError(error_message)

  # Create a new MachineOrm
  machine_orm = MachineOrm(
    name=name,
    fqn=create_data["fqn"],
    asset_type=AssetType.MACHINE,  # Default, updated by linking function if needed
    plr_definition=create_data.get("plr_definition"),
    status=create_data.get("status", MachineStatusEnum.OFFLINE),
    status_details=create_data.get("status_details"),
    workcell_accession_id=create_data.get("workcell_id"),
    location=create_data.get("location"),  # type: ignore
    properties_json=create_data.get("properties_json"),
  )
  db.add(machine_orm)
  logger.info("%s Initialized new machine for creation.", log_prefix)

  try:
    await db.flush()  # Flush to get machine_orm.accession_id
    logger.debug("%s Flushed new machine to get ID.", log_prefix)

    await _create_or_link_resource_counterpart_for_machine(
      db=db,
      machine_orm=machine_orm,
      is_resource=create_data.get("is_resource", False),
      resource_counterpart_accession_id=create_data.get(
        "resource_counterpart_accession_id",
      ),
      resource_def_name=create_data.get("resource_def_name"),
      resource_properties_json=create_data.get("resource_properties_json"),
      resource_initial_status=create_data.get("resource_initial_status"),
    )

    await db.commit()  # type: ignore
    await db.refresh(machine_orm)
    if machine_orm.resource_counterpart:
      await db.refresh(machine_orm.resource_counterpart)
    logger.info("%s Successfully committed new machine.", log_prefix)

  except IntegrityError as e:
    await db.rollback()
    if "uq_assets_name" in str(e.orig):
      error_message = (
        f"{log_prefix} A machine with name '{name}' already exists (integrity "
        f"check failed). Details: {e}"
      )
      logger.exception(error_message)
      raise ValueError(error_message) from e
    error_message = (
      f"{log_prefix} Database integrity error during creation. Details: {e}"
    )
    logger.exception(error_message)
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
  machine_accession_id: uuid.UUID,
  machine_update: MachineUpdate,
) -> MachineOrm:
  """Update an existing machine.

  Args:
      db (AsyncSession): The database session.
      machine_accession_id (uuid.UUID): The ID of the existing machine to update.
      machine_update (MachineUpdate): Pydantic model with updated data.

  Returns:
      MachineOrm: The updated machine object.

  Raises:
      ValueError: If `machine_accession_id` is provided but no matching machine is
          found, or if the updated `name` conflicts with an existing one.
      Exception: For any other unexpected errors during the process.

  """
  update_data = machine_update.model_dump(exclude_unset=True)
  log_prefix = f"Machine (ID: {machine_accession_id}, updating):"  # type: ignore
  logger.info("%s Attempting to update machine.", log_prefix)

  # Fetch the existing machine
  result = await db.execute(
    select(MachineOrm).filter(MachineOrm.accession_id == machine_accession_id),
  )
  machine_orm = result.scalar_one_or_none()
  if not machine_orm:
    error_message = (
      f"{log_prefix} MachineOrm with id {machine_accession_id} not found for update."
    )
    logger.error(error_message)
    raise ValueError(error_message)
  logger.info("%s Found existing machine for update.", log_prefix)

  # Check for name conflict if it's being changed
  name = update_data.get("name")
  if name is not None and machine_orm.name != name:
    existing_name_check = await db.execute(
      select(MachineOrm)
      .filter(MachineOrm.name == name)
      .filter(MachineOrm.accession_id != machine_accession_id),
    )
    if existing_name_check.scalar_one_or_none():
      error_message = (
        f"{log_prefix} Cannot update name to '{name}' as it already exists for "
        f"another machine."
      )
      logger.error(error_message)
      raise ValueError(error_message)
    machine_orm.name = name

    # Synchronize name with linked resource counterpart if it exists
    await synchronize_machine_resource_names(db, machine_orm, name)

  # Update attributes if provided
  for key, value in update_data.items():
    if hasattr(machine_orm, key) and key not in [
      "name",
      "is_resource",
      "resource_counterpart_accession_id",
      "resource_def_name",
      "resource_properties_json",
      "resource_initial_status",
    ]:
      setattr(machine_orm, key, value)

  # Handle `is_resource` update and potential resource counterpart linking
  effective_is_resource = (
    update_data["is_resource"]
    if "is_resource" in update_data
    else (machine_orm.resource_counterpart_accession_id is not None)
  )

  try:
    await _create_or_link_resource_counterpart_for_machine(
      db=db,
      machine_orm=machine_orm,
      is_resource=effective_is_resource,
      resource_counterpart_accession_id=update_data.get(
        "resource_counterpart_accession_id",
      ),
      resource_def_name=update_data.get("resource_def_name"),
      resource_properties_json=update_data.get("resource_properties_json"),
      resource_initial_status=update_data.get("resource_initial_status"),
    )

    await db.commit()
    await db.refresh(machine_orm)  # type: ignore
    if machine_orm.resource_counterpart:
      await db.refresh(machine_orm.resource_counterpart)
    logger.info("%s Successfully committed updated machine.", log_prefix)
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"{log_prefix} Database integrity error during update. "
      f"This might occur if a unique constraint is violated. Details: {e}"
    )
    logger.exception(error_message)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception("%s Unexpected error during update. Rolling back.", log_prefix)
    raise e

  logger.info("%s Update operation completed.", log_prefix)
  return machine_orm


async def read_machine(
  db: AsyncSession, machine_accession_id: uuid.UUID,
) -> MachineOrm | None:
  """Retrieve a specific machine by its ID."""  # type: ignore
  logger.info("Attempting to retrieve machine with ID: %s.", machine_accession_id)
  result = await db.execute(
    select(MachineOrm)
    .options(joinedload(MachineOrm.resource_counterpart))
    .filter(MachineOrm.accession_id == machine_accession_id),
  )
  machine = result.scalar_one_or_none()
  if machine:
    logger.info(
      "Successfully retrieved machine ID %s: '%s'.",
      machine_accession_id,
      machine.name,
    )
  else:
    logger.info("Machine with ID %s not found.", machine_accession_id)
  return machine


async def read_machine_by_name(db: AsyncSession, name: str) -> MachineOrm | None:
  """Retrieve a specific machine by its name."""
  logger.info("Attempting to retrieve machine with name: '%s'.", name)
  result = await db.execute(  # type: ignore
    select(MachineOrm)
    .options(joinedload(MachineOrm.resource_counterpart))
    .filter(MachineOrm.name == name),
  )
  machine = result.scalar_one_or_none()
  if machine:
    logger.info("Successfully retrieved machine by name '%s'.", name)
  else:
    logger.info("Machine with name '%s' not found.", name)
  return machine


async def read_machines_by_workcell_id(
  db: AsyncSession, workcell_accession_id: uuid.UUID,
) -> Sequence[MachineOrm]:
  """Retrieve all machines associated with a specific workcell ID."""  # type: ignore
  logger.info("Retrieving machines for workcell ID: %s.", workcell_accession_id)
  stmt = (
    select(MachineOrm)
    .options(joinedload(MachineOrm.resource_counterpart))
    .filter(MachineOrm.workcell_accession_id == workcell_accession_id)
    .order_by(MachineOrm.name)
  )
  result = await db.execute(stmt)
  machines = result.scalars().all()
  logger.info(
    "Found %d machines for workcell ID %s.", len(machines), workcell_accession_id,
  )
  return machines


async def list_machines(
  db: AsyncSession,
  status: MachineStatusEnum | None = None,
  pylabrobot_class_filter: str | None = None,
  workcell_accession_id: uuid.UUID | None = None,
  current_protocol_run_accession_id_filter: uuid.UUID | None = None,
  name_filter: str | None = None,
  limit: int = 100,
  offset: int = 0,
) -> list[MachineOrm]:
  """List all machines with optional filtering and pagination."""  # type: ignore
  logger.info(
    "Listing machines with various filters (limit=%d, offset=%d).", limit, offset,
  )
  stmt = select(MachineOrm).options(joinedload(MachineOrm.resource_counterpart))
  if status:
    stmt = stmt.filter(MachineOrm.status == status)
  if pylabrobot_class_filter:
    stmt = stmt.filter(MachineOrm.fqn.like(f"%{pylabrobot_class_filter}%"))
  if workcell_accession_id:
    stmt = stmt.filter(MachineOrm.workcell_accession_id == workcell_accession_id)
  if current_protocol_run_accession_id_filter:
    stmt = stmt.filter(
      MachineOrm.current_protocol_run_accession_id
      == current_protocol_run_accession_id_filter,
    )
  if name_filter:
    stmt = stmt.filter(MachineOrm.name.ilike(f"%{name_filter}%"))
  stmt = stmt.order_by(MachineOrm.name).limit(limit).offset(offset)
  result = await db.execute(stmt)
  machines = list(result.scalars().all())
  logger.info("Found %d machines.", len(machines))
  return machines


async def update_machine_status(
  db: AsyncSession,
  machine_accession_id: uuid.UUID,
  new_status: MachineStatusEnum,
  status_details: str | None = None,
  current_protocol_run_accession_id: uuid.UUID | None = None,
) -> MachineOrm | None:
  """Update the status of a specific machine."""  # type: ignore
  logger.info(
    "Attempting to update status for machine ID %s to '%s'.",
    machine_accession_id,
    new_status.value,
  )
  machine_orm = await read_machine(db, machine_accession_id)
  if not machine_orm:
    logger.warning(
      "Machine with ID %s not found for status update.", machine_accession_id,
    )
    return None

  logger.debug(
    "Machine '%s' (ID: %s) status changing from '%s' to '%s'.",  # type: ignore
    machine_orm.name,
    machine_accession_id,
    machine_orm.status.value,
    new_status.value,
  )
  machine_orm.status = new_status

  if new_status == MachineStatusEnum.IN_USE:
    machine_orm.current_protocol_run_accession_id = current_protocol_run_accession_id
    logger.debug(
      "Machine '%s' (ID: %s) set to IN_USE with protocol run GUID: %s.",  # type: ignore
      machine_orm.name,
      machine_accession_id,
      current_protocol_run_accession_id,
    )
  elif (
    machine_orm.current_protocol_run_accession_id == current_protocol_run_accession_id
  ):
    machine_orm.current_protocol_run_accession_id = None
    logger.debug(  # type: ignore
      "Machine '%s' (ID: %s) protocol run GUID cleared as it matches the "
      "current one and status is no longer IN_USE.",
      machine_orm.name,
      machine_accession_id,
    )

  if new_status != MachineStatusEnum.OFFLINE:
    machine_orm.last_seen_online = datetime.datetime.now(datetime.timezone.utc)
    logger.debug(  # type: ignore
      "Machine '%s' (ID: %s) last seen online updated.",
      machine_orm.name,
      machine_accession_id,
    )

  try:
    await db.commit()
    await db.refresh(machine_orm)  # type: ignore
    logger.info(
      "Successfully updated status for machine ID %s to '%s'.",
      machine_accession_id,
      new_status.value,
    )
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error updating status for machine ID %s. Rolling back.",
      machine_accession_id,
    )
    raise e
  return machine_orm


async def delete_machine(db: AsyncSession, machine_accession_id: uuid.UUID) -> bool:
  """Delete a specific machine by its ID."""
  logger.info("Attempting to delete machine with ID: %s.", machine_accession_id)  # type: ignore
  machine_orm = await read_machine(db, machine_accession_id)
  if not machine_orm:
    logger.warning("Machine with ID %s not found for deletion.", machine_accession_id)
    return False
  try:
    await db.delete(machine_orm)
    await db.commit()
    logger.info(
      "Successfully deleted machine ID %s: '%s'.",
      machine_accession_id,
      machine_orm.name,
    )
    return True
  except IntegrityError as e:
    await db.rollback()
    error_message = (
      f"Cannot delete machine ID {machine_accession_id} due to existing references. "
      f"Details: {e}"
    )
    logger.exception(error_message)
    raise ValueError(error_message) from e
  except Exception as e:
    await db.rollback()
    logger.exception(
      "Unexpected error deleting machine ID %s. Rolling back.", machine_accession_id,
    )
    raise e
