"""plr_jit.derive: transitive-closure contract derivation (spec 260901 §7).

**Mechanics only** (§7 header). This module specifies graph plumbing over
data that already exists on disk (``training/verify/data/plr_preconditions.json``,
§7.1) plus one independent, second AST pass over PLR source itself. It
specifies no predicate semantics, no abstract domain, no loop handling --
``condition``/``scope_trail`` stay opaque strings (deferred item (c)).

**RISK-1 detector (§7.6).** This is the single biggest content-risk
detection mechanism in the whole document: whether closure over
``delegates_to`` recovers materially more preconditions than a method's own
body, or whether derivation is sound-but-empty. The gap ledger this module
builds is the measurement; see ``build_gap_ledger``.

**Independence (§1.4).** This module (and the rest of ``src/plr_jit``) must
not import ``praxis``, ``verify``, or ``training`` -- enforced by
``tests/test_import_boundary.py``, which scans the whole ``src/plr_jit``
tree including this package. The dropped-receiver AST pass below
(``scan_dropped_receiver_calls``) is a SECOND, INDEPENDENT stdlib-``ast``
walk over PLR source under ``external/`` -- it does not reuse the survey
JSON or import ``scripts/survey_plr_preconditions.py`` at all, by design
(§7.4's asymmetry note: the point is a measurement that doesn't share the
survey's own blind spot).

Contents:
  * ``SurveyRecord``/``SurveyFinding`` -- typed views of the survey JSON.
  * ``load_survey``/``build_index`` -- load + key by ``(module, qualname)``.
  * ``resolve`` -- bare delegate-name resolution (§7.2, C1), class-first.
  * ``InlinedGuard``/``DerivedContract``/``derive_contract`` -- the
    transitive closure mechanic itself (§7.2).
  * ``SUPPORTED_TOOLS``/``resolve_supported_tool`` -- the D22 derived
    name-to-key mapping for the 10 analyzed LiquidHandler tools.
  * ``scan_dropped_receiver_calls`` and friends -- the independent D3 AST
    pass computing, per method, the honest and validation-looking
    dropped-receiver call-node counts.
  * ``build_gap_ledger`` -- the generated build artifact (§7.4).
"""

from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from plr_jit._provenance import SurveyStamp, survey_stamp
from plr_jit.check._supported_tools import SUPPORTED_TOOLS
from plr_jit.telemetry import FAILURE_CATEGORIES
from plr_jit.verdict import PlrSite

__all__ = [
    "SCHEMA_VERSION",
    "SUPPORTED_TOOLS",
    "SurveyFinding",
    "SurveyRecord",
    "load_survey",
    "build_index",
    "resolve",
    "resolve_supported_tool",
    "InlinedGuard",
    "DerivedContract",
    "derive_contract",
    "DroppedReceiverCounts",
    "scan_dropped_receiver_calls",
    "scan_dropped_receiver_calls_in_source",
    "build_gap_ledger",
    "default_plr_pkg_root",
]

SCHEMA_VERSION = 1

#: Re-exported from plr_jit.check._supported_tools (T8 consolidation, spec
#: 260901 §6.2's D1 note): check/ independently needs this same 10-tool
#: frozenset for the unsupported_tool reason, and check/'s own
#: import-boundary constraints (§1.3: no praxis/verify/training) mean it
#: cannot reach training.verify.dispatcher.SUPPORTED_TOOLS directly either.
#: Rather than a THIRD hand-typed copy (upstream + derive + check), this
#: module now imports the single in-package definition from
#: plr_jit.check._supported_tools, so `from plr_jit.derive import
#: SUPPORTED_TOOLS` keeps resolving to the exact same frozenset object. The
#: one live cross-package drift test against training.verify.dispatcher lives
#: at tests/test_check_graph.py::test_supported_tools_match_upstream --
#: not duplicated here.

#: Mirrors scripts/survey_plr_preconditions.py:107-109's
#: _is_validation_looking prefix list verbatim (lowercased prefix match).
_VALIDATION_LOOKING_PREFIXES: tuple[str, ...] = (
    "_check",
    "check_",
    "_assert",
    "assert_",
    "_validate",
    "validate",
)


def _is_validation_looking(name: str) -> bool:
    lname = name.lower()
    return any(lname.startswith(prefix) for prefix in _VALIDATION_LOOKING_PREFIXES)


