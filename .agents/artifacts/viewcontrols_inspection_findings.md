# ViewControls Inspection Findings

## Summary

Found 4 primary issues across 4 components. The inspection confirms responsive layout issues, potential theming conflicts in overlays, and consistency gaps in the view toggle implementation.

## Issue Catalog

### Issue 1: View Type Toggle Text Visibility

- **File:** `view-type-toggle.component.ts`
- **Line:** 15, 20, 25
- **Problem:** User reported "shows text", but code implements `mat-icon` only.
- **Analysis:** Code uses `mat-button-toggle` with `matTooltip`. No text node exists in the template. The reported issue might be due to a global style overriding `mat-button-toggle` content or a misunderstanding of the UI (perhaps tooltips getting stuck?). However, the current implementation is technically correct for "icons only" unless `mat-button-toggle-group` is forcing text display via CSS content pseudo-elements in the global theme.
- **Fix:** Verify global styles for `mat-button-toggle`. Ensure `aria-label` is not being rendered as text by some accessibility stylesheet.

### Issue 2: "Add Filters" Menu Text Visibility in Dark Mode

- **File:** `view-controls.component.ts`
- **Line:** 120 (mat-menu), 318 (CSS)
- **Problem:** Text invisible in dark mode.
- **Analysis:** The `.filter-label` uses `color: var(--theme-text-secondary)`. The menu itself is a `mat-menu`.
  - If `mat-menu` background doesn't match the expectation for `theme-text-secondary`, contrast fails.
  - Specifically, `mat-menu` usually sits in an overlay container. If that container doesn't receive the correct theme class (e.g. `.dark-theme`), it might default to light background while the text var resolves to light color (for dark mode), resulting in white-on-white.
- **Screenshot:** `view_controls_add_filter_menu`
- **Fix:** Ensure the overlay container receives the theme class, or explicitly set the background color of `.filter-popover-menu` using a theme token like `var(--theme-surface-menu)`.

### Issue 3: Cluttered Layout & Spacing (Refined)

- **File:** `view-controls.component.ts`
- **Line:** 210, 436
- **Problem:** "Weird spacing", "Too long/cluttered", and alignment issues.
- **Analysis (based on screenshot):**
  - **Inconsistent Horizontal Gaps:** There is a large, unexplained gap between the `View Type Toggle` and the `Group By` select.
  - **Multiselect "None" Fallback:** The `PraxisMultiselectComponent` renders a "None" text (line 87) below the select box when no items are selected. This creates unnecessary vertical height and looks like a disconnected label.
  - **Second Row Alignment:** The `Sort By` controls are wrapping to a second row. The `Sort By` label in the `mat-form-field` appears misaligned (overlapping the top border) and the vertical spacing between rows is minimal.
  - **Search Input Padding:** The search icon and placeholder text in the search bar seem to have excessive or mismatched padding.
  - **"Add Filter" Button:** The dashed border and positioning far to the right contribute to a fragmented appearance.
- **Screenshot:** [Screenshot 2026-01-14 at 11.27.12 AM.png](file:///Users/mar/Projects/pylabpraxis/.agents/artifacts/Screenshot%202026-01-14%20at%2011.27.12%E2%80%AFAM.png)
- **Fix:**
  - Standardize gaps using a consistent spacing variable (e.g. `gap: 8px` or `12px` throughout).
  - Remove/Refine the "None" display in `PraxisMultiselectComponent`. It should likely only show content when items *are* selected, or integrate the "None" state into the trigger label.
  - Ensure all controls in the primary row share a consistent height (currently some are 32px, some 36px).
  - Use a more robust grid or flex layout that handles overflow more gracefully without creating "clutter".
  - Fix the `mat-form-field` label alignment for the sort field.

### Issue 5: Chip Display Consistency

- **File:** `praxis-multiselect.component.ts`
- **Problem:** Selected items are displayed as chips *below* the select box, while the `ViewControlsComponent` also has a global "Active Filters" row.
- **Analysis:** This duplication of "chip" concepts (individual component chips vs. global active chips) is confusing. If `ViewControls` is handling the display of active filters globally, the individual multiselects shouldn't necessarily render their own chips below.
- **Fix:** Provide a way to disable the internal chip grid in `PraxisMultiselectComponent` when used inside `ViewControls`.

### Issue 6: Group By & Sort By Text Alignment

- **File:** `group-by-select.component.ts` (line 30), `view-controls.component.ts` (line 329)
- **Problem:** User reported "where text is on the groupby and sort buttons". The labels and values appear misaligned or overlapping borders.
- **Analysis:**
  - Both components use excessive `::ng-deep` overrides to force `mat-form-field` into a 32px height.
  - specifically `.mat-mdc-form-field-label-wrapper { top: -8px; }` is a "magic number" hack that breaks when font sizes or line heights slightly vary.
  - `.mat-mdc-form-field-infix { padding: 0 !important }` removes necessary spacing for the floating label calculation.
  - The combination of `appearance="outline"` and these overrides causes the label "Group By" or "Sort By" to sit awkwardly relative to the top border, and the selected value text to be vertically miscentered.
- **Fix:**
  - Switch to `subscriptSizing="dynamic"` (already there but maybe insufficient).
  - Consider removing the floating label pattern for these "button-like" dropdowns and instead use a standard trigger with a separate or `aria-label` only, OR properly derive the label offset calculations to match the reduced height.
  - Alternatively, increase the height slightly (e.g. 36px/40px) to standard material density sizing to avoid hacking internals.

### Issue 4: Theme Token Usage & Hardcoded Values

- **File:** `view-controls.component.ts`
- **Line:** 262
- **Problem:** usage of `rgba(var(--primary-color-rgb), 0.1)`.
- **Analysis:** While utilizing a CSS variable, manually constructing `rgba` implies that `--primary-color-rgb` is a raw triplet (e.g., `0, 122, 255`). This is a fragile pattern compared to using a dedicated token like `--primary-color-alpha-10`.
- **Fix:** creating/using a proper opacity token or strictly using `color-mix` if supported, or ensuring the token contract is robust.

- **File:** `view-controls.component.ts`
- **Line:** 305
- **Problem:** `border-style: dashed` for `add-filter-btn`.
- **Analysis:** This style choice might deviate from the standard design system (usually solid or no border).
- **Fix:** Confirm if `dashed` is the intended design token for "add" actions.

## Theme Token Violations

| File | Line | Content | Note |
| :--- | :--- | :--- | :--- |
| `view-controls.component.ts` | 420 | `color: var(--mat-sys-error)` | Should likely be a project token e.g. `--color-error` or similar, unless Material tokens are standard. |
| `view-controls.component.ts` | 369 | `background: var(--theme-surface-subtle)` | Verify specific token existence. |
| `view-controls.component.ts` | 469 | `@keyframes fadeIn` | Animations should ideally use standard duration tokens. |

## Recommended Fix Order

1. **Fix Dark Mode Menu Text:** Critical usability issue. (High Priority)
2. **Review View Toggle:** Confirm icon-only status and check global overrides. (Medium Priority)
3. **Refine Spacing/Layout:** Address "cluttered" feel by tightening gaps or adjusting breakpoints. (Medium Priority)
4. **Standardize Tokens:** Replace manual `rgba` and `mat-sys` references with project tokens. (Low Priority)
