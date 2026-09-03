---
title: "plr-sema increment 4 — a second guard family, a content-addressed cache, and a derived inert-name filter"
description: "Fourth post-corpus increment to the plr-sema pre-corpus specification. Four backlog items across five scope sections, plus two go/no-go decisions. (1) #4881 adds guard families beyond tip state, and the evidence reverses the dispatch brief's premise on both of them: the LID family is NOT tip-shaped and is NOT adopted for verdicts -- `Liddable.has_lid` is a plain method not a property, `Liddable.lid` is derived from `children` so there is no state field, the wire format carries `parents` (parent TYPES, upward) and no children at all so entry is unavoidably TOP, and -- fatally -- the two lid guards that reach `LiquidHandler.aspirate`/`dispense` carry conditions `\"lidded is resource\"` and `null`, neither of which is a lid-state atom, because the survey drops the `if lidded is None: return` early-out that actually guards them; the VOLUME family, by contrast, is derivable today and is adopted, narrowly and asymmetrically -- `VolumeTracker.remove_liquid`/`add_liquid` already carry clean depth-0 `Cmp` guards raising taxonomy-`volume_state` exceptions from `pylabrobot.resources.errors`, the same two-conjunct selector shape the tip family uses, so an interval domain over well and tip cells decides the under-draw (`TooLittleLiquidError`) half, while the over-fill (`TooLittleVolumeError`) half stays Kleene half because `max_volume` is labware geometry the graph does not carry. (2) #4922 lands the content-addressed cache on increment 2's key, storing the PRE-relabel `Finding` tuple -- post-relabel storage is unsound because `sideband.origin` is excluded from `bytecode_hash` -- read-through opt-in and default off. (3) #4883 derives the dropped-receiver inert-name filter from `sys.stdlib_module_names` plus the class-object rule already shipped, and the registry finding is that it retires NO row because the surface has none: `_INERT_RECEIVER_PREFIXES`/`_INERT_CALL_SUFFIXES` are unregistered hand-maintained surface, discovery under section 9.4's own rule, so headroom stays 0 and the lid/volume families get none from it. (4) #4946 closes the m1 residual #4938 filed and commit 92f97256 diagnosed without moving: `LiquidHandler.transfer` already inherits its delegate's bridged NoTipError guard (`derived_contracts.json:58364-58383`) but not the delegate call site's literal channel argument -- `use_channels=[0]` on the `dispense` call, and a one-element `resources=[source]` display feeding `aspirate`'s own P3a idiom -- so 17 of 101 m1 mutants stay UNKNOWN and the gate sits at 84/101 against a 91% bar; P9 binds the guard's channel set from the caller's own AST, widens on every other shape, and leaves `channels_for_call` and E2 untouched. Zero new registry rows, zero rows retired, two per-row ceilings bumped (HM-24 1->2, HM-25 5->8), two new REASON_VOCABULARY members (8 -> 10 of cap 12), no wire-format change, no `IR_VERSION` bump. Go/no-go: #4923 NO-GO (the workload is unmeasured -- no committed artifact records a check-only wall time -- and #4922 absorbs the case it targets); #4924 NO-GO (re-planning a liquid move needs the over-fill half, which is undecidable until `max_volume` reaches the wire)."
status: draft
spec_version: 12
amends: 260901_plr-sema-pre-corpus-spec.md
task_id: 260903_sema-followups
date: '260903'
confidence: medium
sources: "Read this session, in full or in the cited ranges. Specs and plans: .praxia/docs/specs/260903_plr-sema-real-programs-increment.md (in full, including the section 12.13 implementation record and the round-1 remediation changelog); .praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md:55-170,173-501,505-646,650-701,1136-1165; .praxia/docs/specs/260902_plr-sema-ir-bytecode-increment.md:88-160,425-491,624-653; .praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:42-138 (Open decisions), 139-205 (section 0 and 0.1), 2287-2345 (section 9.1), 2347-2385 (section 9.2 inventory), 2412-2495 (section 9.4), 2499-2535 (Deferred + boundary summary), plus the section-header index. Audits: .praxia/docs/audits/260903_plr-sema-real-programs-round1-challenger.md:1-58 and its header index. Analyzer source: plr-sema/src/plr_sema/verdict.py:100-179; plr-sema/src/plr_sema/_hand_maintained.py:1-80,240-263,640-690,753-847,851-871 plus a grep index of every `what=`/`id=` field across all 25 REGISTRY rows; plr-sema/src/plr_sema/derive/__init__.py:840-959; plr-sema/src/plr_sema/check/ir.py:50-95,178-192,690-702,770-781,830-870,900-926; plr-sema/src/plr_sema/check/__init__.py:443-457,686-700,713-727. Harness: plr-sema/eval/oracle_common.py:690-739,976-1006; plr-sema/eval/tip_mutants.py:63-70,86-166,166-224,227-251. Front end: praxis/backend/utils/plr_static_analysis/models.py:95-105,340-350,555-563,575-599. PLR at submodule pin dd79c4c89: liquid_handling/liquid_handler.py:90-229,968-1069,1170-1199,1273-1289,1330-1374 and the `_check_no_lid`/`does_volume_tracking`/`maximal_volume` grep index over the whole file; resources/volume_tracker.py (in full, 171 lines); resources/lid.py (in full, 121 lines); resources/container.py:22-88,141-147 (grep context); resources/tip.py:16-80 (grep context). Artifacts: plr-sema/data/derived_contracts.json:53592-53633,58363-58394,58432-58486,157962-158133,159897-159936,161251-161253; training/verify/data/plr_exception_taxonomy.json:2964-2972,2991-2999,3010-3056; training/verify/data/plr_preconditions.json:49451-50431 (grep index for `op.resource.tracker.*`/`op.tip.tracker.*`/`tip.tracker.*`). Data: outputs/plr-sema/oracle_replay_260903_rebaseline.json:2-29; outputs/plr-sema/tip_mutants_260903_4938.json:1-38; outputs/plr-sema/tip_mutants_260903_4946.json:1-38; outputs/plr-sema/tier2a_260903.json:1-26; outputs/plr-sema/tier2b_260903.json:1-45."
---

# Increment 4: families, cache, inert names

> **This document amends `260901_plr-sema-pre-corpus-spec.md` by reference.** It adds §13 to that
> document's numbering and edits exactly one thing in it: **§Open decisions 2**'s sunset clause
> ("leave numeric atoms at Kleene ½ *through v1 and the first post-corpus increment*") has **expired**
> — increments 1, 2 and 3 have all shipped — and §13.2 reopens it for exactly one class of numeric
> atom (§13.10). **It also amends `260902_plr-sema-tip-typestate-increment.md`** (spec_version 9) in
> three places and **`260902_plr-sema-ir-bytecode-increment.md`** (spec_version 10) in two; §13.10 lists
> all six amendments. Everything else in spec_version 8–11 — `Verdict`, `Finding`, `PlrSite`,
> `AnalysisReport`, `join`, the telemetry schema, the fork-drift tests, the derivation closure
> mechanic, the value grammar, the canonical form, the hash, the cache key, `OBLIGED(graph)`, L1/L2/L3
> and B1/B2/B3 — is **unchanged**. No `schema_version` bump; no wire-format change; **no `IR_VERSION`
> bump** (it is `2`, `plr-sema/src/plr_sema/check/ir.py:93`); **zero new registry rows and zero rows
> retired** (24 live against `BUDGET_CAP = 24`, `plr-sema/src/plr_sema/_hand_maintained.py:43`,
> headroom 0). Two per-row ceilings move and two `REASON_VOCABULARY` members are added; §13.7 does the
> arithmetic.

---

## 13.0 What this increment is, in one paragraph

Increment 3 gave the analyzer real programs to run on; this increment asks what it can *say* about
them beyond tip state, whether it has to say it twice, and whether the machinery it says it with is
still hand-typed. Four backlog items across five scope sections, plus two go/no-go decisions.
**#4881** was dispatched as "two new guard families,
derived like the tip family", and the evidence reverses the framing on both. The **lid** family, sold
as the cheap tip-shaped one, is not tip-shaped in any of the four ways that matter — `Liddable` has no
state field, `has_lid` is a plain method rather than a property, the wire format carries no children
so entry state is unavoidably `TOP`, and the lid guards that actually reach `aspirate`/`dispense`
carry conditions `"lidded is resource"` and `null` because the survey drops the `if lidded is None:
return` early-out that guards them — so it is **specified and not adopted for verdicts**, with a named
trigger and a landmine flagged. The **volume** family, sold as the bigger one, turns out to be the one
that is already derivable: `VolumeTracker.remove_liquid` and `add_liquid` carry clean depth-0 `Cmp`
guards raising `TooLittleLiquidError`/`TooLittleVolumeError`, both members of taxonomy category
`volume_state` in module `pylabrobot.resources.errors` — the exact two-conjunct selector shape §10.2.5
already uses — and `dropped_calls` already records the bridge expressions `op.resource.tracker.
remove_liquid` / `op.tip.tracker.add_liquid`. So volume is adopted, **narrowly and asymmetrically**:
an interval domain decides the under-draw half, and the over-fill half stays ½ because container
capacity is labware geometry the graph does not carry. **#4922** lands the cache on increment 2's
existing key, with one correctness argument that is not obvious and is easy to get wrong in the
unsound direction. **#4883** derives the inert-name filter, and its registry finding is the opposite
of the one the dispatch expected: there is no row to retire, because the surface was never registered.
**#4946** is the sixth item and the only one that moves an existing gate: `LiquidHandler.transfer`
already inherits its delegate's bridged `NoTipError` guard, but not the delegate call site's *literal
channel argument*, so 17 of 101 m1 mutants stay `UNKNOWN` and the m1 gate sits at 84/101 against a
91% bar — closed by binding the guard's channel set from the caller's own AST.

| axis | today (spec_version 11) | this increment |
|---|---|---|
| guard families with an evaluator | tip only | tip + **volume (under-draw half)**; lid specified, not adopted |
| channel set for a guard inherited through `delegates_to` | `⊤` — the guard folds to ½ | bound from the **delegate call site's literal** channel argument, else `⊤` (§13.5) |
| `LiquidHandler.transfer`'s bridged `NoTipError` guard | `guard_predicate_unparsed` on every row | evaluated on channel 0; the m1 gate moves **84/101 → ≥ 92/101** |
| abstract domains | one height-2 typestate lattice per channel | + one **interval** lattice per volume cell |
| numeric `Cmp` atoms | all Kleene ½ (main spec §Open decisions 2) | ½ **except** a guard raising a `volume_state` exception from `pylabrobot.resources.errors` |
| well/tip capacity (`max_volume`) | not modelled | still not modelled — **⊤**, and the over-fill half is ½ because of it |
| `does_volume_tracking()` | not modelled | a **runtime-observed** `env` argument, default empty, which gates `WILL_FAIL` only |
| repeat `check_graph` on one program | full re-lower + re-walk | optional read-through cache on §11.3.3's key |
| the inert-name filter | 9 hand-typed prefixes + 11 hand-typed suffixes | derived from `sys.stdlib_module_names` + the shipped class-object rule |
| registry rows | 24 live, cap 24, headroom 0 | **24 live, cap 24, headroom 0** — unchanged |
| per-row ceilings | HM-24 `CAPPED (1)`, HM-25 `CAPPED (5)` | **HM-24 → 2, HM-25 → 8** (loud diffs, no new row) |
| `REASON_VOCABULARY` | 8 of cap 12 | **10 of cap 12** |
| `IR_VERSION` | 2 | **2** — unchanged |

**Deliverable of this increment, stated as the property that must become true:** a protocol that
aspirates 200 µL from a well the harness seeded with 100 µL produces `Verdict.WILL_FAIL` sited at
`PlrSite("external/pylabrobot/pylabrobot/resources/volume_tracker.py", 92,
"VolumeTracker.remove_liquid")`, and an *executed* run of that same call sequence against the
verifier's chatterbox deck raises `TooLittleLiquidError` at the same operation index — while the
*same* protocol run with the volume-tracking hypothesis unasserted produces `UNKNOWN` there, so that
the definite verdict is visibly a function of an observation and not of an assumption.

---

## 13.1 #4881, first half — the lid family: specified, and not adopted

### 13.1.1 The PLR fact, and it is not the one the dispatch described

