"""Tests for plr-sema/eval/t30_measure.py (spec 260904 sec15.9, T30b).

Synthetic guard/call fixtures, one per sec15.7 reason (plus `decidable`),
and the GO/NO-GO gate function over a synthetic per-op set. These do not
touch the frozen benchmark or the real contract table -- that is what
running the script itself (recorded in the T30b commit) exercises.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "plr-sema" / "eval"))
sys.path.insert(0, str(REPO_ROOT / "plr-sema" / "src"))

from plr_sema.check import ir as _ir  # noqa: E402
from t30_measure import (  # noqa: E402
    REASON_DECIDABLE,
    REASON_ENV,
    REASON_OPERAND,
    REASON_UNPARSED,
    classify_guard_for_call,
    classify_guard_structural,
    compute_gate,
    is_tip_family_owned,
)


def _var(name: str) -> dict:
    return {"node": "Var", "name": name}


def _lit(value) -> dict:
    return {"node": "Lit", "value": value}


def _cmp(left: dict, op: str, right: dict) -> dict:
    return {"node": "Cmp", "left": left, "op": op, "right": right}


def _len(term: dict) -> dict:
    return {"node": "Len", "term": term}


def _guard(
    predicate: dict,
    *,
    depth: int = 0,
    bindings: tuple[dict, ...] = (),
    raises: str | None = "ValueError",
    lineno: int = 100,
    qualname: str = "Widget.frobnicate",
    condition: str = "x",
) -> dict:
    return {
        "condition": condition,
        "predicate": predicate,
        "scope_trail": [],
        "raises": raises,
        "kind": "raise_guard",
        "free_vars": [],
        "site": {"file": "synthetic/module.py", "lineno": lineno, "qualname": qualname},
        "depth": depth,
        "bindings": list(bindings),
    }


def _call(kwargs: dict[str, _ir.Value], *, method: str = "frobnicate") -> _ir.Call:
    return _ir.Call(receiver=0, receiver_type="Widget", method=method, kwargs=kwargs)


# ---------------------------------------------------------------------------
# classify_guard_for_call -- one fixture per reason.
# ---------------------------------------------------------------------------


def test_classify_top_level_opaque_is_unparsed() -> None:
    g = _guard({"node": "Opaque", "text": "c not in self.head"})
    call = _call({})
    assert classify_guard_for_call(g, call, {}, {}, set()) == REASON_UNPARSED


def test_classify_nested_opaque_via_alpha_binding_is_unparsed() -> None:
    """sec15.7's own worked example: the top node parses (a plain Cmp over
    a bound name), but the alpha binding's OWN inner predicate is Opaque
    -- the guard stays `guard_predicate_unparsed` under the nested rule.
    """
    pred = _cmp(_len(_var("invalid_channels")), ">", _lit(0))
    binding = {
        "idiom": "alpha",
        "x": "invalid_channels",
        "iter": "channels",
        "pred": {"node": "Opaque", "text": "c not in self.head"},
    }
    g = _guard(pred, depth=1, bindings=(binding,))
    call = _call({"channels": _ir.Top()})
    assert classify_guard_for_call(g, call, {}, {}, set()) == REASON_UNPARSED


def test_classify_dynamic_raise_is_env_dependent() -> None:
    g = _guard({"node": "TRUE"}, raises="<dynamic:e>")
    call = _call({})
    assert classify_guard_for_call(g, call, {}, {}, set()) == REASON_ENV


def test_classify_depth1_unbound_free_name_is_env_dependent() -> None:
    """E-CALL(depth): a depth>=1 guard's free name never resolves against
    the entry point's kwargs, even if the call happens to carry a
    same-named kwarg.
    """
    g = _guard({"node": "Is", "term": _var("resources"), "negated": False}, depth=1)
    call = _call({"resources": _ir.Lit(v=None)})
    assert classify_guard_for_call(g, call, {}, {}, set()) == REASON_ENV


def test_classify_depth0_missing_kwarg_and_no_default_is_env_dependent() -> None:
    pred = _cmp(_var("strictness"), "==", _lit("STRICT"))
    g = _guard(pred, depth=0)
    call = _call({})  # "strictness" is not a kwarg at all.
    assert classify_guard_for_call(g, call, {}, {}, set()) == REASON_ENV


def test_classify_operand_unknown_top_kwarg() -> None:
    """Every free name resolves (it IS a real kwarg), but its VALUE is
    Top (renamed/unresolvable) -- guard_operand_unknown, not env-dependent.
    """
    pred = _cmp(_len(_var("use_channels")), "==", _len(_var("use_channels")))
    g = _guard(pred, depth=0)
    call = _call({"use_channels": _ir.Top()})
    assert classify_guard_for_call(g, call, {}, {}, set()) == REASON_OPERAND


def test_classify_operand_unknown_alpha_element_type_missing() -> None:
    """The alpha-bound Filtered term's element type cannot be decided
    (no RESOURCE declaration for the ref's slot) -- guard_operand_unknown.
    """
    pred = _cmp(_len(_var("not_tip_spots")), ">", _lit(0))
    binding = {
        "idiom": "alpha",
        "x": "not_tip_spots",
        "iter": "tip_spots",
        "pred": {"node": "Not", "predicate": {"node": "IsInstance", "term": _var("ts"), "types": ["TipSpot"]}},
    }
    g = _guard(pred, depth=0, bindings=(binding,))
    call = _call({"tip_spots": _ir.Seq(items=(_ir.Ref(slot=0, cell="A1"),))})
    # No slot_to_resource entry at all for slot 0 -> element type unresolvable.
    assert classify_guard_for_call(g, call, {}, {}, set()) == REASON_OPERAND


def test_classify_decidable_alpha_element_type_known() -> None:
    pred = _cmp(_len(_var("not_tip_spots")), ">", _lit(0))
    binding = {
        "idiom": "alpha",
        "x": "not_tip_spots",
        "iter": "tip_spots",
        "pred": {"node": "Not", "predicate": {"node": "IsInstance", "term": _var("ts"), "types": ["TipSpot"]}},
    }
    g = _guard(pred, depth=0, bindings=(binding,))
    call = _call({"tip_spots": _ir.Seq(items=(_ir.Ref(slot=0, cell="A1"),))})
    slot_to_resource = {
        0: _ir.Resource(
            slot=0, type="TipRack", element_type="TipSpot", is_container=False, is_parameter=True,
            parents=("Deck",), grid=None,
        )
    }
    assert classify_guard_for_call(g, call, slot_to_resource, {}, set()) == REASON_DECIDABLE


def test_classify_decidable_via_param_default() -> None:
    pred = {"node": "Is", "term": _var("target_vols"), "negated": True}  # target_vols is not None
    g = _guard(pred, depth=0)
    call = _call({})
    assert classify_guard_for_call(g, call, {}, {"target_vols": None}, set()) == REASON_DECIDABLE


def test_classify_decidable_via_channel_kwarg() -> None:
    """A depth->=1 guard whose free name IS the receiver's own
    `channel_kwarg` resolves via the channel term, not via call.kwargs.
    """
    pred = {"node": "Is", "term": _var("use_channels"), "negated": True}
    g = _guard(pred, depth=1)
    call = _call({})
    assert (
        classify_guard_for_call(g, call, {}, {}, {"use_channels"}, channel_kwarg="use_channels")
        == REASON_DECIDABLE
    )


def test_classify_env_dependent_depth1_binding_iterand_not_channel() -> None:
    """A depth>=1 alpha binding whose iterand is NOT the receiver's own
    channel_kwarg can never resolve at all (E-CALL(depth)) -- this is the
    `:875` case (`not_containers` bound over `resources`, not
    `use_channels`) -- `guard_env_dependent`, never `guard_operand_unknown`
    on no evidence.
    """
    pred = _cmp(_len(_var("not_containers")), ">", _lit(0))
    binding = {
        "idiom": "alpha",
        "x": "not_containers",
        "iter": "resources",
        "pred": {"node": "Not", "predicate": {"node": "IsInstance", "term": _var("r"), "types": ["Container"]}},
    }
    g = _guard(pred, depth=1, bindings=(binding,))
    call = _call({"resources": _ir.Seq(items=())})
    assert (
        classify_guard_for_call(g, call, {}, {}, {"resources"}, channel_kwarg="use_channels") == REASON_ENV
    )


# ---------------------------------------------------------------------------
# classify_guard_structural -- the no-specific-call block(3) classifier.
# ---------------------------------------------------------------------------


def test_structural_unparsed() -> None:
    g = _guard({"node": "Opaque", "text": "whatever"})
    parsed, bound, reason = classify_guard_structural(g, frozenset(), set())
    assert not parsed
    assert reason == REASON_UNPARSED


def test_structural_bound_and_decidable_or_operand_dependent() -> None:
    pred = _cmp(_len(_var("not_tip_spots")), ">", _lit(0))
    binding = {
        "idiom": "alpha",
        "x": "not_tip_spots",
        "iter": "tip_spots",
        "pred": {"node": "Not", "predicate": {"node": "IsInstance", "term": _var("ts"), "types": ["TipSpot"]}},
    }
    g = _guard(pred, depth=0, bindings=(binding,))
    parsed, bound, reason = classify_guard_structural(g, frozenset({"tip_spots"}), set())
    assert parsed
    assert bound
    assert reason == "decidable_or_operand_dependent"


def test_structural_env_dependent_depth1_non_channel_binding() -> None:
    pred = _cmp(_len(_var("not_containers")), ">", _lit(0))
    binding = {
        "idiom": "alpha",
        "x": "not_containers",
        "iter": "resources",
        "pred": {"node": "Not", "predicate": {"node": "IsInstance", "term": _var("r"), "types": ["Container"]}},
    }
    g = _guard(pred, depth=1, bindings=(binding,))
    parsed, bound, reason = classify_guard_structural(g, frozenset(), {"resources"}, channel_kwarg="use_channels")
    assert parsed
    assert bound
    assert reason == REASON_ENV


def test_structural_unbound_free_local() -> None:
    pred = _cmp(_var("missing"), ">", _lit(0))
    g = _guard(pred, depth=1)
    parsed, bound, reason = classify_guard_structural(g, frozenset(), set())
    assert parsed
    assert not bound
    assert reason == REASON_ENV


# ---------------------------------------------------------------------------
# is_tip_family_owned
# ---------------------------------------------------------------------------


def test_is_tip_family_owned_bool_view_atom() -> None:
    g = _guard({"node": "Opaque", "text": "self.head[channel].has_tip"}, qualname="LiquidHandler.pick_up_tips")
    g["condition"] = "self.head[channel].has_tip"
    receiver_state = {
        "LiquidHandler": {
            "channel_attr": "head",
            "bool_view": {"attr": "has_tip"},
            "state_fields": [],
        }
    }
    assert is_tip_family_owned(g, receiver_state) is True


def test_is_tip_family_owned_false_for_unrelated_condition() -> None:
    g = _guard({"node": "TRUE"}, qualname="LiquidHandler.pick_up_tips")
    g["condition"] = "len(not_tip_spots) > 0"
    receiver_state = {
        "LiquidHandler": {"channel_attr": "head", "bool_view": {"attr": "has_tip"}, "state_fields": []}
    }
    assert is_tip_family_owned(g, receiver_state) is False


def test_is_tip_family_owned_false_when_no_receiver_state() -> None:
    g = _guard({"node": "TRUE"}, qualname="Unrelated.method")
    g["condition"] = "self.head[channel].has_tip"
    assert is_tip_family_owned(g, {}) is False


# ---------------------------------------------------------------------------
# compute_gate -- the GO/NO-GO decision over a synthetic per-op set.
# ---------------------------------------------------------------------------


def test_compute_gate_go_when_one_op_clears() -> None:
    per_op = [
        {"op_id": "op_0", "record_id": "r0", "method": "pick_up_tips", "reasons": [REASON_ENV]},
        {"op_id": "op_1", "record_id": "r1", "method": "pick_up_tips", "reasons": [REASON_UNPARSED]},
    ]
    gate = compute_gate(per_op)
    assert gate["go"] is True
    assert gate["n_ops_clearing"] == 1
    assert gate["methods_clearing"] == ["pick_up_tips"]


def test_compute_gate_no_go_when_every_op_carries_unparsed_or_operand_unknown() -> None:
    per_op = [
        {"op_id": "op_0", "record_id": "r0", "method": "pick_up_tips", "reasons": [REASON_UNPARSED, REASON_ENV]},
        {"op_id": "op_1", "record_id": "r1", "method": "aspirate", "reasons": [REASON_OPERAND]},
    ]
    gate = compute_gate(per_op)
    assert gate["go"] is False
    assert gate["n_ops_clearing"] == 0
    assert gate["methods_clearing"] == []


def test_compute_gate_decidable_alone_clears() -> None:
    per_op = [{"op_id": "op_0", "record_id": "r0", "method": "pick_up_tips", "reasons": [REASON_DECIDABLE]}]
    gate = compute_gate(per_op)
    assert gate["go"] is True
    assert gate["n_ops_clearing"] == 1
