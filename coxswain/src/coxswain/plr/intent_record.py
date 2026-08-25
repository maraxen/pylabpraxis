"""Intent-record shape for the copilot pipeline (P2.0 deliverable 5, C-M3).

ONE shared supervision contract consumed by the P2.2 execution-verify harness:

- the intended CALL SEQUENCE (name + canonical params),
- the EXPECTED EFFECTS (method_contracts.EffectType strings, joined
  by-string to cue-3 vocabulary without an import -- fft owns that module,
  plr must not import fft),
- the SLOT-AGREEMENT axis: intended ``missing_required`` /
  ``unresolved_slots`` per call, checked against the D11 deterministic
  re-derivation rather than taken on faith (the fields stay out of model
  hands by construction).

Location decision (recorded): coxswain/plr, NOT a training/-adjacent home.
F2-rev2 forbids coxswain/ importing training/, while BOTH the kernel-side
harness and the training pipeline must consume this exact shape; coxswain/plr
is already the purity-safe shared layer (stdlib only, NFR-1/NFR-2). When
training/ materializes as a uv workspace member it imports THIS module; the
dependency arrow stays legal.

TypedDicts (not dataclasses) because records serialize into FunctionGemma
JSONL and ride through fixture files; Python 3.10-compatible optionality via
base-class inheritance instead of typing.NotRequired.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Mapping, Sequence, TypedDict

from coxswain.plr.slot_derivation import DerivedSlot, derive_call_gaps

__all__ = [
    "IntentAgreement",
    "IntentCallExpected",
    "IntentEffect",
    "IntentRecord",
    "PredictedCall",
    "check_intent_agreement",
]


class _IntentCallBase(TypedDict):
    name: str
    params: dict[str, Any]


class IntentCallExpected(_IntentCallBase, total=False):
    """One intended call. ``missing_required``/``unresolved_slots`` carry the
    INTENDED gap state: empty for clean-parse examples, populated for
    clarify-class examples (D7) -- authored in table/as-given order."""

    missing_required: list[str]
    unresolved_slots: list[dict[str, str]]  # {arg_name, reference, resource_type}


class IntentEffect(TypedDict, total=False):
    """One expected effect. ``effect`` uses the method_contracts EffectType
    vocabulary verbatim (join-by-string; see module docstring)."""

    effect: str
    target_ref: str


class IntentRecord(TypedDict):
    """The per-example supervision record (P2.2 harness input)."""

    record_id: str
    utterance: str
    #: Provenance slice: human golden, generated floor, notebook overlay.
    source: Literal["golden", "synthetic", "notebook"]
    #: Intended call sequence; EMPTY for out-of-surface clarify examples (D7).
    calls: list[IntentCallExpected]
    #: Expected effects across the sequence; verified post-execution by the
    #: P2.2 tracker post-conditions (AC-2.2.x keys off these tables).
    expected_effects: list[IntentEffect]


@dataclass(frozen=True)
class PredictedCall:
    """The parse-layer side of the agreement check (name + params ONLY, per
    D11: gap fields are derived, never predicted)."""

    name: str
    params: Mapping[str, Any]


@dataclass(frozen=True)
class IntentAgreement:
    """Per-axis agreement report. ``effects_match`` is intentionally absent:
    effect verification needs execution evidence (P2.2 tracker
    post-conditions), not parse-time data."""

    sequence_match: bool
    names_match: bool
    params_match: bool
    gaps_match: bool
    reasons: tuple[str, ...]

    @property
    def overall(self) -> bool:
        return self.sequence_match and self.names_match and self.params_match and self.gaps_match


def check_intent_agreement(
    predicted_calls: Sequence[PredictedCall],
    intent: IntentRecord,
) -> IntentAgreement:
    """Check a predicted parse against the intent record. Pure; derives every
    gap field itself via ``derive_call_gaps`` (D11) instead of trusting any
    predicted gap annotation."""
    intended = intent["calls"]
    reasons: list[str] = []

    sequence_match = len(predicted_calls) == len(intended)
    if not sequence_match:
        reasons.append(f"sequence length {len(predicted_calls)} != intended {len(intended)}")

    names_match = sequence_match and all(
        p.name == i["name"] for p, i in zip(predicted_calls, intended)
    )
    if sequence_match and not names_match:
        bad = [
            f"{idx}: predicted {p.name!r} != intended {i['name']!r}"
            for idx, (p, i) in enumerate(zip(predicted_calls, intended))
            if p.name != i["name"]
        ]
        reasons.append("name mismatch: " + "; ".join(bad))

    params_match = sequence_match and all(
        dict(p.params) == i["params"] for p, i in zip(predicted_calls, intended)
    )
    if sequence_match and not params_match:
        bad = [
            f"{idx}: predicted {dict(p.params)!r} != intended {i['params']!r}"
            for idx, (p, i) in enumerate(zip(predicted_calls, intended))
            if dict(p.params) != i["params"]
        ]
        reasons.append("params mismatch: " + "; ".join(bad))

    gaps_match = True
    if sequence_match:
        for idx, (p, i) in enumerate(zip(predicted_calls, intended)):
            derived = derive_call_gaps(p.name, p.params)  # KeyError on excluded tool: loud
            want_missing = tuple(i.get("missing_required", ()))
            want_slots = tuple(
                DerivedSlot(
                    arg_name=s["arg_name"],
                    reference=s["reference"],
                    resource_type=s["resource_type"],
                )
                for s in i.get("unresolved_slots", ())
            )
            if derived.missing_required != want_missing:
                gaps_match = False
                reasons.append(
                    f"{idx}: missing_required derived {derived.missing_required} "
                    f"!= intended {want_missing}"
                )
            if derived.unresolved_slots != want_slots:
                gaps_match = False
                reasons.append(
                    f"{idx}: unresolved_slots derived {derived.unresolved_slots} "
                    f"!= intended {want_slots}"
                )

    return IntentAgreement(
        sequence_match=sequence_match,
        names_match=names_match,
        params_match=params_match,
        gaps_match=gaps_match,
        reasons=tuple(reasons),
    )
