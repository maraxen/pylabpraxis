"""D3 (ADR Sec 2.3 / Sec 4.3): the AST import-coverage test.

Wheel spec :316/:329 describes D3 as: "walk the AST of every .py under
<dir>, collect Import/ImportFrom module names starting with 'pylabrobot'
plus the string literals in the machine map, assert that set is a subset
of the contract's module set." Of the three drift detectors named in ADR
Sec 2.3 (D1 shell-injected praxis_git_sha, D2 manifest.json sha256, D3 this
file), D3 is the only one that catches SEMANTIC first-party drift -- an
import or machine-map literal that names a module which does not resolve --
rather than whole-deployment or per-file staleness.

This test parses by path (``ast.parse`` on source text) and never imports
the scanned files as Python modules, so -- per ADR Sec 2.4 -- it needs no
package and never puts ``web-repl/overlay/assets/python`` on ``sys.path``
(that directory's ``praxis/`` shadows the repo's real top-level ``praxis``
package).

WHERE THE CONTRACT COMES FROM (read before editing ``_CONTRACT_MODULES``):
wheel-spec T15 (:325-329) creates a real ``web-repl/tests/plr_contract.py``
-- a module-level tuple of ``(module_path, symbol_name)`` -- and this test
is specified to assert against ITS module set. That file does not exist yet
(a separate, not-yet-scheduled task owns it); this task owns only THIS
file. ``_CONTRACT_MODULES`` below is a deliberate, self-contained stand-in:
the set of pylabrobot module paths T15's own description says the browser
path needs "at minimum", plus every module path this test's own AST walk
currently finds in the real tree, WITH ONE DELIBERATE EXCEPTION -- see next
paragraph. When ``plr_contract.py`` lands, replace ``_CONTRACT_MODULES``
with ``{path for path, _symbol in plr_contract.CONTRACT}`` and delete this
note.

THE KNOWN-STALE ENTRY (task brief, "machine-map subtlety"): today
``web_bridge.py``'s ``_MACHINE_CLASS_MAP`` maps ``"Incubator"`` to
``("pylabrobot.incubator", "Incubator")``. Upstream renamed that module to
``pylabrobot.storage`` (wheel-spec :327 already writes the contract's
Incubator entry as ``pylabrobot.storage.Incubator``, not
``pylabrobot.incubator``). At the current submodule pin
(``d9651e2098cd269fc47e6aff80c9242a82d1b587``) the old name may still
resolve at import time -- but resolving is not what D3 checks; D3 checks
CONTRACT COVERAGE, and the corrected contract does not, and must not, list
``pylabrobot.incubator``. Phase 4's P4.2 fixes the source; this test is
NOT the place to paper over that by adding the stale name to the contract.
So ``test_ast_import_coverage_matches_contract`` below WAS marked
``xfail(strict=True)`` for exactly this one known, tracked reason -- not
because the detector was broken, but because it was correctly detecting a
real, already-documented drift. ``strict=True`` meant that the moment P4.2
landed and fixed the source, this test would start UNEXPECTEDLY PASSING and
CI would fail until the ``xfail`` marker was removed -- so the marker could
not silently outlive the bug it documented. P4.2 has now landed
(``_MACHINE_CLASS_MAP`` extracted to ``experimental/machines.py`` with the
Incubator entry corrected to ``pylabrobot.storage``) and the marker has been
removed accordingly; the test now asserts genuine coverage, not an expected
failure.

THE MACHINE-MAP SUBTLETY, other half (task brief): ``_MACHINE_CLASS_MAP``
is inline in ``web_bridge.py`` today; ADR Sec 4.3 extracts it to
``overlay/assets/python/experimental/machines.py`` in Phase 4, which does
not exist yet (only a ``.gitkeep`` is there). ``_collect_machine_map_literals``
below keys off the ASSIGNMENT NAME (``_MACHINE_CLASS_MAP``), found by
walking the AST of every scanned file looking for an assignment target with
that name -- NOT off a hardcoded file path. It therefore finds the dict
literal wherever it lives, before or after the Phase 4 extraction, with no
test edit required in between.
``test_machine_map_literals_found_regardless_of_file_location`` proves this
directly against a synthetic ``experimental/machines.py``.
"""

