"""SQLAlchemy ORM models for managing protocol definitions and execution logs in Praxis.

This file defines the database schema for storing:
- **Protocol Source Information**: Details about where protocol definitions originate
(Git repositories or file systems).
- **Function Protocol Definitions**: Static metadata about callable functions intended
as protocols, including their parameters and required assets.
- **Protocol Run Logs**: Records of top-level protocol executions, tracking status,
inputs, outputs, and associated metadata.
- **Function Call Logs**: Detailed logs for individual function calls within a protocol
run, including their status, arguments, and return values.
"""

import enum
from datetime import datetime
from typing import Optional

import uuid_utils as uuid
from sqlalchemy import (
  JSON,
  UUID,
  Boolean,
  DateTime,
  ForeignKey,
  Integer,
  String,
  Text,
  UniqueConstraint,
)
from sqlalchemy import (
  Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from praxis.backend.utils.db import Base


class ProtocolSourceStatusEnum(enum.Enum):
  """Enumeration for the status of a protocol source (repository or file system)."""

  ACTIVE = "active"
  ARCHIVED = "archived"
  SYNC_ERROR = "sync_error"
  PENDING_DELETION = "pending_deletion"


class ProtocolRunStatusEnum(enum.Enum):
  """Enumeration for the operational status of a protocol run."""

  PENDING = "pending"
  PREPARING = "preparing"
  RUNNING = "running"
  PAUSING = "pausing"
  PAUSED = "paused"
  RESUMING = "resuming"
  COMPLETED = "completed"
  FAILED = "failed"
  CANCELING = "canceling"
  CANCELLED = "cancelled"
  INTERVENING = "intervening"
  REQUIRES_INTERVENTION = "requires_intervention"


class FunctionCallStatusEnum(enum.Enum):
  """Enumeration for the outcome status of an individual function call."""

  SUCCESS = "success"
  ERROR = "error"


class ProtocolSourceRepositoryOrm(Base):
  """SQLAlchemy ORM model for storing details about a Git repository protocol source.

  This model tracks Git repositories where function-based protocols are defined,
  including their URL, default branch, local checkout path, and synchronization status.
  """

  __tablename__ = "protocol_source_repositories"
  id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
  git_url: Mapped[str] = mapped_column(String, nullable=False)
  default_ref: Mapped[str] = mapped_column(String, nullable=False, default="main")
  local_checkout_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  last_synced_commit: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  status: Mapped[ProtocolSourceStatusEnum] = mapped_column(
    SAEnum(ProtocolSourceStatusEnum, name="ps_status_enum_repo_v3"),
    default=ProtocolSourceStatusEnum.ACTIVE,
    nullable=False,
  )
  auto_sync_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
  created_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )
  updated_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
  )
  function_protocol_definitions = relationship(
    "FunctionProtocolDefinitionOrm", back_populates="source_repository"
  )

  def __repr__(self):
    """Return a string representation of the ProtocolSourceRepositoryOrm instance."""
    return f"<ProtocolSourceRepositoryOrm(id={self.id}, name='{self.name}', \
      git_url='{self.git_url}')>"


class FileSystemProtocolSourceOrm(Base):
  """SQLAlchemy ORM model for storing details about a file system protocol source.

  This model tracks local file system paths where function-based protocols are defined,
  including their base path and whether they should be recursively scanned.
  """

  __tablename__ = "file_system_protocol_sources"
  id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
  base_path: Mapped[str] = mapped_column(String, nullable=False)
  is_recursive: Mapped[bool] = mapped_column(Boolean, default=True)
  status: Mapped[ProtocolSourceStatusEnum] = mapped_column(
    SAEnum(ProtocolSourceStatusEnum, name="ps_status_enum_fs_v3"),
    default=ProtocolSourceStatusEnum.ACTIVE,
    nullable=False,
  )
  created_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )
  updated_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
  )
  function_protocol_definitions = relationship(
    "FunctionProtocolDefinitionOrm", back_populates="file_system_source"
  )

  def __repr__(self):
    """Return a string representation of the FileSystemProtocolSourceOrm instance."""
    return f"<FileSystemProtocolSourceOrm(id={self.id}, name='{self.name}', base_path=\
      '{self.base_path}')>"


