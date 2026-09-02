"""plr_sema.check.tipstate: per-channel tip typestate (spec 260902 §10,
`260902_plr-sema-tip-typestate-increment.md`).

**Stdlib only** -- same import boundary as the rest of `check/` (module
docstring of `plr_sema.check`): no `pylabrobot`, no `libcst`, no
`pydantic`. `ast` is permitted (stdlib, used only to parse a guard's own
`condition` string into one of the three atom productions, §10.3.1 --
`derive/` already relies on the same distinction).

**What this module is.** §10.1's three-element lattice (`TipState`), §10.1.3's
channel-set derivation over an already-lowered `ir.Call.kwargs` (§11.9's
amendment: "lowers to a `Seq`", not "`ast.literal_eval`s to a list"),
§10.3's atom parser and evaluator, and §10.4's transfer functions (E1-E5).
`plr_sema.check.__init__.check_ir` threads a :class:`TipWalk` through its
existing region-stack pass over `bytecode.instructions` and calls
:func:`evaluate_call` once per `CALL`, in place of (for the guards this
module claims) or alongside (for `channel_guards`, which have no
`guard_predicate_unparsed` twin to replace) the pre-increment
`guard_predicate_unparsed` emission.

**Exactly one `Finding` per guard, never per operation (§10.3.3).** This
module never aggregates; `plr_sema.verdict.join` still does that, unchanged.

**No hand-typed PLR fact.** Every name this module reads (`channel_attr`,
`bool_view`'s `attr`/`field`, `state_fields`, `channel_default_param`,
`channel_default_disablers`) comes from the `receiver_state` block
`plr_sema.derive.receiver_state` computed at build time (§10.2) -- this
module only reads it via `.get()`, never types a PLR name itself
(AC-10.9's AST literal scan enforces this for this file specifically, same
mechanism as `plr_sema.check.ir`'s own AC-11.8 scan).
"""

from __future__ import annotations

import ast
import dataclasses
from enum import Enum
from typing import Any

from plr_sema.check import ir
from plr_sema.verdict import Finding, PlrSite, Verdict

__all__ = [
    "TipState",
    "join_tip",
    "ChannelState",
    "TipWalk",
    "channels_for_call",
    "evaluate_call",
    "region_receivers",
    "disabled_receivers",
]


# ---------------------------------------------------------------------------
# §10.1.1 -- the lattice. Three elements, no bottom (main spec §Open
# decisions 1's reservation; this increment constructs neither branches nor
# an emptiness-detecting transfer function, so nothing needs one).
# ---------------------------------------------------------------------------


class TipState(Enum):
    NO_TIP = "NO_TIP"
    HAS_TIP = "HAS_TIP"
    TOP = "top"


def join_tip(a: TipState, b: TipState) -> TipState:
    """§10.1.1's join table: `NO_TIP up NO_TIP = NO_TIP`, `HAS_TIP up
    HAS_TIP = HAS_TIP`, everything else (including `TOP` with anything) is
    `TOP` -- the information order, never confused with `plr_sema.verdict
    .join`'s obligation order (§10.1.2).
    """
    return a if a is b else TipState.TOP


def fold_channels(channels: tuple[int, ...] | None, state_of: Any) -> TipState:
    """§10.3.2: `s = the join folded over op's channel set` -- `NO_TIP` iff
    every channel is `NO_TIP`, `HAS_TIP` iff every channel is `HAS_TIP`,
    `TOP` otherwise (including when `channels` is `None`, i.e. rule 4's
    `channels = Top`, §10.1.3).
    """
    if channels is None or not channels:
        return TipState.TOP
    states = {state_of(c) for c in channels}
    if states == {TipState.NO_TIP}:
        return TipState.NO_TIP
    if states == {TipState.HAS_TIP}:
        return TipState.HAS_TIP
    return TipState.TOP


