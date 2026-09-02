---
title: "plr-sema increment 2 — SEMA-IR, a versioned linear bytecode as the analyzer's middle"
description: "Second post-corpus increment to the plr-sema pre-corpus specification, and a blocking prerequisite of increment 1 (#4888, tip typestate). Defines SEMA-IR: a versioned, linear, JSON-serializable bytecode with six opcodes (RESOURCE, CALL, LOOP, BRANCH/ELSE/END, WIDEN) and a four-form value grammar (literal, reference, sequence, top). Two lowerings target it -- one from ProtocolComputationGraph, one from the P2.5 corpus's tool-call form via the verifier's own bound kwargs -- so the static checker and training/verify's simulator consume the same bindings and the checker never sees a tool parameter name again. Replaces check/graph.py's derived-from-consumers mirror with a total, exhaustively-dispositioned lowering input (no upstream field silently dropped), makes check_graph a compatibility entry that lowers then calls the new check_ir core, and defines a canonical form plus content hash and the (bytecode hash, contracts sha, surface identity, ir_version) cache key that #4922 will store against. Zero new registry rows, zero new REASON_VOCABULARY members, zero wire-format change, no schema_version bump; one metric redefinition on HM-21, argued and costed. Names but does not specify the hooks for #4922 (cache), #4923 (incremental re-check) and #4924 (error-recovery interpreter)."
status: draft
spec_version: 10
amends: 260901_plr-sema-pre-corpus-spec.md
task_id: 260902_sema-oracle-tipstate
date: '260902'
confidence: medium
sources: "Read this session, in full or in the cited ranges: .praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md (§Open decisions 1-3, §0, §2.1-2.2, §3.1-3.3, §6.1-6.5, §7.3-7.4, §9.1-9.4, §Deferred, boundary summary); .praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md (all of §10, incl. §10.1.3, §10.5, §10.7's task row, §10.8, §10.10 Q3/Q7); .praxia/docs/plans/260902_plr-sema-oracle-harness.md; praxis/backend/utils/plr_static_analysis/models.py:504-661; praxis/backend/utils/plr_static_analysis/visitors/computation_graph_extractor.py:430-591; plr-sema/src/plr_sema/check/graph.py (whole file); plr-sema/src/plr_sema/check/__init__.py:120-358; plr-sema/src/plr_sema/_provenance/stamp.py (whole file); plr-sema/src/plr_sema/derive/__init__.py:124-192 and the symbol index of the whole module; plr-sema/eval/oracle_common.py (whole file); training/verify/dispatcher.py:1-198; training/verify/verifier.py:20-99; coxswain/src/coxswain/plr/param_namespace.py:78-187,270-273; scripts/survey_plr_preconditions.py:267-274; plr_sema/verdict.py symbol index; one row of training/assemble/out/corpus_p25.jsonl. PLR source at submodule pin dd79c4c89: external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py:438,501,535."
---

# Increment 2: SEMA-IR, the analyzer's middle

