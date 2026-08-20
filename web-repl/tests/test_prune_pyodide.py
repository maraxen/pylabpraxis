"""Tests for ``build_repl.prune_pyodide_bundle``.

The vendored Pyodide bundle is the FULL distribution -- 307 WASM wheels plus 62
test-suite tarballs -- because ``disablePyPIFallback: true`` makes anything not
hosted unobtainable at runtime rather than merely slow. Pruning is therefore
deliberately narrow, and these tests pin the boundaries: what goes, what stays,
and when the build must refuse to prune at all.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import build_repl  # noqa: E402


def _bundle(tmp_path: Path, packages: dict, files: dict[str, bytes]) -> Path:
    pyo = tmp_path / "static" / "pyodide"
    pyo.mkdir(parents=True)
    (pyo / "pyodide-lock.json").write_text(json.dumps({"packages": packages}))
    for name, blob in files.items():
        (pyo / name).write_bytes(blob)
    return tmp_path


def _pkg(file_name: str, depends: list[str] | None = None) -> dict:
    return {"file_name": file_name, "depends": depends or []}


def test_removes_test_suites_and_their_lock_entries(tmp_path):
    out = _bundle(
        tmp_path,
        {
            "scipy": _pkg("scipy-1.0.whl"),
            "scipy-tests": _pkg("scipy-tests.tar"),
            "test": _pkg("test-1.0.whl"),
        },
        {
            "scipy-1.0.whl": b"x" * 100,
            "scipy-tests.tar": b"y" * 5000,
            "test-1.0.whl": b"z" * 5000,
            "scipy-1.0.whl.metadata": b"m",
            "scipy-tests.tar.metadata": b"m",
        },
    )
    stats = build_repl.prune_pyodide_bundle(out)
    pyo = out / "static" / "pyodide"

    assert not (pyo / "scipy-tests.tar").exists()
    assert not (pyo / "scipy-tests.tar.metadata").exists(), "metadata sibling left behind"
    assert not (pyo / "test-1.0.whl").exists()
    assert (pyo / "scipy-1.0.whl").exists(), "a real package was removed"
    assert (pyo / "scipy-1.0.whl.metadata").exists(), "a kept wheel's metadata was removed"

    lock = json.loads((pyo / "pyodide-lock.json").read_text())
    assert set(lock["packages"]) == {"scipy"}
    assert stats["after"] < stats["before"]


def test_removes_stale_duplicate_wheel(tmp_path):
    """Upstream ships both scipy 1.17.0 and 1.17.1 while the lock names one."""
    out = _bundle(
        tmp_path,
        {"scipy": _pkg("scipy-1.17.1-cp314.whl")},
        {"scipy-1.17.1-cp314.whl": b"new", "scipy-1.17.0-cp314.whl": b"old" * 1000},
    )
    build_repl.prune_pyodide_bundle(out)
    pyo = out / "static" / "pyodide"
    assert (pyo / "scipy-1.17.1-cp314.whl").exists()
    assert not (pyo / "scipy-1.17.0-cp314.whl").exists()


def test_keeps_unreferenced_wheel_with_no_referenced_sibling(tmp_path):
    """Not every unreferenced wheel is stale.

    "Unreferenced by pyodide-lock.json" is NOT on its own a safe deletion rule --
    a wheel fetched directly, by a path other than the lock, would be destroyed.
    Only a duplicate of something the lock DOES name is provably unreachable.
    """
    out = _bundle(
        tmp_path,
        {"scipy": _pkg("scipy-1.0.whl")},
        {"scipy-1.0.whl": b"x", "somethingelse-9.9.whl": b"keepme"},
    )
    build_repl.prune_pyodide_bundle(out)
    assert (out / "static" / "pyodide" / "somethingelse-9.9.whl").exists()


def test_keeps_non_wheel_infrastructure(tmp_path):
    """console.html / package.json / ffi.d.ts are unreferenced and load-bearing."""
    out = _bundle(
        tmp_path,
        {"scipy": _pkg("scipy-1.0.whl")},
        {
            "scipy-1.0.whl": b"x",
            "console.html": b"<html>",
            "package.json": b"{}",
            "ffi.d.ts": b"declare",
        },
    )
    build_repl.prune_pyodide_bundle(out)
    pyo = out / "static" / "pyodide"
    for name in ("console.html", "package.json", "ffi.d.ts"):
        assert (pyo / name).exists(), f"{name} was removed"


def test_refuses_when_a_real_package_depends_on_a_test_suite(tmp_path):
    out = _bundle(
        tmp_path,
        {
            "scipy": _pkg("scipy-1.0.whl", depends=["scipy-tests"]),
            "scipy-tests": _pkg("scipy-tests.tar"),
        },
        {"scipy-1.0.whl": b"x", "scipy-tests.tar": b"y"},
    )
    with pytest.raises(build_repl.BuildAssertionError, match="depend on a test-suite"):
        build_repl.prune_pyodide_bundle(out)
    assert (out / "static" / "pyodide" / "scipy-tests.tar").exists(), "pruned despite refusing"


def test_dependency_guard_normalizes_separators(tmp_path):
    """Upstream's lock mixes separators: keys use hyphens, depends use underscores
    and dots. A raw-string comparison would let `scipy_tests` slip past the guard
    that exists precisely to catch it."""
    out = _bundle(
        tmp_path,
        {
            "scipy": _pkg("scipy-1.0.whl", depends=["scipy_tests"]),
            "scipy-tests": _pkg("scipy-tests.tar"),
        },
        {"scipy-1.0.whl": b"x", "scipy-tests.tar": b"y"},
    )
    with pytest.raises(build_repl.BuildAssertionError, match="depend on a test-suite"):
        build_repl.prune_pyodide_bundle(out)


def test_missing_lock_fails_loudly(tmp_path):
    (tmp_path / "static" / "pyodide").mkdir(parents=True)
    with pytest.raises(build_repl.BuildAssertionError, match="does not exist"):
        build_repl.prune_pyodide_bundle(tmp_path)


def test_pruned_lock_stays_self_consistent(tmp_path):
    """Every surviving entry must still resolve to a file on disk."""
    out = _bundle(
        tmp_path,
        {
            "numpy": _pkg("numpy-1.0.whl"),
            "scipy": _pkg("scipy-1.0.whl", depends=["numpy"]),
            "scipy-tests": _pkg("scipy-tests.tar"),
        },
        {"numpy-1.0.whl": b"n", "scipy-1.0.whl": b"s", "scipy-tests.tar": b"t"},
    )
    build_repl.prune_pyodide_bundle(out)
    pyo = out / "static" / "pyodide"
    lock = json.loads((pyo / "pyodide-lock.json").read_text())
    for name, meta in lock["packages"].items():
        assert (pyo / meta["file_name"]).exists(), f"{name} dangles after prune"


def test_real_dist_has_no_test_suites_left():
    """Coherence against the actual build, when one exists."""
    pyo = Path(__file__).resolve().parents[1] / "dist" / "static" / "pyodide"
    if not (pyo / "pyodide-lock.json").is_file():
        pytest.skip("no dist/ built")
    lock = json.loads((pyo / "pyodide-lock.json").read_text())
    leftovers = [k for k in lock["packages"] if k.endswith("-tests") or k == "test"]
    assert leftovers == [], f"test suites survived the prune: {leftovers[:5]}"
    missing = [
        (k, v["file_name"])
        for k, v in lock["packages"].items()
        if not (pyo / v["file_name"]).exists()
    ]
    assert missing == [], f"lock references missing files after prune: {missing[:5]}"
