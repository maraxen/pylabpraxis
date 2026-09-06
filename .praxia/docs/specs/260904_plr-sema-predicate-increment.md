---
title: "plr-sema increment 6 — the predicate language: a three-valued grammar over guard conditions, measured by the UNKNOWN ledger"
description: "Sixth post-corpus increment to the plr-sema pre-corpus specification, taking the main spec's deferred row (c). What it ships, stated as narrowly as the ledger forces: **per-finding SAFE on real executed operations, and a legible residual** -- NOT a joined SAFE. The ledger (544 executed ops, all UNKNOWN, 54 clusters, 6036 findings, n_ops_sole_blocker 0 everywhere) shows the increment cannot be measured by clusters removed, so the gate is per-op residual tier composition. Q1 is taken as (a), a SoundnessScope-annotated scoped SAFE over the PLR precondition layer -- and the document's central finding is that **Q1(a) and Q2 are coupled**: scoping out tier (iii) does not produce a joined SAFE on any executed operation, because every liquid-handling op also carries tier-(ii) guards, so the sprint's headline target moves to increment 7 and that is a user decision. Q2 is recommended DEFER, on evidence rather than cost: the one cheap env member (strictness) decides nothing, because liquid_handler.py:381's `len(extra) > 0` conjunct gates it behind the backend signature in the same guard's own scope. The grammar is a typed mini-AST with Opaque as its only escape; two local-binding idioms, fail-closed; one normative operand observation (O1) without which the benchmark cannot exercise a type atom at all. REASON_VOCABULARY 10 -> 12 of cap 12 (guard_operand_unknown, guard_env_dependent), which exhausts HM-14's headroom; no registry row added, no per-row ceiling proposed to be spent."
status: draft
spec_version: 16
amends: 260901_plr-sema-pre-corpus-spec.md
task_id: 260904_sema-predicates
date: '260904'
confidence: medium
sources: "Sprint plan read in full: .praxia/docs/plans/260904_plr-sema-sprint127-predicates.md (sections 0, 2, 3, 5). Instrument read in full: outputs/plr-sema/unknown_ledger_260904_before.json (header 2-20, baseline_comparison 21-28, totals 29-37, all 54 clusters 38-1891, per_op_reason_set_histogram 1892-1913, notes 1914-1920). Specs: .praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md sections 3.1-3.4 (510-699), 4.1 (757-791), 7.2 (1481-1512), 8.1 (2078-2117), 9.4 (2412-2456), Open decisions 2 (95-105, 3320-3342), Deferred table (2505-2534); .praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md sections 10.2.3 (269-291), 10.3.1-10.3.3 (505-613), 10.4 (617-634), 10.6.3 (744-767), 10.6.4 (769-810), 10.8 (988-1077); .praxia/docs/specs/260903_plr-sema-volume-increment.md sections 14.0 (38-79), 14.0.1 (80-174), 14.0.2 (176), 14.5 (466-598), 14.6 (602-741), 14.7 (745-757), 14.11 (900-969), 14.12 (973-1117), 14.13 (1121-1148), 14.14 (1152-1188), 14.15 (1192-1218), 14.16 (1222-1261), 14.17 (1265-1288). Analyzer source re-read and re-anchored this pass, every citation below verified against the file: plr-sema/src/plr_sema/derive/__init__.py:452-478,513-538; plr-sema/src/plr_sema/check/__init__.py:50-69,291-313; plr-sema/src/plr_sema/verdict.py:120-168; plr-sema/src/plr_sema/_hand_maintained.py:43,613-631,841-896,897-953,957-961; plr-sema/src/plr_sema/check/ir.py:178-192,750-781,918-953; plr-sema/src/plr_sema/check/volumestate.py:108-131,143-205,401-433,436-469; plr-sema/src/plr_sema/check/tipstate.py:355-401,404-439,442-452. Survey: scripts/survey_plr_preconditions.py:140-146,154-171,177-189,191-209,211-218. Harness: plr-sema/eval/oracle_common.py:166-203,251-274,277-308,336-373,397-410,413-442,476-496,524-577,593-611; plr-sema/eval/unknown_ledger.py:123-156,159-186. Lint: plr-sema/scripts/check_spec_citations.py:105-157,160-213; plr-sema/scripts/check_spec_crossrefs.py:52-62,102-156; plr-sema/tests/test_spec_lint.py:28-37,212-255. PLR at submodule pin dd79c4c89: external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:110-120,187-197,315-321,340-389,391-409,490-576,640-674,812-829,871-875,950-1009,1145-1204,1269-1271,1330-1345,1738-1752,1798-1811; external/pylabrobot/pylabrobot/resources/volume_tracker.py:86-109."
---

# Increment 6: the predicate language

> **This document amends `.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md` by reference** and
> adds §15 to that document's numbering, exactly as increment 5 adds §14. It takes the deferred row
> (c) — *"the predicate language turning guard `condition` + `mentions_params` into a checkable
> predicate"* (`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:2518`) — and executes the two
> boundary rows the main spec pre-declared for it: `InlinedGuard` gains a parsed `predicate` field
> interpreted according to `kind`'s polarity with `condition` retained as source of truth
> (`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:2532`), and §8.1's string-mention bridge is
> "replaced wholesale by real predicate comparison"
> (`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:2534`).
>
> **What this increment ships, stated as narrowly as the ledger forces:** *per-finding `SAFE` on real
> executed operations, a `WILL_FAIL` on a syntactically decidable violation, and a residual that names
> which observation is missing.* **Not a joined `SAFE` on a real operation.** §15.5 is the whole
> argument for that last sentence, and it is the document's central finding: the sprint plan's headline
> target is unreachable in this increment for a reason that has nothing to do with the grammar.
>
> **Registry arithmetic this increment carries:** `REASON_VOCABULARY` **10 → 12 of cap 12**
> (`plr-sema/src/plr_sema/_hand_maintained.py:613-631`, HM-14 `declared=12`), which **exhausts HM-14's
> headroom**. No registry row is added; `live_rows()` stays 24 against `BUDGET_CAP = 24`
> (`plr-sema/src/plr_sema/_hand_maintained.py:43`). §15.8 argues that **neither** HM-24 nor HM-25 should
> be spent, and that argument is the one a reviewer should attack first, because the alternative is a
> per-row ceiling spend the user must approve before band B.

---

## 15.0 The instrument and the claim

Sprint 123 closed with every oracle tier at 0 unsound and `unknown_rate` 1.0 on all ten methods. Band
B0 built the instrument that says *why*, and it is a stronger instrument than the planning-time probe:
it reuses `run_static_calls` unmodified and reads findings through the `FINDINGS_SINK` seam installed
after relabelling (`plr-sema/eval/oracle_common.py:593-611`), so the numbers are the pipeline's own.

**The numbers, verbatim.** 544 executed operations, 544 `UNKNOWN`
(`outputs/plr-sema/unknown_ledger_260904_before.json:29-37`); 6,036 findings, of which
`guard_predicate_unparsed` 5,656 / `volume_state_unknown` 194 / `unresolved_delegate` 186; **54
clusters** keyed on `(reason, PLR site, condition text)`.

**Three reason-set combinations, not two** (`outputs/plr-sema/unknown_ledger_260904_before.json:1892-1913`):

| per-op reason set | ops | note |
|---|---|---|
| `{guard_predicate_unparsed}` | 334 | `pick_up_tips`, `drop_tips`, `discard_tips`, `stamp`, and the tip half of the mixed rows |
| `{guard_predicate_unparsed, volume_state_unknown}` | 117 | `aspirate` 77 + `dispense` 40 — the unseeded volume cell |
| `{guard_predicate_unparsed, unresolved_delegate}` | 93 | `move_resource` 29 / `move_lid` 28 / `move_plate` 24 — **deferred row (e)**, `_state_updated` |

**The third combination is out of this increment and can never be a gate candidate.** Its
`unresolved_delegate` cluster is not a guard at all: its `plr_site` is `<none>` and its `condition` is
the bare delegate name `_state_updated`
(`outputs/plr-sema/unknown_ledger_260904_before.json:988-1022`), i.e. the transitive `delegates_to`
closure hit an `unresolved_calls` entry (`plr-sema/src/plr_sema/derive/__init__.py:536-537`). That is
deferred row (e) (`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:2520`), which no predicate
grammar touches. Every `move_*` operation therefore keeps a residual this increment cannot move, and
`move_resource`/`move_lid`/`move_plate` are excluded from §15.9's candidate list by construction.

**`n_ops_sole_blocker` is 0 for all 54 clusters.** Every cluster in the ledger reports
`"n_ops_sole_blocker": 0` — the largest, `liquid_handler.py:375`'s `len(missing) > 0`, blocks 532 of
544 ops and is the sole blocker of none
(`outputs/plr-sema/unknown_ledger_260904_before.json:39-80`). **The consequence is normative for how
this increment is measured**: removing any cluster, or any set of clusters short of *all* of an
operation's, moves `unknown_rate` by exactly zero. A metric of the form "clusters removed" or
"findings converted" would show a large number while the analyzer still says nothing about any
program. §15.9's gate is therefore **per-op residual tier composition** (sprint plan
`.praxia/docs/plans/260904_plr-sema-sprint127-predicates.md:97-110`), and that is the only number in
this document allowed to decide GO.

**Three places the ledger corrects the sprint plan, recorded because a stale premise is how the next
person mis-sizes the work.**

1. **`liquid_handler.py:191`'s `self.setup_finished` guard does not reach real operations.** The plan's
   §0 table carries a `:191 d1 setup` row at count 38 and asks band B0 to explain it
   (`.praxia/docs/plans/260904_plr-sema-sprint127-predicates.md:63`). The ledger's own `notes` show it
   *cannot* appear: `run_static_calls` computes `setup_pcs` from the bytecode's `origin` sideband and
   filters every setup-pc finding out of `raw_findings` **before** relabelling
   (`plr-sema/eval/oracle_common.py:600-607`), so no setup-pc finding can be relabelled onto a real
   `op_<i>` and the seam never sees one
   (`outputs/plr-sema/unknown_ledger_260904_before.json:1914-1915`). The plan's row was an artifact of
   an ephemeral probe that wrapped `check_ir` directly. **No cluster at `liquid_handler.py:191` exists
   in the ledger, and `LiquidHandler.setup`'s own guard is not in scope for this increment.**