> **This document amends `260901_plr-sema-pre-corpus-spec.md` by reference.** It adds §11 to that
> document's numbering and edits exactly three things in it: §6.2's normative mirror table (the
> derived-from-consumers rule is **superseded** by a total disposition table, §11.1.3), §9.2's
> registry row **HM-21** (metric redefined, no new row), and the [§Deferred] boundary-summary row for
> §3.2's `join` (the attachment point is now an instruction stream, not a flat operation list).
> **It also amends `260902_plr-sema-tip-typestate-increment.md`** (spec_version 9, increment 1) in
> four places — §11.9 lists them. Everything else in spec_version 8 and 9 — `Verdict`, `Finding`,
> `PlrSite`, `AnalysisReport`, `join`, `REASON_VOCABULARY`, the telemetry schema, the fork-drift
> tests, the derivation closure mechanic, the budget and ratchet — is **unchanged**. No
> `schema_version` bump anywhere; no wire-format change; **zero new registry rows** (headroom is 0
> after the user's Q7 decision, §11.6).

---

## 11.0 What this increment is, in one paragraph

`plr-sema` is a compiler missing its middle. It has a front end (`praxis`'s libcst extractor →
`ProtocolComputationGraph`, `computation_graph_extractor.py:456-517,572-580`), it has a contract database
(`derive_contract`, `derive/__init__.py:446-492`, 4,770 entries), and it has a back end that walks
`graph.operations` and emits one `Finding` per guard (`_findings_for_operation`,
`check/__init__.py:293-321`). What it does not have is an intermediate representation: the checker
reads the front end's pydantic-shaped output directly, through a hand-chosen field mirror
(`check/graph.py:109-121`), and every other consumer of "a protocol" — the P2.5 corpus's tool-call
form, the verifier's executed call sequence, the oracle harness's ad-hoc adapter
(`adapt_graph`, `oracle_common.py:94-138`) — reaches the checker by a *different* path with
*different* conventions. That is the structural cause of increment 1's §10.10 Q3 defect: the corpus
path hands the checker tool parameter names (`at`, `volume_ul`) while the contract database is
written over PLR parameter names (`tip_spots`, `use_channels`), so the tier-1 oracle gate passes
vacuously. **This increment defines the missing middle: SEMA-IR, a versioned linear bytecode that
both paths lower into, that the checker is a pass over, and that is content-hashable so results can
be cached.** It adds no verdicts, no abstract domain and no precision. It is the substrate the tip
typestate walk (#4888), the content-addressed cache (#4922), incremental re-check (#4923) and the
error-recovery interpreter (#4924) all need, and it is specified now because three of those four
would otherwise each invent their own.

| axis | today (spec_version 8 + 9) | this increment |
|---|---|---|
| checker input | `ProtocolComputationGraph` mirror, 7 mirrored fields chosen by judgement | SEMA-IR bytecode; **all 34** upstream fields carry a declared disposition |
| corpus path | `adapt_graph`, tool-named `arguments` (`oracle_common.py:118-123`) | `lower_calls` over `PlanResult.kwargs` — PLR-named by construction |
| argument arity | `ast.literal_eval` of a source string (increment 1 §10.1.3 rules 1/3) | `len(Seq)` on an IR value — static even when the elements are not |
| checker core | `check_graph(graph_json, contracts_json)` | `check_ir(bytecode, contracts)`; `check_graph` lowers, then calls it |
| identity of a protocol | none | canonical form + `sha256`; cache key defined (store deferred to #4922) |
| registry rows | 24 live, cap 24, headroom 0 | **24 live, cap 24, headroom 0** — unchanged |
| `REASON_VOCABULARY` | 8 of cap 12 | **8 of cap 12** — unchanged |

**Deliverable of this increment, stated as the property that must become true:** for every executable
row of `training/assemble/out/corpus_p25.jsonl`, the bytecode the checker sees carries the same
bindings the simulator executed — `plan.method(**plan.kwargs)` (`verifier.py:47-55`) and
`lower_calls(plan.kwargs)` read one dict, not two conventions — and **no tool parameter name appears
anywhere in the bytecode**, pinned by a test that derives the tool-name set from `params_of`
(`param_namespace.py:270-273`) rather than typing it.

---

## 11.1 The instruction set

### 11.1.1 Name, version, shape

The IR is **SEMA-IR**. Its serialized form is a JSON object:

```jsonc
{
  "ir_version": 1,
  "instructions": [ /* the linear stream; index = pc */ ],
  "sideband":     { /* everything not hashed: spans, names, origin map */ }
}
```

`ir_version` is a module constant `plr_sema.check.ir.IR_VERSION`. **Normative bump rule:** any change
to the opcode set, the value grammar, the canonicalisation rules (§11.3) or the disposition table
(§11.1.3) bumps `ir_version`. It is a cache-key component (§11.3.3) precisely so that a bump
invalidates every stored result rather than silently reusing one computed under different rules.

### 11.1.2 Values

Every operand that can carry program data is one of four forms. This grammar is the whole of it;
there is no fifth form and no escape hatch to a raw source string in the hashed stream.

```
Value ::= Lit(json)                      # a static literal: number, string, bool, null
        | Ref(slot: int, cell: str|null) # a resource, or a cell within one ("A1")
        | Seq(items: [Value])            # an ordered sequence of KNOWN LENGTH
        | Top                            # the analyzer cannot resolve this value
```

Canonical JSON encodings: `{"k":"lit","v":…}`, `{"k":"ref","slot":…,"cell":…}`,
`{"k":"seq","items":[…]}`, `{"k":"top"}`.

**`Seq` is the load-bearing form and the reason the grammar is four-wide rather than three.** A
sequence whose *elements* are unresolvable still has a resolvable *length*, and length is exactly
what increment 1's channel-arity rule needs (§10.1.3 rule 3, mirroring PLR's own
`use_channels = use_channels or self._default_use_channels or list(range(len(tip_spots)))` at
`liquid_handler.py:501`). Today that rule is specified as "`arguments[p]` `ast.literal_eval`s to a
list of length `n`" — which **fails on every realistic protocol**, because
`lh.pick_up_tips(tip_spots=[ts0, ts1])` gives `arguments["tip_spots"] == "[ts0, ts1]"`, a string
`ast.literal_eval` rejects outright. Under this grammar it lowers to `Seq([Ref, Ref])` — or, if the
names do not resolve to declared resources, `Seq([Top, Top])` — and **the arity is 2 in both cases**.
§11.9 records this as a normative amendment to increment 1.

### 11.1.3 The opcodes

Six opcodes. `pc` is the index into `instructions`.

| opcode | operands | meaning |
|---|---|---|
| `RESOURCE` | `slot: int`, `type: str`, `element_type: str\|null`, `is_container: bool`, `is_parameter: bool`, `parents: [str]`, `grid: [int,int]\|null` | declares resource slot `slot`. `grid` is `[items_x, items_y]` when both are non-null, else `null` (= ⊤, "grid unknown") |
| `CALL` | `receiver: int`, `receiver_type: str\|null`, `method: str`, `kwargs: {str: Value}` | one operation. Every `kwargs` value is a `Value` (§11.1.2), never a source string |
| `LOOP` | `trip: int\|null` | opens a loop region. `null` = ⊤. **v1 always emits `null`** — see below |
| `BRANCH` | `pred: null` | opens a two-armed region. **v1 always emits `null`** (= ⊤) — see below |
| `ELSE` | — | separates the arms of the innermost open `BRANCH` |
| `END` | — | closes the innermost open `LOOP` or `BRANCH` |
| `WIDEN` | `reason: str` | an explicit, hashed record that the lowering could not preserve something |

**Why `LOOP` and `BRANCH` carry an operand v1 never fills.** `LOOP null` and `LOOP 8` are different
programs and must hash differently; if the operand were added later, every result cached under the
operand-free encoding would be silently reused for a program the analyzer now knows more about. The
operand exists now so that deferred item (d) (trip counts from `RESOURCE.grid`, i.e. upstream
`items_x`/`items_y`, `models.py:583-589`) and deferred item (c) (a predicate over `pred`) are
*additive with an `ir_version` bump*, not a re-encoding. v1 fills neither, and §11.7's AC-11.11 pins
that it does not pretend to.

**Why every v1 condition lowers to ⊤.** There is no predicate language over protocol-level
expressions — that is main spec deferred item (c), and main spec §Open decisions 2 additionally
resolved that numeric atoms stay Kleene ½ "through v1 and the first post-corpus increment". A
`condition_expr` (`models.py:557-559`) is a raw source string; parsing it would require the binding
chain main spec §3.3 withdrew `argument_not_static` for not having. `BRANCH null` is therefore not a
placeholder for laziness, it is the honest encoding of "both arms are reachable as far as this
analyzer knows".

**Region semantics, so that `BRANCH` is not a licence to straight-line.** A `BRANCH null … ELSE …
END` region is *not* equivalent to its two arms concatenated: concatenation would apply both arms'
effects in sequence, which is unsound. The v1 rule (`check_ir`, §11.4) is: **on `BRANCH`, widen every
receiver mentioned anywhere in either arm, at region entry and again at region exit; visit both arms
normally in between.** Guards inside the arms are still evaluated, against a widened state, so they
yield `UNKNOWN` — which asserts nothing and therefore cannot be wrong. Increment 1's AC-10.6 (a
payload carrying a non-null `condition_expr` yields zero `SAFE`/`WILL_FAIL` findings for that
receiver) is satisfied *by this rule* rather than by a special case in the tip evaluator.

### 11.1.4 The invariant: nothing is dropped, and the disposition table proves it

> **Normative invariant (the no-drop invariant).** For every field of every upstream model, the
> lowering assigns exactly one **disposition**:
> **(I)** an instruction field, **(W)** a widen trigger, **(S)** sideband (carried, never hashed,
> never read by `check_ir`), or **(X)** excluded-with-a-written-reason. There is no fifth
> disposition and no unlisted field. Anything the extractor could not resolve lowers to an explicit
> symbolic instruction or value (`Top`, `LOOP null`, `BRANCH null`, `WIDEN`); nothing is silently
> discarded, and no unresolved thing is quietly treated as resolved.

This replaces §6.2's derived-from-consumers rule. That rule asked "which fields does a consumer need
today?" and answered by deleting the rest (`line_number`, `node_type`, `arguments` were deleted in
the round-4 M1/B4 pass; `check/graph.py:109-121` is the survivor). It was the right rule for a
checker that reads the graph directly and the wrong rule for a *lowering*, whose correctness claim is
precisely that it loses nothing it does not announce losing. The two rules also fail differently: a
missing field under derived-from-consumers is invisible until a consumer wants it; a missing field
under the no-drop invariant fails AC-11.1 mechanically, because the table must be exhaustive over
`Model.model_fields`.

**`OperationNode`** (`models.py:524-559`, 15 fields):

| field | d | lowering |
|---|---|---|
| `id` (`:531`) | S | `sideband.origin[pc] = id` — the relabel map §11.4.3 needs |
| `line_number` (`:532`) | S | `sideband.span[pc]`; never hashed (it is `0` for every operation of the shipped fixture, so hashing it would encode a known-wrong value) |
| `method_name` (`:533`) | I | `CALL.method` |
| `receiver_variable` (`:534`) | I | `CALL.receiver`, canonicalised to a slot id (§11.3.1) |
| `receiver_type` (`:535`) | I+W | `CALL.receiver_type`; `None` additionally emits `WIDEN receiver_type` before the `CALL` |
| `arguments` (`:536-538`) | I+W | `CALL.kwargs`, values by §11.1.2; an untrusted key additionally emits `WIDEN arguments` (§11.2.4) |
| `node_type` (`:539-541`) | S+W | sideband; recomputable (`DYNAMIC` ⟺ some kwarg is `Top` or `depends_on_params` is non-empty). Disagreement between the two views emits `WIDEN node_type` |
| `preconditions` (`:542`) | **X** | produced by upstream's hand-typed frozensets (`_determine_preconditions`, `computation_graph_extractor.py:537-570`, whose tips gate reads `TIPS_REQUIRED_METHODS` at `:547`). §6.2 already forbids consuming these: they are §8's comparison **target**, and lowering them would launder a hand-written contract through the IR |
| `creates_state` (`:543-545`) | **X** | same population, same reason (`TIPS_LOADING_METHODS`, `computation_graph_extractor.py:479-491`) |
| `depends_on_params` (`:546-548`) | W+S | non-empty ⇒ `WIDEN depends_on_params` before the `CALL`; the names go to sideband |
| `foreach_source` (`:551-553`) | I+S | opens `LOOP null`; the iterated expression itself is sideband |
| `foreach_body` (`:554`) | I | the `LOOP` region's extent: body op ids are resolved to the instruction range between `LOOP` and its `END` |
| `condition_expr` (`:557`) | I+S | opens `BRANCH null`; the expression is sideband, never parsed in v1 |
| `true_branch` (`:558`) | I | the first arm |
| `false_branch` (`:559`) | I | the `ELSE` arm |

**`ResourceNode`** (`models.py:562-589`, 9 fields): `variable_name` → the `RESOURCE` slot (I,
canonicalised away by §11.3.1); `declared_type`, `element_type`, `is_container`, `is_parameter`,
`parental_chain` → the like-named `RESOURCE` operands (I); `source_expression` (`:580-582`) →
sideband (S: it is source text, and the semantic content a call actually uses — which well —
reappears as `Ref.cell` in that call's kwargs); `items_x`/`items_y` (`:583-589`) → `RESOURCE.grid`
(I).

**`ProtocolComputationGraph`** (`models.py:613-634`, 10 fields): `protocol_fqn`, `protocol_name` →
sideband, **excluded from the hash** (S — see §11.3.2 for why identity of the *program* must not
include its name); `operations` → the `CALL`/region stream (I); `resources` → the `RESOURCE` stream
(I); `preconditions` (`:629-631`, a list of `StatePrecondition`, `models.py:592-610`) → **X**, at the
container level, for the same reason as `OperationNode.preconditions` (so `StatePrecondition`'s own
fields never need dispositions and it is not a fourth mirrored model); `execution_order` (`:632-634`)
→ emission order (I), with disagreement handled below; `machine_types`, `resource_types` → sideband,
recomputable from the stream (S); `has_loops`, `has_conditionals` (`:643-646`) → cross-checked
against the stream, disagreement emits `WIDEN has_loops` / `WIDEN has_conditionals` (W).

**The one rule behind all four cross-checks.** `execution_order` vs. `operations`, `node_type` vs.
its recomputation, `has_loops`/`has_conditionals` vs. the stream: in each case the payload carries
two views of one fact. Increment 1 §10.5 rule 1 already set the disposition for the first —
*"a disagreement between two views of the same fact is a reason to know less, never to pick one"* —
and this increment generalises it verbatim to all four. Concretely: emission order is
`execution_order` when it is non-empty and a permutation of the operation ids, else `operations`
order; when it is non-empty and *not* a permutation, the lowering emits `WIDEN execution_order` at
`pc = 0` and lowers in `operations` order.

### 11.1.5 The `WIDEN` vocabulary is derived, not typed

> **Normative:** `WIDEN.reason` is **the name of the upstream model field whose disposition forced
> the widening**, verbatim. It is not a new vocabulary, it is a projection of
> `OperationNode.model_fields ∪ ProtocolComputationGraph.model_fields`.

The v1 reason set is therefore exactly
`{receiver_type, arguments, node_type, depends_on_params, execution_order, has_loops,
has_conditionals}` — seven strings, none of them typed as a fact about PLR or about semantics, all
seven checkable by set-inclusion against the live pydantic models (AC-11.8). This is why this
increment needs **no** `REASON_VOCABULARY` member and **no** registry row for a widen vocabulary: had
the reasons been chosen (`"loop"`, `"dynamic"`, `"unknown_shape"`) they would have been a
hand-maintained closed set, and under §9.4's discovery-vs-growth rule that is *growth*, against zero
headroom.

`WIDEN.reason` is **not** a `Finding.reason` and must never be passed as one:
`REASON_VOCABULARY` (`verdict.py:127`) is closed and its forward scan
(`test_reason_vocabulary_closed_forward`) would reject a computed value at the `Finding(...)` call
site anyway. A widened instruction that later yields a finding uses the existing members —
`guard_predicate_unparsed`, or increment 1's `channel_state_unknown`.

---

## 11.2 Two lowerings, one target

### 11.2.1 `lower_graph` — from the extractor

```python
# plr_sema/check/ir.py  -- stdlib only, no libcst, no pylabrobot, no pydantic (§6.2 unchanged)
def lower_graph(payload: dict, *, param_names: Mapping[str, tuple[str, ...]] | None = None) -> Bytecode
```

Input is the same JSON payload `parse_graph` (`check/graph.py:164-178`) reads today — the raw
`model_dump(mode="json")` of a real `ProtocolComputationGraph`. `param_names` maps a contract key
(`f"{receiver_type}.{method_name}"`, §7.3) to that method's PLR parameter names, and is used only by
§11.2.4's trust rule; **`None` means "trust nothing"**, which is the fail-closed default that unit
tests and tier-4 fuzz get for free.

The argument values are lowered by `ast.parse`-ing each `arguments` value as an expression (stdlib
`ast`, permitted under `check/` — §6.2 bans `libcst` and `pylabrobot`, not `ast`, and
`derive/` already relies on that distinction):

- a literal (`ast.literal_eval` succeeds) → `Lit`
- an `ast.List`/`ast.Tuple` → `Seq` of its elements lowered recursively — **length known even when
  the elements are not**
- a `Name` naming a declared resource → `Ref(slot, None)`; a `Subscript` of such a name with a
  string index (`source["A1"]`) → `Ref(slot, "A1")`
- anything else, or an unparseable string → `Top`

### 11.2.2 `lower_calls` — from a corpus row or a verifier run

```python
def lower_calls(calls: Sequence[Mapping[str, Any]], *, resources: Mapping[str, dict],
                param_names: Mapping[str, tuple[str, ...]] | None = None) -> Bytecode
```

`calls` is a sequence of `{"method": <PLR method name>, "kwargs": {<PLR param>: <IR value JSON>}}`.
**It is not the corpus's tool-call form and never sees one.** The conversion happens one layer out,
in `plr-sema/eval/`, where importing `pylabrobot` and `training.verify` is permitted (oracle plan,
"Where it lives"), by a new function `ir_value_of(obj)` that maps a bound PLR object to a `Value`:
a `Resource` with a parent → `Ref(slot_of(parent), obj.name)`; a top-level `Resource` →
`Ref(slot_of(obj), None)`; a `list` → `Seq`; a JSON scalar → `Lit`; anything else → `Top`.

The kwargs come from `PlanResult.kwargs` (`dispatcher.py:54-64`), which `run_runtime` already
harvests through its `recording_plan_call` wrapper (`oracle_common.py:59-65`) and carries out on
`RuntimeOutcome.plr_kwargs` (`oracle_common.py:43-50`). **Those kwargs are PLR-named by
construction**: `plan_call` (`dispatcher.py:92-101`) writes `kwargs[spec.plr_arg]` inside its `bind`
closure (`dispatcher.py:117-135`), and `spec.plr_arg` is `ParamSpec`'s "vendored kwarg name" field
(`param_namespace.py:81-99`, `:88`). For `pick_up_tips` the single row is
`_sym("at", "tip_spots", …)` (`param_namespace.py:168-171`) and `plan_call`'s `bind("at")`
(`dispatcher.py:159-161`) therefore produces `kwargs == {"tip_spots": [TipSpot, …]}` — which lowers
to `Seq` of length *n*, which is exactly increment 1 §10.1.3 rule 3's input. **This is the concrete
mechanism by which AC-10.11 stops being vacuous** (§11.10).

**One correction to the existing harvest, and it is not cosmetic.** `recording_plan_call` currently
stores `{k: repr(v) for k, v in plan_result.kwargs.items()}` (`oracle_common.py:59-65`). A `repr` of
a list of `TipSpot`s is a string like `"[<TipSpot ...>, <TipSpot ...>]"`, which `ast.literal_eval`
rejects and which carries no recoverable arity without re-parsing angle-bracket reprs. `ir_value_of`
replaces the `repr` at the point of harvest; the `repr` string, if wanted for debugging, goes to
sideband.

### 11.2.3 The tool-name barrier, and the exact test that pins it

> **Normative: no tool parameter name may appear as a `CALL.kwargs` key in any bytecode reaching
> `check_ir`.**

The pinning test derives the forbidden set rather than typing it (`test_no_tool_names_in_ir`):

```
forbidden = { s.name for t in PARAM_NAMESPACE for s in params_of(t) if s.plr_arg != s.name }
```

— i.e. every schema-side name that differs from its vendored kwarg (`params_of`,
`param_namespace.py:270-273`). At the current table that is `{at, destination, source, volume_ul,
what}` for the rows where `plr_arg` differs, computed live. The assertion is that
`forbidden ∩ set(kwargs)` is empty for every `CALL` of every lowered corpus row. It is stated as an
intersection with a *derived* set rather than a hardcoded list precisely so that a future
`PARAM_NAMESPACE` row is covered without an edit here.

Two honest caveats, stated rather than hidden. (i) `source` and `destination` are *also* PLR
parameter names for some methods — `transfer`'s three `_sym`/`_lit` rows
(`param_namespace.py:155-161`) map `source → source` and `destination → targets` — so the intersection is scoped per method: a key is forbidden only if
it is a schema-side alias **for the method being lowered**. (ii) The test proves the corpus path is
clean; it cannot prove the *graph* path is, because a protocol's author may legitimately write any
keyword. §11.2.4 is what covers that side.

### 11.2.4 The parameter-name trust rule — the structural close of increment 1's Q3

The graph path has a defect the corpus path does not, and it is upstream:
`_extract_arguments` (`computation_graph_extractor.py:519-535`) names *positional* arguments from a
hand-typed `common_arg_names = ["resource", "volume", "source", "destination", "tips"]`
(`:524`), falling back to `f"arg{i}"`. So `lh.aspirate(plate["A1"], 100)` yields
`arguments == {"resource": ..., "volume": ...}` while PLR's actual parameters are `resources` and
`vols`. A checker that reads `arguments` by PLR parameter name would treat a guessed name as a real
binding.

**Normative trust rule.** A `CALL` kwarg key is *trusted* iff `param_names[contract_key]` is
available and the key is a member of it. An untrusted key keeps its **value** (nothing is dropped)
under a rewritten key `"?{i}"` (positional in `arguments` iteration order) and the `CALL` additionally
emits `WIDEN arguments`. Consumers — including increment 1's channel-set rules — read trusted keys
only.

`param_names` is **DERIVED, and the derivation already exists**: `SurveyRecord.params`
(`derive/__init__.py:138-160`, field at `:147`, populated by `_record_from_dict` at `:174-186`) is
the survey's own record of each function's parameter names, produced by `_function_params`
(`survey_plr_preconditions.py:267-274`). This increment adds one additive key per contract entry:

```jsonc
"contracts": { "LiquidHandler.aspirate": { "gaps": [], "guards": [ /* unchanged */ ],
                                           "params": ["self","resources","vols","use_channels", "…"] } }
```

`schema_version` stays **1**: `check/` reads it through `.get()` with an empty default, so a
pre-increment table degrades to "trust nothing" — maximal widening, today's all-`UNKNOWN` behaviour —
rather than raising (the same fail-closed direction as increment 1's AC-10.7). **Payload cost is an
estimate, not a measurement:** ~6 names × ~12 bytes × 4,770 entries ≈ 0.3 MB pretty-printed against
the current 4.4 MB (§7.3's measured figures). The fixer publishes the measured number; if it exceeds
10% the fixer says so rather than shipping quietly.

**What this rule deliberately does not do.** It does not *recover* the correct name for a positional
argument. Doing so needs the positional/keyword-only boundary, and `_function_params`
(`survey_plr_preconditions.py:267-274`) concatenates `posonlyargs + args + kwonlyargs + vararg +
kwarg` into one flat list without recording where the positionally-bindable prefix ends — so
`params[i+1]` is right for most PLR methods and silently wrong for any method with keyword-only
parameters. Recovering it is a named follow-up with a concrete trigger (the survey emitting
`n_positional`), not a guess made here. Membership is safe without the boundary; indexing is not.

---

## 11.3 Canonical form, content hash, cache key

### 11.3.1 What is normalised

1. **Identifiers → positional slot ids.** Resource and receiver *names* are replaced by integer slots
   assigned in order of first appearance in the emission order. `variable_name`, `receiver_variable`
   and every `Ref.slot` are affected. A receiver with no `ResourceNode` still gets a slot, flagged
   `grounded: false` (the fact `is_grounded`, `check/graph.py:181-186`, already computes).
2. **`Ref.cell` is kept verbatim.** `"A1"` is a position on a labware, not a program identifier;
   renaming it is a semantic change.
3. **Kwarg key order.** `CALL.kwargs` is emitted with keys sorted lexicographically. Trusted and
   untrusted keys sort together; the `"?"` prefix of an untrusted key is part of the key.
4. **Literal formatting.** Numbers use Python's shortest round-trip `repr` (`100` and `100.0` are
   *different* literals and must stay so — PLR's volume arithmetic distinguishes them); strings are
   JSON-escaped with `ensure_ascii=False`; `true`/`false`/`null` are JSON spellings.
5. **`RESOURCE` emission order** follows slot assignment, so it is a function of use order, not of
   the payload's `resources` dict order.
6. **Serialization** is one canonical JSON object per instruction,
   `json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`, joined by `"\n"`.
   `pc` is not written — it is the line index.

### 11.3.2 What is excluded, and the hash

Excluded from the hashed bytes: everything under `sideband` — line numbers (`line_number`, `:532`),
variable and resource *names*, `source_expression`, `foreach_source`'s expression text,
`condition_expr`'s text, `node_type`, `machine_types`, `resource_types`, the `origin` map, and
**`protocol_fqn`/`protocol_name`**.

```python
IR_HASH_PREFIX = f"sema-ir/{IR_VERSION}\n"
bytecode_hash = sha256((IR_HASH_PREFIX + canonical_text).encode("utf-8")).hexdigest()
```

`sha256` is chosen for one reason worth stating: the provenance layer this increment plugs into
already speaks it — `GitState.dirty_content_id` is 40-hex from `git write-tree` or **64-hex sha256**
from the fallback (§2.1), and mixing a third digest into a cache key whose other components are
sha1/sha256 buys nothing.

**Excluding `protocol_fqn` is a deliberate, attackable choice.** Two protocols with identical bodies
and different names hash identically, which is what makes the hash a *program* identity and the cache
useful across renames. Its consequence is that a cached artifact must not be an `AnalysisReport`,
whose `protocol_fqn` field (`verdict.py:193-212`) would then be wrong for the second protocol.
**Design position:** #4922 caches the `Finding` tuple, and the caller reassembles the report with its
own `protocol_fqn` and its own `stamp`. This is recorded as open question Q3 (§11.11) because it
constrains #4922's interface, and a reviewer may prefer the opposite trade.

### 11.3.3 The cache key

```
cache_key = (bytecode_hash, contracts_sha, surface_identity, ir_version)
```

| component | where it already exists |
|---|---|
| `bytecode_hash` | defined here (§11.3.2) |
| `contracts_sha` | `sha256` of the `contracts_json` **string `check_graph` is already handed** (`check/__init__.py:350-358`) — no artifact change, no new field, computable in-band today |
| `surface_identity` | `(stamp.surface, stamp.surface_pin or stamp.plr.hash, stamp.plr.dirty_content_id)` — all four already on `SurveyStamp` (`_provenance/stamp.py:77-103`, `surface`/`surface_pin` at `:96-103`) and already reconstructed by `_stamp_from_dict` (`check/__init__.py:140-154`). `Surface.pin` exists precisely because a non-git extraction cannot answer "what commit is this" (`stamp.py:51-67`), which is why the key falls back to `plr.hash` rather than requiring one form |
| `ir_version` | `plr_sema.check.ir.IR_VERSION` (§11.1.1) |

`contracts_sha` and `surface_identity` are both present because they answer different questions: the
first is "were the contracts these exact bytes?", the second is "which PLR tree were they derived
against?" — a regenerated-but-identical table keeps the first stable, and a re-derived table against
a moved pin changes the second even when the guard set happens to coincide.

**This increment defines the key and stores nothing.** No cache, no eviction, no store interface —
that is #4922 (§11.5).

---

## 11.4 The checker as a pass over the IR

### 11.4.1 The seam

```python
def check_ir(bytecode: Bytecode, contracts: dict) -> tuple[Finding, ...]     # the new core
def check_graph(graph_json: str, contracts_json: str) -> AnalysisReport      # unchanged signature
```

`check_graph` keeps its signature, its docstring's promises (no `libcst`, no `pylabrobot`, never
shells out) and its telemetry emission (`_check`, `check/__init__.py:324-347`). Its body becomes:
`json.loads` both inputs → build `param_names` from the contract table → `lower_graph` →
`check_ir` → relabel (§11.4.3) → `join` (`verdict.py:220-232`) → `AnalysisReport`. **Every existing
acceptance criterion that names `check_graph` continues to name `check_graph`**; AC-6.1 through
AC-6.7 are untouched, and AC-11.6 pins that the shipped fixture's report does not move.

`check_ir` is a single left-to-right pass with a program counter. In *this* increment its per-`CALL`
body is exactly today's `_findings_for_operation` (`check/__init__.py:293-321`), re-keyed from an
`OperationNode` to a `CALL` instruction: `op.receiver_type`/`op.method_name` become
`CALL.receiver_type`/`CALL.method`; the loop test `op.foreach_source is not None or op.foreach_body`
becomes "this `pc` is inside an open `LOOP` region". No verdict changes. Increment 1's tip walk is
then a *second* pass, or a state fold threaded through this one — that is #4888's step 2, and this
increment's job is only to make it a pass over instructions rather than over pydantic-shaped
operations.

### 11.4.2 What §6.2's mirror becomes

**Reduced, not retired: `check/graph.py` becomes the lowering's input schema, and becomes total.**
It keeps its role (JSON in, stdlib dataclasses out, never a pydantic `model_validate`) and loses its
selection rule. Concretely: `OperationNode` (`check/graph.py:109-121`) grows from 7 fields to all 15;
`ResourceNode` (`:124-132`) from 1 to 9; `ProtocolComputationGraph` (`:135-145`) from 3 to 10;
`_operation_from_dict` (`:148-157`) and `parse_graph` (`:164-178`) extract all of them. `is_grounded`
(`:181-186`) survives unchanged and finally acquires a consumer: the `grounded` flag on a `RESOURCE`
slot (§11.3.1).

The module's own long "derived-from-consumers is normative, do not add to it" docstring is replaced
by the disposition table, and Fork C's drift test (§5.3,
`tests/test_check_graph_mirror_drift.py`) is **strengthened from a subset check to an exhaustiveness
check**: `set(DISPOSITIONS[Model]) == set(Model.model_fields)` for all three models, in both
directions. A field added upstream turns it red (today it would pass silently); a disposition for a
field that no longer exists turns it red too.

### 11.4.3 `operation_id`, and an honest conflict

`check_ir` labels each `Finding` with `operation_id = str(pc)` — the instruction index — because that
is the only identity the IR has, and because #4923's memo points and #4924's interpreter both key on
`pc`. But main spec **AC-6.4** requires
`{f.operation_id for f in report.findings} == {op.id for op in graph.operations}` — graph ids, not
instruction indices.

**Resolution: `check_graph` relabels through `sideband.origin` before constructing the report.** The
relabel is total in v1 because the graph lowering emits exactly one `CALL` per `OperationNode`, so
`origin` is a bijection between `CALL` pcs and operation ids. AC-11.7 asserts the bijection rather
than assuming it, and §11.11's Q1 records what happens the day it stops being one (a method that
lowers to more than one `CALL` would make two findings share an `operation_id`, which main spec
§Open decisions 3 has already ruled must *conjoin*, not merge — so the behaviour is defined, but the
`origin` map would need to become one-to-many and AC-6.4's equality would need re-reading).

### 11.4.4 Totality, restated over instructions

Main spec **AC-7.2**'s totality guarantee (`len(findings) >= len(operations)`, strengthened to
surjectivity by AC-6.4) becomes, at the IR level: **every `CALL` instruction receives ≥1 `Finding`.**
`RESOURCE`, `LOOP`, `BRANCH`, `ELSE`, `END` and `WIDEN` instructions receive none — they are not
obligations, they are context. `_findings_for_operation`'s zero-guards/zero-gaps/no-loop fallback
(`check/__init__.py:311-320`, the round-4 B1 fix, which appends `_no_contract_derived`) is what makes
this true and is carried over unchanged. AC-11.7 pins both halves.

---

## 11.5 Hooks for later increments — named, not specified

Each is one named seam and one sentence on why the instruction set does not preclude it. **None of
the three is specified here, and a fixer who implements one of them from this section has
overstepped.**

- **#4923, incremental re-check — the per-instruction memo point.** `check_ir` accepts an optional
  `observer(pc, state_digest)` callback, and the canonical form gives a well-defined *prefix hash*
  `H(0..pc)` for every `pc`. Not precluded because the stream is linear and the state after `pc` is a
  function of the prefix alone: two programs sharing a prefix share every memo point in it, which is
  the whole content of "re-check only what changed".
- **#4922, the content-addressed cache — the store interface.** `CacheStore.get(key) -> tuple[Finding,
  ...] | None` / `.put(key, findings)`, with `key` as §11.3.3 and the report reassembled by the
  caller (§11.3.2). Not precluded because the key's four components are already computable at
  `check_graph`'s boundary today, with no artifact change and no new provenance field.
- **#4924, the error-recovery interpreter — the `(pc, concrete state, abstract state)` triple.** `pc`
  is the join: `lower_calls` assigns `CALL` pcs in the same order `_execute` awaits them
  (`verifier.py:47-55`, whose `for i, call in enumerate(call_sequence)` index *is* that pc), so a
  concrete state captured mid-run and an abstract state computed by `check_ir` are indexed by the
  same integer. Not precluded because `WIDEN` and `Top` make the abstract side's ignorance explicit
  at a `pc` rather than diffuse, which is what an interpreter needs in order to know where re-entry
  is meaningful.

---

## 11.6 Hand-maintained impact

**New registry rows: zero.** Headroom is 0 after the user's Q7 decision (option B: increment 1 takes
HM-24 *and* HM-25, 24 live rows against a cap of 24), so a new row would force a cap conversation,
and this increment does not need one. Every fact it relies on is derived:

| what could have been typed | what it is instead |
|---|---|
| a tool→PLR parameter name map | `PlanResult.kwargs` at runtime — written by `plan_call`'s `bind` from `spec.plr_arg` (`dispatcher.py:117-135`). `PARAM_NAMESPACE` is hand-maintained, but it is **coxswain's** table, consumed across the boundary and never copied into `plr_sema` — the same relationship HM-9 records for `SUPPORTED_TOOLS`. A copy would need a row; there is no copy |
| a per-method PLR parameter list | `SurveyRecord.params` (`derive/__init__.py:147`), already surveyed by `_function_params` (`survey_plr_preconditions.py:267-274`), shipped as an additive `params` key (§11.2.4) |
| a `WIDEN` reason vocabulary | upstream field names, checked by set-inclusion against `model_fields` (§11.1.5, AC-11.8) |
| an opcode↔field mapping table | it *is* the disposition table, and the disposition table is checked exhaustive against `model_fields` (AC-11.1) rather than maintained against a memory of what upstream looks like |

**`REASON_VOCABULARY` (HM-14): unchanged at 8 of cap 12.** The argument for adding a member would be
"the lowering failed" — but by the no-drop invariant the lowering does not fail: an unresolvable
thing becomes `Top`/`WIDEN`, and the finding that eventually reports it uses
`guard_predicate_unparsed` (parse stage) or `channel_state_unknown` (evaluation stage), whose
division of labour increment 1 §10.8 already argued. The one genuine failure mode — a *structurally
invalid* payload, e.g. missing `protocol_fqn`, which `parse_graph` raises on today
(`check/graph.py:164-178`) — keeps today's exception behaviour. That behaviour is arguably wrong
(tier 4 / #4882 wants `check_graph` never to raise), but it is wrong *today*, this increment does not
make it worse, and fixing it is #4882's call, not a reason to spend a vocabulary slot here.

**HM-21: one metric redefinition, no new row, and both numbers must appear in the diff.** HM-21 is
*"field set mirrored by `check/graph.py`"*, metric "fields mirrored", `declared` 15 after increment
1's fix to `_measure_hm21` (`_hand_maintained.py:212-215`, which increment 1 §10.8 extends to count
`ProtocolComputationGraph` too). Under this increment the mirror becomes total: **34 fields**
(15 + 9 + 10). Two options, and the recommendation is stated rather than assumed:

- **Raise `declared` 15 → 36** (live 34 + 2 headroom, §9.1's D16c rule). Honest about the size, but it
  ratchets a number that is no longer a judgement — the mirror is now *required* to equal
  `model_fields`, so its count is a fact about upstream, and a "ceiling" on a derived count is
  meaningless.
- **Redefine the metric to the count of `X` (excluded-with-reason) dispositions**, which is the only
  remaining judgement: **3** (`OperationNode.preconditions`, `OperationNode.creates_state`,
  `ProtocolComputationGraph.preconditions`), status `CAPPED (5)`. HM-21's `why_not_derived` is
  rewritten to name what is actually hand-maintained now: *"which upstream fields the analyzer
  refuses to consume, and why"*.

**Recommended: the second**, with three conditions that keep it from being a downward-gaming metric
change: (i) the commit message states both numbers explicitly — *"under the pre-increment metric this
row reads 34; the metric changed because the judgement it measured no longer exists"* — the same
separation increment 1 §10.8 required for its +3/+2 split; (ii) the exhaustiveness test (AC-11.1) lands
in the same commit, because it is what replaces the count as the protection against invisible growth;
(iii) `_measure_hm21` is rewritten to count dispositions, not dataclass fields, so the measure and the
metric agree. Without all three this is exactly the "split a surface to dilute it" move §9.4's
anti-gaming clause names, and a reviewer should reject it.

---

## 11.7 Acceptance criteria

Written so that none can be satisfied while the property is false. Where a criterion could be passed
by a stub, the stub-defeating half is named.

- **AC-11.1 (the disposition table is exhaustive, both directions).** For each of
  `OperationNode`, `ResourceNode`, `ProtocolComputationGraph`,
  `set(DISPOSITIONS[M]) == set(M.model_fields)`. The test imports the real pydantic models (allowed:
  it lives in `tests/`, like Fork C's existing drift test) and asserts equality, not inclusion —
  so both a new upstream field and a stale disposition turn it red. A hardcoded field list in the
  test would defeat it, so the test reads `model_fields`, and a second assertion pins that the three
  measured counts are `(15, 9, 10)` at the current model, which is the number that must be re-read —
  not re-guessed — when it changes.
- **AC-11.2 (no-drop, field by field).** A fixture graph in which **every** `OperationNode`,
  `ResourceNode` and `ProtocolComputationGraph` field carries a non-default value lowers to a
  bytecode from which each `I`-dispositioned field's value is recoverable, each `S`-dispositioned
  field appears in `sideband`, each `W`-dispositioned field produced its `WIDEN`, and each of the
  three `X` fields appears in **neither** the instruction stream nor `sideband` (the exclusion is
  asserted, not assumed). A lowering that dumps the payload wholesale into sideband fails the `X`
  half; one that drops fields fails the `I`/`S` halves.
- **AC-11.3 (hash invariance under equivalence).** Four transformations of one fixture leave
  `bytecode_hash` **identical**: (a) rename every resource and receiver variable; (b) permute the
  `resources` dict's key order; (c) change every `line_number`; (d) change `protocol_fqn` and
  `protocol_name`. All four in combination also leave it identical.
- **AC-11.4 (hash sensitivity under semantic change).** Seven mutations of the same fixture each
  produce a **distinct** hash, and the seven are pairwise distinct: (a) swap two adjacent `CALL`s;
  (b) `100` → `101` in a kwarg; (c) `100` → `100.0`; (d) change a `Ref.cell` from `"A1"` to `"B1"`;
  (e) delete one kwarg; (f) change a `method`; (g) replace a `Seq` of length 2 with one of length 3.
  AC-11.3 and AC-11.4 are unsatisfiable together by any constant-hash stub and by any
  hash-the-whole-payload stub.
- **AC-11.5 (the checker never sees a tool name).** Over every executable row of
  `corpus_p25.jsonl` plus the 88 golden pairs, no `CALL.kwargs` key is a method-scoped schema-side
  alias, where the alias set is computed live from `params_of` (`param_namespace.py:270-273`) and not
  written in the test. Additionally: for at least one row, the lowered `pick_up_tips` `CALL` carries
  a `tip_spots` kwarg whose value is a `Seq` — an assertion no name-blind lowering can pass, and the
  one that makes this criterion directional rather than merely negative.
- **AC-11.6 (`check_graph` does not move).** Against
  `plr-sema/tests/fixtures/simple_transfer_graph.json` and the shipped `derived_contracts.json`, the
  report is equal to the pre-increment report after JSON round-trip: same `verdict`, same finding
  count per operation, same multiset of `(operation_id, reason, plr_site)` triples. AC-6.3 and AC-6.4
  are re-run unmodified.
- **AC-11.7 (totality over instructions, and the relabel bijection).** For the fixture and for every
  corpus row: every `CALL` pc receives ≥1 `Finding` from `check_ir`; no non-`CALL` pc receives any;
  `sideband.origin` restricted to `CALL` pcs is a bijection onto `{op.id}`; and after relabelling,
  `{f.operation_id} == {op.id for op in graph.operations}` (AC-6.4, re-asserted through the new path).
- **AC-11.8 (the widen vocabulary is derived).** `{i.reason for i in bytecode if i.op == "WIDEN"}`
  over the fixture corpus is a subset of
  `set(OperationNode.model_fields) | set(ProtocolComputationGraph.model_fields)`, and an AST literal
  scan of `plr_sema/check/ir.py` — the mechanism increment 1's AC-10.9 established, not a grep —
  finds no `ast.Constant` string equal to a widen reason outside the single dict that maps a field to
  its disposition.
- **AC-11.9 (the cache key is constructible today, and every component is load-bearing).**
  `cache_key(graph_json, contracts_json)` returns a 4-tuple with no new artifact field and no
  provenance recomputation (`check/` still never shells out). Four sub-assertions, one per component:
  changing the graph's semantics changes component 1 and nothing else; changing one byte of
  `contracts_json` changes component 2 and nothing else; changing `stamp.surface_pin` changes
  component 3 and nothing else; bumping `IR_VERSION` changes component 4 **and** every
  `bytecode_hash`, which is the point of the prefix in §11.3.2.
- **AC-11.10 (the trust rule fires in both directions).** With `param_names` supplied from a contract
  table carrying `params`: a `CALL` whose `arguments` key is a real PLR parameter of that method is
  trusted and emits **no** `WIDEN arguments`; a `CALL` carrying the extractor's guessed positional
  name (`{"resource": ..., "volume": ...}` for `LiquidHandler.aspirate`, the shape
  `_extract_arguments` produces at `computation_graph_extractor.py:519-535`) is untrusted, keeps both
  values under `"?0"`/`"?1"`, and emits `WIDEN arguments`. With `param_names=None`, **every** key is
  untrusted. The `None` case is what makes this fail-closed rather than fail-quiet.
- **AC-11.11 (v1 lowers every condition and every trip count to ⊤, and says so).** For every lowered
  fixture and corpus row, every `LOOP` has `trip is None` and every `BRANCH` has `pred is None`. A
  payload carrying a non-null `condition_expr` lowers to a well-formed `BRANCH … ELSE … END` region
  (both arms present, `END` balanced) and yields zero `SAFE`/`WILL_FAIL` findings for every receiver
  mentioned in either arm — which is increment 1's AC-10.6, now discharged by §11.1.3's region rule
  rather than by a special case.
- **AC-11.12 (stale contract table degrades, does not crash).** `check_graph` against a contract
  table with no `params` key on any entry returns a report identical to AC-11.6's, never raises, and
  the resulting bytecode carries `WIDEN arguments` on every `CALL` that has any kwarg.
- **AC-11.13 (region well-formedness is total).** Over the fixture corpus and over 10,000 `hypothesis`-
  generated payloads (tier 4's harness, #4882, reused not rebuilt), every produced bytecode has
  balanced `LOOP`/`BRANCH`/`END` nesting with `ELSE` only inside an open `BRANCH`, and `check_ir`
  never raises on it. This is the criterion a lowering that silently straight-lines a malformed
  region cannot pass.

---

## 11.8 Task row, and what `#4888` must do first

