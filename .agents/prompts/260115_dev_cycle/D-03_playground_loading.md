# Agent Prompt: Playground Loading Overlay

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed  
**Priority:** P2  
**Batch:** [260115](README.md)  
**Difficulty:** Medium  
**Dependencies:** I-02  
**Input Artifact:** `audit_notes_260114.md` (Section E.3)

---

## 1. The Task

Hide the raw Pyodide initialization text behind a polite loading overlay.

**Issue (Audit E.3):** User sees ugly init code. Previous overlay went infinite.

## 2. Implementation Steps

### Step 1: Create Overlay

- Simple `div` absolute positioned over iframe.
- Text: "Initializing Pyodide Environment..." + Spinner.

### Step 2: Auto-Close Logic

- Listen for specific "Ready" message from iframe (via `postMessage`).
- Implement a fallback timeout (e.g. 15s) to remove overlay if message is missed, preventing "infinite" loading state.

## 3. Constraints

- **UX**: Must fade out smoothly.

## 4. Verification Plan

- [x] Overlay appears on load.
- [x] Overlay vanishes when kernel is ready.
- [x] Overlay vanishes after timeout (test by breaking kernel).

---

## On Completion

- [x] Update this prompt status to 🟢 Completed.
