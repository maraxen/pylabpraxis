"""Fetch the pinned piplite wheels into ``web-repl/vendor/piplite-wheels/``.

The recipe half of ``web-repl/piplite_wheels.json``. Deliberately mirrors
``fetch_pyodide.py``: resolve a pinned artifact from an upstream API that
publishes its own sha256, stream-download while hashing, verify, and only then
rename into place. A failed or interrupted fetch can never be mistaken for a
verified one, because nothing is ever written to the final filename directly.

WHY THIS EXISTS RATHER THAN A COMMITTED WHEEL
---------------------------------------------
``check_wheel_coherence.py --check-untracked`` implements R6/R8: ZERO tracked
``.whl`` files repo-wide, no allowlist. That is not incidental strictness -- ADR
Sec 4.3 considered a name-scoped allowlist and rejected it, and the ADR retired
the hand-committed pylibftdi binary with the phrase "the hand-committed binary
with no recipe is retired, not relocated."

``comm-0.2.3-py3-none-any.whl`` was committed to ``web-repl/piplite-wheels/`` on
260819 to fix a real defect (every boot silently fetching comm from PyPI), which
put the tree in violation of that rule -- caught 260820 when
``--check-untracked`` was re-run. This script resolves the conflict in the
direction the ADR already chose once: keep the offline-boot guarantee, drop the
tracked binary, and make the wheel reproducible from a sha-pinned recipe.

The build-time network dependency is not a new class of dependency: the build
already fetches a ~430 MB Pyodide tarball from GitHub Releases. Both cache under
``web-repl/vendor/``. Offline *runtime* -- the property the ``--offline`` gate
actually tests -- is untouched.

INTEGRITY: PyPI's JSON API publishes ``digests.sha256`` per file. The download is
checked against BOTH that published digest and the sha pinned in
``piplite_wheels.json``; a disagreement between those two is itself an error,
because it means either the pin is stale or the index changed under us.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
WEB_REPL_ROOT = _THIS_FILE.parents[1]
DEFAULT_PIN_PATH = WEB_REPL_ROOT / "piplite_wheels.json"
DEFAULT_DEST_DIR = WEB_REPL_ROOT / "vendor" / "piplite-wheels"

PYPI_JSON_URL = "https://pypi.org/pypi/{name}/{version}/json"
_CHUNK_SIZE = 1 << 16  # wheels here are kilobytes, not hundreds of megabytes
_USER_AGENT = "praxis-fetch-piplite-wheels/1"

logger = logging.getLogger("fetch_piplite_wheels")


class FetchError(RuntimeError):
    """Raised on any resolution, transport, or integrity failure."""


def load_pins(pin_path: Path = DEFAULT_PIN_PATH) -> dict:
    if not pin_path.is_file():
        raise FetchError(f"pin file not found: {pin_path}")
    data = json.loads(pin_path.read_text())
    wheels = data.get("wheels")
    if not isinstance(wheels, list) or not wheels:
        raise FetchError(f"{pin_path} declares no wheels")
    for entry in wheels:
        missing = [k for k in ("name", "version", "filename", "sha256") if not entry.get(k)]
        if missing:
            raise FetchError(f"{pin_path}: wheel entry {entry!r} is missing {missing}")
    return data


def _http_get_json(url: str, *, timeout: float = 30.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - fixed https host
            return json.loads(resp.read())
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        raise FetchError(f"GET {url} failed: {exc}") from exc


def resolve_from_pypi(name: str, version: str, filename: str) -> tuple[str, str, int]:
    """Return ``(url, published_sha256, size)`` for *filename* of *name*==*version*."""
    payload = _http_get_json(PYPI_JSON_URL.format(name=name, version=version))
    for file_info in payload.get("urls", []):
        if file_info.get("filename") == filename:
            digest = (file_info.get("digests") or {}).get("sha256")
            if not digest:
                raise FetchError(
                    f"PyPI published no sha256 for {filename}. Refusing to fetch: "
                    "this script's integrity guarantee is 'verified', not 'best effort'."
                )
            return file_info["url"], digest, int(file_info.get("size", 0))
    available = [f.get("filename") for f in payload.get("urls", [])]
    raise FetchError(
        f"{filename} is not published for {name}=={version}. Available: {available}"
    )


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(_CHUNK_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def download_and_verify(url: str, expected_sha256: str, dest_dir: Path, *, timeout: float = 120.0):
    """Stream *url* to a temp file in *dest_dir*, hashing as it goes.

    Never writes the final filename; the caller renames on success only.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=".piplite-", suffix=".whl.tmp", dir=str(dest_dir))
    tmp_path = Path(tmp_name)
    h = hashlib.sha256()
    written = 0
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    try:
        with os.fdopen(fd, "wb") as out, urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            while True:
                chunk = resp.read(_CHUNK_SIZE)
                if not chunk:
                    break
                out.write(chunk)
                h.update(chunk)
                written += len(chunk)
            out.flush()
            os.fsync(out.fileno())
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        tmp_path.unlink(missing_ok=True)
        raise FetchError(f"download failed: GET {url}: {exc}") from exc
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise

    actual = h.hexdigest()
    if actual != expected_sha256:
        tmp_path.unlink(missing_ok=True)
        raise FetchError(
            f"sha256 MISMATCH for {url}: expected {expected_sha256}, got {actual} "
            f"({written} bytes). Refusing to publish a corrupted or tampered download."
        )
    return tmp_path, written


