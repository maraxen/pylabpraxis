# Agent Prompt: WebSerial NameError Fix

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P1
**Batch:** [260114_frontend_feedback](./README.md)
**Difficulty:** 🟡 Medium
**Type:** 🔴 Bug Fix
**Dependencies:** None
**Backlog Reference:** [GROUP_E_playground_init.md](./GROUP_E_playground_init.md)

---

## 1. The Task

Fix the critical bug preventing the playground from initializing due to `NameError: name 'WebSerial' is not defined`.

**User Feedback:**

```
NameError: name 'WebSerial' is not defined
Traceback in Cell In[1], line 25: _ser.Serial = WebSerial
```

**Impact:** This bug blocks playground functionality entirely - P1 priority.

## 2. Technical Implementation Strategy

**Root Cause Hypothesis:**
The playground attempts to execute `_ser.Serial = WebSerial` in the Python environment, but `WebSerial` is not defined in the scope. This likely means the `web_serial_shim.py` is not being correctly imported or injected into the Pyodide worker's global namespace.

**Investigation Steps:**

1. **Check Worker Initialization:**
   - Review how `python.worker.ts` loads shims
   - Verify shim loading order

2. **Fix Injection:**
   - Ensure `WebSerial` class from `web_serial_shim.py` is made available in global scope
   - Options:
     - Add `from web_serial_shim import WebSerial` in startup script
     - Use `globals()['WebSerial'] = ...` pattern

3. **Verify Fix:**
   - Playground initialization should complete without `NameError`

## 3. Context & References

**Primary Files to Investigate/Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/assets/shims/web_serial_shim.py` | The shim implementation (verified to exist) |
| `praxis/web-client/src/app/core/services/python-runtime.service.ts` | Service managing the Python worker |
| `praxis/web-client/src/app/core/workers/python.worker.ts` | Pyodide worker initialization script |

**Reference Files:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/playground/` | Playground feature components |

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **Pyodide**: Do not modify core Pyodide setup unless necessary
- **Testing**: Must verify in browser mode

## 5. Verification Plan

**Definition of Done:**

1. Playground initializes without `NameError: name 'WebSerial' is not defined`
2. `WebSerial` is correctly instantiable in the Pyodide environment
3. No regressions in existing playground functionality

**Test Commands:**

```bash
cd praxis/web-client
npm run start:browser
# Navigate to /app/playground
# Verify no NameError in console
```

**Manual Verification:**

1. Open browser to `http://localhost:4200/app/playground`
2. Check browser console for errors
3. Verify playground REPL loads successfully
4. Execute a simple Python command to confirm environment works

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status
- [ ] Mark this prompt complete in batch README
- [ ] Set status in this document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `GROUP_E_playground_init.md` - Parent initiative
