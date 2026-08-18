---
title: REPL layout and browser-Python delivery mechanism
description: ADR resolving the path collision between the three refocus specs by deciding what ships as a wheel and what ships as loose fetched files; includes the single-class-object invariant, the three-detector drift design, and the per-spec re-scope tables that Phase 3's gate checks.
category: decisions
task_id: 260817_praxis_repl_refocus
status: accepted
date: 260817
---

# ADR — REPL layout and browser-Python delivery mechanism

**Status:** **ACCEPTED** — revision 2 (accepted 2026-08-17, after three Opus reviews, the §4 re-scope, and the §5.3 decision)
**Task:** `260817_praxis_repl_refocus`
**Supersedes:** the conflicting layout sections of the three converged specs
**Blocks:** Phase 3 onward (narrowed in r2 — see §1.2)

> **Revision 2 (2026-08-17), ACCEPTED.** Three independent Opus reviews (architecture, adversarial challenger, strategic oracle) returned DO NOT LOCK / NOT READY / LOCK-WITH-AMENDMENTS. Two of r1's three deciding rationale findings were false against the artifacts. Every claim below that changed was re-verified against the code, not against the reviews. §8 records what changed and why. **The decision itself survives; most of r1's argument for it did not.**

---

## 1. Context

Three adversarially-reviewed specs landed on 2026-08-17:

- `.praxia/docs/specs/260817_spec-web-repl-extraction.md` (standalone site)
- `.praxia/docs/specs/260817_spec-wheel-build-plr-upgrade.md` (wheel pipeline)
- `.praxia/docs/specs/260817_spec-visualizer-transport-shim.md` (visualizer)

They collide on five paths and, beneath that, on one architectural question.

| path | Standalone spec | Wheel spec | Visualizer spec |
|---|---|---|---|
| `assets/shims/*.py` | `git mv` → `web-repl/overlay/assets/shims/` | `git mv` → `praxis-browser/praxis_browser/shims/` | assumes in place |
| `assets/python/web_bridge.py` | `git mv` → `web-repl/overlay/assets/python/` | `git mv` → `praxis-browser/praxis_browser/` | EDITS in place (T3.2) |
| `assets/python/praxis/` | **MOVED** (`__init__.py`, `interactive.py`); `backend/`, `protocol/`, `sqlmodel/` explicitly NOT moved | left in place | CREATES `praxis/viz/` inside it |
| `assets/jupyterlite/praxis_bootstrap.py` | `git mv` → `web-repl/bootstrap/` | rewritten in place (T10) | EDITS in place (T2.3) |
| `assets/wheels/` | deleted; → `web-repl/overlay/assets/wheels/` | `manifest.json` written here (T9) | n/a |
| **shim delivery** | **loose `.py` files, fetched** | **a `praxis_browser` wheel** | loose files |

The last row is the real decision; every other row falls out of it. Standalone T03 and Wheel T4 are the *same* `git mv` to *different* destinations.

> **r2 correction.** r1's table said the standalone spec DELETES `assets/python/praxis/`. It does not — spec `:68-69` lists `__init__.py` and `interactive.py` as `MOVED`, and `:211` says `backend/`/`protocol/`/`sqlmodel/` are *"NOT moved… leave them where they are for now (T17 relocates them)."* r1 read the wrong half and would have instructed an implementer to delete a live user-facing module. See §4.1.

**Why this must be decided before Phase 3 file moves:** every `verification` field in all three specs is path-keyed. Run any two specs in either order and roughly a third of the verification commands become **unrunnable rather than failing** — a grep against a path that no longer exists returns 0 and reads as green.

That failure mode is not hypothetical, and r1 reproduced it inside its own fix. Verified empirically:

```
$ git check-ignore -v praxis/web-client/src/assets/visualizer/lib.js
$ echo $?
1
```

Visualizer spec R7 (`:174`) asserts **exit 1** as PASS, and the path does not exist — so that *clause* is satisfied by absence and can never fail.

**Correction to r2's first draft, which overstated this.** The adversarial review reported four visualizer verifications that "pass while verifying nothing." Tested directly, that is **wrong at the requirement level for all four** — each requirement is written as a conjunction, and in every case a sibling clause does fail on a missing tree:

| shape | exit on a missing target | consequence |
|---|---|---|
| `git check-ignore -v <missing>` | **1** — the asserted value | vacuous clause (R7) |
| `git diff --exit-code -- <missing pathspec>` | **0** — the asserted value | vacuous clause (R18) |
| `git ls-files <missing> \| wc -l` | **0**, against R7's `>= 11` | **R7 fails loudly** |
| `grep -q <pat> <missing file>` | **2**, so "succeeds" is false | **R18 fails loudly** |
| `grep -rnE <pat> <missing dir>/` | **2**, and R19/R21 assert exit **1** | **R19/R21 fail loudly** |

So only individual clauses are vacuous, never a whole requirement. The residual risk is narrower but real: R19/R21's prose says "returns no matches," and an implementer who checks *empty stdout* instead of the parenthetical exit code would get a silent pass, because a missing directory yields empty stdout. §4.2 hardens the vacuous clauses and makes the exit-code assertion explicit rather than parenthetical.

### 1.1 Unlisted consumers

Four consumers appear in no spec's file list:

| consumer | why it matters |
|---|---|
| `praxis/web-client/e2e/specs/jupyterlite-bootstrap.spec.ts` | breaks under all three layouts; see §4.4 — disposition is **delete** |
| `praxis/web-client/src/app/features/playground/services/playground-jupyterlite.service.ts:287` | `xhr.open('GET', HOST_ROOT + 'assets/jupyterlite/praxis_bootstrap.py', False)` — the **sole live caller** of the file §2.1 marks single-owner |
| `.github/workflows/deploy.yml:42-45` | hardcodes `praxis/web-client/src/assets/jupyterlite/praxis_bootstrap.py` in a `git checkout` restore-over-generated-tree step |
| `tests/shim_verification_test.py:8` | `sys.path.append("praxis/web-client/src/assets/shims")`; calls `patch_pylabrobot_io()`. Invisible to the standalone spec's sweep grep at `:147`, which greps `web_serial_shim\|web_usb_shim` and so misses a file referencing `pyodide_io_patch` |

### 1.2 What this ADR blocks — narrowed in r2

r1 claimed "every later phase." That is false and it held up cheap work:

- **Independent of this ADR:** P1.1, P1.3, P1.5, P1.6 (moves/deletes inside `praxis/web-client/src/app/` plus repo hygiene) and **P1.4** — the one-line `web_serial_shim.py:24` fix removing `window` from the `from js import …` list, which is why WebSerial has never worked in the Web Worker kernel. P0.4's baseline capture is *against the current tree* and needs no layout decision either.
- **Genuinely blocked:** Phase 3 onward, plus P1.2's Python-asset half — and that half is avoidable, since those subtrees were never fetched in a healthy run (spike `standalone` [15]), so leaving them and sweeping at P3 costs nothing.

**Run P1 and P0.4 concurrently with finalising this ADR.**

---

## 2. Decision

**Split delivery along the line where spike evidence actually exists.**

