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

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.dialects.postgresql import JSONB

if TYPE_CHECKING:
  from . import (
    DeckDefinitionOrm,
    FunctionCallLogOrm,
    FunctionDataOutputOrm,
    MachineDefinitionOrm,
    ResourceDefinitionOrm,
    ScheduleEntryOrm,
  )


from sqlalchemy import (
  UUID,
  Boolean,
  Computed,
  DateTime,
  ForeignKey,
  Integer,
  String,
  Text,
  UniqueConstraint,
  func,
)
from sqlalchemy import (
  Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from praxis.backend.models.enums import (
  FunctionCallStatusEnum,
  ProtocolRunStatusEnum,
  ProtocolSourceStatusEnum,
)
from praxis.backend.utils.db import Base


class ProtocolSourceRepositoryOrm(Base):
  """SQLAlchemy ORM model for storing details about a Git repository protocol source.

  This model tracks Git repositories where function-based protocols are defined,
  including their URL, default branch, local checkout path, and synchronization status.
  """

  __tablename__ = "protocol_source_repositories"

  name: Mapped[str] = mapped_column(
    String,
    nullable=False,
    unique=True,
    index=True,
    comment="The name of the protocol source",
    init=False,
  )
  git_url: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    default="",
    comment="The URL of the Git repository containing protocol definitions.",
  )
  default_ref: Mapped[str] = mapped_column(
    String,
    nullable=False,
    default="main",
    comment="The default branch or tag in the Git repository where protocols are defined.",
  )
  local_checkout_path: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    default=None,
    comment="Local file system path where the repository is checked out. If None, it is not checked\
      out locally.",
  )
  last_synced_commit: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="The last commit SHA that was synced from the remote repository.",
    default=None,
  )
  status: Mapped[ProtocolSourceStatusEnum] = mapped_column(
    SAEnum(ProtocolSourceStatusEnum, name="ps_status_enum_repo_v3"),
    default=ProtocolSourceStatusEnum.ACTIVE,
    nullable=False,
  )
  auto_sync_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
  function_protocol_definitions: Mapped[list["FunctionProtocolDefinitionOrm"]] = relationship(
    "FunctionProtocolDefinitionOrm",
    back_populates="source_repository",
    default_factory=list,
    comment="List of function protocol definitions defined in this repository.",
  )

  def __repr__(self) -> str:
    """Return a string representation of the ProtocolSourceRepositoryOrm instance."""
    return f"<ProtocolSourceRepositoryOrm(id={self.accession_id}, name='{self.name}', \
      git_url='{self.git_url}')>"


class FileSystemProtocolSourceOrm(Base):
  """SQLAlchemy ORM model for storing details about a file system protocol source.

  This model tracks local file system paths where function-based protocols are defined,
  including their base path and whether they should be recursively scanned.
  """

  __tablename__ = "file_system_protocol_sources"
  name: Mapped[str] = mapped_column(
    String,
    nullable=False,
    unique=True,
    index=True,
    comment="The name of the protocol source",
    init=False,
  )
  base_path: Mapped[str] = mapped_column(
    String,
    nullable=False,
    comment="The base path for the file system protocol source.",
    default="",
  )
  is_recursive: Mapped[bool] = mapped_column(
    Boolean,
    default=True,
    comment="Whether to recursively scan subdirectories.",
  )
  status: Mapped[ProtocolSourceStatusEnum] = mapped_column(
    SAEnum(ProtocolSourceStatusEnum, name="ps_status_enum_fs_v3"),
    default=ProtocolSourceStatusEnum.ACTIVE,
    nullable=False,
  )
  function_protocol_definitions: Mapped[list["FunctionProtocolDefinitionOrm"]] = relationship(
    "FunctionProtocolDefinitionOrm",
    back_populates="file_system_source",
    default_factory=list,
  )

  def __repr__(self) -> str:
    """Return a string representation of the FileSystemProtocolSourceOrm instance."""
    return (
      f"<FileSystemProtocolSourceOrm(id={self.accession_id}, name='{self.name}', "
      f"base_path='{self.base_path}')>"
    )