def fetch_one(entry: dict, dest_dir: Path, *, force: bool = False) -> Path:
    name, version = entry["name"], entry["version"]
    filename, pinned_sha = entry["filename"], entry["sha256"]
    dest = dest_dir / filename

    if dest.is_file() and not force:
        on_disk = _sha256_file(dest)
        if on_disk == pinned_sha:
            logger.info("already vendored, sha256 verified: %s", dest)
            return dest
        logger.warning(
            "%s exists but sha256 does not match the pin (disk=%s pinned=%s) -- re-fetching",
            dest, on_disk, pinned_sha,
        )

    url, published_sha, size = resolve_from_pypi(name, version, filename)
    if published_sha != pinned_sha:
        # Do not "trust upstream and continue". A disagreement here means either
        # piplite_wheels.json is stale or the index changed; both need a human.
        raise FetchError(
            f"pin/upstream sha256 DISAGREE for {filename}: piplite_wheels.json pins "
            f"{pinned_sha}, PyPI publishes {published_sha}. Either the pin is stale "
            "(update version + sha256 together) or the artifact changed. Refusing to "
            "guess which."
        )

    tmp_path, written = download_and_verify(url, pinned_sha, dest_dir)
    os.replace(tmp_path, dest)
    # mkstemp creates 0600; this is a build input that gets copied into a served
    # tree, so give it ordinary read permissions rather than owner-only.
    dest.chmod(0o644)
    logger.info(
        "vendored %s (%d bytes, sha256=%s) -> %s", filename, written, pinned_sha, dest
    )
    if size and written != size:
        logger.warning("size differs from PyPI metadata (%d vs %d)", written, size)
    return dest


def fetch_all(*, pin_path: Path = DEFAULT_PIN_PATH, dest_dir: Path = DEFAULT_DEST_DIR,
              force: bool = False) -> list[Path]:
    pins = load_pins(pin_path)
    return [fetch_one(entry, dest_dir, force=force) for entry in pins["wheels"]]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pin-file", type=Path, default=DEFAULT_PIN_PATH)
    parser.add_argument("--dest-dir", type=Path, default=DEFAULT_DEST_DIR)
    parser.add_argument("--force", action="store_true", help="re-download even if verified on disk")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
    try:
        paths = fetch_all(pin_path=args.pin_file, dest_dir=args.dest_dir, force=args.force)
    except FetchError as exc:
        logger.error("FETCH FAILED: %s", exc)
        return 1
    logger.info("OK: %d wheel(s) vendored in %s", len(paths), args.dest_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
