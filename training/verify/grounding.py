"""Reference-string grounding for the P2.2 verify harness.

Grammar (the harness-side twin of cue-2 grounding; deterministic):

* ``<name>``              whole deck resource (plate, holder, rack)
* ``<name>.<id>``         one well / tip spot, ALWAYS returned as a 1-list
                          (vendored ItemizedResource.__getitem__ returns lists
                          even for single identifiers)
* ``<name>.<id>:<id2>``   vendored slice semantics -- END-EXCLUSIVE, column
                          major (verified against hamilton_96_tiprack:
                          ``["A1":"H1"]`` yields A1..G1). Prefer explicit
                          identifier lists in fixtures for readability.
* ``{"x":..,"y":..,"z":..}`` structured Coordinate payload -> grounded
                          literal (param_namespace note on move destinations).

Every grounding is recorded as a :class:`Binding` -- the evidence row used by
the slot-agreement check ("every grounded arg in the executed call").
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

__all__ = ["Binding", "GroundingError", "canonical_ref", "ground_ref", "ground_param"]


class GroundingError(KeyError):
    """A reference could not be resolved against the live deck."""


@dataclass(frozen=True)
class Binding:
    """One grounded argument of one executed call."""

    call_index: int
    tool: str
    arg: str          # canonical schema-side param name
    plr_arg: str | None  # vendored kwarg it was dispatched under (None = inert)
    ref: str          # the reference/value as written in the call
    kind: str         # "symbolic" | "literal"
    resolved: str     # human-readable resolution evidence


def ground_ref(ref: str, setup) -> list[Any]:
    """Resolve a ref string to a LIST of PLR objects against a SetupHandle."""
    if not isinstance(ref, str) or not ref.strip():
        raise GroundingError(f"invalid ref {ref!r}")
    base, _, tail = ref.partition(".")
    if base not in setup.resources:
        raise GroundingError(
            f"resource {base!r} not on deck (have: {sorted(setup.resources)})"
        )
    obj = setup.resources[base]
    if not tail:
        return [obj]
    # Well/spot addressing: single id or end-exclusive slice (vendored rules).
    first, sep, second = tail.partition(":")
    try:
        items = obj[first.strip():second.strip()] if sep else obj[first.strip()]
    except Exception as e:  # PLR raises ValueError/KeyError variants
        raise GroundingError(f"cannot address {ref!r} on {base!r}: {e}") from e
    return list(items)


def canonical_ref(ref: str) -> str:
    """Normalized form used when comparing executed vs intended bindings."""
    return " ".join(ref.split())


def _coordinate(value: Mapping[str, Any]) -> Any:
    from pylabrobot.resources import Coordinate

    return Coordinate(float(value["x"]), float(value["y"]), float(value["z"]))


def ground_param(call_index: int, tool: str, arg: str, plr_arg: str | None,
                 value: Any, kind: str, setup) -> tuple[Any, Binding]:
    """Ground ONE parameter value; returns (objects_or_value, binding).

    Symbolic values are ref strings/lists-of-refs and ground into PLR objects.
    Literal values pass through untouched.  Structured Coordinate payloads on
    symbolic params count as grounded literals (recorded convention).
    """
    if kind == "literal":
        return value, Binding(call_index, tool, arg, plr_arg,
                              canonical_ref(str(value)), "literal",
                              f"literal value {value!r}")
    if isinstance(value, Mapping):
        if {"x", "y", "z"} <= set(value.keys()):
            return _coordinate(value), Binding(
                call_index, tool, arg, plr_arg, canonical_ref(str(sorted(value.items()))),
                "literal", f"Coordinate payload -> {_coordinate(value)!r}")
        raise GroundingError(f"{tool}.{arg}: unsupported mapping payload {value!r}")

    refs = value if isinstance(value, list) else [value]
    grounded: list[Any] = []
    seen: list[str] = []
    for r in refs:
        if not isinstance(r, str):
            raise GroundingError(f"{tool}.{arg}: symbolic value must be ref string(s), got {r!r}")
        grounded.extend(ground_ref(r, setup))
        seen.append(canonical_ref(r))
    binding = Binding(call_index, tool, arg, plr_arg, ", ".join(seen), "symbolic",
                      f"{len(grounded)} object(s): {[getattr(g, 'name', type(g).__name__) for g in grounded]}")
    return grounded, binding
