# S-E: hardware gesture spike — human-run protocol

task_id: `260817_praxis_repl_refocus` · spike: S-E (`.praxia/docs/plans/260817_praxis-repl-refocus-execution-plan.md` §Phase 2, GATE G2 criterion 5)

## Why you're being asked to do this by hand

This is **the only unknown in the whole refocus that can invalidate an entire
architecture.** Everything else in the spike battery (S-A/B/C/D/F) ran headlessly.
This one cannot, and no amount of code-reading substitutes for it:

- **PASS** → Phase 5 builds `praxis-shell.js` on **design B-prime** (the JupyterLite
  build itself becomes the top-level document your browser loads).
- **FAIL, or materially worse than the iframe** → the architecture reverts to
  **design A** (a thin vanilla host page with the kernel in an `<iframe>`) — a
  pre-agreed, non-embarrassing reversal, not a failure of your time.

Headless Chromium already reports `navigator.serial`, `navigator.usb`, and
`navigator.hid` as all present and `isSecureContext === true` over
`http://127.0.0.1` (verified 2026-08-17). **That is not the same thing as a real
grant.** `requestDevice()`/`requestPort()` require a live user-activation gesture —
an actual human clicking an actual button in an actual (non-headless) browser window,
with an actual USB/serial/HID device plugged in. Nothing else can produce that.

> Prior-run finding worth repeating here, verbatim, from the research doc: *"Disbelieve
> any S-E PASS that does not name the device."* If whoever reads this run's output
> can't tell you the exact make/VID:PID of the device that was plugged in, treat the
> PASS as unproven.

## What this script proves on its own, and what only you can prove

**Read this before you run anything — it tells you which parts of a "PASS" you are
personally responsible for.**

