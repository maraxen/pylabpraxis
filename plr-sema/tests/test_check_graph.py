"""Spec 260901 §6.3/§6.5, T8 (backlog #4834): `plr_sema.check`'s round-1 entry
point, `check_graph(graph_json, contracts_json) -> AnalysisReport`.

Fixture protocol: `simple_transfer` (`tests/fixtures/simple_transfer_graph.
json`), generated out-of-process (spec §6.2/C5 -- `check/` never imports the
extractor; this file doesn't either) by subprocessing into the EXISTING
`praxis.backend.utils.plr_static_analysis.visitors.computation_graph_
extractor.extract_graph_from_source`, over the `SIMPLE_TRANSFER_SOURCE`
fixture already used by `tests/utils/test_computation_graph.py` at repo
root -- chosen because all four of its operations
(`pick_up_tips`/`aspirate`/`dispense`/`drop_tips`) resolve a concrete
`receiver_type` ("LiquidHandler") and a `method_name` that is BOTH in
`SUPPORTED_TOOLS` AND has a populated entry (>=1 guard) in the real,
committed `derived_contracts.json` -- so this fixture genuinely exercises
the contract-table lookup (spec §6.2's D1 flag: `receiver_type_unknown`
alone must not be the only thing satisfying AC-6.3, or the contract table
goes entirely unexercised). See `test_fixture_exercises_contract_table_
lookup` below for the direct confirmation.
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from plr_sema.check import SUPPORTED_TOOLS, check_graph, ir
from plr_sema.verdict import AnalysisReport, Finding, PlrSite, Verdict

PLR_SEMA_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLR_SEMA_ROOT.parent
FIXTURE_GRAPH_JSON = PLR_SEMA_ROOT / "tests" / "fixtures" / "simple_transfer_graph.json"
CONTRACTS_JSON = PLR_SEMA_ROOT / "data" / "derived_contracts.json"

# The full SHA at the pin AC-6.7 targets -- same pin as test_telemetry.py's
# AC-4.3 (external/pylabrobot HEAD, confirmed live this session via
# `git -C external/pylabrobot rev-parse HEAD`).
_PLR_PIN_SHA = "dd79c4c89bc008629a1c598ea614be5e6067d1f9"


@pytest.fixture(scope="module")
def graph_json() -> str:
    return FIXTURE_GRAPH_JSON.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def contracts_json() -> str:
    return CONTRACTS_JSON.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def report(graph_json: str, contracts_json: str) -> AnalysisReport:
    return check_graph(graph_json, contracts_json)


# ---------------------------------------------------------------------------
# AC-6.1 -- import plr_sema.check with BOTH libcst and pylabrobot poisoned.
# ---------------------------------------------------------------------------


def test_check_imports_without_libcst() -> None:
    """Spec AC-6.1/§6.3's `test_check_imports_without_libcst`: poison BOTH
    `libcst` and `pylabrobot` to `None` in `sys.modules` (stronger than
    simply not installing them -- fails even if the import is merely
    reachable, not just unavailable), then `import plr_sema.check`. Assert
    exit 0."""
    src_path = str(PLR_SEMA_ROOT / "src")
    preamble = (
        "import sys; "
        "sys.modules['libcst'] = None; "
        "sys.modules['pylabrobot'] = None; "
        "import plr_sema.check"
    )
    result = subprocess.run(
        [sys.executable, "-c", preamble],
        cwd=str(PLR_SEMA_ROOT),
        env={"PYTHONPATH": src_path, "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"import plr_sema.check failed with libcst+pylabrobot poisoned:\n"
        f"stdout={result.stdout}\nstderr={result.stderr}"
    )


# ---------------------------------------------------------------------------
# AC-6.3 / AC-6.4 -- fixture graph -> check_graph -> AnalysisReport.
# ---------------------------------------------------------------------------


def test_fixture_graph_yields_unknown_report_with_findings(report: AnalysisReport) -> None:
    """AC-6.3: the committed fixture graph JSON, passed to `check_graph`,
    yields an `AnalysisReport` with `verdict == UNKNOWN` and >=1 finding."""
    assert report.verdict is Verdict.UNKNOWN
    assert len(report.findings) >= 1


def test_operation_ids_are_a_subset_of_real_graph_ids(report: AnalysisReport) -> None:
    """AC-6.4 (round-4 remediation, B2/fix 6: strengthened from subset to
    surjectivity; spec 260903 §12.3.4/§12.9's main-spec amendment: now
    re-read over `OBLIGED(graph)`, not the raw operation-id set).
    `{f.operation_id for f in report.findings}` must equal --  not just be
    a subset of -- `ir.obliged_operation_ids(graph_payload)`. The shipped
    `simple_transfer_graph.json` fixture carries no `REGION` at all
    (AC-12.9), so `OBLIGED(graph) == {op.id for op in graph.operations}`
    here and this test's own behaviour is UNCHANGED from pre-260903 -- see
    `test_dead_loop_body_...` below for the fixture where the two sets
    actually differ. The subset-only form was the anti-fabrication anchor
    but said nothing about COVERAGE: `len(findings) >= len(operations)`
    (AC-6.3) does not imply every operation actually received >=1 finding,
    and nothing in the pre-round-4 suite asserted the surjective direction.
    `research_a_d.md:339-345`'s finding, independently confirmed: a
    `check_graph` that only ever emits findings for op_1 would still pass a
    subset-only check and a count-only check simultaneously, while silently
    never reporting anything about op_2/op_3/op_4."""
    graph_payload = json.loads(FIXTURE_GRAPH_JSON.read_text(encoding="utf-8"))
    real_ids = ir.obliged_operation_ids(graph_payload)

    finding_ids = {f.operation_id for f in report.findings}
    assert finding_ids == real_ids, (
        f"report.findings' operation_id set {sorted(finding_ids)} != the "
        f"fixture graph's OBLIGED(graph) set {sorted(real_ids)} -- either "
        f"a fabricated id ({finding_ids - real_ids}) or an uncovered "
        f"operation ({real_ids - finding_ids})"
    )


def test_fixture_exercises_contract_table_lookup(report: AnalysisReport) -> None:
    """Spec §6.2's D1 flag, directly confirmed: `check_graph` must not be
    satisfiable using ONLY `receiver_type_unknown` (which needs no
    contract-table lookup at all) -- at least one finding must come from a
    REAL, populated contract-table entry, evidenced by a non-null
    `plr_site` pointing into `external/pylabrobot` (a guard's site is only
    ever populated from a resolved `DerivedContract`, never from
    `receiver_type_unknown`/`unsupported_tool`/`no_contract_derived`,
    which all pass `plr_site=None` -- see `plr_sema.check._unknown`)."""
    reasons = {f.reason for f in report.findings}
    assert reasons != {"receiver_type_unknown"}, (
        "every finding is receiver_type_unknown -- the contract table was "
        "never touched (spec §6.2's D1 flag: this is exactly the degenerate "
        "gate the fix closes)"
    )
    grounded_sites = [f for f in report.findings if f.plr_site is not None]
    assert grounded_sites, "no finding carries a plr_site -- no guard from a real contract fired"
    assert any(
        "external/pylabrobot" in f.plr_site.file for f in grounded_sites
    ), "no finding's plr_site points into external/pylabrobot -- contract table not exercised"


# ---------------------------------------------------------------------------
# 260901 T11 -- whole-surface decoupling from SUPPORTED_TOOLS.
# ---------------------------------------------------------------------------


def _single_op_graph(method_name: str, receiver_type: str) -> str:
    return json.dumps(
        {
            "protocol_fqn": "test.t11_whole_surface",
            "operations": [
                {
                    "id": "op_1",
                    "method_name": method_name,
                    "receiver_variable": "x",
                    "receiver_type": receiver_type,
                }
            ],
            "resources": {},
        }
    )


def test_non_liquid_handler_family_resolves_end_to_end(contracts_json: str) -> None:
    """T11 item 1: `check_graph` resolves an operation OUTSIDE
    `LiquidHandler`/the old `SUPPORTED_TOOLS` 10 end-to-end through a real,
    populated contract-table entry. `PlateReader.read_absorbance` has ZERO
    own findings but delegates to `get_plate`, which has one -- so this also
    directly confirms T11 item 4's zero-findings decision: a zero-own-finding
    entry point still surfaces a real, grounded guard inherited through its
    closure, rather than falling back to `unsupported_tool`."""
    report = check_graph(_single_op_graph("read_absorbance", "PlateReader"), contracts_json)
    assert report.verdict is Verdict.UNKNOWN
    reasons = {f.reason for f in report.findings}
    assert "unsupported_tool" not in reasons
    grounded = [f for f in report.findings if f.plr_site is not None]
    assert grounded, "PlateReader.read_absorbance surfaced no grounded finding via its delegate closure"
    assert any(f.plr_site.qualname == "PlateReader.get_plate" for f in grounded), (
        "expected a finding grounded at PlateReader.get_plate (the delegate "
        "read_absorbance's own zero-finding body inlines a guard from)"
    )


def test_unsupported_tool_fires_only_for_genuinely_unknown_methods(contracts_json: str) -> None:
    """T11 items 3/4: `unsupported_tool` now means "key absent from the
    whole-survey contract table" -- verified against all three cases it must
    distinguish:

    * a method name the whole-survey derivation never saw at all -> fires.
    * a real, finding-bearing method OUTSIDE the old 10-name
      `SUPPORTED_TOOLS` allowlist (`pick_up_tips96`) -> must NOT fire (the
      old gate would have fired here; this is the direct regression test
      for decoupling derivation from `SUPPORTED_TOOLS`).
    * a real method the survey scanned with zero own findings and an empty
      closure (`Centrifuge.spin`) -- "known and unconstrained" -- must NOT
      fire either; it resolves via the existing zero-guards/zero-gaps
      `no_contract_derived` fallback instead (T11 item 4's zero-findings
      decision).
    """
    unknown_report = check_graph(
        _single_op_graph("definitely_fake_method_xyz", "LiquidHandler"), contracts_json
    )
    assert {f.reason for f in unknown_report.findings} == {"unsupported_tool"}

    outside_old_allowlist_report = check_graph(
        _single_op_graph("pick_up_tips96", "LiquidHandler"), contracts_json
    )
    assert "unsupported_tool" not in {f.reason for f in outside_old_allowlist_report.findings}

    zero_finding_report = check_graph(_single_op_graph("spin", "Centrifuge"), contracts_json)
    assert {f.reason for f in zero_finding_report.findings} == {"no_contract_derived"}


# ---------------------------------------------------------------------------
# AC-6.5 (D1) -- the ONE live SUPPORTED_TOOLS drift test post-consolidation.
# ---------------------------------------------------------------------------


def test_supported_tools_match_upstream() -> None:
    """`plr_sema.check.SUPPORTED_TOOLS` (the single in-package definition,
    T8 consolidation -- see `plr_sema/check/_supported_tools.py`) must be the
    SAME set as `training.verify.dispatcher.SUPPORTED_TOOLS` today -- a live
    drift test, not a copied constant re-asserted against itself.
    `src/plr_sema` cannot import `verify` (import-boundary test forbids it);
    this test file can, with both `<repo_root>/training` and
    `<repo_root>/coxswain/src` on `sys.path` first (`verify/__init__.py`
    eagerly imports `verify.checks`, which imports
    `coxswain.plr.intent_record`)."""
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
        f"plr_sema.check.SUPPORTED_TOOLS {sorted(SUPPORTED_TOOLS)} != "
        f"verify.dispatcher.SUPPORTED_TOOLS {sorted(upstream_dispatcher.SUPPORTED_TOOLS)}"
    )


# ---------------------------------------------------------------------------
# AC-6.6 (D15, moved from AC-3.4) -- full T8 pipeline round-trips to JSON.
# ---------------------------------------------------------------------------


def _plr_site_from_dict(d: dict | None) -> PlrSite | None:
    return None if d is None else PlrSite(file=d["file"], lineno=d["lineno"], qualname=d["qualname"])


def _git_state_from_dict(d: dict):
    from plr_sema._provenance.git_state import GitState

    return GitState(**d)


def _stamp_from_dict(d: dict):
    from plr_sema._provenance import SurveyStamp

    return SurveyStamp(
        plr=_git_state_from_dict(d["plr"]),
        praxis=_git_state_from_dict(d["praxis"]),
        pylabrobot_version=d["pylabrobot_version"],
        stamped_at=d["stamped_at"],
        schema_version=d["schema_version"],
    )


def _finding_from_dict(d: dict) -> Finding:
    return Finding(
        verdict=Verdict(d["verdict"]),
        operation_id=d["operation_id"],
        category=d["category"],
        plr_site=_plr_site_from_dict(d["plr_site"]),
        reason=d["reason"],
        detail=d["detail"],
        evidence=tuple(_plr_site_from_dict(s) for s in d["evidence"]),
    )


def _report_from_dict(d: dict) -> AnalysisReport:
    return AnalysisReport(
        protocol_fqn=d["protocol_fqn"],
        verdict=Verdict(d["verdict"]),
        findings=tuple(_finding_from_dict(f) for f in d["findings"]),
        stamp=_stamp_from_dict(d["stamp"]),
        schema_version=d["schema_version"],
    )


def test_full_pipeline_report_round_trips_json(report: AnalysisReport) -> None:
    """AC-6.6 (D15, moved from AC-3.4): an `AnalysisReport` produced by
    running the FULL T8 pipeline (fixture graph JSON -> `check_graph` ->
    report) over the fixture protocol serializes to JSON and deserializes
    field-identically. AC-3.4 (`test_verdict.py`) already covers the
    narrower direct-construction form; this is the full-pipeline form T3
    alone could not exercise."""
    import dataclasses

    payload = json.loads(json.dumps(dataclasses.asdict(report)))
    rebuilt = _report_from_dict(payload)
    assert rebuilt == report


# ---------------------------------------------------------------------------
# AC-6.7 (D15, moved from AC-4.3) -- full pipeline + JsonlSink emission.
# ---------------------------------------------------------------------------


def test_full_pipeline_emits_stamped_jsonl(
    graph_json: str, contracts_json: str, tmp_path: Path
) -> None:
    """AC-6.7 (D15, moved from AC-4.3; round-4 remediation, M2/fix 17): with
    `JsonlSink` attached BEFORE the run, `check_graph` itself now emits
    every finding (§3.3:444's "internal_error ... always paired with a
    telemetry emit" used to be false of the code -- nothing under check/
    ever called plr_sema.telemetry.emit*; check_graph now does, for every
    reason, not just internal_error). This test therefore attaches the sink
    and calls `check_graph` directly -- it does NOT call `emit_finding`
    itself, unlike the pre-round-4 version, which emitted from the test and
    proved nothing about the pipeline's own emission behavior. Uses the
    `graph_json`/`contracts_json` fixtures rather than the module-scoped
    `report` fixture, since `report` may have already been built (and
    already emitted, against whatever sink was active then) by an earlier
    test in this module."""
    from plr_sema.telemetry import JsonlSink, set_sink

    sink_path = tmp_path / "events.jsonl"
    set_sink(JsonlSink(sink_path))
    try:
        check_graph(graph_json, contracts_json)
    finally:
        set_sink(None)

    lines = sink_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) >= 1
    # Round-4 remediation (M8/fix 23): asserted against a FALSIFIABLE
    # identity -- the emitted stamp must equal the stamp
    # `derived_contracts.json` itself carries -- rather than a hardcoded
    # pin string that silently passes against an arbitrarily stale
    # artifact (the checker's own code version is unrecorded; `stamp` is
    # build-time-only provenance, reconstructed verbatim from the
    # contracts payload -- see AnalysisReport's docstring).
    expected_hash = json.loads(contracts_json)["stamp"]["plr"]["hash"]
    for line in lines:
        event = json.loads(line)
        assert event["stamp"]["plr"]["hash"] == expected_hash
    # The pin is still confirmed live for THIS checkout, as a secondary,
    # self-scoping sanity check (not the primary assertion above).
    assert expected_hash == _PLR_PIN_SHA


# ---------------------------------------------------------------------------
# Spec 260903 §12.3.4 -- OBLIGED(graph) at check_graph level: a proved-
# trip-0 region's body must never receive a Finding, and AC-6.4/AC-7.2
# amended must both hold over that exclusion.
# ---------------------------------------------------------------------------

DEAD_LOOP_BODY_FIXTURE = PLR_SEMA_ROOT / "tests" / "fixtures" / "dead_loop_body_graph.json"


def test_dead_loop_body_excluded_from_findings_and_obliged(contracts_json: str) -> None:
    graph_json = DEAD_LOOP_BODY_FIXTURE.read_text(encoding="utf-8")
    graph_payload = json.loads(graph_json)
    report = check_graph(graph_json, contracts_json)

    obliged = ir.obliged_operation_ids(graph_payload)
    finding_ids = {f.operation_id for f in report.findings}

    assert "op_3" not in finding_ids, "op_3 is the trip==0 loop's body -- never visited, never a Finding"
    assert "op_3" not in obliged, "OBLIGED(graph) must exclude the dead loop body"
    assert finding_ids == obliged, "AC-6.4 amended: {f.operation_id} == OBLIGED(graph)"
    assert len(report.findings) >= len(obliged), "AC-7.2 amended: len(findings) >= len(OBLIGED(graph))"
    assert finding_ids == {"op_1", "op_4"}


# ---------------------------------------------------------------------------
# Spec 260903 §13.1/§13.9, backlog #4881a -- AC-13.3/AC-13.4. The lid
# family is specified and NOT adopted: `_check_no_lid`'s two guards are
# already inlined (depth 1) into `LiquidHandler.aspirate`'s contract entry
# (they were there before this task; nothing in `plr_sema.derive`/
# `plr_sema.check` was changed to construct a lid Finding), and the
# checker's existing, guard-agnostic `guard_predicate_unparsed` emission
# (`plr_sema.check._finding_from_guard`) already treats BOTH uniformly as
# UNKNOWN -- this is a REGRESSION test that that stays true, most of all
# for the `:117` guard's `condition: null` (the landmine, §13.1.3's own
# disclosure): a future evaluator that read `null` as "raises
# unconditionally" would manufacture `WILL_FAIL` on every one of the six
# `LiquidHandler` methods `_check_no_lid` reaches, for programs that run
# clean.
# ---------------------------------------------------------------------------

LIDDED_PLATE_ASPIRATE_FIXTURE = PLR_SEMA_ROOT / "tests" / "fixtures" / "lidded_plate_aspirate_graph.json"

# The two `_check_no_lid` guard sites (§13.1.1): `:116` is the self-lidded
# raise (`condition == "lidded is resource"`), `:117` is the
# ancestor-lidded raise -- the `condition: null` landmine.
_LID_GUARD_LINENOS = (116, 117)


def test_lid_family_emits_nothing(contracts_json: str) -> None:
    """AC-13.4, first half: for `setup()` then `aspirate(use_channels=[0])`
    on a (nominally lidded, per the fixture's own name) plate, zero
    findings carry a `plr_site` at `liquid_handler.py:116`/`:117` with a
    verdict other than `Verdict.UNKNOWN` -- i.e. the lid family never
    promotes either guard to `SAFE` or `WILL_FAIL`. Also asserts no
    `Finding.reason` contains "lid" anywhere in `report.findings` --
    `REASON_VOCABULARY` has no lid-related member (§13.1's normative
    disposition; the row spends none), so this can never pass by
    coincidence of vocabulary shape.
    """
    graph_json = LIDDED_PLATE_ASPIRATE_FIXTURE.read_text(encoding="utf-8")
    report = check_graph(graph_json, contracts_json)

    assert len(report.findings) >= 1
    for finding in report.findings:
        assert "lid" not in finding.reason.lower(), (
            f"a lid-related reason was constructed: {finding.reason!r} (op {finding.operation_id})"
        )
        site = finding.plr_site
        if site is not None and site.file.endswith("liquid_handler.py") and site.lineno in _LID_GUARD_LINENOS:
            assert finding.verdict is Verdict.UNKNOWN, (
                f"a lid guard at liquid_handler.py:{site.lineno} was promoted to {finding.verdict!r}"
            )


def test_lid_family_findings_identical_to_graph_without_the_plate(contracts_json: str) -> None:
    """AC-13.4, corroborating: the wire format cannot represent a lid at
    all (§13.1.2/L3 -- `RESOURCE`'s only structural operand is
    `parents: tuple[str, ...]`, an upward, type-only chain with no
    children field). So mentioning the (nominally lidded) plate at all,
    versus not mentioning it, must be INVISIBLE to `check_graph` --
    stripping the plate resource and its `aspirate` argument reference
    from the fixture payload must not change a single emitted `Finding`.
    An implementation that somehow keyed a Finding off the plate's
    presence would fail this, even though nothing in §13.1 authorizes one
    to exist.
    """
    graph_json = LIDDED_PLATE_ASPIRATE_FIXTURE.read_text(encoding="utf-8")
    with_plate = json.loads(graph_json)
    without_plate = copy.deepcopy(with_plate)
    del without_plate["resources"]["plate"]
    del without_plate["operations"][1]["arguments"]["resource"]
    without_plate["resource_types"] = ["LiquidHandler"]

    report_with = check_graph(graph_json, contracts_json)
    report_without = check_graph(json.dumps(without_plate), contracts_json)

    assert report_with.findings == report_without.findings
    assert report_with.verdict == report_without.verdict


def test_lid_family_null_condition_guard_is_unknown_not_will_fail(contracts_json: str) -> None:
    """AC-13.4, second half -- the stub-defeating one: the Finding for the
    `:117` guard (whose derived `condition` is `null`) is
    `Verdict.UNKNOWN` with `reason == "guard_predicate_unparsed"`, NOT
    `Verdict.WILL_FAIL`. `null` reads, on its face, as "raises
    unconditionally"; it is not -- `:117`'s raise is reachable only when
    the early `return` at `liquid_handler.py:113-114` did not fire, and
    the precondition survey's `scope_trail` does not model early returns
    (§13.1.3), so no evaluator today or in this fixture can construct that
    fact. An evaluator that treated a `null` condition as "always true"
    would emit `WILL_FAIL` here and fail this assertion.
    """
    graph_json = LIDDED_PLATE_ASPIRATE_FIXTURE.read_text(encoding="utf-8")
    report = check_graph(graph_json, contracts_json)

    null_condition_findings = [
        f
        for f in report.findings
        if f.plr_site is not None
        and f.plr_site.file.endswith("liquid_handler.py")
        and f.plr_site.lineno == 117
    ]
    assert len(null_condition_findings) == 1, (
        f"expected exactly one Finding for the :117 null-condition guard, got {null_condition_findings!r}"
    )
    finding = null_condition_findings[0]
    assert finding.verdict is Verdict.UNKNOWN
    assert finding.reason == "guard_predicate_unparsed"
    assert finding.verdict is not Verdict.WILL_FAIL