2. **544 executed ops, not 548.** `oracle_replay.py`'s own `operations_executed` is 548; the ledger
   counts 544 distinct `(row_id, op_id)` pairs carrying ≥ 1 real finding. The four-op gap is ops that
   received a synthetic zero-finding placeholder rather than a `check_ir` result, which carry no reason
   to cluster (`outputs/plr-sema/unknown_ledger_260904_before.json:1916`). Every ratio in this document
   uses 544.
3. **Two reason-set combinations were planned; there are three.** The plan's §0 probe found
   `{guard_predicate_unparsed}` and `{guard_predicate_unparsed, volume_state_unknown}`
   (`.praxia/docs/plans/260904_plr-sema-sprint127-predicates.md:42-43`); the full-benchmark ledger adds
   the `unresolved_delegate` combination, which is 93 ops — 17% of the benchmark — permanently outside
   this increment.

**The claim, stated as narrowly as increment 5 stated its own.** A joined `SAFE` on a real operation
would claim that operation cannot fail. This increment **does not produce one** (§15.5), and the
narrow claim it does support is: *for a guard whose condition parses to a non-`Opaque` predicate and
whose every operand resolves from the IR call, the analyzer states whether that guard fires, and when
it says `SAFE` the claim is "this PLR precondition does not hold against this call", nothing more.*
Everything wider — that the operation succeeds, that the backend accepts it, that the deck contains
the resource — is out of scope and is named as such, per finding, by §15.7's reasons.

---

## 15.1 The three decidability tiers

> **Normative (the tiers).** Every guard reachable from an executed operation is assigned exactly one
> tier, and the assignment is a property of *what would decide the guard*, not of whether this
> increment decides it.
>
> **(i) syntactic.** Decided from the call's literal kwargs, the resolved contract's parameter
> defaults, and `RESOURCE` operands as declared in the IR (`type`, `element_type`, `grid` —
> `plr-sema/src/plr_sema/check/ir.py:178-192`). No hypothesis, no observation.
>
> **(ii) environment / observation.** Requires state outside the extracted graph: a process-global
> (`get_strictness()`, the `does_volume_tracking()` shape increment 5 already models as an `env`
> member, §14.6), the backend class and its method signatures, the deck (membership, lid topology, head
> channel count), or a container's seeded contents. Decidable only under a recorded hypothesis or an
> observation returned from the executed window.
>
> **(iii) opaque.** The backend's own raise, re-raised. `error is not None` at
> `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:575-576` and its three siblings.
> Never decided from the PLR layer, under any observation this analyzer can take.

**The tiering of every cluster in the ledger.** Conditions are quoted verbatim from the ledger; local
bindings are quoted from PLR at pin `dd79c4c89`. "grammar" = decidable by §15.2 alone; "α"/"β" = needs
that §15.3 idiom; "O1" = needs §15.4's operand observation.

### 15.1.1 The `pick_up_tips` closure — the gate candidate

| PLR site | condition (verbatim) | local binding | tier | needs |
|---|---|---|---|---|
| `liquid_handler.py:498` | `len(not_tip_spots) > 0` | `not_tip_spots = [ts for ts in tip_spots if not isinstance(ts, TipSpot)]` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:496`) | (i) | α + O1 |
| `liquid_handler.py:502` | `len(set(use_channels)) == len(use_channels)` | `use_channels = use_channels or self._default_use_channels or list(range(len(tip_spots)))` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:501`) | (i) | grammar + P3a |
| `liquid_handler.py:522` | `len(tip_spots) == len(offsets) == len(use_channels)` | `offsets = offsets or [Coordinate.zero()] * len(tip_spots)` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:517`) | (i) | β + P3a |
| `liquid_handler.py:514` | `not all((self.backend.can_pick_up_tip(channel, tip) for channel, tip in zip(use_channels, tips)))` | — | (ii) backend | — |
| `liquid_handler.py:375` | `len(missing) > 0` | `missing = non_default - backend_kws` over `inspect.signature(method)` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:353-373`) | (ii) backend signature | — |
| `liquid_handler.py:383` | `strictness == Strictness.STRICT` | under `if len(extra) > 0 and len(vars_keyword) == 0:` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:381`) | (ii) env **and** backend | — |
| `liquid_handler.py:409` | `not len(invalid_channels) == 0` | `invalid_channels = [c for c in channels if c not in self.head]` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:407`) | (ii) head channel count | — |
| `liquid_handler.py:321` | `not resource_from_deck == resource` | `resource_from_deck = self.deck.get_resource(resource.name)` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:318`) | (ii) deck membership | — |
| `liquid_handler.py:576` | `error is not None` | `error` rebound in an `except` handler (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:551-555`) | **(iii)** | — |
| `liquid_handler.py:535` | *(tip typestate; decided since increment 1, `SAFE`/`WILL_FAIL`/`channel_state_unknown`)* | — | decided | — |

`pick_up_tips` carries ten guards and zero gaps at this pin; nine appear in the ledger (223 findings
each, e.g. `outputs/plr-sema/unknown_ledger_260904_before.json:195-227`) and the tenth is already
evaluated. **Its residual after §15.2–§15.4 is predicted to be exactly {(ii), (iii)}**, which is
§15.9's GO condition.

### 15.1.2 The `drop_tips` / `discard_tips` closure — *not* a candidate, and why

| PLR site | condition | local binding | tier | needs |
|---|---|---|---|---|
| `liquid_handler.py:647` | `len(not_tip_spots) > 0` | `not_tip_spots = [ts for ts in tip_spots if not isinstance(ts, (TipSpot, Trash))]` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:645`) | (i) | α (tuple form) + O1 |
| `liquid_handler.py:651` | `len(set(use_channels)) == len(use_channels)` | as `:501` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:650`) | (i) | grammar + P3a |
| `liquid_handler.py:657` | `tip.tracker.get_used_volume() > 0 and (not allow_nonzero_volume)` | `tip = self.head[channel].get_tip()` inside `for channel in use_channels:` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:654-655`) | **½ by decision** | — |
| `liquid_handler.py:666` | `len(tip_spots) == len(offsets) == len(use_channels) == len(tips)` | `tips = []` then `tips.append(tip)` in a loop (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:653-658`) | (i) **unbindable** | — |
| `liquid_handler.py:726` | `error is not None` | — | (iii) | — |
| `:375` / `:383` / `:409` / `:321` | as §15.1.1 | — | (ii) | — |

**Two obstructions, both disclosed rather than discovered at gate time.** `:657` is a compound
condition whose left conjunct is a numeric `Cmp` over a tip's used volume; main spec Open decision 2
and increment 5 §14.14 item 1 keep every numeric `Cmp` outside the `volume_guards` bridge at ½, and
this guard is not a `volume_guards` entry (it calls no tracker mutator). It stays ½ and this increment
does not reopen that. `:666` binds `tips` by an **append inside a loop**, which is neither §15.3
idiom; it fails closed. `drop_tips`/`discard_tips` therefore keep a tier-(i) residual and are **not**
gate candidates. `discard_tips` additionally carries `n == 0`
(`outputs/plr-sema/unknown_ledger_260904_before.json:1396-1428`) whose `n = len(use_channels)` at
`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:819` sits after a conditional
rebinding of `use_channels` at `:817` — excluded by §15.3's rebinding clause.

### 15.1.3 The `aspirate` / `dispense` / `transfer` closure

