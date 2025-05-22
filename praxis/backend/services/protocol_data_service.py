# pylint: disable=too-many-arguments, broad-except, fixme, unused-argument, too-many-lines
"""
praxis/db_services/protocol_data_service.py

Service layer for interacting with protocol-related data in the database.
This includes definitions for protocol sources, static protocol definitions,
protocol run instances, and function call logs.

Version 3: Adds comprehensive query functions.
"""
import datetime
import json
from typing import Dict, Any, Optional, List, Union

from sqlalchemy.orm import Session as DbSession, joinedload, selectinload, aliased
from sqlalchemy import desc, or_

from praxis.backend.database_models import (
    ProtocolSourceRepositoryOrm,
    FileSystemProtocolSourceOrm,
    FunctionProtocolDefinitionOrm,
    ParameterDefinitionOrm,
    AssetDefinitionOrm,
    ProtocolRunOrm,
    FunctionCallLogOrm,
    ProtocolSourceStatusEnum,
    ProtocolRunStatusEnum,
    FunctionCallStatusEnum
)
from praxis.backend.protocol_core.definitions import (
    FunctionProtocolDefinition as FunctionProtocolDefinitionPydantic,
    # ParameterDefinition as ParameterDefinitionPydantic,
    # AssetDefinition as AssetDefinitionPydantic
)


# --- Protocol Source Management ---
# (add_or_update_protocol_source_repository and add_or_update_file_system_protocol_source remain the same as v2)
def add_or_update_protocol_source_repository(
    db: DbSession, name: str, git_url: str, default_ref: str = "main",
    local_checkout_path: Optional[str] = None,
    status: ProtocolSourceStatusEnum = ProtocolSourceStatusEnum.ACTIVE,
    auto_sync_enabled: bool = True, source_id: Optional[int] = None
) -> ProtocolSourceRepositoryOrm:
    if source_id:
        source_repo = db.query(ProtocolSourceRepositoryOrm).filter(ProtocolSourceRepositoryOrm.id == source_id).first()
        if not source_repo: raise ValueError(f"Repo source id {source_id} not found.")
    else:
        source_repo = db.query(ProtocolSourceRepositoryOrm).filter(ProtocolSourceRepositoryOrm.name == name).first()
        if not source_repo: source_repo = ProtocolSourceRepositoryOrm(name=name); db.add(source_repo)
    source_repo.git_url = git_url; source_repo.default_ref = default_ref
    source_repo.local_checkout_path = local_checkout_path; source_repo.status = status
    source_repo.auto_sync_enabled = auto_sync_enabled
    try: db.commit(); db.refresh(source_repo)
    except Exception as e: db.rollback(); print(f"Error upserting repo source '{name}': {e}"); raise
    return source_repo

def add_or_update_file_system_protocol_source(
    db: DbSession, name: str, base_path: str, is_recursive: bool = True,
    status: ProtocolSourceStatusEnum = ProtocolSourceStatusEnum.ACTIVE, source_id: Optional[int] = None
) -> FileSystemProtocolSourceOrm:
    if source_id:
        fs_source = db.query(FileSystemProtocolSourceOrm).filter(FileSystemProtocolSourceOrm.id == source_id).first()
        if not fs_source: raise ValueError(f"FS source id {source_id} not found.")
    else:
        fs_source = db.query(FileSystemProtocolSourceOrm).filter(FileSystemProtocolSourceOrm.name == name).first()
        if not fs_source: fs_source = FileSystemProtocolSourceOrm(name=name); db.add(fs_source)
    fs_source.base_path = base_path; fs_source.is_recursive = is_recursive; fs_source.status = status
    try: db.commit(); db.refresh(fs_source)
    except Exception as e: db.rollback(); print(f"Error upserting FS source '{name}': {e}"); raise
    return fs_source

