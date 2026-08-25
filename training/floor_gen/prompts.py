"""Teacher NL-ification prompt builder (task deliverable 3).

Pure function of (example, declarations). The FULL prompt text -- system +
user -- is versioned by ``PROMPT_VERSION``; any text change bumps that
constant, which changes every cache key, which is exactly how R4/D9
idempotency stays honest.

The user block embeds the FunctionGemma tool declarations rendered from the
namespace table (juror finding 6a) so the teacher sees the same tools[] the
training rows will carry, plus the pinned value-format conventions (finding
6b) phrased for natural language.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Final

from floor_gen.declarations import render_declarations
from floor_gen.synth import SynthExample
from floor_gen.value_formats import VALUE_FORMAT_CONVENTIONS
from floor_gen.versions import PROMPT_VERSION

__all__ = ["build_prompt", "compute_input_hash", "response_shape_instructions"]


#: Shared contract for BOTH backends: the assistant-under-test must reply with
#: EXACTLY one minified JSON object on a single line.
_RESPONSE_SHAPE: Final[str] = (
    "Respond with EXACTLY ONE JSON object and nothing else -- no markdown, no "
    "code fences, no commentary. Shape:\n"
    '{"utterance": "<the user utterance>", "clarification": <string or null>}\n'
    '"utterance": one single-turn user message, quoted speech only.\n'
    '"clarification": null unless instructions below require an assistant '
    "clarification turn."
)


def response_shape_instructions() -> str:
    return _RESPONSE_SHAPE


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def compute_input_hash(payload: dict[str, Any]) -> str:
    """input_hash over the SEMANTIC inputs (version-independent); the cache
    composes it with prompt_version into the full key."""
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


_CLASS_INSTRUCTIONS: Final[dict[str, str]] = {
    "none": (
        "Write a natural, specific user utterance asking for EXACTLY this call. "
        "Mention every parameter: quantities as '<n> microliters', locations using "
        "the given names/positions verbatim."
    ),
    "missing-slot": (
        "Write a natural user utterance that requests this call but OMITS the "
        "parameter '{missing_param}' entirely -- never mention it, never hint at a "
        "value for it. All other parameters MUST appear naturally."
    ),
    "ambiguous-referent": (
        "Write a natural user utterance requesting this call, but refer to the "
        "'{slot_param}' argument ONLY with a vague phrase such as '{vague_hint}' -- "
        "NEVER its concrete id. All other parameters appear normally and concretely."
    ),
    "out-of-surface": (
        "The request below is OUTSIDE the supported tool surface. Write (1) a "
        "natural user utterance asking for it, and (2) 'clarification': a short "
        "friendly assistant reply that says the request is not something the lab "
        "copilot can do, and offers the closest supported alternative from the "
        "tool list if one exists. Do NOT invent any tool call."
    ),
}


def build_prompt(example: SynthExample) -> dict[str, str]:
    """Build {system, user, input_hash} for one example."""
    cell = example.cell
    cls = cell.ambiguity_class

    if cls == "out-of-surface":
        supported = ", ".join(sorted(d["name"] for d in render_declarations()))
        user = "\n".join(
            [
                f"Task context (prompt_version={PROMPT_VERSION}, class=out-of-surface):",
                f"Off-surface request seed: {cell.off_surface_request}",
                f"Supported tools (for the alternative offer): {supported}",
                _CLASS_INSTRUCTIONS["out-of-surface"],
                _RESPONSE_SHAPE,
            ]
        )
    else:
        assert cell.verb is not None
        declarations = render_declarations([cell.verb])
        instruction = _CLASS_INSTRUCTIONS[cls]
        if cls == "missing-slot":
            assert cell.missing_param is not None
            instruction = instruction.replace("{missing_param}", cell.missing_param)
        if cls == "ambiguous-referent":
            vague = "the plate"
            instruction = instruction.replace("{slot_param}", cell.slot_param or "?").replace(
                "{vague_hint}", vague
            )
        calls_block = canonical_json({"calls": example.structured_calls})
        formats_block = json.dumps(VALUE_FORMAT_CONVENTIONS, sort_keys=True)
        user = "\n".join(
            [
                f"Task context (prompt_version={PROMPT_VERSION}, cell={cell.cell_id}):",
                "Tool declaration for this row (FunctionGemma shape):",
                canonical_json(declarations[0]),
                "Structured call(s) to NL-ify (corpus-B keyword style kwargs):",
                calls_block,
                "Value-format conventions (volumes uL floats; wells A1-style):",
                formats_block,
                "Instruction:",
                instruction,
                _RESPONSE_SHAPE,
            ]
        )

    system = (
        "You are a data-generation teacher for a liquid-handling lab copilot "
        "(FunctionGemma training corpus, coverage floor). You convert structured "
        "tool calls into realistic single-turn user utterances under exact "
        "ambiguity-class constraints. You follow the output contract literally."
    )
    payload = {
        "prompt_version": PROMPT_VERSION,
        "cell_id": cell.cell_id,
        "example_index": example.index,
        "ambiguity_class": cls,
        "structured_calls": example.structured_calls,
    }
    return {"system": system, "user": user, "input_hash": compute_input_hash(payload)}