| PLR site | condition | tier | needs |
|---|---|---|---|
| `liquid_handler.py:959`, `:1153` | `len(set(use_channels)) == len(use_channels)` | (i) | grammar + P3a |
| `liquid_handler.py:990`, `:1202` | `len(p) != len(use_channels)` — `p` is the target of `for n, p in [("resources", resources), …]` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:981-989`) | (i) **unbindable** | γ (§15.13) |
| `liquid_handler.py:875` | `len(not_containers) > 0`, `not_containers = [r for r in resources if not isinstance(r, Container)]` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:873-875`) | (i) | α + O1 |
| `liquid_handler.py:1185`, `:1188` | `self._blow_out_air_volume is None`; `requested_bav is not None and done_bav is not None and (requested_bav > done_bav)` — both under `if any(bav is not None and bav != 0.0 for bav in blow_out_air_volume)` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1182-1188`) | (i) **via scope** | β + E-SCOPE |
| `liquid_handler.py:116`, `:117` | `lidded is resource`; `<unconditional>` — `lidded = _lidded_ancestor(resource)` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:112`) | (ii) lid topology | — |
| `liquid_handler.py:1067`, `:1271` | `error is not None` | (iii) | — |
| `volume_tracker.py:92`, `:105` | `volume - self.get_used_volume() > 1e-06`; `volume - self.get_free_volume() > 1e-06` (`external/pylabrobot/pylabrobot/resources/volume_tracker.py:91,104`) | **already evaluated by increment 5**; residual is `volume_state_unknown` = an unseeded cell at `TOP` | (ii) observation |
| `liquid_handler.py:1335`, `:1337`, `:1340` | `ratios is not None`; `source_vol is not None`; `source_vol is None` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1333-1340`) | (i) | grammar alone |
| `:375` / `:383` / `:409` | as §15.1.1 | (ii) | — |

**`:1185`/`:1188` are the increment's cleanest result and are worth naming.** `blow_out_air_volume`
defaults to `[None] * len(use_channels)` at
`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1159`; under that default the
enclosing `any(bav is not None and bav != 0.0 for bav in blow_out_air_volume)` is **F**, the guards
are unreachable, and `SAFE` is true under both branches of the outer `does_volume_tracking()` test —
increment 5 §14.6's asymmetry argument, applied to a scope entry rather than to the guard itself
(§15.4's E-SCOPE). The two volume clusters `volume_tracker.py:92`/`:105`
(`outputs/plr-sema/unknown_ledger_260904_before.json:1023-1055`, `:467-500`) are **not** this
increment's business: increment 5 already evaluates them and their residual is an unseeded cell, not
an unparsed predicate.

### 15.1.4 The two families that stay out

- **The `move_*` family** — nine clusters at `liquid_handler.py:2055`–`:2290`
  (`outputs/plr-sema/unknown_ledger_260904_before.json:603-987`), all inside `pick_up_resource` /
  `move_picked_up_resource` / `drop_resource`. Their conditions divide into instance-state tests
  (`self.setup_finished and (not self._resource_pickups)`, `self._resource_pickup is not None`,
  `self._resource_pickup is None`) — tier (ii), receiver state the graph does not carry — and
  destination-topology tests (`destination.direction == 'z'`,
  `resource_rotation_wrt_destination % 180 != 0`,
  `destination.resource is not None and destination.resource is not resource`,
  `isinstance(destination, ResourceStack) and destination.direction != 'z'`) — tier (ii), deck
  topology. Every one of the 93 ops in this family also carries the `unresolved_delegate` residual
  (§15.0), so none can clear regardless.
- **The 96-head / `stamp` family** — ten clusters at `liquid_handler.py:1743`–`:2030`
  (`outputs/plr-sema/unknown_ledger_260904_before.json:1429-1791`), 27 ops. `:1743` and `:1893`
  (`not (isinstance(resource, (Plate, Container)) or (isinstance(resource, list) and all((isinstance(w, Well) for w in resource))))`,
  `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1739-1743`) and `:1807`/`:1963`
  (`not len(containers) == 96`) are tier (i) under §15.2's `isinstance`/`all` productions;
  `:1778`/`:1940` (`not self._check_96_head_fits_in_container(container)`) and `:1804`/`:1960`
  (`well.parent != plate`, `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1801-1804`)
  are tier (ii) topology; `:1770`/`:1920` are `<unconditional>`. The family is **not excluded by rule**
  — its tier-(i) members are in scope for the grammar — but it is not a gate candidate, because
  `containers` is bound by a branch this increment does not model.

---

## 15.2 The grammar

> **Normative (G0, the parse is a total function).** `parse : condition -> Predicate` is **total**.
> Every `condition` string produces a `Predicate`; the only escape is `Opaque`, and `Opaque` is a
> constructor of the type, not a failure. `parse(None) = TRUE` — a `None` condition means the guard
> fires unconditionally, which is what `check/__init__.py`'s `"<unconditional>"` sentinel already
> encodes (`plr-sema/src/plr_sema/check/__init__.py:298-312`), and 9 of the shipped table's guards
> carry it. A `SyntaxError` from `ast.parse` yields `Opaque`, as `tipstate._parse_atom` already does
> (`plr-sema/src/plr_sema/check/tipstate.py:393-398`).
>
> **`condition` is retained as the source of truth on the wire.** `InlinedGuard` gains `predicate`
> alongside its existing seven fields (`plr-sema/src/plr_sema/derive/__init__.py:466-472`); nothing is
> replaced. This is the boundary the main spec pre-declared
> (`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:2532`).

> **Normative (G1, the mini-AST).** Over Kleene three-valued logic `{T, F, ½}`:
>
> ```
> Predicate ::= TRUE
>             | Not(Predicate)
>             | And(Predicate, …)          # Kleene: F if any F, T if all T, else ½
>             | Or(Predicate, …)           # Kleene: T if any T, F if all F, else ½
>             | Cmp(Term, op, Term)        # op ∈ {==, !=, <, <=, >, >=}, CHAINED allowed
>             | Is(Term, None, negated)    # `x is None` / `x is not None`
>             | AllOf(Var, Predicate)      # all(<pred> for <v> in <seq>)
>             | AnyOf(Var, Predicate)      # any(<pred> for <v> in <seq>)
>             | IsInstance(Term, (Type, …))
>             | Opaque
> Term      ::= Len(Term) | SetOf(Term) | Var(name) | Lit(json) | Attr(Term, name)
>             | Filtered(Term, Predicate)  # the comprehension of §15.3(α), as a TERM
> ```
>
> **Anything the walk does not recognise is `Opaque`.** `Opaque` evaluates to ½ under every state and
> keeps the guard's existing `guard_predicate_unparsed` reason (§15.7) — so an unrecognised shape is
> **exactly today's behaviour**, per finding, with no new failure mode. This is the fail-closed
> direction and it is why G0 can be total.

> **Normative (G2, chained comparisons).** `ast.Compare` with `n` operators is `And` of `n` binary
> `Cmp`s, with each middle operand evaluated once. `len(tip_spots) == len(offsets) == len(use_channels)`
> (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:522`) is
> `And(Cmp(Len(tip_spots), ==, Len(offsets)), Cmp(Len(offsets), ==, Len(use_channels)))`. Under Kleene
> `And`, one unresolved conjunct does **not** poison the rest: if `len(offsets) != len(use_channels)`
> resolves `F`, the whole is `F` regardless of the first conjunct.

> **Normative (G3, the emptiness-of-a-filtered-comprehension idiom).**
> `len(<x>) <cmp> <int>` where `<x>` is `Filtered(seq, pred)` — the term §15.3(α) binds — is evaluated
> as an existential over `seq`: `len(Filtered(seq, pred)) > 0` is `AnyOf(seq, pred)`, and
> `len(Filtered(seq, pred)) == 0` is `Not(AnyOf(seq, pred))`. This is the whole content of PLR's
> "reject the wrongly-typed elements" pattern: `len(not_tip_spots) > 0` with
> `not_tip_spots = [ts for ts in tip_spots if not isinstance(ts, TipSpot)]` becomes
> "**∃** an element of `tip_spots` that is not a `TipSpot`". Only the comparisons `> 0`, `>= 1`,
> `== 0`, `!= 0` are recognised; every other numeric relation over a `Filtered` term is `Opaque`,
> because a count is not an emptiness test.

> **Normative (G4, `set(P)` uniqueness).** `Cmp(Len(SetOf(x)), ==, Len(x))` evaluates `T` iff `x`
> resolves to a `Seq` of hashable `Lit`s with no duplicate, `F` iff it resolves to such a `Seq` with a
> duplicate, and ½ otherwise. This is the only production that reads `set(...)`, and it reads it as an
> operator on a resolved sequence, never as a Python value.

> **Normative (G5, numeric atoms stay at ½ — no change to Open decision 2).** A `Cmp` whose operands
> are numeric and are not `Len`/`SetOf` terms folds to ½, exactly as
> `.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:3327-3330` resolved and increment 5 §14.14
> item 1 narrowed. The **one** exception is increment 5's: a `Cmp` in a guard raising a taxonomy
> `volume_state` exception, evaluated against `volumestate`'s interval domain
> (`plr-sema/src/plr_sema/check/volumestate.py:117-131`, `:401-433`). This increment adds no second
> exception and in particular does **not** decide
> `tip.tracker.get_used_volume() > 0 and (not allow_nonzero_volume)`
> (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:656-657`) — its right conjunct is
> a literal kwarg and resolves, but Kleene `And` of `½` and `T` is `½`.

> **Normative (G6, polarity from `kind`, never from the text).** `kind == "raise_guard"` fires when the
> predicate is `T`; `kind == "assert"` fires when it is `F`
> (`plr-sema/src/plr_sema/derive/__init__.py:458-463`). Unlike increment 1 §10.3.1's criterion 1, this
> increment **admits both**, because the ledger contains real `assert`-kind guards that the grammar
> decides: `len(set(use_channels)) == len(use_channels)` at
> `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:502` is an `assert`, and it is one
> of `pick_up_tips`'s three tier-(i) guards. Increment 1's own condition for re-adding the `assert`
> branch — *"a real or synthetic contract fixture with an `assert`-kind guard, added at the same time as
> the branch"* — is met by AC-15.1's fixture set.

**The grammar subsumes `tipstate`'s atom parser rather than duplicating it.** `parse_own_atom` and
`parse_bridge_atom` (`plr-sema/src/plr_sema/check/tipstate.py:414-439`) produce a three-production
`_Atom` (`BoolView`, `NullCheck(is_none=True)`, `NullCheck(is_none=False)`,
`plr-sema/src/plr_sema/check/tipstate.py:361-363`) whose truth comes from a *channel state*, not from
the call (`plr-sema/src/plr_sema/check/tipstate.py:442-452`). `BoolView(p)` is this grammar's
`Attr(p, has_tip)` used as a bare predicate and `NullCheck` is `Is`. **`tipstate` keeps ownership of
those two shapes and of their evaluation**: the tip family's atoms are decided by the tip lattice, and
G1's evaluator must not re-decide them. §15.4's dispatch rule is: a guard the tip family claims (its
existing `evaluate_call` selection, `plr-sema/src/plr_sema/check/tipstate.py:521-536`) is skipped by the
predicate evaluator entirely; a guard the volume family claims (a `volume_guards` entry) is likewise
skipped. **One `Finding` per guard remains invariant** — the rule increment 1 §10.3.3 states and
`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:3334-3339` records as must-not-implement.

---

## 15.3 The local-binding idiom

A guard's condition names free locals of the enclosing PLR method — `not_tip_spots`, `offsets`,
`missing`, `invalid_channels`. `InlinedGuard.free_vars` is `finding.mentions_params`
(`plr-sema/src/plr_sema/derive/__init__.py:528`), i.e. the intersection with the *parameter* names, so
it is silent about exactly these. Resolving them in general is the dataflow pass increment 4 §13.12
declined. **This increment resolves exactly two statement shapes and fails closed on everything else.**

> **Normative (α — the filtered comprehension).** In the body of the PLR function `K` that *defines*
> the guard, a single-target `ast.Assign` at **statement position** whose target is a bare `ast.Name`
> `x` and whose value is an `ast.ListComp` with **one** `comprehension`, no `is_async`, exactly one
> `if` clause, a bare-`ast.Name` target `e`, an `iter` that is a bare `ast.Name` naming a parameter of
> `K`, and an element expression that is that same `e`. The bound term is `Filtered(iter, pred)` where
> `pred` is `parse`d from the `if` clause. Both polarities are admitted: `if not isinstance(e, T)` and
> `if isinstance(e, T)`. `T` may be a single `ast.Name` or an `ast.Tuple` of them —
> `not isinstance(ts, (TipSpot, Trash))` at
> `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:645` is the real case that forces
> the tuple form.
>
> **Measured expectation, to be reproduced and published:**
> `not_tip_spots` in `pick_up_tips` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:496`),
> in `drop_tips` (`:645`), and `not_containers` in `_check_containers`
> (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:873`). `invalid_channels`
> (`:407`) matches the *shape* but its `if` clause is `c not in self.head`, which `parse`s to
> `Opaque` — so α binds the term and the predicate stays ½. That asymmetry is the point: α is a
> binding rule, not a decision rule.

> **Normative (β — the `or`-default expansion, length only).** A single-target `ast.Assign` whose
> target is a bare `ast.Name` `x`, whose value is an `ast.BoolOp(Or)` whose **first** operand is
> `ast.Name(x)` (the self-default idiom) and whose **last** operand is either
> `list(range(len(<p>)))` or `[<expr>] * len(<p>)` with `<p>` a bare `ast.Name`. β binds **only the
> length** of `x`, as `Len(x) = Len(p)`, and binds it **only when every intermediate operand of the
> `BoolOp` resolves `F`**. It binds no elements.
>
> **The intermediate-operand clause is not decoration.** `use_channels = use_channels or
> self._default_use_channels or list(range(len(tip_spots)))`
> (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:501`) has `self._default_use_channels`
> in the middle, which is instance state the analyzer cannot see — so β **declines** it and the
> already-shipped P3a/P3b machinery owns it instead (increment 1 §10.2.3,
> `.praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md:271-284`): `channel_default_param`
> records `pick_up_tips → tip_spots`, `channel_default_disablers` poisons on a write to the middle
> term, and `channels_for_call` (`plr-sema/src/plr_sema/check/tipstate.py:245`) returns the resolved
> channel list or `None` for ⊤. **The grammar consults `channels_for_call` for every `use_channels`
> term and never re-derives it.** β's real population is the two-operand form:
> `offsets = offsets or [Coordinate.zero()] * len(tip_spots)`
> (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:517`), `:661`, `:962-965`,
> `:1156-1159`.

> **Normative (the scope condition, and the rebinding clause).** Both idioms apply only when: the
> assignment is in the **same function body** as the guard (depth 0 of `K`, or the delegate's own body
> for a guard at `depth == 1`, `plr-sema/src/plr_sema/derive/__init__.py:472`); the assignment's
> `lineno` precedes the guard's; the assignment is not nested inside any `ast.If`, `ast.For`,
> `ast.While`, `ast.Try` or `ast.With` **that does not also contain the guard**; and **`x` is written
> exactly once in `K`**. Any second write to `x` anywhere in `K` — conditional or not, before or after
> the guard — makes the binding `Opaque`. This is what excludes `discard_tips`'s `use_channels`, which
> is rebound under `if use_channels is None:`
> (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:816-817`), and `aspirate`'s
> `offsets`, rebound at `:1004` under the single-resource-spread branch.
>
> **Additionally, `scope_trail` must not place the guard under a header that rebinds `x`.** A guard
> whose nearest-first `scope_trail` (`scripts/survey_plr_preconditions.py:177-189`) contains a `for`
> entry whose target is `x` is `Opaque` for that free var. The survey already records those entries
> with polarity (`scripts/survey_plr_preconditions.py:191-209`; the `orelse` form is pushed as
> `"else of: if …"` at `:206`) and `for` headers at `:211-218`, so this is a read of an existing field,
> not a new derivation.