| Claim | Proven by the script alone (headless-adjacent self-check) | Proven only by you running it for real |
|---|---|---|
| `navigator.{serial,usb,hid}` API surface is present over `http://127.0.0.1` | ✅ (repl_smoke.py, prior run) | — |
| The static server serves both the real repo assets and this spike's overlay host page correctly, on one origin | ✅ (verified directly, no browser needed) | — |
| Chromium launches non-headless with the sandbox disabled and the real REPL console loads with zero page/console errors | ✅ (self-check, 4 runs) | — |
| The real Pyodide kernel boots far enough to load IPython/jedi/parso | ✅ (self-check) | — |
| The real Pyodide kernel goes on to fetch the unmodified shims/`web_bridge.py` and posts a real `USER_INTERACTION`/`device_connect` message, i.e. reaches the actual human-pause point | ✅ (self-check, headless, reached in ~8s — see "Honest limitation" below for the defect that made 4 earlier attempts fail and what that does *not* prove) | ✅ (your terminal's progress line will show `pending={...}` once it happens) |
| A real visible button appears in a real (non-headless) Chromium window | ❌ not observed by the self-check (never reached) | ✅ |
| `requestDevice()`/`requestPort()` actually resolves with a real device, inside a real user-activation window, when a human clicks | ❌ — **cannot be simulated. A synthetic `dispatchEvent` click carries no activation and would prove the opposite of what it claims to prove (see execution plan §"three test-design traps", trap 2).** | ✅ **only you, clicking with a real device plugged in** |
| The kernel can then actually open/read/write the granted device | ❌ | ✅ (script attempts it automatically right after your click; you read the result) |
| Whether the grant persists across a page reload | ❌ | ✅ (script does the reload + recheck automatically; no second gesture needed for this part) |
| Whether design A (iframe) behaves differently from design B-prime (top-level) for any of the above | ❌ | ✅ (you run the script once per topology; script diffs are your evidence) |

If you only run the self-check and never plug in a device, **G2 criterion 5 remains
UNMET.** That is the honest, expected state until you do the real run below.

## What you need

- **A physical device** with a WebSerial-, WebUSB-, or WebHID-capable USB connection.
  Any USB peripheral works for a first pass (an FTDI USB-serial adapter is the closest
  match to what praxis actually drives in production, but even a random USB mouse/HID
  device is enough to prove the *grant mechanics* work — the read/write step will just
  report "no meaningful protocol to speak" for a non-praxis device, which is fine and
  expected; the run still answers the gesture question).
- Chrome/Chromium's device picker needs the OS to actually see the device
  (`lsusb` on Linux should list it before you start).
- A normal terminal — **not** a sandboxed tool call. This launches a real, visible,
  non-headless browser window that you will personally click inside.

## Exact command

From a normal terminal (any working directory — the script anchors itself to the repo
via `pyproject.toml` lookup):

```bash
cd /tmp/claude-1000/praxis-spikes/S-E

# One topology, one API, generous timeout (10 min to find/plug in the device + click):
uv run --project /home/marielle/projects/praxis python3 gesture_spike.py \
  --topology toplevel --api serial \
  --human-timeout 600 \
  --out results_toplevel_serial.json -v

# Then the comparison run — SAME device, iframe-embedded topology:
uv run --project /home/marielle/projects/praxis python3 gesture_spike.py \
  --topology iframe --api serial \
  --human-timeout 600 \
  --out results_iframe_serial.json -v
```

If your machine has no real X display available to a plain terminal session (unlikely
if you're at a normal desktop; more likely if you're SSH'd in without `-X`/`-Y`), you
need "non-sandboxed, non-headless Chromium" conditions — i.e. a real display server.
`ssh -X` / a local desktop session / VNC all satisfy this. **Do not run this through a
sandboxed agent tool call** — Chromium's sandbox needs `unshare(CLONE_NEWUSER)`, which
a sandboxed subprocess denies with a seccomp `SIGABRT`; that failure mode is expected
there and is not evidence of anything about this spike.

Swap `--api serial` for `--api usb` or `--api hid` to test those APIs too, if you have
a device for them. `--topology both` runs both topologies back-to-back with the same
process (default if you omit `--topology`) — useful once you're comfortable with the
flow and don't need to stop between them.

## Step by step

1. **Before you start:** plug your device in. Run `lsusb` (or Device Manager on
   Windows / `system_profiler SPUSBDataType` on macOS) and note its **exact name,
   vendor ID, and product ID** — you will need to confirm the browser's picker shows
   the *same* device, and you will need to write this down in your report (see
   "Disbelieve any S-E PASS that does not name the device" above).
2. Run the `--topology toplevel` command above. A **real, visible Chromium window**
   will open. Leave it alone while the JupyterLite console boots — this can take
   30–90+ seconds (Pyodide is loading real Python packages over the network; this is
   normal, matches repl_smoke.py's own observed timings, and is not a hang). The
   terminal will print progress lines like:
   ```
   [toplevel/serial phase1] waiting for human (598s left) — pending=None gesture_events=0 clicks=0
   ```
3. Once the kernel finishes booting and requests the device, a **yellow button** will
   appear in the top-left corner of the browser window, reading something like:
   `Click to grant SERIAL device access (id=...)`. The terminal's progress line will
   also flip to `pending={'id': ..., 'api': 'serial', ...}`.
4. **Click the yellow button.** This is the actual gesture under test — click it the
   same way you'd click any real button, don't script it, don't use keyboard
   auto-repeat tricks.
5. Your OS/browser's native device picker dialog will appear. **Select your device**
   and confirm.
   - If you see a `NotAllowedError` or the picker closes with nothing selected, the
     button will change to `<ErrorName>: click to retry ...` and stay visible — click
     it again. The script records every attempt, not just the last one, so retries are
     expected and fine to do; note in your report if you needed more than one attempt.
6. After a successful grant, the script automatically (no further clicking needed):
   - has the kernel call the **real, unmodified** `WebSerial`/`WebUSB`/`WebHID` shim's
     `setup()` and attempt a minimal open (+ a benign write/read for serial),
   - reloads the page and re-checks whether the grant is still visible to
     `getPorts()`/`getDevices()` with **no new gesture**, to test persistence.
7. The script exits and writes `--out <path>.json`, plus prints the same JSON to
   stdout. **Do not edit this file by hand.** Send it back as-is (see below).
8. Repeat steps 2–7 for `--topology iframe` with the **same device**, ideally in the
   same terminal session so the comparison is apples-to-apples.

## What a PASS looks like

For **both** topologies, in the returned JSON:
- `phase1.interaction_result.ok == true` and
  `phase1.interaction_result.value.success == true`
- `phase1_gesture_log` contains a `grant_success` entry naming the actual device
  (`describeDevice()`'s output — e.g. `"serial vid=1027 pid=24577"` for a common FTDI
  chip). **This is the "names the device" bar** — if this field is empty or missing,
  the run does not count as a PASS regardless of what else looks good.
- `phase1.device_open_attempt.opened == true` (the kernel could actually open the
  granted device from inside Pyodide, not just receive a grant that goes nowhere).
- `phase2.persisted_grant_check.ok == true` with `count >= 1` (the grant survived a
  reload — this matters because production will reload/redeploy far more often than a
  spike run does).
- `phase1_click_count == 1` (no retries needed) is the *strong* form of PASS;
  `phase1_click_count > 1` with an eventual `grant_success` is still a PASS but should
  be noted as "gesture had to be repeated" in your report — that's exactly one of the
  data points G2 criterion 5 asks for.

## What a FAIL (or "materially worse than the iframe") looks like

- `phase1.interaction_result.ok == false`, or `value.success == false` after the
  button was actually clicked (not just a timeout from nobody clicking it).
- Any `grant_error` entry in `phase1_gesture_log` whose `error_name` is
  `NotAllowedError`/`SecurityError` that **persists across retries** — i.e. every
  click fails the same way, not just the first one.
- `phase1.device_open_attempt.opened == false` after a successful grant (`opened` false
  with `open_error` populated) — the grant worked but the kernel still couldn't use it.
- `phase2.persisted_grant_check.ok == false` or `count == 0` — the grant did not
  survive a reload.
- **Comparative FAIL**: `toplevel` results look fine but `iframe` results show any of
  the above that `toplevel` didn't (e.g. `NotAllowedError` only inside the iframe, or
  the button never appearing there at all because the Permissions-Policy `allow`
  attribute on `<iframe allow="usb; serial; hid">` didn't actually propagate the
  permission the way the code comment assumes). This specific asymmetry is exactly
  what G2 criterion 5 means by "materially worse than the iframe" — record it even if
  `toplevel` alone looks like a clean PASS, because the current shipped app's
  `interaction-dialog.component.ts` lives on the iframe side of that comparison today,
  and B-prime's whole premise is that dropping the iframe doesn't cost you this.

## Copy back to the requester

1. Both `results_toplevel_serial.json` and `results_iframe_serial.json` (or whichever
   `--api` you ran), unedited.
2. The exact device make/model and VID:PID from `lsusb` (or platform equivalent) —
   from step 1, not inferred from the JSON.
3. Anything you saw that the JSON doesn't capture: how many times you had to click,
   whether the browser's device picker looked different between runs, whether the
   window ever appeared frozen/unresponsive, any OS-level permission prompts (some
   Linux distros gate serial/USB device nodes on udev rules separately from the
   browser's own permission — if the picker never lists your device at all, that's
   worth reporting as its own finding, distinct from a browser-side `NotAllowedError`).
4. If you stopped partway (ran out of time, device didn't work, etc.) — say so plainly
   with which step you reached. A truthful partial run is worth more than a silent gap.

## Honest limitation of the self-check the script author (Claude) ran

Before handing this to you, the script was smoke-tested under Xvfb (`xvfb-run`, a
virtual/off-screen X display — not a real desktop, and not the same environment you'll
run in) with `--verify-pause-only`, a mode that launches the real script exactly as you
will, and polls for the state where `window.__praxisPendingRequest` is set (i.e. the
kernel has posted the real `USER_INTERACTION`/`device_connect` message and the yellow
button would be visible to a human at that point) — **without ever calling
`requestDevice()`/`requestPort()`, without a human, and without a device**, because it
structurally cannot: there is no display a click could land on inside Xvfb in a way
that constitutes a real gesture, and there was no device attached to that machine.

Four self-check runs were made before the harness was correct, and **all four were
misleading**. They are recorded here rather than deleted, because the way they misled
is the most useful thing in this document.

Across all four:
- The static server correctly serves both the real, unmodified repo assets and the
  spike's own overlay host page on the same origin (verified directly with `urllib`,
  no browser needed: `/_spike/host_iframe.html` → 200 with the expected content,
  `/assets/jupyterlite/repl/index.html` → 200 with the real REPLite page).
- Chromium launches, navigates to the real REPL console, and the real
  JupyterLite/Pyodide boot sequence proceeds with **zero page errors and zero console
  errors** (`pageerrors: []` every run) through micropip, Pygments/IPython/jedi/parso
  loading, and JupyterLite's own service-worker registration.
- **None of the four reached `__praxisPendingRequest`** within budgets up to 360s:

  ```json
  { "pageerrors": [], "pause_only": true, "reached_pause_point": false, "topology": "toplevel" }
  ```

**The explanation given here previously — that CDN-loaded Pyodide plus Xvfb latency
was making the boot merely slow — was wrong, and was wrong twice over.** It was
labelled "plausible, not confirmed" at the time, and it should have stayed a suspicion
rather than an explanation. Pyodide was later vendored locally (0 non-local requests
per boot, enforced by `build_repl.py`'s `assert_pyodide_is_local`), and the spike still
failed identically. Latency was never the cause.

**The real cause (found 2026-08-20, fixed):** the probe builders interpolate an
already-dedented `prelude` into a `textwrap.dedent()`-ed f-string. `dedent()` strips the
*common* leading whitespace across all lines — and the injected prelude sits at column
0, so the common prefix was `""` and the template's own 8-space indent was never
removed. Every trailing line (`API = ...`, `async def _main()`, and crucially
`await _main()`) was therefore absorbed into the `except Exception as e:` block of
`_bootstrap()` that immediately precedes them.

The payload still **compiled**. `_main` was simply never defined at module level and
`await _main()` never ran — dead code inside an exception handler that never fired. The
cell defined `_bootstrap`, printed nothing, and reported idle. No syntax error, no
traceback, no `pageerror`, no sentinel, no posted message: a perfectly silent no-op that
looked exactly like a slow boot. A syntax check would not have caught it; only a
structural one does, and `_assert_toplevel_entrypoint()` in `gesture_spike.py` now runs
that check on every generated payload and has been observed both passing and failing.

With that fixed, `--verify-pause-only` reaches the pause point in **~8 seconds**. If
your real run sits past ~60s with `pending=None`, that is now a genuine anomaly worth
reporting, not expected warm-up.

**What this does and does not establish:** the self-check is real evidence that the
harness's serving, browser-launch, and real-kernel-boot mechanics are correct and
error-free, and — since the dedent fix — that the kernel really does reach the point of
asking for a device. It is **not**, and structurally cannot be, evidence about the
actual question S-E exists to answer. The gesture chain from a real click through a real OS
device picker to a real granted, openable device has never been exercised by anyone or
anything at the time this protocol was handed to you. **G2 criterion 5 is UNMET** until
you complete the steps above.
