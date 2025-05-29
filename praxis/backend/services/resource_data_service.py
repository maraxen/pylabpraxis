# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""
praxis/db_services/resource_data_service.py

Service layer for interacting with resource-related data in the database.
This includes Resource Definitions, Resource Instances,"""

import datetime
from typing import Dict, Any, Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete  # Added delete for potential direct use
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.attributes import flag_modified


from praxis.backend.models import (
    ResourceDefinitionCatalogOrm,
    ResourceInstanceOrm,
    ResourceInstanceStatusEnum,
)

# --- Resource Definition Catalog Services ---


async def add_or_update_resource_definition(  # MODIFIED
    db: AsyncSession,  # MODIFIED
    pylabrobot_definition_name: str,
    python_fqn: str,
    praxis_resource_type_name: Optional[str] = None,
    description: Optional[str] = None,
    is_consumable: bool = True,
    nominal_volume_ul: Optional[float] = None,
    material: Optional[str] = None,
    manufacturer: Optional[str] = None,
    plr_definition_details_json: Optional[Dict[str, Any]] = None,
) -> ResourceDefinitionCatalogOrm:
    result = await db.execute(
        select(ResourceDefinitionCatalogOrm).filter(
            ResourceDefinitionCatalogOrm.pylabrobot_definition_name
            == pylabrobot_definition_name
        )
    )
    def_orm = result.scalar_one_or_none()

    if not def_orm:
        def_orm = ResourceDefinitionCatalogOrm(
            pylabrobot_definition_name=pylabrobot_definition_name
        )
        db.add(def_orm)

    def_orm.python_fqn = python_fqn
    def_orm.praxis_resource_type_name = praxis_resource_type_name
    def_orm.description = description
    def_orm.is_consumable = is_consumable
    def_orm.nominal_volume_ul = nominal_volume_ul
    def_orm.material = material
    def_orm.manufacturer = manufacturer
    def_orm.plr_definition_details_json = plr_definition_details_json  # type: ignore

    try:
        await db.commit()
        await db.refresh(def_orm)
    except IntegrityError:
        await db.rollback()
        raise ValueError(
            f"Integrity error for resource definition '{pylabrobot_definition_name}'."
        )
    except Exception as e:
        await db.rollback()
        raise e
    return def_orm


async def get_resource_definition(
    db: AsyncSession, pylabrobot_definition_name: str
) -> Optional[ResourceDefinitionCatalogOrm]:  # MODIFIED
    result = await db.execute(
        select(ResourceDefinitionCatalogOrm).filter(
            ResourceDefinitionCatalogOrm.pylabrobot_definition_name
            == pylabrobot_definition_name
        )
    )
    return result.scalar_one_or_none()


async def list_resource_definitions(  # MODIFIED
    db: AsyncSession,  # MODIFIED
    manufacturer: Optional[str] = None,
    is_consumable: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[ResourceDefinitionCatalogOrm]:
    stmt = select(ResourceDefinitionCatalogOrm)
    if manufacturer:
        stmt = stmt.filter(
            ResourceDefinitionCatalogOrm.manufacturer.ilike(f"%{manufacturer}%")
        )  # type: ignore
    if is_consumable is not None:
        stmt = stmt.filter(ResourceDefinitionCatalogOrm.is_consumable == is_consumable)
    stmt = (
        stmt.order_by(ResourceDefinitionCatalogOrm.pylabrobot_definition_name)
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_resource_definition_by_name(
    db: AsyncSession, pylabrobot_definition_name: str
) -> Optional[ResourceDefinitionCatalogOrm]:  # MODIFIED
    return await get_resource_definition(db, pylabrobot_definition_name)


async def get_resource_definition_by_fqn(
    db: AsyncSession, python_fqn: str
) -> Optional[ResourceDefinitionCatalogOrm]:  # MODIFIED
    result = await db.execute(
        select(ResourceDefinitionCatalogOrm).filter(
            ResourceDefinitionCatalogOrm.python_fqn == python_fqn
        )
    )
    return result.scalar_one_or_none()


async def delete_resource_definition(
    db: AsyncSession, pylabrobot_definition_name: str
) -> bool:  # MODIFIED
    def_orm = await get_resource_definition(db, pylabrobot_definition_name)
    if not def_orm:
        return False

    try:
        await db.delete(def_orm)  # MODIFIED
        await db.commit()
        return True
    except IntegrityError as e:
        await db.rollback()
        print(
            f"ERROR: ADS: IntegrityError deleting resource definition '{pylabrobot_definition_name}': {e}"
        )
        return False
    except Exception as e:
        await db.rollback()
        print(
            f"ERROR: ADS: Exception deleting resource definition '{pylabrobot_definition_name}': {e}"
        )
        raise e


# --- Resource Instance Services ---
async def add_resource_instance(  # MODIFIED
    db: AsyncSession,  # MODIFIED
    user_assigned_name: str,
    pylabrobot_definition_name: str,
    initial_status: ResourceInstanceStatusEnum = ResourceInstanceStatusEnum.AVAILABLE_IN_STORAGE,
    lot_number: Optional[str] = None,
    expiry_date: Optional[datetime.datetime] = None,
    properties_json: Optional[Dict[str, Any]] = None,
    physical_location_description: Optional[str] = None,
    is_permanent_fixture: bool = False,
) -> ResourceInstanceOrm:
    definition = await get_resource_definition(db, pylabrobot_definition_name)
    if not definition:
        raise ValueError(
            f"Resource definition '{pylabrobot_definition_name}' not found in catalog."
        )

    instance_orm = ResourceInstanceOrm(
        user_assigned_name=user_assigned_name,
        pylabrobot_definition_name=pylabrobot_definition_name,
        current_status=initial_status,
        lot_number=lot_number,
        expiry_date=expiry_date,
        properties_json=properties_json,  # type: ignore
        physical_location_description=physical_location_description,
        is_permanent_fixture=is_permanent_fixture,
    )
    db.add(instance_orm)
    try:
        await db.commit()
        await db.refresh(instance_orm)
    except IntegrityError:
        await db.rollback()
        raise ValueError(
            f"A resource instance with name '{user_assigned_name}' might already exist."
        )
    except Exception as e:
        await db.rollback()
        raise e
    return instance_orm


async def get_resource_instance_by_id(
    db: AsyncSession, instance_id: int
) -> Optional[ResourceInstanceOrm]:  # MODIFIED
    stmt = (
        select(ResourceInstanceOrm)
        .options(
            joinedload(ResourceInstanceOrm.resource_definition),
            joinedload(ResourceInstanceOrm.location_machine),
        )
        .filter(ResourceInstanceOrm.id == instance_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_resource_instance_by_name(
    db: AsyncSession, user_assigned_name: str
) -> Optional[ResourceInstanceOrm]:  # MODIFIED
    stmt = (
        select(ResourceInstanceOrm)
        .options(
            joinedload(ResourceInstanceOrm.resource_definition),
            joinedload(ResourceInstanceOrm.location_machine),
        )
        .filter(ResourceInstanceOrm.user_assigned_name == user_assigned_name)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_resource_instances(  # MODIFIED
    db: AsyncSession,  # MODIFIED
    pylabrobot_definition_name: Optional[str] = None,
    status: Optional[ResourceInstanceStatusEnum] = None,
    location_machine_id: Optional[int] = None,
    on_deck_slot: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[ResourceInstanceOrm]:
    stmt = select(ResourceInstanceOrm).options(
        joinedload(ResourceInstanceOrm.resource_definition),
        joinedload(ResourceInstanceOrm.location_machine),
    )
    if pylabrobot_definition_name:
        stmt = stmt.filter(
            ResourceInstanceOrm.pylabrobot_definition_name == pylabrobot_definition_name
        )
    if status:
        stmt = stmt.filter(ResourceInstanceOrm.current_status == status)
    if location_machine_id:
        stmt = stmt.filter(
            ResourceInstanceOrm.location_machine_id == location_machine_id
        )
    if on_deck_slot:
        stmt = stmt.filter(ResourceInstanceOrm.current_deck_slot_name == on_deck_slot)

    stmt = (
        stmt.order_by(ResourceInstanceOrm.user_assigned_name)
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_resource_instance_location_and_status(  # MODIFIED
    db: AsyncSession,  # MODIFIED
    resource_instance_id: int,
    new_status: Optional[ResourceInstanceStatusEnum] = None,
    location_machine_id: Optional[int] = None,
    current_deck_slot_name: Optional[str] = None,
    physical_location_description: Optional[str] = None,
    properties_json_update: Optional[Dict[str, Any]] = None,
    current_protocol_run_guid: Optional[str] = None,
    status_details: Optional[str] = None,
) -> Optional[ResourceInstanceOrm]:
    instance_orm = await get_resource_instance_by_id(db, resource_instance_id)
    if instance_orm:
        if new_status is not None:
            instance_orm.current_status = new_status

        if (
            location_machine_id is not None
            or current_deck_slot_name is not None
            or physical_location_description is not None
        ):
            instance_orm.location_machine_id = location_machine_id  # type: ignore
            instance_orm.current_deck_slot_name = current_deck_slot_name
            instance_orm.physical_location_description = physical_location_description

        if status_details is not None:
            instance_orm.status_details = status_details

        if (
            new_status == ResourceInstanceStatusEnum.IN_USE
            and current_protocol_run_guid is not None
        ):
            instance_orm.current_protocol_run_guid = current_protocol_run_guid
        elif new_status != ResourceInstanceStatusEnum.IN_USE:
            if instance_orm.current_protocol_run_guid is not None:
                instance_orm.current_protocol_run_guid = None

        if properties_json_update is not None:
            instance_orm.properties_json = properties_json_update  # type: ignore
            if instance_orm.properties_json is not None:
                flag_modified(instance_orm, "properties_json")

        try:
            await db.commit()
            await db.refresh(instance_orm)
        except Exception as e:
            await db.rollback()
            raise e
        return instance_orm
    return None


async def delete_resource_instance(
    db: AsyncSession, instance_id: int
) -> bool:  # MODIFIED
    stmt = select(ResourceInstanceOrm).filter(ResourceInstanceOrm.id == instance_id)
    result = await db.execute(stmt)
    instance_orm = result.scalar_one_or_none()

    if not instance_orm:
        return False

    try:
        await db.delete(instance_orm)  # MODIFIED
        await db.commit()
        return True
    except IntegrityError as e:
        await db.rollback()
        print(
            f"ERROR: ADS: IntegrityError deleting resource instance ID {instance_id}: {e}"
        )
        raise ValueError(
            f"Cannot delete resource instance ID {instance_id} due to existing references (e.g., in deck layouts). Details: {e}"
        )
    except Exception as e:
        await db.rollback()
        print(f"ERROR: ADS: Exception deleting resource instance ID {instance_id}: {e}")
        raise e