**Why this is not the general dataflow pass.** Increment 4 §13.12 declined "resolving a local's type
from its assignment" as a pass with unbounded blast radius. α and β are two `ast.Assign` shapes with a
single-write requirement, matched inside one function body, producing a *term* rather than a type, and
returning `Opaque` on every ambiguity. The measured population is publishable in one table (AC-15.2),
which a general pass's is not. **The difference that matters is failure mode**: a general pass that
mis-resolves a binding produces a wrong predicate and can produce a wrong verdict; α/β can only produce
`Opaque`, which is today's behaviour.

---

## 15.4 Evaluation against the IR call

> **Normative (E-CALL, operand resolution).** A `Var(name)` term resolves, in order: (1) to
> `call.kwargs[name]` if the IR `Call` carries it (`plr-sema/src/plr_sema/check/ir.py:194-204`) —
> note that `lower_calls` renames an untrusted kwarg to `?<j>`
> (`plr-sema/src/plr_sema/check/ir.py:800-808`), so a renamed key resolves to nothing and the term is
> ⊤; (2) to the resolved contract's recorded default for that parameter; (3) to an α/β binding
> (§15.3); (4) otherwise ⊤. `Len` of a `Seq` is its length; `Len` of a `Ref`, a `Lit` or `Top` is ⊤.

> **Normative (E-TYPE, `RESOURCE` operands).** `IsInstance(t, (T₁ … Tₙ))` where `t` resolves to a
> `Ref` is decided against the referenced `RESOURCE` instruction's declared `type`, or its
> `element_type` when the `Ref` carries a `cell`
> (`plr-sema/src/plr_sema/check/ir.py:178-192`). It is `F` iff the declared name is present and is
> **not** any `Tᵢ` **and** the declared name is a known PLR class that is not a subclass of any `Tᵢ`;
> `T` iff it equals some `Tᵢ`; **½ whenever the declared name is `None`, or is not a class the
> subclass test can decide**. `AnyOf(seq, pred)` over a `Seq` is `T` if any element is `T`, `F` if all
> are `F`, else ½. The subclass relation itself is **derived**, from the P1 class index the derive
> package already builds over the PLR surface — never a hand-typed table (§15.8).

> **Normative (O1 — the operand observation, and why the benchmark cannot run without it).** On tier 1
> the RESOURCE declarations are built by `resources_from_example`
> (`plr-sema/eval/oracle_common.py:397-410`), which sets `type` from `deck_layout.resources` and sets
> **no `element_type` and no grid at all**. `deck_layout` carries only the scaffolding's own additions
> — the harness's own docstring records that most referenced resources are never in it and that
> `infer_layout()` silently defaults an unrecognised name to a bare `Plate`
> (`plr-sema/eval/oracle_common.py:284-292`). **Consequently every `IsInstance` atom on the frozen
> benchmark is ½ today for a reason that has nothing to do with the grammar.**
>
> The fix is the observation the harness already computes and discards: `resource_types_from_kwargs`
> returns `{resource_name: plr_class_name}` for every resource reachable from a call's raw kwargs
> (`plr-sema/eval/oracle_common.py:277-308`), via `resource_type_of`'s parent-wins rule
> (`plr-sema/eval/oracle_common.py:251-274`), and `run_runtime` already captures it into
> `RuntimeOutcome.resource_types` (`plr-sema/eval/oracle_common.py:340,350,370-373`). O1 threads it
> into `resources_from_example` as the RESOURCE `type`, and extends the walk to record the
> **element's own** generic class — the object `ir_value_of` keys as a `cell`
> (`plr-sema/eval/oracle_common.py:198-202`) — as `element_type`.
>
> **This is an observation from the executed window, exactly increment 5 §14.6's shape**, and it is
> therefore a tier-(ii) input by §15.1's own definition. It is admitted here, and only here, because
> without it §15.9's measured sets cannot distinguish "the grammar failed" from "the harness supplied
> no type", which is the one confusion that would make the gate uninterpretable. **In the graph lane
> (`lower_graph`, `plr-sema/src/plr_sema/check/ir.py:690-700`) `element_type` is a graph field and the
> same atoms are tier (i) with no observation at all** — O1 repairs the benchmark, not the analyzer.

> **Normative (E-SCOPE, an unsatisfied enclosing scope makes `SAFE` true).** Before evaluating a
> guard's own predicate, `parse` and evaluate each entry of its `scope_trail` (its own body's
> conditions) and, for a bridged guard, of its `caller_scope` (increment 5 §14.0.2). If **any** entry
> evaluates `F`, the guard is not reached, cannot raise, and the emitted `Finding` is `Verdict.SAFE`
> regardless of the guard's own predicate. This is increment 5 §14.6's asymmetry — *"if the condition
> is false, the site cannot raise, so a `SAFE` finding is true under both branches and needs no
> hypothesis"* — applied to a scope entry. An entry beginning `"else of: if "` is evaluated as the
> negation of its test; an entry that is a `for`/`while` header, or that parses `Opaque`, contributes
> ½ and never `F`.

> **Normative (E-VERDICT, from predicate truth to a `Finding`).** With `fires` computed from the
> predicate and `kind`'s polarity (G6), and with §15.4's E-SCOPE not having already returned `SAFE`:
>
> | `fires` | `Finding` |
> |---|---|
> | **F** | `Verdict.SAFE`, `category=""`, `reason=""`, `plr_site=guard.site`, `detail=guard.condition` |
> | **T** | `Verdict.WILL_FAIL`, `category="precondition_state"`, `reason=""` — **only if the guard is unconditional (E-UNCOND below)**; otherwise `Verdict.UNKNOWN` with `reason="guard_env_dependent"` |
> | **½** | `Verdict.UNKNOWN` with the finest applicable reason (§15.7) |
>
> This is increment 1 §10.3.3's table
> (`.praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md:582-586`) with one row split.
> `precondition_state` is an existing `FAILURE_CATEGORIES` member
> (`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:765-768`) and HM-5 stays FROZEN at 6.

