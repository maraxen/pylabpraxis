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
from pathlib import Path

import pytest
from plr_sema._provenance import SurveyStamp, survey_stamp
from plr_sema.derive import (
    SurveyFinding,
    SurveyRecord,
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
from plr_sema.derive.receiver_state import derive_receiver_states, reset_rule_candidates

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

    # The existing filter (tuned against the SUPPORTED_TOOLS-closure
    # population's logger/inspect/warnings noise, round-5 T0 item 4) still
    # removes logger.* calls here -- reused, not reinvented, for this new
    # population (see build_gap_ledger's T14 docstring note on why a THIRD
    # hand-typed filter table was deliberately not introduced).
    filtered_calls = {row["call"] for row in whole_surface}
    assert not any(call.startswith("logger.") for call in filtered_calls)
    unfiltered_calls = {row["call"] for row in whole_surface_unfiltered}
    assert any(call.startswith("logger.") for call in unfiltered_calls), (
        "fixture assumption violated: expected >=1 logger.* call in the "
        "unfiltered ranking (proves the filter is actually doing something, "
        "not vacuously passing because there was nothing to filter)"
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
