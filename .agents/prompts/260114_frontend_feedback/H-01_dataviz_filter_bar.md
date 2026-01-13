# H-01: DataViz Filter Bar Redesign

**Status:** 🟢 Implementation
**Priority:** P2
**Depends On:** Group A (optional)

---

## Context

The Data Visualization filter bar (`app-filter-header`) currently has UI issues regarding transparency (trailing artifacts), shape (needs rounded corners), and behavior (needs to be dismissable/minimizable and float above content). Additionally, users have requested "Group By" functionality which is currently missing.

`app-filter-header` is a shared component used in multiple features (Protocols, Assets, Monitor, DataViz). Changes should be backwards compatible or purely additive, OR the DataViz implementation should derive/extend specifically if the changes are drastic. Given the feedback "fix trailing/transparency" and "rounded corner", these likely apply essentially to the shared component to benefit all views, but the "Group By" might be specific to DataViz or a new slot in the shared component.

## Objectives

1. **UI Polish:**
    - Update `FilterHeaderComponent` styles to use rounded corners (`border-radius: 12px` or similar).
    - Fix transparency issues: ensure the header has a solid background (e.g., `var(--mat-sys-surface)`) and/or proper `z-index` handling so it doesn't "trail" when scrolling or moving.
    - Make it "float" – add a subtle shadow and potentially detach it slightly from the top if appropriate, or just ensure the sticky behavior is clean.

2. **Interaction:**
    - Add **Minimize/Collapse** functionality to the filter bar. The current `mat-expansion-panel` inside it might already handle some of this, but the *entire* bar or the search field area might need a "docked" state if it takes up too much space.
    - *Specific Requirement:* "Dismissable or minimizable".

3. **New Feature: Group By:**
    - Add a "Group By" selector to the DataViz filter area (in `DataVisualizationComponent`).
    - Options could include: `Protocol`, `Status`, `Date`, `User` (if available).
    - Update the chart data transformation logic (`filteredRuns`, `transferData`) to reflect this grouping (e.g., verify that selecting "Group By Protocol" changes how data is aggregated or colored in the chart).

## Implementation Details

### 1. `FilterHeaderComponent` (Shared)

- **Location:** `praxis/web-client/src/app/features/assets/components/filter-header/filter-header.component.ts`
- **Styles:**
  - Check `.tab-header` and `.filter-panel` classes.
  - Ensure `background` is opaque.
  - Add `box-shadow` for the floating effect.
  - Radius updates.
- **Minimize:**
  - Ensure the expansion panel (which holds filters) defaults to closed or has a clear toggle.
  - Consider adding a "Hit the X" or "Hide" button if the user wants to remove the bar entirely (and a way to bring it back, e.g., a FAB or button in the page header). *Decision:* A "Hide Filters" toggle button in the main page header that hides the `app-filter-header` via `*ngIf` or `[hidden]` is often the cleanest pattern.

### 2. `DataVisualizationComponent` (Feature)

- **Location:** `praxis/web-client/src/app/features/data/data-visualization.component.ts`
- **Template:**
  - Add the "Group By" `app-praxis-select` or `mat-chip-listbox` into the `<div class="selector-row" filterContent>` section.
- **Logic:**
  - Track `groupBy` signal (e.g., `groupBy = signal<string>('none')`).
  - Update `chartData` computed to use this signal. For example, if `groupBy('protocol')`, assign different colors/traces per protocol in the Plotly data array.

## Verification

- **Visual:**
  - Navigate to Data Visualization tab.
  - Scroll the page: Verify the filter bar does not "trail" or show content behind it weirdly (opacity fix).
  - Check rounded corners.
  - Test "Minimize/Dismiss": Can you hide the filter bar? Can you bring it back?
- **Functional:**
  - Select "Group By: Protocol".
  - Verify the chart updates (e.g., multiple lines/bars appear, one per protocol, or legend updates).

## Definition of Done

- Filter bar looks "premium" (rounded, floating, solid/opaque).
- No visual artifacts during scroll.
- "Group By" control exists and affects the chart.
- Filter bar can be minimized or dismissed.
