"""plr_sema.check: the browser-side checker (spec 260901 §6).

**Packaging fact, not a convention.** ``libcst`` ships a Rust native
extension unavailable under Pyodide; importing ``pylabrobot`` to check a
protocol would defeat the point of a static analyzer that runs before the
environment exists. So `check/` (this package) imports NEITHER -- mechanised
by ``tests/test_import_boundary.py::test_no_pylabrobot_import_under_check``
and demonstrated by poisoning both to ``None`` in ``sys.modules`` (AC-6.1).
It also never imports ``pydantic`` (§6.2) -- see ``check/graph.py``'s stdlib
mirror -- and never shells out (no ``git``, no subprocess): the
``SurveyStamp`` an ``AnalysisReport`` carries is deserialized from whatever
the derived-contracts payload already recorded at build time, not
recomputed.

**Round-1 entry point: ``check_graph(graph_json, contracts_json) ->
AnalysisReport``.** Takes two JSON *strings* (matching the ``_json`` naming
and the fact that this function's whole job starts with ``json.loads`` --
neither argument is a pre-parsed dict). ``graph_json`` is the wire format a
(round-2) ``extract/`` would produce, or -- in round 1 -- the committed
fixture generated out-of-process (§6.2, T8; see
``tests/fixtures/simple_transfer_graph.json`` and
``tests/test_check_graph.py``). ``contracts_json`` is
``plr-sema/data/derived_contracts.json`` (§7.3), the build artifact
``plr_sema.derive`` regenerates from the survey.

**Every v1 verdict is UNKNOWN (§0, §7.4's forward hazard).** This module
never constructs a ``SAFE`` or ``WILL_FAIL`` ``Finding`` -- §7.4 names the
soundness fence a future round must build before the first ``SAFE`` is ever
emitted, and this module does not attempt to build it. Findings are produced
purely from *derivation-mechanical* facts (§0.2): which pipeline stage
returned nothing for this operation, never a semantic claim about why.

**Per-operation reason logic (mechanics only, no new classification).
Redefined 260901 T11 -- see "unsupported_tool, redefined" below:**

1. ``op.receiver_type is None`` -> ``receiver_type_unknown`` (no contract
   lookup is even attempted -- there is no key to look up).
2. ``f"{op.receiver_type}.{op.method_name}"`` absent from the contract table
   -> ``unsupported_tool``.
3. Otherwise, the resolved ``DerivedContract`` (§7.2/§7.3) is walked:
   * every recorded gap (``unresolved_delegate`` / ``no_contract_derived``,
     the only two ``plr_sema.derive`` ever emits, §7.2) becomes one Finding
     with that same reason;
   * every guard becomes one ``guard_predicate_unparsed`` Finding (§3.3: "a
     guard condition string could not be turned into a predicate"), which is
     unconditionally true in v1 since no predicate parser exists yet.
     (Round-4 remediation, B4: this used to branch to the more specific
     ``argument_not_static`` when a guard's ``free_vars`` intersected
     ``op.depends_on_params``, but that reason has been withdrawn from
     ``REASON_VOCABULARY`` -- the guard-free-var namespace and the
     protocol-parameter namespace it was meant to intersect are disjoint in
     every shipped fixture, so the branch never fired, and a same-named
     collision would have fired it for no semantic cause. See
     ``plr_sema.verdict.REASON_VOCABULARY``'s docstring for the reinstatement
     path.)
   * an operation whose ``foreach_source``/``foreach_body`` is populated
     additionally gets one ``loop_bounds_unknown`` Finding (§3.3: these
     fields identify the loop construct, never its bounds -- bounds are
     deferred item (d)).

**``unsupported_tool``, redefined (260901 T11).** Before T11, step 2 read
``op.method_name not in SUPPORTED_TOOLS`` -- the analyzer's scope was
identical to the dynamic execution harness's 10-tool capability boundary
(``training.verify.dispatcher.SUPPORTED_TOOLS``), because the derived
contract table only ever held entries for those 10 methods, so the two
checks were redundant. T11 decouples derivation from ``SUPPORTED_TOOLS``
(``plr_sema.derive`` now derives a contract for every one of the whole
survey's 4,770 methods, not just the 10 -- see
``plr_sema.derive.__main__.build_derived_contracts_payload``), so the two
checks are no longer redundant, and keeping the ``SUPPORTED_TOOLS`` gate
would have re-imposed the 10-method scope this whole task exists to remove.
``unsupported_tool`` is therefore now defined purely in terms of the
contract table this module actually has in hand: **"key absent from the
contract table"**, i.e. "not resolvable to any method the whole-surface
derivation analyzed" -- not "outside a hand-maintained 10-name allowlist".
``SUPPORTED_TOOLS`` itself is UNCHANGED and still imported/re-exported here
(``__all__``) for ``test_supported_tools_match_upstream`` (AC-6.5) -- it
remains a real thing, just a DIFFERENT boundary now: the dynamic execution
harness's own capability limit (``verify.dispatcher``), which this static
analyzer no longer shares or gates on.

Because the contract table now spans the whole survey rather than only
finding-bearing methods (T11 item 4's zero-findings decision -- see
``build_derived_contracts_payload``'s docstring), a method the survey
scanned but recorded zero ``PreconditionFinding``s for ("known and
unconstrained") gets a real, present, EMPTY contract entry (``guards: []``,
``gaps: []``) rather than an absent key -- so it resolves via step 3 below,
not ``unsupported_tool``, and falls through to the zero-guards/zero-gaps
fallback described next. ``unsupported_tool`` now fires only for a method
name the whole-survey derivation never saw at all: genuinely not part of
the analyzed PLR surface (a typo, a non-PLR receiver, or PLR relocating/
renaming something between the pin the contracts were derived against and
the graph being checked).

**A resolved contract with zero guards, zero gaps, and no loop now
synthesizes one fallback ``no_contract_derived`` Finding (round-4
remediation, B1/B2/§0(ii); this is also T11's answer for the "known,
zero-own-findings, empty-closure" case above -- 2,178 of the 3,456
zero-finding methods at the current pin).** Before round-4's fix, that
combination fell through to an empty finding list for the operation, and --
if it happened for *every* operation in a graph -- ``join(())`` would
return the pre-fix ``SAFE`` default, a live soundness bug on a reachable
public path (a graph with zero operations reaches it trivially; a
resolved-but-empty contract also reaches it). This never fired against the
pre-T11 ``derived_contracts.json`` (all ten ``SUPPORTED_TOOLS`` entries
carried >=1 guard), which is exactly why it went unnoticed then -- the data
never exercised the gap; it fires routinely now that the whole surface
(including genuinely unconstrained methods) is derived. ``join`` (spec
§3.2) now independently treats the empty multiset as UNKNOWN regardless, so
this fallback is defense in depth, not the sole fix -- see
``plr_sema.verdict.join``'s docstring.
"""

