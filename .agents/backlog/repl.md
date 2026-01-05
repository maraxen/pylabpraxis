# REPL Backlog

**Priority**: Medium
**Owner**: Full Stack
**Last Updated**: 2026-01-04

> ⚠️ **MIGRATION PLANNED**: The xterm.js REPL will be replaced with JupyterLite.
> See [repl_jupyterlite.md](./repl_jupyterlite.md) for the migration plan.

---

## 1. Status Overview

* **Backend**: Foundation complete (ReplSession, WebSocket). Auto-imports for PLR added.
* **Frontend**: xterm.js UI implemented. `PyodideConsole` integration complete.
* **Autocompletion**: UI implemented (Popup/Signature), but manual completion flaky in browser.

---

## 2. Outstanding Tasks

### 1. Autocompletion - ✅ MVP COMPLETE

* [x] Debug Browser Mode `Tab` key handling and Worker communication.
* [x] Implement Jedi-based autocompletion with rlcompleter fallback.
* [x] Common prefix completion for multiple matches.
* [x] Column-based display for completion list.

See [repl_autocompletion.md](./repl_autocompletion.md) for full autocompletion roadmap (Phase 2-5).

### 2. UI/UX Polish (NEW - High Priority)

These items are needed to make the REPL feel production-ready:

* [x] **Completion Popup UI**:
  * [x] Replace inline column display with floating popup menu
  * [x] Add keyboard navigation
  * [x] **Issue**: Manual verification shows flakiness despite passing E2E tests.

* [x] **Signature Help**:
  * [x] Show function signature popup when typing `(`
  * [x] Verified in E2E tests, needs manual confirmation.

* [ ] **Auto-scroll**: Ensure terminal always scrolls to bottom on new output.

* [x] **Split Streams**:
  * [x] Backend returns `output.type` as 'stdout' or 'stderr'
  * [x] Frontend styles applied (Red for stderr, default for stdout).

* [ ] **Copy/Paste**: Verify Ctrl+C/V works correctly in xterm.js.

* [ ] **Resize Handling**: Ensure terminal resizes correctly with window.

### 3. PLR Environment & Execution

* [x] **Integration with PLR Tooling**
  * [x] Ensure `await lh.setup()` works in browser shim.
  * [x] Verify `WebBridgeIO` routing.
  * [x] Ensure correct context (e.g. `LiquidHandler`, `Plate`) is available in REPL.
* [x] **Manual Autocomplete / Signature Help**
  * [x] Debug why `os.` + Tab works in test but fail in manual.
* [x] **Integration with PLR Tooling**
  * [x] Ensure `await lh.setup()` works in browser shim.
  * [x] Verify `WebBridgeIO` routing.
  * [x] Ensure correct context (e.g. `LiquidHandler`, `Plate`) is available in REPL.
* [x] **Manual Autocomplete / Signature Help**
  * [x] Debug why `os.` + Tab works in test but fail in manual.
  * [x] Verify popup positioning and Z-index within terminal container.
  * [x] Ensure `ngZone` change detection triggers for async worker responses.
* [x] **Resource/Machine Context**:
  * [x] Auto-import `LiquidHandler`, `Plate`, `TipRack` (via `web_bridge.py` bootstrap).

### 4. Advanced REPL Features

* [x] **Save to Protocol / Export (P3)**:
  * [x] Export REPL session as protocol file.
  * [x] Generate protocol code from session (via `/api/repl/save_session`).

* [x] **Menu Bar (P3)**:
  * [x] Implemented toolbar with Restart, Clear, Save Session, Toggle Variables.
  * [x] Keyboard accessibility for all REPL actions.

* [x] **Machine Availability Sidebar (P3)**:
  * [x] Backend `get_variables()` method added.
  * [x] WebSocket sends `VARS_UPDATE` on connect and after execution.
  * [x] Frontend sidebar displays connected machines and variables.

* [ ] **Protocol Decorator Specification (P4)**:
  * UI for specifying protocol decorator metadata from REPL.
  * Name, description, parameters, requirements.

### 5. Basic UI (COMPLETE)

* [x] **Command History**: Implement Up/Down arrow navigation.
* [x] **Clear Shortcut**: Implement `Ctrl+L` to clear terminal.
* [x] **Quick Access**: Toggle REPL with `Alt+` ` and Command Palette.
* [x] **Hardware Bridge**: REPL can control WebSerial devices via `WebBridgeIO`.

---

## 3. Related Backlogs

* [repl_autocompletion.md](./repl_autocompletion.md) - Detailed autocompletion phases
* [ui-ux.md](./ui-ux.md) - General UI polish items
