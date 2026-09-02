"""The 625 floor rows that assembly 0.1.3 accepted must stay byte-identical
(modulo provenance.generator_version) across the 0.2.1 synth repair
(task 260902_p26b_surface_data)."""

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DIGESTS = REPO / "training" / "floor_gen" / "data" / "floor_0.2.0_accepted_digests.json"
FLOOR = REPO / "training" / "out" / "corpus_p23_floor.jsonl"


def _canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def row_digest(row: dict) -> str:
    r = json.loads(_canon(row))
    r["provenance"] = {k: v for k, v in r["provenance"].items() if k != "generator_version"}
    return hashlib.sha256(_canon(r).encode("utf-8")).hexdigest()


def test_floor_corpus_accepted_rows_byte_stable():
    pinned = json.loads(DIGESTS.read_text(encoding="utf-8"))
    assert pinned["n_accepted"] == 625
    rows = {json.loads(l)["record_id"]: json.loads(l) for l in FLOOR.read_text(encoding="utf-8").splitlines() if l.strip()}
    assert len(rows) == pinned["n_floor_rows"] == 685
    missing = sorted(set(pinned["rows"]) - set(rows))
    assert not missing, missing[:5]
    changed = [rid for rid, d in pinned["rows"].items() if row_digest(rows[rid]) != d]
    assert not changed, changed[:10]
