"""Tests for ``build_repl.stamp_loader_shas`` -- the build half of the loader pin.

The runtime half (praxis_bootstrap refusing a tampered or unpinned loader) is
covered in ``test_praxis_bootstrap_loader.py``. This file covers the half that
puts the expectation there in the first place.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import build_repl  # noqa: E402 -- path setup must precede this

MARKER = build_repl.LOADER_SHA_MARKER


def _fake_tree(tmp_path: Path, *, marker_lines: int = 1) -> tuple[Path, Path]:
    src_dir = tmp_path / "bootstrap"
    src_dir.mkdir()
    (src_dir / "stages.py").write_text("# stages\n")
    (src_dir / "transport.py").write_text("# transport\n")
    body = ["import builtins"]
    body += [f"_LOADER_MODULE_SHA256 = {{}}  {MARKER}"] * marker_lines
    body.append("def f(): pass")
    boot = tmp_path / "praxis_bootstrap.py"
    boot.write_text("\n".join(body) + "\n")
    return boot, src_dir


def test_stamps_the_real_sha_of_each_loader(tmp_path):
    boot, src_dir = _fake_tree(tmp_path)
    shas = build_repl.stamp_loader_shas(boot, src_dir)

    for name in build_repl.LOADER_MODULES:
        expected = hashlib.sha256((src_dir / name).read_bytes()).hexdigest()
        assert shas[name] == expected
        assert expected in boot.read_text()
    assert "_LOADER_MODULE_SHA256 = {}" not in boot.read_text()


def test_stamped_file_is_valid_python_and_parses_to_the_right_dict(tmp_path):
    """The stamp is executed as code at boot; a syntactically clever string that
    does not actually evaluate to the intended dict would be worse than nothing.
    """
    boot, src_dir = _fake_tree(tmp_path)
    shas = build_repl.stamp_loader_shas(boot, src_dir)

    namespace: dict = {}
    exec(compile(boot.read_text(), "stamped", "exec"), namespace)  # noqa: S102 - the point
    assert namespace["_LOADER_MODULE_SHA256"] == shas


def test_stamping_is_idempotent(tmp_path):
    """A rebuild must replace the value, never append a second one."""
    boot, src_dir = _fake_tree(tmp_path)
    build_repl.stamp_loader_shas(boot, src_dir)
    first = boot.read_text()
    build_repl.stamp_loader_shas(boot, src_dir)
    assert boot.read_text() == first
    assert first.count(MARKER) == 1


def test_restamps_when_a_loader_changes(tmp_path):
    """A stale pin must not survive a rebuild -- that would fail the boot closed
    for a file that is legitimately new."""
    boot, src_dir = _fake_tree(tmp_path)
    build_repl.stamp_loader_shas(boot, src_dir)
    old_sha = hashlib.sha256(b"# stages\n").hexdigest()
    assert old_sha in boot.read_text()

    (src_dir / "stages.py").write_text("# stages, edited\n")
    build_repl.stamp_loader_shas(boot, src_dir)
    new_sha = hashlib.sha256(b"# stages, edited\n").hexdigest()
    assert new_sha in boot.read_text()
    assert old_sha not in boot.read_text()


def test_missing_marker_fails_the_build(tmp_path):
    """Silently skipping the stamp would surface later as a confusing runtime
    'no pinned sha256' refusal; the build is where it should be caught."""
    boot, src_dir = _fake_tree(tmp_path, marker_lines=0)
    with pytest.raises(build_repl.BuildAssertionError, match="exactly one"):
        build_repl.stamp_loader_shas(boot, src_dir)


def test_duplicate_marker_fails_the_build(tmp_path):
    boot, src_dir = _fake_tree(tmp_path, marker_lines=2)
    with pytest.raises(build_repl.BuildAssertionError, match="exactly one"):
        build_repl.stamp_loader_shas(boot, src_dir)


def test_missing_loader_source_fails_the_build(tmp_path):
    boot, src_dir = _fake_tree(tmp_path)
    (src_dir / "transport.py").unlink()
    with pytest.raises(build_repl.BuildError, match="transport.py"):
        build_repl.stamp_loader_shas(boot, src_dir)


def test_built_dist_is_stamped_and_matches_what_it_serves():
    """End-to-end coherence on the real tree, when a dist/ exists.

    The pin is worthless if it names a hash of something other than the file the
    browser will actually fetch.
    """
    web_repl = Path(__file__).resolve().parents[1]
    dist_boot = web_repl / "dist" / "bootstrap"
    if not dist_boot.is_dir():
        pytest.skip("no dist/ built")

    namespace: dict = {}
    text = (dist_boot / "praxis_bootstrap.py").read_text()
    line = next(ln for ln in text.splitlines() if MARKER in ln)
    exec(compile(line, "stamped", "exec"), namespace)  # noqa: S102
    pinned = namespace["_LOADER_MODULE_SHA256"]

    assert set(pinned) == set(build_repl.LOADER_MODULES)
    for name, sha in pinned.items():
        served = hashlib.sha256((dist_boot / name).read_bytes()).hexdigest()
        assert sha == served, (
            f"dist/bootstrap/{name} is pinned to {sha} but the file served is "
            f"{served}. The browser would refuse to boot."
        )
