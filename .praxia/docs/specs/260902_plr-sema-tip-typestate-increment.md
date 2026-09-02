---
title: "plr-sema increment 1 — per-channel tip typestate (deferred (a) and (c), narrowed to the tip-state guard family)"
description: "First post-corpus increment to the plr-sema pre-corpus specification. Narrows deferred item (a) (abstract domain) to a three-element per-channel tip typestate lattice and deferred item (c) (predicate language) to three atom productions over that lattice, so that the tip-loading / tip-requiring / tip-dropping method families produce real SAFE and WILL_FAIL findings instead of UNKNOWN. Every method family, every tracker class, every state field, every effect and every channel-arity default is DERIVED by AST inspection of PLR source and of the shipped contract table -- no hand-written method contract, and no hand-typed exception-class name (the two tip-state exception names come from plr_exception_taxonomy.json's own tip_state category). Adds one REASON_VOCABULARY member (7 -> 8 of 12), two check/graph.py mirror fields, one registry row (HM-24, the front end's six syntactic patterns), and no wire-format change. Gated by the oracle harness (#4879 corpus replay, #4881 mutants), not by a threshold."
status: draft
spec_version: 9
amends: 260901_plr-sema-pre-corpus-spec.md
task_id: 260902_sema-oracle-tipstate
date: '260902'
confidence: medium
sources: "Read this session, in full or in the cited ranges: .praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md (§0, §3, §6.2, §7.2-7.3, §9, Deferred, Open decisions, Fixer task decomposition); .praxia/docs/research/260901_plr-sema-research-a-d.md (Q3, R3); .praxia/docs/research/260901_plr-sema-research-c-e.md (Q2, Q5); .praxia/docs/plans/260902_plr-sema-oracle-harness.md; plr-sema/src/plr_sema/verdict.py; plr-sema/src/plr_sema/check/__init__.py; plr-sema/src/plr_sema/check/graph.py; plr-sema/src/plr_sema/derive/__init__.py; plr-sema/scripts/oracle_spike.py; plr-sema/eval/oracle_common.py; plr-sema/tests/fixtures/simple_transfer_graph.json; plr-sema/data/derived_contracts.json (LiquidHandler.{aspirate,pick_up_tips,drop_tips} and TipTracker.{get_tip,add_tip,remove_tip} entries, read verbatim); training/verify/data/plr_preconditions.json (LiquidHandler.{aspirate,pick_up_tips,drop_tips} records); training/verify/data/plr_exception_taxonomy.json (HasTipError/NoTipError entries); training/verify/failure_taxonomy.py:70-109; training/verify/dispatcher.py:37-41,159-161; training/floor_gen/exec_verify.py:186-210; praxis/backend/utils/plr_static_analysis/models.py:520-651; external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py (:162-164, :197, :455-504, :525-576, :645-726, :940-978, :1372-1390) and external/pylabrobot/pylabrobot/resources/tip_tracker.py:50-118, both at submodule pin dd79c4c89."
---

# Increment 1: per-channel tip typestate

> **This document amends `260901_plr-sema-pre-corpus-spec.md` by reference.** It adds §10 to that
> document's numbering and edits exactly four things in it: §3.3's `REASON_VOCABULARY` (one new
> member), §6.2's normative mirror field table (two new rows), §9.2's registry (one new row, HM-24),
> and the [§Deferred](#references) table's (a) and (c) rows (narrowed, not closed). Everything else
> in spec_version 8 — the verdict wire type, `join`, the telemetry schema, the fork-drift tests, the
> derivation closure mechanic, the differential harness, the budget and ratchet — is **unchanged**.
> No `schema_version` bump anywhere.

## 10.0 What this increment is, in one paragraph

`plr-sema` v1 is a **trivially sound** analyzer: `check/` constructs no `SAFE` or `WILL_FAIL`
`Finding` anywhere (`plr-sema/src/plr_sema/check/__init__.py:177-257` — seven constructors, every
one of them `verdict=Verdict.UNKNOWN`), and `join` maps the empty multiset to `UNKNOWN`
(`plr-sema/src/plr_sema/verdict.py:278-279`). Main spec §0 states this and states plainly that it is
a weak claim. This increment converts the **smallest** family of guards into real verdicts: the
**per-channel tip typestate** of a `LiquidHandler`'s `head` trackers. It is the smallest family that
is worth doing because it is the only one for which (i) PLR raises unconditionally rather than under
a runtime tracking flag, (ii) the abstract domain is finite and three-valued so no widening operator
is needed, and (iii) every fact the analyzer needs — which methods load a tip, which require one,
which drop one, which field holds the state, which exception names mean "tip state" — is derivable
by inspection, so main spec decision 2 ("no hand-written method contracts") survives intact.

**Deliverable of this increment, stated as the property that must become true:** a graph in which
`pick_up_tips` is applied twice to a statically-known channel set, with no intervening drop, produces
`Verdict.WILL_FAIL` on the second operation, with `category="precondition_state"` and
`plr_site=PlrSite("external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py", 535,
"LiquidHandler.pick_up_tips")`. Today it produces ten `UNKNOWN` findings.

| axis | v1 (spec_version 8) | this increment |
|---|---|---|
| abstract domain | none — deferred (a) | per-channel tip typestate, 3 elements, no widening operator |
| predicate language | none — every guard is `guard_predicate_unparsed` | 3 atom productions over the tip typestate; everything else still ½ |
| verdicts constructed by `check/` | `UNKNOWN` only | `UNKNOWN`, `SAFE` (per-guard), `WILL_FAIL` (per-guard) |
| `Verdict` / `Finding` / `AnalysisReport` / `join` | — | **unchanged** |
| `REASON_VOCABULARY` | 7 of cap 12 | 8 of cap 12 |
| registry rows | 22 live, cap 24 | 23 live, cap 24 |
| gate | unit tests | unit tests **plus** oracle #4879 replay and #4881 mutants |

---

## 10.1 The domain (deferred item (a), narrowed)

### 10.1.1 The lattice

For one channel of one `LiquidHandler` receiver, the abstract tip state is

```
TipState  ::=  NO_TIP  |  HAS_TIP  |  TOP
```

with the **information order** `NO_TIP ⊑ TOP`, `HAS_TIP ⊑ TOP`, `NO_TIP ⋢ HAS_TIP`, and the join

| ⊔ | NO_TIP | HAS_TIP | TOP |
|---|---|---|---|
| **NO_TIP** | NO_TIP | TOP | TOP |
| **HAS_TIP** | TOP | HAS_TIP | TOP |
| **TOP** | TOP | TOP | TOP |

`TOP` means "the analyzer knows nothing about this channel". The concretization is
`γ(NO_TIP) = {states where this channel's tracker holds no tip}`, `γ(HAS_TIP)` its complement within
the tracker's reachable states, `γ(TOP)` = everything. `⊑` is `γ`-inclusion; the join is the least
upper bound; the lattice has height 1 above its two atoms, so it is **finite-height and needs no
widening operator** — which is exactly research a-d's Q3 finding (`260901_plr-sema-research-a-d.md:246-254`:
"the whole `SUPPORTED_TOOLS` frontier is tip state on `self.head[channel]` … That is textbook
typestate", and `:256-266`'s cost table ranking typestate the primary candidate and octagons
explicitly not indicated). Main spec's Deferred (d) row already anticipates this: "If (a) resolves
to a finite-height typestate domain, (d) resolves to *nothing to design*."

**There is no ⊥ in this lattice.** Main spec §Open decisions 1 reserves ⊥ for the deferred-(a) state
type on the grounds that it prunes dead paths and is the branch-merge join's unit. This increment
has neither branches (§10.5) nor an emptiness-detecting transfer function, so introducing ⊥ now
would add an element nothing constructs and nothing consumes. `Verdict.UNREACHABLE` stays reserved
and unused; `Verdict.from_wire` (`plr-sema/src/plr_sema/verdict.py:96-113`) is untouched.

### 10.1.2 The two orders, kept apart (main spec §Open decisions 3)

`⊔` above is the **information order** (Kleene / Sagiv-Reps-Wilhelm: knowing less is higher). It
governs merging abstract states *before* any guard is evaluated. It is **not** the order `join`
implements. `plr_sema.verdict.join` (`plr-sema/src/plr_sema/verdict.py:220-285`) implements the
**obligation order** `SAFE ⊏ UNKNOWN ⊏ WILL_FAIL` over already-emitted `Finding`s, and this
increment does not change one line of it. The two live at different pipeline stages, exactly as
`verdict.py:232-246` says. Concretely, in this increment: `TipState.⊔` has call sites only inside the
new `check/tipstate.py` module's state merge; `join` has its existing call site at
`check/__init__.py:334` and nowhere else.

