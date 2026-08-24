"""Tests for ``build_repl``'s ``--base-path`` subpath support.

GitHub Pages serves a project site under ``/<repo>/``, so ``praxis`` deploys at
``https://maraxen.github.io/praxis/``. A notebook that fetches from ``"/"`` reaches
the DOMAIN root there and 404s on every bootstrap file. HOST_ROOT cannot be derived
at runtime -- the kernel is a Web Worker whose global is ``self``, not ``window``, so
there is no document location to read -- which is why this is a build-time rewrite.

The failure this guards against is the "looks healthy, isn't" shape: the site boots,
the notebook opens, and only the first cell fails.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import build_repl  # noqa: E402 -- path setup must precede this


def _notebook(dest: Path, *sources: str) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        json.dumps(
            {
                "cells": [
                    {"cell_type": "code", "source": [s + "\n"], "metadata": {}, "outputs": []}
                    for s in sources
                ],
                "metadata": {},
                "nbformat": 4,
                "nbformat_minor": 5,
            }
        )
    )
    return dest


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("/", "/"),
        ("", "/"),
        ("praxis", "/praxis/"),
        ("/praxis", "/praxis/"),
        ("praxis/", "/praxis/"),
        ("/praxis/", "/praxis/"),
        ("  /praxis/  ", "/praxis/"),
        ("a/b", "/a/b/"),
    ],
)
def test_normalize_base_path(raw, expected):
    assert build_repl.normalize_base_path(raw) == expected


def test_root_base_path_is_a_no_op(tmp_path):
    """The default must not touch anything -- local flows depend on it."""
    nb = _notebook(tmp_path / "files" / "welcome.ipynb", 'HOST_ROOT = "/"')
    before = nb.read_text()
    assert build_repl.apply_base_path(tmp_path, "/") == 0
    assert nb.read_text() == before


def test_rewrites_host_root(tmp_path):
    nb = _notebook(tmp_path / "files" / "welcome.ipynb", 'HOST_ROOT = "/"')
    assert build_repl.apply_base_path(tmp_path, "/praxis/") == 1
    assert 'HOST_ROOT = \\"/praxis/\\"' in nb.read_text()
    build_repl.assert_no_root_host_root(tmp_path, "/praxis/")  # must not raise


def test_rewrites_every_notebook_not_just_the_first(tmp_path):
    """files/ is a directory, not one file -- a loop that stopped early would
    leave later notebooks pointing at the domain root."""
    a = _notebook(tmp_path / "files" / "a.ipynb", 'HOST_ROOT = "/"')
    b = _notebook(tmp_path / "files" / "nested" / "b.ipynb", 'HOST_ROOT = "/"')
    assert build_repl.apply_base_path(tmp_path, "/praxis/") == 2
    for nb in (a, b):
        assert 'HOST_ROOT = \\"/praxis/\\"' in nb.read_text()


def test_leaves_unrelated_source_alone(tmp_path):
    nb = _notebook(
        tmp_path / "files" / "welcome.ipynb",
        'HOST_ROOT = "/"',
        'xhr.open("GET", HOST_ROOT + "bootstrap/praxis_bootstrap.py", False)',
    )
    build_repl.apply_base_path(tmp_path, "/praxis/")
    text = nb.read_text()
    assert "bootstrap/praxis_bootstrap.py" in text, "unrelated source was mangled"


def test_missing_needle_fails_the_build(tmp_path):
    """A silent miss ships a site that boots and 404s on its first cell."""
    _notebook(tmp_path / "files" / "welcome.ipynb", "print(1)")
    with pytest.raises(build_repl.BuildAssertionError, match="no notebook"):
        build_repl.apply_base_path(tmp_path, "/praxis/")


def test_missing_files_dir_fails_the_build(tmp_path):
    with pytest.raises(build_repl.BuildAssertionError, match="does not exist"):
        build_repl.apply_base_path(tmp_path, "/praxis/")


def test_assert_catches_an_unrewritten_notebook(tmp_path):
    """The belt to apply_base_path's braces: if anything reintroduces a root
    HOST_ROOT after the rewrite, the build must still fail."""
    _notebook(tmp_path / "files" / "stale.ipynb", 'HOST_ROOT = "/"')
    with pytest.raises(build_repl.BuildAssertionError, match="still carry"):
        build_repl.assert_no_root_host_root(tmp_path, "/praxis/")


def test_assert_is_a_no_op_at_root(tmp_path):
    _notebook(tmp_path / "files" / "welcome.ipynb", 'HOST_ROOT = "/"')
    build_repl.assert_no_root_host_root(tmp_path, "/")  # must not raise


def test_real_source_notebook_carries_the_needle():
    """Coupling check: the rewrite targets a literal, so the notebook must keep it.

    If welcome.ipynb ever stops containing `HOST_ROOT = "/"` verbatim, the build
    would fail loudly (missing needle) rather than silently -- but this test says
    so at the point of the edit instead.
    """
    src = (Path(__file__).resolve().parents[1] / "files" / "welcome.ipynb").read_text()
    assert 'HOST_ROOT = \\"/\\"' in src
