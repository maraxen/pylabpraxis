# SDET Static Analysis: screenshot_recon.spec.ts

**Target File:** [screenshot_recon.spec.ts](file:///Users/mar/Projects/praxis/praxis/web-client/e2e/specs/screenshot_recon.spec.ts)  
**Review Date:** 2026-01-30  
**Analyst:** Senior SDET & Angular Specialist  
**Lines of Code:** 56

---

## 1. Test Scope & Coverage

### What is Tested
This 56-line file is a **reconnaissance/debugging utility**, NOT a traditional test. It captures screenshots at each step of the Protocol Runner wizard for visual documentation and debugging purposes.

**Screenshots Captured (6 total):**
| Screenshot | Path | State Captured |
|------------|------|----------------|
| `step1_protocol_selection.png` | `/tmp/` | Initial Protocol Runner landing |
| `step1_protocol_selected.png` | `/tmp/` | After clicking first protocol card |
| `step2_parameters.png` | `/tmp/` | Parameter configuration step |
| `step3_machines.png` | `/tmp/` | Machine selection step |
| `step4_assets.png` | `/tmp/` | Asset assignment step |
| `step5_review.png` | `/tmp/` | Final review/deck step |

**UI Elements Interacted With:**
- **Heading**: `h1:has-text("Execute Protocol")` (waitForSelector)
- **Dialog**: Skip button via `getByRole('button', { name: /Skip for Now/i })`
- **Protocol Cards**: `app-protocol-card` Angular component selector
- **Navigation**: `getByRole('button', { name: /Continue/i })` used 4 times

**State Changes Observed:**
- Wizard step progression through 5 distinct steps (Selection → Parameters → Machines → Assets → Review)

### Assertions (Key Success Criteria)
| Assertion Type | Count | Location |
|----------------|-------|----------|
| `expect()` | **0** | - |
| `toBeVisible()` | **0** | - |
| `toHaveText()` | **0** | - |

**⚠️ CRITICAL: This file contains ZERO assertions.** The test will pass even if the application is completely broken, as long as `.click()` doesn't throw an exception.

---

## 2. Code Review & Best Practices (Static Analysis)

### Critique the Code

#### 🔴 CRITICAL: No Assertions (Lines 1-56)
```typescript
// No expect() statements anywhere in the file
// Only console.log() and page.screenshot() calls
```
**Impact:** This "test" produces no pass/fail result based on application behavior. All business logic validation is absent.

**Recommendation:** Add explicit assertions after each step transition to verify expected UI state.

#### 🔴 CRITICAL: Hardcoded URL with Port (Line 6)
```typescript
await page.goto('http://localhost:4200/app/run?mode=browser', { waitUntil: 'networkidle' });
```
**Issues:**
- Hardcodes `localhost:4200`, ignoring Playwright's `baseURL` config
- Will fail in CI environments or with different port configurations
- Uses absolute path, not relative (loses baseURL portability)

**Recommendation:** Use relative URL and let `playwright.config.ts` handle base:
```typescript
await page.goto('/app/run?mode=browser', { waitUntil: 'networkidle' });
```

#### 🔴 CRITICAL: Multiple Hardcoded `waitForTimeout` Calls (6 occurrences)
```typescript
// Line 16: await page.waitForTimeout(500);
// Line 31: await page.waitForTimeout(500);
// Line 37: await page.waitForTimeout(500);
// Line 42: await page.waitForTimeout(500);
// Line 47: await page.waitForTimeout(500);
// Line 52: await page.waitForTimeout(500);
```
**Issues:**
- 3 seconds of unconditional delays total
- Flaky in slow CI environments (too short)
- Wastes time in fast environments (too long)

**Recommendation:** Replace with state-driven waits:
```typescript
// Instead of: await page.waitForTimeout(500);
await expect(page.getByTestId('step-heading')).toBeVisible();
```

#### 🔴 CRITICAL: No Worker Isolation (Lines 4-55)
**Missing:**
- No `testInfo.workerIndex` for database isolation
- No `dbName` query parameter for parallel execution
- No `resetdb=1` to ensure clean state
- No use of `app.fixture.ts` or `worker-db.fixture.ts`

**Impact:** This test cannot run in parallel with other tests without database contention.

#### 🔴 CRITICAL: No Page Object Model Usage
All interactions are inline:
```typescript
await page.waitForSelector('h1:has-text("Execute Protocol")', { timeout: 30000 });
const firstCard = page.locator('app-protocol-card').first();
await page.getByRole('button', { name: /Continue/i }).click();
```

**Available POMs (not used):**
- `WizardPage` - Has methods for `completeParameterStep()`, `selectFirstCompatibleMachine()`, etc.
- `BasePage` - Has `goto()` with proper URL construction

#### 🟡 Medium: CSS Selector for Angular Component (Line 23)
```typescript
const protocolCount = await page.locator('app-protocol-card').count();
```
Using Angular component tag selectors is acceptable for internal components, but `getByTestId` would be more robust for refactoring.

#### 🟡 Medium: Legacy `waitForSelector` Usage (Line 9)
```typescript
await page.waitForSelector('h1:has-text("Execute Protocol")', { timeout: 30000 });
```
Modern Playwright prefers:
```typescript
await expect(page.getByRole('heading', { name: /Execute Protocol/i })).toBeVisible({ timeout: 30000 });
```

#### 🟢 Good: Proper Welcome Dialog Handling (Lines 12-17)
```typescript
const skipBtn = page.getByRole('button', { name: /Skip for Now/i });
if (await skipBtn.isVisible()) {
    console.log('Dismissing welcome dialog...');
    await skipBtn.click();
}
```
Uses ARIA role selector with graceful conditional handling.

### Modern Standards (2026) Evaluation

| Category | Rating | Evidence |
|----------|--------|----------|
| **User-Facing Locators** | 🟡 5/10 | Mix: `getByRole` for dialog, CSS for heading/cards |
| **Test Isolation** | 🔴 1/10 | No worker isolation, hardcoded URL |
| **Page Object Model** | 🔴 0/10 | Zero POM usage despite `WizardPage` existing |
| **Async Angular Handling** | 🔴 1/10 | `waitForTimeout` instead of state-driven waits |
| **Screenshot Strategy** | 🟡 4/10 | Hardcoded `/tmp/` paths, no visual regression framework |

---

## 3. Test Value & Classification

### Scenario Relevance
**Classification: Debugging Utility (Screenshot Reconnaissance)**

This is a **developer tool** intended for:
- Visual documentation of wizard UI state at each step
- Manual visual regression detection
- Understanding wizard flow during development

**NOT suitable for:**
- CI/CD gate testing (no assertions = always passes)
- Automated regression detection (no image comparisons)
- Production readiness validation (no state verification)

### Classification Matrix

| Dimension | Assessment |
|-----------|------------|
| **Happy Path Test** | ❌ No - Doesn't validate success |
| **Edge Case Test** | ❌ No - No edge cases tested |
| **True E2E Test** | ❌ No - No backend/state integration |
| **Interactive Unit Test** | ❌ No - No component isolation |
| **Utility Script** | ✅ Yes |

**Verdict:** This file should be reclassified as a **utility script**, not a test:
1. Rename to `screenshot_recon.util.ts` or move to `e2e/utils/`
2. Exclude from CI test runs via `playwright.config.ts`
3. OR convert to proper visual regression test with Percy/Argos integration

---

## 4. User Flow & Intent Reconstruction

### Reverse-Engineered Workflow
```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Navigate to /app/run?mode=browser                            │
│    └─ Wait for networkidle + "Execute Protocol" heading         │
├─────────────────────────────────────────────────────────────────┤
│ 2. Dismiss Welcome Dialog (if present)                          │
│    └─ Click "Skip for Now" button                               │
├─────────────────────────────────────────────────────────────────┤
│ 3. Screenshot: Protocol Selection (step1_protocol_selection)    │
├─────────────────────────────────────────────────────────────────┤
│ 4. Select First Protocol Card                                   │
│    └─ Wait 500ms                                                │
│    └─ Screenshot: Protocol Selected (step1_protocol_selected)  │
├─────────────────────────────────────────────────────────────────┤
│ 5. Click "Continue" → Parameters Step                           │
│    └─ Wait 500ms                                                │
│    └─ Screenshot: Parameters (step2_parameters)                 │
├─────────────────────────────────────────────────────────────────┤
│ 6. Click "Continue" → Machines Step                             │
│    └─ Wait 500ms                                                │
│    └─ Screenshot: Machines (step3_machines)                     │
├─────────────────────────────────────────────────────────────────┤
│ 7. Click "Continue" → Assets Step                               │
│    └─ Wait 500ms                                                │
│    └─ Screenshot: Assets (step4_assets)                         │
├─────────────────────────────────────────────────────────────────┤
│ 8. Click "Continue" → Review/Deck Step                          │
│    └─ Wait 500ms                                                │
│    └─ Screenshot: Review (step5_review)                         │
└─────────────────────────────────────────────────────────────────┘
```

### Contextual Fit in Application Ecosystem
**Protocol Runner Wizard** is a core feature component:
- **Entry Point:** `/app/run` route with `mode=browser` query param
- **Component:** `app-run-protocol` (Angular standalone component)
- **Steps:** Uses Material Horizontal Stepper for multi-step configuration
- **Purpose:** Configure and launch lab automation protocol executions

**Related Components:**
- `WizardPage` (POM) - Encapsulates wizard step interactions
- `ProtocolPage` (POM) - Protocol selection and configuration
- `AssetPage` (POM) - Asset management and selection
- `MonitorPage` (POM) - Post-execution monitoring

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths
Since this is a utility script, gaps are framed as "what it should become":

| Gap Category | Current State | Required State |
|--------------|---------------|----------------|
| **Wizard Step Validation** | None | Assert each step heading/content |
| **Protocol Selection Verification** | None | Assert selected protocol name/id |
| **Form State Validation** | None | Assert required fields, validation state |
| **Data Persistence** | None | Verify SQLite/Pyodide state changes |
| **Error Handling** | None | Handle/assert on missing protocols |

### Domain-Specific Coverage

#### Data Integrity (`praxis.db` Loading/Parsing)
| Aspect | Coverage | Gap |
|--------|----------|-----|
| DB Load/Init | 🔴 None | Not waiting for `sqliteService.isReady$` |
| Protocol List Query | 🔴 None | Not verifying protocol source |
| Selection Persistence | 🔴 None | Not checking form state saved |

**Required Verification:**
```typescript
// After protocol selection
await page.evaluate(async () => {
    const ng = (window as any).ng;
    const component = ng.getComponent(document.querySelector('app-run-protocol'));
    return component.selectedProtocol?.name;
});
```

#### Simulation vs. Reality (Environment Instantiation)
| Aspect | Coverage | Notes |
|--------|----------|-------|
| Machine Mode | ⚪ N/A | Uses `mode=browser` but doesn't verify |
| Simulation State | ⚪ N/A | Doesn't interact with machine step |

**Gap:** Doesn't verify whether simulated or real machine environments are configured.

#### Serialization (Pyodide Worker Communication)
| Aspect | Coverage | Gap |
|--------|----------|-----|
| Argument Serialization | 🔴 None | Never reaches execution |
| Worker Communication | 🔴 None | No `postMessage` verification |

**Impact:** Wizard screenshots captured, but no verification of data flow to execution engine.

#### Error Handling (Failure States)
| Scenario | Coverage | Gap |
|----------|----------|-----|
| Invalid/Missing DB | 🔴 None | No error UI handling |
| Python Syntax Error | 🔴 None | Doesn't reach execution |
| Empty Protocol List | 🟡 Partial | Conditional branch exists but not tested |
| Network Failure | 🔴 None | No offline handling |

**Positive Note (Line 26-54):**
```typescript
if (protocolCount > 0) {
    // ... proceed with workflow
}
```
The code does handle the "no protocols" edge case by skipping interaction, but there's no assertion that this is an expected state.

---

## Summary Scorecard

| Category | Score | Evidence |
|----------|-------|----------|
| **Test Scope** | 1/10 | Zero assertions, screenshot capture only |
| **Best Practices** | 1/10 | Hardcoded URLs, 6x waitForTimeout, no POM |
| **Test Value** | 2/10 | Useful for debugging, not CI gate |
| **Isolation** | 1/10 | No worker isolation, shared state |
| **Domain Coverage** | 0/10 | Zero SQLite/Pyodide verification |

**Aggregate Score: 1.0/10 🔴 Critical Failure**

---

## Recommendation

**Primary Action: RECLASSIFY OR ENHANCE**

### Option A: Reclassify as Utility (Minimal Effort)
1. Rename file to `screenshot_recon.util.ts`
2. Move to `e2e/utils/` directory
3. Add to `playwright.config.ts` `testIgnore` patterns:
   ```typescript
   testIgnore: ['**/utils/**']
   ```
4. Document as manual debugging tool

### Option B: Convert to Visual Regression Test (Medium Effort)
1. Integrate with Percy, Argos, or Playwright's built-in visual comparison
2. Add baseline assertions for each screenshot
3. Configure CI workflow for visual diff review

### Option C: Convert to Full E2E Test (High Effort)
1. Use `WizardPage` POM for interactions
2. Add state assertions at each wizard step
3. Integrate worker isolation via `app.fixture.ts`
4. Verify SQLite persistence and form state

---

## Immediate Actions Required

| Priority | Action | Effort |
|----------|--------|--------|
| 🔴 P0 | Add `.skip` to exclude from CI | 5 min |
| 🔴 P0 | Remove hardcoded `localhost:4200` | 5 min |
| 🟡 P1 | Replace 6x `waitForTimeout` with state waits | 30 min |
| 🟡 P1 | Migrate to `WizardPage` POM methods | 45 min |
| 🟢 P2 | Add basic assertions per step | 1 hour |
| 🟢 P2 | Integrate visual regression framework | 2+ hours |
