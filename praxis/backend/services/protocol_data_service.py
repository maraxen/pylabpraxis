# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""
praxis/db_services/protocol_data_service.py

Service layer for interacting with protocol-related data in the database.
This includes definitions for protocol sources, static protocol definitions,
protocol run instances, and function call logs.
"""

import datetime
import json
from typing import Dict, Optional, List, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, or_, select, update
from sqlalchemy.orm import joinedload, selectinload, aliased

from praxis.backend.models import (
    ProtocolSourceRepositoryOrm,
    FileSystemProtocolSourceOrm,
    FunctionProtocolDefinitionOrm,
    ParameterDefinitionOrm,
    AssetDefinitionOrm,
    ProtocolRunOrm,
    FunctionCallLogOrm,
    ProtocolSourceStatusEnum,
    ProtocolRunStatusEnum,
    FunctionCallStatusEnum,
    FunctionProtocolDefinitionModel,
)


# --- Protocol Source Management ---
async def add_or_update_protocol_source_repository(  # MODIFIED: async def
    db: AsyncSession,
    name: str,
    git_url: str,
    default_ref: str = "main",  # MODIFIED: DbSession -> AsyncSession
    local_checkout_path: Optional[str] = None,
    status: ProtocolSourceStatusEnum = ProtocolSourceStatusEnum.ACTIVE,
    auto_sync_enabled: bool = True,
    source_id: Optional[int] = None,
) -> ProtocolSourceRepositoryOrm:
    if source_id:
        result = await db.execute(
            select(ProtocolSourceRepositoryOrm).filter(
                ProtocolSourceRepositoryOrm.id == source_id
            )
        )
        source_repo = result.scalar_one_or_none()
        if not source_repo:
            raise ValueError(f"Repo source id {source_id} not found.")
    else:
        result = await db.execute(
            select(ProtocolSourceRepositoryOrm).filter(
                ProtocolSourceRepositoryOrm.name == name
            )
        )
        source_repo = result.scalar_one_or_none()
        if not source_repo:
            source_repo = ProtocolSourceRepositoryOrm(name=name)
            db.add(source_repo)

    source_repo.git_url = git_url
    source_repo.default_ref = default_ref
    source_repo.local_checkout_path = local_checkout_path
    source_repo.status = status
    source_repo.auto_sync_enabled = auto_sync_enabled
    try:
        await db.commit()
        await db.refresh(source_repo)
    except Exception as e:
        await db.rollback()
        print(f"Error upserting repo source '{name}': {e}")
        raise
    return source_repo


async def add_or_update_file_system_protocol_source(  # MODIFIED: async def
    db: AsyncSession,
    name: str,
    base_path: str,
    is_recursive: bool = True,  # MODIFIED: DbSession -> AsyncSession
    status: ProtocolSourceStatusEnum = ProtocolSourceStatusEnum.ACTIVE,
    source_id: Optional[int] = None,
) -> FileSystemProtocolSourceOrm:
    if source_id:
        result = await db.execute(
            select(FileSystemProtocolSourceOrm).filter(
                FileSystemProtocolSourceOrm.id == source_id
            )
        )
        fs_source = result.scalar_one_or_none()
        if not fs_source:
            raise ValueError(f"FS source id {source_id} not found.")
    else:
        result = await db.execute(
            select(FileSystemProtocolSourceOrm).filter(
                FileSystemProtocolSourceOrm.name == name
            )
        )
        fs_source = result.scalar_one_or_none()
        if not fs_source:
            fs_source = FileSystemProtocolSourceOrm(name=name)
            db.add(fs_source)

    fs_source.base_path = base_path
    fs_source.is_recursive = is_recursive
    fs_source.status = status
    try:
        await db.commit()
        await db.refresh(fs_source)
    except Exception as e:
        await db.rollback()
        print(f"Error upserting FS source '{name}': {e}")
        raise
    return fs_source


# --- Static Protocol Definition Management ---
async def upsert_function_protocol_definition(  # MODIFIED: async def
    db: AsyncSession,
    protocol_pydantic: FunctionProtocolDefinitionModel,  # MODIFIED: DbSession -> AsyncSession
    source_repository_id: Optional[int] = None,
    commit_hash: Optional[str] = None,
    file_system_source_id: Optional[int] = None,
) -> FunctionProtocolDefinitionOrm:
    query_filter_dict: dict[str, Union[str, int]] = {
        "name": protocol_pydantic.name,
        "version": protocol_pydantic.version,
    }
    if source_repository_id and commit_hash:
        query_filter_dict["source_repository_id"] = source_repository_id
        query_filter_dict["commit_hash"] = commit_hash
    elif file_system_source_id:
        query_filter_dict["file_system_source_id"] = file_system_source_id
        query_filter_dict["source_file_path"] = protocol_pydantic.source_file_path  # type: ignore
    else:
        raise ValueError("Protocol definition must be linked to a source.")

    stmt = (
        select(FunctionProtocolDefinitionOrm)
        .options(
            selectinload(FunctionProtocolDefinitionOrm.parameters),
            selectinload(FunctionProtocolDefinitionOrm.assets),
        )
        .filter_by(**query_filter_dict)
    )
    result = await db.execute(stmt)
    def_orm = result.scalar_one_or_none()

    if not def_orm:
        def_orm = FunctionProtocolDefinitionOrm(**query_filter_dict)  # type: ignore
        db.add(def_orm)

    def_orm.description = protocol_pydantic.description
    def_orm.source_file_path = protocol_pydantic.source_file_path
    def_orm.module_name = protocol_pydantic.module_name
    def_orm.function_name = protocol_pydantic.function_name
    def_orm.is_top_level = protocol_pydantic.is_top_level
    def_orm.solo_execution = protocol_pydantic.solo_execution
    def_orm.preconfigure_deck = protocol_pydantic.preconfigure_deck
    def_orm.deck_param_name = protocol_pydantic.deck_param_name
    def_orm.state_param_name = protocol_pydantic.state_param_name
    def_orm.category = protocol_pydantic.category
    def_orm.tags = (
        {"values": protocol_pydantic.tags} if protocol_pydantic.tags else None
    )
    def_orm.deprecated = (
        False  # Assuming new/updated definitions are not deprecated by default
    )
    def_orm.source_repository_id = source_repository_id
    def_orm.commit_hash = commit_hash
    def_orm.file_system_source_id = file_system_source_id

    # Parameters
    current_params = {p.name: p for p in def_orm.parameters}
    new_params_list = []
    for param_model in protocol_pydantic.parameters:
        param_orm = current_params.pop(param_model.name, None)
        if not param_orm:
            param_orm = ParameterDefinitionOrm(protocol_definition_id=def_orm.id)
        param_orm.name = param_model.name
        param_orm.type_hint_str = param_model.type_hint_str
        param_orm.actual_type_str = param_model.actual_type_str
        param_orm.is_deck_param = param_model.is_deck_param
        param_orm.optional = param_model.optional
        param_orm.default_value_repr = param_model.default_value_repr
        param_orm.description = param_model.description
        param_orm.constraints_json = (
            param_model.constraints.model_dump() if param_model.constraints else None
        )
        new_params_list.append(param_orm)
    def_orm.parameters = new_params_list  # type: ignore

    # Assets
    current_assets = {p.name: p for p in def_orm.assets}
    new_assets_list = []
    for asset_model in protocol_pydantic.assets:
        asset_orm = current_assets.pop(asset_model.name, None)
        if not asset_orm:
            asset_orm = AssetDefinitionOrm(protocol_definition_id=def_orm.id)
        asset_orm.name = asset_model.name
        asset_orm.type_hint_str = asset_model.type_hint_str
        asset_orm.actual_type_str = asset_model.actual_type_str
        asset_orm.optional = asset_model.optional
        asset_orm.default_value_repr = asset_model.default_value_repr
        asset_orm.description = asset_model.description
        asset_orm.constraints_json = (
            asset_model.constraints.model_dump() if asset_model.constraints else None
        )
        new_assets_list.append(asset_orm)
    def_orm.assets = new_assets_list  # type: ignore

    try:
        await db.commit()
        await db.refresh(def_orm)
    except Exception as e:
        await db.rollback()
        print(f"Error upserting protocol def '{protocol_pydantic.name}': {e}")
        raise
    return def_orm


async def create_protocol_run(  # MODIFIED: async def
    db: AsyncSession,
    run_guid: str,
    top_level_protocol_definition_id: int,  # MODIFIED: DbSession -> AsyncSession
    status: ProtocolRunStatusEnum = ProtocolRunStatusEnum.PENDING,
    input_parameters_json: Optional[str] = None,
    initial_state_json: Optional[str] = None,
) -> ProtocolRunOrm:
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    db_protocol_run = ProtocolRunOrm(
        run_guid=run_guid,
        top_level_protocol_definition_id=top_level_protocol_definition_id,
        status=status,
        input_parameters_json=json.loads(input_parameters_json)
        if input_parameters_json
        else {},  # MODIFIED: ensure dict
        initial_state_json=json.loads(initial_state_json)
        if initial_state_json
        else {},  # MODIFIED: ensure dict
        start_time=utc_now if status != ProtocolRunStatusEnum.PENDING else None,
    )
    db.add(db_protocol_run)
    try:
        await db.commit()
        await db.refresh(db_protocol_run)
    except Exception as e:
        await db.rollback()
        raise e
    return db_protocol_run


async def update_protocol_run_status(  # MODIFIED: async def
    db: AsyncSession,
    protocol_run_id: int,
    new_status: ProtocolRunStatusEnum,  # MODIFIED: DbSession -> AsyncSession
    output_data_json: Optional[str] = None,
    final_state_json: Optional[str] = None,
    error_info: Optional[Dict[str, str]] = None,
) -> Optional[ProtocolRunOrm]:
    stmt = select(ProtocolRunOrm).filter(ProtocolRunOrm.id == protocol_run_id)
    result = await db.execute(stmt)
    db_protocol_run = result.scalar_one_or_none()

    if db_protocol_run:
        db_protocol_run.status = new_status
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        if (
            new_status == ProtocolRunStatusEnum.RUNNING
            and not db_protocol_run.start_time
        ):
            db_protocol_run.start_time = utc_now
        if new_status in [
            ProtocolRunStatusEnum.COMPLETED,
            ProtocolRunStatusEnum.FAILED,
            ProtocolRunStatusEnum.CANCELLED,
        ]:
            db_protocol_run.end_time = utc_now
            if db_protocol_run.start_time and db_protocol_run.end_time:
                duration = db_protocol_run.end_time - db_protocol_run.start_time  # type: ignore
                db_protocol_run.duration_ms = int(duration.total_seconds() * 1000)
            if output_data_json is not None:
                db_protocol_run.output_data_json = json.loads(output_data_json)
            if final_state_json is not None:
                db_protocol_run.final_state_json = json.loads(final_state_json)
            if new_status == ProtocolRunStatusEnum.FAILED and error_info:
                db_protocol_run.output_data_json = error_info  # type: ignore
        try:
            await db.commit()
            await db.refresh(db_protocol_run)
        except Exception as e:
            await db.rollback()
            raise e
        return db_protocol_run
    return None


# --- Function Call Log Management ---
async def log_function_call_start(  # MODIFIED: async def
    db: AsyncSession,
    protocol_run_orm_id: int,
    function_definition_id: int,  # MODIFIED: DbSession -> AsyncSession
    sequence_in_run: int,
    input_args_json: str,
    parent_function_call_log_id: Optional[int] = None,
) -> FunctionCallLogOrm:
    call_log = FunctionCallLogOrm(
        protocol_run_id=protocol_run_orm_id,
        function_protocol_definition_id=function_definition_id,
        sequence_in_run=sequence_in_run,
        parent_function_call_log_id=parent_function_call_log_id,
        start_time=datetime.datetime.now(datetime.timezone.utc),
        input_args_json=json.loads(input_args_json)
        if input_args_json
        else {},  # MODIFIED: ensure dict
        status=FunctionCallStatusEnum.SUCCESS,
    )
    db.add(call_log)
    try:
        await db.commit()
        await db.refresh(call_log)
    except Exception as e:
        await db.rollback()
        raise e
    return call_log


async def log_function_call_end(  # MODIFIED: async def
    db: AsyncSession,
    function_call_log_id: int,
    status: FunctionCallStatusEnum,  # MODIFIED: DbSession -> AsyncSession
    return_value_json: Optional[str] = None,
    error_message: Optional[str] = None,
    error_traceback: Optional[str] = None,
    duration_ms: Optional[float] = None,
) -> Optional[FunctionCallLogOrm]:
    stmt = select(FunctionCallLogOrm).filter(
        FunctionCallLogOrm.id == function_call_log_id
    )
    result = await db.execute(stmt)
    call_log = result.scalar_one_or_none()

    if call_log:
        call_log.end_time = datetime.datetime.now(datetime.timezone.utc)
        if duration_ms is not None:
            call_log.duration_ms = int(duration_ms)
        elif call_log.start_time and call_log.end_time is not None:
            call_log.duration_ms = int(
                (call_log.end_time - call_log.start_time).total_seconds() * 1000  # type: ignore
            )  # type: ignore
        call_log.status = status
        if return_value_json is not None:
            call_log.return_value_json = json.loads(return_value_json)
        if error_message is not None:
            call_log.error_message_text = error_message
        if error_traceback is not None:
            call_log.error_traceback_text = error_traceback
        try:
            await db.commit()
            await db.refresh(call_log)
        except Exception as e:
            await db.rollback()
            raise e
        return call_log
    return None


# --- Query Functions ---
async def get_protocol_definition_by_id(  # MODIFIED: async def
    db: AsyncSession,  # MODIFIED: DbSession -> AsyncSession
    definition_id: int,
) -> Optional[FunctionProtocolDefinitionOrm]:
    stmt = (
        select(FunctionProtocolDefinitionOrm)
        .options(
            selectinload(FunctionProtocolDefinitionOrm.parameters),
            selectinload(FunctionProtocolDefinitionOrm.assets),
            joinedload(FunctionProtocolDefinitionOrm.source_repository),
            joinedload(FunctionProtocolDefinitionOrm.file_system_source),
        )
        .filter(FunctionProtocolDefinitionOrm.id == definition_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_protocol_definition_details(  # MODIFIED: async def
    db: AsyncSession,  # MODIFIED: DbSession -> AsyncSession
    name: str,
    version: Optional[str] = None,
    source_name: Optional[str] = None,
    commit_hash: Optional[str] = None,
) -> Optional[FunctionProtocolDefinitionOrm]:
    stmt = (
        select(FunctionProtocolDefinitionOrm)
        .options(
            selectinload(FunctionProtocolDefinitionOrm.parameters),
            selectinload(FunctionProtocolDefinitionOrm.assets),
            joinedload(FunctionProtocolDefinitionOrm.source_repository),
            joinedload(FunctionProtocolDefinitionOrm.file_system_source),
        )
        .filter(
            FunctionProtocolDefinitionOrm.name == name,
            ~FunctionProtocolDefinitionOrm.deprecated,
        )
    )  # type: ignore

    if version:
        stmt = stmt.filter(FunctionProtocolDefinitionOrm.version == version)

    if commit_hash:
        stmt = stmt.filter(FunctionProtocolDefinitionOrm.commit_hash == commit_hash)
        if source_name:
            stmt = stmt.join(
                ProtocolSourceRepositoryOrm,
                FunctionProtocolDefinitionOrm.source_repository_id
                == ProtocolSourceRepositoryOrm.id,
            ).filter(ProtocolSourceRepositoryOrm.name == source_name)
    elif source_name:
        git_source_alias = aliased(ProtocolSourceRepositoryOrm)
        fs_source_alias = aliased(FileSystemProtocolSourceOrm)
        stmt = (
            stmt.outerjoin(
                git_source_alias,
                FunctionProtocolDefinitionOrm.source_repository_id
                == git_source_alias.id,
            )
            .outerjoin(
                fs_source_alias,
                FunctionProtocolDefinitionOrm.file_system_source_id
                == fs_source_alias.id,
            )
            .filter(
                or_(
                    git_source_alias.name == source_name,
                    fs_source_alias.name == source_name,
                )
            )
        )

    if not version:
        stmt = stmt.order_by(desc(FunctionProtocolDefinitionOrm.created_at))

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_protocol_definitions(  # MODIFIED: async def
    db: AsyncSession,  # MODIFIED: DbSession -> AsyncSession
    limit: int = 100,
    offset: int = 0,
    source_name: Optional[str] = None,
    is_top_level: Optional[bool] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    include_deprecated: bool = False,
) -> List[FunctionProtocolDefinitionOrm]:
    stmt = select(FunctionProtocolDefinitionOrm).options(
        selectinload(FunctionProtocolDefinitionOrm.parameters),
        selectinload(FunctionProtocolDefinitionOrm.assets),
        joinedload(FunctionProtocolDefinitionOrm.source_repository),
        joinedload(FunctionProtocolDefinitionOrm.file_system_source),
    )

    if not include_deprecated:
        stmt = stmt.filter(~FunctionProtocolDefinitionOrm.deprecated)

    if source_name:
        git_source_alias = aliased(ProtocolSourceRepositoryOrm)
        fs_source_alias = aliased(FileSystemProtocolSourceOrm)
        stmt = (
            stmt.outerjoin(
                git_source_alias,
                FunctionProtocolDefinitionOrm.source_repository_id
                == git_source_alias.id,
            )
            .outerjoin(
                fs_source_alias,
                FunctionProtocolDefinitionOrm.file_system_source_id
                == fs_source_alias.id,
            )
            .filter(
                or_(
                    git_source_alias.name == source_name,
                    fs_source_alias.name == source_name,
                )
            )
        )  # type: ignore
    if is_top_level is not None:
        stmt = stmt.filter(FunctionProtocolDefinitionOrm.is_top_level == is_top_level)
    if category:
        stmt = stmt.filter(FunctionProtocolDefinitionOrm.category == category)
    if tags:
        for tag in tags:
            stmt = stmt.filter(FunctionProtocolDefinitionOrm.tags.op("?")(tag))

    stmt = (
        stmt.order_by(
            desc(FunctionProtocolDefinitionOrm.name),
            desc(FunctionProtocolDefinitionOrm.version),
        )
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_protocol_run_by_guid(
    db: AsyncSession, run_guid: str
) -> Optional[ProtocolRunOrm]:
    stmt = (
        select(ProtocolRunOrm)
        .options(
            selectinload(ProtocolRunOrm.function_calls)
            .selectinload(FunctionCallLogOrm.executed_function_definition)
            .selectinload(FunctionProtocolDefinitionOrm.source_repository),
            selectinload(ProtocolRunOrm.function_calls)
            .selectinload(FunctionCallLogOrm.executed_function_definition)
            .selectinload(FunctionProtocolDefinitionOrm.file_system_source),
            joinedload(ProtocolRunOrm.top_level_protocol_definition),
        )
        .filter(ProtocolRunOrm.run_guid == run_guid)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_protocol_runs(  # MODIFIED
    db: AsyncSession,  # MODIFIED
    limit: int = 100,
    offset: int = 0,
    protocol_definition_id: Optional[int] = None,
    protocol_name: Optional[str] = None,
    status: Optional[ProtocolRunStatusEnum] = None,
) -> List[ProtocolRunOrm]:
    stmt = select(ProtocolRunOrm).options(
        joinedload(ProtocolRunOrm.top_level_protocol_definition)
    )

    if protocol_definition_id is not None:
        stmt = stmt.filter(
            ProtocolRunOrm.top_level_protocol_definition_id == protocol_definition_id
        )
    if protocol_name is not None:
        stmt = stmt.join(
            FunctionProtocolDefinitionOrm,
            ProtocolRunOrm.top_level_protocol_definition_id
            == FunctionProtocolDefinitionOrm.id,
        ).filter(FunctionProtocolDefinitionOrm.name == protocol_name)
    if status is not None:
        stmt = stmt.filter(ProtocolRunOrm.status == status)

    stmt = (
        stmt.order_by(desc(ProtocolRunOrm.start_time), desc(ProtocolRunOrm.id))
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_function_call_logs_for_run(  # MODIFIED
    db: AsyncSession,  # MODIFIED
    protocol_run_id: int,
) -> List[FunctionCallLogOrm]:
    stmt = (
        select(FunctionCallLogOrm)
        .options(selectinload(FunctionCallLogOrm.executed_function_definition))
        .filter(FunctionCallLogOrm.protocol_run_id == protocol_run_id)
        .order_by(FunctionCallLogOrm.sequence_in_run)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_active_protocol_sources(  # MODIFIED
    db: AsyncSession,  # MODIFIED
    source_type: Optional[str] = None,
) -> List[Union[ProtocolSourceRepositoryOrm, FileSystemProtocolSourceOrm]]:
    results: List[Union[ProtocolSourceRepositoryOrm, FileSystemProtocolSourceOrm]] = []
    if source_type is None or source_type == "git":
        stmt_git = select(ProtocolSourceRepositoryOrm).filter(
            ProtocolSourceRepositoryOrm.status == ProtocolSourceStatusEnum.ACTIVE
        )
        result_git = await db.execute(stmt_git)
        results.extend(result_git.scalars().all())  # type: ignore
    if source_type is None or source_type == "filesystem":
        stmt_fs = select(FileSystemProtocolSourceOrm).filter(
            FileSystemProtocolSourceOrm.status == ProtocolSourceStatusEnum.ACTIVE
        )
        result_fs = await db.execute(stmt_fs)
        results.extend(result_fs.scalars().all())  # type: ignore
    return results
