"""plr_jit.check.graph: stdlib-dataclass mirror of the extracted protocol
computation graph (spec 260901 §5.3 "Fork C", §6.2).

**Why a mirror, not the real model.** ``OperationNode``/``ResourceNode``/
``ProtocolComputationGraph`` (``praxis/backend/utils/plr_static_analysis/
models.py:524-662``) are pydantic ``BaseModel``s under ``praxis.*`` --
forbidden under ``check/`` by §1.3 (no ``praxis`` import under
``src/plr_jit/``) and unmovable per §1.1 (round 1 moves nothing out of
``praxis/``), independent of any Pyodide/pydantic question. The wire format
between ``extract/`` (server-side, round 2) and ``check/`` (browser-side,
this module) is already JSON (§6.2), so this mirror is populated by
``json.loads`` + explicit field extraction below -- NEVER by a pydantic
``model_validate``. No third model hierarchy is introduced: this pair of
stdlib mirrors is the only model hierarchy ``check/`` ever sees.

**The field set is derived-from-consumers, normative, not exemplary (D1).**
A field is mirrored iff a §3.3 reason or the §7.3 contract-table lookup key
consumes it. This is the enumeration, verbatim from spec §6.2 -- do not add
to it, do not trim it, and a new consumer that needs a field not listed here
requires a visible edit to the spec table, not a silent addition below.

**Round-4 remediation (M1 + B4, spec §6.2's Cluster 2 fix).** The pre-round-4
mirror was over-inclusive in two independent ways, both closed here:
``line_number``/``node_type``/``arguments`` were mirrored but never read by
anything except this module's own declaration/parse (M1, confirmed by grep);
``arguments`` additionally fed the now-withdrawn ``argument_not_static``
reason (B4 -- see ``plr_jit.verdict.REASON_VOCABULARY``'s docstring: the
guard-free-var namespace and the protocol-parameter namespace it intersected
are disjoint in every shipped fixture, so it never fired, and a same-named
collision would have fired it for no semantic cause). All three fields and
their extraction are deleted below. ``depends_on_params`` is KEPT despite
``argument_not_static``'s withdrawal leaving it with no *current* consumer
-- unlike the three deleted fields, it is the one piece B4's own reinstatement
note names as still needed (guard free var -> PLR parameter position ->
``arguments[param]`` -> protocol expression -> ``depends_on_params``), so it
stays mirrored as a forward-looking field, the same treatment ``receiver_variable``
already got from D1/m1 below -- flagged here rather than silently pruned to
match the letter of "derived-from-consumers" while breaking its spirit.

| ``OperationNode`` field                     | consumer                                                          |
|-----------------------------------------------|---------------------------------------------------------------------|
| ``receiver_type`` + ``method_name``           | contract-table lookup key ``f"{receiver_type}.{method_name}"``      |
| ``receiver_type``, checked for ``None``       | reason ``receiver_type_unknown``                                    |
| ``method_name`` (paired with ``receiver_type``), checked against the contract table | reason ``unsupported_tool`` (redefined 260901 T11: key absent from the whole-survey contract table, not ``SUPPORTED_TOOLS`` membership -- see ``plr_jit.check``'s module docstring) |
| ``foreach_source``, ``foreach_body``          | reason ``loop_bounds_unknown`` (identifies the loop, not its bounds)|
| ``id``                                        | ``Finding.operation_id`` provenance (AC-6.4)                        |
| ``receiver_variable``                         | matching against the mirrored ``ResourceNode`` set (forward-looking -- see below) |
| ``depends_on_params``                         | no current consumer -- forward-looking; reinstating ``argument_not_static`` needs it (B4) |

**D1's own flag, restated:** before this fix, ``receiver_type_unknown`` alone
could satisfy AC-6.3's ">=1 finding" with the contract table entirely
unexercised -- a gate that passes without touching the thing it gates. The
fixture this package ships (``tests/fixtures/simple_transfer_graph.json``)
is chosen specifically so every operation resolves a real
``receiver_type``/``method_name`` pair and hits a populated contract-table
entry -- see ``tests/test_check_graph.py`` for the confirmation.

**``ResourceNode`` is mirrored too** -- ``ungroundable_reference`` (§4.1,
static meaning: "a resource variable with no ``ResourceNode`` in the graph")
is a graph-membership test and has no other source: does
``OperationNode.receiver_variable`` correspond to a resource present in the
graph's ``resources`` mapping?

**SPEC GAP, flagged rather than silently worked around.** §5.3/§6.2 describe
the mirrored ``ResourceNode`` field as "``id``, and whatever identifies the
resource variable it corresponds to" -- but the live
``praxis.backend.utils.plr_static_analysis.models.ResourceNode`` (:562-587)
has NO ``id`` field. ``ProtocolComputationGraph.resources`` is
``dict[str, ResourceNode]``, keyed by variable name, and ``ResourceNode``
itself separately carries that same name as its own ``variable_name`` field
(:564) -- THAT field, not a nonexistent ``id``, is what identifies a
resource for the membership test below. Mirroring a field literally named
``id`` here would make Fork C's own drift test
(``tests/test_check_graph_mirror_drift.py``) fail immediately, since ``id``
is not a member of ``ResourceNode.model_fields``. This mirror therefore
carries ``variable_name`` only; see this task's report for the note.

**The membership test itself (``is_grounded``) is not currently wired into
any ``Finding``.** ``ungroundable_reference`` is a member of
``FAILURE_CATEGORIES`` (§4.1), and ``Finding.category`` is validated as
REQUIRED only for ``verdict is WILL_FAIL`` (§3.1) -- round 1 never emits
``WILL_FAIL`` (§0, §11 of this task's brief). Wiring the membership test to
an UNKNOWN finding would require adding an 8th REASON_VOCABULARY member
(the closed 7-member set, §3.3 -- round-4 remediation withdrew
``argument_not_static``, B4 -- has none that means "resource reference is
ungroundable") -- out of round-1 scope. **Restated forward-looking, not as a
live consumer (round-4 remediation, m1):** the mirror and the
membership-test helper below exist so the membership test is *ready* the
moment a future round adds that reason -- five slots of headroom remain
under §3.3's hard cap of 12 (7 today) -- and so Fork C's field-set drift
test has a real comparison target in the meantime; they are not dead code,
just not yet a ``Finding`` source. Flagged, not silently worked around.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

__all__ = [
    "OperationNode",
    "ResourceNode",
    "ProtocolComputationGraph",
    "parse_graph",
    "is_grounded",
]


@dataclass(frozen=True, slots=True)
class OperationNode:
    """Derived-from-consumers stdlib mirror of
    ``praxis.backend.utils.plr_static_analysis.models.OperationNode``
    (:524-662). See module docstring for the per-field consumer table."""

    id: str
    method_name: str
    receiver_variable: str
    receiver_type: str | None
    depends_on_params: tuple[str, ...]
    foreach_source: str | None
    foreach_body: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ResourceNode:
    """Minimal stdlib mirror of
    ``praxis.backend.utils.plr_static_analysis.models.ResourceNode``
    (:562-587). ``variable_name`` is the sole mirrored field -- see the
    module docstring's SPEC GAP note on why this is ``variable_name``, not
    ``id`` (the real model has no ``id`` field)."""

    variable_name: str


@dataclass(frozen=True, slots=True)
class ProtocolComputationGraph:
    """Minimal stdlib mirror of
    ``praxis.backend.utils.plr_static_analysis.models.ProtocolComputationGraph``
    (:613-649) -- only the fields ``check_graph`` (spec §6.2's round-1 entry
    point) actually reads: the protocol identity, the operation sequence,
    and the resource-variable membership set."""

    protocol_fqn: str
    operations: tuple[OperationNode, ...]
    resources: dict[str, ResourceNode]


def _operation_from_dict(d: dict[str, Any]) -> OperationNode:
    return OperationNode(
        id=d["id"],
        method_name=d["method_name"],
        receiver_variable=d["receiver_variable"],
        receiver_type=d.get("receiver_type"),
        depends_on_params=tuple(d.get("depends_on_params", ())),
        foreach_source=d.get("foreach_source"),
        foreach_body=tuple(d.get("foreach_body", ())),
    )


def _resource_from_dict(d: dict[str, Any]) -> ResourceNode:
    return ResourceNode(variable_name=d["variable_name"])


def parse_graph(payload: dict[str, Any]) -> ProtocolComputationGraph:
    """Deserialize one graph JSON payload (§6.2's wire format -- the raw
    ``.model_dump(mode="json")`` output of the real, out-of-process
    ``ProtocolComputationGraph``) into this module's stdlib mirror.
    ``json.loads`` + explicit field extraction only -- never a pydantic
    ``model_validate`` (see module docstring)."""
    operations = tuple(_operation_from_dict(o) for o in payload.get("operations", ()))
    resources = {
        name: _resource_from_dict(r) for name, r in payload.get("resources", {}).items()
    }
    return ProtocolComputationGraph(
        protocol_fqn=payload["protocol_fqn"],
        operations=operations,
        resources=resources,
    )


def is_grounded(op: OperationNode, graph: ProtocolComputationGraph) -> bool:
    """Graph-membership test for ``ungroundable_reference`` (§4.1's static
    meaning): does ``op.receiver_variable`` correspond to a ``ResourceNode``
    present in ``graph.resources``? See module docstring for why this is not
    currently wired into any emitted ``Finding``."""
    return op.receiver_variable in graph.resources