#: A survey index key: (module, qualname).
Qualkey = tuple[str, str]

#: One recorded gap: (reason, name). reason is a REASON_VOCABULARY member
#: ("unresolved_delegate" or "no_contract_derived" -- the only two this
#: module ever emits); name is either an unresolved-call bare name or an
#: unresolvable delegate bare name, depending on reason.
Gap = tuple[str, str]


# ---------------------------------------------------------------------------
# §7.1 -- survey record shape (already on disk, not regenerated here)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class SurveyFinding:
    """One PreconditionFinding record from the survey JSON (§7.1)."""

    kind: str  # "raise_guard" | "assert"
    condition: str | None
    raises: str | None  # exception class name, None (assert), or "<dynamic:...>"
    scope_trail: tuple[str, ...]
    mentions_params: tuple[str, ...]
    lineno: int


@dataclass(frozen=True, slots=True)
class SurveyRecord:
    """One FunctionPreconditions record from the survey JSON (§7.1)."""

    qualname: str
    class_name: str | None
    module: str
    file: str
    lineno: int
    params: tuple[str, ...]
    findings: tuple[SurveyFinding, ...]
    delegates_to: tuple[str, ...]
    unresolved_calls: tuple[str, ...]


def _finding_from_dict(d: dict[str, Any]) -> SurveyFinding:
    return SurveyFinding(
        kind=d["kind"],
        condition=d.get("condition"),
        raises=d.get("raises"),
        scope_trail=tuple(d.get("scope_trail", ())),
        mentions_params=tuple(d.get("mentions_params", ())),
        lineno=d["lineno"],
    )


def _record_from_dict(d: dict[str, Any]) -> SurveyRecord:
    return SurveyRecord(
        qualname=d["qualname"],
        class_name=d.get("class_name"),
        module=d["module"],
        file=d["file"],
        lineno=d["lineno"],
        params=tuple(d.get("params", ())),
        findings=tuple(_finding_from_dict(f) for f in d.get("findings", ())),
        delegates_to=tuple(d.get("delegates_to", ())),
        unresolved_calls=tuple(d.get("unresolved_calls", ())),
    )


