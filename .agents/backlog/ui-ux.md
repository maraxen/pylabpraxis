# UI/UX Backlog

**Area Owner**: Frontend
**Last Updated**: 2026-01-01

---

## Critical (P1)

### Purple Buttons/Toggles in Light Mode - ✅ RESOLVED 2026-01-01

- [x] Some buttons and toggles are purple instead of classic pink.
- [x] Identify affected components and update to use correct theme colors.

### Asset Dashboard Scrolling - ✅ RESOLVED 2026-01-01

- [x] Fix buggy scrolling behavior within asset components.
- [x] Ensure vertical scrollbars appear correctly in nested views.

### Parameter/Deck Selection Scrolling (Protocol Setup) - ✅ RESOLVED 2026-01-01

- [x] Parameter and deck selection screens in protocol setup won't scroll.
- [x] Investigate `mat-stepper` CSS overflow issues.
- [x] **Regression Fix**: Fixed blank screen on downstream steps by correctly collapsing inactive steps (`.mat-horizontal-stepper-content-current`).

### mat-form-field Visual Bug (Notched Outline) - ✅ RESOLVED 2026-01-01

- [x] Vertical line appearing in the notch of `mat-form-field` when using outline appearance.
- [x] Global fix in `styles.scss` removing `border-right` from `.mdc-notched-outline__notch`.

---

## High Priority (P2)

### Filter Search Bar Line Bug - ✅ RESOLVED 2025-12-31

- [x] Weird line appearing down the middle of filter search bars.
- [x] Consistent issue throughout the app - find global CSS cause.

### Activity History Linking - ✅ RESOLVED 2026-01-01

- [x] Activity history items now link to Execution Monitor.
- [x] Added `routerLink` to `/app/monitor/:id` for each run in Recent Activity.
- [x] Added visual feedback: hover effects, chevron icon, tooltips.
- [x] Updated "View All" link to navigate to `/app/monitor`.

### Remove Quick Links Section

- [ ] Home dashboard "Quick Links" serve no purpose.
- [ ] All items are accessible via navbar - remove entire section.

### Command Palette - ✅ RESOLVED 2025-12-31

- [x] **Visual Responsiveness**: Fixed active state styling.

### Light Theme Polish - ✅ RESOLVED 2025-12-31

- [x] **Text Contrast**: Fixed.
- [x] **Button Rendering**: Fixed.
- [x] **Color Tuning**: Fixed.
- [x] **Docs Sidebar**: Fixed white text in light mode (2026-01-01).
- [x] **Mermaid Diagrams**: Fixed light mode text visibility (2026-01-01).

### REPL UI Polish

See [repl.md](./repl.md) for detailed items.

---

## Medium Priority (P3)

### Gentle Gradient Background

- [ ] Add subtle gradient within background for both light and dark mode.
- [ ] Should enhance visual depth without being distracting.

### Loading Skeletons - ✅ RESOLVED 2026-01-02

- [x] Replace generic spinners with skeleton loaders.
- [x] Apply to: protocol cards, asset lists, deck view. (Implemented in Dashboard, History, Run Detail)

### Command Palette Spacing - ✅ RESOLVED 2026-01-01

- [x] Fixed spacing of keyboard shortcuts and tags in command palette.
- [x] Changed meta-container from vertical to horizontal layout.
- [x] Improved shortcut badge styling with modern monospace font.
- [x] Made category chips pill-shaped with better visual separation.

### Navigation - ✅ RESOLVED 2026-01-02

- [x] Review breadcrumbs for deep navigation. (Integrated `BreadcrumbComponent` into Unified Shell)
- [x] Responsive check (Mobile/Tablet validation).

### Deck Visualizer

See [deck_view.md](./deck_view.md) for detailed items.

---

## Low Priority

### Future Enhancements

- [ ] Spatial relationship mapping (workcells in space)
- [ ] Dynamic form generation from capability schemas

---

## Completed - ✅

### Workcell Visualizer (REWRITE)

- [x] **Architectural Rewrite**:
  - Abandoned legacy `DeckVisualizer` (iframe/PLR component).
  - Implemented **Workcell Visualizer**: A configurable canvas of "Deck Windows".
  - Allow users to open/close/arrange windows for different decks/machines.
- [x] **Configurability**:
  - Persist window layout in LocalStorage.
- [x] **PLR Theming**:
  - Dark/light theme support with CSS variables
  - All PLR resource types styled (plates, tip racks, troughs, carriers, lids, petri dishes, tubes, adapters)

### Deck Setup Step (FIXED 2025-12-30)

- [x] ~~**Critical**: Required assets are not showing up for selection.~~ Improved FQN-based matching logic.
- [x] ~~**Critical**: UI does not indicate which items have been autofilled.~~ Added autofill badges and summary.
- [x] Added loading/empty states, match quality indicators, and better UX.

### General Polish

- [x] Chip Hover Information (Tooltips).
- [x] Visual Polish (Spacing, Gradients).
- [x] Command Palette (Alt/Option mapping).
- [x] Text contrast in light theme.

---

## Related Backlogs

- [repl.md](./repl.md) - REPL-specific UI items
- [deck_view.md](./deck_view.md) - Deck visualizer items
- [cleanup.md](./cleanup.md) - Pre-merge cleanup