- **PLR and pylibftdi ship as wheels**, behind `manifest.json` indirection with a fail-closed boot.
- **praxis's own browser Python ships as loose fetched files** — the four device shims, `web_bridge.py`, `praxis/{__init__,interactive}.py`, and the visualizer transport.

There is no `praxis-browser/` top-level Python package. This is the wheel spec's own named runner-up design, which that spec calls "strictly smaller."

**Two invariants are mandated as part of this decision** (r2 additions — the decision is not sound without them):

- **§2.2 the single-class-object invariant** — because the identity guarantee r1 wrongly attributed to `git mv` subtraction has to come from somewhere.
- **§2.3 the three-detector drift design** — because r1's replacement for the dropped `BUILD_ID` check broke a *different*, pre-existing check.

### 2.1 Canonical tree

```
web-repl/                                     # site build root AND praxis's browser Python
  overlay/assets/shims/                       # loose, fetched — edit→reload preserved
    web_serial_shim.py  web_usb_shim.py
    web_hid_shim.py     web_ftdi_shim.py
    __init__.py
    # pyodide_io_patch.py NOT moved — deleted at P3.5 (§4.3)
    # test_hid.py         NOT moved — deleted (§4.1)
  overlay/assets/python/web_bridge.py
  overlay/assets/python/praxis/__init__.py     # 0-byte REGULAR package — see §2.4
  overlay/assets/python/praxis/interactive.py  # user-facing pause()/confirm()/input()
  overlay/assets/python/praxis/viz/            # visualizer transport (was praxis/viz/)
  overlay/assets/python/experimental/          # extracted _MACHINE_CLASS_MAP — see §4.3
  overlay/assets/visualizer/                   # COMMITTED, vendored renderer
  overlay/assets/visualizer-augmentations/     # hand-authored, NEVER regenerated; NAME PRESERVED
  overlay/assets/wheels/                       # gitignored: PLR + pylibftdi + manifest.json
  bootstrap/praxis_bootstrap.py                # ordered fail-closed driver; SINGLE OWNER
  bootstrap/stages.py                          # declarative stage table + error taxonomy
  bootstrap/transport.py                       # _sync_fetch → (ok, status, text); no `import js`
  shell/praxis-shell.js                        # carries the injected praxis_git_sha (§2.3)
  jupyter-lite.json                            # schema-v0 — ONLY home of contentsStorageName/settingsStorageName/workspacesStorageName (G2 amendment, 260817 — see §5.5)
  jupyter_lite_config.json                     # traitlets — ONLY home of pyodide_url
                                                # [CORRECTED 260818] pin pyodide_url EXPLICITLY here — the
                                                # vendored jupyterlite-pyodide-kernel bundle's own default
                                                # (currently v314.0.1/CPython 3.14.2, not the v0.29.0/3.13.2
                                                # this task's earlier docs recorded) otherwise silently
                                                # governs the in-browser Python runtime, with no diff in this
                                                # repo on a bundle upgrade. See 260817_g2-spike-battery-verdict.md §3, §8f.
  files/welcome.ipynb
  augmentations/                               # REMOVED in r2 — merged into overlay/assets/
  vendor/                                      # gitignored: pyodide-<v>.tar.bz2
  scripts/{build_wheels,build_repl,inject_shell,fetch_pyodide,vendor_visualizer}.py
  scripts/pylibftdi_stub/                      # checked-in source for the stub wheel
  tests/                                       # CPython contract + helper tests
  tests/e2e/*.spec.ts
  playwright.config.ts
  pyproject.toml                               # pytest section only (--no-cov) — see §5.4
  README.md
  .gitignore                                   # covers dist/, vendor/, overlay/assets/wheels/
  dist/                                        # gitignored
```

`web-repl/` has **no Python import path in either direction** with `praxis/`. One build-time edge is sanctioned and is the only one: `praxis/web-client → web-repl/dist` as a **pinned copied artifact** (standalone R at `:188`). See §5.2 — r1's unqualified "no import path into `praxis/`" was true but described the wrong direction.

> **r2 correction — the two config files are not interchangeable.** Standalone spec `:86`: *"Conflating them is the predictable failure and is why the current `jupyterlite-config.json` … never bundled a wheel."* r1's tree omitted both. `contentsStorageName` belongs only in `jupyter-lite.json`; `pyodide_url` only in `jupyter_lite_config.json`.

> **r2 correction — `visualizer/` and `visualizer-augmentations/` moved under `overlay/assets/`.** r1 placed them at `web-repl/` root as `vendor-visualizer/` and `augmentations/`. Only `overlay/` reaches `dist/` (`build_repl.py --out web-repl/dist`), and no script staged them — **so as r1 decided it, the visualizer never reached the page.** The rename also broke a verified anchor: the generated `visualizer/index.html` carries a relative `<script src>` to `visualizer-augmentations/index.js` (spec `:207`), which only resolves while the two are siblings. Both names are preserved and both live under `overlay/assets/`, making §4.2 a pure prefix substitution.

### 2.2 The single-class-object invariant (R-ID) — mandatory

**The current boot produces two distinct class objects per shim name, on the live JupyterLite path.** Verified:

1. `praxis_bootstrap.py:227-236` — `ns = {}; exec(fetched[filename], ns); setattr(builtins, 'WebSerial', ns['WebSerial'])` → **class A**
2. `:253` — `_patch_io_modules()` binds `pylabrobot.io.serial.Serial = builtins.WebSerial` → **A**
3. `:274` — `web_bridge.bootstrap_playground(globals())`, which at `web_bridge.py:1462-1466` does `from web_serial_shim import WebSerial` — a *module* import of the VFS file written at `:213-222` — and rebinds `builtins.WebSerial` → **class B**

After boot, `pylabrobot.io.serial.Serial is builtins.WebSerial` is **False**. This is exactly what wheel-spec R13 (`:173`) mandates fixing (*"exactly one … class object exists at runtime … asserted by IDENTITY (`is`), never by name"*) and what standalone `:96` independently flags. A fourth patcher, `pyodide_io_patch.py:28-98`, auto-invokes at import (`:262-263`).

**R-ID, required by this ADR:**

- The bootstrap fetches each shim to the VFS, then `importlib.import_module(...)` it **exactly once**, and staples `getattr(module, name)` onto builtins. **`exec` into a throwaway namespace is forbidden** — it is the mechanism that manufactures class B.
- `bootstrap_playground`'s shim re-injection (`web_bridge.py:1451-1481`) is **deleted**, not preserved. Its stdout-redirect duties (guarded by `_PRAXIS_JUPYTERLITE` at `:1405`) stay.
- A boot stage asserts, by `is`, that `pylabrobot.io.{serial.Serial, usb.USB, hid.HID, ftdi.FTDI}` are the same objects as their `builtins` counterparts. Failure is fail-closed.
- **Negative test:** re-introducing the double-`exec` must be *observed* failing that stage.

This is a bootstrap change, **independent of packaging** — a loose file imported once from the VFS is a single importable module, and module identity is what the invariant needs. Install-time guarantees are what a wheel adds, and they are not what is at issue here.

