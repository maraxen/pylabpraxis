"""Spec 260901 §7.5 / T6 (backlog #4829): the seven `plr_jit.derive` tests
named in §7.5, plus one extra live cross-package drift test for
`SUPPORTED_TOOLS` (mirroring `test_telemetry.py`'s
`test_categories_match_upstream` pattern, per this task's own instructions --
`SUPPORTED_TOOLS` is a maintained mirror of
`training/verify/dispatcher.py:37`, not an import, so it needs the same kind
of drift guard `FAILURE_CATEGORIES` already has).

AC-7.1: all seven §7.5 tests pass. Uses the real survey JSON already on disk
(`training/verify/data/plr_preconditions.json`, §7.1) and the real vendored
PLR source under `external/pylabrobot` for the tests that need real data
(the aspirate/_check_containers regression, the guard-site test); synthetic
in-memory indexes for the tests that are about the closure MECHANIC itself
(cycle safety, unresolved-call gaps) rather than about PLR's actual content.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from plr_jit._provenance import SurveyStamp, survey_stamp
from plr_jit.derive import (
    SUPPORTED_TOOLS,
    SurveyFinding,
    SurveyRecord,
    build_gap_ledger,
    build_index,
    default_plr_pkg_root,
    derive_contract,
    load_survey,
    resolve,
    scan_dropped_receiver_calls,
    scan_dropped_receiver_calls_in_source,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SURVEY_JSON = REPO_ROOT / "training" / "verify" / "data" / "plr_preconditions.json"


# ---------------------------------------------------------------------------
# Shared fixtures: real survey data, loaded once per module.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def survey_records() -> list[SurveyRecord]:
    return load_survey(SURVEY_JSON)


@pytest.fixture(scope="module")
def survey_index(survey_records: list[SurveyRecord]) -> dict[tuple[str, str], SurveyRecord]:
    return build_index(survey_records)


# ---------------------------------------------------------------------------
# test_aspirate_closure_reaches_check_containers -- the load-bearing
# regression (§7.5). Must fail against an own-body-only derivation.
# ---------------------------------------------------------------------------


def test_aspirate_closure_reaches_check_containers(
    survey_index: dict[tuple[str, str], SurveyRecord],
) -> None:
    entry = survey_index[("pylabrobot.liquid_handling.liquid_handler", "LiquidHandler.aspirate")]

    # First, prove the regression is genuinely load-bearing: aspirate's OWN
    # body (depth 0 only, i.e. no closure expansion at all) has zero guards
    # whose site is _check_containers -- own-body findings don't mention it.
    own_body_sites = {f.lineno for f in entry.findings}
    check_containers = survey_index[
        ("pylabrobot.liquid_handling.liquid_handler", "LiquidHandler._check_containers")
    ]
    check_containers_linenos = {f.lineno for f in check_containers.findings}
    assert not (own_body_sites & check_containers_linenos), (
        "fixture assumption violated: aspirate's own body already contains "
        "a finding at one of _check_containers's line numbers, which would "
        "make this regression vacuous"
    )
    assert "_check_containers" in entry.delegates_to  # sanity: it IS a delegate

    # Now derive the full closure and assert it DOES reach _check_containers
    # at depth > 0 -- this is the property that fails if delegate expansion
    # is disabled (own-body-only derivation), which is the whole point.
    contract = derive_contract(entry.module, entry.qualname, survey_index)
    matching = [
        g
        for g in contract.guards
        if g.site.qualname == "LiquidHandler._check_containers" and g.depth > 0
    ]
    assert matching, (
        "derive_contract(LiquidHandler.aspirate) closure did not reach "
        "LiquidHandler._check_containers at depth > 0 -- this is exactly "
        "the own-body-only failure mode §7.2 exists to prevent"
    )
    # And the guard's site really is _check_containers's own recorded line,
    # not aspirate's.
    assert matching[0].site.lineno in check_containers_linenos


# ---------------------------------------------------------------------------
# test_closure_terminates_on_cycle
# ---------------------------------------------------------------------------


def _synthetic_record(
    qualname: str,
    *,
    class_name: str | None,
    module: str = "synthetic.module",
    delegates_to: tuple[str, ...] = (),
    unresolved_calls: tuple[str, ...] = (),
    findings: tuple[SurveyFinding, ...] = (),
) -> SurveyRecord:
    return SurveyRecord(
        qualname=qualname,
        class_name=class_name,
        module=module,
        file="synthetic/module.py",
        lineno=1,
        params=(),
        findings=findings,
        delegates_to=delegates_to,
        unresolved_calls=unresolved_calls,
    )


def _synthetic_finding(lineno: int, kind: str = "raise_guard") -> SurveyFinding:
    return SurveyFinding(
        kind=kind,
        condition="x > 0",
        raises="ValueError" if kind == "raise_guard" else None,
        scope_trail=(),
        mentions_params=("x",),
        lineno=lineno,
    )


@pytest.mark.timeout(5)
def test_closure_terminates_on_cycle() -> None:
    """Synthetic A -> B -> A index (§7.5). Cycle-safety is checked via
    `seen` before expansion (trap 2); a naive recursion would hang. Run
    under pytest-timeout so a regression fails loudly instead of hanging
    the suite."""
    rec_a = _synthetic_record(
        "A", class_name=None, delegates_to=("B",), findings=(_synthetic_finding(10),)
    )
    rec_b = _synthetic_record(
        "B", class_name=None, delegates_to=("A",), findings=(_synthetic_finding(20),)
    )
    index = build_index([rec_a, rec_b])

    contract = derive_contract("synthetic.module", "A", index)

    # Terminates (the @pytest.mark.timeout above is the primary guard) and
    # visits each node's findings exactly once -- one guard from A (depth 0)
    # and one from B (depth 1), not an unbounded/duplicated set.
    assert len(contract.guards) == 2
    depths = sorted(g.depth for g in contract.guards)
    assert depths == [0, 1]
    linenos = sorted(g.site.lineno for g in contract.guards)
    assert linenos == [10, 20]


# ---------------------------------------------------------------------------
# test_unresolved_calls_become_gaps
# ---------------------------------------------------------------------------


def test_unresolved_calls_become_gaps() -> None:
    rec = _synthetic_record(
        "Widget.frobnicate",
        class_name="Widget",
        unresolved_calls=("send_command",),
    )
    index = build_index([rec])

    contract = derive_contract("synthetic.module", "Widget.frobnicate", index)

    assert contract.gaps == (("unresolved_delegate", "send_command"),)


# ---------------------------------------------------------------------------
# test_guard_sites_point_at_defining_file -- respecified per D5: a universal
# over the closure, not gated on cross-file (which is structurally
# unsatisfiable under round-1 resolve()).
# ---------------------------------------------------------------------------


def test_guard_sites_point_at_defining_file(
    survey_index: dict[tuple[str, str], SurveyRecord],
) -> None:
    entry_module = "pylabrobot.liquid_handling.liquid_handler"
    entry_qualname = "LiquidHandler.aspirate"
    contract = derive_contract(entry_module, entry_qualname, survey_index)

    depth_gt_0 = [g for g in contract.guards if g.depth > 0]
    assert depth_gt_0, "fixture assumption violated: expected >=1 depth>0 guard"

    for guard in depth_gt_0:
        assert guard.site.qualname != entry_qualname, (
            f"guard at depth {guard.depth} claims site.qualname == the entry "
            f"point's own qualname -- provenance is not preserved"
        )
        defining_rec = survey_index[(entry_module, guard.site.qualname)]
        defining_linenos = {f.lineno for f in defining_rec.findings}
        assert guard.site.lineno in defining_linenos, (
            f"guard's site.lineno={guard.site.lineno} does not match any "
            f"finding recorded on {guard.site.qualname} -- site does not "
            f"point at the DEFINING site"
        )


# ---------------------------------------------------------------------------
# test_ledger_totals_are_internally_consistent
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def real_stamp() -> SurveyStamp:
    return survey_stamp()


@pytest.fixture(scope="module")
def dropped_receiver_counts():
    return scan_dropped_receiver_calls(default_plr_pkg_root())


@pytest.fixture(scope="module")
def gap_ledger(
    survey_index: dict[tuple[str, str], SurveyRecord],
    survey_records: list[SurveyRecord],
    dropped_receiver_counts,
    real_stamp: SurveyStamp,
) -> dict:
    return build_gap_ledger(
        survey_index,
        survey_records,
        dropped_receiver_counts=dropped_receiver_counts,
        stamp=real_stamp,
    )


def test_ledger_totals_are_internally_consistent(
    gap_ledger: dict,
    survey_index: dict[tuple[str, str], SurveyRecord],
    survey_records: list[SurveyRecord],
    real_stamp: SurveyStamp,
) -> None:
    totals = gap_ledger["totals"]
    assert (
        totals["methods_with_no_recorded_gap"] + totals["methods_with_gaps"]
        == totals["methods_attempted"]
    )

    # sum(by_reason.values()) == total gap count -- recomputed independently
    # (re-running the closures here, not trusting the ledger's own running
    # total) so this is a real cross-check, not a tautology.
    finding_bearing = [rec for rec in survey_records if rec.findings]
    recomputed_gap_count = 0
    for rec in finding_bearing:
        contract = derive_contract(rec.module, rec.qualname, survey_index, stamp=real_stamp)
        recomputed_gap_count += len(contract.gaps)

    assert sum(gap_ledger["by_reason"].values()) == recomputed_gap_count
    assert totals["methods_attempted"] == len(finding_bearing)


# ---------------------------------------------------------------------------
# test_ledger_is_stamped
# ---------------------------------------------------------------------------


def test_ledger_is_stamped(gap_ledger: dict) -> None:
    plr_hash = gap_ledger["stamp"]["plr"]["hash"]
    assert len(plr_hash) == 40
    assert all(c in "0123456789abcdef" for c in plr_hash)


# ---------------------------------------------------------------------------
# test_dropped_receiver_calls_are_counted -- new, T6, corrected predicate D3.
# ---------------------------------------------------------------------------


def test_dropped_receiver_calls_are_counted() -> None:
    subscript_receiver_source = """