`#4888` (increment 1, tip typestate) is **BLOCKED on this increment** and absorbs it as its step 0.
The order matters: increment 1's §10.1.3 channel-set derivation, its §10.5 walk and its §10.8
`arguments`/`execution_order` re-mirroring are all restated by this increment, so building them first
means building them twice.

| task | scope | files | gate | ~LOC | depends on |
|---|---|---|---|---|---|
| **#4921** (`#4888` step 0) | SEMA-IR: (1) `plr_sema/check/ir.py` — `IR_VERSION`, the value grammar, the six opcodes, `DISPOSITIONS`, `lower_graph`, `lower_calls`, canonical form, `bytecode_hash`, `cache_key`; (2) `check/graph.py` made total (all 34 fields) and its docstring rewritten from derived-from-consumers to the disposition table; (3) `check_ir` extracted from `_findings_for_operation`, `check_graph` rewired to lower-then-check with the `origin` relabel; (4) `derive/` emits the additive `params` key per contract entry from `SurveyRecord.params`, artifact regenerated, measured size published; (5) `eval/` gains `ir_value_of` and `run_runtime` harvests IR values instead of `repr`s; `adapt_graph` deleted; (6) Fork C's drift test strengthened to exhaustiveness; (7) HM-21 metric redefinition + `_measure_hm21` rewritten to count dispositions, both numbers in the commit message | create `plr-sema/src/plr_sema/check/ir.py`, `plr-sema/tests/test_ir.py`, `plr-sema/tests/fixtures/all_fields_graph.json`, `plr-sema/tests/fixtures/branchy_graph.json`; modify `plr-sema/src/plr_sema/check/{graph,__init__}.py`, `plr-sema/src/plr_sema/derive/__init__.py`, `plr-sema/src/plr_sema/_hand_maintained.py`, `plr-sema/eval/oracle_common.py`, `plr-sema/tests/test_{check_graph,check_graph_mirror_drift,derive,hand_maintained_ratchet}.py`, `plr-sema/data/derived_contracts.json` (regenerated) | `uv run pytest plr-sema/tests -q` satisfying AC-11.1 through AC-11.4 and AC-11.6 through AC-11.13; then `uv run python -m plr_sema.derive --survey-json training/verify/data/plr_preconditions.json --taxonomy-json training/verify/data/plr_exception_taxonomy.json --out plr-sema/data/derived_contracts.json`; then **AC-11.5** over the 812 + 88 corpus rows via `#4879`'s replay | ~600 | main spec T1–T14 (shipped) |

