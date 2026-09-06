---
title: "plr-sema increment 6 — the predicate language: a three-valued grammar over guard conditions, measured by the UNKNOWN ledger"
description: "Sixth post-corpus increment to the plr-sema pre-corpus specification, taking the main spec's deferred row (c), revised after adversarial round 1 (C1-C18 + D1-D3). What it ships, narrowed as round 1 forced: **per-finding SAFE on real executed operations plus a legible residual** -- NO joined SAFE this increment. Round-1 changes carried here: E-UNCOND gains clauses (4) no WILL_FAIL at depth >= 1, (5) a depth-0 empty scope_trail is not vacuously unconditional, (6) the raise_guard's own condition entry at scope_trail[0] is excluded from both scope tests; the tier-1 soundness fence is left UNMODIFIED (the exc_class -> site narrowing is deleted) and rows_excused_by_scope becomes a pure annotation; tier (iii) is DERIVED as guard.is_dynamic_raise and emits one Finding, UNKNOWN/guard_env_dependent, plus an excludes_sites annotation; the GO gate is restated over REASONS (zero guard_predicate_unparsed and zero guard_operand_unknown on >= 1 executed op) rather than over tiers, which would have been self-satisfying; E-TYPE is restated T iff is-or-subclass-of / F iff hierarchy-disjoint AND exact, with _generic_plr_type_name declarations normatively never exact; E-CALL gains param_defaults (D1), the beta truthiness interaction, the parameter-rebinding clause and the depth->=1 forbiddance; beta gains the length-preserving-rebinding exception (population 8, measured) and the iterand single-write clause; AC-15.8's >= 1,000 floor is replaced by n_findings_decided >= 223. Four decisions are stated as PENDING USER APPROVAL with this round's recommendation: HM-25 declared 8 -> 9 for alpha+beta (recommend yes), the headline substitution to increment 7 (recommend yes), gamma (recommend no, increment 7), and REASON_VOCABULARY 10 -> 12 of cap 12 (recommend yes, one-member fallback described). Ledger re-run under positional (row_idx, op_id) keying: 544 executed ops, unresolved_delegate cluster 93, :375/:383 at 544, consistency ok, n_row_id_collisions 12 all move_*."
status: reviewed-round-1
spec_version: 17
amends: 260901_plr-sema-pre-corpus-spec.md
task_id: 260904_sema-predicates
date: '260904'
confidence: medium
sources: "Round-1 adversarial reports read in full and dispositioned in section 15.16: .praxia/docs/audits/260904_plr-sema-predicate-round1-challenger.md (C1-C18), .praxia/docs/audits/260904_plr-sema-predicate-round1-defender.md (adjudications, three defender-identified gaps D1-D3, the eighteen-item ordered remediation list, the four user decisions, the revised gate prediction). Sprint plan read in full: .praxia/docs/plans/260904_plr-sema-sprint127-predicates.md (sections 0, 2, 3, 5; the gate at 97-110, the decision hooks at 112-140, the baselines at 144-151). Instrument RE-RUN and re-read after the band-B0 row_id fix (commit ca756bce): outputs/plr-sema/unknown_ledger_260904_before.json (header 2-20, baseline_comparison 21-28, totals 29-37, the 54 clusters 38-2161 incl. :375 at 39-85, :383 at 86-132, :409 at 133-140, :116 at 406-445, :117 at 446-486, :2092 at 763-774, the unresolved_delegate cluster at 1123-1134, per_op_reason_set_histogram 2162-2183, n_row_id_collisions/collision_ops 2184-2273, consistency 3243-3263, notes 3264-3271); its producer plr-sema/eval/unknown_ledger.py:122-172,175-203,221-234,249-270,284-303,332-407,505-557. Specs: .praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md sections 3.1-3.4 (510-699), 4.1 (757-791), 7.2 (1481-1512), 8.1 (2078-2117), 9.4 (2412-2456), Open decisions 2 (95-105, 3320-3342), Deferred table (2505-2534); .praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md sections 10.2.3 (269-291), 10.3.1-10.3.3 (505-613), 10.4 (617-634), 10.6.3 (744-767), 10.6.4 (769-810), 10.8 (988-1077); .praxia/docs/specs/260903_plr-sema-volume-increment.md sections 14.0 (38-79), 14.0.1 (80-174), 14.0.2 (176), 14.5 (466-598), 14.6 (602-741), 14.7 (745-757), 14.11 (900-969), 14.12 (973-1117), 14.13 (1121-1148), 14.14 (1152-1188), 14.15 (1192-1218), 14.16 (1222-1261), 14.17 (1265-1288). Analyzer source re-read and re-anchored this pass, every citation below verified against the file: plr-sema/src/plr_sema/derive/__init__.py:446-449,452-478,499-503,513-538; plr-sema/src/plr_sema/derive/receiver_state.py:900-934,937-965,2056-2094; plr-sema/src/plr_sema/check/__init__.py:50-69,291-313; plr-sema/src/plr_sema/verdict.py:118-168; plr-sema/src/plr_sema/_hand_maintained.py:43,613-631,841-896,897-953,957-961; plr-sema/src/plr_sema/check/ir.py:178-192,194-204,686-701,750-781,796-808,918-953; plr-sema/src/plr_sema/check/volumestate.py:108-131,143-205,401-433,436-469; plr-sema/src/plr_sema/check/tipstate.py:245-270,355-401,404-439,442-452,551-565. Survey: scripts/survey_plr_preconditions.py:140-146,154-171,177-189,191-209,211-229,231-254,256-258. Harness: plr-sema/eval/oracle_common.py:166-203,225-232,235-248,251-274,277-308,336-373,397-410,413-442,476-496,524-577,586-624,632-652. Verifier and the exception taxonomy the round-1 fence argument turns on: training/verify/verifier.py:138-151; training/verify/data/plr_exception_taxonomy.json:1-29. Lint: plr-sema/scripts/check_spec_citations.py:105-157,160-213; plr-sema/scripts/check_spec_crossrefs.py:52-62,102-156; plr-sema/tests/test_spec_lint.py:28-37,212-255. PLR at submodule pin dd79c4c89: external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:106-120,187-197,315-321,348-389,403-409,488-524,540-576,643-668,812-825,869-875,950-1011,1145-1181,1269-1279,1328-1345,1755-1773,1798-1811; external/pylabrobot/pylabrobot/resources/volume_tracker.py:86-109; external/pylabrobot/pylabrobot/resources/trash.py:1-8."
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
> **What this increment ships, stated as narrowly as the ledger and round 1 together force:**
> *per-finding `SAFE` on real executed operations, a `WILL_FAIL` on a syntactically decidable violation
> that is also established reachable, and a residual that names which observation is missing.*
> **Not a joined `SAFE` on a real operation.** §15.5 is the whole argument for that last sentence, and
> it is the document's central finding: the sprint plan's headline target is unreachable in this
> increment for a reason that has nothing to do with the grammar.
>
> **This is the round-1-revised text (spec_version 17).** Round 1 filed eighteen items; §15.16 records
> the disposition of each C1–C18 and D1–D3. Four of them changed what the increment ships, not merely
> how it is worded: the soundness fence is left **unmodified** (§15.5), tier (iii) emits an `UNKNOWN`
> `Finding` rather than none (§15.5), the GO gate is stated over **reasons** rather than over tiers
> (§15.9), and no guard at `depth >= 1` may emit `WILL_FAIL` at all (§15.4 E-UNCOND(4)).
>
> **Registry arithmetic this increment carries, with the one spend it now proposes.**
> `REASON_VOCABULARY` **10 → 12 of cap 12** (`plr-sema/src/plr_sema/_hand_maintained.py:613-631`,
> HM-14 `declared=12`), which **exhausts HM-14's headroom** — *proposed, pending user approval*
> (§15.14 Q4; the one-member fallback is §15.7's). No registry **row** is added; `live_rows()` stays 24
> against `BUDGET_CAP = 24` (`plr-sema/src/plr_sema/_hand_maintained.py:43`). §15.8's draft position
> that **neither** HM-24 nor HM-25 should be spent **did not survive round 1**: α and β are filed on
> **HM-25, `declared` 8 → 9** — *proposed, pending user approval before band B*, exactly as increment 5
> carried "HM-24 1 → 2 planned" before the user approved 1 → 3.

---

## 15.0 The instrument and the claim

Sprint 123 closed with every oracle tier at 0 unsound and `unknown_rate` 1.0 on all ten methods. Band
B0 built the instrument that says *why*, and it is a stronger instrument than the planning-time probe:
it reuses `run_static_calls` unmodified and reads findings through the `FINDINGS_SINK` seam installed
after relabelling (`plr-sema/eval/oracle_common.py:593-611`), so the numbers are the pipeline's own.

**The numbers, verbatim, from the ledger as re-run after band B0's `row_id` fix.** 544 executed
operations, 544 with `n_ops_unknown` equal to `n_ops_executed` (`outputs/plr-sema/unknown_ledger_260904_before.json:29-37`); 6,036 findings,
of which `guard_predicate_unparsed` 5,656 / `volume_state_unknown` 194 / `unresolved_delegate` 186;
**54 clusters** keyed on `(reason, PLR site, condition text)`.

> **Round-1 correction (C12 / item 17, landed as `ca756bce` before this revision).** Every per-op set
> in the ledger is now keyed by the **positional** `(row_idx, op_id)` pair, never by `(row_id, op_id)`
> (`plr-sema/eval/unknown_ledger.py:133-155`, whose docstring states the rule and its reason).
> `row_id` is a content digest that collides across a documented ~4% of corpus rows, so the pre-fix
> ledger silently merged two different ops from two different rows into one `ops_blocked` entry.
> **Three published numbers moved as a result**: the `unresolved_delegate` cluster's `n_ops_blocked`
> 81 → **93**, `liquid_handler.py:375`'s and `:383`'s 532 → **544**, and `:2092`'s 81 → **93**. The
> ledger now publishes a `consistency` block reporting `"ok": true` with an empty `violations` list
> and three independent invariants checked
> (`outputs/plr-sema/unknown_ledger_260904_before.json:3243-3263`;
> `plr-sema/eval/unknown_ledger.py:332-407` defines them), plus `n_row_id_collisions` **12** and a
> `collision_ops` section naming every one of the twelve
> (`outputs/plr-sema/unknown_ledger_260904_before.json:2184-2273`). All twelve are `move_*`
> (`move_plate` 7, `move_lid` 3, `move_resource` 2), each carrying the reason set exactly
> `{guard_predicate_unparsed, unresolved_delegate}` and 13 distinct guard sites — `_check_args`'s
> `:375` and `:383` among them
> (`outputs/plr-sema/unknown_ledger_260904_before.json:2216-2230`). **So the challenger's "12
> unaccounted operations" do not exist**: they were duplicate `move_*` occurrences the pre-fix set
> keying folded away, and they are inside the 93 the histogram always reported. §15.14 Q1's stated
> refutation criterion is answered below.

**Three reason-set combinations, not two** (`outputs/plr-sema/unknown_ledger_260904_before.json:2162-2183`):

| per-op reason set | ops | note |
|---|---|---|
| `{guard_predicate_unparsed}` | 334 | `pick_up_tips`, `drop_tips`, `discard_tips`, `stamp`, and the tip half of the mixed rows |
| `{guard_predicate_unparsed, volume_state_unknown}` | 117 | `aspirate` 77 + `dispense` 40 — the unseeded volume cell |
| `{guard_predicate_unparsed, unresolved_delegate}` | 93 | `move_lid` 31 / `move_plate` 31 / `move_resource` 31 — **deferred row (e)**, `_state_updated` |

**The third combination is out of this increment and can never be a gate candidate.** Its
`unresolved_delegate` cluster is not a guard at all: its `plr_site` is `<none>` and its `condition` is
the bare delegate name `_state_updated`, with `n_findings` 186 over `n_ops_blocked` **93** and a
`per_method` breakdown that now sums to 93
(`outputs/plr-sema/unknown_ledger_260904_before.json:1123-1134`), i.e. the transitive `delegates_to`
closure hit an `unresolved_calls` entry (`plr-sema/src/plr_sema/derive/__init__.py:581-582`). That is
deferred row (e) (`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:2520`), which no predicate
grammar touches. Every `move_*` operation therefore keeps a residual this increment cannot move, and
`move_resource`/`move_lid`/`move_plate` are excluded from §15.9's candidate list by construction.

**`n_ops_sole_blocker` is 0 for all 54 clusters.** Every cluster in the ledger reports
`"n_ops_sole_blocker": 0` — the largest, `liquid_handler.py:375`'s `len(missing) > 0`, blocks **all
544** ops and is the sole blocker of none
(`outputs/plr-sema/unknown_ledger_260904_before.json:39-57`). **The consequence is normative for how
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
2. **544 executed ops, not 548 — and 544 is now both the occurrence count and the distinct count.**
   `oracle_replay.py`'s own `operations_executed` is 548; the ledger counts 544 **positional**
   `(row_idx, op_id)` pairs carrying ≥ 1 real finding. The four-op gap is ops that received a synthetic
   zero-finding placeholder rather than a `check_ir` result, which carry no reason to cluster
   (`outputs/plr-sema/unknown_ledger_260904_before.json:3266`). *The draft called 544 "distinct
   `(row_id, op_id)` pairs"; under the old keying that phrase named a smaller population than the
   counter actually held, which is precisely C12's complaint.* Under positional keying the two
   coincide: `n_ops_executed` increments once per `(row_idx, op_id)` and the key is unique by
   construction, asserted in the clustering loop itself
   (`plr-sema/eval/unknown_ledger.py:226-235`). The ledger's own note 2 text retains the legacy
   "distinct `(row_id, op_id)` pairs" wording (`plr-sema/eval/unknown_ledger.py:507-516`); the value it
   reports is correct and this document, not the note string, is the place the distinction is stated.
   Every ratio in this document uses 544.
3. **Two reason-set combinations were planned; there are three.** The plan's §0 probe found
   `{guard_predicate_unparsed}` and `{guard_predicate_unparsed, volume_state_unknown}`
   (`.praxia/docs/plans/260904_plr-sema-sprint127-predicates.md:42-43`); the full-benchmark ledger adds
   the `unresolved_delegate` combination, which is 93 ops — 17% of the benchmark — permanently outside
   this increment.

**The coupling claim is now confirmed per operation, not merely per method.** §15.5's argument used to
rest on a per-method reading of the clusters, which C12 correctly objected could not see an individual
operation. Under the corrected keying it can: `liquid_handler.py:375` and `:383` each report
`n_findings` 544 over `n_ops_blocked` 544 with a `per_method` breakdown summing to 544
(`outputs/plr-sema/unknown_ledger_260904_before.json:39-57`, `:86-104`), and the ledger's own
`consistency` invariant 3 asserts `sum(per_method) == n_ops_blocked` for **every** cluster
(`plr-sema/eval/unknown_ledger.py:353-356`, result at
`outputs/plr-sema/unknown_ledger_260904_before.json:3244-3245`). So **every one of the 544 executed
operations carries both `_check_args` guards**, both of which are tier (ii). §15.14 Q1's refutation
criterion — *"name one executed operation whose non-(iii) residual is empty"* — is therefore answered
in the negative by measurement rather than by argument: there is no such operation.

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

> **Normative (tier (iii) is DERIVED, at zero registry cost — round 1, C8).** A guard is tier (iii)
> **iff** `guard.is_dynamic_raise` — the shipped property that tests `raises.startswith("<dynamic:")`
> (`plr-sema/src/plr_sema/derive/__init__.py:489-493`), which the survey sets for a
> `raise <ast.Name>`, i.e. a re-raise of a locally-bound exception name
> (`scripts/survey_plr_preconditions.py:231-240`). **No site list, no `condition` text match, no new
> pattern, no registry row.** At this pin the rule selects exactly seven sites in
> `liquid_handler.py` — `:576`, `:726`, `:1067`, `:1271`, `:1510`, `:1590`, `:2092` — which is the
> population §15.1's tables name plus `:2092`, the one a syntactic `condition == "error is not None"`
> rule would have missed (`:2092`'s condition is `<unconditional>`,
> `outputs/plr-sema/unknown_ledger_260904_before.json:763-774`).
>
> **Tiers (i) and (ii) are NOT derived and are not the gate.** The draft's implicit assumption — that
> the evaluator could recognise a tier at measurement time — is withdrawn. A derived (i)/(ii) split of
> the form *"decides ⇒ (i), else (ii)"* would make §15.9's GO condition true by construction, which is
> the opposite of what §15.9 says it is for. **§15.1's (i)/(ii) tiering below is therefore this
> document's PREDICTION only**; the gate is restated over reasons in §15.9, and T30's measured block
> (3) publishes the reason each cluster actually carries so prediction and measurement can diverge
> visibly.

**The tiering of every cluster in the ledger.** Conditions are quoted verbatim from the ledger; local
bindings are quoted from PLR at pin `dd79c4c89`. "grammar" = decidable by §15.2 alone; "α"/"β" = needs
that §15.3 idiom; "O1" = needs §15.4's operand observation. **Every (i)/(ii) cell is a prediction to be
falsified by T30, per the box above.**

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
each, e.g. `:498`'s cluster at `outputs/plr-sema/unknown_ledger_260904_before.json:217-227`) and the
tenth is already evaluated. **Its predicted residual after §15.2–§15.4 is `{guard_env_dependent}`
alone** — no `guard_predicate_unparsed`, no `guard_operand_unknown` — which is §15.9's restated GO
condition. Note that all three of the guards the gate rests on (`:498`, `:502`, `:522`) sit at
`depth == 0` in `pick_up_tips`'s own body
(`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:488-524`), so E-UNCOND(4)'s new
`depth >= 1` forbiddance does not reach them; the five depth-1 guards (`:375`, `:383`, `:409`, `:321`
and, at depth 0 but backend-dependent, `:514`) were already predicted `guard_env_dependent`.

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
idiom; it fails closed. `drop_tips`/`discard_tips` therefore keep a `guard_predicate_unparsed`
residual and are **not** gate candidates. `discard_tips` additionally carries `n == 0` at `:822`
(`outputs/plr-sema/unknown_ledger_260904_before.json:1593`) whose `n = len(use_channels)` at
`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:819` sits after a conditional
rebinding of `use_channels` at `:816-817` — excluded by §15.3's rebinding clause.

**Round-1 correction to this table (C4).** `:647`'s `not_tip_spots` comprehension tests
`isinstance(ts, (TipSpot, Trash))`
(`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:645-647`). Under the **draft's**
E-TYPE, an element whose declared name is `"Container"` — which is what O1 records for a `Trash`,
since `Trash` is not in `_PLR_GENERIC_RESOURCE_NAMES` and `Container` is
(`plr-sema/eval/oracle_common.py:225-232`; `external/pylabrobot/pylabrobot/resources/trash.py:4`) —
would have evaluated `F`, making `Not(...)` `T`, `AnyOf` `T`, and the guard fire: **a false
`WILL_FAIL` on the 65 `drop_tips`/`discard_tips` operations that ran clean.** §15.4's restated E-TYPE
makes it `½` instead. This row is not a gate candidate either way; it is recorded because it was one
of round 1's two live false-`WILL_FAIL` mechanisms.

### 15.1.3 The `aspirate` / `dispense` / `transfer` closure

| PLR site | condition | tier | needs |
|---|---|---|---|
| `liquid_handler.py:959`, `:1153` | `len(set(use_channels)) == len(use_channels)` | (i) | grammar + P3a |
| `liquid_handler.py:990`, `:1202` | `len(p) != len(use_channels)` — `p` is the target of `for n, p in [("resources", resources), …]` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:981-989`) | (i) **unbindable** | γ (§15.13) |
| `liquid_handler.py:875` | `len(not_containers) > 0`, `not_containers = [r for r in resources if not isinstance(r, Container)]` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:873-875`) | (i) | α + O1 |
| `liquid_handler.py:1185`, `:1188` | `self._blow_out_air_volume is None`; `requested_bav is not None and done_bav is not None and (requested_bav > done_bav)` — both under `if any(bav is not None and bav != 0.0 for bav in blow_out_air_volume)` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1179-1188`) | **do NOT clear** (round 1, C6) | — |
| `liquid_handler.py:116` | `lidded is resource` — `lidded = _lidded_ancestor(resource)` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:112`) | (ii) lid topology | — |
| `liquid_handler.py:117` | `<unconditional>` — **retiered in round 1 (C8)**: it has no operands at all, so `parse(None) = TRUE` makes it `T`, not ½, and tiering it "(ii) lid topology" mis-stated why it is undecided | **reachability-blocked** | disposed by E-UNCOND(5) ⇒ `UNKNOWN`/`guard_env_dependent` |
| `liquid_handler.py:1067`, `:1271` | `error is not None` | (iii) | — |
| `volume_tracker.py:92`, `:105` | `volume - self.get_used_volume() > 1e-06`; `volume - self.get_free_volume() > 1e-06` (`external/pylabrobot/pylabrobot/resources/volume_tracker.py:91,104`) | **already evaluated by increment 5**; residual is `volume_state_unknown` = an unseeded cell at `TOP` | (ii) observation |
| `liquid_handler.py:1335`, `:1337`, `:1340` | `ratios is not None`; `source_vol is not None`; `source_vol is None` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1333-1340`) | (i) | grammar alone |
| `:375` / `:383` / `:409` | as §15.1.1 | (ii) | — |

**Withdrawn in round 1: `:1185`/`:1188` were the draft's "cleanest result" and they do not clear.**
The draft argued that `blow_out_air_volume` defaults to `[None] * len(use_channels)` at
`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1159`, so the enclosing
`any(bav is not None and bav != 0.0 for bav in blow_out_air_volume)` at `:1183` is **F**, the guards
are unreachable, and E-SCOPE returns `SAFE`. **Two independent defects kill it, and the paragraph is
deleted rather than softened.** (1) β binds **only a length** (§15.3), and the `any(...)` scope entry
needs the *elements*; E-SCOPE gets ½, not `F`. (2) Even an element-binding extension of β would die at
`:1165`, where `blow_out_air_volume` is rebound by a comprehension that preserves the length but not,
syntactically, the elements. §15.9's `dispense` row is corrected to match. The two volume clusters
`volume_tracker.py:92`/`:105`
(`outputs/plr-sema/unknown_ledger_260904_before.json:1165`, `:529`) remain **not** this increment's
business: increment 5 already evaluates them and their residual is an unseeded cell, not an unparsed
predicate.

**Round-1 correction to `:875` (C4b + item 13).** The draft predicted `_check_containers`'s
`len(not_containers) > 0` at
`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:871-875` would clear. It does not,
for a reason the restated E-TYPE alone would have fixed but the depth rule does not: a `Well`'s
declared name is `"Well"`, `Well` **is** a subclass of `Container`, and under §15.4's restated E-TYPE
that is now `T` ⇒ the guard is `SAFE` — **but the guard sits at `depth == 1`** inside a delegate
called positionally at `:956`, and §15.4's E-CALL(depth) forbids resolving its free names against the
entry point's `call.kwargs`. So `resources` is ⊤ and the guard is `½`/`guard_env_dependent`. Both
facts are recorded because they are separable: option (b) of §15.4's substitution disposition would
make it clear, at ~90 LOC that this increment does not spend.

**Round-1 addition (D1): `:1335`/`:1337`/`:1340` need `param_defaults`, which does not exist today.**
The draft tiered them "(i) grammar alone". `target_vols` is absent from `call.kwargs` for every
planned `transfer`, and the contract table records no parameter defaults at all — grep over
`plr-sema/data/derived_contracts.json` for `"defaults"`, `"param_defaults"` and `"signature"` returns
zero matches, and the derive package extracts none. Without a default the term is ⊤, the enclosing
`if target_vols is not None:` at `:1333` is ½, and all three guards are ½. §15.4's E-CALL(2) is
restated over a new derived `param_defaults` field, which restores them; `transfer`'s three
parameters are all `ast.Constant` `None` defaults at
`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1277-1279`.

### 15.1.4 The two families that stay out

- **The `move_*` family** — eleven clusters at `liquid_handler.py:2055`–`:2290`
  (`outputs/plr-sema/unknown_ledger_260904_before.json:685-1122`), all inside `pick_up_resource` /
  `move_picked_up_resource` / `drop_resource`. Their conditions divide into instance-state tests
  (`self.setup_finished and (not self._resource_pickups)`, `self._resource_pickup is not None`,
  `self._resource_pickup is None`) — tier (ii), receiver state the graph does not carry —
  destination-topology tests (`destination.direction == 'z'`,
  `resource_rotation_wrt_destination % 180 != 0`,
  `destination.resource is not None and destination.resource is not resource`,
  `not isinstance(resource, Plate)`,
  `isinstance(destination, ResourceStack) and destination.direction != 'z'`) — tier (ii), deck
  topology — **and one the draft's seven-condition enumeration omitted: `:2092`'s `<unconditional>`**
  (93 ops, `outputs/plr-sema/unknown_ledger_260904_before.json:763-774`), which is `raise e` in an
  `except` handler and is therefore **derived tier (iii)** by `is_dynamic_raise`, not a topology test
  at all (round 1, C8). Every one of the 93 ops in this family also carries the `unresolved_delegate`
  residual (§15.0), so none can clear regardless.
- **The 96-head / `stamp` family** — ten clusters at `liquid_handler.py:1743`–`:2030`
  (`outputs/plr-sema/unknown_ledger_260904_before.json:1631-2048`), 27 ops. `:1743` and `:1893`
  (`not (isinstance(resource, (Plate, Container)) or (isinstance(resource, list) and all((isinstance(w, Well) for w in resource))))`,
  `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1739-1743`) and `:1807`/`:1963`
  (`not len(containers) == 96`) are tier (i) under §15.2's `isinstance`/`all` productions;
  `:1778`/`:1940` (`not self._check_96_head_fits_in_container(container)`) and `:1804`/`:1960`
  (`well.parent != plate`, `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1801-1804`)
  are tier (ii) topology; `:1770`/`:1920` are `<unconditional>`. The family is **not excluded by rule**
  — its tier-(i) members are in scope for the grammar — but it is not a gate candidate, because
  `containers` is bound by a branch this increment does not model.
  **Round-1 correction (C1):** `:1770`/`:1920` are `<unconditional>` but their `scope_trail` is **not
  empty**. Each sits in the `else:` of a three-branch `if`/`elif`/`elif` chain
  (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1761-1773`), and `visit_If`
  pushes an `"else of: if …"` entry for every `orelse`
  (`scripts/survey_plr_preconditions.py:200-209`), an `elif` self-nesting to compound both conditions.
  E-UNCOND already blocks those — an `"else of: if …"` entry is recognised **only** by way (1), whose
  negated `isinstance` test never evaluates `T` under the restated E-TYPE. So these 54 ops were never
  in C1's false-`WILL_FAIL` population; the guards that were are `:117` (163 ops) and `:2092` (93).

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
> **`parse(None) = TRUE` is a statement about the PREDICATE, never about reachability.** A guard whose
> predicate is `TRUE` still has to satisfy E-UNCOND before it may emit `WILL_FAIL`, and round 1 showed
> that the natural reading of the draft's E-UNCOND satisfied it *vacuously* on an empty `scope_trail`
> — which would have produced `WILL_FAIL` on 163 clean `aspirate`/`dispense`/`stamp`/`transfer`
> operations at `:117` and 93 `move_*` operations at `:2092`. §15.4's E-UNCOND(5) closes that, and
> **G0 must not be read as licensing it.**
>
> **`condition` is retained as the source of truth on the wire.** `InlinedGuard` gains `predicate`
> alongside its existing seven fields (`plr-sema/src/plr_sema/derive/__init__.py:452-478`); nothing is
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
> direction and it is why G0 can be total. **A predicate containing an `Opaque` *sub*-node is
> `Opaque` for reason-assignment purposes too** — §15.7's normative nested-`Opaque` rule, added in
> round 1 (C15) so the residual `guard_predicate_unparsed` count remains an honest coverage measure —
> while still being **evaluated** under Kleene, so an `And` with an `F` conjunct still decides.

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
> term, and `channels_for_call` (`plr-sema/src/plr_sema/check/tipstate.py:245-270`) returns the
> resolved channel list or `None` for ⊤.
>
> **The P3a hook, restated (round 1, C7b).** The draft wrote *"the grammar consults `channels_for_call`
> for every `use_channels` term"*, hand-typing a string that `tipstate.py`'s own normative comment
> forbids: `channel_kwarg` is *"read from `receiver_state`'s own derived `channel_kwarg`, never
> hand-typed as `"use_channels"` here — that string is one of AC-13.15(iii)'s forbidden literals"*
> (`plr-sema/src/plr_sema/check/tipstate.py:254-257`). **Correct statement:** *the grammar consults
> `channels_for_call` for every term naming the receiver's derived `channel_kwarg` or its
> `channel_default_param[method]`, and never re-derives it.* There is no ordering collision with
> E-CALL step (1): `channels_for_call` already resolves the explicit kwarg first and falls back to the
> arity default (`plr-sema/src/plr_sema/check/tipstate.py:262-269`), which **is** E-CALL step (1)
> followed by a fallback, so the two rules cannot disagree.
>
> **β's population is eight, and it is published as a measurement rather than asserted.** Round 1
> established that every one of the six `aspirate`/`dispense` names is written a second time two to
> six lines later (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:962-971`,
> `:1156-1165`), so the draft's own rebinding clause would have deleted them all. The
> β-preserving-rebinding clause below rescues six of the eight and correctly fails closed on the other
> two. The eight: `pick_up_tips` `:517`; `drop_tips` `:661`; `aspirate` `:963`, `:964`, `:965`;
> `dispense` `:1157`, `:1158`, `:1159`. **`offsets` at `:962` and `:1156` is NOT in the population** —
> its second write at `:1004`/`:1177` is `offsets = [c + o for c, o in zip(center_offsets, offsets)]`,
> whose `iter` is a `zip(...)` call rather than the bare name, so the length becomes `min(...)` and the
> binding correctly goes `Opaque`.

> **Normative (the scope condition, and the rebinding clause).** Both idioms apply only when: the
> assignment is in the **same function body** as the guard (depth 0 of `K`, or the delegate's own body
> for a guard at `depth == 1`, `plr-sema/src/plr_sema/derive/__init__.py:472`); the assignment's
> `lineno` precedes the guard's; the assignment is not nested inside any `ast.If`, `ast.For`,
> `ast.While`, `ast.Try` or `ast.With` **that does not also contain the guard**; and **`x` — and the
> term's own iterand, i.e. α's `iter` name and β's `<p>` name — is written exactly once in `K`**. Any
> second write to any of those names anywhere in `K` — conditional or not, before or after the guard —
> makes the binding `Opaque`, **except** for the β-preserving shape below. This is what excludes
> `discard_tips`'s `use_channels`, which is rebound under `if use_channels is None:`
> (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:816-817`), and `aspirate`'s
> `offsets`, rebound at `:1004` under the single-resource-spread branch.
>
> **The iterand half is new in round 1 (C13(1)).** The draft constrained writes to `x` only, and PLR
> rebinds iterands routinely — `resources` at `:999` and `:1172`, `use_channels` at `:501`, `:650`,
> `:958`, `:1152`. At this pin α is safe by accident (`_check_containers`'s `resources` is its own
> parameter, written once, `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:871-875`),
> but the *rule* permitted a term over the wrong sequence — a wrong verdict, not an `Opaque`. With this
> clause, α and β can again only produce `Opaque` from a same-body rebinding.

