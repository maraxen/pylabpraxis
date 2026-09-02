"""Oracle spike: does PLR's simulator agree with plr-sema's static verdict?

Feasibility probe for the oracle harness (plan
``.praxia/docs/plans/260902_plr-sema-oracle-harness.md``). For each
verifier example (``training/examples/*.json``: ``call_sequence`` +
``intent_record`` + ``deck_layout``) it produces two independent readings
of the same protocol and lines them up per operation:

* **runtime** -- ``training/verify``'s ``verify()`` runs the call sequence on
  the chatterbox backend with STRICT mode and tip + volume tracking on, so
  PLR itself raises ``NoTipError`` / ``HasTipError`` / ``TooLittleLiquidError``
  / ... at the offending step. ``verify()`` collapses that to one error
  string, so this script wraps ``plan_call`` to learn *which* operation
  index was being executed when it raised.
* **static** -- the same call sequence adapted into the §6.2 graph wire
  format (one ``OperationNode`` per call, one ``ResourceNode`` per deck
  resource; no source, no extractor) and handed to
  ``plr_sema.check_graph`` against the shipped derived-contract table.
  Per-operation verdict = ``join`` of that operation's findings.

The soundness contract this checks, per operation ``i``:

* static ``SAFE`` and the simulator raised at ``i``       -> UNSOUND (bug)
* static ``WILL_FAIL`` and the simulator ran ``i`` cleanly -> UNSOUND (bug)
* static ``UNKNOWN``                                          -> no constraint

Everything else is an agreement row. Tier 1 of the plan (corpus replay)
is this script generalised to the 812-row corpus and made bathos-tracked;
this spike is deliberately unscored and untracked -- it exists to prove
the glue closes, not to publish a number.

Usage::

    uv run python plr-sema/scripts/oracle_spike.py \
        --examples training/examples --json-out $TMPDIR/oracle_spike.json
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import dataclasses
import io
import json
import logging
import sys
from pathlib import Path
from typing import Any

log = logging.getLogger("oracle_spike")

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACTS = REPO_ROOT / "plr-sema" / "data" / "derived_contracts.json"


def _import_verifier():
    """``training/`` installs its subpackages top-level (``verify``), but be
    tolerant of the namespace form too."""
    try:
        import verify.verifier as v  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        import training.verify.verifier as v  # type: ignore[import-not-found,no-redef]
    return v


# --------------------------------------------------------------------------
# runtime side
# --------------------------------------------------------------------------


@dataclasses.dataclass
class RuntimeOutcome:
    error: str | None
    exc_class: str | None
    failing_index: int | None  # index of the call being executed when it raised
    planned_indices: list[int]
    passed: bool


def run_runtime(example: dict[str, Any]) -> RuntimeOutcome:
    verifier = _import_verifier()
    planned: list[int] = []
    real_plan_call = verifier.plan_call

    def recording_plan_call(call, index, setup, *, strict):
        planned.append(index)
        return real_plan_call(call, index, setup, strict=strict)

    verifier.plan_call = recording_plan_call
    sink = io.StringIO()
    try:
        with contextlib.redirect_stdout(sink):
            result = asyncio.run(
                verifier.verify(
                    example["call_sequence"],
                    example["intent_record"],
                    layout=example.get("deck_layout"),
                    backend=example.get("backend", "LiquidHandlerChatterboxBackend"),
                )
            )
    finally:
        verifier.plan_call = real_plan_call
    error = result.get("error")
    exc_class = error.split(":", 1)[0].strip() if error else None
    failing = planned[-1] if (error and planned) else None
    return RuntimeOutcome(error, exc_class, failing, planned, bool(result.get("passed")))


# --------------------------------------------------------------------------
# static side
# --------------------------------------------------------------------------

_LH_TYPE = "LiquidHandler"


def adapt_graph(example: dict[str, Any], protocol_fqn: str) -> dict[str, Any]:
    """Call sequence -> §6.2 graph payload. Field set mirrors the committed
    fixture ``tests/fixtures/simple_transfer_graph.json`` exactly."""
    layout = example.get("deck_layout") or {}
    resources = {
        "lh": {
            "declared_type": _LH_TYPE, "element_type": None, "is_container": False,
            "is_parameter": True, "items_x": None, "items_y": None,
            "parental_chain": [], "source_expression": None, "variable_name": "lh",
        }
    }
    for name, typ in (layout.get("resources") or {}).items():
        resources[name] = {
            "declared_type": typ, "element_type": None, "is_container": False,
            "is_parameter": True, "items_x": None, "items_y": None,
            "parental_chain": ["Deck"], "source_expression": None, "variable_name": name,
        }
    operations = []
    for i, call in enumerate(example["call_sequence"]):
        operations.append({
            "arguments": {k: json.dumps(v) for k, v in (call.get("params") or {}).items()},
            "condition_expr": None, "creates_state": [], "depends_on_params": [],
            "false_branch": [], "foreach_body": [], "foreach_source": None,
            "id": f"op_{i}", "line_number": i + 1, "method_name": call["name"],
            "node_type": "static", "preconditions": [], "receiver_type": _LH_TYPE,
            "receiver_variable": "lh", "true_branch": [],
        })
    return {
        "protocol_fqn": protocol_fqn, "protocol_name": protocol_fqn.rsplit(".", 1)[-1],
        "operations": operations, "resources": resources,
        "execution_order": [o["id"] for o in operations], "has_conditionals": False,
        "has_loops": False, "machine_types": [_LH_TYPE], "preconditions": [],
        "resource_types": sorted({r["declared_type"] for r in resources.values()}),
    }


def run_static(graph: dict[str, Any], contracts_json: str) -> dict[str, dict[str, Any]]:
    sys.path.insert(0, str(REPO_ROOT / "plr-sema" / "src"))
    from plr_sema import check_graph
    from plr_sema.verdict import join

    report = check_graph(json.dumps(graph), contracts_json)
    per_op: dict[str, list] = {o["id"]: [] for o in graph["operations"]}
    for f in report.findings:
        per_op.setdefault(f.operation_id, []).append(f)
    return {
        oid: {
            "verdict": join(fs).value,
            "n_findings": len(fs),
            "reasons": sorted({getattr(f, "reason", None) or "" for f in fs} - {""}),
        }
        for oid, fs in per_op.items()
    }


# --------------------------------------------------------------------------
# comparison
# --------------------------------------------------------------------------


def compare(example: dict[str, Any], rt: RuntimeOutcome, st: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for i, call in enumerate(example["call_sequence"]):
        oid = f"op_{i}"
        if rt.failing_index is None:
            outcome = "ran_ok" if rt.error is None else "not_reached(setup_error)"
        elif i < rt.failing_index:
            outcome = "ran_ok"
        elif i == rt.failing_index:
            outcome = f"raised:{rt.exc_class}"
        else:
            outcome = "not_reached"
        verdict = st[oid]["verdict"]
        unsound = (verdict == "SAFE" and outcome.startswith("raised")) or (
            verdict == "WILL_FAIL" and outcome == "ran_ok"
        )
        rows.append({
            "index": i, "method": call["name"], "static": verdict,
            "static_findings": st[oid]["n_findings"], "runtime": outcome, "unsound": unsound,
        })
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--examples", type=Path, required=True, help="a JSON file or a directory of them")
    ap.add_argument("--contracts", type=Path, default=DEFAULT_CONTRACTS)
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    files = [args.examples] if args.examples.is_file() else sorted(args.examples.glob("*.json"))
    contracts_json = args.contracts.read_text(encoding="utf-8")
    out: list[dict[str, Any]] = []
    n_unsound = 0
    for f in files:
        ex = json.loads(f.read_text(encoding="utf-8"))
        if "call_sequence" not in ex or "intent_record" not in ex:
            log.info("skip %s (no call_sequence/intent_record)", f.name)
            continue
        rt = run_runtime(ex)
        st = run_static(adapt_graph(ex, f"training.examples.{f.stem}"), contracts_json)
        rows = compare(ex, rt, st)
        n_unsound += sum(r["unsound"] for r in rows)
        log.info("%s  runtime=%s  planned=%s", f.name, rt.error or "clean", rt.planned_indices)
        for r in rows:
            log.info("  op_%d %-14s static=%-9s (%2d findings)  runtime=%s%s",
                     r["index"], r["method"], r["static"], r["static_findings"], r["runtime"],
                     "  <-- UNSOUND" if r["unsound"] else "")
        out.append({"example": f.name, "runtime": dataclasses.asdict(rt), "rows": rows})
    log.info("examples=%d operations=%d unsound=%d", len(out), sum(len(o["rows"]) for o in out), n_unsound)
    if args.json_out:
        args.json_out.write_text(json.dumps(out, indent=2))
    return 1 if n_unsound else 0


if __name__ == "__main__":
    sys.exit(main())
