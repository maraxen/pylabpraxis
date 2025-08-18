# pylint: disable=too-few-public-methods,missing-class-docstring,invalid-name
"""Function Data Output ORM Models for Protocol Execution Data Management.

This module defines ORM models for capturing and linking data outputs from protocol function
calls to specific resource, machines, and spatial locations. This enables detailed data
attribution and visualization capabilities.

Key Features:
- Links data outputs to specific function calls and protocol runs
- Associates data with specific resource (plates, wells, etc.)
- Captures spatial and temporal context
- Supports various data types (measurements, images, files)
- Enables data lineage tracking

Includes:
- FunctionDataOutputOrm: Main model for protocol function data outputs
- WellDataOutputOrm: Specialized model for well-specific data outputs with plate context
- Relationships to protocol runs, function call logs, resources, machines, and decks

"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
  UUID,
  DateTime,
  Float,
  ForeignKey,
  Integer,
  LargeBinary,
  String,
  Text,
)
from sqlalchemy import (
  Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from praxis.backend.models.enums.outputs import DataOutputTypeEnum, SpatialContextEnum
from praxis.backend.utils.db import Base
from praxis.backend.utils.uuid import uuid7

if TYPE_CHECKING:
  from . import DeckOrm, FunctionCallLogOrm, MachineOrm, ProtocolRunOrm, ResourceOrm


class FunctionDataOutputOrm(Base):

  """ORM model for capturing data outputs from protocol function calls.

  This model links data outputs to specific function calls and allows association
  with resource, machines, and spatial locations for detailed attribution.
  """

  __tablename__ = "function_data_outputs"

  protocol_run_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("protocol_runs.accession_id"),
    nullable=False,
    index=True,
    kw_only=True,
  )

  function_call_log_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("function_call_logs.accession_id"),
    nullable=False,
    index=True,
    kw_only=True,
  )

  data_type: Mapped[DataOutputTypeEnum] = mapped_column(
    SAEnum(DataOutputTypeEnum, name="data_output_type_enum"),
    nullable=False,
    index=True,
    default=DataOutputTypeEnum.UNKNOWN,
  )

  data_key: Mapped[str] = mapped_column(
    String(255),
    nullable=False,
    default="",
  )

  spatial_context: Mapped[SpatialContextEnum] = mapped_column(
    SAEnum(SpatialContextEnum, name="spatial_context_enum"),
    nullable=False,
    index=True,
    default=SpatialContextEnum.GLOBAL,
  )

  resource_accession_id: Mapped[UUID | None] = mapped_column(
    UUID,
    ForeignKey("resources.accession_id"),
    nullable=True,
    index=True,
    default=None,
  )

  machine_accession_id: Mapped[UUID | None] = mapped_column(
    UUID,
    ForeignKey("machines.accession_id"),
    nullable=True,
    index=True,
    default=None,
  )

  deck_accession_id: Mapped[UUID | None] = mapped_column(
    UUID,
    ForeignKey("decks.accession_id"),
    nullable=True,
    index=True,
    default=None,
  )

  spatial_coordinates_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )

  data_value_numeric: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
  )

  data_value_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )

  data_value_text: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    default=None,
  )

  data_value_binary: Mapped[bytes | None] = mapped_column(
    LargeBinary,
    nullable=True,
    default=None,
  )

  file_path: Mapped[str | None] = mapped_column(
    String(500),
    nullable=True,
    default=None,
  )

  file_size_bytes: Mapped[int | None] = mapped_column(
    Integer,
    nullable=True,
    default=None,
  )

  data_units: Mapped[str | None] = mapped_column(
    String(50),
    nullable=True,
    default=None,
  )

  data_quality_score: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
  )

  measurement_conditions_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )

  measurement_timestamp: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=False,
    default=func.now(),
  )

  sequence_in_function: Mapped[int | None] = mapped_column(
    Integer,
    nullable=True,
    default=None,
  )

  derived_from_data_output_accession_id: Mapped[UUID | None] = mapped_column(
    UUID,
    ForeignKey("function_data_outputs.accession_id"),
    nullable=True,
    index=True,
    default=None,
  )

  processing_metadata_json: Mapped[dict | None] = mapped_column(
    JSONB,
    nullable=True,
    default=None,
  )

  # Relationships
  function_call_log: Mapped["FunctionCallLogOrm"] = relationship(
    "FunctionCallLogOrm",
    foreign_keys=[function_call_log_accession_id],
    back_populates="data_outputs",
    default=None,
  )

  protocol_run: Mapped["ProtocolRunOrm"] = relationship(
    "ProtocolRunOrm",
    foreign_keys=[protocol_run_accession_id],
    back_populates="data_outputs",
    default=None,
  )

  resource: Mapped["ResourceOrm"] = relationship(
    "ResourceOrm",
    foreign_keys=[resource_accession_id],
    back_populates="data_outputs",
    default=None,
  )

  machine: Mapped["MachineOrm"] = relationship(
    "MachineOrm",
    foreign_keys=[machine_accession_id],
    back_populates="data_outputs",
    default=None,
  )

  deck: Mapped["DeckOrm"] = relationship(
    "DeckOrm",
    foreign_keys=[deck_accession_id],
    back_populates="data_outputs",
    default=None,
  )

  derived_from: Mapped["FunctionDataOutputOrm"] = relationship(
    "FunctionDataOutputOrm",
    remote_side=lambda: [FunctionDataOutputOrm.accession_id],
    backref="derived_data_outputs",
    foreign_keys=[derived_from_data_output_accession_id],
    default_factory=list,
  )

  well_data_outputs: Mapped[list["WellDataOutputOrm"]] = relationship(
    "WellDataOutputOrm",
    back_populates="function_data_output",
    cascade="all, delete-orphan",
    default_factory=list,
  )

  def __repr__(self) -> str:
    """Return a string representation of the FunctionDataOutputOrm instance."""
    return (
      f"<FunctionDataOutputOrm(id={self.accession_id}, "
      f"type={self.data_type.value}, "
      f"key='{self.data_key}', "
      f"spatial_context={self.spatial_context.value})>"
    )


class WellDataOutputOrm(Base):

  """Specialized model for well-specific data outputs with plate context.

  This model provides a convenient interface for data that's specifically tied
  to wells in plate-based assays, with built-in plate layout awareness.
  """

  __tablename__ = "well_data_outputs"

  function_data_output_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("function_data_outputs.accession_id"),
    nullable=False,
    index=True,
    default_factory=uuid7,
  )

  plate_resource_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID,
    ForeignKey("resources.accession_id"),
    nullable=False,
    index=True,
    default_factory=uuid7,
  )

  well_name: Mapped[str] = mapped_column(
    String(10),
    nullable=False,
    default="",
  )

  well_row: Mapped[int] = mapped_column(
    Integer,
    nullable=False,
    default=0,
  )

  well_column: Mapped[int] = mapped_column(
    Integer,
    nullable=False,
    default=0,
  )

  well_index: Mapped[int | None] = mapped_column(
    Integer,
    nullable=True,
    default=None,
  )

  data_value: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
    default=None,
  )

  function_data_output: Mapped["FunctionDataOutputOrm"] = relationship(
    "FunctionDataOutputOrm",
    foreign_keys=[function_data_output_accession_id],
    back_populates="well_data_outputs",
    default=None,
  )

  plate_resource: Mapped["ResourceOrm"] = relationship(
    "ResourceOrm",
    foreign_keys=[plate_resource_accession_id],
    back_populates="well_data_outputs",
    default=None,
  )
  resource: Mapped["ResourceOrm"] = relationship(
    "ResourceOrm",
    foreign_keys=[plate_resource_accession_id],
    back_populates="well_data_outputs",
    uselist=False,
    default=None,
  )
  machine: Mapped["MachineOrm"] = relationship(
    "MachineOrm",
    foreign_keys="FunctionDataOutputOrm.machine_accession_id",
    back_populates="well_data_outputs",
    uselist=False,
    default=None,
  )

  def __repr__(self) -> str:
    """Return a string representation of the WellDataOutputOrm instance."""
    return (
      f"<WellDataOutputOrm(id={self.accession_id}, well={self.well_name}, value={self.data_value})>"
    )