> **Normative (β-preserving rebinding — round 1, C6).** A second write to `x` of the form
> `x = [<elt> for <e> in x]` — a single `ast.ListComp` with exactly one `comprehension`, **no `if`
> clause**, `is_async` false, a bare-`ast.Name` target, and an `iter` that is the bare `ast.Name` `x`
> itself — **preserves `Len(x)`** and does **not** invalidate a β binding, because β binds only
> `Len(x)`. Every other second write to `x`, and every second write of any shape to an **α**-bound `x`
> (α binds elements, not a length), makes the binding `Opaque`.
>
> **This is the only clause that saves six of the eight β entries, and the obvious alternative does
> not work.** The natural narrowing — "no write between the β assignment and the guard" — saves none
> of them: `:969-971` sit *before* the guard at `:989-990` that reads them, and `:1163-1165` before
> `:1183`, `:1187` and `:1201`. Read literally, those six writes are
> `flow_rates = [float(fr) if fr is not None else None for fr in flow_rates]` and its two siblings
> (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:969-971`, `:1163-1165`): the
> conditional is an `ast.IfExp` in the *element* expression, not a comprehension filter, so the length
> is preserved exactly and the shape test above is a syntactic decision procedure for it. Contrast
> `:1004`/`:1177`, whose `iter` is a `zip(...)` call — length not preserved, `Opaque`, correctly.
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
mis-resolves a binding produces a wrong predicate and can produce a wrong verdict; α/β, *with the
iterand clause and the depth-≥1 forbiddance of §15.4 both in force*, can only produce `Opaque`, which
is today's behaviour.

**Both qualifiers are load-bearing, and round 1 is why they are written down.** Without the iterand
clause, a future PLR that moved a comprehension below a rebinding of its own `iter` would leave α
matching and binding a term over the wrong sequence — silently wrong, with no published count moving.
Without the depth forbiddance, α's terms would be matched in the *delegate's* parameter namespace and
evaluated against the *entry point's* `call.kwargs`, a substitution nothing in the repo records:
`SurveyRecord.delegates` is a bare `set[str]` (`scripts/survey_plr_preconditions.py:163`) and
`_walk_closure` expands it by name alone (`plr-sema/src/plr_sema/derive/__init__.py:446-449`), so
today `_check_containers(self, resources)` resolves only because the caller's local at `:956` happens
to share the name, and `_make_sure_channels_exist(self, channels)` fails closed only because
`use_channels` at `:980` happens not to. §15.4 forbids the resolution outright and T30 publishes the
size of what is forgone. **§15.8's reason 1 survives only under both qualifiers, and §15.8 no longer
rests the registry disposition on it.**

---

## 15.4 Evaluation against the IR call

> **Normative (E-CALL, operand resolution).** A `Var(name)` term resolves, in order: (1) to
> `call.kwargs[name]` if the IR `Call` carries it (`plr-sema/src/plr_sema/check/ir.py:194-204`) —
> note that `lower_calls` renames an untrusted kwarg to `?<j>`
> (`plr-sema/src/plr_sema/check/ir.py:796-808`), so a renamed key resolves to nothing and the term is
> ⊤; (2) to the contract entry's **`param_defaults`** value for that parameter (below); (3) to an α/β
> binding (§15.3); (4) otherwise ⊤. `Len` of a `Seq` is its length; `Len` of a `Ref` or `Top` is ⊤;
> `Len` of a `Lit` is ⊤ **except** where E-CALL(β) below routes it to a β binding.

> **Normative (E-CALL(2) is restated over a NEW derived field, `param_defaults` — round 1, D1).** The
> draft resolved step (2) against *"the resolved contract's recorded default"*. **No such field
> exists**: grep over `plr-sema/data/derived_contracts.json` for `"defaults"`, `"param_defaults"` and
> `"signature"` returns zero matches, and the derive package extracts no defaults anywhere. T30
> therefore records, per contract entry, `param_defaults: {param: <IR value JSON>}` read from the PLR
> function's own `ast.arguments.defaults` / `kw_defaults` **restricted to `ast.Constant` values** —
> anything else (a call, a name, a display) is **omitted**, fail-closed, never guessed. This is a
> derivation over PLR's own recorded surface, not a hand-typed table, so it adds no registry row.
>
> **It is not merely corrective.** With it, `transfer`'s absent `target_vols` resolves to `Lit(null)`
> ⇒ `if target_vols is not None` at
> `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1333` is `F` ⇒ E-SCOPE ⇒ **`SAFE`**
> at `:1335` and `:1337`; the `else of:` entry then evaluates `T` by E-UNCOND way (1) and
> `source_vol is None` is `F` ⇒ `SAFE` at `:1340`. Without it those three are ½ and §15.9's `transfer`
> row is false. Defaults at this pin: `source_vol` `:1277`, `ratios` `:1278`, `target_vols` `:1279`,
> all `ast.Constant` `None`.

> **Normative (E-CALL(5), the parameter-rebinding clause — round 1, C7a).** §15.3's single-write
> requirement protects α/β-bound locals. It says nothing about a **parameter** PLR rebinds before a
> guard reads it, which E-CALL step (1) would otherwise resolve to the *caller's* value. PLR does this
> constantly: `use_channels` at
> `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:501`, `:650`, `:958`, `:1152`;
> `resources` at `:999`, `:1172`; `vols` at `:968`, `:1162`; `ratios` at `:1343`.
>
> **A `Var(name)` naming a parameter of `K` that is written anywhere in `K` at a `lineno` below the
> guard's resolves to ⊤**, unless that write is a β-preserving rebinding (§15.3) and the term is a
> `Len`. Symmetric with §15.3, fail-closed in both directions.

> **Normative (E-CALL(β), the truthiness interaction — round 1, C14b).** `x = x or <default>` fires
> the default when `x` is `[]`, not only when it is `None`, and nothing in the draft modelled that.
> For a `Var(name)` that is the target of a β assignment in `K`:
>
> 1. if the call-side resolution yields a **statically known-falsy** value — `Lit(null)`, `Lit(false)`,
>    `Lit(0)`, or an empty `Seq` — the term resolves to the **β binding**;
> 2. if it yields a **statically known-truthy** value — a non-empty `Seq`, or a non-zero non-null
>    `Lit` — it resolves to **that value**;
> 3. if the parameter is absent from `call.kwargs` **and** its `param_defaults` entry is known-falsy,
>    the term resolves to the **β binding**;
> 4. otherwise ⊤.
>
> **Both directions are errors the draft would have made.** Resolving `offsets=[]` through step (1) to
> `Seq([])` gives `Len == 0 ≠ len(tip_spots)`, so the `assert`-kind guard at `:522` fires: a **false
> `WILL_FAIL`**. Making β unconditionally win would override a real caller-supplied list and produce a
> **false `SAFE`** on the exact mismatch `:522` exists to catch. The falsy/truthy split is what makes
> both impossible.

> **Normative (E-CALL(depth), the delegate→caller substitution is FORBIDDEN this increment — round 1,
> item 13 option (a)).** A `Var(name)` in a guard at `depth >= 1` resolves **only** through
> `channels_for_call` (for the derived channel term, §15.3) or an α/β binding in the delegate's own
> body over the delegate's own parameters. It **never** resolves against the entry point's
> `call.kwargs`, because no argument mapping across a `delegates_to` edge is recorded anywhere:
> `SurveyRecord.delegates` is a bare `set[str]` (`scripts/survey_plr_preconditions.py:163`) and
> `_walk_closure` expands it by name alone (`plr-sema/src/plr_sema/derive/__init__.py:446-449`). Every
> other depth-≥1 free name is ⊤.
>
> **The closest shipped mechanism does not fit and is not repurposed.** P9's
> `_delegate_channel_bindings` (`plr-sema/src/plr_sema/derive/receiver_state.py:937-965`) **is** a
> delegate-parameter → caller-argument substitution, but it reads `call.keywords` only
> (`plr-sema/src/plr_sema/derive/receiver_state.py:907`) while PLR calls every delegate that matters
> **positionally** — `self._check_containers(resources)` at
> `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:956`,
> `_check_no_lid(resource, "aspirate from")` at `:978`, `self._make_sure_channels_exist(use_channels)`
> at `:980`, `self._assert_resources_exist(tip_spots)` at `:520` — and it requires a `self.` receiver
> (`plr-sema/src/plr_sema/derive/receiver_state.py:954`), excluding a module-level delegate like
> `_check_no_lid` outright. Building the general map is ~90 LOC over a new derived field with its own
> measured selection and its own registry argument; it is **increment 7's**, alongside tier (ii).
>
> **T30 publishes the exposure this forgoes**: the count of depth-≥1 guards whose free vars *would*
> have resolved by name coincidence against the entry point's kwargs (§15.9 block (2)). The cost at
> this pin is `:875` (`_check_containers`) and `:117` (`_check_no_lid`); the gate is untouched, because
> `pick_up_tips`'s three deciding guards are all at depth 0.

> **Normative (E-TYPE, `RESOURCE` operands — restated in round 1, C4).** `IsInstance(t, (T₁ … Tₙ))`
> where `t` resolves to a `Ref` is decided against the referenced `RESOURCE` instruction's declared
> `type`, or its `element_type` when the `Ref` carries a `cell`
> (`plr-sema/src/plr_sema/check/ir.py:178-192`). It is:
>
> - **`T`** iff the declared name **is, or is a subclass of, some `Tᵢ`**;
> - **`F`** iff the declared name and every `Tᵢ` are **disjoint in the class hierarchy** (neither is an
>   ancestor of the other) **and** the declaration is known to be **exact**;
> - **½** otherwise — including whenever the declared name is `None`, or is not a class the subclass
>   test can decide.
>
> **A declaration derived from `_generic_plr_type_name` is NEVER exact**
> (`plr-sema/eval/oracle_common.py:235-248`): it returns the most-specific *generic* MRO ancestor whose
> name is in `_PLR_GENERIC_RESOURCE_NAMES` (`plr-sema/eval/oracle_common.py:225-232`), not the concrete
> class, so on the frozen benchmark the `F` branch is **unreachable** and every `IsInstance` atom is
> `T`-or-`½`. A declaration read from a graph-lane `RESOURCE`
> (`plr-sema/src/plr_sema/check/ir.py:694-695`) is exact iff the graph payload marks it so; absent such
> a mark, it is not exact.
>
> `AnyOf(seq, pred)` over a `Seq` is `T` if any element is `T`, `F` if all are `F`, else ½. The
> subclass relation itself is **derived**, from the P1 class index the derive package already builds
> over the PLR surface — never a hand-typed table (§15.8).
>
> **What the draft's rule did, and why both halves were wrong.** Its `F` clause treated a declared type
> as *exact* when a declaration is an **upper bound**: a `Trash` records `"Container"` under O1
> (`external/pylabrobot/pylabrobot/resources/trash.py:4`; `Trash` is absent from the generic set,
> `Container` is present), so `Container` vs `(TipSpot, Trash)` returned `F` ⇒ `Not` `T` ⇒ `AnyOf` `T`
> ⇒ a **false `WILL_FAIL`** on 65 clean `drop_tips`/`discard_tips` operations. Its `T` clause required
> *equality*, so `_check_containers`'s `isinstance(r, Container)` against a `Well` was neither `T`
> (not equal) nor `F` (`Well` **is** a `Container`, so not disjoint) — ½, falsifying the draft's own
> `:875` prediction. The restated rule keeps `:498` decidable in the `SAFE` direction — `TipSpot` is in
> the generic set and is its own most-specific match, so `element_type == "TipSpot"` ⇒ `IsInstance`
> `T` ⇒ `Not` `F` ⇒ `AnyOf` `F` ⇒ the `raise_guard` does not fire — and makes `:647` fail closed at ½
> rather than fabricating a verdict.

> **Normative (O1 — the operand observation, and why the benchmark cannot run without it).** On tier 1
> the RESOURCE declarations are built by `resources_from_example`
> (`plr-sema/eval/oracle_common.py:397-410`), which sets `type` from `deck_layout.resources` and sets
> **no `element_type` and no grid at all**. `deck_layout` carries only the scaffolding's own additions
> — the harness's own docstring records that most referenced resources are never in it and that
> `infer_layout()` silently defaults an unrecognised name to a bare `Plate`
> (`plr-sema/eval/oracle_common.py:284-292`). **Consequently every `IsInstance` atom on the frozen
> benchmark is ½ today for a reason that has nothing to do with the grammar.**
>
> **The `type` half is already computed; the `element_type` half — the half the gate rests on — is
> NOT, and round 1 corrected the draft on exactly that point (C11a).**
> `resource_types_from_kwargs` returns `{resource_name: plr_class_name}` for every resource reachable
> from a call's raw kwargs (`plr-sema/eval/oracle_common.py:277-308`), and `run_runtime` already
> captures it into `RuntimeOutcome.resource_types`
> (`plr-sema/eval/oracle_common.py:336-373`). But it does so via `resource_type_of`'s **parent-wins**
> rule — `target = parent if parent is not None else obj`
> (`plr-sema/eval/oracle_common.py:251-274`) — so for a list of `TipSpot`s it returns
> `{tip_rack_name: "TipRack"}`. **The element's own class is precisely what that function is written to
> discard.** The draft's *"the observation the harness already computes"* was true of the half that
> does not decide `:498` and false of the half that does.
>
> **O1, sized honestly.** (a) Thread the existing `{resource_name: class}` map into
> `resources_from_example` as the RESOURCE `type` (~10 LOC over
> `plr-sema/eval/oracle_common.py:397-410`). (b) Add a **new element walk** alongside the existing one
> in `resource_types_from_kwargs`, recording `_generic_plr_type_name(obj)` for the object *itself*
> rather than for its parent, keyed by parent name (~10 LOC). (c) The heterogeneity guard below (~5).
> (d) Thread `element_type` through (~10). **~40 LOC, not "~25 lines over data the harness already
> computes."**
>
> **Normative (the heterogeneous-parent rule — round 1, C11b).** A `Resource` instruction carries one
> `element_type` per slot (`plr-sema/src/plr_sema/check/ir.py:178-192`), a slot is one resource *name*,
> and `resource_types_from_kwargs` uses `out.setdefault(name, cls)` — **first element wins**
> (`plr-sema/eval/oracle_common.py:294-308`). A `Deck`-parented reference set (a `Trash`, a `Plate` and
> a `TipRack` all have `parent == deck`) would therefore collapse to one arbitrary sibling's class, and
> E-TYPE would decide every cell under that parent against it. **O1 records, per parent name, the SET
> of element generic classes; `element_type` is that class iff the set is a singleton, and `None`
> otherwise** (fail-closed). The count of parents with heterogeneous children is published in AC-15.4.
>
> **This is an observation from the executed window, exactly increment 5 §14.6's shape**, and it is
> therefore a tier-(ii) input by §15.1's own definition. It is admitted here, and only here, because
> without it §15.9's measured sets cannot distinguish "the grammar failed" from "the harness supplied
> no type", which is the one confusion that would make the gate uninterpretable. **In the graph lane
> (`lower_graph`, `plr-sema/src/plr_sema/check/ir.py:686-701`) `element_type` is a graph field read
> straight off the declaration at `:695` and the same atoms are tier (i) with no observation at all** —
> O1 repairs the benchmark, not the analyzer. **Disclosure the user is owed, in this document's own
> words (round 1, C11c):** *this increment's GO is conditional on one tier-(ii) observation, admitted
> to repair the benchmark's data poverty, in an increment that otherwise defers tier (ii); §15.9(5)'s
> with/without delta measures whether O1 matters, not whether the residual is legitimately tier (i);
> and no count of populated graph-lane payloads is offered here.*

> **Normative (E-SCOPE, an unsatisfied enclosing scope makes `SAFE` true).** Before evaluating a
> guard's own predicate, `parse` and evaluate each entry of its `scope_trail[1:]` (its own body's
> conditions, less the self-entry E-UNCOND(6) excludes). If **any** entry evaluates `F`, the guard is
> not reached, cannot raise, and the emitted `Finding` is `Verdict.SAFE` regardless of the guard's own
> predicate. This is increment 5 §14.6's asymmetry — *"if the condition is false, the site cannot
> raise, so a `SAFE` finding is true under both branches and needs no hypothesis"* — applied to a scope
> entry. An entry beginning `"else of: if "` is evaluated as the negation of its test; an entry that is
> a `for`/`while` header, or that parses `Opaque`, contributes ½ and never `F`.
>
> **`caller_scope` is NOT part of E-SCOPE, contrary to the draft (round 1, C2).** `InlinedGuard` has
> exactly seven fields — `condition`, `scope_trail`, `raises`, `kind`, `free_vars`, `site`, `depth`
> (`plr-sema/src/plr_sema/derive/__init__.py:452-478`) — and **no `caller_scope`**. That field exists
> only on the volume bridge's per-guard JSON, attached by P10
> (`plr-sema/src/plr_sema/derive/receiver_state.py:900-934` is its sibling constructor; the consumer is
> `volume_guard_is_unconditional`). Every guard in §15.1's tables is an `InlinedGuard`, so the draft's
> *"and, for a bridged guard, of its `caller_scope`"* was vacuous, and its *"a `null` scope"* had no
> referent — two readings differing by ~256 operations. **This increment does not build the
> `InlinedGuard` P10 equivalent**; it forbids the `WILL_FAIL` instead (E-UNCOND(4)).

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
> **unconditional**: every entry of its `scope_trail[1:]` is recognised as satisfied, in exactly three
> ways and no others, **and clauses (4) and (5) below do not block it**.
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
> not bind, an entry that evaluates ½, and an entry that parses `Opaque`. In particular, an entry
> beginning `"else of: if …"` is recognised **only** by way (1) — its negated test must itself
> evaluate `T` — and never by way (2), preserving increment 5's AC-14.4 behaviour that an `else of:`
> entry is not satisfied merely because its test text is in `env`.
>
> **Why way (1) is sound where increment 5 needed a structural exception.** Increment 5's R1 exists
> because the analyzer could not evaluate `for op in aspirations:` and had to recognise the node
> instead. Way (1) evaluates the entry as a predicate over the same call the guard is being checked
> against; if it is `T`, the branch is taken on every execution of this call, and the guard is reached.
> It cannot manufacture reachability, because a `for`/`while` header has no predicate form and always
> falls through to way (3) or to unrecognised.

> **Normative (E-UNCOND(4), depth — round 1, C2).** **No guard at `depth >= 1` may emit
> `Verdict.WILL_FAIL` in this increment.** Its `Finding` is `Verdict.UNKNOWN` with
> `reason="guard_env_dependent"`. The reason is structural, not conservatism for its own sake: an
> inlined guard's reachability depends on the *call site* in the entry point, and `InlinedGuard`
> records nothing about it (E-SCOPE's box above). Building that record is entangled with the
> unspecified delegate→caller substitution E-CALL(depth) forbids, and both are increment 7's.

> **Normative (E-UNCOND(5), the empty trail — round 1, C1).** A guard at `depth == 0` whose
> `scope_trail` is empty is **not** vacuously unconditional. It may emit `WILL_FAIL` only if `K`'s body
> contains no `ast.Return`, `ast.Try`, `ast.Raise`, `ast.Break` or `ast.Continue`, at any nesting
> depth, at a `lineno` lower than the guard's. Otherwise **½ and `guard_env_dependent`**.
>
> **This clause exists because the record the evaluator reads cannot distinguish the two cases.**
> `scripts/survey_plr_preconditions.py` overrides exactly six visitors — `visit_If` (`:191`),
> `visit_For`/`visit_AsyncFor` (`:211`/`:220`), `visit_While` (`:222`), `visit_Raise` (`:231`),
> `visit_Assert` (`:256`) — and **there is no `visit_Try` and no `visit_Return`**. So a `raise` after
> an early `return`, and a `raise` inside an `except` handler, both carry an *empty* trail, and nothing
> in the record says which. `_check_no_lid` is exactly that shape:
> `lidded = _lidded_ancestor(resource)`, `if lidded is None: return`, `if lidded is resource: raise …`,
> then a statement-position `raise` at `:117`
> (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:110-120`).
>
> **The shipped precedent implements the wrong reading, and this increment deliberately departs from
> it.** `volume_guard_is_unconditional` fails closed **only on `None`**
> (`plr-sema/src/plr_sema/derive/receiver_state.py:2079-2080`); an empty list falls through its loop
> and returns `True` (`plr-sema/src/plr_sema/derive/receiver_state.py:2084-2094`) — vacuous
> satisfaction, in shipped code. An implementer following the one precedent in the tree would emit
> `WILL_FAIL` on 163 clean operations at `:117` and 93 at `:2092`, and since `join` propagates any
> `WILL_FAIL` to the whole operation
> (`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:576-581`) and `compare` scores
> `verdict == "will_fail" and outcome == "ran_ok"` as unsound
> (`plr-sema/eval/oracle_common.py:645-647`), AC-15.8 would fail by construction. **That is why this is
> normative text and not a note.**

