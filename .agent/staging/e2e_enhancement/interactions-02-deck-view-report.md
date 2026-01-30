# E2E Static Analysis Report: Deck View Interaction

**File Under Review**: `e2e/specs/interactions/02-deck-view.spec.ts`  
**Audit Date**: 2026-01-30  
**Auditor Role**: Senior SDET (Angular/Playwright Specialist)

---

## 1. Test Scope & Coverage

### What is Tested

This test file verifies **Deck View UI interactions** during a live protocol execution. Specifically:

| Test Case | Functionality Verified |
|-----------|----------------------|
| `should show resource details when clicking labware in Live View` | Clicking on labware resources in the deck visualization updates the Resource Inspector Panel |
| `should show tooltip when hovering over resources` | Hovering over deck resources triggers tooltip display with resource information |

**UI Elements Exercised**:
- `.resource-node:not(.is-root)` - Deck resource visualization nodes
- `app-resource-inspector-panel` - Resource details panel
- `.resource-tooltip` - Hover tooltip overlay
- `.tooltip-header` - Tooltip header content

**State Changes Verified**:
- Inspector panel visibility on click
- Inspector panel content update with resource name
- Tooltip visibility on hover
- Tooltip content population

### Key Assertions

| Assertion | Success Criteria |
|-----------|------------------|
| `expect(resourceNode).toBeVisible()` | At least one non-root resource node is visible in deck view |
| `expect(inspector).toBeVisible()` | Resource Inspector Panel appears after clicking a resource |
| `expect(inspector).toContainText(resourceName)` | Inspector panel displays the clicked resource's name |
| `expect(tooltip).toBeVisible()` | Tooltip appears within 5s of hovering |
| `expect(tooltip.locator('.tooltip-header')).toContainText(resourceName)` | Tooltip header matches hovered resource |

**Aggregate Score**: 5.0 / 10.0  
**Classification**: Functional Smoke (Unreliable/Shallow)

---

## 2. Code Review & Best Practices (Static Analysis)

### Critical Issues Identified

#### 2.1 Hardcoded CSS Selectors (Brittle)

**Severity**: HIGH  
**Lines**: 39, 46, 74, 79, 84

```typescript
// PROBLEM: Relies on internal CSS class names that may change
const resourceNode = page.locator('.resource-node:not(.is-root)').first();
const inspector = page.locator('app-resource-inspector-panel');
const tooltip = page.locator('.resource-tooltip');
```

**Issue**: These selectors use implementation-specific CSS classes (`.resource-node`, `.is-root`, `.resource-tooltip`, `.tooltip-header`) rather than semantic identifiers. Any CSS refactor, theming change, or component library update will break these tests.

**2026 Standard**: Use `data-testid` attributes or ARIA roles:
```typescript
// RECOMMENDED
const resourceNode = page.getByTestId('deck-resource-node').first();
const inspector = page.getByTestId('resource-inspector');
const tooltip = page.getByRole('tooltip');
```

#### 2.2 Reliance on `title` Attribute for Correlation

**Severity**: MEDIUM  
**Lines**: 42, 82

```typescript
const resourceName = await resourceNode.getAttribute('title');
```

**Issue**: The `title` attribute is presentation-focused and may not be a reliable unique identifier. If null/undefined, the assertions are skipped via the conditional check, masking potential failures.

**Better Pattern**:
```typescript
const resourceName = await resourceNode.getAttribute('data-resource-id') 
  || await resourceNode.getByTestId('resource-name').textContent();
```

#### 2.3 Long Static Timeouts

**Severity**: MEDIUM  
**Lines**: 40, 75, 80

```typescript
await expect(resourceNode).toBeVisible({ timeout: 20000 });
await expect(tooltip).toBeVisible({ timeout: 5000 });
```

**Issue**: While explicit timeouts are acceptable, 20,000ms for a resource node to appear after the live dashboard is ready is excessive. This may mask real performance regressions.

**Recommendation**: Use more aggressive timeouts (5-10s) and rely on proper prerequisite waits in `waitForLiveDashboard()`.

#### 2.4 No Worker-Indexed Database Isolation

**Severity**: HIGH  
**Lines**: 12-14 (beforeEach)

```typescript
test.beforeEach(async ({ page }) => {
    const welcomePage = new WelcomePage(page);
    await welcomePage.goto();
    await welcomePage.handleSplashScreen();
});
```

