# UX Issues Batch - 2026-01-09

**Priority**: P2 (High)
**Owner**: Frontend
**Created**: 2026-01-09
**Status**: 🔴 New

---

## Overview

Consolidated UX issues identified during user verification session on 2026-01-09. This backlog captures multiple cross-cutting concerns that affect overall application polish.

---

## 1. Run Protocol Workflow Issues

### 1.1 Deck View Hardcoding ⚠️ CONFIRMED

**Location**: `deck-setup-wizard.component.ts:314`

**Issue**: Deck type is hardcoded to `'HamiltonSTARDeck'` regardless of selected machine:

```typescript
this.wizardState.initialize(p, 'HamiltonSTARDeck', assetMap);
```

**Fix Required**: Derive deck type from selected machine's deck definition.

### 1.2 No Specification Auto-Skip

**Issue**: If no asset specification is needed for a protocol, the guided setup step should auto-advance instead of showing an empty configuration.

**Location**: `guided-setup.component.ts`

### 1.3 Well Selection Dialog Button Display

**Status**: ✅ NOT AN ISSUE (investigated - buttons are properly implemented)

---

## 2. Asset Management Issues

### 2.1 Add Asset Button Routing ✅ FIXED

**Issue**: The + button routing was incorrect due to index shifts from the addition of Spatial View.

- Tab 1 (Spatial) opens Add Machine.
- Tab 2 (Machine) opens Add Resource.
- Tab 3 (Resource) triggers Sync Definitions.
**Fix**: Updated indices in `assets.component.ts` to (2=Machine, 3=Resource, 4=Registry). Added Spatial (1) to Machine routing.

### 2.2 Tab-Based Search + Filter Pattern ✅ COMPLETE

**Issue**: All tabs with "Overview" content should have:

- A search bar at the top
- An expandable "Filters" accordion below search

**Affected Components**:

- `assets.component.ts` - Overview tab
- `machines-accordion.component.ts` - Machines tab
- `resource-accordion.component.ts` - Resources tab
- `definitions-list.component.ts` - Registry tab

### 2.3 FQN Display Inconsistency

**Issue**: Resource dialog uses `truncate` class while machine dialog uses `fqn-wrap` with word-break styling.

**Location**:

- `resource-dialog.component.ts:168` - uses `truncate`
- `machine-dialog.component.ts:159` - uses `fqn-wrap`

**Fix**: Standardize to marquee/word-wrap pattern across both dialogs.

### 2.4 Spatial View + Button

**Issue**: No + button exists in Spatial View tab. User expects ability to add assets from spatial view.

**Location**: `spatial-view.component.ts`

### 2.5 Resource Tab Sync Definitions

**Status**: ✅ Working - has `disabled:opacity-50 disabled:cursor-not-allowed` styling.

---

## 3. Protocol Page Issues

### 3.1 Protocol Detail Dialog vs Page

**Issue**: Clicking a protocol navigates to separate page (`/protocols/:id`). User wants inline dialog instead.

**Current Behavior**: `router.navigate(['/protocols', protocol.accession_id])`

**Required Behavior**: Open `ProtocolDetailDialogComponent` with protocol info.

### 3.2 Remove Protocol Info Button

**Issue**: The "i" info icon button that navigates to detail page should be removed.

---

## 4. Workcell/Deck View Issues

### 4.1 Machine Filtering in Workcell

**Issue**: Workcell sidebar/view shows ALL machines including demo machines and non-liquid-handlers.

**Required**: Filter to show only relevant machine categories (e.g., liquid handlers for deck view context).

### 4.2 "Demo" Terminology in Machine Names

**Issue**: Machine names contain "Demo" prefix that should be eliminated.

**Files**:

- `demo.interceptor.ts` → Rename to `browser-mode.interceptor.ts`
- Remove "Demo" from mock machine/user names

---

## 5. Data Visualization Issues

### 5.1 Well Display as Chips vs Component

**Issue**: Wells are displayed as Material chips (`mat-chip-set`) instead of using the dedicated `WellSelectorComponent`.

**Location**: `data-visualization.component.ts:210-221`

**Fix**: Replace chip display with button that opens `WellSelectorDialogComponent`.

---

## 6. Documentation Issues

### 6.1 Diagram Expansion ✅ COMPLETE

**Issue**: Mermaid diagrams are fixed-size and cannot be expanded to full screen.

**Required**: Add expand button that opens diagram in modal/overlay at full viewport size. ✅ (Implemented `DiagramOverlayComponent` + injection in `DocsPageComponent`)

**Location**:

- `system-topology.component.ts`
- `docs-page.component.ts`

### 6.2 API References

**Status**: ✅ Working - API references exist at `/docs/api/*`.

---

## 7. Playground Issues

### 7.1 Loading State UX

**Issue**: User must click "Dismiss Loading" button to see the display.

**Status**: Working as designed, but could auto-dismiss after kernel ready signal.

### 7.2 Heading Text

**Status**: ✅ FIXED - Now shows "Playground Notebook".

### 7.3 Inventory Dialog Redesign ✅ COMPLETE

**Issue**: Current two-column stepper layout doesn't match user expectations.

**Required Changes**:

1. Replace two-column layout with tabbed interface:
   - "Add Items" tab (stepper workflow)
   - "Current Items" tab (list with edit/remove)
2. Add "Quick Add" tab with autocomplete search + filter accordion
3. Polish stepper CSS with completion indicators
4. Fix category display for machines and resources

**Location**: `inventory-dialog.component.ts` ✅ (Improved layout, added quick add, and fixed categories)

---

## 8. General/Cross-Cutting Issues

### 8.1 Demo Terminology Elimination

**Files to Update**:

- `demo.interceptor.ts` → `browser-mode.interceptor.ts`
- Update constant names: `demoInterceptor` → `browserModeInterceptor`
- Replace "Demo User" → "Local User"
- Replace "Demo Workcell" → "Default Workcell"
- Replace "Demo OT-2" → "Simulated OT-2"

### 8.2 CSS Hardcoding Audit ✅ COMPLETE

**Issue**: Need systematic audit of CSS values not using design system variables.

**Scope**: All components using hardcoded colors, spacing, or typography values.

### 8.3 Machine Arguments in Parameter Form ✅ COMPLETE

**Issue**: Machine selection arguments may be appearing in protocol parameter form.

**Solution**: Implemented `isAssetParameter()` method in `parameter-config.component.ts` that filters out:

- Parameters whose names match asset names in the protocol
- Parameters whose FQNs match asset FQNs  
- Parameters with type hints containing machine patterns (`pylabrobot.machines`, `LiquidHandler`, `Machine`, etc.)
- Parameters with type hints containing resource patterns (`pylabrobot.resources`, `Plate`, `TipRack`, `Carrier`, `Deck`, etc.)

---

## Related Documents

- [run_protocol_workflow.md](./run_protocol_workflow.md)
- [asset_management_ux.md](./asset_management_ux.md)
- [ui_consistency.md](./ui_consistency.md)
- [repl_enhancements.md](./repl_enhancements.md)
- [browser_mode.md](./browser_mode.md)
