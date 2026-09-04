---
title: 'plr-sema sprint 123 plan: the volume family (increment 5) plus two carried rows'
description: 'Sprint plan for 260903_sema-volume: Band A adversarial round on increment 5 (spec_version 13) -> reviewed-round-1; Band B the derivation proof T24/T25 as the go/no-go gate (user decision 260903: build the volume family if it is firable); Band C T26-T29 domain, env gate, registry HM-24 1->2 / HM-25 6->8, mutants v1/v2, tier-2b volume fixtures, lint; Band D the carried #4881a landmine test and #4952 build_setup limits. Baselines to hold, exclusions (#4923/#4924 NO-GO, #4956), dispatch conventions.'
status: active
task_id: 260903_sema-volume
date: '260903'
sprint: '123'
backlog_ids: '4962,4958,4959,4960,4963,4952,4881'
---
# plr-sema sprint 123 plan: the volume family (increment 5) plus two carried rows


> Task id `260903_sema-volume`. Spine: `.praxia/docs/specs/260903_plr-sema-volume-increment.md`
> (increment 5, spec_version 13, status `draft`). Governing decision (user, 260903): **build the volume
> family if it is firable at all** — "the corpus is a set of examples, not the sum of what is valid and
> useful". Fail-closed on unrecognised conjuncts stays (soundness); the "no `WILL_FAIL` on real corpus
> rows at this pin" consequence is a precision note, not a blocker. Planned at HEAD `fe9f4f61` on
> `coxswain-p2-pipeline` (sprints 121 `260903_sema-real-programs` and 122 `260903_sema-followups` closed).

## 1. Composition

| Band | Item | Rows | What | Model | Depends on |
|---|---|---|---|---|---|
| A — spec | **#4962** | — | Adversarial round 1 on increment 5 (it has had none), then remediation to `reviewed-round-1`. Dispose Q2 (HM-25 count 8 vs 10), Q3 (derive-side vs survey-side caller scope), Q5 (v2 threshold). Fix the stale "draft-deferred / NOT SCHEDULED" wording that now contradicts §14.13. | Opus (challenger, defender, author) | — |
| B — gate | **#4958** | T24, T25 | The bridge derivation (B1 for-loop-over-comprehension-output; B2 class-level `AnnAssign`; P1c constructor-call typing) and caller-scope threading (P10), every selection **measured and published**. AC-14.1–14.4. **Go/no-go for the family lives here.** | Sonnet | #4962 |
| C — machinery | **#4959** | T26, T27 | `check/volumestate.py` V0–V4 with V2 threaded pair-by-pair; six fixtures; `env` gate with default = unasserted; registry HM-24 1→2, HM-25 6→8, `REASON_VOCABULARY` 8→10, row-count cap unchanged 24/24. AC-14.5–14.8. | Sonnet | #4958 |
| C — oracle | **#4960** | T28, T29 | `eval/volume_mutants.py` v1/v2; four tier-2b executed volume fixtures incl. two-channel/one-well and collective exhaustion; sidecar fields; `SPEC_INCREMENT_5` in the lint; INDEX regenerated. AC-14.9–14.11. | Sonnet / Haiku (T29) | #4959 |
| D — carried | **#4963** | #4881a | Increment 4's `null`-condition landmine regression test + lid gap-ledger block. Verified 260903 it never landed (no fixture, no assertion, absent from §13.14). Independent. | Sonnet | — |
| D — carried | **#4952** | — | `training/verify/deck.py` `build_setup` limits: one TipRack per tip-typed base, free-rail iterator for Troughs, skip auto trash when declared. Closes the 12 residual tier-1 `rows_setup_error`. Coxswain-side file; #4950 touched it in sprint 122 without collision. | Sonnet | — |
| umbrella | **#4881** | — | Tier-3 container. Closes when #4960 lands or when the gate says no-go and the reason is published. | — | — |