from __future__ import annotations

import ast
import shutil
from pathlib import Path

import pytest

_OVERLAY_PYTHON_DIR = Path(__file__).resolve().parents[1] / "overlay" / "assets" / "python"
_OVERLAY_SHIMS_DIR = Path(__file__).resolve().parents[1] / "overlay" / "assets" / "shims"
_OVERLAY_DIRS = (_OVERLAY_PYTHON_DIR, _OVERLAY_SHIMS_DIR)

_MACHINE_MAP_NAME = "_MACHINE_CLASS_MAP"

# See the module docstring's "WHERE THE CONTRACT COMES FROM" section.
_CONTRACT_MODULES = frozenset(
    {
        # pylabrobot.io.{serial,usb,hid,ftdi} -- wheel-spec :327 "at minimum".
        "pylabrobot.io.serial",
        "pylabrobot.io.usb",
        "pylabrobot.io.hid",
        "pylabrobot.io.ftdi",
        # pylabrobot.resources.{...} -- wheel-spec :327 "at minimum", plus
        # the deeper submodules the current source actually imports.
        "pylabrobot.resources",
        "pylabrobot.resources.carrier",
        "pylabrobot.resources.resource_holder",
        "pylabrobot.resources.coordinate",
        # The six experimental machine frontends (_MACHINE_CLASS_MAP module
        # halves), corrected per wheel-spec :327 -- "pylabrobot.storage.
        # Incubator", NOT "pylabrobot.incubator". See the module docstring.
        "pylabrobot.liquid_handling",
        "pylabrobot.plate_reading",
        "pylabrobot.heating_shaking",
        "pylabrobot.shaking",
        "pylabrobot.centrifuge",
        "pylabrobot.storage",
        # Deeper submodules the current shims/web_bridge actually import,
        # beyond plr_contract's "at minimum" list.
        "pylabrobot.liquid_handling.backends",
        "pylabrobot.liquid_handling.backends.hamilton",
        "pylabrobot.plate_reading.clario_star_backend",
    }
)


def _iter_py_files(dirs: tuple[Path, ...] = _OVERLAY_DIRS) -> list[Path]:
    files: list[Path] = []
    for base in dirs:
        if base.is_dir():
            files.extend(sorted(base.rglob("*.py")))
    return files


def _collect_pylabrobot_imports(tree: ast.Module) -> set[str]:
    """Import/ImportFrom module names starting with 'pylabrobot' (wheel-spec
    :316/:329's phrasing, applied literally).
    """
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "pylabrobot" or alias.name.startswith("pylabrobot."):
                    found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            if module and (module == "pylabrobot" or module.startswith("pylabrobot.")):
                found.add(module)
    return found


def _collect_machine_map_literals(tree: ast.Module) -> set[str]:
    """String literals inside any assignment to ``_MACHINE_CLASS_MAP``,
    filtered to ones that look like pylabrobot module paths -- mirroring
    the "starting with 'pylabrobot'" filter already applied on the import
    side, so category names ("LiquidHandler") and class names ("Incubator")
    in the same dict are not mistaken for module paths. Keys off the
    assignment NAME so it finds the dict inline (web_bridge.py today) or
    extracted (experimental/machines.py, Phase 4) without caring which.
    """
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = [node.target]
            value = node.value
        else:
            continue
        if not any(isinstance(t, ast.Name) and t.id == _MACHINE_MAP_NAME for t in targets):
            continue
        for sub in ast.walk(value):
            if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                if sub.value == "pylabrobot" or sub.value.startswith("pylabrobot."):
                    found.add(sub.value)
    return found