### 10.1.3 Channel identity

`LiquidHandler` holds one tracker per channel:
`self.head: Dict[int, TipTracker] = {}` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:162`),
populated at setup as `{c: TipTracker(thing=f"Channel {c}") for c in range(self.backend.num_channels)}`
(`:197`). **The channel count is a backend property and is therefore never statically known** — it is
`self.backend.num_channels`, resolved at `setup()` time. The abstract state consequently maps a
*channel index* to a `TipState` and carries a default for every index not in the map:

```
ChannelState  =  (default: TipState, exact: dict[int, TipState])
state(c)      =  exact.get(c, default)
```

`default` is `TOP` at graph entry (§10.5) and is only ever *lowered* to `NO_TIP`/`HAS_TIP` by a
transfer function that provably applies to every channel — which nothing in this increment does. In
practice `default` stays `TOP` for the whole walk and precision comes entirely from `exact`.

**How an operation's channel set is obtained.** PLR resolves it identically in all four
channel-taking `LiquidHandler` methods:

```python
use_channels = use_channels or self._default_use_channels or list(range(len(tip_spots)))
```

— `liquid_handler.py:501` (`pick_up_tips`), `:650` (`drop_tips`), `:958` (`aspirate`, over
`resources`), `:1152` (`dispense`, over `resources`). The analyzer mirrors that three-term disjunction
exactly, over `OperationNode.arguments` (a `dict[str, str]` of argument name → source expression,
`praxis/backend/utils/plr_static_analysis/models.py:536-538`):

1. **Explicit.** `arguments["use_channels"]` present and `ast.literal_eval`s to a list of `int` →
   `channels = that list`, exact.
2. **Instance default.** If any operation anywhere in the graph, on this receiver variable, has a
   `method_name` in the derived **channel-default-disabler set** (§10.2.3, P3b) → `channels = ⊤` for
   this and every operation on that receiver, permanently. (`self._default_use_channels` is written
   only at `liquid_handler.py:1385` and `:1390`, both inside the `use_channels` async context
   manager; the analyzer cannot see whether a `with` block is active, so a single occurrence of the
   writer method poisons the receiver.)
3. **Arity default.** Else, if the method has a derived channel-default parameter `p` (§10.2.3, P3a)
   and `arguments[p]` `ast.literal_eval`s to a list of length `n` → `channels = [0 … n-1]`, exact.
4. **Otherwise `channels = ⊤`** — the operation's channel set is unknown.

`channels = ⊤` is not "no channels": it is "possibly any channel", and it forces the widening in
§10.5. Rule 1 is tried before rule 3 because PLR's own `or` chain does (`:501`), and rule 2 sits
between them for the same reason.

**Measured against the shipped fixtures, honestly.** The committed four-operation fixture
(`plr-sema/tests/fixtures/simple_transfer_graph.json:13-101`) carries `arguments` of
`{"resource": "tips"}`, `{"resource": "source[\"A1\"]", "volume": "100"}`, … — no `use_channels`, and
no key matching any PLR channel-default parameter (`tip_spots`/`resources`). **Every operation in
that fixture therefore falls to rule 4, and every verdict in it stays `UNKNOWN` under this
increment.** This contradicts the natural expectation (and the dispatch brief's suggested acceptance
criterion) that "the four-op fixture flips specific ops to specific verdicts"; it does not, and
AC-10.4 pins that it does not, rather than pretending otherwise. New fixtures are required
(§10.8, AC-10.1–10.3). The same is true of the oracle harness's tier-1 adapter, for a different and
more interesting reason — see §10.12, Q3.

### 10.1.4 The abstract state

```
AbstractState = dict[receiver_variable: str, ChannelState]
```

State is **per `OperationNode.receiver_variable`** (`plr-sema/src/plr_sema/check/graph.py:117`), not
per `receiver_type`: two `LiquidHandler`s in one protocol are two independent states. Any receiver
variable whose `receiver_type` is not a class carrying a derived channel-tracker attribute (§10.2.1)
never gets an entry, and every operation on it behaves exactly as it does today — `UNKNOWN`,
unchanged. That is the whole of the "other receiver types" answer: they are not touched, not
special-cased.

---

## 10.2 The derived inputs (four build-time passes) — nothing here is hand-typed

Everything the evaluator needs is computed at build time by `plr_sema.derive` and shipped in
`plr-sema/data/derived_contracts.json`. `check/` remains stdlib-only, imports no `pylabrobot`, and
performs no AST work — main spec §6.2's packaging fact is untouched.

The existing derivation (`plr-sema/src/plr_sema/derive/__init__.py:446-492`) already gives us guards
with polarity (`InlinedGuard.kind`, `:406-432`), the raising class (`InlinedGuard.raises`), the
defining site, and depth. It throws away one field that this increment needs:
`SurveyRecord.dropped_calls` (`derive/__init__.py:151-160`) — the receiver-qualified call expressions
the survey drops for every non-`self.<name>` attribute receiver. `derive_contract` never reads it.

### 10.2.1 P1 — receiver-attribute typing (research c-e's rule R3)

A stdlib-`ast` pass over PLR source (the same tree `scan_dropped_receiver_calls` already walks,
`derive/__init__.py:685-720`) building, per class:

- **P1a `annotated_attributes`**: every `self.<name>: <annotation>` `ast.AnnAssign` in the class body
  or its `__init__`, with the annotation unwrapped through `Dict[K,V] → V`, `List[T] → T`,
  `Optional[T] → T` to a bare class name. For `LiquidHandler` this yields `head → TipTracker` from
  `liquid_handler.py:162`.
- **P1b `attribute_writers`**: for every `self.<name> = …` `ast.Assign`, the qualname of the
  enclosing method. For `_default_use_channels` this yields exactly one method (`liquid_handler.py:1385`,
  `:1390`).

This is precisely rule R3 of research c-e's ranked recommendation
(`260901_plr-sema-research-c-e.md:152-160`), and that report already measured the exact case this
increment depends on: "`self.head[channel].get_tip` resolves under R3 to `TipTracker` with
`owns_method=True`" (`:175-176`). **DERIVED.**

### 10.2.2 P2 — the typestate anchor (which field, and which way round)

For a candidate tracker class `C` (any class appearing as a value of P1a), find every **property**
of `C` whose body is a single `return self.<F> <is|is not> None`. `TipTracker` has exactly one:

```python
@property
def has_tip(self) -> bool:
    return self._pending_tip is not None      # tip_tracker.py:52-55
