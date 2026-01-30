# E2E Improvement Plan: Deck View Interaction

**Source Report**: `interactions-02-deck-view-report.md`  
**Test File**: `e2e/specs/interactions/02-deck-view.spec.ts`  
**Priority**: MEDIUM-HIGH (Score: 4.6/10 → Target: 8.0/10)

---

## Executive Summary

The Deck View Interaction tests verify real user behavior (click-to-inspect, hover-for-tooltip) but suffer from:
1. Brittle CSS selectors that will break on UI refactors
2. Missing worker-indexed database isolation for parallel safety
3. Duplicate setup code violating DRY
4. Shallow verification (presence-only, no data correctness)
5. Silent conditional assertions masking failures

This plan provides a four-phase remediation to elevate the test suite to Production Grade (8.0+).

---

## Phase 1: Infrastructure & Reliability (Priority: CRITICAL)

**Goal**: Eliminate parallel test flakiness and ensure consistent execution

### 1.1 Add Worker-Indexed Database Isolation

**Current Code** (Line 11-15):
```typescript
test.beforeEach(async ({ page }) => {
    const welcomePage = new WelcomePage(page);
    await welcomePage.goto();
    await welcomePage.handleSplashScreen();
});
```

**Target Code**:
```typescript
test.beforeEach(async ({ page }, testInfo) => {
    const welcomePage = new WelcomePage(page, testInfo);
    await welcomePage.goto();
    await welcomePage.handleSplashScreen();
});
```

**File Changes Required**:
- `welcome.page.ts`: Constructor must accept optional `testInfo`
- All subsequent page objects need `testInfo` propagation

### 1.2 Extract Shared Setup Fixture

**Create**: `e2e/fixtures/execution-ready.fixture.ts`

```typescript
import { test as base, expect } from '@playwright/test';
import { WelcomePage } from '../page-objects/welcome.page';
import { ProtocolPage } from '../page-objects/protocol.page';
import { WizardPage } from '../page-objects/wizard.page';
import { ExecutionMonitorPage } from '../page-objects/monitor.page';

type ExecutionReadyFixtures = {
    executionContext: {
        protocolPage: ProtocolPage;
        wizardPage: WizardPage;
        monitorPage: ExecutionMonitorPage;
    };
};

export const test = base.extend<ExecutionReadyFixtures>({
    executionContext: async ({ page }, use, testInfo) => {
        // Setup
        const welcomePage = new WelcomePage(page, testInfo);
        await welcomePage.goto();
        await welcomePage.handleSplashScreen();

        const protocolPage = new ProtocolPage(page, testInfo);
        const wizardPage = new WizardPage(page);
        const monitorPage = new ExecutionMonitorPage(page, testInfo);

        await protocolPage.goto();
        await protocolPage.ensureSimulationMode();
        await protocolPage.selectFirstProtocol();
        await protocolPage.continueFromSelection();

        await wizardPage.completeParameterStep();
        await wizardPage.selectFirstCompatibleMachine();
        await wizardPage.waitForAssetsAutoConfigured();
        await wizardPage.advanceDeckSetup();
        await wizardPage.openReviewStep();
        await wizardPage.startExecution();

        await monitorPage.waitForLiveDashboard();

        await use({ protocolPage, wizardPage, monitorPage });
        
        // Cleanup: None needed for read-only deck inspection
    }
});

export { expect };
```

### 1.3 Refactor Test to Use Fixture

```typescript
import { test, expect } from '../../fixtures/execution-ready.fixture';
import { DeckViewPage } from '../../page-objects/deck-view.page';

test.describe('Deck View Interaction', () => {
    test('should show resource details when clicking labware', async ({ page, executionContext }) => {
        const deckView = new DeckViewPage(page);
        
        const resource = await deckView.getFirstResource();
        await resource.click();
        
        await deckView.assertInspectorVisible();
        await deckView.assertInspectorShowsResource(resource);
    });
});
```

**Estimated Effort**: 4 hours  
**Risk Reduction**: HIGH (eliminates parallel flakiness)

---

## Phase 2: Page Object Refactor

**Goal**: Replace inline locators with semantic, maintainable POM methods

### 2.1 Create DeckViewPage Page Object

**Create**: `e2e/page-objects/deck-view.page.ts`