**Then, and only then, `#4888` steps 1–8** as increment 1 §10.7's task row specifies, with three of
its sub-steps changed by this increment (§11.9). Its own ~750 LOC estimate is unchanged; step (2)
("`check/graph.py` mirror gains `arguments` and `execution_order`") is **absorbed here and deleted
there**.

**Splitting.** Sub-steps (1)+(2)+(3) leave the tree green on their own (the IR exists, `check_graph`
routes through it, no verdict moves — AC-11.6 is the proof) and are the minimum shippable split
point. Do not split between (4) and (5): a `params` key with no consumer, or an `ir_value_of` with no
table to validate against, is untested code on both sides of the seam.

---

## 11.9 What this changes in increment 1 (`260902_plr-sema-tip-typestate-increment.md`)

Four normative amendments, listed so a reader of increment 1 is not misled by text this document
supersedes. None of them changes increment 1's *design* — the lattice, the bridge, the depth-0 effect
rule, the E1–E5 transfer functions and every soundness argument stand exactly as written.

1. **§10.1.3 rules 1 and 3 — "`ast.literal_eval`s to a list" is replaced by "lowers to a `Seq`".**
   Rule 1: `use_channels` is exact iff its `CALL.kwargs` value is a `Seq` of `Lit` integers. Rule 3:
   the arity default reads `len(Seq)` for the method's channel-default parameter, **including when
   the elements are `Ref` or `Top`**. This strictly widens what resolves exactly, and it is the fix
   for the case increment 1 could not handle at all (`tip_spots=[ts0, ts1]`, §11.1.2).