```

This one pattern yields three facts at once and is the reason the design needs no hand-typed
polarity table:

- the **boolean view** attribute name: `has_tip`
- the **state field**: `_pending_tip`
- the **polarity**: `has_tip` is true ⟺ the field is not `None` ⟺ `HAS_TIP`

**Fail-closed rule (error-proofing).** If `C` has zero such properties, or more than one, P2 emits
nothing for `C`, the whole tip-typestate feature is disabled for every receiver whose channel
attribute types to `C`, and every verdict reverts to today's `UNKNOWN`. A silent partial derivation
is forbidden; the gap ledger records `tipstate_anchor: "absent"|"ambiguous"|"<field>"` per candidate
class so the condition is visible in the artifact rather than inferred from an absence of verdicts.

**The second state field, and why merging it is sound here.** `C` has a *second* field that tip-state
guards read: `TipTracker.get_tip` guards on `self._tip is None` (`tip_tracker.py:64-65`), the
committed field, while `add_tip`/`remove_tip` guard on and write `self._pending_tip`
(`:91-93`, `:104-106`). They can disagree mid-operation — `remove_tip(commit=False)` is the default
(`:100`). They cannot disagree **at an operation boundary**, which is the only place this analyzer
looks: every `LiquidHandler` tip operation commits or rolls back every touched head tracker before
returning (`liquid_handler.py:570-573` for `pick_up_tips`, `:716-723` for `drop_tips`). P2 therefore
records `state_fields = ["_tip", "_pending_tip"]` — every field named in a `NullCheck` atom by any
guard of `C` that raises a `tip_state` exception — and the evaluator treats all of them as views of
the one abstract cell. This is assumption **A-COMMIT** (§10.7) and it is the one place in this
increment where an abstraction merges two concrete locations.

### 10.2.3 P3 — the channel-arity idiom and its disablers

- **P3a `channel_default_param`**: for each method of a class, match the assignment idiom
  `<p> = <p> or self.<x> or list(range(len(<q>)))` (`ast.Assign` whose value is a two-level
  `BoolOp(Or)` ending in `Call(list, [Call(range, [Call(len, [Name q])])])`). Record `method → q`.
  Expected selection over `LiquidHandler`, from the four sites read this session:
  `pick_up_tips → tip_spots` (`:501`), `drop_tips → tip_spots` (`:650`), `aspirate → resources`
  (`:958`), `dispense → resources` (`:1152`). The fixer must publish the *measured* set, not this one.
- **P3b `channel_default_disablers`**: from P1b, the set of methods that write the `self.<x>` middle
  term of any P3a match — for `LiquidHandler`, `{use_channels}` (the two writes at `:1385`/`:1390`
  live in the `use_channels` async context manager, whose contract key
  `LiquidHandler.use_channels` is present in the shipped table).

A method with no P3a match — `LiquidHandler.transfer` is the important one, since it computes its own
channel usage internally (see `training/floor_gen/exec_verify.py:188-193`, which documents that
`transfer` "internally does ONE `aspirate(resources=[source])` then loops `dispense(…, use_channels=[0])`
serially") — gets no channel-set derivation and is handled by rule 4 of §10.1.3: `channels = ⊤`.
That is correct and deliberately imprecise; making `transfer` precise requires modelling a method
body, which is not this increment.

### 10.2.4 P4 — effects

A guard tells you a *precondition*; it never tells you a *transition*. For each method `m` of an
anchored class `C`, classify `m`'s writes to any field in `state_fields`:

- `self.<F> = None` → `m` establishes `NO_TIP`
- `self.<F> = <expr>` where `<expr>` is not the literal `None` → `m` establishes `HAS_TIP`
- writes to no state field, or writes of both kinds → no effect (the method is transparent to this
  abstraction)

Measured over `TipTracker`: `add_tip` writes `self._pending_tip = tip` (`tip_tracker.py:93`) →
`HAS_TIP`; `remove_tip` writes `self._pending_tip = None` (`:106`) → `NO_TIP`; `commit` writes
`self._tip = self._pending_tip` (`:113`) → both-kinds-unknown → no effect, which is right, since
under A-COMMIT a commit is a no-op on the abstraction. **DERIVED.**

### 10.2.5 The channel bridge, and the shape of the payload addition

For each contract entry `K` on receiver class `R`, and each `dropped_calls` expression reached
anywhere in `K`'s closure, match the **channel-receiver shape**

```
self.<attr>[<name>].<method>            e.g.  self.head[channel].get_tip
```

where `R`'s P1a map sends `<attr>` to a class `C` with a P2 anchor, and `f"{C}.{method}"` is a key in
the contract table. When it matches, attach every guard of `C.<method>` to `K` as a **channel guard**
carrying the originating expression. This is deferred item (e), solved for exactly one receiver
shape, by exactly the annotation mechanism research c-e ranked first and measured
(`260901_plr-sema-research-c-e.md:149-176`) — not by type inference in general.

`derived_contracts.json` gains two additive blocks; `schema_version` stays `1` because `check/`
reads both through `.get()` with empty defaults, so a stale table degrades to today's all-`UNKNOWN`
behaviour rather than raising (pinned by AC-10.7):

```jsonc
{ "schema_version": 1,
  "stamp": { /* unchanged */ },
  "receiver_state": {                                    // NEW — P1..P4 output, one entry per anchored receiver class
    "LiquidHandler": {
      "channel_attr": "head",
      "tracker_class": "TipTracker",
      "bool_view":   {"attr": "has_tip", "field": "_pending_tip", "true_when": "not_none"},
      "state_fields": ["_tip", "_pending_tip"],
      "effects":     {"add_tip": "has_tip", "remove_tip": "no_tip"},
      "channel_default_param":     {"pick_up_tips": "tip_spots", "drop_tips": "tip_spots",
                                    "aspirate": "resources", "dispense": "resources"},
      "channel_default_disablers": ["use_channels"],
      "tip_state_exceptions":      ["HasTipError", "NoTipError"]
    }},
  "contracts": {
    "LiquidHandler.aspirate": {
      "gaps": [], "guards": [ /* unchanged, 9 entries */ ],
      "channel_guards": [                                // NEW
        {"condition": "self._tip is None", "kind": "raise_guard", "raises": "NoTipError",
         "free_vars": ["self"], "scope_trail": ["if self._tip is None"], "depth": 1,
         "site": {"file": "external/pylabrobot/pylabrobot/resources/tip_tracker.py",
                  "lineno": 65, "qualname": "TipTracker.get_tip"},
         "via": "self.head[channel].get_tip"}
      ]}}}
```

`channel_guards` is kept **separate from `guards`** so that the existing per-guard
`guard_predicate_unparsed` emission (`check/__init__.py:219-227`) and every existing count-based
acceptance criterion are untouched by construction.

`tip_state_exceptions` is **not hand-typed**: it is the set of class names whose entry in
`training/verify/data/plr_exception_taxonomy.json` carries `"category": "tip_state"` — which today is
exactly `{HasTipError, NoTipError}` (verified this session: `HasTipError` at that artifact's
`lineno: 16` entry, `NoTipError` at its `lineno: 20` entry, both
`"module": "pylabrobot.resources.errors"`, both `"category": "tip_state"`). `plr_sema.derive` already
takes a required `--taxonomy-json PATH` in the sibling differential harness (main spec T10), so this
is an existing input, not a new dependency, and no HM row is needed for it.

### 10.2.6 What the rules actually select — measured against the shipped table

The whole point of grounding the rules in `plr-sema/data/derived_contracts.json` rather than in what
PLR "should" do is that the shipped table is **much emptier of tip state than it looks**. Measured
this session over the whole 4,770-entry table:

| fact | measurement |
|---|---|
| guards with `"raises": "HasTipError"` | **6** — five are the *same* guard (`LiquidHandler.pick_up_tips`'s own `self.head[channel].has_tip` at `liquid_handler.py:535`) inlined at depth 0 into `pick_up_tips` and at depth 1 into four callers; the sixth is `TipTracker.add_tip` at `tip_tracker.py:92` |
| guards with `"raises": "NoTipError"` | **2**, both at depth 0 inside `TipTracker`'s own contracts: `TipTracker.get_tip` (`tip_tracker.py:65`) and `TipTracker.remove_tip` (`tip_tracker.py:105`) |
| `LiquidHandler.aspirate`'s guard set | **9 guards, 0 gaps, and not one tip-state guard.** Its tip requirement lives entirely in `tips = [self.head[channel].get_tip() for channel in use_channels]` (`liquid_handler.py:974`), a dropped cross-class call |
| `LiquidHandler.drop_tips`'s guard set | **9 guards, 0 gaps, no tip-state guard.** Its volume guard `tip.tracker.get_used_volume() > 0 and (not allow_nonzero_volume)` is at depth 0; its tip requirement is `self.head[channel].get_tip()` at `liquid_handler.py:655` and its effect is `self.head[channel].remove_tip()` at `:684`, both dropped |
| `LiquidHandler.pick_up_tips`'s guard set | **10 guards, 0 gaps**, of which exactly one is tip state: the depth-0 `raise_guard` `self.head[channel].has_tip` / `HasTipError` / `liquid_handler.py:535` |

**Consequence, stated as bluntly as it deserves: without the §10.2.5 bridge, the tip-*requiring*
family is not derivable at all, and this increment would be able to say nothing about `aspirate`,
`dispense`, `drop_tips` or `transfer`.** A design that identified families only by scanning
`InlinedGuard.raises` in `contracts[K]["guards"]` — the obvious reading of the dispatch brief's
"tip-requiring if it raises `NoTipError`" — selects the empty set for every `LiquidHandler` method.
The bridge is not an optimisation; it is load-bearing.

With the bridge, the families are (this is the normative derivation, and the listed selections are
the expected result the fixer must reproduce and publish, not an input):

- **tip-loading(K)** ⟺ `K`'s guards ∪ channel_guards contain a `raise_guard` raising a `tip_state`
  exception whose atom demands `NO_TIP`, **or** `K` bridges to a `C` method whose P4 effect is
  `HAS_TIP`. Expected: `pick_up_tips` (both ways: its own `:535` guard *and*
  `self.head[channel].add_tip` at `:538`).
- **tip-requiring(K)** ⟺ `K`'s guards ∪ channel_guards contain a guard demanding `HAS_TIP`.
  Expected: `aspirate`, `dispense`, `drop_tips`, and — through `delegates_to`, since `self.aspirate(…)`
  *is* a `self.<name>` call and therefore a resolved delegate rather than a dropped one — `transfer`.
- **tip-dropping(K)** ⟺ `K` bridges to a `C` method whose P4 effect is `NO_TIP`. Expected:
  `drop_tips` (`self.head[channel].remove_tip` at `:684`), and by delegation `discard_tips`,
  `return_tips`.

Note the two families are not disjoint and must not be forced to be: `drop_tips` is both
tip-requiring and tip-dropping, which is exactly right.

**Flagged as looking wrong, for the fixer to check rather than assume:** `LiquidHandler.move_tips`,
`consolidate_tip_inventory` and `probe_tip_presence_via_pickup` all carry the `:535` `HasTipError`
guard at depth 1 (verified — the guard appears in their contract entries), so the rule classifies
them tip-loading. For `move_tips` and `consolidate_tip_inventory` that is a *sequence* of pickups
and drops whose net effect on any given channel is not `HAS_TIP`. The rule as written would apply a
`HAS_TIP` effect to them, which is unsound. **Normative fix, and it is the reason effects are P4's
job and not the guard set's:** the effect of `K` on a channel is taken **only** from P4 via the
bridge (`self.<channel_attr>[…].<m>` reached at **depth 0** in `K`'s own body), never from a
guard's polarity, and **never at depth > 0**. A method that reaches a tracker mutator only through a
delegate gets *no* effect and instead widens the receiver to `TOP` (§10.4, rule E4). `move_tips`
and friends therefore widen rather than mis-transition.

---

## 10.3 The evaluator (deferred item (c), narrowed)

### 10.3.1 Which atoms are interpreted

A guard is **tip-state-interpretable** for operation `op` iff **all four** hold:

1. `guard.kind` is `"raise_guard"` or `"assert"` (both are in the table; polarity is read from
   `kind` exactly as `derive/__init__.py:406-432` specifies and is never folded into the condition
   text);
2. `guard.condition` is not `None` and parses under the atom grammar below to a single atom (no
   `and`/`or`/`not` — a compound condition is **not** interpreted in this increment; it falls through
   to `guard_predicate_unparsed`, unchanged);
3. the atom's path is **channel-scoped**: either it begins `self.<channel_attr>[<name>]` (an own
   guard, e.g. `pick_up_tips`'s `self.head[channel].has_tip`) or the guard came from
   `channel_guards`, whose `via` expression supplies the channel scope;
4. `op`'s channel set is exact (§10.1.3 rules 1 or 3) **and** every channel in it has a state that is
   not `TOP`.

The grammar is three productions, a strict subset of the five research c-e proposes
(`260901_plr-sema-research-c-e.md:454-464`, where they appear as `NullCheck` and attribute
truthiness):

```
Atom ::= BoolView(Path)                    #  <path>.<bool_view.attr>       e.g. self.head[c].has_tip
       | NullCheck(Path, is_none=True)     #  <path>.<state_field> is None
       | NullCheck(Path, is_none=False)    #  <path>.<state_field> is not None