# ---------------------------------------------------------------------------
# §10.1.3/§10.1.4 -- per-receiver abstract state.
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class ChannelState:
    """`(default, exact)` (§10.1.3): `default` is `TOP` at graph entry and
    is only ever LOWERED by an exact-channel transfer function that
    provably applies to every channel -- nothing in this increment does
    that, so `default` stays `TOP` for the whole walk (precision comes
    entirely from `exact`).
    """

    default: TipState = TipState.TOP
    exact: dict[int, TipState] = dataclasses.field(default_factory=dict)

    def get(self, channel: int) -> TipState:
        return self.exact.get(channel, self.default)


class TipWalk:
    """Per-receiver-slot `ChannelState`, threaded through `check_ir`'s
    region-stack pass. A slot never seen defaults to a fresh
    `ChannelState()` (`default=TOP, exact={}`) -- §10.1.3's "TOP at graph
    entry", read lazily rather than pre-seeded, since the set of receiver
    slots is only known once `RESOURCE`/`CALL` instructions are walked.
    """

    def __init__(self) -> None:
        self._states: dict[int, ChannelState] = {}

    def _cs(self, slot: int) -> ChannelState:
        cs = self._states.get(slot)
        if cs is None:
            cs = ChannelState()
            self._states[slot] = cs
        return cs

    def state(self, slot: int, channel: int) -> TipState:
        return self._cs(slot).get(channel)

    def widen(self, slot: int) -> None:
        """E4 (§10.4): the whole receiver is widened -- `sigma' =
        (default=TOP, exact={})`. Monotonic: widening can only destroy a
        verdict, never create a wrong one (§10.5's soundness argument).
        """
        self._states[slot] = ChannelState()

    def apply_exact(self, slot: int, channels: tuple[int, ...], effect: TipState) -> None:
        """E2 (§10.4): `sigma'.exact[c] = e` for each `c` in `channels`;
        channels outside the set are unchanged.
        """
        cs = self._cs(slot)
        for c in channels:
            cs.exact[c] = effect


# ---------------------------------------------------------------------------
# §10.1.3 -- channel-set derivation over an already-lowered ir.Value
# (§11.9's amendment: "lowers to a Seq", not "ast.literal_eval's to a
# list").
# ---------------------------------------------------------------------------


def _int_seq(value: ir.Value | None) -> tuple[int, ...] | None:
    """Rule 1 (explicit): `value` is a `Seq` of `Lit` integers -> the exact
    tuple. `bool` is excluded even though `isinstance(True, int)` is `True`
    in Python -- a channel list is never boolean-valued in any real
    payload, and this keeps the rule from silently accepting one.
    """
    if not isinstance(value, ir.Seq):
        return None
    out: list[int] = []
    for item in value.items:
        if not (isinstance(item, ir.Lit) and isinstance(item.v, int) and not isinstance(item.v, bool)):
            return None
        out.append(item.v)
    return tuple(out)


def channels_for_call(call: ir.Call, channel_default_param: dict[str, str]) -> tuple[int, ...] | None:
    """§10.1.3, rules 1/3/4 (rule 2 -- the instance-default disabler -- is
    enforced structurally by :func:`disabled_receivers`'s pre-scan, which
    forces this function to be skipped entirely for a poisoned receiver;
    see `evaluate_call`). Returns the exact channel tuple, or `None` for
    `channels = Top` (rule 4).
    """
    explicit = _int_seq(call.kwargs.get("use_channels"))
    if explicit is not None:
        return explicit
    param = channel_default_param.get(call.method)
    if param is not None:
        value = call.kwargs.get(param)
        if isinstance(value, ir.Seq):
            return tuple(range(len(value.items)))
    return None


