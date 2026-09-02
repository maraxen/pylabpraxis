"""P2.5 deterministic corpus assembly core (backlog 480).

Pure function of three committed input files + this package's constants:
same inputs => identical output bytes (D9/R4; upstream teacher outputs are
cached content-addressed, so regeneration never re-calls a teacher and never
drifts). No timestamps enter any artifact byte -- see
``developer_scaffold_template.txt`` for the recorded no-date-injection
decision (D6-rev2).

Inputs (all landed + jury-cleared before this item):

- golden   P2.1 ``training/golden/golden_pairs.jsonl`` (+ intent sidecar)
- coverage P2.3 ``training/out/corpus_p23_smoke.jsonl``
- naturalness P2.4 ``training/overlay_gen/out/overlay_smoke.jsonl``

Output contract per deliverable 1/2: ONE FunctionGemma-native JSONL whose
rows carry EXACTLY ``{metadata, tools, messages}``; ``metadata`` is the FINAL
assembled split assigned here (the normalization deliverable), all
golden-provenance rows land in eval, train/eval disjoint by construction.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from coxswain.plr.param_namespace import params_of
from coxswain.plr.slot_derivation import derive_call_gaps
from coxswain.plr.tool_schema import PHASE2_TOOL_NAMES

from praxis_training.golden_build.corpus import (
    DECLARED_ARRAY_PARAMS,
    DEVELOPER_SCAFFOLD,
)
from overlay_gen.normalize import normalize_utterance

from .scaffold import (
    SCAFFOLD_TEMPLATE_NAME,
    SCAFFOLD_VERSION,
    scaffold_template_bytes,
    scaffold_template_text,
)

__all__ = [
    "ASSEMBLY_VERSION",
    "CLASS_MAP",
    "CLARIFY_CLASSES",
    "CORPUS_NAME",
    "EVAL_FRACTION",
    "MANIFEST_NAME",
    "SIDECAR_NAME",
    "TARGET_EXAMPLES",
    "build_artifacts",
    "main",
]

#: Bump on ANY change to assembly logic / split rule / validation policy.
#: 0.1.3 (260902): gap fields (missing_required / unresolved_slots) are DERIVED
#: for every call from the params as written (sorted keys), never copied; a
#: source annotation that disagrees is a loud AssertionError. Before, golden
#: rows lost their annotation entirely and floor rows kept an authored slot
#: order that disagreed with the sorted-key params (task 260902_p26_rescore).
ASSEMBLY_VERSION = "0.1.3"
GAP_FIELDS_RULE = (
    "missing_required and unresolved_slots derived per call via "
    "coxswain.plr.slot_derivation.derive_call_gaps(name, params with sorted keys); "
    "source annotations checked as sets (missing_required) / multisets (unresolved_slots)"
)

TRAINING_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = TRAINING_DIR.parent

GOLDEN_PAIRS_REL = "training/golden/golden_pairs.jsonl"
GOLDEN_SIDECAR_REL = "training/golden/golden_intent_sidecar.jsonl"
FLOOR_CORPUS_REL = "training/out/corpus_p23_floor.jsonl"
OVERLAY_CORPUS_REL = "training/overlay_gen/out/overlay_full.jsonl"

CORPUS_NAME = "corpus_p25.jsonl"
SIDECAR_NAME = "corpus_p25_sidecar.jsonl"
MANIFEST_NAME = "manifest.json"

#: Floor-generator class vocabulary -> canonical golden/AmbiguityClass names.
CLASS_MAP: dict[str, str] = {
    "none": "clean_parse",
    "missing-slot": "missing_slot",
    "ambiguous-referent": "ambiguous_referent",
    "out-of-surface": "out_of_surface",
}
CANONICAL_CLASSES: tuple[str, ...] = (
    "clean_parse",
    "missing_slot",
    "ambiguous_referent",
    "out_of_surface",
)
CLARIFY_CLASSES: tuple[str, ...] = ("missing_slot", "ambiguous_referent", "out_of_surface")

#: Held-out fraction per synthetic (provenance x class x verb) stratum.
EVAL_FRACTION = 0.2
#: Strata smaller than this stay ALL-train (D7 negative-mixing priority).
MIN_STRATUM_FOR_EVAL = 4

#: P2.5 target from the task line; shortfall is RECORDED, never padded.
TARGET_EXAMPLES = 1000
SHORTFALL_REASON = (
    "Inputs are the full-scale P2.3 floor sweep (43-cell matrix v2) and the "
    "full P2.4 overlay pass over every mined source; the remaining gap to "
    "1000 is bounded by matrix size x examples_per_cell and by the 37 unique "
    "mined canonicals, not by a pending run. Assembly merges what exists "
    "verbatim and pads nothing."
)

#: Literal params that MUST arrive numeric when present (golden-builder rule).
_NUMERIC_LITERAL_PARAMS = frozenset({
    "volume_ul", "wavelength_nm", "excitation_nm", "emission_nm", "focal_height_mm",
})

THRESHOLDS_DOC_REL = ".praxia/docs/specs/260825_p25_provisional_thresholds.md"


# ---------------------------------------------------------------------------
# small utils
# ---------------------------------------------------------------------------

def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_json(obj: Any) -> str:
    """Byte-stable serialization (sorted keys, compact, ASCII-escaped)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def plr_source_sha() -> str:
    """Vendored pylabrobot submodule HEAD (D9 corpus key)."""
    out = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "submodule", "status", "external/pylabrobot"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    token = out.split()[0]
    return token[1:] if token[0] in "+-U" else token


