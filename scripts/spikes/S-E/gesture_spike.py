#!/usr/bin/env python3
"""gesture_spike.py — S-E driver: real requestDevice()/requestPort() gesture chain
on real hardware, for task_id 260817_praxis_repl_refocus.

THIS FILE IS A SCRATCH COPY of scripts/repl_smoke.py (the ONE repo harness), edited
per that script's own instruction ("If you need different behaviour, cp it into
scratch and edit the COPY"). It reuses repl_smoke's serving/probe idioms:
  - the ThreadingHTTPServer-over-127.0.0.1 pattern (never file://, never about:blank)
  - the two-literals-joined-with-+ sentinel trick (the `code` URL param is echoed
    into the console's editable cell BEFORE execution, so a literal contiguous
    sentinel string would match the pre-run SOURCE DISPLAY, not the printed output)
  - driving the JupyterLite REPL console via ?kernel=python&execute=1&code=...

It does NOT replace repl_smoke.py; it answers a different question repl_smoke.py was
never built to answer: does a REAL `requestDevice()`/`requestPort()` grant, inside a
REAL user-activation window, driven by a REAL Pyodide worker over BroadcastChannel,
actually work — and does it differ between the two candidate site topologies (design
B-prime: this page itself is the top-level document; design A: this page's kernel
lives inside an <iframe>, with the gesture UI on the parent per the pattern already
shipping in interaction-dialog.component.ts).

THIS SCRIPT CANNOT RUN UNATTENDED. It must pause for a human to click a real button
after plugging in a real device. See PROTOCOL.md in this directory for the human
checklist. Running it with nobody at the keyboard is expected to time out waiting for
the gesture — that is not a bug, and `--verify-pause-only` exists precisely to check
(without needing a human or device present) whether the script reaches that pause
point. HONEST STATUS (see PROTOCOL.md "Honest limitation" section for the full
account): four `--verify-pause-only` self-checks under Xvfb (up to 360s) launched
Chromium cleanly, served all assets correctly, and booted the real Pyodide kernel with
zero page/console errors, but none of the four actually observed the kernel reach the
pending-interaction state within budget — plausibly just slow (CDN-loaded Pyodide +
Xvfb + a service-worker-triggered double boot), but NOT confirmed. Treat that specific
claim ("the script reaches the pause point") as unverified, not proven, until you see
it happen live.

Hard constraints (verified 2026-08-17 by repl_smoke.py and by this script's own
Chromium-launch + real-boot self-checks — see plan section 5.6):
  - Playwright can only launch Chromium here with the Bash sandbox DISABLED
    (dangerouslyDisableSandbox=true) AND --no-sandbox --disable-dev-shm-usage.
  - playwright wants a chromium build not installed; --chrome-path must point at the
    verified-present 1228 build instead (default below).
  - Serve everything over http://127.0.0.1:<port>. NEVER about:blank, NEVER file://.
  - This script needs headless=False (a REAL visible window, not headless) plus a
    real human clicking a real button — headless API presence is NOT proof a real
    requestDevice() grant works; that is the entire reason S-E exists (see ADR /
    execution plan G2 criterion 5, and spike-evidence research doc line 390: "Disbelieve
    any S-E PASS that does not name the device.").

Real production mechanism this script mirrors (verified by reading, not invented):
  - assets/shims/web_serial_shim.py:389-394 — the kernel-side WebSerial.setup() calls
    navigator.serial.getPorts() (ALREADY-authorized ports only); the comment there
    states plainly: "The frontend (React/Angular) is responsible for calling
    requestPort() via a user gesture before this code runs." The worker never calls
    requestPort()/requestDevice() itself for the primary path.
  - assets/python/web_bridge.py:1094 request_user_interaction() posts a
    USER_INTERACTION message on the registered BroadcastChannel ('praxis_repl',
    registered by praxis_bootstrap.py's _setup_broadcast_listener) and awaits a
    matching 'praxis:interaction_response' — no timeout is set on that await
    (comment: "Interactions can take a long time (user waiting)").
  - app/shared/components/interaction-dialog/interaction-dialog.component.ts:97-113
    connectDevice() is called directly from an Angular (click) handler and calls
    navigator.{usb,serial,hid}.request*() with ZERO await before it, "to preserve
    transient activation (user gesture)". This script's GESTURE_HOST_INIT_SCRIPT is a
    minimal, framework-free reimplementation of exactly that handler, run in a plain
    <button onclick>, so the click really does carry live user activation.
  - app/features/playground/services/jupyter-channel.service.ts — the real app's
    BroadcastChannel listener for 'praxis_repl' lives in the top-level PARENT app, not
    inside the JupyterLite iframe. Design A's overlay/host_iframe.html host page below
    reproduces that placement exactly: the gesture button lives in the host document,
    the kernel lives in the nested <iframe>.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import textwrap
import threading
import time
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

LOG = logging.getLogger("gesture_spike")

DEFAULT_CHROME_PATH = (
    "/home/marielle/.cache/ms-playwright/chromium-1228/chrome-linux64/chrome"
)
DEFAULT_HUMAN_TIMEOUT_S = 600.0  # 10 minutes per phase — a human has to find/plug in a device
DEFAULT_PAUSE_ONLY_TIMEOUT_S = 30.0
POLL_INTERVAL_S = 2.0

PROBE_START = "===PRAXIS_GESTURE_JSON_START==="
PROBE_END = "===PRAXIS_GESTURE_JSON_END==="

SCRIPT_DIR = Path(__file__).parent.resolve()
OVERLAY_DIR = SCRIPT_DIR / "overlay"

TOPOLOGIES = ("toplevel", "iframe")
APIS = ("serial", "usb", "hid")


def find_repo_root(start: Path) -> Path:
    """Search upward from `start` for the directory containing pyproject.toml.

    Anchored to __file__, never Path.cwd() — see ~/.claude/rules/CLUSTER.md §1a.
    NOTE: `start` here is repl_smoke.py's own original directory
    (/home/marielle/projects/praxis/scripts), NOT this scratch copy's directory,
    because this scratch copy needs to locate the REAL repo to serve its REAL,
    unmodified assets/ tree read-only. This file itself never writes there.
    """
    cur = start.resolve()
    for candidate in (cur, *cur.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    raise RuntimeError(f"could not locate pyproject.toml above {start}")


REPO_ROOT = find_repo_root(Path(__file__).resolve().parent)
# REPOINTED 260818: serve the BUILT standalone site, not the Angular asset
# tree. The shims and web_bridge.py this spike depends on were moved out of
# praxis/web-client/src/assets/ into web-repl/, so serving the old path now
# 404s all seven first-party fetches -- the kernel would boot, skip shim
# injection entirely, and never reach the device_connect pause point. That
# failure is indistinguishable from a genuine gesture failure, which is
# exactly the confusion this spike exists to avoid.
# The built site also vendors Pyodide locally (dist/static/pyodide/), which
# should remove the CDN download that made the original self-check time out
# before reaching the pause point in up to 360s.
DEFAULT_SERVE_DIR = REPO_ROOT / "web-repl" / "dist"


# ---------------------------------------------------------------------------
# Static file server: serves `serve_dir` (the real repo assets, READ-ONLY) at
# the root, with one exception — anything under /_spike/ is instead served from
# `overlay_dir` (this scratch dir's overlay/ subfolder), which holds the
# spike-authored Design-A host page. This keeps repo and scratch content on the
# SAME origin (required: BroadcastChannel is same-origin scoped, so the host
# page and the iframe's kernel must share an origin) without ever writing into
# the repo tree.
# ---------------------------------------------------------------------------

SPIKE_PREFIX = "/_spike/"


def make_handler(serve_dir: Path, overlay_dir: Path, coi: bool) -> type[SimpleHTTPRequestHandler]:
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(serve_dir), **kwargs)

        def translate_path(self, path: str) -> str:  # noqa: D102 - stdlib override
            p = path.split("?", 1)[0].split("#", 1)[0]
            if p.startswith(SPIKE_PREFIX):
                rel = p[len(SPIKE_PREFIX):] or "index.html"
                return str((overlay_dir / rel).resolve())
            return super().translate_path(p)

        def end_headers(self) -> None:  # noqa: D102 - stdlib override
            if coi:
                self.send_header("Cross-Origin-Opener-Policy", "same-origin")
                self.send_header("Cross-Origin-Embedder-Policy", "credentialless")
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def log_message(self, fmt: str, *args: Any) -> None:  # noqa: D102
            LOG.debug("http: " + fmt, *args)

    return Handler


class ServedDir:
    """Context manager wrapping a background ThreadingHTTPServer."""

    def __init__(self, serve_dir: Path, overlay_dir: Path, coi: bool) -> None:
        handler_cls = make_handler(serve_dir, overlay_dir, coi)
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler_cls)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def __enter__(self) -> "ServedDir":
        self.thread.start()
        LOG.info("serving on http://127.0.0.1:%d (repo=%s ro, overlay prefix %s)", self.port, DEFAULT_SERVE_DIR, SPIKE_PREFIX)
        return self

    def __exit__(self, *exc: Any) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()


# ---------------------------------------------------------------------------
# The gesture-carrying host init script. Installed via page.add_init_script(),
# which Playwright runs in EVERY frame of the page (including a nested iframe)
# before any other script. The `window !== window.top` guard makes it a no-op
# inside the kernel iframe for Design A, so only the TOP document ever owns the
# BroadcastChannel listener + the real clickable button — exactly where
# jupyter-channel.service.ts / interaction-dialog.component.ts put it in the
# shipping app. For Design B-prime there is no iframe, so the guard is always
# true and the same code path runs directly on the one document.
# ---------------------------------------------------------------------------

GESTURE_HOST_INIT_SCRIPT = """
(() => {
  if (window !== window.top) { return; }

  window.__praxisGestureLog = [];
  window.__praxisGestureClickCount = 0;
  window.__praxisReadyReceived = false;
  window.__praxisLastClickToGrantMs = null;
  window.__praxisPendingRequest = null;
  window.__praxisRequestLog = [];

  function describeDevice(api, dev) {
    try {
      if (api === 'serial') {
        const info = dev.getInfo ? dev.getInfo() : {};
        return 'serial vid=' + info.usbVendorId + ' pid=' + info.usbProductId;
      }
      if (api === 'usb') {
        return 'usb ' + (dev.manufacturerName || '?') + ' ' + (dev.productName || '?') +
          ' vid=0x' + (dev.vendorId || 0).toString(16) + ' pid=0x' + (dev.productId || 0).toString(16);
      }
      if (api === 'hid') {
        return 'hid ' + (dev.productName || '?') +
          ' vid=0x' + (dev.vendorId || 0).toString(16) + ' pid=0x' + (dev.productId || 0).toString(16);
      }
    } catch (e) { return '<describe error: ' + e + '>'; }
    return '<unknown device>';
  }

  function ensureButton() {
    let btn = document.getElementById('__praxis_gesture_btn');
    if (btn) return btn;
    btn = document.createElement('button');
    btn.id = '__praxis_gesture_btn';
    btn.textContent = 'Click to grant device access';
    Object.assign(btn.style, {
      position: 'fixed', top: '8px', left: '8px', zIndex: 999999,
      fontSize: '22px', padding: '18px 26px', background: '#ffcc00',
      border: '5px solid #000', display: 'none', cursor: 'pointer',
      fontFamily: 'sans-serif',
    });
    document.body.appendChild(btn);
    return btn;
  }

  try {
    const ch = new BroadcastChannel('praxis_repl');
    window.__praxisGestureChannel = ch;
    ch.onmessage = (event) => {
      const data = event.data;
      window.__praxisRequestLog.push({ ts: Date.now(), data: JSON.parse(JSON.stringify(data || {})) });
      if (!data || typeof data !== 'object') return;
      if (data.type === 'praxis:ready') { window.__praxisReadyReceived = true; return; }
      if (data.type !== 'USER_INTERACTION') return;
      const p = data.payload;
      if (!p || p.interaction_type !== 'device_connect') return;

      const id = p.id;
      const payload = p.payload || {};
      const api = payload.api || 'usb';
      const filters = payload.filters || [];
      window.__praxisPendingRequest = { id: id, api: api, filters: filters, ts: Date.now() };
      window.__praxisGestureLog.push({ ts: Date.now(), event: 'interaction_received', id: id, api: api });

      const btn = ensureButton();
      btn.textContent = 'Click to grant ' + api.toUpperCase() + ' device access (id=' + id + ')';
      btn.style.display = 'block';

      // Real click handler, freshly (re)bound per request. The request*() call is
      // the FIRST statement in the handler body — zero `await` precedes it — which
      // is the gesture invariant P5.7 checks statically for praxis-shell.js.
      btn.onclick = () => {
        window.__praxisGestureClickCount += 1;
        const activeAtClick = (navigator.userActivation && typeof navigator.userActivation.isActive === 'boolean')
          ? navigator.userActivation.isActive : null;
        const t0 = performance.now();
        let reqPromise;
        if (api === 'usb') {
          reqPromise = navigator.usb.requestDevice({ filters: filters });
        } else if (api === 'serial') {
          reqPromise = navigator.serial.requestPort({ filters: filters });
        } else if (api === 'hid') {
          reqPromise = navigator.hid.requestDevice({ filters: filters }).then((devs) => devs[0]);
        } else {
          reqPromise = Promise.reject(new Error('unsupported api ' + api));
        }
        reqPromise.then((dev) => {
          const dt = performance.now() - t0;
          window.__praxisLastClickToGrantMs = dt;
          window.__praxisGestureLog.push({
            ts: Date.now(), event: 'grant_success', id: id, api: api,
            device: describeDevice(api, dev), activeAtClick: activeAtClick, clickToGrantMs: dt,
          });
          btn.style.display = 'none';
          ch.postMessage({ type: 'praxis:interaction_response', id: id, value: { success: true, api: api } });
        }).catch((e) => {
          const dt = performance.now() - t0;
          window.__praxisGestureLog.push({
            ts: Date.now(), event: 'grant_error', id: id, api: api,
            error_name: e && e.name, error_message: String((e && e.message) || e),
            activeAtClick: activeAtClick, clickToGrantMs: dt,
          });
          btn.textContent = (e && e.name) + ': click to retry ' + api.toUpperCase() + ' grant (id=' + id + ')';
          // Deliberately left visible so the human can retry — mirrors the real
          // InteractionDialogComponent's NotFoundError/cancel retry behaviour.
        });
      };
    };
  } catch (e) {
    window.__praxisGestureInitError = String(e);
  }
})();
"""


# ---------------------------------------------------------------------------
# Kernel-side probes (Python, injected via the `code` URL param and executed
# inside the real Pyodide worker). Same two-literals-joined-with-+ sentinel
# trick as repl_smoke.py, for the same reason (see module docstring).
# ---------------------------------------------------------------------------


def _sentinel_halves(s: str) -> tuple[str, str]:
    return s[: len(s) // 2], s[len(s) // 2 :]


def build_bootstrap_prelude(host_root: str) -> str:
    """Shared bootstrap block: fetch+exec praxis_bootstrap.py, await praxis_main().

    Identical in spirit to repl_smoke.py's build_probe_code() step 1 — reused here
    because it is the ONLY way to get the real 'praxis_repl' BroadcastChannel
    registered with web_bridge before request_user_interaction() can post on it.
    """
    return textwrap.dedent(
        f"""
        import asyncio, builtins, importlib, json, sys, traceback, time
        import js

        # The kernel's JS global. JupyterLite runs Pyodide in a Web Worker, whose
        # global is `self`, NOT `window` -- `js.window` raises AttributeError there.
        _GLOBAL_SCOPE = getattr(js, "window", None) or js.self

        HOST_ROOT = {host_root!r}
        RESULT: dict = {{"host_root": HOST_ROOT}}

        async def _bootstrap():
            try:
                xhr = js.XMLHttpRequest.new()
                xhr.open("GET", HOST_ROOT + "bootstrap/praxis_bootstrap.py", False)
                xhr.send(None)
                bootstrap_src = str(xhr.responseText)
                exec(compile(bootstrap_src, "praxis_bootstrap.py", "exec"), globals())
                await praxis_main(HOST_ROOT)  # noqa: F821 - injected by exec above
                RESULT["praxis_ready"] = True
            except Exception as e:  # noqa: BLE001
                RESULT["praxis_ready"] = False
                RESULT["bootstrap_error"] = f"{{type(e).__name__}}: {{e}}"
                RESULT["bootstrap_traceback"] = traceback.format_exc()
        """
    ).strip()


def build_gesture_probe_code(host_root: str, api: str) -> str:
    """Phase 1: real device_connect interaction -> PAUSE for human -> attempt open/IO.

    This is the probe that BLOCKS on request_user_interaction(), which has no
    timeout by design (web_bridge.py:1123-1126) — that block IS the human pause
    point. Playwright's poll loop (see run_topology) is what actually waits it out
    and prints progress; this code has no timeout of its own to fail loud honestly
    rather than race a guessed deadline against a human.
    """
    start_a, start_b = _sentinel_halves(PROBE_START)
    end_a, end_b = _sentinel_halves(PROBE_END)
    prelude = build_bootstrap_prelude(host_root)
    return textwrap.dedent(
        f"""
        {prelude}

        API = {api!r}
        _SENTINEL_START = {start_a!r} + {start_b!r}
        _SENTINEL_END = {end_a!r} + {end_b!r}

        async def _main():
            await _bootstrap()
            if not RESULT.get("praxis_ready"):
                return

            # --- capability presence (headless-visible, NOT proof of a real grant) ---
            RESULT["capabilities"] = {{
                "serial": hasattr(js.navigator, "serial"),
                "usb": hasattr(js.navigator, "usb"),
                "hid": hasattr(js.navigator, "hid"),
                # `js.window` does NOT exist in the kernel: JupyterLite runs Pyodide
                # in a Web Worker, whose global is `self`. Reading js.window here
                # raised AttributeError immediately after a SUCCESSFUL bootstrap and
                # before request_user_interaction() was ever reached -- so nothing was
                # posted, no sentinel printed, and pause-only reported a bare timeout.
                # Same class of bug as P1.4's `window` removal from web_serial_shim.py.
                "isSecureContext": bool(_GLOBAL_SCOPE.isSecureContext),
            }}

            # --- the real device-auth interaction request (web_bridge.py:1094) ---
            import web_bridge
            t_request = time.time()
            RESULT["interaction_request_sent_at"] = t_request
            try:
                value = await web_bridge.request_user_interaction(
                    "device_connect", {{"api": API, "filters": []}}
                )
                RESULT["interaction_result"] = {{"ok": True, "value": value}}
            except Exception as e:  # noqa: BLE001
                RESULT["interaction_result"] = {{"ok": False, "error": f"{{type(e).__name__}}: {{e}}"}}
            RESULT["interaction_resolved_at"] = time.time()
            RESULT["interaction_wait_s"] = RESULT["interaction_resolved_at"] - t_request

            interaction_ok = bool(RESULT["interaction_result"].get("ok")) and bool(
                (RESULT["interaction_result"].get("value") or {{}}).get("success")
            )
            RESULT["grant_reported_ok"] = interaction_ok

            # --- attempt a REAL open (and, where safe, a minimal read/write) using
            # the SAME unmodified shim classes production imports ---
            open_result: dict = {{"attempted": False}}
            if interaction_ok:
                open_result["attempted"] = True
                try:
                    if API == "serial":
                        from web_serial_shim import WebSerial
                        s = WebSerial()
                        await s.setup()  # calls navigator.serial.getPorts() per :389-394
                        open_result["opened"] = True
                        open_result["port_name"] = s.port
                        try:
                            await s.write(b"\\n")
                            data = await asyncio.wait_for(s.read(16), timeout=2)
                            open_result["write_ok"] = True
                            open_result["read_bytes"] = list(data)
                        except Exception as e:  # noqa: BLE001
                            open_result["io_error"] = f"{{type(e).__name__}}: {{e}}"
                        finally:
                            try:
                                await s.stop()
                            except Exception:
                                pass
                    elif API == "usb":
                        from web_usb_shim import WebUSB
                        u = WebUSB()
                        await u.setup()
                        open_result["opened"] = True
                    elif API == "hid":
                        from web_hid_shim import WebHID
                        h = WebHID()
                        await h.setup()
                        open_result["opened"] = True
                except Exception as e:  # noqa: BLE001
                    open_result["opened"] = False
                    open_result["open_error"] = f"{{type(e).__name__}}: {{e}}"
                    open_result["open_traceback"] = traceback.format_exc()
            RESULT["device_open_attempt"] = open_result

        await _main()
        print(_SENTINEL_START)
        print(json.dumps(RESULT))
        print(_SENTINEL_END)
        """
    ).strip()


def build_persistence_probe_code(host_root: str, api: str) -> str:
    """Phase 2 (after a page reload, NO new interaction request): does the grant
    persist per-origin? Calls only the already-authorized enumeration APIs
    (getPorts()/getDevices()) — never request*() — so this phase needs no human
    gesture at all, by design (that is exactly what it is testing)."""
    start_a, start_b = _sentinel_halves(PROBE_START)
    end_a, end_b = _sentinel_halves(PROBE_END)
    prelude = build_bootstrap_prelude(host_root)
    return textwrap.dedent(
        f"""
        {prelude}

        API = {api!r}
        _SENTINEL_START = {start_a!r} + {start_b!r}
        _SENTINEL_END = {end_a!r} + {end_b!r}

        async def _main():
            await _bootstrap()
            if not RESULT.get("praxis_ready"):
                return
            persisted: dict = {{}}
            try:
                if API == "serial":
                    ports = await js.navigator.serial.getPorts()
                    persisted["count"] = len(ports)
                elif API == "usb":
                    devs = await js.navigator.usb.getDevices()
                    persisted["count"] = len(devs)
                elif API == "hid":
                    devs = await js.navigator.hid.getDevices()
                    persisted["count"] = len(devs)
                persisted["ok"] = True
            except Exception as e:  # noqa: BLE001
                persisted["ok"] = False
                persisted["error"] = f"{{type(e).__name__}}: {{e}}"
            RESULT["persisted_grant_check"] = persisted

        await _main()
        print(_SENTINEL_START)
        print(json.dumps(RESULT))
        print(_SENTINEL_END)
        """
    ).strip()


# ---------------------------------------------------------------------------
# URL construction per topology
# ---------------------------------------------------------------------------


def _kernel_url_query(code: str) -> str:
    return urllib.parse.urlencode(
        {"kernel": "python", "toolbar": "1", "execute": "1", "code": code}
    )


def build_url(port: int, topology: str, code: str) -> str:
    query = _kernel_url_query(code)
    if topology == "toplevel":
        return f"http://127.0.0.1:{port}/repl/index.html?{query}"
    if topology == "iframe":
        return f"http://127.0.0.1:{port}{SPIKE_PREFIX}host_iframe.html?{query}"
    raise ValueError(f"unknown topology {topology!r}")


# ---------------------------------------------------------------------------
# Playwright driver
# ---------------------------------------------------------------------------


def _extract_sentinel_json(body_text: str) -> dict[str, Any] | None:
    match = re.search(
        re.escape(PROBE_START) + r"\s*(.*?)\s*" + re.escape(PROBE_END), body_text, re.DOTALL
    )
    if not match:
        return None
    return json.loads(match.group(1))


def _poll_for_sentinel(page: Any, timeout_s: float, label: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Poll (not a single blocking wait) so we can print live progress for the
    human and so THIS script can distinguish 'still waiting on the human' from
    'the page errored out' instead of just timing out silently."""
    deadline = time.monotonic() + timeout_s
    last_print = 0.0
    diag: dict[str, Any] = {}
    while time.monotonic() < deadline:
        body_text = page.evaluate("() => document.body.innerText")
        result = _extract_sentinel_json(body_text)
        if result is not None:
            return result, diag
        now = time.monotonic()
        if now - last_print >= POLL_INTERVAL_S:
            last_print = now
            try:
                pending = page.evaluate("() => window.__praxisPendingRequest || null")
                gesture_log_len = page.evaluate("() => (window.__praxisGestureLog || []).length")
                click_count = page.evaluate("() => window.__praxisGestureClickCount || 0")
            except Exception as e:  # noqa: BLE001 - page may be mid-navigation
                pending, gesture_log_len, click_count = None, None, None
            remaining = deadline - now
            LOG.info(
                "[%s] waiting for human (%.0fs left) — pending=%s gesture_events=%s clicks=%s",
                label, remaining, pending, gesture_log_len, click_count,
            )
            diag = {"pending": pending, "gesture_log_len": gesture_log_len, "click_count": click_count}
        time.sleep(0.5)
    return None, diag


