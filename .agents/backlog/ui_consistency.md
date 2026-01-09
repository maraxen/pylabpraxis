# UI Consistency & Polish

**Priority**: P2-P3 (Mixed)
**Owner**: Frontend
**Created**: 2026-01-07 (migrated from TECHNICAL_DEBT.md)
**Status**: 🟢 Planned

---

## Goal

Standardize UI patterns across the application for a cohesive user experience. Address inconsistencies in dropdown chips, navigation labeling, and settings appearance.

---

## Phase 1: Execution Monitor Standardization

- [x] **Status Display**: Convert text/badges to `FilterChipComponent` dropdowns.
- [x] **Filter Bar**: Standardize layout and spacing to match Asset Management.
- [x] **Action Menus**: Audit and align popup menus (None found to standardize; buttons used instead).

## Phase 2: Navigation & Layout

- [x] Rename sidebar item "Deck" to "Workcell" or equivalent ✅ FIXED
- [x] Audit navigation labels for clarity and consistency ✅ FIXED
- [ ] Implement hover-triggered overlay menus for nav items with children

## Phase 3: Settings & Stepper Polish

> [!WARNING]
> User verification confirmed these issues on 2026-01-08.

- [x] **Settings Icons Cutoff**: Rounded corners cutting off icons in settings cards <!-- id: 1 -->
- [x] **Settings Visual Consistency**: Improved layout, icon spacing, and button selector refinements. <!-- id: 2 -->
- [x] **Stepper Theme Sync**: Fix hardcoded white number circles (verified resolved). <!-- id: 3 -->
- [ ] **Stepper → ARIA Tabs**: Consider migrating stepper to `@angular/aria` tabs for accessibility
- [x] Add tooltips for accessibility <!-- id: 4 -->
- [ ] Consider flyout menus for nested navigation

## Phase 4: Component Styling & Interactions (2026-01-08)

- [ ] **Interactive States (Multiselect/Select/Autocomplete)**:
  - **Issue**: Clicking changes rendering permanently.
  - **Requirement**:
    - **Default/Active**: Primary application color with transparent text.
    - **Selection Screen**: Theme background with primary color text.
    - **Button**: Stays consistent.

- [ ] **Rich Multiselect Options**:
  - **Requirement**: Use logos/icons (e.g., PLR resource types) instead of checkboxes whenever possible.

## Phase 5: Resource Dialog Dynamic Facets

- [ ] **Hardcoded Facets**: "More filters" facets are hardcoded in resource dialog.
- [ ] **Dynamic Derivation**: Derive facet definitions/options from resource type definitions automatically.
- [ ] **Sync with Metadata**: Ensure filter chip dropdown stays in sync with available resource metadata.

---

## Notes

Migrated from TECHNICAL_DEBT.md items #7 (Execution Monitor & UI Consistency) and #12 (Navigation Rail Hover Menus).

---

## References

- [TECHNICAL_DEBT.md](../TECHNICAL_DEBT.md) - Original source
- [DEVELOPMENT_MATRIX.md](../DEVELOPMENT_MATRIX.md)
