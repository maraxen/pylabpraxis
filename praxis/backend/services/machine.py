# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""Service layer for Machine Data Management.

praxis/db_services/machine_data_service.py

Service layer for interacting with machine-related data in the database.
This includes Machine Definitions, Machine Instances, and Machine configurations.
"""

import datetime
import uuid
from functools import partial
from typing import Any, cast
from uuid import UUID

from sqlalchemy import Column, DateTime, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from praxis.backend.models.orm.machine import MachineOrm, MachineStatusEnum
from praxis.backend.models.pydantic.filters import SearchFilters
from praxis.backend.models.pydantic.machine import MachineCreate, MachineUpdate
from praxis.backend.services.entity_linking import (
  _create_or_link_resource_counterpart_for_machine,
  synchronize_machine_resource_names,
)
from praxis.backend.services.utils.crud_base import CRUDBase
from praxis.backend.services.utils.query_builder import (
  apply_date_range_filters,
  apply_pagination,
  apply_specific_id_filters,
)
from praxis.backend.utils.db import Base
from praxis.backend.utils.logging import get_logger, log_async_runtime_errors

logger = get_logger(__name__)


class MachineService(CRUDBase[MachineOrm, MachineCreate, MachineUpdate]):
  """Service for machine-related operations."""

  def __init__(self, model: type[MachineOrm]):
    super().__init__(model)
    self.machine_data_service_log = partial(
      log_async_runtime_errors,
      logger_instance=logger,
      exception_type=Exception,
      raises=True,
      raises_exception=ValueError,
      return_=None,
    )

  async def create(
    self,
    db: AsyncSession,
    *,
    obj_in: MachineCreate,
  ) -> MachineOrm:
    @self.machine_data_service_log(
      prefix="Machine Data Service: Creating machine - ",
      suffix=" - Ensure the machine data is valid and unique.",
    )
    async def _create_machine_internal():
      """Internal helper for machine creation with logging."""
      log_prefix = f"Machine (Name: '{obj_in.name}', creating new):"
      logger.info("%s Attempting to create new machine.", log_prefix)

      # Check if a machine with this name already exists
      result = await db.execute(select(MachineOrm).filter(MachineOrm.name == obj_in.name))
      if result.scalar_one_or_none():
        error_message = (
          f"{log_prefix} A machine with name '{obj_in.name}' already exists. Use the update "
          f"function for existing machines."
        )
        logger.error(error_message)
        raise ValueError(error_message)

      # Create a new MachineOrm using the base CRUD method
      machine_orm = await super().create(db=db, obj_in=obj_in)
      logger.info("%s Initialized new machine for creation.", log_prefix)

      try:
        await _create_or_link_resource_counterpart_for_machine(
          db=db,
          machine_orm=machine_orm,
          is_resource=obj_in.is_resource,
          resource_counterpart_accession_id=obj_in.resource_counterpart_accession_id,
          resource_definition_name=obj_in.resource_def_name,
          resource_properties_json=obj_in.resource_properties_json,
          resource_status=obj_in.resource_initial_status,
        )

        await db.commit()
        await db.refresh(machine_orm)
        if machine_orm.resource_counterpart:
          await db.refresh(machine_orm.resource_counterpart)
        logger.info("%s Successfully committed new machine.", log_prefix)

      except IntegrityError as e:
        await db.rollback()
        if "uq_assets_name" in str(e.orig):
          error_message = (
            f"{log_prefix} A machine with name '{obj_in.name}' already exists (integrity "
            f"check failed). Details: {e}"
          )
          logger.exception(error_message)
          raise ValueError(error_message) from e
        error_message = f"{log_prefix} Database integrity error during creation. Details: {e}"
        logger.exception(error_message)
        raise ValueError(error_message) from e
      except Exception as e:
        await db.rollback()
        logger.exception("%s Unexpected error during creation. Rolling back.", log_prefix)
        raise e

      logger.info("%s Creation operation completed.", log_prefix)
      return machine_orm

    return await _create_machine_internal()

  async def update(
    self,
    db: AsyncSession,
    *,
    db_obj: MachineOrm,
    obj_in: MachineUpdate | dict[str, Any],
  ) -> MachineOrm:
    @self.machine_data_service_log(
      prefix="Machine Data Service: Updating machine - ",
      suffix=" - Ensure the machine data is valid and unique.",
    )
    async def _update_machine_internal():
      """Internal helper for machine update with logging."""
      update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
      log_prefix = f"Machine (ID: {db_obj.accession_id}, updating):"
      logger.info("%s Attempting to update machine.", log_prefix)

      # Check for name conflict if it's being changed
      name = update_data.get("name")
      if name is not None and db_obj.name != name:
        existing_name_check = await db.execute(
          select(MachineOrm)
          .filter(MachineOrm.name == name)
          .filter(MachineOrm.accession_id != db_obj.accession_id),
        )
        if existing_name_check.scalar_one_or_none():
          error_message = (
            f"{log_prefix} Cannot update name to '{name}' as it already exists for another machine."
          )
          logger.error(error_message)
          raise ValueError(error_message)
        db_obj.name = name

        # Synchronize name with linked resource counterpart if it exists
        await synchronize_machine_resource_names(db, db_obj, name)

      # Update attributes using the base CRUD method
      updated_machine = await super().update(db=db, db_obj=db_obj, obj_in=obj_in)

      # Handle `is_resource` update and potential resource counterpart linking
      effective_is_resource = (
        update_data["is_resource"]
        if "is_resource" in update_data
        else (db_obj.resource_counterpart_accession_id is not None)
      )

      try:
        await _create_or_link_resource_counterpart_for_machine(
          db=db,
          machine_orm=updated_machine,
          is_resource=effective_is_resource,
          resource_counterpart_accession_id=update_data.get(
            "resource_counterpart_accession_id",
          ),
          resource_definition_name=update_data.get("resource_def_name"),
          resource_properties_json=update_data.get("resource_properties_json"),
          resource_status=update_data.get("resource_initial_status"),
        )

        await db.commit()
        await db.refresh(updated_machine)
        if updated_machine.resource_counterpart:
          await db.refresh(updated_machine.resource_counterpart)
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
      return updated_machine

    return await _update_machine_internal()

  async def get_multi(
    self,
    db: AsyncSession,
    *,
    filters: SearchFilters,
    status: MachineStatusEnum | None = None,
    pylabrobot_class_filter: str | None = None,
    name_filter: str | None = None,
  ) -> list[MachineOrm]:
    """List all machines with optional filtering and pagination."""
    logger.info(
      "Listing machines with filters: %s",
      filters.model_dump_json(),
    )
    stmt = select(self.model).options(joinedload(self.model.resource_counterpart))

    if status:
      stmt = stmt.filter(self.model.status == status)
    if pylabrobot_class_filter:
      stmt = stmt.filter(self.model.fqn.like(f"%{pylabrobot_class_filter}%"))
    if name_filter:
      stmt = stmt.filter(self.model.name.ilike(f"%{name_filter}%"))

    # Apply generic filters from query_builder
    stmt = apply_specific_id_filters(stmt, filters, cast("Base", self.model))
    stmt = apply_date_range_filters(stmt, filters, cast("Column[DateTime]", self.model.created_at))
    # MachineOrm does not have a generic properties_json for apply_property_filters

    stmt = apply_pagination(stmt, filters)

    stmt = stmt.order_by(self.model.name)
    result = await db.execute(stmt)
    machines = list(result.scalars().all())
    logger.info("Found %d machines.", len(machines))
    return machines

  async def update_machine_status(
    self,
    db: AsyncSession,
    machine_accession_id: uuid.UUID,
    new_status: MachineStatusEnum,
    status_details: str | None = None,
    current_protocol_run_accession_id: uuid.UUID | None = None,
  ) -> MachineOrm | None:
    """Update the status of a specific machine."""
    logger.info(
      "Attempting to update status for machine ID %s to '%s'.",
      machine_accession_id,
      new_status.value,
    )
    machine_orm = await self.get(db, accession_id=machine_accession_id)
    if not machine_orm:
      logger.warning(
        "Machine with ID %s not found for status update.",
        machine_accession_id,
      )
      return None

    logger.debug(
      "Machine '%s' (ID: %s) status changing from '%s' to '%s'.",
      machine_orm.name,
      machine_accession_id,
      machine_orm.status.value,
      new_status.value,
    )
    machine_orm.status = new_status
    machine_orm.status_details = status_details

    if new_status == MachineStatusEnum.IN_USE:
      machine_orm.current_protocol_run_accession_id = current_protocol_run_accession_id
      logger.debug(
        "Machine '%s' (ID: %s) set to IN_USE with protocol run GUID: %s.",
        machine_orm.name,
        machine_accession_id,
        current_protocol_run_accession_id,
      )
    elif machine_orm.current_protocol_run_accession_id == current_protocol_run_accession_id:
      machine_orm.current_protocol_run_accession_id = None
      logger.debug(
        "Machine '%s' (ID: %s) protocol run GUID cleared as it matches the "
        "current one and status is no longer IN_USE.",
        machine_orm.name,
        machine_accession_id,
      )

    if new_status != MachineStatusEnum.OFFLINE:
      machine_orm.last_seen_online = datetime.datetime.now(datetime.timezone.utc)
      logger.debug(
        "Machine '%s' (ID: %s) last seen online updated.",
        machine_orm.name,
        machine_accession_id,
      )

    try:
      await db.commit()
      await db.refresh(machine_orm)
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

  async def remove(self, db: AsyncSession, *, accession_id: str | UUID) -> MachineOrm | None:
    """Delete a specific machine by its ID."""
    logger.info("Attempting to delete machine with ID: %s.", accession_id)
    machine_orm = await super().remove(db, accession_id=accession_id)
    if not machine_orm:
      logger.warning("Machine with ID %s not found for deletion.", accession_id)
      return None
    try:
      await db.commit()
      logger.info(
        "Successfully deleted machine ID %s: '%s'.",
        accession_id,
        machine_orm.name,
      )
      return machine_orm
    except IntegrityError as e:
      await db.rollback()
      error_message = (
        f"Cannot delete machine ID {accession_id} due to existing references. Details: {e}"
      )
      logger.exception(error_message)
      raise ValueError(error_message) from e
    except Exception as e:
      await db.rollback()
      logger.exception(
        "Unexpected error deleting machine ID %s. Rolling back.",
        accession_id,
      )
      raise e


machine_service = MachineService(MachineOrm)
