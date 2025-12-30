# Demo Mode Finalization

**Created**: 2025-12-29
**Priority**: High
**Goal**: Finalize PyLabPraxis Demo Mode for GitHub Pages deployment

---

## Critical Bug Fixes

- [x] **Plotly Initialization Error** ✓ Fixed with `PlotlyService.setPlotly()` in `main.ts`
- [x] **SQLite Quota Error** ✓ Added error handling to `sqlite.service.ts`

## Feature Implementations

### Consumables Logic

- [ ] Consumables = infinite by default OR optionally tracked with counts
- [ ] Post-processing states: discard, clean, or custom
- [ ] UI: Tab views for categories, accordion for types (UX TBD after bugs fixed)
- [ ] Machines already have their own tab

### Deck Visualizer

- [ ] Integrate existing DeckVisualizerComponent into protocol run setup
- [ ] Link to PLR-based visualizer view (clarify integration approach)

### Guided Deck Setup (Integrated into Protocol Run Setup)

- [ ] Flow: on-deck machines → carriers → carrier consumables → other
- [ ] Validate space requirements for user-specified decks
- [ ] Confirmation popup before execute screen

### Data Visualization Page

- [ ] New route in sidebar
- [ ] Dashboard for experiment data
- [ ] View runs functionality
- [ ] Link experiment cards to dashboards

---

## Open Questions (After Bugs Fixed)

1. **Resource Manager UX**: What's the best interaction pattern for tabs/accordions?
2. **Deck Visualizer**: Embed PLR SVG directly or use iframe to PLR visualizer?
3. **Guided Setup**: Modal wizard vs inline deck configuration?
