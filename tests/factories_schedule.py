"""Factory functions for creating test fixtures for Schedule and Output models.

These factories handle the complexity of kw_only fields, init=False relationships,
and proper field initialization to make tests easier to write and maintain.

Usage:
    from tests.factories_schedule import create_schedule_entry, create_asset_reservation

    async def test_something(db_session):
        entry = await create_schedule_entry(db_session)
        reservation = await create_asset_reservation(db_session)
"""
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from praxis.backend.models.orm.schedule import ScheduleEntryOrm, AssetReservationOrm
from praxis.backend.models.orm.protocol import (
    FunctionProtocolDefinitionOrm,
    ProtocolRunOrm,
    FunctionCallLogOrm,
    ProtocolSourceRepositoryOrm,
    FileSystemProtocolSourceOrm,
)
from praxis.backend.models.orm.machine import MachineOrm
from praxis.backend.models.orm.resource import ResourceOrm
from praxis.backend.models.orm.outputs import FunctionDataOutputOrm
from praxis.backend.models.enums import (
    ScheduleStatusEnum,
    AssetReservationStatusEnum,
    AssetType,
    DataOutputTypeEnum,
    SpatialContextEnum,
)
from praxis.backend.utils.uuid import uuid7


async def create_protocol_definition(
    db_session: AsyncSession,
    source_repository: ProtocolSourceRepositoryOrm | None = None,
    file_system_source: FileSystemProtocolSourceOrm | None = None,
    **kwargs
) -> FunctionProtocolDefinitionOrm:
    """Factory for creating FunctionProtocolDefinitionOrm."""
    # Create source_repository if not provided
    if not source_repository:
        source_repository = ProtocolSourceRepositoryOrm(
            name="test-repo",
            git_url="https://github.com/test/repo.git",
        )
        db_session.add(source_repository)
        await db_session.flush()

    # Create file_system_source if not provided
    if not file_system_source:
        file_system_source = FileSystemProtocolSourceOrm(
            name="test-fs-source",
            base_path="/tmp/protocols",
        )
        db_session.add(file_system_source)
        await db_session.flush()

    defaults = {
        "name": f"test_protocol_{uuid7()}",
        "fqn": f"test.protocols.test_protocol_{uuid7()}",
        "version": "1.0.0",
        "is_top_level": True,
        "source_repository": source_repository,
        "file_system_source": file_system_source,
    }
    defaults.update(kwargs)

    protocol = FunctionProtocolDefinitionOrm(**defaults)
    db_session.add(protocol)
    await db_session.flush()
    await db_session.refresh(protocol)

    return protocol


async def create_protocol_run(
    db_session: AsyncSession,
    protocol_definition: FunctionProtocolDefinitionOrm | None = None,
    **kwargs
) -> ProtocolRunOrm:
    """Factory for creating ProtocolRunOrm."""
    if not protocol_definition:
        protocol_definition = await create_protocol_definition(db_session)

    defaults = {
        "name": f"test_protocol_run_{uuid7()}",
        "top_level_protocol_definition_accession_id": protocol_definition.accession_id,
    }
    defaults.update(kwargs)

    run = ProtocolRunOrm(**defaults)
    db_session.add(run)
    await db_session.flush()
    await db_session.refresh(run)

    return run


async def create_schedule_entry(
    db_session: AsyncSession,
    protocol_run: ProtocolRunOrm | None = None,
    **kwargs
) -> ScheduleEntryOrm:
    """Factory for creating ScheduleEntryOrm.

    Handles kw_only fields and relationship setup automatically.

    Args:
        db_session: AsyncSession for database operations
        protocol_run: Optional ProtocolRunOrm to associate with
        **kwargs: Override default values

    Returns:
        Created and persisted ScheduleEntryOrm
    """
    if not protocol_run:
        protocol_run = await create_protocol_run(db_session)

    # Build entry with all kw_only fields as keyword args
    entry = ScheduleEntryOrm(
        status=kwargs.get('status', ScheduleStatusEnum.QUEUED),
        priority=kwargs.get('priority', 1),
        name=kwargs.get('name', f"test_schedule_entry_{uuid7()}"),
        protocol_run=protocol_run,
        scheduled_at=kwargs.get('scheduled_at', datetime.now(timezone.utc)),
        asset_analysis_completed_at=kwargs.get('asset_analysis_completed_at', None),
        assets_reserved_at=kwargs.get('assets_reserved_at', None),
        execution_started_at=kwargs.get('execution_started_at', None),
        execution_completed_at=kwargs.get('execution_completed_at', None),
    )

    # Set optional JSONB fields if provided
    if 'asset_requirements_json' in kwargs:
        entry.asset_requirements_json = kwargs['asset_requirements_json']
    if 'user_params_json' in kwargs:
        entry.user_params_json = kwargs['user_params_json']
    if 'initial_state_json' in kwargs:
        entry.initial_state_json = kwargs['initial_state_json']

    db_session.add(entry)
    await db_session.flush()
    await db_session.refresh(entry)

    return entry


