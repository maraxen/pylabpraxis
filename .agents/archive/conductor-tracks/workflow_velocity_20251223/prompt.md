# Prompt for Track B Agent: UI/UX Polish

## 🎯 Your Mission

You are implementing **Operation "Premium Polish"** – making PyLabPraxis feel professional, responsive, and robust. Your focus is on performance, UX quality, and proper data separation.

---

## 📚 Required Reading

Before starting, read these documents in order:

1. **`.agents/TRACK_B_PLAN.md`** – Your detailed implementation plan
2. **`GEMINI.md`** – Project conventions and architecture
3. **`.agents/HANDOFF.md`** – Latest handoff notes
4. **`.agents/FRONTEND_UI_GUIDE.md`** – UI/UX specifications

---

## 🚀 Getting Started

### 1. Start Services

```bash
# Terminal 1: Database
make db-test

# Terminal 2: Backend
PRAXIS_DB_DSN="postgresql+asyncpg://test_user:test_password@localhost:5433/test_db" \
  uv run uvicorn main:app --reload --port 8000

# Terminal 3: Frontend
cd praxis/web-client && npm start
```

### 2. Sync Definitions

```bash
curl -X POST http://localhost:8000/api/v1/discovery/sync-all
```

---

## 📋 Your Tasks (In Order)

### Phase B.1: Backend-Driven Filtering (HIGH PRIORITY)

Move resource definition filtering from client to server for scalability.

**Key Tasks**:

1. Create `GET /api/v1/assets/definitions/resource/search` endpoint
2. Support query params: `q`, `category`, `vendor`, `properties`
3. Return paginated results with facet counts
4. Update `ResourceDialogComponent` to use API instead of client filtering

**Key Files**:

- `praxis/backend/api/assets.py`
- `praxis/backend/services/resource_type_definition.py`
- `praxis/web-client/src/app/features/assets/components/resource-dialog/resource-dialog.component.ts`

### Phase B.2: Property-Based Chips

Replace static category chips with dynamically generated property chips.

**Key Tasks**:

1. Create facet aggregation endpoint
2. Create reusable `ChipCarouselComponent`
3. Integrate into ResourceDialog

### Phase B.3: Logic Separation

Separate "bottom type" (skirted/unskirted) from "plate format" (96-well/384-well).

**Key Tasks**:

1. Update property extraction in discovery service
2. Expose as separate facet categories
3. Update frontend chip labels

### Phase B.4: UI Polish

General polish tasks (can be done in parallel):

- Loading skeletons for all views
- 404/Error pages
- Micro-animations
- Bundle size optimization

---

## ⚠️ Constraints

- **NO AI/LLM code** – Use database queries and computed properties only
- **Backend-first filtering** – Client-side only as fallback for small datasets
- **Theme consistency** – All components must use `--mat-sys-*` variables

---

## ✅ Definition of Done

- [ ] ResourceDialog filtering happens on backend (fast at scale)
- [ ] "Bottom Type" and "Format" are separate filter categories
- [ ] All new components use skeleton loaders
- [ ] Dark/Light theme works everywhere