> **Normative (E-UNCOND(6), the self-entry — round 1, D3).** For a `raise_guard` whose
> `scope_trail[0]` is `"if " + condition`, that entry **is** the guard's own condition: `visit_Raise`
> reads `scope_trail[0]` into `condition` **without popping it**
> (`scripts/survey_plr_preconditions.py:246-254`). It is therefore excluded from both E-SCOPE and
> E-UNCOND, which range over `scope_trail[1:]`. The two rules would otherwise dispose of the same test
> twice; the answers agree, so this is not unsound, but AC-15.5(i)'s "exactly one `SAFE` finding" would
> be ambiguous about which rule produced it.
>
> **A corollary worth stating, because it bounds C1's population.** Since `visit_Raise` sets a non-null
> `condition` only when `scope_trail[0]` starts with `"if "`, **every `raise_guard` with a non-null
> condition has a non-empty trail.** The empty-trail population is therefore exactly the null-condition
> guards with no enclosing `if`/`for`/`while` — `:117`, `:2092`, and the `assert`-kind analogues — and
> *not* every `<unconditional>` cluster: `:1770`/`:1920` are `<unconditional>` with three-deep
> `"else of: if …"` trails (§15.1.4).

**Interaction with the join.** `join` is unchanged
(`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:576-581`) and stays the one function that
aggregates. A per-op `SAFE` therefore requires **every** finding on that operation to be `SAFE` — every
guard `F` or excluded by E-SCOPE, every gap absent, and every family (tip, volume) also `SAFE`. §15.5
is about whether that is reachable. **After round 1 it is not, and now structurally so**: a tier-(iii)
guard emits `UNKNOWN` (§15.5), every liquid-handling operation carries one, and one `UNKNOWN` makes the
operation `UNKNOWN`. What the draft treated as a contingent finding about tier (ii) is now also a
consequence of the fence.

