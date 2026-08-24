---
title: 'REPL autocomplete: as-you-type completion'
description: Scope and outcome for as-you-type completion in the JupyterLite PLR REPL; the planned jedi preload proved unnecessary
status: complete
task_id: 260824_repl_autocomplete_scope
date: '260824'
sprint: ''
backlog_ids: ''
---
# REPL autocomplete: jedi preload and as-you-type completion


## What is actually true today (measured from the built bundle, 260824)

Tab completion already works. The naive framing — "add autocomplete" — is wrong;
the completer is wired end to end and the question is only about *quality* and
*trigger*.

| Layer | State | Evidence |
|---|---|---|
| Frontend completer | present, enabled | `@jupyterlab/completer-extension` bundled (51 refs in `notebooks/build/index.js`, `consoles/build/index.js`); `disabledExtensions` lists only the announcements plugin |
| Kernel `complete_request` | implemented | `pyodide_kernel-0.8.2` `kernel.py:83` → `_experimental_do_complete` via IPython `Completer` |
| Jedi | ~~vendored but NOT loaded~~ **WRONG — see Execution outcome** | The static evidence (ipython's lock `depends` omits jedi; `loadPyodideOptions` null) was real but the conclusion drawn from it was not. Measured in a live kernel: jedi IS loaded and in use. |
| As-you-type | off | `autoCompletion` default `false` in `build/schemas/@jupyterlab/completer-extension/manager.json` |

So users get IPython's `dir()`-based fallback on Tab. `lh.<TAB>` after `lh`
exists completes fine. What is missing: completion on un-evaluated expressions,
type inference, and signatures.

## The two changes are independent

**A — as-you-type** (`autoCompletion: true`). Frontend-only. No kernel change,
no boot cost.

**B — jedi quality** (`loadPyodideOptions: {packages: ["jedi"]}`). Kernel-side
preload. Costs boot bytes.

~~Both go in the same block: `litePluginSettings`.~~ **WRONG — see Execution
outcome.** They use two DIFFERENT channels, and each silently ignores a key meant
for the other.

## Mechanism, confirmed not assumed

`loadPyodideOptions` is a first-class documented setting in the kernel's own
schema (`.../static/schema/kernel.v0.schema.json`), typed `object` with a
`packages: string[]` sub-property, and the extension JS reads it
(`options.loadPyodideOptions || {...}`). Lock keys are exactly `jedi` and
`parso`; parso arrives via `depends`, so `packages: ["jedi"]` suffices.

**The ordering constraint is hard.** `IPython/core/completer.py:254` does
`import jedi` at *module import time* inside a try/except, setting
`JEDI_INSTALLED` (line 258/260); `use_jedi` is `Bool(default_value=JEDI_INSTALLED)`
(line 998). `loadPyodideOptions.packages` loads during `loadPyodide()`, before the
kernel imports IPython — which is why it works.

**There is no clean runtime toggle.** Setting `use_jedi = True` later selects
`self._jedi_matcher` (line 2149ff), which resolves the module-level `jedi` name —
unbound if the original import failed. Preload is the mechanism, not a
convenience.

**Pruning is not a hazard.** `prune_pyodide_bundle` (`build_repl.py:598`) removes
only `-tests` lock entries and stale duplicate wheels. jedi is lock-referenced, so
it survives; `jedi-tests.tar` is correctly pruned.

## Costs

- jedi 1,563,101 B + parso 106,894 B = **~1.67 MB added to the cold-boot path**.
- Against the documented baseline (`build_repl.py:598` docstring, measured
  260820: a real boot fetches 20 files / 17.9 MB), that is ~19.6 MB / 22 files —
  **roughly +9% cold boot**. Computed, not measured; Phase 0 measures it.
- Bundle size is unchanged — the wheels are already shipped.

## Risks

1. **Jedi cold-start vs `providerTimeout` (default 1000 ms).** THE make-or-break
   unknown. Single-threaded WASM; jedi builds a parso grammar cache on first
   call. If first completion exceeds the timeout the completer shows *nothing* —
   strictly worse than today's fast `dir()` fallback. Measure before committing.
2. **Busy-kernel stalling.** The Jupyter shell channel is serial: a running cell
   blocks `complete_request`. In a lab REPL, cells run for minutes. With
   as-you-type on, every keystroke queues against a possibly-busy kernel.
   Degradation is graceful (timeout → no popup, no error), but it is real.
3. **The in-kernel probe payload builder is the known-fragile path** — it carried
   the silent dedent defect. It is also the natural home for the Phase-1 gate.

## Priority inversion worth noting

The instinct is "jedi first, it's the real fix." That is backwards. The highest-
value affordance — typing `lh.` and discovering `aspirate` / `dispense` /
`move_plate` — **already works today**. Jedi adds signatures and un-evaluated-
expression completion: a quality upgrade.

As-you-type is the bigger UX delta, because Tab-only means a user must already
know to press Tab. For a REPL aimed at lab people rather than Python developers,
that is the difference between discoverable and invisible.

**Recommendation: A before B.** A is cheap, frontend-only, zero boot cost, and
delivers the larger share of the benefit.

## Verification (three tiers)

- **T1 — build assertion** (cheap, catches config regression). Assert the built
  `jupyter-lite.json` carries the setting, same discipline as the `HOST_ROOT`
  assertion. Distinguishes "configured" from nothing; does NOT prove it works.
- **T2 — in-kernel probe** (real, cheap; answers Risk 1). Assert
  `IPython.core.completer.JEDI_INSTALLED is True`, that
  `Completer.completions("lh.", 3)` returns matches, and record first-call
  latency. Reuses the existing probe payload path.
- **T3 — browser gate** (real end-to-end; the ONLY tier that tests the frontend
  setting). Playwright types `lh.` into a cell and asserts `.jp-Completer`
  appears. Costs CI time.

T1+T2 always. T3 required for change A, since T1/T2 cannot see the frontend.

## Phases

- **Phase 0 — measure (~30 min, no commitment).** Local build with jedi
  preloaded; run T2; read first-completion latency. **Decision gate:** if it
  exceeds `providerTimeout`, either stop (keep the fast `dir()` fallback) or
  raise `providerTimeout` deliberately and re-measure.
- **Phase 1 — change A (~2 h).** `autoCompletion: true` + T1 + T3.
- **Phase 2 — change B (~2 h), gated on Phase 0.** jedi preload + T1 + T2.

## Cut from scope

- `showDocumentationPanel: true` — extra `inspect_request` round-trips per
  completion for marginal gain in a REPL where `?` already works.
- Raising `providerTimeout` pre-emptively. Only if Phase 0 shows it is needed;
  a longer timeout means a longer stall on a busy kernel.

## Open question

Whether as-you-type should be suppressed while a cell is running. JupyterLab has
no such setting out of the box; the timeout handles it, but the behaviour should
be looked at once with a genuinely long-running PLR cell before calling Phase 1
done.

---

# Execution outcome (2026-08-24)

Executed. **One config line shipped; the other planned change turned out to be
unnecessary.** Three claims in the scope above were wrong and are corrected here.

## Correction 1 — jedi was ALREADY loaded

The scope said jedi was vendored but not loaded, and built Phase 2 around
preloading it. Measured in a live kernel instead: `jedi_installed=True`,
`use_jedi=True`, `jedi_version=0.19.2`, and the browser's own request log shows it
FETCHING `static/pyodide/jedi-0.19.2-py2.py3-none-any.whl` and
`parso-0.8.6-py2.py3-none-any.whl` during boot.

The inference failed because `pyodide-lock.json`'s `depends` is not the resolution
path. micropip reads the `.whl.metadata` sidecars, and IPython's real
`Requires-Dist` includes jedi. `prune_pyodide_bundle`'s own docstring already said
those sidecars are load-bearing for exactly this reason -- the evidence that would
have prevented the error was in code already read.

**Phase 2 is void.** No preload, no `loadPyodideOptions`, no +1.67 MB boot cost --
that cost was already being paid and is already inside the 17.9 MB baseline.

## Correction 2 — two settings channels, not one

`litePluginSettings` configures LITE plugins (the Pyodide kernel).
`settingsOverrides` configures JupyterLab plugins and is what the completer needs
(`jupyterlite_core/constants.py:60`; merged and schema-validated in
`addons/settings.py:54-125`). A key filed in the wrong one is silently ignored --
the site boots, Tab still completes, and only the typed-ahead behaviour is missing.
`assert_completion_autocompletion` exists to make that specific mistake loud.

Also measured, so nobody repeats them: writing `settingsOverrides` as a JSON
*string* breaks the app outright (the REPL never boots), and a hand-placed
`overrides.json` is unnecessary -- page config alone is sufficient.

## Correction 3 — the first version of the T3 gate was wrong

It typed `sys.` and asserted the completer appeared. It did not, and that read as
"the setting does not work". It was the gate that was broken. Continuous hinting
fires on IDENTIFIER characters: typing `sys` opens the popup (3 items), the
following `.` DISMISSES it, and `pa` reopens it (6 items). The gate now types
`sys.pa`. Had this not been chased down, a working feature would have been
reverted as broken.

## What shipped

One line of config: `settingsOverrides["@jupyterlab/completer-extension:manager"]
.autoCompletion = true` in `web-repl/jupyter-lite.json`.

Plus three gates that did not exist before:

| Tier | Where | Sees |
|---|---|---|
| T1 | `build_repl.py::assert_completion_autocompletion` | the setting reached the RUNTIME config |
| T2 | `repl_smoke.py --completion-check [--require-jedi]` | jedi resident, completer answers, cold/warm latency |
| T3 | `repl_smoke.py --typeahead-check` | the popup opens from TYPING ALONE, no Tab |

None subsumes another: T1 passes on a build whose kernel cannot complete, T2 passes
on a build where the frontend setting never applied, T3 is the only one that sees
`autoCompletion` at all. T2 and T3 are wired into `repl.yml`.

`--completion-check` drives `run_probe` through a new `code_override` seam rather
than editing `build_probe_code`, which is shared by two CI gates and is the builder
that carried the silent dedent defect.

## Measurements

- Cold completion on `LiquidHandler.`: **415-543 ms** across runs (88 matches).
  Warm: 22-40 ms. Light (`sys.`): 33-43 ms. Ceiling is the completer's 1000 ms
  `providerTimeout`, so this fits with roughly 2x headroom on the dev box.
- `--max-completion-ms` is deliberately NOT set in CI yet: a GitHub runner is
  slower than this box by an unmeasured factor, so a bound picked from local
  numbers would fail as flake rather than as signal. The step logs the number.

## Negative arms (each check seen failing)

- `assert_completion_autocompletion` raises on the pre-change `dist/`.
- `--typeahead-check` FAILS when `settingsOverrides` is stripped from the built
  config and PASSES with it -- so the gate is sensitive to precisely the setting
  it claims to test, not to the completer merely existing.

## Regression

`--probe`, `--probe --offline`, and `--notebook-check` all still pass after the
`run_probe` signature change (`praxis_ready` true, PLR 0.2.2, no page errors).

## Still open

- The busy-kernel question is UNTESTED. The shell channel is serial, so a
  minutes-long PLR cell blocks completion; with as-you-type on, keystrokes queue
  against it. Degradation should be graceful (timeout, no popup, no error) but
  that was not exercised -- it wants one look with a genuinely long-running cell.
- Cold latency on the Raspberry Pi is unknown, and the Pi is the U1 spike target.
  543 ms on this box could exceed the 1000 ms `providerTimeout` there, which would
  make as-you-type silently do nothing on that hardware. Worth one
  `--typeahead-check` run on the Pi while it is out for the spike.
