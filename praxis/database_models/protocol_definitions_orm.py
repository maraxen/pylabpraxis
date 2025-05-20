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
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, JSON, DateTime, UniqueConstraint, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

# TODO: DB-SETUP-1: Ensure this import path for Base is correct for your project structure.
# Assuming your existing db.py has a Base = declarative_base()
try:
    from praxis.utils.db import Base # Import your project's Base
except ImportError:
    print("WARNING: Could not import Base from praxis.utils.db. Using a local Base for model definition only.")
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()


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
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FunctionCallStatusEnum(enum.Enum):
    SUCCESS = "success"
    ERROR = "error"

# --- Protocol Source Tables ---
class ProtocolSourceRepositoryOrm(Base):
    __tablename__ = "protocol_source_repositories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    git_url = Column(String, nullable=False)
    default_ref = Column(String, nullable=False, default="main")
    local_checkout_path = Column(String, nullable=True)
    last_synced_commit = Column(String, nullable=True)
    status = Column(SAEnum(ProtocolSourceStatusEnum, name="ps_status_enum_repo_v3"), default=ProtocolSourceStatusEnum.ACTIVE, nullable=False)
    auto_sync_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    function_protocol_definitions = relationship("FunctionProtocolDefinitionOrm", back_populates="source_repository")

    def __repr__(self):
        return f"<ProtocolSourceRepositoryOrm(id={self.id}, name='{self.name}', git_url='{self.git_url}')>"

class FileSystemProtocolSourceOrm(Base):
    __tablename__ = "file_system_protocol_sources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    base_path = Column(String, nullable=False)
    is_recursive = Column(Boolean, default=True)
    status = Column(SAEnum(ProtocolSourceStatusEnum, name="ps_status_enum_fs_v3"), default=ProtocolSourceStatusEnum.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    function_protocol_definitions = relationship("FunctionProtocolDefinitionOrm", back_populates="file_system_source")

    def __repr__(self):
        return f"<FileSystemProtocolSourceOrm(id={self.id}, name='{self.name}', base_path='{self.base_path}')>"

# --- Static Protocol Definition Tables ---
class FunctionProtocolDefinitionOrm(Base):
    __tablename__ = "function_protocol_definitions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    version = Column(String, nullable=False, default="0.1.0")
    description = Column(Text, nullable=True)
    source_file_path = Column(String, nullable=False)
    module_name = Column(String, nullable=False, index=True)
    function_name = Column(String, nullable=False)
    source_repository_id = Column(Integer, ForeignKey("protocol_source_repositories.id"), nullable=True)
    commit_hash = Column(String, nullable=True, index=True)
    file_system_source_id = Column(Integer, ForeignKey("file_system_protocol_sources.id"), nullable=True)
    is_top_level = Column(Boolean, default=False, index=True)
    solo_execution = Column(Boolean, default=False)
    preconfigure_deck = Column(Boolean, default=False)
    deck_param_name = Column(String, nullable=True)
    state_param_name = Column(String, nullable=True, comment="Name of the state parameter in the function signature.")
    category = Column(String, nullable=True, index=True)
    tags = Column(JSON, nullable=True)
    deprecated = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

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
    id = Column(Integer, primary_key=True, index=True)
    protocol_definition_id = Column(Integer, ForeignKey("function_protocol_definitions.id"), nullable=False)
    name = Column(String, nullable=False)
    type_hint_str = Column(String, nullable=False)
    actual_type_str = Column(String, nullable=False)
    is_deck_param = Column(Boolean, default=False)
    optional = Column(Boolean, nullable=False)
    default_value_repr = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    constraints_json = Column("constraints", JSON, nullable=True)
    protocol_definition = relationship("FunctionProtocolDefinitionOrm", back_populates="parameters")
    __table_args__ = (UniqueConstraint('protocol_definition_id', 'name', name='uq_param_def_name_per_protocol_v3'),)

    def __repr__(self):
        return f"<ParameterDefinitionOrm(name='{self.name}', protocol_id={self.protocol_definition_id})>"

class AssetDefinitionOrm(Base):
    __tablename__ = "asset_definitions"
    id = Column(Integer, primary_key=True, index=True)
    protocol_definition_id = Column(Integer, ForeignKey("function_protocol_definitions.id"), nullable=False)
    name = Column(String, nullable=False)
    type_hint_str = Column(String, nullable=False)
    actual_type_str = Column(String, nullable=False)
    optional = Column(Boolean, nullable=False)
    default_value_repr = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    constraints_json = Column("constraints", JSON, nullable=True)
    protocol_definition = relationship("FunctionProtocolDefinitionOrm", back_populates="assets")
    __table_args__ = (UniqueConstraint('protocol_definition_id', 'name', name='uq_asset_def_name_per_protocol_v3'),)

    def __repr__(self):
        return f"<AssetDefinitionOrm(name='{self.name}', protocol_id={self.protocol_definition_id})>"

class ProtocolRunOrm(Base):
    __tablename__ = "protocol_runs"
    id = Column(Integer, primary_key=True, index=True)
    run_guid = Column(String, nullable=False, unique=True, index=True)
    top_level_protocol_definition_id = Column(Integer, ForeignKey("function_protocol_definitions.id"), nullable=False)
    status = Column(SAEnum(ProtocolRunStatusEnum, name="protocol_run_status_enum_v3"), default=ProtocolRunStatusEnum.PENDING, nullable=False, index=True)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    input_parameters_json = Column(JSON, nullable=True)
    resolved_assets_json = Column(JSON, nullable=True)
    output_data_json = Column(JSON, nullable=True)
    initial_state_json = Column(JSON, nullable=True)
    final_state_json = Column(JSON, nullable=True)
    data_directory_path = Column(String, nullable=True)
    # created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # TODO: PDS-5
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    top_level_protocol_definition = relationship("FunctionProtocolDefinitionOrm", back_populates="protocol_runs")
    function_calls = relationship("FunctionCallLogOrm", back_populates="protocol_run", cascade="all, delete-orphan", order_by="FunctionCallLogOrm.sequence_in_run")

    def __repr__(self):
        return f"<ProtocolRunOrm(id={self.id}, run_guid='{self.run_guid}', status='{self.status.name if self.status else 'N/A'}')>"


class FunctionCallLogOrm(Base):
    __tablename__ = "function_call_logs"
    id = Column(Integer, primary_key=True, index=True)
    protocol_run_id = Column(Integer, ForeignKey("protocol_runs.id"), nullable=False, index=True)
    sequence_in_run = Column(Integer, nullable=False)
    function_protocol_definition_id = Column(Integer, ForeignKey("function_protocol_definitions.id"), nullable=False)
    parent_function_call_log_id = Column(Integer, ForeignKey("function_call_logs.id"), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Integer, nullable=True)
    input_args_json = Column(JSON, nullable=True)
    return_value_json = Column(JSON, nullable=True)
    status = Column(SAEnum(FunctionCallStatusEnum, name="function_call_status_enum_v3"), nullable=False)
    error_message_text = Column(Text, nullable=True)
    error_traceback_text = Column(Text, nullable=True)
    protocol_run = relationship("ProtocolRunOrm", back_populates="function_calls")
    executed_function_definition = relationship("FunctionProtocolDefinitionOrm", foreign_keys=[function_protocol_definition_id], back_populates="function_call_logs")
    parent_call = relationship("FunctionCallLogOrm", remote_side=[id], backref="child_calls") # type: ignore

    def __repr__(self):
        return f"<FunctionCallLogOrm(id={self.id}, run_id={self.protocol_run_id}, seq={self.sequence_in_run}, status='{self.status.name if self.status else 'N/A'}')>"

