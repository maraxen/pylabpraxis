"""Oracle replay tier 1: corpus evaluation (backlog #4879).

Run the PLR chatterbox simulator (ground truth) and plr-sema's static analyzer
in parallel against rows from corpus_p25.jsonl (812 rows) and golden_pairs.jsonl
(88 rows), join the verdicts, and report soundness metrics + totality +
exception counts.

For every row:
  * runtime: run the call sequence on the chatterbox backend with STRICT +
    tip/volume tracking; capture which operation failed or whether it passed.
  * static: adapt the call sequence into the §6.2 graph wire format and run
    plr-sema's check_graph; per-op verdict is the join of that op's findings.
  * compare: per operation, assess soundness (SAFE+raised=unsound, etc.)
  * check_graph: catch any exception from check_graph and record it.
  * totality: verify len(findings) >= len(operations) per row.
  * crosscheck: join results by record_id and compare against recorded floor
    and overlay results (execution_verify.passed/error).

Report:
  * unsound count (exit 1 if >0)
  * agreement matrix (runtime outcome × static verdict, with counts)
  * unknown_rate_by_method (per method, % of UNKNOWN verdicts)
  * exception_ranking (exception class → count + which method raised it)
  * totality_violations (rows where findings < operations)
  * check_graph exceptions
  * crosscheck agreement/disagreement counts + examples of disagreements

Usage::

    uv run python plr-sema/eval/oracle_replay.py \\
        --corpus training/assemble/out/corpus_p25.jsonl \\
        --corpus training/golden/golden_pairs.jsonl \\
        --crosscheck training/out/corpus_p23_floor.jsonl \\
        --crosscheck training/overlay_gen/out/overlay_full.jsonl \\
        --report /tmp/t16_report.json \\
        --limit 50  # for smoke test
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
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


@dataclasses.dataclass
class RowResult:
    """Result for one row."""
    record_id: str
    corpus_file: str
    row_index: int
    n_operations: int
    runtime_outcome: RuntimeOutcome
    static_verdicts: dict[str, str]  # op_i -> verdict string
    n_findings: int  # total across all ops
    compare_rows: list[dict[str, Any]]
    check_graph_raised: bool
    check_graph_exception: str | None
    intent_check_failures: list[dict[str, Any]]  # verifier checks that failed
    totality_ok: bool
    unsound_count: int


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
        call_sequence, intent_record, deck_layout = row_to_verifier_inputs(
            row, source_file=Path(corpus_file).stem, line=row_index
        )
    except Exception as e:
        log.warning("Failed to parse row %s:%d: %s", corpus_file, row_index, e)
        return RowResult(
            record_id=f"{corpus_file}:{row_index}",
            corpus_file=corpus_file,
            row_index=row_index,
            n_operations=0,
            runtime_outcome=RuntimeOutcome(error=f"parse:{e}", exc_class="ParseError", failing_index=None, planned_indices=[], passed=False),
            static_verdicts={},
            n_findings=0,
            compare_rows=[],
            check_graph_raised=False,
            check_graph_exception="parse error",
            intent_check_failures=[],
            totality_ok=True,
            unsound_count=0,
        )

    # Reconstruct the example dict for compatibility with spike functions
    example = {
        "call_sequence": call_sequence,
        "intent_record": intent_record,
        "deck_layout": deck_layout,
    }

    record_id = intent_record.get("record_id", f"{corpus_file}:{row_index}")

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

    # Static
    check_graph_raised = False
    check_graph_exception = None
    static_verdicts = {}
    n_findings = 0
    try:
        graph = adapt_graph(example, f"corpus.{Path(corpus_file).stem}.{row_index}")
        st = run_static(graph, contracts_json)
        static_verdicts = {oid: sdata["verdict"] for oid, sdata in st.items()}
        n_findings = sum(sdata["n_findings"] for sdata in st.values())
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

    # Intent check failures (from verifier's checks, if available)
    # For now, we don't have access to the full verifier result, so empty
    intent_check_failures = []

    return RowResult(
        record_id=record_id,
        corpus_file=corpus_file,
        row_index=row_index,
        n_operations=len(call_sequence),
        runtime_outcome=rt,
        static_verdicts=static_verdicts,
        n_findings=n_findings,
        compare_rows=compare_rows,
        check_graph_raised=check_graph_raised,
        check_graph_exception=check_graph_exception,
        intent_check_failures=intent_check_failures,
        totality_ok=totality_ok,
        unsound_count=unsound_count,
    )


def load_crosscheck(path: str) -> dict[str, dict[str, Any]]:
    """Load floor/overlay file and index by record_id."""
    index = {}
    try:
        with open(path) as f:
            for line in f:
                if not line.strip():
                    continue
                row = json.loads(line)
                # The floor/overlay files have various structures; look for record_id
                record_id = row.get("record_id")
                if not record_id:
                    # Try to infer from path
                    continue
                index[record_id] = row
    except Exception as e:
        log.warning("Failed to load crosscheck file %s: %s", path, e)
    return index


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

    # Load crosscheck indices
    crosscheck_indices = {}
    for cc_file in args.crosscheck:
        idx = load_crosscheck(cc_file)
        crosscheck_indices.update(idx)
    log.info("Loaded %d crosscheck entries", len(crosscheck_indices))

    # Process corpus files
    results: list[RowResult] = []
    n_rows_processed = 0
    for corpus_file in args.corpus:
        try:
            with open(corpus_file) as f:
                for line_no, line in enumerate(f, 1):
                    if args.limit and n_rows_processed >= args.limit:
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
                    n_rows_processed += 1
                    if n_rows_processed % 100 == 0:
                        log.info("Processed %d rows...", n_rows_processed)
        except Exception as e:
            log.warning("Failed to process corpus file %s: %s", corpus_file, e)

    # Compute summary statistics
    n_unsound = sum(r.unsound_count for r in results)
    n_totality_violations = sum(1 for r in results if not r.totality_ok)
    n_check_graph_exceptions = sum(1 for r in results if r.check_graph_raised)

    # Agreement matrix: runtime outcome × static verdict
    agreement_matrix = collections.defaultdict(lambda: collections.Counter())
    for r in results:
        if not r.compare_rows:
            continue
        for comp in r.compare_rows:
            outcome = comp["runtime"]
            verdict = comp["static"]
            agreement_matrix[outcome][verdict] += 1

    # Unknown rate by method (verdicts are lowercase: "safe", "will_fail", "unknown")
    method_unknown_rate: dict[str, float] = {}
    method_counts: dict[str, int] = collections.defaultdict(int)
    method_unknown: dict[str, int] = collections.defaultdict(int)
    for r in results:
        for comp in r.compare_rows:
            method = comp["method"]
            method_counts[method] += 1
            if comp["static"] == "unknown":
                method_unknown[method] += 1
    for method in method_counts:
        method_unknown_rate[method] = method_unknown[method] / method_counts[method] if method_counts[method] > 0 else 0.0

    # Exception ranking
    exc_counter: dict[str, int] = collections.Counter()
    exc_methods: dict[str, set[str]] = collections.defaultdict(set)
    for r in results:
        if r.runtime_outcome.exc_class and r.runtime_outcome.exc_class != "ParseError":
            exc_counter[r.runtime_outcome.exc_class] += 1
            for comp in r.compare_rows:
                exc_methods[r.runtime_outcome.exc_class].add(comp["method"])
    exception_ranking = [
        {"class": exc, "count": count, "raised_on_methods": sorted(exc_methods[exc])}
        for exc, count in exc_counter.most_common()
    ]

    # Crosscheck agreement
    crosscheck_agreement = {"agree": 0, "disagree": 0, "missing": 0, "examples": []}
    for r in results:
        if r.record_id not in crosscheck_indices:
            crosscheck_agreement["missing"] += 1
            continue
        cc_row = crosscheck_indices[r.record_id]
        cc_passed = cc_row.get("execution_verify", {}).get("passed")
        our_passed = r.runtime_outcome.passed
        if cc_passed == our_passed:
            crosscheck_agreement["agree"] += 1
        else:
            crosscheck_agreement["disagree"] += 1
            if len(crosscheck_agreement["examples"]) < 3:
                crosscheck_agreement["examples"].append({
                    "record_id": r.record_id,
                    "our_outcome": "passed" if our_passed else f"raised:{r.runtime_outcome.exc_class}",
                    "recorded_outcome": "passed" if cc_passed else cc_row.get("execution_verify", {}).get("error", "unknown"),
                })

    # Compute global unknown_rate and crosscheck_agreement fractions
    total_ops = sum(r.n_operations for r in results)
    total_unknown_ops = sum(
        sum(1 for comp in r.compare_rows if comp["static"] == "unknown")
        for r in results
    )
    global_unknown_rate = total_unknown_ops / total_ops if total_ops > 0 else 0.0

    # Crosscheck agreement rate (fraction of joined rows)
    cc_joined = crosscheck_agreement["agree"] + crosscheck_agreement["disagree"]
    cc_agreement_rate = (
        crosscheck_agreement["agree"] / cc_joined if cc_joined > 0 else 0.0
    )

    # Flat summary for bathos/BTH_RESULTS_PATH
    summary_flat = {
        "rows": len(results),
        "operations": total_ops,
        "unsound": n_unsound,
        "check_graph_exceptions": n_check_graph_exceptions,
        "totality_violations": n_totality_violations,
        "unknown_rate": global_unknown_rate,
        "crosscheck_agreement": cc_agreement_rate,
    }

    # Build report
    report = {
        "summary": {
            "rows_processed": len(results),
            "total_operations": total_ops,
            "unsound_count": n_unsound,
            "totality_violations": n_totality_violations,
            "check_graph_exceptions": n_check_graph_exceptions,
        },
        "summary_flat": summary_flat,
        "agreement_matrix": {
            outcome: dict(verdicts)
            for outcome, verdicts in agreement_matrix.items()
        },
        "unknown_rate_by_method": method_unknown_rate,
        "exception_ranking": exception_ranking,
        "crosscheck": crosscheck_agreement,
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
        "summary: rows=%d ops=%d unsound=%d totality_violations=%d check_graph_exc=%d unknown_rate=%.3f crosscheck_agree=%.3f",
        report["summary"]["rows_processed"],
        report["summary"]["total_operations"],
        report["summary"]["unsound_count"],
        report["summary"]["totality_violations"],
        report["summary"]["check_graph_exceptions"],
        global_unknown_rate,
        cc_agreement_rate,
    )

    return 1 if n_unsound > 0 or n_check_graph_exceptions > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