class FunctionProtocolDefinitionOrm(Base):
  """SQLAlchemy ORM model for storing static definitions of function-based protocols.

  This model represents a discoverable protocol, including its name, version,
  source location, and metadata defining its behavior and requirements.
  """

  __tablename__ = "function_protocol_definitions"
  id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  name: Mapped[str] = mapped_column(String, nullable=False, index=True)
  version: Mapped[str] = mapped_column(String, nullable=False, default="0.1.0")
  description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
  source_file_path: Mapped[str] = mapped_column(String, nullable=False)
  module_name: Mapped[str] = mapped_column(String, nullable=False, index=True)
  function_name: Mapped[str] = mapped_column(String, nullable=False)
  source_repository_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    UUID, ForeignKey("protocol_source_repositories.id"), nullable=True
  )
  commit_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
  file_system_source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
    UUID, ForeignKey("file_system_protocol_sources.id"), nullable=True
  )
  is_top_level: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
  solo_execution: Mapped[bool] = mapped_column(Boolean, default=False)
  preconfigure_deck: Mapped[bool] = mapped_column(Boolean, default=False)
  deck_param_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  state_param_name: Mapped[Optional[str]] = mapped_column(
    String,
    nullable=True,
    comment="Name of the state parameter in the function signature.",
  )
  category: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
  tags: Mapped[Optional[dict]] = mapped_column(
    JSON, nullable=True
  )  # Using dict as per refined instructions
  deprecated: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
  created_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )
  updated_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
  )

  parameters = relationship(
    "ParameterDefinitionOrm",
    back_populates="protocol_definition",
    cascade="all, delete-orphan",
  )
  assets = relationship(
    "AssetDefinitionOrm",
    back_populates="protocol_definition",
    cascade="all, delete-orphan",
  )
  source_repository = relationship(
    "ProtocolSourceRepositoryOrm", back_populates="function_protocol_definitions"
  )
  file_system_source = relationship(
    "FileSystemProtocolSourceOrm", back_populates="function_protocol_definitions"
  )
  protocol_runs = relationship(
    "ProtocolRunOrm", back_populates="top_level_protocol_definition"
  )
  function_call_logs = relationship(
    "FunctionCallLogOrm",
    foreign_keys="[FunctionCallLogOrm.function_protocol_definition_id]",
    back_populates="executed_function_definition",
  )

  __table_args__ = (
    UniqueConstraint(
      "name",
      "version",
      "source_repository_id",
      "commit_hash",
      name="uq_repo_protocol_def_version_v3",
    ),
    UniqueConstraint(
      "name",
      "version",
      "file_system_source_id",
      "source_file_path",
      name="uq_fs_protocol_def_version_v3",
    ),
  )

  def __repr__(self):
    """Return a string representation of the FunctionProtocolDefinitionOrm instance."""
    return f"<FunctionProtocolDefinitionOrm(id={self.id}, name='{self.name}', \
      version='{self.version}')>"


class ParameterDefinitionOrm(Base):
  """SQLAlchemy ORM model for defining parameters of a function protocol.

  This model stores metadata about each parameter required by a protocol function,
  including its name, type hints, default values, and any constraints.
  """

  __tablename__ = "parameter_definitions"
  id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  protocol_definition_id: Mapped[uuid.UUID] = mapped_column(
    UUID, ForeignKey("function_protocol_definitions.id"), nullable=False
  )
  name: Mapped[str] = mapped_column(String, nullable=False)
  type_hint_str: Mapped[str] = mapped_column(String, nullable=False)
  actual_type_str: Mapped[str] = mapped_column(String, nullable=False)
  is_deck_param: Mapped[bool] = mapped_column(Boolean, default=False)
  optional: Mapped[bool] = mapped_column(Boolean, nullable=False)
  default_value_repr: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
  constraints_json: Mapped[Optional[dict]] = mapped_column(
    "constraints", JSON, nullable=True
  )
  protocol_definition = relationship(
    "FunctionProtocolDefinitionOrm", back_populates="parameters"
  )
  __table_args__ = (
    UniqueConstraint(
      "protocol_definition_id", "name", name="uq_param_def_name_per_protocol_v3"
    ),
  )

  def __repr__(self):
    """Return a string representation of the ParameterDefinitionOrm instance."""
    return f"<ParameterDefinitionOrm(name='{self.name}', \
      protocol_id={self.protocol_definition_id})>"


