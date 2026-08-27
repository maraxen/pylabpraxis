"""Version pins + provenance-tag factory (AC-2.3.x: versions in provenance).

R4/D9: teacher outputs are cached content-addressed by
``(prompt_version, input_hash)`` with ``teacher_model_version`` recorded in
the manifest and on every row's provenance tags -- same inputs + same cache
=> byte-identical corpus, no re-calling of teachers.
"""

from __future__ import annotations

from typing import Final

__all__ = [
    "AGY_BIN",
    "AMBIGUITY_CLASSES",
    "GEMINI_BATCH_SIZE",
    "GEMINI_MODEL",
    "GENERATOR_VERSION",
    "MATRIX_VERSION",
    "PLR_SUBMODULE_SHA",
    "PROMPT_VERSION",
    "SUPERVISION_NL_CLARIFICATION",
    "SUPERVISION_TOOL_CALL",
    "TITANIX_BASE_URL",
    "TITANIX_MODEL",
    "provenance_tags",
]

#: Bump on ANY change to synthesis logic or value pools (part of the RNG
#: seed, so bumps deliberately reshuffle the floor corpus).
GENERATOR_VERSION: Final[str] = "0.1.0"

#: Bump on ANY change to prompt text (changes every cache key by construction).
PROMPT_VERSION: Final[str] = "p23_nlify_v1"

#: Matrix data revision (committed ambiguity_matrix.json).
MATRIX_VERSION: Final[str] = "1"

#: Vendored PLR the namespace table is parity-pinned to (param_namespace.py).
PLR_SUBMODULE_SHA: Final[str] = "dd79c4c89bc008629a1c598ea614be5e6067d1f9"

#: F6 amendment backend (b): titanix vLLM, OpenAI-compatible, verified live.
#: Kept for the smoke-scale lane; NOT used for the full-scale pass (260827
#: user-flagged blocker -- titanix-vllm-primary doesn't work at that scale).
TITANIX_BASE_URL: Final[str] = "http://localhost:8020/v1"
TITANIX_MODEL: Final[str] = "titanix-vllm-primary"

#: F6 amendment backend (c), 260827 (revised same day): Gemini 3.7 Flash via
#: the ``agy`` CLI (NOT the raw HTTP API -- no API key managed by this repo;
#: auth is agy's own). Chosen teacher for the full-scale floor_gen/
#: overlay_gen pass. Non-Gemma model -- D13's teacher-derivative gate
#: (gemma-license-deployment-gate.md §1) does NOT apply; F6's non-Gemma-
#: teacher assumption still holds. ``agy models`` lists effort-tiered IDs
#: (``-high``/``-medium``/``-low``); bare ``gemini-3.7-flash`` is not a valid
#: ``--model`` value. "medium" balances teacher-quality against the fixed
#: per-call overhead observed empirically (~16-22K tokens/call before any
#: content, heavily cache-discounted on repeat calls within a session).
GEMINI_MODEL: Final[str] = "gemini-3.7-flash-medium"
AGY_BIN: Final[str] = "agy"

#: Cells/items grouped into ONE ``agy`` invocation for the full-scale pass
#: (260827 user-directed: batch rather than issue ~800 individual calls).
#: Empirically, per-call fixed overhead (large cached system-prompt-ish
#: context, ~7-11s wall-clock) dominates at batch size 1; batching amortizes
#: it. 20 is a starting point, not measured against the real full corpus --
#: retune after the first live full-scale run.
GEMINI_BATCH_SIZE: Final[int] = 20

#: The four ambiguity classes (task deliverable 1).
AMBIGUITY_CLASSES: Final[tuple[str, ...]] = (
    "none",
    "missing-slot",
    "ambiguous-referent",
    "out-of-surface",
)

#: Supervision kinds per D7/D11.
SUPERVISION_TOOL_CALL: Final[str] = "tool_call"
SUPERVISION_NL_CLARIFICATION: Final[str] = "nl_clarification"


def provenance_tags(teacher_model_version: str) -> dict[str, str]:
    """The exact provenance tag set required on EVERY example (deliverable 5)."""
    return {
        "provenance": "coverage",
        "generator_version": GENERATOR_VERSION,
        "prompt_version": PROMPT_VERSION,
        "teacher_model_version": teacher_model_version,
    }