# ---------------------------------------------------------------------------
# loaders -> normalized intermediate records
# ---------------------------------------------------------------------------
# Record shape (dict):
#   record_id, provenance, ambiguity_class, verb, utterance,
#   calls: [{name, params}], assistant_text: str|None, supervision_kind,
#   lineage: {...}   (everything traceability wants, kept out of native rows)

def load_golden() -> list[dict[str, Any]]:
    pairs_path = REPO_ROOT / GOLDEN_PAIRS_REL
    sidecar_path = REPO_ROOT / GOLDEN_SIDECAR_REL
    pairs = _read_jsonl(pairs_path)
    sidecars = _read_jsonl(sidecar_path)
    if len(pairs) != len(sidecars):
        raise AssertionError("golden pairs/sidecar length mismatch")
    records: list[dict[str, Any]] = []
    for n, (row, sc) in enumerate(zip(pairs, sidecars)):
        if sorted(row.keys()) != ["messages", "metadata", "tools"]:
            raise AssertionError(f"golden line {n}: unexpected native keys {sorted(row.keys())}")
        msgs = row["messages"]
        utterance = msgs[1]["content"]
        if utterance != sc["utterance"]:
            raise AssertionError(f"golden line {n}: pair/sidecar utterance linkage broken")
        tool_call_msgs = [m for m in msgs if m["role"] == "assistant" and "tool_calls" in m]
        calls = [
            {"name": tc["function"]["name"], "params": dict(tc["function"]["arguments"])}
            for m in tool_call_msgs
            for tc in m["tool_calls"]
        ]
        # Carry the golden sidecar's own gap annotation onto the call so
        # validate_and_normalize can CHECK it against the derivation (before
        # 0.1.3 it was parked under lineage.gap_fields and the assembled
        # sidecar shipped without it -- the gold_slot_annotation defect).
        for k, sc_call in enumerate(sc.get("calls") or []):
            if k < len(calls):
                for key in ("missing_required", "unresolved_slots"):
                    if key in sc_call:
                        calls[k][key] = sc_call[key]
        assistant_text = next(
            (m["content"] for m in msgs if m["role"] == "assistant" and "tool_calls" not in m),
            None,
        )
        cls = sc["ambiguity_class"]
        records.append({
            "record_id": sc["record_id"],
            "provenance": "golden",
            "ambiguity_class": cls,
            "verb": calls[0]["name"] if calls else "",
            "utterance": utterance,
            "calls": calls,
            "assistant_text": assistant_text,
            "supervision_kind": "nl_clarification" if assistant_text is not None else "tool_call",
            "lineage": {
                "pairs_file": GOLDEN_PAIRS_REL,
                "sidecar_file": GOLDEN_SIDECAR_REL,
                "pair_line": n,
                "golden_internal_split": row["metadata"],
                "sidecar_split_tag": sc.get("split"),
                "authoring_note": sc.get("authoring_note", ""),
                "gap_fields": sc.get("calls"),
            },
        })
    return records