```typescript
import { Page, Locator, expect } from '@playwright/test';

export class DeckViewPage {
    private readonly page: Page;
    
    // Locators - prefer test IDs and ARIA roles
    private readonly resourceNodes: Locator;
    private readonly inspector: Locator;
    private readonly tooltip: Locator;
    
    constructor(page: Page) {
        this.page = page;
        
        // If test-ids are not available, use these patterns:
        this.resourceNodes = page.getByTestId('deck-resource').or(
            page.locator('.resource-node:not(.is-root)')
        );
        this.inspector = page.getByTestId('resource-inspector').or(
            page.locator('app-resource-inspector-panel')
        );
        this.tooltip = page.getByRole('tooltip').or(
            page.locator('.resource-tooltip')
        );
    }
    
    async getFirstResource(): Promise<DeckResource> {
        const node = this.resourceNodes.first();
        await expect(node).toBeVisible({ timeout: 15000 });
        return new DeckResource(this.page, node);
    }
    
    async getResources(): Promise<DeckResource[]> {
        const count = await this.resourceNodes.count();
        const resources: DeckResource[] = [];
        for (let i = 0; i < count; i++) {
            resources.push(new DeckResource(this.page, this.resourceNodes.nth(i)));
        }
        return resources;
    }
    
    async assertInspectorVisible(): Promise<void> {
        await expect(this.inspector).toBeVisible({ timeout: 10000 });
    }
    
    async assertInspectorShowsResource(resource: DeckResource): Promise<void> {
        const name = await resource.getName();
        expect(name, 'Resource name should be defined').toBeTruthy();
        await expect(this.inspector).toContainText(name!);
    }
    
    async assertTooltipVisible(): Promise<void> {
        await expect(this.tooltip).toBeVisible({ timeout: 5000 });
    }
    
    async assertTooltipShowsResource(resource: DeckResource): Promise<void> {
        const name = await resource.getName();
        expect(name, 'Resource name should be defined').toBeTruthy();
        const header = this.tooltip.locator('.tooltip-header, [data-testid="tooltip-title"]');
        await expect(header).toContainText(name!);
    }
    
    // Deep state verification
    async getInspectorData(): Promise<ResourceInspectorData | null> {
        return await this.page.evaluate(() => {
            const cmp = (window as any).ng?.getComponent(
                document.querySelector('app-resource-inspector-panel')
            );
            if (!cmp?.selectedResource) return null;
            return {
                id: cmp.selectedResource.id,
                name: cmp.selectedResource.name,
                type: cmp.selectedResource.type,
                slot: cmp.selectedResource.slot,
                contents: cmp.selectedResource.contents
            };
        });
    }
}

export class DeckResource {
    constructor(
        private readonly page: Page,
        private readonly locator: Locator
    ) {}
    
    async click(): Promise<void> {
        await this.locator.click();
    }
    
    async hover(): Promise<void> {
        await this.locator.hover();
    }
    
    async getName(): Promise<string | null> {
        return (
            await this.locator.getAttribute('data-resource-name') ||
            await this.locator.getAttribute('title')
        );
    }
    
    async getId(): Promise<string | null> {
        return await this.locator.getAttribute('data-resource-id');
    }
}

interface ResourceInspectorData {
    id: string;
    name: string;
    type: string;
    slot: string;
    contents?: unknown[];
}
```

### 2.2 Update Component Templates (Optional but Recommended)

Add test IDs to Angular templates for better test stability:

```html
<!-- deck-resource.component.html -->
<div 
    class="resource-node"
    [attr.data-testid]="'deck-resource-' + resource.id"
    [attr.data-resource-id]="resource.id"
    [attr.data-resource-name]="resource.name"
    [attr.data-resource-type]="resource.type">
    <!-- ... -->
</div>

<!-- resource-inspector-panel.component.html -->
<div data-testid="resource-inspector">
    <h2 data-testid="inspector-title">{{ selectedResource?.name }}</h2>
    <span data-testid="resource-type">{{ selectedResource?.type }}</span>
    <!-- ... -->
</div>
```

**Estimated Effort**: 6 hours  
**Maintainability Gain**: HIGH

---

## Phase 3: Domain Verification Enhancement

**Goal**: Transform from presence checks to deep state validation

### 3.1 Add Resource Type Verification

```typescript
test('should display correct resource type in inspector', async ({ page, executionContext }) => {
    const deckView = new DeckViewPage(page);
    const resource = await deckView.getFirstResource();
    
    await resource.click();
    await deckView.assertInspectorVisible();
    
    // Deep verification
    const inspectorData = await deckView.getInspectorData();
    expect(inspectorData).not.toBeNull();
    expect(inspectorData!.type).toMatch(/Plate|TipRack|Reservoir|Tube/i);
    expect(inspectorData!.slot).toBeTruthy();
});
```

### 3.2 Add Multi-Resource Selection Test

```typescript
test('should switch inspector content when clicking different resources', async ({ page, executionContext }) => {
    const deckView = new DeckViewPage(page);
    const resources = await deckView.getResources();
    
    expect(resources.length).toBeGreaterThan(1);
    
    // Click first resource
    await resources[0].click();
    await deckView.assertInspectorVisible();
    const firstData = await deckView.getInspectorData();
    
    // Click second resource
    await resources[1].click();
    const secondData = await deckView.getInspectorData();
    
    // Verify data switched
    expect(secondData!.id).not.toBe(firstData!.id);
});
```

