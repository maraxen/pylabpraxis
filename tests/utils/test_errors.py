"""Tests for custom exception classes in utils/errors.py."""

import pytest

from praxis.backend.utils.errors import (
    AssetAcquisitionError,
    AssetReleaseError,
    DataError,
    ModelError,
    OrchestratorError,
    PraxisAPIError,
    PraxisError,
    ProtocolCancelledError,
    PylabRobotError,
    PyLabRobotGenericError,
    PyLabRobotVolumeError,
    WorkcellRuntimeError,
)


class TestPraxisError:

    """Tests for PraxisError base exception."""

    def test_can_raise_and_catch(self) -> None:
        """Test that PraxisError can be raised and caught."""
        with pytest.raises(PraxisError):
            raise PraxisError("Test error")

    def test_stores_message(self) -> None:
        """Test that error message is stored correctly."""
        error = PraxisError("Test message")
        assert error.message == "Test message"

    def test_str_representation(self) -> None:
        """Test string representation of the error."""
        error = PraxisError("Test message")
        assert str(error) == "Test message"

    def test_inherits_from_exception(self) -> None:
        """Test that PraxisError inherits from Exception."""
        error = PraxisError("Test")
        assert isinstance(error, Exception)


class TestOrchestratorError:

    """Tests for OrchestratorError exception."""

    def test_can_raise_and_catch(self) -> None:
        """Test that OrchestratorError can be raised and caught."""
        with pytest.raises(OrchestratorError):
            raise OrchestratorError("Orchestrator failed")

    def test_stores_message(self) -> None:
        """Test that error message is stored correctly."""
        error = OrchestratorError("Orchestrator failed")
        assert error.message == "Orchestrator failed"

    def test_str_representation(self) -> None:
        """Test string representation of the error."""
        error = OrchestratorError("Orchestrator failed")
        assert str(error) == "Orchestrator failed"

    def test_inherits_from_exception(self) -> None:
        """Test that OrchestratorError inherits from Exception."""
        error = OrchestratorError("Test")
        assert isinstance(error, Exception)


class TestDataError:

    """Tests for DataError exception."""

    def test_can_raise_and_catch(self) -> None:
        """Test that DataError can be raised and caught."""
        with pytest.raises(DataError):
            raise DataError("Database error")

    def test_stores_message(self) -> None:
        """Test that error message is stored correctly."""
        error = DataError("Database error")
        assert error.message == "Database error"

    def test_str_representation(self) -> None:
        """Test string representation of the error."""
        error = DataError("Database error")
        assert str(error) == "Database error"


class TestModelError:

    """Tests for ModelError exception."""

    def test_can_raise_and_catch(self) -> None:
        """Test that ModelError can be raised and caught."""
        with pytest.raises(ModelError):
            raise ModelError("Model validation failed")

    def test_stores_message(self) -> None:
        """Test that error message is stored correctly."""
        error = ModelError("Model validation failed")
        assert error.message == "Model validation failed"

    def test_str_representation(self) -> None:
        """Test string representation of the error."""
        error = ModelError("Model validation failed")
        assert str(error) == "Model validation failed"


class TestAssetAcquisitionError:

    """Tests for AssetAcquisitionError exception."""

    def test_can_raise_and_catch(self) -> None:
        """Test that AssetAcquisitionError can be raised and caught."""
        with pytest.raises(AssetAcquisitionError):
            raise AssetAcquisitionError("Cannot acquire asset")

    def test_stores_message(self) -> None:
        """Test that error message is stored correctly."""
        error = AssetAcquisitionError("Cannot acquire asset")
        assert error.message == "Cannot acquire asset"

    def test_str_representation(self) -> None:
        """Test string representation of the error."""
        error = AssetAcquisitionError("Cannot acquire asset")
        assert str(error) == "Cannot acquire asset"

    def test_inherits_from_runtime_error(self) -> None:
        """Test that AssetAcquisitionError inherits from RuntimeError."""
        error = AssetAcquisitionError("Test")
        assert isinstance(error, RuntimeError)


