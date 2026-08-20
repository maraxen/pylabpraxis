/**
 * Praxis visualizer augmentations -- praxis_viz receiver (P6.6, Phase 6 slice 3).
 *
 * The kernel half (`praxis/viz/transport.py` + `browser.py`) posts PyLabRobot
 * command envelopes onto the `praxis_viz` BroadcastChannel. This module is the
 * browser half: it listens on that channel and hands each command to the
 * vendored renderer's own entry point, `window.receiveFromPython(event, data)`
 * (`../visualizer/vis.js:255`).
 *
 * The vendored renderer is NEVER forked -- GATE G6 asserts `cmp` equality
 * between `external/pylabrobot/.../lib.js` and the vendored copy. Everything
 * praxis adds lives in this file.
 *
 * DIRECTORY NAME IS LOAD-BEARING: `../visualizer/index.html:354` carries
 *     <script type="module" src="../visualizer-augmentations/index.js"></script>
 * as its last body element, injected by `vendor_visualizer.py:141`
 * (`_AUGMENTATION_TAG`), so it is regenerated on every vendor run and cannot be
 * removed. The relative path resolves only while `visualizer/` and
 * `visualizer-augmentations/` remain siblings. See ADR
 * `.praxia/docs/decisions/260817_repl-layout-and-delivery-mechanism.md` 2.1, 4.2.
 *
 * WHY `data` IS PASSED BACK AS A STRING, not as a parsed object
 * -------------------------------------------------------------
 * PLR's `_assemble_command` runs `_sanitize_floats`, which rewrites non-finite
 * floats to the *strings* "Infinity" / "-Infinity" / "NaN" -- because a bare
 * `Infinity` token is invalid JSON and browser `JSON.parse` rejects the whole
 * payload (spike S-D measured a 65,516-byte initial deck paint dying on
 * `SyntaxError: Unexpected token 'I'`; `trash`/`trash_core96` carry
 * `max_volume = float('inf')`).
 *
 * `receiveFromPython` undoes that -- but ONLY on the string branch, via its own
 * reviver at vis.js:256-261. Handing it an already-parsed object skips the
 * reviver, and `max_volume` arrives as the literal string "Infinity" instead of
 * the number. So this module parses only far enough to read the envelope, then
 * re-stringifies `data` and lets the vendored reviver do the conversion. That
 * keeps ONE definition of the Infinity round-trip -- the vendored one -- instead
 * of a copy here that could silently drift from it.
 */

const CHANNEL_NAME = "praxis_viz";
const MAX_LOG = 200;

const state = {
  loaded: true,
  noop: false,
  phase: "6",
  channel: CHANNEL_NAME,
  received: 0,
  dispatched: 0,
  errors: [],
  log: [],
  queued: 0,
};

function note(entry) {
  state.log.push(entry);
  if (state.log.length > MAX_LOG) state.log.shift();
}

function recordError(where, err) {
  const message = `${where}: ${err && err.message ? err.message : String(err)}`;
  state.errors.push(message);
  // Surface it. A visualizer that silently renders nothing is the single
  // hardest failure to diagnose in this stack, and console is what the
  // Playwright harness harvests.
  console.error("[praxis-viz]", message);
}

/**
 * Deliver one envelope to the renderer.
 * @param {string} raw the serialized command from PLR's _assemble_command
 */
async function dispatch(raw) {
  let envelope;
  try {
    envelope = JSON.parse(raw);
  } catch (err) {
    recordError("envelope parse", err);
    return;
  }
  if (!envelope || typeof envelope.event !== "string") {
    recordError("envelope shape", new Error(`no 'event' field in ${raw.slice(0, 120)}`));
    return;
  }
  if (typeof window.receiveFromPython !== "function") {
    recordError("renderer", new Error("window.receiveFromPython is not defined"));
    return;
  }
  try {
    // See the header note: hand back a STRING so vis.js's own Infinity reviver runs.
    await window.receiveFromPython(envelope.event, JSON.stringify(envelope.data ?? {}));
    state.dispatched += 1;
    note({ event: envelope.event, id: envelope.id ?? null, ok: true });
  } catch (err) {
    recordError(`receiveFromPython(${envelope.event})`, err);
    note({ event: envelope.event, id: envelope.id ?? null, ok: false });
  }
}

// The augmentation tag is the last body element, so vis.js has already run and
// receiveFromPython exists. Messages are still queued until DOM-ready when the
// renderer is not yet installed, rather than dropped: a dropped set_root_resource
// leaves every later set_state referring to resources the renderer never heard
// of, which presents as a blank deck with no error at all.
const pending = [];
let ready = typeof window.receiveFromPython === "function";

async function drain() {
  while (pending.length) {
    await dispatch(pending.shift());
  }
  state.queued = 0;
}

let channel = null;
try {
  channel = new BroadcastChannel(CHANNEL_NAME);
  channel.onmessage = (ev) => {
    state.received += 1;
    const raw = typeof ev.data === "string" ? ev.data : JSON.stringify(ev.data);
    if (!ready) {
      pending.push(raw);
      state.queued = pending.length;
      return;
    }
    void dispatch(raw);
  };
} catch (err) {
  recordError("BroadcastChannel", err);
}

if (!ready) {
  window.addEventListener("DOMContentLoaded", () => {
    ready = typeof window.receiveFromPython === "function";
    if (ready) void drain();
    else recordError("renderer", new Error("receiveFromPython still absent at DOMContentLoaded"));
  });
}

// Note: NOT frozen. `state` counters mutate as messages arrive, and the harness
// and a human at the console both read them to tell "nothing was sent" from
// "sent but not rendered" -- two failures that look identical on screen.
globalThis.__praxisVisualizerAugmentations = state;
