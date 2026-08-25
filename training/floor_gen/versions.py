"""Version pins + provenance-tag factory (AC-2.3.x: versions in provenance).

R4/D9: teacher outputs are cached content-addressed by
``(prompt_version, input_hash)`` with ``teacher_model_version`` recorded in
the manifest and on every row's provenance tags -- same inputs + same cache
=> byte-identical corpus, no re-calling of teachers.
"""

from __future__ import annotations

from typing import Final

__all__ = [
    "AMBIGUITY_CLASSES",
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
TITANIX_BASE_URL: Final[str] = "http://localhost:8020/v1"
TITANIX_MODEL: Final[str] = "titanix-vllm-primary"

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
