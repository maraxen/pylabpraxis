from typing import IO, Any


class RealFileSystem:
  """A real file system implementation."""

  def open(self, file: str, mode: str = "r", encoding: str | None = None) -> IO[Any]:
    """Open a file and return a file object."""
    return open(file, mode, encoding=encoding)