# --- Static Protocol Definition Management ---
def upsert_function_protocol_definition(
    db: DbSession, protocol_pydantic: FunctionProtocolDefinitionPydantic,
    source_repository_id: Optional[int] = None, commit_hash: Optional[str] = None,
    file_system_source_id: Optional[int] = None
) -> FunctionProtocolDefinitionOrm:
    # (Same as v2 of this file - robust upsert logic)
    query_filter = {"name": protocol_pydantic.name, "version": protocol_pydantic.version}
    if source_repository_id and commit_hash:
        query_filter["source_repository_id"] = source_repository_id
        query_filter["commit_hash"] = commit_hash
    elif file_system_source_id:
        query_filter["file_system_source_id"] = file_system_source_id
        query_filter["source_file_path"] = protocol_pydantic.source_file_path
    else: raise ValueError("Protocol definition must be linked to a source.")

    def_orm = db.query(FunctionProtocolDefinitionOrm)\
                .options(joinedload(FunctionProtocolDefinitionOrm.parameters),
                         joinedload(FunctionProtocolDefinitionOrm.assets))\
                .filter_by(**query_filter).first()
    if not def_orm: def_orm = FunctionProtocolDefinitionOrm(**query_filter); db.add(def_orm)

    # Populate/Update fields (condensed for brevity, full logic from v2)
    def_orm.description = protocol_pydantic.description; def_orm.source_file_path = protocol_pydantic.source_file_path
    def_orm.module_name = protocol_pydantic.module_name; def_orm.function_name = protocol_pydantic.function_name
    def_orm.is_top_level = protocol_pydantic.is_top_level; def_orm.solo_execution = protocol_pydantic.solo_execution
    def_orm.preconfigure_deck = protocol_pydantic.preconfigure_deck; def_orm.deck_param_name = protocol_pydantic.deck_param_name
    def_orm.state_param_name = protocol_pydantic.state_param_name; def_orm.category = protocol_pydantic.category
    def_orm.tags = protocol_pydantic.tags; def_orm.deprecated = False
    def_orm.source_repository_id = source_repository_id; def_orm.commit_hash = commit_hash
    def_orm.file_system_source_id = file_system_source_id

    # Parameters & Assets (condensed for brevity, full logic from v2)
    existing_params_orm = {p.name: p for p in def_orm.parameters}
    updated_params_orm = []
    for param_pydantic in protocol_pydantic.parameters:
        param_orm = existing_params_orm.get(param_pydantic.name, ParameterDefinitionOrm(protocol_definition_id=def_orm.id))
        # ... (update param_orm fields) ...
        param_orm.name=param_pydantic.name; param_orm.type_hint_str=param_pydantic.type_hint_str; param_orm.actual_type_str=param_pydantic.actual_type_str
        param_orm.is_deck_param=param_pydantic.is_deck_param; param_orm.optional=param_pydantic.optional; param_orm.default_value_repr=param_pydantic.default_value_repr
        param_orm.description=param_pydantic.description; param_orm.constraints_json = param_pydantic.constraints.model_dump() if param_pydantic.constraints else None
        updated_params_orm.append(param_orm)
    def_orm.parameters = updated_params_orm

    existing_assets_orm = {a.name: a for a in def_orm.assets}
    updated_assets_orm = []
    for asset_pydantic in protocol_pydantic.assets:
        asset_orm = existing_assets_orm.get(asset_pydantic.name, AssetDefinitionOrm(protocol_definition_id=def_orm.id))
        # ... (update asset_orm fields) ...
        asset_orm.name=asset_pydantic.name; asset_orm.type_hint_str=asset_pydantic.type_hint_str; asset_orm.actual_type_str=asset_pydantic.actual_type_str
        asset_orm.optional=asset_pydantic.optional; asset_orm.default_value_repr=asset_pydantic.default_value_repr
        asset_orm.description=asset_pydantic.description; asset_orm.constraints_json = asset_pydantic.constraints.model_dump() if asset_pydantic.constraints else None
        updated_assets_orm.append(asset_orm)
    def_orm.assets = updated_assets_orm

    try: db.commit(); db.refresh(def_orm)
    except Exception as e: db.rollback(); print(f"Error upserting protocol def '{protocol_pydantic.name}': {e}"); raise
    return def_orm

# --- Protocol Run Management ---
# (create_protocol_run and update_protocol_run_status remain the same as v2)
def create_protocol_run(
    db: DbSession, run_guid: str, top_level_protocol_definition_id: int,
    status: ProtocolRunStatusEnum = ProtocolRunStatusEnum.PENDING,
    input_parameters_json: Optional[str] = None, initial_state_json: Optional[str] = None,
) -> ProtocolRunOrm:
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    db_protocol_run = ProtocolRunOrm(
        run_guid=run_guid, top_level_protocol_definition_id=top_level_protocol_definition_id,
        status=status, input_parameters_json=input_parameters_json, initial_state_json=initial_state_json,
        start_time=utc_now if status != ProtocolRunStatusEnum.PENDING else None,
    )
    db.add(db_protocol_run);
    try: db.commit(); db.refresh(db_protocol_run)
    except Exception as e: db.rollback(); raise e
    return db_protocol_run

