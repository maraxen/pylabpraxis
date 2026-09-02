"""plr-preflight: Preflight static validation of PyLabRobot execution graphs: SAFE / WILL_FAIL / UNKNOWN before anything runs.

Round-4 remediation (M6): the package used to export nothing
(`__all__ = []`), so `import plr_preflight; plr_preflight.check_graph(...)` failed even
though `plr_preflight.check.check_graph` worked fine -- AC-1.1's "import plr_preflight
exits 0" only ever exercised bare importability, never that the package's
round-1 entry point and record types are actually reachable from the
top-level package name. `check/` is stdlib-only (no libcst/pylabrobot/
pydantic -- see `plr_preflight.check`'s module docstring) and `verdict.py` is
stdlib-only too, so re-exporting both here does not widen the import
boundary `tests/test_import_boundary.py` enforces.
"""

from plr_preflight.check import check_graph
from plr_preflight.verdict import AnalysisReport, Verdict

__all__ = ["check_graph", "AnalysisReport", "Verdict"]
