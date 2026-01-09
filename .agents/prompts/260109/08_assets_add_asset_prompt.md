# Agent Prompt: Add Asset Prompt - Machine vs Resource Choice

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260109](./README.md)
**Backlog Reference:** [asset_management.md](../../backlog/asset_management.md)

---

## 1. The Task

When clicking "Add Asset" from the Overview or Spatial View tabs in Asset Management, the dialog should first prompt whether the user wants to add a **Machine** or a **Resource**, rather than defaulting directly to Add Machine.

Currently, `openAddAsset()` in `AssetsComponent` defaults to opening `MachineDialogComponent` when on Overview tab (index 0) or Spatial tab (index 1).

**User Value:** Users can quickly add either asset type from any view without having to navigate to the specific tab first.

---

## 2. Technical Implementation Strategy

### Architecture

**Component:** `AssetsComponent`

- Located at: `praxis/web-client/src/app/features/assets/assets.component.ts`

**Current Implementation (lines 301-319):**

The current code has **incorrect tab index comments** and buggy behavior:

```typescript
openAddAsset() {
  if (this.isLoading()) return;

  if (this.selectedIndex === 1) { // Comment says "Machine tab" but it's Spatial View!
    this.openAddMachine();
  } else if (this.selectedIndex === 2) { // Comment says "Resource tab" but it's Machines!
    this.openAddResource();  // BUG: Opens Resource dialog on Machines tab
  } else if (this.selectedIndex === 0) {
    // Overview/Dashboard - defaults to machine
    this.openAddMachine();  // <-- THIS SHOULD PROMPT
  } else {
    // Registry tab (index 4)
    this.triggerSyncDefinitions();
  }
}
```

**Correct Tab Indices (from template):**
- 0 = Overview (Dashboard)
- 1 = Spatial View
- 2 = Machines
- 3 = Resources
- 4 = Registry
```

### Proposed Solution

Create a simple choice dialog that appears when adding from Overview/Spatial tabs:

1. **Create `AddAssetChoiceDialogComponent`:**

   ```typescript
   @Component({
     selector: 'app-add-asset-choice-dialog',
     template: `
       <h2 mat-dialog-title>Add New Asset</h2>
       <mat-dialog-content>
         <p class="text-sys-text-secondary mb-4">What would you like to add?</p>
         <div class="grid grid-cols-2 gap-4">
           <button mat-stroked-button class="choice-card" (click)="select('machine')">
             <mat-icon class="!text-4xl">precision_manufacturing</mat-icon>
             <span class="font-medium">Machine</span>
             <span class="text-xs text-sys-text-secondary">Robots, liquid handlers, etc.</span>
           </button>
           <button mat-stroked-button class="choice-card" (click)="select('resource')">
             <mat-icon class="!text-4xl">science</mat-icon>
             <span class="font-medium">Resource</span>
             <span class="text-xs text-sys-text-secondary">Plates, tips, labware</span>
           </button>
         </div>
       </mat-dialog-content>
       <mat-dialog-actions align="end">
         <button mat-button mat-dialog-close>Cancel</button>
       </mat-dialog-actions>
     `
   })
   export class AddAssetChoiceDialogComponent {
     constructor(private dialogRef: MatDialogRef<AddAssetChoiceDialogComponent>) {}
     
     select(type: 'machine' | 'resource') {
       this.dialogRef.close(type);
     }
   }
   ```

2. **Update `openAddAsset()` in `AssetsComponent`:**

   ```typescript
   openAddAsset() {
     if (this.isLoading()) return;

     if (this.selectedIndex === 2) { // Machines tab
       this.openAddMachine();
     } else if (this.selectedIndex === 3) { // Resources tab
       this.openAddResource();
     } else if (this.selectedIndex === 0 || this.selectedIndex === 1) {
       // Overview or Spatial - prompt for choice
       this.openAddAssetChoice();
     } else if (this.selectedIndex === 4) {
       // Registry tab
       this.triggerSyncDefinitions();
     }
   }

   private openAddAssetChoice() {
     const dialogRef = this.dialog.open(AddAssetChoiceDialogComponent, {
       width: '400px'
     });

     dialogRef.afterClosed().subscribe(result => {
       if (result === 'machine') this.openAddMachine();
       if (result === 'resource') this.openAddResource();
     });
   }
   ```

### Alternative: Inline the choice in existing flow

Instead of a separate dialog, add a "Step 0" to both MachineDialog and ResourceDialog that offers the choice. However, this is more invasive.

**Recommendation:** Separate choice dialog is simpler and cleaner.

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/assets.component.ts` | Add choice dialog opening logic |
| `praxis/web-client/src/app/features/assets/components/add-asset-choice-dialog.component.ts` | **NEW FILE** - Choice dialog |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/machine-dialog.component.ts` | Machine dialog pattern |
| `praxis/web-client/src/app/features/assets/components/resource-dialog.component.ts` | Resource dialog pattern |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular commands
- **Frontend Path**: `praxis/web-client`
- **Styling**: Use existing Tailwind classes and CSS variables
- **Dialog**: Use Angular Material `MatDialog`
- **File location**: `praxis/web-client/src/app/features/assets/components/`

---

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors:

   ```bash
   cd praxis/web-client && npm run build
   ```

2. Overview tab verification:
   - Navigate to Assets → Overview tab
   - Click "Add Asset" button
   - Choice dialog appears with Machine/Resource options
   - Selecting Machine opens MachineDialog
   - Selecting Resource opens ResourceDialog
   - Cancel closes without action

3. Spatial View tab verification:
   - Navigate to Assets → Spatial View tab
   - Click "Add Asset" button
   - Same choice dialog behavior

4. Specific tab behavior:
   - Machines tab: "Add Machine" opens MachineDialog directly
   - Resources tab: "Add Resource" opens ResourceDialog directly
   - Registry tab: "Sync Definitions" behavior unchanged

---

## On Completion

- [ ] Commit changes with message: `feat(assets): add machine/resource choice dialog for overview`
- [ ] Update backlog item status in [asset_management.md](../../backlog/asset_management.md)
- [ ] Mark this prompt complete in batch README, update DEVELOPMENT_MATRIX.md if applicable, and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `.agents/codestyles/typescript.md` - TypeScript conventions
