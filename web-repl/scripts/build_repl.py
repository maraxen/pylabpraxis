#!/usr/bin/env python3
"""Fail-loud orchestrator that builds the standalone praxis web REPL site.

Runs ``jupyter lite build`` (as ``uv run python -m jupyterlite_core`` --
**NEVER** the ``jupyter lite`` console script; its shebang points at
``/home/marielle/projects/awesomation/.venv/bin/python`` and exits 127, a
real reproduced failure, not a precaution), then stages ``overlay/``,
``bootstrap/``, and ``shell/`` into the output directory -- none of which
JupyterLite's own build knows anything about -- then regenerates
``manifest.json`` and injects the D1 shell sha, and finally asserts the
result is not hollow.

Per ADR ``.praxia/docs/decisions/260817_repl-layout-and-delivery-mechanism.md``
Sec 4.2: "Only ``overlay/`` reaches ``dist/`` (``build_repl.py --out
web-repl/dist``)" -- an earlier design placed the vendored visualizer at
``web-repl/`` root and no script staged it, so it never reached the page.
This script is where that staging actually happens, for ``overlay/assets/``
AND for the two loose top-level trees a real boot also needs but that live
outside ``overlay/`` on disk: ``bootstrap/`` (fetched by
``praxis_bootstrap.py``'s own two-file self-bootstrap, ADR Sec 2.3's D2
exception -- it cannot be manifest-driven because it IS the code that makes
manifest-driven fetching possible) and ``shell/praxis-shell.js`` (D1's
shell-injected half, deliberately kept outside the JupyterLite asset set).

**Layout decisions this script owns (not yet exercised by any browser run --
see this task's report for the honest boundary this crosses):**

- ``overlay/assets/`` -> ``<out>/assets/`` and ``bootstrap/*.py`` ->
  ``<out>/bootstrap/``, both as siblings of JupyterLite's own ``build/``
  and ``static/`` at the OUTPUT ROOT -- matching the pattern JupyterLite
  itself uses for shared, not-per-app assets (verified: a real build's
  vendored Pyodide lands at ``<out>/static/pyodide/``, not nested under any
  one app). ``praxis_bootstrap.py``'s ``host_root`` parameter is not yet
  wired by any caller (its own docstring: "the minimal external bootstrap
  snippet ... is Phase 5, out of this task's scope") -- this placement is
  this script's best-evidence guess for what that snippet should assume,
  not a proven contract. Flagged for whoever writes that snippet next.
- ``shell/praxis-shell.js`` -> ``<out>/shell/praxis-shell.js``. ONE shared
  copy at the output root, referenced as ``../shell/praxis-shell.js`` from
  every entry's ``index.html`` one directory down. The browser resolves that
  src directly against the page URL (no PageConfig/base-tag machinery has
  loaded when it runs), so the path is forced by arithmetic, not chosen.
  Previously the copy was nested under ``lab/`` with a ``./shell/...`` src,
  so only ``lab/`` could carry the shell -- and ``repl/``, the entry whose
  ``?code=&execute=1`` the smoke harness drives, had none, meaning D1 could
  only ever fail closed there. ``inject_shell.py`` now injects into EVERY
  ``dist/*/index.html`` carrying the anchor, and its own module docstring
  and this one now agree.

**Pyodide mode (ADR Sec 7, U18/U19 -- "whether Pyodide is vendored for
offline operation" -- open there, decided HERE for what this script
actually does):** GATE G5 requires
``grep -rl 'cdn.jsdelivr.net' web-repl/dist | wc -l`` to be **0**. The only
way to get anywhere near that is the vendored copy
(``fetch_pyodide.py``'s output under ``web-repl/vendor/``), passed to
``jupyter lite build`` as ``--PyodideAddon.pyodide_url=vendor/pyodide-<v>.tar.bz2``
-- a LOCAL PATH override that wins over the CDN URL already pinned in
``jupyter_lite_config.json`` (traitlets CLI args beat config-file values).
That file is read, never rewritten (a different task owns it). **Verified
against a real build (2026-08-18): even fully vendored, the string
``cdn.jsdelivr.net`` still appears in 8 files** -- Pyodide's own compiled
``pyodide.mjs`` bakes in ``https://cdn.jsdelivr.net/pyodide/v${ver}/full/``
as micropip's default package-index fallback, and the
``@jupyterlite/pyodide-kernel-extension`` bundle bakes in the same URL as an
unused settings default (``a.pyodideUrl||"https://cdn...`` -- the `||`
never fires once ``pyodideUrl`` is set, which the build's own
``patch:jupyter-lite.json`` step does). Both are dead fallback text inside
third-party compiled artifacts, not a live network call this build makes --
but GATE G5's grep cannot distinguish that from real usage, and this script
does not attempt to patch vendored third-party JS to force the count to
zero (too fragile, and not this task's to fix). Report the real grep result
honestly; do not paper over it. ``--allow-cdn`` exists for local iteration
and makes no attempt to satisfy G5's zero-cdn check.

**Manifest freshness:** this script always regenerates
``overlay/assets/wheels/manifest.json`` via ``build_manifest.py`` before
staging (threading ``--dev`` through if given) -- "wire your half" of ADR
Sec 2.3's D1 escape hatch: ``--dev`` makes BOTH ``build_manifest.py --dev``
(manifest's ``praxis_git_sha: "dev"``) and ``inject_shell.py --dev``
(shell's injected ``"dev"``) fire together, so the boot-time assert is
skipped only when both genuinely read ``"dev"`` -- never weakened for the
real path, where both independently compute the same ``git rev-parse HEAD``.

**``--debug-skip-jupyterlite``:** genuine failure injection for GATE G5, not
a stub. It skips the ``jupyter lite build`` subprocess entirely, leaving
``<out>/build/`` absent -- the SAME structural assertion that guards a real
hollow build (``ls <out>/build/*.js`` must be non-empty) then fires and
exits nonzero with ``BUILD ASSERTION FAILED`` in the message, by construction,
not a special-cased check.

House rules: uv-run only, argparse + logging, narrow runs, fail loud.
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import subprocess
import time
from pathlib import Path

import fetch_piplite_wheels  # same directory; sys.path[0] is this script's dir
import fetch_pyodide  # same directory; sys.path[0] is this script's dir

logger = logging.getLogger("build_repl")

_THIS_FILE = Path(__file__).resolve()
SCRIPTS_DIR = _THIS_FILE.parent
WEB_REPL_ROOT = SCRIPTS_DIR.parent
REPO_ROOT = WEB_REPL_ROOT.parent

DEFAULT_OUT_DIR = WEB_REPL_ROOT / "dist"
VENDOR_DIR = WEB_REPL_ROOT / "vendor"
CONFIG_PATH = WEB_REPL_ROOT / "jupyter_lite_config.json"
OVERLAY_ASSETS_DIR = WEB_REPL_ROOT / "overlay" / "assets"
BOOTSTRAP_DIR = WEB_REPL_ROOT / "bootstrap"
SHELL_DIR = WEB_REPL_ROOT / "shell"

_BOOTSTRAP_FILES = ("praxis_bootstrap.py", "stages.py", "transport.py")

_SKIP_DIR_NAMES = {"__pycache__"}
_SKIP_FILE_SUFFIXES = {".pyc", ".pyo"}
_SKIP_FILE_NAMES = {".gitkeep"}


class BuildError(RuntimeError):
    """Raised for any condition that must fail this build loudly."""


class BuildAssertionError(BuildError):
    """Raised for a post-build structural check failure -- GATE G5's
    ``--debug-skip-jupyterlite`` expects to see this class's message.
    """


# --- subprocess helpers -------------------------------------------------


def _uv_run(args: list[str], *, cwd: Path, timeout: float, log_path: Path | None = None) -> None:
    """Run ``uv run --project <REPO_ROOT> python <args>`` from *cwd*.

    Captures combined output (long-running steps like ``jupyter lite build``
    print a lot -- house rule: redirect to a log file, grep for signal) and
    writes it to *log_path* if given, always logging a short tail on
    success and the full output on failure.
    """
    cmd = ["uv", "run", "--project", str(REPO_ROOT), "python", *args]
    logger.info("+ %s  (cwd=%s)", " ".join(cmd), cwd)
    t0 = time.monotonic()
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired as exc:
        raise BuildError(f"{' '.join(cmd)} timed out after {timeout}s") from exc
    elapsed = time.monotonic() - t0
    combined = (result.stdout or "") + (result.stderr or "")
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(combined)
    if result.returncode != 0:
        tail = "\n".join(combined.splitlines()[-80:])
        raise BuildError(
            f"{' '.join(cmd)} FAILED (exit {result.returncode}, {elapsed:.1f}s)."
            + (f" Full log: {log_path}" if log_path else "")
            + f"\n--- last 80 lines ---\n{tail}"
        )
    logger.info("OK (%.1fs)%s", elapsed, f" -- full log: {log_path}" if log_path else "")


# --- step 1: jupyter lite build ------------------------------------------


def resolve_pyodide_arg(*, allow_cdn: bool) -> str | None:
    """Return the ``--PyodideAddon.pyodide_url`` value to pass, or ``None``
    to leave ``jupyter_lite_config.json``'s own (CDN) value in force.

    Reuses ``fetch_pyodide.read_pinned_version`` rather than re-parsing the
    config -- one parser for "what version does this build target", not two
    that can drift against each other.
    """
    if allow_cdn:
        logger.warning(
            "--allow-cdn: leaving PyodideAddon.pyodide_url on the CDN URL "
            "already pinned in jupyter_lite_config.json. GATE G5's "
            "'grep cdn.jsdelivr.net dist | wc -l == 0' check will NOT pass "
            "in this mode -- it exists for local iteration only."
        )
        return None
    version = fetch_pyodide.read_pinned_version(CONFIG_PATH)
    vendor_path = VENDOR_DIR / f"pyodide-{version}.tar.bz2"
    if not vendor_path.is_file():
        raise BuildError(
            f"{vendor_path} not found. Run "
            f"`uv run python {SCRIPTS_DIR / 'fetch_pyodide.py'}` first to vendor "
            f"Pyodide {version}, or pass --allow-cdn to build against the CDN "
            "URL instead (GATE G5's zero-cdn.jsdelivr.net check will then fail)."
        )
    logger.info("using vendored Pyodide: %s", vendor_path)
    # Local-path form (not a URL): resolved by PyodideAddon relative to
    # lite_dir, i.e. WEB_REPL_ROOT -- see jupyterlite_pyodide_kernel's own
    # addons/pyodide.py:cache_pyodide(). Verified against a real build.
    return f"vendor/pyodide-{version}.tar.bz2"


# jupyterlite drives its build with doit, which caches per-task state here (next to
# --lite-dir). The cache is NOT inside out_dir, so `rm -rf dist` does not clear it.
DOIT_DB_PATH = WEB_REPL_ROOT / ".jupyterlite.doit.db"


def discard_doit_cache() -> None:
    """Delete doit's task-state cache before every build.

    WHY THIS IS UNCONDITIONAL, not an optimisation to skip:

    PyodideAddon.post_build() writes `litePluginSettings[...].pyodideUrl` into
    jupyter-lite.json from a doit task whose only `file_dep` is the extracted
    `static/pyodide/pyodide.mjs`. When the cache says that dep is unchanged, doit
    skips the task -- but jupyter-lite.json is REGENERATED from scratch by an
    earlier addon in the same build. Skipped patch + regenerated config = a
    jupyter-lite.json with no `pyodideUrl` at all, which silently falls back to the
    kernel schema's default: https://cdn.jsdelivr.net/... (kernel.v0.schema.json).

    The failure is invisible in every way that matters. The build exits 0.
    `dist/static/pyodide/` is fully populated (423 files), so vendoring LOOKS
    successful. The site boots fine -- as long as the CDN is reachable, which it is
    on any developer machine. Measured 260819: a site built this way fetched
    pyodide.mjs, pyodide-lock.json, python_stdlib.zip, pyodide.asm.wasm and ~10
    package wheels from cdn.jsdelivr.net on every single boot, while the vendored
    copy sat unused. Only the --offline gate exposed it.

    `rm -rf dist` does NOT prevent this (verified: a clean dist with a stale cache
    still produced no pyodideUrl), so GATE G5's clean-build line is not sufficient
    on its own and this has to be handled here, in the build itself.
    """
    if DOIT_DB_PATH.exists():
        DOIT_DB_PATH.unlink()
        logger.info("discarded stale doit cache %s", DOIT_DB_PATH)
    # doit may also use dbm-style sidecars depending on backend.
    for sidecar in sorted(WEB_REPL_ROOT.glob(".jupyterlite.doit.db.*")):
        sidecar.unlink()
        logger.info("discarded stale doit cache sidecar %s", sidecar)


def assert_pyodide_is_local(out_dir: Path) -> None:
    """Fail the build if the site would fetch Pyodide from a CDN at runtime.

    This is the assertion that would have caught the silent doit-cache failure
    above on the day it started. It checks the RUNTIME config -- the only thing
    the browser actually reads -- not the presence of the extracted files, which
    is exactly the signal that misled us.
    """
    config_path = out_dir / "jupyter-lite.json"
    if not config_path.is_file():
        raise BuildAssertionError(
            f"BUILD ASSERTION FAILED: {config_path} does not exist."
        )
    settings = (
        json.loads(config_path.read_text())
        .get("jupyter-config-data", {})
        .get("litePluginSettings", {})
        .get("@jupyterlite/pyodide-kernel-extension:kernel", {})
    )
    url = settings.get("pyodideUrl")
    if not url:
        raise BuildAssertionError(
            "BUILD ASSERTION FAILED: jupyter-lite.json sets no `pyodideUrl`, so the "
            "kernel will silently use the schema default "
            "(https://cdn.jsdelivr.net/...) and fetch ~30 MB of Pyodide per boot "
            "regardless of what is in dist/static/pyodide/. Usual cause: a stale "
            f"{DOIT_DB_PATH.name} made doit skip PyodideAddon's patch task -- see "
            "discard_doit_cache()."
        )
    if "://" in url:
        raise BuildAssertionError(
            f"BUILD ASSERTION FAILED: `pyodideUrl` is remote ({url!r}). The site must "
            "load Pyodide from its own origin. Pass --allow-cdn only if you "
            "deliberately want a CDN build."
        )
    if not (out_dir / url.lstrip("./")).is_file():
        raise BuildAssertionError(
            f"BUILD ASSERTION FAILED: `pyodideUrl` is {url!r} but "
            f"{out_dir / url.lstrip('./')} does not exist."
        )
    logger.info("pyodide is local: pyodideUrl=%s", url)


def required_piplite_packages() -> tuple[str, ...]:
    """Runtime deps the browser needs that Pyodide does NOT bundle.

    `disablePyPIFallback: true` makes these unobtainable at runtime, so each must
    be vendored through PipliteAddon.piplite_urls. Read from
    ``web-repl/piplite_wheels.json`` rather than hardcoded here, so the pin table
    and this guard cannot drift into disagreeing about what is required -- the
    same duplicate-source-of-truth defect that made D3 report a covered module as
    uncovered (see test_contract_covers_imports.py).
    """
    return tuple(fetch_piplite_wheels.load_pins().get("required", ()))


def assert_required_piplite_wheels(out_dir: Path) -> None:
    """Fail the build if a required unbundled runtime dep is not vendored.

    `comm` is an ipykernel dependency present in NEITHER pyodide-lock.json nor the
    default piplite index. With `disablePyPIFallback: true` set in jupyter-lite.json,
    a missing wheel cannot be fetched at runtime -- piplite fails without even
    attempting a network request.

    This assertion exists because that failure is otherwise UNATTRIBUTED. Measured
    2026-08-20 by removing comm from piplite_urls and rebuilding: the build passed,
    `--probe` passed, and `--probe --offline` failed only as a bare 120s
    wait_for_function timeout. The kernel died in its Web Worker with the console
    ending at "Loaded micropip" -- no error naming comm, piplite, or any failed
    import, and zero failed requests (nothing ever reached the network to fail).

    Catching it here turns a silent two-minute browser timeout into an immediate
    build error naming the missing package.
    """
    index_path = out_dir / "pypi" / "all.json"
    if not index_path.is_file():
        raise BuildAssertionError(
            f"BUILD ASSERTION FAILED: {index_path} does not exist, so NO wheels are "
            "vendored for piplite. With disablePyPIFallback the kernel cannot fetch "
            f"them at runtime and will die silently in its worker. Required: "
            f"{', '.join(required_piplite_packages())}. Usual cause: "
            "scripts/fetch_piplite_wheels.py did not run, or PipliteAddon.piplite_urls "
            "in web-repl/jupyter_lite_config.json does not point at the fetched "
            "vendor/piplite-wheels/<filename>."
        )
    raw = json.loads(index_path.read_text())
    names = {str(k).lower().replace("_", "-") for k in raw} if isinstance(raw, dict) else set()
    names |= {
        w.name.split("-")[0].lower().replace("_", "-")
        for w in (out_dir / "pypi").glob("*.whl")
    }
    missing = [p for p in required_piplite_packages() if p.lower().replace("_", "-") not in names]
    if missing:
        raise BuildAssertionError(
            f"BUILD ASSERTION FAILED: required piplite wheel(s) not vendored: "
            f"{', '.join(missing)}. Found: {sorted(names) or 'nothing'}. These are not "
            "in pyodide-lock.json and disablePyPIFallback blocks the PyPI fallback, so "
            "the kernel will fail to start OFFLINE with no error naming the cause. Pin "
            "it in web-repl/piplite_wheels.json (name/version/filename/sha256) and add "
            "the matching vendor/piplite-wheels/<filename> path to "
            "PipliteAddon.piplite_urls; scripts/fetch_piplite_wheels.py fetches it. Do "
            "NOT commit the .whl -- R6/R8 require zero tracked wheels repo-wide."
        )
    logger.info("required piplite wheels vendored: %s", ", ".join(required_piplite_packages()))


def run_jupyterlite_build(*, out_dir: Path, pyodide_arg: str | None, log_path: Path) -> None:
    discard_doit_cache()
    args = [
        "-m",
        "jupyterlite_core",
        "build",
        "--lite-dir",
        str(WEB_REPL_ROOT),
        "--output-dir",
        str(out_dir),
    ]
    if pyodide_arg is not None:
        args.append(f"--PyodideAddon.pyodide_url={pyodide_arg}")
    # cwd=WEB_REPL_ROOT so jupyter_lite_config.json (traitlets, auto-loaded
    # from cwd by JupyterLite's own Application convention) is picked up --
    # --lite-dir alone does not do this, it only governs jupyter-lite.json
    # (schema-v0) content resolution.
    _uv_run(args, cwd=WEB_REPL_ROOT, timeout=900, log_path=log_path)


def assert_jupyterlite_output_not_hollow(out_dir: Path) -> None:
    """The one check GATE G5's ``--debug-skip-jupyterlite`` run depends on
    firing, and the one that protects a genuinely hollow real build too --
    same code path either way, no special-casing.
    """
    build_dir = out_dir / "build"
    js_files = sorted(build_dir.glob("*.js")) if build_dir.is_dir() else []
    if len(js_files) < 1:
        raise BuildAssertionError(
            f"BUILD ASSERTION FAILED: {build_dir} has {len(js_files)} *.js "
            "file(s) -- jupyter lite build was skipped or produced a hollow "
            "output. GATE G5 requires `ls dist/build/*.js | wc -l` >= 50 "
            "(the deployed husk this replaces had 0)."
        )
    bundle = build_dir / "lab" / "bundle.js"
    if not bundle.is_file() or bundle.stat().st_size == 0:
        raise BuildAssertionError(
            f"BUILD ASSERTION FAILED: {bundle} is missing or empty -- the "
            "lab app's own bundle did not build correctly."
        )
    logger.info(
        "jupyterlite output OK: %d file(s) under build/, bundle.js is %d bytes",
        len(js_files),
        bundle.stat().st_size,
    )


# --- step 2: manifest regeneration --------------------------------------


def run_build_manifest(*, dev: bool) -> None:
    args = [str(SCRIPTS_DIR / "build_manifest.py")]
    if dev:
        args.append("--dev")
    _uv_run(args, cwd=REPO_ROOT, timeout=60)


# --- step 3: staging overlay/ + bootstrap/ + shell/ into <out> ----------


def _copytree_filtered(src: Path, dst: Path) -> int:
    """Copy *src* -> *dst* recursively, skipping ``__pycache__``, ``.pyc``/
    ``.pyo``, and ``.gitkeep`` placeholder files. Returns the count of files
    actually copied.

    Directories are created even when every file inside them gets filtered
    out. This was originally load-bearing for ``visualizer-augmentations/``,
    which held only a ``.gitkeep`` until 260819 -- ADR Sec 4.2 #4 requires that
    directory to exist in ``dist/`` under its preserved name, because the
    vendored ``visualizer/index.html`` reaches it by a relative ``<script src>``.
    It now ships a real (no-op) ``index.js``, so that particular directory no
    longer depends on this behaviour, and the build asserts on the FILE rather
    than the directory. The walk is kept anyway: a file-driven
    ``mkdir(parents=True)`` alone would silently drop any future
    empty-of-real-content directory, which is exactly the 404 this prevented.
    """
    count = 0
    for item in sorted(src.rglob("*")):
        rel = item.relative_to(src)
        if any(part in _SKIP_DIR_NAMES for part in rel.parts):
            continue
        if item.is_dir():
            (dst / rel).mkdir(parents=True, exist_ok=True)
            continue
        if item.suffix in _SKIP_FILE_SUFFIXES or item.name in _SKIP_FILE_NAMES:
            continue
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
        count += 1
    return count


def stage_overlay(out_dir: Path) -> int:
    if not OVERLAY_ASSETS_DIR.is_dir():
        raise BuildError(f"{OVERLAY_ASSETS_DIR} does not exist -- nothing to stage.")
    dst = out_dir / "assets"
    if dst.exists():
        shutil.rmtree(dst)
    n = _copytree_filtered(OVERLAY_ASSETS_DIR, dst)
    if n == 0:
        raise BuildAssertionError(
            f"BUILD ASSERTION FAILED: staged 0 files from {OVERLAY_ASSETS_DIR} "
            "-- overlay/assets/ appears empty."
        )
    logger.info("staged %d file(s) from overlay/assets/ -> %s", n, dst)
    return n


def stage_bootstrap(out_dir: Path) -> int:
    dst = out_dir / "bootstrap"
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for name in _BOOTSTRAP_FILES:
        src = BOOTSTRAP_DIR / name
        if not src.is_file():
            raise BuildError(f"{src} missing -- cannot stage bootstrap/.")
        shutil.copy2(src, dst / name)
    logger.info("staged %d file(s) from bootstrap/ -> %s", len(_BOOTSTRAP_FILES), dst)
    return len(_BOOTSTRAP_FILES)


def stage_shell(out_dir: Path) -> Path:
    src = SHELL_DIR / "praxis-shell.js"
    if not src.is_file():
        raise BuildError(f"{src} missing -- cannot stage shell/.")
    # ONE shared copy at <out>/shell/, referenced as `../shell/praxis-shell.js`
    # from every entry's index.html. Previously this was nested under lab/,
    # which meant only lab/ could carry the shell -- so repl/, the entry whose
    # `?code=&execute=1` the smoke harness drives, had no shell and D1 could
    # only fail closed there.
    dst_dir = out_dir / "shell"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / "praxis-shell.js"
    shutil.copy2(src, dst)
    logger.info("staged shell/praxis-shell.js -> %s", dst)
    return dst


# --- step 4: D1 shell injection ------------------------------------------


def run_inject_shell(*, dev: bool) -> None:
    # No --target: inject_shell.py discovers every dist/*/index.html carrying
    # the anchor, so all app entries get the shell, not just lab/.
    args = [str(SCRIPTS_DIR / "inject_shell.py")]
    if dev:
        args.append("--dev")
    _uv_run(args, cwd=REPO_ROOT, timeout=60)


def run_inject_shell_check() -> None:
    args = [str(SCRIPTS_DIR / "inject_shell.py"), "--check"]
    try:
        _uv_run(args, cwd=REPO_ROOT, timeout=60)
    except BuildError as exc:
        raise BuildAssertionError(f"BUILD ASSERTION FAILED: inject_shell.py --check failed: {exc}") from exc


# --- step 5: final completeness assertion --------------------------------


def assert_dist_complete(out_dir: Path) -> None:
    required = [
        out_dir / "assets" / "wheels" / "manifest.json",
        out_dir / "assets" / "shims" / "web_serial_shim.py",
        out_dir / "assets" / "shims" / "web_usb_shim.py",
        out_dir / "assets" / "shims" / "web_hid_shim.py",
        out_dir / "assets" / "shims" / "web_ftdi_shim.py",
        out_dir / "assets" / "python" / "web_bridge.py",
        out_dir / "assets" / "python" / "praxis" / "__init__.py",
        out_dir / "assets" / "python" / "praxis" / "interactive.py",
        out_dir / "assets" / "visualizer" / "lib.js",
        out_dir / "assets" / "visualizer" / "index.html",
        out_dir / "assets" / "visualizer-augmentations" / "index.js",
        out_dir / "bootstrap" / "praxis_bootstrap.py",
        out_dir / "bootstrap" / "stages.py",
        out_dir / "bootstrap" / "transport.py",
        out_dir / "shell" / "praxis-shell.js",
        out_dir / "lab" / "index.html",
        out_dir / "repl" / "index.html",
        # The welcome notebook, and the contents index that makes it VISIBLE. Both,
        # because they fail independently: jupyterlite-core's `contents` addon needs
        # jupyter-server (a `dev`-group dep) to index files/, and without it the build
        # either hard-raises or -- in the pre-260819 empty-files/ case -- merely warns.
        # Asserting only on the .ipynb would let a site ship the notebook as an
        # unreachable blob with an empty file browser.
        out_dir / "files" / "welcome.ipynb",
        out_dir / "api" / "contents" / "all.json",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise BuildAssertionError(
            "BUILD ASSERTION FAILED: dist/ is missing required staged path(s):\n  "
            + "\n  ".join(missing)
        )
    wheel_count = len(list((out_dir / "assets" / "wheels").glob("*.whl")))
    if wheel_count == 0:
        raise BuildAssertionError(
            "BUILD ASSERTION FAILED: dist/assets/wheels/ contains zero *.whl files."
        )
    logger.info("dist/ completeness OK (%d wheel(s) staged)", wheel_count)


# --- CLI -------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help=f"Build output directory (default: {DEFAULT_OUT_DIR}, gitignored).",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help='Thread the D1 "dev" sentinel through both build_manifest.py --dev '
        "(manifest praxis_git_sha) and inject_shell.py --dev (injected shell "
        "sha) -- ADR Sec 2.3's dev-loop escape hatch. Never weakens the "
        "non-dev path; both scripts independently compute git rev-parse HEAD "
        "when this is not passed.",
    )
    parser.add_argument(
        "--debug-skip-jupyterlite",
        action="store_true",
        help="Failure-injection mode for GATE G5: skip the `jupyter lite "
        "build` subprocess entirely. The post-build structural assertion "
        "then fires for real (dist/build/ is absent), exiting nonzero with "
        "'BUILD ASSERTION FAILED' -- proving the build fails loud rather "
        "than producing a hollow dist/.",
    )
    parser.add_argument(
        "--allow-cdn",
        action="store_true",
        help="Leave PyodideAddon.pyodide_url on the CDN URL already pinned "
        "in jupyter_lite_config.json instead of requiring the vendored "
        "tarball from fetch_pyodide.py. For local iteration only -- GATE "
        "G5's zero-cdn.jsdelivr.net check will not pass in this mode.",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not remove an existing --out directory before building "
        "(default: remove it first, matching GATE G5's `rm -rf dist`).",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug-level logging.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    out_dir = args.out.resolve()

    try:
        if not args.no_clean and out_dir.exists():
            logger.info("removing existing %s", out_dir)
            shutil.rmtree(out_dir)

        if args.debug_skip_jupyterlite:
            logger.warning(
                "--debug-skip-jupyterlite: SKIPPING `jupyter lite build` -- "
                "this is deliberate failure injection for GATE G5, not a "
                "real build path."
            )
            out_dir.mkdir(parents=True, exist_ok=True)
        else:
            # Vendor the pinned piplite wheels first: the jupyterlite build reads
            # them through PipliteAddon.piplite_urls, which now points into
            # web-repl/vendor/ (gitignored) rather than at a committed .whl. See
            # fetch_piplite_wheels.py for why the tracked binary was retired.
            fetch_piplite_wheels.fetch_all()
            pyodide_arg = resolve_pyodide_arg(allow_cdn=args.allow_cdn)
            log_path = out_dir.parent / f".{out_dir.name}-jupyterlite-build.log"
            run_jupyterlite_build(out_dir=out_dir, pyodide_arg=pyodide_arg, log_path=log_path)

        assert_jupyterlite_output_not_hollow(out_dir)
        if not args.debug_skip_jupyterlite and not args.allow_cdn:
            assert_pyodide_is_local(out_dir)
        assert_required_piplite_wheels(out_dir)

        run_build_manifest(dev=args.dev)
        stage_overlay(out_dir)
        stage_bootstrap(out_dir)
        stage_shell(out_dir)

        run_inject_shell(dev=args.dev)
        run_inject_shell_check()

        assert_dist_complete(out_dir)

    except BuildAssertionError as exc:
        msg = str(exc)
        if "BUILD ASSERTION FAILED" not in msg:
            msg = f"BUILD ASSERTION FAILED: {msg}"
        logger.error(msg)
        return 1
    except BuildError as exc:
        logger.error("%s", exc)
        return 1

    logger.info("OK -> %s", out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