from __future__ import annotations

import json
from typing import Any

from plr_sema._provenance import SurveyStamp
from plr_sema._provenance.git_state import GitState
from plr_sema.check._supported_tools import SUPPORTED_TOOLS
from plr_sema.check.graph import OperationNode, ProtocolComputationGraph, parse_graph
from plr_sema.telemetry import emit_finding
from plr_sema.verdict import AnalysisReport, Finding, PlrSite, Verdict, join

__all__ = ["SUPPORTED_TOOLS", "check_graph"]


def _git_state_from_dict(d: dict[str, Any]) -> GitState:
    return GitState(
        hash=d["hash"],
        branch=d["branch"],
        dirty=d["dirty"],
        dirty_content_id=d.get("dirty_content_id"),
        provenance_source=d.get("provenance_source", "git"),
        toplevel=d.get("toplevel"),
    )


def _stamp_from_dict(d: dict[str, Any]) -> SurveyStamp:
    """Reconstruct the ``SurveyStamp`` a derived-contracts payload already
    recorded at build time (§2.2/§7.3) -- ``check/`` never shells out to
    compute a fresh one (module docstring)."""
    return SurveyStamp(
        plr=_git_state_from_dict(d["plr"]),
        praxis=_git_state_from_dict(d["praxis"]),
        pylabrobot_version=d.get("pylabrobot_version"),
        stamped_at=d["stamped_at"],
        schema_version=d.get("schema_version", 1),
        # T13 (260901, backlog #4859): additive -- absent in any pre-T13
        # payload, defaults to DEFAULT_SURFACE's own name/pin.
        surface=d.get("surface", "legacy_pinned"),
        surface_pin=d.get("surface_pin"),
    )