async def create_machine(
    db_session: AsyncSession,
    **kwargs
) -> MachineOrm:
    """Factory for creating MachineOrm."""
    defaults = {
        "accession_id": uuid7(),
        "name": f"test_machine_{uuid7()}",
        "fqn": f"test.machines.TestMachine_{uuid7()}",
        "asset_type": AssetType.MACHINE,
    }
    defaults.update(kwargs)

    machine = MachineOrm(**defaults)
    db_session.add(machine)
    await db_session.flush()
    await db_session.refresh(machine)

    return machine


async def create_resource(
    db_session: AsyncSession,
    **kwargs
) -> ResourceOrm:
    """Factory for creating ResourceOrm."""
    defaults = {
        "accession_id": uuid7(),
        "name": f"test_resource_{uuid7()}",
        "fqn": f"test.resources.TestResource_{uuid7()}",
        "asset_type": AssetType.RESOURCE,
    }
    defaults.update(kwargs)

    resource = ResourceOrm(**defaults)
    db_session.add(resource)
    await db_session.flush()
    await db_session.refresh(resource)

    return resource


async def create_asset_reservation(
    db_session: AsyncSession,
    protocol_run: ProtocolRunOrm | None = None,
    schedule_entry: ScheduleEntryOrm | None = None,
    asset: MachineOrm | None = None,
    **kwargs
) -> AssetReservationOrm:
    """Factory for creating AssetReservationOrm.

    NOTE: Due to unique constraint on protocol_run_accession_id, each protocol
    run can only have ONE reservation. This appears to be a schema limitation.

    Handles all kw_only fields and relationships automatically.

    Args:
        db_session: AsyncSession for database operations
        protocol_run: Optional ProtocolRunOrm to associate with
        schedule_entry: Optional ScheduleEntryOrm to associate with
        asset: Optional asset (Machine/Resource) to reserve
        **kwargs: Override default values

    Returns:
        Created and persisted AssetReservationOrm
    """
    # Create dependencies if not provided
    if not protocol_run:
        protocol_run = await create_protocol_run(db_session)
    if not schedule_entry:
        schedule_entry = await create_schedule_entry(db_session, protocol_run)
    if not asset:
        asset = await create_machine(db_session)

    # Build reservation with all kw_only fields as keyword args
    reservation = AssetReservationOrm(
        protocol_run_accession_id=protocol_run.accession_id,
        schedule_entry_accession_id=schedule_entry.accession_id,
        asset_accession_id=asset.accession_id,
        asset_name=asset.name,
        redis_lock_key=kwargs.get('redis_lock_key', f"lock:asset:{asset.accession_id}"),
        lock_timeout_seconds=kwargs.get('lock_timeout_seconds', 3600),
        status=kwargs.get('status', AssetReservationStatusEnum.PENDING),
        asset_type=kwargs.get('asset_type', AssetType.ASSET),
    )

    # Set optional fields if provided
    if 'redis_lock_value' in kwargs:
        reservation.redis_lock_value = kwargs['redis_lock_value']
    if 'released_at' in kwargs:
        reservation.released_at = kwargs['released_at']
    if 'expires_at' in kwargs:
        reservation.expires_at = kwargs['expires_at']
    if 'required_capabilities_json' in kwargs:
        reservation.required_capabilities_json = kwargs['required_capabilities_json']

    # Set relationships (have init=False)
    reservation.protocol_run = protocol_run
    reservation.schedule_entry = schedule_entry
    reservation.asset = asset

    db_session.add(reservation)
    await db_session.flush()
    await db_session.refresh(reservation)

    return reservation


