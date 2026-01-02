# Asset Management Backlog

**Priority**: CRITICAL
**Owner**: Backend + Frontend
**Last Updated**: 2026-01-02

---

## 1. PLR Inspection & Discovery (Highest Priority)

The core requirement is to inspect `pylabrobot` to dynamically generate machine definitions and capabilities.

### Backend

- [x] **Static PLR Inspection (LibCST)** - COMPLETED 2025-12-30
- [x] **Capability Extraction** - COMPLETED
- [x] **Discovery Service Update** - COMPLETED

### Frontend

- [x] **Collapsible Menus** - COMPLETED
- [x] **Capability Chips** - COMPLETED
- [x] **Manufacturer Rendering** - COMPLETED
- [x] **Backend vs Frontend Selection** - COMPLETED

---

## 2. Asset UX & Visualizer (Completed)

- [x] **Workcell Visualizer (Rewrite)** - COMPLETED
- [x] **Deck Setup Debugging** - COMPLETED

---

## 3. Relationship Visualization (Phase 2)

- [ ] **Spatial View (Asset Filters)**:
  - [ ] Implement `AssetFiltersComponent`.
  - [ ] Sort by: Machine Location, Workcell, Status, Name, Date.
  - [ ] Filter by: Status, Category, Machine, Workcell.
  - [ ] Add `location_label` physical location text field.

### Registry vs Inventory (Conceptual Model)

- [x] **UI Distinction**: Separate tabs for Machines/Resources (Inventory) and Registry (Definitions) - COMPLETED.
- [ ] **Data Model Separation**:
  - [x] **Models**: `MachineDefinition` vs `Machine` exist.
  - [ ] **API Restructuring**: Moved to TECHNICAL_DEBT.md.

---

## 4. Groupings & Organization (P3)

- [x] **Machine Groupings (Inventory)**: Accordion by type - COMPLETED.
- [x] **Resource Groupings**: Accordion by category - COMPLETED.

---

## 5. Maintenance & Alerts (Phase 3)

- [ ] **Maintenance Schema**:
  - [ ] Pydantic models: `MaintenanceInterval`, `MaintenanceSchedule`.
  - [ ] `MAINTENANCE_DEFAULTS` by category (Liquid Handlers daily/weekly/etc).
  - [ ] Backend fields: `maintenance_enabled`, `maintenance_schedule_json`.
- [ ] **Frontend UI**:
  - [ ] Global "Enable Maintenance" toggle in Settings.
  - [ ] Per-asset toggle and schedule override in details dialog.
  - [ ] Maintenance status badges (OK, Warning, Overdue).
  - [ ] "Log Maintenance" action.

---

## 6. Bulk & Advanced (Phase 4)

- [ ] Multi-select mode with floating action bar.
- [ ] Consumables inventory tracking (partial usage).
- [ ] Backend "Smart Selection" for consumables.