def _plr_site_from_dict(d: dict[str, Any] | None) -> PlrSite | None:
    if d is None:
        return None
    return PlrSite(file=d["file"], lineno=d["lineno"], qualname=d["qualname"])


# ---------------------------------------------------------------------------
# §3.3/§3.4's AST-resolvable-reason requirement: `Finding(..., reason=...)`
# must resolve to a string literal or a module-level constant reference at
# EACH call site -- a bare local variable or function parameter fails the
# scan (`test_reason_vocabulary_closed_{forward,reverse}`), even if the
# value it carries at runtime is always a REASON_VOCABULARY member. A single
# shared helper taking `reason: str` as a parameter (the natural-looking
# design) would therefore FAIL both tests, since the `reason=reason` inside
# such a helper is exactly the rejected bare-local-variable form. Each
# REASON_VOCABULARY member below gets its own tiny constructor with the
# literal string written directly into its one `Finding(...)` call.
# ---------------------------------------------------------------------------


def _receiver_type_unknown(op: OperationNode) -> Finding:
    return Finding(
        verdict=Verdict.UNKNOWN,
        operation_id=op.id,
        category="",
        plr_site=None,
        reason="receiver_type_unknown",
    )


def _unsupported_tool(op: OperationNode) -> Finding:
    return Finding(
        verdict=Verdict.UNKNOWN,
        operation_id=op.id,
        category="",
        plr_site=None,
        reason="unsupported_tool",
    )


def _no_contract_derived(op: OperationNode, *, detail: str = "") -> Finding:
    return Finding(
        verdict=Verdict.UNKNOWN,
        operation_id=op.id,
        category="",
        plr_site=None,
        reason="no_contract_derived",
        detail=detail,
    )


def _unresolved_delegate(op: OperationNode, *, detail: str = "") -> Finding:
    return Finding(
        verdict=Verdict.UNKNOWN,
        operation_id=op.id,
        category="",
        plr_site=None,
        reason="unresolved_delegate",
        detail=detail,
    )


def _guard_predicate_unparsed(
    op: OperationNode, *, plr_site: PlrSite | None, detail: str = ""
) -> Finding:
    return Finding(
        verdict=Verdict.UNKNOWN,
        operation_id=op.id,
        category="",
        plr_site=plr_site,
        reason="guard_predicate_unparsed",
        detail=detail,
    )


def _loop_bounds_unknown(op: OperationNode) -> Finding:
    return Finding(
        verdict=Verdict.UNKNOWN,
        operation_id=op.id,
        category="",
        plr_site=None,
        reason="loop_bounds_unknown",
    )


def _internal_error(op: OperationNode, *, detail: str = "") -> Finding:
    """Defensive fallback: a gap reason surfacing from
    ``derived_contracts.json`` that is neither of the two
    ``plr_sema.derive`` ever emits (``no_contract_derived`` /
    ``unresolved_delegate``, §7.2) would itself be a drift between
    ``plr_sema.derive`` and ``plr_sema.check``, not a fact about PLR --
    exactly what ``internal_error`` (§3.3: "analyzer bug; always paired with
    a telemetry emit") exists for."""
    return Finding(
        verdict=Verdict.UNKNOWN,
        operation_id=op.id,
        category="",
        plr_site=None,
        reason="internal_error",
        detail=detail,
    )


def _finding_from_guard(op: OperationNode, guard: dict[str, Any]) -> Finding:
    """Every guard becomes a ``guard_predicate_unparsed`` Finding in v1
    (round-4 remediation, B4: the former ``argument_not_static`` branch --
    which fired when a guard's ``free_vars`` intersected
    ``op.depends_on_params`` -- has been withdrawn from ``REASON_VOCABULARY``
    and is no longer constructed anywhere; see the module docstring).

    ``detail`` (round-4 remediation, m5): ``guard["condition"]`` being
    ``None`` means the guard fires UNCONDITIONALLY -- the predicate is
    ``TRUE``, not "no constraint" (§7.2's ``InlinedGuard.condition``: raw,
    unparsed strings, and ``None`` is a real value the survey emits, not a
    missing-field sentinel). The prior ``guard.get("condition") or ""``
    mapped BOTH ``None`` and an empty-string condition to ``detail = ""``,
    making the two indistinguishable in the emitted Finding -- unsound in
    the ``SAFE`` direction, and not merely cosmetic: 379 of 2,814 (13.5%) of
    survey findings, and 9 of the 119 guards in the shipped contract table,
    carry ``condition: null``. ``None`` now maps to the explicit sentinel
    string ``"<unconditional>"`` instead of being collapsed into ``""``."""
    plr_site = _plr_site_from_dict(guard.get("site"))
    condition = guard.get("condition")
    detail = condition if condition is not None else "<unconditional>"
    return _guard_predicate_unparsed(op, plr_site=plr_site, detail=detail)


