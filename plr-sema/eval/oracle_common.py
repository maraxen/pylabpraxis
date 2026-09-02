"""Shared oracle infrastructure: runtime/static/compare pipeline.

Factored from plr-sema/scripts/oracle_spike.py (260902 spike). This module is
imported by both the oracle_spike.py worked example and the tier-1 corpus-replay
harness (oracle_replay.py). It must NOT import plr_sema.src.* (the boundary test
allows that for code under plr-sema/eval/, but importing the analyzer
infrastructure from src would make this a circular dependency).
"""

from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import io
import json
import logging
import sys
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTRACTS = REPO_ROOT / "plr-sema" / "data" / "derived_contracts.json"


def _import_param_namespace():
    """``training/`` and its ``coxswain`` dependency install top-level."""
    from coxswain.plr.param_namespace import ParamKind, params_of

    return ParamKind, params_of


def _import_overlay_normalizers():
    """overlay_gen's own mined-call normalizers (T16d, #4879): naturalness-
    provenance corpus rows carry VERBATIM MINED SOURCE EXPRESSIONS in their
    tool-call params (e.g. ``plate["C1"]``, ``sample_volume_ul * 0.8``, a
    bare loop-variable slice) -- see overlay_gen/exec_verify.py's module
    docstring. Reused directly rather than duplicated (unlike floor_gen's
    _precondition_plan, which oracle_common intentionally re-implements):
    these are regex-driven and importing avoids drift on the grounding
    grammar. Prior to this fix, oracle_common fed these raw expressions
    straight into _precondition_plan/the dispatcher, producing spurious
    TypeErrors (float() on a variable-name string) and "'Plate' object has
    no attribute 'tracker'" (an un-normalized ``plate["C1"]`` ref treated as
    one opaque resource name instead of grounding to ``plate.C1``) on rows
    overlay_gen's own harness would have skipped as ungroundable-from-source.
    """
    from overlay_gen.exec_verify import _normalize_params

    return _normalize_params


def _import_verifier():
    """``training/`` installs its subpackages top-level (``verify``), but be
    tolerant of the namespace form too.
    """
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
    plr_kwargs: dict[int, dict[str, Any]] = dataclasses.field(default_factory=dict)  # index -> {param: repr(value)}


def run_runtime(example: dict[str, Any]) -> RuntimeOutcome:
    verifier = _import_verifier()
    planned: list[int] = []
    plr_kwargs: dict[int, dict[str, Any]] = {}
    real_plan_call = verifier.plan_call

    def recording_plan_call(call, index, setup, *, strict):
        planned.append(index)
        plan_result = real_plan_call(call, index, setup, strict=strict)
        # Capture PLR-named kwargs from the plan_result
        if hasattr(plan_result, "kwargs"):
            plr_kwargs[index] = {k: repr(v) for k, v in plan_result.kwargs.items()}
        return plan_result

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
    return RuntimeOutcome(error, exc_class, failing, planned, bool(result.get("passed")), plr_kwargs)


# --------------------------------------------------------------------------
# static side
# --------------------------------------------------------------------------

_LH_TYPE = "LiquidHandler"


