# Track B: Operation "Premium Polish" – UI/UX & Non-AI Improvements

**Goal**: Make the app feel professional, responsive, and robust.

**Last Updated**: 2025-12-22

---

## 🎯 Success Criteria

1. Resource filtering is fast and scalable (backend-driven)
2. "Skirted" is separated from "Plate Type" in filtering logic
3. UI feels polished with loading states, error handling, and smooth animations
4. Dark/Light theme works consistently everywhere
5. All components responsive on mobile/tablet

---

## 📋 Current State Analysis

### ✅ Already Completed

| Feature | Status | Notes |
|---------|--------|-------|
| ResourceDialog Base | ✅ | Chip filtering, search, facets working |
| Skeleton Loaders | ✅ | Categories and facets have skeleton states |
| Invert Filtering | ✅ | Client-side toggle implemented |
| Dark/Light Theme | ✅ | System variables used (`--mat-sys-*`) |
| Error Handling | ✅ | `NG0100` and `TS4111` resolved |

### ⚠️ Known Issues / Tech Debt

| Issue | Impact | Priority |
|-------|--------|----------|
| Client-side filtering | Slow with large datasets | High |
| "Skirted" conflated with "plate type" | UX confusion | Medium |
| No backend pagination | Memory issues at scale | Medium |
| Bundle size 775KB | Exceeds 500KB budget | Low |
| Missing 404/error pages | Poor UX on invalid routes | Low |

---

## 🔧 Implementation Backlog

### Phase B.1: Backend-Driven Filtering (High Priority)

**Goal**: Move resource definition filtering from client to server.

#### B.1.1 Create Backend Filter Endpoint

- **File**: `praxis/backend/api/assets.py` (new or extend)
- **Changes**:
  - Create `GET /api/v1/assets/definitions/resource/search`
  - Accept query params: `q` (search), `category`, `vendor`, `properties`
  - Return paginated results with facet counts

#### B.1.2 Extend ResourceTypeDefinition Model

- **File**: `praxis/backend/models/orm/plr_sync.py`
- **Changes**:
  - Ensure `properties_json` JSONB column is indexed for fast filtering
  - Add computed columns or indexes for common filters (category, vendor)

#### B.1.3 Create ResourceDefinition Filter Service

- **File**: `praxis/backend/services/resource_type_definition.py`
- **Changes**:
  - Add `search_definitions(filters: ResourceFilterParams)` method
  - Build SQLAlchemy queries with JSONB operators
  - Return facet aggregations alongside results

#### B.1.4 Update Frontend ResourceDialogComponent

- **File**: `praxis/web-client/src/app/features/assets/components/resource-dialog/resource-dialog.component.ts`
- **Changes**:
  - Replace client-side `allDefinitions` filtering with API calls
  - Debounce search input
  - Update facet counts from server response

---

### Phase B.2: Property-Based Chips (Medium Priority)

**Goal**: Replace static category chips with property-derived dynamic chips.

#### B.2.1 Backend Facet Aggregation

- **File**: `praxis/backend/api/assets.py`
- **Changes**:
  - `GET /api/v1/assets/definitions/resource/facets`
  - Return unique values for each filterable property with counts
  - Support filtering context (e.g., facets filtered by current selection)

#### B.2.2 Frontend Chip Carousel Component

- **File**: `praxis/web-client/src/app/shared/components/chip-carousel/` (new)
- **Changes**:
  - Create reusable horizontal scrolling chip group
  - Input: `chips: { label: string, count: number, selected: boolean }[]`
  - Output: `selectionChange` event
  - Support multi-select within a carousel

#### B.2.3 Integrate Chip Carousel into ResourceDialog

- **File**: `praxis/web-client/src/app/features/assets/components/resource-dialog/`
- **Changes**:
  - Replace static `FilterChipsComponent` with dynamic `ChipCarouselComponent`
  - Group carousels by property category (Type, Vendor, Volume Range, etc.)
  - Wire carousel selections to backend filter requests

---

### Phase B.3: Logic Separation – Skirted vs Plate Type (Medium Priority)

**Goal**: Correctly separate "bottom type" (skirted/unskirted) from "plate format" (96-well, 384-well).

#### B.3.1 Update Property Extraction

- **File**: `praxis/backend/services/resource_type_definition.py`
- **Changes**:
  - In `_extract_properties()`, detect and extract:
    - `bottom_type`: 'flat', 'round', 'v-bottom', 'skirted', 'unskirted'
    - `plate_format`: '96-well', '384-well', '24-well', etc.
  - Parse from class names, attributes, or docstrings

#### B.3.2 Update Facet Generation

- **Changes**:
  - Expose `bottom_type` and `plate_format` as separate facet categories
  - Remove conflated "plate_type" that mixed these concepts

#### B.3.3 Update Frontend Chip Labels

- **Changes**:
  - Display "Bottom Type" and "Format" as separate chip carousels

---

### Phase B.4: UI Polish Backlog (Lower Priority)

#### B.4.1 Loading Skeletons for All Views

- [ ] Protocol Library grid
- [ ] Asset list tables
- [ ] Dashboard stats cards

#### B.4.2 Error Pages

- [ ] Create `NotFoundComponent` (404)
- [ ] Create `ErrorComponent` (500)
- [ ] Add routes in `app.routes.ts`

#### B.4.3 Micro-Animations

- [ ] Chip selection pulse
- [ ] List item hover transitions
- [ ] Card reveal animations

#### B.4.4 Bundle Size Optimization

- [ ] Audit imports with `npx webpack-bundle-analyzer`
- [ ] Lazy load feature modules
- [ ] Tree-shake unused Material components

---

## 📁 Key Files Reference

| Purpose | File Path |
|---------|-----------|
| Resource Dialog | `praxis/web-client/src/app/features/assets/components/resource-dialog/resource-dialog.component.ts` |
| Filter Chips | `praxis/web-client/src/app/features/assets/components/filter-chips/filter-chips.component.ts` |
| Facets Carousel | `praxis/web-client/src/app/features/assets/components/filter-facets-carousel/` |
| Backend Assets API | `praxis/backend/api/assets.py` |
| Resource Type Service | `praxis/backend/services/resource_type_definition.py` |
| Global Styles | `praxis/web-client/src/styles.scss` |

---

## ⚠️ Constraints

1. **NO AI/LLM features** – Use database queries and computed properties only
2. **Backend-first filtering** – Client-side filtering only as fallback for small datasets
3. **Maintain theme consistency** – All new components must use `--mat-sys-*` variables

---

## 📊 Estimated Effort

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| B.1 Backend-Driven Filtering | 6-8 hours | None |
| B.2 Property-Based Chips | 4-6 hours | B.1 |
| B.3 Logic Separation | 2-3 hours | B.1 |
| B.4 UI Polish | 4-6 hours | None (parallel) |
| **Total** | **16-23 hours** | |

---

## 🚫 Explicitly Deferred (Post-Stable)

- AI-Powered Search (Phase 2.7.3)
- Browser-Based Instrument Detection (Phase 2.9)
- Keycloak Theming (Phase 6.5)
- E2E Playwright Tests (Phase 6 - blocked on environment)
