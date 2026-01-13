# H-02: Realistic Simulated Data

**Status:** 🟢 Implementation
**Priority:** P2
**Depends On:** H-01 (optional, for visualization verification)

---

## Context

The current simulated data for Data Visualization is too generic. It uses simple random ranges and linear accumulation. To make the visualization feature useful for demos and testing, we need "realistic" data that mimics actual wet lab process behaviors, such as:

- **Sigmoid curves** for transfer logs (mimicking enzymatic reactions or growth if we were simulating that, though transfer is usually linear/step-wise; perhaps "cumulative volume" should be step-wise, while "temperature" might follow a curve).
- **Varied distributions** across wells (not all wells identical).
- **Meaningful Metadata:** Protocol names should sound real (e.g., "PCR Prep", "Cell Culture Feed"), not just "Protocol A".

## Objectives

1. **Enhance Seeding Logic:**
    - Update `SqliteService` (or `DataVisualizationComponent` fallback logic if that's where the primary mock data lives for the graph) to produce better fake data. *Note: `DataVisualizationComponent` currently has its own `generateMockRuns` / `generateSeededTransferData` functions.*
    - **Refactor Goal:** Ideally, move this realistic generation logic *into* `SqliteService` (or a dedicated `MockDataService`) so it populates the DB table `protocol_runs` and `transfer_logs` (if that table exists or is simulated) rather than just being transient component state. This allows the data to persist across tab switches.

2. **Data Characteristics:**
    - **Volumes:** Step-wise increases (transfers happen at specific times).
    - **Temperature:** Small fluctuations around a set point (e.g., 37°C ± 0.5), maybe a ramp up/down.
    - **Errors:** Inject occasional "failed" status runs with incomplete data.

## Implementation Details

### 1. Refactor Generation Logic

- **Location:** `praxis/web-client/src/app/core/services/sqlite.service.ts`
- **Target Methods:** `seedDefaultRuns` and `generateSeededTransferData` (migrate this from `DataVisualizationComponent` if it's trapped there).
- **Changes:**
  - Create a helper `MockDataGenerator`.
  - Implement specific "profiles":
    - *Profile A (PCR):* Fast transfers, 96 wells, volume 10-50uL.
    - *Profile B (Media Fill):* Slower, larger volumes (100-200uL), 12-24 wells.
  - Update `seedDefaultRuns` to use these profiles to insert rows into the SQLite DB.

### 2. Update `DataVisualizationComponent`

- **Location:** `praxis/web-client/src/app/features/data/data-visualization.component.ts`
- **Changes:**
  - Remove the inline `class SeededRandom` and `generateSeededTransferData` *if* you successfully moved it to a service. If specific visualization-only data is needed, update it to consume the service's robust data.
  - Ensure the component reads from the DB (via `ProtocolService`) rather than generating on the fly, OR update the on-the-fly generation to be "Realistic" if DB persistence isn't feasible in this scope.
  - *Recommendation:* Since `sqlite.service.ts` was confirmed to have `seedDefaultRuns`, prioritize updating that to put good data in the DB.

## Verification

- **Database Check:**
  - Open browser DevTools -> Application -> Storage -> IndexedDB/Sqlite (if visible) or just check the Data Viz UI.
  - Reload page (forcing re-seed if DB is empty or reset).
- **Visual Check:**
  - Open Data Visualization.
  - Select a run.
  - **Graph:** Check if the lines look "organic" or "logical" (e.g., cumulative volume goes UP in steps, not random noise).
  - **Table:** Check Protocol names ("PCR Setup", "Daily Maintenance") and Status variety.

## Definition of Done

- Data Visualization shows at least 3 distinct "types" of protocols with realistic names.
- Graphs show realistic trends (step-wise volume, stable temp).
- Data persists or is consistently re-generated to look high-quality.
