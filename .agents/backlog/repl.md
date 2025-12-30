# REPL Backlog

**Priority**: Medium
**Owner**: Full Stack
**Last Updated**: 2025-12-30

---

## 1. Status Overview

* **Backend**: Foundation largely complete (Kernel, WebSocket, Execution).
* **Frontend**: UI exists but needs significant polish (Keyboard handling, scrolling, responsiveness).

---

## 2. Outstanding Tasks

### Frontend Terminal UI

- [ ] **Keyboard Events**:
  * Fix Up/Down arrow history navigation (currently buggy/unresponsive).
  * Implement standard terminal shortcuts (Ctrl+C, Ctrl+L).
* [ ] **Scrolling**:
  * Auto-scroll to bottom on new output.
  * User pause scrolling on scroll-up.
* [ ] **Visual Polish**:
  * Monospace font consistency.
  * Syntax highlighting for input/output.

### Backend Refinement

- [ ] **Session Isolation**: Ensure multiple browser tabs get distinct kernels (or shared if desired).
* [ ] **Context Injection**: Ensure `lh` (LiquidHandler), `tips`, `plates` are pre-injected into the namespace based on current state.

### Integration

- [ ] **Quick Access**: Toggle REPL from status bar or Command Palette (`Alt+` backtick?).
* [ ] **Hardware Bridge**: Ensure REPL can talk to discovered WebSerial devices.