---

## 15.5 Q1 — what a joined `SAFE` means on an operation carrying a tier-(iii) guard

Every liquid-handling operation carries `error is not None`
(`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:575-576`, `:725-726`, `:1066-1067`,
`:1270-1271`). A `SAFE` finding on it would claim the backend did not raise — which is A-COMPLETES
(`.praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md:752`) applied to the *current*
operation rather than to its predecessors, and A-COMPLETES is an assumption the analyzer explicitly
does not discharge. Two options.

**(a) A scoped `SAFE`.** The report-level verdict is over the PLR precondition layer, and backend
outcomes are excluded, recorded as a `SoundnessScope` annotation. **`SoundnessScope` is NEW in this
increment** — there is no such type anywhere in `plr-sema/src/`. Main spec Open decision 2 is its
*motivation*, not its definition (round 1, C10/C18).

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
>
> **What (a) means after round 1, stated so the position is not read as more than it is.** The
> tier-(iii) guard still emits a `Finding` — `UNKNOWN`, not `SAFE` and not nothing (below) — so (a)
> does not, in this increment, produce a joined `SAFE` on anything. What (a) buys is the *annotation*:
> the report records which sites were excluded from the PLR-precondition claim, so a later increment
> that can reach a joined `SAFE` inherits a scope statement rather than having to invent one. Option
> (b) would forgo even that.

