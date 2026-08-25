---
title: 'Coxswain Phase 2: FunctionGemma copilot pipeline'
description: 'Spec for the synthetic-data pipeline, functiongemma-270m-it fine-tune, browser serving via Transformers.js/WebGPU behind --with-coxswain, and ParseSource integration. Authored from contemplex session 70ae4959 (winner: Approach C hybrid staged corpus), recon 260825_copilot-pipeline-recon.md, and research 260825_functiongemma-training-serving-research.md.'
status: draft-adversarial
task_id: 260825_copilot_pipeline_spec
date: '260825'
---

# Coxswain Phase 2 — FunctionGemma copilot pipeline

## 1. Problem and goal

Coxswain's deterministic substrate shipped complete (W0–W6, backlog 4388–4395): FFT gate,
propose/confirm and clarification cards, audit trail, pre-simulation preview, `--with-coxswain`
build plumbing. The parse layer is a fixture-backed stub (`FixtureParseSource`,
`coxswain/src/coxswain/parse_source.py`) and the chat panel runs a demo regex stub mirroring three
golden utterances (`coxswain-shell.js:52-81`). This spec covers everything needed to replace those
stubs with a real model: generate execution-verified training data, fine-tune
`google/functiongemma-270m-it`, serve it in-browser, and integrate it through the existing
`ParseSource` seam — decomposed into a backlog DAG where every item dispatches without further
design ambiguity.

**Inputs this spec is bound by** (do not re-litigate):
- Scoping: `.praxia/docs/research/260824_gemma-finetuned-plr-voice-text-copilot-scoping.md`
- Recon: `.praxia/docs/research/260825_copilot-pipeline-recon.md` (code-verified, corrects several scoping-doc claims)
- Research: `.praxia/docs/research/260825_functiongemma-training-serving-research.md` (primary-source web facts)
- Contemplex session `70ae4959`: winner = Approach C hybrid staged corpus; pre-mortem counters adopted below.
- Locked constraints (from session frame): safety architecture [F1], import boundary [F2], delivery mechanism [F3],
  lazy-load own-worker [F4], text-input-first [F5], teacher/distillation split [F6]. Details §3.

## 2. Decisions locked by this brainstorm

| # | Decision | Basis |
|---|----------|-------|
| D1 | Data strategy = Approach C: schema-driven synthesis floor (B) + corpus naturalness overlay (A), deduped, all execution-verified | session 70ae4959 winner; B alone is fallback under time pressure (steelman recorded) |
| D2 | Baseline-first gate inside C: measure off-the-shelf model on a ~50-pair golden set before committing generation effort | Approach D absorbed as internal gate |
| D3 | Serving = greedy decoding (`do_sample:false`) + hardened parser for FunctionGemma's native call syntax + schema validation + bounded repair-retry (max 2). Constrained decoding explicitly OUT (transformers.js PR #1758 unmerged, package unpublished; FunctionGemma emits bespoke `<escape>` token syntax, not JSON) | research §4; Physics Playground precedent (greedy + regex works in production) |
| D4 | Quantization = ONNX q4f16 (~426 MB) primary, fp16 (~570 MB) fallback for weak WebGPU; exactly one dtype cached per device class | research §3; q4 (801 MB) rejected — untied 262k-vocab embeddings dominate, q4 saves nothing |
| D5 | Fine-tune = TRL SFTTrainer FULL-parameter (no LoRA at 270M), Google Mobile-Actions recipe hyperparams (lr 1e-5 cosine, completion_only_loss=True, bf16), venue decided at run time: Colab/Kaggle A100 default, Engaging SLURM via myxcel fallback, google/functiongemma-tuning-lab Space as no-code option | research §2; scoping doc's LoRA-family idea DEMOTED to post-MVP (no official multi-adapter story) |
| D6 | Dataset format = FunctionGemma-native JSONL `{metadata, tools[], messages[]}`, developer-role scaffold verbatim per formatting guide, assistant supervision as tool_calls, `completion_only_loss` | research §2a/§2b; mobile-actions shape |
| D7 | Clarify supervision is a FIRST-CLASS class: negative examples (out-of-surface utterances → NL clarification turn, not tool_call) and incomplete-slot examples (→ clarification naming the missing argument) mixed into training at a controlled ratio; base model's Irrelevance prior (73.7 BFCL) must be preserved, not overwritten | research §7; pre-mortem failure #2 |
| D8 | Promotion gates are THREE-number: parse exact-match accuracy ≥ threshold T_acc on held-out eval, clarify recall ≥ T_clr_recall AND clarify precision ≥ T_clr_prec (exact thresholds set at item P2.5 from baseline-measured spread, not invented now) | pre-mortem counter for clarify-class collapse |
| D9 | Eval set is versioned and regenerable, keyed to PLR wheel `PLR_SOURCE_SHA`; regeneration is a pipeline stage, never a one-time artifact | pre-mortem failure #1 |
| D10 | Phase-2 scope boundary: voice input, candidate-resolution adapter (free-text clarify answers), visual ghost rendering, and multi-step call chaining are ALL OUT. Single-turn parses only; clarification re-entry stays deterministic (existing FFT/cards) | session frame F5/F6; scoping doc LoRA note |