Order of execution: A → B → C serially (each band is the next one's premise); D runs in parallel with A
from the first dispatch, in worktrees, because neither D item touches a file the spine writes.

## 2. The go/no-go gate (band B)

The user's condition is *firable*, not *fires on the corpus*. After T24 and T25 have published their
four measured sets and `aspirate`'s `caller_scope`:

- **GO** if the extended bridge binds `remove_liquid`/`add_liquid` guards for at least one real PLR
  method at the pin (`liquid_handler.py:1031-1035` is the expected site) so that a harness fixture can
  drive the `WILL_FAIL` path under the asserted `env`. Proceed to #4959.
- **NO-GO** if, with B1/B2/P1c all landed, the bridge still cannot bind on the pin. Stop the family,
  publish the measured sets and the structural reason in the spec's implementation record, close #4881
  with that finding, do **not** start T26. The decision comes back to the user with the evidence.

Either way the T24/T25 code stays: the three sub-boxes widen P1a/P8 honestly and are useful to every
later family.

## 3. Decision hooks that stop for the user

1. **Q2 re-count.** If round 1 counts B2/P1c/B1/P10 as four HM-25 patterns (ceiling 10, not 8), stop
   before T27. A row split vs a ceiling bump is the user's ratchet call (§9.4 anti-gaming clause).
2. **NO-GO at band B** (above).
3. **Q5 threshold.** If the round holds that an ungated v2 class must not ship, T28 lands v1 only and
   v2 is measured and reported without a gate; the user decides whether a gate is set afterwards.

## 4. Baselines that must hold at close

| Tier | Baseline (sprint 122 close) | Where |
|---|---|---|
| 1 sidecar-gated replay | 331 executed / 528 ops, `rows_setup_error` 12, crosscheck 191/191 agreement 1.0, 0 unsound | `outputs/plr-sema/oracle_replay_260903_4950.json` |
| 2a bytecode differential | 330/330 agreeing, extractor divergences 0 | `outputs/plr-sema/tier2a_*.json` |
| 2b executed regions | 4 findings, 0 unsound, join by `(method, line_number)` | `outputs/plr-sema/tier2b_260903.json` |
| 3 tip mutants | m1 193/193, m2 254/254, 0 unsound | `outputs/plr-sema/tip_mutants_*.json` |
| registry | rows 24/24 (cap 24), HM-25 declared 6/6, HM-24 1, `REASON_VOCABULARY` 8/12 | `test_hand_maintained_ratchet.py` |

Tier-1 replay is always run with `--sidecar training/assemble/out/corpus_p25_sidecar.jsonl
--crosscheck training/out/corpus_p23_floor.jsonl --crosscheck training/overlay_gen/out/overlay_full.jsonl`.
#4952 is the one item allowed to move tier 1 (`rows_setup_error` 12 → published residual, executed
rows up, crosscheck unchanged).

## 5. Explicitly out

- **#4923** incremental re-check and **#4924** recovery interpreter — NO-GO criteria in increment 4
  §13.12 stand (workload unmeasured; over-fill verdict undecidable until `max_volume` reaches the wire).
  Increment 5 puts `max_volume` on the wire, so #4924's criterion may reopen *after* this sprint.
- **#4956** P2.6e label-conflict audit — Coxswain track, needs its own prereg, user's call.
- REPL refocus P0–P7 and Coxswain W0–W6 — other track.
- Any new registry row. Increment 5 spends per-row ceilings only.

## 6. Dispatch conventions (unchanged from sprints 121/122)

- Fixer briefs mandate: `uv run python` never bare python; per-file pytest only (the jax-mem-guard
  blocks any path ending in `/tests`); path-scoped `git add`; **no background Bash, no monitors**;
  foreground with timeout; final line `COMMIT: <full sha>`; trailers `Co-Authored-By: Claude Fable 5.1
  <noreply@anthropic.com>` + `Claude-Session: https://claude.ai/code/session_01QgK1DBdBsTFJou6ML91sNT`.
- Run the **full** per-file set before closing a band: `test_derive`, `test_check_graph`,
  `test_wire_fuzz`, `test_verdict` (the §3.3 reason scan — no fixer gate ran it in sprint 122),
  `test_hand_maintained_ratchet`, `test_cache`, `test_oracle_replay`, `test_spec_lint`.
- Challenger/defender agents have no write tool; the orchestrator persists their reports under
  `.praxia/docs/audits/260903_plr-sema-volume-round1-{challenger,defender}.md`.
- Never touch the other session's dirty entries in the tree; `git push` needs the sandbox off.
- Spec citations drift when code lands: re-anchor pass (`check_spec_citations.py`) before close.

## 7. Estimate

Spec rows: T24 ~420, T25 ~230, T26 ~360, T27 ~200, T28 ~430, T29 ~15, #4881a ~120; #4952 ~150.
Sprint 122 delivered a comparable set (5 rows + a spec round) in one day; band B's measurement
discipline and the round make this one closer to a day and a half.
