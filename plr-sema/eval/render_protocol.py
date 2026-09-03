"""Tier-2a source renderer (spec 260903 `260903_plr-sema-real-programs-
increment.md` §12.4.1, backlog #4880): render one executed corpus row's
call sequence to a minimal Python protocol source, faithful enough that
praxis's extractor -> ``lower_graph`` produces the SAME bytecode
``lower_calls`` produces for the same row -- the bytecode differential
``plr-sema/eval/tier2_extractor.py`` runs.

**Resources become typed parameters** of the rendered function, because
``_initialize_resources_from_params``
(``praxis/backend/utils/plr_static_analysis/visitors/computation_graph_extractor.py:278-298``)
is what turns a parameter's type hint into a ``ResourceNode`` -- an
untyped/unparameterized resource is invisible to the extractor. The type
used for each parameter is the REAL PLR class the runtime actually bound
(:func:`oracle_common.resource_type_of`, threaded through
:attr:`oracle_common.RuntimeOutcome.resource_types`), not a guess from
``deck_layout`` -- most referenced resources (the mined utterance's own
plate/tip rack) are never IN ``deck_layout.resources``, which carries only
the scaffolding's OWN additions (e.g. ``prime_plate``); see
:func:`oracle_common.resource_types_from_kwargs`'s own docstring for why.

Each call renders as ``await lh.<method>(<plr_param>=<value>, ...)`` --
PLR method parameter names taken from the bound ``PlanResult.kwargs``, the
SAME dict ``lower_calls`` reads (``oracle_common.calls_from_plr_kwargs``)
-- so the renderer never invents a name and the tool-name barrier
(§11.2.3) is respected by construction, and ALWAYS as a keyword argument
(never positional), which is what lets the extractor's own
``_extract_arguments`` (``arg.keyword.value``) recover the exact PLR param
name rather than falling back to its positional-index heuristic
(``common_arg_names``). The scaffolding reset (§12.1.6) renders as the
literal line ``await lh.setup()``.

A kwarg value the renderer cannot express as Python source (anything
outside ``{lit, ref, seq-of-{lit,ref}}``, or a ``ref`` naming a resource
whose runtime type this module never captured) is DROPPED from the
rendered call and recorded as a :class:`Residual` -- the "renderer"
divergence cause (§12.4.1's table) -- never invented, never silently
coerced to something else.

This module imports nothing from ``praxis`` and nothing from
``plr_sema.check`` -- it consumes and produces plain Python/JSON, matching
the rest of ``plr-sema/eval/``'s import-boundary discipline (AC-12.16).
"""

from __future__ import annotations

import dataclasses
from collections.abc import Mapping
from typing import Any

__all__ = ["Residual", "RenderedProtocol", "render_protocol"]

_RECEIVER_NAME = "lh"
_RECEIVER_TYPE = "LiquidHandler"


@dataclasses.dataclass(frozen=True, slots=True)
class Residual:
    """One kwarg the renderer could not express as Python source."""

    call_index: int
    method: str
    kwarg: str
    reason: str


@dataclasses.dataclass(frozen=True, slots=True)
class RenderedProtocol:
    source: str
    function_name: str
    residuals: tuple[Residual, ...]
    #: call_index (position in the ``calls`` list this was rendered from,
    #: ``0`` == the prepended setup) -> 1-based source line of that call's
    #: ``await lh.<method>(...)`` line, for divergence reports (AC-12.15's
    #: "source line" requirement).
    call_lines: Mapping[int, int]


def _render_lit(v: Any) -> str:
    """A JSON scalar (``None``/``bool``/``int``/``float``/``str``) as a
    Python literal. ``repr`` round-trips all five through ``ast.literal_eval``
    (what ``lower_graph``'s ``_lower_ast_node`` uses on a non-resource,
    non-subscript, non-list/tuple node).
    """
    return repr(v)


