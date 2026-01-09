# Agent Prompt: Remove Duplicate Clear Button in Filter Dialog

Examine `.agents/README.md` for development context.

**Status:** 🟢 Not Started
**Priority:** P2
**Batch:** [260109](./README.md)
**Backlog Reference:** [ui_polish.md](../../backlog/ui_polish.md)

---

## 1. The Task

The `FilterHeaderComponent` displays a "Clear" button inside the filter panel header when active filters exist. However, this creates duplication with other clear functionality, specifically with the search field's clear (×) button that appears when text is entered. The task is to audit the filter header component and remove any redundant clear button that appears near the sort/order toggle area.

**User Value:** Cleaner UI without confusing duplicate controls; clearer user mental model for clearing filters vs clearing search.

---

## 2. Technical Implementation Strategy

### Architecture

**Component:** `FilterHeaderComponent`

- Located at: `praxis/web-client/src/app/features/assets/components/filter-header/filter-header.component.ts`
- The component has:
  - A search field with its own clear button (×) that appears when `searchControl.value` is truthy
  - A "Clear" button in the `mat-expansion-panel-header` that emits `clearFilters`

### Data Flow

1. User sees filter panel header with badge count + "Clear" button
2. Search field has separate clear (×) button
3. Clicking "Clear" emits `clearFilters` event to parent
4. Parent components (MachineListComponent, SpatialViewComponent, etc.) handle clearing

### Investigation Required

Before making changes:

1. Verify which "clear" button is the duplicate (in panel header vs search field)
2. Check parent components to understand if `clearFilters` should clear BOTH search AND filters, or just filters
3. Backlog says "duplicate clear button inside the filter dialog by the order toggle button" — this suggests the Clear button in the panel header is the issue when combined with another clear in the filter content area

### Proposed Fix

Based on the component structure, the likely fix is:

- **Option A:** Remove the inline "Clear" button from `mat-expansion-panel-header` since search field already has (×)
- **Option B:** Keep panel header Clear button but ensure it clears ALL filters (including search), making it the primary clear mechanism

Recommended: **Option B** — Keep the "Clear" button in panel header as the primary way to reset all filters. The search (×) only clears search text.

---

## 3. Context & References

**Primary Files to Modify:**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/filter-header/filter-header.component.ts` | Main component with duplicate button |

**Reference Files (Read-Only):**

| Path | Description |
|:-----|:------------|
| `praxis/web-client/src/app/features/assets/components/machine-list/machine-list.component.ts` | Consumer of FilterHeaderComponent |
| `praxis/web-client/src/app/features/assets/components/spatial-view/spatial-view.component.ts` | Consumer of FilterHeaderComponent |
| `praxis/web-client/src/app/features/assets/components/asset-filters/asset-filters.component.ts` | Alternate filter pattern for comparison |

---

## 4. Constraints & Conventions

- **Commands**: Use `npm` for Angular CLI commands
- **Frontend Path**: `praxis/web-client`
- **Styling**: Use existing Tailwind utility classes and CSS variables
- **Testing**: Manual verification since no unit test exists for this component

---

## 5. Verification Plan

**Definition of Done:**

1. The code compiles without errors:

   ```bash
   cd praxis/web-client && npm run build
   ```

2. Visual verification:
   - Navigate to Assets → Machines tab
   - Expand the filter panel
   - Confirm only ONE clear mechanism is visible in the expected location
   - Verify Clear button resets all filters including search
   - Verify search (×) only clears search text

3. No regressions in filter functionality across:
   - Machine list filters
   - Spatial view filters
   - Resource accordion filters (if using FilterHeaderComponent)

---

## On Completion

- [ ] Commit changes with message: `fix(ui): remove duplicate clear button in filter dialog`
- [ ] Update backlog item status in [ui_polish.md](../../backlog/ui_polish.md)
- [ ] Mark this prompt complete in batch README, DEVELOPMENT_MATRIX.md if applicable, and set the status in this prompt document to 🟢 Completed

---

## References

- `.agents/README.md` - Environment overview
- `.agents/codestyles/typescript.md` - TypeScript conventions
