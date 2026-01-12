# Agent Prompt: Playground Browser Tab Categories Fix

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260112](./README.md)
**Backlog Reference:** [playground.md](../../backlog/playground.md)

---

## 1. The Task

Fix the blank category view in the Playground inventory dialog's "Browse & Add" tab. When users navigate to Step 2 (Category) after selecting an asset type, the category list renders as a blank area.

**User Value:** Users can browse and select asset categories when adding items to the Playground inventory.

---

## 2. Technical Implementation Strategy

### Problem Analysis

In `InventoryDialogComponent`:
- Step 2 shows `availableCategories()` computed signal (lines 662-677)
- The computed depends on `typeValue()` signal (line 546)
- Categories are derived from `machines()` and `resources()` which are loaded via `toSignal()`

Potential issues:
1. `typeValue()` not updating when stepper advances
2. Race condition: categories computed before data loads
3. Async data not triggering signal recalculation

### Frontend Components

1. **Debug `InventoryDialogComponent`** category loading
   - Add console logging to trace `typeValue()` and `availableCategories()`
   - Verify `machines()` and `resources()` signals have data when step 2 renders
   - Check if `mat-chip-listbox` requires explicit change detection

2. **Possible fixes:**
   - Use `effect()` to debug signal chain
   - Ensure stepper advances don't break signal reactivity
   - Consider explicit subscription pattern if signals fail

### Data Flow

1. User selects "Machine" or "Resource" in Step 1
2. `typeControl.valueChanges` fires, updating `typeValue` signal
3. `availableCategories` computed recalculates
4. Step 2 renders `mat-chip-listbox` with categories

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts` | Component with category rendering (lines 160-185) |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/services/asset.service.ts` | Data source for machines/resources |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **State**: Prefer Signals for new Angular components.
- **Debugging**: Use browser DevTools and Angular DevTools extension

---

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors:
   ```bash
   cd praxis/web-client && npm run build
   ```

2. Manual testing:
   - Open Playground → Inventory Dialog → "Browse & Add" tab
   - Select "Machine" → click Continue
   - Step 2 should show machine categories (e.g., "Liquid Handler", "Plate Reader")
   - Select "Resource" → categories should update to resource types

3. No console errors related to signals or change detection

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status in `playground.md`
- [ ] Update DEVELOPMENT_MATRIX.md if applicable
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