class FunctionProtocolDefinitionOrm(Base):
  """SQLAlchemy ORM model for storing static definitions of function-based protocols.

  This model represents a discoverable protocol, including its name, version,
  source location, and metadata defining its behavior and requirements.
  """

  __tablename__ = "function_protocol_definitions"
  name: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="The name of the protocol function.",
    init=False,
  )
  version: Mapped[str] = mapped_column(
    String,
    nullable=False,
    default="0.1.0",
    comment="The version of the protocol function, following semantic versioning.",
  )
  description: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    comment="A human-readable description of the protocol function.",
    default=None,
  )
  source_file_path: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="The file path where the protocol function is defined, relative to its source \
      repository or file system source.",
    default="",
  )
  module_name: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="The module name where the protocol function is defined, used for import resolution.",
    default="",
  )
  function_name: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="The name of the function that implements the protocol logic.",
    default="",
  )
  source_repository_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("protocol_source_repositories.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the protocol source repository where this function is defined.",
    default=None,
  )
  commit_hash: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    index=True,
    comment="The commit hash of the source repository where this function is defined.",
    default=None,
  )
  file_system_source_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("file_system_protocol_sources.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the file system protocol source where this function is defined.",
    default=None,
  )
  is_top_level: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
  solo_execution: Mapped[bool] = mapped_column(Boolean, default=False)
  preconfigure_deck: Mapped[bool] = mapped_column(Boolean, default=False)
  deck_param_name: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="Name of the deck parameter in the function signature.",
    default=None,
  )
  deck_construction_function_fqn: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="FQN of the function to construct the deck.",
    default=None,
  )
  state_param_name: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="Name of the state parameter in the function signature.",
    default=None,
  )
  category: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    index=True,
    comment="Category of the protocol function, used for grouping or filtering.",
    default=None,
  )
  tags: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="Arbitrary tags associated with the protocol function for categorization.",
    default=None,
  )
  deprecated: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

  parameters: Mapped[list["ParameterDefinitionOrm"]] = relationship(
    "ParameterDefinitionOrm",
    back_populates="protocol_definition",
    cascade="all, delete-orphan",
    default_factory=list,
    comment="List of parameters required by the protocol function, including type hints and default\
      values.",
  )
  assets: Mapped[list["AssetRequirementOrm"]] = relationship(
    "AssetRequirementOrm",
    back_populates="protocol_definition",
    cascade="all, delete-orphan",
    default_factory=list,
    comment="List of assets required by the protocol function, including type hints and default \
      values.",
  )
  source_repository: Mapped["ProtocolSourceRepositoryOrm"] = relationship(
    "ProtocolSourceRepositoryOrm",
    back_populates="function_protocol_definitions",
    foreign_keys=[source_repository_accession_id],
    comment="The protocol source repository where this function is defined, if applicable.",
    init=False,
  )
  file_system_source: Mapped["FileSystemProtocolSourceOrm"] = relationship(
    "FileSystemProtocolSourceOrm",
    back_populates="function_protocol_definitions",
    foreign_keys=[file_system_source_accession_id],
    comment="The file system protocol source where this function is defined, if applicable.",
    init=False,
  )
  protocol_runs: Mapped[list["ProtocolRunOrm"]] = relationship(
    "ProtocolRunOrm",
    back_populates="top_level_protocol_definition",
    default_factory=list,
    comment="List of protocol runs that executed this function definition.",
  )
  function_call_logs: Mapped[list["FunctionCallLogOrm"]] = relationship(
    "FunctionCallLogOrm",
    foreign_keys="[FunctionCallLogOrm.function_protocol_definition_accession_id]",
    back_populates="executed_function_definition",
    default_factory=list,
    comment="List of function call logs that executed this protocol function.",
  )

  __table_args__ = (
    UniqueConstraint(
      "name",
      "version",
      "source_repository_accession_id",
      "commit_hash",
      name="uq_repo_protocol_def_version_v3",
    ),
    UniqueConstraint(
      "name",
      "version",
      "file_system_source_accession_id",
      "source_file_path",
      name="uq_fs_protocol_def_version_v3",
    ),
  )

  def __repr__(self) -> str:
    """Return a string representation of the FunctionProtocolDefinitionOrm instance."""
    return f"<FunctionProtocolDefinitionOrm(id={self.accession_id}, name='{self.name}',\
      version='{self.version}')>"


