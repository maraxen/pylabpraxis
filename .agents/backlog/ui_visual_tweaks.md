# UI Visual Tweaks Backlog

**Priority**: P3 (Medium)
**Owner**: Frontend
**Created**: 2026-01-04
**Status**: Planning

---

## Overview

Minor visual/UI tweaks needed for polish. These are smaller items that improve the overall look and feel without being full features.

---

## Items

### 1. Registry Tab Spacing (Asset Management)

**Location**: Asset Management → Registry tab (Machine Definitions / Resource Definitions)

**Issue**: Spacing between items in the registry tab may be inconsistent or too cramped.

**Tasks**:
- [ ] Audit current spacing in registry accordions
- [ ] Ensure consistent padding/margin between items
- [ ] Match spacing with Inventory tabs (Machines/Resources)

**Files**:
- `praxis/web-client/src/app/features/assets/components/registry-tab/`

---

### 2. Resource Inventory Filters (Match Machine Filters)

**Location**: Asset Management → Resources tab (Inventory)

**Issue**: Resources tab has category dropdowns but lacks the filter chips/toggles that the Machines tab has. Should have parity with machine filtering UX.

**Current State**:
- Categories with dropdowns exist
- No filter chips like Machines tab has

**Filters Needed** (match Machines tab pattern):
- [ ] Resource type filter (Plate, TipRack, Trough, Carrier, etc.)
- [ ] Category filter chips
- [ ] Status filter (available, in-use, maintenance)
- [ ] Parent machine/workcell filter
- [ ] Search by name

**Tasks**:
- [ ] Create `ResourceFiltersComponent` matching `MachineFiltersComponent` pattern
- [ ] Add horizontal scrollable filter chip container (like Execution Monitor)
- [ ] Wire up filters to `AssetService.getResources()` query
- [ ] Persist filter state in URL params

**Files**:
- `praxis/web-client/src/app/features/assets/components/asset-filters/`
- `praxis/web-client/src/app/features/assets/assets.component.ts`
- Reference: Machine filters implementation for pattern

---

### 3. Machine Tab Spacing

**Location**: Asset Management → Machines tab (Inventory)

**Issue**: Similar spacing concerns as Registry tab.

**Tasks**:
- [ ] Audit current spacing in machine accordions
- [ ] Ensure consistent padding/margin between accordion items
- [ ] Proper spacing for machine cards/rows

---

## General UI Audit Items

- [ ] Consistent button sizes across all views
- [ ] Consistent card padding
- [ ] Proper responsive behavior on narrow screens
- [ ] Loading states for all async operations
- [ ] Empty states with helpful messages

---

## Success Criteria

1. [ ] Registry tab has consistent, readable spacing
2. [ ] Resources tab has functional filters matching other filter UIs
3. [ ] Machine tab has consistent spacing
4. [ ] No visual layout issues in Asset Management views
