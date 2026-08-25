"""Dedup-behavior and pair-building tests for P2.4 (AC-2.4.x).

Uses a deterministic fake teacher (no network) to pin:
- normalization parity with coxswain.parse_source (parse_source.py:53-56),
- vs-floor rejection, within-overlay rejection, case/whitespace collision,
- cache round-trip + hit behavior,
- row provenance completeness.
"""

from __future__ import annotations

import json
from pathlib import Path

from overlay_gen.cache import TeacherCache
from overlay_gen.miner import GOLDEN_FIXTURE_DIR, MinedCall
from overlay_gen.normalize import normalize_utterance
from overlay_gen.pair_builder import (
    PROMPT_VERSION,
    canonical_sentence,
    parse_paraphrases,
    build_pairs,
)


class FakeTeacher:
    """Deterministic offline teacher: echoes scripted variants per request."""

    model_version = "fake-teacher-v9"

    def __init__(self, variants: list[str]):
        self.variants = variants
        self.calls = 0

    def complete(self, prompt: str) -> str:
        self.calls += 1
        return "\n".join(self.variants)


def make_call(name="aspirate", params=None, source="n.ipynb", origin="n.ipynb#cell0"):
    return MinedCall(
        name=name,
        receiver_type="liquid_handler",
        params=params if params is not None else {"source": "plate['A1']", "volume_ul": [10.0]},
        source=source,
        origin=origin,
    )


# --- normalization -----------------------------------------------------------


def test_normalize_parity_with_coxswain():
    from coxswain.parse_source import _normalize_utterance as cox_norm

    samples = [
        "  Aspirate   10 uL FROM A1 ",
        "DROP\tthe\nTips",
        "TRANSFER 50uL plate A1 -> B1",
        "",
        42,
        None,
        "ÜNICODE   CASE",
    ]
    for s in samples:
        assert normalize_utterance(s) == cox_norm(s), f"parity broken for {s!r}"


def test_parse_paraphrases_strips_bullets_and_dupes():
    text = '1. Aspirate ten microliters from A1.\n- aspirate  10 uL from A1!\ntake 10 uL out of A1\n\n"pipette 10 uL from A1"\n'
    out = parse_paraphrases(text)
    # all four lines are distinct after normalization (punctuation differs,
    # wording differs); bullets/numbering/quotes are stripped
    assert len(out) == 4


# --- dedup behavior ----------------------------------------------------------


def _variants(*v: str) -> FakeTeacher:
    return FakeTeacher(list(v))


VARIANTS = [
    "aspirate ten microliters from well A1",
    "please take up 10 uL out of A1",
    "pull 10 uL from plate position A1",
]


def test_happy_path_writes_all_variants_with_provenance(tmp_path: Path):
    rows, summary = build_pairs(
        [make_call()],
        teacher=_variants(*VARIANTS),
        cache_dir=tmp_path / "cache",
        n_variants=3,
        generator_version="deadbee",
    )
    assert summary["pairs_written"] == 3
    assert summary["rejected_vs_floor"] == 0
    assert [r["instruction"] for r in rows] == VARIANTS
    prov = rows[0]["provenance"]
    assert prov["provenance"] == "naturalness"
    assert prov["source_notebook_or_protocol"] == "n.ipynb"
    assert prov["prompt_version"] == PROMPT_VERSION
    assert prov["teacher_model_version"]
    assert prov["generator_version"] == "deadbee"


def test_floor_collision_rejected(tmp_path: Path):
    floor_file = tmp_path / "floor.jsonl"
    floor_file.write_text(
        json.dumps({"instruction": VARIANTS[0]}) + "\n", encoding="utf-8"
    )
    _, summary = build_pairs(
        [make_call()],
        teacher=_variants(*VARIANTS),
        cache_dir=tmp_path / "cache",
        floor_extra_paths=[floor_file],
    )
    assert summary["rejected_vs_floor"] >= 1
    assert summary["pairs_written"] == 2


def test_case_and_whitespace_variant_collides_within_overlay(tmp_path: Path):
    # Two mined calls sharing a canonical get the same variant set; a variant
    # differing only by case/whitespace must not double-enter the overlay.
    c2 = make_call(origin="n.ipynb#cell1")
    rows, summary = build_pairs(
        [make_call(), c2],
        teacher=FakeTeacher(VARIANTS[:1] + ["  ASPIRATE   TEN MICROLITERS FROM WELL A1 "]),
        cache_dir=tmp_path / "cache",
    )
    assert summary["rejected_within_overlay"] == 1
    assert summary["pairs_written"] == 1
    assert len({r["id"] for r in rows}) == 1


def test_duplicate_canonicals_share_one_teacher_call(tmp_path: Path):
    teacher = _variants(*VARIANTS)
    calls = [make_call(origin=f"n.ipynb#cell{i}") for i in range(3)]
    _, summary = build_pairs(calls, teacher=teacher, cache_dir=tmp_path / "c")
    assert teacher.calls == 1
    assert summary["unique_canonicals"] == 1


def test_cache_roundtrip_and_hit(tmp_path: Path):
    cache_dir = tmp_path / "cache"
    t1 = _variants(*VARIANTS)
    rows1, s1 = build_pairs([make_call()], teacher=t1, cache_dir=cache_dir)
    assert s1["teacher_calls_made"] == 1 and s1["cache_hits"] == 0

    t2 = _variants()  # would return garbage/empty if consulted
    rows2, s2 = build_pairs([make_call()], teacher=t2, cache_dir=cache_dir)
    assert t2.calls == 0
    assert s2["cache_hits"] == 1 and s2["teacher_calls_made"] == 0
    assert rows1 == rows2  # same sha => same corpus (R4)

    entry = json.loads(next((cache_dir).glob("*.json")).read_text())
    assert entry["prompt_version"] == PROMPT_VERSION
    assert entry["response"] == "\n".join(VARIANTS)


def test_floor_absent_produces_warning_not_crash(tmp_path: Path):
    _, summary = build_pairs(
        [], teacher=_variants(), cache_dir=tmp_path / "c"
    )
    assert any("floor corpus absent" in w for w in summary["warnings"])
    assert summary["pairs_written"] == 0


def test_golden_fixtures_are_in_reference_set(tmp_path: Path):
    # An instruction equal (normalized) to a golden fixture utterance must be
    # rejected even though no explicit floor file exists yet.
    first_fixture = sorted(GOLDEN_FIXTURE_DIR.glob("*.json"))[0]
    golden = json.loads(first_fixture.read_text())
    rows, summary = build_pairs(
        [make_call()],
        teacher=_variants(golden["utterance"], VARIANTS[1]),
        cache_dir=tmp_path / "c",
    )
    assert summary["rejected_vs_floor"] == 1
    assert [r["instruction"] for r in rows] == [VARIANTS[1]]


# --- canonical sentence rendering --------------------------------------------


def test_canonical_sentence_aspirate():
    s = canonical_sentence(make_call(params={"source": "plate['A1:C1']", "volume_ul": [100.0]}))
    assert s == "aspirate 100 uL from plate A1:C1"


def test_canonical_sentence_discard_has_at_clause():
    call = make_call(
        name="discard_tips", params={"what": "tips", "at": "trash[0]"}
    )
    assert canonical_sentence(call) == "discard the tips at trash 0"


def test_canonical_unknown_tool_raises():
    try:
        canonical_sentence(make_call(name="not_a_tool"))
    except KeyError as exc:
        assert "not_a_tool" in str(exc)
    else:
        raise AssertionError("expected KeyError")
