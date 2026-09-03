"""Natural in-surface rows are frozen.

The 519 in-surface natural rows committed at 52860d53 must stay byte-identical
(modulo provenance.teacher_model_version, whose fake-teacher@test stamp is being
corrected) across the out-of-surface lane extension (task 260903_p26c_oos_natural).
"""

import json
from pathlib import Path

from floor_gen.digests import row_digest

REPO = Path(__file__).resolve().parents[2]
DIGESTS = REPO / "training" / "floor_gen" / "data" / "natural_v2_accepted_digests.json"
NATURAL = REPO / "training" / "out" / "corpus_p23_floor_natural.jsonl"


def _rows(path: Path) -> dict[str, dict]:
  return {
    json.loads(line)["record_id"]: json.loads(line)
    for line in path.read_text(encoding="utf-8").splitlines()
    if line.strip()
  }


def test_natural_in_surface_rows_byte_stable():
  pinned = json.loads(DIGESTS.read_text(encoding="utf-8"))
  assert pinned["n_rows"] == 519
  drop = tuple(pinned["drop_provenance_keys"])
  assert drop == ("teacher_model_version",)
  rows = _rows(NATURAL)
  missing = sorted(set(pinned["rows"]) - set(rows))
  assert not missing, missing[:5]
  changed = [
    rid
    for rid, d in pinned["rows"].items()
    if row_digest(rows[rid], drop_provenance_keys=drop) != d
  ]
  assert not changed, changed[:10]


def test_digest_ignores_only_the_dropped_key():
  row = {
    "record_id": "x",
    "utterance": "u",
    "provenance": {"teacher_model_version": "a", "prompt_version": "p"},
  }
  other = json.loads(json.dumps(row))
  other["provenance"]["teacher_model_version"] = "b"
  assert row_digest(row, drop_provenance_keys=("teacher_model_version",)) == row_digest(
    other, drop_provenance_keys=("teacher_model_version",)
  )
  other["provenance"]["prompt_version"] = "q"
  assert row_digest(row, drop_provenance_keys=("teacher_model_version",)) != row_digest(
    other, drop_provenance_keys=("teacher_model_version",)
  )