2. **§10.5's walk is a pass over instructions.** Rule 1 (execution order) moves into the lowering
   (§11.1.4's cross-check rule, `WIDEN execution_order`); rules 2 and 3 (loops widen, dynamic
   arguments widen) become "the receiver is widened on entry to a `LOOP` region" and "on a `WIDEN
   depends_on_params`". The fixpoint-free, left-to-right shape and the soundness argument for it
   (widening can only destroy a verdict) are unchanged.
3. **§10.8's mirror-field rows are superseded.** `arguments` and `execution_order` are no longer two
   new rows in a derived-from-consumers table; they are two of 34 dispositions. HM-21's arithmetic in
   §10.8 (`declared: 10 → 15`, live 8 → 13) is superseded by §11.6's metric redefinition, and the
   fixer must not land both.
4. **AC-10.11's disclosed vacuity becomes closable, and AC-10.12 stays the directional gate.**
   `n_exact_channel_sets` is still reported; §11.10 explains why it is now expected to be non-zero.
   AC-10.12's mutant gate is unchanged and is still `#4888`'s own gate — a non-vacuous AC-10.11 does
   not retire it, because criterion (iii) (the family fires at least once in the right direction) is
   still the only criterion a never-firing evaluator cannot pass.

---

## 11.10 Effect on the oracle plan (`260902_plr-sema-oracle-harness.md`)

