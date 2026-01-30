# Senior SDET Review: `jupyterlite-bootstrap.spec.ts`

**File Under Review:** [`e2e/specs/jupyterlite-bootstrap.spec.ts`](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/jupyterlite-bootstrap.spec.ts)  
**Review Date:** 2026-01-30  
**Reviewer Role:** Senior SDET / Angular + Playwright Specialist  
**Baseline Score:** **5.5/10** (Functional Smoke)

---

## 1. Test Scope & Coverage

### What is Tested

| Verification Area | Covered? | Line(s) |
|-------------------|----------|---------|
| **Welcome Dialog Bypass** | ✅ | L11-22 |
| **JupyterLite Iframe Attachment** | ✅ | L24-29 |
| **Kernel Selection Dialog Suppression** | ✅ | L31-34 |
| **Angular Loading Overlay Dismissal** | ✅ | L36-39 |
| **Kernel Idle State Readiness** | ⚠️ (soft fail) | L55-65 |
| **Phase 1 Bootstrap: Pyodide Ready** | ✅ | L68-75 |
| **Phase 1 Bootstrap: WebSerial/USB Shims** | ✅ | L70-71 |
| **Kernel Execution: `print("hello world")`** | ✅ | L79-103 |
| **`pylabrobot` Import Validation** | ✅ | L105-124 |
| **Custom `web_bridge` Import Validation** | ✅ | L126-144 |

### Key Assertions (Success Criteria)

| Assertion | Purpose | Mode |
|-----------|---------|------|
| `expect(skipBtn).not.toBeVisible()` | Welcome dialog must NOT appear | Absence |
| `expect(jpKernelDialog).not.toBeVisible()` | Kernel selection dialog must NOT appear | Absence |
| `expect(frameElement).toBeVisible()` | JupyterLite iframe must attach | Presence |
| `expect(loadingOverlay).toBeHidden()` | Loading complete | Absence |
| `expect.poll(() => pyodideReady && shimsInjected)` | Bootstrap phase 1 completion | Polling |
| `expect.poll(() => log.includes('hello world'))` | Python code can execute | Polling |
| `expect.poll(() => log.includes('PLR v'))` | `pylabrobot` is importable | Polling |
| `expect.poll(() => log.includes('web_bridge: True'))` | `web_bridge` module works | Polling |
| `expect(pyodideReady).toBe(true)` | Final Pyodide check | Literal |
| `expect(shimsInjected).toBe(true)` | Final shim injection check | Literal |

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique: Brittle Patterns Identified

| Issue | Location | Severity | Details |
|-------|----------|----------|---------|
| **Hardcoded `waitForTimeout`** | L48 | 🔴 **Critical** | `page.waitForTimeout(500)` is an explicit race condition—should wait for a specific UI state instead. |
| **`force: true` Clicks** | L92, L114, L134 | 🔴 **Critical** | `codeInput.click({ force: true })` bypasses actionability checks—may click hidden or obstructed elements. This indicates the element is not properly actionable when the click is attempted. |
| **Loose Iframe Locator** | L24-27 | 🟡 **Medium** | `iframe.notebook-frame` is a CSS class, not a role or test ID. If styling changes, test breaks. |
| **Empty `catch` Blocks** | L50-52, L84-89, L107-112, L127-132 | 🟡 **Medium** | Silent swallowing of errors (`try { ... } catch { /* ignore */ }`) could mask real failures. Should at minimum log to test's console for trace visibility. |
| **No POM Usage** | Entire file | 🟡 **Medium** | No Page Object Model—direct DOM manipulation throughout. Zero encapsulation or reusability. |
| **No Test Isolation** | L17 | 🟡 **Medium** | Uses `resetdb=1` but lacks worker-indexed database (`dbName=praxis-worker-{index}`), limiting parallel execution. |
| **Deep JP Locators** | L32, L57, L80 | 🟡 **Medium** | `.jp-Dialog`, `.jp-mod-idle`, `.jp-CodeConsole-input .jp-InputArea-editor` are JupyterLite internal CSS classes—implementation details, not user-facing. |

### Modern Standards (2026) Evaluation

| Criterion | Status | Notes |
|-----------|--------|-------|
| **User-Facing Locators** | ⚠️ Partial | Uses `getByRole('button', {name: 'OK'})` ✅, but also uses deep CSS like `.jp-mod-idle` ❌. |
| **Web-First Assertions** | ⚠️ Partial | Uses `expect(locator).toBeVisible()` ✅, but also uses `expect.poll()` for console logs (necessary but less reliable than DOM). |
| **Test Isolation** | ❌ Missing | No `dbName=praxis-worker-{index}`. `resetdb=1` is a global reset, not worker-isolated. |
| **Cleanup** | ⚠️ None | Test does not clean up created state. Relies on `resetdb=1` only. |
| **Page Object Model** | ❌ None | Test is monolithic—no `JupyterPage` or `PlaygroundPage` POM. |
| **Async Angular Handling** | ⚠️ Partial | Waits for `.loading-overlay` to be hidden. No explicit Angular stability (`ng.getComponent`). |
| **No Hardcoded Waits** | ❌ Fails | Uses `waitForTimeout(500)` explicitly at L48. |

---

## 3. Test Value & Classification

### Scenario Relevance

| Question | Answer |
|----------|--------|
| **Is this a Critical User Journey?** | ✅ **Yes.** The JupyterLite REPL is the core execution environment for lab protocols. Zero-click kernel bootstrap is essential for every interactive user session. |
| **Happy Path or Edge Case?** | **Happy Path.** This verifies the ideal scenario: dialogs suppressed, kernel auto-started, bootstrap successful. |
| **Would a Real User Perform This?** | ✅ **Yes.** Every user who opens the Playground executes this flow implicitly. |

