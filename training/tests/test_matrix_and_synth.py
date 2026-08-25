"""Matrix validation + synthesis determinism/conformance tests (deliverable 7)."""

from __future__ import annotations

import json

import pytest
from coxswain.plr.param_namespace import ParamKind, params_of

from floor_gen.matrix import (
    MatrixError,
    cells_round_robin,
    committed_matrix_path,
    load_matrix,
)
from floor_gen.synth import synthesize_example, synthesize_plan
from floor_gen.value_formats import WELL_RE, canonical_volume, canonical_well
from floor_gen.versions import AMBIGUITY_CLASSES


def test_committed_matrix_loads_and_validates():
    matrix = load_matrix(committed_matrix_path())
    classes = {cell.ambiguity_class for cell in matrix.cells}
    assert classes == set(AMBIGUITY_CLASSES)
    # >= 1 cell per class, and the full design is present:
    assert len([c for c in matrix.cells if c.ambiguity_class == "none"]) == 13
    assert len([c for c in matrix.cells if c.ambiguity_class == "missing-slot"]) == 12
    assert len([c for c in matrix.cells if c.ambiguity_class == "ambiguous-referent"]) == 10
    assert len([c for c in matrix.cells if c.ambiguity_class == "out-of-surface"]) >= 1


def test_out_of_surface_cells_never_anchor_included_verbs():
    from coxswain.plr.tool_schema import PHASE2_TOOL_NAMES

    matrix = load_matrix(committed_matrix_path())
    for cell in matrix.cells:
        if cell.ambiguity_class != "out-of-surface":
            continue
        assert cell.verb is None or cell.verb not in PHASE2_TOOL_NAMES
        assert cell.off_surface_request


def test_synthesis_is_deterministic():
    matrix = load_matrix(committed_matrix_path())
    plan_a = [ex.structured_calls for ex in synthesize_plan(matrix)]
    plan_b = [ex.structured_calls for ex in synthesize_plan(matrix)]
    assert plan_a == plan_b
    assert json.dumps(plan_a, sort_keys=True) == json.dumps(plan_b, sort_keys=True)


def test_seed_depends_on_generator_version_and_cell(monkeypatch):
    from floor_gen import synth as synth_mod
    from floor_gen.matrix import MatrixCell

    cell = MatrixCell(cell_id="aspirate__none", verb="aspirate", ambiguity_class="none", examples_per_cell=1)
    ex_a = synth_mod.synthesize_example(cell, 0)
    monkeypatch.setattr(synth_mod, "GENERATOR_VERSION", "9.9.9")
    ex_b = synth_mod.synthesize_example(cell, 0)
    assert ex_a.structured_calls != ex_b.structured_calls


def test_all_examples_conform_to_namespace_table_and_value_formats():
    matrix = load_matrix(committed_matrix_path())
    for example in synthesize_plan(matrix):
        cls = example.cell.ambiguity_class
        if cls == "out-of-surface":
            assert example.structured_calls == ()
            continue
        (call,) = example.structured_calls
        specs = {s.plr_arg or s.name: s for s in params_of(example.cell.verb)}
        extra = set(call["kwargs"]) - set(specs)
        assert not extra, f"{example.seed_key}: kwargs outside table: {extra}"
        for key, value in call["kwargs"].items():
            spec = specs[key]
            if spec.kind is ParamKind.SYMBOLIC_RESOURCE_REF:
                values = value if isinstance(value, list) else [value]
                for element in values:
                    assert isinstance(element, str)
            elif spec.plr_type in ("float", "List[float]", "Optional[List[float]]"):
                elements = value if isinstance(value, list) else [value]
                for element in elements:
                    assert isinstance(element, float), f"volume must be float, got {element!r}"
                    assert element > 0
        # well-shaped strings must be A1-style uppercase
        for key, value in call["kwargs"].items():
            for element in value if isinstance(value, list) else [value]:
                if (
                    isinstance(element, str)
                    and len(element) <= 3
                    and element[:1].upper() in "ABCDEFGH"
                    and element[1:].isdigit()
                ):
                    assert element == element.upper()


def test_class_semantics_via_d11_derivation():
    from coxswain.plr.slot_derivation import derive_call_gaps

    matrix = load_matrix(committed_matrix_path())
    seen_classes = set()
    for example in synthesize_plan(matrix):
        cls = example.cell.ambiguity_class
        seen_classes.add(cls)
        if cls == "out-of-surface":
            continue
        (schema_call,) = example.schema_calls
        gaps = derive_call_gaps(schema_call["name"], schema_call["params"])
        if cls == "none":
            assert not gaps.missing_required
        elif cls == "missing-slot":
            assert example.cell.missing_param in gaps.missing_required
        elif cls == "ambiguous-referent":
            assert any(s.arg_name == example.cell.slot_param for s in gaps.unresolved_slots)
    assert seen_classes == set(AMBIGUITY_CLASSES)


def test_missing_slot_omission_is_total():
    """The designated param is ABSENT (not None): D11 presence-based rule."""
    matrix = load_matrix(committed_matrix_path())
    cell = next(c for c in matrix.cells if c.cell_id == "dispense__missing-slot")
    example = synthesize_example(cell, 0)
    (call,) = example.structured_calls
    assert "vols" not in call["kwargs"]


def test_corpus_b_keyword_style_shapes():
    """Kwarg names follow plr_arg + cardinality: vols=[...], targets=[...]."""
    matrix = load_matrix(committed_matrix_path())
    by_id = {c.cell_id: c for c in matrix.cells}
    transfer = synthesize_example(by_id["transfer__none"], 0)
    (call,) = transfer.structured_calls
    assert call["name"] == "transfer"
    assert isinstance(call["kwargs"]["targets"], list)
    assert all(isinstance(t, str) for t in call["kwargs"]["targets"])
    aspirate = synthesize_example(by_id["aspirate__none"], 0)
    (acall,) = aspirate.structured_calls
    assert isinstance(acall["kwargs"]["vols"], list)
    assert all(isinstance(v, float) for v in acall["kwargs"]["vols"])
    stamp = synthesize_example(by_id["stamp__none"], 0)
    (scall,) = stamp.structured_calls
    assert isinstance(scall["kwargs"]["volume"], float)


def test_cells_round_robin_prefix_spans_all_classes():
    matrix = load_matrix(committed_matrix_path())
    ordered = cells_round_robin(matrix.cells)
    first_four = [cell.ambiguity_class for cell in ordered[:4]]
    assert set(first_four) == set(AMBIGUITY_CLASSES)


def test_value_format_guards_are_loud():
    with pytest.raises(ValueError):
        canonical_well("a63")
    with pytest.raises(ValueError):
        canonical_well("A13")
    assert canonical_well("b12") == "B12"
    with pytest.raises(ValueError):
        canonical_volume(-1.0)
    with pytest.raises(ValueError):
        canonical_volume(0)
    assert canonical_volume(50) == 50.0


def test_corrupt_matrix_fails_loud(tmp_path):
    raw = json.loads(committed_matrix_path().read_text(encoding="utf-8"))
    raw["cells"] = [c for c in raw["cells"] if c["ambiguity_class"] != "out-of-surface"]
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(MatrixError):
        load_matrix(bad)


def test_plan_length_matches_design():
    matrix = load_matrix(committed_matrix_path())
    expected = sum(cell.examples_per_cell for cell in matrix.cells)
    assert len(synthesize_plan(matrix)) == expected