class AssetDefinitionOrm(Base):
  """SQLAlchemy ORM model for defining assets required by a function protocol.

  This model describes the assets (e.g., resource, instruments) a protocol function
  expects, including their names, type hints, and descriptions.
  """

  __tablename__ = "asset_definitions"
  id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  protocol_definition_id: Mapped[uuid.UUID] = mapped_column(
    UUID, ForeignKey("function_protocol_definitions.id"), nullable=False
  )
  name: Mapped[str] = mapped_column(String, nullable=False)
  type_hint_str: Mapped[str] = mapped_column(String, nullable=False)
  actual_type_str: Mapped[str] = mapped_column(String, nullable=False)
  optional: Mapped[bool] = mapped_column(Boolean, nullable=False)
  default_value_repr: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
  constraints_json: Mapped[Optional[dict]] = mapped_column(
    "constraints", JSON, nullable=True
  )
  protocol_definition = relationship(
    "FunctionProtocolDefinitionOrm", back_populates="assets"
  )
  __table_args__ = (
    UniqueConstraint(
      "protocol_definition_id", "name", name="uq_asset_def_name_per_protocol_v3"
    ),
  )

  def __repr__(self):
    """Return a string representation of the AssetDefinitionOrm instance."""
    return f"<AssetDefinitionOrm(name='{self.name}', \
      protocol_id={self.protocol_definition_id})>"


class ProtocolRunOrm(Base):
  """SQLAlchemy ORM model for logging a top-level protocol execution.

  This model captures the runtime details of a protocol, such as its GUID,
  status, start/end times, input parameters, resolved assets, and output data.
  """

  __tablename__ = "protocol_runs"
  id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  run_guid: Mapped[uuid.UUID] = mapped_column(
    UUID, nullable=False, unique=True, index=True
  )
  top_level_protocol_definition_id: Mapped[int] = mapped_column(
    Integer, ForeignKey("function_protocol_definitions.id"), nullable=False
  )
  status: Mapped[ProtocolRunStatusEnum] = mapped_column(
    SAEnum(ProtocolRunStatusEnum, name="protocol_run_status_enum_v3"),
    default=ProtocolRunStatusEnum.PENDING,
    nullable=False,
    index=True,
  )
  start_time: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  end_time: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
  input_parameters_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
  resolved_assets_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
  output_data_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
  initial_state_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
  final_state_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
  data_directory_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
  created_by_user: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
  created_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )
  updated_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
  )
  top_level_protocol_definition = relationship(
    "FunctionProtocolDefinitionOrm", back_populates="protocol_runs"
  )
  function_calls = relationship(
    "FunctionCallLogOrm",
    back_populates="protocol_run",
    cascade="all, delete-orphan",
    order_by="FunctionCallLogOrm.sequence_in_run",
  )

  def __repr__(self):
    """Return a string representation of the ProtocolRunOrm instance."""
    return f"<ProtocolRunOrm(id={self.id}, run_guid='{self.run_guid}', \
      status='{self.status.name}')>"


class FunctionCallLogOrm(Base):
  """SQLAlchemy ORM model for logging individual function calls within a protocol run.

  This model captures detailed information for each executed function during a protocol
  run, including its sequence, input arguments, return values, and status.
  """

  __tablename__ = "function_call_logs"
  id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  protocol_run_id: Mapped[uuid.UUID] = mapped_column(
    UUID, ForeignKey("protocol_runs.id"), nullable=False, index=True
  )
  sequence_in_run: Mapped[int] = mapped_column(Integer, nullable=False)
  function_protocol_definition_id: Mapped[uuid.UUID] = mapped_column(
    UUID, ForeignKey("function_protocol_definitions.id"), nullable=False
  )
  parent_function_call_log_id: Mapped[Optional[UUID]] = mapped_column(
    UUID, ForeignKey("function_call_logs.id"), nullable=True
  )
  start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
  end_time: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), nullable=True
  )
  duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
  input_args_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
  return_value_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
  status: Mapped[FunctionCallStatusEnum] = mapped_column(
    SAEnum(FunctionCallStatusEnum, name="function_call_status_enum_v3"),
    nullable=False,
  )
  error_message_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
  error_traceback_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
  protocol_run = relationship("ProtocolRunOrm", back_populates="function_calls")
  executed_function_definition = relationship(
    "FunctionProtocolDefinitionOrm",
    foreign_keys=[function_protocol_definition_id],
    back_populates="function_call_logs",
  )
  parent_call = relationship(
    "FunctionCallLogOrm", remote_side=[id], backref="child_calls"
  )  # type: ignore

  def __repr__(self):
    """Return a string representation of the FunctionCallLogOrm instance."""
    return f"<FunctionCallLogOrm(id={self.id}, run_id={self.protocol_run_id}, \
      seq={self.sequence_in_run}, status='{self.status.name}')>"