class ParameterDefinitionOrm(Base):
  """SQLAlchemy ORM model for defining parameters of a function protocol.

  This model stores metadata about each parameter required by a protocol function,
  including its name, type hints, default values, and any constraints.
  """

  __tablename__ = "parameter_definitions"
  protocol_definition_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("function_protocol_definitions.accession_id"),
    nullable=False,
    index=True,
    comment="Foreign key to the protocol definition this parameter belongs to.",
    init=False,
  )
  name: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="The name of the parameter.",
    default="",
  )
  type_hint: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="The type hint of the parameter.",
    default="",
  )
  fqn: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="The fully qualified name of the parameter.",
    default="",
  )
  is_deck_param: Mapped[bool] = mapped_column(Boolean, default=False)
  optional: Mapped[bool] = mapped_column(
    Boolean,
    nullable=False,
    default=False,
    comment="Whether the parameter is optional.",
  )
  default_value_repr: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="String representation of the default value for the parameter.",
    default=None,
  )
  description: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    comment="A human-readable description of the parameter.",
    default=None,
  )
  constraints_json: Mapped[dict | None] = mapped_column(
    "constraints",
    JSONB,
    nullable=True,
    comment="JSONB representation of any constraints on the parameter, such as allowed values or \
      ranges.",
    default=None,  # TODO(mar): consider using a more structured type for constraints # noqa: TD003
  )
  ui_hint_json: Mapped[dict | None] = mapped_column(
    "ui_hint",
    JSONB,
    nullable=True,
    comment="JSONB representation of UI hints for the parameter.",
    default=None,
  )
  protocol_definition: Mapped["FunctionProtocolDefinitionOrm"] = relationship(
    "FunctionProtocolDefinitionOrm",
    back_populates="parameters",
    init=False,
    comment="The protocol definition this parameter belongs to.",
  )
  __table_args__ = (
    UniqueConstraint(
      "protocol_definition_accession_id",
      "name",
      name="uq_param_def_name_per_protocol_v3",
    ),
  )

  def __repr__(self) -> str:
    """Return a string representation of the ParameterDefinitionOrm instance."""
    return f"<ParameterDefinitionOrm(name='{self.name}', \
      protocol_accession_id={self.protocol_definition_accession_id})>"


class AssetRequirementOrm(Base):
  """SQLAlchemy ORM model for defining assets required by a function protocol.

  This model describes the assets (e.g., resource, machines) a protocol function
  expects, including their names, type hints, and descriptions.
  """

  __tablename__ = "protocol_asset_requirements"
  protocol_definition_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("function_protocol_definitions.accession_id"),
    nullable=False,
    index=True,
    comment="Foreign key to the protocol definition this asset requirement belongs to.",
    init=False,
  )
  name: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="The name of the asset requirement.",
    default="",
  )
  type_hint_str: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="The type hint of the asset requirement.",
    default="",
  )
  actual_type_str: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="The actual type of the asset requirement.",
    default="",
  )
  fqn: Mapped[str] = mapped_column(
    String,
    nullable=False,
    index=True,
    comment="The fully qualified name of the asset requirement's class.",
    default="",
  )  # Fully qualified name for the asset
  optional: Mapped[bool] = mapped_column(
    Boolean,
    nullable=False,
    default=False,
    comment="Whether the asset requirement is optional.",
  )
  default_value_repr: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="String representation of the default value for the asset requirement.",
    default=None,
  )
  description: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    comment="A human-readable description of the asset requirement.",
    default=None,
  )
  constraints_json: Mapped[dict | None] = mapped_column(
    "constraints",
    JSONB,
    nullable=True,
    comment="JSONB representation of any constraints on the asset requirement, such as allowed \
      values or ranges.",
    default=None,  # TODO(mar): consider using a more structured type for constraints # noqa: TD003
  )
  location_constraints_json: Mapped[dict | None] = mapped_column(
    "location_constraints",
    JSONB,
    nullable=True,
    comment="JSONB representation of location constraints for the asset requirement.",
    default=None,
  )
  function_protocol_definition: Mapped["FunctionProtocolDefinitionOrm"] = relationship(
    "FunctionProtocolDefinitionOrm",
    back_populates="assets",
    comment="The protocol definition this asset requirement belongs to.",
    nullable=False,
    init=False,
  )
  resource_definitions: Mapped[list["ResourceDefinitionOrm"]] = relationship(
    "ResourceDefinitionOrm",
    back_populates="asset_requirement",
    cascade="all, delete-orphan",
    default_factory=list,
    comment="List of resource definitions that match this asset requirement.",
  )
  machine_definitions: Mapped[list["MachineDefinitionOrm"]] = relationship(
    "MachineDefinitionOrm",
    back_populates="asset_requirement",
    cascade="all, delete-orphan",
    default_factory=list,
    comment="List of machine definitions that match this asset requirement.",
  )
  deck_definitions: Mapped[list["DeckDefinitionOrm"]] = relationship(
    "DeckDefinitionOrm",
    back_populates="asset_requirement",
    cascade="all, delete-orphan",
    default_factory=list,
    comment="List of deck definitions that match this asset requirement.",
  )

  __table_args__ = (
    UniqueConstraint(
      "protocol_definition_accession_id",
      "name",
      name="uq_asset_def_name_per_protocol_v3",
    ),
  )

  def __repr__(self) -> str:
    """Return a string representation of the AssetDefinitionOrm instance."""
    return f"<AssetDefinitionOrm(name='{self.name}', \
      protocol_accession_id={self.protocol_definition_accession_id})>"


