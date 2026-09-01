"""plr_jit.check._supported_tools: the analyzed-surface boundary (spec
260901 §6.2's D1 note, "adjacent fix, same location").

**Single in-package definition (consolidated).** T6 originally placed a
mirror of this set at ``plr_jit.derive`` (module-level, next to the
transitive-closure machinery it feeds). T8 needs the SAME set inside
``check/`` for the ``unsupported_tool`` reason (§3.3) -- and ``check/`` is
stdlib-only, forbidden from importing ``praxis``/``verify`` (§1.3), so it
cannot reach ``training.verify.dispatcher.SUPPORTED_TOOLS`` directly. Rather
than typing a THIRD copy (upstream + derive + check), this module is now the
single in-package source of truth: ``plr_jit.derive`` imports and re-exports
it from here (``from plr_jit.check._supported_tools import SUPPORTED_TOOLS``)
so ``from plr_jit.derive import SUPPORTED_TOOLS`` keeps resolving to the
exact same object, and exactly ONE live cross-package drift test
(``tests/test_check_graph.py::test_supported_tools_match_upstream``) checks
it against ``training.verify.dispatcher.SUPPORTED_TOOLS`` -- not two.

Mirrors ``training/verify/dispatcher.py:37-41``'s ``SUPPORTED_TOOLS``
verbatim (10-tool frozenset). Copied, not imported -- same pattern §4.1 uses
for ``FAILURE_CATEGORIES`` (promoted from ``training/verify/failure_taxonomy.
py`` rather than imported), for the same reason: the import-boundary test
(§1.3) forbids ``src/plr_jit/`` from reaching into ``training``/``verify`` at
all, poisoned-import or not.
"""

from __future__ import annotations

#: Mirrors training/verify/dispatcher.py:37-41's SUPPORTED_TOOLS verbatim.
#: Kept honest by test_check_graph.py::test_supported_tools_match_upstream,
#: a live cross-package drift test (same pattern as
#: telemetry.FAILURE_CATEGORIES's test_categories_match_upstream, §4.2).
SUPPORTED_TOOLS: frozenset[str] = frozenset(
    {
        "pick_up_tips",
        "drop_tips",
        "discard_tips",
        "aspirate",
        "dispense",
        "transfer",
        "stamp",
        "move_resource",
        "move_plate",
        "move_lid",
    }
)

__all__ = ["SUPPORTED_TOOLS"]
