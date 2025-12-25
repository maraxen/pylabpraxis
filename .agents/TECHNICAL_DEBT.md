# Technical Debt

This document tracks known technical debt items that need future attention.

---

## Consumables and Auto-Assignment

**Added:** 2024-12-24  
**Priority:** Medium  
**Area:** Frontend - Asset Selector

**Issue:**
Current auto-selection logic is naive - it simply picks the Nth item from the filtered list where N is the `autoSelectIndex`. This works for basic cases but lacks sophistication.

**Improvements Needed:**

- [ ] Consider resource `status` (prefer `AVAILABLE_IN_STORAGE` over `IN_USE`)
- [ ] Check remaining capacity for consumables (tip racks, plates with partial fills)
- [ ] Handle case where not enough unique resources exist for all fields
- [ ] UI indication when resources must be shared or duplicated
- [ ] Backend endpoint to suggest "best available" with smart ranking

**Files Affected:**

- `praxis/web-client/src/app/shared/formly-types/asset-selector.component.ts`
- `praxis/web-client/src/app/features/run-protocol/components/parameter-config/parameter-config.component.ts`

---

## POST /resources/ API Error

**Added:** 2024-12-24  
**Priority:** Low (workaround exists)  
**Area:** Backend - Resource API

**Issue:**
The `POST /api/v1/resources/` endpoint returns 500 errors. Direct ORM insertion via `scripts/seed_direct.py` works. The API route needs debugging.

**Workaround:**
Use `scripts/seed_direct.py` for seeding resources.

**Files Affected:**

- `praxis/backend/api/resources.py`
- `praxis/backend/services/resource.py`

---

## Navigation Rail Hover Menus

**Added:** 2024-12-24  
**Priority:** Low  
**Area:** Frontend - Navigation

**Issue:**
The navigation rail currently shows only icons with small labels beneath. For features with sub-menus (e.g., Assets → Machines, Resources, Decks), an overlay menu on hover would improve UX.

**Future Improvements:**

- [ ] Implement hover-triggered overlay menus for nav items with children
- [ ] Add tooltips on hover for accessibility
- [ ] Consider flyout menus for nested navigation

**Files Affected:**

- `praxis/web-client/src/app/layout/main-layout.component.ts`

---

## Protocol Queue and Reservation Management

**Added:** 2025-12-24  
**Priority:** High  
**Area:** Backend - Scheduler / Protocol Execution

**Issue:**
The scheduler uses **in-memory** asset reservations (`_asset_reservations` dict). When a run is scheduled, assets are reserved in memory. If the server restarts, these reservations are lost BUT the database still shows runs in `queued` status. This causes:

1. Assets remain "orphaned" as reserved after server restart
2. New runs fail with "Asset already reserved" errors
3. No visibility into current reservation state

**Immediate Workaround:**
Restart the backend server to clear stale in-memory reservations.

**Improvements Needed:**

- [ ] **Reservation Inspection API** (Admin only): `GET /scheduler/reservations` to view current in-memory reservations
- [ ] **Reservation Clearing API** (Admin only): `DELETE /scheduler/reservations/{asset_key}` to manually release stuck reservations
- [ ] **Startup Recovery**: On server startup, scan for runs stuck in `QUEUED`/`PREPARING` status and either:
  - Resume scheduling them
  - Mark them as `FAILED` with appropriate message
- [ ] **Persistent Reservations**: Store reservations in database with `AssetReservationOrm` instead of in-memory dict
- [ ] **User Permissions for Run Management**:
  - Admin users can cancel any run
  - Regular users can only cancel their own runs
  - Require `created_by_user` field to be populated on run creation

**Files Affected:**

- `praxis/backend/core/scheduler.py` - In-memory `_asset_reservations` dict
- `praxis/backend/api/protocols.py` - Cancel endpoint with permission checks
- `praxis/backend/api/scheduler.py` - Reservation inspection endpoints
- `praxis/backend/models/orm/schedule.py` - `AssetReservationOrm` for persistent reservations
