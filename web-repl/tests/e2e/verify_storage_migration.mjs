// web-repl/tests/e2e/verify_storage_migration.mjs
//
// P5.5 -- verifies the T08 legacy IndexedDB migration (ADR Sec 5.5, amended
// by GATE G2; standalone spec T08) BY CONTENT against a REAL built
// `web-repl/dist/` -- not a name-only comparison (a name-only comparison
// produced a false positive in this project once already, per this
// project's spec).
//
// This is NOT wired into a `playwright test` suite -- `web-repl/` has no
// `playwright.config.ts` / `package.json` of its own yet (that is P5.9's
// job, and the standalone spec's own T08 verification line names a future
// `tests/e2e/storage-migration.spec.ts` built on it). This script is the
// honest, currently-runnable equivalent: a standalone Node script driven by
// `playwright-core`, reusing the browser binaries and the `playwright-core`
// package already vendored under `praxis/web-client/node_modules/` rather
// than adding a new dependency to stand this up. When P5.9 lands, port the
// scenario below into a real `.spec.ts` file and this script can retire.
//
// WHAT THIS PROVES, and how (all five checks below are asserted, not just
// printed -- a non-zero exit means a real failure):
//
//   1. Two legacy per-baseUrl databases ("JupyterLite Storage - /mount-a/",
//      "-/mount-b/"), each holding a notebook (files store), a setting
//      (settings store), and a workspace entry (statedb store) -- exactly
//      the three categories G2's amendment identified -- are seeded BEFORE
//      the migrating page ever loads (on an inert same-origin page that
//      never runs praxis-shell.js, avoiding a real race this script's
//      first draft hit: the migration IIFE can finish running, against
//      zero legacy databases, before a same-navigation seed step gets a
//      chance to write anything).
//   2. The REAL dist/lab/index.html is loaded for real (not stubbed), and
//      the migrated notebook is read back through the REAL app's own
//      `serviceManager.contents.get()` API -- the strongest verification
//      available, going through the actual bundled JupyterLite/localforage
//      code path rather than only a raw IndexedDB read.
//   3. The migrated settings and workspace entries are read back from the
//      pinned destination stores via raw IndexedDB (there is no UI-level
//      settings/workspace API as convenient as `contents.get`).
//   4. `store_enumeration_clean`: after migration, `indexedDB.databases()`
//      contains ZERO entries matching /^JupyterLite Storage - /.
//   5. The legacy bytes are NOT destroyed -- IndexedDB has no rename
//      primitive, so the migration copies each legacy database's full
//      structure into a `praxis-repl-legacy-backup - <baseUrl>` database
//      (a non-legacy-pattern name) before deleting the original. This
//      script asserts that backup database holds the original content.
//   6. Idempotency: reloading the page a second time does not re-run the
//      migration (`window.__praxisMigrationReady` resolves with
//      `{ran: false, reason: "already migrated"}`) and does not duplicate
//      data.
//
// PREREQUISITES this script does NOT set up for you:
//   - `web-repl/dist/` must be a real, current build (`uv run python
//     scripts/build_repl.py --out dist` from `web-repl/`) -- this script
//     does not build it, and a stale `dist/` (e.g. one built before
//     `jupyter-lite.json` had the three storage-name keys, which happened
//     once already in this sprint due to a stale `.jupyterlite.doit.db`
//     incremental-build cache -- delete that file if a rebuild doesn't
//     pick up a jupyter-lite.json edit) will make this script fail in a
//     confusing way, not a useful one.
//   - A `node` binary on PATH (this repo does not vendor one at the
//     top level; this sprint used `~/.nvm/versions/node/v24.14.1/bin`).
//   - `praxis/web-client/node_modules/playwright-core` present (already a
//     dependency of the Angular app's own e2e suite) and a cached Chromium
//     matching one of its supported revisions under
//     `~/.cache/ms-playwright/` (`CHROMIUM_EXECUTABLE` below pins the one
//     used at authoring time -- update it if that cache rotates).
//   - A static file server for `web-repl/dist/` on `PORT` below (e.g.
//     `python -m http.server` from that directory). This script does not
//     start one, so a race with a same-conversation server start does not
//     leave an orphaned process this script cannot see.
//
// Run:
//   PATH="$HOME/.nvm/versions/node/v24.14.1/bin:$PATH" \
//     node web-repl/tests/e2e/verify_storage_migration.mjs
//
// Exits 0 and prints "PASS" with the full evidence JSON on success; exits 1
// and prints the first failing assertion (plus whatever evidence was
// gathered) otherwise.