def _findings_for_gap(op: OperationNode, gap: Any) -> Finding:
    gap_reason, gap_name = gap[0], gap[1]
    if gap_reason == "unresolved_delegate":
        return _unresolved_delegate(op, detail=gap_name)
    if gap_reason == "no_contract_derived":
        return _no_contract_derived(op, detail=gap_name)
    return _internal_error(op, detail=f"unrecognized gap reason {gap_reason!r} for {gap_name!r}")


def _findings_for_operation(op: OperationNode, contracts: dict[str, Any]) -> list[Finding]:
    """T11: step 2 is now a single contract-table lookup, not a
    ``SUPPORTED_TOOLS`` membership test followed by a second lookup -- see
    the module docstring's "``unsupported_tool``, redefined" section. A key
    absent from ``contracts`` now means "the whole-survey derivation never
    saw this method at all", not "outside the old 10-name allowlist"."""
    if op.receiver_type is None:
        return [_receiver_type_unknown(op)]

    key = f"{op.receiver_type}.{op.method_name}"
    contract = contracts.get(key)
    if contract is None:
        return [_unsupported_tool(op)]

    findings: list[Finding] = [_findings_for_gap(op, gap) for gap in contract.get("gaps", ())]
    findings.extend(_finding_from_guard(op, guard) for guard in contract.get("guards", ()))
    if op.foreach_source is not None or op.foreach_body:
        findings.append(_loop_bounds_unknown(op))
    if not findings:
        # Round-4 remediation (B1/B2/§0(ii)): a resolved contract with zero
        # guards, zero gaps, and no loop must not silently produce an empty
        # finding list -- see the module docstring's note on why this was a
        # live soundness gap, not a deferred one.
        findings.append(
            _no_contract_derived(
                op, detail="contract resolved with zero guards, zero gaps and no loop"
            )
        )
    return findings


def _check(graph: ProtocolComputationGraph, contracts_payload: dict[str, Any]) -> AnalysisReport:
    contracts = contracts_payload.get("contracts", {})
    stamp = _stamp_from_dict(contracts_payload["stamp"])

    findings: list[Finding] = []
    for op in graph.operations:
        findings.extend(_findings_for_operation(op, contracts))

    report = AnalysisReport(
        protocol_fqn=graph.protocol_fqn,
        verdict=join(tuple(findings)),
        findings=tuple(findings),
        stamp=stamp,
    )
    # Round-4 remediation (M2): check_graph now actually emits telemetry --
    # previously nothing under check/ ever called plr_sema.telemetry.emit*,
    # despite §3.3:444's "internal_error ... always paired with a telemetry
    # emit" claim. Emitting every finding here (not just internal_error's)
    # makes that claim true for every reason, not just one -- emit() is a
    # process-global no-op by default (spec §4.1's AC-4.4), so this costs
    # nothing when no sink is attached.
    for finding in report.findings:
        emit_finding(finding, protocol_fqn=report.protocol_fqn, stamp=report.stamp)
    return report


def check_graph(graph_json: str, contracts_json: str) -> AnalysisReport:
    """Round-1 entry point (spec §6.2). ``graph_json``/``contracts_json`` are
    JSON strings, not pre-parsed objects -- both are ``json.loads``'d here
    and nowhere else. Never imports ``libcst``/``pylabrobot``/``pydantic``;
    never shells out. Emits every finding via ``plr_sema.telemetry`` (M2,
    round-4 remediation) -- a no-op unless a sink is attached (§4.1)."""
    graph = parse_graph(json.loads(graph_json))
    contracts_payload = json.loads(contracts_json)
    return _check(graph, contracts_payload)
