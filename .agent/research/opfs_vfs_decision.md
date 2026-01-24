# Decision Record: SQLite Wasm OPFS VFS Strategy

**Date:** 2026-01-23
**Status:** DECIDED
**Priority:** P1
**Task:** OPFS-1 (260123084756)

## 1. Executive Summary

For the Praxis application, we have decided to use the **`opfs-sahpool` (SyncAccessHandle Pool) VFS**.

This configuration offers the highest performance and the broadest deployment compatibility by avoiding the strict Cross-Origin Opener Policy (COOP) and Cross-Origin Embedder Policy (COEP) headers required by the standard `opfs` VFS. While `opfs-sahpool` requires running within a Web Worker and manages filenames opaquely, these constraints are acceptable trade-offs for the significant performance gains and deployment simplicity, especially for targets like GitHub Pages.

## 2. Option Analysis

### Option A: `opfs` VFS (Standard)

The standard `opfs` VFS bridges SQLite's synchronous I/O requirements with the browser's asynchronous OPFS API by using `SharedArrayBuffer` and `Atomics.wait`.

* **Mechanism:**
  * Proxies SQLite VFS calls from the Worker thread to an asynchronous "backend" (often the main thread or another worker).
  * Uses `Atomics.wait` on a `SharedArrayBuffer` to block the SQLite thread until the async operation completes.
* **Requirements:**
  * **Strict Security Context:** Requires `SharedArrayBuffer`, which mandates the presence of COOP/COEP headers.
  * **Web Worker:** Must run in a worker (main thread cannot be blocked by `Atomics.wait`).
* **Pros:**
  * Files stored in OPFS retain their user-assigned names (e.g., `my_db.sqlite` is actually stored as `my_db.sqlite`).
* **Cons:**
  * **Deployment Complexity:** COOP/COEP headers are "viral" and can break integration with third-party resources (CDNs, embedded iframes, OAuth popups) that do not explicitly opt-in to cross-origin isolation.
  * **Performance:** Significant overhead due to thread synchronization and proxying.

### Option B: `opfs-sahpool` VFS (Selected)

The `opfs-sahpool` VFS utilizes the `FileSystemSyncAccessHandle` API, which allows for direct, synchronous read/write access to OPFS files within a Worker.

* **Mechanism:**
  * Maintains a "pool" of open file handles.
  * Virtualizes filenames: SQLite might see `/praxis.db`, but the underlying OPFS file might be a randomized hash or ID.
* **Requirements:**
  * **Dedicated Web Worker:** `FileSystemSyncAccessHandle` is only exposed in dedicated workers.
* **Pros:**
  * **No COOP/COEP Headers:** Does *not* require cross-origin isolation.
  * **High Performance:** Direct, synchronous I/O generally outperforms the proxied `opfs` VFS.
  * **Broad Compatibility:** Supported by all major modern browsers.
  * **GitHub Pages Friendly:** Works on standard static hosts without custom header configuration.
* **Cons:**
  * **Opaque Storage:** Files on disk may not have human-readable names.
  * **Locking:** Strict exclusive locking; opening the DB in multiple tabs requires proxying through a single worker/tab.

## 3. Browser Compatibility Matrix

| Feature | Chrome | Firefox | Safari | Edge | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`opfs-sahpool`** | 108+ | 111+ | 16.4+ | 108+ | **Recommended.** Broad support in modern versions. |
| **`opfs` (VFS)** | 89+ | 79+ | 15.2+ | 79+ | Requires COOP/COEP. |

*Note: Safari 16.4 is the key baseline for reliable OPFS SyncAccessHandle support.*

## 4. COOP/COEP Implications

Using the standard `opfs` VFS requires the following HTTP Response Headers:

```http
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
```

Choosing `opfs-sahpool` allows us to avoid these headers, which is critical for **GitHub Pages** deployment where the user cannot configure server headers. This avoids breaking third-party CDNs and simplifies the deployment pipeline.

## 5. Implementation Plan

1. **Worker-First Architecture:** The database layer will be instantiated strictly within a Dedicated Web Worker (`sqlite-opfs.worker.ts`).
2. **Initialization:** Use the `installOpfsSAHPoolVfs` utility provided by `@sqlite.org/sqlite-wasm`.
3. **Migration:** On first run, detect the legacy IndexedDB database, export it, and import it into the `opfs-sahpool` VFS.
4. **Proxying:** The Main Thread will communicate with the Worker via a message protocol (handled by `SqliteOpfsService`).