> **Normative (the annotation).** `AnalysisReport` gains one optional field,
> `scope: SoundnessScope | None = None`. **`SoundnessScope` is a frozen dataclass with exactly one
> field, `excludes_sites: tuple[PlrSite, ...]`** — the guards classified tier (iii). It has no
> `excludes: frozenset[str]` field and no `FAILURE_CATEGORIES` member; the draft defined the dataclass
> twice in five lines with two different single fields, and `harness_internal`
> (`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:781-788`: *"analyzer/plumbing bug; always
> paired with `reason="internal_error"`"*) has nothing to do with a backend re-raise (round 1, C10).
> `join` is unchanged and never sees the annotation.
> `schema_version` stays 1 (additive field, old readers unaffected —
> `.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:3322-3326`'s additive direction).

> **Normative (a tier-(iii) guard emits ONE `Finding`, `Verdict.UNKNOWN`, `reason="guard_env_dependent"`
> — round 1, C9).** It *additionally* contributes its `site` to `excludes_sites`. §15.7 already defines
> `guard_env_dependent` as covering tiers (ii) **and** (iii) together, so no definition changes and no
> thirteenth vocabulary member is needed.
>
> **The draft's "no `Finding` at all" broke three shipped invariants and contradicted its own AC set.**
> AC-15.5(iv) asserts exactly `n` findings for `n` guards, while the draft's AC-15.6 said a tier-(iii)
> guard emits **none** — i.e. `n − k` — and neither fixture was scoped to exclude the other, so an
> implementer satisfies one and fails the other. `derive_contract`'s totality docstring — *"Every
> operation therefore receives at least one Finding downstream"*
> (`plr-sema/src/plr_sema/derive/__init__.py:499-503`) — plus the join's "zero findings ⇒ `UNKNOWN`"
> row mean an all-(iii) operation would become `UNKNOWN` **with no evidence** rather than
> `SAFE`-with-scope. And the ledger clusters *findings*
> (`plr-sema/eval/unknown_ledger.py:271-282`), so a suppressed guard is uncountable and §15.9's per-
> cluster block would be uncomputable for exactly the re-raise clusters.
>
> **The challenger's alternative — emit tier (iii) as `Verdict.SAFE` with a `detail` marker — is
> REJECTED as unsound and must not be implemented.** A `SAFE` at `:576` asserts the guard does not
> fire, i.e. that the backend did not raise. Under `join`, an operation whose other findings were all
> `SAFE` would then join to `SAFE`, claiming the operation cannot fail *including at the backend* —
> A-COMPLETES (`.praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md:752`) applied to the
> current operation, which is exactly the claim this section exists to refuse.
>
> **Cost: none.** §15.5 already establishes that no joined `SAFE` is reachable this increment, so
> making tier (iii) yield `UNKNOWN` removes nothing the increment could have had. It also makes the
> coupling structural rather than incidental (§15.14 Q1).

> **Normative (the tier-1 soundness fence is left UNMODIFIED — round 1, C3; the draft's narrowing is
> DELETED).** The tier-1 unsoundness predicate stays exactly
> `unsound = (verdict == "safe" and outcome.startswith("raised")) or (verdict == "will_fail" and
> outcome == "ran_ok")` (`plr-sema/eval/oracle_common.py:645-647`), unmodified.
> `rows_excused_by_scope` is published as a **pure annotation with no threshold and no effect on any
> gate**, and **no `exc_class → PLR site` mapping is constructed anywhere in T32**.
>
> **Why the draft's narrowing had to go, and why deleting it is free.** The draft would have excused a
> `SAFE`-on-raise row when *"the executed exception's class is one the taxonomy maps to a `plr_site` in
> `excludes_sites`"*. A taxonomy does exist —
> `training/verify/data/plr_exception_taxonomy.json:1-29` carries 132 classes at the same pin, each
> with `trigger_sites` — but it covers **PLR-defined** classes only: it contains none of
> `TypeError`/`ValueError`/`RuntimeError`, which is what the benchmark actually raises, and none of the
> re-raise sites. Building the mapping would mean inventing it, and it **cannot be injective**: a
> re-raise carries the backend's own exception class, which is unbounded by construction, and
> `TypeError` alone is raised at `liquid_handler.py:375`, `:383`, `:498` and `:1770` — all PLR
> precondition sites — *and* re-raised at `:576`. Every `TypeError` row would be excusable, i.e. the
> narrowing excuses precisely the rows the fence exists to catch. The runtime side is no better:
> `exc_class = error.split(":", 1)[0].strip()` (`plr-sema/eval/oracle_common.py:368`) over
> `error = f"{type(e).__name__}: {e}"` (`training/verify/verifier.py:143-144`) — reliable as a class
> name, useless as a site — and **no traceback is captured anywhere**.
>
> **And the narrowing purchased nothing.** It bites only on `SAFE`-on-raise rows, and §15.5's own
> central finding is that no operation reaches a joined `SAFE` this increment. The draft was weakening
> its own fence to buy a result it simultaneously proves it cannot obtain. **§15.14 Q6 therefore
> answers itself: yes, it weakened the fence, and the weakening bought nothing.** The ~3-line
> `traceback.extract_tb(...)[-1]` capture that would make a site-keyed narrowing honest — available at
> the bare `except Exception as e` handler
> (`training/verify/verifier.py:143-144`) — moves to **increment 7**, where a joined `SAFE` first
> becomes possible and the fence actually needs the discrimination.

> **The finding that changes the sprint's target: Q1(a) does not produce a joined `SAFE`, because Q1
> and Q2 are coupled — and round 1 strengthened this rather than weakening it.** Scoping out tier (iii)
> leaves tier (ii). Every one of the ten methods in the benchmark carries tier-(ii) guards that no
> grammar decides — `pick_up_tips` carries five, all inherited from its delegates, starting with the `missing`-arguments raise (`liquid_handler.py:375`, `:383`, `:409`, `:321`,
> `:514`); `aspirate` and `dispense` carry those plus the lid pair (`:116`, `:117`) plus an unseeded
> volume cell; the `move_*` family carries an `unresolved_delegate` gap besides. Under `join`'s third
> row, one `UNKNOWN` makes the operation `UNKNOWN`
> (`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:576-581`). **So the first joined `SAFE` on a
> real operation requires tier (ii), i.e. Q2 answered "ship it", and §15.6 recommends the opposite on
> evidence.** The two questions cannot be decided independently, and the plan's §3 treats them as if
> they could.
>
> **Two round-1 results make the coupling harder, not softer.** (1) The `(row_idx, op_id)` re-keying
> shows `_check_args`'s two tier-(ii) guards on **all 544** executed operations, so the coupling is now
> established per operation and not merely per method (§15.0). (2) With tier (iii) emitting `UNKNOWN`
> (above), every operation carrying a re-raise is `UNKNOWN` *by construction*, independently of tier
> (ii). The claim survives its own adversarial round.

> **PENDING USER DECISION — the headline substitution. This round's recommendation: substitute.**
> The question, in the plan's own stop-and-ask sense
> (`.praxia/docs/plans/260904_plr-sema-sprint127-predicates.md:114-124` reserves that language for
> option (b)): *is "the first definite verdict on a real program" this sprint's deliverable, or
> increment 7's?* The honest answer this document can support is **increment 7's**, and the sprint's
> own deliverable is per-finding `SAFE`, a `WILL_FAIL` on a decidable and reachable violation, and a
> residual that names the missing observation per guard. That is a strictly smaller claim than the
> plan's headline. **Nothing in band B is dispatched against the larger claim until the user answers.**
> If the user declines the substitution, the sprint has no path to its headline that this document can
> defend, and §15.6's Q2 recommendation would have to be reopened first.

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

So tier (ii) is all-or-nothing here: to move either `:375` or `:383` — the two clusters that block
**all 544** operations (`outputs/plr-sema/unknown_ledger_260904_before.json:39-57`, `:86-104`) — the
increment must AST-derive the backend class's method signatures.

> **Round-1 correction to the cost argument (C17), which does not move the disposition.** The draft
> called that *"a whole increment's work"* and priced the **general** case while charging the
> **specific** one for it. On the frozen benchmark the backend is a single named literal class —
> `example.get("backend", "LiquidHandlerChatterboxBackend")`
> (`plr-sema/eval/oracle_common.py:362`) — not a surface, and its `pick_up_tips`/`aspirate`/`dispense`
> signatures are AST-derivable by machinery the derive package already runs over PLR. **The corrected
> reason for deferring is: the general derivation is a new class surface with its own measured
> selection and its own registry argument, AND this increment already carries more soundness risk than
> it can absorb** — round 1 conceded eight blocking items. Deriving over one benchmark backend would
> produce a fact that cannot enter the shipped contract table (which is keyed on PLR's own surface, not
> on a harness choice), i.e. a benchmark-local hack rather than increment 7's derivation. **DEFER
> stands**, alongside the `pred`-aware `BRANCH` the same evaluator serves (increment 3 §12.3.6 B2).
>
> **One passing fact from round 1 that reinforces E-UNCOND(5):** `:377-378`'s
> `if len(vars_keyword) > 0: return set()` makes `:381`'s second conjunct dead — an early-return fact
> the survey's trail records nothing about
> (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:377-381`).

**What defers with it:** the deck-membership observation (`:321`), the lid topology (`:116`/`:117`, and
increment 4 §13.1's lid disposition stands), the head channel count (`:409`), the well-seeding
observation that would move `volume_state_unknown`, and `can_pick_up_tip` (`:514`), which needs the
backend's *method body*, not just its signature.

---

## 15.7 Reasons

> **Normative — PROPOSED, PENDING USER APPROVAL (§15.14 Q4). `REASON_VOCABULARY` 10 → 12, of cap 12**
> (`plr-sema/src/plr_sema/verdict.py:133-168` enumerates the current ten; HM-14 is `CAPPED` at
> `declared=12`, `plr-sema/src/plr_sema/_hand_maintained.py:613-631`, so live 12 ≤ 12 and **no
> `declared` edit is needed**). This exhausts HM-14's headroom, which is why it is the user's call and
> not the sprint's. Two members:
>
> - **`guard_operand_unknown`** — the condition parsed to a non-`Opaque` predicate and every free name
>   resolved, but an **operand of this call** is ⊤: a non-literal kwarg, a kwarg `lower_calls` renamed
>   to `?<j>` (`plr-sema/src/plr_sema/check/ir.py:796-808`), or a `RESOURCE` whose declared `type`/
>   `element_type` cannot decide an `IsInstance`.
> - **`guard_env_dependent`** — the condition parsed, but ≥ 1 free name does not resolve to a call
>   operand or to an α/β binding at all: it names instance state (`self.<x>`), a module global, a
>   backend attribute, or a local the idioms decline; **or the guard's reachability is not established
>   — `depth >= 1` (E-UNCOND(4)), or a depth-0 empty trail in a `K` containing an earlier
>   `Return`/`Try`/`Raise` (E-UNCOND(5))**; **or the guard is a derived tier-(iii) re-raise** (§15.5).
>   This is tiers (ii) **and** (iii) together, plus round 1's two new give-up points.
>
> **If the user declines, the fallback is one member, not zero.** Ship `guard_env_dependent` alone
> (`REASON_VOCABULARY` 10 → 11, one slot of headroom kept) and let `guard_operand_unknown`'s
> population fold into it. The cost is exactly the distinction that scopes increment 7 — *"the analyzer
> needs one observation it could take"* versus *"the analyzer needs one value this call did not
> carry"* — and, concretely, §15.9's GO gate would lose one of its two zero-conditions and would have
> to be restated over `guard_predicate_unparsed` alone, which is a weaker gate.

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
  delta legible: the residual `guard_predicate_unparsed` count *is* the grammar's coverage gap —
  **but only under the nested-`Opaque` rule below, which round 1 showed the draft needed and lacked.**

> **Normative (nested `Opaque` — round 1, C15).** **A predicate containing ANY `Opaque` node is
> `Opaque` for reason-assignment purposes** (i.e. it keeps `guard_predicate_unparsed`), while still
> being **evaluated** under Kleene — so an `And` with an `F` conjunct still decides. Two lines, no
> vocabulary cost.
>
> **Without it the three-reason taxonomy has a hole, and §15.7's own legibility claim is false.**
> §15.3's own worked example creates it: `invalid_channels = [c for c in channels if c not in
> self.head]` (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:405-409`) — α binds
> the term, the `if` clause parses `Opaque`, and every free name resolves. The guard
> `not len(invalid_channels) == 0` is then not `guard_predicate_unparsed` (the top node parsed), not
> `guard_operand_unknown` (no call operand is ⊤; the failure is syntactic, inside the comprehension),
> and not `guard_env_dependent` (the free name resolved via α). All three definitions exclude it, and
> there are **384 such findings** (`outputs/plr-sema/unknown_ledger_260904_before.json:133-140`).
> Under the rule they stay `guard_predicate_unparsed`, which is what makes the ledger delta a coverage
> measure a reader can interpret rather than an overstatement.
- **A third member separating tier (iii) from tier (ii): rejected.** It would be a 13th and the cap
  conversation is the user's, not the sprint's
  (`.praxia/docs/plans/260904_plr-sema-sprint127-predicates.md:130-131`). The (ii)/(iii) distinction is
  published in §15.9's measured set, where it belongs, rather than encoded in a wire vocabulary.
- **Shipping only `guard_operand_unknown`: considered, and rejected as the weaker option.** It would
  collapse "the analyzer needs one observation it could take" into "the analyzer needs one value this
  call did not carry", which is exactly the distinction the next increment is scoped by. **This is the
  cheaper fallback if the user declines to exhaust HM-14's headroom** (§15.14 Q4).

**Cap consequence, stated rather than buried: if the user approves, after this increment
`REASON_VOCABULARY` is at 12 of 12 and HM-14 has zero headroom.** Any future give-up point then needs
the cap conversation. Round 1's own argument for approving is that item 3's widening of
`guard_env_dependent` to cover unestablished reachability makes that member carry strictly more
traffic than the draft anticipated, which sharpens rather than blurs the distinction from
`guard_operand_unknown`.

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

> **PENDING USER DECISION — HM-25 `declared` 8 → 9. This round's recommendation: spend it.** The
> draft's position was *"neither row"*; round 1 broke the leg it rested on and the position is
> withdrawn. **α and β are filed as one HM-25 entry** — an "argument-default and filtered-comprehension
> binding shapes" pattern — with `breaks_when` naming **AC-15.2's exact floor as the loud test**.
> `live_rows()` stays 24 against `BUDGET_CAP = 24`
> (`plr-sema/src/plr_sema/_hand_maintained.py:43`, `:957-961`); **no row is added**, so no cap
> conversation is opened. **Nothing in band B is dispatched until the user answers.** If the user
> declines, α and β ship **unregistered** against a criterion they demonstrably meet, and AC-15.7
> asserts HM-25 `declared == 8`.
>
> **Why HM-25 and not HM-24, which is what the challenger proposed.** The registry's criterion is
> silent-versus-loud. (1) HM-24's harm is a *silent family collapse* —
> *"the tip-requiring/tip-loading families silently empty"*
> (`plr-sema/src/plr_sema/_hand_maintained.py:874-880`). α's failure returns one guard to
> `guard_predicate_unparsed`, its pre-increment reason, and empties **no family**; there is no family
> here. (2) AC-15.2 publishes an exact floor that goes red on a PLR rewrite, which is HM-25's own
> criterion verbatim — *"Fails LOUDLY here (unlike HM-24) … exact-count/gate assertions … go red"*
> (`plr-sema/src/plr_sema/_hand_maintained.py:945-948`). (3) HM-25's `what` **already carries P3a** as
> `<p> = <p> or self.<x> or list(range(len(<q>)))`
> (`plr-sema/src/plr_sema/_hand_maintained.py:899-906`) — β's three-operand sibling, same idiom family,
> same row. The B1 precedent the challenger invoked went to HM-24 because *"R1 (§14.6) makes its
> `ast.For` node load-bearing for SOUNDNESS"* (`plr-sema/src/plr_sema/_hand_maintained.py:855-861`),
> which is a claim about a *loop-recognition* rule, not about a binding shape whose failure is a
> published count going red.
>
> **The draft's own reasoning, kept for the record, and where it fails.** Three reasons, in decreasing
> strength; **reason 1 no longer survives unqualified**.
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
> **What round 1 attacked, and what it found.** The draft nominated reason 3 as its weakest and rested
> on reason 1. Round 1 went at reason 1 instead and broke it two ways. (a) The single-write clause
> covered `x` but not the **iterand**, so a PLR rewrite that moved a comprehension below a rebinding of
> its own `iter` would leave α matching and binding a term over the *wrong* sequence — a wrong verdict,
> silently, with no published count moving. (b) The **delegate→caller substitution** is unspecified, so
> α's terms are matched in the delegate's namespace and evaluated against the entry point's kwargs,
> which works today only by name coincidence. §15.3's iterand clause repairs (a); §15.4's
> E-CALL(depth) forbiddance repairs (b) — **but only because both were written down in this
> revision**, and "reason 1 holds *given two new normative clauses*" is not the same claim as "reason 1
> holds". **Hence the row.** The correct disposition is HM-25 8 → 9, a per-row ceiling spend the user
> must approve before band B
> (`.praxia/docs/plans/260904_plr-sema-sprint127-predicates.md:132-135`); AC-15.7 asserts HM-25
> `declared == 9` and HM-24 `declared == 3` — the reverse of the draft's assertion.

**`cache_key` gains no component, and the whole cache goes cold anyway — round 1, C16.** Its `env`
element already exists and is already the fifth (`plr-sema/src/plr_sema/check/ir.py:918-953`); this
increment adds no component and threads no new value. But `contracts_sha` is
`sha256(contracts_json)`, computed at `plr-sema/src/plr_sema/check/ir.py:946`, and T30 **regenerates
`plr-sema/data/derived_contracts.json`** to add `predicate` and `param_defaults`. **So every key moves,
for every caller, not just the benchmark: the cache is cold after T30 by design.** O1 additionally
moves `bc_hash` for the benchmark, for the same reason. The draft's *"every key it produces is
byte-identical to today's"* was false and sat in the same paragraph as "the benchmark's keys move".
**The property that actually matters is that `env` is untouched** — no partitioning, no correctness
event, a full re-computation. T30's gate includes checking that no test pins a literal `cache_key`.
Under Q2-defer, `strictness` never enters `env`.

---

## 15.9 Measured sets (band B, T30)

> **Normative.** `outputs/plr-sema/t30_measured_260904.json` publishes, computed over the whole
> `plr-sema/data/derived_contracts.json` and over the frozen benchmark's own lowered IR calls (via
> `lower_row_calls`, `plr-sema/eval/oracle_common.py:551-571`, with no analyzer change and no
> `check_ir` invocation):
>
> 1. **Parse coverage.** Of all guards in the contract table: the count parsing to a non-`Opaque`
>    predicate, broken down **per atom kind** (`Cmp`, chained `Cmp`, `Is`, `IsInstance`, `AllOf`/
>    `AnyOf`, `SetOf`-uniqueness, `Filtered`-emptiness, `TRUE`), and the count remaining `Opaque` with
>    the ten most frequent unparsed shapes named.
> 2. **Binding coverage.** The complete set of `(K, x, idiom, term)` tuples α and β bind, and the count
>    of guards with ≥ 1 free local of which every / some / no local binds. **Plus two counts round 1
>    requires**: (i) the number of executed `pick_up_tips` operations for which `channels_for_call`
>    returns non-`None` (D2, floor `== 223`), and (ii) the number of depth-≥1 guards whose free vars
>    *would* have resolved by name coincidence against the entry point's kwargs had E-CALL(depth) not
>    forbidden it (item 13), so the size of what is forgone is on the record.
> 3. **Per ledger cluster** (all 54): the predicted tier, `parsed?`, `bound?`, and **the reason the
>    guard ACTUALLY carries** after §15.7. §15.1's (i)/(ii) tiering is a prediction; this block is the
>    measurement, and any divergence between them is published rather than absorbed.
> 4. **Per executed operation**: the residual **reason set**, plus the residual tier set as a published
>    annotation, plus — separately — the count of guards on that operation that are `parsed but
>    operand-unknown`, so a residual caused by a missing declared type is distinguishable from a
>    genuinely environmental one.
> 5. **The O1 delta**: (4) computed twice, with and without §15.4's operand observation. If the two
>    differ by zero, O1 is not doing what §15.4 claims and the gate is re-opened.
>
> **Normative (the gate is stated over REASONS, not over tiers — round 1, C8).**
>
> > **GO iff ≥ 1 executed real operation carries ZERO findings whose `reason` is
> > `guard_predicate_unparsed` and ZERO whose `reason` is `guard_operand_unknown`** — i.e. every guard
> > on it is either decided (`SAFE`/`WILL_FAIL`), or undecided because a free name resolves to state
> > outside the call (`guard_env_dependent`), or a derived tier-(iii) re-raise (which also carries
> > `guard_env_dependent`).
>
> NO-GO otherwise: publish the counts and the structural reason in §15.15, keep the derive code (it is
> a strict information gain on the contract table either way), and bring the decision to the user
> before the evaluator lands.
>
> **Why not the draft's tier formulation.** The draft's *"residual tier set ⊆ {(ii), (iii)}"* has no
> mechanical referent: there is no `tier` field on `InlinedGuard`
> (`plr-sema/src/plr_sema/derive/__init__.py:452-478`), none in `derived_contracts.json`, and §15.1's
> tiering is a table in a Markdown document. Either the measurement script transcribes that table — in
> which case the gate is this document's own prediction restated as a measurement, and §15.9's framing
> *"to be falsified by the measurement and not assumed by it"* is unsatisfiable — or the tier is
> derived. **The obvious derivation is worse.** *"Condition parses non-`Opaque` ∧ all free names
> resolve ⇒ (i); else (ii)"* makes every guard this increment fails to decide (ii) by construction, so
> every operation's residual is ⊆ {(ii), (iii)} trivially and the gate **always passes**. Reasons are
> shipped (`plr-sema/src/plr_sema/verdict.py:133-168`), mechanical, and non-tautological: a guard
> carries `guard_predicate_unparsed` iff the grammar failed on it, which is exactly the thing the gate
> is trying to see. **The gate number must be computable from `t30_measured_260904.json` without
> reading this document.**

**Expected candidates and their expected residuals — this document's own prediction, to be falsified by
the measurement and not assumed by it. Revised in round 1; every row moved.**

| method | ops | predicted residual (reasons) | the guards that must clear, and how |
|---|---|---|---|
| **`pick_up_tips`** | 223 | **{`guard_env_dependent`} — GO** | `liquid_handler.py:498` clears (α + O1 + restated E-TYPE ⇒ `IsInstance` `T` ⇒ `Not` `F` ⇒ `AnyOf` `F` ⇒ `SAFE`); `:502` clears (G4 + `channels_for_call`, **conditional on D2**); `:522` clears (G2 + β + E-CALL(β) + `channels_for_call`); `:514`/`:375`/`:383`/`:409`/`:321` are `guard_env_dependent`; `:576` is derived (iii) ⇒ `guard_env_dependent` + `excludes_sites`; `:535` is already decided |
| `transfer` | 19 | {`guard_predicate_unparsed`} — NO-GO | `:1335`/`:1337`/`:1340` **now clear via D1's `param_defaults`** (they did **not** on the grammar alone), but `transfer` inherits `aspirate`'s `:990` and `dispense`'s `:1202`, which need γ |
| `aspirate` | 77 | {`guard_predicate_unparsed`} — NO-GO | `:959` clears; **`:875` does NOT** (E-CALL(depth) forbids the depth-1 resolution); `:990` needs γ; `:117` is `guard_env_dependent` under E-UNCOND(5) |
| `dispense` | 40 | {`guard_predicate_unparsed`} — NO-GO | `:1153` clears; **`:1185`/`:1188` do NOT** (β binds no elements, C6); `:1202` needs γ |
| `drop_tips` / `discard_tips` | 65 | {`guard_predicate_unparsed`} — NO-GO | `:666` binds `tips` by loop-append and `:657` is a numeric `Cmp`; both fail closed (§15.1.2). `:647` is now `½` rather than a **false `WILL_FAIL`** (C4) |
| `stamp` | 27 | {`guard_predicate_unparsed`} — NO-GO | `containers` is branch-bound (§15.1.4); `:1770`/`:1920` are `guard_env_dependent`, not false `WILL_FAIL` |
| `move_resource` / `move_lid` / `move_plate` | 93 | out of scope — `unresolved_delegate` (§15.0) | `:2092` is derived (iii) |

**So the gate rests on `pick_up_tips` alone, and it now has three points of failure, not one.** All
three are measurable in T30 **before** T31 constructs a single verdict, which is exactly what the
ordering gate above exists for:

1. **O1's element walk must yield `"TipSpot"`** for `tip_spots`' cells. If it does not, `:498` is ½,
   `pick_up_tips` keeps a `guard_operand_unknown` residual, and the increment is NO-GO on every
   operation. §15.9(5) measures O1's effect directly rather than assuming it. O1 is ~40 LOC (§15.4),
   not the ~25 the draft claimed.
2. **`channels_for_call` must return an exact tuple on 223 real rows** (D2). `:502`'s
   `len(set(use_channels)) == len(use_channels)` clears only then. The path for `pick_up_tips` is
   `channel_default_param["pick_up_tips"] == "tip_spots"` → `call.kwargs["tip_spots"]` must be an
   `ir.Seq` → `tuple(range(len(items)))`
   (`plr-sema/src/plr_sema/check/tipstate.py:262-269`); that should hold, since `tip_spots` is a
   trusted param and so is not renamed `?<j>` (`plr-sema/src/plr_sema/check/ir.py:796-808`). **But no
   number anywhere covers the tier-1 benchmark**, and `tipstate.py` itself records that *"the shipped
   fixture's operations never resolve an exact channel set"*
   (`plr-sema/src/plr_sema/check/tipstate.py:551-565`). If the measured count is 0 the gate fails on
   `:502` for a reason unrelated to the grammar, and without this block §15.9 would have misattributed
   it to O1.
3. **`tip_spots` must lower as an `ir.Seq`**, which (2) depends on and which block (2) also exposes.

**On `:522` surviving C6 and C14 together, explicitly, because round 1 disputed it.** `offsets` is
written **exactly once** in `pick_up_tips` — the β assignment at
`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:517`; `:493` is a kwarg pass inside
`_log_command`, not a write — so C6's eight-second-writes finding does not reach it. The "β is
unreachable" attack rested on E-CALL step (2) returning a signature default of `None`; step (2) had
**no data source at all** before D1, and after D1 it returns `Lit(None)`, which is statically
known-falsy and which E-CALL(β) case (3) routes to the β binding. Both paths end at
`Len(offsets) = Len(tip_spots)`. **The gate keeps a predicted GO candidate.**

---

## 15.10 The oracle and the fence

**Tier 1 re-run is the gate: 0 unsound, under the UNMODIFIED predicate.** A `SAFE` on an operation that
raised is the failure this increment makes possible **for the first time** — increments 1–5 could
produce `WILL_FAIL` and per-finding `SAFE`, but no path from a parsed condition to a `SAFE` on a guard
the analyzer previously declined. Round 1 deleted the draft's narrowing (§15.5): the predicate stays
exactly `plr-sema/eval/oracle_common.py:645-647`, and `rows_excused_by_scope` is published as an
annotation with **no threshold and no gate effect**. T32 contains no reference to `exc_class` in the
comparison path.

**The other direction — a false `WILL_FAIL` on an operation that ran clean — is the one round 1 found
live, and it is now fenced by construction rather than by measurement.** `compare` scores
`verdict == "will_fail" and outcome == "ran_ok"` as unsound at the same three lines, and `join`
propagates one such finding to the whole operation. E-UNCOND(4)/(5) and the restated E-TYPE are the
three clauses that stop it; AC-15.6's fixture set asserts each by name.

**Non-regression, each re-measured and published, any movement attributed before the run is accepted:**
m1 199/199, m2 289/289, v1 67/67 `WILL_FAIL` at the raised index, tier 2b 16 fixtures with
`region_unsound` 0 and `region_will_fail_fired` 7, tier 1 `rows_executed` 343 / `setup_error` 0 /
crosscheck 191/191, and the spec lint at 24 passed with six specs at zero failing citations
(`.praxia/docs/plans/260904_plr-sema-sprint127-predicates.md:144-151`).

**The ledger after-run.** `outputs/plr-sema/unknown_ledger_260904_after.json`, produced by the same
script with no change, plus a published delta over: `n_findings_by_reason`, `n_clusters`, and the
`per_op_reason_set_histogram`. **`unknown_rate` is expected to stay 1.0** under §15.5's finding, and
that expectation is recorded here so a 1.0 at close is read as "predicted", not as "the increment did
nothing".

> **The `guard_predicate_unparsed` 5,656 is published with NO floor — round 1, C5.** The draft made it
> the headline with a floor of ≥ 1,000 converted. That floor is met by the **reason rename alone**:
> `:375`'s `len(missing) > 0` (544 findings) and `:383`'s `strictness == Strictness.STRICT` (544)
> both parse to non-`Opaque` predicates under G1 and both decide **nothing** — their free names
> resolve to a `BinOp` and to module state respectively, so both become `guard_env_dependent`. 1,088 >
> 1,000 from two clusters this document itself tiers (ii) and defers, before a single guard is
> evaluated; add `:409`'s 384 and the floor is met three times over. **An implementation with the
> grammar stubbed to "parse everything, resolve nothing" would have passed AC-15.8's headline.** The
> count is still published, as the grammar's coverage measure and nothing more; the number that gates
> is `n_findings_decided` (AC-15.8).
>
> **The consistency invariants must still hold on the after-ledger.** `consistency.ok` is `true`, with
> `sum(per_method) == n_ops_blocked` for every cluster and `sum(histogram.n_ops) == n_ops_unknown`
> (`plr-sema/eval/unknown_ledger.py:332-407`). A violation means the clustering arithmetic drifted, not
> that the increment worked.

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
>
> **Round-1 consequence for mutant (c), stated before the run rather than discovered by it.** Under the
> restated E-TYPE a `_generic_plr_type_name`-derived declaration is **never exact**, so the `F` branch
> is unreachable and `IsInstance` is `T`-or-`½`. A non-`TipSpot` element therefore yields **½, not
> `WILL_FAIL`** — mutant (c) is expected to report `0 achieved` and `0 unsound`, and it is published as
> such. The floor of ≥ 1 is carried by (a) and (b), which do not depend on the type atom. **This is
> the fail-closed price of not fabricating the `:647` false `WILL_FAIL` (C4)**, and recording it here
> is what stops a zero on (c) being read at close as an implementation defect. Recovering a decidable
> `F` on (c) needs an *exact* declaration, which is a graph-lane property (§15.4 E-TYPE) and is
> increment 7's.
>
> **Mutant (b) survives E-CALL(β) explicitly**: a short but non-empty `offsets` list is statically
> known-truthy, so case (2) resolves it to the caller's value rather than to the β length, and the
> chained equality at `:522` is `F` for an `assert`-kind guard ⇒ fires ⇒ `WILL_FAIL`. Had E-CALL(β)
> let β win unconditionally, this mutant would have been silently defeated — which is the false-`SAFE`
> direction §15.4 names.

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
  an unparsed guard, fails it. **Plus three round-1 fixtures on E-TYPE and nesting**:
  `IsInstance(declared="Container", (TipSpot, Trash))` is **½** (not `F` — C4a's false-`WILL_FAIL`
  mechanism); `IsInstance(declared="Well", (Container,))` is **`T`** (not ½ — C4b); and a predicate
  whose top node parses but which contains an `Opaque` sub-node keeps `guard_predicate_unparsed` while
  still evaluating `F` when conjoined with an `F` conjunct (C15).
- **AC-15.2 (the two idioms bind, are measured, and fail closed).** The complete
  `(K, x, idiom, term)` selection over the whole PLR surface is published with **≥ 3** α entries
  (`liquid_handler.py:496`, `:645`, `:873`) and **≥ 6** β entries — a floor **met by measurement, not
  by assertion**: the expected β population at this pin is **exactly eight** (`:517`, `:661`, `:963`,
  `:964`, `:965`, `:1157`, `:1158`, `:1159`), with `offsets` at `:962`/`:1156` correctly excluded.
  Five fail-closed fixtures, one apiece: a second write to `x` anywhere in `K` binds nothing; an
  assignment nested in an `if` that does not contain the guard binds nothing; a three-operand `or`
  chain whose middle operand is `self.<x>` binds nothing under β **and is instead resolved by the
  existing `channels_for_call`** (`plr-sema/src/plr_sema/check/tipstate.py:245-270`), asserted through
  the receiver's **derived** `channel_kwarg`/`channel_default_param` and never through a hand-typed
  `"use_channels"` (`plr-sema/src/plr_sema/check/tipstate.py:254-257`); an assignment *after* the
  guard's `lineno` binds nothing; and a guard whose `scope_trail` contains a `for` header targeting
  `x` binds nothing. The last two are the stub-defeating halves: an implementation matching on shape
  alone, without the position and scope tests, passes the first three and fails these.
  **Plus six round-1 fixtures.** Two on the β-preserving rebinding: `x = [f(e) for e in x]` preserves a
  β length binding, and `x = [f(a, b) for a, b in zip(y, x)]` does **not**. One on the iterand: a
  second write to α's `iter` name binds nothing. Three on E-CALL(β)'s truthiness branches, one per
  case, including **`offsets=[]` asserted to resolve to the β length and NOT to `Len == 0`** — the
  latter would be a false `WILL_FAIL` at `:522`, which is the stub-defeating half of this group.
- **AC-15.3 (the measured sets are published and the gate is decided by them).**
  `outputs/plr-sema/t30_measured_260904.json` carries all five blocks of §15.9, and the GO/NO-GO
  decision is recorded against the published **per-op reason set** — GO iff ≥ 1 executed real
  operation carries zero `guard_predicate_unparsed` and zero `guard_operand_unknown` findings.
  **The gate number is asserted computable from the JSON alone, without reading this document.**
  `pick_up_tips` is asserted **by name** to be that operation, or the divergence is recorded in §15.15
  and the decision goes to the user before AC-15.5's work starts. Block (3) additionally publishes,
  per cluster, the reason each guard **actually** carries against §15.1's predicted tier, and any
  divergence is recorded rather than absorbed.
- **AC-15.4 (the operand observation, its fail-closed rule, and the counterfactual).** After O1,
  `resources_from_example`'s output carries a non-`None` `type` for **≥ 90%** of the resources
  referenced by the benchmark's planned kwargs, and a non-`None` `element_type` for every `Ref`
  carrying a `cell` **whose parent's element-class set is a singleton**; the pre-O1 baseline (`type`
  from `deck_layout` only, `element_type` universally `None`,
  `plr-sema/eval/oracle_common.py:397-410`) is published beside it. **The count of parents with
  heterogeneous children — for which `element_type` is `None` by the fail-closed rule of §15.4 — is
  published beside the coverage numbers**, and a fixture asserts that a parent with two distinct child
  classes yields `element_type is None` rather than first-element-wins. §15.9(5)'s with/without
  residual comparison differs on **≥ 1** operation. A zero difference fails this criterion — that is
  the stub-defeating half, since a change that threads the field but never reaches an atom would
  otherwise pass on the field counts alone.
