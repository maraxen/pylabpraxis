"""Oracle replay tier 1 (T16b): corpus evaluation with measurement fixes (#4879).

Run the PLR chatterbox simulator (ground truth) and plr-sema's static analyzer
in parallel against rows from corpus_p25.jsonl + golden_pairs.jsonl, with proper
measurement of: rows_total, rows_no_call (clarifications), rows_skipped
(unfixable via preconditions), rows_executed (actually ran), operations_executed.

Per-row output: {record_id, source_file, line, utterance, calls[], skip_reason,
no_call_reason, runtime {outcome, error, exc_class}, static verdicts, compare[],
intent_check_failures[], totality_ok, check_graph_raised}.

Summary: unsound count, agreement matrix (runtime × static), per-method unknown%,
exception ranking split by PLR vs harness category, precondition_state ranking,
crosscheck content-join results.
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import hashlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from oracle_common import (
    DEFAULT_CONTRACTS,
    RuntimeOutcome,
    adapt_graph,
    compare,
    row_to_verifier_inputs,
    run_runtime,
    run_static,
)

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _classify_exception(exc_class: str | None) -> str:
    """Classify an exception into PLR vs harness category.

    PLR exceptions: NoTipError, HasTipError, TooLittleLiquidError,
    TooLittleVolumeError, BlowOutVolumeError, ValueError (from PLR).

    Harness/dispatcher exceptions: GroundingError, DispatchError, TypeError,
    AttributeError, etc.
    """
    if not exc_class:
        return "none"
    # PLR precondition-state exceptions
    if exc_class in ("NoTipError", "HasTipError", "TooLittleLiquidError",
                     "TooLittleVolumeError", "BlowOutVolumeError"):
        return "precondition_state"
    # Dispatcher grounding errors
    if exc_class == "GroundingError":
        return "ungroundable_reference"
    if exc_class == "DispatchError":
        return "unsupported_tool"
    # Other harness errors
    return "harness_error"


def _extract_utterance_and_call(row: dict[str, Any]) -> tuple[str, str]:
    """Extract utterance and first call name from a row.

    Handles corpus format (messages) and crosscheck formats (floor: utterance,
    overlay: instruction).
    """
    utterance = ""
    call_name = ""

    # Corpus format (messages)
    for msg in row.get("messages", []):
        if msg.get("role") == "user":
            utterance = msg.get("content", "")
        elif msg.get("role") == "assistant":
            tool_calls = msg.get("tool_calls", [])
            if tool_calls:
                call_name = tool_calls[0].get("function", {}).get("name", "")
                break

    # Floor format (utterance + structured_calls)
    if not utterance and "structured_calls" in row:
        utterance = row.get("utterance", "")
        calls = row.get("structured_calls", [])
        if calls:
            call_name = calls[0].get("name", "")

    # Overlay format (instruction + call)
    if not utterance and "instruction" in row:
        utterance = row.get("instruction", "")
        call_info = row.get("call", {})
        if isinstance(call_info, dict):
            call_name = call_info.get("name", "")
        elif isinstance(call_info, str):
            call_name = call_info

    return utterance, call_name


@dataclasses.dataclass
class RowResult:
    """Result for one row."""
    record_id: str
    corpus_file: str
    row_index: int
    utterance: str
    call_names: list[str]  # names of all calls in call_sequence
    scaffold_prefix_count: int  # number of prefix calls added
    no_call_reason: str | None
    skip_reason: str | None
    n_operations_executed: int
    runtime_outcome: str  # "no_call", "skipped:<reason>", "ran_ok", "raised:<Class>", "not_reached", "setup_error"
    runtime_error: str | None
    runtime_exc_class: str | None
    static_verdicts: dict[str, str]  # op_i -> verdict string (only executed ops)
    n_findings: int  # total across all executed ops
    compare_rows: list[dict[str, Any]]  # only executed ops
    check_graph_raised: bool
    check_graph_exception: str | None
    intent_check_failures: list[dict[str, Any]]
    totality_ok: bool
    unsound_count: int
    plr_kwargs: dict[int, dict[str, Any]]  # PLR-named arguments by call index
    tool_params: dict[str, dict[str, Any]]  # tool parameter names by op_id


def run_row(
    row: dict[str, Any],
    corpus_file: str,
    row_index: int,
    contracts_json: str,
) -> RowResult:
    """Process one corpus row: runtime + static + compare.

    Catch exceptions and record them, don't crash the harness.
    """
    # Parse row into verifier inputs
    try:
        call_sequence, intent_record, deck_layout, skip_reason, no_call_reason = row_to_verifier_inputs(
            row, source_file=Path(corpus_file).stem, line=row_index
        )
    except Exception as e:
        log.warning("Failed to parse row %s:%d: %s", corpus_file, row_index, e)
        return RowResult(
            record_id=f"{corpus_file}:{row_index}",
            corpus_file=corpus_file,
            row_index=row_index,
            utterance="",
            call_names=[],
            scaffold_prefix_count=0,
            no_call_reason="parse_error",
            skip_reason=None,
            n_operations_executed=0,
            runtime_outcome="setup_error",
            runtime_error=f"parse:{e}",
            runtime_exc_class="ParseError",
            static_verdicts={},
            n_findings=0,
            compare_rows=[],
            check_graph_raised=False,
            check_graph_exception="parse error",
            intent_check_failures=[],
            totality_ok=True,
            unsound_count=0,
            plr_kwargs={},
            tool_params={},
        )

    record_id = intent_record.get("record_id", f"{corpus_file}:{row_index}")
    utterance = intent_record.get("utterance", "")
    call_names = [c["name"] for c in call_sequence]

    # If no_call_reason, skip execution
    if no_call_reason:
        return RowResult(
            record_id=record_id,
            corpus_file=corpus_file,
            row_index=row_index,
            utterance=utterance,
            call_names=call_names,
            scaffold_prefix_count=0,
            no_call_reason=no_call_reason,
            skip_reason=None,
            n_operations_executed=0,
            runtime_outcome="no_call",
            runtime_error=None,
            runtime_exc_class=None,
            static_verdicts={},
            n_findings=0,
            compare_rows=[],
            check_graph_raised=False,
            check_graph_exception=None,
            intent_check_failures=[],
            totality_ok=True,
            unsound_count=0,
            plr_kwargs={},
            tool_params={},
        )

    # If skipped, return skipped outcome
    if skip_reason:
        return RowResult(
            record_id=record_id,
            corpus_file=corpus_file,
            row_index=row_index,
            utterance=utterance,
            call_names=call_names,
            scaffold_prefix_count=0,
            no_call_reason=None,
            skip_reason=skip_reason,
            n_operations_executed=0,
            runtime_outcome=f"skipped:{skip_reason.split()[0]}",  # first word of reason
            runtime_error=None,
            runtime_exc_class=None,
            static_verdicts={},
            n_findings=0,
            compare_rows=[],
            check_graph_raised=False,
            check_graph_exception=None,
            intent_check_failures=[],
            totality_ok=True,
            unsound_count=0,
            plr_kwargs={},
            tool_params={},
        )

    # Reconstruct example dict for spike functions
    example = {
        "call_sequence": call_sequence,
        "intent_record": intent_record,
        "deck_layout": deck_layout,
    }

    # Runtime
    try:
        rt = run_runtime(example)
    except Exception as e:
        log.warning("Runtime failed for %s: %s", record_id, e)
        rt = RuntimeOutcome(
            error=f"runtime_harness:{e}",
            exc_class="RuntimeError",
            failing_index=None,
            planned_indices=[],
            passed=False,
        )

    # Map runtime outcome to string
    if rt.error is None:
        runtime_outcome = "ran_ok"
    elif rt.failing_index is None:
        runtime_outcome = "not_reached(setup_error)"
    else:
        runtime_outcome = f"raised:{rt.exc_class}"

    # Static
    check_graph_raised = False
    check_graph_exception = None
    static_verdicts = {}
    n_findings = 0
    tool_params_dict = {}
    try:
        graph = adapt_graph(example, f"corpus.{Path(corpus_file).stem}.{row_index}", rt.plr_kwargs)
        st = run_static(graph, contracts_json)
        static_verdicts = {oid: sdata["verdict"] for oid, sdata in st.items()}
        n_findings = sum(sdata["n_findings"] for sdata in st.values())
        # Capture tool params for per-row record
        for op in graph["operations"]:
            tool_params_dict[op["id"]] = op.get("arguments", {})
    except Exception as e:
        log.warning("Static analysis failed for %s: %s", record_id, e)
        check_graph_raised = True
        check_graph_exception = f"{type(e).__name__}: {e}"

    # Compare (only if both runtime and static succeeded)
    compare_rows = []
    unsound_count = 0
    if static_verdicts:
        try:
            compare_rows = compare(example, rt, st)
            unsound_count = sum(r["unsound"] for r in compare_rows)
        except Exception as e:
            log.warning("Compare failed for %s: %s", record_id, e)

    # Totality check
    totality_ok = len(call_sequence) == 0 or n_findings >= len(call_sequence)

    return RowResult(
        record_id=record_id,
        corpus_file=corpus_file,
        row_index=row_index,
        utterance=utterance,
        call_names=call_names,
        scaffold_prefix_count=len(call_sequence) - 1 if len(call_sequence) > 0 else 0,
        no_call_reason=None,
        skip_reason=None,
        n_operations_executed=len(call_sequence),
        runtime_outcome=runtime_outcome,
        runtime_error=rt.error,
        runtime_exc_class=rt.exc_class,
        static_verdicts=static_verdicts,
        n_findings=n_findings,
        compare_rows=compare_rows,
        check_graph_raised=check_graph_raised,
        check_graph_exception=check_graph_exception,
        intent_check_failures=[],
        totality_ok=totality_ok,
        unsound_count=unsound_count,
        plr_kwargs=rt.plr_kwargs,
        tool_params=tool_params_dict,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--corpus", type=str, action="append", required=True,
                    help="corpus JSONL file (repeatable)")
    ap.add_argument("--contracts", type=Path, default=DEFAULT_CONTRACTS,
                    help="contract table JSON")
    ap.add_argument("--crosscheck", type=str, action="append", default=[],
                    help="floor/overlay file for comparison (repeatable)")
    ap.add_argument("--report", type=Path, required=True,
                    help="JSON report output")
    ap.add_argument("--limit", type=int, default=None,
                    help="smoke-test limit (rows to process)")
    args = ap.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(message)s",
    )

    # Load contracts
    contracts_json = args.contracts.read_text(encoding="utf-8")

    # Load crosscheck by (utterance, call_name)
    crosscheck_by_content: dict[tuple[str, str], dict[str, Any]] = {}
    for cc_file in args.crosscheck:
        try:
            with open(cc_file) as f:
                for line in f:
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    utterance, call_name = _extract_utterance_and_call(row)
                    if utterance and call_name:
                        key = (utterance, call_name)
                        # Prefer earlier rows if duplicates exist
                        if key not in crosscheck_by_content:
                            crosscheck_by_content[key] = row
        except Exception as e:
            log.warning("Failed to load crosscheck file %s: %s", cc_file, e)
    log.info("Loaded %d crosscheck entries by (utterance, call_name)", len(crosscheck_by_content))

    # Process corpus files
    results: list[RowResult] = []
    n_rows_total = 0
    n_rows_no_call = 0
    n_rows_skipped = 0
    n_rows_executed = 0

    for corpus_file in args.corpus:
        try:
            with open(corpus_file) as f:
                for line_no, line in enumerate(f, 1):
                    if args.limit and n_rows_total >= args.limit:
                        break
                    if not line.strip():
                        continue
                    try:
                        row = json.loads(line)
                    except Exception as e:
                        log.warning("Failed to parse JSON at %s:%d: %s", corpus_file, line_no, e)
                        continue
                    result = run_row(row, corpus_file, line_no, contracts_json)
                    results.append(result)
                    n_rows_total += 1
                    if result.no_call_reason:
                        n_rows_no_call += 1
                    elif result.skip_reason:
                        n_rows_skipped += 1
                    else:
                        n_rows_executed += 1
                    if n_rows_total % 100 == 0:
                        log.info("Processed %d rows (no_call=%d, skipped=%d, executed=%d)...",
                                 n_rows_total, n_rows_no_call, n_rows_skipped, n_rows_executed)
        except Exception as e:
            log.warning("Failed to process corpus file %s: %s", corpus_file, e)

    # Compute summary statistics (only on executed rows)
    executed_results = [r for r in results if not r.no_call_reason and not r.skip_reason]
    n_unsound = sum(r.unsound_count for r in executed_results)
    n_totality_violations = sum(1 for r in executed_results if not r.totality_ok)
    n_check_graph_exceptions = sum(1 for r in executed_results if r.check_graph_raised)
    n_operations_executed = sum(r.n_operations_executed for r in executed_results)

    # Agreement matrix: runtime outcome × static verdict (executed rows only)
    agreement_matrix = collections.defaultdict(lambda: collections.Counter())
    for r in executed_results:
        if not r.compare_rows:
            continue
        for comp in r.compare_rows:
            outcome = comp["runtime"]
            verdict = comp["static"]
            agreement_matrix[outcome][verdict] += 1

    # Unknown rate by method
    method_unknown_rate: dict[str, float] = {}
    method_counts: dict[str, int] = collections.defaultdict(int)
    method_unknown: dict[str, int] = collections.defaultdict(int)
    for r in executed_results:
        for comp in r.compare_rows:
            method = comp["method"]
            method_counts[method] += 1
            if comp["static"] == "unknown":
                method_unknown[method] += 1
    for method in method_counts:
        method_unknown_rate[method] = method_unknown[method] / method_counts[method] if method_counts[method] > 0 else 0.0

    # Exception ranking by category
    exc_counter: dict[str, int] = collections.Counter()
    exc_category_counter: dict[str, int] = collections.Counter()
    exc_methods: dict[str, set[str]] = collections.defaultdict(set)
    precondition_exceptions: dict[str, int] = collections.Counter()
    for r in executed_results:
        if r.runtime_exc_class:
            exc_counter[r.runtime_exc_class] += 1
            category = _classify_exception(r.runtime_exc_class)
            exc_category_counter[category] += 1
            for call_name in r.call_names:
                exc_methods[r.runtime_exc_class].add(call_name)
            if category == "precondition_state":
                precondition_exceptions[r.runtime_exc_class] += 1

    exception_ranking = [
        {"class": exc, "count": count, "raised_on_methods": sorted(exc_methods[exc])}
        for exc, count in exc_counter.most_common()
    ]
    precondition_ranking = [
        {"class": exc, "count": count}
        for exc, count in precondition_exceptions.most_common()
    ]

    # Category breakdown
    category_breakdown = dict(exc_category_counter)

    # Crosscheck: content-based join (utterance, first_call_name)
    crosscheck_result = {"joined": 0, "agree": 0, "disagree": 0, "examples": []}
    for r in executed_results:
        first_call = r.call_names[0] if r.call_names else ""
        if not first_call:
            continue
        key = (r.utterance, first_call)
        cc_row = crosscheck_by_content.get(key)
        if not cc_row:
            continue
        crosscheck_result["joined"] += 1
        cc_passed = cc_row.get("execution_verify", {}).get("passed")
        our_passed = r.runtime_outcome == "ran_ok"
        if cc_passed == our_passed:
            crosscheck_result["agree"] += 1
        else:
            crosscheck_result["disagree"] += 1
            if len(crosscheck_result["examples"]) < 10:
                cc_error = cc_row.get("execution_verify", {}).get("error")
                crosscheck_result["examples"].append({
                    "utterance": r.utterance[:60],
                    "call": first_call,
                    "our_outcome": r.runtime_outcome,
                    "our_error": r.runtime_error,
                    "recorded_outcome": "passed" if cc_passed else "failed",
                    "recorded_error": cc_error[:100] if cc_error else None,
                    "is_plate_tracker_error": "'Plate' object has no attribute 'tracker'" in (r.runtime_error or ""),
                })

    # Compute global unknown_rate
    total_unknown_ops = sum(
        sum(1 for comp in r.compare_rows if comp["static"] == "unknown")
        for r in executed_results
    )
    global_unknown_rate = total_unknown_ops / n_operations_executed if n_operations_executed > 0 else 0.0

    # Crosscheck agreement rate
    cc_joined = crosscheck_result["joined"]
    cc_agreement_rate = (
        crosscheck_result["agree"] / cc_joined if cc_joined > 0 else 0.0
    )

    # Flat summary for bathos/BTH_RESULTS_PATH
    summary_flat = {
        "rows_total": n_rows_total,
        "rows_no_call": n_rows_no_call,
        "rows_skipped": n_rows_skipped,
        "rows_executed": n_rows_executed,
        "operations_executed": n_operations_executed,
        "unsound": n_unsound,
        "check_graph_exceptions": n_check_graph_exceptions,
        "totality_violations": n_totality_violations,
        "unknown_rate": global_unknown_rate,
        "crosscheck_joined": cc_joined,
        "crosscheck_agreement": cc_agreement_rate,
    }

    # Build report
    report = {
        "summary_flat": summary_flat,
        "denominators": {
            "rows_total": n_rows_total,
            "rows_no_call": n_rows_no_call,
            "rows_skipped": n_rows_skipped,
            "rows_executed": n_rows_executed,
            "operations_executed": n_operations_executed,
        },
        "summary": {
            "rows_processed": n_rows_total,
            "rows_no_call": n_rows_no_call,
            "rows_skipped": n_rows_skipped,
            "rows_executed": n_rows_executed,
            "total_operations_executed": n_operations_executed,
            "unsound_count": n_unsound,
            "totality_violations": n_totality_violations,
            "check_graph_exceptions": n_check_graph_exceptions,
        },
        "agreement_matrix": {
            outcome: dict(verdicts)
            for outcome, verdicts in agreement_matrix.items()
        },
        "unknown_rate_by_method": method_unknown_rate,
        "exception_category_breakdown": category_breakdown,
        "exception_ranking": exception_ranking,
        "precondition_state_ranking": precondition_ranking,
        "crosscheck": crosscheck_result,
        "rows": [
            {
                "record_id": r.record_id,
                "source_file": r.corpus_file,
                "line": r.row_index,
                "utterance": r.utterance,
                "calls": r.call_names,
                "scaffold_prefix_count": r.scaffold_prefix_count,
                "no_call_reason": r.no_call_reason,
                "skip_reason": r.skip_reason,
                "runtime": {
                    "outcome": r.runtime_outcome,
                    "error": r.runtime_error,
                    "exc_class": r.runtime_exc_class,
                },
                "static": r.static_verdicts,
                "tool_params": r.tool_params,
                "plr_kwargs": r.plr_kwargs,
                "compare": r.compare_rows,
                "intent_check_failures": r.intent_check_failures,
                "totality_ok": r.totality_ok,
                "check_graph_raised": r.check_graph_raised,
                "check_graph_exception": r.check_graph_exception,
                "unsound": r.unsound_count,
            }
            for r in results
        ],
    }

    # Write report
    args.report.write_text(json.dumps(report, indent=2))
    log.info("Report written to %s", args.report)

    # Write BTH_RESULTS_PATH if set
    bth_path = os.environ.get("BTH_RESULTS_PATH")
    if bth_path:
        Path(bth_path).write_text(json.dumps(summary_flat))
        log.info("Bathos results written to %s", bth_path)

    # Log summary
    log.info(
        "summary: rows_total=%d no_call=%d skipped=%d executed=%d ops=%d unsound=%d check_graph_exc=%d totality_vio=%d unknown_rate=%.3f crosscheck_joined=%d agree=%.3f",
        n_rows_total,
        n_rows_no_call,
        n_rows_skipped,
        n_rows_executed,
        n_operations_executed,
        n_unsound,
        n_check_graph_exceptions,
        n_totality_violations,
        global_unknown_rate,
        cc_joined,
        cc_agreement_rate,
    )

    return 1 if n_unsound > 0 or n_check_graph_exceptions > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
