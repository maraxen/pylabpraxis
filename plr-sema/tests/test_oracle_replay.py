"""Unit tests for oracle_replay tier 1 (backlog #4879).

Tests the common infrastructure (row_to_verifier_inputs, adapt_graph, compare)
without running the full corpus. Smoke test on training/examples.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from oracle_common import (
    RuntimeOutcome,
    adapt_graph,
    compare,
    row_to_verifier_inputs,
    run_runtime,
    run_static,
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


class TestAdaptGraph:
    """Tests for adapting a call sequence into a graph payload."""

    def test_field_set(self):
        """Verify adapt_graph produces all required fields (mirrors
        fixtures/simple_transfer_graph.json exactly)."""
        example = {
            "call_sequence": [
                {"name": "pick_up_tips", "params": {"at": ["tip_rack.A1"]}},
                {"name": "transfer", "params": {
                    "source": "src.A1",
                    "destination": "dst.B1",
                    "volume_ul": 50,
                }},
            ],
            "deck_layout": {
                "resources": {"tip_rack": "TipRack", "src": "Plate", "dst": "Plate"},
                "seed_volumes": {"src.A1": 100},
            },
        }

        graph = adapt_graph(example, "test.protocol")

        # Check top-level structure
        assert graph["protocol_fqn"] == "test.protocol"
        assert graph["protocol_name"] == "protocol"
        assert graph["has_conditionals"] is False
        assert graph["has_loops"] is False
        assert "operations" in graph
        assert "resources" in graph
        assert "execution_order" in graph
        assert "machine_types" in graph
        assert "resource_types" in graph
        assert "preconditions" in graph

        # Check resource fields match fixture exactly
        for res in graph["resources"].values():
            assert "declared_type" in res
            assert "element_type" in res
            assert "is_container" in res
            assert "is_parameter" in res
            assert "items_x" in res
            assert "items_y" in res
            assert "parental_chain" in res
            assert "source_expression" in res
            assert "variable_name" in res

        # Check operation fields
        for op in graph["operations"]:
            assert "arguments" in op
            assert "condition_expr" in op
            assert "creates_state" in op
            assert "depends_on_params" in op
            assert "false_branch" in op
            assert "foreach_body" in op
            assert "foreach_source" in op
            assert "id" in op
            assert "line_number" in op
            assert "method_name" in op
            assert "node_type" in op
            assert "preconditions" in op
            assert "receiver_type" in op
            assert "receiver_variable" in op
            assert "true_branch" in op


class TestCompare:
    """Tests for soundness comparisons."""

    def test_unsound_safe_raised(self):
        """safe + raised = UNSOUND."""
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
        """safe + ran_ok = sound."""
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
        """unknown + anything = no constraint."""
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
    """Tests for PLR-named argument handling (planned fix)."""

    def test_adapt_graph_with_plr_kwargs(self):
        """adapt_graph uses PLR-named kwargs when available."""
        example = {
            "call_sequence": [
                {"name": "pick_up_tips", "params": {"at": ["tip_rack.A1"]}},
            ],
            "deck_layout": {"resources": {"tip_rack": "TipRack"}},
        }

        # Simulate PLR kwargs (tool "at" param maps to PLR "tip_spots" param)
        plr_kwargs = {
            0: {"tip_spots": "['tip_rack.A1']", "use_channels": "[0]"},
        }

        graph = adapt_graph(example, "test.protocol", plr_kwargs)

        # Operation 0 should have PLR-named arguments
        op0_args = graph["operations"][0]["arguments"]
        # When plr_kwargs provided, those names are used instead of tool names
        if 0 in plr_kwargs:
            assert "tip_spots" in op0_args or "at" in op0_args  # depends on usage
            # In this case, adapt_graph uses plr_kwargs[0] directly
            assert set(op0_args.keys()) >= {"tip_spots", "use_channels"}


class TestSmokeOnExamples:
    """Smoke test: run the full pipeline on training/examples."""

    @pytest.mark.skipif(not EXAMPLES_DIR.exists(), reason="examples dir missing")
    def test_full_pipeline_on_examples(self):
        """Run runtime + static + compare on all examples."""
        contracts_json = CONTRACTS_PATH.read_text()

        results = []
        for example_file in sorted(EXAMPLES_DIR.glob("*.json")):
            example = json.loads(example_file.read_text())
            if "call_sequence" not in example or "intent_record" not in example:
                continue

            rt = run_runtime(example)
            graph = adapt_graph(example, f"training.examples.{example_file.stem}")
            st = run_static(graph, contracts_json)
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
