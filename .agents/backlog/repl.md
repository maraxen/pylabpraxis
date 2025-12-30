# REPL Backlog

**Priority**: Medium
**Owner**: Full Stack
**Last Updated**: 2025-12-30

---

## 1. Status Overview

* **Backend**: Foundation complete (ReplSession, WebSocket). Auto-imports for PLR added.
* **Frontend**: xterm.js UI implemented and integrated. Browser Mode (Pyodide) works for execution and stdout.
* **Issues**: Autocompletion (Browser Mode) is implemented but failing in verification.

---

## 2. Outstanding Tasks

### 1. Fix Autocompletion (Immediate)

* [x] Debug Browser Mode `Tab` key handling and Worker communication.
* [x] Ensure `rlcompleter` works in Pyodide or fallback to manual dictionary completion.

### 2. PLR Deep Integration (Next Step)

* [x] **Console Host Output**: Separate stream for "console" logs vs "inline" execution results.
* [ ] **Introspection**: `lh = LiquidHandler` should auto-fill arguments based on available backends. (Requires generic completer)
* [x] **Resource/Machine Context**:
  * [x] Auto-import `LiquidHandler`, `Plate`, `TipRack`.
  * [x] Pre-populate context with discovered machines (e.g., if a STAR is connected, `lh` should be pre-configured or easy to init).

### 3. UI Refinements

* [x] **Command History**: Implement Up/Down arrow navigation for previous commands.
* [x] **Clear Shortcut**: Implement `Ctrl+L` to clear the terminal window.
* [ ] **Auto-scroll**: Ensure terminal always scrolls to bottom on new output.
* [ ] **Split Streams**: Visually distinguish between `stdout` (logs), `stderr` (errors), and `return` values.
* [ ] **Signature Help**: Show function arguments/docstrings when typing `(` (Language Server Protocol lite).

### 4. Integration

* [x] **Quick Access**: Toggle REPL with `Alt+` ` (Backtick) and Command Palette.

* [x] **Hardware Bridge**: REPL can control WebSerial devices via `WebBridgeIO` (IO Layer Shimming - completed 2025-12-30).