import { chromium } from "../../../praxis/web-client/node_modules/playwright-core/index.mjs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const PORT = process.env.PRAXIS_E2E_PORT || "8134";
const BASE = `http://127.0.0.1:${PORT}`;
const CHROMIUM_EXECUTABLE =
  process.env.PRAXIS_E2E_CHROMIUM ||
  path.join(
    process.env.HOME || "",
    ".cache/ms-playwright/chromium-1228/chrome-linux64/chrome"
  );

const evidence = {};
const failures = [];

function assert(cond, message) {
  if (!cond) {
    failures.push(message);
    console.error("ASSERTION FAILED:", message);
  } else {
    console.log("ok:", message);
  }
}

// Injected into page context -- must be self-contained (no closures over
// outer scope; page.evaluate serializes this as source text).
function idbHelpers() {
  window.__idbOpen = function (name, version, upgradeFn) {
    return new Promise((resolve, reject) => {
      const req = version ? indexedDB.open(name, version) : indexedDB.open(name);
      req.onupgradeneeded = (e) => {
        if (upgradeFn) upgradeFn(req.result, e);
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  };
  window.__idbPut = function (db, storeName, key, value) {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, "readwrite");
      tx.objectStore(storeName).put(value, key);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
    });
  };
  window.__idbGet = function (db, storeName, key) {
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, "readonly");
      const r = tx.objectStore(storeName).get(key);
      r.onsuccess = () => resolve(r.result);
      r.onerror = () => reject(r.error);
    });
  };
}

