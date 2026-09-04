---
title: 'P2.6d pre-registration: near-surface out-of-surface matrix cells, arm-A retrain vs A3 on the frozen eval split'
description: Pre-registration (task 260903_p26d_near_surface, backlog 4940) for adding six near-surface out-of-surface cells to the ambiguity matrix (v3, appended so the 685 existing record ids and the 228-row eval pin stay unchanged), generating their rows with the unchanged base prompt, assembling 0.1.6 with a 24-row near-surface probe, retraining the arm-A recipe once and scoring it against arm A3 (control) under the unchanged promotion rule; tripwire, no-regression, retention and near-surface probe predictions registered before generation.
status: registered
task_id: 260903_p26d_near_surface
date: '260903'
---
# P2.6d pre-registration: near-surface out-of-surface matrix cells, arm-A retrain vs A3 on the frozen eval split


Registered BEFORE any matrix, generator, assembler, or training change (commit order is the
proof). Backlog 4940 (depends on 4933, done). Sidecar `scripts/experiments/p26d_finetune.bth.toml`.
Decision it follows: P2.6c decision doc `.praxia/docs/audits/260903_p26c-oos-natural-decision.md`
§6 -- the tripwire rows are near-surface topical confusions no matrix cell covers. Chosen
autonomously 2026-09-03 (the user delegated the direction) over the recipe sweep (confounded
with a data change; the accuracy ceiling is golden misses, not recipe) and the eval revision
(quantified in parallel as a jury brief, `research/260903_*eval-revision*`, scorer untouched).

## 1. What is fixed (frozen), what changes

| Item | Status |
|---|---|
| Eval split | **FROZEN.** The 228 rows pinned by record_id AND native-row content in `training/assemble/data/eval_split_pin.json` (rows sha256 `8e023a33c2320c42a9be3cd0fc98110f3b7fae690871fff58bc9db51e22687d4`, pinned at assembly 0.1.3). Native rows carry no provenance, so the matrix version bump cannot touch a digest. Any drift is a deviation. |
| Comparators | baseline v2 `training/eval/reports/260902_p26_rescore_baseline.json` (45/228 = 0.197); A `260902_p26_rescore_A.json` (145/228 = 0.636, tripwire 1); A2 `260902_p26b_A.json` (153/228 = 0.671, recall 0.920, precision 0.853, tripwire 3); **control: arm A3** `260903_p26c_A3.json` (153/228 = 0.671 [0.608, 0.729], recall 0.898, precision 0.878, tripwire 3; checkpoint sha256 `f8d247d1…`, bathos run `1387da1c-3b4c-4204-be9c-c23b7044ec69`). All under the fixed scorer (amendment 8fe1b111). |
| Recipe | `RECIPE_VERSION 0.1.0` UNCHANGED (lr 1e-5 cosine, warmup 0.1, bf16, bs 4 × accum 4, 8 epochs, completion-only loss). Arm A = raw mix, seed 0. Optimizer steps rise with ~96 more train rows (≈ 1.09×); recorded as a confound, not tuned. |
| Base model, scorer, promotion rule, D8 anchors | UNCHANGED; revision UNSPENT. |
| Floor corpus, existing 685 rows | UNCHANGED: the 625 accepted-row digests (`floor_0.2.0_accepted_digests.json`) still asserted; the 60 repaired rows keep their record ids. The corpus GROWS by the new cells' rows, appended after ordinal 685. |
| Base prompt (`p23_nlify_v1`) | UNCHANGED text; the new cells produce new `input_hash`es, so the 736 cached entries stay hits and generation touches only the new cells. |
| Natural corpus (677 rows, assembly 0.1.5 input) | UNCHANGED, not regenerated: the new cells get NO natural variants in this sprint (one variable). Its manifest keeps `matrix_version: "2"`, which is true of the matrix its base rows came from. |
| Golden rows | UNCHANGED (the id-grammar jury item stays open; see the brief). |
| Matrix | **v3**: six near-surface out-of-surface cells APPENDED (§1.1). New cell field `appended_in_matrix_version` ("3"); `cells_round_robin` iterates the original cells in their existing order first and the appended cells after, so every existing ordinal (record id) is unchanged -- asserted by a test over the committed corpus. `verb: null` for all six (there is no schema verb for these actions); `surface_status: near-surface-unsupported-action`. `MATRIX_VERSION` 2 → 3. |
| Assembly | 0.1.6: pinned eval unchanged; the new rows are `coverage` rows outside the pin → train, EXCEPT indices 16-19 of each new cell (24 rows, the same k = floor(0.2·20) = 4 hold-out the pre-freeze rule used), which form a separate **near-surface probe** (`corpus_p25_probe_near{,_sidecar}.jsonl`), never train, never the 228. `cross_split_duplicate_utterances` must stay ≤ 41. |
| Teacher | Gemini 3.7 Flash medium via `agy` (same as the 0.2.0 floor). |

### 1.1 The six cells (frozen data; seeds are the exact `off_surface_request` strings)

