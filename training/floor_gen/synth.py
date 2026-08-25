"""Structured-call synthesizer (task deliverable 2).

From the canonical namespace table, generate valid call sequences per matrix
cell in CORPUS-B KEYWORD STYLE (recon §3.7: imitate the runnable protocols'
``vols=[...]`` / ``targets=[...]`` kwargs so calls stay execution-verifiable
by the P2.2 harness): kwarg names are the table's ``plr_arg`` column, list
vs scalar follows ``cardinality``, and values obey the pinned value formats.

Determinism: every example's RNG is seeded from
``sha256(GENERATOR_VERSION + "|" + cell_id + "#" + index)`` -- same generator
version + same matrix => identical synthesis, byte for byte, forever.

Each example carries BOTH views:
- ``structured_calls``: corpus-B kwargs (what execution-verify runs),
- ``schema_calls``: schema-side params (the FunctionGemma prediction target)
  with D11 gap fields derived via ``coxswain.plr.slot_derivation`` -- never
  hand-authored.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from typing import Any, Final

from coxswain.plr.param_namespace import (
    ParamKind,
    ParamSpec,
    params_of,
    symbolic_slots,
)
from coxswain.plr.slot_derivation import derive_call_gaps

from floor_gen.matrix import AmbiguityMatrix, MatrixCell
from floor_gen.value_formats import VAGUE_REF_POOLS, canonical_volume, canonical_well
from floor_gen.versions import GENERATOR_VERSION

__all__ = ["SynthExample", "synthesize_cell", "synthesize_plan"]


@dataclass(frozen=True)
class SynthExample:
    """One synthesized pre-teacher example."""

    cell: MatrixCell
    index: int  # within its cell
    #: corpus-B keyword-style calls: [{"name": ..., "kwargs": {...}}]
    structured_calls: tuple[dict[str, Any], ...]
    #: schema-side view: [{"name": ..., "params": {...}}]
    schema_calls: tuple[dict[str, Any], ...]
    #: D11-derived gaps per schema call (missing_required, unresolved_slots).
    derived_missing: tuple[tuple[str, ...], ...]
    derived_slots: tuple[tuple[tuple[str, str, str], ...], ...]

    @property
    def seed_key(self) -> str:
        return f"{self.cell.cell_id}#{self.index}"


# --- deterministic value pools -----------------------------------------------

_PLATE_NAMES: Final[tuple[str, ...]] = ("plate_1", "plate_2")
_LID_NAMES: Final[tuple[str, ...]] = ("lid_1", "lid_2")
_RACK_NAMES: Final[tuple[str, ...]] = ("tip_rack_1", "tip_rack_2")
_RESOURCE_NAMES: Final[tuple[str, ...]] = ("reservoir_1", "hotel_stack_1", "scale_station_1")

_WELL_REFS: Final[tuple[str, ...]] = tuple(
    f"{row}{col}" for row in "ABCDEFGH" for col in range(1, 13)
)

_VOLUME_POOL: Final[tuple[float, ...]] = (10.0, 15.0, 20.0, 25.0, 50.0, 75.0, 100.0, 150.0, 200.0)
_WAVELENGTH_POOL: Final[dict[str, tuple[float, ...]]] = {
    "wavelength_nm": (340.0, 405.0, 450.0, 540.0, 600.0, 650.0),
    "excitation_nm": (485.0, 535.0, 560.0),
    "emission_nm": (520.0, 590.0, 620.0),
}
_FOCAL_HEIGHT_POOL: Final[tuple[float, ...]] = (4.5, 5.0, 7.5, 10.0, 12.5, 15.0)


def _rng(seed_key: str) -> random.Random:
    digest = hashlib.sha256(f"{GENERATOR_VERSION}|{seed_key}".encode("utf-8")).hexdigest()
    return random.Random(int(digest[:16], 16))


def _pick(rng: random.Random, pool: tuple[Any, ...]) -> Any:
    return pool[rng.randrange(len(pool))]


def _grounded_symbolic(rng: random.Random, resource_type: str | None) -> str:
    """A concrete grounding-resolvable name per PLR receiver-side type."""
    if resource_type == "container":
        return f"{_pick(rng, _PLATE_NAMES)}_{canonical_well(_pick(rng, _WELL_REFS))}"
    if resource_type == "plate":
        return _pick(rng, _PLATE_NAMES)
    if resource_type == "lid":
        return _pick(rng, _LID_NAMES)
    if resource_type == "tip_spot":
        return f"{_pick(rng, _RACK_NAMES)}_{canonical_well(_pick(rng, _WELL_REFS))}"
    # resource (ResourceStack / ResourceHolder / Resource / Coordinate refs)
    return _pick(rng, _RESOURCE_NAMES)


def _vague_ref(rng: random.Random, resource_type: str | None) -> str:
    return _pick(rng, VAGUE_REF_POOLS.get(resource_type or "", ("the resource",)))


def _grounded_wells(rng: random.Random, count: int) -> list[str]:
    chosen = rng.sample(list(_WELL_REFS), count)
    return sorted(canonical_well(w) for w in chosen)


def _literal_value(rng: random.Random, spec: ParamSpec) -> Any:
    name = spec.name
    if spec.plr_type == "float":
        if name in _WAVELENGTH_POOL:
            return canonical_volume(_pick(rng, _WAVELENGTH_POOL[name]))
        if name == "focal_height_mm":
            return float(_pick(rng, _FOCAL_HEIGHT_POOL))
        return canonical_volume(_pick(rng, _VOLUME_POOL))
    if spec.plr_type in ("List[float]", "Optional[List[float]]"):
        count = 1 if spec.plr_type.startswith("Optional") else int(rng.choice([1, 2, 3]))
        return [canonical_volume(_pick(rng, _VOLUME_POOL)) for _ in range(count)]
    if spec.plr_type == "Optional[list[str]]":
        # read_*.at: well POSITIONS relative to the loaded plate (literal!).
        return _grounded_wells(rng, int(rng.choice([1, 2, 4])))
    if spec.plr_type == 'Literal["tips"]':
        return "tips"
    if spec.plr_type == "str":
        # discard_tips.at is SYMBOLIC; no literal str rows reach here today.
        raise KeyError(f"unhandled literal str param {name!r}")
    raise KeyError(f"unhandled literal plr_type {spec.plr_type!r}")


def _build_kwargs(cell: MatrixCell, rng: random.Random) -> dict[str, Any]:
    """One call's kwargs in corpus-B style, per class semantics."""
    assert cell.verb is not None
    ambiguous_param = cell.slot_param if cell.ambiguity_class == "ambiguous-referent" else None

    kwargs: dict[str, Any] = {}
    for spec in params_of(cell.verb):
        if cell.ambiguity_class == "missing-slot" and spec.name == cell.missing_param:
            continue  # omitted entirely -> D11 derives missing_required
        key = spec.plr_arg if spec.plr_arg is not None else spec.name

        if spec.kind is ParamKind.SYMBOLIC_RESOURCE_REF and spec.name == ambiguous_param:
            value: Any = _vague_ref(rng, spec.resource_type)
        elif spec.kind is ParamKind.SYMBOLIC_RESOURCE_REF:
            if spec.cardinality == "list":
                value = [_grounded_symbolic(rng, spec.resource_type) for _ in range(rng.choice([1, 1, 2]))]
            else:
                value = _grounded_symbolic(rng, spec.resource_type)
        else:
            value = _literal_value(rng, spec)

        # Optional literals ride along ~half the time to vary surface shape.
        if spec.plr_type.startswith("Optional") and rng.random() < 0.5:
            continue
        kwargs[key] = value
    return kwargs