```

`<bool_view.attr>` and `<state_field>` are the P2-derived names, never literals in our source.
**Everything else stays Kleene ½**, including every numeric `Cmp` — main spec §Open decisions 2
resolved that numeric atoms are uninterpreted "through v1 and the first post-corpus increment", and
this *is* that increment, so `drop_tips`'s
`tip.tracker.get_used_volume() > 0 and (not allow_nonzero_volume)` (depth 0, verified in the shipped
table) remains `guard_predicate_unparsed`. That is unchanged, deliberate, and re-affirmed here.

**`free_vars` must not be used to identify the receiver.** The shipped table proves why: the
`TipTracker.get_tip` guard carries `free_vars: ["self"]` while `LiquidHandler.pick_up_tips`'s `:535`
guard carries `free_vars: []` despite its condition mentioning `self.head[channel]`. Research c-e
says the same from the other end (`260901_plr-sema-research-c-e.md:477-483`: "Do not trust
`mentions_params` as the free-variable set"). The path is recomputed from the parsed condition, and
`free_vars` is at most a cross-check.

### 10.3.2 Atom truth under a state

Let `s` = the meet of the states of `op`'s channels — i.e. `NO_TIP` if every channel is `NO_TIP`,
`HAS_TIP` if every channel is `HAS_TIP`, `TOP` otherwise. (A *mixed* channel set is `TOP`: a guard
inside `for channel in use_channels` fires if it fires for any one channel, so a mixed set can
neither be entailed nor refuted. That is the sound reading and it is why the meet, not the join, is
used here.)

| atom | `s = NO_TIP` | `s = HAS_TIP` | `s = TOP` |
|---|---|---|---|
| `BoolView(p)` | **F** | **T** | ½ |
| `NullCheck(p, is_none=True)` | **T** | **F** | ½ |
| `NullCheck(p, is_none=False)` | **F** | **T** | ½ |

### 10.3.3 From atom truth to a `Finding`

Guard polarity, per `derive/__init__.py:412-417`: a `raise_guard` fires when its condition is TRUE;
an `assert` fires when its condition is FALSE. Let `fires ∈ {T, F, ½}` be the atom's truth composed
with that polarity.

| `fires` | `Finding` emitted for this guard |
|---|---|
| **T** | `Verdict.WILL_FAIL`, `category="precondition_state"`, `reason=""`, `plr_site=guard.site`, `evidence=(site of the effect that established the state,)`, `detail=guard.condition` |
| **F** | `Verdict.SAFE`, `category=""`, `reason=""`, `plr_site=guard.site`, `detail=guard.condition` |
| **½** | `Verdict.UNKNOWN`, `reason="channel_state_unknown"` (**new**, §10.10), `plr_site=guard.site`, `detail=guard.condition` |

`precondition_state` is an existing member of the FROZEN `FAILURE_CATEGORIES`
(`training/verify/failure_taxonomy.py:82-89`, member at `:86`); nothing about that set changes, and
HM-5 stays FROZEN at 6.

**Exactly one `Finding` per guard, and grouping by `operation_id` remains forbidden.** The emission
above replaces, one-for-one, the `guard_predicate_unparsed` finding that
`check/__init__.py:260-281` emits today for the same guard. Two findings sharing an `operation_id`
are still two *independent* obligations — guard A and guard B — which correctly conjoin under `join`'s
obligation order. Research a-d's R3 (`260901_plr-sema-research-a-d.md:520-526`: group by
`operation_id` and Kleene-join within the group) **must not be implemented**, and this increment
makes the reason sharper rather than weaker: `aspirate` under a `NO_TIP` state now emits one
`WILL_FAIL` (the bridged `NoTipError` guard) alongside eight `UNKNOWN`s and possibly a `SAFE`.
Kleene-joining within the operation would collapse `WILL_FAIL ⊔ SAFE` to `UNKNOWN` and **erase the
one true thing the analyzer now knows** — unsound in the `SAFE` direction, and no longer merely
theoretically so. `verdict.py:248-261` already carries this warning; it stays.

**Operation-level `SAFE` is unreachable in practice, and that is not a defect.** Every
`LiquidHandler` method carries 9–17 guards, nearly all of which stay ½ (`_check_args`'s
`len(missing) > 0`, `strictness == Strictness.STRICT`, `error is not None`, …). `join`'s third row
means one ½ makes the operation `UNKNOWN`. So this increment produces **operation-level `WILL_FAIL`
and per-`Finding` `SAFE`**, and the acceptance criteria are written against the finding, not the
operation verdict, wherever `SAFE` is concerned (AC-10.2). Any AC that asserted an operation-level
`SAFE` would be unsatisfiable, and writing one would be the "acceptance criteria satisfiable without
the property being true" failure in its mirror form — a criterion unsatisfiable even when the
property *is* true.

---

## 10.4 Transfer functions

For operation `op` on receiver `v`, with `channels(op)` from §10.1.3 and the pre-state `σ`:

- **E1 (evaluate first, then transition).** Guards are evaluated against `σ` — the state *before*
  `op` — for every guard of `op`. Only then is the post-state computed. A method that is both
  tip-requiring and tip-dropping (`drop_tips`) is therefore checked against the incoming state and
  updates from it, in that order.
- **E2 (exact effect).** If `op`'s method has a depth-0 bridge to a `C` method with P4 effect `e ∈
  {HAS_TIP, NO_TIP}` and `channels(op)` is exact, then for each `c ∈ channels(op)`:
  `σ'.exact[c] = e`. Channels outside the set are unchanged.
- **E3 (no effect).** If the method has no depth-0 tracker-mutating bridge, `σ' = σ`. This covers
  `aspirate`, `dispense`, `transfer` and every non-tip method: they read tip state and do not change
  it.