def disabled_receivers(instructions: tuple[ir.Instruction, ...], receiver_states: dict[str, dict[str, Any]]) -> frozenset[int]:
    """§10.1.3 rule 2 / §10.4 E4 condition 4: a whole-program pre-scan --
    any `CALL` whose `method` is a `channel_default_disablers` member for
    its `receiver_type` poisons that receiver SLOT permanently, regardless
    of where in the stream the disabler call sits (the PLR fact this models
    -- `self._default_use_channels` -- is set by a context manager the
    analyzer cannot see the extent of, main spec §10.1.3). Enforced
    structurally: :func:`channels_for_call` is simply never invoked for a
    poisoned slot (`evaluate_call` checks membership first), so a poisoned
    receiver's channel set is `Top` for EVERY operation on it, matching
    "permanently".
    """
    poisoned: set[int] = set()
    for instr in instructions:
        if not isinstance(instr, ir.Call) or instr.receiver_type is None:
            continue
        rs = receiver_states.get(instr.receiver_type)
        if rs is None:
            continue
        if instr.method in rs.get("channel_default_disablers", ()):
            poisoned.add(instr.receiver)
    return frozenset(poisoned)


def region_receivers(instructions: tuple[ir.Instruction, ...], open_pc: int) -> tuple[frozenset[int], int]:
    """§11.1.3/§11.4.1's region-entry widening: given the pc of a `LOOP`/
    `BRANCH` open instruction, returns `(receiver slots mentioned anywhere
    in the region, the pc of the matching END)`. Handles nesting (a region
    inside the region) via a depth counter over `LOOP`/`BRANCH` opens vs.
    `END`s -- `ELSE` never changes depth (§11.1.3: it separates the two
    arms of the SAME open `BRANCH`).
    """
    depth = 1
    receivers: set[int] = set()
    pc = open_pc + 1
    n = len(instructions)
    while pc < n and depth > 0:
        instr = instructions[pc]
        if isinstance(instr, (ir.Loop, ir.Branch)):
            depth += 1
        elif isinstance(instr, ir.End):
            depth -= 1
            if depth == 0:
                break
        elif isinstance(instr, ir.Call):
            receivers.add(instr.receiver)
        pc += 1
    return frozenset(receivers), pc


# ---------------------------------------------------------------------------
# §10.3.1 -- the atom parser. Two shapes: an OWN guard's condition (must
# name the channel-scoped path `self.<channel_attr>[<idx>].<...>`), and a
# CHANNEL guard's condition (channel-scope already established by its
# `via` field, so a bare `self.<...>` suffices, §10.3.1 criterion 3).
# ---------------------------------------------------------------------------

# (kind, is_none) -- kind is "bool_view" (is_none always None) or
# "null_check" (is_none True/False).
_Atom = tuple[str, "bool | None"]


def _is_self_attr(node: ast.expr, name: str | None = None) -> bool:
    if not (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self"):
        return False
    return name is None or node.attr == name


def _null_check(node: ast.expr, state_fields: frozenset[str], base_ok: Any) -> _Atom | None:
    if not (isinstance(node, ast.Compare) and len(node.ops) == 1 and len(node.comparators) == 1):
        return None
    op = node.ops[0]
    if not isinstance(op, (ast.Is, ast.IsNot)):
        return None
    right = node.comparators[0]
    if not (isinstance(right, ast.Constant) and right.value is None):
        return None
    left = node.left
    if isinstance(left, ast.Attribute) and left.attr in state_fields and base_ok(left.value):
        return ("null_check", isinstance(op, ast.Is))
    return None


def _parse_atom(condition: str | None, *, bool_view_attr: str, state_fields: frozenset[str], base_ok: Any) -> _Atom | None:
    """Shared parser core. `base_ok(node.value)` decides whether the
    Attribute's RECEIVER expression is acceptable (channel-scoped for an
    own guard, or bare `self` for a channel guard) -- the only difference
    between the two call sites below.
    """
    if condition is None:
        return None
    try:
        node = ast.parse(condition, mode="eval").body
    except SyntaxError:
        return None
    if isinstance(node, ast.Attribute) and node.attr == bool_view_attr and base_ok(node.value):
        return ("bool_view", None)
    return _null_check(node, state_fields, base_ok)


def _is_channel_subscript(node: ast.expr, channel_attr: str) -> bool:
    return (
        isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Attribute)
        and isinstance(node.value.value, ast.Name)
        and node.value.value.id == "self"
        and node.value.attr == channel_attr
    )