### 2.3 The three-detector drift design

r1 dropped the two-wheel shared `BUILD_ID` check and nominated `praxis_git_sha` "asserted against a constant injected into the fetched `web_bridge.py`" as its replacement. **That was wrong twice over.** Wheel spec `:101`, `:115`, `:167` are explicit: `praxis_git_sha` is compared against a **SHELL-INJECTED** value, and *"WHOLE-DEPLOYMENT staleness — every asset consistently old — is covered ONLY by the shell-injected `praxis_git_sha` comparison."* Moving the expected value into a fetched asset of the same generation as `manifest.json` makes the comparison `OLD == OLD`, which passes. r1 therefore **destroyed a pre-existing, independently-specified check** and presented the wreckage as compensation for a different lost one.

Three detectors, each with one job, none requiring a wheel:

| detector | catches | expected value lives | when checked |
|---|---|---|---|
| **D1** shell-injected `praxis_git_sha` | whole-deployment staleness (every asset consistently old) | `shell/praxis-shell.js`, injected by `inject_shell.py` into `lab/index.html` — **outside the JupyterLite asset set** | boot, via the `praxis:shell-ping`/`pong` handshake |
| **D2** `manifest.json` sha256 per entry, **wheels AND sources** | per-file integrity and partial drift | the generated `manifest.json` — **no source file is ever stamped** | boot, per fetched file |
| **D3** AST import-coverage test | semantic first-party drift (an import or machine-map literal that does not resolve) | `web-repl/tests/test_contract_covers_imports.py` | CPython, in CI |

**D1 resolves the dev-loop dilemma explicitly** rather than leaving it to an implementer: `build_repl.py --dev` writes `praxis_git_sha: "dev"` into the manifest and `inject_shell.py --dev` injects the same sentinel. The assert is skipped **only when both sides read `"dev"`**, and a negative test asserts that a genuine mismatch still fails closed — so the check is exercised in the loop developers actually use. Neither r1 branch was viable: stamping the tracked source makes the build script co-own a committed file, and stamping only `dist/` requires a rebuild, which nullifies §3(b).

**D2 is the mechanism that makes `manifest.json` genuinely "the only filename seam."** Today `praxis_bootstrap.py:184-194` hardcodes **seven** fetch URL literals (four shims, `web_bridge.py`, `praxis/__init__.py`, `praxis/interactive.py`) that no spec's `\.whl` grep covers. Driving the fetch loop from the manifest brings them under the seam, restores first-party integrity checking without mutating any source, and preserves edit→reload — regenerating a ~15-entry JSON is milliseconds, and the dev server can compute it per request.

Manifest shape:

```json
{ "praxis_git_sha": "<superproject sha, or 'dev'>",
  "wheels":  [ {"package": "...", "filename": "...", "version": "...",
                "source_sha": "...", "sha256": "...", "bytes": 0} ],
  "sources": [ {"path": "assets/shims/web_serial_shim.py", "sha256": "..."},
               {"path": "assets/python/web_bridge.py",     "sha256": "..."},
               {"path": "assets/python/praxis/interactive.py", "sha256": "..."} ] }
```

> **D2 EXCEPTION — bootstrap chicken-and-egg (recorded honestly):** D2 covers everything the bootstrap fetches **except the two files that implement fetching itself.** `praxis_bootstrap.py` fetches `{bootstrap/stages.py, bootstrap/transport.py}` by hardcoded URL over raw XHR, checking only `xhr.status != 200`, with no sha256 verification. These two files execute **before D1 can fire.** This is a genuine bootstrap problem, not sloppiness — the fetcher cannot verify itself. The audit's r2 suggested sha-pinning the two loader filenames into the shell injection alongside `praxis_git_sha` as a **candidate, not yet implemented**. Additionally, D2 verifies **source files**, not **wheel bytes** — manifest entries carry sha256, but the bootstrap does not byte-verify `.whl` downloads before install (the XHR synchronous + binary-safe workaround was judged too hacky to commit). So D2 currently validates sources, not wheel bytes.

**D3 needs no package.** Wheel spec `:316` describes the test as *"walk the AST of every .py under \<dir\>, collect Import/ImportFrom module names starting with 'pylabrobot' plus the string literals in the machine map, assert that set is a subset of the contract's module set."* It parses by path. Repointed at `web-repl/overlay/assets/{python,shims}/` it survives intact — and it is a **better** first-party detector than r1's scheme, because it catches an import that does not resolve rather than a build-id desync.

### 2.4 Namespace decisions

- **`overlay/assets/python/praxis/` keeps the name `praxis`.** `interactive.py` is the user-facing API — `praxis.pause()`, `praxis.confirm()`, `praxis.input()`, all routed through `web_bridge.request_user_interaction`, i.e. the commit-`97a75988` gesture chain the wheel spec (`:118`) requires preserved unchanged. Renaming it breaks the REPL's user contract to buy tidiness.
- **Consequence, and it is a real one:** that package **shadows the repo's real top-level `praxis`** in any interpreter that puts `overlay/assets/python` on `sys.path`. Therefore **`web-repl/tests/` must never append that directory to `sys.path`.** CPython tests of `web_bridge.py` and the shims import via a fixture that copies the subtree to `tmp_path`, or run in a subprocess with an explicit `PYTHONPATH`. This is a testing constraint, asserted by a test that fails if `praxis.__file__` resolves under `web-repl/`.
- **`praxis/__init__.py` stays a 0-byte regular package file.** It is fetched at `praxis_bootstrap.py:192` today. `viz/` goes inside it, so whether `import praxis.viz.transport` resolves depends on regular-package vs PEP 420 namespace semantics; this ADR pins **regular package**, and D2 covers the file's presence.

---

## 3. Rationale

Of r1's three deciding findings, **(a) survives, (b) survives with its quantity still unmeasured, and (c) was false and is replaced.** §3.1 was also wrong and is corrected. The decision stands on a materially narrower base than r1 claimed, and this section says so rather than papering over it.

**(a) The `praxis_browser` wheel has zero spike evidence.** The wheel spec states this itself (`:354`), calling it "the brainstorm's own strongest self-criticism." Three things are unverified: that praxis's browser subtree packages cleanly; that micropip installs two local wheels in sequence without resolver interaction; and — sharpest — that `import praxis_browser` is behaviourally equivalent to today's builtins stapling. `praxis_bootstrap.py:74-82` sprays all of `pylabrobot.resources` onto builtins, and the REPL's user-facing contract (bare `Plate`, `Deck`, `TipRack` in a cell) may depend on that more than anyone has checked (ledger U15).

**Weight this honestly:** absence of evidence for a design is not evidence against it, and no spike was ever *aimed* at packaging — the spikes went at PLR and manifest indirection, the wheel's earned side. (a) is a reason to prefer the option that needs no new unverified structure. It is not proof the wheel would fail.

**(b) It carries the wheel spec's #1 pre-mortem risk.** Today: edit `web_serial_shim.py`, reload, live. Under the wheel: edit → rebuild → past a service worker, and in production past `coi-serviceworker.js` as well. The spec names this (`:356`) "the single most likely cause of total failure" and makes re-litigation a live condition. For a subsystem whose unsolved problems are hardware-adjacent and un-unit-testable, iteration speed is not a comfort — it is the work.

