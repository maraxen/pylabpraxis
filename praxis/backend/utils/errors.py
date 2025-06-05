"""Custom exceptions and logging utility for Praxis backend."""


class PraxisError(Exception):
  """Base exception for all custom Praxis backend errors.

  Attributes:
    message (str): The error message.

  """

  def __init__(self, message: str):
    """Initialize a new instance of the PraxisError.

    Args:
      message (str): The detailed error message.

    """
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    """Return the string representation of the error."""
    return f"{self.message}"


class OrchestratorError(Exception):
  """Exception raised for errors in the orchestrator service.

  Attributes:
    message (str): The error message.

  """

  def __init__(self, message: str):
    """Initialize a new instance of the OrchestratorError.

    Args:
      message (str): The detailed error message.

    """
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    """Return the string representation of the error."""
    return f"{self.message}"


class DataError(Exception):
  """Exception raised for errors during data operations (e.g., database interactions).

  Attributes:
    message (str): The error message.

  """

  def __init__(self, message: str):
    """Initialize a new instance of the DataError.

    Args:
      message (str): The detailed error message.

    """
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    """Return the string representation of the error."""
    return f"{self.message}"


class ModelError(Exception):
  """Exception raised for data models errors (e.g., validation, serialization).

  Attributes:
    message (str): The error message.

  """

  def __init__(self, message: str):
    """Initialize a new instance of the ModelError.

    Args:
      message (str): The detailed error message.

    """
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    """Return the string representation of the error."""
    return f"{self.message}"


class AssetAcquisitionError(RuntimeError):
  """Exception raised when there is an issue acquiring or assigning assets.

  Attributes:
    message (str): The error message.

  """

  def __init__(self, message: str):
    """Initialize a new instance of the AssetAcquisitionError.

    Args:
      message (str): The detailed error message.

    """
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    """Return the string representation of the error."""
    return f"{self.message}"


class AssetReleaseError(RuntimeError):
  """Exception raised when there is an issue releasing or returning assets.

  Attributes:
    message (str): The error message.

  """

  def __init__(self, message: str):
    """Initialize a new instance of the AssetReleaseError.

    Args:
      message (str): The detailed error message.

    """
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    """Return the string representation of the error."""
    return f"{self.message}"


class ProtocolCancelledError(Exception):
  """Exception raised when a protocol run is explicitly cancelled.

  Attributes:
    message (str): The cancellation message.

  """

  def __init__(self, message: str = "Protocol run was cancelled."):
    """Initialize a new instance of the ProtocolCancelledError.

    Args:
      message (str): The detailed cancellation message.
        Defaults to "Protocol run was cancelled.".

    """
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    """Return the string representation of the error."""
    return f"{self.message}"


class WorkcellRuntimeError(Exception):
  """Exception raised for errors specific to the WorkcellRuntime.

  Attributes:
    message (str): The error message.

  """

  def __init__(self, message: str):
    """Initialize a new instance of the WorkcellRuntimeError.

    Args:
      message (str): The detailed error message.

    """
    self.message = message
    super().__init__(self.message)

  def __str__(self) -> str:
    """Return the string representation of the error."""
    return f"{self.message}"
