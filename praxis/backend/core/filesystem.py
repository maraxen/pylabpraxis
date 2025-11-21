"""Filesystem interface for Praxis."""

from pathlib import Path
from typing import IO, Any, overload


class FileSystem:

  """A simple filesystem interface using pathlib for modern path operations."""

  @overload
  def open(
    self,
    file: str | bytes | int,
    mode: str = "r",
    buffering: int = -1,
    encoding: str | None = None,
    errors: str | None = None,
    newline: str | None = None,
    closefd: bool = True,
    opener: Any | None = None,
  ) -> IO[Any]: ...

  def open(self, *args: Any, **kwargs: Any) -> IO[Any]:
    """Open a file and return a file object."""
    return open(*args, **kwargs)

  def exists(self, path: str | bytes | int) -> bool:
    """Return True if path refers to an existing path."""
    return Path(path).exists()

  def isdir(self, path: str | bytes | int) -> bool:
    """Return True if path is an existing directory."""
    return Path(path).is_dir()

  def listdir(self, path: str | bytes | int | None = None) -> list[str]:
    """Return a list of the entries in the directory given by path."""
    if path is None:
      path = "."
    return [item.name for item in Path(path).iterdir()]

  def mkdir(self, path: str | bytes | int, mode: int = 0o777) -> None:
    """Create a directory named path with numeric mode mode."""
    Path(path).mkdir(mode=mode)

  def makedirs(self, path: str | bytes | int, mode: int = 0o777, exist_ok: bool = False) -> None:
    """Create a directory named path with numeric mode mode."""
    Path(path).mkdir(mode=mode, parents=True, exist_ok=exist_ok)

  def remove(self, path: str | bytes | int) -> None:
    """Remove (delete) the file path."""
    Path(path).unlink()

  def rmdir(self, path: str | bytes | int) -> None:
    """Remove (delete) the directory path."""
    Path(path).rmdir()