**Issue**: The `WelcomePage` is instantiated without `testInfo`, so the worker-indexed database isolation pattern (`dbName=praxis-worker-N`) is **not applied**. This means parallel test runs will contend on the same OPFS database, causing race conditions and flaky failures.

**Fix**: Pass `testInfo` to all page objects:
```typescript
test.beforeEach(async ({ page }, testInfo) => {
    const welcomePage = new WelcomePage(page, testInfo);
    // ...
});
```

#### 2.5 Duplicate Setup Code (DRY Violation)

**Severity**: LOW  
**Lines**: 17-35, 53-71

The entire "Prepare and launch execution" block is **duplicated verbatim** across both tests. This violates DRY and increases maintenance burden.

**Recommendation**: Extract to a shared fixture or helper:
```typescript
async function launchExecutionForDeckView(page: Page, testInfo: TestInfo) {
    const protocolPage = new ProtocolPage(page, testInfo);
    // ... setup steps
    await monitorPage.waitForLiveDashboard();
    return { protocolPage, wizardPage, monitorPage };
}
```

#### 2.6 Silent Conditional Assertions

**Severity**: MEDIUM  
**Lines**: 48-50, 83-85

```typescript
if (resourceName) {
    await expect(inspector).toContainText(resourceName);
}
```

**Issue**: If `resourceName` is `null`, the assertion is skipped entirely without warning. The test passes even though the critical verification didn't execute.

**Fix**: Fail fast if data is missing:
```typescript
expect(resourceName).toBeTruthy();
await expect(inspector).toContainText(resourceName!);
```

### Modern Standards Evaluation (2026)

| Standard | Compliance | Notes |
|----------|------------|-------|
| User-Facing Locators | ❌ FAIL | Uses CSS classes, not `getByRole`, `getByLabel`, `getByTestId` |
| Test Isolation | ⚠️ PARTIAL | Uses `beforeEach` but lacks worker-indexed DB isolation |
| POM Effectiveness | ✅ PASS | Leverages WelcomePage, ProtocolPage, WizardPage, ExecutionMonitorPage |
| Async Angular Handling | ✅ PASS | Uses POM methods that wait for service readiness |
| Parallel Safety | ❌ FAIL | No `testInfo` propagation for DB isolation |

---

## 3. Test Value & Classification

### Scenario Relevance

**User Journey Type**: Interactive Feedback (Real User Behavior)

This tests a real user scenario: during a live execution, users click on deck resources to view details and hover for quick information. This is a **valid interaction pattern** that users would perform.

**Criticality**: MEDIUM-HIGH
- The deck view is central to the execution monitoring experience
- Resource inspection is essential for troubleshooting and verification
- Tooltip feedback improves usability

### Classification

| Aspect | Classification |
|--------|---------------|
| **Test Type** | True E2E Test |
| **Integration Depth** | High (Full stack through execution) |
| **Mocking Level** | None visible - appears to use real/simulated execution |
| **Environment** | Browser mode with SQLite/Pyodide |

**Verdict**: This is a **True E2E Test** that exercises the full execution pipeline to reach the deck view interaction surface. However, it does not verify deep state (e.g., whether the correct resource data is displayed, only that *something* appears).

---

## 4. User Flow & Intent Reconstruction