| cell_id | off_surface_request |
|---|---|
| `tip_inventory__out-of-surface` | user asks how many tips are left in a tip rack, whether a rack still has tips, or to check the tip inventory (a question about stock, not a request to pick up or drop tips) |
| `consumables_ordering__out-of-surface` | user asks to order, reorder or buy more tips, plates or reagents from a supplier or vendor website (procurement, not a deck operation) |
| `deck_display__out-of-surface` | user asks to show, display, describe or list the current deck layout, or where a particular plate or tip rack sits on the deck (a view request, not a move) |
| `sample_value_query__out-of-surface` | user asks what the concentration, absorbance, or remaining volume of a specific sample or well is right now (a question about a value, not a request to run a plate read or to aspirate) |
| `scheduling_logging__out-of-surface` | user asks to schedule a run for later, set a reminder, or log a note about a plate or a sample in the lab notebook |
| `run_status__out-of-surface` | user asks how the current run is going, how many steps or how much time remain, or whether the last step finished (a status question, not an instruction) |

Each cell: `examples_per_cell 20`, supervision `nl_clarification` with the teacher-written
refusal + nearest supported alternative (the unchanged out-of-surface instruction of the base
prompt, which lists the supported tools). Expected: 120 rows, acceptance ≥ 90 % (the 0.2.0
out-of-surface cells accepted 160/160).

## 2. Hypothesis

The three A2/A3 tripwire rows name a surface object inside an unsupported request
("concentration of sample 4" → `read_sample`, "show me the deck layout" → `move_plate`,
"order more tips from the vendor website" → `pick_up_tips`). Every training abstention so far
is topically FAR from the surface (mix / blow out / heater-shaker / off-domain), so the model
has never seen "surface noun + unsupported action ⇒ abstain". Cells of exactly that shape
teach it, and because the supervision is the same clarification turn as the existing cells,
the surface mapping learned in P2.6b/c is not disturbed.

## 3. Pre-registered predictions (frozen 228 split, fixed scorer, A4 vs A3 = control)

**P1 (primary).** Tripwire on the 228 **≤ 1** (A3: 3) AND `tripwire3_recovered ≥ 2/3`
(`golden-out-surface-05`, `-10`, `-11`; `p26c_predictions.TRIPWIRE3`, unchanged).

**P2 (no regression vs A3).** Exact ≥ 0.671 (≥ control), clarify recall ≥ 0.705, hit→miss
flips ≤ 5 (every flip listed by id and class).

**P3 (surface gains retained).** `surface6_retained ≥ 4/6`; `verb22_retained ≥ 11/22`;
in-surface natural probe (90 rows) ≥ 0.80 (A3 0.811).

**P4 (near-surface probe, secondary, non-gating).** On the 24 held-out near-surface rows,
scored by the baseline_eval CLI in the same job, A4 abstention exact-match − A3 ≥ +0.10 --
UNLESS the local CPU pre-check (§5.1, run BEFORE submission, lesson 485) shows A3 already at
≥ 0.90 there, in which case P4 is void and recorded as such. The P2.6c natural oos probe is
reported as exploratory only (it was non-discriminative: all checkpoints at ceiling).

**P5 (exploratory).** `ambig4_recovered` (policy item, expected 0-1/4); golden miss count
(A3: 63); `oos44` exact.

**Ceiling and verdict.** Unchanged: 0.732 < T_acc 0.80. **Expected: NOT PROMOTED**;
`promotion.py` decides mechanically with A, A2, A3, A4 against baseline v2.

**Confounds recorded:** ≈ 1.09× optimizer steps at the fixed recipe; single seed, unpaired
shuffle; same teacher; the six cells were written by the orchestrating agent from the three
tripwire rows' SHAPE (surface noun + unsupported action), not from their text -- none of the
three utterances is a seed, and the filter rejects any generated utterance duplicating an eval
row.

## 4. Deviations

Any of: a pinned eval row missing or content-changed; any of the 625 accepted floor rows
changed; any existing record id re-numbered; a base-prompt text edit; a recipe change; more
than one training run; A4 scored on anything but the pinned split with the fixed scorer; a
seventh cell or an edited seed after this commit (a second cell set is a new pre-registration).
A prediction failing is NOT a deviation -- it is the result, reported as such. Cell acceptance
below 70 % on the first cell allows tightening ONLY that cell's seed text before the rest,
because no scored artefact depends on it; the change is recorded here.

## 5. Storage

Floor corpus + manifest + ~120 cache files; assembly 0.1.6 outputs incl. the near probe; train
manifest `training/out/p26d/A/train_manifest.json`; reports `training/eval/reports/260903_p26d_A4.json`,
`260903_p26d_probe_A4.json`, `260903_p26d_near_{A3,A4}.json` with generation dumps under
`training/eval/outputs/`; checkpoint uncommitted at `outputs/p26d/A/checkpoint` (sha256 in the
manifest). bathos run tagged `arm:A4`, reproduces `1387da1c-3b4c-4204-be9c-c23b7044ec69`.
