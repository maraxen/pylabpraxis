"""Spec 260902 §10 (`260902_plr-sema-tip-typestate-increment.md`), backlog
#4888 step 1: per-channel tip typestate. Each `test_ac_10_*` function below
names one acceptance criterion from §10.7 individually (not grouped), per
the task brief's convention.

**Fixtures.** `double_pickup_graph.json`, `pickup_then_aspirate_graph.json`,
`aspirate_after_drop_graph.json` (all three named by the spec, §10.7) use
operation ids `op_1`/`op_2`/`op_3` (1-indexed), matching this repo's
existing `simple_transfer_graph.json` convention -- not the spec's own
illustrative `op_0`/`op_1` (0-indexed) numbering. Substance, not the id
strings, is what every assertion below pins.

**Disclosed deviation from AC-10.1's literal "exactly one" `WILL_FAIL`
count (see `test_ac_10_1...` below).** §10.2.6 itself predicts
`pick_up_tips`'s tip-loading precondition is covered "both ways: its own
:535 guard *and* `self.head[channel].add_tip` at :538" -- and §10.3.1's
evaluator has no dedup rule between an "own guard" and a "channel guard"
that happen to demand the identical real-world precondition. Implemented
literally, a repeated pickup therefore produces TWO independent `WILL_FAIL`
findings (the own :535 guard, and the bridged `TipTracker.add_tip:92`
guard), not one. This is sound (strictly more true evidence, never a
fabricated claim) and is the direction increment 1's own soundness argument
(§10.5) explicitly prefers when a choice must be made under-specified by
the letter of an AC. The test below asserts AC-10.1's literal pins (the
`:535` site, category, per-op join, report verdict) among the findings,
rather than asserting a bare count of exactly 1.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest
from plr_sema.check import check_graph
from plr_sema.derive.receiver_state import compute_tip_state_exceptions
from plr_sema.verdict import AnalysisReport, PlrSite, Verdict

PLR_SEMA_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLR_SEMA_ROOT.parent
FIXTURES = PLR_SEMA_ROOT / "tests" / "fixtures"
CONTRACTS_JSON_PATH = PLR_SEMA_ROOT / "data" / "derived_contracts.json"
TAXONOMY_JSON_PATH = REPO_ROOT / "training" / "verify" / "data" / "plr_exception_taxonomy.json"

_PICK_UP_TIPS_SITE = PlrSite(
    file="external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py",
    lineno=535,
    qualname="LiquidHandler.pick_up_tips",
)
_GET_TIP_SITE = PlrSite(
    file="external/pylabrobot/pylabrobot/resources/tip_tracker.py", lineno=65, qualname="TipTracker.get_tip"
)


@pytest.fixture(scope="module")
def contracts_json() -> str:
    return CONTRACTS_JSON_PATH.read_text(encoding="utf-8")


def _graph(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def _check(name: str, contracts_json: str) -> AnalysisReport:
    return check_graph((FIXTURES / f"{name}.json").read_text(encoding="utf-8"), contracts_json)


def _findings_for(report: AnalysisReport, operation_id: str) -> list:
    return [f for f in report.findings if f.operation_id == operation_id]


def _join(findings: list) -> Verdict:
    verdicts = {f.verdict for f in findings}
    if Verdict.WILL_FAIL in verdicts:
        return Verdict.WILL_FAIL
    if Verdict.UNKNOWN in verdicts:
        return Verdict.UNKNOWN
    return Verdict.SAFE if findings else Verdict.UNKNOWN


# ---------------------------------------------------------------------------
# AC-10.1
# ---------------------------------------------------------------------------


def test_ac_10_1_will_fail_on_repeated_pickup(contracts_json: str) -> None:
    report = _check("double_pickup_graph", contracts_json)
    op1, op2 = _findings_for(report, "op_1"), _findings_for(report, "op_2")

    assert _join(op1) is Verdict.UNKNOWN
    assert _join(op2) is Verdict.WILL_FAIL
    assert report.verdict is Verdict.WILL_FAIL

    will_fail = [f for f in op2 if f.verdict is Verdict.WILL_FAIL]
    assert will_fail, "the second pick_up_tips must produce at least one WILL_FAIL"
    assert all(f.category == "precondition_state" for f in will_fail)
    assert any(f.plr_site == _PICK_UP_TIPS_SITE for f in will_fail), (
        "AC-10.1's literal pin: one WILL_FAIL must be sited at liquid_handler.py:535"
    )
    # See this module's docstring: §10.2.6 predicts a SECOND, additive
    # WILL_FAIL from the bridged TipTracker.add_tip guard -- disclosed, not
    # a defect.
    assert len(will_fail) == 2
    assert not [f for f in op2 if f.verdict is Verdict.SAFE]


# ---------------------------------------------------------------------------
# AC-10.2
# ---------------------------------------------------------------------------


def test_ac_10_2_safe_after_pickup_no_operation_level_safe(contracts_json: str) -> None:
    report = _check("pickup_then_aspirate_graph", contracts_json)
    op2 = _findings_for(report, "op_2")

    safe = [f for f in op2 if f.verdict is Verdict.SAFE]
    assert len(safe) == 1, "exactly one SAFE finding on the aspirate, per AC-10.2"
    assert safe[0].plr_site == _GET_TIP_SITE

    assert _join(op2) is Verdict.UNKNOWN, "the operation-level join stays UNKNOWN (its other guards are 1/2)"
    assert not any(f.verdict is Verdict.WILL_FAIL for f in report.findings), (
        "no Finding in the whole report is WILL_FAIL"
    )
    assert report.verdict is Verdict.UNKNOWN


# ---------------------------------------------------------------------------
# AC-10.3
# ---------------------------------------------------------------------------


def test_ac_10_3_will_fail_sited_in_tip_tracker(contracts_json: str) -> None:
    report = _check("aspirate_after_drop_graph", contracts_json)
    op3 = _findings_for(report, "op_3")  # the aspirate, third op (1-indexed)

    will_fail = [f for f in op3 if f.verdict is Verdict.WILL_FAIL]
    assert len(will_fail) == 1
    assert will_fail[0].category == "precondition_state"
    assert will_fail[0].plr_site == _GET_TIP_SITE
    assert report.verdict is Verdict.WILL_FAIL


# ---------------------------------------------------------------------------
# AC-10.4
# ---------------------------------------------------------------------------


def test_ac_10_4_shipped_fixture_unchanged(contracts_json: str) -> None:
    report = _check("simple_transfer_graph", contracts_json)
    assert report.verdict is Verdict.UNKNOWN
    assert all(f.verdict is Verdict.UNKNOWN for f in report.findings)
    # Pre-increment finding count over this fixture (measured against the
    # pre-increment-shaped contract table, AC-10.7's fixture, below) is the
    # same 38 -- asserted there, cross-checked here by equality.
    pre_contracts = (FIXTURES / "derived_contracts_pre_increment.json").read_text(encoding="utf-8")
    pre_report = _check("simple_transfer_graph", pre_contracts)
    assert len(report.findings) == len(pre_report.findings)
    assert not any(f.reason == "channel_state_unknown" for f in report.findings)


# ---------------------------------------------------------------------------
# AC-10.5 -- three variants, each asserting op_2 (the second pick_up_tips)
# has zero WILL_FAIL and zero SAFE findings, and the report stays UNKNOWN.
# ---------------------------------------------------------------------------


def _assert_widened(report: AnalysisReport) -> None:
    op2 = _findings_for(report, "op_2")
    assert not any(f.verdict is Verdict.WILL_FAIL for f in op2)
    assert not any(f.verdict is Verdict.SAFE for f in op2)
    assert report.verdict is Verdict.UNKNOWN


def test_ac_10_5a_widening_erases_foreach_source(contracts_json: str) -> None:
    graph = _graph("double_pickup_graph")
    graph["operations"][1]["foreach_source"] = "wells"
    graph["has_loops"] = True
    report = check_graph(json.dumps(graph), contracts_json)
    _assert_widened(report)


def test_ac_10_5b_widening_erases_depends_on_params(contracts_json: str) -> None:
    graph = _graph("double_pickup_graph")
    graph["operations"][1]["depends_on_params"] = ["n"]
    report = check_graph(json.dumps(graph), contracts_json)
    _assert_widened(report)


def test_ac_10_5c_widening_erases_bare_name_use_channels(contracts_json: str) -> None:
    graph = _graph("double_pickup_graph")
    graph["operations"][0]["arguments"]["use_channels"] = "channels"  # bare Name, not a literal
    report = check_graph(json.dumps(graph), contracts_json)
    _assert_widened(report)


# ---------------------------------------------------------------------------
# AC-10.6 -- unknown shapes widen: a non-null condition_expr, and a
# use_channels-disabler call anywhere on the receiver.
# ---------------------------------------------------------------------------


def test_ac_10_6_condition_expr_widens(contracts_json: str) -> None:
    graph = _graph("double_pickup_graph")
    graph["operations"][1]["condition_expr"] = "True"
    graph["has_conditionals"] = True
    report = check_graph(json.dumps(graph), contracts_json)
    _assert_widened(report)


def test_ac_10_6_disabler_call_widens(contracts_json: str) -> None:
    graph = _graph("double_pickup_graph")
    graph["operations"].append(
        {
            "arguments": {},
            "condition_expr": None,
            "creates_state": [],
            "depends_on_params": [],
            "false_branch": [],
            "foreach_body": [],
            "foreach_source": None,
            "id": "op_0",
            "line_number": 0,
            "method_name": "use_channels",
            "node_type": "static",
            "preconditions": [],
            "receiver_type": "LiquidHandler",
            "receiver_variable": "lh",
            "true_branch": [],
        }
    )
    graph["execution_order"] = ["op_0", "op_1", "op_2"]
    report = check_graph(json.dumps(graph), contracts_json)
    _assert_widened(report)


# ---------------------------------------------------------------------------
# AC-10.7
# ---------------------------------------------------------------------------


def test_ac_10_7_stale_contract_table_degrades(contracts_json: str) -> None:
    pre_contracts = (FIXTURES / "derived_contracts_pre_increment.json").read_text(encoding="utf-8")
    graph_json = (FIXTURES / "simple_transfer_graph.json").read_text(encoding="utf-8")
    payload = json.loads(pre_contracts)
    assert "receiver_state" not in payload
    for entry in payload["contracts"].values():
        assert "channel_guards" not in entry

    report = check_graph(graph_json, pre_contracts)  # must not raise
    assert report.verdict is Verdict.UNKNOWN
    assert len(report.findings) == 38
    round_tripped = json.loads(json.dumps({"verdict": report.verdict.value, "n": len(report.findings)}))
    assert round_tripped == {"verdict": "unknown", "n": 38}


# ---------------------------------------------------------------------------
# AC-10.8
# ---------------------------------------------------------------------------


def test_ac_10_8_empty_graph_unchanged(contracts_json: str) -> None:
    report = check_graph('{"protocol_fqn":"p","operations":[],"resources":{}}', contracts_json)
    assert report.verdict is Verdict.UNKNOWN
    assert report.findings == ()


# ---------------------------------------------------------------------------
# AC-10.9 -- derivation reproducibility (three sub-assertions).
# ---------------------------------------------------------------------------


def test_ac_10_9_derivation_reproducibility(contracts_json: str) -> None:
    payload = json.loads(contracts_json)
    lh = payload["receiver_state"]["LiquidHandler"]

    # Sub-assertion 1: block equality.
    assert lh["channel_attr"] == "head"
    assert lh["tracker_class"] == "TipTracker"
    assert lh["bool_view"]["field"] == "_pending_tip"
    assert lh["bool_view"]["attr"] == "has_tip"
    assert lh["bool_view"]["true_when"] == "not_none"
    assert lh["effects"]["add_tip"] == "HAS_TIP"
    assert lh["effects"]["remove_tip"] == "NO_TIP"
    assert sorted(lh["tip_state_exceptions"]) == ["HasTipError", "NoTipError"]


def test_ac_10_9_taxonomy_filter_is_checked() -> None:
    """Sub-assertion 2: the module filter is itself an AC-checked fact, not
    just its output.
    """
    taxonomy = json.loads(TAXONOMY_JSON_PATH.read_text(encoding="utf-8"))
    classes = taxonomy["classes"]
    tip_state_unfiltered = {c["name"] for c in classes if c.get("category") == "tip_state"}
    assert tip_state_unfiltered == {
        "HamiltonNoTipError",
        "HasTipError",
        "NoTipError",
        "TipAlreadyFittedError",
        "TipTooLittleVolumeError",
    }
    filtered = {
        c["name"]
        for c in classes
        if c.get("category") == "tip_state" and c.get("module") == "pylabrobot.resources.errors"
    }
    assert filtered == {"HasTipError", "NoTipError"}
    assert set(compute_tip_state_exceptions(classes)) == filtered


_FORBIDDEN_LITERALS = frozenset(
    {"TipTracker", "has_tip", "_pending_tip", "NoTipError", "HasTipError", "head", "setup"}
)  # "setup" added spec 260903 §12.1/AC-12.1(ii): P5's reset-method name must be read from PLR, not typed.
_TIPSTATE_SRC_FILES = (
    PLR_SEMA_ROOT / "src" / "plr_sema" / "check" / "tipstate.py",
    PLR_SEMA_ROOT / "src" / "plr_sema" / "derive" / "receiver_state.py",
)


def _docstring_constant_ids(tree: ast.AST) -> set[int]:
    ids: set[int] = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(body, list) and body:
            first = body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                ids.add(id(first.value))
    return ids


def _scan_hand_typed_literals(source: str, filename: str) -> list[str]:
    tree = ast.parse(source, filename=filename)
    docstring_ids = _docstring_constant_ids(tree)
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in _FORBIDDEN_LITERALS:
            if id(node) in docstring_ids:
                continue
            offenders.append(f"{filename}:{node.lineno}: {node.value!r}")
    return offenders


def test_ac_10_9_no_hand_typed_plr_names_ast_scan() -> None:
    """Sub-assertion 3: an AST LITERAL scan (not grep) of the tip-state
    modules under `plr_sema/src/` finds none of the six forbidden names as
    an `ast.Constant` string value -- reusing `test_verdict.py`'s own
    docstring-exclusion mechanism (a bare-``ast.walk`` `grep` cannot skip
    docstrings/comments; this scan can and does). The docstring-exclusion
    itself is demonstrated on a synthetic fixture that DOES put one of the
    forbidden names in a docstring, per §10.7's own note that this is what
    must be tested.
    """
    # -- The exclusion itself: a docstring containing "has_tip" is NOT a
    # violation; the identical string as a real string constant IS.
    docstring_case = (
        'def _f():\n'
        '    """This talks about has_tip in prose."""\n'
        '    return 1\n'
    )
    assert _scan_hand_typed_literals(docstring_case, "<synthetic:docstring>") == []

    literal_case = "X = 'has_tip'\n"
    offenders = _scan_hand_typed_literals(literal_case, "<synthetic:literal>")
    assert len(offenders) == 1

    module_docstring_case = '"""has_tip appears in the MODULE docstring."""\nY = 1\n'
    assert _scan_hand_typed_literals(module_docstring_case, "<synthetic:module-docstring>") == []

    # -- The real scan.
    all_offenders: list[str] = []
    for path in _TIPSTATE_SRC_FILES:
        all_offenders.extend(_scan_hand_typed_literals(path.read_text(encoding="utf-8"), str(path)))
    assert all_offenders == [], f"hand-typed PLR name(s) found: {all_offenders}"


# ---------------------------------------------------------------------------
# AC-10.10
# ---------------------------------------------------------------------------


def test_ac_10_10_family_selection_is_published(contracts_json: str) -> None:
    payload = json.loads(contracts_json)
    lh = payload["receiver_state"]["LiquidHandler"]
    contracts = payload["contracts"]

    from plr_sema.derive.receiver_state import ReceiverState, compute_tip_families

    rs = ReceiverState(
        channel_attr=lh["channel_attr"],
        tracker_class=lh["tracker_class"],
        tracker_module="pylabrobot.resources.tip_tracker",
        bool_view_attr=lh["bool_view"]["attr"],
        bool_view_field=lh["bool_view"]["field"],
        true_when=lh["bool_view"]["true_when"],
        state_fields=tuple(lh["state_fields"]),
        effects=lh["effects"],
        channel_default_param=lh["channel_default_param"],
        channel_default_disablers=tuple(lh["channel_default_disablers"]),
        tip_state_exceptions=tuple(lh["tip_state_exceptions"]),
    )
    families = compute_tip_families(contracts, receiver_class="LiquidHandler", receiver_state=rs)
    assert families.tip_loading and families.tip_requiring and families.tip_dropping
    assert "pick_up_tips" in families.tip_loading
    assert "aspirate" in families.tip_requiring
    assert "drop_tips" in families.tip_requiring and "drop_tips" in families.tip_dropping


# ---------------------------------------------------------------------------
# AC-12.1(i) -- the reset rule is derived and published, not asserted
# (spec 260903 §12.1). Sub-assertions (ii)/(iii)/(iv) are covered by this
# module's extended `_FORBIDDEN_LITERALS` scan (ii) and by test_derive.py
# (iii, iv), which exercise `reset_rule_candidates`/`derive_receiver_states`
# directly rather than through the shipped artifact.
# ---------------------------------------------------------------------------

GAP_LEDGER_JSON_PATH = REPO_ROOT / "plr-sema" / "data" / "gap_ledger.json"


def test_ac_12_1_i_entry_reset_is_derived_and_published(contracts_json: str) -> None:
    payload = json.loads(contracts_json)
    lh = payload["receiver_state"]["LiquidHandler"]
    assert lh["entry_reset"] == {"method": "setup", "post": "no_tip"}

    ledger = json.loads(GAP_LEDGER_JSON_PATH.read_text(encoding="utf-8"))
    assert ledger["tip_state"]["LiquidHandler"]["entry_reset"] == {"method": "setup", "post": "no_tip"}


# ---------------------------------------------------------------------------
# AC-12.2 -- entry state fires only on an OBSERVED reset, both directions
# (spec 260903 §12.1.5).
# ---------------------------------------------------------------------------


def test_ac_12_2_a_will_fail_after_observed_setup(contracts_json: str) -> None:
    """(a): `setup()` then `aspirate(use_channels=[0])` -- exactly one
    `WILL_FAIL` `Finding` in the whole report, sited at the bridged
    `TipTracker.get_tip` `NoTipError` guard. `setup`'s own guard (`if
    self.setup_finished: raise RuntimeError`, A-RESET-ONCE) does not parse
    as a tip-state atom and so still emits its own (`UNKNOWN`,
    `guard_predicate_unparsed`) finding on `op_1` -- filtering to
    `Verdict.WILL_FAIL` (as (b)/(c) below already do for their own
    zero-count assertions) is what "exactly one" is checked over, not a
    bare `len(report.findings) == 1`.
    """
    report = _check("setup_then_aspirate_graph", contracts_json)
    will_fail = [f for f in report.findings if f.verdict is Verdict.WILL_FAIL]
    assert len(will_fail) == 1
    (finding,) = will_fail
    assert finding.operation_id == "op_2"
    assert finding.category == "precondition_state"
    assert finding.plr_site == _GET_TIP_SITE
    assert report.verdict is Verdict.WILL_FAIL


def test_ac_12_2_b_no_setup_stays_unknown(contracts_json: str) -> None:
    """(b), the stub-defeating half: the identical `aspirate` with no
    preceding `setup()` yields zero `WILL_FAIL` and zero `SAFE` findings
    over the whole report -- an implementation that seeds `NO_TIP` at
    graph entry (instead of only on an observed reset `CALL`) would pass
    (a) and fail this.
    """
    report = _check("aspirate_no_setup_graph", contracts_json)
    assert not [f for f in report.findings if f.verdict is Verdict.WILL_FAIL]
    assert not [f for f in report.findings if f.verdict is Verdict.SAFE]
    assert report.verdict is Verdict.UNKNOWN


def test_ac_12_2_c_stale_contract_table_degrades_without_raising(contracts_json: str) -> None:
    """(c): fixture (a) against a contract table with no `entry_reset` key
    must not raise, and must degrade to (b)'s behaviour for the tip-state
    question -- read via `.get()` with an empty default (AC-12.2's own
    "fires only on an observed reset" claim depends on this NOT crashing
    on a pre-increment table). Fixture (a) additionally contains the
    `setup` operation itself (deleted in (b)), so the two reports are not
    byte-identical as a whole; the equality this asserts is scoped to (i)
    the report-level verdict and (ii) the `aspirate` operation's own
    findings, which is the tip-state-relevant surface (b) has no
    counterpart operation to diverge on.
    """
    payload = json.loads(contracts_json)
    del payload["receiver_state"]["LiquidHandler"]["entry_reset"]
    stale_contracts_json = json.dumps(payload)

    report_a_stale = check_graph(
        (FIXTURES / "setup_then_aspirate_graph.json").read_text(encoding="utf-8"), stale_contracts_json
    )  # must not raise
    report_b = _check("aspirate_no_setup_graph", contracts_json)

    assert report_a_stale.verdict is Verdict.UNKNOWN
    assert report_b.verdict is Verdict.UNKNOWN

    def _aspirate_shape(report: AnalysisReport) -> list[tuple[str, str, str, str]]:
        return sorted(
            (f.verdict.value, f.category, f.reason, f.detail) for f in _findings_for(report, "op_2")
        )

    assert _aspirate_shape(report_a_stale) == _aspirate_shape(report_b)