## 3. Fixed constraints (inherited, enforced by tests)

1. **F1 Safety**: FFT gate unchanged and model-free; the model produces candidate `ParsedCall`s only;
   zero new kernel-side authority; audit trail semantics untouched.
2. **F2 Import boundary**: `coxswain/` never imports `praxis.backend.*` (NFR-1/NFR-2, AST-enforced);
   training/generation code lives in a NEW top-level `training/` directory (uv workspace member),
   which MAY import praxis.backend pieces (it runs in CPython CI/lab context, never ships to browser).
3. **F3 Delivery**: model artifacts NEVER git-committed (R6/R8 zero-tracked-binaries); fetched by a
   script into gitignored `web-repl/vendor/models/`, tracked via a NEW `models` array in build manifest
   (wheels-shaped: name/filename/source_sha/sha256/bytes — NOT the js/css coxswain_assets key);
   G5 forbids CDN at runtime; lazy fetch on first chat interaction from site origin.
4. **F4 Worker**: inference in its own module Web Worker (mount point per recon §5.2:
   `overlay/assets/coxswain/parse_worker.js`), progress events surfaced as system lines, Cache API
   persistence by default with `navigator.storage.persist()` requested after first download.
5. **F5 Text-first**: Web Speech API push-to-talk is a later phase; not in this DAG.
6. **F6 Roles**: strong models (teacher) generate NL + judge quality; FunctionGemma only ever distills.
   **Amendment (260825, user-directed): the teacher does NOT require external Opus/Sonnet routing.**
   Two sanctioned teacher backends, both already wired: (a) **ox-alpha via spawned jcode swarm
   workers** — each generation batch is a worker task writing JSONL directly (same mechanism used to
   build Coxswain itself); (b) **titanix-vllm-primary** (`~/.praxia/backends.toml`, localhost vLLM,
   verified live 260825, 32k ctx, max_concurrent 3) for high-volume bulk passes where per-example
   cost matters more than peak quality. Quality tiering: ox-alpha authors the ambiguity-injection
   and golden-set work; titanix handles mechanical NL-ification volume; P2.1's golden-50 stays
   human-reviewed regardless of generator.

## 4. Corrected ground truth (recon findings the implementer MUST honor)

- Execution backend is `LiquidHandlerChatterboxBackend`
  (`external/pylabrobot/pylabrobot/liquid_handling/backends/chatterbox.py:24-242`); `ChatterBoxBackend`
  is a deprecated tombstone raising NotImplementedError. Verification harness builds on
  `praxis/backend/core/simulation/chatterbox_runner.py` (`DeckFactory.create_setup`, `run_single`;
  DB-free by design, imports verified SQLAlchemy-free).
- Runnable protocol corpus = `praxis/protocol/protocols/` (6 `@protocol_function` files,
  keyword-call style `vols=[...]`). `tests/fixtures/protocols/*.py` are static-analysis fixtures,
  NOT executable — do not use as pairing material.
- PLR docs corpus = **58** notebooks; LH-core subset is `user_guide/00_liquid-handling/**` (16).
- Golden fixtures live at `coxswain/tests/fixtures/parsed_calls/` (6 files); their shape IS the
  ParseSource contract: `{utterance, name, verb, receiver_type, params, missing_required,
  unresolved_slots[{arg_name, reference, resource_type}], expected_phrase}`. The model predicts
  `{name, params, missing_required?, unresolved_slots?}` ONLY — tier/verb/effects metadata comes from
  `TOOL_SCHEMA` keyed by `name` (`tool_schema.py:147-150`) and is never a prediction target.
- **TOOL_SCHEMA drift (must fix before any data generation)**: `tool_schema.py` declares `mix`,
  `blow_out`, `touch_tip` (:103-111) and `dispense_to_waste` (:83-90); vendored LiquidHandler has
  NONE of these (verified by inspect + grep). Reconciliation is item P2.0.

## 5. Work items (the DAG, one line each; full ACs §7)

