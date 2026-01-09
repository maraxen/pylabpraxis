# Agent Prompt: 02_e2e_tests_asset_management

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started  
**Batch:** [260108](./README.md)  
**Backlog:** [quality_assurance.md](../../backlog/quality_assurance.md)  
**Priority:** P2

---

## Task

Implement Playwright E2E tests for Asset Management CRUD operations in Browser Mode.

---

## Implementation Steps

### 1. Create Page Object Models

Create POMs in `praxis/web-client/e2e/page-objects/`:

```typescript
// assets.page.ts
export class AssetsPage {
  constructor(private page: Page) {}
  
  async navigateToResources() { /* ... */ }
  async navigateToMachines() { /* ... */ }
  async openAddResourceDialog() { /* ... */ }
  async openAddMachineDialog() { /* ... */ }
  async selectCategory(category: string) { /* ... */ }
  async selectModel(model: string) { /* ... */ }
  async fillAssetName(name: string) { /* ... */ }
  async submitForm() { /* ... */ }
  async getAssetCards() { /* ... */ }
  async deleteAsset(name: string) { /* ... */ }
}
```

### 2. Implement Test Cases

Create `praxis/web-client/e2e/asset-management.spec.ts`:

| Test Case | Description |
|-----------|-------------|
| `should add a new resource` | Navigate to Resources, add resource via dialog, verify in list |
| `should add a new machine` | Navigate to Machines, add machine via dialog, verify in list |
| `should persist assets after reload` | Add asset, reload page, verify asset still exists |
| `should delete an asset` | Add asset, delete via menu, verify removed from list |
| `should filter assets by category` | Add assets, apply filter chip, verify filtered results |

### 3. Configure Playwright

Ensure `playwright.config.ts` is configured:

- `testDir: './e2e'`
- `baseURL: 'http://localhost:4200'`
- `webServer` block to start Angular dev server if needed

### 4. Run and Verify

```bash
cd praxis/web-client
npx playwright test asset-management.spec.ts --headed
```

---

## Context Files

| File | Purpose |
|:-----|:--------|
| [quality_assurance.md](../../backlog/quality_assurance.md) | Test tracking backlog |
| [playwright.config.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/playwright.config.ts) | Playwright configuration |
| [e2e/](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/e2e) | Existing E2E directory |
| [assets.component.ts](file:///Users/mar/Projects/pylabpraxis/praxis/web-client/src/app/features/assets/assets.component.ts) | Asset page component |

---

## Project Conventions

- **Commands**: Use `uv run` for Python, `npm` for frontend
- **E2E Tests**: `cd praxis/web-client && npx playwright test`

See [codestyles/typescript.md](../../codestyles/typescript.md) for conventions.

---

## On Completion

- [ ] Update [quality_assurance.md](../../backlog/quality_assurance.md) - mark E2E Asset Management complete
- [ ] Update [DEVELOPMENT_MATRIX.md](../../DEVELOPMENT_MATRIX.md)
- [ ] Mark this prompt complete in batch README

---

## References

- [.agents/README.md](../../README.md) - Environment overview
- [TECHNICAL_DEBT.md](../../TECHNICAL_DEBT.md) - Known issues