def load_survey(path: str | Path) -> list[SurveyRecord]:
    """Load ``plr_preconditions.json`` (§7.1). Top level is an object, not a
    list -- ``functions`` holds the per-function records. Does not
    regenerate the survey; this is a pure read of data already on disk."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return [_record_from_dict(d) for d in payload["functions"]]


def build_index(records: list[SurveyRecord]) -> dict[Qualkey, SurveyRecord]:
    """Key every record on ``(module, qualname)`` (§7.2), once."""
    return {(rec.module, rec.qualname): rec for rec in records}


# ---------------------------------------------------------------------------
# §7.2 -- resolve() and the transitive closure mechanic
# ---------------------------------------------------------------------------


def resolve(
    name: str, rec: SurveyRecord, index: dict[Qualkey, SurveyRecord]
) -> Qualkey | None:
    """Resolve one ``delegates_to`` bare name to an index key (§7.2, C1).

    Class-first precedence is normative and unconditional: step 1
    (same-class method, tried only when ``rec.class_name`` is not None) is
    tried before step 2 (module-level function) even when both would
    resolve. The residual ambiguity this creates -- a class method and a
    module-level function sharing a bare name in the same module -- is
    accepted (§7.2): step 1 wins, step 2 is never reached for that name in
    that module.

    Pure: never mutates a gap list. Callers append a
    ``("no_contract_derived", name)`` gap themselves when this returns
    ``None`` -- see ``derive_contract``.
    """
    if rec.class_name is not None:
        same_class = (rec.module, f"{rec.class_name}.{name}")
        if same_class in index:
            return same_class
    module_level = (rec.module, name)
    if module_level in index:
        return module_level
    return None


def _walk_closure(entry: Qualkey, index: dict[Qualkey, SurveyRecord]):
    """Cycle-safe transitive closure walk over ``delegates_to`` (§7.2's
    mechanic). Shared traversal core for ``derive_contract`` and the
    gap-ledger builder's reachable-set computation, so the two can never
    silently drift apart on traversal semantics.

    Yields ``(rec_or_None, key, depth)`` for every node popped off the LIFO
    frontier. ``depth`` is carried explicitly on the frontier as a
    ``(key, depth)`` pair -- never derived from ``len(seen)``, which counts
    total nodes visited across the WHOLE closure (a visit counter), not
    distance from the entry point, and would be wrong under LIFO
    ``frontier.pop()`` traversal order (trap 1). ``seen`` is checked before
    expansion (cycle-safe, trap 2) -- PLR's ``delegates_to`` graph is not
    guaranteed acyclic.

    ``rec`` is ``None`` only when a resolved key is absent from the index --
    defensive; should not occur for a key that passed through ``resolve()``,
    but handled per §7.2's own pseudocode (``index.get(q) or
    gaps.append(...)``) rather than assumed unreachable, since it is also
    the entry-point-not-in-index case.
    """
    seen: set[Qualkey] = set()
    frontier: list[tuple[Qualkey, int]] = [(entry, 0)]
    while frontier:
        key, depth = frontier.pop()
        if key in seen:
            continue
        seen.add(key)
        rec = index.get(key)
        yield rec, key, depth
        if rec is None:
            continue
        for name in rec.delegates_to:
            resolved = resolve(name, rec, index)
            if resolved is not None:
                frontier.append((resolved, depth + 1))


@dataclass(frozen=True, slots=True)
class InlinedGuard:
    """One precondition finding, inlined into an entry point's closure
    (§7.2). ``condition``/``scope_trail`` are RAW STRINGS in v1 -- turning
    them into checkable predicates is deferred item (c).

    ``kind`` carries guard polarity as a first-class field (C4, normative):
    ``"raise_guard"`` fires when ``condition`` evaluates TRUE
    (survey_plr_preconditions.py:198-199); ``"assert"`` fires when
    ``condition`` evaluates FALSE (:208). Folding this into ``condition``'s
    text would make the polarity permanently unrecoverable from the shipped
    artifact.
    """

    condition: str | None
    scope_trail: tuple[str, ...]
    raises: str | None
    kind: str  # "raise_guard" | "assert"
    free_vars: tuple[str, ...]
    site: PlrSite  # the DEFINING site -- the delegate's own file/line, never the entry point's
    depth: int  # 0 = own body, >0 = inlined from a delegate

    @property
    def is_dynamic_raise(self) -> bool:
        """D18: detect a dynamic-sentinel ``raises`` value by prefix, NEVER
        by equality against a literal glob string."""
        return self.raises is not None and self.raises.startswith("<dynamic:")


@dataclass(frozen=True, slots=True)
class DerivedContract:
    """The output of one entry point's closure (§7.2/§7.3): guards, gaps,
    and the provenance stamp of the run that produced them."""

    qualname: str
    guards: tuple[InlinedGuard, ...]
    gaps: tuple[Gap, ...]
    stamp: SurveyStamp


def derive_contract(
    module: str,
    qualname: str,
    index: dict[Qualkey, SurveyRecord],
    *,
    stamp: SurveyStamp | None = None,
) -> DerivedContract:
    """Transitive-closure contract derivation (§7.2). Totality (AC-7.2):
    NEVER raises, regardless of whether ``(module, qualname)`` is present in
    the index -- an absent entry point becomes a single
    ``("no_contract_derived", qualname)`` gap, not an exception. Every
    operation therefore receives at least one Finding downstream.

    Three properties, all testable without semantics (§7.2):
      * cycle-safe (``seen`` checked before expansion, via ``_walk_closure``)
      * provenance-preserving (every guard's ``site`` names the file that
        ACTUALLY contains it, not the entry point's file)
      * gap-recording, never gap-hiding (every ``unresolved_calls`` entry
        and every unresolvable delegate reached during the closure becomes
        a recorded gap)
    """
    if stamp is None:
        stamp = survey_stamp()
    guards: list[InlinedGuard] = []
    gaps: list[Gap] = []
    for rec, key, depth in _walk_closure((module, qualname), index):
        if rec is None:
            gaps.append(("no_contract_derived", key[1]))
            continue
        for finding in rec.findings:
            guards.append(
                InlinedGuard(
                    condition=finding.condition,
                    scope_trail=finding.scope_trail,
                    raises=finding.raises,
                    kind=finding.kind,
                    free_vars=finding.mentions_params,
                    site=PlrSite(file=rec.file, lineno=finding.lineno, qualname=rec.qualname),
                    depth=depth,
                )
            )
        for name in rec.delegates_to:
            if resolve(name, rec, index) is None:
                gaps.append(("no_contract_derived", name))
        for unresolved_name in rec.unresolved_calls:
            gaps.append(("unresolved_delegate", unresolved_name))
    return DerivedContract(qualname=qualname, guards=tuple(guards), gaps=tuple(gaps), stamp=stamp)


# ---------------------------------------------------------------------------
# AC-7.2 / D22 -- derived SUPPORTED_TOOLS -> (module, qualname) mapping
# ---------------------------------------------------------------------------


def _module_of_liquid_handler(index: dict[Qualkey, SurveyRecord]) -> str:
    """AC-7.2 says "any indexed record" -- collect ALL matching modules,
    not just the first found (round-4 remediation, m3). At the current pin
    all 54 ``class_name == "LiquidHandler"`` records sit in one module, so
    dict-iteration-order-dependent first-match happens to be deterministic
    today, but `plr_survey_common.py:127-129` proves duplicate class names
    across modules exist *in general* -- the ambiguity is latent, not live,
    and this is cheap defense in depth against it becoming live. Fails
    LOUDLY, naming every distinct module found, rather than silently
    picking one."""
    modules: set[str] = set()
    for (module, _qualname), rec in index.items():
        if rec.class_name == "LiquidHandler":
            modules.add(module)
    if not modules:
        raise LookupError(
            "no indexed survey record has class_name == 'LiquidHandler' -- cannot "
            "derive SUPPORTED_TOOLS' (module, qualname) mapping (D22)"
        )
    if len(modules) > 1:
        raise LookupError(
            f"multiple distinct modules have a class_name == 'LiquidHandler' "
            f"record: {sorted(modules)} -- SUPPORTED_TOOLS' (module, qualname) "
            f"mapping (D22) is ambiguous; resolve_supported_tool refuses to "
            f"silently pick one"
        )
    return next(iter(modules))


def resolve_supported_tool(name: str, index: dict[Qualkey, SurveyRecord]) -> Qualkey:
    """Map one bare ``SUPPORTED_TOOLS`` name to its ``(module, qualname)``
    index key by a DERIVED rule, not a hand-written map (D22): look up
    ``(module_of(LiquidHandler_record), f"LiquidHandler.{name}")`` against
    the index already built. Fails LOUDLY (``LookupError``), never silently
    skips, if the name is absent -- this gives AC-7.2 a real failure mode if
    PLR ever relocates ``LiquidHandler`` or renames a tool.
    """
    module = _module_of_liquid_handler(index)
    key = (module, f"LiquidHandler.{name}")
    if key not in index:
        raise LookupError(
            f"SUPPORTED_TOOLS name {name!r} does not resolve to {key!r} in the "
            f"survey index -- PLR may have relocated LiquidHandler or renamed "
            f"the tool (D22)"
        )
    return key


# ---------------------------------------------------------------------------
# §7.4 / D3 -- the independent dropped-receiver AST pass (SECOND, separate
# from the survey; walks PLR source directly, no praxis import, §1.4).
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[4]
_DEFAULT_PLR_PKG_ROOT = _REPO_ROOT / "external" / "pylabrobot" / "pylabrobot"


def default_plr_pkg_root() -> Path:
    """Default root for the independent AST pass, derived from this file's
    own location the same way ``plr_jit._provenance.stamp`` derives
    ``_REPO_ROOT`` -- not a hardcoded path coupling this module to a
    caller's layout (that coupling concern is what D19 forbids for
    ``--survey-json``; this path is intrinsic to the repo this file lives
    in, and is overridable via ``--plr-root`` regardless)."""
    return _DEFAULT_PLR_PKG_ROOT


def _is_plr_source_file(path: Path) -> bool:
    """Mirrors scripts/plr_survey_common.py's is_source_file(): PLR's own
    test-file naming has no single convention (STARtests.py,
    backend_tests.py, test_foo.py all coexist)."""
    stem = path.stem
    return not (stem.endswith("test") or stem.endswith("tests") or stem.startswith("test_"))


def _iter_plr_source_files(plr_pkg_root: Path) -> list[Path]:
    return sorted(p for p in plr_pkg_root.rglob("*.py") if _is_plr_source_file(p))


def _module_name_for_plr_file(file: Path, plr_pkg_root: Path) -> str:
    rel = file.relative_to(plr_pkg_root.parent)
    return ".".join(rel.with_suffix("").parts)


def _is_dropped_receiver_call(node: ast.Call) -> str | None:
    """The corrected D3 predicate: ``func`` is ``ast.Attribute`` AND NOT
    (``func.value`` is ``ast.Name`` with ``id == "self"``). Strictly wider
    than "Subscript receiver on self" -- it also drops plain
    ``resource.get_item()``-style calls whose receiver IS a bare
    ``ast.Name``, just not literally ``self``. Returns the attribute name
    (e.g. ``"get_tip"``) when the predicate matches, else ``None``.
    """
    func = node.func
    if not isinstance(func, ast.Attribute):
        return None
    if isinstance(func.value, ast.Name) and func.value.id == "self":
        return None
    return func.attr


class _DroppedReceiverScanner(ast.NodeVisitor):
    """Walks one function/method body counting D3-matching call nodes.
    Recurses into nested function defs (no ``visit_FunctionDef`` override),
    matching the survey's own _BodyScanner's own-body semantics (§7.2's
    entry-point closure treats a whole top-level function/method body,
    including any nested defs, as belonging to that one qualname)."""

    def __init__(self) -> None:
        self.total = 0
        self.validation_looking = 0
        self.by_attr: dict[str, int] = {}

    def visit_Call(self, node: ast.Call) -> None:
        attr = _is_dropped_receiver_call(node)
        if attr is not None:
            self.total += 1
            self.by_attr[attr] = self.by_attr.get(attr, 0) + 1
            if _is_validation_looking(attr):
                self.validation_looking += 1
        self.generic_visit(node)


@dataclass(frozen=True, slots=True)
class DroppedReceiverCounts:
    """Per-method output of the independent D3 AST pass (§7.4).

    ``total`` is the PRIMARY, honest figure and must NOT gate on
    ``_is_validation_looking`` -- that gate is defined over the survey's own
    recording block, which the dropped population never enters, so applying
    it to this counter would be gating on a predicate never evaluated for
    this population. ``validation_looking`` is the tighter secondary
    figure and is always <= ``total``.

    ``by_attr`` (round-4 remediation, M12): the same total, broken down per
    attribute name (e.g. ``"get_tip"``), as a sorted tuple of pairs (frozen
    dataclass -- no mutable dict field). Feeds
    ``_dropped_receiver_worklist``'s ranked view; ``sum(n for _, n in
    by_attr) == total`` always.
    """

    total: int
    validation_looking: int
    by_attr: tuple[tuple[str, int], ...] = ()


def _count_dropped_receiver_calls(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> DroppedReceiverCounts:
    scanner = _DroppedReceiverScanner()
    for stmt in node.body:
        scanner.visit(stmt)
    return DroppedReceiverCounts(
        total=scanner.total,
        validation_looking=scanner.validation_looking,
        by_attr=tuple(sorted(scanner.by_attr.items())),
    )


def scan_dropped_receiver_calls_in_source(source: str) -> DroppedReceiverCounts:
    """Test/inspection helper: run the D3 scan over the FIRST
    function/method body found in a source snippet, without touching the
    filesystem. Used by ``tests/test_derive.py``'s synthetic-fixture test
    (§7.5) so it doesn't depend on real files under ``external/``."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return _count_dropped_receiver_calls(node)
    raise ValueError("source contains no function or method definition")


