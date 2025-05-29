# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""
praxis/db_services/labware_data_service.py

Service layer for interacting with labware-related data in the database.
This includes Labware Definitions, Labware Instances,"""

import datetime
from typing import Dict, Any, Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete  # Added delete for potential direct use
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import flag_modified


from praxis.backend.models.asset_management_orm import (
    MachineOrm,
    MachineStatusEnum,
)

# --- Managed Device Services ---


async def add_or_update_machine(  # MODIFIED
    db: AsyncSession,  # MODIFIED
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
    if device_id:
        result = await db.execute(select(MachineOrm).filter(MachineOrm.id == device_id))
        device_orm = result.scalar_one_or_none()
        if not device_orm:
            raise ValueError(f"MachineOrm with id {device_id} not found for update.")
    else:
        result = await db.execute(
            select(MachineOrm).filter(
                MachineOrm.user_friendly_name == user_friendly_name
            )
        )
        device_orm = result.scalar_one_or_none()
        if not device_orm:
            device_orm = MachineOrm(user_friendly_name=user_friendly_name)
            db.add(device_orm)

    device_orm.pylabrobot_class_name = pylabrobot_class_name
    device_orm.backend_config_json = backend_config_json  # type: ignore
    device_orm.current_status = current_status
    device_orm.status_details = status_details
    device_orm.workcell_id = workcell_id  # type: ignore
    device_orm.physical_location_description = physical_location_description
    device_orm.properties_json = properties_json  # type: ignore

    try:
        await db.commit()
        await db.refresh(device_orm)
    except IntegrityError:
        await db.rollback()
        raise ValueError(
            f"A device with name '{user_friendly_name}' might already exist or other integrity \
            constraint violated."
        )
    except Exception as e:
        await db.rollback()
        raise e
    return device_orm


async def get_machine_by_id(
    db: AsyncSession, device_id: int
) -> Optional[MachineOrm]:  # MODIFIED
    result = await db.execute(select(MachineOrm).filter(MachineOrm.id == device_id))
    return result.scalar_one_or_none()


async def get_machine_by_name(
    db: AsyncSession, name: str
) -> Optional[MachineOrm]:  # MODIFIED
    result = await db.execute(
        select(MachineOrm).filter(MachineOrm.user_friendly_name == name)
    )
    return result.scalar_one_or_none()


async def list_machines(  # MODIFIED
    db: AsyncSession,  # MODIFIED
    status: Optional[MachineStatusEnum] = None,
    pylabrobot_class_filter: Optional[str] = None,
    workcell_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[MachineOrm]:
    stmt = select(MachineOrm)
    if status:
        stmt = stmt.filter(MachineOrm.current_status == status)
    if pylabrobot_class_filter:
        stmt = stmt.filter(
            MachineOrm.pylabrobot_class_name.like(f"%{pylabrobot_class_filter}%")
        )
    if workcell_id:
        stmt = stmt.filter(MachineOrm.workcell_id == workcell_id)
    stmt = stmt.order_by(MachineOrm.user_friendly_name).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_machine_status(  # MODIFIED
    db: AsyncSession,
    device_id: int,
    new_status: MachineStatusEnum,  # MODIFIED
    status_details: Optional[str] = None,
    current_protocol_run_guid: Optional[str] = None,
) -> Optional[MachineOrm]:
    device_orm = await get_machine_by_id(db, device_id)
    if device_orm:
        device_orm.current_status = new_status
        device_orm.status_details = status_details
        if new_status == MachineStatusEnum.IN_USE:
            device_orm.current_protocol_run_guid = current_protocol_run_guid
        elif device_orm.current_protocol_run_guid == current_protocol_run_guid:
            device_orm.current_protocol_run_guid = None
        if new_status != MachineStatusEnum.OFFLINE:
            device_orm.last_seen_online = datetime.datetime.now(datetime.timezone.utc)
        try:
            await db.commit()
            await db.refresh(device_orm)
        except Exception as e:
            await db.rollback()
            raise e
        return device_orm
    return None


async def delete_machine(db: AsyncSession, device_id: int) -> bool:  # MODIFIED
    device_orm = await get_machine_by_id(db, device_id)
    if not device_orm:
        return False
    try:
        await db.delete(device_orm)  # MODIFIED
        await db.commit()
        return True
    except IntegrityError as e:
        await db.rollback()
        print(f"ERROR: ADS: IntegrityError deleting managed device ID {device_id}: {e}")
        raise ValueError(
            f"Cannot delete device ID {device_id} due to existing references. Details: {e}"
        )
    except Exception as e:
        await db.rollback()
        print(f"ERROR: ADS: Exception deleting managed device ID {device_id}: {e}")
        raise e
