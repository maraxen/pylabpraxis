#!/usr/bin/env python3
"""Survey every exception class in vendored PyLabRobot: hierarchy, a proposed
failure-mode category, and every call site that raises it.

Feeds training/verify/failure_taxonomy.py, whose "precondition_state"
category currently lumps EVERY real pylabrobot.* exception into one bucket
(see that module's docstring, 260828). This script exists to make that
bucket legible: which specific PLR exceptions can fire, roughly why
(grouped into finer failure modes), and where in PLR's own source they're
actually raised -- so a precondition-synthesis fix (e.g. the open
multi-channel tip-precondition gap in overlay_gen/exec_verify.py's
_precondition_plan) can be built from real trigger conditions instead of
guesswork.

AST, not tree-sitter: the survey target (vendored PyLabRobot) is pure
Python source, so ast.parse gives exact, dependency-free cross-file
inheritance resolution and raise-site line numbers. Tree-sitter earns its
keep on multi-language or incremental-parse targets; neither applies here.

Two passes per the full file set (not one pass per file in isolation):
inheritance closure needs every class definition visible before any file's
raise sites can be reliably matched against "is this actually one of PLR's
own exception classes" (a base class defined in a DIFFERENT file, processed
out of order, must not cause a false negative).

Usage:
    uv run python scripts/survey_plr_exceptions.py
    uv run python scripts/survey_plr_exceptions.py --plr-root external/pylabrobot/pylabrobot \
        --out training/verify/data/plr_exception_taxonomy.json

Output: a JSON report (see --out) plus a human-readable summary table on
stdout: category -> exception classes -> trigger-site counts.
"""

from __future__ import annotations

import argparse
import ast
import json
import logging
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLR_ROOT = PROJECT_ROOT / "external" / "pylabrobot" / "pylabrobot"
DEFAULT_OUT = PROJECT_ROOT / "training" / "verify" / "data" / "plr_exception_taxonomy.json"

#: Sentinel base names that seed the exception-inheritance closure.
_ROOT_EXCEPTION_NAMES = {"Exception", "BaseException"}

#: (category, keyword) pairs checked in order, first match on the class NAME
#: wins. This is a proposed taxonomy for human review, not a load-bearing
#: runtime classifier -- verify/failure_taxonomy.py still buckets all of
#: these under "precondition_state" for execution-verify purposes; this is
#: the finer-grained breakdown WITHIN that bucket.
_NAME_KEYWORD_CATEGORIES: list[tuple[str, str]] = [
    ("tip_state", "Tip"),
    ("volume_state", "Volume"),
    ("volume_state", "Liquid"),
    ("channel_state", "Channel"),
    ("contamination_state", "Contamination"),
    ("location_state", "Location"),
    ("resource_definition", "DefinitionIncomplete"),
    ("occupancy_state", "NoPlate"),
    ("occupancy_state", "HasPlate"),
    ("occupancy_state", "NoFreeSite"),
    ("occupancy_state", "NotAtBucket"),
    ("calibration_state", "Calibrated"),
    ("resource_state", "Resource"),
]

#: Fallback by defining-module path substring, checked if no name keyword hit.
_MODULE_SUBSTRING_CATEGORIES: list[tuple[str, str]] = [
    ("pump_state", "pumps"),
    ("centrifuge_state", "centrifuge"),
    ("plate_reader_state", "plate_reading"),
    ("storage_state", "storage"),
    ("channel_state", "liquid_handling"),
    ("resource_state", "resources"),
]


@dataclass
class ExceptionClass:
    name: str
    module: str
    file: str
    lineno: int
    bases: list[str]
    docstring: str | None
    category: str = "uncategorized"
    trigger_sites: list["TriggerSite"] = field(default_factory=list)


@dataclass
class TriggerSite:
    file: str
    lineno: int
    enclosing_function: str | None
    enclosing_condition: str | None
    #: "raise" (a literal `raise ClassName(...)`) or "dispatch_table" (the
    #: class appears as a dict-literal VALUE -- PLR's own pattern for
    #: firmware error-code -> exception-class lookup, e.g. STAR_backend.py's
    #: `{8: HamiltonNoTipError, ...}` then `raise error_class_map[code](...)`
    #: elsewhere; a literal raise-site scan structurally cannot see this).
    kind: str = "raise"


class _ClassCollector(ast.NodeVisitor):
    """Pass 1: every ClassDef, regardless of whether it's an exception --
    inheritance closure needs the full graph before it can decide that."""

    def __init__(self, module: str, file: str):
        self.module = module
        self.file = file
        self.classes: dict[str, ExceptionClass] = {}

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        bases = [ast.unparse(b) for b in node.bases]
        doc = ast.get_docstring(node)
        self.classes[node.name] = ExceptionClass(
            name=node.name,
            module=self.module,
            file=self.file,
            lineno=node.lineno,
            bases=bases,
            docstring=(doc.strip().splitlines()[0] if doc else None),
        )
        self.generic_visit(node)