def scan_dropped_receiver_calls(
    plr_pkg_root: Path | None = None,
) -> dict[Qualkey, DroppedReceiverCounts]:
    """The independent stdlib-``ast`` pass over PLR source under
    ``external/`` (§7.4/D3, T6's new work). Does NOT reuse the survey JSON
    at all -- a fresh parse of the same source tree, computing per method
    (keyed the same way the survey keys its own records: ``(module,
    qualname)``) the total D3-matching call-node count and its
    validation-looking subset.

    Only top-level module functions and one level of class methods are
    scanned (mirrors the survey's own scope, §7.1) -- nested classes are
    not descended into, matching ``survey_plr_preconditions.py:273-283``.
    """
    root = plr_pkg_root if plr_pkg_root is not None else default_plr_pkg_root()
    results: dict[Qualkey, DroppedReceiverCounts] = {}
    for file in _iter_plr_source_files(root):
        try:
            source = file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file))
        except (SyntaxError, UnicodeDecodeError):
            continue
        module = _module_name_for_plr_file(file, root)

        def _record(node: ast.FunctionDef | ast.AsyncFunctionDef, class_name: str | None) -> None:
            qualname = f"{class_name}.{node.name}" if class_name else node.name
            results[(module, qualname)] = _count_dropped_receiver_calls(node)

        for top in ast.iter_child_nodes(tree):
            if isinstance(top, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _record(top, None)
            elif isinstance(top, ast.ClassDef):
                for member in ast.iter_child_nodes(top):
                    if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        _record(member, top.name)
    return results


# ---------------------------------------------------------------------------
# §7.4 -- the gap ledger (a generated build artifact)
# ---------------------------------------------------------------------------

_EMPTY_DROPPED = DroppedReceiverCounts(total=0, validation_looking=0)


def _run_population(
    recs: list[SurveyRecord],
    index: dict[Qualkey, SurveyRecord],
    stamp: SurveyStamp,
) -> tuple[dict[str, int], dict[str, int]]:
    """Run ``derive_contract`` with every record in ``recs`` as its own
    entry point; return (totals, by_reason) over that population. Used for
    both the whole-surface (1,314 finding-bearing functions, §7.6) and the
    SUPPORTED_TOOLS-only populations."""
    methods_with_no_recorded_gap = 0
    methods_with_gaps = 0
    by_reason: dict[str, int] = {"unresolved_delegate": 0, "no_contract_derived": 0}
    for rec in recs:
        contract = derive_contract(rec.module, rec.qualname, index, stamp=stamp)
        if contract.gaps:
            methods_with_gaps += 1
        else:
            methods_with_no_recorded_gap += 1
        for reason, _name in contract.gaps:
            by_reason[reason] = by_reason.get(reason, 0) + 1
    totals = {
        "methods_attempted": len(recs),
        "methods_with_no_recorded_gap": methods_with_no_recorded_gap,
        "methods_with_gaps": methods_with_gaps,
    }
    return totals, by_reason


def _methods_with_dropped_receiver_call(
    recs: list[SurveyRecord], dropped_receiver_counts: dict[Qualkey, DroppedReceiverCounts]
) -> int:
    count = 0
    for rec in recs:
        counts = dropped_receiver_counts.get((rec.module, rec.qualname), _EMPTY_DROPPED)
        if counts.total > 0:
            count += 1
    return count


def _top_unresolved_from_records(records: list[SurveyRecord]) -> list[dict[str, Any]]:
    """Rank distinct ``unresolved_calls`` names by how many DISTINCT
    functions' ``unresolved_calls`` list contains them (D12) -- a direct
    aggregation over the survey's own field, not over closure-run gaps.
    Names are not class-qualified (§7.1): an entry may collapse unrelated
    same-named helpers on different classes into one row."""
    blocks: dict[str, int] = {}
    for rec in records:
        for name in set(rec.unresolved_calls):
            blocks[name] = blocks.get(name, 0) + 1
    ranked = sorted(blocks.items(), key=lambda item: (-item[1], item[0]))
    return [{"call": name, "blocks_methods": count} for name, count in ranked]


def _reachable_keys(entry_keys: list[Qualkey], index: dict[Qualkey, SurveyRecord]) -> set[Qualkey]:
    reached: set[Qualkey] = set()
    for entry in entry_keys:
        for rec, key, _depth in _walk_closure(entry, index):
            if rec is not None:
                reached.add(key)
    return reached


def _closure_wide_dropped_receiver_counts(
    entry: Qualkey,
    index: dict[Qualkey, SurveyRecord],
    dropped_receiver_counts: dict[Qualkey, DroppedReceiverCounts],
) -> DroppedReceiverCounts:
    """Sum the independent D3 AST pass's per-method counts over an entry
    point's WHOLE transitive ``delegates_to`` closure (round-4 remediation,
    M11 second half) -- not just the entry point's own body.

    Before this fix, ``dropped_receiver_calls_by_method`` looked up
    ``dropped_receiver_counts`` by the entry key alone (own-body-only),
    which silently under-reports every ``SUPPORTED_TOOLS`` method whose real
    dropped-receiver calls live behind a delegate rather than in its own
    body -- exactly the same own-body-only failure mode §7.2's guard-inlining
    closure exists to prevent for guards (see ``test_aspirate_closure_
    reaches_check_containers``), now also fixed for this counter. Reuses
    ``_walk_closure`` -- the same cycle-safe traversal core ``derive_contract``
    uses -- so the two can never silently drift on traversal semantics.
    """
    total = 0
    validation_looking = 0
    for rec, key, _depth in _walk_closure(entry, index):
        if rec is None:
            continue
        counts = dropped_receiver_counts.get(key, _EMPTY_DROPPED)
        total += counts.total
        validation_looking += counts.validation_looking
    return DroppedReceiverCounts(total=total, validation_looking=validation_looking)


def _dropped_receiver_worklist(
    tool_keys: dict[str, Qualkey],
    index: dict[Qualkey, SurveyRecord],
    dropped_receiver_counts: dict[Qualkey, DroppedReceiverCounts],
) -> list[dict[str, Any]]:
    """The third ``top_unresolved`` view (round-4 remediation, M12/Cluster 3/
    B3(e)): the D3 dropped-receiver AST pass is computed correctly but was
    never ranked into a worklist -- this is that worklist. Built from the
    SAME transitive-closure population the D3 pass covers (the
    ``SUPPORTED_TOOLS`` closure), ranked by how many DISTINCT closure
    methods contain at least one call to that attribute name -- the direct
    analogue of ``_top_unresolved_from_records``'s ``blocks_methods``
    semantics, but over the dropped-receiver population (which structurally
    never enters ``unresolved_calls``, so the other two views can never see
    it) rather than over the survey's own recorded gaps. Reuses each
    record's already-computed ``DroppedReceiverCounts.by_attr`` breakdown --
    no second AST pass over PLR source.
    """
    blocks: dict[str, set[Qualkey]] = {}
    for entry in tool_keys.values():
        for rec, key, _depth in _walk_closure(entry, index):
            if rec is None:
                continue
            counts = dropped_receiver_counts.get(key, _EMPTY_DROPPED)
            for attr, n in counts.by_attr:
                if n > 0:
                    blocks.setdefault(attr, set()).add(key)
    ranked = sorted(
        ((attr, len(methods)) for attr, methods in blocks.items()),
        key=lambda item: (-item[1], item[0]),
    )
    return [{"call": attr, "blocks_methods": count} for attr, count in ranked]


def _stamp_to_dict(stamp: SurveyStamp) -> dict[str, Any]:
    def _git_state_to_dict(state: Any) -> dict[str, Any]:
        return {
            "hash": state.hash,
            "branch": state.branch,
            "dirty": state.dirty,
            "dirty_content_id": state.dirty_content_id,
            "provenance_source": state.provenance_source,
            "toplevel": state.toplevel,
        }

    return {
        "plr": _git_state_to_dict(stamp.plr),
        "praxis": _git_state_to_dict(stamp.praxis),
        "pylabrobot_version": stamp.pylabrobot_version,
        "stamped_at": stamp.stamped_at,
        "schema_version": stamp.schema_version,
    }


def build_gap_ledger(
    index: dict[Qualkey, SurveyRecord],
    records: list[SurveyRecord],
    *,
    dropped_receiver_counts: dict[Qualkey, DroppedReceiverCounts],
    stamp: SurveyStamp | None = None,
) -> dict[str, Any]:
    """Build the gap ledger (§7.4) -- a generated build artifact, never
    hand-maintained (decision 7).

    ``totals``/``by_reason``/``top_unresolved.whole_surface`` are computed
    over the whole surface's 1,314 finding-bearing functions (§7.6: "run
    the closure over all 1,314 finding-bearing functions"). ``supported_tools``
    and the two per-method dicts are the SUPPORTED_TOOLS-only figures AC-7.4
    requires published (three commensurable method counts:
    ``methods_attempted``, ``methods_with_no_recorded_gap``,
    ``methods_with_dropped_receiver_call`` -- plus the two per-method
    call-node counts as secondary diagnostics, never a denominator, trap 8).

    ``by_category`` is keyed on ``FAILURE_CATEGORIES`` (§7 task-table note),
    with every value ``None`` in v1 (round-4 remediation, M3 -- previously
    ``0`` for every category, which reads as a MEASUREMENT of zero, not as
    "not applicable"). A gap here only ever produces an UNKNOWN finding
    downstream (reason, not category -- category is required only for
    WILL_FAIL per ``Finding.__post_init__``), and §0 fixes every v1 verdict
    at UNKNOWN, so no gap this module records is EVER classified into a
    FAILURE_CATEGORY in round 1 -- there is no detection mechanism for
    RISK-4's tripwire yet (that only becomes live once ``WILL_FAIL`` is
    first emitted, a future round). The sibling ``by_category_status`` field
    makes that explicit rather than leaving a reader to infer it from six
    identical zeros. The block is still published (schema completeness,
    forward-compatible with a future round that does classify) rather than
    omitted.

    Round-4 remediation (M11): ``totals["methods_with_dropped_receiver_call"]``
    used to be computed over ALL 4,758 indexed records while
    ``methods_attempted`` counted only the 1,314 finding-bearing ones -- a
    population mismatch that let the subset figure exceed its own
    denominator (1976 > 1314). Both are now computed over the SAME
    ``finding_bearing`` population. Separately (M11 second half),
    ``dropped_receiver_calls_by_method``/``validation_looking_dropped_
    receiver_calls_by_method`` are now summed over each ``SUPPORTED_TOOLS``
    method's WHOLE transitive closure (``_closure_wide_dropped_receiver_
    counts``), not just its own body -- see that function's docstring.
    ``top_unresolved`` gains a third view, ``dropped_receiver`` (M12/Cluster
    3/B3(e)): the D3 population ranked into an actual worklist, since it
    structurally never enters ``unresolved_calls`` and so was invisible to
    the other two views.
    """
    if stamp is None:
        stamp = survey_stamp()

    finding_bearing = [rec for rec in records if rec.findings]  # §7.6: 1,314

    whole_totals, whole_by_reason = _run_population(finding_bearing, index, stamp)
    whole_totals["methods_with_dropped_receiver_call"] = _methods_with_dropped_receiver_call(
        finding_bearing, dropped_receiver_counts
    )

    tool_keys: dict[str, Qualkey] = {
        name: resolve_supported_tool(name, index) for name in sorted(SUPPORTED_TOOLS)
    }
    tool_records = [index[key] for key in tool_keys.values()]
    tools_totals, tools_by_reason = _run_population(tool_records, index, stamp)
    tools_totals["methods_with_dropped_receiver_call"] = _methods_with_dropped_receiver_call(
        tool_records, dropped_receiver_counts
    )

    dropped_by_method = {
        name: _closure_wide_dropped_receiver_counts(key, index, dropped_receiver_counts).total
        for name, key in sorted(tool_keys.items())
    }
    validation_looking_by_method = {
        name: _closure_wide_dropped_receiver_counts(
            key, index, dropped_receiver_counts
        ).validation_looking
        for name, key in sorted(tool_keys.items())
    }

    reachable = _reachable_keys(list(tool_keys.values()), index)
    top_whole = _top_unresolved_from_records(records)
    top_tools = _top_unresolved_from_records([index[key] for key in reachable])
    top_dropped_receiver = _dropped_receiver_worklist(tool_keys, index, dropped_receiver_counts)

    # Round-4 remediation (M3): None, not 0 -- a gap ledger never classifies
    # any gap into a FAILURE_CATEGORY in round 1 (see docstring), so a
    # numeric 0 would read as a measurement rather than as "not applicable
    # yet". by_category_status names that explicitly.
    by_category = {category: None for category in sorted(FAILURE_CATEGORIES)}

    return {
        "schema_version": SCHEMA_VERSION,
        "stamp": _stamp_to_dict(stamp),
        "totals": whole_totals,
        "by_reason": dict(sorted(whole_by_reason.items())),
        "by_category": by_category,
        "by_category_status": "not_applicable_v1",
        "top_unresolved": {
            "whole_surface": top_whole,
            "supported_tools_closure": top_tools,
            "dropped_receiver": top_dropped_receiver,
        },
        "supported_tools": {
            "methods_attempted": tools_totals["methods_attempted"],
            "methods_with_no_recorded_gap": tools_totals["methods_with_no_recorded_gap"],
            "methods_with_gaps": tools_totals["methods_with_gaps"],
            "methods_with_dropped_receiver_call": tools_totals["methods_with_dropped_receiver_call"],
            "by_reason": dict(sorted(tools_by_reason.items())),
        },
        "dropped_receiver_calls_by_method": dropped_by_method,
        "validation_looking_dropped_receiver_calls_by_method": validation_looking_by_method,
    }