def parse_own_atom(
    condition: str | None, *, channel_attr: str, bool_view_attr: str, state_fields: frozenset[str]
) -> _Atom | None:
    """§10.3.1 criterion 3, own-guard half: the path begins
    `self.<channel_attr>[<name>]`, e.g. `self.head[channel].has_tip`.
    """
    return _parse_atom(
        condition,
        bool_view_attr=bool_view_attr,
        state_fields=state_fields,
        base_ok=lambda base: _is_channel_subscript(base, channel_attr),
    )


def parse_bridge_atom(condition: str | None, *, bool_view_attr: str, state_fields: frozenset[str]) -> _Atom | None:
    """§10.3.1 criterion 3, channel-guard half: channel scope is already
    established by the guard's `via` field, so a bare `self.<...>`
    suffices, e.g. `self._tip is None` (from `TipTracker.get_tip`, reached
    via `self.head[channel].get_tip`).
    """
    return _parse_atom(
        condition,
        bool_view_attr=bool_view_attr,
        state_fields=state_fields,
        base_ok=lambda base: isinstance(base, ast.Name) and base.id == "self",
    )


def atom_truth(atom: _Atom, s: TipState) -> str:
    """§10.3.2's truth table. Returns `"T"`, `"F"`, or `"half"`."""
    if s is TipState.TOP:
        return "half"
    kind, is_none = atom
    if kind == "bool_view":
        return "T" if s is TipState.HAS_TIP else "F"
    # null_check
    if is_none:
        return "T" if s is TipState.NO_TIP else "F"
    return "T" if s is TipState.HAS_TIP else "F"


def _finding_for_atom(operation_id: str, guard_json: dict[str, Any], atom: _Atom, s: TipState) -> Finding:
    """§10.3.3's fires -> Finding table. `guard.kind == "raise_guard"` is a
    precondition of calling this (checked by the caller, §10.3.1 criterion
    1) -- `fires` is exactly the atom's truth value.
    """
    truth = atom_truth(atom, s)
    site_json = guard_json.get("site")
    site = PlrSite(file=site_json["file"], lineno=site_json["lineno"], qualname=site_json["qualname"]) if site_json else None
    detail = guard_json.get("condition") or ""
    if truth == "T":
        return Finding(
            verdict=Verdict.WILL_FAIL, operation_id=operation_id, category="precondition_state", plr_site=site, reason="", detail=detail
        )
    if truth == "F":
        return Finding(verdict=Verdict.SAFE, operation_id=operation_id, category="", plr_site=site, reason="", detail=detail)
    return Finding(
        verdict=Verdict.UNKNOWN, operation_id=operation_id, category="", plr_site=site, reason="channel_state_unknown", detail=detail
    )


# ---------------------------------------------------------------------------
# §10.4 -- the transfer function, and the per-CALL entry point.
# ---------------------------------------------------------------------------


def _apply_transfer(
    call: ir.Call,
    channels: tuple[int, ...] | None,
    contract: dict[str, Any],
    walk: TipWalk,
    *,
    poisoned: bool,
) -> None:
    """E1's second half (§10.4): applied AFTER guards are evaluated against
    the pre-state. `contract["channel_effect"]` is `None` (E3, no bridge),
    `"HAS_TIP"`/`"NO_TIP"` (a single agreed depth-0 effect), or `"widen"`
    (E4.2 deep-only or E4.3 conflicting-depth-0 -- both collapse to the
    same transfer-function outcome, `derive.receiver_state
    .compute_channel_bridge`'s own docstring).
    """
    if poisoned:
        return  # rule 2/E4 condition 4: permanently Top; nothing to apply.
    effect = contract.get("channel_effect")
    if effect is None:
        return  # E3.
    if effect == "widen":
        walk.widen(call.receiver)
        return
    if channels is None:
        # E4 condition 1: a tracker-mutating bridge exists but channels(op)
        # is Top.
        walk.widen(call.receiver)
        return
    walk.apply_exact(call.receiver, channels, TipState.HAS_TIP if effect == "HAS_TIP" else TipState.NO_TIP)