### 3.3 Add State Correlation Test

```typescript
test('should correlate inspector data with simulation state', async ({ page, executionContext }) => {
    const deckView = new DeckViewPage(page);
    const resource = await deckView.getFirstResource();
    
    const resourceId = await resource.getId();
    await resource.click();
    
    const inspectorData = await deckView.getInspectorData();
    
    // Verify the inspector is showing data for the clicked resource
    expect(inspectorData!.id).toBe(resourceId);
    
    // Verify against simulation state
    const simulationState = await page.evaluate((id) => {
        const runService = (window as any).runService;
        const deck = runService?.currentRun?.deckState;
        return deck?.resources?.find((r: any) => r.id === id);
    }, resourceId);
    
    expect(simulationState).not.toBeNull();
    expect(inspectorData!.name).toBe(simulationState.name);
});
```

**Estimated Effort**: 4 hours  
**Coverage Gain**: HIGH

---

## Phase 4: Error State Coverage

**Goal**: Add negative test cases for robustness

### 4.1 Empty Deck Handling

```typescript
test('should show empty state when no resources on deck', async ({ page }, testInfo) => {
    // Use a protocol with no deck resources
    const welcomePage = new WelcomePage(page, testInfo);
    await welcomePage.goto();
    
    const protocolPage = new ProtocolPage(page, testInfo);
    await protocolPage.goto();
    await protocolPage.selectProtocolByName('Empty Deck Protocol');
    // ... setup ...
    
    const deckView = new DeckViewPage(page);
    const resources = await deckView.getResources();
    
    expect(resources.length).toBe(0);
    await expect(page.getByTestId('deck-empty-state')).toBeVisible();
});
```

### 4.2 Tooltip Timeout Handling

```typescript
test('should hide tooltip when mouse leaves resource', async ({ page, executionContext }) => {
    const deckView = new DeckViewPage(page);
    const resource = await deckView.getFirstResource();
    
    await resource.hover();
    await deckView.assertTooltipVisible();
    
    // Move mouse away
    await page.mouse.move(0, 0);
    
    await expect(page.locator('.resource-tooltip')).toBeHidden({ timeout: 2000 });
});
```

### 4.3 Inspector Persistence During Pause

```typescript
test('should maintain inspector state during execution pause', async ({ page, executionContext }) => {
    const deckView = new DeckViewPage(page);
    const { monitorPage } = executionContext;
    
    const resource = await deckView.getFirstResource();
    await resource.click();
    
    const dataBefore = await deckView.getInspectorData();
    
    // Pause execution
    await page.getByRole('button', { name: /Pause/i }).click();
    await expect(page.getByTestId('run-status')).toContainText(/Paused/i);
    
    // Inspector should still show same data
    const dataAfter = await deckView.getInspectorData();
    expect(dataAfter!.id).toBe(dataBefore!.id);
});
```

**Estimated Effort**: 3 hours  
**Robustness Gain**: MEDIUM

---

## Implementation Timeline

| Phase | Tasks | Effort | Dependency |
|-------|-------|--------|------------|
| **Phase 1** | DB isolation, fixture extraction | 4h | None |
| **Phase 2** | DeckViewPage POM, test refactor | 6h | Phase 1 |
| **Phase 3** | Deep state verification | 4h | Phase 2 |
| **Phase 4** | Error state tests | 3h | Phase 2 |

**Total Estimated Effort**: 17 hours  
**Target Score**: 8.0/10 (Production Grade)

---

## Test IDs Backlog (Component Changes)

These test IDs should be added to Angular components for optimal test stability:

| Component | Element | Test ID |
|-----------|---------|---------|
| `deck-view.component` | Resource node | `deck-resource-{id}` |
| `deck-view.component` | Root deck | `deck-root` |
| `resource-inspector-panel.component` | Container | `resource-inspector` |
| `resource-inspector-panel.component` | Title | `inspector-title` |
| `resource-inspector-panel.component` | Type badge | `resource-type` |
| `resource-inspector-panel.component` | Slot display | `resource-slot` |
| `resource-tooltip.component` | Container | `resource-tooltip` |
| `resource-tooltip.component` | Title | `tooltip-title` |

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Parallel Test Pass Rate | ~70% (estimated) | 99%+ |
| Selector Stability | LOW (CSS classes) | HIGH (test-ids) |
| State Verification Depth | SHALLOW (presence) | DEEP (data correlation) |
| Error State Coverage | 0% | 80%+ |
| Code Duplication | 100% (duplicated setup) | 0% (fixture) |
