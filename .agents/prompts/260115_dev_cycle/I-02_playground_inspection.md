# Agent Prompt: Playground Regression Inspection

Examine `.agents/README.md` for development context.

**Status:** 🟢 Completed  
**Priority:** P1  
**Batch:** [260115](README.md)  
**Difficulty:** Hard  
**Dependencies:** None  
**Backlog Reference:** [audit_notes_260114.md](../../artifacts/audit_notes_260114.md) Section E

---

## 1. The Task

Investigate the playground regressions related to kernel loading, theme sync, and WebSerial/WebUSB availability. Document root causes and propose fixes.

**User-Reported Issues:**

- Blank or no iframe on first load; requires "Restart Kernel" click
- JupyterLite ignores app theme on startup
- WebSerial and WebUSB not available in Pyodide environment (shims load but not in builtins)
- Previous loading overlay attempt went infinite

**Goal:** Identify root causes with evidence (logs, code paths) and document in findings artifact.

## 2. Technical Inspection Strategy

### Step 1: Code Path Analysis

Review initialization flow in:

| File | Focus |
|:-----|:------|
| `playground.component.ts` | `buildJupyterliteUrl()`, `onIframeLoad()`, theme effect |
| `assets/jupyterlite/` | Pyodide kernel configuration |
| `assets/shims/web_serial_shim.py` | Shim content and exposure to builtins |
| `assets/shims/web_usb_shim.py` | Shim content and exposure to builtins |

### Step 2: Browser Console Investigation

Use browser agent to:

1. Navigate to `/app/playground`
2. Open DevTools Console
3. Capture all console output during initial load
4. Look for:
   - 404 errors for shim files
   - WebSerial/WebUSB injection logs
   - JupyterLite initialization logs
   - Theme-related messages

### Step 3: Pyodide Context Investigation

Inspect the bootstrap code in `generateBootstrapCode()`:

- Where is `WebSerial` expected to be defined?
- Is it added to `__builtins__`?
- Check if shims are executed before pylabrobot imports

### Step 4: Theme Sync Analysis

Trace the theme flow:

1. App theme signal in `AppStore`
2. Effect in `PlaygroundComponent`
3. URL parameter passed to JupyterLite
4. Verify JupyterLite respects `theme=` parameter on initial load

## 3. Output Artifact

Create `.agents/artifacts/playground_inspection_findings.md` with:

```markdown
# Playground Inspection Findings

## Summary
[Root causes identified for X issues]

## Kernel Load Regression

### Current Behavior
[Description with console logs]

### Root Cause
[Analysis]

### Proposed Fix
[Solution]

## Theme Sync Issue

### Current Behavior
[Description]

### Root Cause
[Analysis of URL parameter handling]

### Proposed Fix
[Solution]

## WebSerial/WebUSB Not Available

### Current Behavior
[Console errors, Python traceback if available]

### Shim Loading Analysis
[Are shims fetched? Are they executed?]

### Builtins Injection Analysis
[Is WebSerial added to __builtins__?]

### Root Cause
[Why is it failing]

### Proposed Fix
[Solution]

## Loading Overlay History

### Previous Attempt
[What was tried, why it went infinite]

### Proposed Robust Solution
[New approach]
```

## 4. Constraints & Conventions

- **Commands**: Use browser agent for live debugging.
- **Screenshots**: Capture console output as screenshots.
- **Frontend Path**: `praxis/web-client`

## 5. Verification Plan

**Definition of Done:**

1. `playground_inspection_findings.md` artifact created
2. Root cause identified for kernel load issue
3. Root cause identified for theme sync issue
4. Root cause identified for WebSerial/WebUSB issue
5. Console output captured as evidence

---

## On Completion

- [x] Create `.agents/artifacts/playground_inspection_findings.md`
- [x] Update this prompt status to 🟢 Completed
- [x] Update `HANDOVER_SUMMARY.md` with critical findings

---

## References

- `.agents/README.md` - Environment overview
- `.agents/artifacts/audit_notes_260114.md` - Source requirements
- `.agents/backlog/playground.md` - Existing playground context
