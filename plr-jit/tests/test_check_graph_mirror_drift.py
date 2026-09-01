"""Spec 260901 §5.3 "Fork C" / §5.6 AC-5.5 / D8: the `check/graph.py`
stdlib-dataclass mirror's field-set drift test.

Lives under `tests/`, which spec §1.3's boundary walk does NOT cover (that
walk is scoped to `src/plr_jit/`) -- so, unlike anything under `src/`, this
file MAY import `praxis.backend.utils.plr_static_analysis.models`. Compares
`plr_jit.check.graph`'s mirror dataclasses' field names against the live
pydantic models' `model_fields` keys: DERIVED for the per-field presence
check (the comparison target is the live model, not a typed list), while the
DECISION of which fields to mirror remains HAND-MAINTAINED (registry row
HM-21, spec §9.2) -- a human decided which §3.3 reasons/§7.3 lookups exist
today, and that decision is not itself recoverable from PLR source.

Fails CLOSED (an assertion, not a skip) whenever `praxis` is importable in
the running test environment (spec §5.5's Fork C failure-mode note) --
converting a silent runtime gap (a mirrored field that no longer exists
upstream, producing a silent None/KeyError at `json.loads` time rather than
an import-time error, since the mirror never imports the pydantic model to
fail against) into a red test at review time. Only skips, with an explicit
reason, when `praxis` genuinely is not importable in this environment.
"""

from __future__ import annotations

import dataclasses

import pytest

from plr_jit.check.graph import OperationNode, ResourceNode

try:
    from praxis.backend.utils.plr_static_analysis.models import (
        OperationNode as UpstreamOperationNode,
    )
    from praxis.backend.utils.plr_static_analysis.models import (
        ResourceNode as UpstreamResourceNode,
    )
except ImportError as exc:  # pragma: no cover - environment-dependent
    UpstreamOperationNode = None
    UpstreamResourceNode = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


_MIRROR_TARGETS = [
    (OperationNode, "OperationNode", "UpstreamOperationNode"),
    (ResourceNode, "ResourceNode", "UpstreamResourceNode"),
]


@pytest.mark.parametrize(
    "mirror_cls, mirror_name, upstream_ref", _MIRROR_TARGETS, ids=["OperationNode", "ResourceNode"]
)
def test_mirror_fields_match_operation_node(mirror_cls, mirror_name, upstream_ref) -> None:
    """Every field name in `check/graph.py`'s mirror is a member of the live
    model's `model_fields` (spec §5.3/§5.4/AC-5.5). Fails closed -- if
    `praxis` is not importable here, this is a genuine environment gap, not
    a pass, and is reported via `pytest.skip` with the import error named,
    never a silent pass."""
    if _IMPORT_ERROR is not None:
        pytest.skip(
            f"praxis not importable in this test environment ({_IMPORT_ERROR!r}) -- "
            f"Fork C's mirror-drift check cannot run; this is an environment gap, "
            f"not evidence the mirror is correct"
        )

    upstream_cls = UpstreamOperationNode if upstream_ref == "UpstreamOperationNode" else UpstreamResourceNode
    upstream_fields = set(upstream_cls.model_fields.keys())
    mirror_fields = {f.name for f in dataclasses.fields(mirror_cls)}

    unmatched = mirror_fields - upstream_fields
    assert not unmatched, (
        f"plr_jit.check.graph.{mirror_name} mirrors field(s) {sorted(unmatched)} that "
        f"are NOT present on the live praxis {mirror_name}.model_fields "
        f"({sorted(upstream_fields)}) -- the mirror has drifted from upstream "
        f"(spec §5.3 Fork C)"
    )