**Tier 1 and tier 2 both become "lower, then compare".**

- **Tier 1** (`#4879`) stops adapting and starts lowering: `adapt_graph` (`oracle_common.py:94-138`)
  is deleted, and the replay runs `lower_calls` over the IR values harvested from
  `PlanResult.kwargs`. The fallback branch that built `arguments` from `{k: json.dumps(v) for k, v in
  (call.get("params") or {}).items()}` (`oracle_common.py:118-123`) — the tool-named path — has no
  successor: a row whose call was never planned produces no `CALL` at all rather than a
  tool-named one, and is counted as `not_planned` in the report. `run_static`
  (`oracle_common.py:141-157`) and `compare` (`oracle_common.py:165-185`), including the `unsound`
  predicate at `:178-180`, are unchanged — they read verdicts, not arguments.
- **Tier 2** (`#4880`) renders each call sequence to Python source, extracts with
  `computation_graph_extractor` out of process, and lowers **the same way** with `lower_graph`. The
  comparison moves down a level: tier 1 and tier 2 are compared as **bytecode**, not as verdicts, so
  a divergence localises to an instruction index and a field rather than to "the reports disagree".
  A verdict comparison remains as the coarse backstop.
- **The plan's "extractor defect by construction" claim becomes true again — with one named residual.**
  The plan's tier-2 paragraph says a tier-1/tier-2 divergence is "an extractor defect **or a tier-1
  adapter defect**", and its 260902 qualification block (added by increment 1 §10.10 Q3) explains why
  the adapter half was live: the two sides used different argument-name conventions. Once both sides
  lower through the same `lower_graph`/`lower_calls` pair into the same instruction set, **the
  adapter no longer exists to be defective**, and a divergence is a defect in the extractor *or* in
  tier 2's source renderer. That residual is real (a renderer that emits
  `lh.aspirate(plate["A1"], 100)` positionally will diverge from a tier-1 row that binds
  `resources=`, via §11.2.4's trust rule) and should be stated in the plan rather than dropped —
  the honest replacement sentence is *"a divergence is a defect in the extractor or in the renderer;
  it can no longer be an adapter artefact."*