### Classification

| Category | Assessment |
|----------|------------|
| **True E2E Test?** | ⚠️ **Partially True E2E.** The test uses the real JupyterLite iframe, real Pyodide kernel, and real console logs—no mocking of the Python runtime or boot sequence. However, it does not verify network requests for `.whl` files, does not check OPFS/IndexedDB state, and uses `resetdb=1` which may not test a realistic cold-start scenario. |
| **Interactive Unit Test?** | ❌ No. This is not heavily mocked; it exercises the real integration. |
| **Integration Smoke Test?** | ✅ **Best fit.** It verifies the integration between Angular, JupyterLite, and Pyodide, but lacks deep state verification. |

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered User Workflow

Based **only on the test code**, the intended user experience is:

1. **User arrives at `/app/playground?mode=browser&resetdb=1`.**
   - The Welcome/Onboarding dialog should NOT appear (localStorage flags pre-set).
   
2. **JupyterLite iframe loads automatically.**
   - No kernel selection dialog should appear.
   - User simply waits for the loading overlay to clear.
   
3. **Kernel enters "Idle" state with zero clicks.**
   - Bootstrap logs indicate Pyodide is ready and shims are injected.
   
4. **User can immediately execute Python code.**
   - They type `print("hello world")` and see output.
   - They can `import pylabrobot` successfully.
   - They can access `web_bridge.request_user_interaction` for interactive protocols.

### Contextual Fit

The `PlaygroundComponent` is the **primary interface for hardware control scripting**:

- It hosts the JupyterLite REPL in an iframe.
- It uses `BroadcastChannel('praxis_repl')` for bidirectional communication.
- The **two-phase bootstrap** ensures a fast minimal boot (Phase 1), then sends the full payload (shims, wheel installation) after the kernel is alive (Phase 2).
- The `web_bridge` module enables Python code to trigger Angular dialogs (e.g., "Choose a tip rack").

This test is **foundational**—if bootstrap fails, **all downstream protocol execution is blocked**.

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Description | Risk |
|-----|-------------|------|
| **Phase 2 Bootstrap Verification** | Test only checks Phase 1 (`boot_ready`, shims injected). It does NOT verify the full optimized bootstrap payload was received and executed. No check for `"✓ Ready signal sent"` or `"✓ Asset injection ready"`. | If Phase 2 fails, users can type Python but cannot inject assets or use interactive protocols. |
| **Wheel Installation Verification** | Test imports `pylabrobot` but does NOT verify the `.whl` file was fetched successfully (no network interception checking for `200` on `pylabrobot-0.1.6-py3-none-any.whl`). | If the wheel is 404/corrupted, import may fail silently or produce incorrect behavior. |
| **Asset Injection Channel** | No test for `praxis:execute` messages or asset code injection via BroadcastChannel. | Core use case (clicking "Insert Asset" from inventory) is untested. |
| **Kernel Error Handling** | No test for Python syntax errors, exceptions, or uncaught rejections in the kernel. | User might see cryptic errors with no graceful fallback. |
| **Theme Toggling** | No test for dark/light theme switch mid-session. | JupyterLite may fail to re-render or lose state on theme change. |

### Domain-Specific Verification Gaps

| Domain Area | Covered? | Notes |
|-------------|----------|-------|
| **Data Integrity (`praxis.db`)** | ❌ Not Tested | Test uses `resetdb=1` but never verifies SQLite state or asset persistence. |
| **Simulation vs. Reality** | ⚠️ Unclear | Test uses `mode=browser` (browser mode), but does not explicitly test a simulated machine instantiation or hardware shim activation. |
| **Argument Serialization** | ❌ Not Tested | When a protocol is submitted, are its arguments correctly serialized and passed to Pyodide? This test does not cover protocol execution. |
| **Error States** | ❌ Not Tested | No tests for: invalid import, kernel crash, BroadcastChannel disconnection, or shim injection failure. |
| **OPFS/FS Persistence** | ❌ Not Tested | Test does not verify IndexedDB or OPFS state across kernel reloads. |

---

## Summary Scorecard

| Category | Score | Notes |
|----------|-------|-------|
| **Test Scope** | 6/10 | Covers happy path but misses Phase 2 and asset injection. |
| **Code Quality** | 4/10 | `force: true`, `waitForTimeout`, silent catches, no POM. |
| **Modern Standards** | 5/10 | Partial use of web-first assertions; no worker isolation. |
| **Domain Verification** | 4/10 | No wheel verification, no asset injection, no error states. |
| **True E2E Depth** | 7/10 | Real integration, real kernel, but lacks network/state checks. |

**Overall Baseline Score: 5.5/10 (Functional Smoke — passes in isolation, lacks reliability and deep verification)**

---

## Related Resources

- **KI Reference:** [Praxis Testing Knowledge > JupyterLite Integration](file:///Users/mar/.local/share/ov/profiles/fast-gemini-flash/.gemini/antigravity/knowledge/praxis_testing_knowledge/artifacts/implementation/jupyterlite_integration.md)
- **Service Implementation:** [PlaygroundJupyterliteService](file:///Users/mar/Projects/praxis/praxis/web-client/src/app/features/playground/services/playground-jupyterlite.service.ts)
- **Host Component:** [PlaygroundComponent](file:///Users/mar/Projects/praxis/praxis/web-client/src/app/features/playground/playground.component.ts)
