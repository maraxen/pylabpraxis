---
title: "plr-sema increment 5 — the volume family: an interval domain, deferred out of increment 4 until its derivation is proved"
description: "Fifth post-corpus increment to the plr-sema pre-corpus specification, created by re-scoping section 13.2 out of 260903_plr-sema-families-cache-increment.md after adversarial round 1. Deferred, not dropped: the domain, the transfer functions, the capacity asymmetry, the seeding convention and the oracle plan all survive round 1 intact; what did not survive is the claim that the bridge DERIVES on real PLR at the pin. O1 established three independent structural gaps -- `op` in `op.resource.tracker.remove_liquid` is a for-loop variable over the comprehension's OUTPUT list (`liquid_handler.py:1031`), not a zip-bound comprehension target; `SingleChannelAspiration.resource` is a dataclass class-level bare-name annotation (`external/pylabrobot/pylabrobot/liquid_handling/standard.py:51-60`) that `_annotated_attributes`'s `_is_self_attr` predicate structurally excludes; and `Container.tracker` is an unannotated `ast.Assign` (`container.py:85`) that P1a cannot see at all. O2 established a fourth: `compute_channel_bridge` sources a bridged guard's `scope_trail` from the CALLEE's own contract (`receiver_state.py:977-1041`), and the survey's `dropped_calls` is a bare string list with no line number and no scope (`plr_preconditions.json:49766-49772`), so `does_volume_tracking()` never reaches the bridged guard and a default-`env` run would emit an unsound `WILL_FAIL`. Section 14.0 states all four as this increment's first two tasks, each with its own normative box and its own measured-and-published expectation, before any `Finding` machinery. Also folds O4 (V2 threads pairs sequentially in `cells(op)`/`amounts(op)` order, mirroring PLR's own `for op in aspirations` -- a simultaneous reading gives a false SAFE for two channels drawing one well) and O3 (fail-closed on any unrecognised boolean conjunct, since `is_disabled` is a @property and not a zero-argument call). Carries HM-24 1->2, HM-25 6->8 and REASON_VOCABULARY 8->10 -- none of which increment 4 spends. NOT SCHEDULED: the task rows below are unscheduled by construction and no AC here gates any increment-4 work."
status: draft
spec_version: 13
amends: 260901_plr-sema-pre-corpus-spec.md
task_id: 260903_sema-followups
date: '260903'
confidence: medium
sources: "Created by re-scoping section 13.2 of .praxia/docs/specs/260903_plr-sema-families-cache-increment.md (spec_version 12 draft, b89de024) after adversarial round 1. Round-1 reports read in full: .praxia/docs/audits/260903_plr-sema-families-cache-round1-challenger.md (O1-O6) and .praxia/docs/audits/260903_plr-sema-families-cache-round1-defender.md (all six CONCEDED; ordered remediation list items 1-3 are this document). Specs: .praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md sections 10.1-10.5, 10.9; .praxia/docs/specs/260902_plr-sema-ir-bytecode-increment.md sections 11.1.2-11.1.4, 11.3; .praxia/docs/specs/260903_plr-sema-real-programs-increment.md sections 12.1.2-12.1.6, 12.3.3, 12.13; .praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md sections 0, 0.1, Open decisions 2, 9.1-9.4, Deferred. Analyzer source re-verified this pass: plr-sema/src/plr_sema/derive/receiver_state.py:160-190,523-563,770-799; plr-sema/src/plr_sema/derive/__init__.py:840-959; plr-sema/src/plr_sema/check/ir.py:50-95,178-192,900-926; plr-sema/src/plr_sema/check/__init__.py:443-457,686-700,713-727; plr-sema/src/plr_sema/verdict.py:100-179; plr-sema/src/plr_sema/_hand_maintained.py:1-80,240-263,553-557,781-847,851-871. Harness: plr-sema/eval/oracle_common.py:690-739,976-1006; plr-sema/eval/tip_mutants.py:63-70,86-224,227-251. PLR at submodule pin dd79c4c89: liquid_handling/liquid_handler.py:960-1069,1170-1199; liquid_handling/standard.py:40-67; resources/volume_tracker.py (in full, 171 lines); resources/container.py:22-88; resources/tip.py:16-80. Artifacts: plr-sema/data/derived_contracts.json:157962-158133; training/verify/data/plr_exception_taxonomy.json:2964-2972,2991-2999,3010-3056; training/verify/data/plr_preconditions.json:49764-49773,49863-49864. Data: outputs/plr-sema/oracle_replay_260903_rebaseline.json:2-29; outputs/plr-sema/tier2b_260903.json:1-45."
---

# Increment 5: the volume family