- **Concretely, why `n_exact_channel_sets` should stop being 0.** `plan_call`'s `bind("at")` for
  `pick_up_tips` (`dispatcher.py:159-161`) writes `kwargs["tip_spots"]` via `spec.plr_arg`
  (`param_namespace.py:168-171`), so every planned `pick_up_tips` row lowers to a `CALL` carrying a
  `Seq` under the PLR name that increment 1 §10.1.3 rule 3 reads. Predicted, not asserted: the
  replay's `n_exact_channel_sets` becomes ≥ the count of planned `pick_up_tips` calls. `#4879`
  measures it; if it is still 0, that is a finding about the harness, and AC-11.5's second half is
  the test that localises it.

---

## 11.11 Explicitly not in this increment

- **Any verdict change.** No `SAFE`, no `WILL_FAIL`, no abstract domain. AC-11.6 is the pin.
- **The cache itself** (#4922): key defined, store not. **Incremental re-check** (#4923): memo point
  named, algorithm not. **The interpreter** (#4924): triple named, semantics not.
- **The tip typestate walk** (#4888 steps 1–8) — this increment is its step 0 and nothing more.
- **Trip counts and branch predicates.** `LOOP`/`BRANCH` operands exist and stay `null`; deferred (c)
  and (d) are untouched.
- **Recovering positional argument names.** Membership-based trust only (§11.2.4); the indexing form
  waits on the survey emitting a positional/keyword-only boundary.
- **`extract/`** (round 2). The lowering consumes a graph payload produced out of process, exactly as
  §6.2 specifies today.
- **Wire format.** `Verdict`, `Finding`, `PlrSite`, `AnalysisReport`, `join`, `SCHEMA_VERSION = 1`
  (`verdict.py:74`), `Verdict.from_wire` (`verdict.py:97-113`) and `derived_contracts.json`'s
  `schema_version: 1` are all unchanged. SEMA-IR is an *internal* representation; it is not a
  persisted artifact in this increment and has no consumer outside `plr_sema` and `plr-sema/eval/`.
- **`check_graph` never raising** on a malformed payload (§11.6). Today's behaviour is kept; #4882
  owns the question.

---

## 11.12 Open questions for the adversarial round

1. **`operation_id` = instruction index, relabelled at the boundary (§11.4.3).** The bijection holds
   today because one `OperationNode` lowers to one `CALL`. Is that a property worth *enforcing* (a
   lowering that would emit two `CALL`s for one operation raises), or worth *generalising* now
   (`origin` becomes one-to-many and AC-6.4's equality is re-read as "the image of `origin`")?
   Enforcing it forecloses a plausible future (`transfer` lowering to its constituent
   aspirate/dispense sequence); generalising it weakens an AC that was strengthened for a reason.
2. **Should `WIDEN` be an instruction, or a flag on the following instruction?** As an instruction it
   is hashed, visible in a disassembly and countable; as a flag it cannot drift away from what it
   describes. The case against the instruction form: a `WIDEN` whose following instruction is later
   deleted becomes a widening with no subject, and nothing detects that.
3. **Excluding `protocol_fqn` from the hash (§11.3.2).** The design position is that #4922 caches
   findings and the caller reassembles the report. A reviewer who thinks the cache should store
   reports should say so now, because the alternative is to include `protocol_fqn` in the hash and
   lose cross-rename reuse — the decision constrains #4922's interface either way.
4. **HM-21's metric redefinition (§11.6).** 34-under-the-old-metric versus 3-under-the-new. The three
   conditions attached to the recommendation are what keep it from being a dilution; are they
   sufficient, or does this need the reviewer's own row?
5. **Where the trust rule lives (§11.2.4).** Putting `param_names` into `lower_graph` makes the
   bytecode a function of the program *and* the contract table, so "the bytecode identifies the
   program" is not quite true. Putting it in `check_ir` keeps the bytecode program-pure but makes it
   non-self-describing (the same bytecode means different things under different tables). The cache
   key carries `contracts_sha` either way, so no result is mis-reused; the question is which is the
   more honest object.
6. **`node_type` and the summary-field cross-checks (§11.1.4).** Four `WIDEN` triggers exist for
   fields that are *supposed* to be redundant. Is widening on a disagreement between two views of one
   fact the right response in all four cases, or does it create noise for `has_loops`/
   `has_conditionals`, whose disagreement is an upstream bug that should be reported rather than
   absorbed?
7. **`Seq` arity when the sequence is a `Name`.** `lh.pick_up_tips(tip_spots=spots)` lowers to
   `Top`, not `Seq`, so the arity is lost even though the protocol may bind `spots` two lines up.
   A one-hop local binding pass in the *extractor* would recover it. Named as a follow-up, not
   adopted — but a reviewer may think it belongs here, since it is the most common real-protocol
   shape after the literal list.

---

## References

- Main specification (amended): `.praxia/docs/specs/260901_plr-sema-pre-corpus-spec.md` — §0, §2.1–2.2,
  §3.1–3.3, §6.1–6.5, §7.3–7.4, §9.1–9.4, §Deferred + boundary summary, §Open decisions 1–3.
- Increment 1 (amended): `.praxia/docs/specs/260902_plr-sema-tip-typestate-increment.md` — §10.1.3,
  §10.5, §10.7's task row, §10.8, §10.9, §10.10 Q3 and Q7.
- Oracle plan (affected): `.praxia/docs/plans/260902_plr-sema-oracle-harness.md` — tiers 1–4, the
  260902 T18 qualification block, "Where it lives". Backlog `#4879`/`#4880`/`#4881`/`#4882`.
- Backlog for the later increments this one leaves hooks for: `#4922` (content-addressed cache),
  `#4923` (incremental re-check), `#4924` (error-recovery interpreter); `#4888` (tip typestate,
  blocked on this).
- Code read for this document: `praxis/backend/utils/plr_static_analysis/models.py`;
  `praxis/backend/utils/plr_static_analysis/visitors/computation_graph_extractor.py`;
  `plr-sema/src/plr_sema/check/graph.py`; `plr-sema/src/plr_sema/check/__init__.py`;
  `plr-sema/src/plr_sema/derive/__init__.py`; `plr-sema/src/plr_sema/_provenance/stamp.py`;
  `plr-sema/src/plr_sema/verdict.py`; `plr-sema/eval/oracle_common.py`;
  `training/verify/dispatcher.py`; `training/verify/verifier.py`;
  `coxswain/src/coxswain/plr/param_namespace.py`; `scripts/survey_plr_preconditions.py`.
- Data read: one row of `training/assemble/out/corpus_p25.jsonl` — the assistant tool call is
  `{"function":{"arguments":{"source":"plate_1.C7","volume_ul":25.0},"name":"aspirate"}}`, i.e.
  tool-named (`source`, `volume_ul`) against PLR's `resources`/`vols`, which is the naming gap
  §11.2.3 closes.
- PLR source at submodule pin `dd79c4c89`:
  `external/pylabrobot/pylabrobot/liquid_handling/liquid_handler.py` (`pick_up_tips` at `:438`, the
  `use_channels` channel-default idiom at `:501`, the `HasTipError` raise at `:535`).
