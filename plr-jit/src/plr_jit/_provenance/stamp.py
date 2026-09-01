"""plr_jit._provenance.stamp: process-memoized SurveyStamp (spec 260901 §2.2).

Supersedes plr_survey_common.plr_version_stamp()'s {git_sha, git_dirty: bool}
pair with a full GitState for both the PLR submodule and the analyzer's own
repo, plus the installed pylabrobot package version if importable.

Normative -- memoization: survey_stamp() is memoized at most once per
process (a module-level cache populated on first call); repeated calls
within the same process return the cached SurveyStamp rather than
re-invoking capture_git_state. A dirty tree's tree-OID computation costs
~8 subprocesses (git_state._compute_dirty_content_id), so a SurveyStamp is
~16 subprocesses total (plr + praxis) if recomputed per call -- the
memoization is what keeps "every emitted event carries the full
SurveyStamp" (spec §4.1) affordable. emit() never shells out; it only
serializes whatever SurveyStamp object it is handed.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from plr_jit._provenance.git_state import GitState, capture_git_state

# plr-jit/src/plr_jit/_provenance/stamp.py -> repo root is four parents up.
_REPO_ROOT = Path(__file__).resolve().parents[4]
_PLR_SUBMODULE = _REPO_ROOT / "external" / "pylabrobot"

SCHEMA_VERSION = 1


@dataclass(frozen=True, slots=True)
class SurveyStamp:
    """Provenance pin for one analyzer run or emitted event: which PLR tree,
    which analyzer tree, which installed pylabrobot version (spec 260901
    §2.2)."""

    plr: GitState
    praxis: GitState
    pylabrobot_version: str | None
    stamped_at: str
    schema_version: int = SCHEMA_VERSION


_cache: SurveyStamp | None = None


def _pylabrobot_version() -> str | None:
    try:
        import pylabrobot
    except ImportError:
        return None
    return getattr(pylabrobot, "__version__", None)


def survey_stamp() -> SurveyStamp:
    """Return the process-memoized SurveyStamp, computing it on first call.

    See module docstring: memoized at most once per process. Callers that
    need a fresh capture (e.g. tests) must go through
    ``_reset_survey_stamp_cache_for_tests`` first; there is no public way to
    force recomputation, by design.
    """
    global _cache
    if _cache is not None:
        return _cache
    _cache = SurveyStamp(
        plr=capture_git_state(_PLR_SUBMODULE),
        praxis=capture_git_state(_REPO_ROOT),
        pylabrobot_version=_pylabrobot_version(),
        stamped_at=datetime.now(timezone.utc).isoformat(),
        schema_version=SCHEMA_VERSION,
    )
    return _cache


def _reset_survey_stamp_cache_for_tests() -> None:
    """Test-only: clear the memoization cache so the next survey_stamp()
    call recomputes. Not part of the public surface."""
    global _cache
    _cache = None