def evaluate_call(
    operation_id: str,
    call: ir.Call,
    contract: dict[str, Any],
    receiver_state: dict[str, Any] | None,
    walk: TipWalk,
    *,
    poisoned: bool,
) -> tuple[tuple[Finding, ...], frozenset[int]]:
    """The per-`CALL` entry point. Returns `(tip_state_findings,
    consumed_own_guard_indices)` -- the second element is the set of
    indices into `contract["guards"]` whose `guard_predicate_unparsed`
    emission the caller (`plr_sema.check._findings_for_call`) must SKIP,
    because this function already emitted the real `WILL_FAIL`/`SAFE`/
    `channel_state_unknown` `Finding` in its place (§10.3.3: "the emission
    above REPLACES, one-for-one, the `guard_predicate_unparsed` finding").

    E5 (§10.4): `receiver_state is None` (no P2 anchor for this receiver
    type, or `receiver_type is None`) -> `((), frozenset())`, no
    involvement at all.
    """
    if receiver_state is None:
        return (), frozenset()

    channel_attr = receiver_state["channel_attr"]
    bool_view_attr = receiver_state["bool_view"]["attr"]
    state_fields = frozenset(receiver_state.get("state_fields", ()))
    channel_default_param = receiver_state.get("channel_default_param", {})

    channels = None if poisoned else channels_for_call(call, channel_default_param)

    # §10.3.1 criterion 4, GATING (not a fold-to-Top input): "op's channel
    # set is exact ... and every channel in it has a state that is not
    # Top." An INEXACT channel set (rule 4, `channels is None`) means the
    # guard is not tip-state-interpretable AT ALL -- it falls through to
    # the old `guard_predicate_unparsed` finding, UNCHANGED (AC-10.4: the
    # shipped fixture's operations never resolve an exact channel set, so
    # zero `channel_state_unknown` findings are produced, not "produced
    # with reason=Top"). Only once the channel SET is known exact does the
    # evaluator proceed to FOLD the per-channel STATES (§10.3.2) -- and
    # THAT fold can still legitimately yield Top (disagreeing or
    # individually-Top channel states), which IS when `channel_state_unknown`
    # fires. Conflating "channel set inexact" with "folded state is Top"
    # was an earlier draft's bug; the two are different gates at different
    # points of §10.3.
    findings: list[Finding] = []
    consumed: set[int] = set()

    if channels is not None:
        s = fold_channels(channels, lambda c: walk.state(call.receiver, c))

        for idx, guard in enumerate(contract.get("guards", ())):
            if guard.get("kind") != "raise_guard":
                continue
            atom = parse_own_atom(
                guard.get("condition"), channel_attr=channel_attr, bool_view_attr=bool_view_attr, state_fields=state_fields
            )
            if atom is None:
                continue
            consumed.add(idx)
            findings.append(_finding_for_atom(operation_id, guard, atom, s))

        for guard in contract.get("channel_guards", ()):
            if guard.get("kind") != "raise_guard":
                continue
            atom = parse_bridge_atom(guard.get("condition"), bool_view_attr=bool_view_attr, state_fields=state_fields)
            if atom is None:
                continue
            findings.append(_finding_for_atom(operation_id, guard, atom, s))

    _apply_transfer(call, channels, contract, walk, poisoned=poisoned)

    return tuple(findings), frozenset(consumed)
