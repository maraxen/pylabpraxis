# Agent Prompt: Playground Kernel Load Fix

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed  
**Priority:** P1  
**Batch:** [260115](README.md)  
**Difficulty:** High  
**Dependencies:** I-02  
**Input Artifact:** `playground_inspection_findings.md`

---

## 1. The Task

Resolve the regression where the Playground iframe/kernel fails to load on first attempt.

**Issue (Audit E.1):** Blank or no iframe on first load; requires "Restart Kernel".

## 2. Implementation Steps

### Step 1: Analyze Root Cause

- Refer to `playground_inspection_findings.md` for the diagnosed cause (likely race condition in `onIframeLoad` or Pyodide Init).

### Step 2: Fix Initialization Logic

- Ensure `buildJupyterliteUrl` happens at the correct lifecycle moment.
- Ensure the iframe `src` is set only after readiness checks.
- Implement a robust retry or "Ready" signal listener from the JupyterLite iframe.

## 3. Constraints

- **Reliability**: Must load 10/10 times on page refresh.

## 4. Verification Plan

- [x] Hard refresh page -> Kernel loads automatically.
- [x] Navigate away -> navigate back -> Kernel loads.

---

## On Completion

- [x] Update this prompt status to 🟢 Completed.