class TestAssetReleaseError:

    """Tests for AssetReleaseError exception."""

    def test_can_raise_and_catch(self) -> None:
        """Test that AssetReleaseError can be raised and caught."""
        with pytest.raises(AssetReleaseError):
            raise AssetReleaseError("Cannot release asset")

    def test_stores_message(self) -> None:
        """Test that error message is stored correctly."""
        error = AssetReleaseError("Cannot release asset")
        assert error.message == "Cannot release asset"

    def test_str_representation(self) -> None:
        """Test string representation of the error."""
        error = AssetReleaseError("Cannot release asset")
        assert str(error) == "Cannot release asset"

    def test_inherits_from_runtime_error(self) -> None:
        """Test that AssetReleaseError inherits from RuntimeError."""
        error = AssetReleaseError("Test")
        assert isinstance(error, RuntimeError)


class TestProtocolCancelledError:

    """Tests for ProtocolCancelledError exception."""

    def test_can_raise_and_catch(self) -> None:
        """Test that ProtocolCancelledError can be raised and caught."""
        with pytest.raises(ProtocolCancelledError):
            raise ProtocolCancelledError()

    def test_default_message(self) -> None:
        """Test that default cancellation message is set."""
        error = ProtocolCancelledError()
        assert error.message == "Protocol run was cancelled."

    def test_custom_message(self) -> None:
        """Test that custom message can be provided."""
        error = ProtocolCancelledError("Custom cancellation message")
        assert error.message == "Custom cancellation message"

    def test_str_representation(self) -> None:
        """Test string representation of the error."""
        error = ProtocolCancelledError("Protocol cancelled by user")
        assert str(error) == "Protocol cancelled by user"


class TestWorkcellRuntimeError:

    """Tests for WorkcellRuntimeError exception."""

    def test_can_raise_and_catch(self) -> None:
        """Test that WorkcellRuntimeError can be raised and caught."""
        with pytest.raises(WorkcellRuntimeError):
            raise WorkcellRuntimeError("Workcell runtime failed")

    def test_stores_message(self) -> None:
        """Test that error message is stored correctly."""
        error = WorkcellRuntimeError("Workcell runtime failed")
        assert error.message == "Workcell runtime failed"

    def test_str_representation(self) -> None:
        """Test string representation of the error."""
        error = WorkcellRuntimeError("Workcell runtime failed")
        assert str(error) == "Workcell runtime failed"


class TestPylabRobotError:

    """Tests for PylabRobotError exception."""

    def test_can_raise_and_catch(self) -> None:
        """Test that PylabRobotError can be raised and caught."""
        with pytest.raises(PylabRobotError):
            raise PylabRobotError("PyLabRobot error")

    def test_stores_message(self) -> None:
        """Test that error message is stored correctly."""
        error = PylabRobotError("PyLabRobot error")
        assert error.message == "PyLabRobot error"

    def test_inherits_from_praxis_error(self) -> None:
        """Test that PylabRobotError inherits from PraxisError."""
        error = PylabRobotError("Test")
        assert isinstance(error, PraxisError)

    def test_stores_original_exception(self) -> None:
        """Test that original PyLabRobot exception is stored."""
        original = ValueError("Original error")
        error = PylabRobotError("Wrapped error", original_plr_exception=original)
        assert error.original_plr_exception is original

    def test_original_exception_defaults_to_none(self) -> None:
        """Test that original exception defaults to None."""
        error = PylabRobotError("Test")
        assert error.original_plr_exception is None


class TestPyLabRobotVolumeError:

    """Tests for PyLabRobotVolumeError exception."""

    def test_can_raise_and_catch(self) -> None:
        """Test that PyLabRobotVolumeError can be raised and caught."""
        with pytest.raises(PyLabRobotVolumeError):
            raise PyLabRobotVolumeError()

    def test_default_message(self) -> None:
        """Test that default message is set."""
        error = PyLabRobotVolumeError()
        assert error.message == "Too little liquid for transfer."

    def test_custom_message(self) -> None:
        """Test that custom message can be provided."""
        error = PyLabRobotVolumeError(message="Custom volume error")
        assert error.message == "Custom volume error"

    def test_inherits_from_pylabrobot_error(self) -> None:
        """Test that PyLabRobotVolumeError inherits from PylabRobotError."""
        error = PyLabRobotVolumeError()
        assert isinstance(error, PylabRobotError)

    def test_stores_details(self) -> None:
        """Test that details dictionary is stored."""
        details = {"well": "A1", "required": 100, "available": 50}
        error = PyLabRobotVolumeError(details=details)
        assert error.details == details

    def test_details_defaults_to_empty_dict(self) -> None:
        """Test that details defaults to empty dictionary."""
        error = PyLabRobotVolumeError()
        assert error.details == {}

    def test_stores_original_exception(self) -> None:
        """Test that original PyLabRobot exception is stored."""
        original = Exception("Too little liquid")
        error = PyLabRobotVolumeError(original_plr_exception=original)
        assert error.original_plr_exception is original


