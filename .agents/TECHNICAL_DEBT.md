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
**Updated:** 2025-12-31
**Priority:** ~~High~~ Low (Core issues resolved)
**Area:** Backend - Scheduler / Protocol Execution

**Original Issue:**
The scheduler used **in-memory** asset reservations. Server restarts caused orphaned reservations and "Asset already reserved" errors.

**Status: MOSTLY RESOLVED**

Core reservation persistence and inspection are now implemented:

- [x] **Persistent Reservations**: `AssetReservationOrm` is now the source of truth. The in-memory `_asset_reservations_cache` is just a performance cache.
- [x] **Startup Recovery**: `recover_stale_runs()` scans for stuck `QUEUED`/`PREPARING` runs on startup and marks them as `FAILED`.
- [x] **Reservation Inspection API**: `GET /api/v1/scheduler/reservations` lists all active reservations with filtering options.
- [x] **Reservation Clearing API**: `DELETE /api/v1/scheduler/reservations/{asset_key}` manually releases stuck reservations.

**Remaining Items (Lower Priority):**

- [ ] **User Permissions for Run Management**:
  - Admin users can cancel any run
  - Regular users can only cancel their own runs
  - Require `created_by_user` field to be populated on run creation

**Files Affected:**

- `praxis/backend/core/scheduler.py` - Now uses `AssetReservationOrm` for persistence
- `praxis/backend/api/scheduler.py` - New reservation inspection/clearing endpoints
- `praxis/backend/models/orm/schedule.py` - `AssetReservationOrm` model
- `praxis/backend/models/pydantic_internals/scheduler.py` - Response models for reservation APIs