def pick_up_tips(self, channel):
    tip = self.head[channel].get_tip()
    return tip
"""
    bare_name_receiver_source = """
def use_resource(self, resource):
    item = resource.get_item()
    return item
"""
    only_self_and_bare_source = """
def clean(self):
    self.foo()
    bare_call()
    return None
"""

    subscript_counts = scan_dropped_receiver_calls_in_source(subscript_receiver_source)
    assert subscript_counts.total >= 1

    bare_name_counts = scan_dropped_receiver_calls_in_source(bare_name_receiver_source)
    assert bare_name_counts.total >= 1

    clean_counts = scan_dropped_receiver_calls_in_source(only_self_and_bare_source)
    assert clean_counts.total == 0
    assert clean_counts.validation_looking == 0

    for counts in (subscript_counts, bare_name_counts, clean_counts):
        assert counts.validation_looking <= counts.total


# ---------------------------------------------------------------------------
# Extra, task-mandated: SUPPORTED_TOOLS live cross-package drift test
# (mirrors test_telemetry.py's test_categories_match_upstream, §4.2 pattern).
# ---------------------------------------------------------------------------


def test_supported_tools_matches_upstream_dispatcher() -> None:
    """`plr_jit.derive.SUPPORTED_TOOLS` must be the SAME set as
    `verify.dispatcher.SUPPORTED_TOOLS` today -- a live drift test, not a
    copied constant re-asserted against itself. `src/plr_jit` cannot import
    `verify` (import-boundary test forbids it); this test file can, with
    both `<repo_root>/training` and `<repo_root>/coxswain/src` on sys.path
    first (verify/__init__.py eagerly imports verify.checks, which imports
    coxswain.plr.intent_record)."""
    training_path = str(REPO_ROOT / "training")
    coxswain_src_path = str(REPO_ROOT / "coxswain" / "src")
    for path in (coxswain_src_path, training_path):
        if path not in sys.path:
            sys.path.insert(0, path)

    try:
        import verify.dispatcher as upstream_dispatcher
    except ImportError as exc:
        pytest.skip(f"training/verify not importable: {exc}")
        return

    assert SUPPORTED_TOOLS == upstream_dispatcher.SUPPORTED_TOOLS, (
        f"plr_jit.derive.SUPPORTED_TOOLS {sorted(SUPPORTED_TOOLS)} != "
        f"verify.dispatcher.SUPPORTED_TOOLS {sorted(upstream_dispatcher.SUPPORTED_TOOLS)}"
    )