def _schema_view(tool_name: str, kwargs: dict[str, Any]) -> dict[str, Any]:
    """Invert corpus-B kwargs back to schema-side names via the table."""
    by_kwarg: dict[str, str] = {}
    for spec in params_of(tool_name):
        by_kwarg[spec.plr_arg if spec.plr_arg is not None else spec.name] = spec.name
    return {by_kwarg[key]: value for key, value in kwargs.items()}


def synthesize_example(cell: MatrixCell, index: int) -> SynthExample:
    """Deterministically synthesize ONE example of a matrix cell."""
    if cell.ambiguity_class == "out-of-surface":
        return SynthExample(
            cell=cell,
            index=index,
            structured_calls=(),
            schema_calls=(),
            derived_missing=(),
            derived_slots=(),
        )

    rng = _rng(f"{cell.cell_id}#{index}")
    kwargs = _build_kwargs(cell, rng)
    assert cell.verb is not None
    structured = ({"name": cell.verb, "kwargs": kwargs},)
    schema_params = _schema_view(cell.verb, kwargs)
    gaps = derive_call_gaps(cell.verb, schema_params)

    _assert_class_consistency(cell, kwargs, schema_params, gaps.missing_required, gaps.unresolved_slots)

    return SynthExample(
        cell=cell,
        index=index,
        structured_calls=structured,
        schema_calls=({"name": cell.verb, "params": schema_params},),
        derived_missing=(gaps.missing_required,),
        derived_slots=(
            tuple((s.arg_name, s.reference, s.resource_type) for s in gaps.unresolved_slots),
        ),
    )


def _assert_class_consistency(
    cell: MatrixCell,
    kwargs: dict[str, Any],
    schema_params: dict[str, Any],
    missing: tuple[str, ...],
    slots: tuple[Any, ...],
) -> None:
    """Synthesis self-check: D11 derivation must agree with cell intent."""
    if cell.ambiguity_class == "none":
        if missing:
            raise AssertionError(f"{cell.cell_id}: clean parse derived missing_required={missing}")
    elif cell.ambiguity_class == "missing-slot":
        if cell.missing_param not in missing:
            raise AssertionError(
                f"{cell.cell_id}: expected {cell.missing_param!r} derived missing, got {missing}"
            )
    elif cell.ambiguity_class == "ambiguous-referent":
        slot_names = {s.arg_name for s in slots}
        if cell.slot_param not in slot_names:
            raise AssertionError(
                f"{cell.cell_id}: expected unresolved slot on {cell.slot_param!r}, got {slot_names}"
            )
    del kwargs, schema_params


def synthesize_cell(cell: MatrixCell) -> list[SynthExample]:
    return [synthesize_example(cell, i) for i in range(cell.examples_per_cell)]


def synthesize_plan(matrix: AmbiguityMatrix, cells: tuple[MatrixCell, ...] | None = None) -> list[SynthExample]:
    """Full plan over round-robin-ordered cells (or an explicit selection)."""
    ordered = cells_round_robin_order(matrix) if cells is None else cells
    examples: list[SynthExample] = []
    for cell in ordered:
        examples.extend(synthesize_cell(cell))
    return examples


def cells_round_robin_order(matrix: AmbiguityMatrix):
    from floor_gen.matrix import cells_round_robin

    return cells_round_robin(matrix.cells)
