---
title: 'Coxswain P2.5 slice gate: GO/NO-GO for P2.6 fine-tune spend'
description: 'Blocking gate doc (backlog 480): baseline failure distribution (P2.1 reports incl. recorded-artifact mode) vs coverage-plan adequacy vs ambiguity-class balance, with provisional threshold anchors and an explicit RECOMMENDATION for the orchestrator jury before any P2.6 spend.'
task_id: 260825_copilot_pipeline_spec
date: '260825'
status: ready-for-jury
backlog_item: 480
---

# P2.5 slice gate — baseline vs coverage plan vs class balance

Spec: `.praxia/docs/specs/260825_coxswain-phase-2-functiongemma-copilot-p.md`
rev2 §5 P2.5 / §7 AC-2.5.x. This doc gates P2.6 (fine-tune) spend; the
orchestrator runs a blocking jury on it.

## RECOMMENDATION: **NO-GO — iterate data**

Do not spend P2.6 yet. The assembled corpus is 188 examples against the
~1000-example target (81% short), the D2 real-baseline run is still blocked
on Gemma license/token (only a partial mechanics proof exists, n=8), and the
train-side negative mixing is thin in two of three clarify classes. All three
deficits are closable with work that already has landed tooling — see §5.
A jury override toward conditional-GO would be spending a 270M full-parameter
fine-tune on a fifth of the planned data with no live-model baseline point;
nothing in the current evidence makes that the cheap path.

## 1. What landed as inputs (all jury-cleared at Gate 1)

| Branch | Artifact | Rows |
|---|---|---|
| P2.1 golden | `training/golden/golden_pairs.jsonl` (+ sidecar) | 88 |
| P2.3 coverage floor | `training/out/corpus_p23_smoke.jsonl` | 30 |
| P2.4 naturalness overlay | `training/overlay_gen/out/overlay_smoke.jsonl` | 92 |
| P2.2 verify harness | execution-verification substrate behind synthetic labels | (code, no rows) |

Assembly (`training/assemble/`, assembly_version 0.1.0): ONE
FunctionGemma-native JSONL, every row `{metadata, tools[], messages[]}`,
developer turn byte-matching the committed scaffold template (no date
injection, D6-rev2). PLR_SOURCE_SHA `dd79c4c89bc008629a1c598ea614be5e6067d1f9`
(= submodule HEAD, = golden manifest pin).

## 2. Assembled corpus (after the assembly validation gate)

22 input rows were excluded whole, loudly counted in the manifest
(`exclusions.total = 22`): every exclusion is a multi-value argument on a
param the shipped surface declares SCALAR (`aspirate.volume_ul [50,75,20]`,
`transfer.destination [p1,p2]`) — parallel/multi-channel calls the declared
13-tool grammar cannot express and serving-side schema validation would
reject. Keeping them would train schema violations; padding is forbidden by
the task line.

| Split | clean_parse | missing_slot | ambiguous_referent | out_of_surface | total |
|---|---|---|---|---|---|
| eval | 66 | 12 | 12 | 12 | 102 |
| train | 71 | 1 | 5 | 9 | 86 |
| total | 137 | 13 | 17 | 21 | **188** |

Provenance: golden 88 (ALL eval, per task AC — human-authored instruments
never train on), coverage 20 kept / 10 excluded, naturalness 80 kept / 12
excluded. Eval clarify total = 36 >= D8's 30 floor, spanning all three
classes. Splits are disjoint by construction; stratification is
provenance x class x verb (rule recorded in the manifest).

**Shortfall: 812 examples below target.** Reason (also in manifest):
P2.3/P2.4 branches landed at smoke scale — the committed outputs are the 30 +
92 row smoke runs; full-scale generation (`floor_gen` over all 43 matrix
cells x3 examples ≈ 129 raw; `overlay_gen --full` over all notebooks) is
wired but was not this item's mandate. Assembly merges what exists and pads
with nothing.

## 3. Baseline failure distribution (what a fine-tune must fix)

Source: `training/eval/reports/260825_recorded_fixture_report.json`
(mode=recorded_artifacts; labeled NOT-live-inference, PARTIAL: 8 of 62
in-scope scored; base revision unpinnable — gated repo, no token).

| Metric | Value | Wilson 95% |
|---|---|---|
| exact-match accuracy | 0.75 (6/8) | [0.409, 0.929] |
| clarify recall | 0.50 (2/4) | [0.150, 0.850] |
| clarify precision | 1.00 (2/2) | [0.342, 1.000] |

Failure anatomy (the two exact-match misses):

1. `golden-clean-dispense-03` (clean_parse): volume transcription error —
   predicted 50 where the utterance states 15. Numeric grounding slips on an
   otherwise-correct selection. Class-relevant because clean positives are
   what T_acc measures.
2. `golden-missing-slot-03` (missing_slot): HALLUCINATED an unstated param
   (`destination='waste_plate_A1'` from a "Dispense 100 microliters." prompt)
   AND therefore derived the wrong gap fields. This is exactly the failure
   D7/D11 clarify supervision exists to suppress, and it co-occurred with a
   clarify FALSE NEGATIVE (no abstention). Clarify FN split: one
   out-of-surface + one missing-slot miss; zero false-positive clarifies.