> **Normative (E-UNCOND — generalising increment 5's R1).** A guard may emit `WILL_FAIL` only if it is
> **unconditional**: every entry of its `scope_trail` (and, when present, its `caller_scope`) is
> recognised as satisfied, in exactly three ways and no others.
>
> 1. **By evaluation.** The entry `parse`s to a non-`Opaque` predicate that evaluates **T** under
>    §15.4. This is new, and it is the generalisation: increment 5's rule could only recognise a bare
>    zero-argument call in `env`, because it had no evaluator.
> 2. **By hypothesis.** The entry is a bare zero-argument call `f()` whose callee name is in `env`
>    (increment 5 §14.6, unchanged; `plr-sema/src/plr_sema/check/ir.py:918-944` is the key component
>    that partitions the cache by it).
> 3. **By structure — R1.** The entry is the `ast.For` statement increment 5's B1 bound `<name>` over
>    for this guard, recognised by position containment against its `for_span` (increment 5 §14.6).
>
> **Everything else blocks `WILL_FAIL`**: a `while` header, an `async for`, any `for` header R1 did
> not bind, an entry that evaluates ½, an entry that parses `Opaque`, and a `null` scope. In
> particular, an entry beginning `"else of: if …"` is recognised **only** by way (1) — its negated
> test must itself evaluate `T` — and never by way (2), preserving increment 5's AC-14.4 behaviour that
> an `else of:` entry is not satisfied merely because its test text is in `env`.
>
> **Why way (1) is sound where increment 5 needed a structural exception.** Increment 5's R1 exists
> because the analyzer could not evaluate `for op in aspirations:` and had to recognise the node
> instead. Way (1) evaluates the entry as a predicate over the same call the guard is being checked
> against; if it is `T`, the branch is taken on every execution of this call, and the guard is reached.
> It cannot manufacture reachability, because a `for`/`while` header has no predicate form and always
> falls through to way (3) or to unrecognised.

**Interaction with the join.** `join` is unchanged
(`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:576-581`) and stays the one function that
aggregates. A per-op `SAFE` therefore requires **every** finding on that operation to be `SAFE` — every
guard `F` or excluded by E-SCOPE, every gap absent, and every family (tip, volume) also `SAFE`. §15.5
is about whether that is reachable.

---

## 15.5 Q1 — what a joined `SAFE` means on an operation carrying a tier-(iii) guard

Every liquid-handling operation carries `error is not None`
(`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:575-576`, `:725-726`, `:1066-1067`,
`:1270-1271`). A `SAFE` finding on it would claim the backend did not raise — which is A-COMPLETES
(`.praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md:752`) applied to the *current*
operation rather than to its predecessors, and A-COMPLETES is an assumption the analyzer explicitly
does not discharge. Two options.

**(a) A scoped `SAFE`.** The report-level verdict is over the PLR precondition layer, and backend
outcomes are excluded by failure category, recorded as a `SoundnessScope`-style annotation
(`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:103`, `:3327-3330`).

**(b) Never `SAFE` on such an operation.** The headline is unreachable by construction and the
increment's deliverable is the ledger delta alone.

> **Position: (a), with a disclosure that changes what the sprint can claim.** Option (b) is not a
> soundness position, it is a scope refusal: it says that because the analyzer cannot speak about the
> backend, it may not speak about PLR either. That is the same reasoning increment 5 §14.16 Q1 rejected
> when the user resolved *"build it if it is firable at all"*. The `error is not None` guard is a
> **re-raise of an exception the backend already produced**; it is not a PLR precondition, and the four
> `FAILURE_CATEGORIES` re-interpretations at
> `.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:781-788` already draw exactly this line —
> `precondition_state` is "a derived guard is statically established to fire", which a backend re-raise
> is not.

> **Normative (the annotation, if (a) is confirmed).** `AnalysisReport` gains one optional field,
> `scope: SoundnessScope | None = None`, where `SoundnessScope` is a frozen dataclass with a single
> field `excludes: frozenset[str]` ⊆ `FAILURE_CATEGORIES`. Its **only** value in this increment is
> `frozenset({"harness_internal"})` ∪ the categories a re-raise can carry, which at this pin is
> unbounded — **so the exclusion is stated as a site set, not a category set**: `excludes_sites:
> tuple[PlrSite, ...]`, the guards whose evaluation was skipped as tier (iii). A guard classified
> tier (iii) emits **no `Finding` at all** and instead contributes its `site` to `excludes_sites`.
> `join` is unchanged and never sees it. `schema_version` stays 1 (additive field, old readers
> unaffected — `.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:3322-3326`'s additive direction).
>
> **How the oracle checks it.** A backend-raised error on an operation the analyzer marked `SAFE` is
> **not unsound iff** the raise's PLR site is in `excludes_sites`. The harness already observes the
> raising site: `run_runtime` records `exc_class` and the failing index
> (`plr-sema/eval/oracle_common.py:367-373`), and tier 2b compares on `(operation, iteration)`. The
> comparison is therefore: for a row where execution raised at operation `i` and the static side says
> `SAFE` at `op_i`, the row is unsound **unless** the executed exception's class is one the taxonomy
> maps to a `plr_site` in `excludes_sites`. **This is a real weakening of the fence and it is stated as
> one** — AC-15.8's zero-unsound gate is measured against the *narrowed* predicate, and the count of
> rows excused by `excludes_sites` is published alongside it. If that count is greater than zero on the
> frozen benchmark, the exclusion is doing work and must be reviewed before the increment closes.

> **The finding that changes the sprint's target: Q1(a) does not produce a joined `SAFE`, because Q1
> and Q2 are coupled.** Scoping out tier (iii) leaves tier (ii). Every one of the ten methods in the
> benchmark carries tier-(ii) guards that no grammar decides — `pick_up_tips` carries five
> (`liquid_handler.py:375`, `:383`, `:409`, `:321`, `:514`); `aspirate` and `dispense` carry those plus
> the lid pair (`:116`, `:117`) plus an unseeded volume cell; the `move_*` family carries an
> `unresolved_delegate` gap besides. Under `join`'s third row, one `UNKNOWN` makes the operation
> `UNKNOWN` (`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:576-581`). **So the first joined
> `SAFE` on a real operation requires tier (ii), i.e. Q2 answered "ship it", and §15.6 recommends the
> opposite on evidence.** The two questions cannot be decided independently, and the plan's §3 treats
> them as if they could.
>
> **This is a stop-and-ask, in the plan's own sense** (`.praxia/docs/plans/260904_plr-sema-sprint127-predicates.md:114-124`
> reserves that for option (b)). The trigger is different but the decision is the same shape: *is "the
> first definite verdict on a real program" this sprint's deliverable, or increment 7's?* The
> honest answer this document can support is **increment 7's**, and the sprint's own deliverable is
> per-finding `SAFE`, a `WILL_FAIL` on a decidable violation, and a residual that names the missing
> observation per guard. That is a strictly smaller claim than the plan's headline and the user should
> approve the substitution before band B starts.

---

## 15.6 Q2 — does tier (ii) ship here or as increment 7?

> **Recommendation: DEFER to increment 7. #4981 is not started in this sprint.** The argument is not
> cost; it is that the cheap half does not work.

**The legitimacy question is settled in tier (ii)'s favour, and that is not the obstacle.** Increment 5
§14.6 records two failed `is_disabled` discharges: a second `env` member would be "a quantified claim
dressed as an observation" because a deck carries one tracker per well and per tip, and "no `.disable()`
appears in the program" is sound only if the graph is the whole world. **Neither objection applies to an
observation taken from the executed window.** `strictness`, the backend class, the deck's membership
and the head's channel count are single, observable facts about one run, and the harness already takes
`setup.snapshot()` before execution and returns `backend`. Increment 5 already built the pattern and the
cache-key partition that makes it honest (`plr-sema/src/plr_sema/check/ir.py:918-944`). So the
*mechanism* is available and legitimate.

**The obstacle is that the one cheap member decides nothing.** The plan argues `strictness` is "the
exact `does_volume_tracking` shape and costs one `env` member"
(`.praxia/docs/plans/260904_plr-sema-sprint127-predicates.md:125-129`). It is not, and the reason is
two lines above the guard. `strictness == Strictness.STRICT` at
`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:382-383` sits inside
`if len(extra) > 0 and len(vars_keyword) == 0:` at `:381`, where
`extra = backend_kws - set(args.keys())` at `:380` and `args` comes from
`inspect.signature(method)` over the **backend's own bound method** at `:353-354`. Adding `strictness`
to `env` therefore converts a ½ into a ½: the enclosing scope entry is still tier-(ii) backend, so
E-UNCOND blocks `WILL_FAIL` and E-SCOPE cannot return `SAFE`. **The cheap member is gated behind the
expensive fact in the same guard's own scope.**

So tier (ii) is all-or-nothing here: to move either `:375` or `:383` — the two clusters that block 532
of 544 operations (`outputs/plr-sema/unknown_ledger_260904_before.json:39-80`, `:81-122`) — the
increment must AST-derive the backend class's method signatures, which is a new derivation over a new
class surface, with its own measured selection and its own registry argument. That is a whole
increment's work and it is increment 7's, alongside the `pred`-aware `BRANCH` the same evaluator
serves (increment 3 §12.3.6 B2).

**What defers with it:** the deck-membership observation (`:321`), the lid topology (`:116`/`:117`, and
increment 4 §13.1's lid disposition stands), the head channel count (`:409`), the well-seeding
observation that would move `volume_state_unknown`, and `can_pick_up_tip` (`:514`), which needs the
backend's *method body*, not just its signature.

---

## 15.7 Reasons

> **Normative. `REASON_VOCABULARY` 10 → 12, of cap 12** (`plr-sema/src/plr_sema/verdict.py:133-168`;
> HM-14 is `CAPPED` at `declared=12`, `plr-sema/src/plr_sema/_hand_maintained.py:613-631`, so live 12 ≤
> 12 and **no `declared` edit is needed**). Two members:
>
> - **`guard_operand_unknown`** — the condition parsed to a non-`Opaque` predicate and every free name
>   resolved, but an **operand of this call** is ⊤: a non-literal kwarg, a kwarg `lower_calls` renamed
>   to `?<j>` (`plr-sema/src/plr_sema/check/ir.py:800-808`), or a `RESOURCE` whose declared `type`/
>   `element_type` cannot decide an `IsInstance`.
> - **`guard_env_dependent`** — the condition parsed, but ≥ 1 free name does not resolve to a call
>   operand or to an α/β binding at all: it names instance state (`self.<x>`), a module global, a
>   backend attribute, or a local the idioms decline. This is tiers (ii) **and** (iii) together.

**Against increment 1 §10.8's criterion, which is the right instrument.** That section's argument for
`channel_state_unknown` is that `guard_predicate_unparsed` means "could not be turned into a
predicate", which becomes a **false statement** for a guard the analyzer does parse, and that main spec
§0's rule requires a reason to name *which pipeline stage returned nothing* —
"the parse stage returned something; the *evaluation* stage did not"
(`.praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md:992-998`). Both new members are
evaluation-stage give-up points and both are mechanical (they name our own give-up point, not a
semantic property), so §3.3's hand-maintenance justification carries over unchanged. They are
distinguishable from each other by a purely mechanical test — *did every free name resolve?* — which is
what keeps them from being one member split into two for appearance's sake (§9.4's anti-gaming
concern, `.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:2429-2431`).

**Three members were considered and rejected, each for a stated reason.**

- **`guard_predicate_opaque`: rejected.** `guard_predicate_unparsed` already means exactly that, and an
  `Opaque` predicate is precisely "could not be turned into a predicate". Adding it would be a rename
  costing a vocabulary slot. **`Opaque` keeps `guard_predicate_unparsed`**, which also makes the ledger
  delta legible: the residual `guard_predicate_unparsed` count *is* the grammar's coverage gap.
- **A third member separating tier (iii) from tier (ii): rejected.** It would be a 13th and the cap
  conversation is the user's, not the sprint's
  (`.praxia/docs/plans/260904_plr-sema-sprint127-predicates.md:130-131`). The (ii)/(iii) distinction is
  published in §15.9's measured set, where it belongs, rather than encoded in a wire vocabulary.
- **Shipping only `guard_operand_unknown`: considered, and rejected as the weaker option.** It would
  collapse "the analyzer needs one observation it could take" into "the analyzer needs one value this
  call did not carry", which is exactly the distinction the next increment is scoped by. **This is the
  cheaper fallback if the user declines to exhaust HM-14's headroom** (§15.14 Q4).

**Cap consequence, stated rather than buried: after this increment `REASON_VOCABULARY` is at 12 of 12
and HM-14 has zero headroom.** Any future give-up point needs the cap conversation.

---

## 15.8 Registry

**New rows: zero. Retired rows: zero. Per-row ceilings proposed to move: zero.** `live_rows()` is 24
(`plr-sema/src/plr_sema/_hand_maintained.py:957-961`) against `BUDGET_CAP = 24`
(`plr-sema/src/plr_sema/_hand_maintained.py:43`) before and after. Headroom 0, unchanged.

**The question the round must decide: does the local-binding idiom belong on HM-24 (ceiling 3 → 4) or
HM-25 (8 → 9)?** The registry's own criterion is silent-versus-loud: HM-24 is the pattern "whose
failure mode is a SILENT family collapse rather than a loud exact-count test failure"
(`plr-sema/src/plr_sema/_hand_maintained.py:841-896`), while HM-25's `breaks_when` records "Fails
LOUDLY here (unlike HM-24)" (`plr-sema/src/plr_sema/_hand_maintained.py:934-951`).

> **Position: neither. α and β are derived, measured and loud, and belong on no registry row.** Three
> reasons, in decreasing strength.
>
> 1. **The failure mode is neither silent nor a collapse.** If PLR rewrites
>    `not_tip_spots = [ts for ts in tip_spots if not isinstance(ts, TipSpot)]` as a `filter(...)` call
>    or a generator, α binds nothing, the term is `Opaque`, and the guard emits
>    `guard_predicate_unparsed` — **the pre-increment behaviour**, not a wrong verdict and not an
>    emptied family. Contrast HM-24's own `breaks_when`, whose harm is that "the tip-requiring /
>    tip-loading families silently empty". There is no family here to empty; there is a per-guard
>    coverage number.
> 2. **That number is a published gate, so the failure is loud by construction.** AC-15.2 requires the
>    complete α/β selection to be published with a floor, and AC-15.3 requires the per-op residual. A
>    PLR rewrite that broke α would move a published count and fail an exact-count assertion — which is
>    HM-25's *loud* criterion, not HM-24's, and having satisfied the loud criterion the pattern needs no
>    row to make it loud.
> 3. **α and β are Python language constructs, not PLR idioms** — a list comprehension with a filter,
>    and an `or`-chain default — which is verbatim the argument increment 5 §14.11 already accepted for
>    B2 and P1c (`.praxia/docs/specs/260903_plr-sema-volume-increment.md:930-934`). The one place that
>    argument is genuinely weaker here is β's `[<expr>] * len(<p>)` tail, which is closer to an idiom;
>    β binds **only a length** and declines the three-operand form outright, so the surface it claims is
>    smaller than P3a's, which is already on HM-25.
>
> **What a reviewer should attack.** Reason 3 is the weakest: increment 5's round 1 withdrew exactly
> this style of argument for B1 (`.praxia/docs/specs/260903_plr-sema-volume-increment.md:913-928`) on
> the grounds that B1 *matched a shape*. α and β also match shapes. The distinction this document rests
> on is reason 1 — B1's failure disabled a family's soundness-relevant recognition, α's failure returns
> a finding to its pre-increment reason — and if the round rejects that distinction, **the row is HM-25,
> not HM-24, and 8 → 9 is a per-row ceiling spend the user must approve before band B**
> (`.praxia/docs/plans/260904_plr-sema-sprint127-predicates.md:132-135`).

**`cache_key` must change if, and only if, tier (ii) ships.** Its `env` component already exists and is
already the fifth element (`plr-sema/src/plr_sema/check/ir.py:918-953`); this increment adds no
component and threads no new value, so **every key it produces is byte-identical to today's** and the
cache is neither invalidated nor partitioned. O1 (§15.4) changes the *bytecode* — a RESOURCE's `type`
and `element_type` are hashed into `bc_hash` — so the benchmark's keys move, which is a
re-computation, not a correctness event. Under Q2-defer, `strictness` never enters `env` and `cache_key`
is untouched.

---

## 15.9 Measured sets (band B, T30)

> **Normative.** `outputs/plr-sema/t30_measured_260904.json` publishes, computed over the whole
> `plr-sema/data/derived_contracts.json` and over the frozen benchmark's own lowered IR calls (via
> `lower_row_calls`, `plr-sema/eval/oracle_common.py:476-496`, with no analyzer change and no
> `check_ir` invocation):
>
> 1. **Parse coverage.** Of all guards in the contract table: the count parsing to a non-`Opaque`
>    predicate, broken down **per atom kind** (`Cmp`, chained `Cmp`, `Is`, `IsInstance`, `AllOf`/
>    `AnyOf`, `SetOf`-uniqueness, `Filtered`-emptiness, `TRUE`), and the count remaining `Opaque` with
>    the ten most frequent unparsed shapes named.
> 2. **Binding coverage.** The complete set of `(K, x, idiom, term)` tuples α and β bind, and the count
>    of guards with ≥ 1 free local of which every / some / no local binds.
> 3. **Per ledger cluster** (all 54): tier, `parsed?`, `bound?`, and the reason it would carry after
>    §15.7.
> 4. **Per executed operation**: the residual tier set, plus — separately — the count of guards on that
>    operation that are `parsed but operand-unknown`, so a (ii) residual caused by a missing declared
>    type is distinguishable from a genuinely environmental one.
> 5. **The O1 delta**: (4) computed twice, with and without §15.4's operand observation. If the two
>    differ by zero, O1 is not doing what §15.4 claims and the gate is re-opened.
>
> **GO iff ≥ 1 executed real operation's residual tier set is exactly ⊆ {(ii), (iii)}.** NO-GO
> otherwise: publish the counts and the structural reason in §15.15, keep the derive code (it is a
> strict information gain on the contract table either way), and bring the decision to the user before
> the evaluator lands.

