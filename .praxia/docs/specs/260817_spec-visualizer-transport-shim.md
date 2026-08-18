---
title: Visualizer transport shim and augmentation API
description: Adversarially-reviewed spec for the praxis REPL refocus (visualizer); converged=True after 1 round(s), verdict REVISE.
category: specs
task_id: 260817_praxis_repl_refocus
status: draft
date: 260817
---

# Visualizer transport shim and augmentation API

**Area:** `visualizer` · **Converged:** True · **Rounds:** 1 · **Adjudicated verdict:** REVISE

## Summary

Vendor the PyLabRobot visualizer into the static REPL site as a socket-free, CDN-free renderer, drive it from the Pyodide kernel via a `BrowserVisualizer` subclass over a BroadcastChannel courier, and expose a three-layer augmentation API (`praxisViz.use` / `.overlay`+`.anchor` / Python-side `viz.emit`) that requires zero edits to upstream `lib.js`.

The chosen design is winner A' from contemplex plan `edde4648`. This spec adds five corrections/new findings from my own verification pass, all labelled below, and one of them is a hard blocker the brainstorm did not catch.

NEW EVIDENCE I GATHERED (this session):

1. [RAN — closes a sequencing question] The spike's generator applies cleanly to the repo's CURRENTLY-PINNED PLR, so slice 1 does NOT block on the submodule bump. Command: `cd /tmp/claude-1000/praxis-spikes/s4 && uv run --no-project python build_harness.py --src /home/marielle/projects/praxis/external/pylabrobot/pylabrobot/visualizer --out /tmp/claude-1000/praxis-spikes/spec-check/vis-pinned --konva ./konva.min.js`. Output: `lib.js sha256 src=a71f8874d33be713 out=a71f8874d33be713 identical=True`, all four vis.js edits applied ("ack-send (handleEvent tail)", "openSocket body", "openSocket tail close of dead block", "heartbeat"), 5 CDN substitutions, `index.html remaining external URLs: []`.

2. [READ — HARD BLOCKER, not in the brainstorm] At PLR 0.2.2, `Visualizer.__init__` raises `RuntimeError("The visualizer requires websockets to be installed...")` when `HAS_WEBSOCKETS` is False — `/tmp/claude-1000/praxis-spikes/plr-022/pylabrobot/visualizer/visualizer.py:144`, inside `__init__` (which starts at :113). At the currently-pinned d9651e2 that same check lives at `visualizer.py:444`, inside `setup()` — NOT `__init__`. So at the 0.2.2 target pin, merely CONSTRUCTING `BrowserVisualizer` fails unless `import websockets` AND `import websockets.asyncio.server` both succeed inside Pyodide. `websockets` is a HARD dependency at 0.2.2 (`pyproject.toml: dependencies = ["typing_extensions", "websockets"]`), so micropip will attempt it during the PLR wheel install. [RAN] `curl -s https://pypi.org/pypi/websockets/json` confirms a pure-Python `websockets-17.0.1-py3-none-any.whl` exists, so it is installable — but whether `websockets.asyncio.server` IMPORTS under Pyodide (it pulls asyncio/socket/ssl/threading machinery) has never been tested. This becomes a blocking sub-check of SLICE 0.