- **AC-15.5 (evaluation: F ⇒ SAFE, ½ ⇒ the finest reason, and E-SCOPE).** Four fixtures. (i) A guard
  evaluating `F` yields exactly one `Verdict.SAFE` finding at `guard.site` with `category == ""` and
  `reason == ""` — and, per E-UNCOND(6), the guard's own `scope_trail[0]` self-entry is asserted **not**
  to be evaluated a second time as a scope entry. (ii) A guard whose enclosing scope entry evaluates
  `F` yields `SAFE` **regardless of its own predicate**, asserted with the guard's own predicate at
  `T` — the shape is now `transfer`'s
  (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:1333-1340`), **not** the withdrawn
  `:1185`/`:1188` one, and `:1335`/`:1337`/`:1340` are asserted `SAFE` by name under D1's
  `param_defaults`. (iii) A guard with an unresolvable kwarg yields `guard_operand_unknown`; with an
  unresolvable free name, `guard_env_dependent`. (iv) One `Finding` per guard is preserved: an
  operation with `n` guards — **`k` of them tier (iii)** — yields exactly `n` findings, asserted as a
  count, and `join` is called once. (ii) is the stub-defeating half.
- **AC-15.6 (`WILL_FAIL` only when reachability is established, and the scope annotation).** A guard
  evaluating `T` at depth 0 with an empty `scope_trail` **in a `K` containing no earlier
  `Return`/`Try`/`Raise`/`Break`/`Continue`** yields `Verdict.WILL_FAIL` with
  `category == "precondition_state"`; the same guard yields `Verdict.UNKNOWN` with
  `reason == "guard_env_dependent"` under each of **eight** perturbations, one fixture apiece — a
  `while` header in the trail; a `for` header R1 did not bind; a trail entry parsing `Opaque`; a trail
  entry evaluating ½; a trail entry beginning `"else of: if "` whose test text is in `env` (which must
  **not** satisfy it, preserving increment 5's AC-14.4 behaviour); **the same guard at `depth == 1`
  with a `T` predicate** (E-UNCOND(4)); **`_check_no_lid`'s `:117`, asserted by name**, whose empty
  trail sits after the early `return` at
  `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:113-114` (E-UNCOND(5)); and a
  depth-0 empty-trail guard in a `K` containing an earlier `ast.Try`. Separately: **a tier-(iii) guard
  emits exactly one `Finding`, `Verdict.UNKNOWN`, `reason == "guard_env_dependent"`**, and contributes
  its `site` to `AnalysisReport.scope.excludes_sites`; tier (iii) is asserted to be selected by
  `guard.is_dynamic_raise` (`plr-sema/src/plr_sema/derive/__init__.py:501-505`) and **not** by any site
  list or condition-text match; `join`'s input multiset **is** asserted to contain it; and
  `check_graph`'s two-positional-argument call form returns a report whose `schema_version` is still 1.
  The `else of:` case, the `:117` case and the depth-1 case are the stub-defeating halves.
- **AC-15.7 (the vocabulary and registry arithmetic is exactly as specified, under the user's answers).**
  `len(REASON_VOCABULARY) == 12` against HM-14's unchanged `declared == 12`
  (`plr-sema/src/plr_sema/_hand_maintained.py:613-631`); the commit's parent has 10, so the diff is
  visibly 10 → 12; `len(live_rows()) == 24` and `BUDGET_CAP == 24`; **HM-25's `declared` is 9 and
  HM-24's is 3**, asserted directly, so a spend on the wrong row fails;
  `test_no_surface_exceeds_its_declared_size`, `test_total_declared_within_budget` and
  `test_reason_vocabulary_closed_forward` all pass, the last with both new members reachable from ≥ 1
  construction site. **Conditional on the two pending user decisions (§15.14 Q4, Q5).** If the user
  declines the HM-25 spend, this criterion asserts HM-25 `declared == 8` and α/β ship unregistered; if
  the user declines the second reason, it asserts `len(REASON_VOCABULARY) == 11`. Either way the
  assertion is exact and a silent divergence fails.
- **AC-15.8 (tier 1 — 0 unsound under the unmodified predicate, and the decided-findings floor).** The
  sidecar-gated replay reports `unsound == 0` under the **unmodified** predicate
  (`plr-sema/eval/oracle_common.py:645-647`, unchanged by this increment), `rows_setup_error == 0`,
  `rows_executed == 343`, crosscheck 191/191 at agreement 1.0, and `rows_excused_by_scope` published as
  an annotation with **no threshold**. The after-ledger is produced by the unmodified
  `plr-sema/eval/unknown_ledger.py` with `consistency.ok == true`, and the delta on
  `n_findings_by_reason` / `n_clusters` / `per_op_reason_set_histogram` is published.
  **The gated number is `n_findings_decided`** — findings whose emitted `verdict` is `Verdict.SAFE` or
  `Verdict.WILL_FAIL` — broken down **per PLR site**, with a floor of **≥ 223**. 223 is
  `pick_up_tips`'s own operation count from §15.9's candidate table, i.e. the minimum implied by one of
  its three tier-(i) guards clearing on every op; it is derived from this document's own prediction
  rather than asserted. `guard_env_dependent` and `guard_operand_unknown` counts are published
  **separately** and are explicitly **excluded** from "converted". The `guard_predicate_unparsed` delta
  is published with **no floor**, as the grammar's coverage measure only. **The stub-defeating half:
  an implementation that parses every condition and resolves nothing scores `n_findings_decided == 0`
  and fails** — which the draft's ≥ 1,000-converted floor would have passed (§15.10).
- **AC-15.9 (non-regression across tiers 2b and 3).** m1 199/199, m2 289/289, v1 67/67 at the raised
  index with 0 unsound, tier 2b at 16 fixtures with `region_unsound == 0` and
  `region_will_fail_fired >= 7` and `volume_will_fail_fired == 3`. Every number is re-measured against
  the sprint-123 close baseline and any movement is attributed before the run is accepted — the
  E-SCOPE rule is what could move tier 2b, by converting a previously-`UNKNOWN` guard to `SAFE` inside
  an executed region.
- **AC-15.10 (tier 3 — the predicate mutant fires at the raised index).**
  `plr-sema/eval/predicate_mutants.py` reports p1 with **0 unsound** in both directions and its
  achieved `WILL_FAIL`-at-the-raised-index count published against a floor of **≥ 1**, over all three
  mutators (duplicate `use_channels`, short `offsets`, non-`TipSpot` element), **published per
  mutator**. The duplicate-`use_channels` mutator is asserted to fire against an `assert`-kind guard
  specifically. **The non-`TipSpot` mutator is asserted to report `0 achieved` / `0 unsound`** under
  the restated E-TYPE's never-exact rule (§15.10), so a zero there passes and a `WILL_FAIL` there
  *fails* — an implementation that fabricated it would be the C4 false-positive mechanism reappearing.
- **AC-15.11 (this document is machine-checked).** `plr-sema/tests/test_spec_lint.py` gains
  `SPEC_INCREMENT_6` and parametrises it into both live-spec tests
  (`plr-sema/tests/test_spec_lint.py:212-255`); `.praxia/docs/INDEX.md` is regenerated; and
  `uv run pytest plr-sema/tests/test_spec_lint.py -q` is **actually run** with its result recorded —
  both the citation checker and the AC-gating half of the cross-reference checker reporting **zero**
  failing violations over this file, and the other six specs unchanged at zero.
- **AC-15.12 (tier (ii), conditional — only if the round overturns §15.6).** `env` gains
  `get_strictness`; the observation is returned from inside the executed window as increment 5's
  `volume_tracking_observed` is — **the producer is `run_runtime`'s return at
  `plr-sema/eval/oracle_common.py:370-373`**, not `run_static_calls`'s consumption of the already-
  returned flag at `:593-595`, which is what the draft cited (round 1, C18); `cache_key`'s fifth
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
| **T30** | Derive + measure (§15.2, §15.3, §15.4's O1 and `param_defaults`, §15.9). The typed mini-AST and the total `parse`; `InlinedGuard.predicate` as an additive field with `condition` retained; **`param_defaults` per contract entry** from `ast.arguments.defaults`/`kw_defaults` restricted to `ast.Constant`, fail-closed (D1); the α and β idioms with the scope clause, the **iterand** single-write clause and the **β-preserving-rebinding** exception; O1's **new element walk** with the **heterogeneous-parent singleton rule**; all five measured blocks published — including **D2's `channels_for_call` non-`None` count on executed `pick_up_tips` ops (floor `== 223`)** and the **name-coincidence exposure count** for depth-≥1 guards — and the GO/NO-GO recorded against the reason-based gate | modify `plr-sema/src/plr_sema/derive/__init__.py`, `plr-sema/src/plr_sema/derive/receiver_state.py`, `plr-sema/src/plr_sema/derive/__main__.py`, `plr-sema/eval/oracle_common.py`, `plr-sema/data/derived_contracts.json` (regenerated — this moves `contracts_sha` and cools the whole cache by design, §15.8), `plr-sema/tests/test_derive.py`; create `plr-sema/eval/t30_measure.py` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_derive.py -q`; **`uv run pytest plr-sema/tests/test_cache.py -q`** (no test may pin a literal `cache_key`); then regenerate the contract table and run `t30_measure.py` into `outputs/plr-sema/t30_measured_260904.json` — satisfying **AC-15.1**, **AC-15.2**, **AC-15.3**, **AC-15.4** | ~530 | — | Sonnet — six selections, each measured and published rather than asserted; the gate lives here, and three of its preconditions (O1's element type, D2's channel set, `tip_spots` lowering as a `Seq`) are measurable only in this row |
| **T31** | The evaluator and the reasons (§15.4, §15.5, §15.7): `plr-sema/src/plr_sema/check/predicate.py` with E-CALL (incl. **`param_defaults` step (2)**, **E-CALL(5)** parameter-rebinding, **E-CALL(β)** truthiness, **E-CALL(depth)** forbiddance) / **restated E-TYPE** / E-SCOPE over `scope_trail[1:]` / E-VERDICT / E-UNCOND **(1)–(3) plus (4) depth, (5) empty trail, (6) self-entry**; **tier (iii) derived from `guard.is_dynamic_raise`, emitting one `UNKNOWN`/`guard_env_dependent` `Finding` plus an `excludes_sites` entry**; the **nested-`Opaque`** reason rule; dispatch that skips guards the tip and volume families already claim; `SoundnessScope` (one field, `excludes_sites`) and `AnalysisReport.scope`; `REASON_VOCABULARY` 10 → 12 | create `plr-sema/src/plr_sema/check/predicate.py`; modify `plr-sema/src/plr_sema/check/__init__.py`, `plr-sema/src/plr_sema/verdict.py`, `plr-sema/tests/test_check_graph.py`, `plr-sema/tests/test_verdict.py`, `plr-sema/tests/test_hand_maintained_ratchet.py`, and the fixtures under `plr-sema/tests/fixtures/` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_check_graph.py -q`; `uv run pytest plr-sema/tests/test_verdict.py -q`; `uv run pytest plr-sema/tests/test_hand_maintained_ratchet.py -q`; `uv run pytest plr-sema/tests/test_tip_typestate.py -q` — satisfying **AC-15.5**, **AC-15.6**, **AC-15.7** | ~560 | T30 + a recorded GO + the user's answers to §15.14 Q4/Q5 | Sonnet — **E-UNCOND(4)/(5) and the restated E-TYPE are the three clauses standing between this row and a false `WILL_FAIL` on ~256 clean operations**, and the shipped precedent (`volume_guard_is_unconditional`) implements the wrong reading of (5) |
| **T32** | The oracle (§15.10): tier-1 re-run under the **UNMODIFIED** unsoundness predicate, with `rows_excused_by_scope` published as an annotation and **no `exc_class` reference anywhere in the comparison path**; `n_findings_decided` per PLR site with its ≥ 223 floor; m1/m2/v1/tier-2b non-regression; the after-ledger with `consistency.ok == true` and its published delta; `plr-sema/eval/predicate_mutants.py` with p1's three mutators | create `plr-sema/eval/predicate_mutants.py`; modify `plr-sema/eval/oracle_replay.py`, `plr-sema/eval/tip_mutants.py`, `plr-sema/eval/tier2_extractor.bth.toml`, `plr-sema/tests/test_oracle_replay.py` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_oracle_replay.py -q`; then the tier-1 replay with its three standard flags, `unknown_ledger.py` into `unknown_ledger_260904_after.json`, `predicate_mutants.py`, `tip_mutants.py`, `volume_mutants.py` and `region_oracle.py` — satisfying **AC-15.8**, **AC-15.9**, **AC-15.10** | ~300 | T31 | Sonnet — every published number is a measurement; this row shrank because the narrowed-predicate comparison path was deleted |
| **T33** | Lint and index: add `SPEC_INCREMENT_6` to `plr-sema/tests/test_spec_lint.py:28-37`'s constants and parametrise it into both live-spec tests (`plr-sema/tests/test_spec_lint.py:212-255`); regenerate `.praxia/docs/INDEX.md`; **actually run the lint and record the result** — AC-15.11 was a prediction no one in round 1 could execute | modify `plr-sema/tests/test_spec_lint.py`; regenerate `.praxia/docs/INDEX.md` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_spec_lint.py -q` — satisfying **AC-15.11** | ~6 | — | Haiku |
| **T34** | **CONDITIONAL — do not start. Q2's round-1 disposition is DEFER (§15.6, reaffirmed with a corrected cost argument), so this row belongs to increment 7.** Tier (ii) (#4981): `get_strictness` as an `env` member; the observation record for backend class and signature, deck membership, head channel count and lid topology; the backend-signature derivation with its measured selection; `cache_key` partitioning | modify `plr-sema/src/plr_sema/check/__init__.py`, `plr-sema/src/plr_sema/check/ir.py`, `plr-sema/src/plr_sema/derive/receiver_state.py`, `plr-sema/eval/oracle_common.py`, `training/verify/verifier.py`, `plr-sema/tests/test_cache.py` | `uv sync --all-packages`; `uv run pytest plr-sema/tests/test_cache.py -q`; `uv run pytest training/tests/test_verify_postconditions.py -q` — satisfying **AC-15.12** | ~300 | increment 7 | Sonnet |

**Sizing note, revised honestly after round 1.** T30 grew ~420 → **~530**: `param_defaults` is ~30 LOC
of new derivation (D1), O1 is ~40 rather than ~25 and is a *new* element walk rather than an extension
of `resource_types_from_kwargs` (C11a), the heterogeneous-parent rule is ~5 more, and blocks (2)'s two
new counts — D2's `channels_for_call` tally and the name-coincidence exposure — are ~35 together.
T31 grew ~450 → **~560**: three E-UNCOND clauses, three E-CALL clauses, the restated E-TYPE, the
derived tier-(iii) path, the nested-`Opaque` rule, and roughly a dozen new fixtures. T32 **shrank**
~380 → **~300**, because deleting the fence narrowing removes an entire comparison path and its
published count. **T30 at ~530 is past one session and splits cleanly** at the grammar (G0–G6, pure,
with its own fixtures) versus the idioms plus `param_defaults` plus O1 plus the measurement script.
**Do not split T30 from T31 across a sprint boundary in the other direction**: a landed T31 without
T30's published measurement is the configuration §15.9's gate exists to prevent.

**One item this document deliberately does NOT budget: the delegate→caller argument map.** §15.4's
E-CALL(depth) forbids the resolution rather than building it. Building it — a `delegate_arg_binding`
map over both positional and keyword arguments, matched against the delegate's own `ast.arguments`,
fail-closed on `*args`/`**kwargs`/`Starred`/a delegate called more than once, using P9's shipped
singleton test (`plr-sema/src/plr_sema/derive/receiver_state.py:957-959`) — is **~90 LOC over a new
derived field with its own measured selection and its own registry argument**. It would land `:875`
and `:117`, and it belongs in increment 7 with the tier-(ii) work.

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
  `{guard_env_dependent}`-only residual (§15.9). **Round 1 disposed it: NOT adopted, deferred to
  increment 7, to be revisited alongside the `pred`-aware `BRANCH`** (§15.14 Q3). It is a *loop*
  recognition rule and therefore lands in increment 5 §14.6 R1's territory; this round already
  conceded eight blocking items, and D1's `param_defaults` restores `transfer`'s three guards at
  strictly lower risk. Adopting γ would grow T30 by roughly 60 further lines on top of the ~530 it
  already carries.
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
- **The delegate→caller argument map**, forbidden by §15.4's E-CALL(depth) and sized at ~90 LOC in
  §15.12's sizing note. Increment 7, with tier (ii).
- **A site-keyed soundness-fence narrowing.** The ~3-line `traceback.extract_tb(...)[-1]` capture at
  `training/verify/verifier.py:143` that would let the fence distinguish a backend re-raise from a
  PLR-layer raise is increment 7's, where a joined `SAFE` first becomes possible (§15.5).
- **Precision targets.** Deferred row (f) stands
  (`.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md:2524`). AC-15.8's floor of ≥ 223 decided
  findings is a *floor against a null result*, not a target — and it replaces the draft's ≥ 1,000
  converted findings, which round 1 showed was met by the reason rename alone (§15.10).
- **#4923 / #4924** — decision hooks only, per the plan's §3.5–3.6. **#4956** is the Coxswain track.

---

## 15.14 The six questions, and their round-1 dispositions

**Four of the six are now disposed by argument or measurement. Two remain open only because they are
the user's, not the round's, and one further user decision (Q7) was raised by the round itself.**

1. **Q1 — is the coupling in §15.5 real, and does the sprint's headline move? DISPOSED: the coupling
   holds; the substitution is PENDING USER APPROVAL, recommended.** The stated refutation criterion
   was *"name one executed operation whose non-(iii) residual is empty."* The re-run ledger answers it
   by measurement: `_check_args`'s two tier-(ii) guards carry `n_ops_blocked` 544 with `per_method`
   summing to 544 (§15.0), so **no such operation exists**. The challenger's proposed refutation — 12
   unaccounted operations — was arithmetic: they are duplicate `move_*` occurrences the pre-fix
   `(row_id, op_id)` set keying folded away, now published in `collision_ops`. The coupling is
   additionally now structural via tier (iii) ⇒ `UNKNOWN`.
2. **Q2 — does §15.6's evidence close tier (ii)? DISPOSED: DEFER stands, with a corrected reason.**
   `strictness == Strictness.STRICT` is gated behind `len(extra) > 0` in its own enclosing scope
   (`external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:380-383`), so the one cheap `env`
   member converts no guard — round 1 conceded this half outright. It also showed the draft's *cost*
   argument was wrong: on the frozen benchmark the backend is one named literal class, not a surface.
   **The corrected disposition is "deferred because the general derivation is a new class surface with
   its own measured selection, and because the increment already carries more soundness risk than it
   can absorb"** — not "because the specific case is expensive" (§15.6).
3. **Q3 — does γ (§15.13) belong in this increment? DISPOSED: no. Deferred to increment 7, to be
   revisited alongside the `pred`-aware `BRANCH`.** Without it `aspirate` and `dispense` — 117 of 544
   operations — keep a `guard_predicate_unparsed` residual and the gate rests on `pick_up_tips` alone,
   which is a real cost and is stated as one. Against it: γ is a loop-recognition rule in increment 5
   R1's territory, this round already conceded eight blocking items, and D1's `param_defaults`
   restores `transfer`'s three guards at lower risk.
4. **Q4 — two new reasons, or one? PENDING USER APPROVAL; recommended: two.** Shipping both exhausts
   HM-14 at 12 of 12 (`plr-sema/src/plr_sema/verdict.py:133-168`). §15.7's mechanical
   distinguishability test — *did every free name resolve?* — survived round 1, and item 3's widening
   of `guard_env_dependent` to cover unestablished reachability makes that member carry strictly more
   traffic than the draft anticipated. **The one-member fallback is described in §15.7 and costs the
   distinction that scopes increment 7 plus one of the GO gate's two zero-conditions.**
5. **Q5 — is §15.8's "neither HM-24 nor HM-25" position sound? DISPOSED: no. HM-25 `declared` 8 → 9 is
   PENDING USER APPROVAL; recommended: spend it.** The position rested on reason 1, and round 1 broke
   reason 1 two ways (the unconstrained iterand, and the unspecified delegate→caller substitution).
   Both are repaired by new normative clauses in this revision, which is not the same as reason 1
   having held. The correct row is **HM-25**, not HM-24 — loud, exact-count-gated, same idiom family
   as the P3a entry already on it (`plr-sema/src/plr_sema/_hand_maintained.py:899-906`). `live_rows()`
   stays 24; no row is added and no cap conversation opens.
6. **Q6 — does §15.5's `excludes_sites` weaken the fence more than it appears? DISPOSED: yes, and the
   narrowing is deleted.** The requested construction exists and is easy: any `TypeError` row. There
   is no `exc_class → site` mapping that could be total or injective — the shipped taxonomy covers 132
   PLR-defined classes and none of the builtins the benchmark raises
   (`training/verify/data/plr_exception_taxonomy.json:1-29`), the runtime side captures no traceback,
   and `TypeError` is raised at four PLR precondition sites *and* re-raised at `:576`. The narrowing
   also purchased nothing, because §15.5 proves no joined `SAFE` is reachable for it to protect. The
   fence is now the unmodified `plr-sema/eval/oracle_common.py:645-647` and
   `rows_excused_by_scope` is a pure annotation.
7. **Q7 (raised by round 1) — the headline substitution itself. PENDING USER APPROVAL; recommended:
   substitute.** Formally distinct from Q1, which is the technical claim; Q7 is what the sprint may
   say it delivered. See §15.5's pending-decision box.

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

## 15.16 Round-1 disposition

**Round 1 was `praxia:spec-challenger` (C1–C18) against `praxia:spec-defender` (adjudications plus
three defender-identified gaps D1–D3), both at Opus, both against spec_version 16 at commit
`6407d92a`. Verdict on both sides: `needs_revision`.** This table records what each objection did to
the text. "Adopted" means the remedy is now normative here; "adopted (defender's form)" means the
challenger's diagnosis was accepted and his proposed remedy was replaced; "rebutted" means the text
did not change on the merits.

| id | disposition | what changed in the text | § touched |
|---|---|---|---|
| **C1** | adopted, magnitude corrected | E-UNCOND(5): a depth-0 empty `scope_trail` is not vacuously unconditional unless `K` has no earlier `Return`/`Try`/`Raise`/`Break`/`Continue`. The shipped `volume_guard_is_unconditional` precedent is named as implementing the *wrong* reading. Population is `:117` (163 ops) + `:2092` (93), not the filed ~268: `:1770`/`:1920` have three-deep `"else of: if …"` trails and were already blocked | §15.2 G0, §15.4 E-UNCOND(5), §15.1.4, AC-15.6 |
| **C2** | conceded in full | `InlinedGuard` has no `caller_scope`; E-SCOPE's bridged-guard clause is deleted. Remedy is the forbiddance, not the field: **E-UNCOND(4)**, no `WILL_FAIL` at `depth >= 1` | §15.4 E-SCOPE, E-UNCOND(4), AC-15.6 |
| **C3** | adopted (drop the narrowing); "no taxonomy exists" rebutted | The fence narrowing is **deleted**; the predicate stays `oracle_common.py:645-647` unmodified and `rows_excused_by_scope` becomes a pure annotation. A taxonomy does exist but covers 132 PLR-defined classes and none of the builtins or re-raise sites, and cannot be injective | §15.5, §15.10, AC-15.8, §15.14 Q6 |
| **C4** | conceded in full | E-TYPE restated: `T` iff is-or-subclass-of, `F` iff hierarchy-disjoint **and** exact, ½ otherwise; a `_generic_plr_type_name` declaration is normatively never exact, so the `F` branch is unreachable on the benchmark. Kills a live false `WILL_FAIL` on 65 `drop_tips`/`discard_tips` ops and restores the `:875` type reasoning | §15.4 E-TYPE, §15.1.2, AC-15.1 |
| **C5** | conceded | The ≥ 1,000-converted floor is replaced by **`n_findings_decided ≥ 223`**, per PLR site, with `guard_env_dependent`/`guard_operand_unknown` published separately and excluded; the `guard_predicate_unparsed` delta keeps no floor | AC-15.8, §15.10, §15.13 |
| **C6** | consequence 1 rebutted with a narrower clause; 2 and 3 conceded | **β-preserving rebinding** clause (a single length-preserving `ast.ListComp` over `x` itself) keeps β's population at **eight**, published as a measurement. The `:1185`/`:1188` "cleanest result" paragraph is **deleted**, and §15.9's `dispense` row corrected. The challenger's own suggested narrowing is recorded as dead (it saves none of the six) | §15.3, §15.1.3, §15.9, AC-15.2 |
| **C7** | (a) conceded; (b) literal conceded, collision rebutted | **E-CALL(5)**: a `Var` naming a parameter written below the guard resolves to ⊤. The P3a hook is restated over the receiver's **derived** `channel_kwarg`/`channel_default_param`, never the forbidden literal `"use_channels"`. No ordering collision exists: `channels_for_call` already resolves the kwarg first | §15.3 β, §15.4 E-CALL(5), AC-15.2 |
| **C8** | site-list horn rebutted; tautology conceded, and his remedy rejected | Tier (iii) is **derived** from `guard.is_dynamic_raise` (seven `raise <name>` sites at this pin), zero registry cost. His proposed derived (i)/(ii) tiering is rejected as **self-satisfying**; the GO gate is restated over **reasons**. `:117` retiered, `:2092` added to the `move_*` enumeration | §15.1 (new box), §15.1.3, §15.1.4, §15.9 |
| **C9** | contradiction conceded; his remedy rejected as unsound | Tier (iii) emits **one `Finding`, `UNKNOWN`, `guard_env_dependent`** plus an `excludes_sites` entry. Emitting `SAFE` would let `join` claim the backend did not raise — A-COMPLETES on the current operation. `guard_env_dependent`'s definition widened by one clause for unestablished reachability | §15.5, §15.7, AC-15.5(iv), AC-15.6 |
| **C10** | conceded, all four parts | `SoundnessScope` has exactly one field, `excludes_sites: tuple[PlrSite, ...]`; the `excludes`/`harness_internal` sentence is deleted; the type is stated as **new in this increment**; the two non-definitional citations are replaced by a motivation reference | §15.5 |
| **C11** | (a) fact conceded / sizing rebutted; (b) conceded; (c) conceded as disclosure | O1 restated as a **new element walk** (~40 LOC, not ~25 "over data the harness already computes"); **heterogeneous-parent singleton rule** with `element_type = None` fail-closed and a published count; the tier-(ii)-dependence of the GO is stated plainly in this document's own words | §15.4 O1, §15.9, AC-15.4 |
| **C12** | **REBUTTED on the merits, but the instrument was fixed anyway** | The 93/81 and 544/532 gaps were `(row_id, op_id)` set dedup under content-digest collisions, not unaccounted operations. Item 17 re-keyed the ledger positionally (`ca756bce`); every field now closes at 544/93, `consistency.ok` is `true`, and the 12 collisions are published and are all `move_*`. §15.0's note 2 wording corrected | §15.0 (notes 1–2 + new correction box) |
| **C13** | (1) conceded with a clause; (2) conceded outright; registry **HM-25, not HM-24** | The single-write requirement now ranges over **the iterand** as well as `x`. The delegate→caller substitution is forbidden (E-CALL(depth)) rather than assumed. §15.8's "neither row" position is withdrawn: **HM-25 8 → 9**, pending user approval | §15.3, §15.4 E-CALL(depth), §15.8, AC-15.7, §15.14 Q5 |
| **C14** | (a) rebutted (and exposes D1); (b) conceded | β is **not** dead: E-CALL step (2) had no data source at all, so resolution fell through to the β binding. **E-CALL(β)** models truthiness in four cases, with `Lit(None)` routed to β rather than to ⊤. `:522` survives C6 and C14 together, so the gate keeps a GO candidate | §15.4 E-CALL(β), §15.9, AC-15.2 |
| **C15** | conceded | **Nested-`Opaque` rule**: a predicate containing any `Opaque` node is `Opaque` for reason assignment, still Kleene-evaluated. Restores §15.7's legibility claim; `:409`'s 384 findings keep `guard_predicate_unparsed` | §15.2 G1, §15.7 |
| **C16** | conceded, textual | The contract-table regeneration moves `contracts_sha`, so the whole cache is **cold after T30 by design**; `env` is untouched, which is the property that matters. T30's gate adds a check that no test pins a literal key | §15.8, §15.12 T30 |
| **C17** | wording conceded; disposition unchanged | Q2's cost argument corrected — the draft priced the general case and charged the specific one for it. DEFER stands on soundness-risk grounds. The `:377-378` early-return fact is recorded as reinforcing E-UNCOND(5) | §15.6, §15.14 Q2 |
| **C18** | conceded, both defects | AC-15.12's producer citation corrected to `oracle_common.py:370-373`; §15.5's two non-definitional `SoundnessScope` citations dropped; §15.0's note-2 "distinct pairs" wording corrected | AC-15.12, §15.5, §15.0 |
| **D1** | adopted (defender-identified **blocker**) | E-CALL step (2)'s "recorded default" did not exist. T30 derives **`param_defaults`** from `ast.arguments.defaults`/`kw_defaults` restricted to `ast.Constant`, fail-closed (~30 LOC). Restores `transfer`'s `:1335`/`:1337`/`:1340` and gives E-CALL(β) case (3) a data source | §15.4 E-CALL(2), §15.1.3, §15.12 T30, AC-15.5 |
| **D2** | adopted (must-measure) | T30 block (2) publishes the count of executed `pick_up_tips` ops for which `channels_for_call` returns non-`None`, floor `== 223`. Without it a `:502` failure would be misattributed to O1 | §15.9(2), §15.12 T30/T32 |
| **D3** | adopted (minor) | **E-UNCOND(6)**: the `raise_guard`'s own condition sits at `scope_trail[0]` and is excluded from both scope tests, which range over `scope_trail[1:]` | §15.4 E-SCOPE, E-UNCOND(6), AC-15.5(i) |

**Items that landed outside this document.** Item 0 (routing the two user decisions) is the
orchestrator's. Item 17 (the ledger `row_id` fix and re-run) landed as `ca756bce`; its results are
folded into §15.0. Item 18's lint execution is T33's, and is the one AC in this document that no one in
round 1 could execute.

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
  `plr-sema/eval/unknown_ledger.py` at PLR pin `dd79c4c89` over the sidecar-gated tier-1 benchmark,
  **re-generated after band B0's positional-keying fix (`ca756bce`)** and now carrying `consistency`,
  `n_row_id_collisions` and `collision_ops`.
- Round-1 adversarial reports, dispositioned in §15.16:
  `.praxia/docs/audits/260904_plr-sema-predicate-round1-challenger.md` (C1–C18, six blockers, verdict
  `needs_revision`) and `.praxia/docs/audits/260904_plr-sema-predicate-round1-defender.md`
  (adjudications, D1–D3, the ordered remediation list, the user decisions, the revised gate
  prediction, verdict `needs_revision`).
- Exception taxonomy consulted for §15.5's fence argument and found to cover the wrong population:
  `training/verify/data/plr_exception_taxonomy.json` (132 PLR-defined classes at the same pin).
