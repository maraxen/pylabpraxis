# Agent Prompt: WebSerial/WebUSB Builtins Fix

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed  
**Priority:** P1  
**Batch:** [260115](README.md)  
**Difficulty:** Hard  
**Dependencies:** I-02  
**Input Artifact:** `playground_inspection_findings.md`

---

## 1. The Task

Ensure `WebSerial` and `WebUSB` shims are correctly injected into the Pyodide `__builtins__`.

**Issue (Audit E.4):** Shims load but classes are not available in Python scope.

## 2. Implementation Steps

### Step 1: Debug Injection

- Check `generateBootstrapCode` or the shim JS files.
- Ensure `pyodide.globals.set('WebSerial', ...)` is actually called.
- Or ensuring the python shim module updates `__builtins__`.

### Step 2: Verification Script

- Create a test cell:

  ```python
  print(WebSerial)
  print(WebUSB)
  ```

- It should print the class representation, not raise `NameError`.

## 3. Constraints

- **Browser**: Must work in Chrome (WebSerial/WebUSB supported).

## 4. Verification Plan

- [x] Playground starts without errors.
- [x] `WebSerial` is available in global scope.

---

## On Completion

- [x] Update this prompt status to 🟢 Completed.