def load_floor() -> list[dict[str, Any]]:
    path = REPO_ROOT / FLOOR_CORPUS_REL
    records: list[dict[str, Any]] = []
    for row in _read_jsonl(path):
        cell = row["matrix_cell"]
        prov = row["provenance"]
        clarification = row.get("clarification")
        kind = row["supervision"]["kind"]
        calls = []
        for c in row["intent"]["calls"]:
            entry: dict[str, Any] = {"name": c["name"], "params": dict(c.get("params", {}))}
            if c.get("missing_required"):
                entry["missing_required"] = list(c["missing_required"])
            if c.get("unresolved_slots"):
                entry["unresolved_slots"] = c["unresolved_slots"]
            calls.append(entry)
        if cell["ambiguity_class"] not in CLASS_MAP:
            raise AssertionError(f"{row['record_id']}: unmapped floor class {cell['ambiguity_class']!r}")
        if (kind == "nl_clarification") != (clarification is not None):
            raise AssertionError(f"{row['record_id']}: supervision kind vs clarification mismatch")
        records.append({
            "record_id": row["record_id"],
            "provenance": prov["provenance"],  # "coverage"
            "ambiguity_class": CLASS_MAP[cell["ambiguity_class"]],
            "verb": cell["verb"],
            "utterance": row["utterance"],
            "calls": calls,
            "assistant_text": clarification,
            "supervision_kind": kind,
            "lineage": {
                "source_file": FLOOR_CORPUS_REL,
                "cell_id": cell["cell_id"],
                "matrix_ambiguity_class": cell["ambiguity_class"],
                "matrix_version": prov.get("matrix_version"),
                "generator_version": prov["generator_version"],
                "prompt_version": prov["prompt_version"],
                "teacher_model_version": prov["teacher_model_version"],
                "gap_fields": calls,
            },
        })
    return records


def load_overlay() -> list[dict[str, Any]]:
    path = REPO_ROOT / OVERLAY_CORPUS_REL
    records: list[dict[str, Any]] = []
    for row in _read_jsonl(path):
        prov = row["provenance"]
        call = row["call"]
        records.append({
            "record_id": row["id"],
            "provenance": prov["provenance"],  # "naturalness"
            "ambiguity_class": "clean_parse",
            "verb": call["name"],
            "utterance": row["instruction"],
            "calls": [{"name": call["name"], "params": dict(call.get("params", {}))}],
            "assistant_text": None,
            "supervision_kind": "tool_call",
            "lineage": {
                "source_file": OVERLAY_CORPUS_REL,
                "origin": prov.get("origin"),
                "source_notebook_or_protocol": prov.get("source_notebook_or_protocol"),
                "receiver_type": call.get("receiver_type"),
                "generator_version": prov["generator_version"],
                "prompt_version": prov["prompt_version"],
                "teacher_model_version": prov["teacher_model_version"],
                "gap_fields": [],
            },
        })
    return records


# ---------------------------------------------------------------------------
# validation + normalization (uniform gate over EVERY provenance)
# ---------------------------------------------------------------------------

