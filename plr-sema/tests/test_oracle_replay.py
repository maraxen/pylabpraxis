"""Unit tests for oracle_replay tier 1 (backlog #4879).

Tests the common infrastructure (row_to_verifier_inputs, lower_calls-based
static analysis, compare) without running the full corpus. Smoke test on
training/examples.

260902 (spec §11, SEMA-IR): ``adapt_graph`` is deleted. The corpus path now
lowers PLR-named, already-grounded kwargs through
``plr_sema.check.ir.lower_calls`` (``ir_value_of``, ``run_static_calls`` --
see ``oracle_common.py``'s module docstring) instead of adapting a call
sequence into a §6.2 graph payload. ``TestAdaptGraph``/
``TestPLRNamedArguments`` below are rewritten accordingly (renamed to
reflect what they now test).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from oracle_common import (
    RuntimeOutcome,
    _PRIME_PLATE,
    _normalize_well_refs,
    _underscore_ref_base_counts,
    calls_from_plr_kwargs,
    compare,
    ir_value_of,
    param_names_from_contracts,
    resources_from_example,
    row_to_verifier_inputs,
    run_runtime,
    run_static_calls,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "training" / "examples"
CONTRACTS_PATH = REPO_ROOT / "plr-sema" / "data" / "derived_contracts.json"
FIXTURES_DIR = REPO_ROOT / "plr-sema" / "tests" / "fixtures"


class TestRowToVerifierInputs:
    """Tests for parsing corpus rows into verifier inputs."""

    def test_synthetic_chat_row(self):
        """Parse a synthetic chat-format row (single call extracted, scaffolded)."""
        # Note: corpus rows have only 1 call per row; it gets scaffolded
        row = {
            "messages": [
                {"role": "developer", "content": "You are a model..."},
                {"role": "user", "content": "Transfer 50 microliters from A1 to B1"},
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "transfer",
                                "arguments": {
                                    "source": "src.A1",
                                    "destination": "dst.B1",
                                    "volume_ul": 50,
                                },
                            },
                            "type": "function",
                        },
                    ],
                },
            ],
            "tools": [],
            "metadata": "train",
        }

        call_seq, intent, layout, skip_reason, no_call_reason = row_to_verifier_inputs(
            row, source_file="test", line=1
        )

        # Transfer gets scaffolded with one pick_up_tips prefix
        assert len(call_seq) == 2
        assert call_seq[0]["name"] == "pick_up_tips"
        assert call_seq[1]["name"] == "transfer"
        assert intent["record_id"] == "test:1"
        assert intent["utterance"] == "Transfer 50 microliters from A1 to B1"
        assert intent["source"] == "synthetic"
        assert intent["expected_effects"] == []
        assert layout is not None  # scaffold adds seed volumes
        assert "seed_volumes" in layout
        assert "resources" in layout
        assert skip_reason is None  # transfer is executable
        assert no_call_reason is None  # has a tool call

    def test_real_corpus_row(self):
        """Parse the actual first row from corpus_p25.jsonl."""
        corpus_file = REPO_ROOT / "training" / "assemble" / "out" / "corpus_p25.jsonl"
        if not corpus_file.exists():
            pytest.skip("corpus_p25.jsonl not found")

        with open(corpus_file) as f:
            row = json.loads(f.readline())

        call_seq, intent, layout, skip_reason, no_call_reason = row_to_verifier_inputs(
            row, source_file="corpus_p25", line=1
        )

        # Should have extracted a call sequence (or be marked as no_call/skipped)
        assert isinstance(call_seq, list)
        if no_call_reason is None and skip_reason is None:
            assert len(call_seq) > 0
            # Each call should have name and params
            for call in call_seq:
                assert "name" in call
                assert "params" in call
        # Intent record should match the structure
        assert intent["record_id"] == "corpus_p25:1"
        assert intent["source"] == "synthetic"
        assert len(intent["calls"]) == len(call_seq)


class TestIrValueOf:
    """Tests for `ir_value_of` (§11.2.2) -- the harvest-time mapping from a
    bound PLR object to IR value JSON, replacing `adapt_graph`'s old
    `repr`-based harvest.
    """

    def test_scalars_and_none(self):
        assert ir_value_of(100) == {"k": "lit", "v": 100}
        assert ir_value_of(100.0) == {"k": "lit", "v": 100.0}
        assert ir_value_of("A1") == {"k": "lit", "v": "A1"}
        assert ir_value_of(None) == {"k": "lit", "v": None}
        assert ir_value_of(True) == {"k": "lit", "v": True}

    def test_list_lowers_to_seq_of_lits(self):
        assert ir_value_of([1, 2, 3]) == {
            "k": "seq",
            "items": [{"k": "lit", "v": 1}, {"k": "lit", "v": 2}, {"k": "lit", "v": 3}],
        }

    def test_unresolvable_object_is_top(self):
        class _Opaque:
            pass

        assert ir_value_of(_Opaque()) == {"k": "top"}

    def test_plr_resource_with_parent_is_name_keyed_ref(self):
        from pylabrobot.resources import Coordinate, Plate, Well

        plate = Plate(
            "plate_1", size_x=10, size_y=10, size_z=10, ordered_items={},
        )
        well = Well("well_1", size_x=1, size_y=1, size_z=1)
        plate.assign_child_resource(well, location=Coordinate.zero())
        value = ir_value_of(well)
        assert value == {"k": "ref", "name": "plate_1", "cell": "well_1"}

    def test_plr_top_level_resource_is_ref_with_no_cell(self):
        from pylabrobot.resources import Plate

        plate = Plate("plate_2", size_x=10, size_y=10, size_z=10, ordered_items={})
        value = ir_value_of(plate)
        assert value == {"k": "ref", "name": "plate_2", "cell": None}


class TestResourcesAndCallsFromExample:
    """Tests for `resources_from_example`/`calls_from_plr_kwargs` -- the
    `lower_calls`-path replacements for `adapt_graph`.
    """

    def test_resources_from_example_field_set(self):
        example = {
            "deck_layout": {
                "resources": {"tip_rack": "TipRack", "src": "Plate", "dst": "Plate"},
            },
        }
        resources = resources_from_example(example)
        assert resources["lh"]["type"] == "LiquidHandler"
        assert resources["tip_rack"]["type"] == "TipRack"
        assert resources["src"]["type"] == "Plate"
        assert resources["dst"]["type"] == "Plate"
        for decl in resources.values():
            assert "is_container" in decl
            assert "is_parameter" in decl
            assert "parents" in decl

    def test_calls_from_plr_kwargs_skips_not_planned(self):
        example = {
            "call_sequence": [
                {"name": "pick_up_tips", "params": {"at": ["tip_rack.A1"]}},
                {"name": "transfer", "params": {"source": "src.A1", "destination": "dst.B1", "volume_ul": 50}},
            ],
        }
        plr_kwargs = {0: {"tip_spots": {"k": "seq", "items": [{"k": "ref", "name": "tip_rack", "cell": "A1"}]}}}
        calls, not_planned = calls_from_plr_kwargs(example, plr_kwargs)
        assert not_planned == [1]
        assert len(calls) == 1
        assert calls[0]["method"] == "pick_up_tips"
        assert calls[0]["kwargs"] == plr_kwargs[0]
        assert calls[0]["receiver"] == "lh"
        assert calls[0]["receiver_type"] == "LiquidHandler"


class TestCompare:
    """Tests for soundness comparisons."""

    def test_unsound_safe_raised(self):
        """Safe + raised = UNSOUND."""
        example = {
            "call_sequence": [{"name": "pick_up_tips", "params": {"at": ["tr.A1"]}}],
            "intent_record": {},
        }
        rt = RuntimeOutcome(
            error="NoTipError: no tip mounted",
            exc_class="NoTipError",
            failing_index=0,
            planned_indices=[0],
            passed=False,
        )
        st = {
            "op_0": {
                "verdict": "safe",
                "n_findings": 0,
                "reasons": [],
            }
        }

        rows = compare(example, rt, st)
        assert len(rows) == 1
        assert rows[0]["unsound"] is True

    def test_unsound_willfail_ran_ok(self):
        """will_fail + ran_ok = UNSOUND."""
        example = {
            "call_sequence": [{"name": "aspirate", "params": {"source": "p.A1", "volume_ul": 50}}],
            "intent_record": {},
        }
        rt = RuntimeOutcome(
            error=None,
            exc_class=None,
            failing_index=None,
            planned_indices=[0],
            passed=True,
        )
        st = {
            "op_0": {
                "verdict": "will_fail",
                "n_findings": 1,
                "reasons": ["too_much_volume"],
            }
        }

        rows = compare(example, rt, st)
        assert len(rows) == 1
        assert rows[0]["unsound"] is True

    def test_sound_safe_ran_ok(self):
        """Safe + ran_ok = sound."""
        example = {
            "call_sequence": [{"name": "move_plate", "params": {"plate": "p1", "to": "l1"}}],
            "intent_record": {},
        }
        rt = RuntimeOutcome(
            error=None,
            exc_class=None,
            failing_index=None,
            planned_indices=[0],
            passed=True,
        )
        st = {
            "op_0": {
                "verdict": "safe",
                "n_findings": 0,
                "reasons": [],
            }
        }

        rows = compare(example, rt, st)
        assert len(rows) == 1
        assert rows[0]["unsound"] is False

    def test_unknown_no_constraint(self):
        """Unknown + anything = no constraint."""
        example = {
            "call_sequence": [{"name": "some_op", "params": {}}],
            "intent_record": {},
        }
        rt = RuntimeOutcome(
            error="SomeError: message",
            exc_class="SomeError",
            failing_index=0,
            planned_indices=[0],
            passed=False,
        )
        st = {
            "op_0": {
                "verdict": "unknown",
                "n_findings": 5,
                "reasons": ["some_reason"],
            }
        }

        rows = compare(example, rt, st)
        assert len(rows) == 1
        assert rows[0]["unsound"] is False


class TestRowCategories:
    """Tests for row categorization: no_call, skipped, executed."""

    def test_no_call_row(self):
        """Clarification turn with no tool_calls."""
        row = {
            "messages": [
                {"role": "user", "content": "What's the tip height?"},
                {"role": "assistant", "content": "The tip height is 10mm."},
            ],
            "tools": [],
            "metadata": "train",
        }

        call_seq, intent, layout, skip_reason, no_call_reason = row_to_verifier_inputs(
            row, source_file="test", line=1
        )

        assert no_call_reason == "no_tool_calls"
        assert skip_reason is None
        assert len(call_seq) == 0
        assert intent["calls"] == []

    def test_skipped_row(self):
        """Call that _precondition_plan refuses (e.g., transfer without volume_ul)."""
        row = {
            "messages": [
                {"role": "user", "content": "Transfer from A1 to B1"},
                {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "transfer",
                                "arguments": {
                                    "source": "src.A1",
                                    "destination": "dst.B1",
                                    # missing volume_ul
                                },
                            },
                            "type": "function",
                        },
                    ],
                },
            ],
            "tools": [],
            "metadata": "train",
        }

        call_seq, intent, layout, skip_reason, no_call_reason = row_to_verifier_inputs(
            row, source_file="test", line=1
        )

        assert no_call_reason is None
        assert skip_reason is not None  # transfer without volume_ul is skipped
        assert len(call_seq) == 0


class TestPLRNamedArguments:
    """Tests for PLR-named argument handling through the lower_calls path
    (§11.2.2/§11.2.4) -- the direct successor to adapt_graph's old
    plr_kwargs handling, now via run_static_calls + lower_calls's trust
    rule rather than a graph payload's `arguments` dict.
    """

    def test_run_static_calls_uses_plr_named_kwargs(self):
        """A planned call's IR-value-JSON kwargs (PLR-named by
        construction, §11.2.2) reach `lower_calls`; a real PLR parameter
        name is trusted and surfaces in the CALL's kwargs unmangled when
        `param_names` covers it.
        """
        example = {
            "call_sequence": [
                {"name": "pick_up_tips", "params": {"at": ["tip_rack.A1"]}},
            ],
            "deck_layout": {"resources": {"tip_rack": "TipRack"}},
        }
        plr_kwargs = {
            0: {
                "tip_spots": {"k": "seq", "items": [{"k": "ref", "name": "tip_rack", "cell": "A1"}]},
                "use_channels": {"k": "seq", "items": [{"k": "lit", "v": 0}]},
            },
        }
        contracts_json = json.dumps(
            {
                "contracts": {
                    "LiquidHandler.pick_up_tips": {
                        "guards": [],
                        "gaps": [],
                        "params": ["tip_spots", "use_channels"],
                    }
                }
            }
        )
        param_names = param_names_from_contracts(contracts_json)
        st, not_planned = run_static_calls(example, plr_kwargs, contracts_json, param_names=param_names)
        assert not_planned == []
        assert st["op_0"]["verdict"] == "unknown"
        # zero guards/zero gaps/no loop -> the totality fallback finding.
        assert "no_contract_derived" in st["op_0"]["reasons"]

    def test_run_static_calls_not_planned_index_gets_empty_entry(self):
        example = {
            "call_sequence": [
                {"name": "pick_up_tips", "params": {"at": ["tip_rack.A1"]}},
                {"name": "transfer", "params": {"source": "src.A1", "destination": "dst.B1", "volume_ul": 50}},
            ],
        }
        plr_kwargs = {0: {"tip_spots": {"k": "seq", "items": []}}}
        contracts_json = json.dumps({"contracts": {}})
        st, not_planned = run_static_calls(example, plr_kwargs, contracts_json)
        assert not_planned == [1]
        assert st["op_1"] == {"verdict": "unknown", "n_findings": 0, "reasons": []}


class TestT16dSidecarGating:
    """Regression tests for the T16d (#4879) root-cause fixes: ambiguity_class
    gating, move_*/holders wiring, and naturalness mined-call normalization.
    Each test replays a REAL joined corpus row (by line number, verified
    260902) and asserts our outcome now matches P2.5's recorded outcome.
    """

    CORPUS_FILE = REPO_ROOT / "training" / "assemble" / "out" / "corpus_p25.jsonl"
    SIDECAR_FILE = REPO_ROOT / "training" / "assemble" / "out" / "corpus_p25_sidecar.jsonl"
    FLOOR_FILE = REPO_ROOT / "training" / "out" / "corpus_p23_floor.jsonl"
    OVERLAY_FILE = REPO_ROOT / "training" / "overlay_gen" / "out" / "overlay_full.jsonl"

    @staticmethod
    def _row_and_sidecar(line_no: int):
        with open(TestT16dSidecarGating.CORPUS_FILE) as f:
            corpus_line = f.readlines()[line_no - 1]
        with open(TestT16dSidecarGating.SIDECAR_FILE) as f:
            sidecar_line = f.readlines()[line_no - 1]
        return json.loads(corpus_line), json.loads(sidecar_line)

    def _require_files(self):
        for p in (self.CORPUS_FILE, self.SIDECAR_FILE):
            if not p.exists():
                pytest.skip(f"{p} not found")

    def test_missing_slot_dispense_is_skipped_not_keyerror(self):
        """cov-0080-dispense__missing-slot-00 (line 59): dispense with
        volume_ul deliberately omitted. Pre-fix, _precondition_plan indexed
        params["volume_ul"] unconditionally and KeyError-crashed (17 rows,
        all missing_slot). floor_gen never reaches _precondition_plan for
        non-"none" ambiguity classes (exec_verify.py cls != "none" gate) --
        floor's own record has execution_verify=None (never executed,
        verified 260902). Post-fix: skipped before _precondition_plan runs,
        no exception.
        """
        self._require_files()
        row, srow = self._row_and_sidecar(59)
        assert srow["record_id"] == "cov-0080-dispense__missing-slot-00"
        call_seq, intent, layout, skip_reason, no_call_reason = row_to_verifier_inputs(
            row, source_file="corpus_p25", line=59,
            ambiguity_class=srow["ambiguity_class"], sidecar_record_id=srow["record_id"],
            provenance=srow["provenance"],
        )
        assert no_call_reason is None
        assert skip_reason is not None
        assert "missing_slot" in skip_reason
        assert call_seq == []

    def test_ambiguous_referent_aspirate_is_skipped(self):
        """cov-0030-aspirate__ambiguous-referent-00 (line 21): a
        deliberately-vague ref. Pre-fix, this executed and usually raised
        GroundingError (spurious -- floor_gen's own harness never runs
        ambiguous-referent cells at all). Post-fix: skipped.
        """
        self._require_files()
        row, srow = self._row_and_sidecar(21)
        assert srow["record_id"] == "cov-0030-aspirate__ambiguous-referent-00"
        call_seq, intent, layout, skip_reason, no_call_reason = row_to_verifier_inputs(
            row, source_file="corpus_p25", line=21,
            ambiguity_class=srow["ambiguity_class"], sidecar_record_id=srow["record_id"],
            provenance=srow["provenance"],
        )
        assert no_call_reason is None
        assert skip_reason is not None
        assert "ambiguous_referent" in skip_reason
        assert call_seq == []

    def test_move_resource_holders_fix_matches_p25_passed(self):
        """cov-0455-move_resource__none-00 (line 396): "Move hotel_stack_1
        to reservoir_1." Pre-fix, oracle_common never computed
        DeckLayout.holders, so infer_layout() defaulted both names to a bare
        Plate and PLR raised "RuntimeError: Can only drop Lid resources onto
        Plate 'reservoir_1'." on every move_resource/move_plate/move_lid row
        (45/45 crosscheck disagreements against floor, all this one shape).
        floor_gen.exec_verify computes holders via _resource_type_holders
        (exec_verify.py:126-145); oracle_common now mirrors it. P2.5 recorded
        passed=True for this record_id; assert we now agree.
        """
        self._require_files()
        if not self.FLOOR_FILE.exists():
            pytest.skip(f"{self.FLOOR_FILE} not found")
        row, srow = self._row_and_sidecar(396)
        assert srow["record_id"] == "cov-0455-move_resource__none-00"
        call_seq, intent, layout, skip_reason, no_call_reason = row_to_verifier_inputs(
            row, source_file="corpus_p25", line=396,
            ambiguity_class=srow["ambiguity_class"], sidecar_record_id=srow["record_id"],
            provenance=srow["provenance"],
        )
        assert skip_reason is None and no_call_reason is None
        assert layout is not None and layout.get("holders") == ["hotel_stack_1", "reservoir_1"]
        rt = run_runtime({"call_sequence": call_seq, "intent_record": intent, "deck_layout": layout})
        with open(self.FLOOR_FILE) as f:
            floor_by_id = {json.loads(l)["record_id"]: json.loads(l) for l in f}
        p25_row = floor_by_id[srow["record_id"]]
        p25_passed = p25_row["execution_verify"]["passed"]
        assert p25_passed is True
        assert rt.error is None, f"expected ran_ok (matches P2.5 passed={p25_passed}), got {rt.error!r}"

    def test_naturalness_ungroundable_mined_expr_is_skipped(self):
        """ovl-0740a87130 (line 716): pick_up_tips at a loop-variable slice
        (source_tip_spots[i:i + batch_size]) -- not a literal, statically
        groundable ref. overlay_gen's own harness never executes this
        (execution_verify=None, confirmed 260902); pre-fix, oracle_common fed
        the raw expression straight into the dispatcher. Post-fix: skipped
        via overlay_gen._normalize_params, matching overlay_gen's own gate.
        """
        self._require_files()
        row, srow = self._row_and_sidecar(716)
        assert srow["record_id"] == "ovl-0740a87130"
        assert srow["provenance"] == "naturalness"
        call_seq, intent, layout, skip_reason, no_call_reason = row_to_verifier_inputs(
            row, source_file="corpus_p25", line=716,
            ambiguity_class=srow["ambiguity_class"], sidecar_record_id=srow["record_id"],
            provenance=srow["provenance"],
        )
        assert no_call_reason is None
        assert skip_reason is not None
        assert "variable/computed value" in skip_reason
        assert call_seq == []

    def test_naturalness_bracket_ref_normalizes_and_matches_p25_passed(self):
        """ovl-05a03ba41d (line 715): dispense(destination='plate["C1"]', ...)
        -- a literal bracket-subscript mined ref. Pre-fix, this opaque
        un-normalized name typed as a bare Plate via infer_layout, producing
        "'Plate' object has no attribute 'tracker'" / TypeError (the
        remaining naturalness disagreement classes). Post-fix: normalized to
        'plate.C1' via overlay_gen._normalize_ref before _precondition_plan,
        matching overlay_gen's own execution_verify_call. overlay recorded
        passed=True for this id; assert we now agree.
        """
        self._require_files()
        if not self.OVERLAY_FILE.exists():
            pytest.skip(f"{self.OVERLAY_FILE} not found")
        row, srow = self._row_and_sidecar(715)
        assert srow["record_id"] == "ovl-05a03ba41d"
        call_seq, intent, layout, skip_reason, no_call_reason = row_to_verifier_inputs(
            row, source_file="corpus_p25", line=715,
            ambiguity_class=srow["ambiguity_class"], sidecar_record_id=srow["record_id"],
            provenance=srow["provenance"],
        )
        assert skip_reason is None and no_call_reason is None
        dispense_call = [c for c in call_seq if c["name"] == "dispense"][0]
        assert dispense_call["params"]["destination"] == "plate.C1"
        rt = run_runtime({"call_sequence": call_seq, "intent_record": intent, "deck_layout": layout})
        with open(self.OVERLAY_FILE) as f:
            overlay_by_id = {json.loads(l)["id"]: json.loads(l) for l in f}
        p25_row = overlay_by_id[srow["record_id"]]
        p25_passed = p25_row["execution_verify"]["passed"]
        assert p25_passed is True
        assert rt.error is None, f"expected ran_ok (matches overlay passed={p25_passed}), got {rt.error!r}"


class TestSmokeOnExamples:
    """Smoke test: run the full pipeline on training/examples."""

    @pytest.mark.skipif(not EXAMPLES_DIR.exists(), reason="examples dir missing")
    def test_full_pipeline_on_examples(self):
        """Run runtime + static (lower_calls + check_ir, §11.2.2) + compare
        on all examples.
        """
        contracts_json = CONTRACTS_PATH.read_text()
        param_names = param_names_from_contracts(contracts_json)

        results = []
        for example_file in sorted(EXAMPLES_DIR.glob("*.json")):
            example = json.loads(example_file.read_text())
            if "call_sequence" not in example or "intent_record" not in example:
                continue

            rt = run_runtime(example)
            st, not_planned = run_static_calls(example, rt.plr_kwargs, contracts_json, param_names=param_names)
            assert not_planned == [], f"{example_file.name}: unexpected not-planned indices {not_planned}"
            rows = compare(example, rt, st)

            results.append({
                "file": example_file.name,
                "n_ops": len(rows),
                "unsound": sum(r["unsound"] for r in rows),
                "rows": rows,
            })

        # Per spike output: 4 examples, 10 ops, 0 unsound
        assert len(results) == 4
        assert sum(r["n_ops"] for r in results) == 10
        assert sum(r["unsound"] for r in results) == 0


def _chat_row(name: str, arguments: dict, utterance: str = "test utterance") -> dict:
    """Minimal chat-format corpus row with one tool call (corpus_p25.jsonl shape)."""
    return {
        "messages": [
            {"role": "developer", "content": "sys"},
            {"role": "user", "content": utterance},
            {
                "role": "assistant",
                "tool_calls": [
                    {"function": {"name": name, "arguments": arguments}, "type": "function"},
                ],
            },
        ],
        "tools": [],
        "metadata": "train",
    }


class TestUnderscoreRefBaseCounts:
    """Tests for _underscore_ref_base_counts (§12.4.3's self-consistency signal)."""

    def test_repeated_base_counted(self):
        counts = _underscore_ref_base_counts(
            {"at": ["filter_tip_box_D1", "filter_tip_box_D2", "filter_tip_box_D3"]}
        )
        assert counts["filter_tip_box"] == 3

    def test_distinct_bases_each_counted_once(self):
        counts = _underscore_ref_base_counts(
            {"source": "plate_A_H12", "destination": "plate_B_A1"}
        )
        assert counts == {"plate_A": 1, "plate_B": 1}

    def test_non_matching_shape_not_counted(self):
        # "col1"/"slot2" have no A-H row letter -- not a well-ref shape at all.
        counts = _underscore_ref_base_counts(
            {"destination": "assay_plate_col1", "other": "disposal_rack_slot2"}
        )
        assert counts == {}


class TestNormalizeWellRefs:
    """Tests for _normalize_well_refs (§12.4.3, AC-12.19)."""

    def test_declared_via_precondition_plan_resources_normalizes(self):
        """AC-12.19's worked example, using the ONE base _precondition_plan
        actually declares (``_PRIME_PLATE``): a dispense whose destination
        happens to share that base normalises and its skip_reason stays
        None (dispense is executable either way -- the point is the REF
        got rewritten before _precondition_plan/deck_layout ever saw it).
        """
        ref = f"{_PRIME_PLATE}_A1"
        call = {"name": "dispense", "params": {"destination": ref, "volume_ul": 50}}
        new_call, rewritten = _normalize_well_refs(call)
        assert rewritten == [ref]
        assert new_call["params"]["destination"] == f"{_PRIME_PLATE}.A1"
        # Original call object is untouched (defensive copy, not a mutation).
        assert call["params"]["destination"] == ref

    def test_self_consistent_repeat_normalizes(self):
        """4 tip-spot refs in one pick_up_tips.at list, all on the same
        undeclared base -- internal repetition is its own declaration
        (§12.4.3(b))."""
        call = {
            "name": "pick_up_tips",
            "params": {"at": ["filter_tip_box_D1", "filter_tip_box_D2"]},
        }
        new_call, rewritten = _normalize_well_refs(call)
        assert sorted(rewritten) == ["filter_tip_box_D1", "filter_tip_box_D2"]
        assert new_call["params"]["at"] == ["filter_tip_box.D1", "filter_tip_box.D2"]

    def test_undeclared_single_occurrence_left_verbatim(self):
        """AC-12.19's contrast case: foo_A1 with no foo declared anywhere
        (not in _precondition_plan's resources, not repeated) stays
        exactly as it is."""
        call = {"name": "aspirate", "params": {"source": "foo_A1", "volume_ul": 10}}
        new_call, rewritten = _normalize_well_refs(call)
        assert rewritten == []
        assert new_call is call  # identical object, not even a copy
        assert new_call["params"]["source"] == "foo_A1"

    def test_non_well_shaped_ref_left_untouched(self):
        call = {"name": "drop_tips", "params": {"destination": "trash"}}
        new_call, rewritten = _normalize_well_refs(call)
        assert rewritten == []
        assert new_call["params"]["destination"] == "trash"


class TestRowToVerifierInputsNormalization:
    """Integration tests: §12.4.3's normalisation wired into
    row_to_verifier_inputs (AC-12.19)."""

    def test_declared_base_resolves_and_executes(self):
        ref = f"{_PRIME_PLATE}_A1"
        row = _chat_row("dispense", {"destination": ref, "volume_ul": 50})
        call_seq, intent, layout, skip_reason, no_call_reason = row_to_verifier_inputs(
            row, source_file="test", line=1
        )
        assert no_call_reason is None
        assert skip_reason is None
        assert intent["normalized_refs"] == [ref]
        real_call = call_seq[-1]
        assert real_call["name"] == "dispense"
        assert real_call["params"]["destination"] == f"{_PRIME_PLATE}.A1"

    def test_undeclared_base_left_verbatim_keeps_current_outcome(self):
        row = _chat_row("aspirate", {"source": "foo_A1", "volume_ul": 10})
        call_seq, intent, layout, skip_reason, no_call_reason = row_to_verifier_inputs(
            row, source_file="test", line=1
        )
        assert no_call_reason is None
        assert skip_reason is None  # aspirate has everything _precondition_plan needs
        assert intent["normalized_refs"] == []
        real_call = call_seq[-1]
        assert real_call["params"]["source"] == "foo_A1"  # untouched

    def test_no_call_row_has_no_normalized_refs(self):
        row = {
            "messages": [
                {"role": "developer", "content": "sys"},
                {"role": "user", "content": "what can you do?"},
                {"role": "assistant", "content": "I can pipette."},
            ],
            "tools": [],
            "metadata": "train",
        }
        call_seq, intent, layout, skip_reason, no_call_reason = row_to_verifier_inputs(
            row, source_file="test", line=1
        )
        assert no_call_reason == "no_tool_calls"
        assert intent["normalized_refs"] == []


class TestByteIdentityInvariant:
    """AC-12.19: grounding.py and every file under training/assemble/out/
    are byte-identical before and after normalisation -- this is a LOADER
    reading of an ambiguous ref, not a corpus/grounding-grammar rewrite.
    """

    def _tracked_files(self) -> list[Path]:
        grounding = REPO_ROOT / "training" / "verify" / "grounding.py"
        assemble_out = REPO_ROOT / "training" / "assemble" / "out"
        files = [grounding]
        if assemble_out.is_dir():
            files.extend(sorted(p for p in assemble_out.rglob("*") if p.is_file()))
        return files

    def _hashes(self, files: list[Path]) -> dict[str, str]:
        return {
            str(f): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in files
            if f.exists()
        }

    def test_normalization_does_not_touch_grounding_or_assemble_out(self):
        files = self._tracked_files()
        assert files, "expected grounding.py + training/assemble/out/* to exist"
        before = self._hashes(files)

        # Exercise every normalisation path: declared-via-resources,
        # self-consistent repeat, and undeclared/verbatim -- plus a full
        # row_to_verifier_inputs pass, so any accidental write during
        # normalisation would be caught here.
        _normalize_well_refs(
            {"name": "dispense", "params": {"destination": f"{_PRIME_PLATE}_A1", "volume_ul": 50}}
        )
        _normalize_well_refs(
            {"name": "pick_up_tips", "params": {"at": ["filter_tip_box_D1", "filter_tip_box_D2"]}}
        )
        _normalize_well_refs({"name": "aspirate", "params": {"source": "foo_A1", "volume_ul": 10}})
        row_to_verifier_inputs(
            _chat_row("dispense", {"destination": f"{_PRIME_PLATE}_A1", "volume_ul": 50}),
            source_file="test", line=1,
        )

        after = self._hashes(self._tracked_files())
        assert after == before