def adapt_graph(example: dict[str, Any], protocol_fqn: str, plr_kwargs: dict[int, dict[str, Any]] | None = None) -> dict[str, Any]:
    """Call sequence -> §6.2 graph payload. Field set mirrors the committed
    fixture ``tests/fixtures/simple_transfer_graph.json`` exactly.

    If plr_kwargs is provided, use PLR-named kwargs for OperationNode.arguments
    (the planned fix for parameter name mismatch). Fall back to tool params
    when a call was never planned.
    """
    plr_kwargs = plr_kwargs or {}
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
        # Use PLR-named kwargs if available, otherwise fall back to tool params
        if i in plr_kwargs:
            arguments = plr_kwargs[i]
        else:
            arguments = {k: json.dumps(v) for k, v in (call.get("params") or {}).items()}
        operations.append({
            "arguments": arguments,
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
        unsound = (verdict == "safe" and outcome.startswith("raised")) or (
            verdict == "will_fail" and outcome == "ran_ok"
        )
        rows.append({
            "index": i, "method": call["name"], "static": verdict,
            "static_findings": st[oid]["n_findings"], "runtime": outcome, "unsound": unsound,
        })
    return rows


# --------------------------------------------------------------------------
# row parsing for corpus + P2.5 scaffolding
# --------------------------------------------------------------------------

# Scaffolding constants (match floor_gen.exec_verify exactly)
_TIP_RACK = "tip_rack"
_DUMMY_TIP_SPOT = f"{_TIP_RACK}.A1"
_PRIME_PLATE = "prime_plate"
_PLATE_ROWS = "ABCDEFGH"

# T16d (#4879): floor_gen.exec_verify.execution_verify_example gates on
# ``example.cell.ambiguity_class != "none"`` and returns skipped=True BEFORE
# ever calling ``_precondition_plan`` -- see exec_verify.py:96-103
# (_CLASS_SKIP_REASONS) and :271-274. The corpus assembler's own sidecar
# (corpus_p25_sidecar.jsonl) records this same class per row using
# underscore-separated names ("clean_parse" == floor_gen's "none";
# "missing_slot"/"ambiguous_referent"/"out_of_surface" == floor_gen's
# "missing-slot"/"ambiguous-referent"/"out-of-surface"). Prior to this fix
# (T16b, 6c668aa6) oracle_common ran _precondition_plan on EVERY row with a
# tool call regardless of class, which (a) executed 118/123 ambiguous_referent
# and 95/175 missing_slot rows P2.5 never touched (execution_verify=None in
# corpus_p23_floor.jsonl for every one of them, verified 260902), producing
# spurious GroundingError/DispatchError/RuntimeError "disagreements" against
# a crosscheck P2.5 never ran, and (b) KeyError-crashed on 17 missing_slot
# rows whose required param (volume_ul) was deliberately omitted -- aspirate/
# dispense's own _precondition_plan branches index params["volume_ul"]
# unconditionally (a bug floor_gen's own function shares, but never hits
# because its cls-gate skips these rows first).
_CLASS_SKIP_REASONS: dict[str, str] = {
    "missing_slot": "missing_slot calls are intentionally incomplete (required param "
                     "omitted); not executable ground truth (floor_gen.exec_verify "
                     "_CLASS_SKIP_REASONS['missing-slot'])",
    "ambiguous_referent": "ambiguous_referent calls carry a deliberately vague/ungroundable "
                           "ref; not executable ground truth (floor_gen.exec_verify "
                           "_CLASS_SKIP_REASONS['ambiguous-referent'])",
    "out_of_surface": "out_of_surface rows carry no call sequence (D7 clarify-only example; "
                       "floor_gen.exec_verify _CLASS_SKIP_REASONS['out-of-surface'])",
}
_EXECUTABLE_AMBIGUITY_CLASS = "clean_parse"  # sidecar's name for floor_gen's cell.ambiguity_class == "none"


def _expand_ref(ref: str) -> list[str]:
    """A single grounded dotted ref (name.A1 or name.A1:C1) -> individual well refs.
    Mirrors verify/grounding.py's ground_ref exactly.
    """
    from pylabrobot.utils.positions import expand_string_range
    base, _, tail = ref.partition(".")
    if not tail or ":" not in tail:
        return [ref]
    return [f"{base}.{pos}" for pos in expand_string_range(tail)]


def _expand_channel_wells(refs: Any) -> list[str]:
    """Flat list of individual wells refs addresses, expanding any colon-range."""
    ref_list = refs if isinstance(refs, list) else [refs]
    wells: list[str] = []
    for ref in ref_list:
        wells.extend(_expand_ref(ref))
    return wells


def _row_major_wells(resource: str, n: int) -> list[str]:
    """N distinct row-major wells on resource (A1, B1, ..., H1, A2, ...)."""
    wells = [f"{resource}.{row}{col}" for col in range(1, 13) for row in _PLATE_ROWS]
    if n > len(wells):
        raise ValueError(f"{resource} (96 wells) cannot supply {n} distinct wells")
    return wells[:n]


def _resource_type_holders(call: dict[str, Any]) -> list[str]:
    """Names of this call's RESOURCE_TYPE_RESOURCE-typed symbolic refs.

    Replicates floor_gen.exec_verify._resource_type_holders exactly (T16d,
    #4879): infer_layout() defaults every unrecognized ref name to a bare
    Plate; PLR's move_resource/move_plate/move_lid reject a Plate
    destination for a "resource" (ResourceStack/ResourceHolder) target.
    DeckLayout.holders is the harness's own documented mechanism for
    exactly this. Prior to this fix, oracle_common never computed holders
    at all, so every move_resource/move_plate/move_lid call in the corpus
    hit "RuntimeError: Can only drop Lid resources onto Plate '<name>'"
    even on rows P2.5 recorded as passed (45/141 crosscheck-joined
    clean_parse disagreements, all in this one shape, verified 260902).
    Deduped: the same name can legitimately appear twice (e.g.
    move_resource.resource == .destination would otherwise register two
    holders under one name and crash).
    """
    ParamKind, params_of = _import_param_namespace()
    names: list[str] = []
    for spec in params_of(call["name"]):
        if spec.kind is ParamKind.SYMBOLIC_RESOURCE_REF and spec.resource_type == "resource":
            value = call["params"].get(spec.name)
            if isinstance(value, str):
                names.append(value)
            elif isinstance(value, list):
                names.extend(v for v in value if isinstance(v, str))
    return list(dict.fromkeys(names))


def _precondition_plan(
    call: dict[str, Any],
) -> tuple[str | None, list[dict[str, Any]], dict[str, str], dict[str, float]]:
    """Decide whether call is verifiable, and what synthetic setup it needs.

    Returns (skip_reason, prefix_calls, extra_resources, seed_volumes).
    Replicates floor_gen.exec_verify._precondition_plan exactly.
    """
    # Import SUPPORTED_TOOLS dynamically to avoid hard dep at module level
    try:
        from verify.dispatcher import SUPPORTED_TOOLS
    except ModuleNotFoundError:
        from training.verify.dispatcher import SUPPORTED_TOOLS  # type: ignore[import-not-found]

    name = call["name"]
    params = call["params"]

    if name not in SUPPORTED_TOOLS:
        return (
            f"{name!r} has no LiquidHandler-chatterbox execution path",
            [], {}, {},
        )

    if name == "transfer" and params.get("volume_ul") is None:
        return (
            "transfer without volume_ul cannot be deterministically post-conditioned",
            [], {}, {},
        )

    pickup = {"name": "pick_up_tips", "params": {"at": [_DUMMY_TIP_SPOT]}}

    if name == "transfer":
        if "source" not in params:
            return "transfer missing required 'source' param", [], {}, {}
        vol_param = params.get("volume_ul") or []
        # Handle both scalar and list volume_ul
        if isinstance(vol_param, (int, float)):
            total = float(vol_param)
        else:
            total = sum(float(v) for v in vol_param)
        seeds = {params["source"]: total} if total > 0 else {}
        return None, [pickup], {}, seeds

    if name == "aspirate":
        if "source" not in params:
            return "aspirate missing required 'source' param", [], {}, {}
        sources = _expand_channel_wells(params["source"])
        vols = params["volume_ul"] if isinstance(params["volume_ul"], list) else [params["volume_ul"]]
        pickup_n = {"name": "pick_up_tips", "params": {"at": _row_major_wells(_TIP_RACK, len(sources))}}
        return None, [pickup_n], {}, dict(zip(sources, vols))

    if name == "dispense":
        if "destination" not in params:
            return "dispense missing required 'destination' param", [], {}, {}
        destinations = _expand_channel_wells(params["destination"])
        vols = params["volume_ul"] if isinstance(params["volume_ul"], list) else [params["volume_ul"]]
        n = len(destinations)
        pickup_n = {"name": "pick_up_tips", "params": {"at": _row_major_wells(_TIP_RACK, n)}}
        prime_wells = _row_major_wells(_PRIME_PLATE, n)
        prime = {"name": "aspirate", "params": {"source": prime_wells, "volume_ul": list(vols)}}
        return None, [pickup_n, prime], {_PRIME_PLATE: "Plate"}, dict(zip(prime_wells, vols))

    if name == "drop_tips":
        destination = params.get("destination")
        spots = destination if isinstance(destination, list) else [destination]
        return None, [{"name": "pick_up_tips", "params": {"at": list(spots)}}], {}, {}

    if name == "discard_tips":
        return None, [pickup], {}, {}

    # pick_up_tips / stamp / move_resource / move_plate / move_lid: no precondition
    return None, [], {}, {}


def row_to_verifier_inputs(
    row: dict[str, Any],
    *,
    source_file: str,
    line: int,
    ambiguity_class: str | None = None,
    sidecar_record_id: str | None = None,
    provenance: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any] | None, str | None, str | None]:
    """Parse a chat-format corpus row into call_sequence, intent_record, layout.

    The row format (corpus_p25.jsonl) is:
        {
            "messages": [{role, content, tool_calls?}, ...],
            "tools": [...],
            "metadata": "train"|"test"|...,
        }

    The ground-truth call is extracted from the assistant message's
    tool_calls[*].function.{name, arguments}. The intent comes from the user
    message. Replicate P2.5 scaffolding (floor_gen.exec_verify): add prefix
    calls (pick_up_tips, etc.) to satisfy preconditions, populate seed_volumes,
    and return an intent_record with source="synthetic" and expected_effects=[].

    Args:
        row: a single row from corpus JSONL or chat-format JSON
        source_file: basename of the corpus file, for record_id
        line: line number (1-indexed) for record_id
        ambiguity_class: sidecar-provided class ("clean_parse", "missing_slot",
            "ambiguous_referent", "out_of_surface"); when given and not
            "clean_parse", the row is skipped before _precondition_plan runs
            (mirrors floor_gen.exec_verify's cls != "none" gate). None means
            no sidecar join was available for this row -- fall back to the
            pre-T16d behavior of attempting _precondition_plan unconditionally.
        sidecar_record_id: when given, overrides the synthetic
            "{source_file}:{line}" record_id with the sidecar's own
            record_id (exact join key against floor/overlay crosscheck files).
        provenance: sidecar's "coverage" | "golden" | "naturalness". When
            "naturalness", the row's params are VERBATIM MINED SOURCE
            EXPRESSIONS (overlay_gen provenance) and are run through
            overlay_gen's own _normalize_params before _precondition_plan;
            an unresolvable expression (variable/computed value) produces a
            skip_reason (matches overlay_gen.exec_verify.execution_verify_call),
            not an execution attempt.

    Returns:
        (call_sequence, intent_record, deck_layout, skip_reason, no_call_reason)
        - call_sequence: list of {name, params} dicts (may be empty)
        - intent_record: dict with record_id, utterance, source, calls, expected_effects
        - deck_layout: dict with resources and seed_volumes, or None
        - skip_reason: None if executable; str reason if _precondition_plan rejected it
        - no_call_reason: "no_tool_calls" if assistant had no tool_calls; else None

    """
    record_id = sidecar_record_id or f"{source_file}:{line}"

    # Find the assistant message with tool_calls
    real_call: dict[str, Any] | None = None
    user_message_content = ""
    no_call_reason = None
    for msg in row.get("messages", []):
        if msg.get("role") == "user":
            user_message_content = msg.get("content", "")
        elif msg.get("role") == "assistant":
            tool_calls = msg.get("tool_calls", [])
            if not tool_calls:
                no_call_reason = "no_tool_calls"
            elif tool_calls:
                # Take the first tool call (corpus has 1 call per row)
                func = tool_calls[0].get("function", {})
                real_call = {
                    "name": func.get("name", ""),
                    "params": func.get("arguments", {}),
                }

    skip_reason = None
    call_sequence = []
    extra_resources = {}
    seed_volumes = {}

    if no_call_reason:
        # Row has no tool_calls; this is a clarification turn
        pass
    elif not real_call:
        # Malformed row (should not happen if no_call_reason is set)
        no_call_reason = "malformed_row"
    elif ambiguity_class is not None and ambiguity_class != _EXECUTABLE_AMBIGUITY_CLASS:
        # T16d gate: P2.5 never ran execution_verify on this row (cls != "none");
        # do not call _precondition_plan at all.
        skip_reason = _CLASS_SKIP_REASONS.get(
            ambiguity_class,
            f"ambiguity_class {ambiguity_class!r} is not executable ground truth "
            "(unrecognized class, treated conservatively as non-executable)",
        )
    elif provenance == "naturalness":
        # T16d: mined-call source-expression normalization (overlay_gen's
        # own gate) before any precondition planning.
        normalize_params = _import_overlay_normalizers()
        normalized = normalize_params(real_call["name"], real_call["params"])
        if normalized is None:
            skip_reason = (
                "mined call references a variable/computed value (not a literal deck ref "
                "or numeric volume) that the P2.2 harness's static grounding can't resolve "
                "from source text alone; execution-verify skipped, not rejected "
                "(overlay_gen.exec_verify.execution_verify_call parity)"
            )
        else:
            real_call = {"name": real_call["name"], "params": normalized}
            skip_reason, prefix, extra_resources, seed_volumes = _precondition_plan(real_call)
            if skip_reason is None:
                call_sequence = [*prefix, real_call]
    else:
        # Apply P2.5 scaffolding via _precondition_plan
        skip_reason, prefix, extra_resources, seed_volumes = _precondition_plan(real_call)
        if skip_reason is None:
            call_sequence = [*prefix, real_call]

    # Build deck_layout from scaffold resources, seed volumes, and
    # resource-type holders (real_call only -- matches
    # floor_gen.exec_verify.execution_verify_example, which computes
    # holders from the real call, not the scaffold prefix).
    holders: list[str] = []
    if skip_reason is None and real_call is not None:
        holders = _resource_type_holders(real_call)
    deck_layout = None
    if extra_resources or seed_volumes or holders:
        deck_layout = {
            "resources": extra_resources,
            "seed_volumes": seed_volumes,
            "holders": holders,
        }

    # Replicate P2.5 scaffolding: intent matches the full call sequence
    intent_record = {
        "record_id": record_id,
        "utterance": user_message_content,
        "source": "synthetic",  # per P2.5 exec_verify
        "calls": [{"name": c["name"], "params": c["params"]} for c in call_sequence],
        "expected_effects": [],  # per P2.5 exec_verify
    }

    return call_sequence, intent_record, deck_layout, skip_reason, no_call_reason