def _render_value(value: Mapping[str, Any], *, path: str, reasons: list[str]) -> str | None:
    k = value.get("k") if isinstance(value, Mapping) else None
    if k == "lit":
        return _render_lit(value.get("v"))
    if k == "ref":
        name = value.get("name")
        if not isinstance(name, str) or not name.isidentifier():
            reasons.append(f"{path}: ref name {name!r} is not a renderable Python identifier")
            return None
        cell = value.get("cell")
        return f"{name}[{cell!r}]" if cell is not None else name
    if k == "seq":
        items = value.get("items") or []
        rendered_items: list[str] = []
        for i, item in enumerate(items):
            rendered = _render_value(item, path=f"{path}[{i}]", reasons=reasons)
            if rendered is None:
                return None
            rendered_items.append(rendered)
        return f"[{', '.join(rendered_items)}]"
    reasons.append(f"{path}: unrenderable value kind {k!r} (not lit/ref/seq)")
    return None


def render_protocol(
    calls: list[dict[str, Any]],
    resource_types: Mapping[str, str],
    *,
    function_name: str = "protocol",
) -> RenderedProtocol:
    """Render ``calls`` (:func:`oracle_common.calls_from_plr_kwargs`'s own
    output -- ``calls[0]`` is always the prepended scaffolding ``setup()``,
    §12.1.6) plus ``resource_types``
    (:attr:`oracle_common.RuntimeOutcome.resource_types`) to a minimal
    Python protocol source.

    A resource name referenced by a kwarg ``ref`` but absent from
    ``resource_types`` is treated exactly like any other unrenderable
    value (a residual on that kwarg, not a crash and not a fabricated
    type) -- it simply never becomes a function parameter, so the
    extractor cannot see it as a resource either, which is the correct,
    conservative behaviour: better an honest residual than a guessed type
    that could itself be the source of a spurious divergence.
    """
    params = [f"{_RECEIVER_NAME}: {_RECEIVER_TYPE}"]
    seen_params: set[str] = set()
    for name, cls in resource_types.items():
        if name in seen_params or name == _RECEIVER_NAME:
            continue
        if not name.isidentifier():
            # A real, live deck-layout name (e.g. "plate_carrier-1") that
            # is not a valid Python identifier can never become a function
            # parameter -- declaring it anyway produces a SyntaxError that
            # kills libcst's parse of the WHOLE rendered protocol (found
            # live, 260903 full-corpus run: 95/235 executed rows). Simply
            # not declaring it is enough; every kwarg `ref` naming it is
            # independently caught as its own residual by
            # `_render_value`'s own `.isidentifier()` check below, so no
            # value is silently dropped without a recorded reason.
            continue
        seen_params.add(name)
        params.append(f"{name}: {cls}")

    lines = [f"async def {function_name}({', '.join(params)}):"]
    residuals: list[Residual] = []
    call_lines: dict[int, int] = {}

    for i, call in enumerate(calls):
        method = call.get("method", "")
        if method == "setup":
            call_lines[i] = len(lines) + 1
            lines.append(f"    await {_RECEIVER_NAME}.setup()")
            continue
        kwargs = call.get("kwargs") or {}
        parts: list[str] = []
        for k, v in kwargs.items():
            reasons: list[str] = []
            name = v.get("name") if isinstance(v, Mapping) and v.get("k") == "ref" else None
            if name is not None and name not in resource_types and name != _RECEIVER_NAME:
                residuals.append(
                    Residual(
                        call_index=i, method=method, kwarg=k,
                        reason=f"call[{i}].{method}.{k}: resource {name!r} has no captured "
                                "runtime PLR type (oracle_common.resource_types_from_kwargs)",
                    )
                )
                continue
            rendered = _render_value(v, path=f"call[{i}].{method}.{k}", reasons=reasons)
            if rendered is None:
                residuals.append(
                    Residual(
                        call_index=i, method=method, kwarg=k,
                        reason=reasons[-1] if reasons else "unrenderable",
                    )
                )
                continue
            parts.append(f"{k}={rendered}")
        call_lines[i] = len(lines) + 1
        lines.append(f"    await {_RECEIVER_NAME}.{method}({', '.join(parts)})")

    if len(lines) == 1:
        lines.append("    pass")

    source = "\n".join(lines) + "\n"
    return RenderedProtocol(
        source=source, function_name=function_name,
        residuals=tuple(residuals), call_lines=call_lines,
    )