**The load-bearing quantity here is unmeasured.** Wheel-spec T16 measures the rebuild loop; nobody has run it. r1 used (b) as decisive while (a) disqualified the wheel *for* being unmeasured. That asymmetry was fair to note and is recorded in §6 as a live re-litigation trigger, not buried.

**A second, stronger leg for (b) that r1 never claimed:** automated drift detection for the shims is not weak, it is **absent, and stays absent for the whole plan.** There is no Playwright workflow in `.github/workflows/` and no `e2e` script in `package.json` (only `@playwright/test` as a devDependency); Playwright cannot launch Chromium under the Bash sandbox; and the only meaningful shim gate needs a human plus a physical device. You cannot trade iteration speed against drift detection you do not have. Additionally, the one product-visible shim bug — `web_serial_shim.py:24` importing `window`, unavailable in a Web Worker, which is why WebSerial has **never** worked in the kernel — is a one-line fix that stays edit→reload under this decision and becomes edit→rebuild under the wheel.

**(c) — WITHDRAWN. r1's subtraction argument was false.**

r1 claimed: *"debt-1290's drift is three copies, and P1's retirement of Direct Control and the protocol worker takes it to one — by subtraction, before any packaging exists. The wheel would then be defending an invariant that is already true."* Every clause is wrong:

- **The count is four, not three.** `praxis_bootstrap.py:52-71`; `pyodide_io_patch.py:28-98` (auto-invoked at import, `:262-263`); `direct-control-kernel.service.ts:156-182`; and `web_bridge.py:1451-1481`, which sets `builtins.WebSerial` (`:1466`) and `builtins.WebUSB` (`:1478`) and is called on the JupyterLite path at `praxis_bootstrap.py:274`. The fourth lives in the file this ADR keeps loose and moves verbatim, so P1 does not touch it. The plan's own line 106 makes the same miscount.
- **P1 moves, it does not delete.** P1.1 reads `(MOVE, not delete)`, P1.2 sends the worker to `experimental/`, and P1's verification asserts `test -d …/experimental/direct-control  # MOVED, not deleted`. The plan says "deletes" in prose at `:106` and mandates a move four lines later. Post-P1 there is one *live* copy and **three source copies**, and drift is measured on source. The plan's own pre-mortem notes moved code "decays by neglect" because tsc never checks it.
- **The invariant is violated right now**, on the shipping path — see §2.2.

So the wheel's structural benefit was **not** already bought. It is real and unbought, which is the strongest argument against this ADR's decision that any reviewer produced.

**Why the decision survives anyway:** the guarantee needed is *one class object per name*, and that requires a single **importable module**, not a package. A loose file written once to the VFS and imported once satisfies it. §2.2 mandates exactly that, with an `is`-assertion and a negative test. Packaging would have delivered the invariant as a side effect of install semantics; this ADR delivers it as an explicit, tested boot stage. **That is a weaker position than r1 claimed — the invariant is now something we must actively maintain rather than something the structure gives us for free — and §6 makes its failure a first-class reopening trigger.**

Meanwhile the wheel's value on the PLR side is **demonstrated, not theorised**: a spike renamed the wheel, got a 404, PLR never installed, and `praxis:ready` fired anyway with the shell looking healthy. That is visible in the live code — `praxis_bootstrap.py:239-246` logs the failure and falls through; `:286-293` posts `praxis:ready` regardless. Manifest indirection plus a fail-closed boot defuses exactly that. The wheel is kept where it is earned.

### 3.1 The testability argument — r1 got this wrong

r1 argued CPython unit tests of the shims "exercise almost nothing" because the browser APIs do not exist in CPython. **The premise is false and the conclusion is unsafe.**

- `web_serial_shim.py:23-31` wraps the browser imports in `try/except ImportError` and sets `IN_PYODIDE = False`. **The module imports cleanly in CPython today, with zero new infrastructure.** `tests/shim_verification_test.py` already does this (`sys.path.append` at `:8`).
- The testable surface is not empty, and it currently contains defects: `async def read` is **defined twice** (`:633` with a docstring-only body, immediately shadowed at `:636`); dead code after `return` at `:579-581`; `_calculate_ftdi_baud` (`:567-579`) is a pure divisor table where an unsupported baud silently falls back to 9600 with no error; FTDI `SET_DATA` bit-packing (`:522-534`) is pure integer logic buried in an async browser method where it cannot be tested as written; `serialize`/`deserialize` are **asymmetric** between `WebSerial` (`:296-317`) and `SerialProxy` (`:755-782`), which omits `write_timeout`/`rtscts`/`dsrdtr` and cannot restore them; and `read()` succeeds while `readline()` raises `"Port not open"` on an FTDI device, because `_setup_ftdi` (`:477-565`) never assigns `_reader`.
- **Two of the three specs already mandate CPython tests of this code.** Standalone `:144` requires `_sync_fetch` refactored to return `(ok, status, text)` and importable without `js`, with `tests/test_bootstrap_helpers.py` asserting four cases. Visualizer R15 (`:197-198`) requires a *browserless pytest* against `RecordingTransport` as gate D4. r1's §5 recorded "not unit-testable from CPython" as an accepted cost while §4.1/§4.2 declared those specs unaffected — a straight contradiction.

**Corrected position:** praxis's browser Python **is** CPython-testable, this ADR keeps it so, and loose files on a fixture-controlled path are as importable as a package. What packaging would have added is install-time namespace hygiene, not importability. §2.1 therefore extracts `bootstrap/{stages,transport}.py` as pure-CPython modules with no `import js`, generalising the one testability win rather than leaving it a one-off, and §2.4 pins the `sys.path` discipline that keeps the `praxis` shadowing from biting.

The PLR **contract** tests survive unchanged, because they test the PLR wheel, which still exists.

---

## 4. Per-spec re-scope tables

This is the part Phase 3's entry gate checks. A re-scope is not done until each row's replacement grep has a **non-zero denominator** against the new tree.

> **r2 correction — the gate cannot run at Phase 0 as r1 scheduled it.** `praxis/web-client/src/assets/visualizer*/` does not exist; neither does `praxis/viz/` or `web-repl/`. Every visualizer path, old *and* new, has a zero denominator today. The gate belongs at **Phase 3 entry**, after the tree exists. r1 declared it a Phase 0 gate and then satisfied it with a `praxis-browser` grep — which is how four silent-green verifications survived review.

### 4.1 Standalone spec — small re-scope, NOT zero

r1 said "NO re-scope required" on the basis of zero `praxis-browser` matches. Its `overlay/` shape is adopted, but three things need edits:

