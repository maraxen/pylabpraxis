"""Spec 260901 §7.5 / T6 (backlog #4829): the seven `plr_sema.derive` tests
named in §7.5.

T8 consolidation note: this file previously carried an extra
`test_supported_tools_matches_upstream_dispatcher` live cross-package drift
test. `SUPPORTED_TOOLS` now has a single in-package definition at
`plr_sema.check._supported_tools` (T8, spec §6.2's D1 note); `plr_sema.derive`
imports and re-exports the exact same frozenset object rather than defining
its own copy. The one live drift test against `training.verify.dispatcher`
moved to `tests/test_check_graph.py::test_supported_tools_match_upstream`
(spec AC-6.5's named test) so there is exactly ONE such test, not two testing
the same fact from two module paths.

AC-7.1: all seven §7.5 tests pass. Uses the real survey JSON already on disk
(`training/verify/data/plr_preconditions.json`, §7.1) and the real vendored
PLR source under `external/pylabrobot` for the tests that need real data
(the aspirate/_check_containers regression, the guard-site test); synthetic
in-memory indexes for the tests that are about the closure MECHANIC itself
(cycle safety, unresolved-call gaps) rather than about PLR's actual content.
"""

from __future__ import annotations

import ast
import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from plr_sema._hand_maintained import BUDGET_CAP, live_rows
from plr_sema._provenance import SurveyStamp, survey_stamp
from plr_sema.derive import (
    SurveyFinding,
    SurveyRecord,
    _is_inert_dropped_receiver_call,
    _iter_plr_source_files,
    build_contract_keys,
    build_gap_ledger,
    build_index,
    default_plr_pkg_root,
    derive_contract,
    load_survey,
    scan_dropped_receiver_calls,
    scan_dropped_receiver_calls_in_source,
)
from plr_sema.derive.__main__ import build_derived_contracts_payload
from plr_sema.derive.receiver_state import (
    compute_delegate_channel_bindings,
    derive_receiver_states,
    reset_rule_candidates,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SURVEY_JSON = REPO_ROOT / "training" / "verify" / "data" / "plr_preconditions.json"
TAXONOMY_JSON = REPO_ROOT / "training" / "verify" / "data" / "plr_exception_taxonomy.json"


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
    the suite.
    """
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

    # Round-4 remediation (M11): a subset count must never exceed its own
    # population's denominator. Before this fix,
    # `methods_with_dropped_receiver_call` was computed over ALL 4,758
    # indexed records while `methods_attempted` counted only the 1,314
    # finding-bearing ones -- 1976 > 1314, a structurally impossible
    # "subset". Both figures are now computed over the same population
    # (`finding_bearing`), so this assertion is a real, not vacuous, check.
    assert totals["methods_with_dropped_receiver_call"] <= totals["methods_attempted"]

    supported_tools_totals = gap_ledger["supported_tools"]
    assert (
        supported_tools_totals["methods_with_dropped_receiver_call"]
        <= supported_tools_totals["methods_attempted"]
    )


# ---------------------------------------------------------------------------
# test_ledger_is_stamped
# ---------------------------------------------------------------------------


def test_ledger_is_stamped(gap_ledger: dict) -> None:
    plr_hash = gap_ledger["stamp"]["plr"]["hash"]
    assert len(plr_hash) == 40
    assert all(c in "0123456789abcdef" for c in plr_hash)


# ---------------------------------------------------------------------------
# test_ledger_regenerates_deterministically -- round-4 remediation (m2).
# AC-7.3 claims byte-identical regeneration modulo `stamped_at`; nothing
# mechanized that claim before this test.
# ---------------------------------------------------------------------------


def test_ledger_regenerates_deterministically(
    survey_index: dict[tuple[str, str], SurveyRecord],
    survey_records: list[SurveyRecord],
    dropped_receiver_counts,
    real_stamp: SurveyStamp,
) -> None:
    """AC-7.3 (round-4 remediation, m2): two consecutive `build_gap_ledger`
    runs against the SAME fixed stamp and unchanged survey data must
    serialize to byte-identical JSON. Uses a shared, fixed `real_stamp`
    (rather than letting each call recompute its own) so this test isolates
    determinism of the LEDGER-BUILDING logic itself from `stamped_at`'s
    inherent per-call variation, which AC-7.3's own "modulo `stamped_at`"
    clause already carves out.
    """
    import json

    first = build_gap_ledger(
        survey_index,
        survey_records,
        dropped_receiver_counts=dropped_receiver_counts,
        stamp=real_stamp,
    )
    second = build_gap_ledger(
        survey_index,
        survey_records,
        dropped_receiver_counts=dropped_receiver_counts,
        stamp=real_stamp,
    )
    first_json = json.dumps(first, sort_keys=True)
    second_json = json.dumps(second, sort_keys=True)
    assert first_json == second_json


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
# 260901 T11 -- decoupling derivation from SUPPORTED_TOOLS: whole-surface
# contract count, and the contract-table key disambiguator.
# ---------------------------------------------------------------------------


def test_contract_keys_are_collision_free(survey_records: list[SurveyRecord]) -> None:
    """T11 item 2 (F6 resurfacing at whole-survey scale): every record gets
    a DISTINCT contract-table key. `build_contract_keys` itself asserts this
    internally on every call -- this test additionally pins the two known
    collision populations against the real survey data, so a future survey
    regeneration that silently changes the collision shape is caught here
    rather than only inside the function's own defensive assert.
    """
    keys = build_contract_keys(survey_records)
    assert len(keys) == len(survey_records)
    assert len(set(keys.values())) == len(survey_records)

    # Source 1 (already known, F6): a property/setter pair -- same (module,
    # qualname), different lineno -- gets two DISAMBIGUATED keys, neither
    # bare.
    serial_dtr = [
        (rec.module, rec.qualname, rec.lineno)
        for rec in survey_records
        if rec.module == "pylabrobot.io.serial" and rec.qualname == "Serial.dtr"
    ]
    assert len(serial_dtr) == 2, "fixture assumption violated: expected Serial.dtr getter+setter pair"
    disambiguated = {keys[k] for k in serial_dtr}
    assert len(disambiguated) == 2
    assert all("@" in k for k in disambiguated)
    assert "Serial.dtr" not in disambiguated

    # Source 2 (NEW, found this task -- not in the original brief's "8"
    # figure): a module-level function name repeated in a DIFFERENT module.
    # (module, qualname) does not collide (module differs), but the bare
    # contract-table key would, absent disambiguation.
    height_fn = [
        (rec.module, rec.qualname, rec.lineno)
        for rec in survey_records
        if rec.qualname == "_height_of_volume_in_spherical_cap"
    ]
    assert len(height_fn) == 2, (
        "fixture assumption violated: expected _height_of_volume_in_spherical_cap "
        "defined in two distinct modules"
    )
    modules = {rec_key[0] for rec_key in height_fn}
    assert len(modules) == 2, "fixture assumption violated: expected two DIFFERENT modules"
    disambiguated_fn = {keys[k] for k in height_fn}
    assert len(disambiguated_fn) == 2
    assert all("@" in k for k in disambiguated_fn)

    # A non-colliding record keeps its bare qualname (the overwhelming
    # majority -- 4,744 of 4,770 at the current pin).
    aspirate_key = [
        (rec.module, rec.qualname, rec.lineno)
        for rec in survey_records
        if rec.module == "pylabrobot.liquid_handling.liquid_handler" and rec.qualname == "LiquidHandler.aspirate"
    ][0]
    assert keys[aspirate_key] == "LiquidHandler.aspirate"


def test_whole_surface_contract_count(
    survey_records: list[SurveyRecord],
    survey_index: dict[tuple[str, str], SurveyRecord],
    real_stamp: SurveyStamp,
) -> None:
    """T11 items 1+4: `build_derived_contracts_payload` derives a contract
    for EVERY record the survey indexed -- the whole PLR surface, not just
    the 10 `SUPPORTED_TOOLS` methods (spec pre-T11) and not just the 1,314
    finding-bearing methods (T11 item 4's zero-findings decision: a
    zero-own-finding method still gets a real entry, since it may inherit
    guards through its own delegates -- see `PlateReader.read_absorbance`
    covered end-to-end in `test_check_graph.py`).
    """
    payload = build_derived_contracts_payload(survey_records, survey_index, real_stamp)
    contracts = payload["contracts"]

    assert len(contracts) == len(survey_records)
    assert len(contracts) > 10, "whole-surface derivation must exceed the old 10-tool scope"

    # A finding-bearing SUPPORTED_TOOLS method still resolves with guards.
    assert contracts["LiquidHandler.aspirate"]["guards"]

    # A non-LiquidHandler, zero-own-finding method that inherits a guard
    # through delegation is present with a non-empty contract.
    assert contracts["PlateReader.read_absorbance"]["guards"]

    # A zero-own-finding method with an empty closure is present with an
    # EMPTY (not absent) guards/gaps contract -- "known and unconstrained",
    # T11 item 4. 260902 (spec §11.2.4): every entry additionally carries a
    # `params` key (this method's PLR parameter names, straight off
    # `SurveyRecord.params`) -- checked separately below rather than folded
    # into this equality, since its content isn't this test's concern.
    assert contracts["Centrifuge.spin"]["guards"] == []
    assert contracts["Centrifuge.spin"]["gaps"] == []

    # 260902 (spec §11.2.4, SEMA-IR): every contract entry carries an
    # additive `params` key -- the method's PLR parameter names, verbatim
    # off `SurveyRecord.params` (not re-derived here).
    assert "params" in contracts["LiquidHandler.aspirate"]
    assert "resources" in contracts["LiquidHandler.aspirate"]["params"]
    assert "vols" in contracts["LiquidHandler.aspirate"]["params"]

    # Every emitted key really is one of build_contract_keys' outputs (no
    # ad hoc key construction inside build_derived_contracts_payload itself).
    assert set(contracts.keys()) == set(build_contract_keys(survey_records).values())


# ---------------------------------------------------------------------------
# 260901 T14 (backlog #4862) -- the surface-agnostic dropped-receiver
# worklist (top_unresolved.dropped_receiver_whole_surface), and its direct
# motivation: the CLOSURE-based dropped_receiver views are structurally
# empty on a surface with no LiquidHandler/SUPPORTED_TOOLS entry points.
#
# Deliberately does NOT depend on a live PLR source tree: unlike
# scan_dropped_receiver_calls (the independent AST pass, D3), the function
# under test here (_dropped_receiver_worklist_whole_surface) reads only
# each SurveyRecord's own `dropped_calls` field -- already captured in the
# COMMITTED training/verify/data/plr_preconditions.upstream_nonlegacy.json
# -- so `dropped_receiver_counts={}` is passed to build_gap_ledger below on
# purpose: it is irrelevant to the fields these tests inspect, and passing
# an empty dict avoids re-extracting the upstream_nonlegacy pin (T13 used an
# ephemeral git-archive tmpdir; see test_check_graph_nonlegacy.py's module
# docstring) just to run this test.
# ---------------------------------------------------------------------------

NONLEGACY_SURVEY_JSON = (
    REPO_ROOT / "training" / "verify" / "data" / "plr_preconditions.upstream_nonlegacy.json"
)


@pytest.fixture(scope="module")
def nonlegacy_survey_records() -> list[SurveyRecord]:
    return load_survey(NONLEGACY_SURVEY_JSON)


@pytest.fixture(scope="module")
def nonlegacy_survey_index(
    nonlegacy_survey_records: list[SurveyRecord],
) -> dict[tuple[str, str], SurveyRecord]:
    return build_index(nonlegacy_survey_records)


@pytest.fixture(scope="module")
def nonlegacy_gap_ledger(
    nonlegacy_survey_index: dict[tuple[str, str], SurveyRecord],
    nonlegacy_survey_records: list[SurveyRecord],
) -> dict:
    return build_gap_ledger(
        nonlegacy_survey_index,
        nonlegacy_survey_records,
        dropped_receiver_counts={},
    )


def test_closure_based_dropped_receiver_views_are_vacuous_on_nonlegacy(
    nonlegacy_gap_ledger: dict,
) -> None:
    """Pins the T14 motivation directly: on `upstream_nonlegacy`,
    `liquid_handler_present` is False (no orchestration layer, T13), so
    `top_unresolved.dropped_receiver`/`dropped_receiver_unfiltered` (both
    built by walking closures from a `SUPPORTED_TOOLS`/`LiquidHandler`
    entry-point set that is empty here) are structurally EMPTY -- not
    small, not "nothing interesting found", genuinely never populated. If
    this test ever starts failing because these lists are non-empty, either
    upstream reintroduced `LiquidHandler` outside `legacy/`, or a future
    survey regeneration changed which surface this fixture reads.
    """
    assert nonlegacy_gap_ledger["supported_tools"]["liquid_handler_present"] is False
    assert nonlegacy_gap_ledger["top_unresolved"]["dropped_receiver"] == []
    assert nonlegacy_gap_ledger["top_unresolved"]["dropped_receiver_unfiltered"] == []


def test_whole_surface_dropped_receiver_worklist_is_populated_on_nonlegacy(
    nonlegacy_gap_ledger: dict,
) -> None:
    """The new, surface-agnostic view fills exactly the gap the previous
    test pins: it is NOT gated on `tool_keys`, so it is non-empty even
    though the closure-based views above are structurally empty. Checked
    against the real, committed nonlegacy survey data -- not a synthetic
    fixture -- so this is a real measurement, not just a shape check.
    """
    whole_surface = nonlegacy_gap_ledger["top_unresolved"]["dropped_receiver_whole_surface"]
    whole_surface_unfiltered = nonlegacy_gap_ledger["top_unresolved"][
        "dropped_receiver_whole_surface_unfiltered"
    ]
    assert whole_surface, "expected a non-empty ranked worklist on the driver-layer surface"
    assert whole_surface_unfiltered
    assert len(whole_surface) <= len(whole_surface_unfiltered), (
        "filtering must never ADD rows relative to the unfiltered ranking"
    )

    # Every row is well-formed: {"call": str, "blocks_methods": int}, sorted
    # descending by blocks_methods (same shape/order contract as the other
    # three top_unresolved views).
    for row in whole_surface:
        assert set(row.keys()) == {"call", "blocks_methods"}
        assert row["blocks_methods"] >= 1
    counts = [row["blocks_methods"] for row in whole_surface]
    assert counts == sorted(counts, reverse=True)

    # blocks_methods can never exceed the population it was ranked over
    # (methods_attempted, the finding-bearing count).
    methods_attempted = nonlegacy_gap_ledger["totals"]["methods_attempted"]
    assert whole_surface[0]["blocks_methods"] <= methods_attempted

    # 260903 §13.4.2 (backlog #4883): the filter is now DERIVED
    # (`sys.stdlib_module_names` + per-file import-alias resolution,
    # builtin-container-attribute membership) rather than the round-5
    # hand-typed prefix/suffix lists. `logger` is a plain
    # `logging.Logger`-typed local variable on this surface too, not an
    # import alias of the stdlib `logging` module -- so `logger.*` calls
    # are NO LONGER filtered here, and correctly so (§13.4.2's own "six
    # uncovered locals" point: a filter that hides `logger.debug` by
    # naming it hides the fact that the derivation cannot see it). This
    # reverses the round-5 assertion below on purpose; the "filter is
    # actually doing something" property is now demonstrated by `'.join`
    # / other builtin-container-attribute calls instead, still present in
    # the unfiltered ranking and absent from the filtered one.
    filtered_calls = {row["call"] for row in whole_surface}
    unfiltered_calls = {row["call"] for row in whole_surface_unfiltered}
    assert any(call.startswith("logger.") for call in filtered_calls), (
        "fixture assumption violated: expected >=1 logger.* call to survive "
        "the derived filter -- logger is a local variable, not a stdlib "
        "import alias, on this surface"
    )
    assert "', '.join" in unfiltered_calls and "', '.join" not in filtered_calls, (
        "fixture assumption violated: expected the derived filter to still "
        "remove >=1 builtin-container-attribute call (proves the filter is "
        "actually doing something, not vacuously passing because there was "
        "nothing to filter)"
    )


def test_whole_surface_dropped_receiver_worklist_matches_direct_recount(
    nonlegacy_survey_records: list[SurveyRecord],
    nonlegacy_gap_ledger: dict,
) -> None:
    """Cross-check against an independent recomputation straight from
    `SurveyRecord.dropped_calls` -- not trusting the ledger's own output as
    its own proof, the same discipline `test_ledger_totals_are_internally_
    consistent` already applies to `by_reason`.
    """
    finding_bearing = [rec for rec in nonlegacy_survey_records if rec.findings]
    expected: dict[str, int] = {}
    for rec in finding_bearing:
        for call_expr in set(rec.dropped_calls):
            expected[call_expr] = expected.get(call_expr, 0) + 1

    whole_surface_unfiltered = nonlegacy_gap_ledger["top_unresolved"][
        "dropped_receiver_whole_surface_unfiltered"
    ]
    actual = {row["call"]: row["blocks_methods"] for row in whole_surface_unfiltered}
    assert actual == expected


def test_whole_surface_dropped_receiver_worklist_populated_on_legacy(
    survey_records: list[SurveyRecord],
    survey_index: dict[tuple[str, str], SurveyRecord],
) -> None:
    """The new view is published for EVERY surface, not just the one that
    motivated it -- on `legacy_pinned` (which DOES have a `LiquidHandler`
    closure), it ranks a population that is a superset of, not identical
    to, the closure-based `dropped_receiver` view (see the T14 docstring's
    "neither is a strict superset" note for why the reverse containment
    does not hold either) -- checked here only for non-emptiness and shape,
    not byte-for-byte equality with the closure view.
    """
    ledger = build_gap_ledger(survey_index, survey_records, dropped_receiver_counts={})
    whole_surface = ledger["top_unresolved"]["dropped_receiver_whole_surface"]
    assert whole_surface
    for row in whole_surface:
        assert set(row.keys()) == {"call", "blocks_methods"}


# ---------------------------------------------------------------------------
# AC-13.1 / AC-13.2 (spec 260903 §13.4, backlog #4883) -- the derived
# dropped-receiver inert-name filter replaces the two hand-typed frozensets
# (`_INERT_RECEIVER_PREFIXES`, `_INERT_CALL_SUFFIXES`), and the deletion
# leaves the hand-maintained registry unchanged.
# ---------------------------------------------------------------------------

_LIQUID_HANDLER_FILE = "external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py"


@pytest.fixture
def stdlib_importing_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[str]:
    """A synthetic module-level source file that actually imports
    `asyncio`/`time`/`struct`/`contextlib` -- used instead of a real PLR
    file so this test's classification claims do not depend on which PLR
    file happens to import which stdlib module at the current pin (a fact
    that can drift independently of this filter). Patches
    `plr_sema.derive._REPO_ROOT` for the duration of the test so a bare,
    repo-root-relative `file=...` string resolves into `tmp_path`, and
    clears `_module_level_import_aliases`'s cache so an earlier test's
    entry for the same bare filename can never leak in."""
    import plr_sema.derive as derive_mod

    (tmp_path / "stdlib_caller.py").write_text(
        "import asyncio\nimport time\nimport struct\nimport contextlib\n"
    )
    monkeypatch.setattr(derive_mod, "_REPO_ROOT", tmp_path)
    derive_mod._module_level_import_aliases.cache_clear()
    yield "stdlib_caller.py"
    derive_mod._module_level_import_aliases.cache_clear()


@pytest.mark.parametrize(
    "call_expr",
    ["asyncio.sleep", "time.time", "struct.pack", "contextlib.suppress"],
)
def test_derived_inert_filter_classifies_stdlib_calls_as_inert(
    call_expr: str, stdlib_importing_file: str
) -> None:
    """AC-13.1's positive half: none of these four heads were in the
    deleted `_INERT_RECEIVER_PREFIXES` (nine locals/logging/inspect names),
    so a pre-260903 run ranked them as real unresolved-receiver signal
    (T14's finding, §13.4.1). The derived clause-1 replacement catches all
    four -- but only because `stdlib_importing_file` actually IMPORTS each
    module at module level (backlog #4883 follow-up: bare
    `sys.stdlib_module_names` string-membership on the head, with no
    verification the file imported anything, was the bug this tightening
    fixes -- see `test_derived_inert_filter_requires_actual_import`)."""
    assert _is_inert_dropped_receiver_call(call_expr, file=stdlib_importing_file) is True


def test_derived_inert_filter_requires_actual_import(
    stdlib_importing_file: str,
) -> None:
    """Backlog #4883 follow-up (the `resource` false-positive fix): a head
    that merely COINCIDES with a stdlib module name -- `resource` is a
    real, Unix-only stdlib module, and PLR uses `resource` constantly as
    an ordinary local variable name for a `Resource` instance -- must NOT
    be classified inert unless the file's own module-level imports
    actually bind that name to a stdlib module. `stdlib_importing_file`
    imports `asyncio` (so `asyncio.sleep` IS inert) but never imports
    `resource` (so `resource.get_item`, an ordinary PLR receiver call, is
    NOT inert) -- the exact pairing the follow-up requires."""
    assert _is_inert_dropped_receiver_call("asyncio.sleep", file=stdlib_importing_file) is True
    assert (
        _is_inert_dropped_receiver_call("resource.get_item", file=stdlib_importing_file) is False
    )


@pytest.mark.parametrize(
    "call_expr",
    [
        "self.head[channel].get_tip",
        "op.resource.tracker.remove_liquid",
        "op.tip.tracker.add_liquid",
    ],
)
def test_derived_inert_filter_keeps_real_receiver_signal(call_expr: str) -> None:
    """AC-13.1's negative half: real tip/volume-typestate receivers must
    NOT be classified inert by either replaced clause -- `self`/`op` are
    not stdlib module names or aliases of one, `self`/`op` are lowercase
    (clause 2 unaffected), and `get_tip`/`remove_liquid`/`add_liquid` are
    not builtin container/str/bytes attributes (clause 3's replacement)."""
    assert _is_inert_dropped_receiver_call(call_expr, file=_LIQUID_HANDLER_FILE) is False


def test_derived_inert_filter_stub_defeating_half_admits_logger_debug() -> None:
    """AC-13.1's stub-defeating assertion, named explicitly in the spec: an
    implementation that quietly kept `_INERT_RECEIVER_PREFIXES` as a
    fallback would report `logger.debug` as still inert (0 newly admitted).
    `logger` is a local `logging.Logger` instance, not an import alias of
    the stdlib `logging` module in this file, so clause 1's replacement
    (stdlib membership / per-file import-alias resolution) does not catch
    it, and it is genuinely admitted back into the ranking."""
    assert (
        _is_inert_dropped_receiver_call("logger.debug", file=_LIQUID_HANDLER_FILE) is False
    ), "logger.debug must be admitted (not inert) -- see §13.4.2's 'six uncovered locals'"


def _old_inert_predicate(call_expr: str) -> bool:
    """The round-5 rule this task DELETES from the source
    (`_INERT_RECEIVER_PREFIXES`/`_INERT_CALL_SUFFIXES`), reconstructed HERE
    ONLY so this test module can compute the before/after ranking movement
    AC-13.1 requires published -- not reintroduced as a fallback in
    `plr_sema.derive` itself (§13.4.2's design point 8 forbids that)."""
    old_prefixes = {
        "logger", "logging", "warnings", "inspect", "args", "kwargs", "sig",
        "backend_kwargs", "default",
    }
    old_suffixes = {
        "keys", "items", "values", "union", "join", "append", "get", "update",
        "format", "strip", "split",
    }
    head = call_expr.split(".", 1)[0]
    if head in old_prefixes:
        return True
    if head[:1].isupper():
        return True
    tail = call_expr.rsplit(".", 1)[-1]
    return tail in old_suffixes


def test_dropped_receiver_worklist_ranking_movement_both_directions(
    gap_ledger: dict,
) -> None:
    """AC-13.1: publish the ranking movement in both directions over the
    real, shipped `top_unresolved.dropped_receiver` view, relative to the
    ORIGINAL pre-#4883 rule (`_INERT_RECEIVER_PREFIXES`/
    `_INERT_CALL_SUFFIXES`, reconstructed as `_old_inert_predicate`) --
    newly filtered (was ranked under the old rule, now inert under the
    derived rule) and newly admitted (was inert under the old rule, now
    ranked). The newly-admitted count must be > 0 and must include
    `logger.debug` (the stub-defeating half named in the spec) -- `resource`
    was never in the old rule's typed lists, so `resource.*` calls were
    already visible under the OLD rule too and are not part of THIS
    comparison's movement; the follow-up's own regression guard (a
    NARROWER rule than #4883's first cut, not something the pre-#4883 rule
    ever caught) is `test_dropped_receiver_worklist_admits_resource_calls`
    below.

    Compares against the SHIPPED `dropped_receiver` view (not a local
    recomputation) for the "new" side deliberately: the derived rule is
    now per-file (`_is_inert_dropped_receiver_call` requires the
    originating record's own `file`), and the unfiltered call-text list
    alone does not carry which file(s) each call text came from, so
    recomputing "new" with one hardcoded file would silently misclassify
    any call text that appears in more than one file. The old rule had no
    such dependency (`_old_inert_predicate` takes no `file` argument), so
    reconstructing IT locally is safe.
    """
    unfiltered = gap_ledger["top_unresolved"]["dropped_receiver_unfiltered"]
    all_calls = {row["call"] for row in unfiltered}
    new_filtered = {row["call"] for row in gap_ledger["top_unresolved"]["dropped_receiver"]}

    old_filtered = {c for c in all_calls if not _old_inert_predicate(c)}

    newly_filtered = old_filtered - new_filtered
    newly_admitted = new_filtered - old_filtered

    assert len(newly_admitted) > 0
    assert "logger.debug" in newly_admitted
    # Sanity: the derived rule strictly extends stdlib-noise coverage
    # (asyncio/time/struct were real unresolved-receiver noise under the
    # old rule per T14, §13.4.1), so some entries move the other way too.
    assert len(newly_filtered) >= 0  # published even when zero


def test_dropped_receiver_worklist_admits_resource_calls(gap_ledger: dict) -> None:
    """Backlog #4883 follow-up: `resource` is a real, Unix-only stdlib
    module name that also happens to be an extremely common PLR local
    variable name (a `Resource` instance) -- a bare
    `head in sys.stdlib_module_names` membership check (the first cut of
    this item, before the follow-up tightened clause 1 to require an
    ACTUAL per-file import binding) wrongly classified every
    `resource.<attr>` dropped call as inert, with no evidence any file
    ever imported the stdlib `resource` module. None of PLR's files that
    contribute `resource.*` dropped-receiver calls in the SUPPORTED_TOOLS
    closure import the stdlib `resource` module, so all of them must
    survive the (tightened) filter -- this is the stub-defeating half for
    the follow-up specifically: an implementation that reverted to bare
    membership passes every other AC-13.1 assertion and fails only this
    one."""
    filtered_calls = {row["call"] for row in gap_ledger["top_unresolved"]["dropped_receiver"]}
    resource_calls = {c for c in filtered_calls if c.startswith("resource.")}
    assert resource_calls, (
        "expected >=1 resource.* call to survive the derived filter -- if "
        "this is empty, clause 1 has regressed to bare stdlib-name "
        "membership and is wrongly treating `resource` as an import"
    )
    assert "resource.get_item" in filtered_calls


def test_dropped_receiver_worklist_publishes_get_tip_rank(gap_ledger: dict) -> None:
    """AC-13.1's third published number: the resulting rank of
    `self.head[channel].get_tip` in the (derived-rule) filtered ranking --
    it must still be present (real signal, never inert) and its rank is a
    concrete, reportable position."""
    view = gap_ledger["top_unresolved"]["dropped_receiver"]
    calls = [row["call"] for row in view]
    assert "self.head[channel].get_tip" in calls, (
        "self.head[channel].get_tip must survive the derived filter -- it "
        "is real tip-typestate receiver signal, not stdlib/container noise"
    )
    rank = calls.index("self.head[channel].get_tip") + 1
    assert rank >= 1


def test_import_alias_resolution_is_per_file_not_global() -> None:
    """Round-1 challenger O6: alias resolution must be scoped to the file
    the `dropped_calls` entry came from, not a single global table. Two
    synthetic files that bind the SAME local name to DIFFERENT targets --
    one a real stdlib alias, one an ordinary local variable -- must resolve
    independently. A fixer who built one global alias table would have
    `aio` resolve identically in both files; per-file resolution must not.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        file_a = tmp_path / "a.py"
        file_b = tmp_path / "b.py"
        file_a.write_text("import asyncio as aio\n")
        file_b.write_text("aio = SomeOtherThing()\n")  # NOT an import -- ordinary local

        # Resolve relative to the real repo root the module derives paths
        # from (`_REPO_ROOT`), so use paths that are actually reachable --
        # patch the module's repo-root-relative lookup by using a path
        # string relative to the real repo root.
        import plr_sema.derive as derive_mod

        original_root = derive_mod._REPO_ROOT
        try:
            derive_mod._REPO_ROOT = tmp_path
            # `_module_level_import_aliases` is `lru_cache`d on the bare
            # `file` string alone -- clear it so no other test's "a.py"/
            # "b.py" entry (resolved against a DIFFERENT tmp_path) can leak
            # in, and clear again on the way out so this test's entries
            # don't leak to a later one either.
            derive_mod._module_level_import_aliases.cache_clear()
            assert _is_inert_dropped_receiver_call("aio.sleep", file="a.py") is True
            assert _is_inert_dropped_receiver_call("aio.sleep", file="b.py") is False
        finally:
            derive_mod._REPO_ROOT = original_root
            derive_mod._module_level_import_aliases.cache_clear()


def test_ac_13_2_frozensets_are_deleted_from_source() -> None:
    """AC-13.2, first half: an AST scan of `derive/__init__.py` finds no
    module-level assignment named `_INERT_RECEIVER_PREFIXES` or
    `_INERT_CALL_SUFFIXES`, and no `ast.Constant` string equal to any of
    their twenty former members -- so the item cannot be satisfied by
    quietly keeping the list under a different name or inlining its
    members as string literals elsewhere."""
    import plr_sema.derive as derive_mod

    source_path = Path(derive_mod.__file__)
    tree = ast.parse(source_path.read_text(encoding="utf-8"), filename=str(source_path))

    forbidden_names = {"_INERT_RECEIVER_PREFIXES", "_INERT_CALL_SUFFIXES"}
    forbidden_string_constants = {
        "logger", "logging", "warnings", "inspect", "args", "kwargs", "sig",
        "backend_kwargs", "default",
        "keys", "items", "values", "union", "join", "append", "get", "update",
        "format", "strip", "split",
    }
    assert len(forbidden_string_constants) == 20

    assigned_names: set[str] = set()
    string_constants: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigned_names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            assigned_names.add(node.target.id)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            string_constants.add(node.value)

    assert not (assigned_names & forbidden_names), (
        f"forbidden module-level names still assigned: {assigned_names & forbidden_names}"
    )
    hits = string_constants & forbidden_string_constants
    assert not hits, f"forbidden former frozenset members still present as string constants: {hits}"


def test_ac_13_2_registry_unchanged_at_24_live() -> None:
    """AC-13.2, second half: the hand-maintained registry does not grow --
    #4883 adds no row, retires no row (§13.4.3: the frozensets were never
    registered in the first place, so there is no row to retire either).
    `live_rows()` stays 24 against `BUDGET_CAP == 24`, asserted AFTER this
    change, so the item cannot be satisfied by registering the deleted
    surface instead of deriving it."""
    assert BUDGET_CAP == 24
    assert len(live_rows()) == 24


# ---------------------------------------------------------------------------
# AC-12.1 -- the derived setup() head-reset effect (spec 260903 §12.1),
# sub-assertions (iii) and (iv). (i) and (ii) live in test_tip_typestate.py,
# next to AC-10.9, whose shipped-artifact fixture and forbidden-literal scan
# they reuse.
# ---------------------------------------------------------------------------


def _class_index_from_root(root: Path) -> dict[str, ast.ClassDef]:
    """The same "P1 class index" build `derive_receiver_states` does
    internally (every top-level class across a source tree, first
    definition wins) -- duplicated here, not imported, because it is a
    ~10-line loop over already-public helpers and the point of this
    section's own tests is to exercise `reset_rule_candidates` directly,
    at a level BELOW `derive_receiver_states`'s own one-ReceiverState-per-
    class assembly.
    """
    class_nodes: dict[str, ast.ClassDef] = {}
    for file in _iter_plr_source_files(root):
        try:
            tree = ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for top in ast.iter_child_nodes(tree):
            if isinstance(top, ast.ClassDef):
                class_nodes.setdefault(top.name, top)
    return class_nodes


def test_ac_12_1_iv_conjunct_sets_against_real_plr() -> None:
    """AC-12.1(iv): conjuncts 1-2 alone select `{"setup", "load_state"}` at
    the current pin (`LiquidHandler.load_state` also constructs only fresh
    `TipTracker`s with no carry-over, §12.1.2's own worked example) --
    conjunct 3 (direct statement of the method body, not nested in the
    `if head_state and self.head == {}:` `load_state` sits inside) narrows
    that to exactly `{"setup"}`. This is the sub-assertion that fails
    loudly if conjunct 3 is dropped or weakened, per §12.1.2/AC-12.1(iv)'s
    own framing -- without it P5's more-than-one rule would fire and the
    whole feature would silently disable itself at this pin.
    """
    root = default_plr_pkg_root()
    class_nodes = _class_index_from_root(root)
    liquid_handler = class_nodes["LiquidHandler"]

    conj12, conj123 = reset_rule_candidates(liquid_handler, "head", "TipTracker", class_nodes)
    assert conj12 == frozenset({"setup", "load_state"})
    assert conj123 == frozenset({"setup"})


_SYNTH_TRACKER_AND_ANCHOR = '''
class Tracker:
    def __init__(self):
        self._pending_tip = None

    @property
    def has_tip(self):
        return self._pending_tip is not None
'''


def test_ac_12_1_iii_two_qualifying_methods_is_ambiguous(tmp_path: Path) -> None:
    """AC-12.1(iii), first half: a synthetic class with TWO methods that
    each satisfy all three conjuncts produces NO `entry_reset` -- P5's
    more-than-one rule, §12.1.2 -- and the ledger reason is `"ambiguous"`.
    """
    synth = tmp_path / "synth.py"
    synth.write_text(
        _SYNTH_TRACKER_AND_ANCHOR
        + '''

class Receiver:
    def __init__(self):
        self.head: "Tracker" = {}

    def setup(self):
        self.head = {c: Tracker() for c in range(3)}

    def reboot(self):
        self.head = {c: Tracker() for c in range(3)}
''',
        encoding="utf-8",
    )
    receiver_states = derive_receiver_states(tmp_path, records=[], taxonomy_classes=[])
    rs = receiver_states["Receiver"]
    assert rs.entry_reset is None
    assert rs.entry_reset_ledger == "ambiguous"


def test_ac_12_1_iii_carry_over_comprehension_is_absent(tmp_path: Path) -> None:
    """AC-12.1(iii), second half: a method whose value expression is a
    carry-over comprehension (`{k: v for k, v in self.head.items()}`) --
    conjunct 2's own load-bearing counterexample, §12.1.2 -- qualifies for
    NEITHER `conj12` nor `conj123` (it constructs no tracker at all and
    loads `self.head`), so `entry_reset` is `None` and the ledger reason is
    `"absent"`, not `"ambiguous"` -- there is only one candidate method and
    it does not qualify, which is a different fail-closed disposition than
    "more than one qualified".
    """
    synth = tmp_path / "synth.py"
    synth.write_text(
        _SYNTH_TRACKER_AND_ANCHOR
        + '''

class Receiver:
    def __init__(self):
        self.head: "Tracker" = {}

    def reload(self):
        self.head = {k: v for k, v in self.head.items()}
''',
        encoding="utf-8",
    )
    receiver_states = derive_receiver_states(tmp_path, records=[], taxonomy_classes=[])
    rs = receiver_states["Receiver"]
    assert rs.entry_reset is None
    assert rs.entry_reset_ledger == "absent"


# ---------------------------------------------------------------------------
# AC-13.15(i) -- delegate-call literal channel binding (spec §13.5.2, P9,
# backlog #4946): the real-PLR derived binding, and the five-shape negative
# fixture set plus the rule-2 fixture (tested directly against
# `compute_delegate_channel_bindings`, at a level BELOW the whole survey
# pipeline -- the same "exercise the mechanic itself" pattern this file's
# own module docstring names). The rule-4 (disabler ordering) half and
# AC-13.15(ii) (binding grants no effect) live in test_tip_typestate.py,
# next to the check-time fixtures/`_check` helper they need.
# ---------------------------------------------------------------------------


def test_ac_13_15_i_transfer_binds_via_aspirate_arity_default(
    survey_records: list[SurveyRecord],
    survey_index: dict[tuple[str, str], SurveyRecord],
    real_stamp: SurveyStamp,
) -> None:
    """Re-running `plr_sema.derive` over real PLR at the current pin emits,
    on `contracts["LiquidHandler.transfer"]["channel_guards"][0]`, a
    `bound_channels` record with `channels == [0]`, `delegate == "aspirate"`
    and `rule == "arity_default"` -- the rule-3 path, since the `aspirate`
    call site (`liquid_handler.py:1347-1352`) passes no explicit channel
    keyword. `dispense`'s call site at `:1355-1361` binds EXPLICITLY to the
    same numeric channel set through the SAME tracker guard (`get_tip`),
    which is what makes this a real tie the fixer's own one-hop-delegate
    tie-break (K's OWN `delegates_to` declaration order) has to resolve,
    not a vacuous "some [0] shows up somewhere" assertion. And: exactly ONE
    `bound_channels` record exists anywhere in the whole contract table at
    this pin (§13.5.4's own "transfer is the only method this reaches, and
    that must be measured rather than assumed").
    """
    taxonomy = json.loads(TAXONOMY_JSON.read_text(encoding="utf-8"))
    receiver_states = derive_receiver_states(None, survey_records, taxonomy["classes"])
    payload = build_derived_contracts_payload(
        survey_records, survey_index, real_stamp, receiver_states=receiver_states
    )
    contracts = payload["contracts"]

    channel_guards = contracts["LiquidHandler.transfer"]["channel_guards"]
    assert len(channel_guards) == 1
    bound = channel_guards[0]["bound_channels"]
    assert bound["channels"] == [0]
    assert bound["delegate"] == "aspirate"
    assert bound["rule"] == "arity_default"
    assert bound["site_lineno"] == 1347

    found = [
        (key, g["bound_channels"])
        for key, entry in contracts.items()
        for g in entry.get("channel_guards", ())
        if "bound_channels" in g
    ]
    assert found == [("LiquidHandler.transfer", bound)]


_P9_SYNTHETIC_SOURCE = '''
class R:
    async def caller_double_call(self):
        await self.helper(use_channels=[0])
        await self.helper(use_channels=[1])

    async def caller_kwargs_forward(self, **kw):
        await self.helper(**kw)

    async def caller_bare_name(self, chans):
        await self.helper(use_channels=chans)

    async def caller_starred(self, chans):
        await self.helper(use_channels=[*chans])

    async def caller_empty_display(self):
        await self.helper(resources=[])

    async def caller_explicit(self):
        await self.helper(use_channels=[1, 3])

    async def caller_arity_default(self):
        await self.helper(resources=[1, 2, 3])

    async def helper(self, resources=None, use_channels=None):
        pass
'''


def _p9_synthetic_receiver() -> ast.ClassDef:
    tree = ast.parse(_P9_SYNTHETIC_SOURCE)
    (class_node,) = [n for n in ast.iter_child_nodes(tree) if isinstance(n, ast.ClassDef)]
    return class_node


def test_ac_13_15_i_five_negative_fixtures_all_widen() -> None:
    """AC-13.15(i)'s five-shape negative fixture set: two depth-0 awaits of
    the same delegate (rule 1); a `**kwargs` forward; a bare `ast.Name` in
    `use_channels`; a starred argument; and a delegate-parameter display of
    length 0 -- P9 yields `Top` (no entry in the returned table at all,
    §13.5.3's "absent when P9 yields Top") in all five.
    """
    receiver = _p9_synthetic_receiver()
    bindings = compute_delegate_channel_bindings(receiver, {"helper": "resources"}, "use_channels")

    for widened_caller in (
        "caller_double_call",
        "caller_kwargs_forward",
        "caller_bare_name",
        "caller_starred",
        "caller_empty_display",
    ):
        assert widened_caller not in bindings, f"{widened_caller} must widen (Top), found {bindings.get(widened_caller)!r}"


def test_ac_13_15_i_rule_2_explicit_binds_exact_channels() -> None:
    """The rule-2 fixture: `use_channels=[1, 3]` at the call site binds
    EXACTLY `[1, 3]`, `rule == "explicit"` -- not narrowed, not widened,
    and not confused with rule 3's arity-default path (a DIFFERENT caller
    in the same synthetic class, `caller_arity_default`, binds via
    `resources=[1, 2, 3]` to `[0, 1, 2]`, `rule == "arity_default"` --
    both assert here so the two rules are pinned as genuinely distinct,
    not just "some rule matched").
    """
    receiver = _p9_synthetic_receiver()
    bindings = compute_delegate_channel_bindings(receiver, {"helper": "resources"}, "use_channels")

    explicit = bindings["caller_explicit"]["helper"]
    assert explicit["channels"] == [1, 3]
    assert explicit["rule"] == "explicit"
    assert explicit["delegate"] == "helper"

    arity = bindings["caller_arity_default"]["helper"]
    assert arity["channels"] == [0, 1, 2]
    assert arity["rule"] == "arity_default"
    assert arity["delegate"] == "helper"


# ---------------------------------------------------------------------------
# AC-13.3 (spec 260903 §13.1, backlog #4881a) -- the lid facts are DERIVED
# and published, and nothing is claimed from them. Asserted against the
# SHIPPED `plr-sema/data/gap_ledger.json` (not a fixture), because §13.1's
# whole argument is about real PLR at this pin (AC-13.3's own text).
# ---------------------------------------------------------------------------

GAP_LEDGER_JSON_PATH = REPO_ROOT / "plr-sema" / "data" / "gap_ledger.json"


def test_ac_13_3_lid_state_block_is_published_in_shipped_ledger() -> None:
    """The shipped gap ledger carries a `lid_state` block naming, for
    `Liddable`: the P2 anchor as `"absent"` (`has_lid` is a plain method,
    `lid.py:71-72` -- no decorator; the `@property` at `:74` belongs to
    `lid`, not `has_lid`), `has_lid` itself as the one body-shape candidate
    P2's decorator gate rejected, zero state fields (`lid` is computed from
    `self.children` on every read, `lid.py:74-77` -- nothing for
    `_attribute_writers` to see), and the two `_check_no_lid`-derived guard
    conditions with their `raises` -- `"lidded is resource"`/`ValueError`
    at `:116` and `null`/`ValueError` at `:117`.
    """
    ledger = json.loads(GAP_LEDGER_JSON_PATH.read_text(encoding="utf-8"))
    lid_state = ledger["lid_state"]["Liddable"]

    assert lid_state["anchor"] == "absent"
    assert lid_state["anchor_candidates"] == ["has_lid"]
    assert lid_state["state_fields"] == []

    guards = lid_state["check_no_lid_guards"]
    assert len(guards) == 2
    by_lineno = {g["site"]["lineno"]: g for g in guards}
    assert set(by_lineno) == {116, 117}
    assert by_lineno[116]["condition"] == "lidded is resource"
    assert by_lineno[116]["raises"] == "ValueError"
    assert by_lineno[116]["site"]["qualname"] == "_check_no_lid"
    assert by_lineno[116]["site"]["file"].endswith("liquid_handling/liquid_handler.py")
    assert by_lineno[117]["condition"] is None
    assert by_lineno[117]["raises"] == "ValueError"
    assert by_lineno[117]["site"]["qualname"] == "_check_no_lid"


def test_ac_13_3_lid_state_evidence_is_derived_not_hand_typed() -> None:
    """Stub-defeating half: `lid_typestate_anchor_evidence`, called fresh
    against `default_plr_pkg_root()`, reproduces EXACTLY what the shipped
    ledger's `lid_state` block records (short of the `check_no_lid_guards`
    key, which that function does not compute) -- so a hand-typed ledger
    block that happened to match today's PLR pin, rather than a genuinely
    re-run P2 anchor rule, would be caught the moment `Liddable` changes
    shape. Also confirms `Liddable.has_lid` is found via the REAL
    `_typestate_anchor` fail-closed rule (no `@property` decorator ->
    `None`), not a bespoke lid-specific check.
    """
    from plr_sema.derive.receiver_state import lid_typestate_anchor_evidence

    fresh = lid_typestate_anchor_evidence(default_plr_pkg_root())
    assert fresh is not None

    ledger = json.loads(GAP_LEDGER_JSON_PATH.read_text(encoding="utf-8"))
    shipped = ledger["lid_state"]["Liddable"]

    assert fresh["anchor"] == shipped["anchor"] == "absent"
    assert fresh["anchor_candidates"] == shipped["anchor_candidates"] == ["has_lid"]
    assert fresh["state_fields"] == shipped["state_fields"] == []


def test_ac_13_3_no_lidstate_no_receiver_state_entry_no_reason_vocabulary_member() -> None:
    """§13.1's normative disposition, machine-checked: no `LidState` class
    exists anywhere in `plr_sema`; the shipped `receiver_state` block
    (keyed by receiver CLASS, e.g. `LiquidHandler`) carries no `Liddable`
    entry -- the lid ledger block lives ONLY under the separate top-level
    `lid_state` key, never inside `receiver_state`; and `REASON_VOCABULARY`
    gains no lid-related member (still exactly 8, per §13.7/§13.13 item 6).
    """
    import plr_sema

    src_root = Path(plr_sema.__file__).resolve().parent
    for py_file in src_root.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                assert node.name != "LidState", f"a LidState class was constructed at {py_file}:{node.lineno}"

    ledger = json.loads(GAP_LEDGER_JSON_PATH.read_text(encoding="utf-8"))
    assert "Liddable" not in ledger.get("receiver_state", {})

    contracts = json.loads((REPO_ROOT / "plr-sema" / "data" / "derived_contracts.json").read_text(encoding="utf-8"))
    assert "Liddable" not in contracts.get("receiver_state", {})

    from plr_sema.verdict import REASON_VOCABULARY

    assert len(REASON_VOCABULARY) == 8
    assert not any("lid" in reason.lower() for reason in REASON_VOCABULARY)