**Expected candidates and their expected residuals — this document's own prediction, to be falsified by
the measurement and not assumed by it.**

| method | ops | predicted residual | the guards that must clear, and how |
|---|---|---|---|
| `pick_up_tips` | 223 | **{(ii), (iii)}** — GO | `liquid_handler.py:498` (α + O1), `:502` (G4 + P3a), `:522` (G2 + β + P3a) |
| `transfer` | 19 | {(ii), (iii)} — GO, **conditional on γ** | `liquid_handler.py:1335`/`:1337`/`:1340` clear on the grammar alone; but `transfer` inherits `aspirate`'s `:990` and `dispense`'s `:1202`, which need γ |
| `aspirate` | 77 | {(i), (ii), (iii)} — **NO-GO without γ** | `:959` and `:875` clear; `:990`'s `p` is a loop target over a literal display (§15.13) |
| `dispense` | 40 | {(i), (ii), (iii)} — **NO-GO without γ** | `:1153` clears, `:1185`/`:1188` clear via E-SCOPE; `:1202` needs γ |
| `drop_tips` / `discard_tips` | 65 | {(i), (ii), (iii)} — **NO-GO** | `:666` binds `tips` by loop-append and `:657` is a numeric `Cmp`; both fail closed (§15.1.2) |
| `stamp` | 27 | {(i), (ii), (iii)} — NO-GO | `containers` is branch-bound (§15.1.4) |
| `move_resource` / `move_lid` / `move_plate` | 81 | out of scope — `unresolved_delegate` (§15.0) | — |

**So the gate rests on `pick_up_tips` alone, and on O1.** That is a single point of failure and it is
stated as one: if `tip_spots`' `element_type` does not resolve to `TipSpot` after O1, `:498` is ½,
`pick_up_tips`'s residual gains tier (i), and **the increment is NO-GO on every operation**. The
mitigation is that O1 is a ~25-line harness change over data the harness already computes, and that
§15.9(5) measures its effect directly rather than assuming it.

---

## 15.10 The oracle and the fence

**Tier 1 re-run is the gate: 0 unsound.** A `SAFE` on an operation that raised is the failure this
increment makes possible **for the first time** — increments 1–5 could produce `WILL_FAIL` and
per-finding `SAFE`, but no path from a parsed condition to a `SAFE` on a guard the analyzer previously
declined. Under §15.5's option (a) the unsoundness predicate is narrowed by `excludes_sites`, and both
numbers are published: `unsound` under the narrowed predicate (gate: 0) and `rows_excused_by_scope`
(published, no threshold, reviewed if > 0).

**Non-regression, each re-measured and published, any movement attributed before the run is accepted:**
m1 199/199, m2 289/289, v1 67/67 `WILL_FAIL` at the raised index, tier 2b 16 fixtures with
`region_unsound` 0 and `region_will_fail_fired` 7, tier 1 `rows_executed` 343 / `setup_error` 0 /
crosscheck 191/191, and the spec lint at 24 passed with six specs at zero failing citations
(`.praxia/docs/plans/260904_plr-sema-sprint127-predicates.md:144-151`).

**The ledger after-run.** `outputs/plr-sema/unknown_ledger_260904_after.json`, produced by the same
script with no change, plus a published delta over: `n_findings_by_reason` (the
`guard_predicate_unparsed` 5,656 is the number that must move), `n_clusters`, and the
`per_op_reason_set_histogram`. **`unknown_rate` is expected to stay 1.0** under §15.5's finding, and
that expectation is recorded here so a 1.0 at close is read as "predicted", not as "the increment did
nothing".

> **Normative (a new mutant class — p1, `predicate_arity`).** Adopt one, in this increment, at tier 3.
> `plr-sema/eval/predicate_mutants.py` mutates a *planned* call's kwargs to violate one decided guard
> and asserts the static side emits `WILL_FAIL` at the raised index: (a) a duplicated `use_channels`
> entry, which violates `len(set(use_channels)) == len(use_channels)`
> (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:501-502`) and raises
> `AssertionError`; (b) an `offsets` list one element short, violating the chained equality at `:522`;
> (c) a non-`TipSpot` element in `tip_spots`, violating `:496-498` and raising `TypeError`.
>
> **Why it belongs here rather than in increment 7.** It is the only way to show a predicate
> `WILL_FAIL` lands at the *raised index* rather than merely somewhere, which is the property tier 1's
> aggregate cannot see and which increment 5's v1 class exists to prove for volume. It reuses
> `run_one_mutant(mutator, expected_exc)`, already parameterised by increment 5's T28
> (`.praxia/docs/specs/260903_plr-sema-volume-increment.md:1279`). **Its floor is ≥ 1 achieved
> `WILL_FAIL` at the raised index with 0 unsound in both directions** — increment 5 §14.16's own
> resolution that a class which can only ever report 0 is a publication, not a gate.
>
> **Mutant (a) is the stub-defeating one**: it fires on an `assert`-kind guard, so an implementation
> that kept increment 1 §10.3.1's `raise_guard`-only restriction (G6) passes (b) and (c) and fails (a).

---

## 15.11 Acceptance criteria

- **AC-15.1 (the grammar is total, and `Opaque` is its only escape).** Over the whole shipped
  `derived_contracts.json`, `parse` returns for **every** guard without raising, and the count of
  non-`Opaque` results is published. Six fixtures pin the productions, one apiece: a chained
  comparison of three `Len`s yields two conjoined `Cmp`s and evaluates `F` when the *second* conjunct
  is `F` and the first is ½; `len(<Filtered>) > 0` yields `AnyOf` and `len(<Filtered>) == 0` yields its
  negation; `len(set(x)) == len(x)` on `[0, 1, 1]` is `T` for the guard's polarity and on `[0, 1]` is
  `F`; `x is None` / `x is not None` on a `Lit(null)` kwarg are exact opposites; an `assert`-kind guard
  fires on `F` and a `raise_guard` on `T` for the identical condition string (G6); and an unrecognised
  shape — `c not in self.head` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:407`)
  — yields `Opaque` and a `guard_predicate_unparsed` finding **identical to the one emitted today**.
  The last is the stub-defeating half: an implementation that raised, or that emitted a new reason for
  an unparsed guard, fails it.