3. [READ — closes brainstorm assumption #8] All `visualizer.py` line references in the brainstorm were read at d9651e2, not 0.2.2. Real 0.2.2 line numbers, read directly: `_serialize_resource_tree`:53, `_build_method_registry`:65, `__init__`:113, `_assemble_command`:292, `has_connection`:307, `send_command`:312, `_detect_source_filename`:383, `setup`:471, `stop`:609, `_send_resources_and_state`:643, `_handle_resource_assigned_callback`:675 (`run_coroutine_threadsafe` at :698), `_handle_resource_unassigned_callback`:700 (:707), `_handle_state_update_callback`:709 (`call_soon_threadsafe` at :714), `_enqueue_state_update`:716 (`call_soon` at :721), `_flush_state_updates`:723. Also: `send_command` is `async def` with signature `(self, event: str, data: Optional[Dict[str,Any]] = None, wait_for_response: bool = True)`, and `has_connection` reads `self._websocket` (underscore), not `self.websocket`.

4. [CORRECTION to the brainstorm's vis.js edit list] The brainstorm names the four anchors as ack / openSocket / heartbeat / load-listener. The spike's ACTUAL working generator (`/tmp/claude-1000/praxis-spikes/s4/build_harness.py`) edits ack / openSocket-body / openSocket-dead-block-close / heartbeat and leaves the `window.addEventListener("load", ...)` listener untouched. Use the generator's real set. Corroborating evidence for making anchors textual rather than positional: the same four sites sit at vis.js:148/156/200/207 at d9651e2 [RAN grep] but at :178/:185/:230/:237 at 0.2.2 [per spike] — line numbers move, text does not.

5. [READ — new, breaks subpath deploys] `index.html` references `/favicon.png` at TWO absolute-path sites: `:8` (`<link rel="icon">`) and `:32` at 0.2.2 / `:22` at d9651e2 (the header `<img>` logo). The brainstorm's "copy `visualizer/img/logo.png` to `/favicon.png`" fixes the tab icon only at a site root; under a GitHub Pages subpath (`/praxis/assets/visualizer/`) BOTH 404 and the header logo visibly breaks. The generator must rewrite both to `./favicon.png`. Also pin-sensitive: 0.2.2 has 4 `{{ }}` placeholders (incl. `{{ liquid_color }}`), d9651e2 has only 3 [RAN grep on both].

## Decision: the `websockets` hard dependency is met by a VENDORED WHEEL, not a boot-time PyPI fetch (260818)

**This is the right home for this decision**, not the ADR: nothing about the ADR's canonical tree
(§2.1), its three detectors (§2.3), or its namespace rules (§2.4) changes. The mechanism used below is
the *existing* D2 wheel-manifest pipeline, applied to a third package — structurally identical to how
`pylabrobot` and `pylibftdi` already ship. If this decision ever required a new detector or a new
tree path, it would belong in the ADR; it requires neither.

**The GATE G2 verdict recorded criterion 1 as PASS "conditional on a named fix": `await
micropip.install("websockets")` added to `praxis_bootstrap.py`'s install step** (verdict §"Criterion
1", `.praxia/docs/research/260817_g2-spike-battery-verdict.md:84-89`). That verdict is **not adopted
here**, and the reason is spelled out in its own §9: *"Criterion 1 → FAIL if `micropip.install`
proves unavailable in the offline/vendored configuration (all evidence here is CDN/PyPI-reachable)."*
GATE G5 (execution plan, PHASE 5) mandates exactly that configuration: `chromium
--host-resolver-rules="MAP cdn.jsdelivr.net 127.0.0.1:1"` plus `pypi.org` and `files.pythonhosted.org`,
and asserts `grep -rl 'cdn.jsdelivr.net' web-repl/dist | wc -l` is `0`. A boot-time `micropip.install`
against PyPI is a live network fetch of a **third** host neither G5's grep nor its host-resolver-rules
name — G5 as written would not even catch it — but it is unambiguously the same class of violation
the gate exists to prevent: the deployed site making an uncontrolled runtime fetch to a CDN/PyPI host.
Shipping the one-line fix the G2 verdict recommended would pass G2's own criterion 1 while silently
setting up a G5 failure (or a G5 gate that fails to catch it, which is worse). This tension is exactly
what this decision resolves, and neither G2 nor the transport-shim spec's own risk/open-question
entries (below) weighed it — they treat `micropip.install("websockets")` as free.

**Three options were on the table, not two:**

- **(a) `await micropip.install("websockets")` at boot.** Verified to work (S-A, G2 criterion 1) —
  but only in a CDN/PyPI-reachable configuration, which G5 explicitly forbids. REJECTED for that
  reason alone; it is otherwise the simplest option.
- **(b) A stub `websockets` module.** Viable per S-A's own reasoning (`BrowserVisualizer` overrides
  `setup`/`stop`/`has_connection`/`send_command` and never calls the real
  `websockets.asyncio.server.serve(...)`), and it has no network dependency. REJECTED in favor of (c):
  a stub is strictly worse than a real, cheaply-vendored library along every axis that matters here —
  it adds a second import-shadowing surface next to the six `NATIVE_STUB_MODULES` `stages.py` already
  maintains, it must be kept in sync by hand if PLR's import surface (`websockets`,
  `websockets.asyncio.server`, `websockets.exceptions`) ever grows, and "must fail loudly if anything
  ever calls a real server function" is a property this task would have to hand-build and keep
  correct, whereas a real library gets it for free (an unimplemented/broken call fails on its own
  terms, not on a maintainer's memory of which functions were stubbed).
- **(c) Vendor `websockets-17.0.1-py3-none-any.whl` into `overlay/assets/wheels/`.** CHOSEN. Real
  library, zero boot-time network, and — the decisive point neither S-A nor the spec's risk bullet
  noticed — **it requires ZERO code changes**, in `praxis_bootstrap.py` or anywhere else:
  `build_manifest.py`'s `collect_wheels()` (`scripts/build_manifest.py:159-173`) already globs
  `wheels_dir.glob("*.whl")` with no allowlist, and `praxis_bootstrap.py`'s wheel-install stage
  (`:300-306`) already loops `for wheel_entry in manifest["wheels"]: await
  micropip.install(wheel_url, deps=False)` for every manifest entry. Dropping a third `.whl` next to
  the existing `pylabrobot-…` and `pylibftdi-…` wheels and re-running `build_manifest.py` is the
  entire change. `deps=False` is already the standing policy for every wheel install here, which
  also forecloses `websockets` (itself dependency-free — confirmed below) from ever triggering a
  transitive PyPI fetch of its own.

**Provenance, RAN.** Fetched `websockets-17.0.1-py3-none-any.whl` from PyPI (`pypi.org` and
`files.pythonhosted.org` are both on this sandbox's network allowlist) and verified it byte-for-byte
against PyPI's own published digest before vendoring:
```
$ curl -s https://pypi.org/pypi/websockets/17.0.1/json | … # locate the py3-none-any entry
websockets-17.0.1-py3-none-any.whl
  https://files.pythonhosted.org/packages/09/ce/…/websockets-17.0.1-py3-none-any.whl
  sha256=c6be9cba65c65cc76dfa3d4619e359ff02a4476c74e179b215236c11a0b32345  size=206718

$ sha256sum websockets-17.0.1-py3-none-any.whl   # after download
c6be9cba65c65cc76dfa3d4619e359ff02a4476c74e179b215236c11a0b32345  websockets-17.0.1-py3-none-any.whl
# matches PyPI's own digest exactly; size 206718 also matches.

$ python3 -c "import zipfile; ..."   # read METADATA out of the wheel
Name: websockets
Version: 17.0.1
Requires-Python: >=3.11
# no `Requires-Dist:` lines at all -- confirmed dependency-free, so `deps=False`
# forecloses nothing this package would otherwise have wanted.
```
Placed at `web-repl/overlay/assets/wheels/websockets-17.0.1-py3-none-any.whl` (gitignored by
`web-repl/.gitignore:8`, same as the other two wheels — confirmed with `git check-ignore -v`).

**Manifest regeneration, RAN** (no code change to `build_manifest.py`; the existing glob picked it up):
```
$ uv run python web-repl/scripts/build_manifest.py
INFO build_manifest: wrote …/manifest.json (3 wheel(s), 9 source(s))
$ uv run python web-repl/scripts/build_manifest.py --verify
INFO build_manifest: D2 OK: 3 wheel(s), 9 source(s) all match disk
```
`manifest.json`'s `"wheels"` array now carries a third entry: `{"package": "websockets", "filename":
"websockets-17.0.1-py3-none-any.whl", "version": "17.0.1", "source_sha": null, "sha256":
"c6be9cba65c65cc76dfa3d4619e359ff02a4476c74e179b215236c11a0b32345", "bytes": 206718}`.
`source_sha: null` is correct and matches the existing `pylibftdi` precedent (`_BUILD_INFO_FIELD` in
`build_manifest.py` has no entry for `websockets`; it is not a praxis-built wheel, so there is no
`_praxis_build_info.PLR_SOURCE_SHA` to extract — the PyPI sha256 above is `websockets`'s provenance
record instead).

**CPython verification, RAN — from a clean scratch dir, throwaway venv, no `--deps`:**
```
$ mkdir -p /tmp/claude-1000/ws-verify && cd /tmp/claude-1000/ws-verify
$ uv venv .venv --python 3.14
$ uv pip install --python .venv/bin/python --no-deps \
    …/overlay/assets/wheels/pylabrobot-0.2.2+gdd79c4c8-py3-none-any.whl \
    …/overlay/assets/wheels/websockets-17.0.1-py3-none-any.whl
 + pylabrobot==0.2.2+gdd79c4c8 (from file://…)
 + websockets==17.0.1 (from file://…)
$ .venv/bin/python probe.py
{
  "websockets_import": {"ok": true, "version": "17.0.1",
    "file": "/tmp/claude-1000/ws-verify/.venv/lib/python3.14/site-packages/websockets/__init__.py"},
  "websockets_asyncio_server_import": {"ok": true},
  "plr_HAS_WEBSOCKETS": true,
  "import_pylabrobot_visualizer": {"ok": true}
}
```
`websockets.__file__` resolves inside the throwaway venv's own `site-packages`, not a stray scratch
package (checked: `ls /tmp/claude-1000/ws-verify/` shows only `.venv/` and `probe.py`, no
package-shaped directory to shadow it). `--no-deps` mirrors `praxis_bootstrap.py`'s `deps=False`
policy — this is the same install shape the browser bootstrap will exercise, minus the browser.

**What this does NOT prove — the honest boundary still stands.** This is a CPython venv check, not a
Pyodide one. `import websockets.asyncio.server` inside Pyodide (Emscripten's asyncio/socket/ssl
surface differs from CPython's) is still UNTESTED by this task — that is GATE 0 / T0.1's job in this
same spec, which requires a real Pyodide kernel and has not run. What this decision closes is narrower
and structural: the wheel is provenance-verified, vendored, D2-covered, and will be fetched and
`micropip.install`-ed by the *existing* bootstrap code path with no further engineering — whatever
T0.1 finds when it actually runs in-kernel, it will be exercising this vendored wheel, not a live PyPI
fetch, and not a stub.

**Consequence for this spec's Risks and Open-questions entries below:** the "NEW, and the brainstorm
missed it" risk bullet and the first Open-questions bullet are RESOLVED by the above — the mechanism
question ("how does `websockets` get satisfied without a boot-time PyPI fetch") is answered; T0.1's
narrower question ("does `websockets.asyncio.server` actually import under Pyodide") remains open and
is unaffected by this decision either way, since it would apply equally to options (a), (b), or (c).

## Design

## Seam map (all paths real unless marked CREATE)

### Upstream source (read-only, never edited)
- `external/pylabrobot/pylabrobot/visualizer/` — `index.html`, `lib.js` (renderer, consumed byte-identical), `vis.js` (the only file with socket glue), `main.css`, `gif.js`, `gif.worker.js`, `img/{logo,integrated_arm,multi_channel_pipette,single_channel_pipette}.png`, `visualizer.py`.
- Submodule pinned at `d9651e2098cd269fc47e6aff80c9242a82d1b587` [RAN `git submodule status`]. Target pin is PLR 0.2.2 (`dd79c4c89`), owned by the wheel-pipeline area (debt-1289), NOT by this spec. Finding 1 above proves this spec's slice 1 works at either pin.

### Generated, committed vendor tree — CREATE `web-repl/overlay/assets/visualizer/`
Produced by CREATE `web-repl/scripts/vendor_visualizer.py`, a promotion of the verified spike generator at `/tmp/claude-1000/praxis-spikes/s4/build_harness.py`. Treatment per file:

| file | treatment |
|---|---|
| `lib.js` | byte-identical copy, sha256 asserted equal src↔out |
| `main.css`, `gif.js`, `gif.worker.js`, `img/` | plain copy |
| `vis.js` | 4 textual anchors, each asserting `count(old) == 1` (raise otherwise), + append the `window.receiveFromPython` bridge |
| `index.html` | 5 CDN tags → local `konva.min.js` / dropped; both `/favicon.png` → `./favicon.png`; all `{{ }}` placeholders removed; one `<script type="module" src="../visualizer-augmentations/index.js">` injected |
| `favicon.png` | copy of `img/logo.png` |
| `konva.min.js` | Konva 8.4.3, 158,587 bytes, md5 `28374db26d35a1227ce7142b26eda52a` |
| `VENDOR_MANIFEST.json` | CREATE — records source pin SHA, `pylabrobot.__version__`, per-file sha256, generator version |

The tree is COMMITTED, not gitignored. Rationale is empirical, not stylistic: `praxis/web-client/.gitignore:10` gitignores `/src/assets/jupyterlite/*`, and the resulting checked-in `assets/jupyterlite/build/` contains only `service-worker.js`, so `git clone && serve` yields a dead page [established by the standalone spike]. Do not reproduce that failure mode.

### Hand-authored extension point — CREATE `web-repl/overlay/assets/visualizer-augmentations/`
Deliberately OUTSIDE the regenerated tree, loaded by the single module tag the generator injects. Design rule: if an augmentation cannot be added without editing a generated file, the API does not exist.

### Python seam — CREATE `web-repl/overlay/assets/python/praxis/viz/`
`__init__.py`, `transport.py`, `browser.py`. Sits alongside the existing `praxis/web-client/src/assets/python/praxis/{__init__.py,interactive.py}` [RAN `ls`], which are already fetched by the bootstrap.

`BrowserVisualizer(pylabrobot.visualizer.Visualizer)` overrides exactly four members and injects one attribute:
- `__init__` → `super().__init__(resource, open_browser=False, name=<explicit>)`. `name=` is MANDATORY: `_detect_source_filename` (0.2.2:383) probes ipynbname / `jupyter_server.list_running_servers` / `urllib.request.urlopen` against a live Jupyter REST API, none of which exist in Pyodide.
- `setup()` → set `self._loop = _PyodideLoopShim(asyncio.get_running_loop())`, `self.setup_finished = True`, open transport, announce. No thread, no lock, no httpd, no websockets server.
- `has_connection()` → `self._transport.is_open`. (Must NOT call super — 0.2.2:307 reads `self._websocket`.)
- `async def send_command(self, event, data=None, wait_for_response=False)` → `serialized, id_ = self._assemble_command(event=event, data=data or {})` (INHERITED, 0.2.2:292 — reuses upstream's envelope and `_sanitize_floats`), then `self._transport.send(serialized)`. Raise `NotImplementedError` if `wait_for_response=True`. Note the inherited default is `True`; none of the four stock events use it.
- `stop()` → send `"stop"`, close transport. No `self.httpd`.

**Why the override set never names a serializer:** the 485 KB → 164 KB schema change between pins is exactly the `_serialize_with_methods` → `_serialize_resource_tree` + `_build_method_registry` split (d9651e2:52 vs 0.2.2:53/:65). Because we only override the funnel and inherit everything above it, that change is invisible to praxis code. This is the single reason A' was chosen over candidate C.

**THE TRAP — the #1 pre-mortem risk.** Three inherited callbacks reach `self.loop`, which upstream sets ONLY inside `_run_ws_server`:
- 0.2.2:698 `asyncio.run_coroutine_threadsafe(fut, self.loop)` — resource_assigned
- 0.2.2:707 `asyncio.run_coroutine_threadsafe(fut, self.loop)` — resource_unassigned
- 0.2.2:714 `self.loop.call_soon_threadsafe(self._enqueue_state_update, ...)` — state update
A subclass overriding only `send_command` renders the deck once (the plain `await` path) and then dies silently on the first `pick_up_tips`, with NO ack path because all four events use `wait_for_response=False`. `_PyodideLoopShim` (~15 lines, implementing `call_soon`, `call_soon_threadsafe`, `create_future`, and enough loop protocol for `run_coroutine_threadsafe`) exists to close this. **Documented fallback if the shim cannot satisfy WebLoop:** additionally override `_handle_resource_assigned_callback` (0.2.2:675), `_handle_resource_unassigned_callback` (:700), `_handle_state_update_callback` (:709) — +30 lines, removes the loop dependency entirely, at the cost of depending on three private names.

### Transport abstraction — `praxis/viz/transport.py`
```python
class VisualizerTransport(Protocol):
    def send(self, serialized: str) -> None: ...
    @property
    def is_open(self) -> bool: ...
```
Implementations: `BroadcastChannelTransport('praxis_viz')` (browser), `RecordingTransport` (pytest, no browser), `FileTransport` (`.plrviz` dump), `NullTransport`. Each wraps a bounded ring buffer exposing `viz.stats()` (monotonic send counter) and `viz.replay()`. The Protocol exists specifically so a `CommTransport` (runner-up design B, anywidget/Jupyter comm) can be dropped in later without touching `BrowserVisualizer`.

### Data flow
```
Pyodide kernel worker (DedicatedWorkerGlobalScope)
  Resource.assign_child_resource / state update
    -> inherited callbacks (0.2.2 :675/:700/:709)
      -> inherited _enqueue_state_update / _flush_state_updates (:716/:723)   [batching: 96-ch pickup = 1 msg]
        -> send_command  (OVERRIDDEN)
          -> _assemble_command  (INHERITED :292 — id/version/data/event + _sanitize_floats)
            -> VisualizerTransport.send(json_str) + ring buffer
              -> js.BroadcastChannel('praxis_viz').postMessage
                    | same-origin; no parent/child relationship needed
                    v
Visualizer iframe (Document, main thread)
  courier: onmessage -> window.receiveFromPython(event, data)
    -> handleEvent   [praxisViz.use middleware wraps here]
      -> processCentralEvent
        -> lib.js renderer (UNMODIFIED, 5853 lines)
```

**Channel name is `praxis_viz`, deliberately distinct from `praxis_repl`.** `praxis_repl` is the existing device-auth channel — `praxis_bootstrap.py:93` opens it and `:169` calls `web_bridge.register_broadcast_channel(ch)` [RAN grep]. That channel carries the commit-97a75988 user-gesture chain and MUST NOT be multiplexed with visualizer traffic; a malformed viz payload on that channel would degrade device authorization.

**Why not `js.self.postMessage`:** from inside the kernel worker that posts into `@jupyterlite/pyodide-kernel`'s own message protocol, where an unknown message type is at best ignored and at worst breaks the kernel driver.

**Handshake (solves BroadcastChannel's no-replay problem):** the iframe courier posts `{event:"ready"}` on `praxis_viz` when it initialises; the Python side responds by calling upstream's own `_send_resources_and_state()` (0.2.2:643). This is literally upstream's existing `"ready"` path from `_socket_handler` — reused, not reinvented. A late-loading iframe therefore recovers automatically.

**De-risking note:** BroadcastChannel from inside the kernel worker is already production code — `praxis_bootstrap.py:85-95` does exactly this, bidirectionally. And `asyncio.ensure_future(_run_async())` at `praxis_bootstrap.py:145` is called from a bare JS `onmessage` callback with no coroutine on the stack and works in production — the same situation `_flush_state_updates` is in.

### Augmentation API — three layers, all spike-verified, zero lib.js internals
```js
// A1 — event middleware (wraps window.handleEvent / window.processCentralEvent)
praxisViz.use((ctx, next) => { /* {id, event, data}; observe, mutate, or drop */ next(); });

// A2 — draw surface + coordinate registration
praxisViz.overlay                  // Konva.Layer({name:'praxis-overlay', listening:false}), stage.add()ed
praxisViz.anchor(resourceName)     // -> {x, y} in overlay-local coords

// A3 — Python side channel (emitted alongside the 4 stock events)
viz.emit("praxis:device_state", {...})
```
`anchor` must implement the verified inverse-transform that undoes the Y-flip lib.js sets at `lib.js:3218-3219` (`stage.scaleY(-1); stage.offsetY(canvasHeight)` — [RAN grep, confirmed at both pins]):
```js
stage.getAbsoluteTransform().copy().invert().point(resources[name].group.getAbsolutePosition())
```
Spike-measured: `plate_01_well_A1` screen `(287.71, 637.78)` → local `(272.37, 142.27)`; rings landed pixel-accurately (screenshot `/tmp/claude-1000/praxis-spikes/s4/out/12_overlay_registered.png`).

Total dependency surface of the API: the 4-event protocol (documented upstream contract), the `stage` / `resources` script-scope globals, and Konva's public API. None changed across d9651e2 → 0.2.2 → main. That is why this survives lib.js refactors.

### First augmentation — F3 "device-reality overlay"
Colour each machine/resource by the health of its ACTUAL browser transport: WebSerial/WebUSB/WebHID connected · permission not yet granted (needs the 97a75988 gesture dialog) · shim inert. Chosen because upstream structurally cannot ship it (no browser device layer), it serves product premise (b), it renders the confirmed-inert WebSerial bug as a visible badge instead of a buried `RuntimeError`, and it exercises all three layers end-to-end (A3 emits → A1 intercepts → A2 draws) — making it a proof of the API rather than a feature.

**Device-auth preservation (commit 97a75988) is a hard constraint.** F3 may only READ device state. Any "click to connect" affordance drawn on the overlay MUST route through `web_bridge.request_user_interaction()` → dialog → real button click. It must NEVER call `navigator.usb.requestDevice()` / `navigator.serial.requestPort()` / `navigator.hid.requestDevice()` from the Konva click handler, and must never call them from the kernel worker at all (no user gesture exists there).

### Drift detection
| | mechanism | gate |
|---|---|---|
| D2 | vis.js anchors assert exactly-one match at generate time; on failure print ±10 lines of surrounding upstream text | blocking per-PR |
| D4 | browserless pytest: scripted deck build + `pick_up_tips` against `RecordingTransport`; snapshot the EVENT SEQUENCE and payload keys | blocking per-PR |
| D3 | golden render: inject committed fixture, assert 396 shapes / 220 resources / 18 tree nodes; tipspot A1 `#40CDA1` → `white` | nightly, pinned system Chrome path |
| D1 | sha256 of every upstream file | REJECTED |

D1 is rejected on spike evidence: `lib.js` changed +39/-25 between 0.2.2 and main with byte-identical render results (396/220/18 both), so it would have false-alarmed on the single most important real bump. D3 cannot be a per-PR blocker because Playwright 1.62.0 wants chromium build 1234, which is unfetchable from a sandboxed environment (spike worked around with `chromium_headless_shell-1228` / Chrome-for-Testing 149.0.7827.55).

D3's expected numbers are pin-sensitive: 396 shapes / 3 layers at 0.2.2 and main; 355 shapes / 2 layers (no gridLayer) at d9651e2. The fixture and the expected counts must be regenerated together with any pin change.

### Escalation trigger
If the vis.js anchor count ever needs to exceed 4, that is a design regression, not a maintenance chore: stop and escalate to V4 (upstream a transport hook to PLR), which is the only structural fix. Tracked as a parallel slow track; nothing in this spec depends on it.

## Requirements

- **R1**
  - `text`: `web-repl/scripts/vendor_visualizer.py` regenerates the vendored visualizer tree from `external/pylabrobot/pylabrobot/visualizer/` and fails loudly if any vis.js textual anchor does not match exactly once.
  - `verification`: `uv run python web-repl/scripts/vendor_visualizer.py --src external/pylabrobot/pylabrobot/visualizer --out /tmp/claude-1000/praxis-spikes/regen` exits 0 and its log contains the 4 lines `vis.js edit applied: ack-send (handleEvent tail)` / `openSocket body` / `openSocket tail close of dead block` / `heartbeat`. Negative case: `sed -i 's/function heartbeat()/function heartbeat_X()/' <a scratch copy of vis.js>` then re-run with `--src` pointing at the mutated copy; the process must exit non-zero with a message naming the `heartbeat` anchor and printing surrounding upstream text. (Baseline already RAN this session with the spike generator: all 4 matched at pin d9651e2.)
- **R2**
  - `text`: `lib.js` is copied byte-identically — the renderer is never forked.
  - `verification`: `cmp external/pylabrobot/pylabrobot/visualizer/lib.js web-repl/overlay/assets/visualizer/lib.js` exits 0. Also `python3 -c "import hashlib;print(hashlib.sha256(open('web-repl/overlay/assets/visualizer/lib.js','rb').read()).hexdigest())"` equals the `lib.js` sha256 recorded in `VENDOR_MANIFEST.json` (at pin d9651e2 that is `a71f8874d33be713...`, RAN this session).
- **R3**
  - `text`: The vendored `index.html` references ZERO external hosts — the page loads with no CDN.
  - `verification`: `grep -c 'https://' web-repl/overlay/assets/visualizer/index.html` prints `0`. (RAN this session against the spike generator's output at pin d9651e2: printed 0.)
- **R4**
  - `text`: Konva 8.4.3 is vendored locally with verified provenance.
  - `verification`: `ls -l web-repl/overlay/assets/visualizer/konva.min.js` shows 158587 bytes and `md5sum` prints `28374db26d35a1227ce7142b26eda52a`; `head -c 200 web-repl/overlay/assets/visualizer/konva.min.js | grep -q 'Konva JavaScript Framework v8.4.3'`.
- **R5**
  - `text`: No absolute-path asset reference survives vendoring — the page works when served from a subdirectory (GitHub Pages `/praxis/`), not just a site root.
  - `verification`: `grep -nE 'href="/|src="/' web-repl/overlay/assets/visualizer/index.html` returns no matches (exit 1). Specifically both `/favicon.png` sites become `./favicon.png`: `grep -c './favicon.png' web-repl/overlay/assets/visualizer/index.html` prints `2`. And `test -f web-repl/overlay/assets/visualizer/favicon.png`. (I RAN the grep on the un-fixed generator output: `/favicon.png` present at index.html:8 and :22 — this requirement is a real regression fix, not a formality.)
- **R6**
  - `text`: All server-side template placeholders are removed; the page renders with no Python server substituting them.
  - `verification`: `grep -c '{{' web-repl/overlay/assets/visualizer/index.html` prints `0`. Note the count is pin-sensitive (3 placeholders at d9651e2, 4 at 0.2.2 incl. `{{ liquid_color }}` — both RAN this session), so the generator must strip by pattern, not by a hardcoded list.
- **R7**
  - `text`: The generated tree is COMMITTED to git, not gitignored — a clean clone serves a working page.
  - `verification`: **ORDER MATTERS — the existence clause comes FIRST and is the one that fails loudly.** `git ls-files web-repl/overlay/assets/visualizer/ | wc -l` is >= 11 (RAN: on a nonexistent directory this prints 0, so this clause is what makes the requirement fail on a missing tree); THEN `test -f web-repl/overlay/assets/visualizer/lib.js` succeeds; THEN `git check-ignore -v web-repl/overlay/assets/visualizer/lib.js` exits 1 (not ignored). **The check-ignore clause is pattern-only and CANNOT fail on a nonexistent path** (RAN: exits 1 for a path that does not exist), so it must never be the sole assertion and must never be reordered ahead of the existence clauses. ADR v2 §4.2. Contrast with the live failure this prevents: `git ls-files praxis/web-client/src/assets/jupyterlite/ | wc -l` currently prints 5 while the app needs ~64 MB of build output.
- **R8**
  - `text`: CI regenerates the vendored tree and fails on any drift (gate D2).
  - `verification`: In `.github/workflows/ci.yml`, a job runs `uv run python web-repl/scripts/vendor_visualizer.py --src external/pylabrobot/pylabrobot/visualizer --out web-repl/overlay/assets/visualizer` followed by `git diff --exit-code -- web-repl/overlay/assets/visualizer`. Locally reproducible: run both commands on a clean tree; the diff must exit 0.
- **R9**
  - `text`: The static vendored page renders a real deck from a committed fixture with NO Python and NO network.
  - `verification`: Serve the tree (`cd web-repl/dist && python3 -m http.server 8911`), drive headless Chromium with the fixture at `web-repl/tests/fixtures/visualizer/set_root_resource.json`, calling `window.receiveFromPython('set_root_resource', <fixture>)`, then assert in-page: `Object.keys(resources).length === 220`, `stage.find('Shape').length` equals the pin's expected count (396 at 0.2.2/main, 355 at d9651e2), and `pageerrors.length === 0`. Chromium must be launched with `executable_path=/home/marielle/.cache/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-linux64/chrome-headless-shell` — Playwright 1.62.0's expected build 1234 is NOT installed and its download host is not reachable from this sandbox.
- **R10**
  - `text`: `import pylabrobot.visualizer` succeeds inside a real Pyodide kernel at the target pin — including the `websockets` hard dependency.
  - `verification`: In-kernel probe returning JSON: `{'import_visualizer': <bool/err>, 'HAS_WEBSOCKETS': <bool>, 'websockets_version': <str>, 'construct': <bool/err>}` where `construct` is `bool(BrowserVisualizer(Deck(), name='probe'))`. MUST be executed in the JupyterLite kernel, not a CPython venv. This is a NEW blocking check: at 0.2.2, `visualizer.py:144` raises `RuntimeError('The visualizer requires websockets to be installed...')` from `__init__` when `HAS_WEBSOCKETS` is False; at d9651e2 the same check is at `:444` inside `setup()`. A pure-Python `websockets-17.0.1-py3-none-any.whl` exists on PyPI (RAN: `curl -s https://pypi.org/pypi/websockets/json`), but whether `import websockets.asyncio.server` succeeds under Pyodide is UNTESTED.
- **R11**
  - `text`: `_PyodideLoopShim` satisfies every loop member the inherited callbacks touch — proven by an actual state update, not by reading source.
  - `verification`: In-kernel: build a deck, attach `BrowserVisualizer` with `RecordingTransport`, `await lh.pick_up_tips(tip_rack['A1:D1'])`, then assert `viz.stats()['sent'] >= 2` AND that the recorded event sequence contains `set_root_resource` followed by at least one `set_state`. A result of exactly 1 (root only) is the documented FAILURE signature of the #1 pre-mortem risk and must fail the gate, not be reported as partial success.
- **R12**
  - `text`: The full Python→JS handoff works end-to-end in a real kernel: a `pick_up_tips` in the JupyterLite kernel visibly repaints the vendored iframe.
  - `verification`: Headless-Chromium run of the standalone site with the visualizer iframe present. Assert BEFORE: in-iframe `resources['tips_01_tipspot_A1'].group.findOne('Circle').fill() === '#40CDA1'`. Execute `await lh.pick_up_tips(tip_rack['A1:D1'])` in the kernel. Assert AFTER: the same fill is `'white'` and `resources['plate_01_well_A1']` volume is 100. Screenshot diff must show changed pixels confined to the tip column bbox. NOTHING IN ANY SPIKE HAS EVER RUN PLR VISUALIZER PYTHON IN PYODIDE — this is the SLICE 0 deliverable and a FAIL here is a valid, valuable result that redirects the design.
- **R13**
  - `text`: A 164 KB `set_root_resource` payload survives BroadcastChannel structured-clone from the kernel worker, and the cost is measured.
  - `verification`: In the R12 run, record `performance.now()` deltas around the courier's `onmessage` and log `JSON.stringify(data).length`. Assert the payload arrives intact (`Object.keys(resources).length === 220` after) and record the wall time. In-page `receiveFromPython` alone was measured at 34.6 ms for this payload; the worker→document hop has NEVER been measured. Record the number; do not assert a threshold on the first run.
- **R14**
  - `text`: `resource_assigned` and `resource_unassigned` are exercised — neither was touched by any spike.
  - `verification`: In-kernel: `deck.assign_child_resource(plate, ...)` then `plate.unassign()`. Assert the recorded event sequence contains both `resource_assigned` and `resource_unassigned`, and in the browser run assert no `pageerror` is raised. `resource_unassigned` is the risky one: it calls `snapshotResource()` → `res.serialize()` and `destroy()` in vis.js, an untested path.
- **R15**
  - `text`: A browserless pytest snapshots the event sequence and payload keys against `RecordingTransport` (gate D4).
  - `verification`: `uv run pytest web-repl/tests/viz/test_browser_visualizer.py -q` exits 0. NARROW RUN ONLY — do not invoke the whole suite (house rule: whole-suite runs exhaust swap on this box and are hook-blocked). The test must assert the ordered event list and the top-level key set of each payload, NOT a byte-exact payload, so that the `_serialize_with_methods` → `_serialize_resource_tree` + `_build_method_registry` schema change (the one that actually happened between pins) does not false-alarm.
- **R16**
  - `text`: `praxisViz.use()` middleware observes every event before the renderer sees it, without editing lib.js.
  - `verification`: In the R9 static-page run, register `praxisViz.use((ctx,next)=>{ (window.__seen ||= []).push(ctx.event); next(); })` from an injected module, then inject `set_root_resource` and a `set_state` delta. Assert `window.__seen` deep-equals `['set_root_resource','set_state']`. (The spike RAN the equivalent raw monkey-patch and observed `window.__central === ['set_state']` and intercepted keys `['tips_01_tipspot_A1',...]` — proving the wrapper runs in the real dispatch path.)
- **R17**
  - `text`: `praxisViz.anchor(name)` returns overlay-local coordinates that land pixel-accurately on the named resource, correctly undoing the stage Y-flip.
  - `verification`: In-page: `praxisViz.anchor('plate_01_well_A1')` returns `{x,y}` within 2 px of `(272.37, 142.27)` for the committed fixture at the pinned viewport, and drawing `new Konva.Circle({...praxisViz.anchor('plate_01_well_A1'), radius: 12})` on `praxisViz.overlay` produces a screenshot whose non-transparent overlay pixels fall inside the well's bounding box. Negative control: the naive `group.getAbsolutePosition()` without the inverse transform must land Y-mirrored — assert the two differ.
- **R18**
  - `text`: Augmentations load from a directory that is NEVER regenerated, and the loader survives regeneration.
  - `verification`: **Precondition, asserted first:** `test -d web-repl/overlay/assets/visualizer-augmentations && test -f web-repl/overlay/assets/visualizer/index.html`. THEN `uv run python web-repl/scripts/vendor_visualizer.py --out web-repl/overlay/assets/visualizer`, then `git diff --exit-code -- web-repl/overlay/assets/visualizer-augmentations` exits 0 (untouched) — **note this clause is vacuous on its own** (RAN: a pathspec matching nothing yields no diff and exits 0), which is why the precondition is mandatory — AND `grep -q 'visualizer-augmentations/index.js' web-repl/overlay/assets/visualizer/index.html` succeeds (the tag is re-injected; RAN: this exits 2 on a missing file, so it does fail loudly). **The sibling-directory NAME `visualizer-augmentations` is load-bearing and MUST NOT be shortened** — the generated `index.html` carries a relative `<script src>` to `visualizer-augmentations/index.js`, which only resolves while the two remain siblings under `overlay/assets/`. ADR v2 §2.1/§4.2.
- **R19**
  - `text`: The F3 device-reality overlay preserves the commit-97a75988 user-gesture chain — it never calls a `requestDevice`-family API outside a real button click.
  - `verification`: `grep -rnE 'requestDevice|requestPort' web-repl/overlay/assets/visualizer-augmentations/` exits **1 EXACTLY**. **Assert on the exit code, never on empty stdout** — a missing or renamed directory exits **2** with empty stdout (RAN), so an empty-stdout check would pass while verifying nothing, whereas `exit == 1` correctly fails. Precede it with `test -d web-repl/overlay/assets/visualizer-augmentations`. Any connect affordance must instead call `web_bridge.request_user_interaction()`; verify by `grep -rn 'request_user_interaction' web-repl/overlay/assets/python/praxis/viz/` returning at least one match if F3 exposes a connect action. Behavioural check: in a browser run, clicking the overlay badge must open the existing device-auth dialog, and the browser console must show no `NotAllowedError: Must be handling a user gesture`.
- **R20**
  - `text`: F3 exercises all three augmentation layers end-to-end — it is a proof of the API, not a feature bolted beside it.
  - `verification`: In one browser run, assert: (A3) the recorded transport log contains an event named `praxis:device_state`; (A1) a middleware registered by the augmentation observed that event; (A2) `stage.findOne('.praxis-overlay')` exists and its canvas has >0 non-transparent pixels. All three assertions in the same run, or the requirement fails.
- **R21**
  - `text`: Visualizer traffic never rides the `praxis_repl` channel that carries device authorization.
  - `verification`: `grep -rn "praxis_repl" web-repl/overlay/assets/python/praxis/viz/ web-repl/overlay/assets/visualizer/ web-repl/overlay/assets/visualizer-augmentations/` exits **1 EXACTLY** (assert the exit code, never empty stdout — a missing directory exits **2** with empty stdout, RAN, and would read as green); precede it with `test -d` on all three paths; `grep -rn "praxis_viz" web-repl/overlay/assets/python/praxis/viz/transport.py` returns at least one match. Rationale: `praxis_bootstrap.py:93` opens `praxis_repl` and `:169` registers it with `web_bridge` — it is the 97a75988 gesture channel.
- **R22**
  - `text`: The bootstrap fetch of `praxis/viz/browser.py` FAILS LOUDLY — it does not inherit the silent-warn failure mode.
  - `verification`: Rename `web-repl/overlay/assets/python/praxis/viz/browser.py` in a served scratch copy so the fetch 404s, then boot the kernel and assert the ready message carries a non-empty failure list (e.g. `praxis:ready` payload contains `{'failed': ['praxis/viz/browser.py']}`) rather than announcing a clean ready. Precedent this guards against, both RAN by prior spikes: `_sync_fetch` currently only `console.warn`s on failure, and the wheel-404 case still fired `praxis:ready` with pylabrobot absent.
- **R23**
  - `text`: `VENDOR_MANIFEST.json` records the exact upstream provenance, so a pin bump is auditable rather than archaeological.
  - `verification`: `python3 -c "import json;m=json.load(open('web-repl/overlay/assets/visualizer/VENDOR_MANIFEST.json'));print(m['source_sha'], m['pylabrobot_version'], len(m['files']))"` prints a 40-char SHA matching `git -C external/pylabrobot rev-parse HEAD`, the version string from `external/pylabrobot/pylabrobot/__version__.py`, and a file count >= 8.

## Tasks

- **T0.1**
  - `title`: SLICE 0a — probe pylabrobot.visualizer importability inside a real Pyodide kernel
  - `files`: ["/tmp/claude-1000/praxis-spikes/s5/probe_import.py", "web-repl/bootstrap/praxis_bootstrap.py"]
  - `detail`: CREATES scratch only; MUST NOT mutate the repo. Stand up the standalone site the way the standalone spike did (fresh `jupyter lite build` into scratch + tracked `praxis_bootstrap.py` overlaid; the checked-in `assets/jupyterlite/build/` has only `service-worker.js` and cannot serve). Drive headless Chromium with `executable_path=/home/marielle/.cache/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-linux64/chrome-headless-shell` and `dangerouslyDisableSandbox: true` (Playwright cannot launch under the agent sandbox: `apply-seccomp: unshare(CLONE_NEWUSER): Invalid argument`; and cdn.jsdelivr.net is not on the network allowlist). In-kernel, `await micropip.install('websockets')` then probe: `import websockets`, `import websockets.asyncio.server`, `pylabrobot.visualizer.visualizer.HAS_WEBSOCKETS`, `import pylabrobot.visualizer`, and `Visualizer.__init__` reachability. Report each as literal value-or-error-string. This is the NEW blocker: at 0.2.2 `visualizer.py:144` raises RuntimeError from `__init__` when HAS_WEBSOCKETS is False (at d9651e2 the check is at `:444` in `setup()`), and PLR 0.2.2 declares `websockets` a hard dependency. A FAIL is a valid result: report it verbatim and stop — do not work around it by monkeypatching HAS_WEBSOCKETS without saying so.
  - `depends_on`: []
- **T0.2**
  - `title`: SLICE 0b — probe _PyodideLoopShim against WebLoop
  - `files`: ["/tmp/claude-1000/praxis-spikes/s5/probe_loop.py"]
  - `detail`: CREATES scratch only. In the same kernel, get `asyncio.get_running_loop()` and probe, one at a time with literal results: (1) `loop.call_soon(fn)` fires; (2) `loop.call_soon_threadsafe(fn, arg)` fires; (3) `loop.create_future()` returns an awaitable future; (4) `asyncio.run_coroutine_threadsafe(coro, loop)` returns something and the coroutine actually runs. These are the exact four members the inherited callbacks touch (0.2.2 `visualizer.py:698`, `:707`, `:714`, `:721`). Prior evidence is one-directional only: `praxis_bootstrap.py:145` proves `asyncio.ensure_future` from a bare JS callback works in production; the other three are READ-only inferences. Output a table of which members are native, which need shimming, and which cannot be shimmed. If (4) is unshimmable, the answer is the +30-line callback-override fallback (override `_handle_resource_assigned_callback` / `_handle_resource_unassigned_callback` / `_handle_state_update_callback`) — record that verdict explicitly.
  - `depends_on`: ["T0.1"]
- **T0.3**
  - `title`: SLICE 0c — end-to-end Python→JS handoff proof in a real kernel
  - `files`: ["/tmp/claude-1000/praxis-spikes/s5/probe_e2e.py"]
  - `detail`: CREATES scratch only. Wire a throwaway `BrowserVisualizer` + `BroadcastChannelTransport('praxis_viz')` in the kernel, load the spike's vendored visualizer harness (`/tmp/claude-1000/praxis-spikes/spec-check/vis-pinned`, already generated and RAN this session) into an iframe with a courier that calls `window.receiveFromPython`. Then: build a deck, `await lh.pick_up_tips(tip_rack['A1:D1'])`, `deck.assign_child_resource(...)`, `plate.unassign()`. Satisfies R11, R12, R13, R14. Record: event sequence, `viz.stats()['sent']`, payload byte size, worker→document hop wall time, before/after Konva fills for `tips_01_tipspot_A1` (`#40CDA1` → `white`), and any pageerror verbatim. THE FAILURE SIGNATURE TO WATCH FOR: root renders, then nothing — that is the #1 pre-mortem risk and it is silent (all four events use `wait_for_response=False`). Report a PASS/FAIL verdict; a FAIL redirects T2.2 to the callback-override fallback or reopens runner-up design B (anywidget over Jupyter comm).
  - `depends_on`: ["T0.2"]
- **T1.1**
  - `title`: Promote the spike harness to web-repl/scripts/vendor_visualizer.py
  - `files`: ["web-repl/scripts/vendor_visualizer.py", "/tmp/claude-1000/praxis-spikes/s4/build_harness.py", "external/pylabrobot/pylabrobot/visualizer/"]
  - `detail`: CREATES `web-repl/scripts/vendor_visualizer.py`. Start from the verified generator at `/tmp/claude-1000/praxis-spikes/s4/build_harness.py` — I RAN it against the repo's current pin this session and all four anchors matched exactly once with zero external URLs left, so DO NOT re-derive the anchors. Keep: `argparse` + `logging` (house rule), the exactly-one-match assertion per anchor, the lib.js sha256 src↔out check, and the CDN strip regexes. ADD, all net-new: (a) rewrite BOTH `/favicon.png` occurrences (index.html:8 and :22@d9651e2 / :32@0.2.2) to `./favicon.png` — absolute paths break GH Pages subpath deploys, R5; (b) copy `img/logo.png` → `favicon.png`; (c) strip ALL `{{ ... }}` placeholders by pattern, not by list (3 at d9651e2, 4 at 0.2.2 — RAN); (d) inject `<script type="module" src="../visualizer-augmentations/index.js"></script>` exactly once; (e) emit `VENDOR_MANIFEST.json` with source SHA, `pylabrobot.__version__`, and per-file sha256 (R23); (f) on anchor mismatch, print ±10 lines of surrounding upstream text before exiting non-zero (D2 usability — the pre-mortem's failure-3 mitigation). Konva 8.4.3 is sourced from `/tmp/claude-1000/praxis-spikes/s4/konva.min.js` (158,587 B, md5 28374db26d35a1227ce7142b26eda52a) — note unpkg.com, the URL upstream declares, is UNREACHABLE from this sandbox (curl → 000); cdnjs and jsdelivr work.
  - `depends_on`: []
- **T1.2**
  - `title`: Generate and commit the vendored visualizer tree + Justfile recipe
  - `files`: ["web-repl/overlay/assets/visualizer/", "Justfile", "praxis/web-client/.gitignore"]
  - `detail`: CREATES `web-repl/overlay/assets/visualizer/` (generated output, COMMITTED). Run the generator against `external/pylabrobot/pylabrobot/visualizer` and `git add` the result. Add a `viz-vendor:` recipe to `Justfile` — it currently has only 5 recipes (`generate-db`, `test`, `test-changed`, `lint`, `build`; RAN grep), so this is net-new. Verify `praxis/web-client/.gitignore` does NOT swallow the new path: line 10 is `/src/assets/jupyterlite/*`, and that exact pattern is why the checked-in jupyterlite tree has only 5 tracked files and a clean clone serves a dead page. Satisfies R2, R3, R4, R5, R6, R7, R23.
  - `depends_on`: ["T1.1"]
- **T1.3**
  - `title`: Wire the D2 regeneration gate into CI
  - `files`: [".github/workflows/ci.yml"]
  - `detail`: EDITS the existing `.github/workflows/ci.yml`. Add a job that runs `uv run python web-repl/scripts/vendor_visualizer.py --src external/pylabrobot/pylabrobot/visualizer --out web-repl/overlay/assets/visualizer` then `git diff --exit-code -- web-repl/overlay/assets/visualizer`. Blocking per-PR. Must NOT add an sha256-of-every-upstream-file check (rejected D1): lib.js changed +39/-25 between 0.2.2 and main with byte-identical render output, so D1 would have false-alarmed on the most important real bump. Requires the submodule to be checked out in CI. Satisfies R8.
  - `depends_on`: ["T1.2"]
- **T1.4**
  - `title`: Commit golden payload fixtures and a browserless static-render check
  - `files`: ["web-repl/tests/fixtures/visualizer/set_root_resource.json", "web-repl/tests/fixtures/visualizer/delta_set_state.json", "scripts/viz_render_check.py"]
  - `detail`: CREATES all three. Source the payloads from the spike captures at `/tmp/claude-1000/praxis-spikes/s4/payloads/` (0.2.2) or `payloads-pinned/` — MUST match the pin the vendored tree was generated from, since the schema differs (`_serialize_with_methods` at d9651e2 vs `_serialize_resource_tree` + `_build_method_registry` at 0.2.2; 485 KB vs 164 KB). `scripts/viz_render_check.py` serves the tree, injects the fixture via `window.receiveFromPython`, and asserts 220 resources / the pin's shape count (396 at 0.2.2+, 355 at d9651e2) / 0 pageerrors, then injects the delta and asserts `tips_01_tipspot_A1` fill goes `#40CDA1` → `white`. Must accept `--chrome <path>` and default to `/home/marielle/.cache/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-linux64/chrome-headless-shell`; document in the script docstring that Playwright 1.62.0's expected build 1234 cannot be downloaded here. Satisfies R9; becomes the D3 nightly body in T3.3.
  - `depends_on`: ["T1.2"]
- **T2.1**
  - `title`: Implement the transport layer with a bounded ring buffer
  - `files`: ["web-repl/overlay/assets/python/praxis/viz/__init__.py", "web-repl/overlay/assets/python/praxis/viz/transport.py"]
  - `detail`: CREATES both. `VisualizerTransport` Protocol (`send(serialized: str) -> None`, `is_open` property) plus `BroadcastChannelTransport('praxis_viz')`, `RecordingTransport`, `FileTransport`, `NullTransport`. Each wraps a bounded ring buffer exposing a monotonic send counter (for `viz.stats()`) and `viz.replay()`. The channel name MUST be `praxis_viz`, never `praxis_repl` — the latter is opened at `praxis_bootstrap.py:93` and registered with `web_bridge` at `:169` and carries the commit-97a75988 device-auth gesture chain; multiplexing viz payloads onto it risks degrading device authorization (R21). `BroadcastChannelTransport` must handle the `js.BroadcastChannel.new(...)` vs `js.BroadcastChannel(...)` split the bootstrap already handles at `:93-95`.
  - `depends_on`: ["T0.3"]
- **T2.2**
  - `title`: Implement BrowserVisualizer and _PyodideLoopShim
  - `files`: ["web-repl/overlay/assets/python/praxis/viz/browser.py", "external/pylabrobot/pylabrobot/visualizer/visualizer.py"]
  - `detail`: CREATES `browser.py`. Subclass `pylabrobot.visualizer.Visualizer`, overriding EXACTLY four members — `setup`, `stop`, `has_connection`, `send_command` — plus injecting `self._loop = _PyodideLoopShim(asyncio.get_running_loop())` in `setup()`. Signature notes verified by READ at 0.2.2 (`/tmp/claude-1000/praxis-spikes/plr-022/pylabrobot/visualizer/visualizer.py`): `send_command` is `async def (self, event, data=None, wait_for_response=True)` at `:312` — the inherited DEFAULT is True, so the override must explicitly raise `NotImplementedError` on True rather than silently returning None; `has_connection` at `:307` reads `self._websocket` (underscore) so the override must not delegate; `_assemble_command` at `:292` is inherited and supplies id/version/data/event + `_sanitize_floats`. `__init__` MUST pass `name=<explicit>` to skip `_detect_source_filename` (`:383`), which probes `jupyter_server.list_running_servers` and `urllib.request.urlopen` against a live Jupyter REST API. DO NOT name any serializer function — the whole point of A' is that `_serialize_with_methods` vs `_serialize_resource_tree`+`_build_method_registry` stays invisible. Implement `_PyodideLoopShim` per the T0.2 verdict; if T0.2 found `run_coroutine_threadsafe` unshimmable, implement the documented fallback instead: additionally override `_handle_resource_assigned_callback` (`:675`), `_handle_resource_unassigned_callback` (`:700`), `_handle_state_update_callback` (`:709`), and record in the module docstring that this depends on three private upstream names. Also implement `viz.emit(event, data)` (A3) and the `{event:'ready'}` handshake that responds by calling inherited `_send_resources_and_state()` (`:643`). Satisfies R11, R14.
  - `depends_on`: ["T2.1"]
- **T2.3**
  - `title`: Wire praxis/viz into the bootstrap with fail-loud fetch semantics
  - `files`: ["web-repl/bootstrap/praxis_bootstrap.py"]
  - `detail`: EDITS the `other_files` dict at `praxis_bootstrap.py:190-194` to add `praxis/viz/__init__.py`, `praxis/viz/transport.py`, `praxis/viz/browser.py` alongside the existing `web_bridge.py` / `praxis/__init__.py` / `praxis/interactive.py` entries. CRITICAL: do NOT inherit the existing silent-failure mode — `_sync_fetch` failures currently only emit `js.console.warn` (`:206-209`), which is the same class of bug as the wheel-404 that still fired `praxis:ready` with pylabrobot absent (RAN by a prior spike). Collect fetch failures into a list and include it in the `praxis:ready` payload constructed at `:286-289` so a consumer can detect a broken boot. Satisfies R22.
  - `depends_on`: ["T2.2"]
- **T2.4**
  - `title`: Browserless pytest against RecordingTransport (gate D4)
  - `files`: ["web-repl/tests/viz/test_browser_visualizer.py", "web-repl/tests/viz/__init__.py"]
  - `detail`: CREATES both. Build a scripted deck (STARLet + tip carrier + plate carrier, matching the spike's 220-resource deck), attach `BrowserVisualizer` with `RecordingTransport`, run `pick_up_tips` on `A1:D1`, an `assign_child_resource`, and an `unassign`. Assert the ORDERED event list and the top-level key set of each payload — deliberately NOT a byte-exact snapshot, because the payload schema is the surface that actually changed between pins (485 KB → 164 KB). Assert `viz.stats()['sent'] >= 4`. Run NARROW ONLY: `uv run pytest web-repl/tests/viz/test_browser_visualizer.py -q`. Never invoke the whole suite (house rule; hook-blocked). Satisfies R15.
  - `depends_on`: ["T2.2"]
- **T3.1**
  - `title`: Implement the praxisViz runtime (A1 middleware, A2 overlay + anchor, A3 receive)
  - `files`: ["web-repl/overlay/assets/visualizer-augmentations/index.js", "web-repl/overlay/assets/visualizer-augmentations/praxis-viz.js"]
  - `detail`: CREATES both — hand-authored, OUTSIDE the generated tree, loaded by the single module tag T1.1 injects. `praxisViz.use(fn)` wraps `window.handleEvent` / `window.processCentralEvent` (both verified monkey-patchable by the spike: wrapping observed `window.__central === ['set_state']` and the real intercepted keys, proving the wrapper ran in the live dispatch path). `praxisViz.overlay` is a `Konva.Layer({name:'praxis-overlay', listening:false})` added via `stage.add()` (spike-verified: stage children went 3 → 4 and a 4th canvas appeared). `praxisViz.anchor(name)` MUST use `stage.getAbsoluteTransform().copy().invert().point(resources[name].group.getAbsolutePosition())` to undo the Y-flip set at `lib.js:3218-3219` (`stage.scaleY(-1); stage.offsetY(canvasHeight)` — RAN grep, present at both pins); the naive `getAbsolutePosition()` lands Y-mirrored. Depend ONLY on the 4-event protocol, the `stage`/`resources` script-scope globals, and Konva's public API — never a lib.js internal. Satisfies R16, R17, R18.
  - `depends_on`: ["T1.2"]
- **T3.2**
  - `title`: Build the F3 device-reality overlay as the API proof
  - `files`: ["web-repl/overlay/assets/visualizer-augmentations/device-reality.js", "web-repl/overlay/assets/python/praxis/viz/browser.py", "praxis/web-client/src/assets/python/web_bridge.py"]
  - `detail`: CREATES `device-reality.js`; EDITS `browser.py` to emit `praxis:device_state` via A3. Colour each machine/resource by real browser transport health: connected · permission-not-yet-granted · shim inert. HARD CONSTRAINT (commit 97a75988): the overlay may only READ device state. `grep -rnE 'requestDevice|requestPort'` over the augmentations dir must return nothing. Any connect affordance routes through `web_bridge.request_user_interaction()` → dialog → real button click; WebUSB/WebHID `requestDevice()` requires a user gesture the Pyodide worker cannot produce, and calling it from a Konva handler or from the kernel will throw `NotAllowedError`. Note this augmentation will legitimately render WebSerial as INERT: `web_serial_shim.py:24` does `from js import ... window`, which does not exist in the `DedicatedWorkerGlobalScope` the kernel runs in, so `IN_PYODIDE=False` and every `WebSerial(...)` raises `RuntimeError` (RAN by the standalone spike). Surfacing that as a visible badge is the point. Satisfies R19, R20.
  - `depends_on`: ["T3.1", "T2.2"]
- **T3.3**
  - `title`: Wire the D3 golden-render check as a nightly CI job
  - `files`: [".github/workflows/ci.yml", "scripts/viz_render_check.py"]
  - `detail`: EDITS `ci.yml` to add a scheduled (nightly) job invoking `scripts/viz_render_check.py`. NOT a per-PR blocker: the spike established that Playwright 1.62.0's expected chromium build 1234 is unfetchable from a sandboxed environment, so the job must pin a system Chrome path and be allowed to be skipped-with-notice rather than blocking merges. Expected numbers are pin-sensitive and must be regenerated alongside any submodule bump (396 shapes / 3 layers at 0.2.2 and main; 355 / 2 at d9651e2).
  - `depends_on`: ["T1.4", "T3.2"]

## Gates

- GATE 0 (BLOCKING, before any repo mutation in slices 2-3) — SLICE 0 verdict. T0.1 + T0.2 + T0.3 must produce a written PASS/FAIL with literal outputs. PASS requires all of: `import pylabrobot.visualizer` succeeds in a real Pyodide kernel with `HAS_WEBSOCKETS` True (R10); `BrowserVisualizer(...)` constructs without the 0.2.2 `visualizer.py:144` RuntimeError; and a `pick_up_tips` produces at least one `set_state` AFTER the initial `set_root_resource` (R11, R12). The specific FAIL to watch for is 'root rendered, nothing after' — it is silent because every event uses `wait_for_response=False`. A FAIL is a legitimate deliverable: it redirects T2.2 to the +30-line callback-override fallback, or reopens runner-up design B (anywidget over Jupyter comm). DO NOT proceed to T2.1 on a partial pass.
- GATE 1 (blocking, ends slice 1) — vendoring is reproducible and the static page renders with no Python. `uv run python web-repl/scripts/vendor_visualizer.py --src external/pylabrobot/pylabrobot/visualizer --out web-repl/overlay/assets/visualizer && git diff --exit-code -- web-repl/overlay/assets/visualizer` exits 0; `cmp` on lib.js exits 0; `grep -c 'https://' .../index.html` prints 0; `grep -E 'href="/|src="/' .../index.html` exits 1; `uv run python scripts/viz_render_check.py` asserts 220 resources / the pin's shape count / 0 pageerrors. Slice 1 does NOT depend on GATE 0 — I RAN the generator against the repo's current pin this session and all four anchors matched, so slices 0 and 1 can proceed in parallel.
- GATE 2 (blocking, ends slice 2) — the Python seam holds without a browser and with one. `uv run pytest web-repl/tests/viz/test_browser_visualizer.py -q` exits 0 with the event-sequence snapshot green (R15), AND the T0.3 end-to-end browser run is re-executed against the committed `browser.py`/`transport.py` (not the scratch prototype) showing `tips_01_tipspot_A1` fill `#40CDA1` → `white` (R12) plus both `resource_assigned` and `resource_unassigned` firing without pageerrors (R14). Record the measured worker→document structured-clone cost for the 164 KB payload (R13) — record, do not gate on a threshold.
- GATE 3 (blocking, ends slice 3) — the augmentation API is proven by an independent user. In one browser run, F3 must satisfy all three of R20's assertions simultaneously (A3 event in the transport log, A1 middleware observed it, A2 overlay has non-transparent pixels), AND `grep -rnE 'requestDevice|requestPort' web-repl/overlay/assets/visualizer-augmentations/` must exit 1 (R19, the 97a75988 gesture chain), AND regenerating the vendor tree must leave `visualizer-augmentations/` byte-identical (R18).
- GATE X (design regression, fires any time) — if `web-repl/scripts/vendor_visualizer.py` ever needs a FIFTH vis.js anchor, STOP. Do not add it. Escalate to V4 (upstream a transport hook into PLR), the only structural fix. Anchor-count growth is the pre-mortem's failure-3 signature: D2 fires, re-anchoring requires understanding vis.js, it gets deferred, the pin freezes three versions behind.

## Risks

- THE PRIMARY RISK, and it is silent. `_PyodideLoopShim` may not satisfy `asyncio.run_coroutine_threadsafe` / `call_soon_threadsafe` under Pyodide's WebLoop. Because `set_root_resource` travels the plain `await` path, the first demo looks perfect; every subsequent state update then dies inside an inherited Resource callback (0.2.2 `visualizer.py:698`/`:707`/`:714`) with no ack path, since all four events use `wait_for_response=False`. This would be the THIRD silent failure in a codebase already characterised by them (wheel-404 still fires `praxis:ready`; WebSerial is inert while the shell reports healthy). Mitigations, all in-spec: GATE 0 is blocking, `viz.stats()` exposes a monotonic counter, and D4 asserts event SEQUENCE not just presence.
- NEW, and the brainstorm missed it: at the 0.2.2 target pin, `Visualizer.__init__` (`visualizer.py:113`) raises `RuntimeError` at `:144` when `HAS_WEBSOCKETS` is False — so `BrowserVisualizer` cannot even be constructed unless `import websockets.asyncio.server` succeeds under Pyodide. At the currently-pinned d9651e2 the check sits at `:444` inside `setup()`, which we override, so the risk is INTRODUCED BY THE PIN BUMP, not present today. **RESOLVED 260818** — see "Decision: the `websockets` hard dependency is met by a VENDORED WHEEL" above. `websockets-17.0.1-py3-none-any.whl` is vendored into `overlay/assets/wheels/` (D2-covered, zero code changes) rather than fetched from PyPI at boot (which would violate GATE G5's offline requirement) or stubbed (a real dependency-free library is strictly less maintenance than a hand-kept stub). Whether the real import succeeds *inside Pyodide specifically* is still T0.1's open question, immediately below and in Open questions — this resolves the mechanism, not that empirical result.
- Vendored-tree rot. D2 catches drift but does not fix it; re-anchoring requires understanding vis.js, which invites deferral until the pin freezes. Mitigated by GATE X (anchor count > 4 escalates to V4) and by D2 printing surrounding upstream text so re-anchoring is mechanical rather than archaeological.
- The augmentation API ends up with exactly one user forever, because augmentations can only live inside a CI-regenerated tree. Mitigated structurally: `visualizer-augmentations/` is hand-authored, never regenerated, and R18 asserts regeneration leaves it untouched.
- Pin-shape coupling. The `set_root_resource` schema is NOT stable across candidate pins (485 KB with per-node method signatures at d9651e2 vs 164 KB with a per-class `method_registry` at 0.2.2 vs 137 KB at main), and D3's expected shape count differs too (355/2-layer at d9651e2 vs 396/3-layer at 0.2.2+). The renderer, the fixtures, and the serializer MUST all come from the same pin. `VENDOR_MANIFEST.json` (R23) makes the coupling auditable; a pin bump is a coordinated change to the vendor tree, the fixtures, and the D3 expected numbers.
- 0.2.2 looks modern in August 2026 and legacy by winter. At 0.2.2 there is no `pylabrobot.legacy` and `pylabrobot.liquid_handling` IS the modern non-deprecated home — so targeting 0.2.2 satisfies the prefer-modern directive with zero legacy fallback, and debt-1291 is a non-issue at this pin. Re-evaluation trigger: the first TAGGED release containing `pylabrobot.legacy` (when the v1b1 reorg ships), at which point `pylabrobot.legacy.liquid_handling` becomes the modern reference and this decision must be revisited. Recorded as a DATED decision, not a permanent one.
- This spec's target pin depends on debt-1289 (the wheel pipeline) landing — the shipped wheel is `pylabrobot-0.1.6-py3-none-any.whl` and the literal filename is hardcoded at three sites I confirmed by grep (`praxis_bootstrap.py:33`, `direct-control-kernel.service.ts:88`, `python.worker.ts:406`) plus a `jupyter-lite.gh-pages.json` index entry. A bump missing any one 404s silently. This spec does NOT own that work; slice 1 is deliberately pin-agnostic so it cannot be blocked by it.
- Device-auth regression. Any 'click to connect' affordance drawn on the Konva overlay is one careless line away from calling `navigator.usb.requestDevice()` directly and throwing `NotAllowedError` from a context with no user gesture — breaking the chain commit 97a75988 established. Mitigated by R19's grep gate and by keeping F3 read-only by default.
- Bootstrap-CSS-less UI panels were never audited. The main canvas, toolbar and Workcell Tree render correctly in spike screenshots and lib.js uses zero bootstrap JS (`grep -c 'bootstrap|new bootstrap' lib.js` → 0), but sidebar and machine-tool modals were never clicked through. Dropping bootstrap CSS could visually break panels no spike opened.
- Konva provenance is one hop off the upstream-declared source. Upstream loads it from unpkg; unpkg is unreachable from this sandbox (curl → 000), so the vendored bytes came from cdnjs and were never diffed against unpkg. Low risk (version-pinned, banner-verified, md5 recorded) but honestly not byte-verified against the declared origin.

## Open questions

- Does `import websockets.asyncio.server` succeed inside Pyodide? STILL UNTESTED (this is the one part of the websockets question that stays open -- see the Decision section above for what IS now resolved: the wheel is vendored, D2-covered, and installed by the existing `manifest["wheels"]` loop with zero boot-time PyPI fetch, so whatever T0.1 finds, it exercises the vendored wheel, not a live fetch or a stub). A pure-Python `websockets-17.0.1-py3-none-any.whl` exists on PyPI (I RAN `curl -s https://pypi.org/pypi/websockets/17.0.1/json`, and separately downloaded and sha256-verified it against PyPI's own digest, 260818), so it installs cleanly under CPython (RAN, throwaway venv, `HAS_WEBSOCKETS: true`), but the module pulls asyncio/socket/ssl/threading machinery that Pyodide only partially provides, and CPython-venv success does not predict Pyodide/Emscripten success. This gates `BrowserVisualizer.__init__` at the 0.2.2 pin (see risks). PROVE IT: T0.1's in-kernel probe. It has never been run.
- Does Pyodide's WebLoop support `asyncio.run_coroutine_threadsafe` and `call_soon_threadsafe`? INFERRED FROM READING SOURCE ONLY. The only production evidence is one-directional: `praxis_bootstrap.py:145` proves `asyncio.ensure_future` works from a bare JS `onmessage` callback with no coroutine on the stack. The other three loop members are unverified. PROVE IT: T0.2.
- Has ANY PyLabRobot visualizer Python ever run in Pyodide? NO. Every visualizer spike drove the renderer from Playwright `page.evaluate` with hand-built payloads. The entire Python→JS handoff is unproven. `visualizer.py` imports `http.server`, `threading`, `webbrowser` and optionally `websockets` at module scope — even `import pylabrobot.visualizer` is untested there. PROVE IT: T0.1 + T0.3.
- What does a 164 KB structured-clone across BroadcastChannel from a worker actually cost? UNMEASURED. Only the in-page `receiveFromPython` half was measured (34.6 ms full deck, 2.2 ms full set_state, 0.2 ms delta). The worker→document hop has no number. R13 says record it, deliberately without asserting a threshold on the first run.
- Do `resource_assigned` and `resource_unassigned` work at all? NEVER EXERCISED by any spike — only `set_root_resource` and `set_state` (full and delta) were. `resource_unassigned` is the riskier one: it calls `snapshotResource()` → `res.serialize()` and `destroy()` in vis.js. R14/T0.3 covers it.
- Do the visualizer's sidebar and machine-tool panels still look right without bootstrap CSS? NOT AUDITED. Canvas, toolbar and Workcell Tree verified by screenshot; no modal was ever opened. Needs a manual click-through, which no automated gate in this spec covers.
- Is a host page / two-iframe shell needed, and what owns it? ENTIRELY UNTESTED. Nothing in either spike exercised a host page. The visualizer iframe must be embedded somewhere, and the REPL app alone has no file browser — so the host-page choice is entangled with the notebook-persistence question below and may still change under slice 3.
- Notebook persistence (product deliverable a) is untested and may force an app change. The JupyterLite REPL app has no file browser; savable notebooks additionally require shipping the `lab/` or `notebooks/` app plus the contents-API storage layer. If that lands, the visualizer's host surface changes with it. Out of scope here, but it is a live dependency on this spec's slice-3 shape.
- Should the vendored visualizer inherit the site's internet dependency? The standalone spike proved the JupyterLite payload fetches ~30 MB from cdn.jsdelivr.net at runtime and, offline, hangs at `[*]` forever with NO error UI. The visualizer tree itself is fully offline-capable after Konva vendoring — so the visualizer would work offline while the kernel that drives it would not. Whether to vendor the pyodide distribution (a separate, larger decision) is not settled and is not this spec's call.
- What exactly does the `{event:'ready'}` handshake do if the kernel is not yet up when the iframe loads, or if two iframes open on the same channel? The reuse of upstream's `_send_resources_and_state()` handles the late-iframe case by construction, but the no-kernel-yet and duplicate-listener cases are undesigned. Worth resolving during T2.2 rather than discovering in the field.
- Konva 8.4.3 bytes were obtained from cdnjs, not the unpkg URL upstream declares, because unpkg is unreachable from this sandbox. They were never diffed against unpkg. Anyone with unpkg access should confirm md5 `28374db26d35a1227ce7142b26eda52a` matches `https://unpkg.com/konva@8/konva.min.js`.
- The brainstorm's own repo-mutation note flags that `brainstorm_finalize` wrote `.praxia/docs/specs/260817_visualizer-transport-shim-and-augmentati-2.md` into the real repo despite the do-not-mutate instruction. I did not touch it; the working tree is already dirty from that write and from the pre-existing test-file modifications shown in `git status`. Someone should decide whether that spec file is kept, moved, or reverted before the fixer starts — the house rule is to commit or stash dirty areas before dispatching implementation work.

## Surviving concerns (non-blocking, from adversarial review)

- SCOPE GROWTH IS SUBSTANTIAL AND SHOULD BE RE-PLANNED, NOT ABSORBED SILENTLY. The accepted fixes add one new task (T2.5, a framework-free static shell that re-implements the Angular device-auth dialog responders and hosts the courier) and eleven new requirements (R24-R34). T2.5 in particular is arguably a different area's deliverable (the Angular-free shell for the standalone site) that this spec now owns by necessity. The revised spec should either claim it explicitly with a sizing note or hand it to the shell/standalone area with a blocking cross-reference.
- THE THREE-PIN INCOHERENCE IS DETECTED, NOT CURED. After R24 lands, GATE 2 will correctly FAIL on the current tree (vendored renderer d9651e2 vs shipped wheel 0.1.6 vs stated target 0.2.2). Nothing in this spec produces a coherent wheel. Whoever schedules this must sequence debt-1289 ahead of slice 2 or slice 2 cannot exit.
- Bootstrap-CSS-less UI panels (sidebar modals, machine-tool panels) remain unaudited. C10's fix disables `show_machine_tools` at start, which removes the immediate collision but also removes the only path that would have exercised `openAllMachineToolPanels` — so the gap is now less likely to bite and less likely to be discovered. Keep it in open_questions with a manual click-through owner.
- Konva 8.4.3 bytes were sourced from cdnjs and never diffed against the unpkg URL upstream declares (unpkg unreachable from this sandbox). Version-pinned, banner- and md5-recorded, but not provenance-verified against the declared origin.
- Notebook persistence (product deliverable a) still entangles the shell's app choice (`repl/` vs `lab/`). C19's fix asserts the courier contract is invariant under that choice; that assertion is reasonable but untested.
- Repo hygiene precondition: the working tree is already dirty, including `.praxia/docs/specs/260817_visualizer-transport-shim-and-augmentati-2.md` written by `brainstorm_finalize` in violation of the do-not-mutate instruction. Decide keep/move/revert and commit or stash before dispatching any fixer, per house rules.
