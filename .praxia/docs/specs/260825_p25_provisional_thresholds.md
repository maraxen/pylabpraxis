---
title: 'Coxswain P2.5 provisional promotion thresholds (T_acc / T_clr_recall / T_clr_prec)'
description: 'Numeric anchor proposal for the P2.6 three-number promotion gate (D8), derived from the P2.1 recorded-artifact baseline spread and the assembled P2.5 eval slice sizes. PROVISIONAL PER D8: exactly ONE revision permitted at P2.6 fine-tune eval, with recorded justification.'
task_id: 260825_copilot_pipeline_spec
date: '260825'
status: provisional-per-D8
backlog_item: 480
---

# Provisional thresholds for the P2.6 promotion gate

Spec: `.praxia/docs/specs/260825_coxswain-phase-2-functiongemma-copilot-p.md`
rev2 D8 / §5 P2.5 deliverable 5 / §7 AC-2.5.x ("thresholds labeled
provisional"). These are ANCHORS for the blocking jury, not final gates:
**P2.6 may revise each number at most once, with recorded justification**
(D8 rev2). All reported values at P2.6 must carry Wilson 95% intervals beside
point estimates (AC-2.6.x).

## 1. Proposed anchors

| Metric | Provisional anchor | Baseline point (P2.1 recorded-artifact proof) | Baseline Wilson 95% |
|---|---|---|---|
| `T_acc` (exact-match accuracy) | **>= 0.80** | 0.75 (6/8) | [0.409, 0.929] |
| `T_clr_recall` | **>= 0.70** | 0.50 (2/4) | [0.150, 0.850] |
| `T_clr_prec`   | **>= 0.90** | 1.00 (2/2) | [0.342, 1.000] |

## 2. Where each number comes from

Baseline evidence is `training/eval/reports/260825_recorded_fixture_report.json`
-- RECORDED ARTIFACTS, NOT live inference, PARTIAL coverage (8 scored of 62
in-scope; real model lane blocked on Gemma license acceptance + `HF_TOKEN`,
see training README). With n that small the intervals are wide, so anchors are
set by POLICY margins over the baseline points, not by interval arithmetic:

- **T_acc = 0.80**: baseline point 0.75 already sits near it; a 270M model
  fine-tuned on this surface must CLEAR the off-the-shelf point estimate,
  not tie it. 0.80 is the smallest round anchor strictly above 0.75 that a
  correct-ish model cannot miss by transcription noise alone.
- **T_clr_recall = 0.70**: baseline 0.50 misses half of clarify-expected
  items. Cue-1 (out-of-surface abstention + derived missing-slot surfacing)
  is the safety behavior F1 protects; the gate must force real movement
  above coin-flip. 0.70 leaves headroom below Mobile-Actions-style targets
  while being falsifiable on the current slice.
- **T_clr_prec = 0.90**: baseline 1.00 (n=2). Over-triggering clarification
  destroys usable parses (every false positive is a blocked action); the
  asymmetric cost justifies anchoring precision higher than recall.

## 3. Slice sizes these anchors will be measured on (assembled P2.5 eval)

From `training/assemble/out/manifest.json` (assembly_version 0.1.0):

| Eval slice | n |
|---|---|
| clean_parse | 66 |
| out_of_surface | 12 |
| missing_slot | 12 |
| ambiguous_referent | 12 |
| total eval clarify (3 classes) | 36 (>= D8's 30 floor) |

Recorded scope caveat (P2.1 decision, unchanged): the STATIC harness scores
clarify over out-of-surface + missing-slot ONLY (24 items); ambiguous-referent
detection needs live kernel grounding (cue 2, F1-rev2/C-M1) and verifies at
P2.9 integration. The three-class >=30 sizing is satisfied by the corpus;
the statically-scoreable subset is 24 -- flagged in the slice-gate doc.

## 4. Revision rule (D8)

At most ONE revision of any anchor at P2.6, requiring: observed eval slice
sizes, Wilson intervals beside every point estimate, and a written reason.
Suggested legitimate reasons: full-scale corpus regeneration materially grew
a slice; live-model baseline (post-token) lands far outside the recorded
mechanics-proof spread. Vague "model feels better" is not a reason.
