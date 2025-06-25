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
"""

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
  pass

from sqlalchemy import (
  JSON,
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
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from praxis.backend.utils.db import Base


class DataOutputTypeEnum(enum.Enum):
  """Enumeration for different types of data outputs."""

  # Measurement data
  ABSORBANCE_READING = "absorbance_reading"
  FLUORESCENCE_READING = "fluorescence_reading"
  LUMINESCENCE_READING = "luminescence_reading"
  OPTICAL_DENSITY = "optical_density"
  TEMPERATURE_READING = "temperature_reading"
  VOLUME_MEASUREMENT = "volume_measurement"
  GENERIC_MEASUREMENT = "generic_measurement"

  # Image data
  PLATE_IMAGE = "plate_image"
  MICROSCOPY_IMAGE = "microscopy_image"
  CAMERA_SNAPSHOT = "camera_snapshot"

  # File data
  RAW_DATA_FILE = "raw_data_file"
  ANALYSIS_REPORT = "analysis_report"
  CONFIGURATION_FILE = "configuration_file"

  # Calculated/derived data
  CALCULATED_CONCENTRATION = "calculated_concentration"
  KINETIC_ANALYSIS = "kinetic_analysis"
  STATISTICAL_SUMMARY = "statistical_summary"

  # Status/state data
  MACHINE_STATUS = "machine_status"
  LIQUID_LEVEL = "liquid_level"
  ERROR_LOG = "error_log"


class DataOutputSpatialContextEnum(enum.Enum):
  """Enumeration for spatial context types."""

  WELL_SPECIFIC = "well_specific"  # Data tied to specific well(s)
  PLATE_LEVEL = "plate_level"  # Data for entire plate
  MACHINE_LEVEL = "machine_level"  # Data from machine/machine
  DECK_POSITION = "deck_position"  # Data tied to deck position
  GLOBAL = "global"  # Run-level data without specific location


# Alias for backwards compatibility and cleaner imports
SpatialContextEnum = DataOutputSpatialContextEnum


class FunctionDataOutputOrm(Base):
  """ORM model for capturing data outputs from protocol function calls.

  This model links data outputs to specific function calls and allows association
  with resource, machines, and spatial locations for detailed attribution.
  """

  __tablename__ = "function_data_outputs"

  accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID, primary_key=True, nullable=False
  )

  function_call_log_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID, ForeignKey("function_call_logs.accession_id"), nullable=False, index=True
  )

  protocol_run_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID, ForeignKey("protocol_runs.accession_id"), nullable=False, index=True
  )

  data_type: Mapped[DataOutputTypeEnum] = mapped_column(
    SAEnum(DataOutputTypeEnum, name="data_output_type_enum"), nullable=False, index=True
  )

  data_key: Mapped[str] = mapped_column(
    String(255),
    nullable=False,
    comment="Unique key within the function call (e.g., 'absorbance_580nm', 'well_A1_od')",
  )

  spatial_context: Mapped[DataOutputSpatialContextEnum] = mapped_column(
    SAEnum(DataOutputSpatialContextEnum, name="data_output_spatial_context_enum"),
    nullable=False,
    index=True,
  )

  resource_instance_accession_id: Mapped[Optional[UUID]] = mapped_column(
    UUID, ForeignKey("resource_instances.accession_id"), nullable=True, index=True
  )

  machine_accession_id: Mapped[Optional[UUID]] = mapped_column(
    UUID, ForeignKey("machines.accession_id"), nullable=True, index=True
  )

  deck_instance_accession_id: Mapped[Optional[UUID]] = mapped_column(
    UUID, ForeignKey("deck_instances.accession_id"), nullable=True, index=True
  )

  spatial_coordinates_json: Mapped[Optional[dict]] = mapped_column(
    JSON,
    nullable=True,
    comment="Spatial coordinates within resource (e.g., {'well': 'A1', 'row': 0, 'col': 0})",
  )

  data_value_numeric: Mapped[Optional[float]] = mapped_column(
    Float, nullable=True, comment="Numeric data values"
  )

  data_value_json: Mapped[Optional[dict]] = mapped_column(
    JSON, nullable=True, comment="Structured data (arrays, objects, etc.)"
  )

  data_value_text: Mapped[Optional[str]] = mapped_column(
    Text, nullable=True, comment="Text data or serialized content"
  )

  data_value_binary: Mapped[Optional[bytes]] = mapped_column(
    LargeBinary, nullable=True, comment="Binary data (images, files)"
  )

  # File reference (for large files stored externally)
  file_path: Mapped[Optional[str]] = mapped_column(
    String(500), nullable=True, comment="Path to external file"
  )

  file_size_bytes: Mapped[Optional[int]] = mapped_column(
    Integer, nullable=True, comment="File size in bytes"
  )

  data_units: Mapped[Optional[str]] = mapped_column(
    String(50), nullable=True, comment="Units of measurement (e.g., 'nm', 'μL', 'OD')"
  )

  data_quality_score: Mapped[Optional[float]] = mapped_column(
    Float, nullable=True, comment="Quality score (0.0-1.0)"
  )

  measurement_conditions_json: Mapped[Optional[dict]] = mapped_column(
    JSON,
    nullable=True,
    comment="Measurement conditions (temperature, wavelength, etc.)",
  )

  measurement_timestamp: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    nullable=False,
    default=func.now(),
    comment="When the measurement/data was captured",
  )

  sequence_in_function: Mapped[Optional[int]] = mapped_column(
    Integer, nullable=True, comment="Sequence number within the function call"
  )

  derived_from_data_output_accession_id: Mapped[Optional[UUID]] = mapped_column(
    UUID, ForeignKey("function_data_outputs.accession_id"), nullable=True
  )

  processing_metadata_json: Mapped[Optional[dict]] = mapped_column(
    JSON, nullable=True, comment="Metadata about data processing/transformation"
  )

  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )

  updated_at: Mapped[Optional[datetime]] = mapped_column(
    DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
  )

  # Relationships
  function_call_log = relationship(
    "FunctionCallLogOrm",
    foreign_keys=[function_call_log_accession_id],
    back_populates="data_outputs",
  )

  protocol_run = relationship(
    "ProtocolRunOrm",
    foreign_keys=[protocol_run_accession_id],
    back_populates="data_outputs",
  )

  resource_instance = relationship(
    "ResourceInstanceOrm",
    foreign_keys=[resource_instance_accession_id],
    back_populates="data_outputs",
  )

  machine = relationship(
    "MachineOrm", foreign_keys=[machine_accession_id], back_populates="data_outputs"
  )

  deck_instance = relationship(
    "DeckOrm",
    foreign_keys=[deck_instance_accession_id],
    back_populates="data_outputs",
  )

  derived_from = relationship(
    "FunctionDataOutputOrm", remote_side=[accession_id], backref="derived_data_outputs"
  )

  well_data_outputs = relationship(
    "WellDataOutputOrm",
    back_populates="function_data_output",
    cascade="all, delete-orphan",
  )

  def __repr__(self):
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

  accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID, primary_key=True, nullable=False
  )

  function_data_output_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID, ForeignKey("function_data_outputs.accession_id"), nullable=False, index=True
  )

  plate_resource_instance_accession_id: Mapped[uuid.UUID] = mapped_column(
    UUID, ForeignKey("resource_instances.accession_id"), nullable=False, index=True
  )

  well_name: Mapped[str] = mapped_column(
    String(10), nullable=False, comment="Well name (e.g., 'A1', 'H12')"
  )

  well_row: Mapped[int] = mapped_column(
    Integer, nullable=False, comment="0-based row index"
  )

  well_column: Mapped[int] = mapped_column(
    Integer, nullable=False, comment="0-based column index"
  )

  well_index: Mapped[Optional[int]] = mapped_column(
    Integer, nullable=True, comment="Linear well index (0-based)"
  )

  data_value: Mapped[Optional[float]] = mapped_column(
    Float, nullable=True, comment="Primary numeric value for this well"
  )

  created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), server_default=func.now()
  )

  function_data_output = relationship(
    "FunctionDataOutputOrm",
    foreign_keys=[function_data_output_accession_id],
    back_populates="well_data_outputs",
  )

  plate_resource_instance = relationship(
    "ResourceInstanceOrm", foreign_keys=[plate_resource_instance_accession_id]
  )

  def __repr__(self):
    """Return a string representation of the WellDataOutputOrm instance."""
    return (
      f"<WellDataOutputOrm(id={self.accession_id}, "
      f"well={self.well_name}, "
      f"value={self.data_value})>"
    )
