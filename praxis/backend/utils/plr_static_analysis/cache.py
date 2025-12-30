"""Cache layer for PLR static analysis results."""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path

from praxis.backend.utils.plr_static_analysis.models import DiscoveredClass

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
  """A cache entry for parsed PLR source files."""

  file_hash: str
  mtime: float
  classes: list[dict]


class ParseCache:
  """Cache for parsed PLR source files.

  Uses both memory and disk caching for performance.
  Cache is invalidated when file content changes (hash) or modification time changes.

  """

  def __init__(self, cache_dir: Path | None = None) -> None:
    """Initialize the cache.

    Args:
      cache_dir: Directory to store disk cache. Defaults to ~/.cache/praxis/plr_parse

    """
    self.cache_dir = cache_dir or Path.home() / ".cache" / "praxis" / "plr_parse"
    self.cache_dir.mkdir(parents=True, exist_ok=True)
    self._memory_cache: dict[str, CacheEntry] = {}

  def get(self, file_path: Path) -> list[DiscoveredClass] | None:
    """Get cached parse results if valid.

    Args:
      file_path: Path to the source file.

    Returns:
      List of discovered classes if cache hit, None if cache miss.

    """
    cache_key = self._cache_key(file_path)

    # Check memory cache first
    if cache_key in self._memory_cache:
      entry = self._memory_cache[cache_key]
      if self._is_valid(file_path, entry):
        return self._deserialize_classes(entry.classes)

    # Check disk cache
    cache_file = self.cache_dir / f"{cache_key}.json"
    if cache_file.exists():
      try:
        data = json.loads(cache_file.read_text())
        entry = CacheEntry(**data)
        if self._is_valid(file_path, entry):
          self._memory_cache[cache_key] = entry
          return self._deserialize_classes(entry.classes)
      except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.debug("Cache read error for %s: %s", file_path, e)

    return None

  def set(self, file_path: Path, classes: list[DiscoveredClass]) -> None:
    """Cache parse results.

    Args:
      file_path: Path to the source file.
      classes: List of discovered classes to cache.

    """
    cache_key = self._cache_key(file_path)
    try:
      entry = CacheEntry(
        file_hash=self._file_hash(file_path),
        mtime=file_path.stat().st_mtime,
        classes=[c.model_dump() for c in classes],
      )

      self._memory_cache[cache_key] = entry

      cache_file = self.cache_dir / f"{cache_key}.json"
      cache_file.write_text(json.dumps(asdict(entry)))
    except (OSError, TypeError) as e:
      logger.debug("Cache write error for %s: %s", file_path, e)

  def invalidate(self, file_path: Path) -> None:
    """Invalidate cache for a specific file.

    Args:
      file_path: Path to the source file.

    """
    cache_key = self._cache_key(file_path)
    self._memory_cache.pop(cache_key, None)
    cache_file = self.cache_dir / f"{cache_key}.json"
    if cache_file.exists():
      cache_file.unlink()

  def clear(self) -> None:
    """Clear all cache entries."""
    self._memory_cache.clear()
    for cache_file in self.cache_dir.glob("*.json"):
      cache_file.unlink()

  def _cache_key(self, file_path: Path) -> str:
    """Generate cache key from file path.

    Args:
      file_path: Path to the source file.

    Returns:
      MD5 hash of the file path.

    """
    return hashlib.md5(str(file_path.resolve()).encode()).hexdigest()

  def _file_hash(self, file_path: Path) -> str:
    """Compute hash of file contents.

    Args:
      file_path: Path to the source file.

    Returns:
      MD5 hash of the file contents.

    """
    return hashlib.md5(file_path.read_bytes()).hexdigest()

  def _is_valid(self, file_path: Path, entry: CacheEntry) -> bool:
    """Check if cache entry is still valid.

    Args:
      file_path: Path to the source file.
      entry: The cache entry to validate.

    Returns:
      True if cache entry is valid.

    """
    try:
      if not file_path.exists():
        return False
      # Quick check: modification time
      if file_path.stat().st_mtime != entry.mtime:
        return False
      # Deep check: file hash (only if mtime matches but we want extra safety)
      return self._file_hash(file_path) == entry.file_hash
    except OSError:
      return False

  def _deserialize_classes(self, classes: list[dict]) -> list[DiscoveredClass]:
    """Deserialize cached class data.

    Args:
      classes: List of class dictionaries.

    Returns:
      List of DiscoveredClass objects.

    """
    return [DiscoveredClass(**c) for c in classes]
