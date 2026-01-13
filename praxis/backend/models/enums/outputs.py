"""Enumerated types for various data output attributes.

Classes:
  DataOutputTypeEnum (enum.Enum): Enum representing the different categories of data outputs, such
  as measurement readings, image data, file data, calculated data, and status/state data.
  SpatialContextEnum (enum.Enum): Enum representing the spatial context of data outputs, indicating
  where the data was collected or to what it pertains (e.g., well-specific, plate-level,
  machine-level).
"""

import enum


class DataOutputTypeEnum(str, enum.Enum):
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

  # Other types
  UNKNOWN = "unknown"  # Fallback for unclassified data types


class SpatialContextEnum(str, enum.Enum):
  """Enumeration for spatial context types."""

  WELL_SPECIFIC = "well_specific"  # Data tied to specific well(s)
  PLATE_LEVEL = "plate_level"  # Data for entire plate
  MACHINE_LEVEL = "machine_level"  # Data from machine/machine
  DECK_POSITION = "deck_position"  # Data tied to deck position
  GLOBAL = "global"  # Run-level data without specific location
  UNKNOWN = "unknown"  # Fallback for unclassified spatial contexts
