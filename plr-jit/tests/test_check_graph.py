"""Spec 260901 §6.3/§6.5, T8 (backlog #4834): `plr_jit.check`'s round-1 entry
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

import json
import subprocess
import sys
from pathlib import Path

import pytest

from plr_jit.check import SUPPORTED_TOOLS, check_graph
from plr_jit.verdict import AnalysisReport, Finding, PlrSite, Verdict

PLR_JIT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLR_JIT_ROOT.parent
FIXTURE_GRAPH_JSON = PLR_JIT_ROOT / "tests" / "fixtures" / "simple_transfer_graph.json"
CONTRACTS_JSON = PLR_JIT_ROOT / "data" / "derived_contracts.json"

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
# AC-6.1 -- import plr_jit.check with BOTH libcst and pylabrobot poisoned.
# ---------------------------------------------------------------------------


def test_check_imports_without_libcst() -> None:
    """Spec AC-6.1/§6.3's `test_check_imports_without_libcst`: poison BOTH
    `libcst` and `pylabrobot` to `None` in `sys.modules` (stronger than
    simply not installing them -- fails even if the import is merely
    reachable, not just unavailable), then `import plr_jit.check`. Assert
    exit 0."""
    src_path = str(PLR_JIT_ROOT / "src")
    preamble = (
        "import sys; "
        "sys.modules['libcst'] = None; "
        "sys.modules['pylabrobot'] = None; "
        "import plr_jit.check"
    )
    result = subprocess.run(
        [sys.executable, "-c", preamble],
        cwd=str(PLR_JIT_ROOT),
        env={"PYTHONPATH": src_path, "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f"import plr_jit.check failed with libcst+pylabrobot poisoned:\n"
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
    surjectivity). `{f.operation_id for f in report.findings}` must equal
    -- not just be a subset of -- the fixture graph's REAL `OperationNode.id`
    values. The subset-only form was the anti-fabrication anchor but said
    nothing about COVERAGE: `len(findings) >= len(operations)` (AC-6.3)
    does not imply every operation actually received >=1 finding, and
    nothing in the pre-round-4 suite asserted the surjective direction.
    `research_a_d.md:339-345`'s finding, independently confirmed: a
    `check_graph` that only ever emits findings for op_1 would still pass a
    subset-only check and a count-only check simultaneously, while silently
    never reporting anything about op_2/op_3/op_4."""
    graph_payload = json.loads(FIXTURE_GRAPH_JSON.read_text(encoding="utf-8"))
    real_ids = {op["id"] for op in graph_payload["operations"]}

    finding_ids = {f.operation_id for f in report.findings}
    assert finding_ids == real_ids, (
        f"report.findings' operation_id set {sorted(finding_ids)} != the "
        f"fixture graph's real operation id set {sorted(real_ids)} -- either "
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
    which all pass `plr_site=None` -- see `plr_jit.check._unknown`)."""
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
# AC-6.5 (D1) -- the ONE live SUPPORTED_TOOLS drift test post-consolidation.
# ---------------------------------------------------------------------------


def test_supported_tools_match_upstream() -> None:
    """`plr_jit.check.SUPPORTED_TOOLS` (the single in-package definition,
    T8 consolidation -- see `plr_jit/check/_supported_tools.py`) must be the
    SAME set as `training.verify.dispatcher.SUPPORTED_TOOLS` today -- a live
    drift test, not a copied constant re-asserted against itself.
    `src/plr_jit` cannot import `verify` (import-boundary test forbids it);
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
        f"plr_jit.check.SUPPORTED_TOOLS {sorted(SUPPORTED_TOOLS)} != "
        f"verify.dispatcher.SUPPORTED_TOOLS {sorted(upstream_dispatcher.SUPPORTED_TOOLS)}"
    )


# ---------------------------------------------------------------------------
# AC-6.6 (D15, moved from AC-3.4) -- full T8 pipeline round-trips to JSON.
# ---------------------------------------------------------------------------


def _plr_site_from_dict(d: dict | None) -> PlrSite | None:
    return None if d is None else PlrSite(file=d["file"], lineno=d["lineno"], qualname=d["qualname"])


def _git_state_from_dict(d: dict):
    from plr_jit._provenance.git_state import GitState

    return GitState(**d)


def _stamp_from_dict(d: dict):
    from plr_jit._provenance import SurveyStamp

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
    ever called plr_jit.telemetry.emit*; check_graph now does, for every
    reason, not just internal_error). This test therefore attaches the sink
    and calls `check_graph` directly -- it does NOT call `emit_finding`
    itself, unlike the pre-round-4 version, which emitted from the test and
    proved nothing about the pipeline's own emission behavior. Uses the
    `graph_json`/`contracts_json` fixtures rather than the module-scoped
    `report` fixture, since `report` may have already been built (and
    already emitted, against whatever sink was active then) by an earlier
    test in this module."""
    from plr_jit.telemetry import JsonlSink, set_sink

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
