# Agent Prompt: Backend Selector UX - Disable Unless Category Selected

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260109](./README.md)
**Backlog Reference:** [asset_management.md](../../backlog/asset_management.md)

---

## 1. The Task

The backend selector in the Machine Dialog workflow should be disabled (or hidden) until a machine category/type is selected. Currently, users can potentially navigate to the backend step without first selecting a machine type, which doesn't make sense UX-wise.

The backlog suggests either:

1. Disable backend step unless category selected, OR
2. Convert to autocomplete for better UX

The current implementation already uses a stepper pattern, but we should ensure the "Next" button properly gates progression.

**User Value:** Clearer step-by-step workflow prevents user confusion and reduces errors in machine configuration.

---

## 2. Technical Implementation Strategy

### Architecture

**Component:** `MachineDialogComponent`

- Located at: `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts`

### Current Implementation Analysis

The dialog uses a 3-step stepper:

1. **Machine Type** (Step 0) - Select frontend type (Liquid Handler, Plate Reader, etc.)
2. **Backend** (Step 1) - Select backend implementation
3. **Configuration** (Step 2) - Enter instance details

**Current gating logic (lines 530-534):**

```typescript
canProceed(): boolean {
  if (this.currentStep === 0) return !!this.selectedFrontendFqn;
  if (this.currentStep === 1) return !!this.selectedDefinition;
  if (this.currentStep === 2) return !!this.form.get('name')?.valid;
  return false;
}
```

This already gates Step 0 → Step 1 transition on `selectedFrontendFqn`. The "Next" button uses:

```html
<button mat-flat-button color="primary"
  [disabled]="!canProceed()"
  (click)="nextStep()">
  Next
</button>
```

### Issue Clarification Needed

The current implementation appears correct. The issue may be:

1. **Visual feedback**: Backend step should show "Select a machine type first" if somehow accessed without selection
2. **Stepper header clicks**: Clicking step 2 header directly might bypass gate
3. **Empty state**: Backend list shows "No backends available" but should clarify WHY

### Proposed Enhancement

Add defensive UI in Backend step (Step 1):

```html
@if (currentStep === 1) {
  <div class="fade-in flex flex-col gap-4">
    @if (!selectedFrontendFqn) {
      <div class="muted-box text-center py-8">
        <mat-icon class="!text-4xl mb-2">arrow_back</mat-icon>
        <p>Please select a machine type first</p>
      </div>
    } @else {
      <!-- existing backend selection UI -->
    }
  </div>
}
```

Also ensure stepper doesn't allow jumping:

```html
<mat-stepper #stepper [linear]="true" ...>
```

The `[linear]="true"` should already prevent step jumping, but verify.

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts` | Add defensive UI and verify linear stepper |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts` | Similar stepper pattern for reference |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular commands
- **Frontend Path**: `praxis/web-client`
- **Styling**: Use existing component styles (`.muted-box` class)
- **Stepper**: Angular Material `mat-stepper` with `[linear]="true"`

---

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors:

   ```bash
   cd praxis/web-client && npm run build
   ```

2. Linear stepper verification:
   - Navigate to Assets → Machines → Add Machine
   - Verify cannot click on Step 2 header before completing Step 1
   - Verify cannot click on Step 3 header before completing Step 2
   - Stepper should be strictly linear

3. Next button gating:
   - Step 1: "Next" disabled until machine type selected
   - Step 2: "Next" disabled until backend selected
   - Step 3: "Finish" disabled until name is valid

4. Edge case:
   - If somehow on Step 2 without Step 1 selection, show helpful message
   - Back button should work correctly

---

## On Completion

- [ ] Commit changes with message: `feat(assets): enforce linear flow in machine dialog stepper`
- [ ] Update backlog item status in [asset_management.md](../../backlog/asset_management.md)
- [ ] Mark this prompt complete in batch README, update DEVELOPMENT_MATRIX.md if applicable, and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- [Angular Material Stepper](https://material.angular.io/components/stepper/overview) - Linear stepper docs