def update_protocol_run_status(
    db: DbSession, protocol_run_id: int, new_status: ProtocolRunStatusEnum,
    output_data_json: Optional[str] = None, final_state_json: Optional[str] = None,
    error_info: Optional[Dict[str, str]] = None
) -> Optional[ProtocolRunOrm]:
    db_protocol_run = db.query(ProtocolRunOrm).filter(ProtocolRunOrm.id == protocol_run_id).first()
    if db_protocol_run:
        db_protocol_run.status = new_status; utc_now = datetime.datetime.now(datetime.timezone.utc)
        if new_status == ProtocolRunStatusEnum.RUNNING and not db_protocol_run.start_time: db_protocol_run.start_time = utc_now
        if new_status in [ProtocolRunStatusEnum.COMPLETED, ProtocolRunStatusEnum.FAILED, ProtocolRunStatusEnum.CANCELLED]:
            db_protocol_run.end_time = utc_now
            if db_protocol_run.start_time: db_protocol_run.duration_ms = int((db_protocol_run.end_time - db_protocol_run.start_time).total_seconds() * 1000)
            if output_data_json is not None: db_protocol_run.output_data_json = output_data_json
            if final_state_json is not None: db_protocol_run.final_state_json = final_state_json
            if new_status == ProtocolRunStatusEnum.FAILED and error_info: db_protocol_run.output_data_json = json.dumps(error_info)
        try: db.commit(); db.refresh(db_protocol_run)
        except Exception as e: db.rollback(); raise e
        return db_protocol_run
    return None

# --- Function Call Log Management ---
# (log_function_call_start and log_function_call_end remain the same as v2)
def log_function_call_start(
    db: DbSession, protocol_run_orm_id: int, function_definition_id: int,
    sequence_in_run: int, input_args_json: str, parent_function_call_log_id: Optional[int] = None
) -> FunctionCallLogOrm:
    call_log = FunctionCallLogOrm(
        protocol_run_id=protocol_run_orm_id, function_protocol_definition_id=function_definition_id,
        sequence_in_run=sequence_in_run, parent_function_call_log_id=parent_function_call_log_id,
        start_time=datetime.datetime.now(datetime.timezone.utc), input_args_json=input_args_json,
        status=FunctionCallStatusEnum.SUCCESS # Default
    )
    db.add(call_log)
    try: db.commit(); db.refresh(call_log)
    except Exception as e: db.rollback(); raise e
    return call_log

def log_function_call_end(
    db: DbSession, function_call_log_id: int, status: FunctionCallStatusEnum,
    return_value_json: Optional[str] = None, error_message: Optional[str] = None,
    error_traceback: Optional[str] = None, duration_ms: Optional[float] = None # Added duration_ms
) -> Optional[FunctionCallLogOrm]:
    call_log = db.query(FunctionCallLogOrm).filter(FunctionCallLogOrm.id == function_call_log_id).first()
    if call_log:
        call_log.end_time = datetime.datetime.now(datetime.timezone.utc)
        if duration_ms is not None: # Prefer passed duration if available
            call_log.duration_ms = int(duration_ms)
        elif call_log.start_time: # Calculate if not passed
            call_log.duration_ms = int((call_log.end_time - call_log.start_time).total_seconds() * 1000)
        call_log.status = status; call_log.return_value_json = return_value_json
        call_log.error_message_text = error_message; call_log.error_traceback_text = error_traceback
        try: db.commit(); db.refresh(call_log)
        except Exception as e: db.rollback(); raise e
        return call_log
    return None

# --- NEW: Query Functions (PDS-7) ---

def get_protocol_definition_by_id(db: DbSession, definition_id: int) -> Optional[FunctionProtocolDefinitionOrm]:
    """Fetches a single protocol definition by its primary key, including parameters and assets."""
    return db.query(FunctionProtocolDefinitionOrm)\
             .options(selectinload(FunctionProtocolDefinitionOrm.parameters),
                      selectinload(FunctionProtocolDefinitionOrm.assets),
                      joinedload(FunctionProtocolDefinitionOrm.source_repository),
                      joinedload(FunctionProtocolDefinitionOrm.file_system_source))\
             .filter(FunctionProtocolDefinitionOrm.id == definition_id)\
             .first()

