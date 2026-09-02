---
title: 'plr-preflight oracle harness: assessing the analyzer in simulated use'
description: 'Design for catching plr-preflight bugs by comparing static verdicts against PLR''s chatterbox simulator (STRICT + tip/volume tracking) as ground-truth oracle: four input tiers (corpus replay, source-rendered corpus, mutation/metamorphic, wire-format fuzz), the soundness contract each verdict must satisfy, metrics, and phasing.'
status: draft
task_id: 260902_preflight-checkers-rename
date: '260902'
sprint: ''
backlog_ids: '4879, 4880, 4881, 4882'
---
# plr-preflight oracle harness: assessing the analyzer in simulated use

## The question

`plr-preflight` is a sound static analyzer: for every operation in a protocol's
execution graph it returns `SAFE` / `WILL_FAIL` / `UNKNOWN`. Its tests check
that the *machinery* behaves (contracts derive, findings are total, the join is
right). None of them check that a verdict is *true* — that a protocol the
analyzer calls `SAFE` really runs, or one it calls `WILL_FAIL` really raises.
That is the class of bug a static analyzer ships silently, and it needs an
independent second reading of the same protocol to catch.

PyLabRobot supplies that second reading for free. `LiquidHandler` on the
`LiquidHandlerChatterboxBackend` with `set_tip_tracking(True)` and
`set_volume_tracking(True)` enforces the very preconditions the analyzer
targets, at runtime, with no hardware:

| PLR raises | where | when |
|---|---|---|
| `NoTipError` | `tip_tracker.py:65,105` | aspirate/dispense/drop with no tip mounted |
| `HasTipError` | `tip_tracker.py:92`, `liquid_handler.py:535` | pick up onto a channel that has a tip |
| `TooLittleLiquidError` | `volume_tracker.py:92` | aspirate more than the well holds |
| `TooLittleVolumeError` | `volume_tracker.py:105` | dispense over capacity |
| `BlowOutVolumeError` | `liquid_handler.py:1185-1188` | dispense volume exceeds the tip |
| `ValueError` | `liquid_handler.py:116,990` | lidded resource; volume-list shape mismatch |

(Line numbers at submodule pin `dd79c4c89`.) `training/verify/verifier.py`
already wires all of this: `verify(call_sequence, intent_record)` builds a
chatterbox deck, sets STRICT + both trackers, plans each call through
`dispatcher.plan_call`, awaits it, and absorbs any exception into one
`error: "ExcClass: message"` string. The corpus that P2.5/P2.6 executed through
it — 812 rows in `training/assemble/out/corpus_p25.jsonl` plus 88 golden pairs
— is in **tool-call form** (`[{name, params}]`), not Python source.

So the oracle exists in fragments. What is missing is the glue that produces the
static reading of the same protocol and lines the two up per operation.

## Feasibility: the spike (260902)

`plr-preflight/scripts/oracle_spike.py` closes the loop for the four verifier
examples in `training/examples/`:

1. **runtime** — `verify()` with `plan_call` wrapped to record which operation
   index was being planned when the run raised (the verifier itself only keeps
   the string).
2. **static** — the same call sequence adapted straight into the §6.2 graph
   wire format (one `OperationNode` per call on receiver `lh: LiquidHandler`,
   one `ResourceNode` per deck-layout resource), then `check_graph` against the
   shipped `derived_contracts.json`; per-operation verdict = `join` of that
   operation's findings.
3. **compare** — per operation: `ran_ok` / `raised:<Class>` / `not_reached`
   against the static verdict.

Result: 4 examples, 10 operations, every operation aligned, 0 unsound. A
hand-made mutant (`clean_transfer` with `pick_up_tips` removed) produced
`raised:NoTipError` at op_0 and `not_reached` at op_1 — the oracle sees
precondition failures at the right step. Every static verdict was `UNKNOWN`
with 9–17 findings per operation, exactly as v1 specifies (§0: no `SAFE`
constructed anywhere, `join(∅) = UNKNOWN`).

Two facts the spike surfaced that shape the design:

- **Ground truth has two kinds.** `wrong_slot_known_failure.json` runs *clean*
  on the simulator; its failure is an intent-agreement check
  (`checks.py:_check_slot_agreement`), i.e. a postcondition against the user's
  stated intent, not a PLR precondition. The harness must record PLR exceptions
  and verifier check failures as separate columns — only the first is a claim
  the static analyzer makes.