- **AC-15.2 (the two idioms bind, are measured, and fail closed).** The complete
  `(K, x, idiom, term)` selection over the whole PLR surface is published with **≥ 3** α entries
  (`liquid_handler.py:496`, `:645`, `:873`) and **≥ 6** β entries. Five fail-closed fixtures, one
  apiece: a second write to `x` anywhere in `K` binds nothing; an assignment nested in an `if` that
  does not contain the guard binds nothing; a three-operand `or` chain whose middle operand is
  `self.<x>` binds nothing under β **and is instead resolved by the existing `channels_for_call`**
  (`plr-sema/src/plr_sema/check/tipstate.py:245`), asserted directly; an assignment *after* the guard's
  `lineno` binds nothing; and a guard whose `scope_trail` contains a `for` header targeting `x` binds
  nothing. The last two are the stub-defeating halves: an implementation matching on shape alone,
  without the position and scope tests, passes the first three and fails these.
- **AC-15.3 (the measured sets are published and the gate is decided by them).**
  `outputs/plr-sema/t30_measured_260904.json` carries all five blocks of §15.9, and the GO/NO-GO
  decision is recorded against the published per-op residual — GO iff ≥ 1 executed real operation's
  residual is ⊆ {(ii), (iii)}. `pick_up_tips` is asserted **by name** to be that operation, or the
  divergence is recorded in §15.15 and the decision goes to the user before AC-15.5's work starts.
- **AC-15.4 (the operand observation, and the counterfactual).** After O1, `resources_from_example`'s
  output carries a non-`None` `type` for **≥ 90%** of the resources referenced by the benchmark's
  planned kwargs, and a non-`None` `element_type` for every `Ref` carrying a `cell`; the pre-O1
  baseline (`type` from `deck_layout` only, `element_type` universally `None`,
  `plr-sema/eval/oracle_common.py:397-410`) is published beside it. §15.9(5)'s with/without residual
  comparison differs on **≥ 1** operation. A zero difference fails this criterion — that is the
  stub-defeating half, since a change that threads the field but never reaches an atom would otherwise
  pass on the field counts alone.