Read: base-model failures cluster on (a) numeric transcription and (b)
missing-slot hallucination-without-abstention. Both are trainable behaviors,
but (b) needs enough train-side negatives to learn from — which §4 shows we
do not yet have at scale.

## 4. Adequacy analysis

### 4.1 Coverage plan vs corpus

- Train side holds 86 rows (71 positive / 15 negative ≈ 17% negative mixing —
  inside D7's "controlled ratio" spirit, but from only 15 negative examples).
  The research §2a precedent (40 synthetic examples moving tool-selection
  2/20 -> 16/20) suggests small data CAN teach selection INTENT; our eval,
  however, demands generalization across 13 tools plus calibrated abstention,
  and D8's slices deserve more than ~12 support points per clarify class.
- Verb coverage is complete on positives (every one of the 13 included verbs
  appears in both splits via golden), but synthetic diversity per verb is
  smoke-scale (largest naturalness stratum n=27).
- The 43-cell committed ambiguity matrix supports ≈129 floor examples/cell-
  sweep; today's corpus carries 20 kept. The generator to fix this is LANDED;
  only teacher spend + a full run are missing.

### 4.2 Ambiguity-class balance

Eval side is balanced by construction (12/12/12 golden + synthetic support).
Train side is NOT balanced: out_of_surface 9, ambiguous_referent 5,
missing_slot **1**. A model trained now would see essentially no
missing-slot-negative gradient — the single worst-supported behavior given
§3's failure anatomy. This alone would predictably fail T_clr_recall's intent
even if T_acc improved.

### 4.3 Measurement caveats the jury should hold

- **UPDATE 260827: D2 unblocked.** Real local CPU inference now runs
  (HF_TOKEN exported; gated-repo terms already accepted). A harness bug was
  found and fixed in the same pass: the prompt builder never applied the
  model's chat template or passed the 13 tool declarations, producing a
  degenerate first result (0.194 acc, uniform empty completions) that was
  NOT a real capability measurement — see
  `260825_p25_provisional_thresholds.md` §5 for the fix and the corrected
  real baseline (T_acc 0.210 [0.127,0.326], T_clr_recall 0.833
  [0.642,0.933], T_clr_prec 0.556 [0.396,0.705], n=62,
  `training/eval/reports/260827_baseline_real.json`). Anchors in the
  thresholds doc remain provisional policy margins (unchanged, per D8's
  one-revision-at-P2.6 rule) but are now checked against a real baseline
  point instead of the n=8 mechanics-proof partial.
- Static clarify scoring covers out-of-surface + missing-slot only (24 eval
  items); ambiguous_referent verifies at P2.9 with live grounding (F1-rev2/C-M1).
  The three-class corpus sizing (36) satisfies D8's letter; the statically
  scoreable slice is smaller than 30.

## 5. What flips this to GO

1. **UNBLOCKED 260827: backend chosen + wired + real-verified (Gemini 3.7
   Flash via `agy`), full-scale run still pending.** User named the
   replacement backend for the pass titanix couldn't handle at full scale:
   `gemini-3.7-flash-medium`, reached by shelling to the local `agy` CLI
   (NOT a raw API key — `agy` owns its own auth, already installed +
   authenticated on this machine). Non-Gemma — D13 re-check does not apply
   (see the decision doc). Wired end-to-end and verified against real `agy`
   calls (8 cells, 24 examples, pass_rate=1.000):
   `floor_gen.teachers.GeminiTeacher` (`--backend gemini --batch-size N` in
   `floor_gen/cli.py`, batched per user direction — group many items per
   call rather than ~800 individual calls) and
   `overlay_gen.pair_builder.GeminiTeacherClient` (`--backend gemini` in
   `overlay_gen/run_smoke.py`, not yet batched — fast-follow), both
   enforcing the response contract via `agy --json-schema` guided decoding.
   Full design, empirical caveats (guided-decoding null-handling quirks,
   agy schema requirements), and PLR coverage/brittleness analysis:
   `.praxia/docs/decisions/260827_teacher-backend-gemini-3-7-flash-for-full-scale-floor_gen-overlay_gen-pass.md`.
   **Still to do**: no external setup needed; run `floor_gen` over all cells
   + `overlay_gen --full`, teacher caches make the re-run
   incremental; re-assemble; target >= ~800 assembled rows with missing_slot
   train mass >= ~30 and each clarify class >= ~40 eval or better.
2. ~~Unblock the REAL baseline~~ **DONE 260827** — see §4.3 update and
   `260825_p25_provisional_thresholds.md` §5. Real T_acc (0.210) confirms
   the base model needs the fine-tune; T_clr_recall (0.833) already clears
   anchor zero-shot, a useful signal for D5's training recipe.
3. Re-run THIS gate with fresh numbers (assembly idempotency makes step 1
   byte-comparable apart from intended growth).

## 6. Deliverable cross-links

- Corpus + sidecar + manifest: `training/assemble/out/` (manifest records
  versions, provenance counts, exclusions, shortfall, split rule).
- Scaffold template: `training/assemble/developer_scaffold_template.txt`.
- Thresholds (PROVISIONAL per D8):
  `.praxia/docs/specs/260825_p25_provisional_thresholds.md`.
- Storage ledger updated (C-m8): see footprint doc §6 — assembly adds ~1.24 MB
  tracked repo bytes, ZERO staged-dist bytes (trainer input, never served).