def run_topology(
    *,
    topology: str,
    api: str,
    chrome_path: str,
    serve_dir: Path,
    overlay_dir: Path,
    human_timeout_s: float,
    persistence_timeout_s: float,
    pause_only: bool,
    pause_only_timeout_s: float,
) -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    result: dict[str, Any] = {"topology": topology, "api": api}

    with ServedDir(serve_dir, overlay_dir, coi=False) as served:
        phase1_code = build_gesture_probe_code("/", api)
        url = build_url(served.port, topology, phase1_code)
        LOG.info("[%s] phase 1 url length %d", topology, len(url))

        console_messages: list[dict[str, Any]] = []
        pageerrors: list[str] = []

        with sync_playwright() as p:
            # The real human run MUST be headed -- a visible window is the whole
            # point, and a synthetic click carries no user activation. But
            # --verify-pause-only runs with no human, and on a box with no display
            # server a headed Chromium loads the page without ever running the
            # REPL's ?execute=1 auto-run, so the payload sits in the cell as
            # unexecuted source. Self-check therefore runs headless by default.
            browser = p.chromium.launch(
                executable_path=chrome_path,
                headless=pause_only,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--window-size=1280,900"],
            )
            try:
                context = browser.new_context(viewport={"width": 1280, "height": 900})
                page = context.new_page()
                page.add_init_script(GESTURE_HOST_INIT_SCRIPT)
                page.on("pageerror", lambda exc: pageerrors.append(str(exc)))
                page.on(
                    "console",
                    lambda msg: console_messages.append({"type": msg.type, "text": msg.text}),
                )

                page.goto(url, wait_until="load", timeout=60_000)

                print(
                    f"\n{'=' * 78}\n"
                    f"TOPOLOGY: {topology}   API: {api}\n"
                    f"A real, visible Chromium window is now open. See PROTOCOL.md for the\n"
                    f"human checklist. Waiting up to {human_timeout_s:.0f}s for the yellow button\n"
                    f"to appear and be clicked.\n{'=' * 78}\n",
                    flush=True,
                )

                if pause_only:
                    # Self-check mode: only prove the script reaches the human pause
                    # point (a pending device_connect request exists). Never waits for
                    # or requires an actual grant. Used to verify this script without
                    # a human/device present.
                    #
                    # On TIMEOUT this branch also captures the signals that actually
                    # explain a non-arrival. It used to record only
                    # __praxisPendingRequest -- the success-path variable -- so a fatal
                    # bootstrap error that had already printed a full JSON diagnosis
                    # into the cell 20s in was reported identically to "Pyodide is
                    # still warming up". Four earlier runs were misattributed to slow
                    # CDN-loaded Pyodide on exactly that basis, when the real cause was
                    # a 404 on a stale bootstrap URL whose HTML error page was exec'd
                    # and raised SyntaxError into a swallowing except.
                    deadline = time.monotonic() + pause_only_timeout_s
                    reached_pause = False
                    last_print = 0.0
                    while time.monotonic() < deadline:
                        pending = page.evaluate("() => window.__praxisPendingRequest || null")
                        if pending:
                            reached_pause = True
                            break
                        now = time.monotonic()
                        if now - last_print >= POLL_INTERVAL_S:
                            last_print = now
                            LOG.info(
                                "[%s/%s pause-only] still waiting for kernel to reach the "
                                "interaction-request point (%.0fs left) — this is normal while "
                                "Pyodide finishes booting, not a hang",
                                topology, api, deadline - now,
                            )
                        time.sleep(0.5)
                    result["pause_only"] = True
                    result["reached_pause_point"] = reached_pause
                    result["pageerrors"] = pageerrors
                    if reached_pause:
                        result["console_tail"] = console_messages[-20:]
                    else:
                        # Diagnose, do not just report absence. The sentinel the kernel
                        # prints carries praxis_ready/bootstrap_error; __praxisReadyReceived
                        # says whether praxis:ready was ever posted. Keep the WHOLE console
                        # -- a [-20:] tail truncates away the boot messages where a 404 shows.
                        body_text = page.evaluate("() => document.body.innerText")
                        result["sentinel"] = _extract_sentinel_json(body_text)
                        # Keep the raw cell text when the sentinel is ABSENT: a null
                        # sentinel says the JSON never printed, not why. The cell
                        # normally carries the Python traceback that explains it.
                        if result["sentinel"] is None:
                            result["body_text"] = body_text[-4000:]
                        result["ready_received"] = page.evaluate(
                            "() => window.__praxisReadyReceived === true"
                        )
                        result["request_log"] = page.evaluate(
                            "() => window.__praxisRequestLog || []"
                        )
                        result["console"] = console_messages
                        LOG.error(
                            "[%s/%s pause-only] did NOT reach the pause point. "
                            "sentinel=%s ready_received=%s -- check result['console'] for 404s.",
                            topology, api,
                            "present" if result["sentinel"] else "ABSENT",
                            result["ready_received"],
                        )
                    return result

                phase1, diag1 = _poll_for_sentinel(page, human_timeout_s, f"{topology}/{api} phase1")
                result["phase1_diag"] = diag1
                if phase1 is None:
                    result["phase1"] = None
                    result["phase1_timed_out"] = True
                    result["pageerrors"] = pageerrors
                    result["console_tail"] = console_messages[-40:]
                    LOG.error("[%s] phase 1 TIMED OUT waiting for the human gesture", topology)
                    return result
                result["phase1"] = phase1
                result["phase1_gesture_log"] = page.evaluate("() => window.__praxisGestureLog || []")
                result["phase1_click_count"] = page.evaluate("() => window.__praxisGestureClickCount || 0")
                result["phase1_click_to_grant_ms"] = page.evaluate("() => window.__praxisLastClickToGrantMs")
                result["ready_received"] = page.evaluate("() => window.__praxisReadyReceived === true")

                # --- Phase 2: reload, no new interaction, check grant persistence ---
                phase2_code = build_persistence_probe_code("/", api)
                url2 = build_url(served.port, topology, phase2_code)
                LOG.info("[%s] reloading for phase 2 (persistence check)", topology)
                page.goto(url2, wait_until="load", timeout=60_000)
                phase2, diag2 = _poll_for_sentinel(page, persistence_timeout_s, f"{topology}/{api} phase2")
                result["phase2_diag"] = diag2
                result["phase2"] = phase2
                result["phase2_timed_out"] = phase2 is None

                result["pageerrors"] = pageerrors
                result["console_tail"] = console_messages[-40:]
            finally:
                browser.close()

    return result


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--topology", choices=(*TOPOLOGIES, "both"), default="both")
    p.add_argument("--api", choices=APIS, default="serial")
    p.add_argument("--chrome-path", default=DEFAULT_CHROME_PATH)
    p.add_argument("--serve-dir", type=Path, default=DEFAULT_SERVE_DIR)
    p.add_argument("--overlay-dir", type=Path, default=OVERLAY_DIR)
    p.add_argument("--human-timeout", type=float, default=DEFAULT_HUMAN_TIMEOUT_S,
                    help="Seconds to wait for the human to plug in + click, per topology (default 600).")
    p.add_argument("--persistence-timeout", type=float, default=60.0,
                    help="Seconds to wait for the phase-2 (reload) getPorts/getDevices check.")
    p.add_argument("--verify-pause-only", action="store_true",
                    help=(
                        "Self-check mode: run ONE topology/api, wait only up to "
                        "--pause-only-timeout for the pending-request state to appear, "
                        "then exit. Does NOT require or wait for a human/device. This is "
                        "the mechanism the spike author used to verify the script reaches "
                        "its pause point without a human present — it is NOT a substitute "
                        "for the real spike."
                    ))
    p.add_argument("--pause-only-timeout", type=float, default=DEFAULT_PAUSE_ONLY_TIMEOUT_S)
    p.add_argument("--out", type=Path, default=None)
    p.add_argument("-v", "--verbose", action="store_true")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )

    serve_dir = args.serve_dir.resolve()
    if not serve_dir.is_dir():
        LOG.error("--serve-dir does not exist: %s", serve_dir)
        return 2
    overlay_dir = args.overlay_dir.resolve()
    if not (overlay_dir / "host_iframe.html").is_file():
        LOG.error("overlay host page missing: %s/host_iframe.html", overlay_dir)
        return 2
    chrome_path = Path(args.chrome_path)
    if not (chrome_path.is_file() and chrome_path.stat().st_mode & 0o111):
        LOG.error("chrome executable not found or not executable at %s", chrome_path)
        return 2

    topologies = list(TOPOLOGIES) if args.topology == "both" else [args.topology]

    all_results: dict[str, Any] = {"api": args.api, "topologies": {}}
    try:
        for topo in topologies:
            LOG.info("=== running topology=%s api=%s ===", topo, args.api)
            res = run_topology(
                topology=topo,
                api=args.api,
                chrome_path=str(chrome_path),
                serve_dir=serve_dir,
                overlay_dir=overlay_dir,
                human_timeout_s=args.human_timeout,
                persistence_timeout_s=args.persistence_timeout,
                pause_only=args.verify_pause_only,
                pause_only_timeout_s=args.pause_only_timeout,
            )
            all_results["topologies"][topo] = res
    except Exception as e:  # noqa: BLE001 - infra failure, report verbatim
        LOG.error("run failed: %s: %s", type(e).__name__, e)
        LOG.error(
            "If this is a Chromium launch failure ('apply-seccomp: unshare(CLONE_NEWUSER)'), "
            "this script must be invoked with the Bash sandbox disabled "
            "(dangerouslyDisableSandbox=true / a normal terminal, not a sandboxed tool call)."
        )
        return 1

    output = json.dumps(all_results, indent=2, sort_keys=True, default=str)
    print(output)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output)
        LOG.info("wrote result to %s", args.out)

    return 0


if __name__ == "__main__":
    sys.exit(main())