def get_protocol_definition_details(
    db: DbSession,
    name: str,
    version: Optional[str] = None,
    source_name: Optional[str] = None, # Name of Git repo or FS source
    commit_hash: Optional[str] = None  # Specific commit if Git-sourced
) -> Optional[FunctionProtocolDefinitionOrm]:
    """
    Fetches a specific protocol definition with details, similar to Orchestrator's internal getter.
    If version is None, tries to get the latest non-deprecated version matching other criteria.
    """
    query = db.query(FunctionProtocolDefinitionOrm)\
              .options(selectinload(FunctionProtocolDefinitionOrm.parameters),
                       selectinload(FunctionProtocolDefinitionOrm.assets),
                       joinedload(FunctionProtocolDefinitionOrm.source_repository),
                       joinedload(FunctionProtocolDefinitionOrm.file_system_source))\
              .filter(FunctionProtocolDefinitionOrm.name == name,
                      FunctionProtocolDefinitionOrm.deprecated == False) # type: ignore

    if version:
        query = query.filter(FunctionProtocolDefinitionOrm.version == version)

    if commit_hash: # Most specific for Git-sourced
        query = query.filter(FunctionProtocolDefinitionOrm.commit_hash == commit_hash)
        if source_name:
            query = query.join(ProtocolSourceRepositoryOrm, FunctionProtocolDefinitionOrm.source_repository_id == ProtocolSourceRepositoryOrm.id)\
                         .filter(ProtocolSourceRepositoryOrm.name == source_name)
    elif source_name:
        # If source_name is provided, filter by it. This could be ambiguous if name exists in both Git and FS.
        # For simplicity, this query part might need to be more specific or use subqueries if ambiguity is an issue.
        # This assumes source_name is unique across Git and FS sources, or the user knows which one they mean.
        git_source_alias = aliased(ProtocolSourceRepositoryOrm)
        fs_source_alias = aliased(FileSystemProtocolSourceOrm)
        query = query.outerjoin(git_source_alias, FunctionProtocolDefinitionOrm.source_repository_id == git_source_alias.id)\
                     .outerjoin(fs_source_alias, FunctionProtocolDefinitionOrm.file_system_source_id == fs_source_alias.id)\
                     .filter(or_(git_source_alias.name == source_name, fs_source_alias.name == source_name))

    # If no version, order by creation to get latest (or by semantic version if implemented)
    if not version:
        query = query.order_by(desc(FunctionProtocolDefinitionOrm.created_at)) # Or semantic version sort

    return query.first()


def list_protocol_definitions(
    db: DbSession,
    limit: int = 100,
    offset: int = 0,
    source_name: Optional[str] = None,
    is_top_level: Optional[bool] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None, # Query for protocols containing ALL listed tags
    include_deprecated: bool = False
) -> List[FunctionProtocolDefinitionOrm]:
    """Lists protocol definitions with filtering and pagination."""
    query = db.query(FunctionProtocolDefinitionOrm)\
              .options(selectinload(FunctionProtocolDefinitionOrm.parameters), # Eager load for efficiency if needed
                       selectinload(FunctionProtocolDefinitionOrm.assets),
                       joinedload(FunctionProtocolDefinitionOrm.source_repository),
                       joinedload(FunctionProtocolDefinitionOrm.file_system_source))

    if not include_deprecated:
        query = query.filter(FunctionProtocolDefinitionOrm.deprecated == False) # type: ignore

    if source_name:
        git_source_alias = aliased(ProtocolSourceRepositoryOrm)
        fs_source_alias = aliased(FileSystemProtocolSourceOrm)
        query = query.outerjoin(git_source_alias, FunctionProtocolDefinitionOrm.source_repository_id == git_source_alias.id)\
                     .outerjoin(fs_source_alias, FunctionProtocolDefinitionOrm.file_system_source_id == fs_source_alias.id)\
                     .filter(or_(git_source_alias.name == source_name, fs_source_alias.name == source_name))
    if is_top_level is not None:
        query = query.filter(FunctionProtocolDefinitionOrm.is_top_level == is_top_level)
    if category:
        query = query.filter(FunctionProtocolDefinitionOrm.category == category)
    if tags:
        for tag in tags:
            # This searches for JSON array containing the tag. Adjust for your DB's JSON query syntax.
            # For PostgreSQL: query = query.filter(FunctionProtocolDefinitionOrm.tags.contains([tag]))
            # For generic JSON: query = query.filter(FunctionProtocolDefinitionOrm.tags.astext.like(f'%"{tag}"%')) # Less efficient
            query = query.filter(FunctionProtocolDefinitionOrm.tags.op('?')(tag)) # PostgreSQL JSONB contains operator


    return query.order_by(desc(FunctionProtocolDefinitionOrm.name), desc(FunctionProtocolDefinitionOrm.version))\
                .limit(limit).offset(offset).all()


