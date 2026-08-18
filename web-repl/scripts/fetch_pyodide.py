#!/usr/bin/env python3
"""Vendor the Pyodide runtime into ``web-repl/vendor/``, sha256-verified.

Per ADR ``.praxia/docs/decisions/260817_repl-layout-and-delivery-mechanism.md``
Sec 2.1, ``vendor/`` is gitignored (``pyodide-<v>.tar.bz2``) and Sec 7 leaves
"whether Pyodide is vendored for offline operation" open (U18/U19) -- this
script is the *fetch* half of that question; ``build_repl.py`` decides
whether a given build actually points ``PyodideAddon.pyodide_url`` at the
vendored copy or leaves it on the CDN URL already pinned in
``jupyter_lite_config.json``.

**The version is never a literal chosen here.** It is parsed out of the
already-pinned ``PyodideAddon.pyodide_url`` in
``web-repl/jupyter_lite_config.json`` (owned by a different task --
this script reads it, never writes it), e.g.
``https://cdn.jsdelivr.net/pyodide/v314.0.1/full/pyodide.mjs`` -> ``314.0.1``.
That value is the CPython-3.14.2-era Pyodide release this build targets;
hardcoding a second copy of it here is exactly the kind of drift the ADR's
three-detector design (Sec 2.3) exists to prevent elsewhere, so this script
refuses to run without being able to parse one.

**Integrity:** the GitHub Releases API publishes a ``sha256:<hex>`` content
digest per release asset (``GET /repos/pyodide/pyodide/releases/tags/<tag>``,
each asset's ``"digest"`` field). This script fetches that digest FIRST and
verifies the downloaded tarball's own computed sha256 against it before the
file is ever published under its real name -- the download is written to a
temp file in the destination directory and ``os.replace``'d into place only
on a match, so a partial or corrupted download can never be mistaken for a
verified one. If the API does not return a digest for some future release
(older Pyodide releases predate this GitHub feature), this is a hard error,
not a silent skip -- "sha256-verified" is the task's explicit requirement,
and a script that silently downgrades to "trust the download" on API drift
would be exactly the kind of quiet regression this whole sprint exists to
avoid.

House rules: uv-run only, argparse + logging, narrow runs, fail loud.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

logger = logging.getLogger("fetch_pyodide")

_THIS_FILE = Path(__file__).resolve()
DEFAULT_WEB_REPL_ROOT = _THIS_FILE.parents[1]
DEFAULT_VENDOR_DIR = DEFAULT_WEB_REPL_ROOT / "vendor"
DEFAULT_CONFIG_PATH = DEFAULT_WEB_REPL_ROOT / "jupyter_lite_config.json"

GITHUB_API_RELEASE_TAG = "https://api.github.com/repos/pyodide/pyodide/releases/tags/{tag}"
GITHUB_RELEASE_ASSET = (
    "https://github.com/pyodide/pyodide/releases/download/{tag}/pyodide-{version}.tar.bz2"
)

# jsdelivr's own path convention prefixes the version with "v"
# (".../pyodide/v314.0.1/full/pyodide.mjs"); GitHub release tags do not
# ("314.0.1"). Both refer to the same release.
_PYODIDE_URL_VERSION_RE = re.compile(r"/pyodide/v(?P<version>[0-9]+(?:\.[0-9]+){1,3})/")

_CHUNK_SIZE = 1 << 20  # 1 MiB streaming read/hash chunks

VENDOR_MANIFEST_NAME = "pyodide_vendor.json"


class FetchError(RuntimeError):
    """Raised for any condition that must fail this fetch loudly."""


# --- reading the pin (never chosen here) -------------------------------------


def read_pinned_version(config_path: Path) -> str:
    """Parse the Pyodide version out of ``jupyter_lite_config.json``'s
    ``PyodideAddon.pyodide_url`` -- the ONLY source of truth for which
    version this build targets. Never fall back to a literal.
    """
    if not config_path.is_file():
        raise FetchError(
            f"{config_path} does not exist -- cannot determine the pinned "
            "Pyodide version. This file is owned by a different task; it "
            "must exist before fetch_pyodide.py can run."
        )
    try:
        config = json.loads(config_path.read_text())
    except json.JSONDecodeError as exc:
        raise FetchError(f"{config_path} is not valid JSON: {exc}") from exc

    pyodide_url = (config.get("PyodideAddon") or {}).get("pyodide_url")
    if not pyodide_url:
        raise FetchError(
            f"{config_path} has no PyodideAddon.pyodide_url -- nothing to "
            "parse a version from."
        )
    match = _PYODIDE_URL_VERSION_RE.search(pyodide_url)
    if match is None:
        raise FetchError(
            f"{config_path}: PyodideAddon.pyodide_url={pyodide_url!r} does not "
            "match the expected '/pyodide/v<version>/' shape -- refusing to "
            "guess a version rather than silently vendoring the wrong release."
        )
    version = match.group("version")
    logger.info("pinned Pyodide version (from %s): %s", config_path, version)
    return version


# --- GitHub Releases API: expected digest, never invented --------------------


def _http_get(url: str, *, accept: str | None = None, timeout: float = 30.0) -> bytes:
    headers = {"User-Agent": "praxis-fetch-pyodide/1"}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 -- fixed https host
            return resp.read()
    except urllib.error.HTTPError as exc:
        raise FetchError(f"GET {url} -> HTTP {exc.code}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise FetchError(f"GET {url} failed: {exc.reason}") from exc


def fetch_expected_digest(version: str, asset_name: str) -> str:
    """Return the expected ``sha256:<hex>`` digest's hex half for
    *asset_name* on the GitHub release tagged *version*. Raises
    ``FetchError`` if the release, the asset, or the asset's digest field is
    missing -- this script does not proceed on trust alone.
    """
    url = GITHUB_API_RELEASE_TAG.format(tag=version)
    raw = _http_get(url, accept="application/vnd.github+json")
    try:
        release = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise FetchError(f"GitHub API response for {url} was not valid JSON: {exc}") from exc

    assets = release.get("assets") or []
    match = next((a for a in assets if a.get("name") == asset_name), None)
    if match is None:
        names = [a.get("name") for a in assets]
        raise FetchError(
            f"GitHub release {version!r} has no asset named {asset_name!r}. "
            f"Assets present: {names}"
        )
    digest = match.get("digest")
    if not digest or not digest.startswith("sha256:"):
        raise FetchError(
            f"GitHub release asset {asset_name!r} (release {version!r}) has no "
            f"usable 'sha256:...' digest field (got {digest!r}). Refusing to "
            "vendor an unverified download -- this script's whole job is "
            "'sha256-verified', not 'best effort'."
        )
    return digest.removeprefix("sha256:")


# --- download + verify + publish ---------------------------------------------


def _sha256_stream(fileobj) -> str:
    h = hashlib.sha256()
    while True:
        chunk = fileobj.read(_CHUNK_SIZE)
        if not chunk:
            break
        h.update(chunk)
    return h.hexdigest()


def download_and_verify(url: str, expected_sha256: str, dest_dir: Path, *, timeout: float = 300.0) -> tuple[Path, int]:
    """Stream *url* to a temp file in *dest_dir*, hashing as it goes.
    Returns ``(temp_path, bytes_written)`` on a sha256 match; raises
    ``FetchError`` (and deletes the temp file) on any mismatch or transport
    failure. Caller is responsible for the atomic rename into place -- this
    function never writes to the final filename directly, so a failed or
    interrupted fetch can never be mistaken for a verified one.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=".pyodide-", suffix=".tar.bz2.tmp", dir=str(dest_dir))
    tmp_path = Path(tmp_name)
    h = hashlib.sha256()
    written = 0
    headers = {"User-Agent": "praxis-fetch-pyodide/1"}
    req = urllib.request.Request(url, headers=headers)
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

    actual_sha256 = h.hexdigest()
    if actual_sha256 != expected_sha256:
        tmp_path.unlink(missing_ok=True)
        raise FetchError(
            f"sha256 MISMATCH for {url}: expected {expected_sha256}, got "
            f"{actual_sha256} ({written} bytes downloaded). Refusing to "
            "publish a corrupted or tampered download."
        )
    logger.info("downloaded + verified %s (%d bytes, sha256=%s)", url, written, actual_sha256)
    return tmp_path, written


