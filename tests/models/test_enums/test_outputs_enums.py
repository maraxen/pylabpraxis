"""Tests for output enum types in models/enums/outputs.py."""

import enum

from praxis.backend.models.enums.outputs import DataOutputTypeEnum, SpatialContextEnum


class TestDataOutputTypeEnum:

    """Tests for DataOutputTypeEnum."""

    def test_is_enum(self) -> None:
        """Test that DataOutputTypeEnum is an enum."""
        assert issubclass(DataOutputTypeEnum, enum.Enum)

    def test_has_absorbance_reading(self) -> None:
        """Test that enum has ABSORBANCE_READING."""
        assert DataOutputTypeEnum.ABSORBANCE_READING.value == "absorbance_reading"

    def test_has_fluorescence_reading(self) -> None:
        """Test that enum has FLUORESCENCE_READING."""
        assert DataOutputTypeEnum.FLUORESCENCE_READING.value == "fluorescence_reading"

    def test_has_luminescence_reading(self) -> None:
        """Test that enum has LUMINESCENCE_READING."""
        assert DataOutputTypeEnum.LUMINESCENCE_READING.value == "luminescence_reading"

    def test_has_plate_image(self) -> None:
        """Test that enum has PLATE_IMAGE."""
        assert DataOutputTypeEnum.PLATE_IMAGE.value == "plate_image"

    def test_has_raw_data_file(self) -> None:
        """Test that enum has RAW_DATA_FILE."""
        assert DataOutputTypeEnum.RAW_DATA_FILE.value == "raw_data_file"

    def test_has_unknown(self) -> None:
        """Test that enum has UNKNOWN."""
        assert DataOutputTypeEnum.UNKNOWN.value == "unknown"

    def test_has_measurement_types(self) -> None:
        """Test that enum has measurement data types."""
        measurement_types = [
            "ABSORBANCE_READING",
            "FLUORESCENCE_READING",
            "LUMINESCENCE_READING",
            "OPTICAL_DENSITY",
            "TEMPERATURE_READING",
            "VOLUME_MEASUREMENT",
            "GENERIC_MEASUREMENT",
        ]
        actual_names = [member.name for member in DataOutputTypeEnum]
        for mtype in measurement_types:
            assert mtype in actual_names

    def test_has_image_types(self) -> None:
        """Test that enum has image data types."""
        image_types = ["PLATE_IMAGE", "MICROSCOPY_IMAGE", "CAMERA_SNAPSHOT"]
        actual_names = [member.name for member in DataOutputTypeEnum]
        for itype in image_types:
            assert itype in actual_names

    def test_has_file_types(self) -> None:
        """Test that enum has file data types."""
        file_types = ["RAW_DATA_FILE", "ANALYSIS_REPORT", "CONFIGURATION_FILE"]
        actual_names = [member.name for member in DataOutputTypeEnum]
        for ftype in file_types:
            assert ftype in actual_names

    def test_has_calculated_types(self) -> None:
        """Test that enum has calculated data types."""
        calc_types = [
            "CALCULATED_CONCENTRATION",
            "KINETIC_ANALYSIS",
            "STATISTICAL_SUMMARY",
        ]
        actual_names = [member.name for member in DataOutputTypeEnum]
        for ctype in calc_types:
            assert ctype in actual_names

    def test_has_status_types(self) -> None:
        """Test that enum has status data types."""
        status_types = ["MACHINE_STATUS", "LIQUID_LEVEL", "ERROR_LOG"]
        actual_names = [member.name for member in DataOutputTypeEnum]
        for stype in status_types:
            assert stype in actual_names

    def test_all_members_have_unique_values(self) -> None:
        """Test that all members have unique values."""
        values = [member.value for member in DataOutputTypeEnum]
        assert len(values) == len(set(values))


class TestSpatialContextEnum:

    """Tests for SpatialContextEnum."""

    def test_is_enum(self) -> None:
        """Test that SpatialContextEnum is an enum."""
        assert issubclass(SpatialContextEnum, enum.Enum)

    def test_has_well_specific(self) -> None:
        """Test that enum has WELL_SPECIFIC."""
        assert SpatialContextEnum.WELL_SPECIFIC.value == "well_specific"

    def test_has_plate_level(self) -> None:
        """Test that enum has PLATE_LEVEL."""
        assert SpatialContextEnum.PLATE_LEVEL.value == "plate_level"

    def test_has_machine_level(self) -> None:
        """Test that enum has MACHINE_LEVEL."""
        assert SpatialContextEnum.MACHINE_LEVEL.value == "machine_level"

    def test_has_deck_position(self) -> None:
        """Test that enum has DECK_POSITION."""
        assert SpatialContextEnum.DECK_POSITION.value == "deck_position"

    def test_has_global(self) -> None:
        """Test that enum has GLOBAL."""
        assert SpatialContextEnum.GLOBAL.value == "global"

    def test_member_count(self) -> None:
        """Test that enum has exactly 5 members."""
        assert len(SpatialContextEnum) == 5

    def test_spatial_hierarchy(self) -> None:
        """Test that enum represents spatial hierarchy."""
        # From most specific to most general
        hierarchy = [
            SpatialContextEnum.WELL_SPECIFIC,
            SpatialContextEnum.PLATE_LEVEL,
            SpatialContextEnum.DECK_POSITION,
            SpatialContextEnum.MACHINE_LEVEL,
            SpatialContextEnum.GLOBAL,
        ]
        # Verify all exist
        for context in hierarchy:
            assert context in SpatialContextEnum


class TestOutputEnumsIntegration:

    """Integration tests for output enums."""

    def test_enums_are_independent(self) -> None:
        """Test that output type and spatial context are independent."""
        type_names = {member.name for member in DataOutputTypeEnum}
        context_names = {member.name for member in SpatialContextEnum}
        assert len(type_names.intersection(context_names)) == 0

    def test_can_combine_type_and_context(self) -> None:
        """Test that output type and spatial context can be combined."""
        output_data = {
            "type": DataOutputTypeEnum.ABSORBANCE_READING,
            "context": SpatialContextEnum.WELL_SPECIFIC,
        }
        assert output_data["type"] == DataOutputTypeEnum.ABSORBANCE_READING
        assert output_data["context"] == SpatialContextEnum.WELL_SPECIFIC

    def test_type_and_context_pairing_makes_sense(self) -> None:
        """Test logical pairing of types and contexts."""
        # Well-specific data should pair with measurement types
        well_data = {
            "type": DataOutputTypeEnum.ABSORBANCE_READING,
            "context": SpatialContextEnum.WELL_SPECIFIC,
        }
        assert well_data["type"] in DataOutputTypeEnum
        assert well_data["context"] in SpatialContextEnum

        # Plate-level data should pair with image types
        plate_data = {
            "type": DataOutputTypeEnum.PLATE_IMAGE,
            "context": SpatialContextEnum.PLATE_LEVEL,
        }
        assert plate_data["type"] in DataOutputTypeEnum
        assert plate_data["context"] in SpatialContextEnum
