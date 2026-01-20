# Status: Complete
# Asset Wizard Component & Unification Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal**: Unify asset creation into a single `AssetWizardComponent` to replace disparate dialogs (`AddAssetDialog`, `MachineDialog`, `InventoryDialog`).

**Architecture Strategy**:
1.  **Consolidation**: Deprecate existing dialogs. Replace with `AssetWizardComponent`.
2.  **Wizard Steps**:
    1.  **Type/Category**: Select Machine vs Resource, then Category (e.g., Liquid Handler). Filter out "Unknown" or raw backend types.
    2.  **Definition**: Searchable grid of definitions. Show "Frontend" name (User facing). Chips for metadata.
    3.  **Config**:
        -   If Machine: Backend selection (Simulated vs Real), Connection settings (Serial Port).
        -   If Resource: Labware type specifics.
    4.  **Review**: Summary before creation.
3.  **Strict Mode**:
    -   Inventory List must ONLY show "Frontend" assets.
    -   Raw backends (Chatterbox, etc.) should be hidden or shown as details of the frontend machine.

**Tech Stack**: Angular (Standalone Components, MatStepper), SqliteService, AssetService, Playwright.

---

**Current Status (Jan 19, 2026):**
- The `AssetWizardComponent` is fully implemented and integrated.
- Tasks 1-4 are complete.
- Task 5 (Verification) is complete.

### Task 1: Wizard Skeleton & Type Selection (Completed)

**Files:**
- Create: `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.component.ts`
- Create: `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.component.html`
- Create: `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.component.scss`
- Test: `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.component.spec.ts`

**Step 1: Write the skeleton test**

```typescript
// asset-wizard.component.spec.ts
describe('AssetWizardComponent', () => {
  it('should create', () => {
    // Basic creation test
  });
  it('should initialize with step 1: Type Selection', () => {
     // Verify stepper is present and starts at step 1
  });
});
```

**Step 2: Run test to verify it fails**

Run: `uv run ng test --include src/app/shared/components/asset-wizard/asset-wizard.component.spec.ts`
Expected: FAIL (Component doesn't exist)

**Step 3: Implement Skeleton & Step 1**

- Create standalone `AssetWizardComponent` with `MatStepperModule`.
- Implement Step 1:
  - Two big cards/buttons: "Machine" vs "Resource".
  - On selection, show `mat-select` or `mat-chip-list` for Categories (fetched from `AssetService.getFacets()`).
  - Filter out "Unknown" types.

**Step 4: Run test to verify it passes**

Run: `uv run ng test --include src/app/shared/components/asset-wizard/asset-wizard.component.spec.ts`
Expected: PASS

**Step 5: Commit**

```bash
git add praxis/web-client/src/app/shared/components/asset-wizard/
git commit -m "feat: add AssetWizardComponent skeleton and step 1"
```

### Task 2: Definition Selection & Search (Completed)

**Files:**
- Modify: `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.component.ts`
- Modify: `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.component.html`
- Test: `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.component.spec.ts`

**Step 1: Write test for Step 2**

```typescript
it('should load definitions based on selected category', () => {
  // Mock SqliteService/AssetService
  // Simulate category selection
  // Expect definition grid to be populated
});
```

**Step 2: Implement Step 2 UI**

- Add Step 2 to Stepper.
- Searchable Grid (or List) of definitions.
- Columns/Cards: "Name" (Frontend Name), "Description", "Tags".
- Logic:
  - Query `SqliteService` (or `AssetService`) for definitions matching the selected category.
  - Filter out raw backends.

**Step 3: Verify**

Run: `uv run ng test --include src/app/shared/components/asset-wizard/asset-wizard.component.spec.ts`

**Step 4: Commit**

```bash
git add praxis/web-client/src/app/shared/components/asset-wizard/
git commit -m "feat: implement asset wizard step 2 definition search"
```

### Task 3: Configuration & Backend Selection (Completed)

**Files:**
- Modify: `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.component.ts`
- Modify: `praxis/web-client/src/app/shared/components/asset-wizard/asset-wizard.component.html`

**Step 1: Write test for Step 3**

```typescript
it('should show backend config if machine is selected', () => {
  // ...
});
```

**Step 2: Implement Step 3 UI**

- Condition: If `type === 'Machine'`:
  - Show "Backend Implementation" dropdown (e.g., "Simulated", "Real Device via Serial").
  - Default to "Simulated" or "Chatterbox" (browser-compatible).
  - If "Real Device" selected, show inputs for `port`, `baudRate`, etc.
- Condition: If `type === 'Resource'`:
  - Show Labware specifics (if any).

**Step 3: Implement Step 4 (Review)**

- Simple summary screen showing all selections.
- "Create" button calls `AssetService.createAsset(...)`.

**Step 4: Verify**

Run: `uv run ng test --include src/app/shared/components/asset-wizard/asset-wizard.component.spec.ts`

**Step 5: Commit**

```bash
git add praxis/web-client/src/app/shared/components/asset-wizard/
git commit -m "feat: implement asset wizard step 3 config and step 4 review"
```

### Task 4: Integration (Completed)

**Files:**
- Modify: `praxis/web-client/src/app/features/assets/assets.component.ts` (Inventory)
- Modify: `praxis/web-client/src/app/features/playground/playground.component.ts`
- Delete: `praxis/web-client/src/app/shared/dialogs/add-asset-dialog/`
- Delete: `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts` (or deprecate)

**Step 1: Replace in AssetsComponent**

- Change "Add Asset" button to open `AssetWizardComponent`.
- Ensure strict mode: Filter the inventory list to hide raw backends.

**Step 2: Replace in Playground**

- Replace `InventoryDialog` usage with `AssetWizardComponent` (or wrap it if needed, but aim for direct usage).

**Step 3: Cleanup**

- Remove `AddAssetDialogComponent`.
- Remove/Deprecate `MachineDialogComponent` and `InventoryDialogComponent`.

**Step 4: Commit**

```bash
git add praxis/web-client/src/app/features/
git rm praxis/web-client/src/app/shared/dialogs/add-asset-dialog/
git commit -m "refactor: replace old dialogs with AssetWizardComponent"
```

### Task 5: Verification (The "Gold Standard") (Completed)

**Files:**
- Create: `praxis/web-client/e2e/specs/asset-wizard.spec.ts`

**Step 1: Create Playwright Test**

```typescript
test('Asset Wizard E2E Flow', async ({ page }) => {
  // 1. Open Wizard
  // 2. Select 'Liquid Handler' -> 'STAR'
  // 3. Select 'Simulated'
  // 4. Create
  // 5. Verify asset appears in list
  // 6. Screenshot at each step
});
```

**Step 2: Run Verification**

Run: `npx playwright test e2e/specs/asset-wizard.spec.ts`

**Step 3: Multimodal Check**

- Use `multimodal-looker` (if available via skill) or manual review of screenshots to ensure UI polish.
- Verify: No "Unknown" types, clean alignment, chips visible.

**Step 4: Commit**

```bash
git add praxis/web-client/e2e/specs/asset-wizard.spec.ts
git commit -m "test: add e2e verification for asset wizard"
```

### Status Update
- Confirmed Wizard implementation works.
- Confirmed E2E test runs (note the fix in `BrowserMockRouter`).
- Screenshots captured.

**This marks the completion of Phase 2.**