| ID | Item | Depends on |
|----|------|-----------|
| P2.0 | Tool-schema reconciliation: generated-signature sweep vs `TOOL_SCHEMA`, pinned to `PLR_SOURCE_SHA`; remove/justify phantom verbs; assert subset relation as a test | — |
| P2.1 | Golden-50 set (hand-authored, human-reviewed, provenance=golden) + baseline eval harness reporting the three D8 metrics for off-the-shelf checkpoint | P2.0 |
| P2.2 | Execution-verify harness: `chatterbox_runner`-based async verifier with tracker post-conditions + `set_strictness(STRICT)` + intent-record slot-agreement axis | — (parallel with P2.1) |
| P2.3 | Coverage-floor generator: enumerate tool schema × deck shapes → structured calls + systematic ambiguity matrix (missing-slot / ambiguous-referent / out-of-surface classes) → teacher NL-ification prompts | P2.0 |
| P2.4 | Naturalness overlay: mine 16 LH-core notebooks + 6 runnable protocols → real calls → teacher NL pairs → dedupe against floor | P2.0 |
| P2.5 | Corpus assembly + slice gate: assemble ~1000-example calibration/training split (train/eval stratified by provenance and ambiguity class), regenerate keyed to PLR sha; GO/NO-GO review comparing baseline (P2.1) failure distribution vs coverage plan | P2.1, P2.2, P2.3, P2.4 |
| P2.6 | Fine-tune run: TRL SFT full-parameter on chosen venue; produce merged checkpoint + eval report against P2.1 harness + held-out eval split; promotion per D8 thresholds | P2.5 |
| P2.7 | Export/delivery spike: optimum ONNX export of fine-tuned gemma3_text checkpoint → q4f16 quantization; `fetch_models.py` + `models` manifest array + first-use integrity check; measure real footprint beside live Pyodide | P2.6 |
| P2.8 | Serving worker: `parse_worker.js` (lazy module worker), greedy decode, hardened `<start_function_call>` grammar parser, schema validation + bounded retry, envelope-wrapped results on `praxis_coxswain`, progress/cache system lines | P2.7 |
| P2.9 | ParseSource integration: worker-backed `ParseSource` implementation behind the existing interface; swap stub at shell layer; FR-3 parity tests extended to model outputs; kernel-guard bridge for in-tab grounding if still missing (recon GAPS #6) | P2.8 |

Critical path: P2.0 → P2.1 → P2.5 → P2.6 → P2.7 → P2.8 → P2.9. Parallel branches: P2.2 ∥ P2.1;
P2.3 ∥ P2.4 after P2.0.

## 6. Non-goals (explicit)

Voice input; candidate-resolution adapter; visual ghosting of disambiguation candidates; multi-step
chained calls; production-mode (`WorkcellRuntime`) backend; LoRA adapter family; publishing the
dataset or model publicly (Gemma license + lab-specificity).

## 7. Acceptance criteria (per DAG item)

**P2.0 — Schema reconciliation**
- AC-2.0.1: Test asserts every `TOOL_SCHEMA.name` has a same-named public method on the vendored
  LiquidHandler (or mapped receiver class), pinned to current `PLR_SOURCE_SHA`.
- AC-2.0.2: Phantom entries removed or annotated `experimental: true` and EXCLUDED from generation.
- AC-2.0.3: Required-param derivation per method matches `inspect.signature` output (table in recon §1.4).

**P2.1 — Golden set + baseline**
- AC-2.1.1: ≥50 hand-authored pairs covering every TOOL_SCHEMA verb at least twice, ≥8
  clarify-expected examples spanning missing-slot, ambiguous-referent, out-of-surface classes.
- AC-2.1.2: Harness reports {exact_match_accuracy, clarify_recall, clarify_precision} for any
  checkpoint given any JSONL pair-set; runs in CPython CI (<2 min for 50 pairs via API-free local
  inference OR recorded-artifact mode for CI).
- AC-2.1.3: Baseline numbers recorded in-tree (doc + JSON) — this is the D2 gate artifact.

**P2.2 — Execution-verify harness**
- AC-2.2.1: Verifier accepts a call sequence + intent record; returns pass/fail + serialized
  before/after state diff; raises on STRICT-mode anomalies.
- AC-2.2.2: Post-condition checks: mounted-tips delta matches intent; source volume decreased /
  target increased within tolerance for transfer/aspirate/dispense examples.
- AC-2.2.3: Slot-agreement check: every grounded arg in the executed call matches the intent record
  (catches executes-cleanly-but-wrong-reading).
- AC-2.2.4: ≥100 verifications complete <5 min single-process.

**P2.3/P2.4 — Generators**
- AC-2.3.1: Floor generator emits ≥1 example per (verb × ambiguity-class) cell of its matrix;
  matrix itself committed as data.
- AC-2.3.2: Every emitted pair carries intent record + provenance tag (`coverage|naturalness|golden`)
  + generator/prompt version.
- AC-2.4.1: Overlay pairs reference only calls that independently pass P2.2 verification.
- AC-2.4.2: Dedup: no duplicate normalized utterances corpus-wide.

**P2.5 — Assembly + slice gate**
- AC-2.5.1: Corpus JSONL validates against the FunctionGemma dataset format (developer scaffold
  byte-identical to formatting guide example).
- AC-2.5.2: Split report: counts by provenance × ambiguity-class × verb; eval split disjoint from
  train by construction.
- AC-2.5.3: Manifest records `PLR_SOURCE_SHA` + generator versions; regeneration script is idempotent.
- AC-2.5.4: GO/NO-GO doc comparing baseline failures (P2.1.3) to coverage plan; explicit sign-off.

**P2.6 — Fine-tune**
- AC-2.6.1: Training config committed (venue, deps pins `transformers==4.57.1 trl==0.25.1`, epochs, lr).
- AC-2.6.2: Eval report shows D8 metrics on held-out split AND on golden-50; promotion requires
  meeting T_acc/T_clr_recall/T_clr_prec set in P2.5.4, else iterate-or-stop decision recorded.
- AC-2.6.3: Clarify-behavior check: model emits NO tool_call for every out-of-surface golden example.

**P2.7 — Export/delivery spike**
- AC-2.7.1: Fine-tuned checkpoint exports to ONNX q4f16; smoke inference matches Python-side outputs
  on 20 utterances (token-level or semantic-equivalent).
- AC-2.7.2: `fetch_models.py` lands artifact in gitignored vendor dir; manifest gains `models` array
  (sha256, bytes, source_sha); zero new tracked binaries (repo-wide grep gate).
- AC-2.7.3: Footprint measurement doc: download size, peak memory beside live Pyodide kernel, decode
  tok/s on target hardware class; go/no-go on q4f16 vs fp16 recorded.

**P2.8 — Serving worker**
- AC-2.8.1: First chat interaction triggers lazy fetch with byte-progress system lines; second visit
  uses Cache API without network (testable offline).
- AC-2.8.2: Parser handles the full call grammar incl. `<escape>` round-trip; malformed output →
  bounded retry (≤2) → structured `clarify:parse_failed` payload; never throws raw into UI.
- AC-2.8.3: Worker posts envelopes valid under `assertValidEnvelope`; foreign-session messages dropped.
- AC-2.8.4: Default build contains zero coxswain/model assets (AC-11 pattern holds); flagged build
  stages worker but NOT the binary (binary is fetched, per F3).

**P2.9 — Integration**
- AC-2.9.1: `ParseSource.parse()` backed by worker round-trip; existing fixture corpus passes
  unchanged through the new source (contract regression).
- AC-2.9.2: FR-3 phrase parity tests extend to ≥20 model-output examples (phrase derived from parsed
  fields, not from the utterance).
- AC-2.9.3: End-to-end: typed utterance → propose card renders literal call; confirm re-runs cues 0/3;
  audit trail records the turn. Demo stub deleted.
- AC-2.9.4: Kernel-side grounding module ships as fetched Python module if cue-2/3 need it in-tab
  (closes recon GAPS #6); otherwise documented why not needed yet.

## 8. Risks (from pre-mortem + research, with counters)

| Risk | Counter |
|------|---------|
| Silent eval-set rotation on PLR upgrades | D9: versioned regeneration keyed to `PLR_SOURCE_SHA` (AC-2.5.3) |
| Clarify-class collapse (over-triggering) | D7 controlled negative ratio + D8 precision/recall dual gate (AC-2.6.2/2.6.3) |
| Serving reality gap (latency/decoding) | P2.7.3 early footprint go/no-go; D3 bounded-retry UX specified up front |
| ONNX export friction for gemma3_text post-v4 restructure | P2.7.1 smoke-parity test; -GQA community export proves arch converts |
| Teacher-output licensing/provenance | Provenance tags mandatory (AC-2.3.2); Gemma terms reviewed at P2.6 (fine-tunes inherit license) |
| Storage budget: ~479 MB site + 426 MB model ≈ 905 MB of 1 GB Pages limit | Single-dtype policy (D4); prune re-check at P2.7; CDN escape explicitly forbidden by G5 |

## 9. Open questions (resolved at item time, not blocking DAG creation)

- Exact T_acc/T_clr thresholds: set empirically at P2.5.4 from baseline spread (D8).
- Training venue per run: Colab A100 default; Engaging SLURM via myxcel if Colab unavailable (D5).
- Whether cue-2/3 in-tab grounding bridge is required for P2.9 or deferrable (AC-2.9.4 decides).
