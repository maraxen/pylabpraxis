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

- [x] **Spatial View (Asset Filters)**:
  - [x] Implement `AssetFiltersComponent`.
  - [x] Sort by: Name, Status, etc (Location sorting implied by search).
  - [x] Filter by: Status, Category, Machine, Workcell.
  - [x] Add `location_label` physical location text field.

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

## 5. Maintenance & Alerts (Completed 2026-01-03)

- [x] **Maintenance Schema**:
  - [x] Pydantic models: `MaintenanceInterval`, `MaintenanceSchedule` - `praxis/backend/models/pydantic_internals/maintenance.py`
  - [x] `MAINTENANCE_DEFAULTS` by category (Liquid Handlers daily/weekly/etc).
  - [x] Backend fields: `maintenance_enabled`, `maintenance_schedule_json` - Alembic migration `bb6b6f27cedb`
- [x] **Frontend UI**:
  - [x] Global "Enable Maintenance" toggle in Settings - `AppStore.maintenanceEnabled()`
  - [x] Per-asset toggle and schedule override in details dialog - `machine-details-dialog.component.ts`
  - [x] Maintenance status badges (OK, Warning, Overdue) - `MaintenanceBadgeComponent`
  - [ ] "Log Maintenance" action - TODO: Add button to log maintenance event

---

## 6. Bulk & Advanced (Phase 4)

- [ ] Multi-select mode with floating action bar.
- [ ] Consumables inventory tracking (partial usage).
- [ ] Backend "Smart Selection" for consumables.

## 7. Technical Debt & UI Polish (2026-01-07)

- [ ] **Needs Attention Icons**: Fix occlusion issue where icons in the "Needs Attention" section are partially cut off.
- [ ] **Add Machine Flow Refactor**: Frontend Category -> Backend Selection flow. Remove Step 2.
- [ ] **Capabilities Interface**: Replace hardcoded JSON with a proper configuration interface.
- [ ] **Add Resource Flow Refactor**: Use cards instead of chips, include filters, Model selection step.
- [ ] **Sidebar Renaming**: Rename "Deck" to "Workcell".
- [ ] **Inventory Menu**: Match Asset Management menu (popup/multi-select).