### Reverse Engineered Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 1: Application Bootstrap                                     │
├─────────────────────────────────────────────────────────────────────┤
│  1. Navigate to root (/)                                            │
│  2. Handle splash screen (Skip or Get Started)                      │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 2: Protocol Configuration Wizard                             │
├─────────────────────────────────────────────────────────────────────┤
│  3. Navigate to /app/run                                            │
│  4. Enable Simulation mode                                          │
│  5. Select first available protocol                                 │
│  6. Continue to parameters step                                     │
│  7. Complete parameters (use defaults)                              │
│  8. Select simulation machine                                       │
│  9. Wait for assets auto-configuration                              │
│  10. Skip deck setup                                                │
│  11. Advance to Review & Run tab                                    │
│  12. Start Execution                                                │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  PHASE 3: Live Execution Monitoring                                 │
├─────────────────────────────────────────────────────────────────────┤
│  13. Wait for Live Dashboard to load                                │
│  14. Locate first resource node in deck view                        │
│  15. Click resource → Verify Inspector Panel opens with resource    │
│  --- OR ---                                                         │
│  15. Hover resource → Verify Tooltip appears with resource name     │
└─────────────────────────────────────────────────────────────────────┘
```

### Contextual Fit

The Deck View is a critical component in the Praxis ecosystem:

1. **Execution Context**: Users monitor live protocol runs via the deck visualization
2. **Resource Inspection**: Clicking resources reveals detailed properties (volumes, contents, status)
3. **Quick Feedback**: Tooltips provide summary information without panel navigation
4. **Machine Simulation**: This ties into the Pyodide/simulation stack for browser-mode execution

**Ecosystem Role**: This component bridges the abstract protocol execution with tangible deck state visualization, essential for debugging and verification during lab automation runs.

---

## 5. Gap Analysis (Scientific & State Logic)

### Missing Critical Paths

| Gap | Severity | Description |
|-----|----------|-------------|
| **No Deep State Verification** | HIGH | Tests only check that text *appears*, not that it's *correct* |
| **No Resource Type Validation** | HIGH | Doesn't verify what *kind* of resource (plate, tiprack, sample) |
| **No Multi-Resource Testing** | MEDIUM | Only tests `.first()` resource, not selection between multiple |
| **No Inspector Panel Content Depth** | HIGH | Doesn't verify volume, well contents, or metadata |
| **No State Synchronization Check** | MEDIUM | No verification that inspector data matches actual simulation state |
| **No Deselection/Re-selection** | LOW | Doesn't test clicking another resource to switch inspector |

### Domain-Specific Analysis

#### Data Integrity

**Issue**: The test does not validate that `praxis.db` loaded correctly or that the deck state reflects the actual protocol execution context.

**Gap**:
```typescript
// MISSING: Verify the resource data is scientifically correct
// e.g., that a 96-well plate has expected properties
const volume = await inspector.locator('[data-testid="resource-volume"]').textContent();
expect(parseFloat(volume)).toBeGreaterThan(0);
```

#### Simulation vs. Reality

**Status**: ✅ Partially Addressed

The test explicitly uses `ensureSimulationMode()`, so it's clear we're testing against a simulated machine. However:
- No verification that the simulation actually instantiated correctly
- No check that the deck layout matches expected simulation configuration

#### Serialization

**Issue**: Not applicable for this test.

This test is focused on UI interactions, not protocol argument serialization. Serialization verification should occur in the protocol execution tests, not here.

#### Error Handling

**Critical Gaps**:

| Missing Scenario | Impact |
|-----------------|--------|
| Click on disabled/locked resource | Should show different UI feedback |
| Click during execution pause | Should still update inspector |
| Click on resource that gets removed mid-execution | Graceful handling |
| Tooltip on resource with no metadata | Should show placeholder or minimal info |
| Network/OPFS failure during live view | Error boundary behavior |

### Recommended Additions

1. **Deep Property Verification**:
   ```typescript
   await expect(inspector.getByTestId('resource-type')).toContainText(/Plate|TipRack|Reservoir/i);
   await expect(inspector.getByTestId('resource-slot')).not.toBeEmpty();
   ```

2. **Multi-Resource Switching**:
   ```typescript
   const resources = page.locator('.resource-node:not(.is-root)');
   for (let i = 0; i < Math.min(3, await resources.count()); i++) {
       await resources.nth(i).click();
       await expect(inspector).toBeVisible();
   }
   ```

3. **State Correlation**:
   ```typescript
   // Verify inspector data matches simulation state
   const inspectorData = await page.evaluate(() => {
       const cmp = (window as any).ng?.getComponent(document.querySelector('app-resource-inspector-panel'));
       return cmp?.selectedResource;
   });
   expect(inspectorData.id).toBe(expectedResourceId);
   ```

---

## Summary Scores

| Category | Score | Rationale |
|----------|-------|-----------|
| **Test Scope** | 5/10 | Covers interaction surface but lacks depth |
| **Best Practices** | 4/10 | CSS selectors, no worker isolation, duplicate code |
| **Test Value** | 6/10 | Real user journey, but shallow verification |
| **Isolation** | 4/10 | No explicit cleanup, missing DB isolation |
| **Domain Coverage** | 4/10 | Very shallow domain verification |

**Aggregate**: **4.6 / 10.0** → **Functional Smoke (Unreliable/Shallow)**

---

## Next Steps

See the accompanying **Improvement Plan** document for a phased remediation approach:
- `interactions-02-deck-view-improvement-plan.md`