- **E4 (widen).** If the method *does* have a tracker-mutating bridge but `channels(op)` is `⊤`, or
  the bridge is only reachable at depth > 0 (§10.2.6's `move_tips` case), then
  `σ' = (default=TOP, exact={})` for `v` — the whole receiver is widened. Also applies whenever a
  channel-default disabler method (§10.2.3, P3b) appears anywhere in the graph on `v`.
- **E5 (unknown receiver).** `receiver_type is None`, or a type with no P2 anchor: no state, no
  evaluation, findings unchanged from today.

E1's ordering assumes the operation *completes* — see A-COMPLETES in §10.7.

---

## 10.5 The graph walk, v1

`check/__init__.py:329-330` iterates `graph.operations`. This increment keeps that shape and adds a
single left-to-right state fold. Three rules, and no fixpoint:

1. **Order.** The mirror gains `execution_order` (§10.10). Operations are visited in
   `execution_order` when it is non-empty and is a permutation of the operation ids; otherwise in
   `operations` order, which the upstream model documents as execution order
   (`praxis/backend/utils/plr_static_analysis/models.py:623-625`). If `execution_order` is non-empty
   and is *not* such a permutation, the walk widens every receiver to `TOP` immediately and emits
   nothing but today's findings — a disagreement between two views of the same fact is a reason to
   know less, never to pick one.
2. **Loops widen.** Any operation with `foreach_source is not None` or non-empty `foreach_body`
   (`check/graph.py:120-121`) widens its receiver to `TOP` **before** its own guards are evaluated,
   and the receiver stays `TOP` for the remainder of the walk. There is no trip-count reasoning, no
   loop-body re-entry, and no fixpoint iteration. The existing `loop_bounds_unknown` finding
   (`check/__init__.py:309-310`) is unchanged and still emitted.
3. **Dynamic arguments widen.** Any operation with non-empty `depends_on_params`
   (`check/graph.py:119`) widens its receiver to `TOP` before evaluation, same permanence. In the
   committed fixture that is `op_1` and `op_4` (`depends_on_params: ["tips"]`).

**Why this is sound and not merely convenient (Rival & Yi §1.3.5's over-approximation discipline).**
Widening a channel to `TOP` can only move an atom from `T`/`F` to `½`, and `½` yields
`Verdict.UNKNOWN`, which asserts nothing. So every widening can only *destroy* a verdict, never
create a wrong one: it can turn a would-be `SAFE` or `WILL_FAIL` into `UNKNOWN`, and it can never
turn an `UNKNOWN` into either. The absence of a fixpoint is therefore a precision decision, not a
soundness one. It also means the increment cannot regress the oracle's zero-unsound-rows gate by
being *too coarse* — only by being too fine.

Branches are not handled at all: `condition_expr`/`true_branch`/`false_branch` are still not
mirrored (main spec §6.2's B5 note), so the walk never sees a branch. If a future extractor emits
branch nodes, they will arrive as operations with unrecognised shape; AC-10.6 pins that an operation
carrying a non-empty `condition_expr` in the raw payload widens rather than being silently
straight-lined. This is the one place where a *future* upstream change could otherwise turn this
increment unsound, so it is fenced now rather than later.

---

## 10.6 The soundness argument

### 10.6.1 The chain behind a `WILL_FAIL`

For the double-`pick_up_tips` case, the claim "operation `op_1` must fail" rests on exactly these
links, each one checkable:

1. **Graph.** `op_0` and `op_1` are on the same `receiver_variable`, in this order, neither in a
   loop, neither with dynamic arguments (`check/graph.py:115-121`).
2. **Channel set.** Both carry `use_channels` (or a `tip_spots` list) that `ast.literal_eval`s to
   `[0]`, so `channels = {0}` exactly, by rules 1/3 of §10.1.3, which mirror
   `liquid_handler.py:501`.
3. **Effect.** `op_0`'s method bridges at depth 0 to `TipTracker.add_tip` (from
   `LiquidHandler.pick_up_tips`'s `dropped_calls` entry `self.head[channel].add_tip`, verified in
   `training/verify/data/plr_preconditions.json`), whose P4 effect is `HAS_TIP`
   (`tip_tracker.py:93`). So `σ.exact[0] = HAS_TIP` after `op_0`.
4. **Guard.** `op_1`'s contract carries the depth-0 guard
   `{"condition": "self.head[channel].has_tip", "kind": "raise_guard", "raises": "HasTipError",
   "site": {"file": ".../liquid_handler.py", "lineno": 535}}` — verified verbatim in
   `plr-sema/data/derived_contracts.json`'s `LiquidHandler.pick_up_tips` entry.
5. **Atom.** `self.head[channel].has_tip` parses as `BoolView` with a channel-scoped path, using the
   P2-derived `bool_view.attr = "has_tip"` (`tip_tracker.py:53-55`).
6. **Evaluation.** `BoolView` under `HAS_TIP` is `T` (§10.3.2); `kind = "raise_guard"` fires on `T`;
   so `fires = T` ⟹ `WILL_FAIL` with `category="precondition_state"`.
7. **Runtime correspondence.** PLR executes exactly this: `if self.head[channel].has_tip: raise
   HasTipError("Channel has tip")` (`liquid_handler.py:534-535`), unconditionally — not inside any
   `does_tip_tracking()` test.

### 10.6.2 The chain behind a `SAFE` finding

Same links 1–3, with `op_1` an `aspirate` on `channels = {0}`; link 4 becomes the *bridged* guard
`{"condition": "self._tip is None", "kind": "raise_guard", "raises": "NoTipError", "site":
{".../tip_tracker.py", 65, "TipTracker.get_tip"}}` reached via `self.head[channel].get_tip`
(`liquid_handler.py:974`); link 5 parses it as `NullCheck(is_none=True)` on the P2 state field; link
6 gives `F` under `HAS_TIP` ⟹ that guard is `SAFE`. The operation's aggregate verdict stays
`UNKNOWN` because its other eight guards are ½ — which is the correct, honest answer.

### 10.6.3 The assumptions, named

Every one of these is an assumption the analyzer cannot discharge from the graph. They are listed so
a reviewer can attack them; none of them is buried in code.

| id | assumption | why it is needed | what breaks if it is false |
|---|---|---|---|
| **A-SINGLE** | one `receiver_variable` denotes one `LiquidHandler` instance for the whole graph, and no other name aliases it | state is keyed on the variable name (§10.1.4) | a second alias mutating the head trackers desynchronises `σ`; both a false `SAFE` and a false `WILL_FAIL` become possible. Mitigation: no `plr_static_analysis` graph today emits two names for one instance, and `is_grounded` (`check/graph.py:181-186`) exists to detect ungrounded references when a reason for it lands |
| **A-COMPLETES** | each operation preceding the one being checked completed without raising | E1/E2's post-state is the state *after a successful* call | it is the same assumption the oracle's own comparison already makes: `oracle_common.py:148-163` marks every operation after the failing index `not_reached` and imposes no constraint there. A `WILL_FAIL` at index `i` is a claim about the trace *reaching* `i` |
| **A-COMMIT** | at operation boundaries, `_tip` and `_pending_tip` agree | P2 merges two concrete fields into one abstract cell (§10.2.2) | verified true for the two methods that matter: every touched head tracker is committed or rolled back before return (`liquid_handler.py:570-573`, `:716-723`). A future PLR method that mutates a head tracker without committing breaks it, and Fork D's pin test is the tripwire |
| **A-ENABLED** | the head trackers are not `disable()`d | `TipTracker.add_tip`/`remove_tip` raise `RuntimeError` when disabled (`tip_tracker.py:89-90`, `:102-103`) | **largely self-discharging**: under A-COMPLETES, if `op_0`'s `add_tip` had raised `RuntimeError`, `op_0` would not have completed, so a completed `pick_up_tips` implies its head tracker was enabled. The residual is a `disable()` call *between* two operations, which no graph emits |

**The brief's premise about `does_tip_tracking()` is, for this family, false — and that is good news
worth stating.** Main spec §Open decisions 2 correctly notes that PLR's *volume* guards are gated by
a process-global tracking flag, and the oracle plan runs with `set_tip_tracking(True)`. But the head
trackers are **not** so gated. At `liquid_handler.py:536-538`, only the *tip-spot* tracker call is
inside `if does_tip_tracking() and not op.resource.tracker.is_disabled:`; the head-tracker call
`self.head[channel].add_tip(op.tip, origin=op.resource, commit=False)` at `:538` sits outside it. The
same asymmetry holds in `drop_tips` (`:678-684`: the guarded block covers `op.resource.tracker.add_tip`,
while `self.head[channel].remove_tip()` at `:684` is unguarded), and the `HasTipError` raise at
`:534-535` is unguarded too. So a `WILL_FAIL` from this increment is a claim about PLR **regardless
of the tip-tracking flag**, and no `SoundnessScope` environment record is required for it — unlike
the volume family, which does need one. This is the strongest single reason to pick tip state as the
first increment rather than volume.

---

## 10.7 Acceptance criteria

Written so that none can be satisfied while the property is false. Each names the fixture, the
operation, and the exact site, so a stubbed evaluator that returns a constant fails.

- **AC-10.1 (`WILL_FAIL` on a repeated pickup).** Fixture `double_pickup_graph.json`: two
  `pick_up_tips` operations on receiver `lh` (`receiver_type: "LiquidHandler"`), each with
  `arguments["use_channels"] == "[0]"`, empty `depends_on_params`, no loop.
  `check_graph(...)` yields a report in which `op_1` has **exactly one** `Finding` with
  `verdict is Verdict.WILL_FAIL`, and that finding has `category == "precondition_state"` and
  `plr_site == PlrSite("external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py", 535,
  "LiquidHandler.pick_up_tips")`. The per-operation `join` of `op_1`'s findings is
  `Verdict.WILL_FAIL`; the per-operation join of `op_0`'s is `Verdict.UNKNOWN`.
- **AC-10.2 (`SAFE` finding after a pickup, and no operation-level `SAFE`).** Fixture
  `pickup_then_aspirate_graph.json`: `pick_up_tips(use_channels=[0])` then
  `aspirate(use_channels=[0])`. `op_1` has **exactly one** `Finding` with
  `verdict is Verdict.SAFE`, whose `plr_site` is
  `PlrSite("external/pylabrobot/pylabrobot/resources/tip_tracker.py", 65, "TipTracker.get_tip")`.
  The per-operation join of `op_1` is `Verdict.UNKNOWN` (its other guards are ½). No `Finding` in
  the whole report has `verdict is Verdict.WILL_FAIL`.
- **AC-10.3 (`WILL_FAIL` sited in the tip tracker).** Fixture `aspirate_after_drop_graph.json`:
  `pick_up_tips(use_channels=[0])`, `drop_tips(use_channels=[0])`, `aspirate(use_channels=[0])`.
  `op_2` has exactly one `WILL_FAIL` finding, `category == "precondition_state"`, `plr_site ==
  PlrSite(".../resources/tip_tracker.py", 65, "TipTracker.get_tip")`, and `report.verdict is
  Verdict.WILL_FAIL`. (This is the criterion that cannot pass without the §10.2.5 bridge, the P4
  effect derivation, *and* the channel-set derivation all being right — it is the increment's single
  best end-to-end gate.)
- **AC-10.4 (the shipped fixture is unchanged in verdict, changed in one reason).** Against
  `plr-sema/tests/fixtures/simple_transfer_graph.json`, `report.verdict is Verdict.UNKNOWN` and
  every `Finding.verdict is Verdict.UNKNOWN`, exactly as today; and the finding count per operation
  is unchanged from the pre-increment run. Additionally, no finding in that report carries
  `reason == "channel_state_unknown"` (its operations widen on `depends_on_params` before any guard
  is evaluated, so the new reason is not reached).
- **AC-10.5 (widening erases, never inverts).** Take `double_pickup_graph.json` and produce three
  variants: (a) `op_1.foreach_source = "wells"`, (b) `op_1.depends_on_params = ["n"]`, (c)
  `op_0.arguments["use_channels"] = "channels"` (a bare name, not a literal). In all three, `op_1`
  has **zero** findings with `verdict is Verdict.WILL_FAIL` and zero with `verdict is Verdict.SAFE`,
  and `report.verdict is Verdict.UNKNOWN`.
- **AC-10.6 (unknown shapes widen).** A graph payload whose operation carries a non-null
  `condition_expr`, or a `use_channels` disabler operation
  (`method_name` in the derived `channel_default_disablers`) anywhere on the receiver, yields zero
  `SAFE`/`WILL_FAIL` findings for every operation on that receiver.
- **AC-10.7 (stale contract table degrades, does not crash).** `check_graph` against a contract
  table with no `receiver_state` block and no `channel_guards` keys (i.e. the pre-increment
  artifact, committed as a test fixture) returns the pre-increment report, byte-identical after
  JSON round-trip. `check_graph` never raises on it.
- **AC-10.8 (empty graph unchanged).** `check_graph('{"protocol_fqn":"p","operations":[],"resources":{}}',
  contracts)` returns `Verdict.UNKNOWN` with zero findings — main spec AC-3.5 / §3.2's empty-multiset
  row, re-asserted because this increment adds the first code path that could have special-cased it.
- **AC-10.9 (derivation reproducibility, published not asserted).** `python -m plr_sema.derive
  --survey-json … --out …` re-emits `derived_contracts.json` with a `receiver_state` block whose
  `LiquidHandler` entry has `channel_attr == "head"`, `tracker_class == "TipTracker"`,
  `bool_view.field == "_pending_tip"`, `effects == {"add_tip": "has_tip", "remove_tip": "no_tip"}`,
  and `tip_state_exceptions == ["HasTipError", "NoTipError"]` — each read out of PLR source and the
  taxonomy artifact, none written into `plr_sema`'s source. A test asserts the block equals that
  value **and** that grepping `plr-sema/src/` for the literals `"TipTracker"`, `"has_tip"`,
  `"_pending_tip"`, `"NoTipError"`, `"HasTipError"` and `"head"` returns nothing outside docstrings
  and comments. This is the anti-hand-typing gate and it is mechanical.
- **AC-10.10 (family selection is published).** The gap ledger gains a `tip_state` block listing, per
  anchored receiver class, the derived tip-loading / tip-requiring / tip-dropping method sets and the
  `tipstate_anchor` status. The test asserts the sets are non-empty and that
  `"aspirate" ∈ tip_requiring`, `"pick_up_tips" ∈ tip_loading`, `"drop_tips" ∈ tip_requiring ∩
  tip_dropping` — the three §10.2.6 expectations, so a rule that silently selects nothing fails.
- **AC-10.11 (oracle gate — replay).** `#4879`'s tier-1 corpus replay over the 812 + 88 rows reports
  **0 unsound rows** under `oracle_common.compare`'s own predicate
  (`plr-sema/eval/oracle_common.py:161-163`): no operation is `SAFE` where the simulator raised, and
  none is `WILL_FAIL` where the simulator ran clean. This is a hard gate. The `UNKNOWN` rate is
  **reported, not gated** — main spec Deferred (f) still defers the number.
- **AC-10.12 (oracle gate — mutants, direction only).** `#4881`'s tip-family mutants (remove
  `pick_up_tips` → `NoTipError`; duplicate it → `HasTipError`) are replayed with **PLR-named
  arguments** (see §10.12, Q3). The gate is directional and has no rate: (i) **zero** mutant rows in
  which the simulator raised `NoTipError`/`HasTipError` at index `i` carry a static `SAFE` at `i`;
  (ii) **zero** rows in which the simulator ran index `i` clean carry a static `WILL_FAIL` at `i`;
  (iii) **at least one** row in each of the two mutation classes carries a static `WILL_FAIL` at the
  index the simulator raised — i.e. the family moved off `UNKNOWN` in the correct direction at least
  once. Criterion (iii) is what makes this gate unsatisfiable by an evaluator that never fires.

### Task row

| task | scope | files | gate | ~LOC | depends on |
|---|---|---|---|---|---|
| **#4888** | Tip typestate increment, in this order: (1) derive P1/P2/P3/P4 passes + `channel_guards` bridge + `receiver_state` payload block + ledger `tip_state` block; (2) `check/graph.py` mirror gains `arguments` and `execution_order`, §6.2 table edit, Fork C drift test extended; (3) `plr_sema/check/tipstate.py` — lattice, channel-set derivation, atom parser, evaluator; (4) `check/__init__.py` wiring + the `channel_state_unknown` constructor; (5) `test_reason_vocabulary_closed_forward` verdict-aware exemption (§10.10); (6) three new fixtures + tests; (7) HM-14 7→8, HM-24 new row, HM-21 declared bump | create `plr-sema/src/plr_sema/check/tipstate.py`, `plr-sema/src/plr_sema/derive/receiver_state.py`, `plr-sema/tests/test_tipstate.py`, `plr-sema/tests/fixtures/{double_pickup,pickup_then_aspirate,aspirate_after_drop}_graph.json`, `plr-sema/tests/fixtures/derived_contracts_pre_increment.json`; modify `plr-sema/src/plr_sema/check/{__init__,graph}.py`, `plr-sema/src/plr_sema/derive/__init__.py`, `plr-sema/src/plr_sema/verdict.py`, `plr-sema/src/plr_sema/_hand_maintained.py`, `plr-sema/tests/test_{verdict,derive,check_graph,check_graph_mirror_drift,hand_maintained_ratchet}.py`, `plr-sema/data/derived_contracts.json` (regenerated) | `uv run pytest plr-sema/tests -q` + AC-10.1–10.10, then `uv run python -m plr_sema.derive --survey-json training/verify/data/plr_preconditions.json --taxonomy-json training/verify/data/plr_exception_taxonomy.json --out plr-sema/data/derived_contracts.json` + AC-10.11/10.12 via `#4879`/`#4881` | ~700 | main spec T1–T9 (shipped); oracle `#4879` for AC-10.11, `#4881` for AC-10.12 |

**Honest sizing note.** ~700 LOC is at the upper edge of one session, above every task in the main
spec's own decomposition except T6 (~450). Sub-steps (1)+(2) are independently completable and leave
the tree green (the payload grows, `check/` ignores it, every existing test passes) — that is the
**minimum shippable split point** if the session runs long. Do not split between (3) and (4): an
evaluator with no emitter is untested code.

---

## 10.8 Registry, vocabulary and wire-format impact

### `REASON_VOCABULARY` (HM-14): 7 → 8, cap 12 unchanged

One new member, `channel_state_unknown`: *"a guard's condition parsed as a tip-state atom, but the
channel state it reads is ⊤"*. It is required and cannot be folded into an existing member:
`guard_predicate_unparsed` means "could not be turned into a predicate", which would become a **false
statement** for a guard this increment does parse, and main spec §0's rule that a reason names *which
pipeline stage returned nothing* would be violated — the parse stage returned something; the
*evaluation* stage did not. The member is mechanical, not semantic (it names our own give-up point),
so §3.3's classification argument for hand-maintaining the vocabulary carries over unchanged. HM-14's
`declared` moves 7 → 8; the cap of 12 is untouched; the ratchet sees a one-line reviewable diff,
which is exactly what it is for.

`test_reason_vocabulary_closed_forward` **must be amended**, and this is the sharpest trap in the
task. It AST-scans every `Finding(..., reason=...)` construction and requires the resolved literal or
module-level constant to be in `REASON_VOCABULARY` (main spec §3.4). `Finding.reason` has no default
(`plr-sema/src/plr_sema/verdict.py:173`), so the new `SAFE`/`WILL_FAIL` constructors must pass
`reason=""`, which the scan would reject. **Amendment:** the scan resolves the `verdict=` argument at
the same call site; when it resolves to the attribute literal `Verdict.SAFE` or `Verdict.WILL_FAIL`,
the `reason=` argument must be the empty-string literal and is exempt from membership; when it
resolves to `Verdict.UNKNOWN`, or is unresolvable, the existing rule applies unchanged. The reverse
test (every vocabulary member reachable from ≥1 construction site) is unaffected. Giving `reason` a
default instead is **forbidden** — that is a field-set change to the wire record, which §3.5 names as
the highest-consequence assumption in the document.

### Mirror field set (HM-21): 8 → 10 fields

`check/graph.py` gains two `OperationNode` fields, and main spec §6.2's normative derived-from-
consumers table gains two rows:

| field | consumer |
|---|---|
| `arguments` (`models.py:536-538`) | §10.1.3's channel-set derivation (rules 1 and 3) — the *only* source for `use_channels` and for the channel-default parameter's cardinality |
| `execution_order` (`models.py:632-634`, on `ProtocolComputationGraph`) | §10.5 rule 1 — cross-checks the `operations` list order the state fold depends on |

`arguments` was deliberately **deleted** by the main spec's round-4 M1/B4 pass ("never read by
anything except `graph.py`'s own declaration/parse"; it also fed the withdrawn `argument_not_static`).
Re-adding it is not a reversal of that finding — the finding was that it had no consumer; it now has
one, named above, which is precisely the condition §6.2 sets for a field to be mirrored. B4's
warning still stands and is respected: this increment reads `arguments` **by PLR parameter name and
by `ast.literal_eval` of the value**, never by intersecting it with `depends_on_params`, so the
same-named-collision false-positive path B4 withdrew stays closed.

HM-21's `measure` is a live field count; it moves 8 → 10. Under §9.1's live+2 headroom rule for
`CAPPED` rows, T9's baseline of 8 would have been declared at 10, so this lands exactly at the
ceiling. The fixer must bump `declared` to 12 in the same commit — a visible, reviewable one-line
diff, which is the mechanism working, not being defeated (§9.3: "growth is not forbidden, it is made
loud"). Fork C's `test_mirror_fields_match_operation_node` (§5.3) must be extended to the two new
fields in the same commit or it will not see them.

### Registry: one new row, HM-24 — the front end's syntactic patterns

The design needs **no** hand-typed PLR fact: no class name, no method list, no exception name, no
field name. What it does need is six *syntactic patterns* — heuristics over how PLR is written, in
the same spirit as HM-3's validator-name prefixes:

| # | pattern | where |
|---|---|---|
| 1 | channel-receiver shape `self.<attr>[<name>].<method>` | §10.2.5 bridge |
| 2 | typestate-anchor shape: a property whose body is `return self.<F> is/is not None` | §10.2.2 |
| 3 | channel-default idiom `<p> = <p> or self.<x> or list(range(len(<q>)))` | §10.2.3 |
| 4 | atom `<path>.<bool_view.attr>` | §10.3.1 |
| 5 | atom `<path>.<state_field> is None` | §10.3.1 |
| 6 | atom `<path>.<state_field> is not None` | §10.3.1 |

**HM-24** — *tip-typestate front-end syntactic patterns* — metric: patterns; baseline **6**; status
**CAPPED (8)** (live+2, §9.1's D16c rule); `why_not_derived`: *"These are patterns over PLR's coding
style, not facts about PLR that any artifact records. Deriving them would require a meta-analysis
that recognises 'this is how this codebase spells a typestate', which is the analyzer's own
judgement, not PLR's data — the same argument HM-3 makes for validator-name prefixes."*;
`breaks_when`: *"PLR renames `has_tip`'s pattern, replaces `self.head[c]` with a method accessor
(`self.channel(c)`), or drops the `or list(range(len(...)))` idiom. All three fail **closed**: the
pattern stops matching, the feature disables itself for that class (§10.2.2's fail-closed rule), and
every verdict reverts to `UNKNOWN`. None of them can produce a wrong verdict."*

Live rows: 22 → **23**. Cap stays **24**; headroom 2 → **1**. Registering these as *one* row rather
than two or six is deliberate and is the opposite of RISK-8's splitting concern: they are one
coherent surface (the front end's syntax) with one failure mode.

**No HM row is needed for the two exception class names** — `HasTipError`/`NoTipError` are selected
by `category == "tip_state"` from `training/verify/data/plr_exception_taxonomy.json`, an artifact
whose categories are themselves derived by HM-19's already-registered keyword table. Writing them
into `plr_sema` would be new hand-typed surface; reading them out of the artifact is not. AC-10.9's
grep is the enforcement.

### Wire format: no change

`Verdict`'s three members, `Finding`'s seven fields, `PlrSite`, `AnalysisReport`'s field set,
`SCHEMA_VERSION = 1` (`plr-sema/src/plr_sema/verdict.py:74`), and `join`'s body and signature are all
**unchanged**. `Verdict.from_wire`'s widening rule is unchanged. `derived_contracts.json` keeps
`schema_version: 1`: both additions are new optional keys read through `.get()`, and a checker
running against a pre-increment table degrades to today's behaviour (AC-10.7) rather than raising —
which is the same fail-closed-to-`UNKNOWN` direction §Open decisions 1 establishes as always sound.

---

## 10.9 Explicitly not in this increment

- **Volume atoms.** Every numeric `Cmp` stays ½, per main spec §Open decisions 2, including
  `drop_tips`'s depth-0 `tip.tracker.get_used_volume() > 0 and (not allow_nonzero_volume)`. Volume
  also needs a `SoundnessScope` record for `does_volume_tracking()`, which tip state does not
  (§10.6.3).
- **Branches.** `condition_expr`/`true_branch`/`false_branch` stay unmirrored; the walk widens on
  them (AC-10.6) rather than modelling them. No branch-merge join, no ⊥, no fixpoint.
- **Loops.** Widen, do not analyse. `items_x`/`items_y` trip counts are not consulted; deferred (d)
  stays deferred.
- **Aliasing.** A-SINGLE is assumed, not checked (§10.6.3).
- **The 96-head.** `head96`, `pick_up_tips96`, `aspirate96`, `drop_tips96`, `stamp` are untouched.
  `head96` has a different attribute name and a different tracker arity; the P1 pass will type it,
  but §10.1.3 has no channel-set rule for it, so every 96-head operation falls to rule 4 (`⊤`).
- **Compound conditions.** Only single atoms are interpreted; `and`/`or`/`not` conditions fall
  through to `guard_predicate_unparsed`, unchanged.
- **Non-`LiquidHandler` receivers.** Any receiver class without a P1a channel attribute typing to a
  P2-anchored class gets no state and no behaviour change. The whole-surface contract table
  (4,770 entries) is untouched; this increment reads it, it does not narrow it.
- **The non-legacy surface.** The verifier and the oracle run at submodule pin `dd79c4c89`, where
  `LiquidHandler` lives under `legacy/`. `upstream_nonlegacy` has contracts (T14) but no executable
  oracle, so this increment is specified, derived and gated **at the pin**. `SurveyStamp.surface` /
  `surface_pin` (`check/__init__.py:150-153`) already record which surface a table came from; the
  fixer changes nothing there.
- **Precision targets.** No threshold, no rate, no `UNKNOWN`-reduction goal. Deferred (f) stands.

---

## 10.10 Open questions for the adversarial round

1. **Is merging `_tip` and `_pending_tip` into one abstract cell defensible, or is it the increment's
   soundness hole?** A-COMMIT is justified from two call sites (`liquid_handler.py:570-573`,
   `:716-723`) that were read, not from a proof over all of PLR. `TipTracker.rollback` and
   `TipTracker.clear` exist and were not analysed for this property. A challenger should look for a
   PLR path that leaves a head tracker uncommitted across an operation boundary. If one exists, the
   fix is to track the two fields as two cells and only emit a verdict when they agree — more
   machinery, same shape.

2. **Does "meet over the channel set" (§10.3.2) have the polarity right for `assert`-kind guards?**
   The argument given is for `raise_guard`s inside `for channel in use_channels` loops, where firing
   for any one channel fires the operation. No tip-state guard in the shipped table is an `assert`,
   so this production is specified but **unexercised** — an untested branch, and the kind that rots.
   Options: (a) specify it and test it against a synthetic contract fixture; (b) refuse to interpret
   `assert`-kind tip atoms in this increment and drop that row from §10.3.3. I lean (b) on
   Chesterton grounds but have specified (a); a reviewer should pick.

3. **The oracle's tier-1 adapter emits *tool* parameter names, so AC-10.11 may measure nothing.**
   `oracle_common.adapt_graph` builds `arguments` as `{k: json.dumps(v) for k, v in call["params"]}`
   (`plr-sema/eval/oracle_common.py:106-114`), and the corpus's tool schema names `pick_up_tips`'s
   argument `at`, not `tip_spots` (`training/verify/dispatcher.py:159-161`), while carrying no
   `use_channels` at all (grep of `training/assemble/out/corpus_p25.jsonl`: zero occurrences). Under
   §10.1.3's rules, **every corpus row falls to rule 4 and every verdict stays `UNKNOWN`** — so
   AC-10.11's zero-unsound gate would pass vacuously, which is exactly the "gate that passes without
   touching the thing it gates" failure main spec §6.2 flags for `receiver_type_unknown`. Three ways
   out, and the choice is not mine to make: (a) fix `adapt_graph` to emit PLR parameter names — it
   lives under `plr-sema/eval/`, outside `src/`, so it costs no import-boundary or registry surface,
   but it hand-types a tool→PLR name map that already exists in `dispatcher.py`; (b) route tier 1
   through tier 2's real extractor, where arguments are captured as written; (c) accept that tier 1
   gates only totality and non-regression for this increment, and move the real gate to
   AC-10.12's mutants with hand-authored PLR-named arguments. **AC-10.12 is written assuming (c) and
   is the reason it exists as a separate criterion.** A challenger should decide whether (c) is
   honest or an evasion.
   *Corollary for the oracle plan:* its tier-2 section calls any tier-1/tier-2 divergence "an
   extractor defect by construction". Under this increment that is no longer true — a divergence can
   equally be an `adapt_graph` argument-naming artefact. That sentence should be qualified.

4. **Is `channel_state_unknown` one member or two?** A `⊤` channel state and an *inexact channel set*
   are different give-up points (the state was widened vs. the argument was not a literal), and a
   ledger that cannot tell them apart cannot tell "we need better arguments" from "we need better
   flow". One member is specified, to spend the vocabulary budget conservatively; a challenger may
   argue for two (8 → 9 of 12, still under cap).

5. **Does E4's "widen the whole receiver" over-widen?** When `move_tips` reaches a tracker mutator at
   depth > 0, §10.2.6 widens every channel of the receiver rather than only the channels
   `move_tips` might touch — which are unknown, hence the widening. A more precise rule would widen
   only channels not provably untouched, which needs a may-touch set the graph does not carry. The
   coarse rule is sound (§10.5) and it is the sort of imprecision that is invisible until someone
   measures the `UNKNOWN` rate by method family, which is exactly what #4879 reports.

6. **Should `default` ever leave `TOP`?** §10.1.3 defines a per-receiver `default` that in practice
   never lowers, making it dead weight. Removing it simplifies the state to a plain `dict[int,
   TipState]` with an implicit `TOP`. It is kept because a future `setup()`-aware rule ("a fresh
   `LiquidHandler` has all channels `NO_TIP`", grounded in `liquid_handler.py:197`) would lower it,
   and that rule is the cheapest precision win left. But keeping an unexercised field is the same
   smell as question 2, and a reviewer may reasonably ask for it to go.

7. **Is one registry row for six patterns gaming the ratchet?** §9.4's anti-gaming clause is written
   against *splitting* one surface into many rows, and RISK-8 concedes there is no cross-row sum
   check. This does the reverse — merging six patterns into one row — which spends less headroom
   than six rows would. Both directions are unconstrained by the current mechanism. The argument for
   merging is that all six fail closed in the same way for the same reason; a challenger may argue
   that the bridge shape (pattern 1) and the atom grammar (patterns 4–6) have genuinely different
   breakage profiles and belong in separate rows.

---

## References

- Main specification (amended by this document): `.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md`
  — §0 (the organizing claim), §3 (verdict/finding/join, `REASON_VOCABULARY`), §6.2 (mirror field
  set, `check_graph`), §7.2–7.3 (closure mechanic, `InlinedGuard`, contract table), §9 (registry,
  budget, ratchet), Deferred (a)/(c)/(d)/(e)/(f), Open decisions 1–3.
- Research: `.praxia/docs/research/260901_plr-sema-research-a-d.md` (Q3's typestate adjudication,
  `:246-266`; R3 at `:520-526` is **wrong and must not be implemented**, per main spec §Open
  decisions 3's correction and `plr-sema/src/plr_sema/verdict.py:248-261`);
  `.praxia/docs/research/260901_plr-sema-research-c-e.md` (Q2's ranked resolution mechanisms and the
  measured `self.head[channel].get_tip → TipTracker` result, `:149-176`; Q5's atom grammar,
  `:439-483`).
- Oracle: `.praxia/docs/plans/260902_plr-sema-oracle-harness.md`; `plr-sema/scripts/oracle_spike.py`;
  `plr-sema/eval/oracle_common.py`. Backlog `#4879` (tier-1 replay), `#4880` (tier-2 extractor),
  `#4881` (tier-3 mutants), `#4882` (tier-4 fuzz).
- Code read for this document: `plr-sema/src/plr_sema/verdict.py`,
  `plr-sema/src/plr_sema/check/__init__.py`, `plr-sema/src/plr_sema/check/graph.py`,
  `plr-sema/src/plr_sema/derive/__init__.py`, `plr-sema/tests/fixtures/simple_transfer_graph.json`,
  `training/verify/failure_taxonomy.py`, `training/verify/dispatcher.py`,
  `training/floor_gen/exec_verify.py`, `praxis/backend/utils/plr_static_analysis/models.py`.
- Artifacts read verbatim: `plr-sema/data/derived_contracts.json`,
  `training/verify/data/plr_preconditions.json`, `training/verify/data/plr_exception_taxonomy.json`.
- PLR source at submodule pin `dd79c4c89`:
  `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py`,
  `external/pylabrobot/pylabrobot/resources/tip_tracker.py`.