> **This document amends `260901_plr-sema-pre-corpus-spec.md` by reference** and adds §14 to that
> document's numbering. **It is `draft-deferred`: nothing in it is scheduled.** It was created by
> moving §13.2 out of `260903_plr-sema-families-cache-increment.md` (spec_version 12) after that
> document's adversarial round 1, on the defender's recommendation and the user's decision (260903).
> Increment 4 ships the cache (#4922), the derived inert filter (#4883) and the delegate-call channel
> binding (#4946), and keeps a one-paragraph §13.2 stub pointing here.
>
> **The registry arithmetic increment 4 does *not* spend, and this increment carries:** HM-24
> `declared` 1 → 2, HM-25 `declared` 6 → 8, and `REASON_VOCABULARY` 8 → 10 of cap 12. Increment 4
> spends only HM-25 5 → 6, for P9 alone. The row-count cap is untouched at 24 live against
> `BUDGET_CAP = 24` (`plr-sema/src/plr_sema/_hand_maintained.py:43`) in both documents.

---

## 14.0 Why this is deferred, and what must be proved first

§13.2 claimed the volume family was *the* derivable one — the counterpart to the lid family, which
§13.1 declined on four structural blockers. Round 1 verified that claim and falsified it in a
specific, bounded way that is worth stating precisely, because **almost all of the section survives.**

**What survived, unchallenged in either report:** the interval domain and its lattice (§14.3), the
capacity asymmetry that makes the over-fill half undecidable (§14.2), the two-conjunct taxonomy
selector that picks `{TooLittleLiquidError, TooLittleVolumeError}` out of four `volume_state` members
(§14.1), the seeding convention that reuses §12.1.6's scaffolding-`CALL` precedent (§14.8), the
assumption table (§14.7), and the oracle plan (§14.9). The challenger checked the guard shapes, the
taxonomy categories and the `dropped_calls` entries against source and confirmed all of them.

**What did not survive is one sentence: that the bridge derives.** §13.2.1 offered four facts as
evidence, and fact 3 — *"the bridge expressions are already recorded"* — is true of the *survey* and
false of the *matcher*. `dropped_calls` does record `op.resource.tracker.remove_liquid`
(`training/verify/data/plr_preconditions.json:49768`), and §13.2.4's normative box cannot match it.
Four independent gaps, each verified against the pin by both reports:

| id | gap | evidence | precedent in `derive/` |
|---|---|---|---|
| **G1** | `<name>` must be "a comprehension target of a P8 match". `op` is not one: P8's zip-bound names are `r, v, o, fr, lh, t, bav, m` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1018-1031`), and `op` is the loop variable of a **separate** statement, `for op in aspirations:` (`:1031`), iterating the comprehension's *output list* assigned at `:1007` | `liquid_handler.py:1007-1031` | none |
| **G2** | `<attr>`'s type must come from a P1a map. `SingleChannelAspiration` is a `@dataclass(frozen=True)` whose fields are **class-level bare-name annotations** — `resource: Container` at `external/pylabrobot/pylabrobot/liquid_handling/standard.py:53`, `tip: Tip` at `:55`, `volume: float` at `:56`. `_annotated_attributes` keeps only `ast.AnnAssign` nodes whose target passes `_is_self_attr` (`plr-sema/src/plr_sema/derive/receiver_state.py:177`, predicate at `:164-167`), and a dataclass field's target is `ast.Name("resource")`, which fails that predicate unconditionally | `external/pylabrobot/pylabrobot/liquid_handling/standard.py:51-60`, `receiver_state.py:164-181` | none |
| **G3** | Even granting G2, the *second* hop fails independently: `Container.__init__` writes `self.tracker = VolumeTracker(...)` as a plain `ast.Assign` (`external/pylabrobot/pylabrobot/resources/container.py:85`), and P1a walks `ast.AnnAssign` only | `container.py:85`, `receiver_state.py:177` | **yes** — `_constructor_state` (`receiver_state.py:523-563`) already walks both `ast.Assign` (`:548`) and `ast.AnnAssign` (`:551`) in a class's own `__init__` |
| **G4** | The `env` gate has nothing to gate. `compute_channel_bridge` sources a bridged guard's `scope_trail` from `derive_contract(...)` on the **callee** (`receiver_state.py:977-1041`, the copy at `:787`), and `VolumeTracker.remove_liquid`'s own record names only its own condition. The caller-side conjuncts `if does_volume_tracking():` and `if not …is_disabled:` (`liquid_handler.py:1032-1033`) live one syntactic level above the dropped call, and the survey's `dropped_calls` is a **bare string list** with no line number and no scope (`plr_preconditions.json:49766-49772`) | as cited | partial — the survey *does* carry `scope_trail` for a method's own findings, just never for a dropped call |

**G4 is a soundness gap, not a precision gap, and that is why the whole section moved rather than
being patched.** With the bridge fixed (G1–G3) and the threading absent, §14.6's rule finds no
`does_volume_tracking` anywhere in the bridged guard, never marks it conditional, and under the
**default** `env = frozenset()` emits `WILL_FAIL` for a program in which volume tracking may never
have been on and the guard body never ran. That is the first-severity error class — a definite
verdict constructed from a hypothesis nobody asserted — and it is exactly what §13.2.6 was written to
prevent. A document that shipped the bridge fix without the threading fix would have introduced the
bug the mechanism exists to prevent.

> **Normative (the gate on this increment).** No `Finding`-constructing machinery from §14.5 or §14.6
> may land until **T24 and T25 have both landed and published their measured selections**. This is
> not a scheduling preference; it is G4's soundness argument. A partial landing of T24 alone leaves
> the analyzer able to construct a definite volume verdict with no hypothesis gate, which is strictly
> worse than today's `guard_predicate_unparsed`.

### 14.0.1 Task (a) — the volume bridge, three normative sub-boxes

Each box below is stated at the same discipline §13.2.4 demanded of P7 and P8: **the expectation is
measured and published by the fixer, never assumed from this document.**

> **Normative (B1 — for-loop binding over a comprehension's output list).** Extend the `<name>`
> binding of the volume bridge. In addition to a P8 comprehension target, `<name>` may be the single
> target of an `ast.For` statement, at **depth 0** in `K`'s body (excluding nested function and lambda
> definitions), whose `iter` is a bare `ast.Name` that is the single `ast.Assign` target of a P8
> match's own comprehension **within the same method**. The bound element type is that P8 match's
> element class `O`.
>
> **Fail-closed.** If `K`'s body contains more than one such `ast.For` over the same name, or the
> `ast.For` target is a tuple rather than a single `ast.Name`, or the assignment of the comprehension
> to that name is not a single-target `ast.Assign`, B1 binds nothing and the bridge widens. Two loops
> over one list can disagree about which element field is read, and picking one is §10.5 rule 1's
> "two views of one fact" case.
>
> **Measured expectation, to be reproduced and published:** in `LiquidHandler.aspirate`, the P8 match
> assigns to `aspirations` (`liquid_handler.py:1007`) with element class `SingleChannelAspiration`
> (`:1008`), and the single depth-0 `ast.For` over it binds `op` (`:1031`) — so `op : SingleChannelAspiration`.
> The fixer publishes the complete set of `(K, name, element_class)` triples B1 binds over the whole
> contract table, not only `aspirate`'s.

> **Normative (B2 — P1a over dataclass field annotations).** `_annotated_attributes`
> (`plr-sema/src/plr_sema/derive/receiver_state.py:170-181`) additionally admits an `ast.AnnAssign`
> that is a **direct statement of the class body** (not inside any method) whose target is a bare
> `ast.Name`, recording `name → unwrapped annotation`. `_is_self_attr` (`:164-167`) is **not**
> changed — the new admission is a second, disjoint branch, so every existing P1a selection is
> bit-for-bit unaffected and no shipped `receiver_state` value moves.
>
> **This is a widening of P1a's population and must be measured as one.** The fixer publishes the
> count of classes and attributes P1a selects before and after, and asserts that the *pre-existing*
> selections — `LiquidHandler.head → TipTracker` above all — are unchanged. A widening that silently
> altered the tip family's anchor would be caught by AC-14.1(iii) and by nothing else.
>
> **Measured expectation:** `SingleChannelAspiration.resource → Container`, `.tip → Tip`,
> `.volume → float` (`external/pylabrobot/pylabrobot/liquid_handling/standard.py:53-56`), and the
> mirror for `SingleChannelDispense` (`:63-67`).

> **Normative (P1c — constructor-call typing through an unannotated write).** A new pass in
> `derive/receiver_state.py`, modelled directly on `_constructor_state`
> (`plr-sema/src/plr_sema/derive/receiver_state.py:523-563`), which already establishes the
> architecture: it locates a class's own `__init__` (`:540-545`) and walks both `ast.Assign` (`:548`)
> and `ast.AnnAssign` (`:551`) within it. P1c walks the same `__init__` and, for every
> `self.<name> = <Callee>(...)` whose value is an `ast.Call` with an `ast.Name` func that is a key of
> the P1 class index, records `name → <Callee>`.
>
> **Fail-closed.** A name written more than once in `__init__` with two different constructors, or
> written both by a constructor call and by something else, records nothing. P1c is consulted **only
> after** P1a: an annotated attribute always wins, so P1c can add knowledge and never overwrite it.
>
> **Measured expectation:** `Container.tracker → VolumeTracker`
> (`external/pylabrobot/pylabrobot/resources/container.py:85`) and `Tip.tracker → VolumeTracker`
> (`external/pylabrobot/pylabrobot/resources/tip.py:45`). The fixer publishes the complete P1c
> selection over the whole surface — this pass sees every unannotated constructor write in PLR, so
> its population is large and its *size* is the first thing a reviewer should be shown.

With B1, B2 and P1c, the two-hop resolution of `op.resource.tracker` is:
`op → SingleChannelAspiration` (B1) → `.resource → Container` (B2) → `.tracker → VolumeTracker` (P1c),
and `VolumeTracker` is P7-anchored (§14.4). **That chain is the thing T24 must demonstrate, and
demonstrating it is AC-14.2, not an argument in this document.**

### 14.0.2 Task (b) — caller-scope threading, and the choice between two places to put it

G4 needs the caller's enclosing conjuncts attached to a guard that arrives through `dropped_calls`.
There are exactly two places to do it, and the tradeoff is blast radius against reuse:

| option | what changes | cost | who else benefits |
|---|---|---|---|
| **survey-side** — `scripts/survey_plr_preconditions.py` records, per `dropped_calls` entry, its line number and enclosing scope trail | the survey artifact's schema; `plr_preconditions.json` is regenerated; `dropped_calls` stops being a `list[str]` | every consumer of the survey re-reads a changed shape; the artifact is an input to `plr_sema.derive` **and** to the differential harness; a schema change is a cross-package event | every future bridge, and the deferred-item-(e) worklist, which could then rank by scope |
| **derive-side** — a new pass in `derive/receiver_state.py` re-parses the caller's own AST, locates the call expression matching the `dropped_calls` string, and accumulates its enclosing `ast.If`/`ast.For`/`ast.While` tests | one new pass in one module; no artifact change; no schema change | the match is by *reconstructed expression text* rather than by position, so a method containing the same call expression twice under different scopes is ambiguous | only `plr_sema` |

> **Decision: derive-side.** `derive/receiver_state.py`'s P1–P4 are already "a stdlib-`ast` pass over
> every PLR class body", so the tree is already being walked and the pass adds a visitor, not a
> dependency. The survey-side option is *better* in the long run — position is a stronger key than
> text, and other consumers would benefit — but it changes an artifact that two packages read, and
> this increment is already carrying four unproved derivations. **The ambiguity the derive-side
> option introduces is handled fail-closed** (below), which is what makes the weaker key acceptable.
>
> **Normative (P10, caller-scope threading).** For a bridged guard attached to contract entry `K` via
> a `dropped_calls` expression `E`, P10 re-parses `K`'s own source, finds every `ast.Call` whose
> reconstructed dotted-callee text equals `E`, and for the **unique** such call records
> `caller_scope`: the ordered list of enclosing `ast.If` test sources and `ast.For`/`ast.While`
> headers between `K`'s body and that call, outermost first. The bridged guard's payload gains
> `caller_scope` as an additive key alongside its existing `scope_trail`, which is **not** modified —
> the callee's own trail and the caller's are different facts and are kept apart.
>
> **Fail-closed.** Zero matches, or two or more matches, records `caller_scope: null`, and §14.6's
> rule treats a `null` caller scope as **an unrecognised conjunct** — blocking `WILL_FAIL`. An
> ambiguous scope must not read as an absent one.
>
> **Measured expectation:** for `LiquidHandler.aspirate`'s `op.resource.tracker.remove_liquid`, exactly
> one match, with `caller_scope == ["if does_volume_tracking()", "for op in aspirations",
> "if not op.resource.tracker.is_disabled"]` or whatever the pass in fact produces — **the fixer
> publishes what it produces and does not reconcile it to this line**, which is written from
> `liquid_handler.py:1031-1035` by eye and is exactly the kind of expectation §13.2.4's own discipline
> exists to make measurable.

---

## 14.1 Why the volume family is the derivable one, and the correction to the original dispatch

The dispatch that produced §13.2 described the volume guards as testing `_used_volume`/`_pending_volume`
against `max_volume`. **The field names are wrong and the correction matters**, because the anchor
derivation keys on them: `VolumeTracker.__init__` writes `self.volume` and `self.pending_volume`
(`external/pylabrobot/pylabrobot/resources/volume_tracker.py:49-50`), and the guards read them only
through two accessor **methods** — `get_used_volume` returning `self.pending_volume` (`:114-116`) and
`get_free_volume` returning `self.max_volume - self.get_used_volume()` (`:118-120`). There is no
`_used_volume` anywhere in the module. The raises are at `:92` (`TooLittleLiquidError` inside
`remove_liquid`, `:88-99`), `:105` (`TooLittleVolumeError` inside `add_liquid`, `:101-112`) and `:136`
(`TooLittleLiquidError` inside the deprecated `get_liquids`, `:122-138`).

Four facts, all in shipped artifacts, and **round 1 verified all four**:

1. **The guards are clean, depth-0 and already derived.** `plr-sema/data/derived_contracts.json`
   carries `"VolumeTracker.remove_liquid"` (`:158102-158133`) with a single depth-0 `raise_guard`,
   `condition: "volume - self.get_used_volume() > 1e-06"`, `raises: "TooLittleLiquidError"`, sited at
   `volume_tracker.py:92`; and `"VolumeTracker.add_liquid"` (`:157965-157996`) with
   `condition: "volume - self.get_free_volume() > 1e-06"`, `raises: "TooLittleVolumeError"`, sited at
   `:105`. Both carry `free_vars: ["self", "volume"]` — the condition mentions the method's own
   parameter, which is exactly the value a `CALL`'s kwarg supplies.
2. **The exception selector is the tip selector, verbatim in shape.** Both classes carry
   `"category": "volume_state"` and `"module": "pylabrobot.resources.errors"`
   (`training/verify/data/plr_exception_taxonomy.json:3011-3019` and `:3038-3046`). The unfiltered
   `category == "volume_state"` set has **four** members; the module conjunct narrows it to **two**,
   excluding `BlowOutVolumeError` (module `pylabrobot.liquid_handling.liquid_handler`, `:2964-2972`)
   and `LiquidLevelError` (a Hamilton backend class, `:2991-2999`). That is the same 5 → 2 narrowing
   §10.2.5 performs for tip state, against the same module path, so **no new hand-typed string enters
   `plr_sema`** — the module literal is the one AC-10.9 already declares.
3. **The bridge expressions are recorded — by the survey, and not yet matchable by the matcher.**
   `training/verify/data/plr_preconditions.json`'s `dropped_calls` carries
   `"op.resource.tracker.remove_liquid"` and `"op.tip.tracker.add_liquid"` for aspirate
   (`:49766-49772`) and the mirror pair for dispense (`:49863-49864`). They survive the inert filter.
   **§13.2.1 stated this fact as if it discharged the derivation; it does not** — §14.0's G1–G3 are the
   distance between "the survey wrote the string down" and "a rule matches it", and that distance is
   why this increment exists.
4. **`BlowOutVolumeError` is genuinely out of scope and the module conjunct is what puts it there.**
   Its two raises (`liquid_handler.py:1185` and `:1188`, inside the `does_volume_tracking()` block at
   `:1182-1188`) guard `self._blow_out_air_volume` against a requested blow-out volume — a
   `LiquidHandler` instance field, not a tracker cell, and therefore a different domain.

---

## 14.2 The two cell kinds, and the capacity problem

A volume cell is **a `VolumeTracker` instance**, and there are two kinds in the verdict path:

- **container cells** — `Container.__init__` sets
  `self.tracker = VolumeTracker(thing=..., max_volume=self.max_volume)` with
  `self.max_volume = max_volume or (size_x * size_y * size_z)`
  (`external/pylabrobot/pylabrobot/resources/container.py:84-85`). Wells, troughs, tubes.
- **tip cells** — `Tip.__post_init__` sets
  `self.tracker = VolumeTracker(thing=thing, max_volume=self.maximal_volume)`
  (`external/pylabrobot/pylabrobot/resources/tip.py:45`), with `maximal_volume: float` declared at
  `:27`. An aspirate moves liquid out of a container cell **and into a tip cell** in the same
  statement pair (`liquid_handler.py:1034-1035`).

Both writes are the unannotated `ast.Assign` shape §14.0's P1c exists to read.

> **Normative (the capacity asymmetry).** `max_volume` is **⊤ for every cell**. For a container it is
> a function of the labware's physical dimensions (`container.py:84`), and for a tip it is
> `Tip.maximal_volume` (`tip.py:27,45`); neither reaches the analyzer, because `RESOURCE`'s operands
> are `slot`/`type`/`element_type`/`is_container`/`is_parameter`/`parents`/`grid`
> (`plr-sema/src/plr_sema/check/ir.py:184-191`) and none of them is a capacity. Therefore:
>
> - the **under-draw** half — `remove_liquid`'s `volume - get_used_volume() > 1e-06`, raising
>   `TooLittleLiquidError` — is **decidable** from the interval alone, since `get_used_volume()`
>   returns `self.pending_volume` (`volume_tracker.py:114-116`) and nothing else;
> - the **over-fill** half — `add_liquid`'s `volume - get_free_volume() > 1e-06`, raising
>   `TooLittleVolumeError` — is **not decidable**, since `get_free_volume()` is
>   `self.max_volume - self.get_used_volume()` (`:118-120`) and `max_volume` is ⊤. It stays Kleene ½
>   and emits `volume_state_unknown`.
>
> A rule that guessed a capacity — a default well volume, a nominal tip volume — would construct a
> definite verdict from a number nobody measured, which is the failure §0 exists to prevent.

The half that would make over-fill decidable is a capacity operand on `RESOURCE`, which is a wire
change and an `IR_VERSION` bump. §14.15 keeps it deferred **and records round 1's correction to the
sequencing argument for taking it early**: `ir_version` is already a component of §11.3.3's cache key
(`plr-sema/src/plr_sema/check/ir.py:918-926`), so a later bump invalidates a populated cache exactly
as completely as an early one. There is no accumulating cost being avoided by taking the bump before
#4922 ships, and increment 4's §13.13 Q2 is resolved against the sequencing framing on that basis.

---

## 14.3 The abstract state

```
Interval    ::=  [lo, hi]  with 0 <= lo <= hi <= +inf   |   TOP
VolumeState =  dict[cell: CellId, Interval]
CellId      =  ("container", slot: int, cell: str|null)  |  ("tip", channel: int)
```

`TOP` is `[0, +inf]` and the two are identified; the join is `[min(lo), max(hi)]`, which is the least
upper bound in the information order and gives a lattice of infinite height. **Infinite height is why
a widening operator is needed here and was not needed for tip state** (§10.1.1: "height 1 above its
two atoms … needs no widening operator"). The widening is §14.5's V4.

`CellId`'s container form reuses the `Ref(slot, cell)` pair the value grammar already produces
(§11.1.2), so a well reference in a kwarg *is* a cell id with no new resolution machinery. The tip
form keys on the channel index the tip family already computes (§10.1.3), which is the one place the
two families touch: **a tip cell exists only where the tip family says a channel has a tip.** If the
channel's `TipState` is not `HAS_TIP`, the tip cell is `TOP` — the analyzer does not know which tip is
mounted, so it cannot know its used volume.

---

## 14.4 The derived inputs

> **Normative (P7, the volume anchor).** A class `C` is **volume-anchored** iff it has ≥1
> zero-argument method whose body is a single `return <expr>` over `self.<F>` for some instance field
> `<F>` written in `C.__init__`, **and** ≥1 method whose body contains an `ast.Raise` of a class in
> the two-conjunct `volume_state` set (§14.1 fact 2) guarded by an `ast.Compare` mentioning one of
> those accessors and one of the method's own parameters. `C`'s **used-volume accessor** is the
> accessor named by the `TooLittleLiquidError` guard's comparison; its **free-volume accessor** is the
> one named by the `TooLittleVolumeError` guard's. Both are recorded by name; neither name is typed
> into `plr_sema`.
>
> **Fail-closed rule.** Zero anchors, or ≥2 candidate used-volume accessors, and P7 emits nothing for
> `C`; the volume family is disabled for every cell typing to `C`, and every verdict reverts to
> today's. The gap ledger records `volume_anchor: "absent"|"ambiguous"|{...}` per candidate class, the
> same visible-absence discipline §10.2.2 established for `tipstate_anchor`.
>
> **Measured expectation**, to be reproduced and published: `C = VolumeTracker`, used-volume accessor
> `get_used_volume`, free-volume accessor `get_free_volume`, field `pending_volume`.

> **Normative (P8, the operand-pairing idiom).** For a method `m` of receiver class `R`, match an
> `ast.ListComp` (or `GeneratorExp`) whose element is an `ast.Call` to a class `O` with keyword
> arguments, and whose single comprehension iterates `zip(a1, …, an)` where each `ai` is an
> `ast.Name`. Record, per keyword `k` of the element call whose value is a comprehension target bound
> at zip position `i`, the pair `(O.k → ai)`. When `ai` is a parameter of `m`, the binding is a
> **parameter pairing**; otherwise it is a **local pairing** and is recorded but not consumed.
> **P8 additionally records the comprehension's own assignment target**, which is what §14.0's B1
> binds a `for` loop against.
>
> **Measured expectation:** `LiquidHandler.aspirate`'s comprehension
> (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1007-1028`, element call at
> `:1008`, `zip` at `:1018-1027`) yields `SingleChannelAspiration.resource → resources` (`:1009`, zip
> position 0), `.volume → vols` (`:1010`, position 1) and `.tip → tips` (`:1014`, position 5 — a
> **local** pairing, since `tips` is the list built at `:974`, not a parameter), with assignment
> target `aspirations` (`:1007`).

> **Normative (the volume bridge, a second HM-24 pattern).** Match, against every `dropped_calls`
> entry reached at **depth 0** in `K`'s own body, the shape
>
> ```
> <name>.<field>.<attr>.<method>          e.g.  op.resource.tracker.remove_liquid
> ```
>
> where `<name>` is bound either by a P8 comprehension target **or by §14.0's B1**, `<field>` is a
> keyword of the bound element class `O` typed by P1a-as-extended-by-B2, `<attr>` is sent by P1a or
> **P1c** to a P7-anchored class `C`, and `f"{C}.{method}"` is a key in the contract table. When it
> matches, attach every guard of `C.<method>` to `K` as a **volume guard** carrying the originating
> expression in `via`, the paired parameter name in `cell_param`, the guard-parameter-to-`K`-parameter
> binding in `amount_param`, and **P10's `caller_scope`** (§14.0.2).
>
> `derived_contracts.json` gains one additive block per anchored class under `receiver_state` and one
> additive `volume_guards` list per contract entry, both read through `.get()` with an empty default
> so a pre-increment table degrades to today's behaviour. `schema_version` stays **1**.

**Measured expectation, to be reproduced and published:** `LiquidHandler.aspirate` acquires two volume
guards — `cell_param: "resources"`, `amount_param: "vols"`,
`via: "op.resource.tracker.remove_liquid"`, raising `TooLittleLiquidError`; and
`cell_param: <the tip local>`, `via: "op.tip.tracker.add_liquid"`, raising `TooLittleVolumeError`.
`LiquidHandler.dispense` acquires the mirror pair (`plr_preconditions.json:49775,49863-49864`).
**This is the expectation round 1 showed the §13.2.4 rule could not meet; AC-14.2 is what proves the
extended rule does.**

---

## 14.5 Transfer functions and the interval arithmetic

For an operation `op` with a volume guard carrying `cell_param` and `amount_param`, let `cells(op)` be
the `Value` of `op.kwargs[cell_param]` and `amounts(op)` the `Value` of `op.kwargs[amount_param]`.

> **Normative (V0, pairing).** If `cells(op)` is `Seq([c₁…cₙ])` with every `cᵢ` a `Ref`, and
> `amounts(op)` is `Seq([a₁…aₙ])` with every `aᵢ` a `Lit` of a JSON number, and the two lengths agree,
> then `op` pairs to the **ordered list** `[(cell(c₁), a₁), …, (cell(cₙ), aₙ)]`. A bare `Ref`/`Lit`
> pair is the length-1 case. **In every other case — either operand `Top`, a length mismatch, a `Seq`
> containing a `Top` or a non-numeric `Lit` — V0 does not apply and V3 does.** This mirrors PLR's own
> zip (`liquid_handler.py:1018-1027`), which is why the length agreement is a *conjunct* and not a
> recovery. **`cells(op)` may contain the same `Ref` more than once and this is not an error** — see
> V2.
>
> **Normative (V1, evaluate then transition).** Guards are evaluated against the pre-state, then the
> post-state is computed — E1's ordering, unchanged. **"Pre-state" means the state at the pair's own
> position in V2's threading, not at the operation's entry.**
>
> **Normative (V2, exact transfer, threaded sequentially — round-1 O4).** The pairs of V0's ordered
> list are applied **one at a time, in list order, to a running state**: pair `i`'s guard is evaluated
> against the state produced by pairs `1 … i-1`, and its own transfer is applied before pair `i+1` is
> evaluated. For a pair `(cell, a)` with running-state interval `[lo, hi]`: a used-volume-**decreasing**
> effect (the `TooLittleLiquidError` guard's own method, `remove_liquid`) gives
> `[max(0, lo - a), max(0, hi - a)]`; a used-volume-**increasing** effect (`add_liquid`) gives
> `[lo + a, hi + a]`. Cells outside `cells(op)` are unchanged. Which method is which is **derived**,
> not typed: the decreasing one is P7's `TooLittleLiquidError`-guarded method and the increasing one is
> the `TooLittleVolumeError`-guarded one.
>
> **Normative (V3, widen).** Every cell in `cells(op)` becomes `TOP` when V0 does not apply; **every
> cell of the whole state** becomes `TOP` when `op`'s method has a volume bridge only at depth > 0, or
> when two depth-0 volume bridges on the same cell disagree in direction — the E4.2/E4.3 discipline of
> §10.4, transposed.
>
> **Normative (V4, region widening).** On entry to a `LOOP` region whose `trip` is `null`, and on the
> `K`-th iteration of L1's bounded unroll (§12.3.3), **every** volume cell mentioned in the region
> becomes `TOP`. This is the widening operator the infinite-height lattice needs, and it is
> deliberately the crudest one: an interval that grows without bound across a fixpoint is exactly the
> non-termination case §12.3.3's finite-height argument did not have to handle, and jumping straight
> to `TOP` terminates in one step. Precision inside a **proved-trip** unroll is unaffected, because L1
> threads real iterations and only the tail widens.

**Why V2 threads rather than snapshots, and why the draft's silence here was a soundness bug (O4).**
PLR explicitly supports one well being drawn by several channels in one call: when a single resource
is passed with multiple channels, `resources = [resource] * len(use_channels)`
(`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:997-999`). It then processes the
paired operations **sequentially** — `for op in aspirations:` at `:1031`, with
`op.resource.tracker.remove_liquid(op.volume)` at `:1034` mutating `pending_volume` synchronously
(`volume_tracker.py:96`) before the next iteration. So the second channel's guard is checked against
the volume the first channel already reduced. §13.2.5's V1 read as *simultaneous* — evaluate every
guard against one shared pre-operation snapshot, then transition — and against PLR's sequential order
that produces a **false `SAFE`**: a well seeded to 100 µL with `aspirate(resources=[well, well],
vols=[60, 60], use_channels=[0, 1])` gives both guards `60 - 100 ≤ 1e-06` under a snapshot reading,
while the real run raises `TooLittleLiquidError` on the second channel. That is an unsound `SAFE`
where the execution raised — the first-severity class — and no fixture in the draft's oracle set
exercised it, because every named fixture was single-channel. AC-14.6 is that fixture.

**Guard evaluation.** The two conditions are `volume - self.get_used_volume() > 1e-06` and
`volume - self.get_free_volume() > 1e-06`, where `volume` binds to the paired amount `a` and the
accessor reads the cell's running interval. With `used ∈ [lo, hi]`:

| guard | fires (`T`) iff | does not fire (`F`) iff | otherwise |
|---|---|---|---|
| under-draw (`remove_liquid`) | `a - hi > 1e-06` | `a - lo <= 1e-06` | `½` |
| over-fill (`add_liquid`) | never (capacity ⊤) | never | **always `½`** (§14.2) |

`T`/`F`/`½` then produce `WILL_FAIL`/`SAFE`/`UNKNOWN` through §10.3.3's existing table unchanged,
with `category = "precondition_state"` and, for `½`, `reason = "volume_state_unknown"`.

**The `1e-06` tolerance is read from the guard, not typed.** It is a literal in the derived
`condition` string (`plr-sema/data/derived_contracts.json:158119`) and is evaluated as part of the
`Cmp`; nothing in `plr_sema`'s source names it.

---

## 14.6 The hypothesis gate — generalised fail-closed after round 1

Every volume guard in `LiquidHandler` sits under conditions the analyzer cannot evaluate. In
`aspirate` they are a scope: `if does_volume_tracking():` at
`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1032`, and
`if not op.resource.tracker.is_disabled:` at `:1033`, wrapping the tracker call at `:1034`. Main spec
§Open decisions 2 and increment 1 §10.9 both record that a definite volume verdict therefore needs a
`SoundnessScope` environment record, which does not exist.

**It is not needed, because the two verdict directions are not symmetric under such a condition:**

- If the condition is **false**, `remove_liquid` is never called from `aspirate` at all, so the site
  cannot raise. A `SAFE` finding for that guard — "this guard does not fire" — is therefore **true
  under both branches** and needs no hypothesis.
- A `WILL_FAIL` finding claims the site *does* raise, which is false when the condition is false. It
  needs the hypothesis.

> **Normative (the conditional-guard rule, generalised — round-1 O3).** A volume guard is
> **conditional** iff its P10 `caller_scope` (§14.0.2) is `null`, **or** contains any entry the
> evaluator does not recognise as satisfied. A conditional guard may emit `SAFE` and `UNKNOWN` but
> **never `WILL_FAIL`**. A `T`-evaluating conditional guard emits `UNKNOWN` with reason
> `volume_tracking_unasserted`.
>
> **An entry is recognised as satisfied in exactly one way:** it is a bare zero-argument call `f()`
> whose callee name is a member of `env`. **Everything else — a `for` header, an attribute test, a
> comparison, a `UnaryOp`, a call with arguments, an unparseable string — is unrecognised and blocks
> `WILL_FAIL`.** The draft's rule spoke only of "a zero-argument call `f()`" and then asserted in
> prose that `not op.resource.tracker.is_disabled` "is handled by the same rule"; it was not, because
> `VolumeTracker.is_disabled` is a `@property` (`external/pylabrobot/pylabrobot/resources/volume_tracker.py:54-56`)
> and the conjunct is an `ast.UnaryOp` over an `ast.Attribute` with no `ast.Call` in it at all. The
> generalised rule covers it by **not** recognising it, which is the fail-closed direction and needs no
> second mechanism.
>
> **Normative (the env argument).** `check_ir` gains a keyword-only parameter
> `env: frozenset[str] = frozenset()`. **`env` defaults to empty and `check_graph`'s
> two-positional-argument signature does not change**
> (`plr-sema/src/plr_sema/check/__init__.py:713`), so every existing test, every existing fixture and
> the whole tier-1 replay are unaffected by construction. `env` is added to §11.3.3's cache key as a
> fifth component, `tuple(sorted(env))`.
>
> **The harness asserts the hypothesis by observation, not by typing it.** `plr-sema/eval/` already
> imports from the verifier's package at runtime (`plr-sema/eval/oracle_common.py:698-702`), so after
> the verifier establishes its configuration the harness **calls**
> `pylabrobot.resources.volume_tracker.does_volume_tracking()` (`volume_tracker.py:21-22`) and passes
> `env = {"does_volume_tracking"}` iff it returns `True`. The name reaching `env` is read from the
> guard's own `caller_scope` on one side and from the callable's `__name__` on the other; **no string
> is typed into `plr_sema` or into the harness**, which is why this costs no registry row.

**Consequence, stated plainly: at the current pin, `aspirate`'s volume guard will be conditional even
with `env = {"does_volume_tracking"}`, because its `caller_scope` also contains the `is_disabled`
test and the `for` header.** So the *first* landing of this increment produces `SAFE` and `UNKNOWN`
and **no `WILL_FAIL` at all** on real corpus rows, and only the tier-3 mutants — whose fixtures the
harness controls — will exercise the `WILL_FAIL` path, and only if the harness can discharge the
`is_disabled` conjunct too. **That is a real and unattractive consequence of the fail-closed rule, it
is disclosed here rather than discovered at gate time, and it is §14.16's Q1.** Recognising a
per-instance property test requires per-instance knowledge the analyzer does not have; recognising it
by *assuming* trackers are enabled is exactly the assumption A-TRACKER-ENABLED's "what breaks if it
is false" column forbids.

---

## 14.7 The assumptions, named so a reviewer can attack them

| id | assumption | why it is needed | what breaks if it is false | oracle |
|---|---|---|---|---|
| **A-VOLUME-TRACKING** | when `"does_volume_tracking"` ∈ `env`, tracking was on for the whole walk | `WILL_FAIL` claims the guard was reached | a `WILL_FAIL` on a run that never evaluated the guard. `no_volume_tracking()` is a context manager (`volume_tracker.py:25-30`) the analyzer cannot see, exactly as §10.1.3's `use_channels` manager | tier 3's volume mutants (0 unsound gate) and tier 1's 0-unsound gate over 525 operations (`outputs/plr-sema/oracle_replay_260903_rebaseline.json:10-11`) |
| **A-TRACKER-ENABLED** | no cell's tracker was individually disabled | `liquid_handler.py:1033`'s `not …is_disabled` conjunct is unrecognised | **nothing, as of §14.6's generalisation** — an unrecognised conjunct blocks `WILL_FAIL` outright, so this assumption is no longer load-bearing for soundness. It is retained as a *precision* note: it is the reason real corpus rows produce no definite volume verdict (§14.6's closing paragraph) | §14.6's rule is asserted directly by AC-14.4 |
| **A-NO-CORRECTION** | the volume PLR charges a cell is the literal the kwarg carries | V2 adds and subtracts the kwarg literal verbatim | an interval that drifts from the real one, in either direction, after the first corrected transfer. PLR's `vols` are `[float(v) for v in vols]` at `liquid_handler.py:968` — no liquid-class correction is applied on this path at the current pin | tier 1 + tier 3; a drift shows up as an unsound row, because the oracle compares against the executed raise |
| **A-COMMIT-VOLUME** | a committed transfer equals a pending one for the abstraction | V2 reads `get_used_volume()`, which returns `pending_volume` (`volume_tracker.py:114-116`), while `commit` copies it to `volume` (`:140-146`) and `rollback` restores it (`:148-151`) | an interval that reflects a rolled-back operation. `aspirate` commits or rolls back every touched tracker in one block (`liquid_handler.py:1058-1064`), which is A-COMMIT's own argument (§10.2.2) transposed to volume — and the rollback path only runs when the backend raised, which A-COMPLETES already scopes out | tier 3's volume mutants |
| **A-TIP-CELL** | a tip cell's interval is `TOP` unless the tip family says the channel is `HAS_TIP` | the tip cell's identity is the mounted tip | nothing in the `SAFE` direction: an unknown tip cell is `TOP` and every guard on it is ½. Recorded because it is the one place the two families are coupled | AC-14.5's tip-cell assertion |
| **A-SCOPE-TEXT** (new, from §14.0.2) | a `dropped_calls` expression appearing exactly once by text in `K`'s body is the call the survey recorded | P10 keys on reconstructed callee text, not position | a `caller_scope` attached to the wrong call site. Discharged **fail-closed**, not by argument: two matches record `null`, and `null` blocks `WILL_FAIL`. What would break it is a *single* textual match that is nonetheless the wrong call — impossible while the key is the full dotted callee | AC-14.3(iii)'s duplicate-expression fixture |

---

## 14.8 Seeding, and why it reuses increment 3's scaffolding precedent

An executed corpus row starts with wells that already contain liquid. The harness computes those
seeds itself — `_precondition_plan` returns a `seed_volumes` dict (`plr-sema/eval/oracle_common.py:690-696`;
the aspirate branch builds `dict(zip(sources, vols))` at `:733-739`) and `row_to_verifier_inputs` puts
it in `deck_layout` at `:983-989`. **That dict is a harness artifact and is not in the extractor's
graph**, so a `check_graph` on real extracted source sees no seeds and every cell is `TOP` at entry.
That is correct and is not a defect.

For the *oracle*, the two sides must describe one execution, which is §12.1.6's argument for lowering
the scaffolding `setup()` call. The same remedy applies:

> **Normative.** For each `(cell, volume)` in the row's `deck_layout.seed_volumes`, the caller in
> `plr-sema/eval/` prepends a `CALL` to the derived volume-setting method — `VolumeTracker.set_volume`
> at the current pin (`external/pylabrobot/pylabrobot/resources/volume_tracker.py:66-72`, which writes
> both `volume` and `pending_volume`) — with the cell as receiver and the seed as a `Lit` kwarg,
> **before** the scaffolding reset, with `origin` the string `"seed"`. It is emitted **by the caller**,
> not synthesised inside `lower_calls`, which stays a pure function of its input sequence. The method
> is selected by P7's own accessor pass (a method assigning the anchored field from a parameter,
> unconditionally, at statement position), not named in our source.

**This is why no `IR_VERSION` bump is needed for seeding.** A prepended `CALL` reuses an opcode, a
lowering path and an `origin` convention that all shipped in increment 3 and are pinned by AC-12.3.

---

## 14.9 The oracle: two mutant classes and a fixture set

**Tier 3 (mutants).** `plr-sema/eval/tip_mutants.py`'s pattern generalises exactly, and the reason it
generalises is a property of the existing code that must be stated because the whole construction
depends on it: `row_to_verifier_inputs` is called on the **base** row and its `deck_layout` — seeds
included — is carried into the mutant unchanged (`plr-sema/eval/tip_mutants.py:238-247`, where
`example` is built from the base row's three outputs and the mutators at `:167` then edit only
`example["call_sequence"]`). So a mutant that *raises* an aspirate volume over-draws against a seed
computed from the **unmutated** call, and genuinely raises. Had the seeds been recomputed from the
mutant, the mutation would be self-cancelling and the class would measure nothing — the same trap
`_shift_tip_ref`'s docstring records for m2 (`tip_mutants.py:127-140`).

> **Normative.** Two classes, in a new `plr-sema/eval/volume_mutants.py`:
> **v1 (`v1_overdraw_aspirate`)** multiplies the last `aspirate`'s `volume_ul` so it exceeds the
> base row's seed for that source; expected exception `TooLittleLiquidError`.
> **v2 (`v2_overdraw_transfer`)** does the same to a `transfer`'s `volume_ul`; expected exception
> `TooLittleLiquidError`.
> Both reuse `run_one_mutant`'s shape (`tip_mutants.py:170-224`), which is refactored to take the
> mutator and the expected exception as arguments rather than reading the module globals `_MUTATORS`
> (`:167`) and `_EXPECTED_EXC` (`:69`). **The refactor must not move the m1/m2 numbers**, and AC-14.9
> gates that as a non-regression.
>
> **No over-fill mutant class is specified**, because §14.2 makes an over-fill `WILL_FAIL`
> unreachable; a class whose gate can only ever be `0 of n` measures the spec's own scope decision
> rather than the implementation.

**Tier 2b (executed fixtures).** The region fixture set (`plr-sema/eval/fixtures/regions/`, 11 fixtures
at `outputs/plr-sema/tier2b_260903.json:7`) gains volume fixtures: one straight-line over-draw, one
over-draw at the second iteration of a proved-trip loop, one loop whose per-iteration draw is safe
individually and exhausts the well collectively, **and one two-channel single-well fixture (§14.5's
O4 case)**. The existing `region_unsound = 0` and `region_will_fail_fired = 3`
(`tier2b_260903.json:8-9`) become the floor, not the target.

---

## 14.10 Soundness claims and the oracle that checks each

| claim | § | oracle |
|---|---|---|
| the bridge actually matches on real PLR at the pin | 14.0.1, 14.4 | AC-14.2 — the published `volume_guards` block for `aspirate`/`dispense`. **This is the claim round 1 falsified about §13.2 and is the reason this increment exists** |
| B2's P1a widening does not disturb any existing selection | 14.0.1 | AC-14.1(iii)'s before/after assertion on `LiquidHandler.head → TipTracker` |
| the caller's hypothesis conjuncts reach the bridged guard | 14.0.2 | AC-14.3 — `caller_scope` published for `aspirate`'s bridged guard |
| an unrecognised conjunct cannot produce `WILL_FAIL` | 14.6 | AC-14.4, asserted over `is_disabled`, a `for` header and a `null` caller scope |
| a paired under-draw guard evaluating `T` really raises | 14.5 | tier 3's v1/v2 mutants (0 unsound) and tier 1's 0-unsound gate over 525 operations |
| **two channels drawing one well are checked sequentially, not simultaneously** | 14.5 V2 | AC-14.6's two-channel/one-well fixture, executed — the round-1 O4 case, whose absence would be a false `SAFE` |
| the over-fill half is genuinely undecidable and is not quietly guessed | 14.2 | AC-14.5(d)'s assertion that an `add_liquid`-derived guard yields `volume_state_unknown` for every fixture |
| V4's `TOP` widening terminates the fixpoint on an infinite-height lattice | 14.5 | AC-14.5's `while`-loop volume fixture |
| A-VOLUME-TRACKING, A-NO-CORRECTION, A-COMMIT-VOLUME, A-TIP-CELL, A-SCOPE-TEXT | 14.7 | the per-row entries in that table |
| the volume exception set is `{TooLittleLiquidError, TooLittleVolumeError}` and is derived | 14.1 | AC-14.2(ii): 4 members unfiltered, 2 after the module conjunct, plus an AST literal scan |

---

## 14.11 Hand-maintained impact

**New registry rows: zero. Retired registry rows: zero.** `live_rows()` is 24
(`plr-sema/src/plr_sema/_hand_maintained.py:851-855`) against `BUDGET_CAP = 24` (`:43`).
**Headroom 0, before and after.**

**Two per-row ceilings move, both loud one-line diffs and neither a row addition:**

| row | on entry to this increment | after | what the new patterns are |
|---|---|---|---|
| **HM-24** (`_hand_maintained.py:781-814`, `metric="patterns"`/`declared=1`/`status="CAPPED"` at `:793-795`) | live 1, declared 1 | **live 2, declared 2** | the volume bridge `<name>.<field>.<attr>.<method>` (§14.4). `_measure_hm24` (`:244-261`) asserts `_BRIDGE_SHAPE_RE.groups == 3` on the *tip* regex and is unaffected; the volume regex gets its own measure, asserted the same way |
| **HM-25** (`:815-847`, the same three fields at `:828-830`) | live 6, declared 6 **after increment 4's P9 bump** | **live 8, declared 8** | P7's accessor-anchor shape and P8's zip-comprehension pairing idiom (§14.4) |

**B1, B2, P1c and P10 are deliberately *not* counted as HM-25 patterns, and the reason has to be
argued rather than assumed.** HM-25's metric is "patterns over how PLR is written" — a shape that can
stop matching when PLR changes its idiom. B2 (admit class-level annotations) and P1c (read
constructor calls in `__init__`) are **Python language constructs**, not PLR idioms: every dataclass
in every codebase declares fields that way, and `self.x = C()` is not a style choice PLR could
abandon while still writing Python. B1 and P10 are closer to the line — a `for` over a comprehension's
output is a shape PLR could stop writing — but what they match is a *binding*, resolved by Python's
own scoping rules, not a recognisable idiom. **A reviewer may disagree**, and §14.16's Q2 puts the
question directly: if B1 and P10 are counted, HM-25 is 10 rather than 8, and that is a bigger diff
than any single row has taken.

**`REASON_VOCABULARY` (HM-14): 8 → 10 of cap 12** (`plr-sema/src/plr_sema/verdict.py:129-154`; the row
is `CAPPED` at declared 12, `_hand_maintained.py:561-565`, so live 10 ≤ 12 and **no `declared` edit is
needed**). `volume_state_unknown` (the cell's interval, or the capacity, is `TOP`) and
`volume_tracking_unasserted` (the atom evaluated `T` but the guard is conditional, §14.6). Neither
member is added by increment 4 — round 1's Q6 observed that shipping a vocabulary member whose
producer does not work is the same "dead data" problem §13.7 raises for `lid_state_unknown`, and the
user's decision holds `REASON_VOCABULARY` at 8 until this increment lands.

**What could have been hand-typed, and what it is instead:**

| what could have been typed | what it is instead |
|---|---|
| `{"TooLittleLiquidError", "TooLittleVolumeError"}` as a class-name list | the two-conjunct taxonomy filter (§14.1 fact 2), reusing the module literal AC-10.9 already declares. 4 members → 2 |
| `"get_used_volume"` / `"get_free_volume"` / `"pending_volume"` as accessor names | P7 reads them off the guards' own `ast.Compare` operands (§14.4) |
| a per-method map from resource parameter to volume parameter (`aspirate → (resources, vols)`) | P8's zip-comprehension pairing over `liquid_handler.py:1007-1028` |
| `"op"`, or a map from method to loop-variable name | B1 resolves the binding through Python's own `for`-over-`Name` scoping (§14.0.1) |
| `"tracker"`, or `Container.tracker → VolumeTracker` as a fact | P1c reads the constructor call (§14.0.1), precedented by `_constructor_state` |
| `"does_volume_tracking"` as an environment key | the harness **calls** `does_volume_tracking()` and reads the callable's own name (§14.6) |
| a list of "conjuncts that are safe to ignore" | §14.6 recognises exactly one shape and fails closed on everything else |
| a default well capacity or nominal tip volume | **nothing.** The over-fill half stays ½ (§14.2) |

**Wire format: no change.** `volume_guards`, the per-class volume block and `caller_scope` are new
optional keys read through `.get()`; `env` is a keyword-only parameter with a default that reproduces
today's behaviour. `IR_VERSION` stays **2**.

---

## 14.12 Acceptance criteria

**None of these gates any increment-4 work.** They gate the unscheduled rows of §14.13.

- **AC-14.1 (the three bridge sub-boxes derive, and the widening disturbs nothing).** Four
  sub-assertions, each published as a measured set rather than asserted: (i) **B1** binds
  `op : SingleChannelAspiration` in `LiquidHandler.aspirate` via the comprehension assigned to
  `aspirations` (`liquid_handler.py:1007,1031`), and the complete set of `(K, name, element_class)`
  triples is published; a two-`for`-loops-over-one-list fixture binds **nothing**. (ii) **B2** yields
  `SingleChannelAspiration.resource → Container`, `.tip → Tip`, `.volume → float`
  (`external/pylabrobot/pylabrobot/liquid_handling/standard.py:53-56`), and the complete before/after count of P1a's selections is published.
  (iii) **B2 disturbs no existing selection**: `receiver_state["LiquidHandler"]["channel_attr"]` is
  still `"head"` with tracker class `TipTracker`, and the shipped `derived_contracts.json`'s
  `receiver_state` block is **byte-identical** except for the additive volume keys — the
  stub-defeating half, since a widening that captured a bare `ast.Name` inside a method body would
  pass (ii) and fail this. (iv) **P1c** yields `Container.tracker → VolumeTracker` (`container.py:85`)
  and `Tip.tracker → VolumeTracker` (`tip.py:45`), with the whole-surface selection count published,
  and a two-different-constructors fixture records nothing.
- **AC-14.2 (the bridge matches on the real pin — the claim round 1 falsified).**
  `contracts["LiquidHandler.aspirate"]["volume_guards"]` contains exactly two entries: one raising
  `TooLittleLiquidError` with `via == "op.resource.tracker.remove_liquid"`, `cell_param ==
  "resources"`, `amount_param == "vols"`; one raising `TooLittleVolumeError` with `via ==
  "op.tip.tracker.add_liquid"`. `LiquidHandler.dispense` carries the mirror pair. Two further
  sub-assertions: (ii) the unfiltered taxonomy set `category == "volume_state"` has **4** members and
  the module conjunct selects exactly `{TooLittleLiquidError, TooLittleVolumeError}`, asserted against
  `training/verify/data/plr_exception_taxonomy.json`; (iii) an AST literal scan of `plr-sema/src/`
  finds no `ast.Constant` string equal to `"get_used_volume"`, `"get_free_volume"`,
  `"pending_volume"`, `"tracker"`, `"op"`, `"TooLittleLiquidError"`, `"TooLittleVolumeError"`,
  `"resources"` or `"vols"`.
- **AC-14.3 (caller scope reaches the bridged guard).** `aspirate`'s `TooLittleLiquidError` volume
  guard carries a non-null `caller_scope` whose entries include the `does_volume_tracking()` test and
  the `is_disabled` test from `liquid_handler.py:1032-1033`, published verbatim as produced. Two
  further sub-assertions: (ii) the guard's own `scope_trail` is **unchanged** from the callee's
  contract — `["if volume - self.get_used_volume() > 1e-06"]` — so the two facts are kept apart;
  (iii) a fixture whose method body contains the same dotted call expression twice under different
  `if` scopes records `caller_scope: null`, asserted directly, not inferred from an absent verdict.
- **AC-14.4 (fail-closed on anything unrecognised).** With `env == {"does_volume_tracking"}`, a guard
  whose `caller_scope` is exactly `["if does_volume_tracking()"]` may emit `WILL_FAIL`; the same guard
  with any one of — an added `is_disabled` attribute test, an added `for` header, a call with
  arguments, or `caller_scope: null` — emits `UNKNOWN` with reason `volume_tracking_unasserted`
  instead. Four fixtures, one per shape. The `null` case is the stub-defeating half: an implementation
  that treated a missing scope as an empty one passes the other three and fails this.
- **AC-14.5 (the interval domain decides one half and provably declines the other).** Four fixtures,
  each with a prepended seed `CALL` (§14.8). (a) seed 100, `aspirate(vols=[200])` → exactly one
  `Finding` with `verdict is Verdict.WILL_FAIL`, `category == "precondition_state"`, `plr_site ==
  PlrSite("external/pylabrobot/pylabrobot/resources/volume_tracker.py", 92,
  "VolumeTracker.remove_liquid")`. (b) seed 100, `aspirate(vols=[50])` → a `Verdict.SAFE` finding at
  the same site. (c) the same graph with `vols` lowering to `Top` → `Verdict.UNKNOWN` with reason
  `volume_state_unknown`. (d) **the declining half**: `dispense(vols=[10_000])` into a seeded well
  yields `Verdict.UNKNOWN` with reason `volume_state_unknown` at the `add_liquid` site — never
  `WILL_FAIL` — because the capacity is `TOP`; and a tip cell on a channel whose `TipState` is not
  `HAS_TIP` likewise yields `volume_state_unknown` (A-TIP-CELL). A fifth fixture, a `while` loop whose
  body aspirates a literal volume, asserts `check_ir` converges within `K` passes, does not raise, and
  leaves every cell in the region `TOP` after the region's `END` (V4). (d) is the stub-defeating half.
- **AC-14.6 (V2 threads sequentially — round-1 O4).** A well seeded to 100 with
  `aspirate(resources=[well, well], vols=[60, 60], use_channels=[0, 1])` yields a `Verdict.SAFE`
  finding for the **first** pair and a `Verdict.WILL_FAIL` for the **second**, both sited at
  `VolumeTracker.remove_liquid`, and **no** `SAFE` for the second. The same fixture is executed
  against the chatterbox deck under tier 2b and the execution raises `TooLittleLiquidError` at the
  second channel, with the static and executed sides agreeing. An implementation that evaluated both
  guards against one shared pre-operation snapshot emits two `SAFE`s and fails — which is the
  false-`SAFE` round 1 found and no draft fixture exercised.
- **AC-14.7 (`env` gates `WILL_FAIL` only, and defaults to unasserted).** AC-14.5's fixture (a), run
  through `check_ir` with the default `env == frozenset()`, yields `Verdict.UNKNOWN` with reason
  `volume_tracking_unasserted` — **not** `WILL_FAIL` — while fixture (b)'s `SAFE` is **unchanged** by
  `env`, in both directions. `check_graph(g, c)` with two positional arguments compiles, runs and
  returns the identical report it returns today for every shipped fixture. The `SAFE`-unchanged half
  is the whole content of §14.6's asymmetry argument.
- **AC-14.8 (the registry arithmetic is exactly as specified).** After this increment,
  `len(live_rows()) == 24` and `BUDGET_CAP == 24`; HM-24's `declared` is **2** and its measure returns
  2; HM-25's `declared` is **8** and its measure returns 8; `len(REASON_VOCABULARY) == 10` against
  HM-14's unchanged `declared == 12`; and `test_no_surface_exceeds_its_declared_size` and
  `test_total_declared_within_budget` both pass. A second assertion pins the *entry* condition: the
  commit's parent has HM-25 at 6, so the diff is visibly 6 → 8 and not 5 → 8.
- **AC-14.9 (tier 3 — the volume mutants fire, and the tip mutants do not regress).**
  `plr-sema/eval/volume_mutants.py` reports v1 with **0 unsound** in both directions and its achieved
  `WILL_FAIL`-at-the-raised-index count published; v2 likewise with its own achieved number and no
  threshold (`transfer`'s guard interacts with #4946's binding and the interaction must be measured
  before it is gated). As a non-regression, m1's and m2's numbers are re-measured and published
  against whatever baseline is current at the time this increment runs, and any movement is attributed
  before the run is accepted — the `run_one_mutant` refactor (§14.9) is what could move them.
- **AC-14.10 (tier 2b — executed volume ground truth, including the collective and two-channel
  cases).** The four new region fixtures (§14.9) are executed against the chatterbox deck and compared
  on `(operation, iteration)`: **zero** unsound rows; the straight-line over-draw and the
  second-iteration over-draw each carry a static `WILL_FAIL` at the `(operation, iteration)` the
  execution raised; the **collective-exhaustion** fixture carries a static `WILL_FAIL` at the
  iteration the execution raised, **not** at the first iteration and **not** nowhere; and the
  existing `region_unsound == 0` and `region_will_fail_fired >= 3`
  (`outputs/plr-sema/tier2b_260903.json:8-9`) still hold. The collective case is the stub-defeating
  half: a per-operation check that never accumulates passes the first two and fails this one.
- **AC-14.11 (this document is machine-checked).** `plr-sema/tests/test_spec_lint.py` gains a
  `SPEC_INCREMENT_5` entry, and both the citation checker and the AC-gating half of the
  cross-reference checker report **zero** failing violations over this file.

---

## 14.13 Task rows — **scheduled: next sprint (user decision 260903)**

> **Every row in this table is unscheduled.** No row is dispatched by increment 4's sprint, no gate
> below is run this round, and no `**AC-14.n**` above gates any increment-4 work. The table is written
> in full — with its gates, its dependencies and its models — so that the increment is *dispatchable
> when it is scheduled*, and so the AC-gating lint can verify that every criterion has exactly one
> home. Ordering within the table is forced by §14.0's normative gate: **T24 and T25 must both land
> before T26 or T27.**

| task | scope | files | gate | ~LOC | depends on | model |
|---|---|---|---|---|---|---|
| **T24** | The bridge derivation (§14.0.1): B1's for-loop-over-comprehension-output binding with its two fail-closed cases; B2's class-level-`AnnAssign` branch of `_annotated_attributes`, disjoint from `_is_self_attr` and asserted not to disturb any existing selection; P1c's constructor-call typing over `__init__`, modelled on `_constructor_state`; the extended volume bridge and the `volume_guards` payload; every selection published as a measured set | modify `plr-sema/src/plr_sema/derive/receiver_state.py`, `plr-sema/src/plr_sema/derive/__main__.py`, `plr-sema/tests/test_derive.py`, `plr-sema/data/derived_contracts.json` (regenerated) | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_derive.py -q`; then `uv run python -m plr_sema.derive --survey-json training/verify/data/plr_preconditions.json --taxonomy-json training/verify/data/plr_exception_taxonomy.json --out $TMPDIR/contracts_t24.json --gap-ledger $TMPDIR/ledger_t24.json` and publish the four measured sets — satisfying **AC-14.1**, **AC-14.2** | ~420 | — | Sonnet — four derivations, each of which must be measured and published rather than asserted |
| **T25** | Caller-scope threading (§14.0.2): P10 as a derive-side AST pass over the caller's own source, the `caller_scope` additive key kept disjoint from `scope_trail`, and the fail-closed `null` on zero or multiple textual matches; the generalised conditional-guard rule of §14.6 with its single recognised shape | modify `plr-sema/src/plr_sema/derive/receiver_state.py`, `plr-sema/src/plr_sema/derive/__main__.py`, `plr-sema/tests/test_derive.py` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_derive.py -q`; then re-run the derivation command from T24 into `$TMPDIR/contracts_t25.json` and publish `aspirate`'s `caller_scope` verbatim — satisfying **AC-14.3**, **AC-14.4** | ~230 | T24 | Sonnet — the fail-closed boundary is the soundness fence and the published scope is a measurement |
| **T26** | The interval domain and the transfer functions (§14.3, §14.5): `check/volumestate.py` with V0–V4, **V2 threaded pair-by-pair**, wired into `check/__init__.py`; the two-channel/one-well fixture and the `while` fixture | create `plr-sema/src/plr_sema/check/volumestate.py`, `plr-sema/tests/fixtures/volume_{overdraw,safe,top,overfill,while,two_channel_one_well}_graph.json`; modify `plr-sema/src/plr_sema/check/__init__.py`, `plr-sema/tests/test_check_graph.py` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_check_graph.py -q`; `uv run pytest plr-sema/tests/test_wire_fuzz.py -q` — satisfying **AC-14.5**, **AC-14.6** | ~360 | T24, T25 | Sonnet — V2's threading order is the one place a plausible implementation is unsound |
| **T27** | The hypothesis gate and the registry (§14.6, §14.11): `env` on `check_ir` and as the cache key's fifth component; the two new `REASON_VOCABULARY` members; the harness's runtime observation of `does_volume_tracking()`; **HM-24 `declared` 1 → 2 and HM-25 `declared` 6 → 8**, each with its `why_not_derived`/`breaks_when` extended | modify `plr-sema/src/plr_sema/check/__init__.py`, `plr-sema/src/plr_sema/check/ir.py`, `plr-sema/src/plr_sema/verdict.py`, `plr-sema/src/plr_sema/_hand_maintained.py`, `plr-sema/eval/oracle_common.py`, `plr-sema/tests/test_{verdict,check_graph,hand_maintained_ratchet,cache}.py` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_verdict.py -q`; `uv run pytest plr-sema/tests/test_hand_maintained_ratchet.py -q`; `uv run pytest plr-sema/tests/test_cache.py -q` — satisfying **AC-14.7**, **AC-14.8** | ~200 | T26 | Sonnet — the default-`env` direction is a soundness assertion, not a wiring one |
| **T28** | The oracle (§14.9): `volume_mutants.py` with v1/v2 and the `run_one_mutant` parameterisation; the four tier-2b volume fixtures including the two-channel/one-well and collective-exhaustion cases; the bathos sidecar fields `volume_fixtures`/`volume_unsound`/`volume_will_fail_fired` | create `plr-sema/eval/volume_mutants.py`, `plr-sema/eval/fixtures/regions/volume_*.py`; modify `plr-sema/eval/tip_mutants.py`, `plr-sema/eval/region_oracle.py`, `plr-sema/eval/tier2_extractor.bth.toml`, `plr-sema/tests/test_oracle_replay.py` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_oracle_replay.py -q`; then `uv run python plr-sema/eval/volume_mutants.py --corpus training/assemble/out/corpus_p25.jsonl --examples-dir training/examples --contracts plr-sema/data/derived_contracts.json --report $TMPDIR/volume_mutants.json`; `uv run python plr-sema/eval/tip_mutants.py --corpus training/assemble/out/corpus_p25.jsonl --examples-dir training/examples --contracts plr-sema/data/derived_contracts.json --report $TMPDIR/tip_mutants_regression.json`; `uv run python plr-sema/eval/region_oracle.py --fixtures plr-sema/eval/fixtures/regions --contracts plr-sema/data/derived_contracts.json --report $TMPDIR/tier2b_volume.json` — satisfying **AC-14.9**, **AC-14.10** | ~430 | T27 | Sonnet — every published number is a measurement |
| **T29** | Lint and index: add `SPEC_INCREMENT_5` to `plr-sema/tests/test_spec_lint.py`'s two parametrised live-spec tests; regenerate `.praxia/docs/INDEX.md` | modify `plr-sema/tests/test_spec_lint.py`; regenerate `.praxia/docs/INDEX.md` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_spec_lint.py -q` — satisfying **AC-14.11** | ~15 | — | Haiku |

**Sizing note.** T24 at ~420 is past one session and splits at B2/P1c (the two P1 extensions, which
land together and leave the tree green because nothing consumes them yet) versus B1 plus the extended
bridge. **Do not split T24 from T25 across a sprint boundary**: §14.0's normative gate makes a landed
T24 without T25 the configuration in which the analyzer can construct an ungated volume `WILL_FAIL`,
which is the soundness bug this whole re-scope exists to avoid. T28 at ~430 splits cleanly at
mutants-versus-fixtures.

---

## 14.14 What this changes in increments 1–4

1. **Main spec §Open decisions 2's sunset clause.** Its resolution reads *"leave numeric atoms at ½
   through v1 and the first post-corpus increment"*. Increments 1–4 have shipped, so the reservation
   no longer holds anything back, and this increment reopens it **for exactly one class of atom**: a
   `Cmp` in a guard raising a taxonomy `volume_state` exception from `pylabrobot.resources.errors`,
   evaluated against §14.3's interval domain. **Every other numeric `Cmp` still folds to ½** —
   including `drop_tips`'s `tip.tracker.get_used_volume() > 0 and (not allow_nonzero_volume) and
   does_volume_tracking()`, which is a **compound** condition excluded by §10.3.1's single-atom
   criterion, not by its numerics.
2. **§Open decisions 2's `SoundnessScope` prerequisite is discharged by narrowing, not by building
   it** (§14.6). `SoundnessScope` as a wire record remains unbuilt and remains deferred row (b).
3. **Increment 1 §10.9's first bullet** ("Volume atoms — every numeric `Cmp` stays ½ … Volume also
   needs a `SoundnessScope` record") is superseded by items 1 and 2. Its *second* clause — that tip
   state does not need such a record — is unchanged and still true.
4. **Increment 1 §10.1.1's "finite-height and needs no widening operator"** is narrowed to the tip
   lattice. §14.3's interval lattice has infinite height and §14.5's V4 is its widening operator.
5. **Increment 1 §10.2.1's P1a** gains B2's disjoint class-level branch and is joined by P1c
   (§14.0.1). Neither changes any existing P1a selection, and AC-14.1(iii) is what pins that.
6. **Increment 2 §11.3.3's cache key gains a fifth component**, `tuple(sorted(env))`. Increment 4
   ships the cache without it (its `env` is always empty); this increment adds the component and
   invalidates every entry written before it, which is correct and is the cheap direction.
7. **Increment 4 §13.2** is a stub pointing here, and increment 4's §13.7 carries only HM-25 5 → 6.

---

## 14.15 Explicitly not in this increment

- **A capacity operand on `RESOURCE`.** What would make the over-fill half decidable (§14.2): a wire
  change, an `IR_VERSION` bump, and an upstream extractor change to read `Container.max_volume` /
  `Tip.maximal_volume` off the labware definition. Round 1 removed the argument for taking it early —
  `ir_version` is already a cache-key component, so a later bump costs exactly what an early one does.
- **Liquid-class corrections.** A-NO-CORRECTION assumes none is applied; PLR at this pin applies none
  on the aspirate path (`liquid_handler.py:968`).
- **The 96-head's volume cells.** Excluded by A-TIP-CELL, with no separate rule.
- **`BlowOutVolumeError`.** Excluded by the module conjunct (§14.1 fact 4).
- **A survey-side scope field for `dropped_calls`.** §14.0.2 chose the derive-side pass; the
  survey-side option is the better long-run key and is named there, not adopted.
- **Recognising a per-instance flag such as `is_disabled`.** §14.6 fails closed on it. Recognising it
  needs per-instance knowledge the analyzer does not have, and assuming it is what A-TRACKER-ENABLED
  forbids. This is the direct cause of §14.6's disclosed consequence and of §14.16's Q1.
- **Precision targets.** Deferred (f) stands. AC-14.9's v1 number is published, not gated.

---

## 14.16 Open questions for the adversarial round

1. **§14.6's disclosed consequence: a family that ships with no `WILL_FAIL` on real data.** Because
   `aspirate`'s `caller_scope` contains an `is_disabled` attribute test that §14.6 cannot recognise,
   the fail-closed rule blocks `WILL_FAIL` on every real corpus row, and only harness-controlled
   fixtures exercise the definite path. That is sound and it may also be worthless. A reviewer should
   decide whether the honest move is (a) ship it anyway, since `SAFE` findings are real and the
   `WILL_FAIL` path returns for free when the recognition set grows; (b) build the `SoundnessScope`
   record now so the hypothesis can be asserted explicitly rather than fail-closed around; or (c)
   defer again until a mechanism exists that can discharge a per-instance flag. **This is the
   successor to §13.13's Q3 and it is now the increment's central question**, because round 1 turned
   the `env` mechanism from a convenience into the thing that decides whether the family says anything.
   **RESOLVED (user, 260903): (a) — build it if it is firable at all.** The corpus is a set of
   examples, not the sum of what is valid and useful; a family that produces `SAFE` on real rows and
   `WILL_FAIL` on every protocol a fixture or a future corpus row can construct is covered, not
   worthless, and the `WILL_FAIL` path on today's rows returns for free when the recognition set
   grows. The fail-closed rule stays (soundness); §14.6's disclosure stays as a precision note; the
   increment is no longer deferred and its task rows are scheduled (§14.13).
2. **§14.11's pattern accounting.** B2 and P1c are argued to be Python-language constructs and not
   HM-25 patterns; B1 and P10 are argued to be bindings rather than idioms. If a reviewer counts all
   four, HM-25 is 10 rather than 8 — a bigger single-row diff than the registry has taken — and the
   right response may be a row split rather than a ceiling bump, which §9.4's own anti-gaming clause
   names as a known, unenforced gap.
3. **The derive-side-versus-survey-side choice (§14.0.2).** Taken on blast radius. The survey-side
   option keys on *position*, which is strictly stronger than reconstructed text, and would let the
   deferred-item-(e) worklist rank by scope. A reviewer who thinks a schema change is the honest cost
   should say so before T25 writes a text matcher whose ambiguity case is fail-closed-by-necessity.
4. **Whether `volume_tracking_unasserted` survives.** Round 1's Q6 flagged it as a vocabulary member
   at risk of having no working producer. §14.6 gives it one — but by §14.16's Q1, that producer fires
   only on fixtures at the current pin. If Q1 resolves to (c), the member should not land. **Q1 resolved to (a) (user, 260903), so the member lands.**
5. **AC-14.9's v2 has no threshold.** `transfer`'s volume guard interacts with increment 4's #4946
   channel binding, and neither this document nor increment 4 has measured that interaction. Setting a
   gate before measuring it would be a prediction. A reviewer may hold that an ungated class should not
   ship at all.

---

## References

- Main specification (amended): `.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md` — §0, §0.1,
  §Open decisions 2 (amended, §14.14), §6.2, §7.3–7.4, §9.1–9.4, §Deferred rows (b)/(c)/(d)/(f).
- Increment 1 (amended): `.praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md` — §10.1.1
  (narrowed), §10.1.3, §10.2.1 (extended by B2/P1c), §10.2.2, §10.2.5–10.2.6, §10.3.1–10.3.3, §10.4,
  §10.5, §10.9 (superseded for volume).
- Increment 2 (amended): `.praxia/docs/specs/260902_plr-sema-ir-bytecode-increment.md` — §11.1.2,
  §11.1.3, §11.1.4, §11.3.1–11.3.3 (cache key gains a fifth component), §11.4.1.
- Increment 3: `.praxia/docs/specs/260903_plr-sema-real-programs-increment.md` — §12.1.2 (the
  `_constructor_state` precedent P1c is modelled on), §12.1.6 (the scaffolding-`CALL` convention §14.8
  reuses), §12.3.3 (L1's tail widen, which V4 attaches to), §12.13.
- Increment 4 (the document this was re-scoped out of):
  `.praxia/docs/specs/260903_plr-sema-families-cache-increment.md` — §13.2 (the stub pointing here),
  §13.7 (which carries HM-25 5 → 6 only), §13.13 Q2/Q3/Q6.
- Adversarial round 1 on increment 4, which produced this document:
  `.praxia/docs/audits/260903_plr-sema-families-cache-round1-challenger.md` (O1 the bridge does not
  match at the pin; O2 the `env` gate cannot reach a bridged guard; O3 `is_disabled` is a property;
  O4 the V0/V2 update order) and
  `.praxia/docs/audits/260903_plr-sema-families-cache-round1-defender.md` (all six CONCEDED; the
  re-scope recommendation and the ordered remediation list whose items 1–3 are §14.0, §14.5 and
  §14.6). **This document has had no adversarial round of its own.**
- PLR source at submodule pin `dd79c4c89`: `liquid_handling/liquid_handler.py` (`vols` coercion at
  `:968`, the multi-channel expansion at `:997-999`, the aspiration comprehension at `:1007-1028` with
  `resource=r` at `:1009`, `volume=v` at `:1010`, `tip=t` at `:1014` and the `zip` at `:1018-1027`,
  the `for op in aspirations:` at `:1031`, the tracking and `is_disabled` conjuncts at `:1032-1033`,
  the tracker calls at `:1034-1035`, the commit/rollback block at `:1058-1064`, the
  `BlowOutVolumeError` raises at `:1185`/`:1188`); `liquid_handling/standard.py:51-60` and `:63-67`
  (the two dataclasses whose class-level annotations B2 must admit); `resources/volume_tracker.py`
  (the tracking flag at `:17-22`, `no_volume_tracking` at `:25-30`, `__init__`'s fields at `:40-52`,
  `is_disabled` as a `@property` at `:54-56`, `set_volume` at `:66-72`, `remove_liquid` at `:88-99`
  with its guard and raise at `:91-94`, `add_liquid` at `:101-112` with its guard and raise at
  `:104-107`, `get_used_volume` at `:114-116`, `get_free_volume` at `:118-120`, `get_liquids`'s raise
  at `:135-136`, `commit`/`rollback` at `:140-151`); `resources/container.py:84-85` (the unannotated
  `self.tracker` write P1c must read); `resources/tip.py:27,45`.
- Analyzer source: `plr-sema/src/plr_sema/derive/receiver_state.py` (`_is_self_attr` at `:164-167`,
  `_annotated_attributes` at `:170-181` with the `ast.AnnAssign` test at `:177`, `_constructor_state`
  at `:523-563` walking `ast.Assign` at `:548` and `ast.AnnAssign` at `:551`, `compute_channel_bridge`
  at `:770-799` with the callee-sourced `scope_trail` at `:787` and the `derive_contract` call at
  `:777-779`); `plr-sema/src/plr_sema/check/ir.py:184-191,918-926`;
  `plr-sema/src/plr_sema/check/__init__.py:443-445,713`;
  `plr-sema/src/plr_sema/_hand_maintained.py:43,244-261,553-557,781-847,851-855`;
  `plr-sema/src/plr_sema/verdict.py:129-154`; `plr-sema/eval/oracle_common.py:690-739,983-989`;
  `plr-sema/eval/tip_mutants.py:69,127-140,167,170-224,238-247`.
- Artifacts: `plr-sema/data/derived_contracts.json:157965-157996,158102-158133`;
  `training/verify/data/plr_exception_taxonomy.json:2964-2972,2991-2999,3010-3056`;
  `training/verify/data/plr_preconditions.json:49766-49772,49863-49864`.
- Data: `outputs/plr-sema/oracle_replay_260903_rebaseline.json:2-29`;
  `outputs/plr-sema/tier2b_260903.json:1-45`.

---

## Remediation changelog (round 1)

This document *is* increment 4's round-1 remediation for O1, O2, O3 and O4 — it did not exist at the
time of the round and has had no adversarial round of its own. The four objections map to text as
follows.

| O-id | verdict | where it landed here |
|---|---|---|
| **O1** | CONCEDE (blocking) | §14.0's G1/G2/G3 table and §14.0.1's three normative sub-boxes (B1, B2, P1c), each with a measured expectation the fixer must publish; §14.4's bridge box rewritten to consume them; AC-14.1 and AC-14.2 |
| **O2** | CONCEDE (blocking, live soundness bug) | §14.0's G4, §14.0.2's survey-vs-derive tradeoff table and its **derive-side** decision, P10's normative box with its fail-closed `null`; §14.0's normative gate forbidding T26/T27 before T24 **and** T25; AC-14.3 |
| **O3** | CONCEDE | §14.6's conditional-guard rule **generalised** from "a zero-argument call" to "anything not recognised blocks `WILL_FAIL`", with `is_disabled`'s `@property` shape (`volume_tracker.py:54-56`) as the worked case; A-TRACKER-ENABLED downgraded from a soundness assumption to a precision note; AC-14.4; the disclosed consequence in §14.6's closing paragraph and §14.16's Q1 |
| **O4** | CONCEDE (soundness) | §14.5's V2 rewritten to thread pairs **sequentially in cells(op) order**, mirroring `liquid_handler.py:1031`; V0 made explicit that a repeated `Ref` is legal; V1's "pre-state" defined as the running state; the worked false-`SAFE` counterexample; AC-14.6 and the tier-2b two-channel/one-well fixture |
