# Application Audit Notes - January 14, 2026

**Status:** 📋 Specification Complete  
**Purpose:** Consolidated issue specifications from user review session. To be used as source of truth for generating inspection and implementation prompts.

---

## A. Simulation Architecture

**Issue:** Currently ~70 simulated backends are displayed directly in Add Machine Dialog, one per backend.

**Specified Solution:**

- ONE simulated frontend definition per frontend type (LiquidHandler, PlateReader, etc.)
- Backend type selection happens at **instantiation** (in protocols or playground), not at machine creation
- Backend-specific config should be available when needed
- Display: Short names (e.g., `chatterbox`), FQNs visible on hover or as animated ticker text

**Files Implicated:** `machine-dialog.component.ts`, `simulation_architecture_plan.md`, backend discovery service

---

## B. View Controls & Filtering

### B.1 Visual/Spacing Issues

**Issue:** Weird spacing, too long, cluttered on both desktop and mobile.  
**Action:** Programmatic DOM/CSS inspection first, then browser agent screenshots.

### B.2 View Type Toggle

**Issue:** Toggle currently shows text.  
**Specified Solution:** Icons only, no text labels.

### B.3 Status Filter Missing "Available"

**Issue:** "Available" status not appearing in filter dropdown.  
**Specified Solution:** Likely not wired up. Need consistent application sync - items in DB are "Available" but enum/filter mismatch.

### B.4 GroupBy Toggle

**Issue:** GroupBy shows 2 "None" categories; dropdown unnecessary for binary options.  
**Specified Solution:** If options are [None, X], render as toggle instead of dropdown.

### B.5 Add Filters Menu Text Invisible

**Issue:** Cannot see text in Add Filters menu.  
**Specified Solution:** Dark mode issue at minimum. Audit all components for themed CSS usage (no hardcoded colors).

### B.6 Filter Chip Display

**Issue:** Currently shows `[Status: Available, Error x]` as single chip.  
**Specified Solution:** Group chips by filter key: `Status: [Available]x [Error]x`

---

## C. ViewControls Adoption

**Issue:** Multiple pages have their own search/filter implementations instead of `ViewControlsComponent`.

| Page | Action |
|:-----|:-------|
| Protocol Library | Inspect existing filters, replace with ViewControls |
| Execution Monitor | Inspect existing filters, replace with ViewControls |
| Data Visualization | Inspect existing filters, replace with ViewControls |

---

## D. Breadcrumbs

**Issue:** Breadcrumb bar serves no current purpose.  
**Specified Solution:** Remove entirely from `unified-shell.component.ts`. Document decision in notes.

---

## E. Playground & Browser Mode

### E.1 Kernel Load Regression

**Issue:** Blank or no iframe on first load; requires "Restart Kernel" click.

### E.2 Theme Sync

**Issue:** JupyterLite ignores app theme on startup.  
**Note:** Mid-session sync not expected.

### E.3 Background Bootstrap

**Issue:** User sees initialization code in first cell.  
**Specified Solution:** Partially transparent overlay with "Initializing Pyodide" + loading spinner. Previous attempt went infinite - need robust auto-close logic.

### E.4 WebSerial/WebUSB

**Issue:** WebSerial and WebUSB not available in Pyodide environment.  
**Specified Solution:** Shims appear to load, but `WebSerial` not in builtins. Need investigation.

### E.5 Inventory Optimizations

**Issue:** Unite inventory selection style with add asset in inventory management.  
**Reference:** `inventory_ux_design.md`

---

## F. Protocol Execution & Run Protocol

### F.1 Well Arguments Duplication

**Issue:** Well selection shows in Parameters step AND Well Selection step.  
**Specified Solution:** Remove from Parameters. Show in protocol summary screen after selection.

### F.2 Selective Transfer Index Hint

**Issue:** Linked indices (source/dest) need size validation.  
**Specified Solution:** Both:

- Validation error at end of well selection step
- Live counter: "Source: 4 wells | Destination: 4 wells"
- Index linking logic from protocol decorator OR simulation/DAG analysis

### F.3 Well Selector Lag [DONE]

**Issue:** Laggy on click+drag for 384-well plates.  
**Note:** Not a problem with 96-well.

### F.4 Asset Autocomplete Bug

**Issue:** Selections don't persist, interaction clunky.  
**Specified Solution:** Fresh approach to interaction scheme while keeping autoselect convenience.

### F.5 Guided Deck Setup

**Issue:** Deck should start EMPTY (except machine defaults like OT-2 trash).  
**Specified Solution:** Pull deck state from database, appropriate type for machine.

---

## G. Documentation

### G.1 Installation Docs

**Issue:** `api-production` paths not found; production mode info missing.  
**Specified Solution:** Create:

- `installation-browser.md` (website URL + local setup)
- `installation-production.md` (full stack)
- Note: Also need `installation-lite.md` (SQLite + no-setup KV store)

### G.2 Mermaid Diagrams

**Issue:** Diagrams not rendering.  
**Possible Cause:** Related to production/browser mode tab switching in docs viewer.

---

## H. Home Page & Settings

### H.1 Recent Activity

**Issue:** Uses hardcoded mock data ("Serial Dilution Run #42").  
**Specified Solution:** Use realistic mock data based on actual bundled example protocols. Add easy way for users to clear fake runs.

### H.2 Settings UX

**Issue:** Settings page needs overhaul.  
**Specified Solution:** In-depth planning task to determine valuable settings and presentation (search bar, tabs, etc.).

---

## I. Cards & Visual Declutter

### I.1 General Assessment

**Issue:** Cards throughout application have overlap issues (corner chips, text).

### I.2 Specified Direction

- Better hierarchy
- Smarter flex controls
- Define "minimum card" for limited space, progressive content as canvas expands
- Current information level is appropriate, just layout fixes needed

---

## J. Deck View & Constraints

### J.1 Deck Placement Constraints

**Issue:** Need to specify restrictions for deck layouts.  
**Source:** Protocol decorator OR simulation inference.  
**Scope:** NOT marked as tech debt.

### J.2 Deck View UX

**Issue:** Needs optimization and overhaul.  
**Scope:** Keep separate from Workcell UX Redesign.

---

## Workstream Mapping

| Workstream | Issues | Priority |
|:-----------|:-------|:---------|
| Simulation Refactor | A | P2 |
| ViewControls Polish | B.1-B.6 | P2 |
| ViewControls Adoption | C, D | P2 |
| Playground Fixes | E.1-E.5 | P1/P2 |
| Protocol Execution | F.1-F.5 | P2 |
| Documentation | G.1-G.2 | P3 |
| Home/Settings UX | H.1-H.2 | P3 |
| Card Visual Polish | I | P3 |
| Deck View UX | J | P2 |