def find_uncovered_pylabrobot_references(
    paths: list[Path], contract: frozenset[str]
) -> dict[str, list[Path]]:
    """Parse every path's AST, collect pylabrobot imports + machine-map
    literals, and return {module_name: [referencing files]} for anything
    NOT in ``contract``. Empty dict means full coverage.
    """
    referenced: dict[str, set[Path]] = {}
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        names = _collect_pylabrobot_imports(tree) | _collect_machine_map_literals(tree)
        for name in names:
            referenced.setdefault(name, set()).add(path)
    return {
        name: sorted(files)
        for name, files in referenced.items()
        if name not in contract
    }


def _format_uncovered(uncovered: dict[str, list[Path]]) -> str:
    lines = ["module(s) referenced but not in the contract's module set:"]
    for name in sorted(uncovered):
        files = ", ".join(str(f) for f in uncovered[name])
        lines.append(f"  {name!r} <- {files}")
    return "\n".join(lines)


def test_ast_import_coverage_matches_contract() -> None:
    files = _iter_py_files()
    assert files, f"expected .py files under {_OVERLAY_DIRS!r}"
    uncovered = find_uncovered_pylabrobot_references(files, _CONTRACT_MODULES)
    assert not uncovered, _format_uncovered(uncovered)


def test_ast_import_coverage_catches_injected_bad_import(tmp_path: Path) -> None:
    """Non-vacuousness proof (task brief): copy the real overlay tree,
    inject an import of a module certainly absent from the contract, and
    assert the detector names it. If this test ever passes with an EMPTY
    uncovered set, the detector is not detecting anything.
    """
    dest_python = tmp_path / "python"
    dest_shims = tmp_path / "shims"
    shutil.copytree(_OVERLAY_PYTHON_DIR, dest_python)
    shutil.copytree(_OVERLAY_SHIMS_DIR, dest_shims)

    bogus_module = "pylabrobot.definitely_not_a_real_module_xyz"
    target = dest_python / "web_bridge.py"
    target.write_text(
        target.read_text(encoding="utf-8") + f"\n\nimport {bogus_module}\n",
        encoding="utf-8",
    )

    files = _iter_py_files((dest_python, dest_shims))
    uncovered = find_uncovered_pylabrobot_references(files, _CONTRACT_MODULES)
    assert bogus_module in uncovered
    assert uncovered[bogus_module] == [target]


def test_machine_map_literals_found_regardless_of_file_location(tmp_path: Path) -> None:
    """The machine-map subtlety (task brief): _MACHINE_CLASS_MAP is inline
    in web_bridge.py today and moves to overlay/assets/python/experimental/
    machines.py in Phase 4. The collector keys off the assignment name, not
    a hardcoded path, so it must catch a bogus module literal in a
    synthetic 'extracted' location with no test edit.
    """
    experimental_dir = tmp_path / "experimental"
    experimental_dir.mkdir()
    machines_py = experimental_dir / "machines.py"
    bogus_module = "pylabrobot.this_module_does_not_exist"
    machines_py.write_text(
        "_MACHINE_CLASS_MAP = {\n"
        f'    "Foo": ({bogus_module!r}, "Foo"),\n'
        "}\n",
        encoding="utf-8",
    )

    uncovered = find_uncovered_pylabrobot_references([machines_py], _CONTRACT_MODULES)
    assert bogus_module in uncovered
    assert uncovered[bogus_module] == [machines_py]


def test_machine_map_collector_ignores_non_module_string_literals() -> None:
    """Guards against the false-positive this test would otherwise produce:
    _MACHINE_CLASS_MAP's dict ALSO contains category-name keys ("Incubator")
    and class-name values ("Incubator") that are NOT module paths. Without
    the 'pylabrobot' prefix filter, those would be flagged as uncovered
    modules even though they were never meant to resolve as one.
    """
    tree = ast.parse(
        '_MACHINE_CLASS_MAP = {\n'
        '    "Incubator": ("pylabrobot.storage", "Incubator"),\n'
        '}\n'
    )
    literals = _collect_machine_map_literals(tree)
    assert literals == {"pylabrobot.storage"}
    assert "Incubator" not in literals
