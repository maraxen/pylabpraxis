"""P2.4 pair builder: normalized call -> teacher NL instruction candidates.

For each mined call a deterministic canonical sentence is rendered from the
namespace-table shapes; the teacher (titanix-vllm-primary, OpenAI-compatible,
localhost:8020/v1) rewrites it into natural bench-language variants. Each
accepted variant becomes one candidate row::

    {"id", "instruction", "call": {name, receiver_type, params}, "provenance"}

Acceptance pipeline per variant: normalize (parse_source.py:53-56 semantics)
-> reject if already present in the coverage floor corpus -> reject if seen
earlier in this overlay -> shape-validate row against the P2.0 tables. Every
rejection is counted with its reason; nothing is silently dropped.

The floor corpus (P2.3 output) does not exist yet as of 260825; the loader
accepts the canonical future location and tolerates absence (reported as a
deviation), while ALWAYS including the golden FR-3 fixture utterances as an
additional reference set -- a naturalness instruction colliding with the
human-reviewed fixtures would be just as wrong.
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Protocol

from overlay_gen.cache import TeacherCache
from overlay_gen.miner import (
    GOLDEN_FIXTURE_DIR,
    REPO_ROOT,
    MinedCall,
)
from overlay_gen.normalize import normalize_utterance
from overlay_gen.shapes import validate_row

__all__ = [
    "PROMPT_VERSION",
    "TeacherBackend",
    "VllmTeacherClient",
    "build_pairs",
    "canonical_sentence",
    "load_floor_normalized",
]

PROMPT_VERSION = "p24-naturalness-v1"

#: Floor corpus location owned by P2.3 (coverage-floor generator). Absent at
#: 260825 -- see module docstring.
FLOOR_OUT_GLOB = "training/coverage_floor/out/*.jsonl"


class TeacherBackend(Protocol):
    """Minimal teacher surface so tests can inject a deterministic fake."""

    def complete(self, prompt: str) -> str: ...
    @property
    def model_version(self) -> str: ...


class VllmTeacherClient:
    """OpenAI-compatible chat client for titanix-vllm-primary. Stdlib-only
    (urllib) on purpose: training code stays dependency-free."""

    def __init__(
        self,
        base_url: str = "http://localhost:8020/v1",
        model: str = "titanix-vllm-primary",
        timeout_s: float = 120.0,
        temperature: float = 0.8,
        max_tokens: int = 512,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_s = timeout_s
        self.temperature = temperature
        self.max_tokens = max_tokens
        #: The served model (served_model_version recorded by build_pairs).
        self.last_served_model: str | None = None
        self._served_root: str | None = None

    @property
    def model_version(self) -> str:
        return self.model

    def served_model_version(self) -> str:
        """The concrete served checkpoint behind the serving alias (from
        ``GET /models``'s ``root``), falling back to the alias. Recorded in
        provenance so AC-2.3/2.4.x's teacher-version tagging names the real
        weights, not just the endpoint nickname."""
        if self._served_root is None:
            try:
                with urllib.request.urlopen(
                    f"{self.base_url}/models", timeout=15.0
                ) as response:
                    data = json.loads(response.read().decode("utf-8"))
                entry = next(
                    (m for m in data.get("data", []) if m.get("id") == self.model),
                    {},
                )
                self._served_root = str(entry.get("root") or self.model)
            except Exception:
                self._served_root = self.model
        return self._served_root

    def _post(self, payload: dict) -> dict:
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            raise RuntimeError(f"teacher HTTP {exc.code}: {detail}") from exc

    def complete(self, prompt: str) -> str:
        base_payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        # titanix serves a Qwen3 reasoning model; thinking off keeps the whole
        # budget for the paraphrase lines. If the server rejects the template
        # flag, fall back to a plain request.
        try:
            body = self._post({**base_payload, "chat_template_kwargs": {"enable_thinking": False}})
        except RuntimeError:
            body = self._post(base_payload)
        message = body.get("choices", [{}])[0].get("message", {})
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError(
                f"teacher returned no usable content (finish_reason="
                f"{body.get('choices', [{}])[0].get('finish_reason')!r}); "
                "refusing to guess"
            )
        self.last_served_model = body.get("model") or self.model
        return content


# ---------------------------------------------------------------------------
# Canonical sentence rendering (teacher INPUT only -- never emitted verbatim;
# dedup would catch a lazy teacher that echoed it anyway).
# ---------------------------------------------------------------------------

_TEMPLATES: dict[str, str] = {
    "aspirate": "aspirate {volume_ul} uL from {source}",
    "dispense": "dispense {volume_ul} uL to {destination}",
    "transfer": "transfer {volume_ul} uL from {source} to {destination}",
    "stamp": "stamp {source} onto {destination} transferring {volume_ul} uL",
    "pick_up_tips": "pick up tips from {at}",
    "drop_tips": "drop tips into {destination}",
    "discard_tips": "discard the tips{at_clause}",
    "move_resource": "move {resource} to {destination}",
    "move_plate": "move the plate {plate} to {destination}",
    "move_lid": "move the lid {lid} to {destination}",
    "read_absorbance": "read absorbance at {wavelength_nm} nm{at_clause}",
    "read_fluorescence": (
        "read fluorescence with excitation {excitation_nm} nm and emission "
        "{emission_nm} nm at focal height {focal_height_mm} mm{at_clause}"
    ),
    "read_luminescence": "read luminescence at focal height {focal_height_mm} mm{at_clause}",
}


def _fmt_value(value) -> str:
    if isinstance(value, list):
        return "+".join(_fmt_value(v) for v in value)
    if isinstance(value, str):
        # plate['A1:C1'] -> plate A1:C1 ; bare variable names stay themselves.
        pretty = re.sub(r"\s+", " ", re.sub(r"[\[\]'\"]+", " ", value)).strip()
        return pretty or value.strip()
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def canonical_sentence(call: MinedCall | dict) -> str:
    params = call.params if isinstance(call, MinedCall) else dict(call.get("params", {}))
    name = call.name if isinstance(call, MinedCall) else str(call.get("name"))
    template = _TEMPLATES.get(name)
    if template is None:
        raise KeyError(f"no canonical template for phase-2 tool {name!r}")
    fields: dict[str, str] = {k: _fmt_value(v) for k, v in params.items()}
    fields.setdefault("at_clause", "")
    if params.get("at"):
        fields["at_clause"] = f" at {_fmt_value(params['at'])}"
    missing = {
        brace
        for _, brace, _, _ in __import__("string").Formatter().parse(template)
        if brace
    }
    unresolved = missing - set(fields)
    if unresolved:
        raise ValueError(f"call {name} missing fields {sorted(unresolved)} for canonical render")
    return template.format(**fields)


def paraphrase_prompt(canonical: str, call_repr: str, n_variants: int) -> str:
    return (
        "You are generating natural-language training data for a lab-automation "
        "copilot that controls a liquid-handling robot.\n"
        f"Rewrite the lab instruction below into {n_variants} DISTINCT natural "
        "phrasings a bench scientist might say or type.\n"
        "Rules:\n"
        "- Keep the action, every location/reference, and every volume exactly "
        "as stated. Do not add or drop steps or parameters.\n"
        "- Vary sentence structure, politeness and vocabulary.\n"
        "- One phrase per line. No numbering, no quotes, no explanations.\n\n"
        f"Instruction: {canonical}\n"
        f"Canonical call: {call_repr}\n"
    )


_BULLET_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")


def parse_paraphrases(text: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for raw in text.splitlines():
        line = _BULLET_RE.sub("", raw.strip()).strip().strip('"').strip()
        if not (3 <= len(line) <= 200):
            continue
        key = normalize_utterance(line)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(line)
    return out


# ---------------------------------------------------------------------------
# Floor-corpus loading (dedup reference set)
# ---------------------------------------------------------------------------


def load_floor_normalized(
    extra_paths: list[Path] | None = None,
) -> tuple[set[str], list[str]]:
    """Normalized utterances of the floor corpus + golden FR-3 fixtures.

    Returns ``(normalized_set, warnings)``. Absent floor outputs produce a
    warning, never a crash -- P2.3 may land after P2.4."""
    warnings: list[str] = []
    normalized: set[str] = set()

    floor_files = sorted((REPO_ROOT / FLOOR_OUT_GLOB).parent.glob("*.jsonl"))
    if not floor_files:
        warnings.append(
            f"floor corpus absent ({FLOOR_OUT_GLOB}): vs-floor dedup ran against "
            "golden fixtures only; re-run overlay generation once P2.3 lands"
        )
    for path in floor_files + sorted(GOLDEN_FIXTURE_DIR.glob("*.json")):
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".jsonl":
            for line in text.splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                utterance = row.get("instruction") or row.get("utterance") or ""
                normalized.add(normalize_utterance(utterance))
        else:
            entry = json.loads(text)
            normalized.add(normalize_utterance(entry.get("utterance", "")))
    if extra_paths:
        for path in extra_paths:
            for line in Path(path).read_text(encoding="utf-8").splitlines():
                if line.strip():
                    normalized.add(
                        normalize_utterance(json.loads(line).get("instruction", ""))
                    )
    normalized.discard("")
    return normalized, warnings


# ---------------------------------------------------------------------------
# Pair building
# ---------------------------------------------------------------------------


def build_pairs(
    calls: list[MinedCall],
    *,
    teacher: TeacherBackend,
    cache_dir: Path | None = None,
    out_path: Path | None = None,
    n_variants: int = 3,
    generator: str = "training/overlay_gen (P2.4, backlog item 479)",
    generator_version: str = "unknown",
    floor_extra_paths: list[Path] | None = None,
) -> tuple[list[dict], dict]:
    """Prove pairs for every mined call. Returns ``(rows, summary)``.

    Deterministic ordering throughout (calls sorted by origin, variants by
    first occurrence) so equal inputs yield byte-equal outputs given cache
    hits."""
    rows: list[dict] = []
    summary = {
        "mined_calls_in": len(calls),
        "unique_canonicals": 0,
        "teacher_calls_made": 0,
        "cache_hits": 0,
        "variants_parsed": 0,
        "pairs_written": 0,
        "rejected_vs_floor": 0,
        "rejected_within_overlay": 0,
        "rejected_invalid_shape": 0,
        "shape_error_samples": [],
        "warnings": [],
    }

    floor, warns = load_floor_normalized(floor_extra_paths)
    summary["warnings"].extend(warns)

    cache = TeacherCache(cache_dir) if cache_dir is not None else None
    teacher_model_version = teacher.model_version
    _resolver = getattr(teacher, "served_model_version", None)
    served_model_version: str | None = (
        _resolver() if callable(_resolver) else getattr(teacher, "last_served_model", None)
    )

    # One teacher request per unique canonical sentence (identical mined calls
    # share paraphrase sets; provenance keeps each row's own source).
    unique: dict[str, list[MinedCall]] = {}
    for call in sorted(calls, key=lambda c: c.origin):
        unique.setdefault(canonical_sentence(call), []).append(call)
    summary["unique_canonicals"] = len(unique)

    overlay_seen: set[str] = set()

    for canonical, group in unique.items():
        call_repr = f"{group[0].name}({', '.join(f'{k}={_fmt_value(v)}' for k, v in group[0].params.items())})"
        prompt = paraphrase_prompt(canonical, call_repr, n_variants)
        text = None
        if cache is not None:
            text = cache.get(PROMPT_VERSION, teacher_model_version, prompt)
            if text is not None:
                summary["cache_hits"] += 1
        if text is None:
            text = teacher.complete(prompt)
            summary["teacher_calls_made"] += 1
            if cache is not None:
                cache.put(
                    PROMPT_VERSION,
                    teacher_model_version,
                    prompt,
                    text,
                    served_model_version=served_model_version,
                )

        variants = parse_paraphrases(text)
        summary["variants_parsed"] += len(variants)

        for call in group:
            for variant in variants:
                key = normalize_utterance(variant)
                if key in floor:
                    summary["rejected_vs_floor"] += 1
                    continue
                if key in overlay_seen:
                    summary["rejected_within_overlay"] += 1
                    continue
                row_id = "ovl-" + hashlib.sha256(key.encode()).hexdigest()[:10]
                row = {
                    "id": row_id,
                    "instruction": variant,
                    "call": call.call_dict(),
                    "provenance": {
                        "provenance": "naturalness",
                        "source_notebook_or_protocol": call.source,
                        "origin": call.origin,
                        "generator": generator,
                        "generator_version": generator_version,
                        "prompt_version": PROMPT_VERSION,
                        "teacher_model_version": served_model_version
                        or teacher_model_version,
                    },
                }
                errors = validate_row(row)
                if errors:
                    summary["rejected_invalid_shape"] += 1
                    if len(summary["shape_error_samples"]) < 10:
                        summary["shape_error_samples"].append(
                            {"row_id": row_id, "errors": errors}
                        )
                    continue
                overlay_seen.add(key)
                rows.append(row)
                summary["pairs_written"] += 1

    if out_path is not None:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = "".join(json.dumps(r, sort_keys=True) + "\n" for r in rows)
        tmp = out_path.with_suffix(".tmp")
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(out_path)
    return rows, summary
