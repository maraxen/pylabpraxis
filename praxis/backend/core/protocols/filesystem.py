from typing import IO, Any, Protocol, runtime_checkable


@runtime_checkable
class IFileSystem(Protocol):
  """A protocol for file system operations."""

  def open(self, file: str, mode: str = "r", encoding: str | None = None) -> IO[Any]:
    """Open a file and return a file object."""
    ...