class _RaiseCollector(ast.NodeVisitor):
    """Pass 2: every `raise` call, matched against the exception-class
    closure computed after pass 1 across ALL files."""

    def __init__(self, file: str, exception_names: set[str]):
        self.file = file
        self.exception_names = exception_names
        self._func_stack: list[str] = []
        self._condition_stack: list[str] = []
        self.sites: list[tuple[str, TriggerSite]] = []

    def _resolved_name(self, exc_node: ast.expr) -> str | None:
        target = exc_node.func if isinstance(exc_node, ast.Call) else exc_node
        if isinstance(target, ast.Name):
            return target.id
        if isinstance(target, ast.Attribute):
            return target.attr
        return None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._func_stack.append(node.name)
        self.generic_visit(node)
        self._func_stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_If(self, node: ast.If) -> None:
        try:
            cond = ast.unparse(node.test)
        except Exception:  # noqa: BLE001 - best-effort context only
            cond = None
        self._condition_stack.append(cond or "<unparseable>")
        for child in node.body:
            self.visit(child)
        self._condition_stack.pop()
        for child in node.orelse:
            self.visit(child)

    def visit_Raise(self, node: ast.Raise) -> None:
        if node.exc is None:
            return  # bare `raise` (re-raise) -- no new exception identity
        name = self._resolved_name(node.exc)
        if name is None or name not in self.exception_names:
            return
        self.sites.append((
            name,
            TriggerSite(
                file=self.file,
                lineno=node.lineno,
                enclosing_function=self._func_stack[-1] if self._func_stack else None,
                enclosing_condition=self._condition_stack[-1] if self._condition_stack else None,
                kind="raise",
            ),
        ))

    def visit_Dict(self, node: ast.Dict) -> None:
        for value in node.values:
            if isinstance(value, ast.Name) and value.id in self.exception_names:
                self.sites.append((
                    value.id,
                    TriggerSite(
                        file=self.file,
                        lineno=value.lineno,
                        enclosing_function=self._func_stack[-1] if self._func_stack else None,
                        enclosing_condition=None,
                        kind="dispatch_table",
                    ),
                ))
        self.generic_visit(node)


def _module_name(file: Path, root: Path) -> str:
    rel = file.relative_to(root.parent)
    return ".".join(rel.with_suffix("").parts)


def _categorize(exc: ExceptionClass) -> str:
    for category, keyword in _NAME_KEYWORD_CATEGORIES:
        if keyword in exc.name:
            return category
    for category, keyword in _MODULE_SUBSTRING_CATEGORIES:
        if keyword in exc.module:
            return category
    return "uncategorized"


def survey(plr_root: Path) -> list[ExceptionClass]:
    py_files = sorted(
        p for p in plr_root.rglob("*.py")
        # PLR's own test-file naming is inconsistent (STARtests.py,
        # backend_tests.py, test_foo.py) -- match on stem suffix, not a
        # single fixed pattern, to actually exclude test-only mock classes
        # (e.g. _MockError) that would otherwise pollute the real hierarchy.
        if not (p.stem.endswith("test") or p.stem.endswith("tests") or p.stem.startswith("test_"))
    )
    logger.info("scanning %d files under %s", len(py_files), plr_root)

    all_classes: dict[str, ExceptionClass] = {}
    parsed: dict[str, ast.Module] = {}
    for f in py_files:
        try:
            source = f.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(f))
        except (SyntaxError, UnicodeDecodeError) as e:
            logger.warning("skip %s: %s", f, e)
            continue
        parsed[str(f)] = tree
        module = _module_name(f, plr_root)
        collector = _ClassCollector(module, str(f.relative_to(PROJECT_ROOT)))
        collector.visit(tree)
        for name, info in collector.classes.items():
            if name in all_classes:
                logger.warning("duplicate class name %r in %s and %s -- keeping first",
                                name, all_classes[name].file, info.file)
                continue
            all_classes[name] = info

    # Fixpoint closure: a class is an exception if any base is a root
    # sentinel or an already-known exception (handles cross-file chains
    # regardless of file processing order).
    exception_names = set(_ROOT_EXCEPTION_NAMES)
    changed = True
    while changed:
        changed = False
        for name, info in all_classes.items():
            if name in exception_names:
                continue
            if any(base in exception_names for base in info.bases):
                exception_names.add(name)
                changed = True

    exception_classes = {
        name: info for name, info in all_classes.items() if name in exception_names
    }
    logger.info("found %d exception classes (of %d total classes)",
                len(exception_classes), len(all_classes))

    for info in exception_classes.values():
        info.category = _categorize(info)

    for f, tree in parsed.items():
        rel = str(Path(f).relative_to(PROJECT_ROOT))
        raiser = _RaiseCollector(rel, exception_names)
        raiser.visit(tree)
        for name, site in raiser.sites:
            if name in exception_classes:
                exception_classes[name].trigger_sites.append(site)

    return sorted(exception_classes.values(), key=lambda e: (e.category, e.name))


def print_summary(classes: list[ExceptionClass]) -> None:
    by_category: dict[str, list[ExceptionClass]] = defaultdict(list)
    for exc in classes:
        by_category[exc.category].append(exc)

    for category in sorted(by_category):
        members = by_category[category]
        print(f"\n=== {category} ({len(members)} classes) ===")
        for exc in members:
            raises = [s for s in exc.trigger_sites if s.kind == "raise"]
            dispatch = [s for s in exc.trigger_sites if s.kind == "dispatch_table"]
            funcs = sorted({s.enclosing_function for s in raises if s.enclosing_function})
            if raises:
                where = f"raised in: {', '.join(funcs)}"
            elif dispatch:
                where = f"NO literal raise site -- only in {len(dispatch)} error-code dispatch table(s)"
            else:
                where = "no trigger evidence found (declared, unreferenced, or unresolvable)"
            print(f"  {exc.name:<32} {len(raises):>3} raise site(s)  {where}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--plr-root", type=Path, default=DEFAULT_PLR_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    classes = survey(args.plr_root)
    print_summary(classes)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "plr_root": str(args.plr_root.relative_to(PROJECT_ROOT)),
        "total_exception_classes": len(classes),
        "classes": [asdict(exc) for exc in classes],
    }
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"\nwrote {args.out.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