def get_protocol_run_by_guid(db: DbSession, run_guid: str) -> Optional[ProtocolRunOrm]:
    """Fetches a protocol run by its user-facing GUID, including its call logs."""
    return db.query(ProtocolRunOrm)\
             .options(selectinload(ProtocolRunOrm.function_calls)
                        .selectinload(FunctionCallLogOrm.executed_function_definition) # Load def for each call
                        .selectinload(FunctionProtocolDefinitionOrm.source_repository), # And its source
                      selectinload(ProtocolRunOrm.function_calls)
                        .selectinload(FunctionCallLogOrm.executed_function_definition)
                        .selectinload(FunctionProtocolDefinitionOrm.file_system_source),
                      joinedload(ProtocolRunOrm.top_level_protocol_definition))\
             .filter(ProtocolRunOrm.run_guid == run_guid)\
             .first()

def list_protocol_runs(
    db: DbSession,
    limit: int = 100,
    offset: int = 0,
    protocol_definition_id: Optional[int] = None,
    protocol_name: Optional[str] = None, # Added for convenience
    status: Optional[ProtocolRunStatusEnum] = None,
    # user_id: Optional[int] = None, # TODO: PDS-5
) -> List[ProtocolRunOrm]:
    """Lists protocol runs with filtering and pagination."""
    query = db.query(ProtocolRunOrm)\
              .options(joinedload(ProtocolRunOrm.top_level_protocol_definition)) # Load basic def info

    if protocol_definition_id is not None:
        query = query.filter(ProtocolRunOrm.top_level_protocol_definition_id == protocol_definition_id)
    if protocol_name is not None:
        query = query.join(FunctionProtocolDefinitionOrm, ProtocolRunOrm.top_level_protocol_definition_id == FunctionProtocolDefinitionOrm.id)\
                     .filter(FunctionProtocolDefinitionOrm.name == protocol_name)
    if status is not None:
        query = query.filter(ProtocolRunOrm.status == status)
    # if user_id is not None: query = query.filter(ProtocolRunOrm.created_by_user_id == user_id)

    return query.order_by(desc(ProtocolRunOrm.start_time), desc(ProtocolRunOrm.id))\
                .limit(limit).offset(offset).all()

def get_function_call_logs_for_run(
    db: DbSession,
    protocol_run_id: int # This is ProtocolRunOrm.id (PK)
) -> List[FunctionCallLogOrm]:
    """Fetches all function call logs for a specific protocol run, ordered by sequence."""
    return db.query(FunctionCallLogOrm)\
             .options(selectinload(FunctionCallLogOrm.executed_function_definition))\
             .filter(FunctionCallLogOrm.protocol_run_id == protocol_run_id)\
             .order_by(FunctionCallLogOrm.sequence_in_run)\
             .all()

def list_active_protocol_sources(
    db: DbSession,
    source_type: Optional[str] = None # "git" or "filesystem"
) -> List[Union[ProtocolSourceRepositoryOrm, FileSystemProtocolSourceOrm]]:
    """Lists active protocol sources."""
    results: List[Union[ProtocolSourceRepositoryOrm, FileSystemProtocolSourceOrm]] = []
    if source_type is None or source_type == "git":
        git_sources = db.query(ProtocolSourceRepositoryOrm)\
                        .filter(ProtocolSourceRepositoryOrm.status == ProtocolSourceStatusEnum.ACTIVE).all()
        results.extend(git_sources)
    if source_type is None or source_type == "filesystem":
        fs_sources = db.query(FileSystemProtocolSourceOrm)\
                       .filter(FileSystemProtocolSourceOrm.status == ProtocolSourceStatusEnum.ACTIVE).all()
        results.extend(fs_sources)
    return results