- **The failing index needs the wrapper.** `verify()`'s return carries
  `bindings` from executed calls but not a count; wrapping `plan_call` is the
  cheapest faithful source and should become a supported return field
  (`executed_count`) rather than a monkeypatch when tier 1 lands.

## The soundness contract being checked

Per operation `i`, with `s_i` the static verdict and `r_i` the runtime outcome:

| `s_i` | `r_i` | reading |
|---|---|---|
| `SAFE` | `raised:*` | **unsound** — a bug of the first severity; `SAFE` must never be wrong |
| `WILL_FAIL` | `ran_ok` | **unsound** — a definite-failure claim the semantics contradict |
| `WILL_FAIL` | `raised:C` | agreement; additionally check `C ∈ contract.raises` for that guard |
| `SAFE` | `ran_ok` | agreement |
| `UNKNOWN` | anything | no constraint — counted as the precision cost |
| any | `not_reached` | no constraint (an earlier operation raised) |

Zero unsound rows is a hard gate. The `UNKNOWN` rate per method family is the
number that should fall as deferred items (a) abstract domain and (c) predicate
evaluator land; it is 100% today by construction.

## Four input tiers

**Tier 1 — corpus replay (#4879, first).** The spike generalised to the 812 +
88 rows, bathos-tracked. Outputs: the agreement matrix above; `UNKNOWN` rate by
method family; and — the actionable one — the ranked list of exception classes
the simulator actually raised across the corpus. That list says which contract
guards are worth making decidable first: there is no point evaluating a guard
family the corpus never trips. Also checks totality on real inputs
(`len(findings) >= len(operations)` for every row, AC-7.2) and that
`check_graph` never raises.

**Tier 2 — through the extractor (#4880).** Tier 1 bypasses libcst. Tier 2
renders each call sequence to a minimal Python protocol
(`await lh.transfer(source["A1"], dest["B1"], 50)` with resources as
parameters), runs praxis's `computation_graph_extractor` out of process, and
feeds *that* graph to `check_graph`. Tier-1 and tier-2 verdicts for the same
row must agree; any divergence is an extractor defect by construction — the
flow-sensitive tips gate at `computation_graph_extractor.py:547`, receiver
typing, argument capture.

**Tier 3 — mutation / metamorphic (#4881).** Every clean corpus row spawns
mutants PLR is known to reject: remove `pick_up_tips` → `NoTipError`; duplicate
it → `HasTipError`; aspirate above seed volume → `TooLittleLiquidError`;
dispense over capacity → `TooLittleVolumeError`; lid a plate before access →
`ValueError`. Metamorphic relation: the simulator's rejection at op `i` forbids
`SAFE` at `i`; its acceptance forbids `WILL_FAIL`. Each mutation class also
names the guard family the analyzer must eventually decide, so the report
tracks per class how many mutants flip from `UNKNOWN` to `WILL_FAIL` over time.

**Tier 4 — wire-format fuzz (#4882).** `hypothesis` over random §6.2 payloads
and contract tables into `check_graph`: never raises; totality holds; never
`SAFE` without an evaluated guard; `Verdict.from_wire` widens every unknown
string to `UNKNOWN`; `join` is order-independent and idempotent. Fast, no PLR
import, runs in the normal suite.

## Where it lives

Not under `src/plr_preflight/` — the harness imports `pylabrobot` and
`training.verify`, and `tests/test_import_boundary.py` exists precisely to keep
those out of the analyzer. `plr-preflight/eval/` (tiers 1–3, bathos sidecar per
run, `uv run --package plr-preflight`) and `plr-preflight/tests/test_wire_fuzz.py`
(tier 4). The spike stays in `scripts/` as the worked example.

## What this does not measure

- Precision. Until an emitter constructs `SAFE` or `WILL_FAIL`, there are no
  positives to be false; the harness is armed, not firing.
- Anything the chatterbox backend does not enforce — physical collisions,
  timing, backend-specific limits. Those are hardware truths, not simulator
  truths, and out of v1 scope with error recovery and optimization.
- Non-legacy PLR. The verifier runs at the pinned submodule (`dd79c4c89`);
  the `upstream_nonlegacy` surface has contracts (T14) but no executable
  oracle here until praxis migrates off the pin.