`LiquidHandler` refuses to pipette into or out of a lidded resource. The refusal is one module-level
helper (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:110-120`):

```python
def _check_no_lid(resource: Resource, action: str) -> None:
  lidded = _lidded_ancestor(resource)
  if lidded is None:
    return
  if lidded is resource:
    raise ValueError(f"Cannot {action} {resource.name!r}: it has a lid. Remove the lid first.")
  raise ValueError(...)
```

called at six sites — `:978` and `:1762`/`:1765` with `"aspirate from"`, `:1191` and `:1912`/`:1915`
with `"dispense to"`. `_lidded_ancestor` (`:95-107`) walks the **parent chain**, testing
`isinstance(current, Liddable) and current.has_lid()` at `:104`, so a lid anywhere in the ancestry
blocks pipetting — not only one on the direct parent. The dispatch brief cited `:104-116` and the
`isinstance`/`has_lid` test, and both check out; what the brief did not carry is the ancestor walk,
and the ancestor walk is one of the four reasons this family is not cheap.

### 13.1.2 The domain, specified so a later increment does not re-derive it

> **Normative (the lid lattice).** For one resource slot, `LidState ::= NO_LID | HAS_LID | TOP`, with
> the information order and join table of §10.1.1 read with `NO_LID` for `NO_TIP` and `HAS_LID` for
> `HAS_TIP`. The abstract state is `dict[slot: int, LidState]` — **per resource slot**, not per
> receiver, which is the one structural difference from the tip domain: tip state lives on the
> `LiquidHandler`, lid state lives on the `Plate`.
>
> **Normative (entry state).** The entry `LidState` of every resource slot is `TOP`, unconditionally
> and with no derivable exception. `NO_LID` and `HAS_LID` at entry are **not** establishable.

Entry `TOP` is forced by the wire format and is not a choice. The `RESOURCE` instruction's only
structural operand is `parents: tuple[str, ...]` (`plr-sema/src/plr_sema/check/ir.py:190`), lowered
from `ResourceNode.parental_chain` (`:698`), which the upstream model documents as *"Parent types from
resource to deck"* (`praxis/backend/utils/plr_static_analysis/models.py:587-589`). Three separate
things are missing at once: it records **types**, not names, so it cannot identify a slot; it records
**ancestors**, not children, and a lid is a *child* (`Liddable.lid` is
`next((child for child in self.children if isinstance(child, Lid)), None)`,
`external/pylabrobot/pylabrobot/resources/lid.py:74-77`); and it is a chain **upward**, which is the
direction `_lidded_ancestor` walks but not the direction that answers "does this plate carry a lid".
So the answer to the dispatch's question — *does the wire format say whether a plate has a lid child?*
— is **no, in three independent ways**, and the family can only ever fire after an observed lid
movement. That is stated here rather than discovered later.

### 13.1.3 Effects, and where the anchor would have to come from

`Liddable`'s mutators are the `lid` setter (`lid.py:79-86`: `None` → `unassign_child_resource`,
otherwise `assign_child_resource`) and `Liddable.assign_child_resource` itself (`lid.py:102-120`),
which raises `ValueError(f"'{self.name}' already has a lid.")` at `:110` when one is already seated.
A P4-shaped effect classification would give `assign_child_resource → HAS_LID` and
`unassign_child_resource → NO_LID`, and `LiquidHandler.move_lid` would bridge to them — the same
depth-0-only discipline §10.2.6 imposes on tip effects. **None of that is the blocker.**

The blockers are the anchor and the guard, and there are four:

| # | blocker | evidence |
|---|---|---|
| **B1** | P2's anchor rule matches a **property** whose body is `return self.<F> is/is not None` (§10.2.2). `Liddable.has_lid` is a plain **method** (`lid.py:71-72`, no decorator; the `@property` at `:74` belongs to `lid`) | `lid.py:71-77` |
| **B2** | P2 requires a **state field** `<F>` that P4 can classify writes to. `Liddable` has none: `lid` is computed from `self.children` on every read (`lid.py:74-77`), so there is nothing for `_classify_write` to see | `lid.py:74-77` |
| **B3** | The wire format carries no children, so entry is `TOP` (§13.1.2) | `ir.py:190`, `models.py:587-589` |
| **B4** | **The fatal one.** The lid guards that reach a `LiquidHandler` contract entry are unevaluable | see below |

**B4, in full, because it is the one that decides the section.** The shipped table already inlines
`_check_no_lid`'s two guards at depth 1 into six `LiquidHandler` contract entries — one such inlining
is `plr-sema/data/derived_contracts.json:53597-53630` — and carries `_check_no_lid`'s own entry with
the same two guards at depth 0 (`:159897-159933`). Their recorded shape is:

| guard | `condition` | `raises` | `site` |
|---|---|---|---|
| the self-lidded raise | `"lidded is resource"` | `"ValueError"` | `liquid_handler.py:116` |
| the ancestor-lidded raise | **`null`** | `"ValueError"` | `liquid_handler.py:117` |

Neither is a lid-state atom. The first tests *which* resource carries the lid, not *whether* one does;
the second has no condition at all. The predicate that actually decides both — `_lidded_ancestor(
resource) is None` — is expressed as an **early `return`** (`liquid_handler.py:113-114`), and the
precondition survey's `scope_trail` models `if` scopes, not early returns, so it is simply absent.
An evaluator cannot construct a lid verdict from these two rows no matter how good the state
derivation is.

And `ValueError` compounds it: the tip family selects its exception set by the two-conjunct taxonomy
filter `category == "tip_state" AND module == "pylabrobot.resources.errors"` (§10.2.5), which is
`DERIVED` precisely because no class name is typed into `plr_sema`. `ValueError` is a builtin with
**no entry at all** in `training/verify/data/plr_exception_taxonomy.json` — verified by search — so
there is no category to select on and no analogous filter to write. Selecting the lid family would
require naming `ValueError` plus a site filter in our own source, which is a hand-typed fact against
zero headroom.

> **Normative (the disposition).** The lid family is **specified and not adopted**. `plr_sema` derives
> and publishes the lid *ledger* facts — see AC-13.3 — and constructs **no `Finding` of any verdict**
> from a lid guard. Every operation carrying a `_check_no_lid`-derived guard continues to emit
> `guard_predicate_unparsed`, exactly as it does today. No `LidState` is computed, no lid entry is
> added to `receiver_state`, and no new `REASON_VOCABULARY` member is spent on a producer that does
> not exist.
>
> **The named trigger that converts this to adoptable:** the precondition survey records an
> early-`return` guard scope — i.e. `_check_no_lid`'s `:117` raise acquires the condition
> `not (lidded is None)` in its `scope_trail` — at which point B4 falls and B1/B2 become the ordinary
> cost of one new anchor shape.

**The landmine, disclosed because nothing else in this repo will.** A `raise_guard` with
`condition: null` reads, on its face, as *"this method raises unconditionally at this point"*. It is
not: `:117`'s raise is reachable only when the early `return` at `:113-114` did not fire. Today this
is harmless — a `null` condition falls through to `guard_predicate_unparsed` and asserts nothing — but
**any future rule that treats a `null`-condition `raise_guard` as a definite failure would manufacture
`WILL_FAIL` on six `LiquidHandler` methods for programs that run clean.** #4924's recovery interpreter
is precisely the consumer that would be tempted by such a rule. AC-13.4 pins the current behaviour so
the temptation is caught by a test rather than by a reader.

**This section reverses the dispatch brief's premise, on evidence.** The brief scoped lid as
"tip-shaped, cheap". It is neither, and the four blockers above are all read out of source and shipped
artifacts at the current pin rather than argued from taste.

---

## 13.2 #4881, second half — the volume family: an interval domain, adopted asymmetrically

### 13.2.1 Why this one *is* derivable, and the correction the dispatch needs

The dispatch brief described the volume guards as testing `_used_volume`/`_pending_volume` against
`max_volume`. **The field names are wrong and the correction matters**, because the anchor derivation
keys on them: `VolumeTracker.__init__` writes `self.volume` and `self.pending_volume`
(`external/pylabrobot/pylabrobot/resources/volume_tracker.py:49-50`), and the guards read them only
through two accessor **methods** — `get_used_volume` returning `self.pending_volume` (`:114-116`) and
`get_free_volume` returning `self.max_volume - self.get_used_volume()` (`:118-120`). There is no
`_used_volume` anywhere in the module. The line numbers the brief gave are right: the raises are at
`:92` (`TooLittleLiquidError` inside `remove_liquid`, `:88-99`), `:105` (`TooLittleVolumeError` inside
`add_liquid`, `:101-112`) and `:136` (`TooLittleLiquidError` inside the deprecated `get_liquids`,
`:122-138`).

Four facts make this family derivable where the lid family is not, and all four are already in shipped
artifacts:

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
   and `LiquidLevelError` (a Hamilton backend class, `:2991-2999`). That is the same 5→2 narrowing
   §10.2.5 performs for tip state, against the same module path, so **no new hand-typed string enters
   `plr_sema`** — the module literal is the one AC-10.9 already declares.
3. **The bridge expressions are already recorded.** `training/verify/data/plr_preconditions.json`'s
   `dropped_calls` carries `"op.resource.tracker.remove_liquid"` and `"op.tip.tracker.add_liquid"` for
   aspirate (`:49768-49769`) and `"op.resource.tracker.add_liquid"` / `"op.tip.tracker.remove_liquid"`
   for dispense (`:49863-49864`). They survive the inert filter: head `op` is lowercase and not a
   prefix member, and the tails are not suffix members
   (`plr-sema/src/plr_sema/derive/__init__.py:884-905`).
4. **`BlowOutVolumeError` is genuinely out of scope and the module conjunct is what puts it there.**
   Its two raises (`liquid_handler.py:1185` and `:1188`, inside the `does_volume_tracking()` block at
   `:1182-1188`) guard `self._blow_out_air_volume` against a requested blow-out volume — a
   `LiquidHandler` instance field, not a tracker cell, and therefore a different domain. The dispatch
   brief listed it; this increment excludes it, by the selector rather than by an exception.

### 13.2.2 The two cell kinds, and the capacity problem

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

> **Normative (the capacity asymmetry, and it is the section's main scope decision).** `max_volume` is
> **⊤ for every cell**. For a container it is a function of the labware's physical dimensions
> (`container.py:84`), and for a tip it is `Tip.maximal_volume` (`tip.py:27,45`); neither reaches the
> analyzer, because `RESOURCE`'s operands are `slot`/`type`/`element_type`/`is_container`/
> `is_parameter`/`parents`/`grid` (`plr-sema/src/plr_sema/check/ir.py:184-191`) and none of them is a
> capacity. Therefore:
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

**This narrows the dispatch brief's specification, deliberately.** The brief asked for
`WILL_FAIL iff lo > capacity`; that half is unreachable at the current wire format and is named in
§13.12 with its trigger (a capacity operand on `RESOURCE`, which is an `IR_VERSION` bump and therefore
not free — precisely the reason increment 3 took its bump when it was free).

### 13.2.3 The abstract state

```
Interval    ::=  [lo, hi]  with 0 <= lo <= hi <= +inf   |   TOP
VolumeState =  dict[cell: CellId, Interval]
CellId      =  ("container", slot: int, cell: str|null)  |  ("tip", channel: int)
```

`TOP` is `[0, +inf]` and the two are identified; the join is `[min(lo), max(hi)]`, which is the least
upper bound in the information order and gives a lattice of infinite height. **Infinite height is why
a widening operator is needed here and was not needed for tip state** (§10.1.1: "height 1 above its
two atoms … needs no widening operator"). The widening is stated in §13.2.5 and is the one place this
domain differs structurally from every domain the analyzer has had so far.

`CellId`'s container form reuses the `Ref(slot, cell)` pair the value grammar already produces
(§11.1.2), so a well reference in a kwarg *is* a cell id with no new resolution machinery. The tip
form keys on the channel index the tip family already computes (§10.1.3), which is the one place the
two families touch: **a tip cell exists only where the tip family says a channel has a tip.** If the
channel's `TipState` is not `HAS_TIP`, the tip cell is `TOP` — the analyzer does not know which tip is
mounted, so it cannot know its used volume.

### 13.2.4 The derived inputs — two new passes, and what they cost

Everything below is computed at build time by `plr_sema.derive` and shipped in
`derived_contracts.json`; `check/` stays stdlib-only.

> **Normative (P7, the volume anchor).** A class `C` is **volume-anchored** iff it has ≥1 zero-argument
> method whose body is a single `return <expr>` over `self.<F>` for some instance field `<F>` written
> in `C.__init__`, **and** ≥1 method whose body contains an `ast.Raise` of a class in the two-conjunct
> `volume_state` set (§13.2.1 fact 2) guarded by an `ast.Compare` mentioning one of those accessors and
> one of the method's own parameters. `C`'s **used-volume accessor** is the accessor named by the
> `TooLittleLiquidError` guard's comparison; its **free-volume accessor** is the one named by the
> `TooLittleVolumeError` guard's. Both are recorded by name; neither name is typed into `plr_sema`.
>
> **Fail-closed rule.** Zero anchors, or ≥2 candidate used-volume accessors, and P7 emits nothing for
> `C`; the volume family is disabled for every cell typing to `C`, and every verdict reverts to
> today's. The gap ledger records `volume_anchor: "absent"|"ambiguous"|{...}` per candidate class, the
> same visible-absence discipline §10.2.2 established for `tipstate_anchor`.
>
> Measured expectation over the current pin, which the fixer must **reproduce and publish, not
> assume**: `C = VolumeTracker`, used-volume accessor `get_used_volume`, free-volume accessor
> `get_free_volume`, field `pending_volume`.

> **Normative (P8, the operand-pairing idiom).** For a method `m` of receiver class `R`, match an
> `ast.ListComp` (or `GeneratorExp`) whose element is an `ast.Call` to a class `O` with keyword
> arguments, and whose single comprehension iterates `zip(a1, …, an)` where each `ai` is an
> `ast.Name`. Record, per keyword `k` of the element call whose value is a comprehension target bound
> at zip position `i`, the pair `(O.k → ai)`. When `ai` is a parameter of `m`, the binding is a
> **parameter pairing**; otherwise it is a **local pairing** and is recorded but not consumed.
>
> Measured expectation over the current pin: `LiquidHandler.aspirate`'s comprehension
> (`liquid_handler.py:1007-1028`, element call at `:1008`, `zip` at `:1018-1027`) yields
> `SingleChannelAspiration.resource → resources` (`:1009`, zip position 0),
> `.volume → vols` (`:1010`, position 1) and `.tip → tips` (`:1014`, position 5 — a **local**
> pairing, since `tips` is the list built at `:974`, not a parameter).

> **Normative (the volume bridge, a second HM-24 pattern).** Match, against every `dropped_calls`
> entry reached at **depth 0** in `K`'s own body, the shape
>
> ```
> <name>.<field>.<attr>.<method>          e.g.  op.resource.tracker.remove_liquid
> ```
>
> where `<name>` is a comprehension target of a P8 match in `K`, `<field>` is a keyword of that
> match's element call, `R`'s P1a map (or the element class `O`'s) sends `<attr>` to a P7-anchored
> class `C`, and `f"{C}.{method}"` is a key in the contract table. When it matches, attach every guard
> of `C.<method>` to `K` as a **volume guard** carrying the originating expression in `via`, the paired
> parameter name in `cell_param`, and the guard-parameter-to-`K`-parameter binding in `amount_param`.
>
> `derived_contracts.json` gains one additive block per anchored class under `receiver_state` and one
> additive `volume_guards` list per contract entry, both read through `.get()` with an empty default so
> a pre-increment table degrades to today's behaviour. `schema_version` stays **1**.

Measured expectation, to be reproduced and published: `LiquidHandler.aspirate` acquires two volume
guards — `cell_param: "resources"`, `amount_param: "vols"`, `via: "op.resource.tracker.remove_liquid"`,
raising `TooLittleLiquidError`; and `cell_param: <the tip local>`, `via: "op.tip.tracker.add_liquid"`,
raising `TooLittleVolumeError`. `LiquidHandler.dispense` acquires the mirror pair
(`plr_preconditions.json:49863-49864`).

**The honest cost, stated here rather than in §13.7's table alone.** The volume bridge is a **second**
pattern for HM-24, whose row declares `metric="patterns"`, `declared=1`, `status="CAPPED"`
(`_hand_maintained.py:781-814`, the three fields at `:793-795`), and P7's accessor shape plus P8's
zip-comprehension shape are a **sixth and seventh** pattern for HM-25, whose row declares the same
metric at `declared=5` (`:815-847`, the fields at `:828-830`). Increment 3 §12.1.2 declined a sixth HM-25 pattern on the
grounds that "the registry has zero headroom, so a sixth pattern is a cap conversation". **That
inference is wrong on the mechanics and is corrected here:** §9.4's cap of 24 is a cap on the *count
of rows*, enforced by `test_total_declared_within_budget` over `live_rows()`
(`_hand_maintained.py:851-855`); a per-row `declared` ceiling is enforced separately by
`test_no_surface_exceeds_its_declared_size`, and §9.3 says of exactly that test, *"growth is not
forbidden, it is made loud."* Bumping HM-24 to 2 and HM-25 to 7 adds **no row**, moves **no cap**, and
produces two one-line reviewable diffs. §13.13's Q1 invites a reviewer who holds increment 3's
stricter line to say so — under that line, the volume family does not land in this increment at all,
and neither does §13.5's P9, which takes the same row 7 → 8 on the same argument.

### 13.2.5 Transfer functions and the interval arithmetic

For an operation `op` with a volume guard carrying `cell_param` and `amount_param`, let `cells(op)` be
the `Value` of `op.kwargs[cell_param]` and `amounts(op)` the `Value` of `op.kwargs[amount_param]`.

> **Normative (V0, pairing).** If `cells(op)` is `Seq([c₁…cₙ])` with every `cᵢ` a `Ref`, and
> `amounts(op)` is `Seq([a₁…aₙ])` with every `aᵢ` a `Lit` of a JSON number, and the two lengths agree,
> then `op` pairs to `[(cell(cᵢ), aᵢ)]`. A bare `Ref`/`Lit` pair is the length-1 case. **In every other
> case — either operand `Top`, a length mismatch, a `Seq` containing a `Top` or a non-numeric `Lit` —
> V0 does not apply and V3 does.** This mirrors PLR's own zip (`liquid_handler.py:1018-1027`), which
> is why the length agreement is a *conjunct* and not a recovery.
>
> **Normative (V1, evaluate then transition).** Guards are evaluated against the pre-state, then the
> post-state is computed — E1's ordering, unchanged.
>
> **Normative (V2, exact transfer).** For each paired `(cell, a)` with pre-state `[lo, hi]`:
> a used-volume-**decreasing** effect (the `TooLittleLiquidError` guard's own method,
> `remove_liquid`) gives `[max(0, lo - a), max(0, hi - a)]`; a used-volume-**increasing** effect
> (`add_liquid`) gives `[lo + a, hi + a]`. Cells outside `cells(op)` are unchanged. Which method is
> which is **derived**, not typed: the decreasing one is P7's `TooLittleLiquidError`-guarded method and
> the increasing one is the `TooLittleVolumeError`-guarded one.
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

**Guard evaluation.** The two conditions are `volume - self.get_used_volume() > 1e-06` and
`volume - self.get_free_volume() > 1e-06`, where `volume` binds to the paired amount `a` and the
accessor reads the cell's interval. With `used ∈ [lo, hi]`:

| guard | fires (`T`) iff | does not fire (`F`) iff | otherwise |
|---|---|---|---|
| under-draw (`remove_liquid`) | `a - hi > 1e-06` | `a - lo <= 1e-06` | `½` |
| over-fill (`add_liquid`) | never (capacity ⊤) | never | **always `½`** (§13.2.2) |

`T`/`F`/`½` then produce `WILL_FAIL`/`SAFE`/`UNKNOWN` through §10.3.3's existing table unchanged,
with `category = "precondition_state"` and, for `½`, `reason = "volume_state_unknown"`.

**The `1e-06` tolerance is read from the guard, not typed.** It is a literal in the derived
`condition` string (`derived_contracts.json:158111`) and is evaluated as part of the `Cmp`; nothing in
`plr_sema`'s source names it.

### 13.2.6 The `does_volume_tracking()` hypothesis — discharged by narrowing, not by machinery

Every volume guard in `LiquidHandler` sits under a process-global flag. In `aspirate` it is a scope:
`if does_volume_tracking():` at `liquid_handler.py:1032`, wrapping the two tracker calls at
`:1034-1035`. In `drop_tips` it is a *conjunct of the condition itself* —
`"tip.tracker.get_used_volume() > 0 and (not allow_nonzero_volume) and does_volume_tracking()"`
(`training/verify/data/plr_preconditions.json:50077-50080`). Main spec §Open decisions 2 and increment
1 §10.9 both record that a definite volume verdict therefore needs a `SoundnessScope` environment
record, which does not exist.

**It is not needed, because the two verdict directions are not symmetric under the flag:**

- If tracking is **off**, `remove_liquid` is never called from `aspirate` at all, so the site cannot
  raise. A `SAFE` finding for that guard — "this guard does not fire" — is therefore **true under both
  branches of the flag** and needs no hypothesis.
- A `WILL_FAIL` finding claims the site *does* raise, which is false when tracking is off. It needs
  the hypothesis.

> **Normative (the env argument).** `check_ir` gains a keyword-only parameter
> `env: frozenset[str] = frozenset()`. A volume guard whose `scope_trail` or `condition` mentions a
> zero-argument call `f()` that the evaluator cannot interpret is **conditional on `f`**; a conditional
> guard may emit `SAFE` and `UNKNOWN` but **never `WILL_FAIL`** unless `f`'s name is a member of `env`.
> A `T`-evaluating conditional guard with `f ∉ env` emits `UNKNOWN` with reason
> `volume_tracking_unasserted`.
>
> **`env` defaults to empty and `check_graph`'s two-positional-argument signature does not change**
> (`plr-sema/src/plr_sema/check/__init__.py:713`), so every existing test, every existing fixture and
> the whole tier-1 replay are unaffected by construction — which is what makes this additive rather
> than a re-baselining.
>
> **The harness asserts the hypothesis by observation, not by typing it.** `plr-sema/eval/` already
> imports from the verifier's package at runtime (`plr-sema/eval/oracle_common.py:698-702`), so after
> the verifier establishes its configuration the harness **calls**
> `pylabrobot.resources.volume_tracker.does_volume_tracking()` (`volume_tracker.py:21-22`) and passes
> `env = {"does_volume_tracking"}` iff it returns `True`. The name reaching `env` is read from the
> guard's own text on one side and from the callable's `__name__` on the other; **no string is typed
> into `plr_sema` or into the harness**, which is why this costs no registry row.

`f`'s other live instance is `not op.resource.tracker.is_disabled` (`liquid_handler.py:1033`), a
*per-tracker* flag rather than a process-global one. It is handled by the same rule — it is an
uninterpretable conjunct, so it makes the guard conditional — and it is recorded as an assumption
rather than observed, because the harness can observe a module-level function and cannot observe every
tracker instance.

### 13.2.7 The assumptions, named so a reviewer can attack them

| id | assumption | why it is needed | what breaks if it is false | oracle |
|---|---|---|---|---|
| **A-VOLUME-TRACKING** | when `"does_volume_tracking"` ∈ `env`, tracking was on for the whole walk | `WILL_FAIL` claims the guard was reached | a `WILL_FAIL` on a run that never evaluated the guard. `no_volume_tracking()` is a context manager (`volume_tracker.py:25-30`) the analyzer cannot see, exactly as §10.1.3's `use_channels` manager | tier 3's volume mutants (0 unsound gate) and tier 1's 0-unsound gate over 525 operations (`outputs/plr-sema/oracle_replay_260903_rebaseline.json:10-11`) |
| **A-TRACKER-ENABLED** | no cell's tracker was individually disabled | `liquid_handler.py:1033`'s `not …is_disabled` conjunct is uninterpreted; a disabled tracker skips the call | a `WILL_FAIL` where the tracker was disabled. `VolumeTracker.disable` (`volume_tracker.py:58-60`) has no `LiquidHandler` caller in the corpus's executed path | the same two |
| **A-NO-CORRECTION** | the volume PLR charges a cell is the literal the kwarg carries | V2 adds and subtracts the kwarg literal verbatim | an interval that drifts from the real one, in either direction, after the first corrected transfer. PLR's `vols` are `[float(v) for v in vols]` at `liquid_handler.py:968` — no liquid-class correction is applied on this path at the current pin, which is why the assumption discharges today and would not under a backend that applied one | tier 1 + tier 3; a drift shows up as an unsound row, not as a silent skew, because the oracle compares against the executed raise |
| **A-COMMIT-VOLUME** | a committed transfer equals a pending one for the abstraction | V2 reads `get_used_volume()`, which returns `pending_volume` (`volume_tracker.py:114-116`), while `commit` copies it to `volume` (`:140-146`) and `rollback` restores it (`:148-151`) | an interval that reflects a rolled-back operation. `aspirate` commits or rolls back every touched tracker in one block (`liquid_handler.py:1058-1064`), which is A-COMMIT's own argument (§10.2.2) transposed to volume — and the rollback path only runs when the backend raised, which A-COMPLETES already scopes out | tier 3's volume mutants |
| **A-TIP-CELL** | a tip cell's interval is `TOP` unless the tip family says the channel is `HAS_TIP` | the tip cell's identity is the mounted tip | nothing in the `SAFE` direction: an unknown tip cell is `TOP` and every guard on it is ½. Recorded because it is the one place the two families are coupled, and a later change to either could decouple them silently | AC-13.10's tip-cell assertion |

### 13.2.8 Seeding, and why it reuses increment 3's scaffolding precedent

An executed corpus row starts with wells that already contain liquid. The harness computes those
seeds itself — `_precondition_plan` returns a `seed_volumes` dict (`plr-sema/eval/oracle_common.py:
690-696`; the aspirate branch builds `dict(zip(sources, vols))` at `:733-739`) and
`row_to_verifier_inputs` puts it in `deck_layout` at `:983-989`. **That dict is a harness artifact and
is not in the extractor's graph**, so a `check_graph` on real extracted source sees no seeds and every
cell is `TOP` at entry. That is correct and is not a defect.

For the *oracle*, the two sides must describe one execution, which is §12.1.6's argument for lowering
the scaffolding `setup()` call. The same remedy applies:

> **Normative.** For each `(cell, volume)` in the row's `deck_layout.seed_volumes`, the caller in
> `plr-sema/eval/` prepends a `CALL` to the derived volume-setting method — `VolumeTracker.set_volume`
> at the current pin (`volume_tracker.py:66-72`, which writes both `volume` and `pending_volume`) —
> with the cell as receiver and the seed as a `Lit` kwarg, **before** the scaffolding reset, with
> `origin` the string `"seed"`. It is emitted **by the caller**, not synthesised inside `lower_calls`,
> which stays a pure function of its input sequence. The method is selected by P7's own accessor pass
> (a method assigning the anchored field from a parameter, unconditionally, at statement position),
> not named in our source.

**This is why no `IR_VERSION` bump is needed.** The alternative — a `seed` operand on `RESOURCE` — is
a wire change and a bump, and would additionally have to carry `max_volume` to be worth having, which
is §13.12's deferred item. A prepended `CALL` reuses an opcode, a lowering path and an `origin`
convention that all shipped in increment 3 and are pinned by AC-12.3.

### 13.2.9 The oracle: two mutant classes and a fixture set

**Tier 3 (mutants).** `plr-sema/eval/tip_mutants.py`'s pattern generalises exactly, and the reason it
generalises is a property of the existing code that must be stated because the whole construction
depends on it: `row_to_verifier_inputs` is called on the **base** row and its `deck_layout` — seeds
included — is carried into the mutant unchanged (`plr-sema/eval/tip_mutants.py:238-247`, where
`example` is built from the base row's three outputs and the mutators at `:167` then edit only
`example["call_sequence"]`). So a mutant that *raises* an aspirate volume over-draws against a seed
computed from the **unmutated** call, and genuinely raises. Had the seeds been recomputed from the
mutant, the mutation would be self-cancelling and the class would measure nothing — which is the same
trap `_shift_tip_ref`'s docstring records for m2 (`tip_mutants.py:127-140`).

> **Normative.** Two classes, in a new `plr-sema/eval/volume_mutants.py`:
> **v1 (`v1_overdraw_aspirate`)** multiplies the last `aspirate`'s `volume_ul` so it exceeds the
> base row's seed for that source; expected exception `TooLittleLiquidError`.
> **v2 (`v2_overdraw_transfer`)** does the same to a `transfer`'s `volume_ul`; expected exception
> `TooLittleLiquidError`.
> Both reuse `run_one_mutant`'s shape (`tip_mutants.py:170-224`), which is refactored to take the
> mutator and the expected exception as arguments rather than reading the module globals `_MUTATORS`
> (`:167`) and `_EXPECTED_EXC` (`:69`). **The refactor must not move the m1/m2 numbers**, and AC-13.12
> gates that as a non-regression against the committed
> `outputs/plr-sema/tip_mutants_260903_4938.json`.
>
> **No over-fill mutant class is specified**, because §13.2.2 makes an over-fill `WILL_FAIL`
> unreachable; a class whose gate can only ever be `0 of n` is a class that measures the spec's own
> scope decision rather than the implementation, and would be deleted at the first cleanup.

**Tier 2b (executed fixtures).** The region fixture set (`plr-sema/eval/fixtures/regions/`, 11 fixtures
at `outputs/plr-sema/tier2b_260903.json:7`) gains volume fixtures: one straight-line over-draw, one
over-draw at the second iteration of a proved-trip loop, and one loop whose per-iteration draw is safe
individually and exhausts the well collectively — the last being the case that distinguishes a real
interval domain from a per-operation check. The existing `region_unsound = 0` and
`region_will_fail_fired = 3` (`tier2b_260903.json:8-9`) become the floor, not the target.

---

## 13.3 #4922 — the content-addressed report cache

### 13.3.1 What is already built, and what is not

Increment 2 §11.3.3 defined `cache_key = (bytecode_hash, contracts_sha, surface_identity,
ir_version)`, and **the function already exists**: `plr_sema.check.ir.cache_key`
(`plr-sema/src/plr_sema/check/ir.py:918-926`) takes a bytecode, a `contracts_json` string and a stamp
and returns the four-tuple, with `bytecode_hash` at `:909-915` over `IR_HASH_PREFIX + canonical_text`
(`:906`). §11.5 named the store interface as the missing half. So this item is a *store* for a *key*
that is already computed, tested and hashed — the reverse of #4932's producer/consumer situation, and
correspondingly smaller.

### 13.3.2 The correctness argument, which is a purity argument and has one non-obvious half

> **Normative (the purity premise).** `check_ir(bytecode, contracts, receiver_states, env=…)` is a
> pure function of its arguments (`plr-sema/src/plr_sema/check/__init__.py:443-445`, plus §13.2.6's
> `env`). Nothing it reads is outside them: it does no I/O, imports no `pylabrobot`, and reads no
> clock, environment variable or global. **A cache is sound iff its key determines every argument.**
>
> - `bytecode_hash` determines `bytecode` up to the canonical form, which is everything `check_ir`
>   reads: §11.3.2 excludes only `sideband`, and `sideband` is by §11.1.4's disposition invariant the
>   **S** class — "carried, never hashed, never read by `check_ir`".
> - `contracts_sha` is a sha256 of the **whole `contracts_json` string** `check_graph` is handed
>   (§11.3.3), and `receiver_states` is a top-level key of that same document —
>   `_check` reads `contracts_payload.get("receiver_state", {})` and
>   `contracts_payload.get("contracts", {})` from one parsed object
>   (`plr-sema/src/plr_sema/check/__init__.py:686-691`). So one hash covers both arguments. This is
>   load-bearing and is easy to break: a key computed over the `contracts` *sub-dict* would not cover
>   `receiver_state`, and a table regenerated with a changed `entry_reset` or a changed volume anchor
>   would silently reuse stale findings.
> - `surface_identity` and `ir_version` answer "which PLR tree" and "which encoding" and are already
>   in the key.
> - **`env` is not in the key and must be**, since §13.2.6 makes it a real input. It is added as a
>   fifth component, `tuple(sorted(env))`.

**The non-obvious half: the cache must store the *pre-relabel* findings.** `_check` calls `check_ir`
and then `ir.relabel_findings(raw_findings, origin)` (`check/__init__.py:691-693`), mapping each
finding's `operation_id` from `str(pc)` to the graph's own operation id through `sideband["origin"]`.
**`sideband` is excluded from `bytecode_hash`** (§11.3.2). Therefore two different graphs — the same
program with different `OperationNode` ids — share a `bytecode_hash` and have *different* origin maps.
Storing post-relabel findings would return the first graph's operation ids for the second graph: a
silently wrong report, not a cache miss.

> **Normative.** The cache stores the **`check_ir` output, before relabelling**. On a hit, the caller
> relabels with **its own** `sideband["origin"]`, joins, and assembles the `AnalysisReport` with its
> own `protocol_fqn` and its own `stamp` — which is exactly the design position §11.3.2 recorded for
> `protocol_fqn` and which §11.12's Q3 left open. **Q3 is hereby answered: findings, not reports, and
> pre-relabel findings specifically.**

**Telemetry is part of the observable behaviour and must not be skipped.** `check_graph` "emits every
finding via `plr_sema.telemetry`" (`check/__init__.py:713-719`). A hit that returned findings without
emitting them would make the cache observable, which would falsify the purity claim the cache rests
on. The emit therefore happens on the cached findings, on the hit path, unchanged.

### 13.3.3 The store

> **Normative.** `CacheStore` is a small class in a new module `plr_sema/check/cache.py`, stdlib-only
> (the §6.2 packaging fact is untouched):
>
> ```python
> class CacheStore:
>     def __init__(self, root: Path) -> None: ...
>     def get(self, key: tuple) -> tuple[Finding, ...] | None: ...
>     def put(self, key: tuple, findings: tuple[Finding, ...]) -> None: ...
>     def invalidate_by_methods(self, methods: frozenset[str]) -> int: ...
> ```
>
> - **Location.** `root` defaults to `plr-sema/.cache/` — inside the package tree, gitignored, and
>   **never `$TMPDIR` or a system temp dir**. A cache under a temp dir is silently emptied between
>   runs, which turns a persistence bug into a performance mystery.
> - **Layout.** One JSON file per entry, at `root/<sha256(canonical_key)>.json`, where `canonical_key`
>   is `json.dumps(key, sort_keys=True, separators=(",", ":"), ensure_ascii=False)` — the same
>   canonicalisation §11.3.1 item 6 already uses, so there is one serialisation convention in the
>   package and not two.
> - **Entry.** `{"key": <the five components, as JSON>, "created": <ISO-8601 UTC>, "findings":
>   [<Finding as the wire form already defines>], "methods": [<sorted distinct CALL.method in the
>   bytecode>]}`. The key is stored **in the entry** as well as in the filename so a hash collision or
>   a filename-truncating filesystem is a loud mismatch rather than a wrong answer: `get` compares the
>   stored key to the requested key and treats a mismatch as a miss.
> - **`methods`** is what makes §13.3.4's targeted invalidation possible and is the only field that is
>   not either the key or the payload.
> - **No eviction policy.** Entries are removed only by `invalidate_by_methods` or by deleting the
>   directory. An LRU or a size cap is a real requirement the moment this runs in CI over a large
>   corpus, and it is deferred (§13.12) rather than guessed at.
>
> **Read-through is opt-in.** `check_graph` gains a keyword-only `cache: CacheStore | None = None`,
> defaulting to `None`. **With the default, no file is read, no file is written, and no directory is
> created** — so the existing test suite stays pure and hermetic, and a test that wanted to exercise
> the cache has to say so. `check_ir` itself is **not** given a cache parameter: it is the pure core
> the cache's soundness argument is about, and giving it a cache would make the premise circular.

### 13.3.4 Invalidation on a pin bump

A pin bump changes `surface_identity`, so **every** entry misses — correct, and free. The interesting
case is the one the dispatch names: a contract table regenerated at the *same* pin (a derivation fix,
as in #4938's `_constructor_state` repair, §12.13) changes `contracts_sha` and therefore also misses
everything, which is correct but wasteful when one method's guards moved.

> **Normative.** `invalidate_by_methods(methods)` deletes every entry whose stored `methods` list
> intersects `methods`, and returns the count. The caller computes `methods` by **diffing two contract
> tables**: the set of keys `receiver.method` whose contract entry differs between them, compared over
> the canonical JSON of the entry. A key present in one table and absent from the other counts as
> changed.
>
> **This is a tool, not an automatic mechanism, and the distinction is deliberate.** Nothing calls it
> during `check_graph`. It is exposed as `python -m plr_sema.check.cache --old A.json --new B.json
> --root plr-sema/.cache` and is for the human who regenerated a table and does not want to discard a
> corpus-sized cache. **A bug in the diff produces a stale hit — a wrong answer — whereas a bug in the
> "miss everything" path produces only slowness**, so the safe default (miss everything, via
> `contracts_sha`) is the one that runs unattended, and the sharp tool is the one a human invokes.

### 13.3.5 The fork-D drift test guards the pin half

`surface_identity` is only a real guard if the pin literal it is compared against is itself pinned.
That is HM-23 — `EXPECTED_SUBMODULE_PIN` in `plr-sema/tests/test_fork_drift.py`, a `FROZEN` row at
declared 1 (`plr-sema/src/plr_sema/_hand_maintained.py:754-768`). **No change is needed to it**, and
saying so is the point: the cache adds a consumer of the pin identity, and a reviewer should be able to
see that the existing drift test already covers the new consumer rather than having to check. AC-13.8
asserts the coverage rather than assuming it — a cache entry written at the expected pin and read back
after the stamp's pin is perturbed must miss.

---

## 13.4 #4883 — the derived inert-name filter, and the registry finding the dispatch did not expect

### 13.4.1 What is there today

`_is_inert_dropped_receiver_call` (`plr-sema/src/plr_sema/derive/__init__.py:884-905`) is a
three-clause predicate over a full receiver-qualified call expression:

1. the head — text before the first `.` — is in `_INERT_RECEIVER_PREFIXES`, a hand-typed frozenset of
   **nine** entries: `logger`, `logging`, `warnings`, `inspect`, `args`, `kwargs`, `sig`,
   `backend_kwargs`, `default` (`:868-871`);
2. the head is capitalized, i.e. a call on a class object rather than an instance (`:902-903`) —
   **already derived**, and its comment already makes the right argument: *"this rule generalizes past
   any one PLR class name rather than hand-naming `Coordinate`"*;
3. the tail — text after the last `.` — is in `_INERT_CALL_SUFFIXES`, a hand-typed frozenset of
   **eleven** entries: `keys`, `items`, `values`, `union`, `join`, `append`, `get`, `update`,
   `format`, `strip`, `split` (`:878-881`).

The predicate gates the two published `top_unresolved.dropped_receiver` worklist views
(`:940` and `:1011`), which are deferred item (e)'s worklist. T14 found the tables miss stdlib noise:
`asyncio.sleep`, `time.time`, `struct.*`, `bytes.*`, `contextlib.*` all pass clause 1 (their heads are
not listed) and clause 2 (lowercase) and clause 3 (their tails are not listed), so they rank as real
unresolved receivers.

### 13.4.2 The derivation

> **Normative.** Clause 1 is **replaced** by: the head is a member of `sys.stdlib_module_names`, or the
> head is a module-level import alias resolving to such a member in the file the `dropped_calls` entry
> came from. Clause 2 is **kept unchanged** — it is already derived and already carries its argument.
> Clause 3 is **replaced** by: the tail is an attribute of a builtin container or `str`/`bytes` type,
> i.e. `tail in set().union(*(dir(t) for t in (dict, list, set, tuple, str, bytes)))`, excluding
> dunders.
>
> `_INERT_RECEIVER_PREFIXES` and `_INERT_CALL_SUFFIXES` are **deleted**, not left in place as a
> fallback. A retained fallback would make the derivation unfalsifiable: every entry the derived rule
> missed would be silently covered by the list, and nobody would ever learn which rule was doing the
> work.

`sys.stdlib_module_names` is a frozenset shipped by CPython since 3.10 (the package's
`requires-python`, main spec §1.1) and is a fact about **Python**, not about PLR — so it cannot go
stale when PLR changes, which is the `breaks_when` question §9.1 makes every hand-maintained row
answer. The same is true of `dir(dict)`.

**Both replacements strictly extend the shipped behaviour, and both must be measured rather than
assumed.** Of the nine typed prefixes, `logging`, `warnings` and `inspect` are stdlib module names and
are covered; `logger`, `args`, `kwargs`, `sig`, `backend_kwargs` and `default` are **local variable
names** and are **not**. So the derived rule is not a superset of the typed one, and AC-13.1 requires
the before/after ranking to be published rather than asserted — the same "show the ranked view before
and after filtering" discipline the existing `filtered=False` path was built for (`:926-932`).

> **Normative (what happens to the six uncovered locals).** They are **not** re-added by any means.
> `logger.debug` is caught by nothing after this change and will re-enter the ranking. That is the
> correct outcome and is the reason the item is worth doing: the ranking exists to be *read*, and a
> filter that hides `logger.debug` by naming it hides the fact that the derivation cannot see it. The
> honest remedy — resolving a local's type from its assignment (`logger = logging.getLogger(…)`) — is a
> real dataflow pass, is named in §13.12, and is not attempted here. AC-13.1 publishes the resulting
> ranking movement in both directions so the cost is visible rather than absorbed.

### 13.4.3 The registry arithmetic, and the dispatch's premise is false

The dispatch asked which registry row this retires, and predicted 24 → 23 live with headroom 1.
**There is no such row.** Searched: `_hand_maintained.py` contains no occurrence of
`_INERT_RECEIVER_PREFIXES` or `_INERT_CALL_SUFFIXES`, and the §9.2 inventory table's 25 rows
(HM-1 … HM-25, main spec `260901_plr-sema-pre-corpus-spec.md:2351-2375`) name no dropped-receiver
filter. The surface was introduced by round-5 T0 item 4 — after the §9.2 inventory was written — and
was never registered.

Under §9.4's own vocabulary this is **discovery**, not growth: *"registering pre-existing surface that
was always there but unregistered"*. §9.4 permits discovery to re-baseline the cap **once**, at T9,
and that re-baseline has been spent. So the position is:

- **Registering it** would need a 25th row against `BUDGET_CAP = 24` — a cap conversation, for a
  surface that is about to be deleted.
- **Deriving it** means it never needs one. Two hand-typed sets totalling **20 strings** leave the
  codebase, counting against §9.4's ≥82-facts shrink target, and the row that would have been added is
  never added.

> **Normative.** #4883 adds no registry row, retires no registry row, and moves no cap. `live_rows()`
> stays **24**, `BUDGET_CAP` stays **24**, headroom stays **0**. **The lid and volume families get no
> headroom from this item**, and §13.2.4's per-row ceiling bumps are the mechanism they use instead.
> AC-13.2 asserts the deletion and the unchanged registry together, so that a fixer cannot satisfy the
> item by adding a row and calling it registered.

---

## 13.5 #4946 — delegate-call literal channel binding

### 13.5.1 The measured gap, and what is already working

`#4938`'s AC-12.4 gate asked for m1 ≥ 50 of 55 and got **84 `will_fail` of 101 raised-as-expected,
with 17 `unknown` and 0 unsound** (`outputs/plr-sema/tip_mutants_260903_4938.json:9-16`) — 83%
against a 91% bar. §12.13 records that *"all 17 misses collapse to a lone `transfer` call whose
derived guard is `guard_predicate_unparsed`"* and files the residual as #4946. The #4946 fixer's own
run (commit `92f97256`, `outputs/plr-sema/tip_mutants_260903_4946.json:9-16`) reports **the identical
numbers** — 84 `will_fail`, 17 `unknown`, m2 190/190 (`:24-29`), `gate_passed` true (`:34`).
**That is the point: #4946 diagnosed the residual and did not move it.** The report is this item's
*baseline*, not its result, and any reading of it as a result would conclude the bar is unreachable.

**Delegation inheritance is not the gap.** `LiquidHandler.transfer`'s contract entry already carries
the bridged tip guard: `plr-sema/data/derived_contracts.json:58363` opens the entry and its
`channel_guards` list at `:58364-58383` holds one guard — `condition: "self._tip is None"`,
`depth: 1`, `raises: "NoTipError"`, sited at `tip_tracker.py:65` `TipTracker.get_tip`, with
`via: "self.head[channel].get_tip"`. P4's bridge, inherited through `delegates_to`, works exactly as
§10.2.6 says it does. (The same entry inherits `dispense`'s `BlowOutVolumeError` guards at
`:58449-58483`, whose `scope_trail` carries `"if does_volume_tracking()"` — independent corroboration
of §13.2.6's claim that the flag is visible to the analyzer as a scope, not only as a conjunct.)

**The gap is the channel set.** `transfer`'s signature
(`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1273-1283`) declares `source`,
`targets`, `source_vol`, `ratios`, `target_vols`, `aspiration_flow_rate`, `dispense_flow_rates` and
`**backend_kwargs` — **no `use_channels`**, and no `tip_spots`/`resources` either — and its body
contains no P3a idiom, which §10.2.3 already records (*"`LiquidHandler.transfer` … gets no channel-set
derivation and is handled by rule 4 of §10.1.3: `channels = ⊤`"*). So §10.3.1's fourth
interpretability criterion — *"`op`'s channel set is exact"* — fails, the bridged guard folds to ½,
and the finding is `UNKNOWN`. The state is known; the channel it applies to is not.

**But the channels are literals, at the delegate call sites** (`liquid_handler.py:1347-1361`):

```python
await self.aspirate(resources=[source], vols=[sum(target_vols)],
                    flow_rates=[aspiration_flow_rate], **backend_kwargs)          # :1347-1352
dispense_flow_rates = dispense_flow_rates or [None] * len(targets)                # :1353
for target, vol, dfr in zip(targets, target_vols, dispense_flow_rates):           # :1354
  await self.dispense(resources=[target], vols=[vol], flow_rates=[dfr],
                      use_channels=[0], **backend_kwargs)                         # :1355-1361
```

The `dispense` call names `use_channels=[0]` outright. The `aspirate` call does not, but passes
`resources=[source]` — a **one-element literal list** in `aspirate`'s own P3a channel-default
parameter (§10.2.3 measured `aspirate → resources`), so PLR's own three-term disjunction
(`use_channels = use_channels or self._default_use_channels or list(range(len(resources)))`) yields
`[0]`. Both channel sets are decidable from the caller's AST alone.

### 13.5.2 The rule

> **Normative (P9, delegate-call channel binding).** Let `K` be a contract entry on receiver class
> `R` that carries a `channel_guards` entry `g` inherited from a delegate `D` — i.e. `g` reached `K`
> through a `delegates_to` hop to `R.D` rather than through a depth-0 bridge in `K`'s own body. Let
> `S` be the set of `ast.Await`/`ast.Call` expressions in `K`'s own body (**depth 0**, excluding
> nested function and lambda definitions) whose callee is an `ast.Attribute` on `self` naming `D`.
> Then `g` acquires a **bound channel set** `bound_channels(g)` computed as:
>
> 1. **`S` must be a singleton.** If `K`'s body awaits `D` zero times or more than once,
>    `bound_channels(g)` is `⊤`. Two call sites can disagree, and picking one is the "two views of one
>    fact" case §10.5 rule 1 dispositions as *a reason to know less*.
> 2. **Explicit.** If the single call site passes `use_channels=<E>` where `<E>` is an `ast.List` or
>    `ast.Tuple` display whose every element is an `ast.Constant` of type `int`, then
>    `bound_channels(g)` is that list of ints, **exact**.
> 3. **Arity default, P3a re-applied at the call site.** Else, if `D` has a P3a
>    `channel_default_param` `q` (§10.2.3) and the call site passes `q=<E>` where `<E>` is an
>    `ast.List` or `ast.Tuple` **display** of length `n ≥ 1`, then `bound_channels(g)` is
>    `[0 … n-1]`, **exact**. *The elements need not be resolvable* — only the display's length is
>    read, which is the same length-without-contents property §11.1.2 makes `Seq` the load-bearing
>    value form for. This is P3a's own `list(range(len(<q>)))` production evaluated one frame up, at
>    the site that supplies `<q>`, rather than inside `D` where `<q>` is opaque.
> 4. **Disabler poisoning still applies.** If any method in P3b's `channel_default_disablers` set
>    appears anywhere in the graph on the receiver, `bound_channels(g)` is `⊤` — rule 2 of §10.1.3 is
>    unchanged and is checked *after* 2 and 3, never before.
> 5. **Otherwise `⊤`.** A `**kwargs` forward, a name, a comprehension, a starred argument, a
>    non-`int` constant, an empty display, or a `q` the call site does not pass at all — every one of
>    these widens.
>
> **The binding is per-guard, not per-operation.** `channels_for_call` is **unchanged** and still
> returns `⊤` for a `transfer` operation; §10.3.1's criterion 4 is re-read to accept, for a guard
> carrying a `bound_channels`, that bound set in place of the operation's own. A guard with no
> `bound_channels` is evaluated exactly as today.
>
> **E2 is not extended.** A bound channel set makes a guard *evaluable*; it does **not** give
> `transfer` a tip *effect*. §10.2.6's depth-0-only effect rule stands, `transfer` still reaches
> `TipTracker` mutators only through delegates, and E4.2 still widens the receiver after the call.
> This is deliberate: reading a state through a delegate is sound from the caller's AST, but claiming
> a post-state through one requires knowing the delegate ran to completion on every channel, which is
> a different and larger claim.

**Why the `for` loop around the `dispense` call does not defeat rule 1.** The call at `:1355-1361` is
lexically single — one `ast.Await` in `K`'s body — and its `use_channels=[0]` operand is a constant
display, so the bound set is iteration-invariant by construction: every iteration binds the same
`[0]`. Rule 1 counts **syntactic call sites**, not dynamic invocations, and that is the right count
here precisely because the operand carries no comprehension target. A call site whose channel operand
*did* mention a loop variable falls to rule 5 and widens, because the operand would not be a constant
display. This is stated because it is the first thing a reviewer will test.

**Soundness.** Rules 2 and 3 assert only what PLR's own resolution asserts, over syntax the caller
literally contains, and every non-matching shape widens — and widening can only destroy a verdict
(§10.5's argument, unchanged). The one new claim is that PLR's three-term disjunction is
faithfully mirrored when its **first** term is present (rule 2) or **absent and the third decides**
(rule 3); the second term is `self._default_use_channels`, which rule 4 handles by the existing
poisoning mechanism rather than by a new one.

### 13.5.3 Provenance, payload, and no hand-typed names

`bound_channels` is an additive key on an existing `channel_guards` entry — no new block, no
`schema_version` bump, read through `.get()` with a `None` default so a pre-increment table degrades
to today's `⊤` behaviour:

```jsonc
"channel_guards": [
  {"condition": "self._tip is None", "via": "self.head[channel].get_tip",
   "bound_channels": {"channels": [0], "rule": "arity_default", "delegate": "aspirate",
                      "site_lineno": 1347},        // NEW -- absent when P9 yields Top
   "…": "every other key unchanged"}]
```

The gap ledger's `tip_state` block gains a `bound_channels` entry per contract key, valued with the
derived record or the strings `"absent"` / `"ambiguous"` / `"widened"` and the rule that widened it —
the same visible-absence discipline §10.2.2 established for `tipstate_anchor` and §12.1.3 for
`entry_reset`. **Every name in the record is read from PLR:** `"aspirate"` is the callee of an
`ast.Attribute` on `self`, `"use_channels"` and `"resources"` come from P3a's own measured map, and
`1347` is a line number. AC-13.15(iii) asserts this with the AST literal scan AC-10.9 established.

### 13.5.4 What this does and does not reach

The 17 residual m1 rows are rows whose call sequence collapses to a lone `transfer`
(§12.13). P9 makes the `aspirate`-delegated `NoTipError` guard evaluable on channel 0 for every one
of them, so a mutant that removed the preceding `pick_up_tips` — leaving `default = NO_TIP` from the
scaffolding reset (§12.1.4) — fires `WILL_FAIL` at the `transfer` index. **The gate is therefore
directional and is set at m1 ≥ 92 of 101**, which is 9 of the 17 recovered rather than all 17: some
of the 17 may fail for a second reason the residual analysis did not separate, and a gate set at
101/101 would be a prediction rather than a threshold. AC-13.15(iv) requires the per-mutant residual
to be published if the bar is missed, so a shortfall is diagnosed rather than merely reported.

**`transfer` is the only method this reaches at the current pin, and that must be measured rather
than assumed.** P9 applies to any inherited `channel_guards` entry, and the fixer publishes the full
selected set — every `(K, delegate, rule, channels)` tuple P9 binds — so a second beneficiary shows
up in the artifact instead of in a surprise.

---

## 13.6 Soundness claims and the oracle that checks each

Every claim this increment makes, and the thing that would catch it being wrong. A claim with no
oracle is a claim this document is not entitled to make.

| claim | § | oracle |
|---|---|---|
| a paired `(cell, amount)` under-draw guard evaluating `T` really raises | 13.2.5 | tier 3's v1/v2 mutants (`WILL_FAIL` at the raised index, 0 unsound) and tier 1's 0-unsound gate over 525 operations |
| a paired under-draw guard evaluating `F` really does not raise, **whether or not tracking is on** | 13.2.6 | tier 1 (every executed row runs clean under the scaffolding, so any `SAFE` that was wrong is an unsound row) + AC-13.11's tracking-off fixture |
| the over-fill half is genuinely undecidable and is not quietly guessed | 13.2.2 | AC-13.10's assertion that an `add_liquid`-derived guard yields `volume_state_unknown` for **every** fixture, including one whose interval would decide it if a capacity were assumed |
| V2's interval arithmetic tracks the real used volume across a sequence | 13.2.5 | tier 2b's collective-exhaustion loop fixture, whose per-iteration draws are individually safe |
| V4's `TOP` widening terminates the fixpoint on an infinite-height lattice | 13.2.5 | AC-13.10's `while`-loop volume fixture: `check_ir` converges within `K` passes and does not raise |
| A-VOLUME-TRACKING, A-TRACKER-ENABLED, A-NO-CORRECTION, A-COMMIT-VOLUME, A-TIP-CELL | 13.2.7 | the per-row entries in that table |
| the volume exception set is `{TooLittleLiquidError, TooLittleVolumeError}` and is derived | 13.2.1 | AC-13.9(ii): the unfiltered `volume_state` set has 4 members and the module conjunct selects 2, asserted against the taxonomy artifact, plus an AST literal scan finding no `ast.Constant` equal to either class name in `plr-sema/src/` |
| the lid family emits nothing, and a `null`-condition guard is not a definite failure | 13.1.3 | AC-13.4, which asserts both the zero-lid-findings property and the `null`-condition non-firing directly |
| a delegate call site's literal channel argument really is the channel PLR uses | 13.5.2 | **tier 3's existing m1 class** — the gate moves 84 → ≥ 92 of 101 with 0 unsound in both directions, and a mis-bound channel shows up as a `WILL_FAIL` where the simulator ran clean, which m1 already counts (`tip_mutants.py:205-211`) |
| binding a channel does **not** license a tip effect for the caller | 13.5.2 | AC-13.15(ii): an operation *after* the `transfer` yields `channel_state_unknown`, so E4.2's widen is still in force |
| P9 selects only where the caller's AST decides, and widens everywhere else | 13.5.2 | AC-13.15(i)'s five-shape negative fixture set, each shape asserted to yield `⊤` |
| a cache hit returns exactly what a miss computes | 13.3.2 | AC-13.5's hit/miss equality over every shipped fixture |
| a cache hit is correct for a *second* graph sharing a bytecode hash | 13.3.2 | AC-13.6, the pre-relabel storage assertion — the one case where a plausible implementation is silently wrong |
| a moved pin misses | 13.3.5 | AC-13.8 |
| the derived inert filter changes the published ranking in both directions and hides nothing | 13.4.2 | AC-13.1's before/after publication |

---

## 13.7 Hand-maintained impact

**New registry rows: zero. Retired registry rows: zero.** `live_rows()` is 24
(`plr-sema/src/plr_sema/_hand_maintained.py:851-855` — `RETIRED` rows do not count, and HM-8 is the
only one) against `BUDGET_CAP = 24` (`:43`). **Headroom: 0, before and after.**

**Two per-row ceilings move, and both are loud one-line diffs, not row additions:**

| row | today | after | what the new pattern is |
|---|---|---|---|
| **HM-24** (`_hand_maintained.py:781-814`), tip-typestate channel-receiver bridge shape, `metric="patterns"`/`declared=1`/`status="CAPPED"` at `:793-795` | live 1 | **live 2, declared 2** | the volume bridge `<name>.<field>.<attr>.<method>` (§13.2.4). `_measure_hm24` (`:244-261`) asserts `_BRIDGE_SHAPE_RE.groups == 3` on the *tip* regex and is unaffected; the volume regex gets its own measure, asserted the same way |
| **HM-25** (`:815-847`, the same three fields at `:828-830` with `declared=5`), tip-typestate front-end syntactic patterns | live 5 | **live 8, declared 8** | P7's accessor-anchor shape and P8's zip-comprehension pairing idiom (§13.2.4), **plus P9's delegate-call channel-argument shape (§13.5.2)** |

**P9 is the third pattern on HM-25 and takes it 7 → 8, and it carries the identical argument to P7's
and P8's**: it is a syntactic pattern over *how PLR is written* — a keyword argument at a
`self.<delegate>(…)` call site holding an int-constant display, or a display in the delegate's own
P3a parameter — not a fact PLR records about itself. Its `breaks_when` is that PLR stops passing the
channel literally at the call site (e.g. `transfer` computes `use_channels` into a local first), and
it **fails closed**: `bound_channels` goes to `⊤`, the guard reverts to ½, and the m1 gate falls back
toward 84/101 — fewer verdicts, never a wrong one. That failure is caught loudly by AC-13.15(iv)'s
gate rather than silently, which is the HM-25 half of the HM-24/HM-25 split (§10.10 Q7) working as
designed.

Per §9.3, `test_no_surface_exceeds_its_declared_size` turns red on live 6 against declared 5, and the
fixer must edit `declared` in a reviewable commit — which is the whole mechanism. Per §9.4, growth
never raises the **row-count** cap, and neither of these does.

**`REASON_VOCABULARY` (HM-14): 8 → 10 of cap 12** (`plr-sema/src/plr_sema/verdict.py:129-154`; the row
is `CAPPED` at declared 12, `_hand_maintained.py:553-557`, so live 10 ≤ 12 and **no `declared` edit is
needed**). Two members, each naming a distinct give-up point in the sense §0's second consequence
requires:

- **`volume_state_unknown`** — a guard parsed as a volume `Cmp` atom, but the cell's interval is `TOP`
  (or the capacity is, which is always). Cannot fold into `channel_state_unknown`: that reason names a
  *channel*, and a volume cell is a well or a tip, keyed differently and widened by different rules.
  Cannot fold into `guard_predicate_unparsed` for §10.8's own reason — the parse stage returned
  something and the evaluation stage did not.
- **`volume_tracking_unasserted`** — the atom evaluated to `T` but the guard is conditional on a
  callable not in `env` (§13.2.6). This is a *third* stage: parse succeeded, evaluation succeeded, and
  the **hypothesis** was not available. Without it a consumer cannot distinguish "I do not know the
  volume" from "I know it over-draws but cannot prove tracking was on", and those are the two
  different things a user would do two different things about.

**No `lid_state_unknown` member.** §13.1 emits no lid finding, so a member for it would be vocabulary
with no producer — dead data of exactly the kind §12.1.4 spent an argument discharging for
`ChannelState.default`. It is added by whichever increment fires the lid family, and not before.

**What could have been hand-typed, and what it is instead:**

| what could have been typed | what it is instead |
|---|---|
| `{"TooLittleLiquidError", "TooLittleVolumeError"}` as a class-name list | the two-conjunct taxonomy filter `category == "volume_state" AND module == "pylabrobot.resources.errors"` (§13.2.1), reusing the module literal AC-10.9 already declares. 4 members → 2 |
| `"get_used_volume"` / `"get_free_volume"` / `"pending_volume"` as accessor names | P7 reads them off the guards' own `ast.Compare` operands (§13.2.4) |
| a per-method map from resource parameter to volume parameter (`aspirate → (resources, vols)`) | P8's zip-comprehension pairing over `liquid_handler.py:1007-1028`, which is where PLR itself states the pairing |
| `"does_volume_tracking"` as an environment key | the harness **calls** `does_volume_tracking()` (`volume_tracker.py:21-22`) and reads the callable's own name (§13.2.6). No string in `plr_sema`, none in the harness |
| a default well capacity or nominal tip volume, to make the over-fill half decidable | **nothing.** The half stays ½ (§13.2.2) |
| `"ValueError"` plus a site filter, to select the lid family | **nothing.** The family is not adopted (§13.1.3) |
| a `{"LiquidHandler.transfer": [0]}` channel map, or `"use_channels"`/`"aspirate"` as literals in our source | P9 reads the callee off an `ast.Attribute` on `self` and the keyword off P3a's own measured `channel_default_param` map (§13.5.3). AC-13.15(iii) scans for both strings |
| a cache eviction policy tuned to the corpus | no policy at all; explicit invalidation only (§13.3.3) |
| 9 receiver prefixes + 11 call suffixes | `sys.stdlib_module_names` and `dir(dict)`-class attributes — facts about **Python** (§13.4.2). 20 strings deleted |

**HM-21 (X dispositions): unchanged at live 3.** This increment reads no new upstream field and moves
no field into or out of `X`. `RESOURCE`'s operand set does not change, which is the same statement as
"no `IR_VERSION` bump".

**Wire format: no change.** `Verdict`, `Finding`, `PlrSite`, `AnalysisReport`, `join`,
`SCHEMA_VERSION`, `derived_contracts.json`'s `schema_version: 1` and `IR_VERSION = 2` are all
unchanged. `volume_guards` and the per-class volume block are new optional keys read through `.get()`;
`env` and `cache` are keyword-only parameters with defaults that reproduce today's behaviour exactly.

---

## 13.8 Acceptance criteria

Written so that none can be satisfied while the property is false. Where a criterion could be passed by
a stub, the stub-defeating half is named.

- **AC-13.1 (the inert filter is derived, and the ranking movement is published in both directions).**
  `_is_inert_dropped_receiver_call` classifies `asyncio.sleep`, `time.time`, `struct.pack` and
  `contextlib.suppress` as inert and `self.head[channel].get_tip`,
  `op.resource.tracker.remove_liquid` and `op.tip.tracker.add_liquid` as **not** inert. The gap
  ledger's `top_unresolved.dropped_receiver` view is regenerated and the run publishes **three**
  numbers: entries newly filtered, entries newly admitted, and the resulting rank of
  `self.head[channel].get_tip`. The newly-admitted count must be **> 0** and must include
  `logger.debug` — the stub-defeating half, because an implementation that quietly kept the typed
  prefix list as a fallback would report 0 there (§13.4.2).
- **AC-13.2 (the deletion is real and the registry does not grow).** An AST scan of
  `plr-sema/src/plr_sema/derive/__init__.py` finds no module-level assignment named
  `_INERT_RECEIVER_PREFIXES` or `_INERT_CALL_SUFFIXES` and no `ast.Constant` string equal to any of
  their twenty former members; and `len(live_rows()) == 24` with `BUDGET_CAP == 24`, asserted after
  the change, so the item cannot be satisfied by registering the surface instead of deriving it.
- **AC-13.3 (the lid facts are derived and published, and nothing is claimed from them).** The gap
  ledger gains a `lid_state` block naming, per candidate class: the `Liddable` anchor candidates found
  (expected: `has_lid` as a **method**, not a property, so the P2 anchor is `"absent"`), the state
  fields found (expected: **none**), and the two `_check_no_lid`-derived guard conditions with their
  `raises` (expected: `"lidded is resource"`/`ValueError` and `null`/`ValueError`). Each expectation is
  asserted against the shipped `plr-sema/data/derived_contracts.json` rather than against a fixture,
  because §13.1's whole argument is about real PLR at this pin.
- **AC-13.4 (the lid family emits nothing, and the `null`-condition landmine is pinned).** For a graph
  whose operations are `setup()` then `aspirate(use_channels=[0])` on a plate: **zero** findings carry
  a `plr_site` whose `file` is `liquid_handler.py` and whose `lineno` is `116` or `117` with a verdict
  other than `Verdict.UNKNOWN`; and the finding for the `:117` guard — the one whose derived
  `condition` is `null` — is `Verdict.UNKNOWN` with reason `guard_predicate_unparsed`, **not**
  `WILL_FAIL`. The second half is the stub-defeating one: an evaluator that read a `null` condition as
  "raises unconditionally" would pass the first half and fail the second.
- **AC-13.5 (a hit equals a miss).** For every shipped graph fixture, `check_graph(g, c)` and
  `check_graph(g, c, cache=store)` called twice in a row produce reports whose `findings` tuples are
  equal element-wise and whose `verdict` is equal; the second call's store reports a hit; and with
  `cache=None` (the default) **no file is created and no directory is created** under
  `plr-sema/.cache/` or anywhere else, asserted by comparing a directory listing before and after.
- **AC-13.6 (the stored findings are pre-relabel, and a second graph proves it).** Two graph payloads
  that differ **only** in their `OperationNode` ids lower to the same `bytecode_hash`; running the
  first with a cold cache and the second against the now-warm cache yields, for the second, findings
  whose `operation_id`s are the **second** graph's ids. An implementation that stored post-relabel
  findings returns the first graph's ids and fails. A third assertion pins the key's coverage: two
  contract tables differing only in their `receiver_state` block produce **different** cache keys
  (§13.3.2), which a key computed over the `contracts` sub-dict alone would not.
- **AC-13.7 (targeted invalidation deletes what changed and only what changed).** Given two contract
  tables differing in exactly one entry (`LiquidHandler.aspirate`), `invalidate_by_methods` computed
  from their diff deletes every cached entry whose bytecode contains an `aspirate` `CALL` and **zero**
  entries whose bytecode does not; the returned count equals the number deleted; and a subsequent
  `get` on a deleted key is a miss while a `get` on a retained key is a hit.
- **AC-13.8 (a moved pin misses, and the drift test covers it).** An entry written with a stamp at
  `EXPECTED_SUBMODULE_PIN` is a **miss** when read with a stamp whose `surface_pin` differs by one
  character; `plr-sema/tests/test_fork_drift.py` passes unmodified; and HM-23's row is unchanged at
  `FROZEN`/declared 1.
- **AC-13.9 (the volume passes select the measured set, published not assumed).** Re-running
  `plr_sema.derive` emits, in `receiver_state`, a volume block for `VolumeTracker` with used-volume
  accessor `get_used_volume`, free-volume accessor `get_free_volume` and field `pending_volume`; and
  `contracts["LiquidHandler.aspirate"]["volume_guards"]` contains exactly two entries, one raising
  `TooLittleLiquidError` with `via == "op.resource.tracker.remove_liquid"` and `cell_param ==
  "resources"`, `amount_param == "vols"`, the other raising `TooLittleVolumeError` with `via ==
  "op.tip.tracker.add_liquid"`. Three sub-assertions: (i) the emitted values equal the above;
  (ii) the unfiltered taxonomy set `category == "volume_state"` has **4** members and the module
  conjunct selects exactly `{TooLittleLiquidError, TooLittleVolumeError}`, asserted against
  `training/verify/data/plr_exception_taxonomy.json`, so the narrowing is exercised rather than
  incidental; (iii) an AST literal scan of `plr-sema/src/` finds no `ast.Constant` string equal to
  `"get_used_volume"`, `"get_free_volume"`, `"pending_volume"`, `"TooLittleLiquidError"`,
  `"TooLittleVolumeError"`, `"resources"` or `"vols"`.
- **AC-13.10 (the interval domain decides one half and provably declines the other).** Four fixtures,
  each with a prepended seed `CALL` (§13.2.8). (a) seed 100, `aspirate(vols=[200])` → exactly one
  `Finding` with `verdict is Verdict.WILL_FAIL`, `category == "precondition_state"`, `plr_site ==
  PlrSite("external/pylabrobot/pylabrobot/resources/volume_tracker.py", 92,
  "VolumeTracker.remove_liquid")`. (b) seed 100, `aspirate(vols=[50])` → a `Verdict.SAFE` finding at
  the same site. (c) the same graph with `vols` lowering to `Top` → `Verdict.UNKNOWN` with reason
  `volume_state_unknown`. (d) **the declining half**: `dispense(vols=[10_000])` into a seeded well
  yields `Verdict.UNKNOWN` with reason `volume_state_unknown` at the `add_liquid` site — never
  `WILL_FAIL` — because the capacity is `TOP`; and a tip cell on a channel whose `TipState` is not
  `HAS_TIP` likewise yields `volume_state_unknown` (A-TIP-CELL). A fifth fixture, a `while` loop
  whose body aspirates a literal volume, asserts `check_ir` converges within `K` passes, does not
  raise, and leaves every cell in the region `TOP` after the region's `END` (V4). (d) is the
  stub-defeating half: an implementation that assumed a default capacity passes (a)–(c) and fails (d).
- **AC-13.11 (the tracking hypothesis gates `WILL_FAIL` only, and defaults to unasserted).** AC-13.10's
  fixture (a), run through `check_ir` with the default `env == frozenset()`, yields `Verdict.UNKNOWN`
  with reason `volume_tracking_unasserted` — **not** `WILL_FAIL` — while fixture (b)'s `SAFE` is
  **unchanged** by `env`, in both directions. `check_graph(g, c)` with two positional arguments
  compiles, runs and returns the identical report it returns today for every shipped fixture. The
  `SAFE`-unchanged half is what distinguishes this from a blanket "no volume verdicts without `env`"
  rule, and is the whole content of §13.2.6's asymmetry argument.
- **AC-13.12 (tier 3 — the volume mutants fire, and the tip mutants do not regress).**
  `plr-sema/eval/volume_mutants.py` reports **v1 ≥ 60 of the rows that raised as expected** carrying a
  static `WILL_FAIL` at the index the simulator raised, with **0 unsound** in both directions, and v2
  reported with its own achieved number (no threshold — `transfer`'s guard is
  `guard_predicate_unparsed` today, §12.13's #4946). And, as a non-regression over the committed
  `outputs/plr-sema/tip_mutants_260903_4938.json`: m1 stays at **84 `will_fail` / 17 `unknown` of 101
  raised-as-expected** (`:9-14`) and m2 at **190 of 190** (`:24-29`), with `gate_passed` still true
  (`:34`) — the run-one-mutant refactor (§13.2.9) is what could move these, and this is what catches it.
- **AC-13.13 (tier 2b — executed volume ground truth, including the collective case).** The three new
  region fixtures (§13.2.9) are executed against the chatterbox deck under the verifier's
  configuration and compared on `(operation, iteration)`: **zero** unsound rows; the straight-line
  over-draw and the second-iteration over-draw each carry a static `WILL_FAIL` at the `(operation,
  iteration)` the execution raised; and the **collective-exhaustion** fixture — per-iteration draws
  individually safe, cumulatively over the seed — carries a static `WILL_FAIL` at the iteration the
  execution raised, **not** at the first iteration and **not** nowhere. The existing
  `region_unsound == 0` and `region_will_fail_fired >= 3`
  (`outputs/plr-sema/tier2b_260903.json:8-9`) still hold. The collective case is the stub-defeating
  half: a per-operation check that never accumulates passes the first two and fails this one.
- **AC-13.14 (this document is machine-checked).** `plr-sema/tests/test_spec_lint.py` gains a
  `SPEC_INCREMENT_4` entry alongside `SPEC_INCREMENT_3`, and both the citation checker and the
  AC-gating half of the cross-reference checker report **zero** failing violations over this file.
- **AC-13.15 (delegate-call channel binding is derived, selective, and moves the gate).** Four
  sub-assertions. (i) **Selectivity, from both sides.** Re-running `plr_sema.derive` emits, on
  `contracts["LiquidHandler.transfer"]["channel_guards"][0]`, a `bound_channels` record with
  `channels == [0]`, `delegate == "aspirate"` and `rule == "arity_default"` — the rule-3 path, since
  the `aspirate` call site passes no `use_channels` (`liquid_handler.py:1347-1352`) — and the fixer
  publishes the **complete** set of `(K, delegate, rule, channels)` tuples P9 binds over the whole
  contract table, not only `transfer`'s. Against five synthetic caller fixtures — two depth-0 awaits
  of the same delegate; a `**kwargs` forward; a bare `ast.Name` in `use_channels`; a starred
  argument; and a delegate-parameter display of length 0 — P9 yields `⊤` in **all five** and the
  ledger records the widening rule for each. A rule-2 fixture passing `use_channels=[1, 3]` binds
  exactly `[1, 3]`, and a rule-4 fixture in which a P3b disabler appears on the receiver yields `⊤`
  **despite** an explicit `use_channels=[0]` at the call site — the ordering half, which an
  implementation that checked the disabler first or not at all would fail.
  (ii) **Binding a channel grants no effect.** On a fixture whose operations are `setup()`,
  `pick_up_tips(use_channels=[0])`, `transfer(...)`, then `aspirate(use_channels=[0])`: the
  `transfer` operation carries a `Verdict.SAFE` finding for the bridged guard sited at
  `PlrSite("external/pylabrobot/pylabrobot/resources/tip_tracker.py", 65, "TipTracker.get_tip")`,
  and the **following** `aspirate` yields `channel_state_unknown` — E4.2 still widens the receiver
  after a delegate-only method (§10.2.6). An implementation that extended E2 passes the first half
  and fails the second.
  (iii) **No hand-typed names.** An AST literal scan of `plr-sema/src/` finds no `ast.Constant`
  string equal to `"transfer"`, `"aspirate"`, `"dispense"` or `"use_channels"`.
  (iv) **The gate, directional, with a published residual.** Tier 3's existing m1 class reports
  **≥ 92 of 101** raised-as-expected rows carrying a static `WILL_FAIL` at the index the simulator
  raised, with **0 unsound** in both directions; **m2 stays 190 of 190**; and tier 1 is byte-identical
  to `outputs/plr-sema/oracle_replay_260903_rebaseline.json`. If the bar is missed, the run publishes
  the **per-mutant residual** — base id, the operation the simulator raised at, the static reason
  emitted there, and P9's `bound_channels` value for that guard — so a shortfall is diagnosed rather
  than reported. The baseline this must move is 84 `will_fail` / 17 `unknown`
  (`outputs/plr-sema/tip_mutants_260903_4946.json:9-16`, identical to `…_4938.json:9-16`), and the
  directional half is that a binding which never fires cannot reach 92.
---

## 13.9 Task rows

Ordering is forced in three places and free elsewhere: **#4883 lands first** because it is the only
item that touches the derivation's shared filter and it must not land under a merge with #4881b's and
#4946's new passes; **#4881b then #4946 land last, in that order**, because they share HM-25 and each
bumps its `declared` (5 → 7, then 7 → 8) — landing them out of order or concurrently makes the ratchet
red for a reason a reviewer would misattribute, and the second commit's diff would silently absorb the
first's. #4922 is independent of all four.

| task | scope | files | gate | ~LOC | depends on | model |
|---|---|---|---|---|---|---|
| **#4883** | Derived inert-name filter (§13.4.2): replace clause 1 with `sys.stdlib_module_names` + import-alias resolution, keep clause 2 unchanged, replace clause 3 with builtin-container attribute membership, **delete** both frozensets; regenerate the gap ledger and publish the three ranking numbers of AC-13.1 including the newly-admitted `logger.debug`; assert the registry is unchanged at 24 live | modify `plr-sema/src/plr_sema/derive/__init__.py`, `plr-sema/tests/test_derive.py`, `plr-sema/tests/test_hand_maintained_ratchet.py`, `plr-sema/data/gap_ledger.json` (regenerated) | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_derive.py -q`; `uv run pytest plr-sema/tests/test_hand_maintained_ratchet.py -q`; then `uv run python -m plr_sema.derive --survey-json training/verify/data/plr_preconditions.json --taxonomy-json training/verify/data/plr_exception_taxonomy.json --out $TMPDIR/contracts_4883.json --gap-ledger plr-sema/data/gap_ledger.json` and publish the before/after ranking — satisfying **AC-13.1**, **AC-13.2** | ~130 | — | Sonnet — the ranking movement is a measurement, and the newly-admitted count is the finding |
| **#4881a** | Lid family, derivation-and-ledger only (§13.1): the `lid_state` gap-ledger block recording the absent P2 anchor, the absent state fields, and the two `_check_no_lid` guard conditions with their `raises`; **no** `LidState`, **no** `receiver_state` entry, **no** `Finding` construction, **no** new `REASON_VOCABULARY` member; plus the negative fixture and the `null`-condition assertion | modify `plr-sema/src/plr_sema/derive/__main__.py`, `plr-sema/src/plr_sema/derive/receiver_state.py`, `plr-sema/tests/test_derive.py`, `plr-sema/tests/test_check_graph.py`; create `plr-sema/tests/fixtures/lidded_plate_aspirate_graph.json` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_derive.py -q`; `uv run pytest plr-sema/tests/test_check_graph.py -q` — satisfying **AC-13.3**, **AC-13.4** | ~120 | #4883 | Sonnet — the four blockers must be re-verified against the pin and published, not copied from this document |
| **#4922** | The content-addressed cache (§13.3): `plr_sema/check/cache.py` with `CacheStore.get`/`.put`/`.invalidate_by_methods`, `plr-sema/.cache/` as the default root (never `$TMPDIR`), the entry carrying key + `created` + **pre-relabel** findings + `methods`; `env` added as the key's fifth component; read-through in `_check` behind `check_graph`'s new keyword-only `cache=None`, with telemetry emitted on the hit path; the `python -m plr_sema.check.cache` diff-and-invalidate entry point; `.gitignore` for the cache dir | create `plr-sema/src/plr_sema/check/cache.py`, `plr-sema/tests/test_cache.py`; modify `plr-sema/src/plr_sema/check/__init__.py`, `plr-sema/src/plr_sema/check/ir.py`, `.gitignore` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_cache.py -q`; `uv run pytest plr-sema/tests/test_check_graph.py -q`; `uv run pytest plr-sema/tests/test_fork_drift.py -q` — satisfying **AC-13.5**, **AC-13.6**, **AC-13.7**, **AC-13.8** | ~330 | — | Sonnet — the pre-relabel storage argument is the one place a plausible implementation is silently wrong |
| **#4881b** | The volume family (§13.2), in this order: (1) P7 + P8 + the volume bridge in `derive/`, with both fail-closed cases and the `volume_anchor` ledger value; (2) the `volume_guards` block and the per-class volume block in the payload; (3) the interval domain and V0–V4 in a new `check/volumestate.py` plus its wiring in `check/__init__.py`; (4) `env` and the two new `REASON_VOCABULARY` members; (5) `plr-sema/eval/` prepends the seed `CALL`s with `origin == "seed"` and observes `does_volume_tracking()` at runtime; (6) `volume_mutants.py` and the `run_one_mutant` parameterisation; (7) the three tier-2b volume fixtures; (8) **HM-24 declared 1 → 2 and HM-25 declared 5 → 7 in `_hand_maintained.py`, each with its own `why_not_derived`/`breaks_when` sentence extended** | create `plr-sema/src/plr_sema/check/volumestate.py`, `plr-sema/eval/volume_mutants.py`, `plr-sema/eval/fixtures/regions/volume_*.py`, `plr-sema/tests/fixtures/volume_{overdraw,safe,top,overfill,while}_graph.json`; modify `plr-sema/src/plr_sema/derive/receiver_state.py`, `plr-sema/src/plr_sema/derive/__main__.py`, `plr-sema/src/plr_sema/check/__init__.py`, `plr-sema/src/plr_sema/verdict.py`, `plr-sema/src/plr_sema/_hand_maintained.py`, `plr-sema/eval/oracle_common.py`, `plr-sema/eval/tip_mutants.py`, `plr-sema/eval/region_oracle.py`, `plr-sema/tests/test_{derive,check_graph,verdict,hand_maintained_ratchet}.py`, `plr-sema/data/derived_contracts.json` (regenerated) | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_derive.py -q`; `uv run pytest plr-sema/tests/test_check_graph.py -q`; `uv run pytest plr-sema/tests/test_verdict.py -q`; `uv run pytest plr-sema/tests/test_hand_maintained_ratchet.py -q`; then `uv run python -m plr_sema.derive --survey-json training/verify/data/plr_preconditions.json --taxonomy-json training/verify/data/plr_exception_taxonomy.json --out plr-sema/data/derived_contracts.json --gap-ledger plr-sema/data/gap_ledger.json`; then `uv run python plr-sema/eval/volume_mutants.py --corpus training/assemble/out/corpus_p25.jsonl --examples-dir training/examples --contracts plr-sema/data/derived_contracts.json --report $TMPDIR/volume_mutants.json`; `uv run python plr-sema/eval/tip_mutants.py --corpus training/assemble/out/corpus_p25.jsonl --examples-dir training/examples --contracts plr-sema/data/derived_contracts.json --report $TMPDIR/tip_mutants_regression.json`; `uv run python plr-sema/eval/region_oracle.py --fixtures plr-sema/eval/fixtures/regions --contracts plr-sema/data/derived_contracts.json --report $TMPDIR/tier2b_volume.json` — satisfying **AC-13.9**, **AC-13.10**, **AC-13.11**, **AC-13.12**, **AC-13.13** | ~780 | #4883, #4881a | Sonnet — every published number is a measurement, and the v1 gate is directional |
| **#4946** | Delegate-call literal channel binding (§13.5): P9 in `derive/receiver_state.py` — the singleton-call-site rule, the explicit `use_channels` int-display path (rule 2), P3a re-applied at the call site over a length-`n` display (rule 3), P3b disabler poisoning checked **after** both (rule 4), and `⊤` for every other shape (rule 5); the additive `bound_channels` key on a `channel_guards` entry and the ledger's `bound_channels` value with its widening rule; §10.3.1 criterion 4 re-read to accept a guard's bound set in place of the operation's; **`channels_for_call` unchanged and E2 not extended**; the five negative fixtures plus the rule-2 and rule-4 fixtures; the AST literal scan; artifact regenerated and the full selected `(K, delegate, rule, channels)` set published | modify `plr-sema/src/plr_sema/derive/receiver_state.py`, `plr-sema/src/plr_sema/derive/__main__.py`, `plr-sema/src/plr_sema/check/tipstate.py`, `plr-sema/tests/test_{derive,tip_typestate,check_graph}.py`, `plr-sema/data/derived_contracts.json` (regenerated), `plr-sema/src/plr_sema/_hand_maintained.py` (**HM-25 `declared` 7 → 8**); create `plr-sema/tests/fixtures/transfer_after_pickup_graph.json` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_derive.py -q`; `uv run pytest plr-sema/tests/test_tip_typestate.py -q`; `uv run pytest plr-sema/tests/test_check_graph.py -q`; `uv run pytest plr-sema/tests/test_hand_maintained_ratchet.py -q`; then `uv run python -m plr_sema.derive --survey-json training/verify/data/plr_preconditions.json --taxonomy-json training/verify/data/plr_exception_taxonomy.json --out plr-sema/data/derived_contracts.json --gap-ledger plr-sema/data/gap_ledger.json`; then `uv run python plr-sema/eval/tip_mutants.py --corpus training/assemble/out/corpus_p25.jsonl --examples-dir training/examples --contracts plr-sema/data/derived_contracts.json --report $TMPDIR/tip_mutants_4946.json` and `uv run python plr-sema/eval/oracle_replay.py --corpus training/assemble/out/corpus_p25.jsonl --contracts plr-sema/data/derived_contracts.json --report $TMPDIR/replay_4946.json` — satisfying **AC-13.15** | ~260 | #4883, #4881b | Sonnet — the m1 number is a measurement and the residual analysis is diagnostic |
| **T23** | Lint and index: add `SPEC_INCREMENT_4` to `plr-sema/tests/test_spec_lint.py`'s two parametrised live-spec tests; regenerate `.praxia/docs/INDEX.md` | modify `plr-sema/tests/test_spec_lint.py`; regenerate `.praxia/docs/INDEX.md` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_spec_lint.py -q` — satisfying **AC-13.14** | ~15 | — | Haiku |

**Honest sizing note.** **#4881b at ~780 is well past one session and must be split**, and the split
point is stated here rather than left to whoever runs out of context: **sub-steps (1)–(2) — the
derivation and the payload — land first and leave the tree green on their own**, because `check/`
reads the new blocks through `.get()` with empty defaults and therefore ignores them entirely until
(3) lands; sub-steps (3)–(5) are the evaluator; (6)–(8) are the oracle and the registry diff.
**Do not split (3) from (4)**: an evaluator that can construct `WILL_FAIL` before `env` exists to gate
it is unsound for the duration of the gap, and "we will add the gate in the next commit" is exactly the
sequencing that ships it. **Do not split (6) from (8)** either: the ceiling bumps are what make the
ratchet green, and a commit that adds patterns without them is red for a reason a reader will
misdiagnose. #4922's ~330 is the most trustworthy number on the table — the key already exists
(`ir.py:918-926`) and the store is a file per entry — and #4881a's ~120 is the least interesting, since
most of its work is verification rather than code. **#4946's ~260 is a single session and should not
be split**, but its risk is not its size: seven of its LOC are P9's five rules and the rest is the
seven fixtures that pin them, and a fixer under pressure will be tempted to ship rules 2 and 3 without
1, 4 and 5. AC-13.15(i) exists to make that fail, and it is the sub-assertion to run first rather than
last.

---

## 13.10 What this changes in increments 1–3

Seven normative amendments, listed so a reader of the earlier documents is not misled by text this one
supersedes. None changes any increment's *design*.

**In the main spec (`260901_plr-sema-pre-corpus-spec.md`):**

1. **§Open decisions 2's sunset clause has expired, and this increment is the one that spends it.**
   Its resolution reads *"leave numeric atoms at ½ through v1 and the first post-corpus increment"*
   (`:92`). Increments 1, 2 and 3 have all shipped, so the reservation no longer holds anything back,
   and §13.2 reopens it **for exactly one class of atom**: a `Cmp` in a guard raising a taxonomy
   `volume_state` exception from `pylabrobot.resources.errors`, evaluated against §13.2.3's interval
   domain. **Every other numeric `Cmp` still folds to ½** — including `drop_tips`'s
   `tip.tracker.get_used_volume() > 0 and (not allow_nonzero_volume) and does_volume_tracking()`
   (`training/verify/data/plr_preconditions.json:50077-50080`), which is a **compound** condition and
   is excluded by §10.3.1's single-atom criterion, not by its numerics. The decision's own reversibility
   claim — *"it touches one grammar production … and nothing on the wire"* — is confirmed: nothing on
   the wire changes.
2. **§Open decisions 2's `SoundnessScope` prerequisite is discharged by narrowing, not by building
   it.** The text holds that *"any definite volume verdict needs a `SoundnessScope` record … before it
   can be honest"*. §13.2.6 shows the requirement applies to the `WILL_FAIL` direction only, and meets
   it with a runtime-observed `env` argument that defaults to unasserted. `SoundnessScope` as a wire
   record remains unbuilt and remains deferred row (b).

**In `260902_plr-sema-tip-typestate-increment.md` (spec_version 9):**

3. **§10.9's first bullet, "Volume atoms — every numeric `Cmp` stays ½ … Volume also needs a
   `SoundnessScope` record"**, is superseded by items 1 and 2 above. Its *second* clause — that tip
   state does not need such a record — is unchanged and is still true.
4. **§10.1.1's "finite-height and needs no widening operator"** is narrowed to the tip lattice, which
   is what it was always about. §13.2.3's interval lattice has infinite height and §13.2.5's V4 is its
   widening operator. The two domains do not interact except through A-TIP-CELL.
5. **§10.3.1's fourth interpretability criterion — *"`op`'s channel set is exact"* — is re-read over
   the guard, not only the operation** (§13.5.2). A `channel_guards` entry carrying a P9
   `bound_channels` set is interpreted against *that* set; a guard without one is unchanged. §10.2.3's
   observation that *"`LiquidHandler.transfer` … gets no channel-set derivation and is handled by
   rule 4 of §10.1.3: `channels = ⊤`"* stays **literally true of the operation** — `channels_for_call`
   is not touched — and stops being the end of the story for its inherited guards. §10.2.3's closing
   sentence, *"making `transfer` precise requires modelling a method body"*, is narrowed: it requires
   modelling a method body's **call sites**, which is strictly less, and §13.5.2 rules 1 and 5 are
   what keep it less.

**In `260902_plr-sema-ir-bytecode-increment.md` (spec_version 10):**

6. **§11.12's Q3 — "whether the cache stores findings or reports" — is answered**, and more narrowly
   than the question was posed: it stores **pre-relabel** findings, and §13.3.2 gives the reason
   (`sideband.origin` is outside the hash). §11.3.2's design position — *"#4922 caches the `Finding`
   tuple, and the caller reassembles the report"* — is confirmed and sharpened.
7. **§11.3.3's cache key gains a fifth component**, `tuple(sorted(env))`, because §13.2.6 introduces a
   real input the four-tuple does not cover. `plr_sema.check.ir.cache_key`
   (`plr-sema/src/plr_sema/check/ir.py:918-926`) gains the corresponding keyword-only parameter with an
   empty default, so an existing caller's key is unchanged.

**And in increment 3 (`260903_plr-sema-real-programs-increment.md`, spec_version 11):** §12.11's first
bullet — *"the volume and lid guard families (#4881's other mutation classes) … unchanged from
increment 1 §10.9"* — is **superseded for volume** (§13.2) and **reaffirmed for lid, on new evidence**
(§13.1): the family is still not adopted, but for four specific reasons rather than by inheritance.

---

## 13.11 Effect on the oracle plan (`260902_plr-sema-oracle-harness.md`)

- **Tier 3's existing m1 class acquires a moving gate and becomes #4946's oracle.** The plan's tier-3
  row records m1 as measuring the tip family's directional reach; §13.5 makes it the *only* evidence
  that a delegate-bound channel is the right channel, so the row should say which item each threshold
  belongs to — 84/101 is #4938's achieved number and ≥ 92/101 is #4946's gate, over the same class and
  the same corpus. A single unlabelled "m1" threshold in the plan will be read as a property of the
  tip family rather than of a binding rule, which is exactly the misreading §13.5.1 had to correct
  about `tip_mutants_260903_4946.json`.
- **Tier 3 gains a second module.** `plr-sema/eval/volume_mutants.py` sits alongside `tip_mutants.py`
  with two classes, v1 and v2 (§13.2.9). The plan's tier-3 description — mutate a clean corpus row,
  execute, compare the static verdict at the raised index — is unchanged in every respect except the
  mutation and the expected exception. The plan should say which module produces which classes, since
  "tier 3" is now two runs with two reports and two gates.
- **Tier 2b gains three fixtures**, inside the existing region fixture set rather than as a new tier —
  the same argument §12.10 makes for not adding a fifth input class. The `[result_schema]` of
  `plr-sema/eval/tier2_extractor.bth.toml` gains `volume_fixtures`, `volume_unsound` and
  `volume_will_fail_fired`, mirroring the region fields it already publishes.
- **The plan's "which families are firing and which are still armed" sentence gains a second entry,
  and it must be written with the asymmetry visible.** The volume family is firing for under-draw and
  armed-but-structurally-silent for over-fill; a plan that recorded "volume: firing" would be read as
  claiming an over-fill capability that §13.2.2 proves does not exist.
- **Tier 1 is unchanged and must stay unchanged.** `check_graph`'s default `env` is empty and its
  default `cache` is `None`, so the replay's committed numbers — 330 executed, 525 operations,
  0 unsound, 0 totality violations, agreement 1.0
  (`outputs/plr-sema/oracle_replay_260903_rebaseline.json:2-18`) — must be reproduced **byte-identically**
  after every task in §13.9. That is the cheapest possible regression detector for five items that all
  touch the derivation or the checker, and it costs one existing command.

---

## 13.12 Explicitly not in this increment

- **Lid verdicts.** §13.1's disposition. The named trigger is the precondition survey recording an
  early-`return` guard scope.
- **A capacity operand on `RESOURCE`.** This is what would make the over-fill half decidable
  (§13.2.2), and it is a wire change plus an `IR_VERSION` bump plus an upstream extractor change to
  read `Container.max_volume`/`Tip.maximal_volume` off the labware definition. Increment 3 took its
  bump when it was free (§12.2.7); this one is not free, and buying it for one guard direction is not
  obviously worth it. Named with its cost, not deferred silently.
- **Liquid-class corrections.** A-NO-CORRECTION assumes none is applied. PLR at this pin applies none
  on the aspirate path (`liquid_handler.py:968`); a backend that did would need a correction model in
  V2, which is a different increment.
- **The 96-head's volume cells.** `head96` is excluded from the tip family (§10.9) and its tip cells
  are therefore excluded here by A-TIP-CELL, with no separate rule.
- **`BlowOutVolumeError`.** Excluded by the module conjunct (§13.2.1 fact 4); it guards a
  `LiquidHandler` instance field, not a tracker cell.
- **Cache eviction.** No LRU, no size cap, no TTL (§13.3.3). Required the moment this runs unattended
  over a corpus; guessing a policy now would be tuning against a workload nobody has measured — which
  is the same reason #4923 is a no-go below.
- **Single-hop passthrough effects, still.** §13.5's P9 binds a *channel set* for a guard inherited
  through `delegates_to`; it does **not** give the caller the delegate's *effect*, so §10.2.6's named
  follow-up — recovering `discard_tips`/`return_tips` without recovering `move_tips` — is untouched
  and `transfer` still widens its receiver after the call (§13.5.2, AC-13.15(ii)). The two are easy to
  conflate because both are about reading a delegate from its caller, and the asymmetry is the point:
  a precondition read through a call site is sound from syntax, a post-state is not.
- **Resolving a local's type from its assignment** — the pass that would recover `logger.debug` after
  §13.4.2 deletes the prefix list. A real dataflow pass; named, not attempted.
- **A `pred`-aware `BRANCH`.** Still §12.3.6's B2, still the natural next increment.
- **Precision targets.** Deferred (f) stands. AC-13.12's v1 number is a *directional* gate on one
  mutation class, not an `UNKNOWN`-rate threshold.

### 13.12.1 Go/no-go: #4923, incremental re-check — **NO-GO**

**Decision criterion.** Incrementality earns its complexity iff, *after* #4922 ships, a whole-corpus
re-check following a contract-table regeneration still costs more than ~60 s of **check** time — check
only, excluding execution and excluding the extractor subprocess.

**The measurement does not exist, and this is the finding.** No committed artifact records a
check-only wall time. `outputs/plr-sema/oracle_replay_260903_rebaseline.json`'s `summary_flat`
(`:2-18`) has no timing field at all. The only two committed timings measure something else:
`outputs/plr-sema/tier2a_260903.json:16` reports `elapsed_seconds: 89.256` for 330 rows, which
includes executing every row against the simulator **and** an out-of-process extractor invocation per
row (§12.4.1), so it is an upper bound on the check cost by an unknown and probably large factor; and
`outputs/plr-sema/tier2b_260903.json:14` reports `6.069` for 11 fixtures, which is too small a
population to extrapolate. **The threshold therefore cannot be evaluated today, and a go decision
taken now would be taken on no data.**

**Two further reasons the answer is no even before the measurement.** First, **#4922 absorbs the case
#4923 targets.** The dominant re-check workload is "the same programs, again" — a corpus replay after
a derivation fix — and a content-addressed cache answers that with a file read. What is left for
incrementality is only the *changed-prefix* case: a program edited in the middle, where a prefix of the
bytecode is shared. That case does not arise in a corpus replay at all; it arises in an editor loop
that does not exist. Second, **increment 3 already recorded that unrolling breaks #4923's memo point**:
§12.11 notes that a `pc` inside an unrolled region has one prefix hash per iteration, so the
per-instruction memo §11.5 hooked is no longer unique and #4923 would have to define what it means
first. That is design work with no measured payoff.

**Recommendation: no-go.** Re-open only after (a) `plr-sema/eval/oracle_replay.py` publishes a
check-only elapsed field — a ~5-line change that should be folded into whichever task next touches the
replay — and (b) the post-#4922 residual exceeds the threshold.

### 13.12.2 Go/no-go: #4924, error-recovery interpreter — **NO-GO**

**Decision criterion.** The interpreter is worth building iff a pass produces state a re-planner can
act on. The dispatch states the precondition as "a pass produces real state"; **that precondition is
already met and is not the right one.** The tip family produces real state today: 84 of 101
raised-as-expected m1 mutants carry a `WILL_FAIL` at the raised index with zero unsound rows
(`outputs/plr-sema/tip_mutants_260903_4938.json:9-16`). If "a pass produces real state" were the test,
#4924 would already be a go. The sharper precondition is: **the state must answer the questions a
re-planner asks**, and a liquid-move re-planner asks two — *"where is there enough liquid to draw
from"* and *"where is there room to put it"*.

**This increment answers the first and provably cannot answer the second.** §13.2.2 makes the
over-fill half undecidable at the current wire format, so an interpreter re-planning a dispense would
have to choose a destination with no capacity information — i.e. re-plan into exactly the failure class
it is recovering from, and do so with a `WILL_FAIL` it is not entitled to construct. That is worse than
not re-planning.

**The minimum this increment would have to deliver, and does not.** #4922's cache (delivered) plus a
volume family whose **over-fill half is decidable** (not delivered, and blocked on the `RESOURCE`
capacity operand, §13.12). §11.5's own hook — the `(pc, concrete state, abstract state)` triple — is
untouched and remains available; the pc join it rests on is unchanged by this increment.

**Recommendation: no-go.** Revisit when the capacity operand lands, which is a decision about the wire
format and not about the interpreter.

---

## 13.13 Open questions for the adversarial round

Six, and the first three are the ones where a design was chosen over a live alternative rather than
found.

1. **§13.2.4's per-row ceiling bumps, and whether increment 3 was right.** Increment 3 §12.1.2 declined
   a sixth HM-25 pattern on the grounds that zero *row* headroom makes it "a cap conversation". §13.2.4
   argues that conflates the row-count cap with a per-row ceiling and that bumping HM-24 to 2 and HM-25
   to 8 is ordinary, loud growth under §9.3. **A reviewer who holds increment 3's stricter line should
   say so plainly, because the consequence is not a redesign — it is that the volume family does not
   land in this increment at all**, since P7, P8 and the volume bridge are all irreducibly new
   syntactic surface. **This question now decides two items, not one**, and the second is the awkward
   one: §13.5's P9 is a third HM-25 pattern, and it is the only thing in this increment that moves an
   *already-missed* gate (m1 84/101 against a 91% bar, unmoved since #4938). Under the stricter
   reading, the reviewer is choosing to leave a known-failing gate failing in order to hold a ceiling —
   which may still be the right call, but should be made with that framing visible rather than as a
   side effect of a rule about the volume family. This is the single question that decides whether
   §13.2 and §13.5 ship.
2. **§13.2.2's capacity asymmetry.** The over-fill half is declined because `max_volume` is labware
   geometry. A reviewer may hold that a family which decides one of its two directions is worse than no
   family — that it invites a reader to believe volume is "handled" — or, conversely, that the capacity
   operand should simply be taken now with an `IR_VERSION` bump, since the bump is cheap while nothing
   is cached and expensive once #4922 has populated a cache. **That second framing is the strongest
   argument against this document's own sequencing** and it deserves a direct answer, because #4922
   and the deferred bump are in the same increment and land in the wrong order for it.
3. **§13.2.6's `env` mechanism.** A runtime-observed environment hypothesis, passed as a parameter with
   an empty default, is deliberately the smallest thing that could work, and it is *not* the
   `SoundnessScope` record main spec deferred row (b) reserves machinery for. Three sub-questions:
   (a) is "observe the flag in the harness and pass a name" honest, or is it a hypothesis smuggled in
   as an observation, given that the observation happens once and the walk covers a whole program?
   (b) should `env` be in the report — a consumer reading a `WILL_FAIL` cannot currently tell which
   hypotheses it rests on — which would be a wire change this document declines to make; (c) should
   A-TRACKER-ENABLED be handled by the same mechanism rather than left as an assumption, given that it
   is per-instance and therefore not observable the same way?
4. **§13.1's non-adoption.** The lid family is specified and not adopted, and the fixer is nonetheless
   asked to build a ledger block for it (#4881a, ~120 LOC) that produces no verdict. A reviewer may
   reasonably say that a section which builds nothing that fires should build nothing at all, and that
   #4881a is documentation wearing a task row. The counter-argument is AC-13.4's landmine assertion,
   which is a real regression guard and has to live somewhere. Which half survives is the reviewer's
   call.
5. **§13.3.4's invalidation-as-a-tool.** Targeted invalidation is exposed as a CLI a human runs, never
   called automatically, on the argument that a diff bug produces a wrong answer while the automatic
   path (miss everything via `contracts_sha`) produces only slowness. A reviewer may hold that a tool
   nobody runs is dead code and that the item should ship without it, leaving `contracts_sha` to do all
   the work. The measurement that would settle it is the same one #4923 lacks.
6. **The two new `REASON_VOCABULARY` members.** `volume_state_unknown` and
   `volume_tracking_unasserted` take the vocabulary from 8 to 10 of a cap of 12, leaving two. §13.7
   argues they name genuinely different give-up stages. A reviewer may hold that
   `volume_tracking_unasserted` is a *hypothesis* failure rather than a *stage* failure and so belongs
   in a soundness annotation (deferred row (b)) rather than in a vocabulary §0 defines as
   "derivation-mechanical, not semantic" — in which case the count is 9, and the distinction a consumer
   needs is lost until row (b) lands.

---

## References

- Main specification (amended): `.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md` — §0 (the
  organizing claim), §0.1 (the DERIVED / HAND-MAINTAINED classification and decision 2's scope note),
  §Open decisions 1–3 (decision 2 is amended, §13.10), §6.2, §7.3–7.4, §9.1 (the registry dataclass and
  the `measure` forms), §9.2 (the 25-row inventory), §9.3 (the ratchet tests), §9.4 (the row-count cap,
  discovery-vs-growth, and `RETIRED` semantics), §Deferred rows (b)/(c)/(d)/(e)/(f).
- Increment 1 (amended): `.praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md` — §10.1.1 (the
  lattice and the no-widening claim, narrowed by §13.10 item 4), §10.1.3–10.1.4, §10.2.1–10.2.6 (P1–P4,
  the bridge, the two-conjunct exception filter, the families), §10.3.1–10.3.3 (atoms, truth,
  emission — criterion 4 re-read by §13.10 item 5), §10.4 (E1–E5), §10.5, §10.6.3, §10.8, §10.9
  (superseded for volume by §13.10 item 3).
- Increment 2 (amended): `.praxia/docs/specs/260902_plr-sema-ir-bytecode-increment.md` — §11.1.2 (the
  value grammar), §11.1.3 (the opcodes and `RESOURCE`'s operands), §11.1.4 (the disposition invariant
  and the S class), §11.3.1–11.3.3 (canonical form, hash, cache key — amended, §13.10 item 7), §11.4.1,
  §11.5 (the #4922/#4923/#4924 hooks), §11.6, §11.12 Q3 (answered, §13.10 item 6).
- Increment 3 (amended): `.praxia/docs/specs/260903_plr-sema-real-programs-increment.md` — §12.1.2 (the
  template-free rule and its HM-25 arithmetic, corrected in §13.2.4), §12.1.5–12.1.6 (the assumption
  table and the scaffolding-`CALL` precedent §13.2.8 reuses), §12.2.7 (`IR_VERSION` 1 → 2), §12.3.3
  (L1/L2/L3, whose tail widen §13.2.5's V4 attaches to), §12.3.4 (`OBLIGED(graph)`), §12.4.2 (tier 2b's
  recorder), §12.6, §12.11 (superseded for volume), §12.13 (the implementation record whose numbers
  this document cites).
- Oracle plan (affected): `.praxia/docs/plans/260902_plr-sema-oracle-harness.md` — the soundness
  contract table, tiers 1–4, "Where it lives".
- Adversarial round 1 on increment 3:
  `.praxia/docs/audits/260903_plr-sema-real-programs-round1-challenger.md` (O1–O6 plus the
  orchestrator's O7) and `.praxia/docs/audits/260903_plr-sema-real-programs-round1-defender.md`. Read
  for the objection style this document is written to pre-empt: a location, a mechanism that does not
  exist on the actual code path, a counterexample from shipped code, and a named remedy.
- Backlog: `#4881` (the two families), `#4922` (the cache), `#4883` (the derived inert filter),
  `#4946` (delegate-call literal channel binding — the residual #4938 filed and commit `92f97256`
  diagnosed without moving); go/no-go only: `#4923` (incremental re-check), `#4924` (error-recovery
  interpreter). Related open item referenced but not addressed: `#4948` (`OperationNode.line_number`
  is 0 at every call site).
- Code read for this document: `plr-sema/src/plr_sema/verdict.py`;
  `plr-sema/src/plr_sema/_hand_maintained.py`; `plr-sema/src/plr_sema/derive/__init__.py`;
  `plr-sema/src/plr_sema/check/ir.py`; `plr-sema/src/plr_sema/check/__init__.py`;
  `plr-sema/eval/oracle_common.py`; `plr-sema/eval/tip_mutants.py`;
  `praxis/backend/utils/plr_static_analysis/models.py`.
- PLR source at submodule pin `dd79c4c89`: `liquid_handling/liquid_handler.py` (`BlowOutVolumeError` at
  `:91-92`, `_lidded_ancestor` at `:95-107` with the `Liddable`/`has_lid` test at `:104`,
  `_check_no_lid` at `:110-120` with its two raises at `:116` and `:117-120`, the aspirate lid check at
  `:978`, the dispense lid check at `:1191`, `vols` coercion at `:968`, the aspiration comprehension at
  `:1007-1028` with `resource=r` at `:1009`, `volume=v` at `:1010` and the `zip` at `:1018-1027`, the
  tracking-gated tracker calls at `:1032-1035`, the commit/rollback block at `:1058-1064`, the
  `BlowOutVolumeError` raises at `:1185`/`:1188`, `transfer`'s signature at `:1273-1283` with no
  `use_channels` parameter, and its two delegate call sites at `:1347-1352` (`aspirate`, with
  `resources=[source]` at `:1348` and no `use_channels`) and `:1355-1361` (`dispense`, with
  `use_channels=[0]` at `:1359`, inside the `for` at `:1354`)); `resources/volume_tracker.py` (the tracking flag at
  `:17-22`, `no_volume_tracking` at `:25-30`, `__init__`'s fields at `:40-52`, `set_volume` at
  `:66-72`, `remove_liquid` at `:88-99` with its guard and raise at `:91-94`, `add_liquid` at `:101-112`
  with its guard and raise at `:104-107`, `get_used_volume` at `:114-116`, `get_free_volume` at
  `:118-120`, `get_liquids`'s raise at `:135-136`, `commit`/`rollback` at `:140-151`, `disable` at
  `:58-60`, `no_volume_tracking` at `:25-30`, `load_state` at
  `:162-167`); `resources/lid.py` (`Liddable` at `:62-72` with `has_lid` as a plain method at `:71-72`,
  the `lid` property at `:74-77`, the setter at `:79-86`, `assign_child_resource` at `:102-120` with
  the already-lidded raise at `:110`); `resources/container.py:84-85`; `resources/tip.py:27,45`.
- Artifacts read: `plr-sema/data/derived_contracts.json` (`VolumeTracker.add_liquid` at
  `:157965-157996`, `VolumeTracker.remove_liquid` at `:158102-158133`, `_check_no_lid`'s own entry at
  `:159897-159933`, `_lidded_ancestor`'s at `:161251-161253`, one of the six depth-1 lid-guard
  inlinings at `:53597-53630`, and `LiquidHandler.transfer`'s entry at `:58363` with its
  single inherited `channel_guards` bridge at `:58364-58383` and `dispense`'s inherited
  `BlowOutVolumeError` guards — whose `scope_trail` carries `"if does_volume_tracking()"` — at
  `:58449-58483`); `training/verify/data/plr_exception_taxonomy.json`
  (`BlowOutVolumeError` at `:2964-2972`, `LiquidLevelError` at `:2991-2999`, `TooLittleLiquidError` at
  `:3010-3036`, `TooLittleVolumeError` at `:3037-3056`); `training/verify/data/plr_preconditions.json`
  (the `dropped_calls` bridge expressions at `:49768-49769` and `:49863-49864`, and `drop_tips`'s
  compound tracking-gated guard at `:50077-50080`).
- Data read: `outputs/plr-sema/oracle_replay_260903_rebaseline.json:2-29` (330 executed, 525
  operations, 0 unsound, 0 `check_graph` exceptions, 0 totality violations, `unknown_rate` 1.0,
  191 exact crosscheck joins, agreement 1.0 — **and no elapsed-time field, which is §13.12.1's
  finding**); `outputs/plr-sema/tip_mutants_260903_4938.json:1-38` (m1 84 `will_fail` / 17 `unknown` of
  101 raised-as-expected over 190 run, m2 190/190, both with empty unsound lists, `gate_passed` true);
`outputs/plr-sema/tip_mutants_260903_4946.json:1-38` (commit `92f97256` — **numerically identical** to
the `…_4938` run in every field, which is what establishes it as §13.5's baseline rather than a
result);
  `outputs/plr-sema/tier2a_260903.json:1-26` (330 compared, 235 agreeing, extractor divergences 0,
  renderer 122, grammar 0, reset 0, directional 208/210, `elapsed_seconds` 89.256);
  `outputs/plr-sema/tier2b_260903.json:1-45` (11 fixtures, 35 operations, `region_unsound` 0,
  `region_will_fail_fired` 3, trip mismatches 0, `elapsed_seconds` 6.069).

---

## Remediation changelog (round 1)
