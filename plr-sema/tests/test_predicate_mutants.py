"""Unit tests for plr-sema/eval/predicate_mutants.py (spec 260904 §15.10,
backlog #4979, T32).

Synthetic and fast: the three mutator functions are pure (`dict[str, Any] ->
bool`, mutating in place) and are tested directly with no PLR/asyncio
involvement. One lightweight end-to-end test runs the real
`run_one_predicate_mutant` pipeline against the repo's own tiny tip fixture
(`plr-sema/eval/fixtures/tip_mutant_probe.json`) to pin the CURRENT,
MEASURED behaviour end to end -- see its own docstring for why "0 achieved"
is the CORRECT pinned expectation, not a bug this test is failing to catch.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "eval"))

from predicate_mutants import (  # noqa: E402
    _EXPECTED_EXC,
    _MUTATORS,
    _ZERO_ACHIEVED_EXPECTED,
    make_p1a_duplicate_use_channels,
    make_p1b_short_offsets,
    make_p1c_non_tipspot_element,
    run_one_predicate_mutant,
)
from tip_mutants import _example_files  # noqa: E402
import oracle_common as oc  # noqa: E402

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "eval" / "fixtures"
CONTRACTS_PATH = Path(__file__).resolve().parents[1] / "data" / "derived_contracts.json"


class TestMutatorTable:
    def test_three_mutators_registered(self):
        assert set(_MUTATORS) == {
            "p1a_duplicate_use_channels",
            "p1b_short_offsets",
            "p1c_non_tipspot_element",
        }

    def test_expected_exceptions_named_per_mutator(self):
        assert _EXPECTED_EXC == {
            "p1a_duplicate_use_channels": "AssertionError",
            "p1b_short_offsets": "AssertionError",
            "p1c_non_tipspot_element": "TypeError",
        }

    def test_only_c_is_zero_achieved_expected(self):
        """§15.10's own restated-E-TYPE prediction: (c) alone is asserted
        0 achieved / 0 unsound; the >= 1 floor is carried by (a)/(b)."""
        assert _ZERO_ACHIEVED_EXPECTED == {"p1c_non_tipspot_element"}


class TestMakeP1aDuplicateUseChannels:
    def test_always_constructible_and_sets_duplicate(self):
        kwargs = {"tip_spots": ["a", "b", "c"]}
        assert make_p1a_duplicate_use_channels(kwargs) is True
        assert kwargs["use_channels"] == [0, 0]

    def test_constructible_even_with_one_tip_spot(self):
        """The guard `:502`'s
        `len(set(use_channels)) == len(use_channels)` is a pure
        self-uniqueness test over `use_channels`, independent of
        `tip_spots` -- this mutator never declines."""
        kwargs = {"tip_spots": ["only_one"]}
        assert make_p1a_duplicate_use_channels(kwargs) is True
        assert kwargs["use_channels"] == [0, 0]

    def test_constructible_with_no_tip_spots_key_at_all(self):
        kwargs = {}
        assert make_p1a_duplicate_use_channels(kwargs) is True
        assert kwargs["use_channels"] == [0, 0]


class TestMakeP1bShortOffsets:
    def test_declines_with_fewer_than_two_tip_spots(self):
        assert make_p1b_short_offsets({"tip_spots": ["only_one"]}) is False
        assert make_p1b_short_offsets({"tip_spots": []}) is False
        assert make_p1b_short_offsets({}) is False

    def test_declines_when_tip_spots_not_a_sequence(self):
        assert make_p1b_short_offsets({"tip_spots": "not_a_list"}) is False
        assert make_p1b_short_offsets({"tip_spots": None}) is False

    def test_offsets_one_element_short_and_non_empty(self):
        kwargs = {"tip_spots": ["a", "b", "c"]}
        assert make_p1b_short_offsets(kwargs) is True
        assert len(kwargs["offsets"]) == 2  # len(tip_spots) - 1
        assert len(kwargs["offsets"]) > 0  # non-empty -- E-CALL(beta)'s known-truthy branch

    def test_offsets_length_scales_with_tip_spots(self):
        kwargs = {"tip_spots": tuple(range(5))}
        assert make_p1b_short_offsets(kwargs) is True
        assert len(kwargs["offsets"]) == 4


class TestMakeP1cNonTipspotElement:
    def test_declines_on_empty_or_missing_tip_spots(self):
        assert make_p1c_non_tipspot_element({"tip_spots": []}) is False
        assert make_p1c_non_tipspot_element({}) is False
        assert make_p1c_non_tipspot_element({"tip_spots": "nope"}) is False

    def test_replaces_first_element_only(self):
        kwargs = {"tip_spots": ["ts0", "ts1", "ts2"]}
        assert make_p1c_non_tipspot_element(kwargs) is True
        mutated = kwargs["tip_spots"]
        assert len(mutated) == 3
        assert mutated[0] not in ("ts0",)  # replaced
        assert not isinstance(mutated[0], str)  # a plain non-TipSpot object
        assert mutated[1] == "ts1" and mutated[2] == "ts2"  # rest untouched

    def test_single_element_still_constructible(self):
        kwargs = {"tip_spots": ["only_one"]}
        assert make_p1c_non_tipspot_element(kwargs) is True
        assert len(kwargs["tip_spots"]) == 1
        assert not isinstance(kwargs["tip_spots"][0], str)


class TestRunOnePredicateMutantEndToEnd:
    """One lightweight, real (asyncio + PLR) invocation per mutator, over
    the repo's own tiny `tip_mutant_probe.json` fixture (2 pick_up_tips
    calls, 2 tip spots each -- `plr-sema/eval/fixtures/tip_mutant_probe.
    json`, already used by `tip_mutants.py`'s own tests/regression run).

    **Why `achieved` (a `WILL_FAIL` at the raised index) is asserted
    `False` for ALL THREE mutators here, not just (c).** Measured at full
    corpus scale (T32, #4979, `outputs/plr-sema/predicate_mutants_
    260908_inc6.json`): (a) 288/288 and (c) 288/288 raised the expected
    exception with 0 achieved; (b) 16/16 (rows with >= 2 tip_spots) raised
    with 0 achieved. **This is NOT the C4 false-`WILL_FAIL` mechanism and
    NOT an unsoundness regression** -- `n_unsound` is 0 in every case, both
    directions, at every scale this module has been run at. The root
    cause, traced directly against the shipped evaluator this pass: EVERY
    real caller of `predicate.evaluate_guard` (`plr_sema/check/__init__.
    py`'s `_findings_for_call`, the ONLY production call site) omits the
    keyword-only `k_reachability_clear` argument, so it is always `None`.
    `guard_is_unconditional`'s clause (5) (`plr_sema/src/plr_sema/check/
    predicate.py`'s own `if not scope_entries: return
    bool(k_reachability_clear)`) therefore ALWAYS returns `False` for
    every depth-0, empty-`scope_trail` guard -- which is exactly what
    `:498`/`:502`/`:522` (`pick_up_tips`'s three grammar-decidable guards)
    all are. A guard in this shape can therefore decide `SAFE` (the
    `fires is False` branch, which never consults
    `guard_is_unconditional` at all -- this is how :502/:522 decide SAFE
    on 223/223 real corpus operations) but can NEVER decide `WILL_FAIL`
    through `plr_sema.check.predicate` as currently wired, regardless of
    how a caller mutates the call: `guard_is_unconditional` fails closed
    on the SAME missing fact every time. This is a documented,
    IN-SCOPE-ACKNOWLEDGED gap of `predicate.py` itself (its own module
    docstring, "What this module does NOT have data for", item 2), not a
    T32 defect -- and T32's mandate is measurement-only (no analyzer
    changes), so this test PINS the current, measured, SOUND-but-
    incomplete behaviour rather than asserting the spec's originally
    predicted >= 1 floor, which this measurement pass falsified for a
    documented, non-unsoundness reason. A future increment that threads a
    real `k_reachability_clear` fact through `check/__init__.py` should
    make this test's `achieved is False` assertions start failing --
    that is the intended trip-wire for when this becomes reachable again.
    """

    @pytest.fixture(scope="class")
    @staticmethod
    def probe_example():
        examples = _example_files(FIXTURES_DIR)
        by_name = dict(examples)
        assert "tip_mutant_probe" in by_name, sorted(by_name)
        return by_name["tip_mutant_probe"]

    @pytest.fixture(scope="class")
    @staticmethod
    def contracts_and_params():
        contracts_json = CONTRACTS_PATH.read_text(encoding="utf-8")
        return contracts_json, oc.param_names_from_contracts(contracts_json)

    @pytest.mark.parametrize(
        "mutant_class",
        ["p1a_duplicate_use_channels", "p1b_short_offsets", "p1c_non_tipspot_element"],
    )
    def test_zero_unsound_every_mutator(self, probe_example, contracts_and_params, mutant_class):
        contracts_json, param_names = contracts_and_params
        result = run_one_predicate_mutant(
            "tip_mutant_probe", mutant_class, probe_example, contracts_json, param_names,
            _MUTATORS[mutant_class], _EXPECTED_EXC[mutant_class],
        )
        assert result.ran is True, result.error
        assert result.error is None
        assert result.raised_as_expected is True, (
            f"expected {_EXPECTED_EXC[mutant_class]!r}, simulator raised {result.raised_exc_class!r}"
        )
        # The soundness invariant this module gates on: NEVER a static SAFE
        # where the simulator raised, NEVER a static WILL_FAIL where it
        # didn't -- this must hold regardless of the floor-miss finding
        # documented in this class's own docstring.
        assert result.unsound_safe is False
        assert result.unsound_will_fail_elsewhere is False

    def test_achieved_is_false_pinning_the_k_reachability_clear_gap(self, probe_example, contracts_and_params):
        """Pins the measured (a)/(b)/(c) `static_verdict_at_index` as
        `"unknown"`, per this class's own docstring. If this starts
        failing, `guard_is_unconditional` has gained a real
        `k_reachability_clear` fact somewhere -- update this test, don't
        just relax it."""
        contracts_json, param_names = contracts_and_params
        for mutant_class in ("p1a_duplicate_use_channels", "p1b_short_offsets", "p1c_non_tipspot_element"):
            result = run_one_predicate_mutant(
                "tip_mutant_probe", mutant_class, probe_example, contracts_json, param_names,
                _MUTATORS[mutant_class], _EXPECTED_EXC[mutant_class],
            )
            assert result.static_verdict_at_index == "unknown", (mutant_class, result)

    def test_mutation_declines_gracefully_when_no_pick_up_tips(self, contracts_and_params):
        """A base example with no `pick_up_tips` call at all: the mutator
        never fires (`target_idx` stays `None`), and this function reports
        it as a declined construction, mirroring `tip_mutants.
        make_m1_remove_pickup`'s own "skip, don't guess" discipline."""
        contracts_json, param_names = contracts_and_params
        example = {
            "call_sequence": [{"name": "aspirate", "params": {"source": "plate.A1", "volume_ul": 10.0}}],
            "intent_record": {"record_id": "synthetic-no-pickup"},
            "deck_layout": {"resources": {"plate": "Plate"}},
        }
        result = run_one_predicate_mutant(
            "synthetic-no-pickup", "p1a_duplicate_use_channels", example, contracts_json, param_names,
            _MUTATORS["p1a_duplicate_use_channels"], _EXPECTED_EXC["p1a_duplicate_use_channels"],
        )
        assert result.ran is False
        assert result.error == "mutation could not be constructed"