class ProtocolRunOrm(Base):
  """SQLAlchemy ORM model for logging a top-level protocol execution.

  This model captures the runtime details of a protocol, such as its GUID,
  status, start/end times, input parameters, resolved assets, and output data.
  """

  __tablename__ = "protocol_runs"

  top_level_protocol_definition_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("function_protocol_definitions.accession_id"),
    nullable=False,
    index=True,
    comment="Foreign key to the top-level protocol definition that this run executes.",
    init=False,
  )
  status: Mapped[ProtocolRunStatusEnum] = mapped_column(
    SAEnum(ProtocolRunStatusEnum, name="protocol_run_status_enum_v3"),
    default=ProtocolRunStatusEnum.PENDING,
    nullable=False,
    index=True,
  )
  start_time: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="The start time of the protocol run. Null if not yet started.",
    default=None,
  )
  end_time: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="The end time of the protocol run. Null if not yet completed.",
    default=None,
  )
  completed_duration_ms: Mapped[int | None] = mapped_column(
    Integer,
    Computed(
      "(EXTRACT(EPOCH FROM (end_time - start_time)) * 1000)",
      persisted=True,
    ),
    comment="Stored duration in milliseconds, computed by the DB when a run completes.",
    nullable=True,
    init=False,
  )

  current_duration_ms: Mapped[int | None] = mapped_column(
    Integer,
    Computed(
      """CASE
              WHEN start_time IS NULL THEN NULL
              WHEN end_time IS NOT NULL THEN (EXTRACT(EPOCH FROM (end_time - start_time)) * 1000)
              ELSE (EXTRACT(EPOCH FROM (NOW() - start_time)) * 1000)
           END
        """,
      persisted=False,
    ),
    comment="Virtual duration in ms. For ongoing runs, it's calculated on-the-fly against the \
      current time.",
    nullable=True,
    init=False,
  )
  input_parameters_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="Input parameters for the protocol run.",
    default=None,
  )
  resolved_assets_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="Resolved assets for the protocol run.",
    default=None,
  )
  output_data_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="Output data for the protocol run.",
    default=None,
  )
  initial_state_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="Initial state for the protocol run.",
    default=None,
  )
  final_state_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="Final state for the protocol run.",
    default=None,
  )
  data_directory_path: Mapped[str | None] = mapped_column(
    String,
    nullable=True,
    comment="File path to the data directory for the protocol run.",
    default=None,
  )
  created_by_user: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    comment="Information about the user who created this protocol run.",
    default=None,
  )
  top_level_protocol_definition: Mapped["FunctionProtocolDefinitionOrm"] = relationship(
    "FunctionProtocolDefinitionOrm",
    back_populates="protocol_runs",
    foreign_keys=[top_level_protocol_definition_accession_id],
    comment="The top-level protocol definition that this run executes.",
    init=False,
  )
  function_calls: Mapped[list["FunctionCallLogOrm"]] = relationship(
    "FunctionCallLogOrm",
    back_populates="protocol_run",
    cascade="all, delete-orphan",
    order_by="FunctionCallLogOrm.sequence_in_run",
    comment="List of function call logs executed during this protocol run, ordered by their \
      sequence in the run.",
    default_factory=list,
  )

  # Relationship to data outputs
  data_outputs: Mapped[list["FunctionDataOutputOrm"]] = relationship(
    "FunctionDataOutputOrm",
    back_populates="protocol_run",
    cascade="all, delete-orphan",
    default_factory=list,
    comment="List of data outputs generated by this protocol run.",
  )
  previous_accession_id: Mapped[uuid.UUID | None] = mapped_column(
    UUID,
    ForeignKey("protocol_runs.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the previous protocol run in a continuation chain.",
    default=None,
  )
  continuing_from_accession_id: Mapped["ProtocolRunOrm | None"] = relationship(
    "ProtocolRunOrm",
    back_populates="continuations",
    remote_side=[previous_accession_id],
    foreign_keys=[previous_accession_id],
    uselist=False,
    comment="The protocol run that this run continues from, if applicable.",
    default=None,
  )
  continuations: Mapped[list["ProtocolRunOrm"]] = relationship(
    "ProtocolRunOrm",
    back_populates="continuing_from",
    foreign_keys="ProtocolRunOrm.continuing_from_accession_id",
    default_factory=list,
    comment="List of protocol runs that continue from this run, forming a chain of execution.",
  )
  schedule_entries: Mapped[list["ScheduleEntryOrm"]] = relationship(
    "ScheduleEntryOrm",
    back_populates="protocol_run",
    default_factory=list,
  )

  def __repr__(self) -> str:
    """Return a string representation of the ProtocolRunOrm instance."""
    return f"<ProtocolRunOrm(accession_id={self.accession_id}, status='{self.status.name}')>"


class FunctionCallLogOrm(Base):
  """SQLAlchemy ORM model for logging individual function calls within a protocol run.

  This model captures detailed information for each executed function during a protocol
  run, including its sequence, input arguments, return values, and status.
  """

  __tablename__ = "function_call_logs"
  accession_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, index=True)
  protocol_run_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("protocol_runs.accession_id"),
    nullable=False,
    index=True,
    comment="Foreign key to the protocol run this function call belongs to.",
    init=False,
  )
  sequence_in_run: Mapped[int] = mapped_column(
    Integer,
    nullable=False,
    index=True,
    comment="Sequence number of this function call within the protocol run, starting from 0.",
    init=False,
  )
  function_protocol_definition_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("function_protocol_definitions.accession_id"),
    nullable=False,
    index=True,
    comment="Foreign key to the function protocol definition that this call executes.",
    init=False,
  )
  parent_function_call_log_accession_id: Mapped[UUID | None] = mapped_column(
    UUID,
    ForeignKey("function_call_logs.accession_id"),
    nullable=True,
    index=True,
    comment="Foreign key to the parent function call log, if this call is a child of another call.",
    default=None,
  )
  start_time: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=False,
    server_default=func.now(),
    init=False,
    comment="The start time of the function call, automatically set when the call is created.",
  )
  end_time: Mapped[datetime | None] = mapped_column(
    DateTime(timezone=True),
    nullable=True,
    comment="The end time of the function call, automatically set when the call is completed.",
    default=None,
    init=False,
  )
  completed_duration_ms: Mapped[int | None] = mapped_column(
    Integer,
    Computed(
      "(EXTRACT(EPOCH FROM (end_time - start_time)) * 1000)",
      persisted=True,
    ),
    comment="Stored duration in milliseconds, computed by the DB when a call completes.",
    nullable=True,
    init=False,
  )
  current_duration_ms: Mapped[int | None] = mapped_column(
    Integer,
    Computed(
      """CASE
              WHEN start_time IS NULL THEN NULL
              WHEN end_time IS NOT NULL THEN (EXTRACT(EPOCH FROM (end_time - start_time)) * 1000)
              ELSE (EXTRACT(EPOCH FROM (NOW() - start_time)) * 1000)
           END
        """,
      persisted=False,
    ),
    comment="Virtual duration in ms. For ongoing calls, it's calculated on-the-fly against the \
      current time.",
    nullable=True,
    init=False,
  )
  input_args_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
    comment="Input arguments for the function call.",
  )
  return_value_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
    comment="Return value of the function call.",
  )
  status: Mapped[FunctionCallStatusEnum] = mapped_column(
    SAEnum(FunctionCallStatusEnum, name="function_call_status_enum_v3"),
    nullable=False,
    default=FunctionCallStatusEnum.UNKNOWN,
  )
  error_message_text: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    default=None,
    comment="Error message, if any.",
  )
  error_traceback_text: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    default=None,
    comment="Error traceback, if any.",
  )
  protocol_run: Mapped["ProtocolRunOrm"] = relationship(
    "ProtocolRunOrm",
    back_populates="function_calls",
    foreign_keys=[protocol_run_accession_id],
    comment="The protocol run that this function call belongs to.",
    init=False,
  )
  executed_function_definition: Mapped["FunctionProtocolDefinitionOrm"] = relationship(
    "FunctionProtocolDefinitionOrm",
    foreign_keys=[function_protocol_definition_accession_id],
    back_populates="function_call_logs",
    comment="The function protocol definition that this call executes.",
    init=False,
  )
  parent_call: Mapped["FunctionCallLogOrm"] = relationship(
    "FunctionCallLogOrm",
    remote_side=[accession_id],
    backref="child_calls",
    init=False,
  )

  # Relationship to data outputs
  data_outputs: Mapped[list["FunctionDataOutputOrm"]] = relationship(
    "FunctionDataOutputOrm",
    back_populates="function_call_log",
    cascade="all, delete-orphan",
    default_factory=list,
    comment="List of data outputs generated by this function call.",
  )

  def __repr__(self) -> str:
    """Return a string representation of the FunctionCallLogOrm instance."""
    return (
      f"<FunctionCallLogOrm(id={self.accession_id}, "
      f"run_accession_id={self.protocol_run_accession_id}, "
      f"seq={self.sequence_in_run}, status='{self.status.name}')>"
    )