- **AC-15.5 (evaluation: F ⇒ SAFE, ½ ⇒ the finest reason, and E-SCOPE).** Four fixtures. (i) A guard
  evaluating `F` yields exactly one `Verdict.SAFE` finding at `guard.site` with `category == ""` and
  `reason == ""`. (ii) A guard whose enclosing scope entry evaluates `F` yields `SAFE` **regardless of
  its own predicate**, asserted with the guard's own predicate at `T` — the `:1185`/`:1188` shape
  (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1182-1188`). (iii) A guard with an
  unresolvable kwarg yields `guard_operand_unknown`; with an unresolvable free name, `guard_env_dependent`.
  (iv) One `Finding` per guard is preserved: an operation with `n` guards yields exactly `n` findings,
  asserted as a count, and `join` is called once. (ii) is the stub-defeating half.
- **AC-15.6 (`WILL_FAIL` only when unconditional, and the scoped-`SAFE` annotation).** A guard
  evaluating `T` at depth 0 with an empty `scope_trail` yields `Verdict.WILL_FAIL` with
  `category == "precondition_state"`; the same guard yields `Verdict.UNKNOWN` with
  `reason == "guard_env_dependent"` under each of five perturbations, one fixture apiece — a `while`
  header in the trail; a `for` header R1 did not bind; a trail entry parsing `Opaque`; a trail entry
  evaluating ½; and a trail entry beginning `"else of: if "` whose test text is in `env` (which must
  **not** satisfy it, preserving increment 5's AC-14.4 behaviour). Separately: a tier-(iii) guard emits
  **no** `Finding` and contributes its `site` to `AnalysisReport.scope.excludes_sites`; `join`'s input
  multiset is asserted not to contain it; and `check_graph`'s two-positional-argument call form returns
  a report whose `schema_version` is still 1. The `else of:` case and the no-`Finding` assertion are the
  stub-defeating halves.
- **AC-15.7 (the vocabulary arithmetic is exactly as specified).** `len(REASON_VOCABULARY) == 12`
  against HM-14's unchanged `declared == 12`
  (`plr-sema/src/plr_sema/_hand_maintained.py:613-631`); the commit's parent has 10, so the diff is
  visibly 10 → 12; `len(live_rows()) == 24` and `BUDGET_CAP == 24`; HM-24's `declared` is **still 3**
  and HM-25's **still 8**, asserted directly, so a silent ceiling spend fails;
  `test_no_surface_exceeds_its_declared_size`, `test_total_declared_within_budget` and
  `test_reason_vocabulary_closed_forward` all pass, the last with both new members reachable from ≥ 1
  construction site.
- **AC-15.8 (tier 1 — 0 unsound, and the ledger delta).** The sidecar-gated replay reports
  `unsound == 0` under §15.5's narrowed predicate, `rows_setup_error == 0`, `rows_executed == 343`,
  crosscheck 191/191 at agreement 1.0, and `rows_excused_by_scope` published. The after-ledger is
  produced by the unmodified `plr-sema/eval/unknown_ledger.py` and the delta on
  `n_findings_by_reason` / `n_clusters` / `per_op_reason_set_histogram` is published; the
  `guard_predicate_unparsed` count is asserted to have **decreased**, with a floor of **≥ 1,000**
  findings converted, and `unknown_rate` is published without a threshold (§15.10).
- **AC-15.9 (non-regression across tiers 2b and 3).** m1 199/199, m2 289/289, v1 67/67 at the raised
  index with 0 unsound, tier 2b at 16 fixtures with `region_unsound == 0` and
  `region_will_fail_fired >= 7` and `volume_will_fail_fired == 3`. Every number is re-measured against
  the sprint-123 close baseline and any movement is attributed before the run is accepted — the
  E-SCOPE rule is what could move tier 2b, by converting a previously-`UNKNOWN` guard to `SAFE` inside
  an executed region.
- **AC-15.10 (tier 3 — the predicate mutant fires at the raised index).**
  `plr-sema/eval/predicate_mutants.py` reports p1 with **0 unsound** in both directions and its
  achieved `WILL_FAIL`-at-the-raised-index count published against a floor of **≥ 1**, over all three
  mutators (duplicate `use_channels`, short `offsets`, non-`TipSpot` element). The duplicate-
  `use_channels` mutator is asserted to fire against an `assert`-kind guard specifically.
- **AC-15.11 (this document is machine-checked).** `plr-sema/tests/test_spec_lint.py` gains
  `SPEC_INCREMENT_6` and parametrises it into both live-spec tests
  (`plr-sema/tests/test_spec_lint.py:212-255`); `.praxia/docs/INDEX.md` is regenerated; and
  `uv run pytest plr-sema/tests/test_spec_lint.py -q` is **actually run** with its result recorded —
  both the citation checker and the AC-gating half of the cross-reference checker reporting **zero**
  failing violations over this file, and the other six specs unchanged at zero.
- **AC-15.12 (tier (ii), conditional — only if the round overturns §15.6).** `env` gains
  `get_strictness`; the observation is returned from inside the executed window as increment 5's
  `volume_tracking_observed` is (`plr-sema/eval/oracle_common.py:593-595`); `cache_key`'s fifth
  component partitions on it, with the default-`env` key asserted byte-identical to today's; and the
  backend-signature derivation publishes its complete measured selection. **If §15.6's recommendation
  stands, this criterion is withdrawn together with its task row rather than left unsatisfied.**

---

## 15.12 Task rows

> Ordering is forced by §15.9's gate: **T30 must land and publish its measured sets, and the GO/NO-GO
> must be recorded, before T31 constructs any `SAFE` or `WILL_FAIL`.** This is the same normative gate
> increment 5 §14.0 imposes for the same reason: a landed evaluator without a published coverage
> measurement can construct a definite verdict whose basis nobody has inspected.

| task | scope | files | gate | ~LOC | depends on | model |
|---|---|---|---|---|---|---|
| **T30** | Derive + measure (§15.2, §15.3, §15.4's O1, §15.9): the typed mini-AST and the total `parse`; `InlinedGuard.predicate` as an additive field with `condition` retained; the α and β idioms with the scope and rebinding clauses; O1's operand observation threaded into `resources_from_example`; all five measured blocks published and the GO/NO-GO recorded | modify `plr-sema/src/plr_sema/derive/__init__.py`, `plr-sema/src/plr_sema/derive/receiver_state.py`, `plr-sema/src/plr_sema/derive/__main__.py`, `plr-sema/eval/oracle_common.py`, `plr-sema/data/derived_contracts.json` (regenerated), `plr-sema/tests/test_derive.py`; create `plr-sema/eval/t30_measure.py` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_derive.py -q`; then regenerate the contract table and run `t30_measure.py` into `outputs/plr-sema/t30_measured_260904.json` — satisfying **AC-15.1**, **AC-15.2**, **AC-15.3**, **AC-15.4** | ~420 | — | Sonnet — four selections, each measured and published rather than asserted; the gate lives here |
| **T31** | The evaluator and the reasons (§15.4, §15.5, §15.7): `plr-sema/src/plr_sema/check/predicate.py` with E-CALL / E-TYPE / E-SCOPE / E-VERDICT / E-UNCOND; dispatch that skips guards the tip and volume families already claim; `SoundnessScope` and `AnalysisReport.scope`; `REASON_VOCABULARY` 10 → 12 | create `plr-sema/src/plr_sema/check/predicate.py`; modify `plr-sema/src/plr_sema/check/__init__.py`, `plr-sema/src/plr_sema/verdict.py`, `plr-sema/tests/test_check_graph.py`, `plr-sema/tests/test_verdict.py`, `plr-sema/tests/test_hand_maintained_ratchet.py`, and the fixtures under `plr-sema/tests/fixtures/` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_check_graph.py -q`; `uv run pytest plr-sema/tests/test_verdict.py -q`; `uv run pytest plr-sema/tests/test_hand_maintained_ratchet.py -q`; `uv run pytest plr-sema/tests/test_tip_typestate.py -q` — satisfying **AC-15.5**, **AC-15.6**, **AC-15.7** | ~450 | T30 + a recorded GO | Sonnet — E-UNCOND's fail-closed boundary and the tier-(iii) no-`Finding` rule are the two places a plausible implementation is unsound |
| **T32** | The oracle (§15.10): tier-1 re-run with the narrowed unsoundness predicate and `rows_excused_by_scope`; m1/m2/v1/tier-2b non-regression; the after-ledger and its published delta; `plr-sema/eval/predicate_mutants.py` with p1's three mutators | create `plr-sema/eval/predicate_mutants.py`; modify `plr-sema/eval/oracle_replay.py`, `plr-sema/eval/tip_mutants.py`, `plr-sema/eval/tier2_extractor.bth.toml`, `plr-sema/tests/test_oracle_replay.py` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_oracle_replay.py -q`; then the tier-1 replay with its three standard flags, `unknown_ledger.py` into `unknown_ledger_260904_after.json`, `predicate_mutants.py`, `tip_mutants.py`, `volume_mutants.py` and `region_oracle.py` — satisfying **AC-15.8**, **AC-15.9**, **AC-15.10** | ~380 | T31 | Sonnet — every published number is a measurement, and the fence is what this row exists for |
| **T33** | Lint and index: add `SPEC_INCREMENT_6` and parametrise it into both live-spec tests; regenerate `.praxia/docs/INDEX.md`; run the lint and record the result | modify `plr-sema/tests/test_spec_lint.py`; regenerate `.praxia/docs/INDEX.md` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_spec_lint.py -q` — satisfying **AC-15.11** | ~4 | — | Haiku |
| **T34** | **CONDITIONAL — do not start unless round 1 overturns §15.6.** Tier (ii) (#4981): `get_strictness` as an `env` member; the observation record for backend class and signature, deck membership, head channel count and lid topology; the backend-signature derivation with its measured selection; `cache_key` partitioning | modify `plr-sema/src/plr_sema/check/__init__.py`, `plr-sema/src/plr_sema/check/ir.py`, `plr-sema/src/plr_sema/derive/receiver_state.py`, `plr-sema/eval/oracle_common.py`, `training/verify/verifier.py`, `plr-sema/tests/test_cache.py` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_cache.py -q`; `uv run pytest training/tests/test_verify_postconditions.py -q` — satisfying **AC-15.12** | ~300 | T31, round-1 disposition of Q2 | Sonnet |

**Sizing note.** T30 at ~420 is past one session and splits cleanly at the grammar (G0–G6, pure, with
its own fixtures) versus the idioms plus O1 plus the measurement script. **Do not split T30 from T31
across a sprint boundary in the other direction**: a landed T31 without T30's published measurement is
the configuration §15.9's gate exists to prevent. T32 grew from the plan's estimate because the
narrowed unsoundness predicate needs its own comparison path and its own published count.

---

## 15.13 Not in this increment

- **Tier (ii), under §15.6's recommendation.** The backend signature (`liquid_handler.py:375`,
  `:383`), deck membership (`:321`), head channel count (`:409`), lid topology (`:116`/`:117`, and
  increment 4 §13.1's lid disposition stands), `can_pick_up_tip` (`:514`), and the well-seeding
  observation that would move `volume_state_unknown`.
- **A third binding idiom (γ), the bounded literal-display loop.** `for n, p in [("resources", resources), …]`
  (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:981-989`) is a `for` over an
  `ast.List` of `(str, Name)` tuples whose trip count and per-iteration binding are both syntactically
  evident, and it is the **only** thing standing between `aspirate`/`dispense` and a
  {(ii), (iii)} residual (§15.9). It is named here rather than adopted because it is a *loop*
  recognition rule and therefore lands in increment 5 §14.6 R1's territory, which the round should
  weigh as a whole rather than in passing. **§15.14 Q3 puts it to the round explicitly.**
- **A fourth idiom for loop-append bindings** (`tips = []` then `tips.append(...)`,
  `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:653-658`) and for
  `n = len(<param>)` (`:819`). Both are real, both are needed by `drop_tips`/`discard_tips`, and both
  are a general dataflow pass by another name.
- **Numeric `Cmp` outside the volume bridge.** Open decision 2's resolution stands unchanged (G5).
- **A `pred`-aware `BRANCH`** (increment 3 §12.3.6 B2). The same evaluator serves it and it is the
  natural increment 7 alongside tier (ii).
- **Replacing §8's hand-written-contract bridge.** The main spec's boundary row says (c) replaces the
  string-mention bridge "wholesale"
  (`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:2534`) and adds "must be replaced *before*
  §8 is ever made gating". §8 is **not** gating (AC-8.3), so the replacement is deferred, and this
  document records the debt rather than discharging it: the grammar this increment ships is the
  machinery §8.1's `requires_tips` comparison needs
  (`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:2111-2117`), and rewiring §8 onto it is a
  separate task with its own disagreement-rate measurement.
- **Precision targets.** Deferred row (f) stands
  (`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:2524`). AC-15.8's floor of ≥ 1,000 converted
  findings is a *floor against a null result*, not a target.
- **#4923 / #4924** — decision hooks only, per the plan's §3.5–3.6. **#4956** is the Coxswain track.

---

## 15.14 Open questions for round 1

1. **Q1 — is the coupling in §15.5 real, and if so does the sprint's headline move?** The claim to
   attack: *scoping out tier (iii) does not produce a joined `SAFE` on any executed operation, because
   every operation also carries tier-(ii) guards, so the first joined `SAFE` needs Q2 answered "ship
   it".* A refutation would name one executed operation whose non-(iii) residual is empty. If the
   coupling holds, the substitution — per-finding `SAFE` plus a legible residual, joined `SAFE` in
   increment 7 — is a user decision before band B.
2. **Q2 — does §15.6's evidence actually close tier (ii)?** The claim to attack:
   `strictness == Strictness.STRICT` is gated behind `len(extra) > 0` in its own enclosing scope
   (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:380-383`), so the one cheap `env`
   member converts no guard. A refutation would show a guard the `strictness` member alone decides, or
   show that the backend-signature derivation is materially cheaper than this document assumes.
3. **Q3 — does γ (§15.13) belong in this increment?** Without it `aspirate` and `dispense` — 117 of 544
   operations — keep a tier-(i) residual, and the gate rests on `pick_up_tips` alone. With it the
   increment gains a loop-recognition rule, which is where increment 5's R1 needed its most careful
   soundness argument. The round should decide, and if it adopts γ, T30 grows by roughly 60 lines and
   §15.9's candidate table gains two rows.
4. **Q4 — two new reasons, or one?** Shipping both exhausts HM-14 at 12 of 12
   (`plr-sema/src/plr_sema/verdict.py:133-168`). The round should test §15.7's argument that
   `guard_operand_unknown` and `guard_env_dependent` are distinguishable by a mechanical test and that
   the distinction is what scopes increment 7 — and, if it rejects that, take the one-member fallback
   rather than the cap conversation.
5. **Q5 — is §15.8's "neither HM-24 nor HM-25" position sound?** Its weakest leg is reason 3, which
   increment 5's round 1 withdrew for B1. If the round rejects it, HM-25 8 → 9 is a per-row ceiling
   spend requiring user approval before band B.
6. **Q6 — does §15.5's `excludes_sites` weaken the fence more than it appears?** The tier-1 unsoundness
   predicate is narrowed by it, and AC-15.8 publishes `rows_excused_by_scope` precisely so this can be
   audited. A challenger should try to construct a row the narrowed predicate excuses and the old one
   would have caught.

---

## 15.15 Implementation record

*(Empty until band B lands. Column shape mirrors increment 5 §14.17.)*

| row | commit | what landed | measured vs the spec's expectation | divergences |
|---|---|---|---|---|
| T30 | — | — | — | — |
| T31 | — | — | — | — |
| T32 | — | — | — | — |
| T33 | — | — | — | — |
| T34 | — | — | — | — |

---

## References

- Main specification (amended): `.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md` — §3.1–§3.4
  (the `Finding` field set, the join table, the reason vocabulary), §4.1 (`FAILURE_CATEGORIES` and the
  static re-interpretation), §7.2 (the closure), §8.1 (the bridge this row replaces), §9.4 (the budget),
  Open decisions 2 (numeric atoms and the `SoundnessScope` prerequisite), Deferred rows (c), (e), (f)
  and the boundary summary.
- Increment 1: `.praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md` — §10.2.3 (P3a/P3b,
  which §15.3(β) defers to rather than duplicating), §10.3.1–§10.3.3 (the atom grammar this one
  subsumes, and the verdict table), §10.6.3 (A-COMPLETES, A-ENABLED), §10.8 (the parse-stage /
  evaluation-stage criterion §15.7 applies).
- Increment 3: `.praxia/docs/specs/260903_plr-sema-real-programs-increment.md` — §12.3.6 B2, the
  `pred`-aware `BRANCH` the same evaluator would serve, deferred to increment 7.
- Increment 4: `.praxia/docs/specs/260903_plr-sema-families-cache-increment.md` — §13.1 (the lid
  disposition, unchanged), §13.12 (the general dataflow pass §15.3 declines).
- Increment 5 (amended): `.praxia/docs/specs/260903_plr-sema-volume-increment.md` — §14.0 (the
  measure-before-you-construct gate §15.9 reuses), §14.5 (the guard-evaluation table §15.2 G5 leaves
  alone), §14.6 (the conditional-guard rule and R1, generalised by §15.4's E-UNCOND), §14.11 (the
  registry criterion §15.8 argues against), §14.14 item 6 (the cache key), §14.16 Q1/Q2, §14.17 (the
  implementation-record shape).
- Sprint plan: `.praxia/docs/plans/260904_plr-sema-sprint127-predicates.md` — §2 (the tiers and the
  gate), §3 (Q1–Q6), §4 (the baselines §15.10 holds to), §5 (the exclusions §15.13 carries).
- Instrument: `outputs/plr-sema/unknown_ledger_260904_before.json`, produced by
  `plr-sema/eval/unknown_ledger.py` at PLR pin `dd79c4c89` over the sidecar-gated tier-1 benchmark.
