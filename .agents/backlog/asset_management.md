# Asset Management Backlog

**Priority**: CRITICAL
**Owner**: Backend + Frontend
**Last Updated**: 2025-12-30

---

## 1. PLR Inspection & Discovery (Highest Priority)

The core requirement is to inspect `pylabrobot` to dynamically generate machine definitions and capabilities.

### Backend

- [x] **Static PLR Inspection (LibCST)** - COMPLETED 2025-12-30:
  - [x] Created `praxis/backend/utils/plr_static_analysis/` module with LibCST visitors.
  - [x] **Enumerate Machine Types**: Discovers LiquidHandler, PlateReader, and Backend classes via AST.
  - [x] Manufacturers inferred from module paths (Hamilton, Opentrons, Tecan, etc.).
  - [x] Frontend vs Backend distinction via class type classification.
- [x] **Capability Extraction** - COMPLETED:
  - [x] Channel detection from `num_channels` property/defaults and method patterns.
  - [x] Module detection (iSWAP, CoRe96, HEPA) from method names and attributes.
- [x] **Discovery Service Update** - COMPLETED:
  - [x] `MachineTypeDefinitionService` now uses `PLRSourceParser` for static analysis.
  - [x] Deprecation warnings added to old runtime inspection functions in `plr_inspection.py`.

**Known Issues** (see [capability_tracking.md](./capability_tracking.md) for full status):

- [x] ~~Classification bug: LiquidHandler misclassified.~~ FIXED
- [x] ~~Expansion of machine types.~~ FIXED
- [x] ~~Generic capability schemas.~~ FIXED

### Frontend

- [x] **Collapsible Menus**:
  - Implement collapsible categories for Machine Types (e.g., `Liquid Handlers > Hamilton > STAR`).
  - Similar UI pattern to Resources.
- [x] **Capability Chips**:
  - Render capability tags (e.g., `[8-channel]`, `[96-channel]`, `[SmartSteps]`).
  - Add tooltips/hover info for these chips.
- [x] **Manufacturer Rendering**:
  - Explicitly render Manufacturer name/logo if available.
  - Group availability by Manufacturer.
- [x] **Backend vs Frontend Selection**:
  - UI to select the "Machine Type" (Frontend) and then allow selecting the "Driver" (Backend) if applicable (e.g., STAR vs Simulated).

---

## 2. Asset UX & Visualizer Rewrite

- [x] **Workcell Visualizer (Rewrite)**:
  - **Goal**: Rework the deck visualizer into a "Workcell Visualizer".
  - **Architecture**: Configurable set of deck view windows.
  - **Space**: Relation of workcells in physical space (future).
  - **Immediate Task**: Remove legacy iframe/PLR visualizer components and build new Angular-native grid/deck views.
- [ ] **Deck Setup Debugging**:
  - Fix rendering issues in the Deck Setup step of the Protocol Wizard.

---

## 3. Relationship Visualization (Phase 2)

- [ ] "What's where" spatial view for machines (breadcrumbs).
- [x] Protocol requirements → asset matching UI - COMPLETED 2025-12-30.
- [ ] Context-aware add dialogs (suggest compatible resources).

### Registry vs Inventory (Conceptual Model)

- [ ] **Data Model Separation**:
  - **Registry (Definitions)**: Abstract "Types" of resources (e.g., "Corning 96-well Plate").
  - **Inventory (Instances)**: Physical instances with unique IDs/barcodes (e.g., "Plate #1024").
- [ ] **UI Distinction**:
  - Separate views for managing "What we *can* use" vs "What we *have*".

---

## 4. Groupings & Organization (P3)

### Machine Groupings (Inventory)

- [ ] **PLR Type Hierarchy**: Group by `LiquidHandler > STAR > STARlet`.
- [ ] **Location/Workcell Chips**: Show location as chips or column.
- [ ] **Capability Chips**: Show capabilities as color-coded chips.
- [ ] **Collapsible Accordions**: Expand/collapse by high-level machine type.

### Machine Groupings (Registry)

- [ ] **Collapsible by Machine Type**: LiquidHandler, PlateReader, HeaterShaker, etc.
- [ ] **Capability Chips**: Filter/display by capability.

### Resource Groupings (Registry)

- [ ] **Group by Type/Category**: Plates, TipRacks, Carriers, Reservoirs.
- [ ] **Chips for Capacity**: `[96-well]`, `[300µL tips]`, etc.

---

## 5. Bulk & Advanced (Phase 4)

- [ ] Multi-select mode with floating action bar.
- [ ] Expert mode toggle (show FQNs, backends, drivers).
- [ ] Maintenance scheduling UI.
- [ ] Inventory alerts.

---

## Related Backlogs

- **[Capability Tracking System](./capability_tracking.md)**: Comprehensive plan for fixing classification, expanding machine types, and enabling user-configurable capabilities.

---

## Reference Patterns

- **Benchling**: Registry/Inventory split.
- **LabArchives**: Freezer box visualization.
- **Docker**: Capabilities/Driver abstraction.