def validate_and_normalize(record: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    """Returns (normalized_calls, exclusion_reasons). Non-empty reasons => the
    RECORD is excluded whole: a half-supervised utterance would be junk, and
    this corpus pads with nothing."""
    rid = record["record_id"]
    reasons: list[str] = []
    normalized: list[dict[str, Any]] = []
    for call in record["calls"]:
        name = call["name"]
        if name not in PHASE2_TOOL_NAMES:
            reasons.append(f"{rid}: call {name!r} outside PHASE2_TOOL_NAMES surface")
            continue
        known = {spec.name for spec in params_of(name)}
        params: dict[str, Any] = {}
        bad_call = False
        for pname, value in call["params"].items():
            if pname not in known:
                reasons.append(f"{rid}: {name}.{pname} outside canonical namespace")
                bad_call = True
                continue
            spec = next(s for s in params_of(name) if s.name == pname)
            is_array_param = (name, pname) in DECLARED_ARRAY_PARAMS
            if is_array_param:
                if not (isinstance(value, list) and value):
                    reasons.append(f"{rid}: {name}.{pname} declared ARRAY got non-list/empty")
                    bad_call = True
                    continue
                params[pname] = value
            elif isinstance(value, list):
                if len(value) == 1:
                    params[pname] = value[0]  # lossless unwrap to declared scalar
                else:
                    reasons.append(
                        f"{rid}: {name}.{pname} multi-value {value!r} inexpressible in "
                        f"declared scalar surface (dispatcher wraps scalar->[v])"
                    )
                    bad_call = True
                    continue
            else:
                if pname in _NUMERIC_LITERAL_PARAMS and (
                    isinstance(value, bool) or not isinstance(value, (int, float))
                ):
                    reasons.append(f"{rid}: {name}.{pname} must be numeric, got {value!r}")
                    bad_call = True
                    continue
                params[pname] = value
        if not bad_call:
            entry: dict[str, Any] = {"name": name, "params": params}
            gaps = derive_call_gaps(name, dict(sorted(params.items())))
            derived_missing = list(gaps.missing_required)
            derived_slots = [
                {"arg_name": s.arg_name, "reference": s.reference, "resource_type": s.resource_type}
                for s in gaps.unresolved_slots
            ]
            # Loud gate: a source annotation may only differ from the
            # derivation in order (slots) -- never in content.
            if "missing_required" in call and set(call["missing_required"]) != set(derived_missing):
                raise AssertionError(
                    f"{rid}: {name} missing_required annotation {call['missing_required']!r} "
                    f"!= derived {derived_missing!r}"
                )
            if "unresolved_slots" in call:
                src = Counter(_canonical_json(x) for x in call["unresolved_slots"])
                if src != Counter(_canonical_json(x) for x in derived_slots):
                    raise AssertionError(
                        f"{rid}: {name} unresolved_slots annotation {call['unresolved_slots']!r} "
                        f"!= derived {derived_slots!r}"
                    )
            entry["missing_required"] = derived_missing
            entry["unresolved_slots"] = derived_slots
            normalized.append(entry)
    return normalized, reasons


# ---------------------------------------------------------------------------
# split assignment (disjoint BY CONSTRUCTION)
# ---------------------------------------------------------------------------

def assign_splits(records: list[dict[str, Any]]) -> dict[str, set[str]]:
    """Golden -> eval unconditionally. Synthetic strata keyed
    (provenance, class, verb), sorted by record_id; LAST k go eval where
    k = min(n-1, floor(n*EVAL_FRACTION)), bumped to >=1 once n >= MIN_STRATUM_FOR_EVAL."""
    by_split: dict[str, set[str]] = {"train": set(), "eval": set()}
    strata: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    for r in records:
        if r["provenance"] == "golden":
            by_split["eval"].add(r["record_id"])  # task AC: golden ALWAYS held out
        else:
            strata[(r["provenance"], r["ambiguity_class"], str(r["verb"]))].append(r["record_id"])
    for (_prov, _cls, _verb), ids in sorted(strata.items()):
        ids = sorted(ids)
        n = len(ids)
        k = math.floor(n * EVAL_FRACTION)
        if n >= MIN_STRATUM_FOR_EVAL:
            k = max(k, 1)
        k = min(k, n - 1)  # every stratum keeps >= 1 train row
        by_split["train"].update(ids[: n - k])
        by_split["eval"].update(ids[n - k:])
    total = sum(len(v) for v in by_split.values())
    if total != len({r["record_id"] for r in records}):
        raise AssertionError("split assignment lost/duplicated records")
    return by_split


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

def render_native_row(record: dict[str, Any], split: str, tools: list[dict]) -> dict:
    """FunctionGemma-native row: keys EXACTLY {metadata, tools, messages};
    developer turn byte-matches the committed scaffold template."""
    messages: list[dict] = [
        {"role": "developer", "content": scaffold_template_text()},
        {"role": "user", "content": record["utterance"]},
    ]
    if record["assistant_text"] is not None:
        messages.append({"role": "assistant", "content": record["assistant_text"]})
    else:
        messages.append({
            "role": "assistant",
            "tool_calls": [
                {"type": "function", "function": {"name": c["name"], "arguments": c["params"]}}
                for c in record["normalized_calls"]
            ],
        })
    return {"metadata": split, "tools": tools, "messages": messages}


def render_sidecar_row(record: dict[str, Any], split: str) -> dict:
    return {
        "record_id": record["record_id"],
        # Line-alignment contract shared with the golden sidecar: consumers
        # (praxis_training.baseline_eval.runner.load_pair_set) verify the
        # sidecar utterance equals the pair's user turn on every line.
        "utterance": record["utterance"],
        "split": split,
        "provenance": record["provenance"],
        "ambiguity_class": record["ambiguity_class"],
        "verb": record["verb"],
        "supervision_kind": record["supervision_kind"],
        "calls": record["normalized_calls"],
        "lineage": record["lineage"],
    }


# ---------------------------------------------------------------------------
# manifest
# ---------------------------------------------------------------------------

def _input_meta(rel: str) -> dict:
    path = REPO_ROOT / rel
    return {
        "path": rel,
        "sha256": _sha256_file(path),
        "bytes": path.stat().st_size,
        "rows": len(_read_jsonl(path)),
    }


def _count_strata(records: list[dict], by_split: dict[str, set[str]]) -> list[dict]:
    agg: dict[tuple[str, str, str], dict[str, int]] = {}
    for r in records:
        key = (r["provenance"], r["ambiguity_class"], str(r["verb"]))
        slot = agg.setdefault(key, {"n": 0, "n_eval": 0})
        slot["n"] += 1
        if r["record_id"] in by_split["eval"]:
            slot["n_eval"] += 1
    return [
        {"provenance": p, "ambiguity_class": c, "verb": v, **counts}
        for (p, c, v), counts in sorted(agg.items())
    ]


def build_manifest(
    records: list[dict],
    by_split: dict[str, set[str]],
    exclusion_map: dict[str, list[str]],
    scaffold_sha256: str,
) -> dict:
    n_total = len(records)
    n_eval = len(by_split["eval"])
    per_split_class = {
        split: dict(Counter(r["ambiguity_class"] for r in records if r["record_id"] in ids))
        for split, ids in by_split.items()
    }
    eval_clarify = sum(per_split_class["eval"].get(c, 0) for c in CLARIFY_CLASSES)
    # Measured, never dropped: floor_gen has no utterance-level dedup (only
    # cache-key dedup) and overlay_gen dedups only against floor + itself, so
    # cross-provenance paraphrase collapse is only visible here. Same
    # normalization rule as P2.4's dedup (trim/collapse/casefold).
    normalized = [normalize_utterance(r["utterance"]) for r in records]
    duplicate_utterances = len(normalized) - len(set(normalized))

    def _lineage_versions(field: str) -> list[str]:
        return sorted({r["lineage"][field] for r in records if field in r["lineage"]})

    def _provenance_versions(prov: str) -> list[str]:
        return sorted({r["lineage"]["generator_version"] for r in records if r["provenance"] == prov})

    return {
        "artifact": "praxis-copilot-p25-assembled-corpus",
        "task_id": "260825_copilot_pipeline_spec",
        "backlog_item": 480,
        "spec_ref": ".praxia/docs/specs/260825_coxswain-phase-2-functiongemma-copilot-p.md rev2 §5 P2.5 / §7 AC-2.5.x",
        "assembly_version": ASSEMBLY_VERSION,
        "gap_fields_rule": GAP_FIELDS_RULE,
        "plr_source_sha": plr_source_sha(),
        "scaffold": {
            "template_file": f"training/assemble/{SCAFFOLD_TEMPLATE_NAME}",
            "template_sha256": scaffold_sha256,
            "version": SCAFFOLD_VERSION,
            "date_timestamp_injection": False,
        },
        "dataset_format": "FunctionGemma-native JSONL {metadata, tools[], messages[]} (research §2a / mobile-actions)",
        "inputs": {
            "golden_pairs": _input_meta(GOLDEN_PAIRS_REL),
            "golden_sidecar": _input_meta(GOLDEN_SIDECAR_REL),
            "floor_corpus": _input_meta(FLOOR_CORPUS_REL),
            "overlay_corpus": _input_meta(OVERLAY_CORPUS_REL),
        },
        "generator_versions": {
            "assemble": ASSEMBLY_VERSION,
            "floor_gen": _provenance_versions("coverage"),
            "overlay_gen": _provenance_versions("naturalness"),
        },
        "prompt_versions": _lineage_versions("prompt_version"),
        "teacher_model_versions": _lineage_versions("teacher_model_version"),
        "split_rule": (
            "golden-provenance -> eval unconditionally; synthetic strata "
            "(provenance x ambiguity-class x verb) sorted by record_id, LAST "
            "k -> eval, k = min(n-1, floor(n*0.2)) bumped to >=1 when n>=4; "
            "train/eval disjoint by construction (single membership pass)"
        ),
        "counts": {
            "total_rows": n_total,
            "by_split": {s: len(ids) for s, ids in sorted(by_split.items())},
            "by_provenance": dict(sorted(Counter(r["provenance"] for r in records).items())),
            "by_class": dict(sorted(Counter(r["ambiguity_class"] for r in records).items())),
            "by_split_and_class": {s: dict(sorted(m.items())) for s, m in sorted(per_split_class.items())},
            "eval_clarify_total": eval_clarify,
            "duplicate_utterances_normalized": duplicate_utterances,
            "distinct_verbs": sorted({str(r["verb"]) for r in records if r["verb"]}),
            "strata": _count_strata(records, by_split),
        },
        "target": {
            "examples_requested": TARGET_EXAMPLES,
            "examples_assembled": n_total,
            "shortfall": max(0, TARGET_EXAMPLES - n_total),
            "shortfall_reason": SHORTFALL_REASON,
        },
        "exclusions": {
            # RECORDS excluded (a record with two bad calls is one exclusion);
            # reason_entries counts (reason, record) pairs and can exceed it.
            "total": len({rid for rids in exclusion_map.values() for rid in rids}),
            "reason_entries": sum(len(v) for v in exclusion_map.values()),
            "reasons": dict(sorted(exclusion_map.items())),
        },
        "thresholds_doc": THRESHOLDS_DOC_REL,
        "slice_gate_doc": ".praxia/docs/specs/260825_p25_slice_gate.md",
    }


# ---------------------------------------------------------------------------
# orchestration
# ---------------------------------------------------------------------------

def build_artifacts() -> dict[str, bytes]:
    """Pure assembly: returns the THREE artifact byte payloads.

    Deterministic: no clock, no RNG, no dict-order dependence (sorted JSON +
    record_id-sorted rows). Same committed inputs => same bytes, always.
    """
    records = load_golden() + load_floor() + load_overlay()

    ids = [r["record_id"] for r in records]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        raise AssertionError(f"duplicate record_ids across branches: {dupes}")

    # Uniform validation gate; excluded records leave loudly + counted.
    kept: list[dict] = []
    exclusion_map: dict[str, list[str]] = defaultdict(list)
    for r in records:
        normalized, reasons = validate_and_normalize(r)
        if reasons:
            for reason in reasons:
                exclusion_map[reason].append(r["record_id"])
            continue
        r["normalized_calls"] = normalized
        kept.append(r)
    if not kept:
        raise AssertionError("assembly kept zero records")

    kept.sort(key=lambda r: r["record_id"])  # global deterministic order

    by_split = assign_splits(kept)
    tools = None
    corpus_lines: list[str] = []
    sidecar_lines: list[str] = []
    for r in kept:
        if tools is None:
            from praxis_training.golden_build.corpus import tool_declarations

            tools = tool_declarations()
        split = "eval" if r["record_id"] in by_split["eval"] else "train"
        corpus_lines.append(_canonical_json(render_native_row(r, split, tools)))
        sidecar_lines.append(_canonical_json(render_sidecar_row(r, split)))

    scaffold_bytes = scaffold_template_bytes()
    if scaffold_bytes != DEVELOPER_SCAFFOLD.encode("utf-8"):
        raise AssertionError(
            "committed scaffold template drifted from golden builder constant "
            "(praxis_training.golden_build.corpus.DEVELOPER_SCAFFOLD)"
        )

    manifest = build_manifest(kept, by_split, exclusion_map, hashlib.sha256(scaffold_bytes).hexdigest())
    manifest_bytes = (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode("utf-8")
    return {
        CORPUS_NAME: ("\n".join(corpus_lines) + "\n").encode("utf-8"),
        SIDECAR_NAME: ("\n".join(sidecar_lines) + "\n").encode("utf-8"),
        MANIFEST_NAME: manifest_bytes,
    }


def main(out_dir: Path | None = None) -> dict:
    """Write artifacts (default training/assemble/out/) + print summary."""
    out_dir = out_dir or (Path(__file__).resolve().parent / "out")
    artifacts = build_artifacts()
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in artifacts.items():
        (out_dir / name).write_bytes(payload)
    manifest = json.loads(artifacts[MANIFEST_NAME])
    summary = {
        "written_to": str(out_dir),
        "total_rows": manifest["counts"]["total_rows"],
        "by_split": manifest["counts"]["by_split"],
        "by_provenance": manifest["counts"]["by_provenance"],
        "by_class": manifest["counts"]["by_class"],
        "shortfall_vs_target": manifest["target"]["shortfall"],
        "exclusions": manifest["exclusions"]["total"],
    }
    print(json.dumps(summary, indent=1, sort_keys=True))
    return summary


if __name__ == "__main__":
    main()
