"""plr_sema._hand_maintained: the hand-maintained surface registry (spec
260901 §9, task 260901_plr-jit-t9-registry-ratchet, backlog #4835).

**A data module, not an analysis module.** Every hand-typed fact `plr_sema`
(and the packages it draws on) depends on gets exactly one row here: a size
metric, a declared ceiling, and a status. `tests/test_hand_maintained_ratchet.py`
is what turns this data into an enforced ratchet -- this module only holds
the registry plus the small measurement helpers that are cleanly importable
without any `sys.path` surgery. The handful of rows that need AST-reading
(facts embedded in function bodies) or a `scripts/`-directory shim live in
the test module instead (spec §9.1's C7 note) -- see that file's own
docstring for why.

**`--update-baselines`** (spec §9.2, "MEASURE"): a one-off, human-run helper
that prints every row's live count next to its declared ceiling. It never
writes `_hand_maintained.py` itself (§9.2: "the ratchet test itself never
writes" -- and neither does this helper; a human copies numbers into a
reviewable commit). Run it with:

    uv run python -m plr_sema._hand_maintained --update-baselines
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib
import sys
from pathlib import Path
from typing import Literal

REPO_ROOT = Path(__file__).resolve().parents[3]
_TESTS_DIR = Path(__file__).resolve().parents[2] / "tests"
_FAILURE_TAXONOMY_PATH = REPO_ROOT / "training" / "verify" / "failure_taxonomy.py"

#: Spec §9.4: re-baselined once at T9 to `live_rows + 3` (21 + 3 = 24).
#: Fixed after T9 ships -- no further re-baselining without a new
#: adversarial round finding new discovery (§9.4). 260901 T13 added one new
#: live row (HM-23, the Fork D expected-pin literal) -- live_rows moved
#: 21 -> 22, still <= 24, so the cap itself is UNCHANGED: 22 live rows still
#: fit inside the room T9 already reserved, and per §9.4 growth alone is
#: never grounds to widen a cap without a new adversarial-round argument.
BUDGET_CAP = 24


@dataclasses.dataclass(frozen=True, slots=True)
class HandMaintainedSurface:
    """One row of the hand-maintained surface registry (spec §9.1)."""

    id: str
    what: str
    metric: str  # what is counted
    declared: int  # the ceiling
    status: Literal[
        "FROZEN", "CAPPED", "DERIVABLE_NOT_YET", "TARGET_ZERO", "RETIRED"
    ]
    why_not_derived: str  # REQUIRED, non-empty
    breaks_when: str  # REQUIRED, non-empty
    trigger: str = ""  # REQUIRED and non-empty iff status == DERIVABLE_NOT_YET
    #: Either "module:attr" pointing at a zero-arg callable returning the
    #: live count (plain-import form), or the same shape pointing at a
    #: zero-arg callable defined in test_hand_maintained_ratchet.py that
    #: internally AST-reads a specific (source_path, target_symbol) pair
    #: (C7's AST-reading form). Empty string for rows with no live measure
    #: (none currently -- every row is measurable).
    measure: str = ""
    #: D16(a): the recorded high-water mark for rows whose declared ceiling
    #: must monotonically DECREASE after a peak (HM-16). 0 for every other
    #: row. `test_shims_never_grow_after_peak` reads this field directly.
    peak: int = 0


def resolve_measure(import_path: str) -> int:
    """Resolve a `measure` field ("module:attr") to a live int.

    Both the plain-import form and the AST-reading form (C7) resolve the
    same way from here: the string names a zero-arg callable, and this
    function calls it. The two forms differ only in what that callable
    does internally (import a fact vs. AST-parse a fact out of a function
    body) -- never in how it is invoked.

    `test_hand_maintained_ratchet` rows are resolvable from here too (e.g.
    when this module's own `--update-baselines` CLI runs standalone,
    outside pytest) because this inserts the tests directory onto
    `sys.path` before importing it.
    """
    if not import_path:
        raise ValueError("empty measure import path")
    module_name, sep, attr = import_path.partition(":")
    if not sep:
        raise ValueError(
            f"measure path {import_path!r} must be 'module:attr', missing ':'"
        )
    if module_name == "test_hand_maintained_ratchet":
        tests_dir = str(_TESTS_DIR)
        if tests_dir not in sys.path:
            sys.path.insert(0, tests_dir)
    module = importlib.import_module(module_name)
    fn = getattr(module, attr)
    return fn()


# ---------------------------------------------------------------------------
# Measure helpers for rows that are cleanly importable with no sys.path
# shim, no AST-reading, and no cross-boundary import -- HM-8, 9, 10, 12, 13,
# 14, 16, 17, 18, 21.
#
# HM-1 and HM-11 (praxis.*) and HM-5 (training.*) are NOT here even though
# they would otherwise qualify as "plain import path" rows: this module
# lives under `src/plr_sema/`, and `tests/test_import_boundary.py` AST-scans
# every file under that tree (whole-tree `ast.walk`, not just module level)
# for ANY `import praxis`/`verify`/`training`, function-body imports
# included (spec §1.3 AC-1.2 / AC-1.3 -- `plr_sema` must stay corpus- and
# harness-independent). Their measure callables live in
# test_hand_maintained_ratchet.py instead, alongside the scripts/-sourced
# and AST-reading ones -- not a spec deviation, the same C7/D6 "define it in
# the ratchet test module" guidance applies for the identical reason.
# ---------------------------------------------------------------------------


def _measure_hm8() -> int:
    """RETIRED (T7 `3a3a9f00`): the 2-module `inspect.getmembers` allowlist
    this row named was deleted outright, not shrunk. Grep for its
    reintroduction rather than hardcoding 0, so the RETIRED extension of
    `test_frozen_surfaces_are_exact` (measure() == 0 exactly) actually
    detects a reappearance instead of vacuously returning a constant.
    """
    text = _FAILURE_TAXONOMY_PATH.read_text()
    return text.count("inspect.getmembers(")


def _measure_hm9() -> int:
    from plr_sema.check._supported_tools import SUPPORTED_TOOLS

    return len(SUPPORTED_TOOLS)


def _measure_hm10() -> int:
    from coxswain.fft.preconditions.method_contracts import EffectType

    return len(list(EffectType))


def _measure_hm12() -> int:
    from coxswain.fft.preconditions.method_contracts import MethodContract

    return len(dataclasses.fields(MethodContract))


def _measure_hm13() -> int:
    from coxswain.fft.preconditions.method_contracts import METHOD_CONTRACTS

    return len(METHOD_CONTRACTS)


def _measure_hm14() -> int:
    from plr_sema.verdict import REASON_VOCABULARY

    return len(REASON_VOCABULARY)


def _measure_hm16() -> int:
    """Compatibility shim modules under `praxis/backend/utils/plr_static_analysis/`
    (spec §1.2): `from plr_sema.<mod> import *` re-export shims. Round 1 has
    nothing migrated yet, so this is 0 today -- the row exists so the FIRST
    migration is forced through a reviewable ratchet bump.
    """
    shim_dir = REPO_ROOT / "praxis" / "backend" / "utils" / "plr_static_analysis"
    count = 0
    for path in sorted(shim_dir.glob("*.py")):
        if path.name == "__init__.py":
            continue
        text = path.read_text()
        if "from plr_sema." in text and "import *" in text:
            count += 1
    return count


def _git_state_cherry_pick_header():
    tests_dir = str(_TESTS_DIR)
    if tests_dir not in sys.path:
        sys.path.insert(0, tests_dir)
    import test_fork_drift  # noqa: PLC0415 -- deliberate lazy/local import, see module docstring

    return test_fork_drift.parse_cherry_pick_header(test_fork_drift.GIT_STATE_PATH)


def _measure_hm17() -> int:
    """LOC of the cherry-picked git_state.py EXCLUDING the §2.1 provenance
    header (round-6 remediation, R19). Reuses T5's `parse_cherry_pick_header`
    to find the header boundary by scanning for its closing fence, never by
    a hardcoded line count -- a header that gains a line must not silently
    break this row.
    """
    import test_fork_drift  # noqa: PLC0415

    header = _git_state_cherry_pick_header()
    body_lines = test_fork_drift.GIT_STATE_PATH.read_text().splitlines()[
        header.header_line_count :
    ]
    return len(body_lines)


def _measure_hm18() -> int:
    """The two recorded provenance fields (upstream sha256, upstream
    commit) in git_state.py's cherry-pick header. `parse_cherry_pick_header`
    raises if either is absent, so a successful parse always yields 2 --
    this still calls through it rather than hardcoding 2, so a header
    reshaped to drop a field turns this row red via the raise, not via a
    silently-wrong constant.
    """
    header = _git_state_cherry_pick_header()
    return sum(1 for v in (header.upstream_sha256, header.upstream_commit) if v)


def _measure_hm21() -> int:
    """260902 (spec §11.6, SEMA-IR): metric REDEFINED. Pre-increment this
    counted mirrored fields (a judgement about which §3.3 reasons/§7.3
    lookups existed); under the no-drop invariant the mirror is now
    REQUIRED to equal `model_fields`, so that count is a fact about
    upstream, not a judgement, and a "ceiling" on it is meaningless. The
    only remaining judgement is which fields the lowering refuses to
    consume -- the `X` (excluded-with-reason) dispositions in
    `plr_sema.check.ir.DISPOSITIONS`. Under the PRE-increment metric this
    row read 34 (15 OperationNode + 9 ResourceNode + 10
    ProtocolComputationGraph, the full no-drop mirror, spec §11.6); the
    metric changed because the judgement it measured (which fields to
    mirror) no longer exists -- every field now gets a disposition, and the
    disposition table's own exhaustiveness is what `tests/test_ir.py`'s
    AC-11.1 and `tests/test_check_graph_mirror_drift.py` protect, not this
    ratchet. This is the anti-gaming-relevant direction NOTE (§11.6's
    condition iv): counting `X` guards against GROWTH (someone typing a
    new judgement call), but reclassifying a field OUT of `X` -- the
    laundering move -- LOWERS this count, which a growth-guarding ratchet
    reads as safe. `tests/test_ir.py::test_excluded_fields_are_excluded`
    (AC-11.14) is what actually guards that direction, independently of
    this measure.
    """
    from plr_sema.check.ir import EXCLUDED_FIELDS

    return len(EXCLUDED_FIELDS)


def _measure_hm24() -> int:
    """260902 (spec §10.8/§10.10 Q7, tip typestate increment, user decision
    SPLIT): HM-24 is the channel-receiver bridge pattern ALONE (pattern 1
    of the original 6 -- §10.2.5's `self.<attr>[<name>].<method>` shape,
    the one whose failure mode is a SILENT family collapse rather than a
    loud exact-count test failure). One module-level regex constant,
    `plr_sema.derive.receiver_state._BRIDGE_SHAPE_RE`; importing it proves
    it still exists (fails loudly, ImportError, if deleted), and the
    3-group assertion catches a structural reshape (e.g. dropping the
    `<name>` capture group) that a bare existence check would miss.
    """
    from plr_sema.derive.receiver_state import _BRIDGE_SHAPE_RE

    assert _BRIDGE_SHAPE_RE.groups == 3, (
        f"HM-24's bridge-shape pattern changed group count: {_BRIDGE_SHAPE_RE.groups} != 3 "
        f"(attr, name, method) -- update this row's `what`/`breaks_when` before bumping the measure"
    )
    return 1


def _measure_hm25() -> int:
    """260902 (spec §10.8/§10.10 Q7, tip typestate increment, user decision
    SPLIT): HM-25 is the OTHER five patterns from the original 6 -- the
    typestate-anchor property shape (P2), the channel-default idiom (P3a),
    and the three atom productions (BoolView, NullCheck-is-None,
    NullCheck-is-not-None, §10.3.1) -- each of whose failures AC-10.1
    through AC-10.3's exact-count assertions catch loudly, unlike HM-24's
    bridge shape. Measured by importing the five symbols that implement
    them (two in `derive/receiver_state.py`, three atom-kind branches
    inside `check/tipstate.py`'s shared parser, proven live via
    `TipState`'s two atom-bearing members plus the bool-view branch) --
    fails loudly, ImportError/AttributeError, if any is deleted.
    """
    from plr_sema.check.tipstate import TipState, atom_truth
    from plr_sema.derive.receiver_state import _channel_default_idiom, _typestate_anchor

    shape_matchers = (_typestate_anchor, _channel_default_idiom)  # P2, P3a
    # atom_truth's three productions: BoolView, NullCheck(is_none=True),
    # NullCheck(is_none=False) -- proven live by actually exercising all
    # three against TipState.HAS_TIP (any concrete, non-Top state suffices
    # to exercise every branch of the truth table).
    productions = (
        atom_truth(("bool_view", None), TipState.HAS_TIP),
        atom_truth(("null_check", True), TipState.HAS_TIP),
        atom_truth(("null_check", False), TipState.HAS_TIP),
    )
    return len(shape_matchers) + len(productions)


REGISTRY: tuple[HandMaintainedSurface, ...] = (
    HandMaintainedSurface(
        id="HM-1",
        what="PLR_RESOURCE_TYPES class-name set (praxis/common/type_inspection.py:14-56)",
        metric="entries",
        declared=34,
        status="DERIVABLE_NOT_YET",
        why_not_derived=(
            "A hand-typed class-name set; the exception_name_closure fixpoint "
            "machinery exists and is proven on 132 exception classes but is "
            "not yet pointed at Resource/Machine."
        ),
        breaks_when=(
            "PyLabRobot adds, renames, or removes a Resource/Machine subclass "
            "whose name is not (or no longer) reflected in the set."
        ),
        trigger=(
            "Point plr_survey_common.collect_all_classes + the "
            "exception_name_closure fixpoint at Resource/Machine instead of "
            "Exception."
        ),
        measure="test_hand_maintained_ratchet:_measure_hm1",
    ),
    HandMaintainedSurface(
        id="HM-2",
        what=(
            "infer_category_from_name substring rules "
            "(praxis/backend/models/enums/plr_category.py:129+, self-documented BRITTLE)"
        ),
        metric="branches",
        declared=16,
        status="DERIVABLE_NOT_YET",
        why_not_derived=(
            "A documented BRITTLE substring-matching fallback used only when "
            "the real class object (and its category attribute) is "
            "unavailable, e.g. parsing type annotations in strings."
        ),
        breaks_when=(
            "PyLabRobot adds a resource/machine category whose name doesn't "
            "match any existing substring rule, or renames a class so an "
            "existing rule stops matching."
        ),
        trigger=(
            "PLR classes carry a real category attribute; derive by "
            "AST-reading the attribute per class into a table instead of "
            "pattern-matching the name."
        ),
        measure="test_hand_maintained_ratchet:_measure_hm2",
    ),
    HandMaintainedSurface(
        id="HM-3",
        what="validator-name prefixes in _is_validation_looking (scripts/survey_plr_preconditions.py:121-123)",
        metric="prefixes",
        declared=8,
        status="CAPPED",
        why_not_derived=(
            "A heuristic over PLR's own naming conventions for "
            "validator-like helper functions; PLR has no formal marker for "
            "'this method is a precondition check'."
        ),
        breaks_when=(
            "The survey target introduces a validator-shaped helper whose "
            "name doesn't start with one of the six recognized prefixes."
        ),
        measure="test_hand_maintained_ratchet:_measure_hm3",
    ),
    HandMaintainedSurface(
        id="HM-4",
        what="PLR test-file stem heuristic (scripts/plr_survey_common.py:35-40)",
        metric="rules",
        declared=4,
        status="CAPPED",
        why_not_derived=(
            "PLR's own test files have no single naming convention "
            "(STARtests.py, backend_tests.py, test_foo.py all coexist), so "
            "distinguishing real source from test fixtures is a hand-typed "
            "heuristic."
        ),
        breaks_when=(
            "PyLabRobot introduces a fourth test-file naming convention this "
            "heuristic doesn't recognize, silently pulling test-only classes "
            "into a survey."
        ),
        measure="test_hand_maintained_ratchet:_measure_hm4",
    ),
    HandMaintainedSurface(
        id="HM-5",
        what="FAILURE_CATEGORIES (training/verify/failure_taxonomy.py:82-89)",
        metric="categories",
        declared=6,
        status="FROZEN",
        why_not_derived=(
            "Describes our own verification semantics, not anything "
            "PyLabRobot exposes -- there is nothing upstream to derive it "
            "from."
        ),
        breaks_when=(
            "Our own failure taxonomy changes (a category added, removed, "
            "or renamed) without updating this row -- a drift between "
            "plr_sema.telemetry and training/verify/failure_taxonomy.py."
        ),
        measure="test_hand_maintained_ratchet:_measure_hm5",
    ),
    HandMaintainedSurface(
        id="HM-6",
        what="classify_exception module-prefix dispatch (training/verify/failure_taxonomy.py:197,209)",
        metric="prefixes",
        declared=3,
        status="CAPPED",
        why_not_derived=(
            "A hand-typed decision about which of our own packages own "
            "which failure category; not a PLR fact."
        ),
        breaks_when=(
            "A new top-level source of live exceptions is added to the "
            "harness (e.g. a third package prefix) without a corresponding "
            "dispatch branch."
        ),
        measure="test_hand_maintained_ratchet:_measure_hm6",
    ),
    HandMaintainedSurface(
        id="HM-7",
        what="our_names harness-exception map (training/verify/failure_taxonomy.py:241-242)",
        metric="entries",
        declared=3,
        status="DERIVABLE_NOT_YET",
        why_not_derived=(
            "Duplicates the isinstance dispatch in classify_exception by "
            "hand, as a name -> reason string map, since "
            "classify_check_failure only has the class NAME by that point "
            "(the original exception object is gone)."
        ),
        breaks_when=(
            "A fourth harness exception class is added to "
            "classify_exception's isinstance dispatch without a matching "
            "entry in our_names."
        ),
        trigger=(
            "Derive the map from the three classes' own __name__ attributes "
            "instead of hand-typing the mapping."
        ),
        measure="test_hand_maintained_ratchet:_measure_hm7",
    ),
    HandMaintainedSurface(
        id="HM-8",
        what="_plr_exception_class_names module allowlist -- RETIRED (round 4, M5)",
        metric="modules",
        declared=0,
        status="RETIRED",
        why_not_derived=(
            "Trigger FIRED: T7 (commit 3a3a9f00) replaced the 2-module "
            "inspect.getmembers walk with a validated load of "
            "plr_exception_taxonomy.json (11 -> 132 names, 121 newly "
            "visible, none lost). The surface this row named no longer "
            "exists in source."
        ),
        breaks_when=(
            "Someone reintroduces a hand-typed inspect.getmembers "
            "module-allowlist for PLR exception names -- this row's "
            "measure (grepping failure_taxonomy.py for "
            "'inspect.getmembers(') would go nonzero and turn the ratchet "
            "red instead of passing vacuously."
        ),
        measure="plr_sema._hand_maintained:_measure_hm8",
    ),
    HandMaintainedSurface(
        id="HM-9",
        what="SUPPORTED_TOOLS (plr_sema/check/_supported_tools.py; mirrors training/verify/dispatcher.py)",
        metric="tools",
        declared=10,
        status="CAPPED",
        why_not_derived=(
            "Growth of the dynamic execution harness's dispatchable-tool "
            "boundary is a deliberate, reviewed scope decision made in "
            "training/verify/, orthogonal to what plr_sema derives or "
            "checks (T11 decoupled the two -- see the module's own "
            "docstring)."
        ),
        breaks_when=(
            "training.verify.dispatcher.SUPPORTED_TOOLS changes without a "
            "corresponding update to this row (caught structurally by "
            "test_check_graph.py::test_supported_tools_match_upstream, not "
            "by this ratchet)."
        ),
        measure="plr_sema._hand_maintained:_measure_hm9",
    ),
    HandMaintainedSurface(
        id="HM-10",
        what="EffectType enum (coxswain/.../method_contracts.py:18-29)",
        metric="members",
        declared=9,
        status="CAPPED",
        why_not_derived=(
            "Enumerates OUR semantic effect vocabulary for state simulation "
            "(v1 does not simulate effects at all); nothing in PLR maps "
            "1:1 to it."
        ),
        breaks_when=(
            "A new class of state effect needs modeling (e.g. a new "
            "instrument category) before a contract can declare it."
        ),
        measure="plr_sema._hand_maintained:_measure_hm10",
    ),
    HandMaintainedSurface(
        id="HM-11",
        what="PreconditionType enum (praxis/backend/utils/plr_static_analysis/models.py:~500-521)",
        metric="members",
        declared=8,
        status="CAPPED",
        why_not_derived=(
            "A hand-typed enum of state-precondition kinds; a candidate for "
            "derivation from guard `raises` classes once that AST work "
            "(deferred item (c)) lands, but not yet."
        ),
        breaks_when=(
            "A new precondition kind is needed by a contract (hand-written "
            "or derived) that doesn't map to any existing PreconditionType "
            "member."
        ),
        measure="test_hand_maintained_ratchet:_measure_hm11",
    ),
    HandMaintainedSurface(
        id="HM-12",
        what="MethodContract field vocabulary (coxswain/.../method_contracts.py)",
        metric="fields",
        declared=21,
        status="TARGET_ZERO",
        why_not_derived=(
            "The hand-typed schema the 45 hand-written contracts (HM-13) "
            "are instances of; superseded entirely by DerivedContract once "
            "section 7's derivation pipeline is trusted."
        ),
        breaks_when=(
            "A field is added to MethodContract to support a hand-written "
            "contract, growing the vocabulary DerivedContract must "
            "eventually match field-for-field."
        ),
        measure="plr_sema._hand_maintained:_measure_hm12",
    ),
    HandMaintainedSurface(
        id="HM-13",
        what="the 45 MethodContract instances (coxswain/.../method_contracts.py)",
        metric="contracts",
        declared=45,
        status="TARGET_ZERO",
        why_not_derived=(
            "The cautionary case section 9 opens with -- hand-typed PLR "
            "method semantics that grew with no ceiling. Section 7's "
            "derivation pipeline replaces them; section 8's differential "
            "harness measures the replacement."
        ),
        breaks_when=(
            "A 46th hand-written contract is added (count ratchet), or an "
            "existing contract's field values are hand-edited (content-pin "
            "ratchet, C18 -- e.g. requires_tips silently flipped to make a "
            "section 8 disagreement go away)."
        ),
        measure="plr_sema._hand_maintained:_measure_hm13",
    ),
    HandMaintainedSurface(
        id="HM-14",
        what="REASON_VOCABULARY (plr_sema/verdict.py, section 3.3)",
        metric="reasons",
        declared=12,
        status="CAPPED",
        why_not_derived=(
            "Describes our own give-up points in the verdict/telemetry "
            "model; deriving it from our own AST would be circular (we'd "
            "be deriving our own reasons for failing to derive)."
        ),
        breaks_when=(
            "A new class of give-up condition is added to the checker "
            "without a corresponding REASON_VOCABULARY member, or a "
            "withdrawn member like argument_not_static is reinstated "
            "without re-specifying its binding chain (round-4 B4)."
        ),
        measure="plr_sema._hand_maintained:_measure_hm14",
    ),
    HandMaintainedSurface(
        id="HM-15",
        what="_ROOT_EXCEPTION_NAMES (scripts/plr_survey_common.py:32)",
        metric="names",
        declared=2,
        status="FROZEN",
        why_not_derived=(
            "Names Python's own two root exception classes (Exception, "
            "BaseException) -- a language fact, not a PyLabRobot fact. "
            "Zero drift risk."
        ),
        breaks_when=(
            "Never, in practice -- flagged FROZEN precisely because Python "
            "changing its own root exception hierarchy is not a realistic "
            "maintenance event."
        ),
        measure="test_hand_maintained_ratchet:_measure_hm15",
    ),
    HandMaintainedSurface(
        id="HM-16",
        what="compatibility shim modules (spec section 1.2)",
        metric="modules",
        declared=0,
        status="CAPPED",
        why_not_derived=(
            "A byproduct of the praxis -> plr_sema migration itself; the "
            "shim's existence is coupled to praxis's own import sites, not "
            "to anything PLR exposes."
        ),
        breaks_when=(
            "A migrated module's shim is added but never deleted after its "
            "last praxis.* caller migrates, so the count fails to return "
            "to 0 -- or exceeds its recorded peak."
        ),
        measure="plr_sema._hand_maintained:_measure_hm16",
    ),
    HandMaintainedSurface(
        id="HM-17",
        what="picked git_state.py (plr_sema/_provenance/git_state.py, section 2)",
        metric="LOC excluding the section-2.1 provenance header",
        declared=241,
        status="FROZEN",
        why_not_derived=(
            "A verbatim cherry-pick from cisternal (section 2.1); section 5 "
            "tier 1 forbids local edits entirely, so there is nothing to "
            "'derive' -- the whole point is that this file tracks upstream "
            "exactly."
        ),
        breaks_when=(
            "Someone edits the cherry-picked body locally (caught first, "
            "more precisely, by test_fork_drift.py's self-consistency "
            "sha256 check), or the header gains/loses lines in a way that "
            "changes what 'body' means."
        ),
        measure="plr_sema._hand_maintained:_measure_hm17",
    ),
    HandMaintainedSurface(
        id="HM-18",
        what="cherry-pick header recorded hashes (section 5.2)",
        metric="hashes",
        declared=2,
        status="FROZEN",
        why_not_derived=(
            "The two recorded fields (upstream sha256, upstream commit) "
            "are the cherry-pick's own provenance identity -- there is "
            "nothing to derive, they identify what was picked."
        ),
        breaks_when=(
            "A future cherry-pick of a different upstream file uses a "
            "header form that records a different number of identifying "
            "fields."
        ),
        measure="plr_sema._hand_maintained:_measure_hm18",
    ),
    HandMaintainedSurface(
        id="HM-19",
        what="category-keyword pairs table, _NAME_KEYWORD_CATEGORIES (scripts/survey_plr_exceptions.py:66-80)",
        metric="pairs",
        declared=15,
        status="CAPPED",
        why_not_derived=(
            "A heuristic over PLR's exception CLASS NAMES, in the same "
            "spirit as HM-3 -- first-match keyword pairs, not a fact PLR "
            "itself exposes anywhere."
        ),
        breaks_when=(
            "PyLabRobot introduces an exception class whose name doesn't "
            "match any of the recognized keywords, or a keyword needs "
            "re-ordering because a new class matches two keywords "
            "ambiguously."
        ),
        measure="test_hand_maintained_ratchet:_measure_hm19",
    ),
    HandMaintainedSurface(
        id="HM-20",
        what="module-substring category fallback table, _MODULE_SUBSTRING_CATEGORIES (scripts/survey_plr_exceptions.py:83-90)",
        metric="pairs",
        declared=8,
        status="CAPPED",
        why_not_derived=(
            "A heuristic over PLR's MODULE PATH structure, consulted only "
            "on an HM-19 name-keyword miss; same spirit as HM-3/HM-19."
        ),
        breaks_when=(
            "PyLabRobot introduces a new module path whose exception "
            "classes need a category and none of the substring rules "
            "match (falls through to 'uncategorized' rather than "
            "miscategorizing, per the row's own note)."
        ),
        measure="test_hand_maintained_ratchet:_measure_hm20",
    ),
    HandMaintainedSurface(
        id="HM-21",
        what=(
            "REDEFINED 260902 (spec section 11.6, SEMA-IR): which upstream "
            "OperationNode/ResourceNode/ProtocolComputationGraph fields the "
            "analyzer refuses to consume, and why -- the X "
            "(excluded-with-reason) dispositions in "
            "plr_sema.check.ir.DISPOSITIONS. Pre-increment this counted "
            "fields mirrored by check/graph.py (34 under that metric, at "
            "the same live model: 15 OperationNode + 9 ResourceNode + 10 "
            "ProtocolComputationGraph); the judgement that metric measured "
            "no longer exists now that the mirror is total (the no-drop "
            "invariant, section 11.1.4), so the metric was redefined to "
            "what remains hand-maintained rather than ratcheting a count "
            "that is now a fact about upstream, not a judgement."
        ),
        metric="excluded (X-dispositioned) fields",
        declared=5,
        status="CAPPED",
        why_not_derived=(
            "Which fields the analyzer refuses to consume is a judgement "
            "about laundering risk (OperationNode.preconditions/"
            "creates_state and ProtocolComputationGraph.preconditions are "
            "populated by hand-typed TIPS_REQUIRED_METHODS/"
            "TIPS_LOADING_METHODS frozensets that section 8's comparison "
            "targets -- consuming them would launder the analyzer's own "
            "comparison target through CALL.kwargs), not a fact recoverable "
            "from PLR source. Each field's continued presence in the "
            "upstream pydantic model is separately drift-tested (Fork C, "
            "section 5.3, now an exhaustiveness check); the DECISION of "
            "which fields to exclude is hand-maintained, and is "
            "additionally pinned by identity (independent of this table) "
            "by tests/test_ir.py::test_excluded_fields_are_excluded "
            "(AC-11.14) -- because this metric counts X dispositions, "
            "reclassifying a field OUT of X (the laundering move) LOWERS "
            "the count, which a growth-guarding ratchet alone would read "
            "as safe."
        ),
        breaks_when=(
            "A field is reclassified out of X in "
            "plr_sema.check.ir.DISPOSITIONS (caught by "
            "test_excluded_fields_are_excluded, AC-11.14, independently of "
            "this ratchet, precisely because this count would DECREASE and "
            "look safe), or a new field is judged excludable (a reviewable "
            "ratchet-visible diff -- this row's declared ceiling is 5, "
            "live is 3, so two slots of headroom exist before a cap "
            "conversation is needed)."
        ),
        measure="plr_sema._hand_maintained:_measure_hm21",
    ),
    HandMaintainedSurface(
        id="HM-22",
        what=(
            "_TAXONOMY_PATH + the 2-key artifact-validation schema "
            "(training/verify/failure_taxonomy.py:140-153)"
        ),
        metric="validated artifact keys",
        declared=4,
        status="CAPPED",
        why_not_derived=(
            "Our own hand-typed contract for what a trustworthy taxonomy "
            "artifact must contain (version.git_sha, classes); introduced "
            "by T7, registered here per round-4 remediation M5."
        ),
        breaks_when=(
            "The taxonomy artifact's own shape changes (a new required "
            "key, or one of these two keys is renamed) without updating "
            "both the loader and this row."
        ),
        measure="test_hand_maintained_ratchet:_measure_hm22",
    ),
    HandMaintainedSurface(
        id="HM-23",
        what=(
            "EXPECTED_SUBMODULE_PIN, Fork D's expected-pin literal "
            "(plr-sema/tests/test_fork_drift.py, 260901 T13, backlog #4835's "
            "own ratchet applied to T13's new hand-typed surface)"
        ),
        metric="declared pin literals",
        declared=1,
        status="FROZEN",
        why_not_derived=(
            "The whole point of Fork D's tier-1 upstream-drift test is a "
            "fixed value to diff the LIVE external/pylabrobot submodule "
            "HEAD against -- deriving the expectation from the submodule "
            "itself would make the self-consistency check vacuous, the "
            "same reasoning HM-17/HM-18 already apply to the Fork B "
            "cherry-pick header's recorded hashes."
        ),
        breaks_when=(
            "The constant is removed or becomes malformed (not a 40-hex-"
            "char sha) without a corresponding update to Fork D's tier-1 "
            "test, or a second such pin constant is introduced elsewhere "
            "(e.g. for a second surface, T13's own Surface parameter) "
            "without its own registry row."
        ),
        measure="test_hand_maintained_ratchet:_measure_hm23",
    ),
    HandMaintainedSurface(
        id="HM-24",
        what=(
            "tip-typestate channel-receiver bridge shape (spec §10.2.5, "
            "260902 tip typestate increment): the pattern "
            "`self.<attr>[<name>].<method>` matched against every "
            "SurveyRecord.dropped_calls entry, "
            "`plr_sema.derive.receiver_state._BRIDGE_SHAPE_RE`. Split out "
            "of the original single 6-pattern HM-24 per the user's 260902 "
            "Q7 decision (option B): its failure mode differs materially "
            "from the other five patterns (HM-25) -- a silent family "
            "collapse, not a loud exact-count assertion failure."
        ),
        metric="patterns",
        declared=1,
        status="CAPPED",
        why_not_derived=(
            "A syntactic pattern over how PLR is WRITTEN (a specific "
            "attribute-indexing-then-method-call shape), not a fact PLR "
            "records anywhere about itself -- same argument HM-3 makes for "
            "validator-name prefixes."
        ),
        breaks_when=(
            "PLR renames `self.head[c]` to a method accessor "
            "(`self.channel(c)`), or otherwise stops writing the channel "
            "bridge in this subscript-then-attribute-call shape. Fails "
            "CLOSED: the pattern stops matching, `channel_guards`/"
            "`channel_effect` go empty for the affected receiver class, "
            "the tip-requiring/tip-loading families silently empty (only "
            "AC-10.10's own non-empty assertion catches this), and every "
            "verdict for that class reverts to UNKNOWN -- it cannot "
            "produce a wrong verdict, only fewer of them."
        ),
        measure="plr_sema._hand_maintained:_measure_hm24",
    ),
    HandMaintainedSurface(
        id="HM-25",
        what=(
            "tip-typestate front-end syntactic patterns, the other five "
            "(spec §10.2.2/§10.2.3/§10.3.1, 260902 tip typestate "
            "increment): the typestate-anchor property shape (`return "
            "self.<F> is/is not None`, P2), the channel-default idiom "
            "(`<p> = <p> or self.<x> or list(range(len(<q>)))`, P3a), and "
            "the three atom productions (`BoolView`, "
            "`NullCheck(is_none=True)`, `NullCheck(is_none=False)`, "
            "§10.3.1). Split out of the original single 6-pattern HM-24 "
            "per the user's 260902 Q7 decision (option B)."
        ),
        metric="patterns",
        declared=5,
        status="CAPPED",
        why_not_derived=(
            "Syntactic patterns over how PLR/its own analyzer is written "
            "(a property-body shape, an argument-default idiom, three "
            "condition-string grammars), not facts PLR records anywhere "
            "-- same argument HM-3/HM-24 make."
        ),
        breaks_when=(
            "PLR stops writing the `has_tip`-style boolean-view property "
            "in the single-return-Compare shape P2 matches, drops the "
            "`or list(range(len(...)))` idiom P3a matches, or a guard "
            "condition stops parsing under one of the three atom "
            "productions. Fails LOUDLY here (unlike HM-24): "
            "AC-10.1/AC-10.2/AC-10.3's exact-count assertions on the "
            "shipped fixtures go red."
        ),
        measure="plr_sema._hand_maintained:_measure_hm25",
    ),
)


def live_rows(
    registry: tuple[HandMaintainedSurface, ...] = REGISTRY,
) -> tuple[HandMaintainedSurface, ...]:
    """Spec section 9.4: RETIRED rows do not count toward `live_rows`."""
    return tuple(row for row in registry if row.status != "RETIRED")


def _update_baselines() -> None:
    print(f"{'id':6} {'declared':>8} {'live':>8}  status")
    for row in REGISTRY:
        if not row.measure:
            print(f"{row.id:6} {row.declared:>8} {'--':>8}  {row.status} (no measure)")
            continue
        try:
            live = resolve_measure(row.measure)
        except Exception as exc:
            print(f"{row.id:6} {row.declared:>8} {'ERROR':>8}  {exc}")
            continue
        flag = "" if live <= row.declared else "  <-- OVER DECLARED CEILING"
        print(f"{row.id:6} {row.declared:>8} {live:>8}  {row.status}{flag}")
    print(f"\nlive_rows={len(live_rows())}  cap={BUDGET_CAP}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="plr_sema._hand_maintained")
    parser.add_argument(
        "--update-baselines",
        action="store_true",
        help="Print every row's live count next to its declared ceiling. "
        "Never writes this file -- a human copies numbers into a "
        "reviewable commit (spec section 9.2).",
    )
    args = parser.parse_args(argv)
    if args.update_baselines:
        _update_baselines()
        return 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
