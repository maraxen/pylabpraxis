"""surface_violations: the deterministic identifier-leak filter of the
natural-phrasing lane (task 260902_p26b_surface_data)."""

from floor_gen.natural import natural_record_id, surface_violations

BASE = "Aspirate 25 microliters from plate_1.C7."


def _v(utt, evals=()):
    return surface_violations(utt, base_utterance=BASE, eval_utterances=evals)


def test_natural_phrasing_passes():
    assert _v("Pull 25 microliters out of well C7 on plate 1.") == []
    assert _v("Grab tips from the C5 spot on the tip rack.") == []
    assert _v("Put the tips back in the same well.") == []       # vague phrase passes
    assert _v("Carry the hotel stack over to the scale station.") == []


def test_underscore_identifier_rejected():
    assert "underscore_identifier" in _v("Pull 25 microliters from plate_1 well C7.")
    assert "underscore_identifier" in _v("Please pick_up_tips at A1.")
    assert "underscore_identifier" in _v("Move it to scale_station_1.")


def test_dotted_well_and_bracket_rejected():
    assert "dotted_well_ref" in _v("Take 25 microliters from plate 1.C7.")
    assert "bracket" in _v("Put 10 microliters into plate[1] well A1.")


def test_canonical_liquid_verbs_rejected_but_move_and_read_allowed():
    assert "canonical_verb" in _v("Aspirate 25 microliters from well C7 of plate 1.")
    assert "canonical_verb" in _v("Please dispense 10 microliters into well A1 of plate 2.")
    assert "canonical_verb" in _v("Stamp the layout onto plate 2.")
    assert _v("Move the plate onto the scale station.") == []
    assert _v("Read the OD of wells A1 through A6 at 600 nm.") == []


def test_duplicates_rejected():
    assert "duplicate_of_base" in _v("aspirate 25 microliters from plate_1.C7.")  # normalized equal
    assert "duplicate_of_eval_row" in _v("Pull 25 microliters out of well C7 on plate 1.",
                                         evals={"pull 25 microliters out of well c7 on plate 1."})


def test_record_id_mapping():
    assert natural_record_id("cov-0015-aspirate__missing-slot-00") == "nat-0015-aspirate__missing-slot-00"