async function main() {
  const browser = await chromium.launch({ executablePath: CHROMIUM_EXECUTABLE });
  const page = await browser.newPage();
  page.setDefaultTimeout(180000);
  const consoleLines = [];
  page.on("console", (m) => consoleLines.push(`[console:${m.type()}] ${m.text()}`));
  page.on("pageerror", (e) => consoleLines.push(`[pageerror] ${e}`));

  try {
    // Step 1: seed two legacy databases on an INERT same-origin page that
    // never loads praxis-shell.js -- see header comment for why this
    // ordering matters.
    await page.goto(`${BASE}/__seed_placeholder__`, { waitUntil: "domcontentloaded" });

    const seedResult = await page.evaluate(async (helpersSrc) => {
      eval(helpersSrc);
      const legacyNames = ["JupyterLite Storage - /mount-a/", "JupyterLite Storage - /mount-b/"];
      const markers = {};
      for (const name of legacyNames) {
        const db = await window.__idbOpen(name, 1, (d) => {
          if (!d.objectStoreNames.contains("files")) d.createObjectStore("files");
          if (!d.objectStoreNames.contains("settings")) d.createObjectStore("settings");
          if (!d.objectStoreNames.contains("statedb")) d.createObjectStore("statedb");
        });
        const fileMarker = "CONTENTS_MARKER_" + name + "_" + Date.now();
        const settingsMarker = "SETTINGS_MARKER_" + name + "_" + Date.now();
        const workspaceMarker = "WORKSPACE_MARKER_" + name + "_" + Date.now();
        const notebookKey = name === legacyNames[0] ? "legacy.ipynb" : "legacy-b.ipynb";
        await window.__idbPut(db, "files", notebookKey, {
          name: notebookKey,
          path: notebookKey,
          last_modified: new Date().toISOString(),
          created: new Date().toISOString(),
          format: "json",
          mimetype: null,
          content: {
            cells: [{ cell_type: "code", source: fileMarker, outputs: [], execution_count: null }],
            metadata: {},
            nbformat: 4,
            nbformat_minor: 5,
          },
          writable: true,
          type: "notebook",
          size: 0,
        });
        await window.__idbPut(db, "settings", "@jupyterlab/apputils-extension:themes", {
          id: "@jupyterlab/apputils-extension:themes",
          raw: JSON.stringify({ marker: settingsMarker }),
        });
        await window.__idbPut(db, "statedb", "layout-restorer:data", { marker: workspaceMarker });
        db.close();
        markers[name] = { notebookKey, fileMarker, settingsMarker, workspaceMarker };
      }
      return { markers };
    }, `(${idbHelpers.toString()})()`);
    evidence.seedResult = seedResult;
    assert(
      Object.keys(seedResult.markers).length === 2,
      "seeded exactly two legacy databases with content in all three categories"
    );

    // Step 2: real navigation to the migrating page.
    await page.goto(`${BASE}/lab/index.html`, { waitUntil: "domcontentloaded" });

    const migrationOutcome = await page.evaluate(async () => {
      if (!window.__praxisMigrationReady) {
        return { error: "window.__praxisMigrationReady is not defined" };
      }
      try {
        return { ok: true, result: await window.__praxisMigrationReady };
      } catch (e) {
        return { ok: false, error: String(e) };
      }
    });
    evidence.migrationOutcome = migrationOutcome;
    assert(migrationOutcome.ok === true, "window.__praxisMigrationReady resolved without throwing");
    assert(
      migrationOutcome.result && migrationOutcome.result.ran === true,
      "migration reported ran:true on first load (found legacy data to migrate)"
    );

    // Step 3: wait for the real app to boot, then verify through its own API.
    const deadline = Date.now() + 120000;
    let appReady = false;
    while (Date.now() < deadline) {
      appReady = await page.evaluate(
        () =>
          !!(window.jupyterapp && window.jupyterapp.serviceManager && window.jupyterapp.serviceManager.isReady)
      );
      if (appReady) break;
      await new Promise((r) => setTimeout(r, 1500));
    }
    evidence.appReady = appReady;
    assert(appReady, "the real JupyterLite app booted (window.jupyterapp.serviceManager.isReady)");

    let contentsCheck = { ok: false, error: "app never became ready" };
    if (appReady) {
      contentsCheck = await page.evaluate(async () => {
        try {
          const model = await window.jupyterapp.serviceManager.contents.get("legacy.ipynb", { content: true });
          return { ok: true, source: model.content.cells[0].source };
        } catch (e) {
          return { ok: false, error: String(e) };
        }
      });
    }
    evidence.contentsCheck = contentsCheck;
    assert(
      contentsCheck.ok === true &&
        contentsCheck.source === seedResult.markers["JupyterLite Storage - /mount-a/"].fileMarker,
      "migrated notebook readable through the REAL app's serviceManager.contents API, correct marker"
    );

    // Step 4/5: raw destination checks, store_enumeration_clean, backups.
    const finalState = await page.evaluate(async (helpersSrc) => {
      eval(helpersSrc);
      const allDbs = (await indexedDB.databases()).map((d) => d.name).sort();
      const legacyPattern = /^JupyterLite Storage - /;
      const legacyRemaining = allDbs.filter((n) => legacyPattern.test(n));

      async function readFrom(dbName, storeName, key) {
        try {
          const db = await window.__idbOpen(dbName);
          if (!db.objectStoreNames.contains(storeName)) {
            db.close();
            return { error: `store ${storeName} not present in ${dbName}` };
          }
          const val = await window.__idbGet(db, storeName, key);
          db.close();
          return { value: val };
        } catch (e) {
          return { error: String(e) };
        }
      }

      return {
        allDbs,
        legacyRemaining,
        store_enumeration_clean: legacyRemaining.length === 0,
        settingsA: await readFrom(
          "praxis-repl-settings",
          "settings",
          "@jupyterlab/apputils-extension:themes"
        ),
        workspacesA: await readFrom("praxis-repl-workspaces", "statedb", "layout-restorer:data"),
        contentsB: await readFrom("praxis-repl-contents", "files", "legacy-b.ipynb"),
        backupA: await readFrom("praxis-repl-legacy-backup - /mount-a/", "files", "legacy.ipynb"),
        backupB: await readFrom("praxis-repl-legacy-backup - /mount-b/", "files", "legacy-b.ipynb"),
        migratedFlag: localStorage.getItem("praxis-repl-migrated"),
      };
    }, `(${idbHelpers.toString()})()`);
    evidence.finalState = finalState;

    assert(
      finalState.store_enumeration_clean === true,
      "store_enumeration_clean: zero databases match /^JupyterLite Storage - / after migration"
    );
    assert(
      finalState.settingsA.value &&
        JSON.parse(finalState.settingsA.value.raw).marker ===
          seedResult.markers["JupyterLite Storage - /mount-a/"].settingsMarker,
      "migrated settings entry present in praxis-repl-settings/settings with correct marker"
    );
    assert(
      finalState.workspacesA.value &&
        finalState.workspacesA.value.marker ===
          seedResult.markers["JupyterLite Storage - /mount-a/"].workspaceMarker,
      "migrated workspace entry present in praxis-repl-workspaces/statedb with correct marker"
    );
    assert(
      finalState.contentsB.value &&
        finalState.contentsB.value.content.cells[0].source ===
          seedResult.markers["JupyterLite Storage - /mount-b/"].fileMarker,
      "second legacy database (mount-b) also migrated correctly"
    );
    assert(
      finalState.backupA.value &&
        finalState.backupA.value.content.cells[0].source ===
          seedResult.markers["JupyterLite Storage - /mount-a/"].fileMarker,
      "legacy bytes for mount-a preserved under praxis-repl-legacy-backup - /mount-a/ (recovery path, not deleted)"
    );
    assert(
      finalState.backupB.value &&
        finalState.backupB.value.content.cells[0].source ===
          seedResult.markers["JupyterLite Storage - /mount-b/"].fileMarker,
      "legacy bytes for mount-b preserved under praxis-repl-legacy-backup - /mount-b/ (recovery path, not deleted)"
    );
    assert(finalState.migratedFlag === "1", "praxis-repl-migrated flag set after a successful migration");

    // Step 6: idempotency.
    await page.reload({ waitUntil: "domcontentloaded" });
    const secondRunOutcome = await page.evaluate(async () => window.__praxisMigrationReady);
    evidence.secondRunOutcome = secondRunOutcome;
    assert(
      secondRunOutcome && secondRunOutcome.ran === false && secondRunOutcome.reason === "already migrated",
      "second page load does not re-run the migration (idempotent)"
    );
  } finally {
    evidence.consoleTail = consoleLines.slice(-40);
    await browser.close();
  }
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  main()
    .then(() => {
      console.log("\n--- evidence ---");
      console.log(JSON.stringify(evidence, null, 2));
      if (failures.length > 0) {
        console.error(`\nFAIL (${failures.length} assertion(s) failed):`);
        failures.forEach((f) => console.error(" -", f));
        process.exit(1);
      }
      console.log("\nPASS");
      process.exit(0);
    })
    .catch((err) => {
      console.error("\n--- evidence (partial, run threw) ---");
      console.error(JSON.stringify(evidence, null, 2));
      console.error("\nFAIL (unhandled error):", err);
      process.exit(1);
    });
}
