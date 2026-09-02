"""Natural lane end-to-end with a scripted FakeTeacher: ids, lineage,
provenance, out-of-surface skipped, filter applied, base tampering loud
(task 260902_p26b_surface_data)."""

import json
from pathlib import Path

import pytest

from floor_gen.cache import TeacherCache
from floor_gen.corpus import CorpusError
from floor_gen.matrix import committed_matrix_path, load_matrix
from floor_gen.natural import build_natural_manifest, generate_natural_corpus
from floor_gen.teachers import FakeTeacher
from floor_gen.versions import PROMPT_VERSION_NATURAL

ROOT = Path(__file__).resolve().parents[1]


def _base_rows(cells, n=2):
    rows = [json.loads(l) for l in (ROOT / "out" / "corpus_p23_floor.jsonl").read_text().splitlines() if l.strip()]
    out = []
    for cid in cells:
        out += [r for r in rows if r["matrix_cell"]["cell_id"] == cid][:n]
    return out


def _natural_teacher():
    def respond(system, user):
        # mimic a compliant teacher: everyday verb, natural location, no ids
        return json.dumps({"utterance": "Pull 25 microliters out of well C7 on plate 1, please.", "clarification": None})
    return FakeTeacher(responder=respond)


def test_offline_lane_rows_lineage_and_skip(tmp_path):
    matrix = load_matrix(committed_matrix_path())
    base = _base_rows(["aspirate__none", "pick_up_tips__ambiguous-referent", "mix__out-of-surface"])
    assert any(r["matrix_cell"]["ambiguity_class"] == "out-of-surface" for r in base)
    rows, stats = generate_natural_corpus(base, matrix, _natural_teacher(), TeacherCache(tmp_path), batch_size=1)
    assert stats.skipped_out_of_surface == 2 and stats.base_rows == 6
    assert stats.accepted == 4 and stats.rejected_filter == 0
    for row, b in zip(rows, [r for r in base if r["matrix_cell"]["ambiguity_class"] != "out-of-surface"]):
        assert row["record_id"] == "nat-" + b["record_id"][4:]
        assert row["lineage"]["base_record_id"] == b["record_id"]
        assert row["provenance"]["provenance"] == "coverage_natural"
        assert row["provenance"]["prompt_version"] == PROMPT_VERSION_NATURAL
        assert row["structured_calls"] == b["structured_calls"] and row["intent"] == b["intent"]
        assert "execution_verify" not in row
    m = build_natural_manifest(stats, base_corpus="x", base_manifest={"generator_version": "0.2.1", "prompt_version": "p"})
    assert m["accepted"] == 4 and m["prompt_version"] == PROMPT_VERSION_NATURAL


def test_offline_lane_filter_rejects_identifier_leak_and_counts(tmp_path):
    matrix = load_matrix(committed_matrix_path())
    base = _base_rows(["aspirate__none"], n=2)
    leaky = FakeTeacher(responder=lambda s, u: json.dumps({"utterance": "Aspirate 25 microliters from plate_1.C7.", "clarification": None}))
    rows, stats = generate_natural_corpus(base, matrix, leaky, TeacherCache(tmp_path))
    assert rows == [] and stats.rejected_filter == 2
    assert stats.rejected_by_reason["underscore_identifier"] == 2
    assert stats.rejected_by_reason["canonical_verb"] == 2


def test_second_run_is_cache_hits_only_and_identical(tmp_path):
    matrix = load_matrix(committed_matrix_path())
    base = _base_rows(["dispense__missing-slot"], n=3)
    t = _natural_teacher()
    cache = TeacherCache(tmp_path)
    rows1, s1 = generate_natural_corpus(base, matrix, t, cache)
    rows2, s2 = generate_natural_corpus(base, matrix, t, cache)
    assert s1.cache_misses == 3 and s2.cache_misses == 0 and s2.cache_hits == 3
    assert rows1 == rows2


def test_tampered_base_row_is_loud(tmp_path):
    matrix = load_matrix(committed_matrix_path())
    base = _base_rows(["aspirate__none"], n=1)
    base[0]["structured_calls"][0]["kwargs"]["vols"] = [999.0]
    with pytest.raises(CorpusError, match="structured_calls differ"):
        generate_natural_corpus(base, matrix, _natural_teacher(), TeacherCache(tmp_path))
