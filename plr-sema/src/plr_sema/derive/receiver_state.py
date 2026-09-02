"""plr_sema.derive.receiver_state: the four build-time passes for per-channel
tip typestate (spec 260902 §10.2, `260902_plr-sema-tip-typestate-increment.md`).

**What this module computes, and why it is a second, independent AST pass
(mirrors `scan_dropped_receiver_calls`'s own independence argument, §7.4).**
Everything `plr_sema.check.tipstate` needs at check time is DERIVED here,
by inspection of PLR source (P1-P3) and of the whole-survey index's own
records (P2's `state_fields`, the bridge scan) -- no PLR class name, method
name, field name or exception name is hand-typed anywhere in this file or
in `plr_sema.check.tipstate` (AC-10.9's AST literal scan enforces the
`check/`-side half of that claim; this module is `derive/`, which is
already permitted to import `ast` and read PLR source, §6.2/§7).

Four passes, matching the spec section numbers:

* **P1** (§10.2.1) -- ``_annotated_attributes``/``_attribute_writers``: a
  stdlib-``ast`` pass over every PLR class body finding ``self.<name>:
  <annotation>`` (unwrapped through ``Dict``/``List``/``Optional`` to a bare
  class name) and every ``self.<name> = ...`` write, keyed by the writing
  method's qualname. Research c-e's rule R3.
* **P2** (§10.2.2) -- ``_typestate_anchor``: the fail-closed single-property
  scan (`return self.<F> is/is not None`) that yields the boolean-view
  attribute name, the state field, and the polarity, all at once. Zero or
  more-than-one such property disables the feature for that class
  (fail-closed, not an error).
* **P3** (§10.2.3) -- ``_channel_default_idiom``: the
  ``<p> = <p> or self.<x> or list(range(len(<q>)))`` idiom match, per
  method of the RECEIVER class (not the tracker class); P3b derives the
  disabler method set from P1b's writer index for the same class.
* **P4** (§10.2.4) -- ``_effects``: classifies each of the tracker class's
  own methods' writes to a field in ``state_fields`` as NO_TIP / HAS_TIP /
  no-effect. A write whose RHS is itself another ``state_fields`` member
  (e.g. ``TipTracker.commit``'s ``self._tip = self._pending_tip``) is
  "ambiguous", which folds into "no effect" under the same both-kinds rule
  as a method that writes both a literal ``None`` and a literal non-``None``
  -- the literal P4 text ("`self.<F> = <expr>` where `<expr>` is not the
  literal `None`") under-specifies this case, and §10.2.4's own worked
  measurement of `commit` ("both-kinds-unknown -> no effect") only holds
  under this reading; see this module's own test for the synthetic
  counterexample that pins it.

**The channel bridge (§10.2.5) is the fifth piece and lives in
``compute_channel_bridge``.** It walks the SAME depth-tracked
``delegates_to`` closure ``derive_contract`` already walks
(``plr_sema.derive._walk_closure``), but keys on each visited record's
``dropped_calls`` (never ``delegates_to`` itself -- a dropped call is by
definition NOT a resolved delegate) matching the channel-receiver shape
``self.<channel_attr>[<name>].<method>``. "Depth 0" in this module's output
means the SAME thing §10.2.2/§10.2.4/§10.2.6 mean by it: the matching
``dropped_calls`` entry belongs to the record visited at closure depth 0
(the entry point's own body), never the guard's own internal depth within
the bridged tracker method (which the payload's illustrative JSON snippet's
``"depth": 1`` for `aspirate` does not actually mean, given `aspirate`'s own
`self.head[channel].get_tip` dropped call sits in its own body -- §10.2.6
states this in prose as depth 0; the JSON snippet is shape-illustrative
only, per this module's own worked-example tests).
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from plr_sema.derive import (
    Qualkey,
    SurveyRecord,
    _iter_plr_source_files,
    _module_name_for_plr_file,
    _walk_closure,
    default_plr_pkg_root,
    derive_contract,
)

__all__ = [
    "TIP_STATE_EXCEPTION_MODULE",
    "ReceiverState",
    "compute_tip_state_exceptions",
    "derive_receiver_states",
    "receiver_state_to_json",
    "compute_channel_bridge",
    "TipFamilies",
    "compute_tip_families",
]

#: §10.2.5's second conjunct: the taxonomy module path that narrows the
#: 5-member unfiltered `category == "tip_state"` set to exactly
#: {HasTipError, NoTipError}. Named as a constant (not re-typed at each use
#: site) because AC-10.9's AST literal scan treats "the module path is one
#: string literal in plr_sema's source, and that is disclosed, not hidden"
#: (§10.2.5) as the ONE sanctioned literal -- see plr_sema.check.tipstate
#: for the check-side half of that disclosure.
TIP_STATE_EXCEPTION_MODULE = "pylabrobot.resources.errors"

# The channel-receiver bridge shape (§10.2.5, HM-24 pattern 1):
# self.<attr>[<name>].<method>
_BRIDGE_SHAPE_RE = re.compile(r"^self\.(\w+)\[(\w+)\]\.(\w+)$")


def compute_tip_state_exceptions(taxonomy_classes: list[dict[str, Any]]) -> tuple[str, ...]:
    """§10.2.5's two-conjunct filter: `category == "tip_state"` AND
    `module == TIP_STATE_EXCEPTION_MODULE`, both fields already on every
    `plr_exception_taxonomy.json` entry -- nothing hand-typed but the module
    path itself (see this module's docstring and AC-10.9 sub-assertion 2).
    """
    return tuple(
        sorted(
            c["name"]
            for c in taxonomy_classes
            if c.get("category") == "tip_state" and c.get("module") == TIP_STATE_EXCEPTION_MODULE
        )
    )


# ---------------------------------------------------------------------------
# P1 (§10.2.1) -- receiver-attribute typing (research c-e's rule R3) and the
# attribute-writer index P3b needs.
# ---------------------------------------------------------------------------


def _unwrap_annotation(node: ast.expr | None) -> str | None:
    """Unwrap `Dict[K,V] -> V`, `List[T] -> T`, `Optional[T] -> T` (both the
    `typing.Optional[T]` subscript form and the PEP 604 `T | None` form) to
    a bare class name.
    """
    if node is None:
        return None
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Subscript):
        base = node.value
        base_name = (
            base.id
            if isinstance(base, ast.Name)
            else (base.attr if isinstance(base, ast.Attribute) else None)
        )
        sl = node.slice
        if base_name in ("Dict", "dict"):
            if isinstance(sl, ast.Tuple) and len(sl.elts) == 2:
                return _unwrap_annotation(sl.elts[1])
            return None
        if base_name in ("List", "list", "Sequence", "Optional", "Tuple", "tuple"):
            if isinstance(sl, ast.Tuple):
                return _unwrap_annotation(sl.elts[0]) if sl.elts else None
            return _unwrap_annotation(sl)
        return None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        left, right = _unwrap_annotation(node.left), _unwrap_annotation(node.right)
        if right == "None":
            return left
        if left == "None":
            return right
        return left
    return None


def _is_self_attr(node: ast.expr, name: str | None = None) -> bool:
    if not (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self"):
        return False
    return name is None or node.attr == name


def _annotated_attributes(class_node: ast.ClassDef) -> dict[str, str]:
    """P1a: every `self.<name>: <annotation>` `AnnAssign` anywhere in the
    class body (class-level or inside any method, e.g. `__init__`), first
    occurrence wins (deterministic).
    """
    out: dict[str, str] = {}
    for node in ast.walk(class_node):
        if isinstance(node, ast.AnnAssign) and _is_self_attr(node.target):
            unwrapped = _unwrap_annotation(node.annotation)
            if unwrapped is not None:
                out.setdefault(node.target.attr, unwrapped)  # type: ignore[union-attr]
    return out


def _attribute_writers(class_node: ast.ClassDef, class_name: str) -> dict[str, list[str]]:
    """P1b: for every `self.<name> = ...` `Assign` in the class, the
    qualname of the enclosing method. Descends into nested statements
    (`ast.walk` over the whole method body, including `try`/`finally`) so a
    write inside a context-manager `finally` block (`use_channels`'s own
    reset) is found.
    """
    out: dict[str, list[str]] = {}
    for member in ast.iter_child_nodes(class_node):
        if not isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        method_qualname = f"{class_name}.{member.name}"
        for node in ast.walk(member):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if _is_self_attr(target):
                        methods = out.setdefault(target.attr, [])  # type: ignore[union-attr]
                        if method_qualname not in methods:
                            methods.append(method_qualname)
    return out


# ---------------------------------------------------------------------------
# P2 (§10.2.2) -- the typestate anchor. Fail-closed: 0 or >1 candidate
# properties disables the feature for this class.
# ---------------------------------------------------------------------------


def _is_docstring_stmt(stmt: ast.stmt) -> bool:
    return isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str)


def _is_property_decorator(node: ast.expr) -> bool:
    return isinstance(node, ast.Name) and node.id == "property"


def _typestate_anchor(class_node: ast.ClassDef) -> tuple[str, str, str] | None:
    """Returns `(bool_view_attr, field, true_when)` where `true_when` is
    `"not_none"` (the property is true iff the field is not `None`) or
    `"is_none"` -- or `None` if zero or more than one candidate property
    exists (§10.2.2's fail-closed rule).
    """
    candidates: list[tuple[str, str, str]] = []
    for member in ast.iter_child_nodes(class_node):
        if not isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not any(_is_property_decorator(d) for d in member.decorator_list):
            continue
        body = [s for s in member.body if not _is_docstring_stmt(s)]
        if len(body) != 1:
            continue
        stmt = body[0]
        if not (isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Compare)):
            continue
        cmp = stmt.value
        if len(cmp.ops) != 1 or len(cmp.comparators) != 1:
            continue
        op = cmp.ops[0]
        if not isinstance(op, (ast.Is, ast.IsNot)):
            continue
        right = cmp.comparators[0]
        if not (isinstance(right, ast.Constant) and right.value is None):
            continue
        if not _is_self_attr(cmp.left):
            continue
        true_when = "not_none" if isinstance(op, ast.IsNot) else "is_none"
        candidates.append((member.name, cmp.left.attr, true_when))  # type: ignore[union-attr]
    if len(candidates) != 1:
        return None
    return candidates[0]


# ---------------------------------------------------------------------------
# P3 (§10.2.3) -- the channel-arity idiom (P3a) and its disablers (P3b).
# Both scanned over the RECEIVER class R (not the tracker class C).
# ---------------------------------------------------------------------------


def _is_list_range_len_call(node: ast.expr, param_name: str | None) -> str | None:
    """Matches `list(range(len(<q>)))`; returns `<q>`'s name if it matches
    (and, when `param_name` is given, requires `<q> == param_name` is NOT
    required -- `<q>` is an independent name, e.g. `tip_spots`, distinct
    from `<p>`).
    """
    if not (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "list"
        and len(node.args) == 1
    ):
        return None
    range_call = node.args[0]
    if not (
        isinstance(range_call, ast.Call)
        and isinstance(range_call.func, ast.Name)
        and range_call.func.id == "range"
        and len(range_call.args) == 1
    ):
        return None
    len_call = range_call.args[0]
    if not (
        isinstance(len_call, ast.Call)
        and isinstance(len_call.func, ast.Name)
        and len_call.func.id == "len"
        and len(len_call.args) == 1
        and isinstance(len_call.args[0], ast.Name)
    ):
        return None
    return len_call.args[0].id


def _channel_default_idiom(class_node: ast.ClassDef) -> dict[str, tuple[str, str]]:
    """P3a: `method_name -> (q, x)` for every method matching
    `<p> = <p> or self.<x> or list(range(len(<q>)))`.
    """
    out: dict[str, tuple[str, str]] = {}
    for member in ast.iter_child_nodes(class_node):
        if not isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(member):
            if not (isinstance(node, ast.Assign) and len(node.targets) == 1):
                continue
            target = node.targets[0]
            if not isinstance(target, ast.Name):
                continue
            p = target.id
            value = node.value
            if not (isinstance(value, ast.BoolOp) and isinstance(value.op, ast.Or) and len(value.values) == 3):
                continue
            v0, v1, v2 = value.values
            if not (isinstance(v0, ast.Name) and v0.id == p):
                continue
            if not _is_self_attr(v1):
                continue
            q = _is_list_range_len_call(v2, p)
            if q is None:
                continue
            out.setdefault(member.name, (q, v1.attr))  # type: ignore[union-attr]
    return out


def _channel_default_disablers(
    idiom_matches: dict[str, tuple[str, str]], attribute_writers: dict[str, list[str]]
) -> tuple[str, ...]:
    """P3b: the set of methods writing the `self.<x>` middle term of any P3a
    match, unioned across every distinct `x`. `attribute_writers` (P1b) is
    keyed by QUALIFIED method name (`f"{class_name}.{method}"`, per P1b's
    own definition); this result is the BARE method name (the shape
    `receiver_state["...]["channel_default_disablers"]` uses, matched at
    check time against `ir.Call.method`, which never carries a qualname).
    """
    disablers: set[str] = set()
    for _q, x in idiom_matches.values():
        for qualname in attribute_writers.get(x, ()):
            disablers.add(qualname.rsplit(".", 1)[-1])
    return tuple(sorted(disablers))


# ---------------------------------------------------------------------------
# P2's state_fields -- every field named in a NullCheck atom by any guard of
# C that raises a tip_state exception (§10.2.2's last paragraph). Needs the
# survey's own records for C, and the taxonomy filter.
# ---------------------------------------------------------------------------


def _null_check_field(condition: str | None) -> str | None:
    if condition is None:
        return None
    try:
        node = ast.parse(condition, mode="eval").body
    except SyntaxError:
        return None
    if not (isinstance(node, ast.Compare) and len(node.ops) == 1 and len(node.comparators) == 1):
        return None
    op = node.ops[0]
    if not isinstance(op, (ast.Is, ast.IsNot)):
        return None
    right = node.comparators[0]
    if not (isinstance(right, ast.Constant) and right.value is None):
        return None
    left = node.left
    if _is_self_attr(left):
        return left.attr  # type: ignore[union-attr]
    return None


def _state_fields_for_class(
    records_by_class: dict[str, list[SurveyRecord]],
    class_name: str,
    tip_state_exceptions: frozenset[str],
    bool_view_field: str,
) -> tuple[str, ...]:
    """§10.2.2: every field named in a NullCheck atom by any of C's OWN
    guards that raises a tip_state exception, plus the P2 anchor's own
    `bool_view_field` (always included -- it is load-bearing for BoolView
    atoms even on a class whose guards happen to name only the OTHER
    field, or none at all).
    """
    fields: set[str] = {bool_view_field}
    for rec in records_by_class.get(class_name, ()):
        for finding in rec.findings:
            if finding.raises in tip_state_exceptions:
                f = _null_check_field(finding.condition)
                if f is not None:
                    fields.add(f)
    return tuple(sorted(fields))


# ---------------------------------------------------------------------------
# P4 (§10.2.4) -- effects. Scanned over the TRACKER class C's own methods.
# ---------------------------------------------------------------------------


def _classify_write(value: ast.expr, state_field_set: frozenset[str]) -> str:
    """One write's classification: `"NO_TIP"` (literal `None`),
    `"ambiguous"` (the RHS is itself `self.<G>` for another/the-same state
    field -- its own runtime value is not analyzable as one literal kind,
    e.g. `TipTracker.commit`'s `self._tip = self._pending_tip`), or
    `"HAS_TIP"` (anything else non-`None`).
    """
    if isinstance(value, ast.Constant) and value.value is None:
        return "NO_TIP"
    if _is_self_attr(value) and value.attr in state_field_set:  # type: ignore[union-attr]
        return "ambiguous"
    return "HAS_TIP"


def _effects(class_node: ast.ClassDef, state_fields: tuple[str, ...]) -> dict[str, str]:
    """P4: `method_name -> "HAS_TIP"|"NO_TIP"` for every method of C whose
    writes to `state_fields` unambiguously establish one polarity. A method
    with no such write, or whose writes disagree/are ambiguous, is omitted
    (no effect -- E3).
    """
    state_field_set = frozenset(state_fields)
    out: dict[str, str] = {}
    for member in ast.iter_child_nodes(class_node):
        if not isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        kinds: set[str] = set()
        for node in ast.walk(member):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if _is_self_attr(target) and target.attr in state_field_set:  # type: ignore[union-attr]
                        kinds.add(_classify_write(node.value, state_field_set))
        if kinds == {"NO_TIP"}:
            out[member.name] = "NO_TIP"
        elif kinds == {"HAS_TIP"}:
            out[member.name] = "HAS_TIP"
        # {} (untouched), {"ambiguous"}, or any mix -> no effect, omitted.
    return out


# ---------------------------------------------------------------------------
# Assembling one ReceiverState per qualifying receiver class.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ReceiverState:
    channel_attr: str
    tracker_class: str
    tracker_module: str
    bool_view_attr: str
    bool_view_field: str
    true_when: str
    state_fields: tuple[str, ...]
    effects: dict[str, str]
    channel_default_param: dict[str, str]
    channel_default_disablers: tuple[str, ...]
    tip_state_exceptions: tuple[str, ...]


def receiver_state_to_json(rs: ReceiverState) -> dict[str, Any]:
    return {
        "channel_attr": rs.channel_attr,
        "tracker_class": rs.tracker_class,
        "bool_view": {"attr": rs.bool_view_attr, "field": rs.bool_view_field, "true_when": rs.true_when},
        "state_fields": list(rs.state_fields),
        "effects": dict(sorted(rs.effects.items())),
        "channel_default_param": dict(sorted(rs.channel_default_param.items())),
        "channel_default_disablers": list(rs.channel_default_disablers),
        "tip_state_exceptions": list(rs.tip_state_exceptions),
    }


def derive_receiver_states(
    plr_pkg_root: Path,
    records: list[SurveyRecord],
    taxonomy_classes: list[dict[str, Any]],
) -> dict[str, ReceiverState]:
    """Runs P1-P4 over the whole PLR source tree and returns one
    `ReceiverState` per qualifying receiver class (measured: `{"LiquidHandler":
    ...}` at the current pin -- `head96` also types to `TipTracker` under
    P1a but loses the deterministic tie-break, §10.9's non-goal).
    """
    root = plr_pkg_root if plr_pkg_root is not None else default_plr_pkg_root()
    tip_state_exceptions = compute_tip_state_exceptions(taxonomy_classes)
    tip_state_exceptions_set = frozenset(tip_state_exceptions)

    class_nodes: dict[str, ast.ClassDef] = {}
    class_modules: dict[str, str] = {}
    for file in _iter_plr_source_files(root):
        try:
            source = file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file))
        except (SyntaxError, UnicodeDecodeError):
            continue
        module = _module_name_for_plr_file(file, root)
        for top in ast.iter_child_nodes(tree):
            if isinstance(top, ast.ClassDef):
                class_nodes.setdefault(top.name, top)
                class_modules.setdefault(top.name, module)

    records_by_class: dict[str, list[SurveyRecord]] = {}
    for rec in records:
        if rec.class_name is not None:
            records_by_class.setdefault(rec.class_name, []).append(rec)

    # Cache P2/P4 results per tracker class -- multiple receiver classes
    # could type an attribute to the same tracker class.
    anchor_cache: dict[str, tuple[str, str, str] | None] = {}
    effects_cache: dict[str, dict[str, str]] = {}
    state_fields_cache: dict[str, tuple[str, ...]] = {}

    out: dict[str, ReceiverState] = {}
    for receiver_name, receiver_node in sorted(class_nodes.items()):
        annotated = _annotated_attributes(receiver_node)
        # Deterministic tie-break (§10.2's own note): among attributes
        # typing to an anchored class, pick alphabetically first
        # ("head" < "head96").
        for attr_name in sorted(annotated):
            tracker_class = annotated[attr_name]
            tracker_node = class_nodes.get(tracker_class)
            if tracker_node is None:
                continue
            if tracker_class not in anchor_cache:
                anchor_cache[tracker_class] = _typestate_anchor(tracker_node)
            anchor = anchor_cache[tracker_class]
            if anchor is None:
                continue  # P2 fail-closed: feature disabled for this class.
            bool_view_attr, bool_view_field, true_when = anchor

            if tracker_class not in state_fields_cache:
                state_fields_cache[tracker_class] = _state_fields_for_class(
                    records_by_class, tracker_class, tip_state_exceptions_set, bool_view_field
                )
            state_fields = state_fields_cache[tracker_class]

            if tracker_class not in effects_cache:
                effects_cache[tracker_class] = _effects(tracker_node, state_fields)
            effects = effects_cache[tracker_class]

            idiom_matches = _channel_default_idiom(receiver_node)
            channel_default_param = {m: q for m, (q, _x) in idiom_matches.items()}
            attribute_writers = _attribute_writers(receiver_node, receiver_name)
            disablers = _channel_default_disablers(idiom_matches, attribute_writers)

            out[receiver_name] = ReceiverState(
                channel_attr=attr_name,
                tracker_class=tracker_class,
                tracker_module=class_modules[tracker_class],
                bool_view_attr=bool_view_attr,
                bool_view_field=bool_view_field,
                true_when=true_when,
                state_fields=state_fields,
                effects=effects,
                channel_default_param=channel_default_param,
                channel_default_disablers=disablers,
                tip_state_exceptions=tip_state_exceptions,
            )
            break  # first (alphabetically) qualifying attribute wins.
    return out


# ---------------------------------------------------------------------------
# §10.2.5 -- the channel bridge, and §10.2.6's tip-loading / tip-requiring /
# tip-dropping family selection (AC-10.10).
# ---------------------------------------------------------------------------


def compute_channel_bridge(
    entry: Qualkey,
    index: dict[Qualkey, SurveyRecord],
    *,
    receiver_state: ReceiverState,
    stamp: Any,
) -> tuple[list[dict[str, Any]], str | None]:
    """§10.2.5: walk `entry`'s SAME depth-tracked `delegates_to` closure
    `derive_contract` walks, matching every `dropped_calls` entry against
    `self.<channel_attr>[<name>].<method>`. Returns
    `(channel_guards_json, channel_effect)` where `channel_effect` is
    `None` (E3, no bridge at all), `"HAS_TIP"`/`"NO_TIP"` (E2, exactly one
    agreeing depth-0 effect), or `"widen"` (E4.2 deep-only or E4.3
    conflicting-depth-0, per §10.2.4/§10.4 -- both collapse to the SAME
    transfer-function outcome, so the evaluator does not need to
    distinguish them).
    """
    channel_guards: list[dict[str, Any]] = []
    depth0_effects: set[str] = set()
    any_deep_effect = False
    seen: set[tuple[int, str]] = set()

    for rec, _key, depth in _walk_closure(entry, index):
        if rec is None:
            continue
        for expr in rec.dropped_calls:
            # HM-24, pattern 1: the ONE canonical bridge-shape regex,
            # checked against THIS receiver's own `channel_attr` (group 1)
            # -- not a fresh per-call `re.compile`.
            m = _BRIDGE_SHAPE_RE.match(expr)
            if m is None or m.group(1) != receiver_state.channel_attr:
                continue
            method = m.group(3)
            c_key: Qualkey = (receiver_state.tracker_module, f"{receiver_state.tracker_class}.{method}")
            if c_key not in index:
                continue
            if (depth, method) in seen:
                continue
            seen.add((depth, method))

            method_contract = derive_contract(
                receiver_state.tracker_module, f"{receiver_state.tracker_class}.{method}", index, stamp=stamp
            )
            for guard in method_contract.guards:
                channel_guards.append(
                    {
                        "condition": guard.condition,
                        "kind": guard.kind,
                        "raises": guard.raises,
                        "free_vars": list(guard.free_vars),
                        "scope_trail": list(guard.scope_trail),
                        "depth": depth,
                        "site": {
                            "file": guard.site.file,
                            "lineno": guard.site.lineno,
                            "qualname": guard.site.qualname,
                        },
                        "via": expr,
                    }
                )

            effect = receiver_state.effects.get(method)
            if effect is not None:
                if depth == 0:
                    depth0_effects.add(effect)
                else:
                    any_deep_effect = True

    if len(depth0_effects) == 1:
        channel_effect: str | None = next(iter(depth0_effects))
    elif len(depth0_effects) >= 2 or any_deep_effect:
        channel_effect = "widen"
    else:
        channel_effect = None
    return channel_guards, channel_effect


@dataclass(frozen=True, slots=True)
class TipFamilies:
    """§10.2.6/AC-10.10: the three derived method-name sets, published (not
    asserted) per anchored receiver class.
    """

    tip_loading: tuple[str, ...] = ()
    tip_requiring: tuple[str, ...] = ()
    tip_dropping: tuple[str, ...] = ()


def _guard_demanded_state(condition: str | None, bool_view_attr: str) -> str | None:
    """§10.2.6's classification of one raise_guard's atom into which state
    it DEMANDS (the state under which the guard does NOT fire, i.e. the
    precondition for the call to be legal): a `BoolView` atom (fires when
    HAS_TIP) demands `"NO_TIP"`; a `NullCheck(is_none=True)` atom (fires
    when NO_TIP) demands `"HAS_TIP"`; a `NullCheck(is_none=False)` atom
    (fires when HAS_TIP) demands `"NO_TIP"`. Returns `None` for anything
    that doesn't parse to one of the three atom productions -- this is a
    REPORTING classifier (AC-10.10), independent of (but structurally
    identical to) `plr_sema.check.tipstate`'s evaluator-side atom parser.
    """
    if condition is None:
        return None
    try:
        node = ast.parse(condition, mode="eval").body
    except SyntaxError:
        return None
    if _is_self_attr(node, bool_view_attr) or (
        isinstance(node, ast.Attribute) and node.attr == bool_view_attr
    ):
        return "NO_TIP"
    if isinstance(node, ast.Compare) and len(node.ops) == 1 and len(node.comparators) == 1:
        op = node.ops[0]
        right = node.comparators[0]
        if isinstance(op, (ast.Is, ast.IsNot)) and isinstance(right, ast.Constant) and right.value is None:
            if isinstance(op, ast.Is):
                return "HAS_TIP"  # fires when the field IS None (NO_TIP) -> demands HAS_TIP
            return "NO_TIP"  # fires when the field is NOT None (HAS_TIP) -> demands NO_TIP
    return None


def compute_tip_families(
    contract_entries: dict[str, dict[str, Any]],
    *,
    receiver_class: str,
    receiver_state: ReceiverState,
) -> TipFamilies:
    """§10.2.6: derived directly from the ALREADY-BUILT contract table (own
    `guards` + additive `channel_guards`, and the additive `channel_effect`)
    -- no re-walking of the closure. `f"{receiver_class}.<method>"` keys are
    scanned; a colliding (disambiguated, `@module:lineno`-suffixed) key is
    skipped (§7.2's `build_contract_keys` note: unreachable via
    `receiver_type.method_name` lookup anyway, so it cannot appear as a
    real `CALL.method` either).
    """
    tip_state_exceptions = frozenset(receiver_state.tip_state_exceptions)
    loading: set[str] = set()
    requiring: set[str] = set()
    dropping: set[str] = set()
    prefix = f"{receiver_class}."
    for key, entry in contract_entries.items():
        if not key.startswith(prefix) or "@" in key:
            continue
        method = key[len(prefix) :]
        all_guards = list(entry.get("guards", ())) + list(entry.get("channel_guards", ()))
        for g in all_guards:
            if g.get("kind") != "raise_guard" or g.get("raises") not in tip_state_exceptions:
                continue
            demanded = _guard_demanded_state(g.get("condition"), receiver_state.bool_view_attr)
            if demanded == "NO_TIP":
                loading.add(method)
            elif demanded == "HAS_TIP":
                requiring.add(method)
        channel_effect = entry.get("channel_effect")
        if channel_effect == "HAS_TIP":
            loading.add(method)
        if channel_effect == "NO_TIP":
            dropping.add(method)
    return TipFamilies(
        tip_loading=tuple(sorted(loading)),
        tip_requiring=tuple(sorted(requiring)),
        tip_dropping=tuple(sorted(dropping)),
    )