| item | change |
|---|---|
| tree `:68-69` `praxis/{__init__,interactive}.py` | unchanged — **but §1's collision table misreported these as deleted; that row is corrected** |
| `:84` "`assets/{shims,python,wheels}/` DELETED after the move" vs T03 `:211` "`assets/python/{sqlmodel,praxis/backend,praxis/protocol}` NOT moved" | **inherited contradiction, resolved here:** `assets/python/` is *not* deleted at T03. Only the moved subpaths are removed; the deferred experimental subtrees stay until T17. |
| T03 `:210` `test_hid.py` "(DELETE or move to web-repl/tests/)" | **resolved: DELETE.** It is a shim-directory smoke file, superseded by `web-repl/tests/`. |
| `:147` sweep grep (`web_serial_shim\|web_usb_shim`) | **widen** to include `pyodide_io_patch` — otherwise it misses `tests/shim_verification_test.py` (§1.1) |
| `web-repl/tests/` `sys.path` usage | must respect §2.4 — no `sys.path.append` of `overlay/assets/python` |

### 4.2 Visualizer spec — eight changes, not one

r1 said "one destination change." Actual count is eight, and four of its verifications currently pass while verifying nothing.

| # | spec artifact | old | new |
|---|---|---|---|
| 1 | `praxis/viz/` package | `assets/python/praxis/viz/` | `web-repl/overlay/assets/python/praxis/viz/` |
| 2 | T2.3 bootstrap edit | `assets/jupyterlite/praxis_bootstrap.py` | `web-repl/bootstrap/praxis_bootstrap.py` |
| 3 | vendored renderer | `assets/visualizer/` | `web-repl/overlay/assets/visualizer/` (**committed**) |
| 4 | augmentations | `assets/visualizer-augmentations/` | `web-repl/overlay/assets/visualizer-augmentations/` — **name preserved** |
| 5 | `vendor_visualizer.py` (R8 `:177`, a CI job) | repo-root `scripts/` | `web-repl/scripts/` |
| 6 | `VENDOR_MANIFEST.json` (`:222`) | inside `assets/visualizer/` | inside `overlay/assets/visualizer/` |
| 7 | test fixture (R9 `:180`) | `tests/fixtures/visualizer/set_root_resource.json` | `web-repl/tests/fixtures/…` |
| 8 | browserless pytest (R15 `:198`) | `tests/viz/test_browser_visualizer.py` | `web-repl/tests/viz/…`; R9's serve root moves from `praxis/web-client/src` to `web-repl/dist` |

**The four verifications with a vacuous clause — hardened, not rewritten.** Per §1's correction, none of these was silent-green *as a requirement*; each already fails via a sibling clause. What follows removes the dead clauses and makes the protecting one explicit, so a later edit cannot drop the clause that is doing the work:

| ref | assertion | why it passes vacuously | fix |
|---|---|---|---|
| ref | vacuous clause | what already protects it | hardening applied |
|---|---|---|---|
| **R7** `:174` | `git check-ignore -v …/visualizer/lib.js` exits 1 (pattern-only; cannot fail on a missing path) | `git ls-files …/visualizer/ \| wc -l >= 11` → 0 on a missing tree | existence clauses asserted **first**, plus `test -f` on `lib.js`; the check-ignore clause annotated as never-sole and never-reorderable |
| **R18** `:207` | `git diff --exit-code -- …/visualizer-augmentations` exits 0 (empty pathspec → no diff) | `grep -q …index.js …/visualizer/index.html` → exit 2 on a missing file | `test -d`/`test -f` precondition asserted first; vacuous clause labelled as such; **the name `visualizer-augmentations` marked load-bearing** (the relative `<script src>` at spec `:207` only resolves while the two are siblings) |
| **R19** `:210` | none — but the prose "returns no matches" invites an empty-stdout check, which *would* be vacuous | the parenthetical **(exit 1)**; a missing dir exits **2** | rewritten to "exits **1 EXACTLY**", with an explicit warning never to assert on empty stdout. **Guards the user-gesture security chain.** |
| **R21** `:216` | same | same | same. **Guards the device-auth channel from visualizer traffic.** |

R7 remains the instructive case: r1 claimed "`vendor-visualizer/` (**committed**, R7 preserved)" while its own move made R7's *first clause* vacuous and broke the `:207` anchor outright. R7 would still have failed — via `git ls-files` — but for the wrong reason and with a misleading message. Keeping the renderer under `overlay/assets/visualizer/` restores the anchor and makes rows 1–8 a mechanical prefix substitution.

Its `praxis_viz` / `praxis_repl` BroadcastChannel separation is untouched — but see §5.3: there is a **third** channel and it crosses the boundary.

### 4.3 Wheel spec — absorbs most of the change

