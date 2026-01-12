# Agent Prompt: Playground Resource Filters Fix

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260112](./README.md)
**Backlog Reference:** [playground.md](../../backlog/playground.md)

---

## 1. The Task

Fix the broken resource filters in the Playground inventory dialog:
1. Filter controls are not working (selecting a filter doesn't update the list)
2. Filter styling is inconsistent with filters in other tabs/components

**User Value:** Users can efficiently filter and find resources in the Playground inventory.

---

## 2. Technical Implementation Strategy

### Problem Analysis

Looking at `InventoryDialogComponent` (lines 538-548, 700-724):
- `quickFilterType` and `quickFilterCategory` are FormControls
- They are converted to signals via `toSignal()`
- The `filteredQuickAssets` computed signal depends on these

Potential issues:
1. The `toSignal()` may not be triggering reactivity correctly
2. The filter logic in `filteredQuickAssets()` may have bugs

### Frontend Components

1. **Fix `InventoryDialogComponent`** (`praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts`)
   - Debug the reactive chain: FormControl → toSignal → computed
   - Verify filter application logic at lines 700-724
   - Consider using `effect()` or explicit subscriptions if signals aren't reactive

2. **Align styling with other filter components**
   - Reference `FilterHeaderComponent` for consistent styling
   - Use `PraxisSelectComponent` consistently (already imported)
   - Match the visual style of asset filters in other views

### Data Flow

1. User selects filter option in dropdown
2. FormControl value changes
3. Signal updates
4. Computed `filteredQuickAssets()` recalculates
5. Template re-renders with filtered list

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/playground/components/inventory-dialog/inventory-dialog.component.ts` | Main component with filter logic |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/filter-header/filter-header.component.ts` | Consistent filter header pattern |
| `praxis/web-client/src/app/features/assets/components/asset-filters/asset-filters.component.ts` | Working filter implementation |
| `praxis/web-client/src/app/shared/components/praxis-select/praxis-select.component.ts` | Styled select component |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular.
- **Frontend Path**: `praxis/web-client`
- **Styling**: Use Tailwind utility classes where possible.
- **State**: Prefer Signals for new Angular components.

---

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors:
   ```bash
   cd praxis/web-client && npm run build
   ```

2. Manual testing:
   - Open Playground → Inventory Dialog → Quick Add tab
   - Select "Machines" from Type filter → only machines shown
   - Select "Resources" from Type filter → only resources shown
   - Select a specific category → only matching items shown
   - Clear filters → all items shown

3. Visual consistency: Filters match styling of other filter components in the app

---

## On Completion

- [ ] Commit changes with descriptive message
- [ ] Update backlog item status in `playground.md`
- [ ] Update DEVELOPMENT_MATRIX.md if applicable
- [ ] Mark this prompt complete in batch README

---

## References

- `.agents/README.md` - Environment overview
