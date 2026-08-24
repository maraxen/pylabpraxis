# Coxswain

Working name, not yet the published one (see the naming section of the scoping doc below).

A baseline library for deploying a fine-tuned function-calling model in the browser against a
live grounding source: model loading, a deterministic fast-and-frugal-tree triage gate for
ambiguous/underspecified commands, and propose-confirm execution primitives.

First and, for now, only consumer: translating voice/text lab instructions into validated
PyLabRobot calls inside praxis's `web-repl`. Scope is intentionally narrow to that one consumer
until a second one actually materializes -- see
`.praxia/docs/research/260824_gemma-finetuned-plr-voice-text-copilot-scoping.md` for the full
scoping record, including the naming decision, the state-architecture writeup, and the open
kernel-ownership fork that hasn't been resolved yet.

## Status

Scaffold only. No model loading, no FFT gate, no PLR integration yet.

## Boundary

Same import discipline as the existing `praxis`/`web-repl` split (ADR
`.praxia/docs/decisions/260817_repl-layout-and-delivery-mechanism.md` §5.2): no import from
`praxis.backend.*`. Anything this package needs from praxis's backend gets reimplemented
dependency-free here, not imported.