| old path | disposition |
|---|---|
| `praxis-browser/pyproject.toml` | **DROPPED** — no package exists |
| `praxis-browser/praxis_browser/shims/` | → `web-repl/overlay/assets/shims/` (loose) |
| `praxis-browser/praxis_browser/web_bridge.py` | → `web-repl/overlay/assets/python/web_bridge.py` (loose) |
| `praxis-browser/praxis_browser/viz/` | → `web-repl/overlay/assets/python/praxis/viz/` (loose) |
| **`praxis-browser/praxis_browser/io_patch.py`** | **r2 ADDITION — r1 omitted this entirely.** → merged into `web-repl/bootstrap/praxis_bootstrap.py` + `stages.py`. It carries `install_native_stubs()` (which "REPLACES `_mock_native_deps` entirely" — today's MagicMock is **load-bearing**; naive removal flips all four capability flags False, spec `:90-93`) and `apply()`, the home of the identity assertion. **R13/R14 re-scope to the bootstrap.** R14's grep (`:176`, "names exactly ONE file") becomes: `grep -rln 'def patch_pylabrobot_io\|_inject_serial_shim\|def _mock_native_deps' --include=*.py` names exactly one file, `web-repl/bootstrap/praxis_bootstrap.py`. |
| **`praxis-browser/praxis_browser/errors.py`** | **r2 ADDITION.** **DROPPED** — the taxonomy has exactly one home, `bootstrap/stages.py`. This is a genuine gain: wheel spec `:355` warns the two-home design could let `except PraxisDriftError` fail to catch the loader's class, and mandates an identity assertion as the first boot stage to guard it. With one home that risk does not exist and the assertion is unnecessary. |
| `praxis-browser/praxis_browser/boot.py` | **MERGED** into `web-repl/bootstrap/praxis_bootstrap.py`; the loader owns the ordered fail-closed stage ledger and `praxis:ready` stays inside the guarded region |
| `praxis-browser/praxis_browser/experimental/machines.py` | → `web-repl/overlay/assets/python/experimental/machines.py`. **This file does not exist yet** — `_MACHINE_CLASS_MAP` is inline at `web_bridge.py:407-414` (resolved at `:435`), so this is an **extraction task, not a move**, and must be scheduled as such. The "never delete" reasoning carried over from spec `:121` applies once it exists. |
| `praxis-browser/vendor/pylibftdi-0.0.0-py3-none-any.whl` | → generated into `web-repl/overlay/assets/wheels/` from checked-in source at `web-repl/scripts/pylibftdi_stub/`. The hand-committed binary with no recipe is **retired, not relocated**. |
| `praxis-browser/tests/test_plr_contract.py` | → `web-repl/tests/test_plr_contract.py` — survives unchanged; still runs in a throwaway venv so `pylabrobot.__file__` is NOT under `external/` |
| `praxis-browser/tests/test_contract_covers_imports.py` | → `web-repl/tests/`, repointed at `overlay/assets/{python,shims}/`. **This is D3 (§2.3)** — keep it; it is the best first-party drift detector available. |
| `praxis-browser/README.md` | merged into `web-repl/README.md` |
| **`.gitignore:25` `!**/src/assets/wheels/`** | **r2 ADDITION — r1 had no row for this.** Becomes a **dead negation** once `praxis/web-client/src/assets/wheels/` is deleted. R6 (`:150`) is line-number-keyed to `sed -n '22,26p' .gitignore`. Remove the negation in the same commit as the deletion, and re-derive R6's line numbers. |

**Two gates r1 wrongly listed as "preserved verbatim":**

- **R6** (`:150`) requires `git ls-files 'praxis-browser/vendor/*.whl'` to print exactly one line. Unsatisfiable — fails loud, which is acceptable — but its second clause is the `.gitignore` line-number assertion above, which must be re-derived.
- **R8** (`:156`) requires `check_wheel_coherence.py --check-untracked` to exit 0 *"with `praxis-browser/vendor/pylibftdi-…whl` tracked and allowlisted BY NAME"*, plus a negative arm proving the allowlist is name-scoped rather than directory-scoped. With the binary retired there is no allowlist entry, so the positive arm exits 0 trivially and the negative arm proves nothing. **R8 must be re-specified** against the generated stub: the allowlist entry becomes the *generated* filename in `overlay/assets/wheels/`, and the negative arm force-adds a differently-named wheel there. Retiring the binary is still better engineering — but it is not "unaffected," and r1 asserted the opposite.

**Preserved verbatim** (verified content unaffected by this ADR): `scripts/build_wheels.py` with git-archive export and `+g<sha8>` version stamping; `manifest.json` written atomically via `os.replace`; the error taxonomy (`PraxisUnavailableError` / `PraxisDriftError`); the four negative browser runs; and `check_wheel_contract.py`.

### 4.4 The fourth consumer — disposition: DELETE

`praxis/web-client/e2e/specs/jupyterlite-bootstrap.spec.ts` has never run in CI (no Playwright workflow; no `e2e` script in `package.json`) and is largely vacuous: `.loading-overlay` `not.toBeVisible()` passes on an element that never existed, `readyLogs.length > 0 || overlayGone` passes whenever the overlay is absent, and `errorOverlay.count() ≤ 1` is near-tautological on a locator yielding 0 or 1. It does contain one real assertion — `expect(errors).toHaveLength(0)` filtering console output for `SyntaxError`/`Bootstrap failed` — so it is not *entirely* vacuous.

It tests the Angular playground path P1 retires. **Delete it**, and let `web-repl/tests/e2e/` plus `scripts/repl_smoke.py` be the real harness. Re-scoping it to a new path would ship an already-green vacuous test into the new tree — the exact pathology §1 exists to prevent.

---

## 5. Consequences

**Accepted:**
- Two delivery mechanisms coexist (wheels for third-party, loose files for first-party). That is a seam, and seams rot. It is justified only because the evidence is asymmetric across it — and §2.3's manifest-covers-sources design narrows it, since both sides now share one integrity mechanism at the fetch layer.
- `web-repl/` is a new top-level directory in a repo that already has several.
- **The single-class-object invariant is maintained by assertion, not by structure** (§2.2). Packaging would have given it for free. This is the decision's principal ongoing cost.

**Gained:**
- The path collision dissolves; each contested file has exactly one owner.
- Edit→reload stays seconds for the hardware-adjacent code where iteration matters most, including the never-worked WebSerial fix.
- Phase 3 shrinks: no package scaffolding, no two-wheel micropip sequencing, no `import praxis_browser` behavioural-equivalence risk.
- The error taxonomy gets exactly one home, retiring wheel-spec `:355`'s two-home hazard and the boot-stage assertion it required.
- Seven previously-uncovered fetch literals come under the manifest seam (§2.3 D2).
- Drift detection is now *stronger* than r1 proposed and than the two-wheel `BUILD_ID` scheme: D1 keeps the whole-deployment check r1 broke, D2 adds per-source integrity, D3 adds semantic import coverage.

### 5.1 The builtins namespace is the second seam, and it is undeclared

`manifest.json` is the only *filename* seam, but the actual cross-file contract is `builtins`: `praxis_bootstrap.py:226-236` staples four shim classes; `:52-71` reads them back to overwrite `pylabrobot.io.*`; `:74-82` sprays all of `pylabrobot.resources`; `:269` sets `builtins._PRAXIS_JUPYTERLITE`, read at `web_bridge.py:1405`. Five named attributes plus an unbounded spray, across four files, with no schema.

**Required:** a `BUILTINS_CONTRACT` tuple at the top of `bootstrap/stages.py`, asserted stage-by-stage by the fail-closed ledger. That converts an invisible seam into a checkable one for ~10 lines, and it is what makes §6's failure signal observable. U15 remains open for the REPL's user contract.

### 5.2 The boundary is directional, and the sanctioned edge is build-time

r1's "`web-repl/` has no import path into `praxis/`" is true but guards the direction that needs no guarding. The direction that matters is the reverse, and the standalone spec **mandates** it: `:100` has `angular.json` gaining an asset entry copying a pinned `web-repl` release tarball into `dist/…/assets/repl/`, and `:188` requires Angular to embed "a PINNED web-repl artifact at a same-origin subpath."

**Restated:** no *Python import* path in either direction; **one** build-time, pinned-artifact edge `praxis/web-client → web-repl/dist`, and it is the only sanctioned edge. No enforcement exists today (no import-linter, no tach; `TID252` is ignored at `pyproject.toml:239`). `[tool.setuptools] packages = ["praxis"]` (`:121`) correctly keeps `web-repl` out of the distribution, but that is packaging, not a boundary. **Make it checkable:** one CI assertion that `angular.json` references `web-repl` at most once and that the entry names a pinned artifact, not a live directory.

### 5.3 `SerialProxy` — DECIDED: delete the Python half, retire the driver layer, gate FTDI on S-E

The channel set is **three**, not the two §4.2 discusses. Two exist in live code — `praxis_repl` (`praxis_bootstrap.py:90`, `:288`) and `praxis_serial` (`web_serial_shim.py:102`) — and the visualizer spec creates `praxis_viz`. `web_serial_shim.py:40-317` defines `SerialProxy`, whose docstring (`:41-49`) says it *"delegates all I/O to the main thread via BroadcastChannel… The main thread SerialManager service handles the actual device communication."* The counterparty is `praxis/web-client/src/app/core/services/serial-manager.service.ts` — inside `praxis/`.

`praxis_repl` crosses the same way, with **three** Angular counterparties: `jupyter-channel.service.ts:26`, `playground-jupyterlite.service.ts:84`, `playground-asset.service.ts:66`. So the runtime coupling into `praxis/` is broader than one class — but `praxis_repl`’s counterparties all sit inside the playground surface P1 retires, whereas `SerialManager` is device infrastructure with no replacement in the standalone site.

A BroadcastChannel needs no import, so §5.2's boundary is silent about it. Post-extraction the standalone site has no Angular main thread and therefore no `SerialManager`, so `SerialProxy._send_request` (`:126-160`) posts and times out after 5s with `"Request serial:open timed out"` — an entire transport class shipping as guaranteed-dead code.

**Correction to the framing this section inherited from the adversarial review.** It reported that post-extraction "an entire transport class ships as guaranteed-dead code." Investigated: it is dead **now**, not post-extraction. Nothing constructs `SerialProxy` — all 20 references are inside its own class body, it is never stapled onto `builtins`, and `_patch_io_modules` binds `pylabrobot.io.serial.Serial = builtins.WebSerial` (`praxis_bootstrap.py:59`), never `SerialProxy`. The counterparty `SerialManager` is instantiated (`playground.component.ts:374`) and logs *"ready for main-thread serial I/O"* (`:431-432`) while listening forever for messages nobody sends. So `praxis_serial` is a complete, tested, two-sided bridge with **zero live callers on either end**, and extraction removes an already-idle listener rather than creating a regression.

**Two independent things were bundled in that one dead class:**

- **(a) the RPC pattern** — kernel delegates gesture-requiring operations to the main thread, because a worker cannot call `requestPort()`. `web_serial_shim.py:393` records this explicitly: *"The frontend (React/Angular) is responsible for calling `requestPort()`."* This pattern survives regardless; `praxis-shell.js` is being built for exactly it.
- **(b) an FTDI-over-WebUSB driver** — `FtdiSerial`'s constructor takes a **`USBDevice`** (`ftdi-web-serial.ts:45`), so this is a genuinely different transport from Web Serial, backed by 898 LOC of TypeScript. Real capability, currently reachable only through the dead bridge.

**DECISION (2026-08-17, user-directed):**

| artifact | disposition | why |
|---|---|---|
| `SerialProxy` (`web_serial_shim.py:40-317`) | **DELETE** | Provably unreachable. The "move, never delete" rule protects code a revert might need; a revert cannot need a class nothing calls. |
| `SerialManager` + spec | **MOVE** to `experimental/services/` | Complete, tested reference implementation of a transport Web Serial cannot provide. |
| `features/playground/drivers/` (898 LOC) | **MOVE** to `experimental/drivers/` | Same. |
| "does the REPL need main-thread FTDI?" | **GATED ON SPIKE S-E** | S-E already carries the human+hardware dependency that would settle it. Building the shell-side counterparty now would be unproven structure — the same shape this ADR rejected for the `praxis_browser` wheel. |

If S-E shows that WebSerial's `getPorts()` plus a shell-side `requestPort()` is insufficient for real hardware, porting the counterparty into `praxis-shell.js` becomes a scheduled task **with a known reference implementation to work from** — which is precisely what retiring rather than deleting buys.

**Ordering hazard, recorded:** `serial-manager.service.ts:20` imports `PlaygroundComponent` — a core service reaching into a feature component. That inversion must be broken before the move, and it is why this is not a lift-and-shift into the shell. Implemented as standalone-spec **R31 / T20**, gated by **G7**.

### 5.4 Tooling exposure created by the move

- **ruff.** `pyproject.toml:217` `exclude` does not list `web-repl`, and ruff runs `select = ["ALL"]` with `fix = true` and `indent-width = 2`. The bootstrap and shims are 4-space indented and escape ruff today only because `praxis/web-client/.gitignore:10` gitignores them. Moving them un-ignored subjects browser Python (`from js import …`, `import micropip`) to autofix reindentation, which is incompatible with standalone T03's "move the kernel payload **verbatim**." **Add `"web-repl/overlay"` and `"web-repl/bootstrap"` to `[tool.ruff] exclude` in the same commit as the move.** Keep `web-repl/scripts` and `web-repl/tests` in scope — those are real CPython and should be linted.
- **pytest.** `pyproject.toml:131` `testpaths = ["tests"]`, `:159` `addopts` includes `--cov=praxis`, and `norecursedirs` (`:137-153`) omits `web-repl`. `web-repl/tests/` would run under `--cov=praxis` reporting ~0% and hard-fail when CI restores `--cov-fail-under`. **Hence `web-repl/pyproject.toml` (pytest section only, `--no-cov`) in §2.1.**
- **gitignore.** `.gitignore:14` `dist/` and `:23` `wheels/` are bare patterns matching at any depth, so `web-repl/dist/` and `web-repl/overlay/assets/wheels/` are ignored with no new rules. But `:14` being bare means a vendored renderer containing a `dist/` subdir would be **silently re-broken into the dead-page bug**. **Add `!web-repl/overlay/assets/visualizer/**` defensively and assert it:** `git check-ignore -v web-repl/overlay/assets/visualizer/lib.js` exits 1 *on a file that exists*.

### 5.5 The served path change is the only irreversible thing here

§2.1 moves the site root to `web-repl/dist/`. JupyterLite keys its IndexedDB store as `JupyterLite Storage - ${baseUrl}`, and the persistence spike proved *by content* that this isolates stores per mount path (mount A wrote `shared.txt`; mount B read `NOT-FOUND`; neither saw the other's writes). The two shipped configs already disagree (`"./"` vs `"/praxis/assets/jupyterlite/"`) with nothing pinning the name. Ship the path move without a migration and existing notebooks are orphaned with no in-app recovery and no undo.

> **G2 amendment (260817) — the constraint pins three keys, not one.** GATE G2 spike S-C proved by CONTENT that `contentsStorageName` does override the IndexedDB store name, but it also surfaced a third read site the original two-key recipe missed: the shipped bundle (`praxis/web-client/.../build/8262.7bb3dc3.js`) shows `LiteWorkspaceManager.activate` reading `workspacesStorageName` independently, defaulting to the same baseUrl-derived name if unset — `a=getOption("workspacesStorageName")||i` — alongside `contentsStorageName` and `settingsStorageName` (which itself falls back to the contents key, `getOption("settingsStorageName")||s`, not to the baseUrl default directly). Pinning only `contentsStorageName` left `store_enumeration_clean=false`: two orphaned per-baseUrl `JupyterLite Storage - ${baseUrl}` workspace databases survived alongside the pinned contents store. Pinning all three keys together produced `store_enumeration_clean=true` — exactly one database, `praxis-repl-contents`, with zero databases matching the legacy pattern. See `.praxia/docs/research/260817_g2-spike-battery-verdict.md` (criterion G2-4) for the full evidence. The constraint below is amended accordingly; the "same commit as the path move" requirement is unchanged.

**Constraint, binding on this tree (amended 260817 — G2):** it does **not** authorise a served-path change until `contentsStorageName`, `settingsStorageName`, and `workspacesStorageName` are all explicitly pinned in `jupyter-lite.json` (§2.1) and the migration lands in the same commit as the path move.

**The signal this ADR was wrong:** the §2.2 identity assertion fires in normal development, or the shims drift again at the *text* level after P1 — note the check must be text-level, since P1 leaves three source copies (§3(c)).

---

## 6. Revisit triggers

**r2 change: these are DISJUNCTIVE.** r1 required all three, and its trigger (3) was "a first-party drift ships undetected" — an unobservable event, ANDed with two unscheduled spikes, which priced a ~1-day reversal as if it were irreversible. Reversal is cheap: §4.3 preserves the entire wheel pipeline, every move is `git mv`, and the wheel spec's T4–T11 survive on disk as an unexecuted recipe. Reopen on **any** of:

1. **The §2.2 identity assertion proves unmaintainable** — it fires in ordinary development, or a change lands that re-introduces a second class object without tripping it. This is the direct consequence of withdrawing §3(c) and is the trigger to watch.
2. **Wheel-spec T16 measures the rebuild loop in tens of seconds rather than a few.** §3(b) rests on this unmeasured quantity; measuring it is scheduled and cheap.
3. **A spike shows the browser subtree packages cleanly and `import praxis_browser` preserves builtins-spray parity** (closes U15 for the layout), removing §3(a)'s objection.
4. **D1's dev-sentinel design (§2.3) cannot be observed failing on a genuine mismatch** in its negative test. Checkable at Phase 3 — not after a production incident.

---

## 7. Open, and deliberately not decided here

- Whether Angular embeds the REPL at all post-extraction (U20). This ADR is agnostic; §5.2's single build-time edge holds either way.
- Whether Pyodide is vendored for offline operation (U18/U19). Changes artifact size, not layout. `vendor/` is in §2.1's tree either way.
- The `repl/` vs `lab/` app choice — a Phase 5 surface decision. The courier contract is asserted invariant under it (visualizer C19), which is itself untested.
- **Whether S-E/U1 (the hardware gesture spike) invalidates §2.1.** If it fails and the architecture reverts to Design A's iframe topology, `web-repl/` as a sibling must be re-evaluated. Not evaluated here.

---

## 8. Review record

| review | verdict | what it changed |
|---|---|---|
| architecture (opus) | **DO NOT LOCK** | §3(c) withdrawn (P1 moves, not deletes); §2.3 D2 manifest-covers-sources; §4.2 visualizer staging gap — r1's tree meant the visualizer never reached the page; §2.1 eight omitted paths; §5.2 boundary restated as directional; §5.4 ruff/pytest/gitignore exposure; §5.1 builtins as second seam |
| challenger (opus) | **NOT READY** | §2.3 D1 — r1 destroyed a pre-existing shell-injected check; §2.2 the four-site count and the live identity violation; §4.3 `io_patch.py` and `errors.py` rows; §4.2 four silent-green verifications; §4.1 `praxis/interactive.py` dropped from the tree; §3.1 empirically refuted; §5.3 the third channel; §6 one-way ratchet; §4.3 R6/R8 not "preserved verbatim" |
| oracle (opus) | **LOCK WITH AMENDMENTS** | §6 disjunctive triggers; §5.5 mount-path/IndexedDB constraint; §4.3 D3 kept and repointed by path; §4.4 delete the vacuous e2e spec; §1.2 "blocks" narrowed; §3(b)'s second leg (drift detection is absent, not weak) |

**Every claim above that changed was re-verified against the code before acceptance**, including: the plan's `:106`-vs-`P1.1` self-contradiction; the four monkeypatch sites and the `A is not B` identity violation; `git check-ignore` exiting 1 on a nonexistent path; the duplicate `async def read`; ruff's `exclude` omitting `web-repl`; and wheel spec `:101`/`:115` on shell injection.

**Two reviewer claims were rejected or corrected:**

- The challenger concluded the identity violation makes packaging *necessary* — *"the only specified mechanism that structurally guarantees one class object is a single importable module — i.e. `praxis_browser.io_patch`."* Rejected: a loose file written once to the VFS and imported once **is** a single importable module. Packaging buys install-time guarantees, not `is`-identity. §2.2 delivers the invariant without it, at the cost recorded in §5.
- The architecture review counted "ten hardcoded fetch literals" at `praxis_bootstrap.py:184-194`. It is **seven** (four shims plus three other files).

**A third reviewer claim was corrected after testing (§1, §4.2):** the challenger's "four verifications that pass while verifying nothing" is wrong at the requirement level for all four. Each is a conjunction whose sibling clause fails on a missing tree — `git ls-files` returns 0 against R7's `>= 11`; `grep -q` and `grep -r` both exit **2**, not 1, on a missing target. r2's own first draft repeated the claim uncritically before the exit codes were run. Only individual clauses were vacuous, and those are now hardened.

## 9. Re-scope applied (2026-08-17)

§4.1–§4.3 have been **applied to all three spec documents**.

| spec | applied |
|---|---|
| standalone | `assets/python/` no longer declared deleted (only the moved files are removed; `sqlmodel/`/`backend/`/`protocol/` stay until T17); `test_hid.py` resolved to **DELETE**; the `:147` sweep grep widened to `pyodide_io_patch` so it can no longer miss `tests/shim_verification_test.py`; tree completed with `viz/`, `experimental/`, both visualizer dirs, `bootstrap/{stages,transport}.py`, `scripts/{vendor_visualizer,pylibftdi_stub}`, the contract tests and `pyproject.toml`; **new R27–R30** (sys.path discipline, ruff exclude, pytest `--no-cov`, and R-ID the single-class-object invariant), each with a negative arm that must be observed failing |
| visualizer | all eight path changes applied (54 substitutions, zero residual old paths); the four vacuous clauses hardened per §4.2; `visualizer-augmentations` name preserved and marked load-bearing; R9's serve root moved to `web-repl/dist` |
| wheel | **supersession banner** at the top declaring the `praxis_browser` package rejected and provenance-only; ~60 path substitutions to `web-repl/…`; package-only artifacts (`pyproject.toml`, `__init__.py`, `_build_info.py`) struck through rather than repointed; **R6 and R8 re-specified** to zero-tracked-wheels with a three-arm negative test replacing the dead name-scoped allowlist; R11b repointed (its SHELL-SUPPLIED wording was already correct and is now detector D1); R13's identity check repointed to the VFS module and strengthened; GATE 4's negative run (4) re-specified from two-wheel `BUILD_ID` drift to D2 source-integrity plus D1 staleness, including a dev-sentinel-cannot-mask-it arm; T4 retitled to "no package" |

**38 `praxis_browser` module references remain in the wheel spec by design** — they describe the rejected package and are covered by the supersession banner as provenance. They are not repointed, because there is nothing to repoint them to.

**§5.3 decided 2026-08-17** — SerialProxy deleted, the FTDI-over-WebUSB counterparty retired to `experimental/`, the capability question gated on S-E. Implemented as standalone-spec R31/T20 and asserted by G7.

**Both lock conditions this ADR named for itself are now met**, so its status moves from PROPOSED to **ACCEPTED**. What remains is execution, not decision — plus the four §6 triggers, which are monitoring conditions rather than blockers. The one genuinely irreversible downstream item stays constrained by §5.5: no served-path change until `contentsStorageName`, `settingsStorageName`, and `workspacesStorageName` are all pinned (amended 260817 — G2) and the migration lands in the same commit.
