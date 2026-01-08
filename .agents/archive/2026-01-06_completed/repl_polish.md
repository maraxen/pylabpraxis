---
description: Improve stability and user experience of the JupyterLite REPL integration
---

# REPL Polish & Stability

**Issue:**
The JupyterLite REPL integration has several usability and stability issues reported by users:

1. **Inconsistent Loading:** Sometimes requires a page refresh or kernel restart on first load to function correctly.
2. **Theme Sync:** "Inconsistent light vs dark mode rendering" - likely the iframe not receiving or applying the theme change event correctly, or race conditions during initialization.
3. **Kernel Stability:** needing to restart kernel implies the initial boot might be hanging or failing to load dependencies (micropip/pylabrobot) in the correct order.

**Analysis:**

* **Loading/Kernel:**
  * The `JupyterLite` iframe initialization might be racing with the Angular component lifecycle.
  * `micropip` installation of `pylabrobot` might be failing silently or timing out.
  * The `BroadcastChannel` setup might be delayed.

* **Theme:**
  * JupyterLite has its own theming system. We need to ensure we're programmatically setting its theme to match the Angular app's theme (Material Dark/Light) via message passing or configuration.

**Tasks:**

* [ ] **Investigate Kernel Startup:**
  * Add logging to the boot sequence in `jupyterlite-repl.component.ts`.
  * Ensure `pylabrobot` wheel installation is retried or blocking until successful.
  * Check for race conditions in `BroadcastChannel` initialization.

* [ ] **Fix Theme Sync:**
  * Implement a message handler in the REPL (python/js side) to listen for theme changes from the main app.
  * Use `jupyterlab` theme manager API if accessible, or CSS overrides.

* [ ] **UI Feedback:**
  * Show a detailed "Initializing..." status with specific steps (e.g., "Booting Kernel", "Installing PyLabRobot", "Ready").
  * Add a "Restart Kernel" button in the Angular UI that sends the command to the iframe.

**Files Affected:**
* `praxis/web-client/src/app/features/repl/jupyterlite-repl.component.ts`
* `praxis/web-client/src/assets/jupyterlite/` (configuration/extensions)