async def create_function_call_log(
    db_session: AsyncSession,
    protocol_run: ProtocolRunOrm | None = None,
    protocol_definition: FunctionProtocolDefinitionOrm | None = None,
    **kwargs
) -> FunctionCallLogOrm:
    """Factory for creating FunctionCallLogOrm."""
    if not protocol_run:
        protocol_run = await create_protocol_run(db_session)
    if not protocol_definition:
        # Use the protocol run's definition
        await db_session.refresh(protocol_run, ["top_level_protocol_definition"])
        protocol_definition = protocol_run.top_level_protocol_definition

    defaults = {
        "protocol_run_accession_id": protocol_run.accession_id,
        "function_protocol_definition_accession_id": protocol_definition.accession_id,
        "sequence_in_run": kwargs.get('sequence_in_run', 0),
        "start_time": kwargs.get('start_time', datetime.now(timezone.utc)),
    }
    # Don't let kwargs override the required fields
    for key in ['protocol_run_accession_id', 'function_protocol_definition_accession_id']:
        if key in kwargs:
            del kwargs[key]
    defaults.update(kwargs)

    call_log = FunctionCallLogOrm(**defaults)

    # Set relationships
    call_log.protocol_run = protocol_run
    call_log.executed_function_definition = protocol_definition

    db_session.add(call_log)
    await db_session.flush()
    await db_session.refresh(call_log)

    return call_log


async def create_function_data_output(
    db_session: AsyncSession,
    protocol_run: ProtocolRunOrm | None = None,
    function_call_log: FunctionCallLogOrm | None = None,
    **kwargs
) -> FunctionDataOutputOrm:
    """Factory for creating FunctionDataOutputOrm.

    Handles kw_only fields and optional relationships.

    Args:
        db_session: AsyncSession for database operations
        protocol_run: Optional ProtocolRunOrm to associate with
        function_call_log: Optional FunctionCallLogOrm to associate with
        **kwargs: Override default values including:
            - data_type: DataOutputTypeEnum
            - data_key: str
            - spatial_context: SpatialContextEnum
            - data_value_numeric: float
            - data_value_json: dict
            - data_value_text: str
            - data_value_binary: bytes
            - resource_accession_id: UUID (for resource association)
            - machine_accession_id: UUID (for machine association)
            - deck_accession_id: UUID (for deck association)
            - spatial_coordinates_json: dict
            - measurement_conditions_json: dict

    Returns:
        Created and persisted FunctionDataOutputOrm
    """
    # Create dependencies if not provided
    if not function_call_log:
        function_call_log = await create_function_call_log(db_session, protocol_run)
    if not protocol_run:
        protocol_run = function_call_log.protocol_run

    # Build output with kw_only fields
    output = FunctionDataOutputOrm(
        protocol_run_accession_id=protocol_run.accession_id,
        function_call_log_accession_id=function_call_log.accession_id,
        data_type=kwargs.get('data_type', DataOutputTypeEnum.UNKNOWN),
        data_key=kwargs.get('data_key', ""),
        spatial_context=kwargs.get('spatial_context', SpatialContextEnum.GLOBAL),
    )

    # Set optional numeric data
    if 'data_value_numeric' in kwargs:
        output.data_value_numeric = kwargs['data_value_numeric']

    # Set optional JSONB data
    if 'data_value_json' in kwargs:
        output.data_value_json = kwargs['data_value_json']
    if 'spatial_coordinates_json' in kwargs:
        output.spatial_coordinates_json = kwargs['spatial_coordinates_json']
    if 'measurement_conditions_json' in kwargs:
        output.measurement_conditions_json = kwargs['measurement_conditions_json']

    # Set optional text/binary data
    if 'data_value_text' in kwargs:
        output.data_value_text = kwargs['data_value_text']
    if 'data_value_binary' in kwargs:
        output.data_value_binary = kwargs['data_value_binary']

    # Set optional file info
    if 'file_path' in kwargs:
        output.file_path = kwargs['file_path']
    if 'file_size_bytes' in kwargs:
        output.file_size_bytes = kwargs['file_size_bytes']

    # Set optional FK relationships
    if 'resource_accession_id' in kwargs:
        output.resource_accession_id = kwargs['resource_accession_id']
    if 'machine_accession_id' in kwargs:
        output.machine_accession_id = kwargs['machine_accession_id']
    if 'deck_accession_id' in kwargs:
        output.deck_accession_id = kwargs['deck_accession_id']

    # Set relationships
    output.protocol_run = protocol_run
    output.function_call_log = function_call_log

    db_session.add(output)
    await db_session.flush()
    await db_session.refresh(output)

    return output
