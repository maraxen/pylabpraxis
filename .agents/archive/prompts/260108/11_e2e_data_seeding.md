# Agent Prompt: 11_e2e_data_seeding

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260108](./README.md)  
**Backlog:** [quality_assurance.md](../../backlog/quality_assurance.md)  
**Priority:** P2

---

## Task

Implement database seeding for Playwright E2E tests so that Asset Management CRUD tests can run without relying on browser-mode discovery/sync.

---

## Problem Statement

E2E tests for asset creation fail because:

- The browser-mode database isn't pre-populated with resource/machine definitions
- Discovery sync may not complete before tests run
- Tests need known type definitions to select from

---

## Implementation Steps

### 1. Create Seed Data Script

Create `praxis/web-client/e2e/fixtures/seed-data.ts`:

```typescript
// Pre-defined resource and machine type definitions
export const SEED_RESOURCES = [
  { name: 'Corning 96 Well Plate', category: 'plate', ... },
  { name: 'Hamilton Core96 Tip Rack', category: 'tip_rack', ... },
];

export const SEED_MACHINES = [
  { name: 'Hamilton STAR', category: 'liquid_handler', ... },
  { name: 'BMG CLARIOstar', category: 'plate_reader', ... },
];
```

### 2. Implement Global Setup

Create `praxis/web-client/e2e/global-setup.ts`:

```typescript
import { chromium } from '@playwright/test';

export default async function globalSetup() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  // Navigate to app and wait for IndexedDB initialization
  await page.goto('http://localhost:4200');
  await page.waitForSelector('[data-ready="true"]');  // or similar signal
  
  // Seed data via browser console or SQLite injection
  await page.evaluate(async (seedData) => {
    // Insert into IndexedDB/SqliteService
  }, { resources: SEED_RESOURCES, machines: SEED_MACHINES });
  
  await browser.close();
}
```

### 3. Update Playwright Config

```typescript
// playwright.config.ts
export default defineConfig({
  globalSetup: require.resolve('./e2e/global-setup'),
  // ...
});
```

### 4. Alternative: Wait for Discovery

If seeding is too complex, implement "wait for ready" in test setup:

```typescript
test.beforeAll(async ({ page }) => {
  await page.goto('/settings');
  await page.click('text=Sync Definitions');
  await page.waitForSelector('text=Sync complete');
});
```

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [quality_assurance.md](../../backlog/quality_assurance.md) | Backlog tracking |
| [playwright.config.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/playwright.config.ts) | Playwright config |
| [e2e/](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/e2e/) | E2E test directory |

---

## Project Conventions

- **E2E Tests**: `cd praxis/web-client && npx playwright test`

See [codestyles/typescript.md](../../codestyles/typescript.md) for conventions.

---

## On Completion

- [ ] Commit changes with message: `test(e2e): implement database seeding for Playwright tests`
- [ ] Update [quality_assurance.md](../../backlog/quality_assurance.md) - mark E2E Data Seeding complete
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