class TestPyLabRobotGenericError:

    """Tests for PyLabRobotGenericError exception."""

    def test_can_raise_and_catch(self) -> None:
        """Test that PyLabRobotGenericError can be raised and caught."""
        with pytest.raises(PyLabRobotGenericError):
            raise PyLabRobotGenericError()

    def test_default_message(self) -> None:
        """Test that default message is set."""
        error = PyLabRobotGenericError()
        assert error.message == "A PyLabRobot operation failed."

    def test_custom_message(self) -> None:
        """Test that custom message can be provided."""
        error = PyLabRobotGenericError(message="Custom PLR error")
        assert error.message == "Custom PLR error"

    def test_inherits_from_pylabrobot_error(self) -> None:
        """Test that PyLabRobotGenericError inherits from PylabRobotError."""
        error = PyLabRobotGenericError()
        assert isinstance(error, PylabRobotError)

    def test_stores_original_exception(self) -> None:
        """Test that original PyLabRobot exception is stored."""
        original = Exception("PLR failed")
        error = PyLabRobotGenericError(original_plr_exception=original)
        assert error.original_plr_exception is original


class TestPraxisAPIError:

    """Tests for PraxisAPIError exception."""

    def test_can_raise_and_catch(self) -> None:
        """Test that PraxisAPIError can be raised and caught."""
        with pytest.raises(PraxisAPIError):
            raise PraxisAPIError("API error")

    def test_stores_message(self) -> None:
        """Test that error message is stored correctly."""
        error = PraxisAPIError("API error")
        assert error.message == "API error"

    def test_inherits_from_praxis_error(self) -> None:
        """Test that PraxisAPIError inherits from PraxisError."""
        error = PraxisAPIError("Test")
        assert isinstance(error, PraxisError)

    def test_str_representation(self) -> None:
        """Test string representation (inherited from PraxisError)."""
        error = PraxisAPIError("API endpoint failed")
        assert str(error) == "API endpoint failed"


class TestExceptionHierarchy:

    """Tests for exception inheritance hierarchy."""

    def test_pylabrobot_errors_inherit_from_praxis_error(self) -> None:
        """Test that PyLabRobot errors inherit from PraxisError."""
        error1 = PylabRobotError("Test")
        error2 = PyLabRobotVolumeError()
        error3 = PyLabRobotGenericError()

        assert isinstance(error1, PraxisError)
        assert isinstance(error2, PraxisError)
        assert isinstance(error3, PraxisError)

    def test_volume_and_generic_inherit_from_pylabrobot_error(self) -> None:
        """Test that specific PLR errors inherit from PylabRobotError."""
        error1 = PyLabRobotVolumeError()
        error2 = PyLabRobotGenericError()

        assert isinstance(error1, PylabRobotError)
        assert isinstance(error2, PylabRobotError)

    def test_all_praxis_errors_inherit_from_exception(self) -> None:
        """Test that all Praxis errors inherit from base Exception."""
        errors = [
            PraxisError("test"),
            OrchestratorError("test"),
            DataError("test"),
            ModelError("test"),
            WorkcellRuntimeError("test"),
            PylabRobotError("test"),
            PyLabRobotVolumeError(),
            PyLabRobotGenericError(),
            PraxisAPIError("test"),
        ]

        for error in errors:
            assert isinstance(error, Exception)

    def test_asset_errors_inherit_from_runtime_error(self) -> None:
        """Test that asset-related errors inherit from RuntimeError."""
        error1 = AssetAcquisitionError("test")
        error2 = AssetReleaseError("test")

        assert isinstance(error1, RuntimeError)
        assert isinstance(error2, RuntimeError)
        assert isinstance(error1, Exception)
        assert isinstance(error2, Exception)
