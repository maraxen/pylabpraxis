"""Tests for ``web-repl/scripts/fetch_piplite_wheels.py``.

Network-free: the PyPI JSON lookup and the download are both faked, so these run
in CI and offline. The point of the fetcher is INTEGRITY, and integrity checks
are worth nothing unless they have been seen refusing -- every rejection path
below is exercised, not just the happy one.

Context: ``comm-0.2.3-py3-none-any.whl`` used to be committed under
``web-repl/piplite-wheels/``, which violated R6/R8 (``check_wheel_coherence.py
--check-untracked``: ZERO tracked .whl repo-wide, no allowlist). It is now
fetched from a sha-pinned recipe into gitignored ``web-repl/vendor/``.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import fetch_piplite_wheels as F  # noqa: E402 -- path setup must precede this

_PAYLOAD = b"pretend wheel bytes"
_GOOD_SHA = hashlib.sha256(_PAYLOAD).hexdigest()
_NAME, _VERSION = "demo", "1.2.3"
_FILENAME = "demo-1.2.3-py3-none-any.whl"


def _pin_file(tmp_path: Path, **over) -> Path:
    entry = {
        "name": _NAME,
        "version": _VERSION,
        "filename": _FILENAME,
        "sha256": _GOOD_SHA,
    }
    entry.update(over)
    path = tmp_path / "pins.json"
    path.write_text(json.dumps({"wheels": [entry], "required": [_NAME]}))
    return path


class _FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body
        self._pos = 0

    def read(self, n: int = -1) -> bytes:
        if n is None or n < 0:
            chunk, self._pos = self._body[self._pos:], len(self._body)
            return chunk
        chunk = self._body[self._pos:self._pos + n]
        self._pos += len(chunk)
        return chunk

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def fake_pypi(monkeypatch):
    """Fake both the metadata lookup and the download. Returns a mutable config."""
    cfg = {"published_sha": _GOOD_SHA, "body": _PAYLOAD, "downloads": 0}

    def fake_json(url, timeout=30.0):
        return {
            "urls": [
                {
                    "filename": _FILENAME,
                    "url": f"https://files.pythonhosted.org/{_FILENAME}",
                    "digests": {"sha256": cfg["published_sha"]},
                    "size": len(cfg["body"]),
                }
            ]
        }

    def fake_urlopen(req, timeout=120.0):
        cfg["downloads"] += 1
        return _FakeResponse(cfg["body"])

    monkeypatch.setattr(F, "_http_get_json", fake_json)
    monkeypatch.setattr(F.urllib.request, "urlopen", fake_urlopen)
    return cfg


# --------------------------------------------------------------------------
# Happy path
# --------------------------------------------------------------------------
def test_fetches_and_verifies(tmp_path, fake_pypi):
    dest = tmp_path / "out"
    paths = F.fetch_all(pin_path=_pin_file(tmp_path), dest_dir=dest)
    assert len(paths) == 1
    assert paths[0].read_bytes() == _PAYLOAD
    assert F._sha256_file(paths[0]) == _GOOD_SHA
    assert fake_pypi["downloads"] == 1


def test_verified_file_on_disk_is_not_refetched(tmp_path, fake_pypi):
    pins, dest = _pin_file(tmp_path), tmp_path / "out"
    F.fetch_all(pin_path=pins, dest_dir=dest)
    F.fetch_all(pin_path=pins, dest_dir=dest)
    assert fake_pypi["downloads"] == 1, "second call re-downloaded an already-verified wheel"


def test_force_refetches_even_when_verified(tmp_path, fake_pypi):
    pins, dest = _pin_file(tmp_path), tmp_path / "out"
    F.fetch_all(pin_path=pins, dest_dir=dest)
    F.fetch_all(pin_path=pins, dest_dir=dest, force=True)
    assert fake_pypi["downloads"] == 2


def test_corrupted_file_on_disk_is_refetched_not_trusted(tmp_path, fake_pypi):
    dest = tmp_path / "out"
    dest.mkdir()
    (dest / _FILENAME).write_bytes(b"corrupted")
    paths = F.fetch_all(pin_path=_pin_file(tmp_path), dest_dir=dest)
    assert paths[0].read_bytes() == _PAYLOAD
    assert fake_pypi["downloads"] == 1


# --------------------------------------------------------------------------
# Refusals -- the reason this file exists
# --------------------------------------------------------------------------
def test_pin_and_upstream_sha_disagreement_refuses(tmp_path, fake_pypi):
    """Stale pin, or the index changed. Either way a human decides, not this script."""
    fake_pypi["published_sha"] = "f" * 64
    with pytest.raises(F.FetchError, match="DISAGREE"):
        F.fetch_all(pin_path=_pin_file(tmp_path), dest_dir=tmp_path / "out")


def test_download_not_matching_sha_refuses_and_leaves_no_file(tmp_path, fake_pypi):
    """Pin and PyPI agree, but the bytes on the wire do not match either."""
    fake_pypi["body"] = b"tampered bytes"
    dest = tmp_path / "out"
    with pytest.raises(F.FetchError, match="MISMATCH"):
        F.fetch_all(pin_path=_pin_file(tmp_path), dest_dir=dest)
    # Nothing may be left behind that a later run could mistake for verified --
    # not the final name, and not a stray temp file either.
    assert not (dest / _FILENAME).exists()
    assert list(dest.glob("*")) == [], f"temp debris left behind: {list(dest.glob('*'))}"


def test_missing_sha_from_pypi_refuses(tmp_path, monkeypatch):
    """'Best effort' is not the guarantee this script makes."""
    monkeypatch.setattr(
        F, "_http_get_json",
        lambda url, timeout=30.0: {
            "urls": [{"filename": _FILENAME, "url": "https://x/y", "digests": {}}]
        },
    )
    with pytest.raises(F.FetchError, match="no sha256"):
        F.fetch_all(pin_path=_pin_file(tmp_path), dest_dir=tmp_path / "out")


def test_filename_not_published_refuses_and_lists_alternatives(tmp_path, fake_pypi):
    with pytest.raises(F.FetchError, match="not published"):
        F.fetch_all(
            pin_path=_pin_file(tmp_path, filename="demo-1.2.3-cp99-none-any.whl"),
            dest_dir=tmp_path / "out",
        )


@pytest.mark.parametrize("missing", ["name", "version", "filename", "sha256"])
def test_incomplete_pin_entry_refuses(tmp_path, missing):
    entry = {
        "name": _NAME, "version": _VERSION,
        "filename": _FILENAME, "sha256": _GOOD_SHA,
    }
    del entry[missing]
    path = tmp_path / "pins.json"
    path.write_text(json.dumps({"wheels": [entry]}))
    with pytest.raises(F.FetchError, match=missing):
        F.load_pins(path)


def test_empty_or_absent_pin_file_refuses(tmp_path):
    empty = tmp_path / "empty.json"
    empty.write_text(json.dumps({"wheels": []}))
    with pytest.raises(F.FetchError, match="no wheels"):
        F.load_pins(empty)
    with pytest.raises(F.FetchError, match="not found"):
        F.load_pins(tmp_path / "nope.json")


# --------------------------------------------------------------------------
# The real pin file must stay coherent with the real config.
# --------------------------------------------------------------------------
def test_real_pin_file_matches_piplite_urls():
    """Every pinned wheel must be referenced by PipliteAddon.piplite_urls.

    The pin file drives the fetch and the config drives what jupyterlite indexes.
    If they disagree, the wheel is fetched and then ignored -- which presents at
    runtime as the kernel dying in its worker with no error naming the cause.
    """
    web_repl = Path(__file__).resolve().parents[1]
    pins = F.load_pins(web_repl / "piplite_wheels.json")
    config = json.loads((web_repl / "jupyter_lite_config.json").read_text())
    urls = config["PipliteAddon"]["piplite_urls"]

    for entry in pins["wheels"]:
        assert any(u.endswith(entry["filename"]) for u in urls), (
            f"{entry['filename']} is pinned but no piplite_urls entry references it"
        )
    for url in urls:
        assert any(url.endswith(e["filename"]) for e in pins["wheels"]), (
            f"piplite_urls references {url} but nothing pins it, so nothing fetches it"
        )


def test_required_packages_are_actually_pinned():
    web_repl = Path(__file__).resolve().parents[1]
    pins = F.load_pins(web_repl / "piplite_wheels.json")
    pinned = {e["name"] for e in pins["wheels"]}
    for name in pins.get("required", []):
        assert name in pinned, f"{name!r} is required but not pinned"


def test_no_tracked_wheel_remains_under_piplite_wheels():
    """The directory this replaced must not come back.

    R6/R8 require zero tracked .whl repo-wide; check_wheel_coherence.py enforces
    it globally, and this is the local reminder of why the directory is gone.
    """
    web_repl = Path(__file__).resolve().parents[1]
    legacy = web_repl / "piplite-wheels"
    assert not legacy.exists(), (
        f"{legacy} is back. Wheels belong in gitignored vendor/piplite-wheels/, "
        "fetched by scripts/fetch_piplite_wheels.py -- see its module docstring."
    )
