# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""
praxis/database_models/protocol_definitions_orm.py

SQLAlchemy ORM models for storing:
1. Static definitions of function-based protocols, parameters, assets.
2. Protocol sources (Git/Filesystem).
3. Runtime logs for top-level protocol executions (ProtocolRunOrm).
4. Runtime logs for individual function calls within a top-level run (FunctionCallLogOrm).

Version 3: Imports Base from praxis.utils.db.
"""
from datetime import datetime
from typing import Optional # Any can be used for JSON if type is not strictly dict/list
import enum

from sqlalchemy import (
    Integer, String, Text, Boolean, ForeignKey, JSON, DateTime, UniqueConstraint, Enum as SAEnum
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from praxis.backend.utils.db import Base # Import your project's Base


# --- Enum Definitions for Status Fields ---
# (Enum definitions remain the same as in v2 of this file)
class ProtocolSourceStatusEnum(enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    SYNC_ERROR = "sync_error"
    PENDING_DELETION = "pending_deletion"

class ProtocolRunStatusEnum(enum.Enum):
    PENDING = "pending"
    PREPARING = "preparing"
    RUNNING = "running"
    PAUSING = "pausing" # New
    PAUSED = "paused"
    RESUMING = "resuming" # New
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELING = "canceling" # New
    CANCELLED = "cancelled"

class FunctionCallStatusEnum(enum.Enum):
    SUCCESS = "success"
    ERROR = "error"

# --- Protocol Source Tables ---
class ProtocolSourceRepositoryOrm(Base):
    __tablename__ = "protocol_source_repositories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    git_url: Mapped[str] = mapped_column(String, nullable=False)
    default_ref: Mapped[str] = mapped_column(String, nullable=False, default="main")
    local_checkout_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_synced_commit: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[ProtocolSourceStatusEnum] = mapped_column(SAEnum(ProtocolSourceStatusEnum, name="ps_status_enum_repo_v3"), default=ProtocolSourceStatusEnum.ACTIVE, nullable=False)
    auto_sync_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    function_protocol_definitions = relationship("FunctionProtocolDefinitionOrm", back_populates="source_repository")

    def __repr__(self):
        return f"<ProtocolSourceRepositoryOrm(id={self.id}, name='{self.name}', git_url='{self.git_url}')>"

class FileSystemProtocolSourceOrm(Base):
    __tablename__ = "file_system_protocol_sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    base_path: Mapped[str] = mapped_column(String, nullable=False)
    is_recursive: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[ProtocolSourceStatusEnum] = mapped_column(SAEnum(ProtocolSourceStatusEnum, name="ps_status_enum_fs_v3"), default=ProtocolSourceStatusEnum.ACTIVE, nullable=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    function_protocol_definitions = relationship("FunctionProtocolDefinitionOrm", back_populates="file_system_source")

    def __repr__(self):
        return f"<FileSystemProtocolSourceOrm(id={self.id}, name='{self.name}', base_path='{self.base_path}')>"

# --- Static Protocol Definition Tables ---
class FunctionProtocolDefinitionOrm(Base):
    __tablename__ = "function_protocol_definitions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    version: Mapped[str] = mapped_column(String, nullable=False, default="0.1.0")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_file_path: Mapped[str] = mapped_column(String, nullable=False)
    module_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    function_name: Mapped[str] = mapped_column(String, nullable=False)
    source_repository_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("protocol_source_repositories.id"), nullable=True)
    commit_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    file_system_source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("file_system_protocol_sources.id"), nullable=True)
    is_top_level: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    solo_execution: Mapped[bool] = mapped_column(Boolean, default=False)
    preconfigure_deck: Mapped[bool] = mapped_column(Boolean, default=False)
    deck_param_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    state_param_name: Mapped[Optional[str]] = mapped_column(String, nullable=True, comment="Name of the state parameter in the function signature.")
    category: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Using dict as per refined instructions
    deprecated: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    parameters = relationship("ParameterDefinitionOrm", back_populates="protocol_definition", cascade="all, delete-orphan")
    assets = relationship("AssetDefinitionOrm", back_populates="protocol_definition", cascade="all, delete-orphan")
    source_repository = relationship("ProtocolSourceRepositoryOrm", back_populates="function_protocol_definitions")
    file_system_source = relationship("FileSystemProtocolSourceOrm", back_populates="function_protocol_definitions")
    protocol_runs = relationship("ProtocolRunOrm", back_populates="top_level_protocol_definition")
    function_call_logs = relationship("FunctionCallLogOrm", foreign_keys="[FunctionCallLogOrm.function_protocol_definition_id]", back_populates="executed_function_definition")

    __table_args__ = (
        UniqueConstraint('name', 'version', 'source_repository_id', 'commit_hash', name='uq_repo_protocol_def_version_v3'),
        UniqueConstraint('name', 'version', 'file_system_source_id', 'source_file_path', name='uq_fs_protocol_def_version_v3'),
    )
    def __repr__(self):
        return f"<FunctionProtocolDefinitionOrm(id={self.id}, name='{self.name}', version='{self.version}')>"


class ParameterDefinitionOrm(Base):
    __tablename__ = "parameter_definitions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    protocol_definition_id: Mapped[int] = mapped_column(Integer, ForeignKey("function_protocol_definitions.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type_hint_str: Mapped[str] = mapped_column(String, nullable=False)
    actual_type_str: Mapped[str] = mapped_column(String, nullable=False)
    is_deck_param: Mapped[bool] = mapped_column(Boolean, default=False)
    optional: Mapped[bool] = mapped_column(Boolean, nullable=False)
    default_value_repr: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    constraints_json: Mapped[Optional[dict]] = mapped_column("constraints", JSON, nullable=True)
    protocol_definition = relationship("FunctionProtocolDefinitionOrm", back_populates="parameters")
    __table_args__ = (UniqueConstraint('protocol_definition_id', 'name', name='uq_param_def_name_per_protocol_v3'),)

    def __repr__(self):
        return f"<ParameterDefinitionOrm(name='{self.name}', protocol_id={self.protocol_definition_id})>"

class AssetDefinitionOrm(Base):
    __tablename__ = "asset_definitions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    protocol_definition_id: Mapped[int] = mapped_column(Integer, ForeignKey("function_protocol_definitions.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type_hint_str: Mapped[str] = mapped_column(String, nullable=False)
    actual_type_str: Mapped[str] = mapped_column(String, nullable=False)
    optional: Mapped[bool] = mapped_column(Boolean, nullable=False)
    default_value_repr: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    constraints_json: Mapped[Optional[dict]] = mapped_column("constraints", JSON, nullable=True) # Using dict
    protocol_definition = relationship("FunctionProtocolDefinitionOrm", back_populates="assets")
    __table_args__ = (UniqueConstraint('protocol_definition_id', 'name', name='uq_asset_def_name_per_protocol_v3'),)

    def __repr__(self):
        return f"<AssetDefinitionOrm(name='{self.name}', protocol_id={self.protocol_definition_id})>"

class ProtocolRunOrm(Base):
    __tablename__ = "protocol_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    run_guid: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    top_level_protocol_definition_id: Mapped[int] = mapped_column(Integer, ForeignKey("function_protocol_definitions.id"), nullable=False)
    status: Mapped[ProtocolRunStatusEnum] = mapped_column(SAEnum(ProtocolRunStatusEnum, name="protocol_run_status_enum_v3"), default=ProtocolRunStatusEnum.PENDING, nullable=False, index=True)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    input_parameters_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Using dict
    resolved_assets_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Using dict
    output_data_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Using dict
    initial_state_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Using dict
    final_state_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Using dict
    data_directory_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_by_user: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    top_level_protocol_definition = relationship("FunctionProtocolDefinitionOrm", back_populates="protocol_runs")
    function_calls = relationship("FunctionCallLogOrm", back_populates="protocol_run", cascade="all, delete-orphan", order_by="FunctionCallLogOrm.sequence_in_run")

    def __repr__(self):
        return f"<ProtocolRunOrm(id={self.id}, run_guid='{self.run_guid}', status='{self.status.name}')>"


class FunctionCallLogOrm(Base):
    __tablename__ = "function_call_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    protocol_run_id: Mapped[int] = mapped_column(Integer, ForeignKey("protocol_runs.id"), nullable=False, index=True)
    sequence_in_run: Mapped[int] = mapped_column(Integer, nullable=False)
    function_protocol_definition_id: Mapped[int] = mapped_column(Integer, ForeignKey("function_protocol_definitions.id"), nullable=False)
    parent_function_call_log_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("function_call_logs.id"), nullable=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    input_args_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Using dict
    return_value_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True) # Using dict
    status: Mapped[FunctionCallStatusEnum] = mapped_column(SAEnum(FunctionCallStatusEnum, name="function_call_status_enum_v3"), nullable=False)
    error_message_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_traceback_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    protocol_run = relationship("ProtocolRunOrm", back_populates="function_calls")
    executed_function_definition = relationship("FunctionProtocolDefinitionOrm", foreign_keys=[function_protocol_definition_id], back_populates="function_call_logs")
    parent_call = relationship("FunctionCallLogOrm", remote_side=[id], backref="child_calls") # type: ignore

    def __repr__(self):
        return f"<FunctionCallLogOrm(id={self.id}, run_id={self.protocol_run_id}, seq={self.sequence_in_run}, status='{self.status.name}')>"
