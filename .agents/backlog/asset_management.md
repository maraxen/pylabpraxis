# Asset Management Backlog

**Priority**: CRITICAL
**Owner**: Backend + Frontend
**Last Updated**: 2025-12-30

---

## 1. PLR Inspection & Discovery (Highest Priority)

The core requirement is to inspect `pylabrobot` to dynamically generate machine definitions and capabilities.

### Backend

- [ ] **Enumerate Machine Types**:
  - Introspect PLR to find all available `LiquidHandler` and `PlateReader` subclasses.
  - Identify Manufacturers (Hamilton, Opentrons, Tecan, etc.).
  - Distinguish between **Frontend** (Logic/API) and **Backend** (Driver/Communication) classes.
- [ ] **Capability Extraction**:
  - Extract channel counts (e.g., "8-channel", "96-channel", "384-channel").
  - Identify optional modules (Swap, HEPA, etc.).
  - Parse identifiers and metadata into a structured format for the UI.
- [ ] **Discovery Service Update**:
  - Ensure `sync-all` endpoints populate this rich metadata into database/store.

### Frontend

- [ ] **Collapsible Menus**:
  - Implement collapsible categories for Machine Types (e.g., `Liquid Handlers > Hamilton > STAR`).
  - Similar UI pattern to Resources.
- [ ] **Capability Chips**:
  - Render capability tags (e.g., `[8-channel]`, `[96-channel]`, `[SmartSteps]`).
  - Add tooltips/hover info for these chips.
- [ ] **Manufacturer Rendering**:
  - Explicitly render Manufacturer name/logo if available.
  - Group availability by Manufacturer.
- [ ] **Backend vs Frontend Selection**:
  - UI to select the "Machine Type" (Frontend) and then allow selecting the "Driver" (Backend) if applicable (e.g., STAR vs Simulated).

---

## 2. Asset UX & Visualizer Rewrite

- [ ] **Workcell Visualizer (Rewrite)**:
  - **Goal**: Rework the deck visualizer into a "Workcell Visualizer".
  - **Architecture**: Configurable set of deck view windows.
  - **Space**: Relation of workcells in physical space (future).
  - **Immediate Task**: Remove legacy iframe/PLR visualizer components and build new Angular-native grid/deck views.
- [ ] **Deck Setup Debugging**:
  - Fix rendering issues in the Deck Setup step of the Protocol Wizard.

---

## 3. Relationship Visualization (Phase 2)

- [ ] "What's where" spatial view for machines (breadcrumbs).
- [ ] Protocol requirements → asset matching UI.
- [ ] Context-aware add dialogs (suggest compatible resources).

---

## 4. Bulk & Advanced (Phase 3)

- [ ] Multi-select mode with floating action bar.
- [ ] Expert mode toggle (show FQNs, backends, drivers).
- [ ] Maintenance scheduling UI.
- [ ] Inventory alerts.

---

## Reference Patterns

* **Benchling**: Registry/Inventory split.
- **LabArchives**: Freezer box visualization.
- **Docker**: Capabilities/Driver abstraction.