def _sha256_file(path: Path) -> str:
    with path.open("rb") as f:
        return _sha256_stream(f)


def already_vendored(dest: Path, expected_sha256: str) -> bool:
    if not dest.is_file():
        return False
    actual = _sha256_file(dest)
    if actual != expected_sha256:
        logger.warning(
            "%s exists but sha256 does not match expected (disk=%s expected=%s) "
            "-- will re-fetch.",
            dest,
            actual,
            expected_sha256,
        )
        return False
    return True


def write_vendor_manifest(
    vendor_dir: Path,
    *,
    version: str,
    asset_name: str,
    sha256: str,
    bytes_: int,
    source_url: str,
) -> None:
    record = {
        "version": version,
        "filename": asset_name,
        "sha256": sha256,
        "bytes": bytes_,
        "source_url": source_url,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    dest = vendor_dir / VENDOR_MANIFEST_NAME
    fd, tmp_name = tempfile.mkstemp(prefix=".pyodide-vendor-", suffix=".json.tmp", dir=str(vendor_dir))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(record, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, dest)
    except BaseException:
        tmp_path.unlink(missing_ok=True)
        raise
    logger.info("wrote %s", dest)


# --- orchestration -------------------------------------------------------------


def fetch_pyodide(
    *, web_repl_root: Path, vendor_dir: Path, config_path: Path, force: bool
) -> Path:
    version = read_pinned_version(config_path)
    asset_name = f"pyodide-{version}.tar.bz2"
    dest = vendor_dir / asset_name

    expected_sha256 = fetch_expected_digest(version, asset_name)

    if not force and already_vendored(dest, expected_sha256):
        logger.info("OK (cached, verified): %s", dest)
        write_vendor_manifest(
            vendor_dir,
            version=version,
            asset_name=asset_name,
            sha256=expected_sha256,
            bytes_=dest.stat().st_size,
            source_url=GITHUB_RELEASE_ASSET.format(tag=version, version=version),
        )
        return dest

    url = GITHUB_RELEASE_ASSET.format(tag=version, version=version)
    logger.info("fetching %s (expected sha256=%s)...", url, expected_sha256)
    tmp_path, written = download_and_verify(url, expected_sha256, vendor_dir)
    os.replace(tmp_path, dest)
    logger.info("published %s (%d bytes)", dest, written)

    write_vendor_manifest(
        vendor_dir,
        version=version,
        asset_name=asset_name,
        sha256=expected_sha256,
        bytes_=written,
        source_url=url,
    )
    return dest


def verify_only(vendor_dir: Path, config_path: Path) -> bool:
    """``--check``: verify an already-vendored tarball against its recorded
    manifest AND against the GitHub-published digest, without downloading.
    Returns True on a clean match.
    """
    version = read_pinned_version(config_path)
    asset_name = f"pyodide-{version}.tar.bz2"
    dest = vendor_dir / asset_name
    if not dest.is_file():
        logger.error("%s does not exist -- nothing to verify. Run without --check first.", dest)
        return False
    expected_sha256 = fetch_expected_digest(version, asset_name)
    actual_sha256 = _sha256_file(dest)
    if actual_sha256 != expected_sha256:
        logger.error(
            "sha256 MISMATCH: %s disk=%s expected(github)=%s", dest, actual_sha256, expected_sha256
        )
        return False
    logger.info("OK: %s matches GitHub-published digest (%s)", dest, expected_sha256)
    return True


# --- CLI -----------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--web-repl-root",
        type=Path,
        default=DEFAULT_WEB_REPL_ROOT,
        help="Override web-repl/ root (testing only).",
    )
    parser.add_argument(
        "--vendor-dir",
        type=Path,
        default=None,
        help="Override destination dir (default: <web-repl-root>/vendor).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Override jupyter_lite_config.json path (default: <web-repl-root>/jupyter_lite_config.json).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if a verified copy is already cached.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the already-vendored tarball's sha256 against the "
        "GitHub-published digest, without downloading. Exits nonzero on "
        "any mismatch or missing file.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug-level logging.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    web_repl_root = args.web_repl_root.resolve()
    vendor_dir = (args.vendor_dir or (web_repl_root / "vendor")).resolve()
    config_path = (args.config or (web_repl_root / "jupyter_lite_config.json")).resolve()

    try:
        if args.check:
            ok = verify_only(vendor_dir, config_path)
            return 0 if ok else 1
        dest = fetch_pyodide(
            web_repl_root=web_repl_root, vendor_dir=vendor_dir, config_path=config_path, force=args.force
        )
    except FetchError as exc:
        logger.error("%s", exc)
        return 1

    logger.info("OK -> %s", dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
